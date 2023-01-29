var lead_capture_initialted = false;
var longitude = null;
var latitude = null;
var agent_location ='Location not shared'
var agent_name = null
var easyassist_tickmarks_clicked=new Array(11).fill(false);

if (window.EASYASSIST_COBROWSE_META.allow_popup_on_browser_leave == true) {
    document.addEventListener("mouseleave", function(e) {
        if ((e.clientY < 0 || e.clientX < 0) && (get_easyassist_cookie("easyassist_session_id") == undefined) && get_easyassist_cookie("page_leave_status") == "None") {
            set_easyassist_cookie("page_leave_status", "true");
            if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
                show_easyassist_product_category_modal();
            } else {
                show_easyassist_browsing_modal();
            }
        }
    }, false);
}


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
    el.nextElementSibling.style.display = "inline-table";
}

function easyassist_change_tooltiphide(el) {
    el.nextElementSibling.style.display = "none";
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
            document_input_tag_list[d_index].onchange = (function (onchange) { return function(evt) { evt  = evt || event; if (onchange) { onchange(evt); } sync_html_element_value_change(evt); } })(document_input_tag_list[d_index].onchange);
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

            if(is_obfuscated_element[0])
                add_warning_element(document_input_tag_list[d_index]);

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
                document_input_tag_list[d_index].onchange = (function (onchange) { return function(evt) { evt  = evt || event; if (onchange) { onchange(evt); } delay_sync_html_data(evt); } })(document_input_tag_list[d_index].onchange);
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
                document_input_tag_list[d_index].onchange = send_attachment_to_agent_for_validation;
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
                add_warning_element(document_textarea_tag_list[d_index]);
            } else if (is_numeric) {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value));
            } else {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, document_textarea_tag_list[d_index].value);
            }
        }

        document_select_tag_list = document.querySelectorAll("select");
        for (var d_index = 0; d_index < document_select_tag_list.length; d_index++) {

            document_select_tag_list[d_index].setAttribute("easyassist-element-id", easyassist_id_count);
            document_select_tag_list[d_index].onchange = (function (onchange) { return function(evt) { evt  = evt || event; if (onchange) { onchange(evt); } send_data_to_server(evt); } })(document_select_tag_list[d_index].onchange);

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
            if(is_obfuscated_element[0])
                add_warning_element(document_select_tag_list[d_index]);
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
                add_warning_element(document_span_tag_list[d_index]);
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
                    table_element.onchange = sync_html_element_value_change;
                    easyassist_id_count += 1;
                }
            }
            if(is_obfuscated_element)
                add_warning_element(document_table_tag_list[d_index]);
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
            var is_obfuscated_element = is_this_obfuscated_element(screenshot_input_tag_list[s_index]);
            if(is_obfuscated_element[0])
                remove_warning_element(screenshot_input_tag_list[s_index]);
        }

        screenshot_textarea_tag_list = screenshot.querySelectorAll("textarea");
        for (var s_index = 0; s_index < screenshot_textarea_tag_list.length; s_index++) {
            if (easyassist_edit_access != "true") {
                screenshot_textarea_tag_list[s_index].style.pointerEvents = 'none';
            }
            easyassist_tag_value = screenshot_textarea_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
            screenshot_textarea_tag_list[s_index].innerHTML = easyassist_tag_value;
            screenshot_textarea_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);
            var is_obfuscated_element = is_this_obfuscated_element(screenshot_textarea_tag_list[s_index]);
            if(is_obfuscated_element[0])
                remove_warning_element(screenshot_textarea_tag_list[s_index]);
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

            var is_obfuscated_element = is_this_obfuscated_element(screenshot_table_tag_list[s_index]);
            if (!is_obfuscated_element[0]) {

                continue;
            }
            for (var row_index = 0; row_index < screenshot_table_tag_list[d_index].tBodies[0].rows.length; row_index++) {

                for (var col_index = 0; col_index < screenshot_table_tag_list[d_index].tBodies[0].rows[row_index].children.length; col_index++) {

                    var table_element = screenshot_table_tag_list[d_index].tBodies[0].rows[row_index].children[col_index];
                    obfuscate_data_using_recursion(table_element);
                }
            }
            if(is_obfuscated_element[0])
                remove_warning_element(screenshot_table_tag_list[d_index]);
        }

        screenshot_label_tag_list = screenshot.querySelectorAll("label");
        for (var d_index = 0; d_index < screenshot_label_tag_list.length; d_index++) {
            if (easyassist_edit_access != "true") {
                screenshot_label_tag_list[d_index].style.pointerEvents = 'none';
            }
            label_id = screenshot_label_tag_list[d_index].getAttribute("id");
            if (label_id == null || label_id == undefined) {
                continue;
            }
            
            var is_obfuscated_element = is_this_obfuscated_element(screenshot_label_tag_list[d_index]);
            if (!is_obfuscated_element[0]) {

                continue;
            }
            screenshot_label_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_label_tag_list[d_index].innerHTML);
            if(is_obfuscated_element[0])
                remove_warning_element(screenshot_label_tag_list[d_index]);
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
                remove_warning_element(screenshot_p_tag_list[p_index])
            }

        }


        screenshot_div_tag_list = screenshot.querySelectorAll("div");

        for (var div_index = 0; div_index < screenshot_div_tag_list.length; div_index++) {
            screenshot_div_tag_list[div_index].onscroll = sync_mouse_position
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
                remove_warning_element(document_span_tag_list[d_index])  
            }
            if(document_span_tag_list[d_index].className == "easyassist-tooltiptext")
                document_span_tag_list[d_index].style.display = "none";
        }

        screenshot_a_tag_list = screenshot.querySelectorAll("a");
        for (var index = 0; index < screenshot_a_tag_list.length; index++) {
            if (easyassist_edit_access != "true") {
                screenshot_a_tag_list[index].style.pointerEvents = 'none';
            }
        }

        screenshot_button_tag_list = screenshot.querySelectorAll("button");
        for (var index = 0; index < screenshot_a_tag_list.length; index++) {
            if (easyassist_edit_access != "true") {
                screenshot_a_tag_list[index].style.pointerEvents = 'none';
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
            // screenshot.style.pointerEvents = 'none';
            // screenshot.style.webkitUserSelect = 'none';
            // screenshot.style.mozUserSelect = 'none';
            // screenshot.style.msUserSelect = 'none';
            // screenshot.style.oUserSelect = 'none';
            // screenshot.style.userSelect = 'none';
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

        try{
            easyassist_agent_information_modal = screenshot.querySelector("#easyassist-agent-information-modal");
            easyassist_agent_information_modal.parentNode.removeChild(easyassist_agent_information_modal);
        }catch(err){
            console.log(err);
        }
        

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
        			'<h6>Connect with our Experts</h6>',
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
            if(EASYASSIST_COBROWSE_META.allow_video_meeting_only == true){
                add_connect_sidenav_into_page(true)
            }else{
                add_connect_sidenav_into_page(false);
            }
        }
        //Add Model
        var div_model = document.createElement("div");
        div_model.id = "easyassist-co-browsing-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        if (EASYASSIST_COBROWSE_META.enable_location) {
            if (window.navigator.geolocation) {
                window.navigator.geolocation.getCurrentPosition(accept_location_request, cancel_location_request);
            }
        }
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

        if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code == true){
            virtual_agent_code_html += [
            	'<div class="easyassist-customer-connect-modal-content-wrapper">',
            		'<input type="number" autocomplete="off" name="easyassist-client-agent-virtual-code" id="easyassist-client-agent-virtual-code" placeholder="Enter agent code" >',
            		'<label id="modal-cobrowse-virtual-agent-code-error"></label>',
            	'</div>',
            ].join('');
        }

        if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            var dropdown_option_html = "";
            for (var index = 0; index < EASYASSIST_COBROWSE_META.supported_language.length; index++) {
                if (EASYASSIST_COBROWSE_META.supported_language[index]["value"].toLowerCase() == "english") {
                    dropdown_option_html += '<option selected="" value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
                } else {
                    dropdown_option_html += '<option value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
                }
            }
            lang_dropdown_html += [
            	'<div class="easyassist-customer-connect-modal-content-wrapper">',
	            	'<select id="easyassist-inline-form-input-preferred-language" >',
	                    dropdown_option_html,
	                '</select>',
	                '<label id="modal-cobrowse-customer-language-error"></label>',
	            '</div>',
	        ].join('');
        }

        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header" style="text-align: center;">',
                    '<h6>Connect with our Experts</h6>',
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
		        		'<button class ="easyassist-modal-primary-btn" id="easyassist-co-browsing-connect-button"  onclick="connect_with_easyassist_agent()">Connect</button>',
		        	'</div>',
                '</div>',
            '</div>'
        ].join('');

        div_model.innerHTML = modal_html;
        var sharable_link = '<div id="easychat_share_link_Model"><div class="easychat_share_link_Model-content"><h3>Share with Others</h3><br><div class="easychat_share_link_Model-content_wrapper" ><div class="easychat_share_link_Model-content_buttons_wrapper"><button disabled style="width: 75%;">Anyone with the link can guide you</button><button style="width: 25%;" onclick="copy_text_to_clipboard_sharable_link_easyassist()">Copy link</button></div><input id="easychat_share_link_Model-content_link_wrapper" type="text" value="" disabled autocomplete="off"></div><br><p style="color: black;">*Your personal information will be masked and will not be shared with anyone.</p><br><button class="easychat_share_link_Model-content-close_button">Done</button></div></div>';
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-co-browsing-connect-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-co-browsing-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sharable_link);

        if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            document.getElementById("easyassist-inline-form-input-preferred-language").selectedIndex = -1;
            var product_category_dropdown = new EasyassistCustomSelect(
                '#easyassist-inline-form-input-preferred-language', 
                'Choose preferred language',
                EASYASSIST_COBROWSE_META.floating_button_bg_color);
        }

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

    function add_connect_sidenav_into_page(value) {
        //Add Span
        var nav_span = document.createElement("span");
        nav_span.id = "easyassist-side-nav-options-co-browsing";
        nav_span.setAttribute("class", "easyassist-side-nav-class");
        nav_span.style.backgroundColor = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        if (EASYASSIST_COBROWSE_META.floating_button_position == "left") {
            if(value == true){
                nav_span.style.left = "-"+ "30" +"px";
            } else {
                nav_span.style.left = "-"+ EASYASSIST_COBROWSE_META.floating_button_left_right_position.toString() +"px";
            }
            nav_span.style.borderRadius = "0px 0px 10px 10px";
        } else {
            nav_span.style.right = "-"+ EASYASSIST_COBROWSE_META.floating_button_left_right_position.toString() +"px";
            nav_span.style.borderRadius = "10px 10px 0px 0px";
        }
        if(value == true){
            nav_span.textContent = "Contact Us";
        }else{
            nav_span.textContent = "Request for Support";
        }
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
        hide_easyassist_agent_information_modal();
        document.getElementById("easyassist-client-feedback").value = "";
        reset_easyassist_rating_bar();
        document.getElementById("easyassist-co-browsing-feedback-modal").style.display = "flex";
        hide_easyassist_livechat_iframe();
    }

    function hide_easyassist_agent_joining_modal(el) {
        document.getElementById("easyassist_agent_joining_modal").style.display = "none";
    }

    function show_easyassist_agent_joining_modal(el) {
        document.getElementById("easyassist_agent_joining_modal").style.display = "flex";
    }

    function hide_easyassist_agent_information_modal(el) {
        document.getElementById("easyassist-agent-information-modal").style.display = "none";
    }

    function show_easyassist_agent_information_modal(el) {
        document.getElementById("easyassist-agent-information-modal").style.display = "flex";
    }

    function add_easyassist_request_assist_modal() {
    	var request_modal_html
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
                } else {
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
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
            })
        }
    }

    function add_easyassist_request_meeting_modal() {
        var meeting_modal_html = [
        	'<div id="easyassist-co-browsing-request-meeting-modal" class="easyassist-customer-connect-modal">',
        		'<div class="easyassist-customer-connect-modal-content">',
        			'<div class="easyassist-customer-connect-modal-header">',
        				'<h6>Connect with our Experts</h6>',
        			'</div>',
        			'<div class="easyassist-customer-connect-modal-body">',
        				EASYASSIST_COBROWSE_META.meeting_message,
        				'<label id="easyassist-request-meeting-error"></label>',
        			'</div>',
        			'<div class="easyassist-customer-connect-modal-footer">',
        				'<button class="easyassist-modal-cancel-btn" onclick="update_agent_meeting_request(\'false\')" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Decline</button>',
                		'<button clsas="easyassist-modal-primary-btn" onclick="update_agent_meeting_request(\'true\')" id="easyassist-meeting-connect-button">Connect</button>',
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
    					'Our Customer Service Agent has requested Edit Access to help you in filling the form. Would you like to allow?',
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
    //         <button onclick="submit_client_feedback(\'no_feedback\')" style="background-color: #486EDB; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em; border-style: none; float: right; margin-right: 5%;outline:none;">No thanks</button>\
    //         <button onclick="submit_client_feedback(\'feedback\')" style="background-color: #1b5e20; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em; border-style: none; float: right; margin-right: 5%;outline:none;">Submit</button>\
    //     </div>\
    //     <br><br>\
    //   </div>\
    // </div>';
    //     document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form);
    // }

    function add_easyassist_feedback_form() {
        var add_easyassist_feedback_form = [
            '<div id="easyassist-co-browsing-feedback-modal" class="easyassist-customer-feedback-modal" style="display: none;">',
                '<div class="easyassist-customer-feedback-modal-content">',
                    '<div class="easyassist-customer-feedback-modal-header">',
                        '<h6 style="padding-bottom: 1em!important;width:100%;">Feedback</h6>',
                        '<div onclick="hide_easyassist_feedback_form()" ea_visible="true">',
                            '<svg width="23" height="23" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M0 11.5C0 5.14873 5.14873 0 11.5 0C17.8513 0 23 5.14873 23 11.5C23 17.8513 17.8513 23 11.5 23C5.14873 23 0 17.8513 0 11.5ZM16.1434 6.80013C16.5075 7.16427 16.5075 7.75465 16.1434 8.11879L12.7904 11.4718L16.1434 14.8247C16.5075 15.1889 16.5075 15.7792 16.1434 16.1434C15.7792 16.5075 15.1889 16.5075 14.8247 16.1434L11.4718 12.7904L8.11879 16.1434C7.75465 16.5075 7.16427 16.5075 6.80013 16.1434C6.43599 15.7792 6.43599 15.1889 6.80013 14.8247L10.1531 11.4718L6.80013 8.11879C6.43599 7.75465 6.43599 7.16427 6.80013 6.80013C7.16427 6.43599 7.75465 6.43599 8.11879 6.80013L11.4718 10.1531L14.8247 6.80013C15.1889 6.43599 15.7792 6.43599 16.1434 6.80013Z" fill="#717274" />',
                            '</svg>',
                        '</div>',
                    '</div>',
                    '<div class="easyassist-customer-feedback-modal-body">',
                        '<label>',
                            '<p>Please rate us on the scale of 0-10</p>',
                            '<div class="easyassist-tickmarks">',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 0)" onmouseout="changeColor(this)">0</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 1)" onmouseout="changeColor(this)">1</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 2)" onmouseout="changeColor(this)">2</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 3)" onmouseout="changeColor(this)">3</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 4)" onmouseout="changeColor(this)">4</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 5)" onmouseout="changeColor(this)">5</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 6)" onmouseout="changeColor(this)">6</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 7)" onmouseout="changeColor(this)">7</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 8)" onmouseout="changeColor(this)">8</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 9)" onmouseout="changeColor(this)">9</span>',
                                '<span onclick="rateAgent(this);" onmouseover="show_emoji_by_user_rating(this, 10)" onmouseout="changeColor(this)">10</span>',
                            '</div>',
                        '</label>',
                        '<div class="easyassist-gyraMojis">',
                            '<img src=' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/static/EasyAssistSalesforceApp/img/easyassist_feedback_face_1.svg alt="reaction emoji" width="50px" height="50px" id="emojiOne" />',
                            '<img src=' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/static/EasyAssistSalesforceApp/img/easyassist_feedback_face_3.png alt="reaction emoji" width="50px" height="50px" id="emojiTwo" />',
                            '<img src=' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/static/EasyAssistSalesforceApp/img/easyassist_feedback_face_4.svg alt="reaction emoji" width="50px" height="50px" id="emojiThree" />',
                            '<img src=' + EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + '/static/EasyAssistSalesforceApp/img/easyassist_feedback_face_5.svg alt="reaction emoji" width="50px" height="50px" id="emojiFour" />',
                        '</div>',
                        '<textarea id="easyassist-client-feedback" class="easyassist-feedbackComments" property="comment" cols="30" rows="5" placeholder="Comments"></textarea>',
                    '</div>',
                    '<div class="easyassist-customer-feedback-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" id="easyassist-feedback-nothanks-btn" onclick="submit_client_feedback(\'no_feedback\')" type="button" data-dismiss="easyassist-modal">',
                            'No Thanks',
                        '</button>',
                        '<button class="easyassist-modal-primary-btn" id="easyassist-feedback-submit-button" onclick="submit_client_feedback(\'feedback\')">',
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
          <div class="easyassist-custom-nav-bar">\
          <a href="javascript:void(0)" onclick="show_easyassist_livechat_iframe();hide_easyassist_feedback_form();">\
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"\
              onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                <path id="easyassist-icon-path-2"\
                  d="M11 1.83325C16.0625 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0625 20.1666 11 20.1666C9.49628 20.1666 8.04388 19.8035 6.74278 19.12L2.80991 20.1439C2.39349 20.2525 1.96797 20.0028 1.85951 19.5863C1.82597 19.4576 1.82596 19.3224 1.85948 19.1936L2.8828 15.2626C2.19741 13.9602 1.83331 12.5058 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM12.1474 11.9166H8.02081L7.92752 11.9228C7.59195 11.9684 7.33331 12.256 7.33331 12.6041C7.33331 12.9521 7.59195 13.2398 7.92752 13.2854L8.02081 13.2916H12.1474L12.2407 13.2854C12.5763 13.2398 12.8349 12.9521 12.8349 12.6041C12.8349 12.256 12.5763 11.9684 12.2407 11.9228L12.1474 11.9166ZM13.9791 8.70825H8.02081L7.92752 8.71453C7.59195 8.76005 7.33331 9.04769 7.33331 9.39575C7.33331 9.74381 7.59195 10.0315 7.92752 10.077L8.02081 10.0833H13.9791L14.0725 10.077C14.408 10.0315 14.6666 9.74381 14.6666 9.39575C14.6666 9.04769 14.408 8.76005 14.0725 8.71453L13.9791 8.70825Z"\
                  fill="#2B2B2B" />\
              </svg>\
              <label id="easyassist-icon-path-2-label">Chat with the Expert</label>\
            </a>\
            <a href="javascript:void(0)" onclick="revoke_easyassist_edit_access();" id="revoke-edit-access-button" style="display:none;">\
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"\
              onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                <path id="easyassist-icon-path-3" fill-rule="evenodd" clip-rule="evenodd" d="M19.2778 2.72247L19.1376 2.59012C17.8495 1.4431 15.8741 1.48722 14.6388 2.72247L13.7492 3.61155L18.3885 8.24989L19.2778 7.36141C20.5131 6.12616 20.5572 4.15082 19.4102 2.8627L19.2778 2.72247ZM12.7775 4.58321L17.4168 9.22249L16.5978 10.0415C15.7155 9.3843 14.6489 9 13.5 9C10.4624 9 8 11.6863 8 15C8 16.0668 8.25521 17.0686 8.70266 17.9366L8.30685 18.3324C8.05304 18.5862 7.73739 18.7694 7.39111 18.8638L2.70173 20.1427C2.18852 20.2827 1.7176 19.8117 1.85756 19.2986L3.13649 14.6092C3.23093 14.2629 3.4141 13.9473 3.66791 13.6934L12.7775 4.58321ZM5.98125 10.0832L4.60625 11.4582L2.52084 11.4586C2.14114 11.4586 1.83334 11.1508 1.83334 10.7711C1.83334 10.3914 2.14114 10.0836 2.52084 10.0836L5.98125 10.0832ZM9.64795 6.41656L8.27292 7.79156L2.52084 7.79194C2.14114 7.79194 1.83334 7.48414 1.83334 7.10444C1.83334 6.72475 2.14114 6.41694 2.52084 6.41694L9.64795 6.41656ZM11.9396 4.12488L13.3146 2.74989L2.52084 2.75028C2.14114 2.75028 1.83334 3.05808 1.83334 3.43778C1.83334 3.81748 2.14114 4.12528 2.52084 4.12528L11.9396 4.12488ZM19.0833 15.0417C19.0833 12.2572 16.8261 10 14.0417 10C11.2572 10 9 12.2572 9 15.0417C9 17.8261 11.2572 20.0833 14.0417 20.0833C16.8261 20.0833 19.0833 17.8261 19.0833 15.0417ZM14.6911 15.0418L16.3134 13.4204C16.4924 13.2414 16.4924 12.9512 16.3134 12.7722C16.1344 12.5933 15.8442 12.5933 15.6652 12.7722L14.0429 14.3936L12.4214 12.7721C12.2424 12.5932 11.9522 12.5932 11.7732 12.7721C11.5942 12.9511 11.5942 13.2413 11.7732 13.4203L13.3945 15.0416L11.7732 16.6619C11.5942 16.8409 11.5942 17.1311 11.7732 17.31C11.9522 17.4891 12.2424 17.4891 12.4214 17.31L14.0427 15.6898L15.665 17.3121C15.844 17.4911 16.1342 17.4911 16.3132 17.3121C16.4922 17.1331 16.4922 16.8429 16.3132 16.6639L14.6911 15.0418Z" fill="#2B2B2B"/>\
                </svg>\
                <label id="easyassist-icon-path-3-label">Revoke edit access</label>\
            </a>\
            <a href="javascript:void(0)" onclick="hide_easyassist_feedback_form();hide_easyassist_livechat_iframe();show_easyassist_agent_information_modal();" id="show-agent-details-button">\
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"\
              onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                <path id="easyassist-icon-path-4"\
                   d="M11 1.83325C16.0626 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0626 20.1666 11 20.1666C5.93737 20.1666 1.83331 16.0625 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM11.1146 14.6666C10.7349 14.6666 10.4271 14.9744 10.4271 15.3541C10.4271 15.7338 10.7349 16.0416 11.1146 16.0416C11.4942 16.0416 11.8021 15.7338 11.8021 15.3541C11.8021 14.9744 11.4942 14.6666 11.1146 14.6666ZM11.1146 5.95825C9.57291 5.95825 8.24998 7.28036 8.24998 8.82284C8.24998 9.13927 8.50646 9.39575 8.8229 9.39575C9.09978 9.39575 9.33073 9.19936 9.38417 8.93829L9.39283 8.88141L9.39833 8.73516C9.44816 7.86199 10.2349 7.10409 11.1146 7.10409C12.0242 7.10409 12.8333 7.91231 12.8333 8.82284C12.8338 9.36688 12.6405 9.75784 12.091 10.3791L11.9961 10.4848L11.5253 10.988C10.7776 11.8005 10.4615 12.3613 10.4674 13.1811C10.4696 13.4975 10.728 13.7522 11.0443 13.75C11.3014 13.7481 11.5178 13.5772 11.5886 13.3435L11.6024 13.2885L11.6106 13.2315L11.6132 13.1729L11.6146 13.0988C11.6311 12.7318 11.7952 12.4178 12.2018 11.9499L12.2863 11.8542L12.7515 11.3561C13.6269 10.4129 13.9801 9.79409 13.9791 8.82229C13.9791 7.27922 12.6567 5.95825 11.1146 5.95825Z"/>\
              </svg>\
              <label id="easyassist-icon-path-4-label">Show agent details</label>\
            </a>\
             <hr style="color: black;width: 30px;margin-top: 10px;margin-bottom: 10px;">\
             <a href="javascript:void(0)" onclick="show_easyassist_feedback_form();hide_easyassist_agent_information_modal();hide_easyassist_livechat_iframe();">\
               <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"\
               onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                 <path id="easyassist-icon-path-1"\
                   d="M11 1.83325C16.0626 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0626 20.1666 11 20.1666C5.93737 20.1666 1.83331 16.0625 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM14.2361 7.76378L14.159 7.69722C13.9198 7.51971 13.5914 7.51751 13.35 7.69064L13.2638 7.76378L11 10.0273L8.73612 7.76378L8.65901 7.69722C8.41977 7.51971 8.0914 7.51751 7.84997 7.69064L7.76384 7.76378L7.69728 7.84089C7.51977 8.08013 7.51757 8.40849 7.6907 8.64993L7.76384 8.73605L10.0274 10.9999L7.76384 13.2638L7.69728 13.3409C7.51977 13.5801 7.51757 13.9085 7.6907 14.1499L7.76384 14.2361L7.84095 14.3026C8.08019 14.4801 8.40855 14.4823 8.64999 14.3092L8.73612 14.2361L11 11.9725L13.2638 14.2361L13.341 14.3026C13.5802 14.4801 13.9086 14.4823 14.15 14.3092L14.2361 14.2361L14.3027 14.1589C14.4802 13.9197 14.4824 13.5913 14.3093 13.3499L14.2361 13.2638L11.9726 10.9999L14.2361 8.73605L14.3027 8.65895C14.4802 8.41971 14.4824 8.09134 14.3093 7.8499L14.2361 7.76378L14.159 7.69722L14.2361 7.76378Z"\
                   fill="#2B2B2B" />\
               </svg>\
               <label id="easyassist-icon-path-1-label">End Session</label>\
             </a>\
          </div>\
        </div>';
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sidenav_menu);
        document.getElementById("easyassist-icon-path-1").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-2").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-3").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-4").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-1-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-2-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-3-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        document.getElementById("easyassist-icon-path-4-label").style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
    }

    function show_floating_sidenav_menu() {
        document.getElementById("easyassist-sidenav-menu-id").style.display = "block";
        if (get_easyassist_cookie("easyassist_edit_access") == "true") {
            document.getElementById("revoke-edit-access-button").style.display = "block";
        } else {
            document.getElementById("revoke-edit-access-button").style.display = "none";
        }
    }

    function add_easyassist_agent_information_modal(){
        var div_model = document.createElement("div");
        div_model.id = "easyassist-agent-information-modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
        	'<div class="easyassist-customer-connect-modal-content">',
        		'<div class="easyassist-customer-connect-modal-header">',
        			'<div style="display:flex;align-items:center;flex-direction:column;">',
        				'<h6 style="padding-bottom:12px;">Agent Details</h6>',
        				'<div>',
        					'<svg width="76" height="70" viewBox="0 0 76 70" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M56.6469 21.6467V23.2422H52.5453V21.6467C52.5453 11.9725 44.6744 4.10156 35.0002 4.10156C25.326 4.10156 17.4551 11.9725 17.4551 21.6467V23.2422H13.3535V21.6467C13.3535 9.71113 23.0633 0 35.0002 0C46.9371 0 56.6469 9.71113 56.6469 21.6467Z" fill="#393E9F"/>',
                                '<path d="M56.6467 21.6467V23.2422H52.5451V21.6467C52.5451 11.9725 44.6742 4.10156 35 4.10156V0C46.9369 0 56.6467 9.71113 56.6467 21.6467Z" fill="#340D66"/>',
                                '<path d="M23.9653 33.9875H16.4496C14.5674 33.9875 13.0415 32.4616 13.0415 30.5794V24.5773C13.0415 22.6951 14.5674 21.1692 16.4496 21.1692H23.9653V33.9875Z" fill="#1857FA"/>',
                                '<path d="M45.7607 33.9875H53.5502C55.4324 33.9875 56.9583 32.4616 56.9583 30.5794V24.5773C56.9583 22.6951 55.4324 21.1692 53.5502 21.1692H45.7607V33.9875Z" fill="#1857FA"/>',
                                '<path d="M70 64.2017V69.9999H55.8783L53.8275 67.9492L51.7768 69.9999H18.2232L16.1725 67.9492L14.1217 69.9999H0V64.2017C0 61.6943 1.61055 59.4726 3.99219 58.6906L25.0004 51.8054H45.0584V51.8246L66.0078 58.6906C68.3895 59.4726 70 61.6943 70 64.2017Z" fill="#0254D7"/>',
                                '<path d="M70 64.2017V69.9999H55.8783L53.8275 67.9492L51.7768 69.9999H35V51.8054H45.0584V51.8246L66.0078 58.6906C68.3895 59.4726 70 61.6943 70 64.2017Z" fill="#022D58"/>',
                                '<path d="M45.0585 41.8811V51.8055C45.0585 51.8055 39.9999 56.8053 35.0001 56.8053C30.0003 56.8053 25.0005 51.8055 25.0005 51.8055V41.8811H45.0585Z" fill="#FDFEDC"/>',
                                '<path d="M45.0584 41.8811V51.8055C45.0584 51.8055 39.9998 56.8053 35 56.8053V41.8811H45.0584Z" fill="#FDFEDC"/>',
                                '<path d="M47.9498 20.8797V25.1836L46.6209 26.615H23.3787L22.0498 25.1836V20.8797C22.0498 17.3031 23.499 14.0656 25.8424 11.7223C28.1857 9.37891 31.4232 7.92969 34.9998 7.92969C42.1516 7.92969 47.9498 13.7279 47.9498 20.8797Z" fill="#4D4D4D"/>',
                                '<path d="M47.95 20.8797V25.1836L46.6211 26.615H35V7.92969C42.1518 7.92969 47.95 13.7279 47.95 20.8797Z" fill="#4D4D4D"/>',
                                '<path d="M47.9498 25.1916V34.0605C47.9498 34.9752 47.8664 35.868 47.7065 36.732C47.5766 37.4361 45.7609 38.7828 45.7609 38.7828C45.7609 38.7828 46.6277 40.1814 46.2805 40.8336C44.0588 45.0199 39.8397 47.8459 34.9998 47.8459C31.4232 47.8459 28.1857 46.3037 25.8424 43.8086C23.499 41.3135 22.0498 37.8682 22.0498 34.0605V25.1916H28.9568C31.2824 25.1916 33.4029 24.3084 34.9998 22.8592C36.8127 21.2131 37.9516 18.8383 37.9516 16.1982C37.9516 21.1652 41.9779 25.1916 46.9449 25.1916H47.9498Z" fill="#FDFEDC"/>',
                                '<path d="M47.95 25.1916V34.0605C47.95 34.9752 47.8666 35.868 47.7066 36.732C47.5768 37.4361 45.7611 38.7828 45.7611 38.7828C45.7611 38.7828 46.6279 40.1814 46.2807 40.8336C44.059 45.0199 39.8398 47.8459 35 47.8459V22.8592C36.8129 21.2131 37.9518 18.8383 37.9518 16.1982C37.9518 21.1652 41.9781 25.1916 46.9451 25.1916H47.95Z" fill="#FDFEDC"/>',
                                '<path d="M47.7058 36.7322C47.4364 38.1964 46.9483 39.5759 46.2798 40.8337H37.3521V36.7322H47.7058Z" fill="#340D66"/>',
                                '<path d="M14.1211 63.7109H18.2227V70H14.1211V63.7109Z" fill="#0254D7"/>',
                                '<path d="M51.7773 63.7109H55.8789V70H51.7773V63.7109Z" fill="#022D58"/>',
                                '<path d="M76 52.5L73.3382 49.4443L73.7091 45.4029L69.7709 44.5048L67.7091 41L64 42.599L60.2909 41L58.2291 44.4938L54.2909 45.381L54.6618 49.4333L52 52.5L54.6618 55.5557L54.2909 59.6081L58.2291 60.5062L60.2909 64L64 62.39L67.7091 63.989L69.7709 60.4952L73.7091 59.5971L73.3382 55.5557L76 52.5ZM61.1418 56.8919L58.5455 54.2633C58.4443 54.162 58.3641 54.0417 58.3093 53.9092C58.2546 53.7767 58.2264 53.6346 58.2264 53.4912C58.2264 53.3477 58.2546 53.2057 58.3093 53.0732C58.3641 52.9407 58.4443 52.8204 58.5455 52.719L58.6218 52.6424C59.0473 52.2152 59.7455 52.2152 60.1709 52.6424L61.9273 54.4167L67.5455 48.7652C67.9709 48.3381 68.6691 48.3381 69.0945 48.7652L69.1709 48.8419C69.5964 49.269 69.5964 49.959 69.1709 50.3862L62.7127 56.8919C62.2655 57.319 61.5782 57.319 61.1418 56.8919Z" fill="#12DB00"/>',
                            '</svg>',
        				'</div>',
        			'</div>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-body">',
        			'<div class="easyassist-agent-information-text" id="easyassist-agent-information-agent-name">',
        			'</div>',
        			'<div class="easyassist-agent-information-text" id="easyassist-agent-information-agent-location">',
        			'</div>',
        			'<div class="easyassist-customer-connect-modal-content-wrapper">',
        				'<span class="easyassist-customer-connect-modal-small-text"> You are connected to offical agents/ advisors </span>',
        				'<svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;">',
							'<path d="M13 6.5L11.5582 4.77286L11.7591 2.48857L9.62591 1.98095L8.50909 0L6.5 0.90381L4.49091 0L3.37409 1.97476L1.24091 2.47619L1.44182 4.76667L0 6.5L1.44182 8.22714L1.24091 10.5176L3.37409 11.0252L4.49091 13L6.5 12.09L8.50909 12.9938L9.62591 11.019L11.7591 10.5114L11.5582 8.22714L13 6.5ZM4.95182 8.98238L3.54545 7.49667C3.49068 7.4394 3.44722 7.37137 3.41756 7.29648C3.38791 7.22159 3.37265 7.14131 3.37265 7.06024C3.37265 6.97916 3.38791 6.89888 3.41756 6.82399C3.44722 6.74911 3.49068 6.68108 3.54545 6.62381L3.58682 6.58048C3.81727 6.33905 4.19545 6.33905 4.42591 6.58048L5.37727 7.58333L8.42045 4.38905C8.65091 4.14762 9.02909 4.14762 9.25955 4.38905L9.30091 4.43238C9.53136 4.67381 9.53136 5.06381 9.30091 5.30524L5.80273 8.98238C5.56045 9.22381 5.18818 9.22381 4.95182 8.98238Z" fill="#12DB00" fill-opacity="0.5"/>',
						'</svg>',
        			'</div>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-footer" style="justify-content:center;">',
        			'<button class="easyassist-modal-primary-btn" id="easyassist-agent-info-modal-close-btn" onclick="hide_easyassist_agent_information_modal(this)">Close</button>',
        		'</div>',
        	'</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-agent-info-modal-close-btn").style.setProperty(
            'background', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
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
        if (EASYASSIST_COBROWSE_META.allow_connect_with_drop_link == true) {
            if (get_easyassist_cookie("easyassist_session_id") != undefined) {
                return;
            }
            var first_index = window.location.href.indexOf("eadKey");
            if (first_index > 0) {
                initialize_cobrowsing_using_drop_link();
                return;
            }
        }
        if (EASYASSIST_COBROWSE_META.show_floating_easyassist_button == false && EASYASSIST_COBROWSE_META.show_easyassist_connect_agent_icon == false) {
            return;
        }
        if (EASYASSIST_COBROWSE_META.enable_waitlist == true && EASYASSIST_COBROWSE_META.show_floating_button_on_enable_waitlist == false) {
            return;
        }
        if (is_time_to_show() == false) {
            // hide_floating_sidenav_easyassist_button();
            EASYASSIST_COBROWSE_META.agents_available = false;
            document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
            document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("title", EASYASSIST_COBROWSE_META.message_on_non_working_hours);
            document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "show_easyassist_toast('" + EASYASSIST_COBROWSE_META.message_on_non_working_hours + "')");
            return;
        } else {
            EASYASSIST_COBROWSE_META.agents_available = undefined;
            document.getElementById("easyassist-side-nav-options-co-browsing").removeAttribute("title");
            if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
                document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "show_easyassist_product_category_modal()");
            } else {
                document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "show_easyassist_browsing_modal()");
            }
        }
        if (document.getElementById("easyassist-co-browsing-modal-id").style.display == "flex") {
            return;
        }
        if (document.getElementById("easyassist-product-category-modal-id").style.display == "flex") {
            return;
        }
        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            return;
        }
        if (EASYASSIST_COBROWSE_META.show_only_if_agent_available == true) {
            check_agent_available_status();
        } else if (EASYASSIST_COBROWSE_META.disable_connect_button_if_agent_unavailable == true) {
            check_agent_available_status();
        } else {
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

    function modal_event_handler(event) {
        var key = event.key || event.keyCode;
        if (key === 'Enter' || key === 'enter' || key === 13) {
            document.getElementById('easyassist-client-mobile-number').focus();
            document.getElementById('easyassist-client-mobile-number').select();
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
        document.getElementById('easyassist-client-name').focus();
        document.getElementById('easyassist-client-name').select();
        document.addEventListener('keydown', modal_event_handler);
        hide_floating_sidenav_easyassist_button();
    }

    function close_easyassist_browsing_modal(el) {
        document.removeEventListener('keydown',modal_event_handler);
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

    function initialize_cobrowsing_using_drop_link() {
        var first_index = window.location.href.indexOf("eadKey");
        if (first_index <= 0) return;
        var drop_link_key = window.location.href.substring(first_index);
        drop_link_key = drop_link_key.substring(drop_link_key.indexOf("=")+1).trim();
        if (drop_link_key == "") return;

        var url = window.location.href;
        url = url.substring(0, first_index-1);
        var title = url;
        if (document.querySelector("title") != null) {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        var request_id = easyassist_request_id();

        var easyassist_customer_id = get_easyassist_cookie("easyassist_customer_id");
        if (easyassist_customer_id == null || easyassist_customer_id == undefined) {
            easyassist_customer_id = "None";
        }

        json_string = JSON.stringify({
            "drop_link_key": drop_link_key,
            "request_id": request_id,
            "longitude": longitude,
            "latitude": latitude,
            "active_url": window.location.href,
            "customer_id": easyassist_customer_id,
            "meta_data": {
                "product_details": {
                    "title": title,
                    "description": description,
                    "url": url
                }
            }
        });

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/initialize-using-droplink/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {
                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");

                    window.location.href = url;

                } else {
                    show_easyassist_toast("Cobrowsing session could not be initialized. Please try again.");
                }
            }
        }
        xhttp.send(params);
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

    function connect_with_easyassist_agent(event) {
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
        var virtual_agent_code = "None";
        if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code) {
            virtual_agent_code = document.getElementById("easyassist-client-agent-virtual-code").value;
            if (virtual_agent_code.toString().trim() == "") {
            	document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = "Please enter valid agent code";
                return;
            }
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

        var easyassist_customer_id = get_easyassist_cookie("easyassist_customer_id");
        if (easyassist_customer_id == null || easyassist_customer_id == undefined) {
            easyassist_customer_id = "None";
        }

        var selected_language = -1;
        if (EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "True") {

            selected_language = document.getElementById("easyassist-inline-form-input-preferred-language").value;
        }

        if (selected_language == "None" || selected_language == "") {
        	document.getElementById("modal-cobrowse-customer-language-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            document.getElementById("modal-cobrowse-customer-language-error").innerHTML = "Please select the preferred language";
            return;
        }

        var selected_product_category = -1;
        if (window.EASYASSIST_PRODUCT_CATEGORY != null && window.EASYASSIST_PRODUCT_CATEGORY != undefined && window.EASYASSIST_PRODUCT_CATEGORY.length > 0) {
            selected_product_category = window.EASYASSIST_PRODUCT_CATEGORY;
        }
        document.getElementById("easyassist-co-browsing-connect-button").disabled = true;

        json_string = JSON.stringify({
            "request_id": request_id,
            "name": full_name,
            "mobile_number": mobile_number,
            "longitude": longitude,
            "latitude": latitude,
            "selected_language": selected_language,
            "selected_product_category": selected_product_category,
            "active_url": window.location.href,
            "virtual_agent_code": virtual_agent_code,
            "customer_id": easyassist_customer_id,
            "meta_data": {
                "product_details": {
                    "title": title,
                    "description": description,
                    "url": url
                }
            }
        });

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/initialize/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {

                    close_easyassist_browsing_modal();
                    set_easyassist_cookie("easyassist_session_id", response.session_id);

                    if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code == true || EASYASSIST_COBROWSE_META.show_verification_code_modal == false) {
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                    }else{
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }

                    if (EASYASSIST_COBROWSE_META.show_connect_confirmation_modal) {
                        show_connection_easyassist_modal();
                    }

                    // if (EASYASSIST_COBROWSE_META.get_sharable_link == true) {
                    //     var share_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/agent/" + response.session_id;
                    //     var message = share_url;
                    //     document.getElementById("easychat_share_link_Model-content_link_wrapper").value = message;
                    //     document.getElementById("easychat_share_link_Model").style.display = "block";
                    // }
                } else if (response.status == 103) {

                    document.getElementById("modal-cobrowse-connect-error").innerHTML = "Please enter code shared by our agent";

                } else{

                    console.error(response);

                }
            } else if (this.readyState == 4) {
                var description = "Initiate lead API (/easy-assist-salesforce/initialize/) failed with status code " + this.status.toString();
                document.getElementById("easyassist-co-browsing-connect-button").disabled = false;
                // save_easyassist_system_audit_trail("api_failure", description);
            }
            document.getElementById("easyassist-co-browsing-connect-button").disabled = false;
        }
        xhttp.send(params);
    }

    setInterval(function(e) {
        if (document.getElementById("easyassist-co-browsing-modal-id").style.display == "flex") {
            set_easyassist_user();
        }
    }, 5000);

    function set_easyassist_user() {

        var easyassist_customer_id = get_easyassist_cookie("easyassist_customer_id");
        if (easyassist_customer_id == null || easyassist_customer_id == undefined) {
            easyassist_customer_id = "None";
        }

        var full_name = "None";
        var mobile_number = "None";
        if (document.getElementById("easyassist-client-name") != null) {
            full_name = document.getElementById("easyassist-client-name").value.trim();
        }
        if (document.getElementById("easyassist-client-mobile-number") != null) {
            mobile_number = document.getElementById("easyassist-client-mobile-number").value.trim();
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

        json_string = JSON.stringify({
            "easyassist_customer_id": easyassist_customer_id,
            "full_name": full_name,
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

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/set-easyassist-customer/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    if (response.status == 200) {
                        var customer_id = response.customer_id;
                        set_easyassist_cookie("easyassist_customer_id", customer_id);
                    } else {
                        console.error(response);
                    }
                }
            } else if (this.readyState == 4) {
                var description = "set_easyassist_user api failed" + this.status.toString();
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

        var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

        if (window.location.hostname.split(".").length == 2) {
            domain = window.location.hostname;
        }

        if (window.location.protocol == "https:") {
            document.cookie = cookiename + "=" + cookievalue + ";path=/;domain=" + domain + ";secure";
        } else {
            document.cookie = cookiename + "=" + cookievalue + ";path=/;";
        }
        update_easyassist_url_history();
    }

    function get_easyassist_cookie(cookiename) {
        var matches = document.cookie.match(new RegExp(
            "(?:^|; )" + cookiename.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
        ));
        return matches ? matches[1] : undefined;
    }

    function delete_easyassist_cookie(cookiename) {

        var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

        if (window.location.hostname.split(".").length == 2) {
            domain = window.location.hostname;
        }

        if (window.location.protocol == "https:") {
            document.cookie = cookiename + "=;path=/;domain=" + domain + ";secure;expires = Thu, 01 Jan 1970 00:00:00 GMT";
        } else {
            document.cookie = cookiename + "=;path=/;expires = Thu, 01 Jan 1970 00:00:00 GMT";
        }
        update_easyassist_url_history();
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
        copyText.select();
        document.execCommand("copy");
        alert("Copied the text: " + copyText.value);
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

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/capture-lead/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
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
                var description = "Capture lead API (/easy-assist-salesforce/capture-lead/) failed with status code " + this.status.toString();
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
        iframe.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/sales-ai.html?id=" + EASYASSIST_COBROWSE_META.access_token;
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

        encrypted_data = custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/capture-lead/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
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
                var description = "Capture lead API (/easy-assist-salesforce/capture-lead/) failed with status code " + this.status.toString();
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
    }


    function connect_with_easyassist_agent_with_details(full_name, mobile_number) {

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

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/initialize/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
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
                var description = "Initiate lead API (/easy-assist-salesforce/capture-lead/) failed with status code " + this.status.toString();
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
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

        encrypted_data = custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/save-system-audit/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response.Response);
                response = JSON.parse(response);
            }
        }
        xhttp.send(params);
    }

    function create_easyassist_livechat_iframe() {
        iframe = document.createElement("iframe");
        iframe.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/sales-ai/client/livechat/?access_token=" + EASYASSIST_COBROWSE_META.access_token;
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
        agent_mouse_pointer.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/static/EasyAssistSalesforceApp/img/Agent_cursor.svg"
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
    
    function add_warning_element(reference_node){
        if(reference_node == null || reference_node == undefined)
            return;
        var focus_in_function = reference_node.getAttribute("onfocusin");
        if(focus_in_function == null || focus_in_function == undefined)
            focus_in_function = ""
        var focus_out_function = reference_node.getAttribute("onfocusout");
        if(focus_out_function == null || focus_out_function == undefined)
            focus_out_function = ""
        if(focus_in_function.split(';')[0] != "display_masked_field_warning(this)")
            reference_node.setAttribute("onfocusin", "display_masked_field_warning(this);" + focus_in_function);
        if(focus_out_function.split(';')[0] != "remove_masked_field_warning()")
            reference_node.setAttribute("onfocusout", "remove_masked_field_warning();" + focus_out_function);
    }

    function remove_warning_element(reference_node){
        if(reference_node == null || reference_node == undefined)
            return;
        var focus_in_function = reference_node.getAttribute("onfocusin");
        var focus_out_function = reference_node.getAttribute("onfocusout");
        if(focus_in_function == null || focus_in_function == undefined) {
            focus_in_function = ""
        } else {
            focus_in_function = focus_in_function.split(';')
            focus_in_function = focus_in_function.splice(1,focus_in_function.length).join(';')
        }
        if(focus_out_function == null || focus_out_function == undefined) {
            focus_out_function = ""
        } else {
            focus_out_function = focus_out_function.split(';')
            focus_out_function = focus_out_function.splice(1,focus_out_function.length).join(';')
        }
        if(focus_in_function.length == 0)
            reference_node.removeAttribute("onfocusin");
        else
            reference_node.setAttribute("onfocusin",focus_in_function);
        if(focus_out_function.length == 0)
            reference_node.removeAttribute("onfocusout");
        else
            reference_node.setAttribute("onfocusout",focus_out_function);
        
    }

    function add_masked_field_tooltip(){
        var warning = document.createElement("span");
        warning.innerHTML = EASYASSIST_COBROWSE_META.masked_field_warning_text;
        warning.setAttribute("class", "easyassist-tooltiptext");
        warning.style.display = "none";
        warning.style.cursor = "default";
        warning.style.fontSize = "11px";
        document.getElementsByTagName("body")[0].appendChild(warning);
    }

    function display_masked_field_warning(element){
        var dimensions = element.getBoundingClientRect();
        var warning_element =  document.getElementsByClassName("easyassist-tooltiptext")[0];
        if(warning_element == null || warning_element == undefined)
            return;
        warning_element.style.visibility = "visible";
        warning_element.style.opacity = "1";
        warning_element.style.left = (dimensions.left + element.offsetWidth/2 + window.scrollX - warning_element.offsetWidth/2) + "px";
        warning_element.style.top = (dimensions.top - element.offsetHeight + window.scrollY - 3) + "px";
    }

    function remove_masked_field_warning(){

        document.getElementsByClassName("easyassist-tooltiptext")[0].style.visibility = "hidden";
        document.getElementsByClassName("easyassist-tooltiptext")[0].style.opacity = "0";
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
    exports.connect_with_easyassist_agent = connect_with_easyassist_agent;
    exports.set_easyassist_cookie = set_easyassist_cookie;
    exports.get_easyassist_cookie = get_easyassist_cookie;
    exports.delete_easyassist_cookie = delete_easyassist_cookie;
    exports.show_easyassist_toast = show_easyassist_toast;
    exports.copy_text_to_clipboard_sharable_link_easyassist = copy_text_to_clipboard_sharable_link_easyassist;
    exports.hide_easyassist_feedback_form = hide_easyassist_feedback_form;
    exports.show_easyassist_feedback_form = show_easyassist_feedback_form;
    exports.hide_easyassist_agent_joining_modal = hide_easyassist_agent_joining_modal;
    exports.show_easyassist_agent_joining_modal = show_easyassist_agent_joining_modal;
    exports.hide_easyassist_agent_information_modal = hide_easyassist_agent_information_modal;
    exports.show_easyassist_agent_information_modal = show_easyassist_agent_information_modal;
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
    exports.connect_with_easyassist_agent_with_details = connect_with_easyassist_agent_with_details;
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
    exports.display_masked_field_warning = display_masked_field_warning;
    exports.remove_masked_field_warning = remove_masked_field_warning;

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
    //create_easyassist_hidden_iframe();
    create_easyassist_livechat_iframe();
    add_easyassist_request_edit_access();
    add_agent_mouse_pointer();
    set_easyassist_cookie("page_leave_status", "None");
    add_masked_field_tooltip();
    add_easyassist_agent_information_modal();


    if (EASYASSIST_COBROWSE_META.lead_generation) {
        setInterval(function(e) {
            add_easyassist_search_field_tag();
        }, 5000);
        add_easyassist_search_field_tag();
    }

    setInterval(function(e) {
        show_floating_sidenav_easyassist_button();
    }, 10000);

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

function change_verification_input_color(el) {
    el.style.setProperty('border-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    el.style.color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
}

function check_agent_available_status() {
    json_string = JSON.stringify({
        "access_token": window.EASYASSIST_COBROWSE_META.access_token
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/available-agent-list/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (EASYASSIST_COBROWSE_META.show_only_if_agent_available == true) {
                if (response.status == 200 && response.agent_available == true) {
                    EASYASSIST_COBROWSE_META.agents_available = true;
                    document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
                } else {
                    EASYASSIST_COBROWSE_META.agents_available = false;
                    hide_floating_sidenav_easyassist_button();
                }
            } else if (EASYASSIST_COBROWSE_META.disable_connect_button_if_agent_unavailable == true) {
                document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
                if (response.status == 200 && response.agent_available == false) {
                    EASYASSIST_COBROWSE_META.agents_available = false;
                    document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("title", EASYASSIST_COBROWSE_META.message_if_agent_unavailable);
                    document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "show_easyassist_toast('" + EASYASSIST_COBROWSE_META.message_if_agent_unavailable + "')");
                } else {
                    EASYASSIST_COBROWSE_META.agents_available = true;
                    document.getElementById("easyassist-side-nav-options-co-browsing").removeAttribute("title");
                    if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "show_easyassist_product_category_modal()");
                    } else {
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "show_easyassist_browsing_modal()");
                    }
                }
            } else {
                hide_floating_sidenav_easyassist_button();
            }
        } else if (this.readyState == 4 && this.status == 500) {
            hide_floating_sidenav_easyassist_button();
        }
    }
    xhttp.send(params);
}

if(EASYASSIST_COBROWSE_META.allow_video_meeting_only == true){
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id != "" || easyassist_session_id != null || easyassist_session_id != undefined){
        is_cobrowsing_meeting = setInterval(function(){
            check_cobrowsing_meeting_status()
        },60000)
    }
}


function check_cobrowsing_meeting_status() {
    if(window.EASYASSIST_COBROWSE_META.allow_video_meeting_only == false){
        return;
    }
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id == "" || easyassist_session_id == null || easyassist_session_id == undefined){
        return;
    }

    json_string = JSON.stringify({
        "session_id": easyassist_session_id,
    });

    encrypted_data = custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist-salesforce/check-cobrowsing-meeting-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (window.EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
                if (response.status == 200) {
                    delete_easyassist_cookie("easyassist_session_id")
                }
            }
        }
    }
    xhttp.send(params);
}