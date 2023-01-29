var lead_capture_initialted = false;
var longitude = null;
var latitude = null;
var easyassist_tickmarks_clicked=new Array(11).fill(false);
window.check_meeting_status_interval = null;
window.auto_msg_popup_on_client_call_declined = false;

/***************** EasyAssist Custom Select ***********************/

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        background_color = background_color;

        var select_element = document.querySelector(selector);
        var selected_list_class = "easyassist-option-selected";
        var show_option_container_class = "easyassist-dropdown-show";
        var custom_dropdown_selected_option = "";
        var dropdown_option_selected = false;

        var custom_dropdown_wrapper = "";
        var custom_dropdown_option_container = "";
        var custom_dropdown_options = "";
        var custom_dropdown_selected_option_wrapper = "";

        // Create elements
        custom_dropdown_wrapper = create_element('div', 'easyassist-custom-dropdown-container');
        custom_dropdown_option_container = create_element('ul', 'easyassist-custom-dropdown-option-container');
        custom_dropdown_selected_option_wrapper = create_element('div', 'easyassist-dropdown-selected');
        // select_element.wrap(custom_dropdown_wrapper);

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element)

        for(var idx = 0; idx < select_element.children.length; idx ++) {
            let option_el = select_element.children[idx];
            let option_text = option_el.text.trim();
            let option_value = option_el.value;

            if(option_el.selected) {
                dropdown_option_selected = true;
                custom_dropdown_selected_option = option_text;
                custom_dropdown_options += [
                    '<li  class="' + selected_list_class + '">',
                        '<span>' + option_text + '</span>',
                        '<input type="hidden" value="' + option_value + '">',
                    '</li>',
                ].join('');
            } else {
                custom_dropdown_options += [
                    '<li>',
                        '<span>' + option_text + '</span>',
                        '<input type="hidden" value="' + option_value + '">',
                    '</li>',
                ].join('');
            }
        }

        custom_dropdown_option_container.innerHTML = custom_dropdown_options;
        select_element.insertAdjacentElement('afterend', custom_dropdown_option_container)

        if(dropdown_option_selected) {
            custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
        } else if(this.placeholder) { 
            custom_dropdown_selected_option_wrapper.innerHTML = this.placeholder;
        } else {
            custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
        }

        select_element.insertAdjacentElement('afterend', custom_dropdown_selected_option_wrapper);

        // Add eventlistener
        document.addEventListener('click', function(e) {
            if(e.target == custom_dropdown_selected_option_wrapper) {
                custom_dropdown_option_container.classList.toggle(show_option_container_class);
            } else {
                custom_dropdown_option_container.classList.remove(show_option_container_class);
            }
        });

        for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
            let li_element = custom_dropdown_option_container.children[idx];
            li_element.addEventListener('click', function(e) {
                let selected_option_text = this.innerHTML;
                reset_dropdown();
                li_element.classList.add(selected_list_class);
                li_element.style.setProperty('background-color', background_color, 'important');
                custom_dropdown_selected_option_wrapper.innerHTML = selected_option_text;
                custom_dropdown_option_container.classList.toggle(show_option_container_class);

                // Update selecte drodown
                let option_value = li_element.children[1].value;
                select_element.value = option_value;
                var change_event = new Event('change');
                select_element.dispatchEvent(change_event);
            });

            li_element.addEventListener('mouseover', function(e) {
                li_element.style.setProperty('background-color', background_color, 'important');
            });

            li_element.addEventListener('mouseout', function(e) {
                if(!li_element.classList.contains(selected_list_class)) {
                    li_element.style.removeProperty('background-color');
                }
            })
        }

        function reset_dropdown() {
            for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
                custom_dropdown_option_container.children[idx].classList.remove(selected_list_class);
                custom_dropdown_option_container.children[idx].style.removeProperty('background-color');
            }
        }

        function create_element(html_tag, css_class) {
            let html_element = document.createElement(html_tag);
            html_element.className = css_class;
            return html_element;
        }
    }
}

function easyassist_change_tooltipshow(el) {
    el.querySelector('label').style.display = "inline-block";
}

function easyassist_change_tooltiphide(el) {
    el.querySelector('label').style.display = "none";
}

function setValuetoSome(el) {
    el.parentElement.setAttribute("zQPK", "true")
    var rate_value = el.getAttribute("value")
}

function change_color_easyassist_rating_bar_all(el) {
    current_hover_value = parseInt(el.childElementCount);
    if (el.getAttribute("zQPK") == "false") {
        for (var i = 0; i <= current_hover_value; i++) {
            if (el.children[i] != undefined) {
                el.children[i].style.color = "black"
                el.children[i].style.backgroundColor = "white"
            }
        }
    }
}

function change_color_rating_z_bar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for (var i = current_hover_value; i <= current_hover_value; i++) {
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color = "black"
            el.parentElement.children[i].style.backgroundColor = "white"
        }
    }
}

function change_color_rating_v_bar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for (var i = 0; i < current_hover_value; i++) {
        if (current_hover_value <= 6) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "red"
        }
        if (6 < current_hover_value && current_hover_value <= 8) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "orange"
        }
        if (8 < current_hover_value) {
            el.parentElement.children[i].style.color = "white"
            el.parentElement.children[i].style.backgroundColor = "green"
        }
    }
    for (var j = current_hover_value; j <= el.parentElement.childElementCount; j++) {
        if (el.parentElement.children[j] != undefined) {
            el.parentElement.children[j].style.color = "black"
            el.parentElement.children[j].style.backgroundColor = "white"
        }
    }
}

window.addEventListener('message', function(event) {
    // IMPORTANT: Check the origin of the data!

    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    /*if(easyassist_session_id!=null && easyassist_session_id!=undefined){
        console.log("session already set");
        return;
    }*/

    if (~event.origin.indexOf(EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST)) {
        data = {};
        try {
            data = JSON.parse(event.data);
        } catch {}
        if (data.event_id == "collect-cookie-updates") {
            if (data != "None") {
                data = atob(data.eacSession);
                try {
                    data = JSON.parse(data);
                    if (data.hostname != window.location.hostname) {
                        delete data["hostname"];
                        for (cookie_name in data) {
                            console.log(cookiename, data[cookiename]);
                            set_easyassist_cookie(cookie_name, data[cookie_name]);
                        }
                    }
                } catch {
                    console.warn("unable to decode session details.");
                }
            }
        } else if (data.event_id == "close-bot") {
            hide_easyassist_livechat_iframe();
        } else if (data.event_id == "cobrowsing-client-chat-message") {
            message = data.data.message;
            attachment = data.data.attachment;
            attachment_file_name = data.data.attachment_file_name;
            send_livechat_message_to_agent(message, attachment, attachment_file_name);
        }

        if(event.data == "voip_meeting_ready") {
            send_voip_meeting_ready_over_socket();
            var voip_meeting_ready_interval = setInterval(function() {
                if(get_easyassist_cookie("is_agent_voip_meeting_joined") == get_easyassist_cookie("easyassist_session_id")) {
                    if(get_easyassist_cookie("is_meeting_audio_muted") == "true") {
                        document.getElementById("easyassist-client-meeting-mic-off-btn").click();
                    }
                    document.getElementById("easyassist-voip-loader").style.display = 'none';
                    clearInterval(voip_meeting_ready_interval);
                }
            }, 1000);

        } else if(event.data == "voip_meeting_ended") {
            reset_voip_meeting();
        }
    } else {
        // The data hasn't been sent from your site!
        // Be careful! Do not use it.
        return;
    }
});

function feedback_easyassist_modal(el) {
    el.parentElement.setAttribute("zQPK", "true")
    contentvalue = parseInt(el.getAttribute("value"));
    window.EASYASSIST_CLIENT_FEEDBACK = contentvalue;
}

(function(exports) {

    window.EASYASSIST_TAG_VALUE = "easyassist-tag-value";

    var search_html_field = window.EASYASSIST_COBROWSE_META.search_html_field;
    var obfuscated_fields = window.EASYASSIST_COBROWSE_META.obfuscated_fields
    var easyassist_id_count = 0;
    window.easyassist_close_nav_timeout = null;

    function convert_urls_to_absolute(nodeList) {

        if (!nodeList.length) {
            return [];
        }

        var attrName = 'href';
        if (nodeList[0].__proto__ === HTMLImageElement.prototype ||
            nodeList[0].__proto__ === HTMLScriptElement.prototype) {
            attrName = 'src';
        }

        nodeList = [].map.call(nodeList, function(el, i) {
            var attr = el.getAttribute(attrName);
            // If no src/href is present, disregard.
            if (!attr) {
                return;
            }

            var absURL = /^(https?|data):/i.test(attr);
            if (absURL) {
                return el;
            } else {
                // Set the src/href attribute to an absolute version.
                // if (attr.indexOf('/') != 0) { // src="images/test.jpg"
                //        el.setAttribute(attrName, document.location.origin + document.location.pathname + attr);
                //      } else if (attr.match(/^\/\//)) { // src="//static.server/test.jpg"
                //        el.setAttribute(attrName, document.location.protocol + attr);
                //      } else {
                //        el.setAttribute(attrName, document.location.origin + attr);
                //      }

                // Set the src/href attribute to an absolute version. Accessing
                // el['src']/el['href], the browser will stringify an absolute URL, but
                // we still need to explicitly set the attribute on the duplicate.
                el.setAttribute(attrName, el[attrName]);

                return el;
            }
        });
        return nodeList;
    }

    function add_event_listner_into_element(html_element, event_type, target_function){
        html_element.removeEventListener(event_type, target_function);
        html_element.addEventListener(event_type, target_function);
    }

    function obfuscate_data_using_recursion(element) {

        if (!element.children.length) {

            element.innerHTML = easyassist_obfuscate(element.innerHTML);
            return;
        }

        for (var index = 0; index < element.children.length; index++) {

            obfuscate_data_using_recursion(element.children[index]);
        }

        var child_objects = element.children;

        var inner_text = element.innerText;
        if (inner_text.length > 0 && inner_text[0] != 'X') {

            element.innerHTML = "XXXXXXXXXX";
            for (var index = 0; index < child_objects.length; index++) {

                element.appendChild(child_objects[index]);
            }
            return;
        }
        return;
    }

    function is_this_obfuscated_element(element) {

        var is_obfuscated_element = false;
        for (var mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            element_value = element.getAttribute(obfuscated_fields[mask_index]["key"]);
            if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                return [true, obfuscated_fields[mask_index]["masking_type"]];
            }
        }
        return [false, ""];
    }

    function create_easyassist_value_attr_into_document() {

        document_input_tag_list = document.querySelectorAll("input");

        for (var d_index = 0; d_index < document_input_tag_list.length; d_index++) {

            document_input_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            // document_input_tag_list[d_index].onchange = sync_html_element_value_change;
            add_event_listner_into_element(document_input_tag_list[d_index], "change", sync_html_element_value_change)
            easyassist_id_count += 1;

            var is_numeric = false;
            if (isNaN(parseInt(document_input_tag_list[d_index].value)) == false) {
                is_numeric = true;
            }

            var is_type_text = false;
            var attr_type = document_input_tag_list[d_index].getAttribute("type");
            if (attr_type == "text") {
                is_type_text = true;
            }

            var is_active_element = false;
            if (document.activeElement == document_input_tag_list[d_index]) {
                is_active_element = true;
            }
            if (attr_type == "button" || attr_type == "submit") {
                document_input_tag_list[d_index].classList.add("easyassist-click-element");
            }

            var is_obfuscated_element = is_this_obfuscated_element(document_input_tag_list[d_index]);

            document_input_tag_list[d_index].removeAttribute("easyassist-active");
            if (is_active_element) {
                document_input_tag_list[d_index].setAttribute("easyassist-active", "true");
            }

            value = document_input_tag_list[d_index].value;

            if (attr_type == "checkbox") {
                if (document_input_tag_list[d_index].checked) {
                    document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, "checked");
                } else {
                    document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, "unchecked");
                }
            } else if (attr_type == "radio") {
                // document_input_tag_list[d_index].onchange = delay_sync_html_data;
                add_event_listner_into_element(document_input_tag_list[d_index], "change", delay_sync_html_data)
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
                // document_input_tag_list[d_index].onchange = send_attachment_to_agent_for_validation;
                add_event_listner_into_element(document_input_tag_list[d_index], "chnage", send_attachment_to_agent_for_validation)
            } else {
                document_input_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, value);
            }
        }

        document_textarea_tag_list = document.querySelectorAll("textarea");
        for (var d_index = 0; d_index < document_textarea_tag_list.length; d_index++) {

            document_textarea_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            easyassist_id_count += 1;

            var is_active_element = false;
            if (document.activeElement == document_textarea_tag_list[d_index]) {
                is_active_element = true;
            }

            document_textarea_tag_list[d_index].removeAttribute("easyassist-active");
            if (is_active_element) {
                document_textarea_tag_list[d_index].setAttribute("easyassist-active", "true");
            }

            var is_numeric = false;
            if (isNaN(parseInt(document_textarea_tag_list[d_index].value)) == false) {
                is_numeric = true;
            }

            var is_obfuscated_element = is_this_obfuscated_element(document_textarea_tag_list[d_index]);
            if (is_obfuscated_element[0]) {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value, is_obfuscated_element[1]));
            } else if (is_numeric) {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value));
            } else {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, document_textarea_tag_list[d_index].value);
            }
        }

        document_select_tag_list = document.querySelectorAll("select");
        for (var d_index = 0; d_index < document_select_tag_list.length; d_index++) {

            document_select_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            // document_select_tag_list[d_index].onchange = send_data_to_server;
            add_event_listner_into_element(document_select_tag_list[d_index], "change", send_data_to_server)

            easyassist_id_count += 1;

            var is_active_element = false;
            if (document.activeElement == document_select_tag_list[d_index]) {
                is_active_element = true;
            }

            document_select_tag_list[d_index].removeAttribute("easyassist-active");
            if (is_active_element) {
                document_select_tag_list[d_index].setAttribute("easyassist-active", "true");
            }

            var is_obfuscated_element = is_this_obfuscated_element(document_select_tag_list[d_index]);

            var selected_option = document_select_tag_list[d_index].options[document_select_tag_list[d_index].selectedIndex];
            if (selected_option != null && selected_option != undefined) {
                var selected_option_inner_html = selected_option.innerHTML;
                var selected_option_value = selected_option.value;
                if (is_obfuscated_element[0] == false) {
                    document_select_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, selected_option_inner_html);
                } else {
                    document_select_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(selected_option_inner_html, is_obfuscated_element[1]));
                }
            }
        }

        var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
        var observer = new MutationObserver(function(e) {
            sync_html_element_value_change();
        });

        document_label_tag_list = document.querySelectorAll("label");
        for (var d_index = 0; d_index < document_label_tag_list.length; d_index++) {
            document_label_tag_list[d_index].classList.add("easyassist-click-element");

            document_label_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            easyassist_id_count += 1;

            label_id = document_label_tag_list[d_index].getAttribute("id");
            if (label_id == null || label_id == undefined) {
                continue;
            }

            observer.observe(document_label_tag_list[d_index], {
                childList: true
            });
        }

        document_span_tag_list = document.querySelectorAll("span");
        for (var d_index = 0; d_index < document_span_tag_list.length; d_index++) {
            var is_obfuscated_element = is_this_obfuscated_element(document_span_tag_list[d_index]);
            if (is_obfuscated_element[0]) {
                document_span_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_span_tag_list[d_index].innerHTML, is_obfuscated_element[1]));
            }

            span_id = document_span_tag_list[d_index].getAttribute("id");
            if (span_id == null || span_id == undefined) {
                continue;
            }

            document_span_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            easyassist_id_count += 1;

            observer.observe(document_span_tag_list[d_index], {
                childList: true
            });
        }

        document_table_tag_list = document.querySelectorAll("table");
        for (var d_index = 0; d_index < document_table_tag_list.length; d_index++) {

            var is_obfuscated_element = false;
            for (var mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
                element_value = document_table_tag_list[d_index].getAttribute(obfuscated_fields[mask_index]["key"]);
                if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                    is_obfuscated_element = true;
                    break;
                }
            }

            if (!is_obfuscated_element) {

                continue;
            }
            for (var row_index = 0; row_index < document_table_tag_list[d_index].tBodies[0].rows.length; row_index++) {

                for (var col_index = 0; col_index < document_table_tag_list[d_index].tBodies[0].rows[row_index].children.length; col_index++) {

                    var table_element = document_table_tag_list[d_index].tBodies[0].rows[row_index].children[col_index];
                    table_element.setAttribute("easyassist-element-id", easyassist_id_count);
                    // table_element.onchange = sync_html_element_value_change;
                    add_event_listner_into_element(table_element, "change", sync_html_element_value_change)
                    easyassist_id_count += 1;
                }
            }
        }

        document_li_tag_list = document.querySelectorAll("li");
        for (var d_index = 0; d_index < document_li_tag_list.length; d_index++) {

            li_id = document_li_tag_list[d_index].getAttribute("id");
            if (li_id == null || li_id == undefined) {
                continue;
            }

            document_li_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            easyassist_id_count += 1;

            observer.observe(document_li_tag_list[d_index], {
                childList: true
            });
        }

        document_a_tag_list = document.querySelectorAll("a");
        for (var index = 0; index < document_a_tag_list.length; index++) {
            document_a_tag_list[index].classList.add("easyassist-click-element");
            document_a_tag_list[index].setAttribute("easyassist-element-id", easyassist_id_count);
            easyassist_id_count += 1;
        }

        document_button_tag_list = document.querySelectorAll("button");
        for (var index = 0; index < document_button_tag_list.length; index++) {
            document_button_tag_list[index].classList.add("easyassist-click-element");
            document_button_tag_list[index].setAttribute("easyassist-element-id", easyassist_id_count);
            easyassist_id_count += 1;
        }
    }


    function set_value_attr_into_screenshot(screenshot) {
        var easyassist_edit_access = get_easyassist_cookie("easyassist_edit_access");
        screenshot_input_tag_list = screenshot.querySelectorAll("input");
        for (var s_index = 0; s_index < screenshot_input_tag_list.length; s_index++) {
            if (easyassist_edit_access != "true") {
                screenshot_input_tag_list[s_index].style.pointerEvents = 'none';
            }
            attr_type = screenshot_input_tag_list[s_index].getAttribute("type");
            easyassist_tag_value = screenshot_input_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
            if (attr_type == "checkbox" || attr_type == "radio") {
                screenshot_input_tag_list[s_index].removeAttribute("checked");
                if (easyassist_tag_value == "checked") {
                    screenshot_input_tag_list[s_index].setAttribute("checked", "checked");
                }
            } else {
                screenshot_input_tag_list[s_index].setAttribute("value", easyassist_tag_value);
            }
            screenshot_input_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }

        screenshot_textarea_tag_list = screenshot.querySelectorAll("textarea");
        for (var s_index = 0; s_index < screenshot_textarea_tag_list.length; s_index++) {
            if (easyassist_edit_access != "true") {
                screenshot_textarea_tag_list[s_index].style.pointerEvents = 'none';
            }
            easyassist_tag_value = screenshot_textarea_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
            screenshot_textarea_tag_list[s_index].innerHTML = easyassist_tag_value;
            screenshot_textarea_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }

        screenshot_select_tag_list = screenshot.querySelectorAll("select");
        for (var s_index = 0; s_index < screenshot_select_tag_list.length; s_index++) {
            if (easyassist_edit_access != "true") {
                screenshot_select_tag_list[s_index].style.pointerEvents = 'none';
            }
            easyassist_tag_value = screenshot_select_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
            screenshot_select_tag_list[s_index].setAttribute("value", easyassist_tag_value);
            screenshot_select_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);

            if (easyassist_tag_value == "XXXXX") {
                var obfuscated_option = document.createElement("option");
                obfuscated_option.value = "XXXXX";
                obfuscated_option.innerHTML = "XXXXX";
                screenshot_select_tag_list[s_index].appendChild(obfuscated_option);
            }

            for (var option_index = 0; option_index < screenshot_select_tag_list[s_index].options.length; option_index++) {
                screenshot_select_tag_list[s_index].options[option_index].removeAttribute("selected");
                if (screenshot_select_tag_list[s_index].options[option_index].innerHTML == easyassist_tag_value) {
                    screenshot_select_tag_list[s_index].options[option_index].setAttribute("selected", "selected");
                }
            }
        }

        screenshot_table_tag_list = screenshot.querySelectorAll("table");

        for (var d_index = 0; d_index < screenshot_table_tag_list.length; d_index++) {

            if (!is_this_obfuscated_element(screenshot_table_tag_list[d_index])[0]) {

                continue;
            }
            for (var row_index = 0; row_index < screenshot_table_tag_list[d_index].tBodies[0].rows.length; row_index++) {

                for (var col_index = 0; col_index < screenshot_table_tag_list[d_index].tBodies[0].rows[row_index].children.length; col_index++) {

                    var table_element = screenshot_table_tag_list[d_index].tBodies[0].rows[row_index].children[col_index];
                    obfuscate_data_using_recursion(table_element);
                }
            }
        }

        screenshot_label_tag_list = screenshot.querySelectorAll("label");
        for (var d_index = 0; d_index < screenshot_label_tag_list.length; d_index++) {

            label_id = screenshot_label_tag_list[d_index].getAttribute("id");
            if (label_id == null || label_id == undefined) {
                continue;
            }

            if (!is_this_obfuscated_element(screenshot_label_tag_list[d_index])[0]) {

                continue;
            }
            screenshot_label_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_label_tag_list[d_index].innerHTML);
        }

        screenshot_li_tag_list = screenshot.querySelectorAll("li");
        for (var d_index = 0; d_index < screenshot_li_tag_list.length; d_index++) {

            li_id = screenshot_li_tag_list[d_index].getAttribute("id");
            if (li_id == null || li_id == undefined) {
                continue;
            }

            if (!is_this_obfuscated_element(screenshot_li_tag_list[d_index])[0]) {

                continue;
            }
            screenshot_li_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_li_tag_list[d_index].innerHTML);
        }

                screenshot_p_tag_list = screenshot.querySelectorAll("p");

        for (var p_index = 0; p_index < screenshot_p_tag_list.length; p_index++) {
            var is_obfuscated_element = false;
            for (var mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
                element_value = screenshot_p_tag_list[p_index].getAttribute(obfuscated_fields[mask_index]["key"]);
                if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                    is_obfuscated_element = true;
                    break;
                }
            }

            if (is_obfuscated_element) {
                screenshot_p_tag_list[p_index].innerHTML = "XXXXXXXXXXXXX";
            }

        }


        screenshot_div_tag_list = screenshot.querySelectorAll("div");

        for (var div_index = 0; div_index < screenshot_div_tag_list.length; div_index++) {
            var is_obfuscated_element = false;
            for (var mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
                element_value = screenshot_div_tag_list[div_index].getAttribute(obfuscated_fields[mask_index]["key"]);
                if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                    is_obfuscated_element = true;
                    break;
                }
            }

            if (is_obfuscated_element) {
                screenshot_div_tag_list[div_index].innerHTML = "XXXXXXXXXXXXX";
            }

        }

        document_span_tag_list = screenshot.querySelectorAll("span");
        for (var d_index = 0; d_index < document_span_tag_list.length; d_index++) {
            var is_obfuscated_element = is_this_obfuscated_element(document_span_tag_list[d_index]);
            if (is_obfuscated_element[0]) {
                easyassist_tag_value = document_span_tag_list[d_index].getAttribute(EASYASSIST_TAG_VALUE);
                document_span_tag_list[d_index].innerHTML = easyassist_tag_value;
                document_span_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
            }
        }

    }

    function remove_easyassist_attr_value_from_document() {
        document_input_tag_list = document.querySelectorAll("input");
        for (var d_index = 0; d_index < document_input_tag_list.length; d_index++) {
            document_input_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
        document_select_tag_list = document.querySelectorAll("select");
        for (var d_index = 0; d_index < document_select_tag_list.length; d_index++) {
            document_select_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
        document_textarea_tag_list = document.querySelectorAll("textarea");
        for (var d_index = 0; d_index < document_textarea_tag_list.length; d_index++) {
            document_textarea_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
    }

    function create_proxy_server_pass_urls(nodeList) {

        if (!nodeList.length) {
            return [];
        }

        var attrName = 'href';
        if (nodeList[0].__proto__ === HTMLImageElement.prototype ||
            nodeList[0].__proto__ === HTMLScriptElement.prototype) {
            attrName = 'src';
        }

        nodeList = [].map.call(nodeList, function(el, i) {
            var attr = el.getAttribute(attrName);
            // If no src/href is present, disregard.
            if (!attr) {
                return;
            }

            var absURL = /^(https?|data):/i.test(attr);
            if (absURL) {
                if (/^(data):/i.test(attr)) {
                    el.setAttribute(attrName, attr);
                    return el;
                } else {
                    // if(attr=="https://www.nipponindiamf.com/investeasy/main.18241e80171d76ccabe6.js"){
                    //     el.setAttribute(attrName, "javascript:void(0)");
                    //     return el;
                    // }else{
                    attr = EASYASSIST_COBROWSE_META.proxy_server + attr
                    el.setAttribute(attrName, attr);
                    return el;
                    // }
                }
            } else {
                // Set the src/href attribute to an absolute version.
                // if (attr.indexOf('/') != 0) { // src="images/test.jpg"
                //        el.setAttribute(attrName, document.location.origin + document.location.pathname + attr);
                //      } else if (attr.match(/^\/\//)) { // src="//static.server/test.jpg"
                //        el.setAttribute(attrName, document.location.protocol + attr);
                //      } else {
                //        el.setAttribute(attrName, document.location.origin + attr);
                //      }

                // Set the src/href attribute to an absolute version. Accessing
                // el['src']/el['href], the browser will stringify an absolute URL, but
                // we still need to explicitly set the attribute on the duplicate.
                el.setAttribute(attrName, EASYASSIST_COBROWSE_META.proxy_server + el[attrName]);
                return el;
            }
        });
        return nodeList;
    }

    function set_scroll_into_document() {
        div_elements = document.querySelectorAll("div");
        for (var index = 0; index < div_elements.length; index++) {
            div_ele = div_elements[index];
            div_ele.setAttribute("easyassist-data-scroll-x", div_ele.scrollLeft);
            div_ele.setAttribute("easyassist-data-scroll-y", div_ele.scrollTop);
        }
    }

    function set_animation_into_screenshot(screenshot) {
        div_elements = screenshot.querySelectorAll("div");
        for (var index = 0; index < div_elements.length; index++) {
            div_ele = div_elements[index];
            //div_ele.setAttribute("style", "animation-name: none !important;");
        }
    }

    function add_canvas_tag_into_document() {
        canvas_elements = document.getElementsByTagName("canvas");
        for (var index = 0; index < canvas_elements.length; index++) {
            canvas_elements[index].setAttribute("easyassist-canvas-id", index);
        }
    }

    function convert_canvas_into_image(screenshot) {
        canvas_elements = screenshot.getElementsByTagName("canvas");
        for (var index = 0; index < canvas_elements.length; index++) {
            easyassist_canvas_id = canvas_elements[index].getAttribute("easyassist-canvas-id");
            doc_element = document.querySelector("[easyassist-canvas-id='" + easyassist_canvas_id + "']");

            data_url = doc_element.toDataURL("img/png");
            img_tag = document.createElement("img");
            img_tag.src = data_url;
            canvas_elements[index].style.display = "none";
            canvas_elements[index].parentElement.appendChild(img_tag);
        }
    }

    function remove_blocked_html_tags(screenshot) {
        blocked_html_tags = EASYASSIST_COBROWSE_META.blocked_html_tags;
        if (blocked_html_tags.length == 0) {
            return;
        }

        for (var b_index = 0; b_index < blocked_html_tags.length; b_index++) {
            selected_blocked_html_tags = screenshot.querySelectorAll(blocked_html_tags[b_index]);
            for (var index = 0; index < selected_blocked_html_tags.length; index++) {
                blocked_tag_id = selected_blocked_html_tags[index].getAttribute("id");
                if (blocked_tag_id != null && blocked_tag_id != undefined) {
                    continue;
                }
                selected_blocked_html_tags[index].parentNode.removeChild(selected_blocked_html_tags[index]);
            }
        }
        return;
    }

    function remove_easyassist_items(screenshot){

        try{
            screenshot.getElementsByTagName("div").namedItem("easyassist-co-browsing-request-edit-access").remove()
        }catch(err){}
    }

    function disable_button_elements(screenshot) {
        disable_fields = EASYASSIST_COBROWSE_META.disable_fields;
        if (disable_fields.length == 0) return;
        button_elements = screenshot.querySelectorAll("button");
        for (var index = 0; index < button_elements.length; index++) {
            for (var f_index = 0; f_index < disable_fields.length; f_index++) {
                attr_value = button_elements[index].getAttribute(disable_fields[f_index].key);
                if (attr_value != null && attr_value != undefined && attr_value == disable_fields[f_index].value) {
                    button_elements[index].disabled = true;
                    button_elements[index].onclick = null;
                    button_elements[index].style.setProperty("background-color", "#808080", "important");
                    button_elements[index].style.setProperty("background-image", "unset", "important");
                }
            }
        }

        a_tag_elements = screenshot.querySelectorAll("a");
        for (var index = 0; index < a_tag_elements.length; index++) {
            for (var f_index = 0; f_index < disable_fields.length; f_index++) {
                attr_value = a_tag_elements[index].getAttribute(disable_fields[f_index].key);
                if (attr_value != null && attr_value != undefined && attr_value == disable_fields[f_index].value) {
                    a_tag_elements[index].removeAttribute("href");
                    a_tag_elements[index].onclick = null;
                }
            }
        }

        input_tag_elements = screenshot.querySelectorAll("input");
        for (var index = 0; index < input_tag_elements.length; index++) {
            for (var f_index = 0; f_index < disable_fields.length; f_index++) {
                attr_value = input_tag_elements[index].getAttribute(disable_fields[f_index].key);
                if (attr_value != null && attr_value != undefined && attr_value == disable_fields[f_index].value) {
                    input_tag_elements[index].onclick = null;
                    input_tag_elements[index].disabled = true;
                    input_tag_elements[index].style.setProperty("background-color", "#808080", "important");
                    input_tag_elements[index].style.setProperty("background-image", "unset", "important");
                }
            }
        }
    }

    // TODO: current limitation is css background images are not included.
    function screenshot_page() {
        // 1. Rewrite current doc's imgs, css, and script URLs to be absolute before
        // we duplicate. This ensures no broken links when viewing the duplicate.
        convert_urls_to_absolute(document.images);
        convert_urls_to_absolute(document.querySelectorAll("link"));
        convert_urls_to_absolute(document.querySelectorAll("iframe"));
        convert_urls_to_absolute(document.scripts);
        easyassist_id_count = 0;
        // Create Easy-Assist Custom Value container
        create_easyassist_value_attr_into_document();
        set_scroll_into_document();
        add_canvas_tag_into_document();

        // 2. Duplicate entire document.
        var screenshot = document.documentElement.cloneNode(false);
        screenshot = document.documentElement.cloneNode(true);

        remove_blocked_html_tags(screenshot);
        // Set Value Attribute
        set_value_attr_into_screenshot(screenshot);
        // Remove Attr
        remove_easyassist_attr_value_from_document();

        set_animation_into_screenshot(screenshot);
        disable_button_elements(screenshot);

        remove_easyassist_items(screenshot);
        // createProxyPassURL
        create_proxy_server_pass_urls(document.querySelectorAll("iframe"));
        create_proxy_server_pass_urls(screenshot.querySelectorAll("link[rel='stylesheet']"));
        convert_canvas_into_image(screenshot);

        screenshot_scripts = screenshot.querySelectorAll("script");
        for (var index = 0; index < screenshot_scripts.length; index++) {
            if (EASYASSIST_COBROWSE_META.strip_js) {
                //screenshot_scripts[index].setAttribute("src", "javascript:void(0)");
                screenshot_scripts[index].parentNode.removeChild(screenshot_scripts[index]);
            }
        }

        // Use <base> to make anchors and other relative links absolute.
        var b = document.createElement('base');
        b.href = document.location.protocol + '//' + location.host;
        // b.href = "https://easyassist.allincall.in";
        var head = screenshot.querySelector('head');
        head.insertBefore(b, head.firstChild);

        // 3. Screenshot should be readyonly, no scrolling, and no selections.
        if (get_easyassist_cookie("easyassist_edit_access") != "true") {
            screenshot.style.pointerEvents = 'none';
            screenshot.style.webkitUserSelect = 'none';
            screenshot.style.mozUserSelect = 'none';
            screenshot.style.msUserSelect = 'none';
            screenshot.style.oUserSelect = 'none';
            screenshot.style.userSelect = 'none';
        }
        // screenshot.style.overflow = 'hidden';

        // 4. Preserve current x,y scroll position of this page. See add_on_page_load_().
        screenshot.dataset.scrollX = window.scrollX;
        screenshot.dataset.scrollY = window.scrollY;
        screenshot.dataset.screenWidth = screen.width;
        screenshot.dataset.screenHeight = screen.height;

        // 4.5. When the screenshot loads (e.g. as ablob URL, as iframe.src, etc.),
        // scroll it to the same location of this page. Do this by appending a
        // window.onDOMContentLoaded listener which pulls out the saved scrollX/Y
        // state from the DOM.
        var script = document.createElement('script');
        script.textContent = '(' + add_on_page_load_.toString() + ')();'; // self calling.
        screenshot.querySelector('body').appendChild(script);

        ripple_element = screenshot.querySelector("#easyassist-ripple_effect");
        ripple_element.parentNode.removeChild(ripple_element);

        cobrowsing_modal_element = screenshot.querySelector("#easyassist-co-browsing-modal-id");
        cobrowsing_modal_element.parentNode.removeChild(cobrowsing_modal_element);

        easyassist_product_category_modal_element = screenshot.querySelector("#easyassist-product-category-modal-id");
        easyassist_product_category_modal_element.parentNode.removeChild(easyassist_product_category_modal_element);

        easychat_share_link_modal = screenshot.querySelector("#easychat_share_link_Model");
        easychat_share_link_modal.parentNode.removeChild(easychat_share_link_modal);

        easyassist_nav_options_cobrowsing = screenshot.querySelector("#easyassist-side-nav-options-co-browsing");
        easyassist_nav_options_cobrowsing.parentNode.removeChild(easyassist_nav_options_cobrowsing);

        easyassist_request_assist_modal = screenshot.querySelector("#easyassist-co-browsing-request-assist-modal");
        easyassist_request_assist_modal.parentNode.removeChild(easyassist_request_assist_modal);

        easyassist_request_meeting_modal = screenshot.querySelector("#easyassist-co-browsing-request-meeting-modal");
        easyassist_request_meeting_modal.parentNode.removeChild(easyassist_request_meeting_modal);

        easyassist_feedback_modal = screenshot.querySelector("#easyassist-co-browsing-feedback-modal");
        easyassist_feedback_modal.parentNode.removeChild(easyassist_feedback_modal);

        easyassist_agent_joining_modal = screenshot.querySelector("#easyassist_agent_joining_modal");
        easyassist_agent_joining_modal.parentNode.removeChild(easyassist_agent_joining_modal);

        easyassist_sidenav_menu = screenshot.querySelector("#easyassist-sidenav-menu-id");
        easyassist_sidenav_menu.parentNode.removeChild(easyassist_sidenav_menu);

        var chatbot_element = screenshot.querySelector("#allincall-chat-box");
        if (chatbot_element != null && chatbot_element != undefined) {
            chatbot_element.parentNode.removeChild(chatbot_element);
        }

        easyassist_snackbar = screenshot.querySelector("#easyassist-snackbar");
        easyassist_snackbar.parentNode.removeChild(easyassist_snackbar);

        easyassist_livechat = screenshot.querySelector("#easyassist-livechat-iframe");
        easyassist_livechat.parentNode.removeChild(easyassist_livechat);

        agent_mouse_pointer = screenshot.querySelector("#agent-mouse-pointer");
        agent_mouse_pointer.parentNode.removeChild(agent_mouse_pointer);

        try{
            easyassist_dataiframe = screenshot.querySelector("#easyassist-iframe");
            easyassist_dataiframe.parentNode.removeChild(easyassist_dataiframe);
        }catch(err){

        }

        try {
            easyassist_voip_modal = screenshot.querySelector("#easyassist-voip-video-calling-request-modal");
            easyassist_voip_modal.parentNode.removeChild(easyassist_voip_modal);
        } catch(err) {}

        try {
            easyassist_audio_player = screenshot.querySelector("#cobrowsing-voip-ringing-sound");
            easyassist_audio_player.parentNode.removeChild(easyassist_audio_player);
        } catch(err) {}

        // console.log(screenshot.outerHTML);
        // 5. Create a new .html file from the cloned content.
        // var blob = new Blob([screenshot.outerHTML], {type: 'text/html'});
        // compressed = EasyAssistLZString.compress(screenshot.outerHTML);
        outerhtml = screenshot.outerHTML;
        outerhtml = outerhtml.replace(/\s+/g, " ");
        return outerhtml;
    }

    function add_easyassist_ripple_animation_frame() {
        //Add span tag
        var span = document.createElement("span");
        span.id = "easyassist-ripple_effect";
        span.style.height = "15px";
        span.style.width = "15px";
        span.style.border = "1px solid red";
        span.style.borderRadius = "50%";
        span.style.position = "fixed";
        span.style.zIndex = "2147483647";
        span.style.WebkitAnimationName = "easyassist-ripple-animation";
        span.style.animationName = "easyassist-ripple-animation";
        span.style.animationDuration = "1s";
        span.style.animationTimingFunction = "ease";
        span.style.animationIterationCount = "infinite";
        document.getElementsByTagName("body")[0].appendChild(span);
        document.getElementById("easyassist-ripple_effect").style.display = "none";
        var div = document.createElement("span");
        div.id = "easyassist-snackbar";
        document.getElementsByTagName("body")[0].appendChild(div);
    }

    var show_ripple_timer = null;

    function show_easyassist_ripple_effect(clientX, clientY) {
        if (show_ripple_timer != null) {
            clearTimeout(show_ripple_timer);
        }
        var span = document.getElementById("easyassist-ripple_effect");
        hide_easyassist_ripple_effect();
        span.style.display = "inline-block";
        span.style.top = clientY + "px";
        span.style.left = clientX + "px";
        show_ripple_timer = setTimeout(function(e) {
            hide_easyassist_ripple_effect();
        }, 5000);
    }

    function hide_easyassist_ripple_effect() {
        var span = document.getElementById("easyassist-ripple_effect");
        span.style.display = "none";
    }

    function add_connection_easyassist_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-conection-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header">',
                    '<h6>Connect with the Client</h6>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body">',
                     EASYASSIST_COBROWSE_META.message_on_connect_confirmation_modal,
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class="easyassist-modal-primary-btn" onclick="close_connection_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">OK</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function add_floating_sidenav_easyassist_button() {
        if (EASYASSIST_COBROWSE_META.show_easyassist_connect_agent_icon == true && EASYASSIST_COBROWSE_META.source_easyassist_connect_agent_icon != "null") {
            var src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/" + EASYASSIST_COBROWSE_META.source_easyassist_connect_agent_icon;
            add_connect_icon_into_page(src);
        } else {
            add_connect_sidenav_into_page();
        }
        //Add Model
        var div_model = document.createElement("div");
        div_model.id = "easyassist-co-browsing-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";

        var mobile_input_html = "";
        var virtual_agent_code_html = "";
        var lang_dropdown_html = "";
        if (EASYASSIST_COBROWSE_META.ask_client_mobile == true || EASYASSIST_COBROWSE_META.ask_client_mobile == "true" || EASYASSIST_COBROWSE_META.ask_client_mobile == "True") {
            if (EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == true || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "true" || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "True") {
                mobile_input_html += [
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row; border-radius:30px;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                            '<input type="number" autocomplete="off" name="easyassist-client-mobile-number" id="easyassist-client-mobile-number" placeholder="Enter Mobile number" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
                        '<label id="modal-cobrowse-customer-number-error"></label>',
                    '</div>',
                ].join('');
            } else {
                mobile_input_html += [
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row;border-radius:30px;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                            '<input type="number" autocomplete="off" name="easyassist-client-mobile-number" id="easyassist-client-mobile-number" placeholder="Enter Mobile Number (optional)" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
                        '<label id="modal-cobrowse-customer-number-error"></label>',
                    '</div>'
                ].join('');
            }
        }

        virtual_agent_code_html += [
            '<div class="easyassist-customer-connect-modal-content-wrapper">',
                '<input type="text" autocomplete="off" name="easyassist-client-agent-virtual-code" id="easyassist-client-agent-virtual-code" placeholder="Enter agent code" >',
                '<label id="modal-cobrowse-virtual-agent-code-error"></label>',
            '</div>',
        ].join('');

        // if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
        //     var dropdown_option_html = "";
        //     for (var index = 0; index < EASYASSIST_COBROWSE_META.supported_language.length; index++) {
        //         if (EASYASSIST_COBROWSE_META.supported_language[index]["value"].toLowerCase() == "english") {
        //             dropdown_option_html += '<option selected="" value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
        //         } else {
        //             dropdown_option_html += '<option value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
        //         }
        //     }
        //     lang_dropdown_html += [
        //         '<div class="easyassist-customer-connect-modal-content-wrapper">',
        //             '<select id="easyassist-inline-form-input-preferred-language" >',
        //                 dropdown_option_html,
        //             '</select>',
        //             '<label id="modal-cobrowse-customer-language-error"></label>',
        //         '</div>',
        //     ].join('');
        // }

        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header" style="text-align: center;">',
                    '<h6>Connect with the Client</h6>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body" style="padding: 1rem 2rem!important;">',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<input type="text" autocomplete="off" name="easyassist-client-name" id="easyassist-client-name" placeholder="Enter Full name">',
                        '<label id="modal-cobrowse-customer-name-error"></label>',
                    '</div>',
                    mobile_input_html,
                    virtual_agent_code_html,
                    lang_dropdown_html,
                    '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;">',
                        '<span>' + EASYASSIST_COBROWSE_META.connect_message + '</span>',
                    '</div>',
                    '<label id="modal-cobrowse-connect-error"></label>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<div style="padding-top: 1em;">',
                        '<button class ="easyassist-modal-cancel-btn" id="easyassist-co-browsing-connect-cancel-btn" onclick="close_easyassist_browsing_modal()">Cancel</button>',
                        '<button class ="easyassist-modal-primary-btn" id="easyassist-co-browsing-connect-button"  onclick="connect_with_easyassist_customer()">Generate Link</button>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        // if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
        //     modal_html += '<select id="easyassist-inline-form-input-preferred-language" >\
        //             <option selected="" value="None">Choose preferred language</option>';

        //     for (var index = 0; index < EASYASSIST_COBROWSE_META.supported_language.length; index++) {
        //         if (EASYASSIST_COBROWSE_META.supported_language[index]["value"].toLowerCase() == "english") {
        //             modal_html += '<option selected="" value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
        //         } else {
        //             modal_html += '<option value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
        //         }

        //     }
        //     modal_html += '</select><br><br>';
        // }

        div_model.innerHTML = modal_html;
        var sharable_link = '<div id="easychat_share_link_Model"><div class="easychat_share_link_Model-content"><h3>Share with Customer</h3><br><div class="easychat_share_link_Model-content_wrapper" ><div class="easychat_share_link_Model-content_buttons_wrapper"><button disabled style="width: 75%;color:black;">Anyone with the link can guide you</button><button style="width: 25%;" onclick="copy_text_to_clipboard_sharable_link_easyassist()">Copy link</button></div><input id="easychat_share_link_Model-content_link_wrapper" type="text" value="" disabled autocomplete="off"></div><br><p style="color: black;">*Copy above generated link and share with customer.</p><br><button class="easychat_share_link_Model-content-close_button">Done</button></div></div>';
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-co-browsing-connect-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-co-browsing-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sharable_link);

        // if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
        //     document.getElementById("easyassist-inline-form-input-preferred-language").selectedIndex = -1;
        //     var product_category_dropdown = new EasyassistCustomSelect(
        //         '#easyassist-inline-form-input-preferred-language', 
        //         'Choose preferred language',
        //         EASYASSIST_COBROWSE_META.floating_button_bg_color);
        // }

        document.getElementById("easyassist-client-name").addEventListener('keydown', function(e) {
            var target_el = e.target;
            if(target_el.value.length > 40) {
                if(e.key != 'Backspace' && e.key != 'Delete' && e.key != 'ArrowLeft' && e.key != 'ArrowRight') {
                    e.preventDefault()
                }
            }
        });
    }

    function add_easyassist_product_category_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-product-category-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var dropdown_html = "";
        var dropdown_option_html = "";
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            for (var index = 0; index < EASYASSIST_COBROWSE_META.product_category_list.length; index++) {
                dropdown_option_html += '<option value="' + EASYASSIST_COBROWSE_META.product_category_list[index]["key"] + '">' + EASYASSIST_COBROWSE_META.product_category_list[index]["value"] + '</option>';
            }
        }

        dropdown_html += [
            '<div class="easyassist-customer-connect-modal-content-wrapper">',
                '<select id="easyassist-inline-form-input-product-category">',
                    dropdown_option_html,
                '</select>',
                '<label id="easyassist-product-category-modal-error" ></label>',
            '</div>'
        ].join('');

        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header">',
                    '<h6>Make a selection</h6>',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        EASYASSIST_COBROWSE_META.message_on_choose_product_category_modal,
                    '</div>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body">',
                    dropdown_html,
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class ="easyassist-modal-cancel-btn" onclick="close_easyassist_product_category_modal()" style="color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">Deny</button>',
                    '<button class ="easyassist-modal-primary-btn" id="easyassist-product-category-proceed-button"  onclick="set_easyassist_product_category()">Proceed</button>',
                '</div>',
            '</div>'
        ].join('');

        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-inline-form-input-product-category").selectedIndex = -1;
        var product_category_dropdown = new EasyassistCustomSelect(
            '#easyassist-inline-form-input-product-category', 
            'Select one',
            EASYASSIST_COBROWSE_META.floating_button_bg_color);
        document.getElementById("easyassist-product-category-proceed-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function add_connect_sidenav_into_page() {
        //Add Span
        var nav_span = document.createElement("span");
        nav_span.id = "easyassist-side-nav-options-co-browsing";
        nav_span.setAttribute("class", "easyassist-side-nav-class");
        nav_span.style.backgroundColor = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        if (EASYASSIST_COBROWSE_META.floating_button_position == "left") {
            nav_span.style.left = "-"+ EASYASSIST_COBROWSE_META.floating_button_left_right_position.toString() +"px";
            nav_span.style.borderRadius = "0px 0px 10px 10px";
        } else {
            nav_span.style.right = "-"+ EASYASSIST_COBROWSE_META.floating_button_left_right_position.toString() +"px";
            nav_span.style.borderRadius = "10px 10px 0px 0px";
        }
        nav_span.textContent = "Generate Support Link";
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            nav_span.setAttribute("onclick", "show_easyassist_product_category_modal()");
        } else {
            nav_span.setAttribute("onclick", "show_easyassist_browsing_modal()");
        }

        document.getElementsByTagName("body")[0].appendChild(nav_span);
    }

    function add_connect_icon_into_page(src) {
        var easychat_popup_image = document.createElement("img");
        easychat_popup_image.id = "easyassist-side-nav-options-co-browsing";
        easychat_popup_image.style.position = "fixed";
        easychat_popup_image.style.cursor = "pointer";
        easychat_popup_image.style.bottom = "20px";
        easychat_popup_image.style.width = "8em";
        easychat_popup_image.style.zIndex = "2147483647";
        easychat_popup_image.style.right = "20px";
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            easychat_popup_image.setAttribute("onclick", "show_easyassist_product_category_modal()");
        } else {
            easychat_popup_image.setAttribute("onclick", "show_easyassist_browsing_modal()");
        }
        easychat_popup_image.src = src;
        easychat_popup_image.style.display = "none";
        document.body.appendChild(easychat_popup_image);

        var easychat_popup_minimize_tooltip = document.createElement("span");
        easychat_popup_minimize_tooltip.id = "allincall-minimize-popup-tooltip";
        easychat_popup_minimize_tooltip.style.visibility = "hidden";
        easychat_popup_minimize_tooltip.style.backgroundColor = "blue";
        easychat_popup_minimize_tooltip.style.right = "10px";
        easychat_popup_minimize_tooltip.style.bottom = "120px";
        easychat_popup_minimize_tooltip.style.position = "fixed";
        easychat_popup_minimize_tooltip.style.zIndex = "2147483647";
        easychat_popup_minimize_tooltip.style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        easychat_popup_minimize_tooltip.style.color = "white";
        easychat_popup_minimize_tooltip.style.padding = "4px 8px";
        easychat_popup_minimize_tooltip.style.borderRadius = "10px";

        document.getElementsByTagName("body")[0].appendChild(easychat_popup_minimize_tooltip);


        document.getElementById("easyassist-side-nav-options-co-browsing").addEventListener("mouseover", function(e) {
            document.getElementById("allincall-minimize-popup-tooltip").textContent = "Connect with an agent";
            document.getElementById("allincall-minimize-popup-tooltip").style.visibility = "unset";
        });

        document.getElementById("easyassist-side-nav-options-co-browsing").addEventListener("mouseout", function(e) {
            document.getElementById("allincall-minimize-popup-tooltip").style.visibility = "hidden";
        });
    }

    function hide_easyassist_feedback_form(el) {
        document.getElementById("easyassist-co-browsing-feedback-modal").style.display = "none";
    }

    function show_easyassist_feedback_form(el) {
        // document.getElementById("easyassist-close-session-remarks").value = "";
        // reset_easyassist_rating_bar();
        hide_easyassist_video_calling_request_modal();
        document.getElementById("easyassist-co-browsing-feedback-modal").style.display = "flex";
        hide_easyassist_livechat_iframe();
    }

    function hide_easyassist_agent_joining_modal(el) {
        document.getElementById("easyassist_agent_joining_modal").style.display = "none";
    }

    function show_easyassist_agent_joining_modal(el) {
        document.getElementById("easyassist_agent_joining_modal").style.display = "flex";
    }

    function hide_easyassist_video_calling_request_modal(el) {
        try {
            document.getElementById("easyassist-voip-video-calling-request-modal").style.display = "none";
        } catch(err) {}
    }

    function show_easyassist_video_calling_request_modal(el) {
        try {
            document.getElementById("easyassist-voip-video-calling-request-modal").style.display = "flex";
        } catch(err) {}
    }

    function add_easyassist_request_assist_modal() {
        var request_modal_html = "";
        if (EASYASSIST_COBROWSE_META.enable_verification_code_popup == true) {
            request_modal_html = [
                '<div id="easyassist-co-browsing-request-assist-modal" class="easyassist-customer-verification-modal" >',
                    '<div class="easyassist-customer-connect-modal-content">',
                        '<div class="easyassist-customer-connect-modal-header">',
                            '<div style="display:flex;align-items:center;flex-direction:column;">',
                                '<h6 style="padding-bottom:12px;">Verification Code</h6>',
                                '<div class="easyassist-customer-verification-icon-wrapper">',
                                    '<div class="easyassist-customer-verification-icon">',
                                        '<svg width="34" height="40" viewBox="0 0 34 40" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M33.3585 8.31703C33.2087 8.15026 33.0252 8.01542 32.8195 7.92095C32.6138 7.82649 32.3904 7.77443 32.1631 7.76803C28.6323 7.67803 24.1646 3.99703 21.2108 2.55253C19.3862 1.66303 18.1816 1.07653 17.277 0.922034C17.0933 0.895938 16.9066 0.896443 16.7231 0.923534C15.8185 1.07803 14.6139 1.66453 12.7908 2.55403C9.83695 3.99703 5.36926 7.67803 1.83849 7.76803C1.61106 7.77476 1.38747 7.82696 1.18158 7.9214C0.97569 8.01583 0.791888 8.15049 0.641566 8.31703C0.329986 8.66073 0.169227 9.10995 0.193874 9.56803C0.952335 24.6025 6.48311 33.907 16.1877 39.3145C16.44 39.454 16.72 39.526 16.9985 39.526C17.277 39.526 17.557 39.454 17.8108 39.3145C27.5154 33.907 33.0446 24.6025 33.8046 9.56803C33.8307 9.11002 33.6704 8.66047 33.3585 8.31703ZM25.6416 14.23L17.4523 26.0125C17.1585 26.4355 16.697 26.716 16.24 26.716C15.7816 26.716 15.2723 26.4715 14.9508 26.158L9.17849 20.5285C8.99003 20.3441 8.88422 20.0944 8.88422 19.834C8.88422 19.5737 8.99003 19.324 9.17849 19.1395L10.6046 17.746C10.7942 17.563 11.0502 17.4603 11.317 17.4603C11.5837 17.4603 11.8397 17.563 12.0293 17.746L15.7831 21.406L22.3046 12.0205C22.4555 11.8058 22.6875 11.6579 22.9498 11.6093C23.2121 11.5607 23.4834 11.6152 23.7046 11.761L25.3739 12.865C25.5944 13.0119 25.7463 13.2379 25.7965 13.4937C25.8467 13.7495 25.791 14.0142 25.6416 14.23Z" fill="#00DB3D"/>',
                                        '</svg>',
                                    '</div>',
                                '</div>',
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body">',
                            '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;padding-top:0!important;">',
                                EASYASSIST_COBROWSE_META.assist_message,
                            '</div>',
                            '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;padding-top:0!important;">',
                                'Please enter Support Code shared by the Expert',
                            '</div>',
                            '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;">',
                                '<div style="border-color: #E6E6E6;">',
                                    '<input class="easyassist-verfication-otp-input" type="number" onfocus="change_verification_input_color(this);" autocomplete="off">',
                                    '<input class="easyassist-verfication-otp-input" type="number" onfocus="change_verification_input_color(this);" autocomplete="off">',
                                    '<input class="easyassist-verfication-otp-input" type="number" onfocus="change_verification_input_color(this);" autocomplete="off">',
                                    '<input class="easyassist-verfication-otp-input" type="number" onfocus="change_verification_input_color(this);" autocomplete="off">',
                                '</div>',
                                '<label id="easyassist-request-assist-otp-error"></label>',
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer">',
                            '<div style="padding-top: 1em;">',
                                '<button class="easyassist-modal-cancel-btn" onclick="update_agent_assistant_request(\'false\')" id="easyassist-verification-cancel-btn">Cancel</button>',
                                '<button class="easyassist-modal-primary-btn" onclick="update_agent_assistant_request(\'true\')" id="easyassist-verify-button">Allow</button>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');
        } else {
            request_modal_html = [
                '<div id="easyassist-co-browsing-request-assist-modal" class="easyassist-customer-verification-modal" >',
                    '<div class="easyassist-customer-connect-modal-content">',
                        '<div class="easyassist-customer-connect-modal-header">',
                            '<h6 style="padding-bottom:12px; text-align: center;">Connect with our Experts</h6>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body">',
                            '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;padding-top:0!important;">',
                                EASYASSIST_COBROWSE_META.assist_message,
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer">',
                            '<div style="padding-top: 1em;">',
                                '<button class="easyassist-modal-cancel-btn" onclick="update_agent_assistant_request(\'false\')" id="easyassist-verification-cancel-btn">Cancel</button>',
                                '<button class="easyassist-modal-primary-btn" onclick="update_agent_assistant_request(\'true\')" id="easyassist-verify-button">Allow</button>',
                            '</div>',
                        '</div>',
                    '</div>',
                '</div>'
            ].join('');
        }

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', request_modal_html);
        document.getElementById("easyassist-verify-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-verification-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');

        var verify_inputs = document.getElementsByClassName('easyassist-verfication-otp-input');
        for(let idx = 0; idx < verify_inputs.length; idx ++) {
            verify_inputs[idx].addEventListener('keyup', function(e) {
                if(e.key == 'Backspace') {
                    if(this.previousSibling) {
                        this.previousSibling.focus();
                    }
                    if(e.target != document.getElementsByClassName('easyassist-verfication-otp-input')[0]) {
                        e.target.style.color = "inherit";
                        e.target.style.borderColor = "inherit";
                    }
                } else if(e.key >= '0' && e.key <= '9') {
                    keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                    if (keys.indexOf(this.value) != -1) {
                        if(this.nextSibling) {
                            this.nextSibling.focus();
                        }
                    }
                }
            });

            verify_inputs[idx].addEventListener('keydown', function(e) {
                if(e.key >= 0 && e.key <= 9) {
                    if(this.value.length + 1 > 1) {
                        if(this.nextSibling) {
                            this.nextSibling.focus();
                        } else {
                            e.preventDefault();
                            e.stopPropagation();
                        }
                    }
                }
            });

            verify_inputs[idx].addEventListener('paste', function(e) {
                var regex_code = /^[0-9]{4}$/g;
                var clipboard_data = e.clipboardData || e.originalEvent.clipboardData || window.clipboardData;
                var pasted_data = clipboard_data.getData('text');

                if(idx == 0) {
                    if(regex_code.test(pasted_data)){
                        for(var index = 0; index < verify_inputs.length; index ++) {
                            verify_inputs[index].value = pasted_data[index];
                            verify_inputs[index].focus();
                        }
                    }
                }
                e.preventDefault();
                e.stopPropagation();
            });
        }
    }

    function add_easyassist_request_meeting_modal() {
        var meeting_modal_html = [
            '<div id="easyassist-co-browsing-request-meeting-modal" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>Connect with the client</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body">',
                        EASYASSIST_COBROWSE_META.meeting_message,
                        '<label id="easyassist-request-meeting-error"></label>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" onclick="update_agent_meeting_request(\'false\')" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Decline</button>',
                        '<button class="easyassist-modal-primary-btn" onclick="update_agent_meeting_request(\'true\')" id="easyassist-meeting-connect-button">Connect</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', meeting_modal_html);
        document.getElementById("easyassist-meeting-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function add_easyassist_request_edit_access() {
        var request_edit_access_modal_html = [
            '<div id="easyassist-co-browsing-request-edit-access" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-body" style="text-align:center;">',
                        'Customer has requested for Edit Access. Would you like to allow?',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class="easyassist-modal-cancel-btn" id="easyassist-edit-access-cancel-btn" onclick="update_agent_request_edit_access(\'false\')">Deny</button>',
                    '<button class="easyassist-modal-primary-btn" id="easyassist-edit-access-allow-button" onclick="update_agent_request_edit_access(\'true\')">Allow</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', request_edit_access_modal_html);
        document.getElementById("easyassist-edit-access-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-edit-access-allow-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function add_easyassist_video_calling_request_modal() {
        var meeting_modal_html = "";
        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            var meeting_modal_html = [
                '<div id="easyassist-voip-video-calling-request-modal" class="easyassist-customer-connect-modal">',
                    '<div class="easyassist-customer-connect-modal-content">',
                        '<div class="easyassist-customer-connect-modal-header">',
                            '<h6>',
                                '<span class="easyassist-svg-wrapper" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">',
                                    '<svg width="17" height="12" viewBox="0 0 17 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M11.9 9.20003C11.9 10.5515 10.6632 11.6471 9.1375 11.6471H2.7625C1.23681 11.6471 0 10.5515 0 9.20003V2.80003C0 1.44855 1.23681 0.352966 2.7625 0.352966H9.1375C10.6632 0.352966 11.9 1.44855 11.9 2.80003V9.20003ZM16.7977 1.40207C16.9283 1.5382 17 1.71103 17 1.88969V10.1102C17 10.526 16.6194 10.8631 16.15 10.8631C15.9483 10.8631 15.7532 10.7996 15.5995 10.6839L12.75 8.53814V3.46106L15.5995 1.31597C15.9572 1.04667 16.4937 1.08521 16.7977 1.40207Z" fill="white"/>',
                                    '</svg>',
                                '</span>',
                                'Video Call',
                            '</h6>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body"  style="padding-top: 1.5em!important; min-height: 5em!important;">',
                            'A request will be sent to the customer and you will be connected with him/her on virtual meeting',
                            '<label id="easyassist-video-meeting-error" style="margin: 2em 0 1em -1em!important;"></label>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Request</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
        } else if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            var meeting_modal_html = [
                '<div id="easyassist-voip-video-calling-request-modal" class="easyassist-customer-connect-modal">',
                    '<div class="easyassist-customer-connect-modal-content">',
                        '<div class="easyassist-customer-connect-modal-header">',
                            '<h6>',
                                '<span class="easyassist-svg-wrapper" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">',
                                    '<svg width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M13.7528 9.33678C12.7881 9.33678 11.8548 9.19851 10.9842 8.94962C10.8478 8.90887 10.7011 8.90282 10.561 8.93217C10.4209 8.96152 10.293 9.02507 10.192 9.11555L8.96064 10.4775C6.74103 9.54419 4.6626 7.78123 3.55672 5.75555L5.08613 4.60789C5.2979 4.41431 5.36064 4.14468 5.27437 3.90271C4.98417 3.1353 4.83515 2.31259 4.83515 1.46222C4.83515 1.08888 4.48221 0.777771 4.05868 0.777771H1.34495C0.921425 0.777771 0.411621 0.943697 0.411621 1.46222C0.411621 7.88493 6.47437 13.2222 13.7528 13.2222C14.3097 13.2222 14.5293 12.7867 14.5293 12.4064V10.0212C14.5293 9.64789 14.1763 9.33678 13.7528 9.33678Z" fill="white"/>',
                                    '</svg>',
                                '</span>',
                                'Audio Call',
                            '</h6>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body"  style="padding-top: 1.5em!important; min-height: 5em!important;">',
                            'A request will be sent to the customer and you will be connected with him/her on audio call',
                            '<label id="easyassist-video-meeting-error" style="margin: 2em 0 1em -1em!important;"></label>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Request</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
        } else if(EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {
            var meeting_modal_html = [
                '<div id="easyassist-voip-video-calling-request-modal" class="easyassist-customer-connect-modal">',
                    '<div class="easyassist-customer-connect-modal-content">',
                        '<div class="easyassist-customer-connect-modal-header">',
                            '<h6>',
                                '<span class="easyassist-svg-wrapper" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">',
                                    '<svg width="17" height="12" viewBox="0 0 17 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M11.9 9.20003C11.9 10.5515 10.6632 11.6471 9.1375 11.6471H2.7625C1.23681 11.6471 0 10.5515 0 9.20003V2.80003C0 1.44855 1.23681 0.352966 2.7625 0.352966H9.1375C10.6632 0.352966 11.9 1.44855 11.9 2.80003V9.20003ZM16.7977 1.40207C16.9283 1.5382 17 1.71103 17 1.88969V10.1102C17 10.526 16.6194 10.8631 16.15 10.8631C15.9483 10.8631 15.7532 10.7996 15.5995 10.6839L12.75 8.53814V3.46106L15.5995 1.31597C15.9572 1.04667 16.4937 1.08521 16.7977 1.40207Z" fill="white"/>',
                                    '</svg>',
                                '</span>',
                                'Video Call',
                            '</h6>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body"  style="padding-top: 1.5em!important; min-height: 5em!important;">',
                            'A request will be sent to the customer and you will be connected with him/her on virtual meeting',
                            '<label id="easyassist-video-meeting-error" style="margin: 2em 0 1em -1em!important;"></label>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Request</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
        }

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', meeting_modal_html);
    }

    function add_easyassist_voip_audio_player() {
        var audio_player_html = "";
        if(EASYASSIST_COBROWSE_META.enable_voip_calling || EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            audio_player_html = [
                '<div id="cobrowsing-voip-ringing-sound">',
                    '<audio loop="loop" id="easyassist-voip-ring-sound" src="' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/files/sounds/phone_ringing_sound.mp3" type="audio/mpeg">',
                    '</audio>',
                '</div>',
                '<div id="cobrowsing-voip-beep-sound">',
                    '<audio id="easyassist-voip-beep-sound" src="' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/files/sounds/beep_sound.mp3" type="audio/mpeg">',
                    '</audio>',
                '</div>',
            ].join('');
        }
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', audio_player_html);
    }
    // function add_easyassist_feedback_form() {
    //     var add_easyassist_feedback_form = '<div id="easyassist-co-browsing-feedback-modal" style="display: none;">\
    //   <div id="easyassist-co-browsing-modal-content" style="padding: 1em; text-align: center;">\
    //     <h6 style="font-size:1.5em !important; margin-bottom:0.5em !important; color:black;">Feedback <span style="cursor:pointer;float:right;box-sizing: border-box;font-size: 1.5rem;font-weight: 700;line-height: 1;color: #000;text-shadow: 0 1px 0 #fff;" onclick="hide_easyassist_feedback_form()">x</span></h6>\
    //     <hr><p style="color:black;">We would love to hear your valuable feedback. It would help us serve you better!</p>\
    //     <div id="easyAssist-nps-rating-bar-container__XqPZ" class="easyAssist-nps-rating-bar-container" zqpk="false" onmouseout="change_color_easyassist_rating_bar_all(this)">\
    //       <button onmouseover="change_color_rating_v_bar(this)" onmouseout="change_color_rating_z_bar(this)" onclick="feedback_easyassist_modal(this)" value="1">1</button>\
    //       <button onclick="feedback_easyassist_modal(this)" onmouseover="change_color_rating_v_bar(this)" onmouseout="change_color_rating_z_bar(this)" value="2">2</button>\
    //       <button onmouseover="change_color_rating_v_bar(this)" onclick="feedback_easyassist_modal(this)" onmouseout="change_color_rating_z_bar(this)" value="3">3</button>\
    //       <button onclick="feedback_easyassist_modal(this)" onmouseover="change_color_rating_v_bar(this)" onmouseout="change_color_rating_z_bar(this)" value="4">4</button>\
    //       <button onmouseover="change_color_rating_v_bar(this)" onclick="feedback_easyassist_modal(this)" onmouseout="change_color_rating_z_bar(this)" value="5">5</button>\
    //       <button onclick="feedback_easyassist_modal(this)" onmouseover="change_color_rating_v_bar(this)" onmouseout="change_color_rating_z_bar(this)" value="6">6</button>\
    //       <button onmouseover="change_color_rating_v_bar(this)" onclick="feedback_easyassist_modal(this)" onmouseout="change_color_rating_z_bar(this)" value="7">7</button>\
    //       <button onclick="feedback_easyassist_modal(this)" onmouseover="change_color_rating_v_bar(this)" onmouseout="change_color_rating_z_bar(this)" value="8">8</button>\
    //       <button onmouseover="change_color_rating_v_bar(this)" onclick="feedback_easyassist_modal(this)" onmouseout="change_color_rating_z_bar(this)" value="9">9</button>\
    //       <button onclick="feedback_easyassist_modal(this)" onmouseover="change_color_rating_v_bar(this)" onmouseout="change_color_rating_z_bar(this)" value="10">10</button>\
    //     </div>\
    //     <textarea id="easyassist-client-feedback" placeholder="comments..." class="easyassist-form-control" style="height:10em !important;width:-webkit-fill-available;"></textarea><br>\
    //     <div>\
    //         <button onclick="submit_agent_feedback(\'no_feedback\')" style="background-color: #486EDB; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em; border-style: none; float: right; margin-right: 5%;outline:none;">No thanks</button>\
    //         <button onclick="submit_agent_feedback(\'feedback\')" style="background-color: #1b5e20; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em; border-style: none; float: right; margin-right: 5%;outline:none;">Submit</button>\
    //     </div>\
    //     <br><br>\
    //   </div>\
    // </div>';
    //     document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form);
    // }

    function add_easyassist_feedback_form() {
        var add_easyassist_feedback_form = [
            '<div id="easyassist-co-browsing-feedback-modal" class="easyassist-customer-feedback-modal" style="display: none;">',
                '<div class="easyassist-customer-feedback-modal-content" style="width: 450px !important">',
                    '<div class="easyassist-customer-feedback-modal-header">',
                        '<h6 style="padding-bottom: 1em!important;width:100%; cursor:pointer">Ready to end the session?</h6>',
                    '</div>',
                    '<div class="easyassist-customer-feedback-modal-body">',
                        '<label style="margin-bottom:15px !important;">',
                            '<label for="easyassist-mask-successfull-cobrowsing-session" style="width: fit-content !important;margin-right:10px;">Lead has been closed successfully.</label>',
                            '<input id="easyassist-mask-successfull-cobrowsing-session" type="checkbox" checked>',
                        '</label>',
                        '<label for="easyassist-close-session-remarks" style="margin-bottom:10px !important;">Comments<sup>*</sup></label>',
                        '<textarea id="easyassist-close-session-remarks" class="easyassist-feedbackComments" property="comment" cols="30" rows="5" placeholder="Remarks"></textarea>',
                    '</div>',
                    '<div class="easyassist-customer-feedback-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" id="easyassist-feedback-nothanks-btn" onclick="hide_easyassist_feedback_form()" type="button" data-dismiss="easyassist-modal">',
                            'Cancel',
                        '</button>',
                        '<button class="easyassist-modal-primary-btn" id="easyassist-feedback-submit-button" onclick="submit_agent_feedback(\'feedback\')">',
                            'Submit',
                        '</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form);
        document.getElementById("easyassist-feedback-submit-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-feedback-nothanks-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function add_easyassist_agent_joining_modal(){
        var div_model = document.createElement("div");
        div_model.id = "easyassist_agent_joining_modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header">',
                    '<h6>Connect with our Experts</h6>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body">',
                    'Our Customer Support Agent will be connecting with you shortly. Please wait.',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class ="easyassist-modal-primary-btn" onclick="hide_easyassist_agent_joining_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;" >OK</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function add_sidenav_floating_menu() {
        var sidenav_menu = '<div class="easyassist-custom-nav-bar_wrapper" id="easyassist-sidenav-menu-id" style="display:none;">\
          <div class="easyassist-custom-nav-bar" id="easyassist-sidenav-submenu-id" onmouseover="on_easyassist_client_mouse_over_nav_bar(this)" onmouseout="on_easyassist_mouse_out_nav_bar(this)">\
            <a href="javascript:void(0)" onclick="close_easyassist_sidenav();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path d="M11.6044 8L6.76923 3L1.93407 8L-4.37114e-08 7L6.76923 -2.95892e-07L13.5385 7L11.6044 8Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
              </svg>\
              <label id="easyassist-icon-path-0-label">\
                <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                  <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                </svg>\
                <span>Minimise</span>\
              </label>\
            </a>\
            <a href="javascript:void(0)" onclick="show_easyassist_livechat_iframe();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path id="easyassist-icon-path-2"\
                  d="M11 1.83325C16.0625 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0625 20.1666 11 20.1666C9.49628 20.1666 8.04388 19.8035 6.74278 19.12L2.80991 20.1439C2.39349 20.2525 1.96797 20.0028 1.85951 19.5863C1.82597 19.4576 1.82596 19.3224 1.85948 19.1936L2.8828 15.2626C2.19741 13.9602 1.83331 12.5058 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM12.1474 11.9166H8.02081L7.92752 11.9228C7.59195 11.9684 7.33331 12.256 7.33331 12.6041C7.33331 12.9521 7.59195 13.2398 7.92752 13.2854L8.02081 13.2916H12.1474L12.2407 13.2854C12.5763 13.2398 12.8349 12.9521 12.8349 12.6041C12.8349 12.256 12.5763 11.9684 12.2407 11.9228L12.1474 11.9166ZM13.9791 8.70825H8.02081L7.92752 8.71453C7.59195 8.76005 7.33331 9.04769 7.33331 9.39575C7.33331 9.74381 7.59195 10.0315 7.92752 10.077L8.02081 10.0833H13.9791L14.0725 10.077C14.408 10.0315 14.6666 9.74381 14.6666 9.39575C14.6666 9.04769 14.408 8.76005 14.0725 8.71453L13.9791 8.70825Z"\
                  fill="#2B2B2B" />\
              </svg>\
              <label id="easyassist-icon-path-2-label">\
                <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                <span>Chat with the Customer</span>\
              </label>\
            </a>';
        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            sidenav_menu += '<a href="javascript:void(0)" id="show-voip-modal-btn" onclick="show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
              </svg>\
              <label id="easyassist-icon-path-12-label">\
                <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                <span>Video Call</span>\
              </label>\
            </a>';
        } else if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            sidenav_menu += '<a href="javascript:void(0)" id="show-voip-modal-btn" onclick="show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-call-icon">\
                <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
              </svg>\
              <svg width="19" height="19" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-calling-icon" style="display: none;">\
                <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
              </svg>\
              <label id="easyassist-icon-path-12-label">\
                <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                <span>Audio Call</span>\
              </label>\
            </a>';
        } else if(EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {
            sidenav_menu += '<a href="javascript:void(0)" id="show-voip-modal-btn" onclick="show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
              </svg>\
              <label id="easyassist-icon-path-12-label">\
                <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                <span>Video Call</span>\
              </label>\
            </a>';
        }

        sidenav_menu += '<a href="javascript:void(0)" onclick="revoke_easyassist_edit_access();" id="revoke-edit-access-button" style="display:none;" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path id="easyassist-icon-path-3" fill-rule="evenodd" clip-rule="evenodd" d="M19.2778 2.72247L19.1376 2.59012C17.8495 1.4431 15.8741 1.48722 14.6388 2.72247L13.7492 3.61155L18.3885 8.24989L19.2778 7.36141C20.5131 6.12616 20.5572 4.15082 19.4102 2.8627L19.2778 2.72247ZM12.7775 4.58321L17.4168 9.22249L16.5978 10.0415C15.7155 9.3843 14.6489 9 13.5 9C10.4624 9 8 11.6863 8 15C8 16.0668 8.25521 17.0686 8.70266 17.9366L8.30685 18.3324C8.05304 18.5862 7.73739 18.7694 7.39111 18.8638L2.70173 20.1427C2.18852 20.2827 1.7176 19.8117 1.85756 19.2986L3.13649 14.6092C3.23093 14.2629 3.4141 13.9473 3.66791 13.6934L12.7775 4.58321ZM5.98125 10.0832L4.60625 11.4582L2.52084 11.4586C2.14114 11.4586 1.83334 11.1508 1.83334 10.7711C1.83334 10.3914 2.14114 10.0836 2.52084 10.0836L5.98125 10.0832ZM9.64795 6.41656L8.27292 7.79156L2.52084 7.79194C2.14114 7.79194 1.83334 7.48414 1.83334 7.10444C1.83334 6.72475 2.14114 6.41694 2.52084 6.41694L9.64795 6.41656ZM11.9396 4.12488L13.3146 2.74989L2.52084 2.75028C2.14114 2.75028 1.83334 3.05808 1.83334 3.43778C1.83334 3.81748 2.14114 4.12528 2.52084 4.12528L11.9396 4.12488ZM19.0833 15.0417C19.0833 12.2572 16.8261 10 14.0417 10C11.2572 10 9 12.2572 9 15.0417C9 17.8261 11.2572 20.0833 14.0417 20.0833C16.8261 20.0833 19.0833 17.8261 19.0833 15.0417ZM14.6911 15.0418L16.3134 13.4204C16.4924 13.2414 16.4924 12.9512 16.3134 12.7722C16.1344 12.5933 15.8442 12.5933 15.6652 12.7722L14.0429 14.3936L12.4214 12.7721C12.2424 12.5932 11.9522 12.5932 11.7732 12.7721C11.5942 12.9511 11.5942 13.2413 11.7732 13.4203L13.3945 15.0416L11.7732 16.6619C11.5942 16.8409 11.5942 17.1311 11.7732 17.31C11.9522 17.4891 12.2424 17.4891 12.4214 17.31L14.0427 15.6898L15.665 17.3121C15.844 17.4911 16.1342 17.4911 16.3132 17.3121C16.4922 17.1331 16.4922 16.8429 16.3132 16.6639L14.6911 15.0418Z" fill="#2B2B2B"/>\
                </svg>\
                <label id="easyassist-icon-path-3-label">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Revoke edit access</span>\
                </label>\
            </a>\
            <a href="javascript:void(0)" onclick="show_sharable_link_dialog_box();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                <svg width="22" height="22" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve"><g><g>\
                    <path id="easyassist-icon-path-4" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124\
                        c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90\
                        c0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59\
                        C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806\
                        l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90\
                        C496,372.371,455.629,332,406,332z"/>\
                </g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g></svg>\
                <label id="easyassist-icon-path-4-label">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Get Sharable link</span>\
                </label>\
            </a>\
            <a href="javascript:void(0)" onclick="show_easyassist_feedback_form();hide_easyassist_livechat_iframe();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
               <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"\>\
                 <path id="easyassist-icon-path-1"\
                   d="M11 1.83325C16.0626 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0626 20.1666 11 20.1666C5.93737 20.1666 1.83331 16.0625 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM14.2361 7.76378L14.159 7.69722C13.9198 7.51971 13.5914 7.51751 13.35 7.69064L13.2638 7.76378L11 10.0273L8.73612 7.76378L8.65901 7.69722C8.41977 7.51971 8.0914 7.51751 7.84997 7.69064L7.76384 7.76378L7.69728 7.84089C7.51977 8.08013 7.51757 8.40849 7.6907 8.64993L7.76384 8.73605L10.0274 10.9999L7.76384 13.2638L7.69728 13.3409C7.51977 13.5801 7.51757 13.9085 7.6907 14.1499L7.76384 14.2361L7.84095 14.3026C8.08019 14.4801 8.40855 14.4823 8.64999 14.3092L8.73612 14.2361L11 11.9725L13.2638 14.2361L13.341 14.3026C13.5802 14.4801 13.9086 14.4823 14.15 14.3092L14.2361 14.2361L14.3027 14.1589C14.4802 13.9197 14.4824 13.5913 14.3093 13.3499L14.2361 13.2638L11.9726 10.9999L14.2361 8.73605L14.3027 8.65895C14.4802 8.41971 14.4824 8.09134 14.3093 7.8499L14.2361 7.76378L14.159 7.69722L14.2361 7.76378Z"\
                   fill="#2B2B2B" />\
               </svg>\
               <label id="easyassist-icon-path-1-label">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>End Session</span>\
               </label>\
             </a>\
          </div>\
          <div class="easyassist-custom-nav-bar" id="easyassist-maximise-sidenav-button" style="display:none;">\
              <a href="javascript:void(0)" onclick="open_easyassist_sidenav();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                <svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">\
                  <path d="M1.93418 -5.07244e-07L6.76934 5L11.6045 -8.45407e-08L13.5386 1L6.76934 8L0.000113444 0.999999L1.93418 -5.07244e-07Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                </svg>\
                <label id="easyassist-icon-path-10-label">\
                  <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <span>Maximise</span>\
                </label>\
              </a>\
           </div>';

        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            sidenav_menu += '\
                <div id="easyassist-cobrowse-voip-container" style="display: none;">\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-on-btn" type="button" onclick="toggle_client_voice(this, true)" style="display: none;" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33597 0.721564C1.16629 0.55188 0.891186 0.551878 0.721503 0.721557C0.551819 0.891237 0.551816 1.16635 0.721496 1.33603L4.07021 4.68481V6.38759C4.07021 7.66741 5.10771 8.70491 6.38753 8.70491C6.87038 8.70491 7.31874 8.55723 7.6899 8.30457L8.35376 8.96844C7.84603 9.34868 7.2155 9.5739 6.53236 9.5739H6.2427L6.11733 9.57136C4.4957 9.50562 3.20122 8.17019 3.20122 6.53242V6.24276L3.19725 6.1838C3.16848 5.97172 2.98669 5.80826 2.76672 5.80826C2.52676 5.80826 2.33223 6.00279 2.33223 6.24276V6.53242L2.33458 6.66934C2.40339 8.66902 3.9736 10.2874 5.95304 10.4323L5.95303 11.7464L5.957 11.8053C5.98577 12.0174 6.16756 12.1809 6.38753 12.1809C6.62749 12.1809 6.82203 11.9864 6.82203 11.7464L6.82259 10.4323C7.63306 10.3728 8.3749 10.0663 8.97313 9.58783L11.439 12.0537C11.6086 12.2234 11.8837 12.2234 12.0534 12.0537C12.2231 11.884 12.2231 11.6089 12.0534 11.4392L1.33597 0.721564ZM7.05738 7.67204C6.85706 7.77672 6.62921 7.83591 6.38753 7.83591C5.58764 7.83591 4.93921 7.18748 4.93921 6.38759V5.55382L7.05738 7.67204Z" fill="white"/>\
                          <path d="M7.83585 2.91162V5.9926L8.66436 6.82113C8.69094 6.68069 8.70484 6.53576 8.70484 6.38759V2.91162C8.70484 1.6318 7.66735 0.594299 6.38753 0.594299C5.31701 0.594299 4.41603 1.32021 4.14997 2.30665L4.93921 3.0959V2.91162C4.93921 2.11173 5.58764 1.46329 6.38753 1.46329C7.18742 1.46329 7.83585 2.11173 7.83585 2.91162Z" fill="white"/>\
                          <path d="M9.39781 7.55459L10.0617 8.21848C10.306 7.70796 10.4428 7.13617 10.4428 6.53242V6.24276L10.4389 6.1838C10.4101 5.97172 10.2283 5.80826 10.0083 5.80826C9.76837 5.80826 9.57384 6.00279 9.57384 6.24276V6.53242L9.5713 6.65779C9.55859 6.97128 9.49843 7.27254 9.39781 7.55459Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-5-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn on microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-off-btn" type="button" onclick="toggle_client_voice(this, false)" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M4.5 0C3.10203 0 1.96875 1.00736 1.96875 2.25001V6.25003C1.96875 7.49268 3.10203 8.50004 4.5 8.50004C5.89797 8.50004 7.03125 7.49268 7.03125 6.25003V2.25001C7.03125 1.00736 5.89797 0 4.5 0ZM2.8125 2.25001C2.8125 1.42158 3.56802 0.750004 4.5 0.750004C5.43198 0.750004 6.1875 1.42158 6.1875 2.25001V6.25003C6.1875 7.07846 5.43198 7.75004 4.5 7.75004C3.56802 7.75004 2.8125 7.07846 2.8125 6.25003V2.25001Z" fill="white"/>\
                          <path d="M0.84375 5.87527C0.84375 5.66817 0.65487 5.50027 0.421875 5.50027C0.18888 5.50027 0 5.66838 0 5.87548V6.24999C0 8.33268 1.79067 10.0436 4.07813 10.2327V11.625C4.07813 11.8321 4.26701 12 4.5 12C4.733 12 4.92188 11.8321 4.92188 11.625V10.2327C7.20934 10.0436 9 8.33268 9 6.24999V5.87528C9 5.66817 8.81112 5.50028 8.57812 5.50028C8.34513 5.50028 8.15625 5.6683 8.15625 5.8754V6.24999C8.15625 8.04492 6.51929 9.50001 4.5 9.50001C2.48071 9.50001 0.84375 8.04471 0.84375 6.24978V5.87527Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-6-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn off microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-end-btn" type="button" onclick="end_cobrowse_video_meet()" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="13" height="5" viewBox="0 0 13 5" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M12.1528 3.3789L12.0384 3.97941C11.9313 4.54213 11.4055 4.92001 10.8098 4.86244L9.62424 4.74788C9.10762 4.69796 8.66745 4.33102 8.53601 3.84069L8.17026 2.47623C7.62889 2.25423 7.03222 2.15276 6.38025 2.17182C5.72828 2.19088 5.12184 2.32752 4.56093 2.58175L4.33437 3.85902C4.24849 4.34316 3.84901 4.70429 3.34307 4.75516L2.16441 4.87366C1.5763 4.93279 1.01242 4.55857 0.845229 3.99819L0.66606 3.39764C0.487718 2.79987 0.64687 2.17079 1.08386 1.74619C2.11552 0.743789 3.83556 0.241029 6.24398 0.237899C8.6559 0.234793 10.4295 0.734491 11.5648 1.73701C12.0424 2.15885 12.2661 2.78345 12.1528 3.3789Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-7-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>End Call</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn"  id="easyassist-client-meeting-video-on-btn" type="button" onclick="toggle_client_video(this, true)" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33573 1.06458C1.16605 0.894898 0.890942 0.894895 0.721258 1.06457C0.551575 1.23425 0.551572 1.50936 0.721252 1.67905L1.62904 2.58685C1.01503 2.89701 0.593994 3.53357 0.593994 4.26846V9.19276C0.593994 10.2326 1.43696 11.0756 2.47681 11.0756H7.40111C8.13596 11.0756 8.77249 10.6546 9.08267 10.0406L11.4387 12.3967C11.6084 12.5664 11.8835 12.5664 12.0532 12.3967C12.2229 12.227 12.2229 11.9519 12.0532 11.7823L1.33573 1.06458ZM8.40133 9.35927C8.32189 9.83997 7.90431 10.2066 7.40111 10.2066H2.47681C1.91689 10.2066 1.46299 9.75268 1.46299 9.19276V4.26846C1.46299 3.76522 1.82965 3.34761 2.3104 3.26823L8.40133 9.35927Z" fill="white"/>\
                          <path d="M8.41494 6.91496V4.26846C8.41494 3.70854 7.96103 3.25463 7.40111 3.25463H4.75468L3.88571 2.38564H7.40111C8.44096 2.38564 9.28393 3.22861 9.28393 4.26846V4.36868L11.5224 3.0258C11.812 2.85192 12.1806 3.06052 12.1806 3.39831V10.0617C12.1806 10.2364 12.0821 10.3765 11.9469 10.447L11.3116 9.81166V4.16598L9.28393 5.38338V7.78397L8.41494 6.91496Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-8-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn on camera</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn"  id="easyassist-client-meeting-video-off-btn" type="button" onclick="toggle_client_video(this, false)" style="display: none;" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M8.225 0C9.48145 0 10.5 1.06705 10.5 2.38333V2.5102L13.2048 0.810331C13.5547 0.590233 14 0.854285 14 1.28187V9.71667C14 10.1442 13.5548 10.4082 13.2049 10.1883L10.5 8.48833V8.61667C10.5 9.93295 9.48145 11 8.225 11H2.275C1.01855 11 0 9.93295 0 8.61667V2.38333C0 1.06705 1.01855 0 2.275 0H8.225ZM8.225 1.1H2.275C1.59845 1.1 1.05 1.67457 1.05 2.38333V8.61667C1.05 9.32543 1.59845 9.9 2.275 9.9H8.225C8.90155 9.9 9.45 9.32543 9.45 8.61667V2.38333C9.45 1.67457 8.90155 1.1 8.225 1.1ZM12.95 2.25361L10.5 3.79463V7.20526L12.95 8.74526V2.25361Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-9-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn off camera</span>\
                       </label>\
                    </button>\
                    <button onclick="toggle_meeting_iframe_visibility();" class="easyassist-show-cobrowse-meeting-btn">\
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M10 10L5.9375 10L7.5 8.4375L5.625 6.5625L6.5625 5.625L8.4375 7.5L10 5.9375L10 10ZM3.4375 4.375L1.5625 2.5L-1.77578e-07 4.0625L0 -4.37114e-07L4.0625 -2.59536e-07L2.5 1.5625L4.375 3.4375L3.4375 4.375Z" fill="#B4B4B4"/>\
                      </svg>\
                    </button>\
                    <div id="easyassist-cobrowse-meeting-iframe-container" style="display: none;">\
                      <iframe style="width: 100%; height: 100%;" allow="camera *;microphone *">\
                      </iframe>\
                      <div class="easyassist-meeting-video-container">\
                        <video autoplay="true" id="easyassist-meeting-video-element">\
                        </video>\
                      </div>\
                    </div>\
                    <div class="easyassist-gy-loader easyassist-loader-container" id="easyassist-voip-loader" style="display: none;">\
                      <div>\
                        <div class="easyassist-line" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></div>\
                        <div class="easyassist-line" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></div>\
                        <div class="easyassist-line" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></div>\
                      </div>\
                    </div>\
                </div>';
        } else if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            sidenav_menu += '\
                <div id="easyassist-cobrowse-voip-container" style="display: none;">\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-on-btn" type="button" onclick="toggle_client_voice(this, true)" style="display: none;" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33597 0.721564C1.16629 0.55188 0.891186 0.551878 0.721503 0.721557C0.551819 0.891237 0.551816 1.16635 0.721496 1.33603L4.07021 4.68481V6.38759C4.07021 7.66741 5.10771 8.70491 6.38753 8.70491C6.87038 8.70491 7.31874 8.55723 7.6899 8.30457L8.35376 8.96844C7.84603 9.34868 7.2155 9.5739 6.53236 9.5739H6.2427L6.11733 9.57136C4.4957 9.50562 3.20122 8.17019 3.20122 6.53242V6.24276L3.19725 6.1838C3.16848 5.97172 2.98669 5.80826 2.76672 5.80826C2.52676 5.80826 2.33223 6.00279 2.33223 6.24276V6.53242L2.33458 6.66934C2.40339 8.66902 3.9736 10.2874 5.95304 10.4323L5.95303 11.7464L5.957 11.8053C5.98577 12.0174 6.16756 12.1809 6.38753 12.1809C6.62749 12.1809 6.82203 11.9864 6.82203 11.7464L6.82259 10.4323C7.63306 10.3728 8.3749 10.0663 8.97313 9.58783L11.439 12.0537C11.6086 12.2234 11.8837 12.2234 12.0534 12.0537C12.2231 11.884 12.2231 11.6089 12.0534 11.4392L1.33597 0.721564ZM7.05738 7.67204C6.85706 7.77672 6.62921 7.83591 6.38753 7.83591C5.58764 7.83591 4.93921 7.18748 4.93921 6.38759V5.55382L7.05738 7.67204Z" fill="white"/>\
                          <path d="M7.83585 2.91162V5.9926L8.66436 6.82113C8.69094 6.68069 8.70484 6.53576 8.70484 6.38759V2.91162C8.70484 1.6318 7.66735 0.594299 6.38753 0.594299C5.31701 0.594299 4.41603 1.32021 4.14997 2.30665L4.93921 3.0959V2.91162C4.93921 2.11173 5.58764 1.46329 6.38753 1.46329C7.18742 1.46329 7.83585 2.11173 7.83585 2.91162Z" fill="white"/>\
                          <path d="M9.39781 7.55459L10.0617 8.21848C10.306 7.70796 10.4428 7.13617 10.4428 6.53242V6.24276L10.4389 6.1838C10.4101 5.97172 10.2283 5.80826 10.0083 5.80826C9.76837 5.80826 9.57384 6.00279 9.57384 6.24276V6.53242L9.5713 6.65779C9.55859 6.97128 9.49843 7.27254 9.39781 7.55459Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-5-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn on microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-off-btn" type="button" onclick="toggle_client_voice(this, false)" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M4.5 0C3.10203 0 1.96875 1.00736 1.96875 2.25001V6.25003C1.96875 7.49268 3.10203 8.50004 4.5 8.50004C5.89797 8.50004 7.03125 7.49268 7.03125 6.25003V2.25001C7.03125 1.00736 5.89797 0 4.5 0ZM2.8125 2.25001C2.8125 1.42158 3.56802 0.750004 4.5 0.750004C5.43198 0.750004 6.1875 1.42158 6.1875 2.25001V6.25003C6.1875 7.07846 5.43198 7.75004 4.5 7.75004C3.56802 7.75004 2.8125 7.07846 2.8125 6.25003V2.25001Z" fill="white"/>\
                          <path d="M0.84375 5.87527C0.84375 5.66817 0.65487 5.50027 0.421875 5.50027C0.18888 5.50027 0 5.66838 0 5.87548V6.24999C0 8.33268 1.79067 10.0436 4.07813 10.2327V11.625C4.07813 11.8321 4.26701 12 4.5 12C4.733 12 4.92188 11.8321 4.92188 11.625V10.2327C7.20934 10.0436 9 8.33268 9 6.24999V5.87528C9 5.66817 8.81112 5.50028 8.57812 5.50028C8.34513 5.50028 8.15625 5.6683 8.15625 5.8754V6.24999C8.15625 8.04492 6.51929 9.50001 4.5 9.50001C2.48071 9.50001 0.84375 8.04471 0.84375 6.24978V5.87527Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-6-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn off microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-end-btn" type="button" onclick="end_cobrowse_video_meet()" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="13" height="5" viewBox="0 0 13 5" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M12.1528 3.3789L12.0384 3.97941C11.9313 4.54213 11.4055 4.92001 10.8098 4.86244L9.62424 4.74788C9.10762 4.69796 8.66745 4.33102 8.53601 3.84069L8.17026 2.47623C7.62889 2.25423 7.03222 2.15276 6.38025 2.17182C5.72828 2.19088 5.12184 2.32752 4.56093 2.58175L4.33437 3.85902C4.24849 4.34316 3.84901 4.70429 3.34307 4.75516L2.16441 4.87366C1.5763 4.93279 1.01242 4.55857 0.845229 3.99819L0.66606 3.39764C0.487718 2.79987 0.64687 2.17079 1.08386 1.74619C2.11552 0.743789 3.83556 0.241029 6.24398 0.237899C8.6559 0.234793 10.4295 0.734491 11.5648 1.73701C12.0424 2.15885 12.2661 2.78345 12.1528 3.3789Z" fill="white"/>\
                      </svg>\
                      <label id="easyassist-icon-path-7-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>End Call</span>\
                       </label>\
                    </button>\
                    <div id="easyassist-cobrowse-meeting-iframe-container" style="display: none;">\
                      <iframe style="width: 100%; height: 100%;" allow="camera *;microphone *">\
                      </iframe>\
                    </div>\
                    <div class="easyassist-gy-loader easyassist-loader-container" id="easyassist-voip-loader" style="display: none;">\
                      <div>\
                        <div class="easyassist-line" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></div>\
                        <div class="easyassist-line" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></div>\
                        <div class="easyassist-line" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></div>\
                      </div>\
                    </div>\
                </div>';
        }
        sidenav_menu += '</div>';
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sidenav_menu);
        document.getElementById("easyassist-icon-path-1").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-2").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-3").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-4").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-1-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-2-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-3-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-4-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        if(document.getElementById("easyassist-icon-path-5-label")) {
            document.getElementById("easyassist-icon-path-5-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
        if(document.getElementById("easyassist-icon-path-6-label")) {
            document.getElementById("easyassist-icon-path-6-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
        if(document.getElementById("easyassist-icon-path-7-label")) {
            document.getElementById("easyassist-icon-path-7-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
        if(document.getElementById("easyassist-icon-path-8-label")) {
            document.getElementById("easyassist-icon-path-8-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
        if(document.getElementById("easyassist-icon-path-9-label")) {
            document.getElementById("easyassist-icon-path-9-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }

        if(document.getElementById("easyassist-icon-path-0-label")) {
            document.getElementById("easyassist-icon-path-0-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
        if(document.getElementById("easyassist-icon-path-10-label")) {
            document.getElementById("easyassist-icon-path-10-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
        if(document.getElementById("easyassist-icon-path-12-label")) {
            document.getElementById("easyassist-icon-path-12-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }
    }

    function show_floating_sidenav_menu() {
        document.getElementById("easyassist-sidenav-menu-id").style.display = "block";
        if (get_easyassist_cookie("easyassist_edit_access") == "true") {
            document.getElementById("revoke-edit-access-button").style.display = "flex";
        } else {
            document.getElementById("revoke-edit-access-button").style.display = "none";
        }

        show_cobrowse_meeting_option();
        create_easyassist_close_nav_timeout();
    }

    function close_easyassist_sidenav() {
        try {
            document.getElementById("easyassist-sidenav-submenu-id").style.display = "none";
            document.getElementById("easyassist-maximise-sidenav-button").style.display = "flex";
        } catch(err) {}
    }

    function open_easyassist_sidenav() {
        try {
            document.getElementById("easyassist-maximise-sidenav-button").style.display = "none";
            document.getElementById("easyassist-sidenav-submenu-id").style.display = "flex";
        } catch(err) {}
    }

    function on_easyassist_client_mouse_over_nav_bar() {
        clear_easyassist_close_nav_timeout();
    }

    function on_easyassist_mouse_out_nav_bar() { 
        create_easyassist_close_nav_timeout();
    }

    function create_easyassist_close_nav_timeout(){
        if(easyassist_close_nav_timeout == null){
            easyassist_close_nav_timeout = setTimeout(close_easyassist_sidenav, 15*1000);
        }
    }

    function clear_easyassist_close_nav_timeout(){
        clearTimeout(easyassist_close_nav_timeout);
        easyassist_close_nav_timeout = null;
    }

    function hide_floating_sidenav_menu() {
        document.getElementById("easyassist-sidenav-menu-id").style.display = "none";
    }

    function hide_floating_sidenav_easyassist_button() {
        document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "none";
    }

    function show_easyassist_request_edit_access_form() {
        hide_easyassist_livechat_iframe();
        document.getElementById("easyassist-co-browsing-request-edit-access").style.display = "flex"
    }

    function hide_easyassist_request_edit_access_form() {
        document.getElementById("easyassist-co-browsing-request-edit-access").style.display = "none";
    }

    function show_floating_sidenav_easyassist_button() {
        easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == undefined || EASYASSIST_SESSION_ID == null) {
            document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
        }
    }

    function add_easyassist_payment_consent_modal() {

        consent_element = document.querySelector("#easyassist-co-browsing-payment-consent-modal");
        if (consent_element != undefined && consent_element != null) {
            consent_element.remove();
        }

        const request_modal_html = '<div id="easyassist-co-browsing-payment-consent-modal" style="display: none;">\
      <div id="easyassist-co-browsing-modal-content" style="padding: 2em; text-align: center;">\
      <h4>Co-browsing Alert*</h4><hr>\
      <p style="text-align: justify;">Upon clicking on Pay button, you will be directed to payment gateway page to complete your transaction. For your security reasons, please note your co-browsing session will be paused during this session and our sales agent will not be able to view your details.</p><br>\
      <div style="display: flex;justify-content: center;">\
          <button onclick="hide_payment_consent_modal(this)" style="background-color: #1b5e20; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em; border-style: none; float: right; margin-right: 5%;outline:none;">Ok</button>\
      </div>\
      </div>\
    </div>';
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', request_modal_html);
    }

    function show_sharable_link_dialog_box(){
        var share_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client/" + get_easyassist_cookie("easyassist_session_id");
        document.getElementById("easychat_share_link_Model-content_link_wrapper").value = share_url;
        document.getElementById("easychat_share_link_Model").style.display = "block";
    }

    function hide_payment_consent_modal(element) {
        document.getElementById("easyassist-co-browsing-payment-consent-modal").style.display = "none";
    }

    function show_payment_consent_modal(element) {
        document.getElementById("easyassist-co-browsing-payment-consent-modal").style.display = "block";
    }

    function auto_fetch_details(el) {
        var auto_fetch_fields = EASYASSIST_COBROWSE_META.auto_fetch_fields;
        for (var index = 0; index < auto_fetch_fields.length; index++) {
            var fetch_element = document.querySelectorAll('[' + auto_fetch_fields[index].fetch_field_key + '="' + auto_fetch_fields[index].fetch_field_value + '"]');
            var modal_element = document.querySelectorAll('[' + auto_fetch_fields[index].modal_field_key + '="' + auto_fetch_fields[index].modal_field_value + '"]');
            if (fetch_element != null && modal_element != null && fetch_element.length > 0 && modal_element.length > 0) {
                fetch_element = fetch_element[0];
                modal_element = modal_element[0];
                modal_element.value = fetch_element.value;
            }
        }
    }

    function show_easyassist_browsing_modal(el) {
        document.getElementById("modal-cobrowse-connect-error").innerHTML = "";

        if(document.getElementById("modal-cobrowse-customer-name-error")) {
            document.getElementById("modal-cobrowse-customer-name-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-name-error").innerHTML = "";
        }
        if(document.getElementById("modal-cobrowse-customer-language-error")) {
            document.getElementById("modal-cobrowse-customer-language-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-language-error").innerHTML = "";
        }
        if(document.getElementById("modal-cobrowse-virtual-agent-code-error")) {
            document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = "";
        }
        if(document.getElementById("modal-cobrowse-customer-number-error")) {
            document.getElementById("modal-cobrowse-customer-number-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-number-error").innerHTML = "";
        }

        document.getElementById("easyassist-client-name").value = "";
        if (document.getElementById("easyassist-client-mobile-number") != null) {
            document.getElementById("easyassist-client-mobile-number").value = "";
        }

        if (document.getElementById("easyassist-client-agent-virtual-code") != null) {
            document.getElementById("easyassist-client-agent-virtual-code").value = "";
        }

        auto_fetch_details();
        document.getElementById("easyassist-co-browsing-modal-id").style.display = "flex";
        hide_floating_sidenav_easyassist_button();
    }

    function close_easyassist_browsing_modal(el) {
        document.getElementById("easyassist-co-browsing-modal-id").style.display = "none";
        show_floating_sidenav_easyassist_button();
    }

    function show_connection_easyassist_modal(){
        document.getElementById("easyassist-conection-modal-id").style.display = "flex";
        setTimeout(function(){
            document.getElementById("easyassist-conection-modal-id").style.display = "none";
        },10000);
    }

    function close_connection_modal(el) {
        document.getElementById("easyassist-conection-modal-id").style.display = "none";
    }

    function show_easyassist_product_category_modal() {
        document.getElementById("easyassist-product-category-modal-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
        document.getElementById("easyassist-product-category-modal-error").innerHTML = "";
        document.getElementById("easyassist-product-category-modal-id").style.display = "flex";
        hide_floating_sidenav_easyassist_button();
        document.getElementById("easyassist-co-browsing-modal-id").style.display = "none";
    }

    function close_easyassist_product_category_modal() {
        document.getElementById("easyassist-product-category-modal-id").style.display = "none";
        show_floating_sidenav_easyassist_button();
    }

    function accept_location_request(pos) {
        latitude = pos.coords.latitude;
        longitude = pos.coords.longitude;
    }

    function cancel_location_request(pos) {
        latitude = null;
        longitude = null;
    }

    function set_easyassist_product_category() {
        window.EASYASSIST_PRODUCT_CATEGORY = "";
        var selected_product_category = "None";
        selected_product_category = document.getElementById("easyassist-inline-form-input-product-category").value;

        if (selected_product_category == "None" || selected_product_category == "") {
            document.getElementById("easyassist-product-category-modal-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            document.getElementById("easyassist-product-category-modal-error").innerHTML = "Please select a category";
            return;
        }
        window.EASYASSIST_PRODUCT_CATEGORY = selected_product_category;
        close_easyassist_product_category_modal();
        show_easyassist_browsing_modal();
    }

    function connect_with_easyassist_customer(event) {

        document.getElementById("modal-cobrowse-connect-error").innerHTML = "";

        if(document.getElementById("modal-cobrowse-customer-name-error")) {
            document.getElementById("modal-cobrowse-customer-name-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-name-error").innerHTML = "";
        }

        if(document.getElementById("modal-cobrowse-customer-language-error")) {
            document.getElementById("modal-cobrowse-customer-language-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-language-error").innerHTML = "";
        }

        if(document.getElementById("modal-cobrowse-virtual-agent-code-error")) {
            document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = "";
        }

        if(document.getElementById("modal-cobrowse-customer-number-error")) {
            document.getElementById("modal-cobrowse-customer-number-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-number-error").innerHTML = "";
        }

        var full_name = document.getElementById("easyassist-client-name").value;
        var mobile_number = "None";
        var regName = /^[a-zA-Z]+[a-zA-Z ]+$/;
        var regMob = /^[6-9]{1}[0-9]{9}$/;

        if (!regName.test(full_name)) {
            document.getElementById("modal-cobrowse-customer-name-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-name-error").innerHTML = "Please enter valid name";
            return;
        }

        if (EASYASSIST_COBROWSE_META.ask_client_mobile == true || EASYASSIST_COBROWSE_META.ask_client_mobile == "true" || EASYASSIST_COBROWSE_META.ask_client_mobile == "True") {
            mobile_number = document.getElementById("easyassist-client-mobile-number").value;
            if (EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == true || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "true" || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "True") {
                if (!regMob.test(mobile_number)) {
                    document.getElementById("modal-cobrowse-customer-number-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("modal-cobrowse-customer-number-error").innerHTML = "Please enter valid 10-digit mobile number";
                    return;
                }
            } else {
                if (mobile_number.trim() != "" && !regMob.test(mobile_number)) {
                    document.getElementById("modal-cobrowse-customer-number-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("modal-cobrowse-customer-number-error").innerHTML = "Please enter valid 10-digit mobile number";
                    return;
                }
            }
        }

        var virtual_agent_code = document.getElementById("easyassist-client-agent-virtual-code").value;
        if (virtual_agent_code.trim() == "") {
            document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = "Please enter valid agent code";
            return;            
        }

        var title = window.location.href;
        if (document.querySelector("title") != null) {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        var url = window.location.href;
        var request_id = easyassist_request_id();

        json_string = JSON.stringify({
            "request_id": request_id,
            "name": full_name,
            "mobile_number": mobile_number,
            "virtual_agent_code": virtual_agent_code,
            "active_url": window.location.href,
            "meta_data": {
                "product_details": {
                    "title": title,
                    "description": description,
                    "url": url
                }
            }
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/initialize/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {

                    close_easyassist_browsing_modal();

                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                    document.getElementById("easyassist-co-browsing-connect-button").disabled = false;

                    var share_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client/" + response.session_id;
                    var message = share_url;
                    document.getElementById("easychat_share_link_Model-content_link_wrapper").value = message;
                    document.getElementById("easychat_share_link_Model").style.display = "block";

                    show_floating_sidenav_menu();

                    
                } else if (response.status == 101) {

                    document.getElementById("modal-cobrowse-connect-error").innerHTML = "Please enter valid agent code"; 

                } else if (response.status == 103) {

                    document.getElementById("modal-cobrowse-connect-error").innerHTML = "Please enter code shared by our agent";

                } else{

                    console.error(response);

                }
            } else if (this.readyState == 4) {
                var description = "Initiate lead API (/easy-assist/initialize/) failed with status code " + this.status.toString();
                document.getElementById("easyassist-co-browsing-connect-button").disabled = false;
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
    }

    // NOTE: Not to be invoked directly. When the screenshot loads, it should scroll
    // to the same x,y location of this page.
    function add_on_page_load_() {
        window.addEventListener('DOMContentLoaded', function(e) {
            var scrollX = document.documentElement.dataset.scrollX || 0;
            var scrollY = document.documentElement.dataset.scrollY || 0;
            scrollX = parseInt(scrollX);
            scrollY = parseInt(scrollY);
        });
    }

    function set_easyassist_cookie(cookiename, cookievalue) {

        var domain = window.location.hostname;

        if (window.location.protocol == "https:") {
            document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;domain=" + domain + ";secure";
        } else {
            document.cookie = cookiename + "=" + cookievalue + ";max-age=86400" + ";path=/;";
        }
    }

    function get_easyassist_cookie(cookiename) {
        var matches = document.cookie.match(new RegExp(
            "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
        ));
        return matches ? matches[1] : undefined;
    }

    function delete_easyassist_cookie(cookiename) {

        var domain = window.location.hostname;

        if (window.location.protocol == "https:") {
            document.cookie = cookiename + "=;path=/;domain=" + domain + ";secure;expires = Thu, 01 Jan 1970 00:00:00 GMT";
        } else {
            document.cookie = cookiename + "=;path=/;expires = Thu, 01 Jan 1970 00:00:00 GMT";
        }
    }

    function show_easyassist_toast(message) {
        var x = document.getElementById("easyassist-snackbar");
        x.innerHTML = message;
        x.className = "show";
        setTimeout(function() {
            x.className = x.className.replace("show", "");
        }, EASYASSIST_COBROWSE_META.toast_timeout);
    }

    function copy_text_to_clipboard_sharable_link_easyassist() {
        var copyText = document.getElementById("easychat_share_link_Model-content_link_wrapper");
        el = document.createElement('textarea');
        el.value = copyText.value;
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
        show_easyassist_toast("Sharable link has been copied");
    }

    function ascii_to_hexa(str) {

        var temp_arr = [];
        for (var n = 0, l = str.length; n < l; n++) {
            var hex = Number(str.charCodeAt(n)).toString(16);
            temp_arr.push(hex);
        }
        return temp_arr.join('');
    }

    function check_new_lead_data(title, description, url, easyassist_sync_data) {

        var meta_data = {
            "product_details": {
                "title": title,
                "description": description,
                "url": url
            },
            "easyassist_sync_data": easyassist_sync_data
        }

        old_encrypted_meta_data = ascii_to_hexa(JSON.stringify(meta_data));
        var encrypted_meta_data = get_easyassist_cookie("encrypted_meta_data");
        return encrypted_meta_data == old_encrypted_meta_data
    }

    function update_meta_data(title, description, url, easyassist_sync_data) {

        var meta_data = {
            "product_details": {
                "title": title,
                "description": description,
                "url": url
            },
            "easyassist_sync_data": easyassist_sync_data
        }

        encrypted_meta_data = ascii_to_hexa(JSON.stringify(meta_data));
        set_easyassist_cookie("encrypted_meta_data", encrypted_meta_data);
    }

    function sync_client_lead_data_at_server() {

        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            easyassist_session_id = "None";
        }

        var title = window.location.href;
        if (document.querySelector("title") != null) {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        var url = window.location.href;

        primary_sync_elements = document.querySelectorAll("[easyassist-sync-element=\"primary\"]");
        if (primary_sync_elements.length <= 0) {
            return;
        }

        primary_value_list = [];

        for (var index = 0; index < primary_sync_elements.length; index++) {

            primary_value = primary_sync_elements[index].value.trim();

            if (primary_value != "") {

                primary_value_list.push(primary_value)
            }
        }
        if (primary_value_list.length <= 0) {
            return;
        }

        easyassist_sync_elements = document.querySelectorAll("[easyassist-sync-element]");
        if (easyassist_sync_elements.length == 0) {
            return;
        }

        var easyassist_sync_data = [];
        for (var index = 0; index < easyassist_sync_elements.length; index++) {
            easyassist_sync_data.push({
                "value": easyassist_sync_elements[index].value,
                "sync_type": easyassist_sync_elements[index].getAttribute("easyassist-sync-element"),
                "name": easyassist_sync_elements[index].getAttribute("easyassist-sync-element-label")
            });
        }

        if (check_new_lead_data(title, description, url, easyassist_sync_data) && lead_capture_initialted) {

            return;
        }

        lead_capture_initialted = true;

        update_meta_data(title, description, url, easyassist_sync_data);

        var request_id = easyassist_request_id();

        json_string = JSON.stringify({
            "request_id": request_id,
            "primary_value_list": primary_value_list,
            "session_id": easyassist_session_id,
            "meta_data": {
                "product_details": {
                    "title": title,
                    "description": description,
                    "url": url
                },
                "easyassist_sync_data": easyassist_sync_data
            }
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/capture-lead/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    if (easyassist_session_id == "None") {
                        set_easyassist_cookie("easyassist_session_id", response.session_id);
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }
                } else {
                    console.error(response);
                }
            } else if (this.readyState == 4) {
                var description = "Capture lead API (/easy-assist/capture-lead/) failed with status code " + this.status.toString();
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
    }

    // function detect_value_change_event() {
    //     form_elements = document.querySelectorAll("[easyassist-sync-element]");
    //     for (var index = 0; index < form_elements.length; index++) {
    //         form_elements[index].addEventListener("focusout", sync_client_lead_data_at_server, true);
    //     }
    // }

    function add_easyassist_search_field_tag() {
        for (var search_tag in search_html_field) {
            form_elements = document.querySelectorAll(search_tag);
            for (var element_index = 0; element_index < form_elements.length; element_index++) {
                var element_id = form_elements[element_index].getAttribute("id");
                var element_name = form_elements[element_index].getAttribute("name");
                var element_react_id = form_elements[element_index].getAttribute("data-reactid");

                if (form_elements[element_index].type == "hidden") {
                    continue;
                }
                for (var search_index = 0; search_index < search_html_field[search_tag].length; search_index++) {
                    var search_element_id = search_html_field[search_tag][search_index]["id"];
                    var search_element_name = search_html_field[search_tag][search_index]["name"];
                    var search_element_primary = search_html_field[search_tag][search_index]["type"];
                    var search_element_react_id = search_html_field[search_tag][search_index]["data-reactid"];
                    var search_element_label = search_html_field[search_tag][search_index]["label"];
                    var search_element_key = search_html_field[search_tag][search_index]["key"];
                    var search_element_value = search_html_field[search_tag][search_index]["value"];

                    var element_value = form_elements[element_index].getAttribute(search_element_key);

                    if (element_value == search_element_value && search_element_value != undefined && search_element_value != null) {
                        form_elements[element_index].setAttribute("easyassist-sync-element", search_element_primary);
                        form_elements[element_index].setAttribute("easyassist-sync-element-label", search_element_label);
                    } else if (element_id == search_element_id && search_element_id != undefined && search_element_id != null) {
                        form_elements[element_index].setAttribute("easyassist-sync-element", search_element_primary);
                        form_elements[element_index].setAttribute("easyassist-sync-element-label", search_element_label);
                    } else if (element_name == search_element_name && search_element_name != undefined && search_element_name != null) {
                        form_elements[element_index].setAttribute("easyassist-sync-element", search_element_primary);
                        form_elements[element_index].setAttribute("easyassist-sync-element-label", search_element_label);
                    } else if (element_react_id == search_element_react_id && search_element_react_id != undefined && search_element_react_id != null) {
                        form_elements[element_index].setAttribute("easyassist-sync-element", search_element_primary);
                        form_elements[element_index].setAttribute("easyassist-sync-element-label", search_element_label);
                    }
                }
            }
        }

        sync_client_lead_data_at_server();
    }

    function count_hidden_element_in_document(tag_name_list) {
        var count = 0;
        for (var index = 0; index < tag_name_list.length; index++) {
            element_list = document.getElementsByTagName(tag_name_list[index]);
            for (var index_e = 0; index_e < element_list.length; index_e++) {
                var visible = "true";
                if (element_list[index_e].offsetParent == null) {
                    visible = "false";
                }
                if (element_list[index_e].getAttribute("ea_visible") != visible) {
                    count += 1;
                }
                element_list[index_e].setAttribute("ea_visible", visible);
            }
        }
        return count;
    }

    function get_easyassist_session_details() {
        return {
            "hostname": window.location.hostname,
            "easyassist_session_id": get_easyassist_cookie("easyassist_session_id"),
            "easyassist_customer_id": get_easyassist_cookie("easyassist_customer_id"),
            "easyassist_agent_connected": get_easyassist_cookie("easyassist_agent_connected"),
            "easyassist_cobrowsing_allowed": get_easyassist_cookie("easyassist_cobrowsing_allowed"),
            "easyassist_edit_access": get_easyassist_cookie("easyassist_edit_access")
        };
    }

    function update_easyassist_url_history() {
        return;
        var eacSession = get_easyassist_session_details();
        if (eacSession != null) {
            var src = document.getElementById("easyassist-iframe").src;
            eacSession = btoa(JSON.stringify(get_easyassist_session_details()));
            src = src.split("&")[0];
            src += "&eacSession=" + eacSession;
            document.getElementById("easyassist-iframe").src = src;
        }
    }

    function create_easyassist_hidden_iframe() {
        no_script = document.createElement("noscript");
        iframe = document.createElement("iframe");
        iframe.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/sales-ai.html?id=" + EASYASSIST_COBROWSE_META.access_token;
        iframe.id = "easyassist-iframe";
        iframe.style.display = "none";
        iframe.style.visibility = "hidden";
        iframe.height = "0";
        iframe.width = "0";
        no_script.appendChild(iframe);
        document.querySelector("body").appendChild(no_script);
    }

    function create_easyassist_cobrowsing_lead(primary_value, primary_name) {

        var easyassist_sync_data = [];

        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            easyassist_session_id = "None";
        }

        var title = window.location.href;
        if (document.querySelector("title") != null) {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        var url = window.location.href;

        easyassist_sync_data.push({
            "value": primary_value,
            "sync_type": "primary",
            "name": primary_name
        });

        var request_id = easyassist_request_id();

        json_string = JSON.stringify({
            "request_id": request_id,
            "primary_value_list": [primary_value],
            "session_id": easyassist_session_id,
            "meta_data": {
                "product_details": {
                    "title": title,
                    "description": description,
                    "url": url
                },
                "easyassist_sync_data": easyassist_sync_data
            }
        });

        encrypted_data = easyassist_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/capture-lead/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    if (easyassist_session_id == "None") {
                        set_easyassist_cookie("easyassist_session_id", response.session_id);
                        window.EASYASSIST_COBROWSE_META.is_lead_generated = true;
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }
                } else {
                    console.error(response);
                }
            } else if (this.readyState == 4) {
                var description = "Capture lead API (/easy-assist/capture-lead/) failed with status code " + this.status.toString();
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
    }


    function connect_with_easyassist_customer_with_details(full_name, mobile_number) {

        var title = window.location.href;
        if (document.querySelector("title") != null) {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        var url = window.location.href;

        json_string = JSON.stringify({
            "name": full_name,
            "mobile_number": mobile_number,
            "active_url": window.location.href,
            "meta_data": {
                "product_details": {
                    "title": title,
                    "description": description,
                    "url": url
                }
            }
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/initialize/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    close_easyassist_browsing_modal();
                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    show_easyassist_toast("Thank you, we have captured your details. We will notify you as soon as our agent connects with you.");
                } else {
                    console.error(response);
                }
            } else if (this.readyState == 4) {
                var description = "Initiate lead API (/easy-assist/capture-lead/) failed with status code " + this.status.toString();
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
    }

    function easyassist_obfuscate(str, masking_type) {

        if (EASYASSIST_COBROWSE_META.allow_agent_to_customer_cobrowsing) {
            return str;
        }

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

    function save_easyassist_system_audit_trail(category, description) {

        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            easyassist_session_id = "None";
        }

        if (category.trim() == "") {
            return;
        }

        if (description.trim() == "") {
            return;
        }

        json_string = JSON.stringify({
            "category": category,
            "description": description,
            "session_id": easyassist_session_id,
            "access_token": window.EASYASSIST_COBROWSE_META.access_token
        });

        encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/save-system-audit/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
            }
        }
        xhttp.send(params);
    }

    function create_easyassist_livechat_iframe() {
        iframe = document.createElement("iframe");
        iframe.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/sales-ai/client/livechat/?access_token=" + EASYASSIST_COBROWSE_META.access_token;
        iframe.id = "easyassist-livechat-iframe";
        iframe.style.display = "none";
        document.querySelector("body").appendChild(iframe);
    }

    function add_agent_mouse_pointer() {
        var agent_mouse_pointer = document.createElement("img");
        agent_mouse_pointer.id = "agent-mouse-pointer";
        agent_mouse_pointer.style.top = "0%";
        agent_mouse_pointer.style.right = "0%";
        agent_mouse_pointer.style.position = "absolute";
        agent_mouse_pointer.style.width = "80px";
        agent_mouse_pointer.style.zIndex = "2147483647";
        agent_mouse_pointer.style.display = "none";
        if(window.EASYASSIST_COBROWSE_META.DEVELOPMENT == true){
            agent_mouse_pointer.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/static/EasyAssistApp/img/Client_cursor.svg"
        }else{
            agent_mouse_pointer.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/static/EasyAssistApp/img/" + EASYASSIST_COBROWSE_META.access_token + "/Client_cursor.svg"
        }
        document.body.appendChild(agent_mouse_pointer);
    }

    function show_easyassist_livechat_iframe() {
        livechat_iframe = document.getElementById("easyassist-livechat-iframe");
        livechat_iframe_window = livechat_iframe.contentWindow;
        if (livechat_iframe != null && livechat_iframe != undefined) {
            document.getElementById("easyassist-livechat-iframe").style.display = "block";
            allincall_chatbot_window = document.getElementById("allincall-popup");
            if (allincall_chatbot_window != null && allincall_chatbot_window != undefined) {
                document.getElementById("allincall-popup").style.display = "none";
                document.getElementById("allincall-chat-box").style.display = "none";
            }
        }
        livechat_iframe_window.postMessage(JSON.stringify({
          "focus_textbox": "focus-textbox"
        }),EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
    }

    function hide_easyassist_livechat_iframe() {
        livechat_iframe = document.getElementById("easyassist-livechat-iframe");
        if (livechat_iframe != null && livechat_iframe != undefined) {
            document.getElementById("easyassist-livechat-iframe").style.display = "none";
            allincall_chatbot_window = document.getElementById("allincall-popup");
            if (allincall_chatbot_window != null && allincall_chatbot_window != undefined) {
                document.getElementById("allincall-popup").style.display = "block";
                document.getElementById("allincall-chat-box").style.display = "none";
            }
        }
    }

    function refresh_easyassist_livechat_iframe() {
        livechat_iframe = document.getElementById("easyassist-livechat-iframe");
        if (livechat_iframe != null && livechat_iframe != undefined) {
            livechat_iframe.src = livechat_iframe.src;
        }
    }

    exports.close_connection_modal = close_connection_modal;
    exports.screenshot_page = screenshot_page;
    exports.add_easyassist_ripple_animation_frame = add_easyassist_ripple_animation_frame;
    exports.show_easyassist_ripple_effect = show_easyassist_ripple_effect;
    exports.hide_easyassist_ripple_effect = hide_easyassist_ripple_effect;
    exports.add_floating_sidenav_easyassist_button = add_floating_sidenav_easyassist_button;
    exports.hide_floating_sidenav_easyassist_button = hide_floating_sidenav_easyassist_button;
    exports.show_floating_sidenav_easyassist_button = show_floating_sidenav_easyassist_button;
    exports.show_easyassist_browsing_modal = show_easyassist_browsing_modal;
    exports.close_easyassist_browsing_modal = close_easyassist_browsing_modal;
    exports.add_easyassist_product_category_modal = add_easyassist_product_category_modal;
    exports.show_easyassist_product_category_modal = show_easyassist_product_category_modal;
    exports.close_easyassist_product_category_modal = close_easyassist_product_category_modal;
    exports.set_easyassist_product_category = set_easyassist_product_category;
    exports.connect_with_easyassist_customer = connect_with_easyassist_customer;
    exports.set_easyassist_cookie = set_easyassist_cookie;
    exports.get_easyassist_cookie = get_easyassist_cookie;
    exports.delete_easyassist_cookie = delete_easyassist_cookie;
    exports.show_easyassist_toast = show_easyassist_toast;
    exports.copy_text_to_clipboard_sharable_link_easyassist = copy_text_to_clipboard_sharable_link_easyassist;
    exports.hide_easyassist_feedback_form = hide_easyassist_feedback_form;
    exports.show_easyassist_feedback_form = show_easyassist_feedback_form;
    exports.hide_easyassist_agent_joining_modal = hide_easyassist_agent_joining_modal;
    exports.show_easyassist_agent_joining_modal = show_easyassist_agent_joining_modal;
    exports.show_floating_sidenav_menu = show_floating_sidenav_menu;
    exports.hide_floating_sidenav_menu = hide_floating_sidenav_menu;
    exports.add_easyassist_search_field_tag = add_easyassist_search_field_tag;
    exports.count_hidden_element_in_document = count_hidden_element_in_document;
    exports.show_payment_consent_modal = show_payment_consent_modal;
    exports.hide_payment_consent_modal = hide_payment_consent_modal;
    exports.get_easyassist_session_details = get_easyassist_session_details;
    exports.update_easyassist_url_history = update_easyassist_url_history;
    exports.create_easyassist_hidden_iframe = create_easyassist_hidden_iframe;
    exports.create_easyassist_cobrowsing_lead = create_easyassist_cobrowsing_lead;
    exports.connect_with_easyassist_customer_with_details = connect_with_easyassist_customer_with_details;
    exports.easyassist_obfuscate = easyassist_obfuscate;
    exports.save_easyassist_system_audit_trail = save_easyassist_system_audit_trail;
    exports.create_easyassist_livechat_iframe = create_easyassist_livechat_iframe;
    exports.show_easyassist_livechat_iframe = show_easyassist_livechat_iframe;
    exports.hide_easyassist_livechat_iframe = hide_easyassist_livechat_iframe;
    exports.add_easyassist_request_edit_access = add_easyassist_request_edit_access;
    exports.refresh_easyassist_livechat_iframe = refresh_easyassist_livechat_iframe;
    exports.show_easyassist_request_edit_access_form = show_easyassist_request_edit_access_form;
    exports.hide_easyassist_request_edit_access_form = hide_easyassist_request_edit_access_form;
    exports.add_connection_easyassist_modal = add_connection_easyassist_modal;
    exports.show_connection_easyassist_modal = show_connection_easyassist_modal;
    exports.close_connection_modal = close_connection_modal;
    exports.show_sharable_link_dialog_box = show_sharable_link_dialog_box;
    exports.hide_easyassist_video_calling_request_modal = hide_easyassist_video_calling_request_modal
    exports.show_easyassist_video_calling_request_modal = show_easyassist_video_calling_request_modal
    exports.open_easyassist_sidenav = open_easyassist_sidenav;
    exports.close_easyassist_sidenav = close_easyassist_sidenav;
    exports.on_easyassist_client_mouse_over_nav_bar = on_easyassist_client_mouse_over_nav_bar;
    exports.on_easyassist_mouse_out_nav_bar = on_easyassist_mouse_out_nav_bar;
    exports.clear_easyassist_close_nav_timeout = clear_easyassist_close_nav_timeout;
    exports.create_easyassist_close_nav_timeout = create_easyassist_close_nav_timeout;

    add_easyassist_ripple_animation_frame();
    add_floating_sidenav_easyassist_button();
    add_easyassist_product_category_modal();
    add_sidenav_floating_menu();
    add_easyassist_feedback_form();
    add_easyassist_agent_joining_modal();
    add_easyassist_request_assist_modal();
    add_easyassist_request_meeting_modal();
    add_easyassist_payment_consent_modal();
    add_connection_easyassist_modal();
    create_easyassist_livechat_iframe();
    add_easyassist_request_edit_access();
    add_agent_mouse_pointer();
    add_easyassist_video_calling_request_modal();
    add_easyassist_voip_audio_player();
    set_easyassist_cookie("page_leave_status", "None");

    document.getElementsByClassName("easychat_share_link_Model-content-close_button")[0].onclick = function() {
        document.getElementById("easychat_share_link_Model").style.display = "none";
    }

})(window);

/* feedback js */

emojiFour = document.querySelector('#emojiFour');
emojiThree = document.querySelector('#emojiThree');
emojiTwo = document.querySelector('#emojiTwo');
emojiOne = document.querySelector('#emojiOne');
function show_default_feedback_emoji() {

    emojiFour.style.display = "none";
    emojiThree.style.display = "initial";
    emojiTwo.style.display = "none";
    emojiOne.style.display = "none";
}

function show_emoji_by_user_rating(element, user_rating) {

    emojiFour.style.display = "none";
    emojiThree.style.display = "none";
    emojiTwo.style.display = "none";
    emojiOne.style.display = "none";

    if(user_rating <= 3) {
        emojiOne.style.display = "initial";
    } else if(user_rating <= 6) {
        emojiTwo.style.display = "initial";
    } else if(user_rating <= 8) {
        emojiThree.style.display = "initial";
    } else {
        emojiFour.style.display = "initial";
    }

    rating_spans = element.parentNode.children;
    for (var index = 0; index < rating_spans.length; index ++) {
        if (parseInt(rating_spans[index].innerHTML) <= user_rating) {
            rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
            rating_spans[index].style.color = "#fff";
        } else {
            rating_spans[index].style.background = "unset"
            rating_spans[index].style.color = "initial";
        }
    }
}

function changeColor(element) {

    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");

    var show_default_emoji = true;
    for(var index = 0; index < rating_spans.length; index ++) {
        if(!easyassist_tickmarks_clicked[index]) {
            rating_spans[index].style.color = "initial";
            rating_spans[index].style.background = "unset";
        } else {
            show_default_emoji = false;
        }
    }

    if(show_default_emoji) {
        show_default_feedback_emoji();
    }
}

function rateAgent(element) {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    var user_rating = parseInt(element.innerHTML);

    window.EASYASSIST_CLIENT_FEEDBACK = user_rating;

    for(var index = 0; index <= user_rating; index ++) {
        var current_rating = parseInt(rating_spans[index].innerHTML);
        rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        rating_spans[index].style.color = "#fff";
        easyassist_tickmarks_clicked[current_rating] = true;
    }

    for(var index = user_rating + 1; index < rating_spans.length; index ++) {
        var current_rating = parseInt(rating_spans[index].innerHTML);
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = "initial";
        easyassist_tickmarks_clicked[current_rating] = false;
    }
}

function reset_easyassist_rating_bar() {
    var rating_bar = document.getElementsByClassName("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    for (var index = 0; index < rating_spans.length; index++) {
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = "initial";
        easyassist_tickmarks_clicked[index] = false;
    }

    show_default_feedback_emoji();
}

function change_verification_input_color(el) {
    el.style.setProperty('border-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    el.style.color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
}

function is_time_to_show() {

    var currentTime = new Date();
    var currentOffset = currentTime.getTimezoneOffset();
    var ISTOffset = 330; // IST offset UTC +5:30
    var ISTTime = new Date(currentTime.getTime() + (ISTOffset + currentOffset) * 60000);
    // ISTTime now represents the time in IST coordinates
    var hoursIST = ISTTime.getHours()
    var minutesIST = ISTTime.getMinutes()

    var start_time = window.EASYASSIST_COBROWSE_META.start_time
    var end_time = window.EASYASSIST_COBROWSE_META.end_time

    var startHour = parseInt(start_time.substring(0, 2));
    var startMinute = parseInt(start_time.substring(3, 5));

    var endHour = parseInt(end_time.substring(0, 2));
    var endMinute = parseInt(end_time.substring(3, 5));

    if (hoursIST > startHour && hoursIST < endHour) {
        return true;
    } else if (hoursIST == startHour && hoursIST == endHour) {
        if (minutesIST >= startMinute && minutesIST <= endMinute) {
            return true;
        } else {
            return false;
        }
    } else if (hoursIST == startHour) {
        if (minutesIST >= startMinute) {
            return true;
        } else {
            return false;
        }
    } else if (hoursIST == endHour) {
        if (minutesIST <= endMinute) {
            return true;
        } else {
            return false;
        }
    } else {
        return false;
    }
}

function easyassist_request_for_meeting(el) {

    var session_id = get_easyassist_cookie("easyassist_session_id");
    request_params = {
        "session_id": session_id,
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var request_meeting_error = document.getElementById("easyassist-video-meeting-error");

    if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
        if(request_meeting_error.offsetParent == null) {
            show_easyassist_toast("An audio call has been initiated to the customer.");
        }
        document.getElementById("easyassist-voip-call-icon").style.display = 'none';
        document.getElementById("easyassist-voip-calling-icon").style.display = 'block';
        setTimeout(function() {
            toggle_voip_ringing_sound(true);
        }, 2000);
    }

    if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
        if(request_meeting_error.offsetParent == null) {
            show_easyassist_toast("A video call has been initiated to the customer.");
        }
        setTimeout(function() {
            toggle_voip_ringing_sound(true);
        }, 2000);
    }
    request_meeting_error.innerHTML = "";
    el.innerText = "Requesting...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/request-assist-meeting/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response.status == 200) {
                request_meeting_error.innerHTML = "Meeting request has been sent to customer.";
                request_meeting_error.style.setProperty('color', 'green', "important");
                check_meeting_status_interval = setInterval(function() {
                    check_easyassist_meeting_status(session_id)
                }, 5000)
                el.innerText = "Request";

            }
        }
    }
    xhttp.send(params);
}

function check_easyassist_meeting_status(session_id) {
    request_params = {
        "session_id": session_id
    };

    json_params = JSON.stringify(request_params);
    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/reverse/check-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var request_meeting_error = document.getElementById("easyassist-video-meeting-error");
                if (response.is_meeting_allowed == true) {
                    if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                        set_easyassist_cookie("is_cobrowse_meeting_active", session_id);
                        set_easyassist_cookie("cobrowse_meeting_id", session_id);
                        show_cobrowse_meeting_option();
                        hide_easyassist_video_calling_request_modal();

                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.setProperty('color', 'green', "important");
                        toggle_voip_ringing_sound(false);
                    } else if(EASYASSIST_COBROWSE_META.enable_voip_calling == true) {
                        set_easyassist_cookie("is_cobrowse_meeting_active", session_id);
                        set_easyassist_cookie("cobrowse_meeting_id", session_id);
                        show_cobrowse_meeting_option();
                        hide_easyassist_video_calling_request_modal();

                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';
                        
                        toggle_voip_ringing_sound(false);
                        document.getElementById("easyassist-voip-calling-icon").style.display = 'none';
                        document.getElementById("easyassist-voip-call-icon").style.display = 'block';
                    } else {
                        request_meeting_error.innerHTML = "Meeting request has been accepted by the customer. Please click on 'Connect' to join the meeting."
                        request_meeting_error.style.setProperty('color', 'green', "important");

                        var html = document.getElementById("easyassist_request_meeting_button");
                        var button = [
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_connect_with_client(this)" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; margin-right: 1em!important;">Connect</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Resend Request</button>',
                        ].join('');
                        html.innerHTML = button;
                        easyassist_connect_with_client();
                    }

                    if(check_meeting_status_interval) {
                        clearInterval(check_meeting_status_interval);
                    }
                    auto_msg_popup_on_client_call_declined = false;
                } else if (response.is_meeting_allowed == false) {
                    if(response.is_client_answer == true){
                        if(EASYASSIST_COBROWSE_META.enable_voip_calling == true) {
                            toggle_voip_ringing_sound(false);
                            toggle_voip_beep_sound(true);
                            document.getElementById("easyassist-voip-calling-icon").style.display = 'none';
                            document.getElementById("easyassist-voip-call-icon").style.display = 'block';
                            if(auto_msg_popup_on_client_call_declined == true) {
                                show_easyassist_toast("Customer declined the call");
                                // allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
                                // allincall_chat_window.postMessage(JSON.stringify({
                                //     "id": "agent_name",
                                //     "name": window.AGENT_NAME,
                                //     "session_id": COBROWSE_SESSION_ID,
                                //     "agent_connect_message": VOIP_DECLINE_MEETING_MESSAGE
                                // }), window.location.protocol + "//" + window.location.host);
                                // open_livechat_agent_window();
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    show_easyassist_toast("Customer declined the call");
                                }
                                request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                                request_meeting_error.style.color = 'red';
                                // var html = document.getElementById("easyassist_request_meeting_button");
                                // var button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                                //     <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                                // html.innerHTML = button
                            }
                        } else if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling == true) {
                            toggle_voip_ringing_sound(false);
                            toggle_voip_beep_sound(true);
                            if(auto_msg_popup_on_client_call_declined == true) {
                                show_easyassist_toast("Customer declined the call");
                                // allincall_chat_window = document.getElementById("allincall-chat-box").contentWindow
                                // allincall_chat_window.postMessage(JSON.stringify({
                                //     "id": "agent_name",
                                //     "name": window.AGENT_NAME,
                                //     "session_id": COBROWSE_SESSION_ID,
                                //     "agent_connect_message": VOIP_DECLINE_MEETING_MESSAGE
                                // }), window.location.protocol + "//" + window.location.host);
                                // open_livechat_agent_window();
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    show_easyassist_toast("Customer declined the call");
                                }
                                request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                                request_meeting_error.style.color = 'red';
                                // var html = document.getElementById("request_meeting_button");
                                // var button = '<button class="btn btn-secondary" type="button" data-dismiss="modal">Close</button>\
                                //     <button class="btn btn-primary" id="request_button" type="button" onclick="request_for_meeting(\'' + session_id + '\')">Resend Request</button>';
                                // html.innerHTML = button
                            }
                        } else {
                            request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                            request_meeting_error.style.setProperty('color', 'red', "important");
                            var html = document.getElementById("easyassist_request_meeting_button");
                            var button = [
                                '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                                '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Resend Request</button>',
                            ].join('');
                            html.innerHTML = button;
                        }
                        auto_msg_popup_on_client_call_declined = false;
                        if(check_meeting_status_interval) {
                            clearInterval(check_meeting_status_interval);
                        }
                    }
                }
            } else if (response.status == 301) {}
        }
    }
    xhttp.send(params);
}

function show_cobrowse_meeting_option() {
    if (get_easyassist_cookie("easyassist_session_id") == undefined) {
        return;
    }
    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(cobrowse_meeting_id == easyassist_session_id) {
        document.getElementById("show-voip-modal-btn").style.display = 'none';
        if(document.getElementById("easyassist-cobrowse-voip-container").style.display == 'none') {
            send_client_meeting_joined_over_socket();
            document.getElementById("easyassist-voip-loader").style.display = 'flex';
            document.getElementById("easyassist-cobrowse-voip-container").style.display = 'flex';
            var cobrowsing_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
            var meeting_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/agent-cobrowse-meeting/" + easyassist_session_id;
            cobrowsing_meeting_iframe.src = meeting_url;
        } 
    }
}

function toggle_meeting_iframe_visibility() {
    var meeting_iframe_container = document.getElementById("easyassist-cobrowse-meeting-iframe-container");
    if(meeting_iframe_container.style.display == 'none') {
        meeting_iframe_container.style.display = 'block';
    } else {
        meeting_iframe_container.style.display = 'none';
    }
}

function toggle_client_voice(element, status) {
    try {
        var cobrowse_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "toggle_voice",
            "status": status,
            "name": window.CLIENT_NAME
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);

        if(status) {
            set_easyassist_cookie("is_meeting_audio_muted", false);
        } else {
            set_easyassist_cookie("is_meeting_audio_muted", true);
        }

        if(element.id == "easyassist-client-meeting-mic-on-btn") {
            document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = 'none';
            document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = 'flex';
        } else if(element.id == "easyassist-client-meeting-mic-off-btn") {
            document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = 'none';
            document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = 'flex';
        }
    } catch(err) {
        console.log(err);
    }
}

function toggle_client_video(element, status) {
    try {
        var cobrowse_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "toggle_video",
            "name": window.CLIENT_NAME,
            "status": status,
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);

        var video_element = document.getElementById("easyassist-meeting-video-element");
        if(status) {
            document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'flex';
            navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream) => {
                captured_video_stream = stream;
                video_element.srcObject = stream;
                video_element.parentNode.style.display = 'block';
            })
            .catch(function() {
                video_element.srcObject = null;
                video_element.parentNode.style.display = 'none';
            });
        } else {
            video_element.srcObject = null;
            video_element.parentNode.style.display = 'none';
            try {
                captured_video_stream.getTracks().forEach(function(track) {
                    track.stop();
                });
            } catch(err) {}
        }
        if(element.id == "easyassist-client-meeting-video-on-btn") {
            document.getElementById("easyassist-client-meeting-video-on-btn").style.display = 'none';
            document.getElementById("easyassist-client-meeting-video-off-btn").style.display = 'flex';
        } else if(element.id == "easyassist-client-meeting-video-off-btn") {
            document.getElementById("easyassist-client-meeting-video-off-btn").style.display = 'none';
            document.getElementById("easyassist-client-meeting-video-on-btn").style.display = 'flex';
        }
    } catch(err) {
        console.log(err);
    }
}

function end_cobrowse_video_meet(auto_end_meeting=false) {
    try {
        var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
        var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if(cobrowse_meeting_id != easyassist_session_id) {
            return;
        }
        document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'none';
        var cobrowse_meeting_iframe = document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0];
        cobrowse_meeting_window = cobrowse_meeting_iframe.contentWindow;
        cobrowse_meeting_window.postMessage(JSON.stringify({
            "message": "end_meeting",
            "name": window.CLIENT_NAME
        }), EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
        send_end_meeting_messsage_over_socket(auto_end_meeting)
    } catch (err) { 
        console.log(err)
    }
}

function reset_voip_meeting() {
    set_easyassist_cookie("cobrowse_meeting_id", "");
    delete_easyassist_cookie("is_meeting_audio_muted");
    delete_easyassist_cookie("is_agent_voip_meeting_joined");
    document.getElementById("show-voip-modal-btn").style.display = 'flex';
    document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'none';
    document.getElementById("easyassist-cobrowse-voip-container").style.display = 'none';
    document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = 'none';
    document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = 'flex';
    if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
        document.getElementById("easyassist-client-meeting-video-on-btn").style.display = 'flex';
        document.getElementById("easyassist-client-meeting-video-off-btn").style.display = 'none';
        try {
            captured_video_stream.getTracks().forEach(function(track) {
                track.stop();
            });
        } catch(err) {}
    }

    setTimeout(function() {
        document.getElementById("easyassist-cobrowse-meeting-iframe-container").children[0].src = "";
    }, 2000);
}

function easyassist_connect_with_client() {
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    hide_easyassist_video_calling_request_modal();
    if (easyassist_session_id == null || easyassist_session_id == undefined) {
        return;
    }

    var meeting_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/meeting/" + easyassist_session_id + "?is_meeting_cobrowsing=true";
    window.open(meeting_url, "_blank",);
}

function toggle_voip_ringing_sound(play_music) {
    try {
        var audio_player = document.getElementById("easyassist-voip-ring-sound");
        if(!audio_player) {
            return;
        }
        if(play_music) {
            audio_player.play();
        } else {
            audio_player.pause();
        }
    } catch(err) { console.log(err) }
}

function toggle_voip_beep_sound(play_music) {
    try {
        var audio_player = document.getElementById("easyassist-voip-beep-sound");
        if(!audio_player) {
            return;
        }
        if(play_music) {
            audio_player.play();
        } else {
            audio_player.pause();
        }
    } catch(err) { console.log(err) }
}