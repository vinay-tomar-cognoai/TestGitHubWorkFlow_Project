var lead_capture_initialted = false;
var longitude = null;
var latitude = null;
var agent_location ='Location not shared'
var agent_name = null
var easyassist_tickmarks_clicked=new Array(11).fill(false);
var is_recursive_call_ended = true;
var is_all_nodes_visited_for_first_time = false;
var document_readystate_interval = null;

var CUSTOMER_BROWSING_INTERVAL_TIME = 2;
var customer_browsing_interval = null;

var EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE = 500;
var EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE = "Due to some network issue, we are unable to process your request. Please Refresh the page.";
var easyassist_function_fail_time = 0;
var easyassist_function_fail_count = 0;
var easyassist_drawing_canvas = null;
var easyassist_drag_element = null;
var is_greeting_bubble_closed = false;
var is_request_from_greeting_bubble = false;
var is_request_from_exit_intent = false;
var is_request_from_button = false;
const REGEX_AGENT_CODE = /^[0-9a-zA-Z]+$/;

/* This is done for the IOS specific devices, 
In IOS devices after interacting with the DOM the audio was not playing, 
to fix this issue we simply play and stop the audio when the user touch the screen for the first time, so this will 
trigger the audio file initially and will allow the audio to play after that.*/
document.body.addEventListener('touchstart', function() {
    let audio_element = document.getElementById("easyassist-greeting-bubble-popup-sound");
    if(audio_element) {
        audio_element.play()
        audio_element.pause()
        audio_element.currentTime = 0
    }
}, false);

/* This is done for the IOS specific devices, 
In IOS devices after interacting with the DOM the audio was not playing, 
to fix this issue we simply play and stop the audio when the user touch the screen for the first time, so this will 
trigger the audio file initially and will allow the audio to play after that.*/
document.body.addEventListener('touchstart', function() {
    let audio_element = document.getElementById("easyassist-greeting-bubble-popup-sound");
    if(audio_element) {
        audio_element.play()
        audio_element.pause()
        audio_element.currentTime = 0
    }
}, false);

document.addEventListener("mouseout", function(e) {
    if ((e.clientY < 0 || e.clientX < 0) && (get_easyassist_cookie("easyassist_session_id") == undefined)) {
        if(window.EASYASSIST_COBROWSE_META.allow_popup_on_browser_leave == true && get_easyassist_cookie("page_leave_status") == "None" && check_exit_intent_access()) {
            if(easyassist_time_to_show_support_button() == true) {
                if(EASYASSIST_COBROWSE_META.enable_recursive_browser_leave_popup == false) {
                    set_exit_intent_counter_cookie();
                    let open_modal_element = document.getElementById("easyassist-co-browsing-modal-id");
                    if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
                        open_modal_element = document.getElementById("easyassist-product-category-modal-id");
                    }
                    
                    if(parseInt(get_easyassist_cookie("no_of_time_exit_modal_popup")) < window.EASYASSIST_COBROWSE_META.no_of_times_exit_intent_popup) {
                        if (open_modal_element.style.display != "flex") {
                            easyassist_check_agent_available_status(easyassist_show_cobrowsing_modal);
                            increment_exit_intent_modal_popup_count();
                            is_request_from_exit_intent = true;
                            is_request_from_greeting_bubble = false;
                            is_request_from_inactivity_popup = false;
                            is_request_from_button = false;
                        }
                    } else {
                        set_easyassist_cookie("page_leave_status", "true");
                    }
                } else {
                    easyassist_check_agent_available_status(easyassist_show_cobrowsing_modal);
                    is_request_from_exit_intent = true;
                    is_request_from_greeting_bubble = false;
                    is_request_from_inactivity_popup = false;
                    is_request_from_button = false;
                }
            }
        }
    }
    
    if ((e.clientY < 0 || e.clientX < 0) && EASYASSIST_COBROWSE_META.no_agent_connects_toast && window.EASYASSIST_COBROWSE_META.allow_popup_on_browser_leave == true && check_exit_intent_access()) {
        set_only_single_exit_intent_cookie();
        var agent_connected_cookie = get_easyassist_cookie("easyassist_agent_connected");
        var session_creation_mode = get_easyassist_cookie("easyassist_session_created_on");
        if (agent_connected_cookie != "true" && session_creation_mode == "request" && !is_easyassist_connection_timer_closed()) {
            if(EASYASSIST_COBROWSE_META.enable_recursive_browser_leave_popup == false){
                var minimized_modal_ele = document.getElementById("easyassist-minimized-connection-timer-modal-id");
                if(parseInt(get_easyassist_cookie("count_of_time_exit_modal_popup")) > 0) {
                    easyassist_hide_minimized_timer_modal();
                    easyassist_show_connection_with_timer_modal();
                    decrement_single_exit_intent_modal_popup_count();
                }
            } else {
                if(parseInt(get_easyassist_cookie("count_of_time_exit_modal_popup")) > 0) {
                    easyassist_hide_minimized_timer_modal();
                    easyassist_show_connection_with_timer_modal();
                    decrement_single_exit_intent_modal_popup_count();
                }
            }
        }
    }
}, false);

function check_exit_intent_access() {
    if (EASYASSIST_COBROWSE_META.enable_url_based_exit_intent_popup) {
        // ignoring the get request params in the url
        let customer_url = window.location.href.split("?")[0]
        return JSON.parse(EASYASSIST_COBROWSE_META.exit_intent_popup_urls).indexOf(customer_url) != -1;
    }
    return true;
}

function increment_exit_intent_modal_popup_count() {
    let exit_intent_count = parseInt(get_easyassist_cookie("no_of_time_exit_modal_popup"));
    exit_intent_count = exit_intent_count + 1;
    set_easyassist_cookie("no_of_time_exit_modal_popup", exit_intent_count.toString());
}

function set_exit_intent_counter_cookie() {
    let exit_intent_cookie_value = get_easyassist_cookie("no_of_time_exit_modal_popup");
    if (exit_intent_cookie_value == undefined || exit_intent_cookie_value == null) {
        set_easyassist_cookie("no_of_time_exit_modal_popup", "0");
    }
}

function decrement_single_exit_intent_modal_popup_count() {
    let single_exit_intent_count = parseInt(get_easyassist_cookie("count_of_time_exit_modal_popup"));
    single_exit_intent_count = single_exit_intent_count - 1;
    set_easyassist_cookie("count_of_time_exit_modal_popup", single_exit_intent_count.toString());
}

function set_only_single_exit_intent_cookie() {
    let single_exit_intent_cookie_value = get_easyassist_cookie("count_of_time_exit_modal_popup");
    if (single_exit_intent_cookie_value == undefined || single_exit_intent_cookie_value == null) {
        set_easyassist_cookie("count_of_time_exit_modal_popup", "1");
    }
}

/****** Setting and Decrementing the Auto Assign Timer Counter *******/

function decrement_repeted_text_count() {
    let repeated_text_count = parseInt(get_easyassist_cookie("no_of_times_default_text_on_modal"));
    repeated_text_count = repeated_text_count - 1;
    set_easyassist_cookie("no_of_times_default_text_on_modal", repeated_text_count.toString());
}

function set_repeted_text_count_cookie() {
    let repeated_text_count = get_easyassist_cookie("no_of_times_default_text_on_modal");
    if (repeated_text_count == undefined || repeated_text_count == null) {
        set_easyassist_cookie("no_of_times_default_text_on_modal", "1");
    }
}

setTimeout(() => {
    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    if(local_storage_obj && local_storage_obj.hasOwnProperty("hide_customer_call_initiation_icon")) {
        if(local_storage_obj["hide_customer_call_initiation_icon"] == "true") {
            show_customer_side_call_icon(false);
        }
    }

    if(local_storage_obj && local_storage_obj.hasOwnProperty("agent_details_json")) {
        var agent_details_json = JSON.parse(local_storage_obj["agent_details_json"]);
        easyassist_update_agent_location_detail(agent_details_json);
    }
}, 1500);

/***************** EasyAssist Custom Select ***********************/

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.background_color = background_color;

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
        select_element.style.display = "none";

        select_element.parentNode.insertBefore(custom_dropdown_wrapper, select_element);
        custom_dropdown_wrapper.appendChild(select_element)

        if(this.placeholder){
            select_element.selectedIndex = -1;
        }

        for(let idx = 0; idx < select_element.children.length; idx ++) {
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

/***************** EasyAssist Canvas ***********************/

class EasyAssistCanvas {
    constructor(canvas_element, color, line_width) {
        this.canvas = canvas_element;

        this.canvas.setAttribute("data-canvas", "easyassist-canvas");
        this.ctx = this.canvas.getContext("2d");
        this.color = color;
        this.line_width = line_width;
        this.reset_canvas_timer = null;
    }

    draw_dot(curr_x, curr_y, line_width) {
        this.ctx.beginPath();
        this.ctx.fillStyle = this.color;
        this.ctx.arc(curr_x, curr_y, line_width / 2, 0, 2 * Math.PI, true);
        this.ctx.fill();
        this.ctx.closePath();

        this.start_clear_canvas_interval();
    }

    draw_line(prev_x, prev_y, curr_x, curr_y, line_width) {
        this.ctx.lineCap = "round";
        this.ctx.beginPath();
        this.ctx.moveTo(prev_x, prev_y);
        this.ctx.lineTo(curr_x, curr_y);
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = line_width;
        this.ctx.stroke(); 
        this.ctx.closePath();

        this.start_clear_canvas_interval();
    }

    reset_canvas(points_queue) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.reset_clear_canvas_interval();
    }

    resize_canvas(width, height) {
        this.canvas.width = width;
        this.canvas.height = height;
    }

    start_clear_canvas_interval() {
        var _this = this;

        _this.reset_clear_canvas_interval();

        _this.reset_canvas_timer = setTimeout(function() {
            _this.reset_canvas();
        }, 6000);
    }

    reset_clear_canvas_interval() {
        var _this = this;

        if(_this.reset_canvas_timer != null) {
            clearTimeout(_this.reset_canvas_timer);
            _this.reset_canvas_timer = null;
        }
    }
}

/***************** EasyAssist Drag Element ***********************/

class EasyAssistDragElement {
    constructor(element) {
        this.element = element;
        this.element.setAttribute("data-easyassist-drag", "true");
        this.element.style.cursor = "move";
        this.horizontal_flip_selector_list = ["span", "svg", "iframe", "#easyassist-minimized-timer-modal-connect"];
        this.currX = 0;
        this.currY = 0;
        this.offset = 12;
        this.is_dragging = false;
        this.drag_container = null;
        this.prevX = 0;
        this.prevY = 0;

        var _this = this;
        _this.element.addEventListener("mousedown", function(e) {
            _this.drag_element('down', e);
        });

        _this.element.addEventListener("mouseup", function(e) {
            _this.drag_element('up', e);
        });

        document.addEventListener("mouseleave", function(e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.element.addEventListener("touchstart", function(e) {
            _this.prevX = e.touches[0].clientX;
            _this.prevY = e.touches[0].clientY;
            _this.drag_element('down', e);
        });

        _this.element.addEventListener("touchmove", function(e) {
            _this.prevX = e.touches[0].clientX;
            _this.prevY = e.touches[0].clientY;
            _this.mousemove_handler(e);
        });

        _this.element.addEventListener("touchend", function(e) {
            _this.prevX = 0;
            _this.prevY = 0;
            _this.drag_element('out', e);
        });
    }

    set_drag_container() {
        if(easyassist_get_eles_by_class_name("easyassist-drag-element").length) {
            return;
        }

        this.drag_container = document.createElement("div");
        this.drag_container.classList.add("easyassist-drag-element");
        this.drag_container.style.position = "absolute";
        this.drag_container.setAttribute("easyassist_avoid_sync", "true");
        this.drag_container.style.top = "0";
        this.drag_container.style.left = "0";
        this.drag_container.style.width = "100%";
        this.drag_container.style.height = "100%";
        this.drag_container.style.zIndex = "2147483600";

        var _this = this;
        _this.drag_container.addEventListener("mousemove", function(e) {
            _this.mousemove_handler(e);
        });

        _this.drag_container.addEventListener("mouseup", function(e) {
            _this.drag_element('up', e);
        });

        _this.element.classList.add("cobrowsing-moving");
        document.body.appendChild(this.drag_container);
    }

    remove_drag_container() {
        this.element.classList.remove("cobrowsing-moving");
        if(!this.drag_container) {
            return;
        }
        this.drag_container.remove();
        this.drag_container = null;
    }

    mousemove_handler(e){
        e.preventDefault();
        if (this.is_dragging) {

            let originalStyles = window.getComputedStyle(this.element);
            this.currX = e.movementX + parseInt(originalStyles.left);
            this.currY = e.movementY + parseInt(originalStyles.top)

            this.drag();
        }
    }

    drag_element(direction, e) {
        if (direction == 'down') {

            this.is_dragging = true;
            this.set_drag_container();
        }

        if (direction == 'up' || direction == "out") {
            if(this.is_dragging == false) {
                return;
            }

            this.is_dragging = false;
            this.remove_drag_container();
            this.relocate_element();
        }
    }

    drag(horizontal_flip = false) {
        this.currX = Math.max(this.currX, 0);

        this.element.style.setProperty("left", this.currX + "px", "important");
        this.element.style.setProperty("top", this.currY + "px", "important");

        if(horizontal_flip) {
            this.flip_element_horizontally("-1");
        } else {
            this.flip_element_horizontally("1");
        }
    }

    flip_element_horizontally(offset) {
        this.element.style.transform = "scaleX(" + offset + ")";
        for(let index = 0; index < this.horizontal_flip_selector_list.length; index ++) {
            var selector = this.horizontal_flip_selector_list[index];
            var tooltip_spans = this.element.querySelectorAll(selector);
            for(let idx = 0; idx < tooltip_spans.length; idx ++) {
                tooltip_spans[idx].style.transform = "scaleX(" + offset + ")";
            }
        }
    }

    relocate_element() {
        var top = this.element.offsetTop;
        var left = this.element.offsetLeft;
        var flip_horizontal = false;

        if(top > window.innerHeight / 2) {
            top = window.innerHeight - this.element.clientHeight - this.offset;
        } else {
            top = this.offset;
        }

        if(left > window.innerWidth / 2) {
            var scrollbar_width = window.innerWidth - document.body.clientWidth;
            left = window.innerWidth - this.element.clientWidth - scrollbar_width;
            left = Math.max(left, 0);

            if(left != 0) {
                flip_horizontal = true;
            }
        } else {
            left = 0;
        }

        this.currX = left;
        this.currY = top;
        this.drag(flip_horizontal);

        var offset_left = this.element.getAttribute("data-left-offset");
        if(offset_left != null && offset_left != undefined) {
            if(flip_horizontal) {
                this.element.style.setProperty("margin-left", "-1rem", "important");
            } else {
                this.element.style.setProperty("margin-left", "1rem", "important");
            }
        }
    }
}

function easyassist_find_light_color(color, percent) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R<255)?R:255;  
    G = (G<255)?G:255;  
    B = (B<255)?B:255;  

    var RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
    var GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
    var BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));

    return "#"+RR+GG+BB;
}

function easyassist_find_light_color_by_opacity(color, opacity) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);
    var rgba_color = "rgba(" + R + "," + G + "," + B + "," + opacity + ")";
    return rgba_color;
}

function easyassist_show_tooltip(el) {
    el.querySelector('label').style.display = "inline-block";
}

function easyassist_hide_tooltip(el) {
    el.querySelector('label').style.display = "none";
}

function add_easyassist_event_listner_into_element(html_element, event_type, target_function){
    html_element.removeEventListener(event_type, target_function);
    html_element.addEventListener(event_type, target_function);
}

function remove_easyassist_event_listner_into_element(html_element, event_type, target_function){
    html_element.removeEventListener(event_type, target_function);
}

function easyassist_convert_urls_to_absolute(nodeList) {

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
        if (!attr) {
            return;
        }

        var absURL = /^(https?|data):/i.test(attr);
        if (absURL) {
            return el;
        } else {
            if(el[attrName]) {
                el.setAttribute(attrName, el[attrName]);
            }

            return el;
        }
    });
    return nodeList;
}

function easyassist_create_proxy_server_pass_urls(nodeList) {

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
        if (!attr) {
            return;
        }

        var absURL = /^(https?|data):/i.test(attr);
        if (absURL) {
            if (/^(data):/i.test(attr)) {
                el.setAttribute(attrName, attr);
            } else {
                attr = EASYASSIST_COBROWSE_META.proxy_server + attr
                el.setAttribute(attrName, attr);
            }
        } else {
            el.setAttribute(attrName, EASYASSIST_COBROWSE_META.proxy_server + el[attrName]);
        }
        return el;
    });
    return nodeList;
}

function set_easyassist_cookie(cookiename, cookievalue) {

    var domain = window.location.hostname;
    var max_age = 24 * 60 * 60;

    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;domain=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";max-age=" + max_age + ";path=/;";
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

function set_easyassist_cookie_with_path(cookiename, cookievalue) {

    var domain = window.location.pathname;
    var date = easyassist_expire_midnight_cookie();
    if (window.location.protocol == "https:") {
        document.cookie = cookiename + "=" + cookievalue + ";expires=" + date + ";path=" + domain + ";secure";
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";expires=" + date + ";path=" + domain;
    }
}

function easyassist_expire_midnight_cookie(name, value, path)
{
    var now = new Date();
    var expire = new Date();
    expire.setFullYear(now.getFullYear());
    expire.setMonth(now.getMonth());
    expire.setDate(now.getDate()+1);
    expire.setHours(0);
    expire.setMinutes(0);
    return expire.toGMTString();
}

function create_easyassist_local_storage_object(session_id) {
    let local_storage_obj = localStorage.getItem("easyassist_session")
    if(local_storage_obj == null) {
       var local_storage_json_object = {};
        local_storage_json_object[session_id] = {};
        localStorage.setItem("easyassist_session", JSON.stringify(local_storage_json_object));
    }
}

function get_easyassist_current_session_local_storage_obj() {
    let local_storage_obj = null;
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if(localStorage.getItem("easyassist_session") != null) {
        local_storage_obj = localStorage.getItem("easyassist_session");
        local_storage_obj = JSON.parse(local_storage_obj);
        if(local_storage_obj.hasOwnProperty(easyassist_session_id)) {
            local_storage_obj = local_storage_obj[easyassist_session_id];
        }
    }
    return local_storage_obj;
}

function set_easyassist_current_session_local_storage_obj(key, value) {
    try{
        let local_storage_obj = localStorage.getItem("easyassist_session");
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if(local_storage_obj) {
            local_storage_obj = JSON.parse(local_storage_obj);
            local_storage_obj[easyassist_session_id][key] = value;
            localStorage.setItem("easyassist_session", JSON.stringify(local_storage_obj));
        }
    }catch(err){
        console.log("ERROR: set_easyassist_current_session_local_storage_obj ", err);
    }
}

function easyassist_prevent_non_numeric_characters(event) {
    var blacklisted_keycode = [69, 107, 109, 110, 187, 189, 190];
    if(blacklisted_keycode.includes(event.keyCode)) {
        event.preventDefault();
    }
}

function easyassist_prevent_space_input(event) {
    if (event.keyCode == 32) {
        easyassist_show_toast("Please enter an agent code without spaces");
        event.preventDefault();
    }
}

function easyassist_get_last_char_keycode(input_str) {
    return input_str.charCodeAt(input_str.length - 1);
}

function easyassist_prevent_space_oninput(event) {
    let keycode_value = easyassist_get_last_char_keycode(event.target.value);
    if(keycode_value == 32) {
        event.target.value = event.target.value.replace(/\s/g, ""); 
        easyassist_show_toast("Please enter an agent code without spaces");
    }
}

function easyassist_prevent_space_paste(event) {
    let easyassist_pasted_data_agent_code = (event.clipboardData || window.clipboardData).getData('text');
    if(easyassist_pasted_data_agent_code.indexOf(' ') > -1) {
        easyassist_show_toast("Please enter an agent code without spaces");
        event.preventDefault();
    }
}

function easyassist_phone_number_paste_handler(event) {
    let easyassist_pasted_data = (event.clipboardData || window.clipboardData).getData('text');
    if(easyassist_pasted_data.indexOf('.') > -1) {
        event.preventDefault();
    }
}

function easyassist_verification_input_color_change(el) {
    el.style.setProperty('border-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    el.style.color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
}

function easyassist_feedback_icon_color_change(element) {

    let rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    let rating_spans = rating_bar.querySelectorAll("span");

    for(let index = 0; index < rating_spans.length; index ++) {
        if(!easyassist_tickmarks_clicked[index]) {
            rating_spans[index].style.color = '#2D2D2D';
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.border = "1px solid #E6E6E6";
        }
    }
}

function easyassist_time_to_show_support_button() {

    var currentTime = new Date();
    var current_day = currentTime.getDay();

    if(!EASYASSIST_COBROWSE_META.is_working_day) {
        return false;
    }

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

function easyassist_show_emoji_on_rating_change(element, user_rating) {

    rating_spans = element.parentNode.children;
    for (let index = 0; index < rating_spans.length; index ++) {
        if (parseInt(rating_spans[index].innerHTML) <= user_rating) {
            if(index <= 6){
                rating_spans[index].style.background = 'rgba(255, 70, 70, 1)';
            } else if( index <= 8){
                rating_spans[index].style.background = 'rgba(255, 153, 0, 1)';
            } else {
                rating_spans[index].style.background = 'rgba(5, 178, 54, 1)';
            }
            rating_spans[index].style.border = "none";
            // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
            rating_spans[index].style.color = "#fff";
        } else if(!easyassist_tickmarks_clicked[index]){
            rating_spans[index].style.border = "1px solid #E6E6E6";
            rating_spans[index].style.background = "unset";
            rating_spans[index].style.color = '#2D2D2D';

        }
    }
}

function easyassist_rate_agent(element) {
    let rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    let rating_spans = rating_bar.querySelectorAll("span");
    let user_rating = parseInt(element.innerHTML);

    for(let index = 0; index <= user_rating; index ++) {
        if(index <= 6){
            rating_spans[index].style.background = 'rgba(255, 70, 70, 1)';
        } else if( index <= 8){
            rating_spans[index].style.background = 'rgba(255, 153, 0, 1)';
        } else {
            rating_spans[index].style.background = 'rgba(5, 178, 54, 1)';
        }
        // rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        rating_spans[index].style.color = "#fff";
        easyassist_tickmarks_clicked[index] = true;
        rating_spans[index].style.border = "none";
    }

    for(let index = user_rating + 1; index < rating_spans.length; index ++) {
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = '#2D2D2D';
        easyassist_tickmarks_clicked[index] = false;
        rating_spans[index].style.border = "1px solid #E6E6E6";
    }
}

function easyassist_reset_rating_bar() {
    let rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    let rating_spans = rating_bar.querySelectorAll("span");
    for (let index = 0; index < rating_spans.length; index++) {
        rating_spans[index].style.background = "unset";
        rating_spans[index].style.color = '#2D2D2D';
        rating_spans[index].style.border = "1px solid #E6E6E6";
        easyassist_tickmarks_clicked[index] = false;
    }
}

function easyassist_get_user_rating() {
    let user_rating = null;
    for(let idx = 0; idx < easyassist_tickmarks_clicked.length; idx ++) {
        if(easyassist_tickmarks_clicked[idx] == true) {
            user_rating = idx;
        } else {
            break;
        }
    }
    return user_rating;
}

function easyassist_word_limit(event, element, max_count){
    var value = element.value;
    var count = value.length;

    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= max_count){
            event.preventDefault(); // Cancel event
        }
    }
}

window.addEventListener('message', function(event) {
    // IMPORTANT: Check the origin of the data!

    if (~event.origin.indexOf(EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST)) {
        let data = {};
        try {
            data = JSON.parse(event.data);
        } catch (error) {}

        if (data.event_id == "collect-cookie-updates") {
            if (data != "None") {
                data = atob(data.eacSession);
                try {
                    data = JSON.parse(data);
                    if (data.hostname != window.location.hostname) {
                        delete data["hostname"];
                        for (let cookie_name in data) {
                            console.log(cookiename, data[cookiename]);
                            set_easyassist_cookie(cookie_name, data[cookie_name]);
                        }
                    }
                } catch (error) {
                    console.warn("unable to decode session details.");
                }
            }
        } else if(data.event_id == "open_pdf_render_modal"){
            easyassist_hide_livechat_iframe();
            easyassist_send_close_agent_chatbot_over_socket();
            easyassist_show_chat_bubble();
            easyassist_show_pdf_render_modal(data.file_name,data.file_src,data.session_id);

        }
        else if (data.event_id == "close-bot") {
            easyassist_hide_livechat_iframe();
            if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
                document.querySelector(".chat-talk-bubble").style.display = "none";
                document.getElementById("chat-minimize-icon-wrapper").style.display = "none";
            }
        } else if (data.event_id == "cobrowsing-client-chat-message") {
            let message = data.data.message;
            let attachment = data.data.attachment;
            let attachment_file_name = data.data.attachment_file_name;
            easyassist_send_livechat_message_to_agent(message, attachment, attachment_file_name);
        } else if (event.data.event_id === "livechat-typing") {
            easyassist_send_livechat_typing_indication()
        } else if(data.event_id == "minimize-chatbot") {
            document.querySelector(".chat-talk-bubble").style.display = "none";
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
        }

        if(event.data == "voip_meeting_ready") {
            easyassist_send_voip_meeting_ready_over_socket();
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
            easyassist_reset_voip_meeting();
        }

        if(event.data.event == "voip_audio_status") {
            if(event.data.is_muted) {
                document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = 'none';
                document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = '';
            } else {
                document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = 'none';
                document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = '';
            }

            set_easyassist_cookie("is_meeting_audio_muted", event.data.is_muted);
        }

        if(event.data.event == "voip_function_error") {
            easyassist_show_function_fail_modal(code=event.data.error_code);
        }

        if(event.data.event == "voip_video_status") {
            if(event.data.is_muted) {
                document.getElementById("easyassist-client-meeting-video-off-btn").style.display = 'none';
                document.getElementById("easyassist-client-meeting-video-on-btn").style.display = '';
            } else {
                document.getElementById("easyassist-client-meeting-video-on-btn").style.display = 'none';
                document.getElementById("easyassist-client-meeting-video-off-btn").style.display = '';
            }
        }
    } else {
        return;
    }
});

/******************************* Custom EasyAssist Utils Functions *******************************************/

function easyassist_get_eles_by_class_name(clsName, target_doc=document){
    var retVal = [];
    try {
        retVal = target_doc.getElementsByClassName(clsName);
    } catch(err) {
        retVal = new Array();
        var elements = target_doc.getElementsByTagName("*");
        for(let i = 0; i < elements.length; i++) {
            if(elements[i].className){
                if(typeof(elements[i].className) != "string"){
                    continue;
                }
                if(elements[i].className.indexOf(clsName) > -1){
                    retVal.push(elements[i]);
                }
            }
        }
    }

    return retVal;

}

/******************************* Time before clicked on "Connect" button. *******************************************/

function easyassist_set_customer_browsing_time(){
    let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

    if (easyassist_session_id != null && easyassist_session_id != undefined && easyassist_session_id != "") {
        clearInterval(customer_browsing_interval)
        return;
    }

    var easyassist_customer_browsing_time = get_easyassist_cookie("easyassist_customer_browsing_time");
    if(easyassist_customer_browsing_time == null || easyassist_customer_browsing_time == undefined){
        easyassist_customer_browsing_time = 0;
    }else{
        easyassist_customer_browsing_time = parseInt(easyassist_customer_browsing_time);
    }
    easyassist_customer_browsing_time += CUSTOMER_BROWSING_INTERVAL_TIME;
    set_easyassist_cookie("easyassist_customer_browsing_time", easyassist_customer_browsing_time)
}

(function(exports) {

    var search_html_field = window.EASYASSIST_COBROWSE_META.search_html_field;
    var obfuscated_fields = window.EASYASSIST_COBROWSE_META.obfuscated_fields;
    var custom_select_removed_fields = window.EASYASSIST_COBROWSE_META.custom_select_removed_fields;
    // window.easyassist_element_id_counter = 0;
    // window.easyassist_total_low_bandwidth_elements = 0;
    window.easyassist_close_nav_timeout = null;
    window.EASYASSIST_TAG_VALUE = "easyassist-tag-value";

    function easyassist_add_root_style_variable(){
        var root_style = ['<style>',
            ':root {',
                '--easyassist_color_rgb:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + ';',
                '--easyassist_font_family:' + EASYASSIST_COBROWSE_META.easyassist_font_family + ';',
            '}',
            '</style>',
        ].join('')

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', root_style);
    }

    function remove_easyassist_attr_value_from_document() {
        let document_input_tag_list = document.querySelectorAll("input");
        for (let d_index = 0; d_index < document_input_tag_list.length; d_index++) {
            document_input_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
        let document_select_tag_list = document.querySelectorAll("select");
        for (let d_index = 0; d_index < document_select_tag_list.length; d_index++) {
            document_select_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
        let document_textarea_tag_list = document.querySelectorAll("textarea");
        for (let d_index = 0; d_index < document_textarea_tag_list.length; d_index++) {
            document_textarea_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }
    }

    function easyassist_set_scroll_into_document() {
        let div_elements = document.querySelectorAll("div");
        for (let index = 0; index < div_elements.length; index++) {
            let div_ele = div_elements[index];
            div_ele.setAttribute("easyassist-data-scroll-x", div_ele.scrollLeft);
            div_ele.setAttribute("easyassist-data-scroll-y", div_ele.scrollTop);
        }
    }

    function easyassist_add_canvas_tag_into_document() {
        let canvas_elements = document.getElementsByTagName("canvas");
        for (let index = 0; index < canvas_elements.length; index++) {
            canvas_elements[index].setAttribute("easyassist-canvas-id", index);
        }
    }

    function easyassist_convert_canvas_into_image(screenshot) {
        let canvas_elements = screenshot.getElementsByTagName("canvas");
        for (let index = 0; index < canvas_elements.length; index++) {
            let easyassist_canvas_id = canvas_elements[index].getAttribute("easyassist-canvas-id");
            let doc_element = document.querySelector("[easyassist-canvas-id='" + easyassist_canvas_id + "']");

            let data_url = doc_element.toDataURL("img/png");
            let img_tag = document.createElement("img");
            img_tag.src = data_url;
            canvas_elements[index].style.display = "none";
            canvas_elements[index].parentElement.appendChild(img_tag);
        }
    }

    function easyassist_remove_blocked_html_tags(screenshot) {
        let blocked_html_tags = EASYASSIST_COBROWSE_META.blocked_html_tags;
        if (blocked_html_tags.length == 0) {
            return;
        }

        for (let b_index = 0; b_index < blocked_html_tags.length; b_index++) {
            let selected_blocked_html_tags = screenshot.querySelectorAll(blocked_html_tags[b_index]);
            for (let index = 0; index < selected_blocked_html_tags.length; index++) {
                let blocked_tag_id = selected_blocked_html_tags[index].getAttribute("id");
                if (blocked_tag_id != null && blocked_tag_id != undefined) {
                    continue;
                }
                selected_blocked_html_tags[index].parentNode.removeChild(selected_blocked_html_tags[index]);
            }
        }
    }

    function easyassist_disable_button_elements(screenshot) {
        let disable_fields = EASYASSIST_COBROWSE_META.disable_fields;
        if (disable_fields.length == 0) return;
        let button_elements = screenshot.querySelectorAll("button");
        for (let index = 0; index < button_elements.length; index++) {
            for (let f_index = 0; f_index < disable_fields.length; f_index++) {
                let attr_value = button_elements[index].getAttribute(disable_fields[f_index].key);
                if (attr_value != null && attr_value != undefined && attr_value == disable_fields[f_index].value) {
                    button_elements[index].disabled = true;
                    button_elements[index].onclick = null;
                    button_elements[index].style.setProperty("background-color", "#808080", "important");
                    button_elements[index].style.setProperty("background-image", "unset", "important");
                }
            }
        }

        let a_tag_elements = screenshot.querySelectorAll("a");
        for (let index = 0; index < a_tag_elements.length; index++) {
            for (let f_index = 0; f_index < disable_fields.length; f_index++) {
                let attr_value = a_tag_elements[index].getAttribute(disable_fields[f_index].key);
                if (attr_value != null && attr_value != undefined && attr_value == disable_fields[f_index].value) {
                    a_tag_elements[index].removeAttribute("href");
                    a_tag_elements[index].onclick = null;
                }
            }
        }

        let input_tag_elements = screenshot.querySelectorAll("input");
        for (let index = 0; index < input_tag_elements.length; index++) {
            for (let f_index = 0; f_index < disable_fields.length; f_index++) {
                let attr_value = input_tag_elements[index].getAttribute(disable_fields[f_index].key);
                if (attr_value != null && attr_value != undefined && attr_value == disable_fields[f_index].value) {
                    input_tag_elements[index].onclick = null;
                    input_tag_elements[index].disabled = true;
                    input_tag_elements[index].style.setProperty("background-color", "#808080", "important");
                    input_tag_elements[index].style.setProperty("background-image", "unset", "important");
                }
            }
        }
    }

    function easyassist_add_ripple_animation_frame() {

        var span = document.createElement("span");
        span.id = "easyassist-ripple_effect";
        span.style.height = "45px";
        span.style.width = "45px";
        span.style.border = "4px solid red";
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

    function easyassist_show_ripple_effect(clientX, clientY) {
        if (show_ripple_timer != null) {
            clearTimeout(show_ripple_timer);
        }
        var span = document.getElementById("easyassist-ripple_effect");
        easyassist_hide_ripple_effect();
        span.style.display = "inline-block";
        span.style.top = clientY + "px";
        span.style.left = clientX + "px";
        show_ripple_timer = setTimeout(function(e) {
            easyassist_hide_ripple_effect();
        }, 2000);
    }

    function easyassist_hide_ripple_effect() {
        var span = document.getElementById("easyassist-ripple_effect");
        if(span){
            span.style.display = "none";
        }
    }

    function easyassist_add_connection_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-conection-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
        	'<div class="easyassist-customer-connect-modal-content">',
        		'<div class="easyassist-customer-connect-modal-header">',
        			'<h6>Connect with our experts</h6>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-body">',
        			 EASYASSIST_COBROWSE_META.message_on_connect_confirmation_modal,
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-footer">',
        			'<button class="easyassist-modal-primary-btn" onclick="easyassist_close_connection_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">OK</button>',
        		'</div>',
        	'</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_add_connection_timer_reset_modal() {
        if(!EASYASSIST_COBROWSE_META.no_agent_connects_toast) {
            return;
        }

        var div_model = document.createElement("div");
        div_model.id = "easyassist-conection-timer-reset-modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
        	'<div class="easyassist-customer-connect-modal-content">',
        		'<div class="easyassist-customer-connect-modal-header">',
        			'<h6>Agents are busy</h6>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-body">',
        			 EASYASSIST_COBROWSE_META.no_agent_connects_toast_reset_message,
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-footer">',
        			'<button class="easyassist-modal-primary-btn" onclick="easyassist_close_connection_timer_reset_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">Ok</button>',
        		'</div>',
        	'</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        easyassist_initialize_modal_reset_timer_count();
    }

    function easyassist_initialize_modal_reset_timer_count() {
        let timer_modal_reset_count = get_easyassist_cookie("timer_modal_reset_count");
        if(timer_modal_reset_count == null || timer_modal_reset_count == undefined) {
            set_easyassist_cookie("timer_modal_reset_count", 0);
        }
        
        let is_timer_iterations_elapsed = get_easyassist_cookie("is_timer_iterations_elapsed");
        if(is_timer_iterations_elapsed == null || is_timer_iterations_elapsed == undefined) {
            set_easyassist_cookie("is_timer_iterations_elapsed", "false");
        }
    }

    function easyassist_add_connection_with_timer_modal() {

        var waiting_time_seconds, modal_body_text, modal_header_text;
        var timer_color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_timer_value")) {
            waiting_time_seconds = parseInt(local_storage_obj["easyassist_timer_value"]);
            if (waiting_time_seconds <= 15) {
                timer_color = "#E53E3E";
            }
        } else {
            waiting_time_seconds = EASYASSIST_COBROWSE_META.no_agent_connects_toast_threshold * 60;
        }

        if(local_storage_obj && local_storage_obj["easyassist_initial_timer_exhausted"] == "true") {
            modal_header_text = "Thank you for your patience, our agent will connect you";
            if(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_agent_reassigned")) {
                if(local_storage_obj["easyassist_agent_reassigned"] == "true" && EASYASSIST_COBROWSE_META.enable_auto_assign_unattended_lead) {
                    modal_body_text = EASYASSIST_COBROWSE_META.auto_assign_unattended_lead_message;
                } else {
                    modal_body_text = EASYASSIST_COBROWSE_META.no_agent_connects_toast_text;    
                }
            } else {
                modal_body_text = EASYASSIST_COBROWSE_META.no_agent_connects_toast_text;
            }
        } else {
            modal_header_text = "Connecting you to our expert";

            if(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_agent_reassigned")) {
                if(local_storage_obj["easyassist_agent_reassigned"] == "true" && EASYASSIST_COBROWSE_META.enable_auto_assign_unattended_lead) {
                    modal_body_text = EASYASSIST_COBROWSE_META.auto_assign_unattended_lead_message;
                } else {
                    modal_body_text = EASYASSIST_COBROWSE_META.message_on_connect_confirmation_modal;    
                }
            } else {
                modal_body_text = EASYASSIST_COBROWSE_META.message_on_connect_confirmation_modal;
            }
        }

        if(!(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_timer_modal_minimized"))) {
            set_easyassist_current_session_local_storage_obj("easyassist_timer_modal_minimized", "false");
        }

        var div_model = document.createElement("div");
        div_model.id = "easyassist-connection-timer-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div id="easyassist-connection-timer-modal-connect" class="easyassist-customer-connect-modal-content">',
                '<div id="easyassist-minimize-connection-timer-modal" style="margin-left: auto; cursor: pointer; z-index: 2147483646 !important;">',
                    '<svg width="15" height="15" viewBox="0 0 25 26" fill="none" onclick="easyassist_minimize_connection_with_timer_modal()" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M23.133 0.862671L24.9354 2.6651L17.4796 10.1209H20.7227V12.6699H13.0757V5.02287H15.6247V8.37095L23.133 0.862671Z" fill="#BFBFBF"/>',
                        '<path d="M11.8012 13.9444V21.5915H9.25218V18.5047L1.90057 25.8563L0.0981445 24.0539L7.65857 16.4935H4.15414V13.9444H11.8012Z" fill="#BFBFBF"/>',
                    '</svg>',
                    '<svg width="15" height="15" viewBox="0 0 10 9" fill="none" onclick="easyassist_close_timer_connection_modal()" xmlns="http://www.w3.org/2000/svg" style="margin-left: 10px;">',
                        '<path d="M8.6839 9L5.0029 5.3156L1.32186 9L0.5 8.1787L4.1868 4.5L0.5 0.82134L1.32186 0L5.0029 3.6844L8.6839 0.00578022L9.5 0.82134L5.819 4.5L9.5 8.1787L8.6839 9Z" fill="#BFBFBF"></path>',
                    '</svg>',
                '</div>',
                '<div id="easyassist-connection-timer-content" style="display: flex; flex-direction: column;">',
                    '<div id="easyassist-connection-timer-header-div" class="easyassist-customer-connect-modal-header" style="text-align: center;">',
                        '<h6>'+ modal_header_text +'</h6>',
                    '</div>',
                    '<div id="easyassist-connection-timer-modal-body" class="easyassist-customer-connect-modal-body" style="text-align: center; min-height: 6em!important;">',
                        '<p>',
                            modal_body_text,
                        '</p>',
                    '</div>',
                    '<div id="easyassist-connection-timer-div" style="text-align: center; padding: 0rem 1rem;">',
                        '<div class="easyassist-connection-timer-inner-div" style="color:' + timer_color + '">','<div id="easyassist-waiting-time-value" style="font-size: 60px !important;">'+ waiting_time_seconds +'</div>','<div id="easyassist-waiting-time-unit" style="margin-top: 2rem;">sec</div>','</div>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_initiate_connection_with_timer_modal() {
        if(EASYASSIST_COBROWSE_META.no_agent_connects_toast && !is_easyassist_connection_timer_closed()) {
            var local_storage_obj = get_easyassist_current_session_local_storage_obj();
            if(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_timer_value")) {
                easyassist_start_agent_wait_timer(parseInt(local_storage_obj["easyassist_timer_value"]));
            } else {
                var waiting_time_seconds = EASYASSIST_COBROWSE_META.no_agent_connects_toast_threshold * 60;
                if (document.getElementById("easyassist-connection-timer-header-div").children[0]) {
                    document.getElementById("easyassist-connection-timer-header-div").children[0].innerHTML = "Connecting you to our expert";
                    document.getElementById("easyassist-minimized-timer-header-div").children[0].innerHTML = "Connecting you to our expert in";
                }
                if(document.getElementById("easyassist-connection-timer-modal-body").children[0]) {
                    document.getElementById("easyassist-connection-timer-modal-body").children[0].innerHTML = EASYASSIST_COBROWSE_META.message_on_connect_confirmation_modal;
                }
                easyassist_start_agent_wait_timer(waiting_time_seconds);
            }

            if(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_timer_modal_minimized")) {
                if(local_storage_obj["easyassist_timer_modal_minimized"] == "true") {
                    easyassist_hide_minimized_timer_modal();
                    easyassist_maximize_connection_with_timer_modal();
                    return;
                }
            }
            easyassist_show_connection_with_timer_modal();
        }
    }

    function easyassist_show_connection_with_timer_modal() {
        document.getElementById("easyassist-connection-timer-modal-id").style.display = 'flex';
    }

    function easyassist_hide_connection_with_timer_modal() {
        document.getElementById("easyassist-connection-timer-modal-id").style.display = 'none';
    }

    function easyassist_add_minimized_timer_modal() {
        var waiting_time_seconds, modal_header_text;
        var timer_color = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        var local_storage_obj = get_easyassist_current_session_local_storage_obj();
        if(local_storage_obj && local_storage_obj.hasOwnProperty("easyassist_timer_value")) {
            waiting_time_seconds = parseInt(local_storage_obj["easyassist_timer_value"]);
            if (waiting_time_seconds <= 15) {
                timer_color = "#E53E3E";
            }
        } else {
            waiting_time_seconds = EASYASSIST_COBROWSE_META.no_agent_connects_toast_threshold * 60;
        }

        if(local_storage_obj && local_storage_obj["easyassist_initial_timer_exhausted"] == "true") {
            modal_header_text = "Thank you for your patience, our agent will connect you in";
        } else {
            modal_header_text = "Connecting you to our expert in";
        }

        var div_model = document.createElement("div");
        div_model.id = "easyassist-minimized-connection-timer-modal-id"
        div_model.style.display = "none";
        div_model.setAttribute("data-left-offset", "12");
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div id="easyassist-minimized-timer-modal-connect" class="easyassist-customer-connect-modal-content" style="border-radius: 5px !important;">',
                '<div id="easyassist-maximize-connection-timer-modal" style="margin-left: auto; cursor: pointer ; z-index: 2147483646 !important;">',
                    '<svg width="15" height="15" viewBox="0 0 19 18" fill="none" onclick="easyassist_maximize_connection_with_timer_modal()" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M0.5 0H6.5V2H3.96173L8.80471 6.84298L7.3905 8.2572L2.5 3.3667V6H0.5V0Z" fill="#BFBFBF"/>',
                        '<path d="M0.5 18H6.5V16H3.8764L8.80459 11.0718L7.39038 9.65759L2.5 14.548V12H0.5V18Z" fill="#BFBFBF"/>',
                        '<path d="M12.5 18H18.5V12H16.5V14.5244L11.6332 9.65756L10.219 11.0718L15.1472 16H12.5V18Z" fill="#BFBFBF"/>',
                        '<path d="M18.5 0H12.5V2H15.0619L10.2189 6.84301L11.6331 8.25723L16.5 3.39032V6H18.5V0Z" fill="#BFBFBF"/>',
                    '</svg>', 
                    '<svg width="15" height="15" viewBox="0 0 10 9" fill="none" onclick="easyassist_close_minimise_connection_modal()" xmlns="http://www.w3.org/2000/svg" style="margin-left: 10px;">',
                        '<path d="M8.6839 9L5.0029 5.3156L1.32186 9L0.5 8.1787L4.1868 4.5L0.5 0.82134L1.32186 0L5.0029 3.6844L8.6839 0.00578022L9.5 0.82134L5.819 4.5L9.5 8.1787L8.6839 9Z" fill="#BFBFBF"></path>',
                    '</svg>',          
                '</div>',
                '<div id="easyassist-minimized-timer-content" style="margin-right: 30px;">',
                    '<div id="easyassist-minimized-timer-header-div" class="easyassist-customer-connect-modal-header" style="text-align: center; padding: 0rem !important; margin-bottom: 1rem;">',
                        '<h6 style="font-weight: normal !important;">'+ modal_header_text +'</h6>',
                    '</div>',
                    '<div id="easyassist-minimized-timer-div" style="margin-bottom: 1rem; text-align: center; padding: 0rem 1rem;">',
                        '<div class="easyassist-minimized-timer-inner-div" style="color:' + timer_color + '">','<div id="easyassist-minimized-waiting-time-value" style="font-size: 60px !important;">'+ waiting_time_seconds +'</div>','<div>sec</div>','</div>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        easyassist_initialize_drag_timer();
    }

    function easyassist_show_minimized_timer_modal() {
        document.getElementById("easyassist-minimized-connection-timer-modal-id").style.display = 'flex';
    }

    function easyassist_hide_minimized_timer_modal() {
        document.getElementById("easyassist-minimized-connection-timer-modal-id").style.display = 'none';
    }

    function easyassist_clear_local_storage() {
        localStorage.removeItem("easyassist_session");
    }

    function easyassist_add_floating_sidenav_button() { 
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
                var geolocation_options = {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                };
                window.navigator.geolocation.getCurrentPosition(easyassist_accept_location_request, easyassist_cancel_location_request, geolocation_options);
            }
        }
        var mobile_input_html = "";
        var virtual_agent_code_html = "";
        var lang_dropdown_html = "";
        if (EASYASSIST_COBROWSE_META.ask_client_mobile == true || EASYASSIST_COBROWSE_META.ask_client_mobile == "true" || EASYASSIST_COBROWSE_META.ask_client_mobile == "True") {
            if (EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == true || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "true" || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "True") {
                mobile_input_html += [
                	'<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row; border-radius:30px !important;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                		    '<input type="number" autocomplete="off" name="easyassist-client-mobile-number" id="easyassist-client-mobile-number" placeholder="Enter mobile number" onpaste="easyassist_phone_number_paste_handler(event);" onkeydown="easyassist_prevent_non_numeric_characters(event);easyassist_word_limit(event, this, 10);" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
        		        '<label id="modal-cobrowse-customer-number-error"></label>',
                	'</div>',
                ].join('');
            } else {
                mobile_input_html += [
                	'<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row;border-radius:30px !important;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                		    '<input type="number" autocomplete="off" name="easyassist-client-mobile-number" id="easyassist-client-mobile-number" placeholder="Enter Mobile Number (optional)" onpaste="easyassist_phone_number_paste_handler(event);" onkeydown="easyassist_prevent_non_numeric_characters(event);easyassist_word_limit(event, this, 10);" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
                		'<label id="modal-cobrowse-customer-number-error"></label>',
                	'</div>'
                ].join('');
            }
        }

        if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code){
            let placeholder_text = "Enter agent code";
            if (!EASYASSIST_COBROWSE_META.connect_with_virtual_agent_code_mandatory) {
                placeholder_text = "Enter agent code (optional)";
            }
            virtual_agent_code_html += [
                '<div class="easyassist-customer-connect-modal-content-wrapper">',
                    '<input type="text" autocomplete="off" name="easyassist-client-agent-virtual-code" id="easyassist-client-agent-virtual-code" placeholder="' + placeholder_text + '" oninput="easyassist_prevent_space_oninput(event)" onkeydown="easyassist_prevent_space_input(event);" onpaste="easyassist_prevent_space_paste(event);">',
                    '<label id="modal-cobrowse-virtual-agent-code-error"></label>',
                '</div>',
            ].join('');
        }

        if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            var dropdown_option_html = "";
            for (let index = 0; index < EASYASSIST_COBROWSE_META.supported_language.length; index++) {
                dropdown_option_html += '<option value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
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
                    '<h6>Connect with our experts</h6>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body" style="padding: 1rem 2rem!important;">',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<input type="text" autocomplete="off" name="easyassist-client-name" id="easyassist-client-name" placeholder="Enter full name">',
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
                	'<div style="padding-top: 1em; display:flex;">',
		                '<button class ="easyassist-modal-cancel-btn" id="easyassist-co-browsing-connect-cancel-btn" onclick="easyassist_close_browsing_modal()">Cancel</button>',
		        		'<button class ="easyassist-modal-primary-btn" id="easyassist-co-browsing-connect-button"  onclick="easyassist_connect_with_agent()">Connect</button>',
		        	'</div>',
                '</div>',
            '</div>'
        ].join('');

        div_model.innerHTML = modal_html;
        var sharable_link = '<div id="easychat_share_link_Model"><div class="easychat_share_link_Model-content"><h3>Share with Others</h3><br><div class="easychat_share_link_Model-content_wrapper" ><div class="easychat_share_link_Model-content_buttons_wrapper"><button disabled style="width: 75%;">Anyone with the link can guide you</button><button style="width: 25%;" onclick="easyassist_copy_text_to_clipboard_sharable_link()">Copy link</button></div><input id="easychat_share_link_Model-content_link_wrapper" type="text" value="" disabled autocomplete="off"></div><br><p style="color: black;">*Your personal information will be masked and will not be shared with anyone.</p><br><button class="easychat_share_link_Model-content-close_button">Done</button></div></div>';
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-co-browsing-connect-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-co-browsing-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sharable_link);

        if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            document.getElementById("easyassist-inline-form-input-preferred-language").selectedIndex = -1;
            new EasyassistCustomSelect(
                '#easyassist-inline-form-input-preferred-language', 
                'Choose preferred language',
                EASYASSIST_COBROWSE_META.floating_button_bg_color);
        }

        document.getElementById("easyassist-client-name").addEventListener('keydown', function(e) {
            var target_el = e.target;
            if(target_el.value.length > 40) {
                if(e.key != 'Backspace' && e.key != 'Delete' && e.key != 'ArrowLeft' && e.key != 'ArrowRight') {
                    e.preventDefault()
                }
            }
        });
    }

    function easyassist_add_non_working_hour_modal() {
        //Add Model
        var div_model = document.createElement("div");
        div_model.id = "easyassist-non-working-hours-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";

        var mobile_input_html = "";
        if (EASYASSIST_COBROWSE_META.ask_client_mobile == true || EASYASSIST_COBROWSE_META.ask_client_mobile == "true" || EASYASSIST_COBROWSE_META.ask_client_mobile == "True") {
            if (EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == true || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "true" || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "True") {
                mobile_input_html += [
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row; border-radius:30px !important;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                            '<input type="number" autocomplete="off" name="modal-non-working-client-mobile-number" id="modal-non-working-client-mobile-number" placeholder="Enter mobile number" onpaste="easyassist_phone_number_paste_handler(event);" onkeydown="easyassist_prevent_non_numeric_characters(event);easyassist_word_limit(event, this, 10);" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
                        '<label id="modal-non-working-customer-number-error"></label>',
                    '</div>',
                ].join('');
            } else {
                mobile_input_html += [
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row;border-radius:30px !important;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                            '<input type="number" autocomplete="off" name="modal-non-working-client-mobile-number" id="modal-non-working-client-mobile-number" placeholder="Enter Mobile Number (optional)" onpaste="easyassist_phone_number_paste_handler(event);" onkeydown="easyassist_prevent_non_numeric_characters(event);easyassist_word_limit(event, this, 10);" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
                        '<label id="modal-non-working-customer-number-error"></label>',
                    '</div>'
                ].join('');
            }
        }

        var product_dropdown_html = "";
        var lang_dropdown_html = "";
        
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            var product_dropdown_option_html = "";
            for (let index = 0; index < EASYASSIST_COBROWSE_META.product_category_list.length; index++) {
                product_dropdown_option_html += '<option value="' + EASYASSIST_COBROWSE_META.product_category_list[index]["key"] + '">' + EASYASSIST_COBROWSE_META.product_category_list[index]["value"] + '</option>';
            }
            product_dropdown_html += [
                '<div class="easyassist-customer-connect-modal-content-wrapper">',
                    '<select id="easyassist-non-working-hours-product-category">',
                        product_dropdown_option_html,
                    '</select>',
                    '<label id="easyassist-non-working-hours-product-category-error"></label>',
                '</div>'
            ].join('');
        }

        if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            var language_dropdown_option_html = "";
            for (let index = 0; index < EASYASSIST_COBROWSE_META.supported_language.length; index++) {
                language_dropdown_option_html += '<option value="' + EASYASSIST_COBROWSE_META.supported_language[index]["key"] + '">' + EASYASSIST_COBROWSE_META.supported_language[index]["value"] + '</option>';
            }
            lang_dropdown_html += [
            	'<div class="easyassist-customer-connect-modal-content-wrapper">',
	            	'<select id="easyassist-non-working-hours-preferred-language" >',
	                    language_dropdown_option_html,
	                '</select>',
	                '<label id="easyassist-non-working-hours-language-error"></label>',
	            '</div>',
	        ].join('');
        }

        let virtual_agent_code_html = "";

        if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code){
            let placeholder_text = "Enter agent code";
            if (!EASYASSIST_COBROWSE_META.connect_with_virtual_agent_code_mandatory) {
                placeholder_text = "Enter agent code (optional)";
            }
            virtual_agent_code_html += [
                '<div class="easyassist-customer-connect-modal-content-wrapper">',
                    '<input type="text" autocomplete="off" name="easyassist-non-working-hours-agent-virtual-code" id="easyassist-non-working-hours-agent-virtual-code" placeholder="' + placeholder_text + '" oninput="easyassist_prevent_space_oninput(event)" onkeydown="easyassist_prevent_space_input(event);" onpaste="easyassist_prevent_space_paste(event);">',
                    '<label id="virtual-agent-code-error-non-working-hours"></label>',
                '</div>',
            ].join('');
        }

        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header" style="text-align: center;">',
                    '<h6>Connect with our experts</h6>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body" style="padding: 1rem 2rem!important; max-height: 400px; overflow-y: auto;">',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<input type="text" autocomplete="off" name="modal-non-working-client-name" id="modal-non-working-client-name" placeholder="Enter full name">',
                        '<label id="modal-non-working-customer-name-error"></label>',
                    '</div>',
                    mobile_input_html,
                    product_dropdown_html,
                    lang_dropdown_html,
                    virtual_agent_code_html,
                    '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;">',
                        '<span>' + EASYASSIST_COBROWSE_META.message_on_non_working_hours + '</span>',
                    '</div>',
                    '<label id="modal-non-working-connect-error"></label>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<div style="padding-top: 1em; display:flex;">',
                        '<button class ="easyassist-modal-cancel-btn" id="modal-non-working-connect-cancel-btn" onclick="easyassist_close_non_working_hour_browsing_modal()">Cancel</button>',
                        '<button class ="easyassist-modal-primary-btn" id="modal-non-working-connect-button"  onclick="easyassist_save_non_working_hour_customer_details()">Submit</button>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("modal-non-working-connect-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("modal-non-working-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');

        document.getElementById("modal-non-working-client-name").addEventListener('keydown', function(e) {
            var target_el = e.target;
            if(target_el.value.length > 40) {
                if(e.key != 'Backspace' && e.key != 'Delete' && e.key != 'ArrowLeft' && e.key != 'ArrowRight') {
                    e.preventDefault()
                }
            }
        });

        if(EASYASSIST_COBROWSE_META.choose_product_category == true) {
            document.getElementById("easyassist-non-working-hours-product-category").selectedIndex = -1;
            new EasyassistCustomSelect(
                '#easyassist-non-working-hours-product-category', 
                'Select one',
                EASYASSIST_COBROWSE_META.floating_button_bg_color);
        }

        if (EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            document.getElementById("easyassist-non-working-hours-preferred-language").selectedIndex = -1;
            new EasyassistCustomSelect(
                '#easyassist-non-working-hours-preferred-language', 
                'Choose preferred language',
                EASYASSIST_COBROWSE_META.floating_button_bg_color);
        }
    }

    function easyassist_show_non_working_hour_modal(clicked_on) {
        if(clicked_on == 'greeting_bubble'){
            is_request_from_greeting_bubble = true;
            is_request_from_exit_intent = false;
            is_request_from_inactivity_popup = false;
            is_request_from_button = false;
        } else {
            is_request_from_greeting_bubble = false;
        }
        document.getElementById("modal-non-working-connect-error").innerHTML = "";
        if(document.getElementById("modal-non-working-customer-name-error")) {
            document.getElementById("modal-non-working-customer-name-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-non-working-customer-name-error").innerHTML = "";
        }
        if(document.getElementById("modal-non-working-customer-number-error")) {
            document.getElementById("modal-non-working-customer-number-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-non-working-customer-number-error").innerHTML = "";
        }
        if(document.getElementById("easyassist-non-working-hours-product-category-error")) {
        	document.getElementById("easyassist-non-working-hours-product-category-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
			document.getElementById("easyassist-non-working-hours-product-category-error").innerHTML = "";
        }
        if(document.getElementById("easyassist-non-working-hours-language-error")) {
        	document.getElementById("easyassist-non-working-hours-language-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
			document.getElementById("easyassist-non-working-hours-language-error").innerHTML = "";
        }
        if(document.getElementById("virtual-agent-code-error-non-working-hours")) {
            document.getElementById("easyassist-non-working-hours-agent-virtual-code").value = "";
            document.getElementById("virtual-agent-code-error-non-working-hours").previousSibling.classList.remove('easyassist-customer-connect-input-error');
			document.getElementById("virtual-agent-code-error-non-working-hours").innerHTML = "";
        }

        document.getElementById("modal-non-working-client-name").value = "";
        if (document.getElementById("modal-non-working-client-mobile-number") != null) {
            document.getElementById("modal-non-working-client-mobile-number").value = "";
        }

        document.getElementById("easyassist-non-working-hours-modal-id").style.display = "flex";
        document.getElementById('modal-non-working-client-name').focus();
        document.getElementById('modal-non-working-client-name').select();
        easyassist_hide_floating_sidenav_button();
        // easyassist_hide_greeting_bubble();
    }

    function easyassist_close_non_working_hour_browsing_modal(el) {
        document.getElementById("easyassist-non-working-hours-modal-id").style.display = "none";
        easyassist_show_floating_sidenav_button();
    }

    function easyassist_add_product_category_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-product-category-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var dropdown_html = "";
        var dropdown_option_html = "";
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            for (let index = 0; index < EASYASSIST_COBROWSE_META.product_category_list.length; index++) {
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
                    '<button class ="easyassist-modal-cancel-btn" onclick="easyassist_close_product_category_modal()" style="color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">Deny</button>',
                    '<button class ="easyassist-modal-primary-btn" id="easyassist-product-category-proceed-button"  onclick="easyassist_set_product_category()">Proceed</button>',
                '</div>',
            '</div>'
        ].join('');

        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-inline-form-input-product-category").selectedIndex = -1;
        new EasyassistCustomSelect(
            '#easyassist-inline-form-input-product-category', 
            'Select one',
            EASYASSIST_COBROWSE_META.floating_button_bg_color);
        document.getElementById("easyassist-product-category-proceed-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function add_connect_sidenav_into_page(value) {
        var nav_div = document.createElement("div");
        if (EASYASSIST_COBROWSE_META.enable_greeting_bubble){
            setTimeout(function(){
                if(get_easyassist_cookie("easyassist_session_id") == undefined && !EASYASSIST_COBROWSE_META.show_only_if_agent_available)
                    add_greeting_bubble(nav_div, false);
            }, EASYASSIST_COBROWSE_META.greeting_bubble_auto_popup_timer*1000);
        }
        //Add Span
        var nav_span = document.createElement("span");
        nav_span.id = "easyassist-side-nav-options-co-browsing";
        nav_span.setAttribute("class", "easyassist-side-nav-class");
        nav_span.style.backgroundColor = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        if (EASYASSIST_COBROWSE_META.floating_button_position == "left") {
            nav_div.id = "easyassist-auto-assign-agent-modal-left";
            nav_span.style.left = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            nav_span.style.top = "40%";
            nav_span.style.setProperty("border-radius", "10px 0px 0px 10px", "important");
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            nav_div.id = "easyassist-auto-assign-agent-modal-right";
            nav_span.style.right = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            nav_span.style.setProperty("border-radius", "0px 10px 10px 0px", "important");
            nav_span.style.top = "40%";
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "top") {
            nav_div.id = "easyassist-auto-assign-agent-modal-top";
            nav_span.style.top = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            nav_span.style.setProperty("transform", "rotate(0deg) translateX(-50%)", "important")
            nav_span.style.setProperty("writing-mode", "horizontal-tb", "important")
            nav_span.style.left = "50%";
            nav_span.style.padding = "5px 5px";
        }
        else {
            nav_div.id = "easyassist-auto-assign-agent-modal-bottom";
            nav_span.style.bottom = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            nav_span.style.left = "50%";
            nav_span.style.padding = "5px 5px";
            nav_span.style.setProperty("writing-mode", "horizontal-tb", "important")
            nav_span.style.setProperty("transform", "rotate(0deg) translateX(-50%)", "important")
            nav_span.style.setProperty("border-radius", "10px 10px 0px 0px", "important");
        }

        if(value == true){
            nav_span.textContent = "Contact Us";
        }else{
            nav_span.textContent = "Request for Support";
        }
        nav_span.setAttribute("onclick", "easyassist_show_cobrowsing_modal(); easyassist_source_of_lead()");

        nav_div.appendChild(nav_span);
        document.getElementsByTagName("body")[0].appendChild(nav_div);
    }

    function add_connect_icon_into_page(src) {
        var nav_div = document.createElement("div");
        if (EASYASSIST_COBROWSE_META.enable_greeting_bubble){        
            setTimeout(function(){
                if(get_easyassist_cookie("easyassist_session_id") == undefined)
                    add_greeting_bubble(nav_div, true);
            }, EASYASSIST_COBROWSE_META.greeting_bubble_auto_popup_timer*1000);
        }
        if (EASYASSIST_COBROWSE_META.floating_button_position == "left"){
            nav_div.id = "easyassist-auto-assign-agent-modal-left";
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            nav_div.id = "easyassist-auto-assign-agent-modal-right";
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "top") {
            nav_div.id = "easyassist-auto-assign-agent-modal-top";
        } else {
            nav_div.id = "easyassist-auto-assign-agent-modal-bottom";
        }
        var easychat_popup_image = document.createElement("img");
        easychat_popup_image.id = "easyassist-side-nav-options-co-browsing";
        easychat_popup_image.setAttribute("onclick", "easyassist_show_cobrowsing_modal(); easyassist_source_of_lead()");
        easychat_popup_image.style.zIndex = "2147483647";
        easychat_popup_image.style.top = "48%";
        easychat_popup_image.style.position = "fixed";
        easychat_popup_image.style.cursor = "pointer";
        easychat_popup_image.style.width = "4em";
        easychat_popup_image.src = src;
        easychat_popup_image.style.display = "none";
        nav_div.appendChild(easychat_popup_image);

        var easychat_popup_minimize_tooltip = document.createElement("span");
        easychat_popup_minimize_tooltip.id = "allincall-minimize-popup-tooltip";
        easychat_popup_minimize_tooltip.style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        easychat_popup_minimize_tooltip.style.zIndex = "2147483647";
        easychat_popup_minimize_tooltip.style.top = "50%";
        easychat_popup_minimize_tooltip.textContent = "Connect with an agent";
        easychat_popup_minimize_tooltip.style.position = "fixed";
        easychat_popup_minimize_tooltip.style.display = "none";
        // easychat_popup_minimize_tooltip.style.backgroundColor = "blue";
        easychat_popup_minimize_tooltip.style.color = "white";
        easychat_popup_minimize_tooltip.style.padding = "4px 8px";
        easychat_popup_minimize_tooltip.style.borderRadius = "10px";
        easychat_popup_minimize_tooltip.style.height = "30px";
        easychat_popup_minimize_tooltip.style.lineHeight = "20px";

        if(EASYASSIST_COBROWSE_META.floating_button_position == "right"){
            easychat_popup_image.style.right = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            easychat_popup_minimize_tooltip.style.right = "130px";  
            easychat_popup_minimize_tooltip.style.bottom = "107px"; 
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "left") {
            easychat_popup_image.style.left = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            easychat_popup_minimize_tooltip.style.left = "130px";
            easychat_popup_minimize_tooltip.style.right = "unset";
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "top") {
            easychat_popup_image.style.top = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            easychat_popup_image.style.left = "50%";
            easychat_popup_minimize_tooltip.style.left = "55%";
            easychat_popup_minimize_tooltip.style.top = "5px";
        } else {
            easychat_popup_image.style.top = "unset"
            easychat_popup_image.style.bottom = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
            easychat_popup_image.style.left = "50%";
            easychat_popup_minimize_tooltip.style.left = "55%";
            easychat_popup_minimize_tooltip.style.bottom = "8px";
            easychat_popup_minimize_tooltip.style.top = "unset";
        }

        nav_div.appendChild(easychat_popup_minimize_tooltip);
        document.getElementsByTagName("body")[0].appendChild(nav_div);

        if(EASYASSIST_COBROWSE_META.is_mobile == false){
            document.getElementById(nav_div.id).addEventListener("mouseover", function(e) {
                document.getElementById("allincall-minimize-popup-tooltip").style.display = "block";
            });

            document.getElementById(nav_div.id).addEventListener("mouseout", function(e) {
                document.getElementById("allincall-minimize-popup-tooltip").style.display = "none";
            });
        }   
    }

    function easyassist_hide_feedback_form(el) {
        try{
            document.getElementById("easyassist-co-browsing-feedback-modal").style.display = "none";
        }catch(err){}
    }

    function easyassist_hide_pdf_coview(){
        try{
            easyassist_send_remove_event_listener_over_socket();
            document.getElementById("easyassist_pdf_render_modal_wrapper").style.display = "none";
        } catch(err){}
    }

    function easyassist_show_pdf_coview(){
        try{
            document.getElementById("easyassist_pdf_render_modal_wrapper").style.display = "flex";
        } catch(err){}
    }

    function easyassist_hide_cobrowse_mobile_navbar_menu(el) {
        try{
            document.getElementById("cobrowse-mobile-navbar").style.display = "none";
        }catch(err){}
    }

    function hide_easyassist_cobrowsing_request_assist_modal() {
        try {
        document.getElementById("easyassist-co-browsing-request-assist-modal").style.display = "none";
        } catch (error) {}
    }

    function easyassist_show_feedback_form(el) {
        if(document.getElementById("easyassist-co-browsing-feedback-modal").style.display == "flex") {
            return;
        }
        easyassist_hide_livechat_iframe();
        easyassist_hide_agent_information_modal();
        hide_easyassist_cobrowsing_request_meeting_modal();
        hide_easyassist_voip_with_video_calling_request_modal();
        hide_easyassist_voip_calling_request_modal();
        hide_easyassist_cobrowsing_request_assist_modal();
        easyassist_hide_pdf_coview();
        document.getElementById("easyassist-client-feedback").value = "";
        document.getElementById("easyassist-feedback-error").innerHTML = "";
        easyassist_reset_rating_bar();
        close_modal();

        if(EASYASSIST_COBROWSE_META.allow_video_meeting_only == true) {
            document.getElementById("easyassist-feedback-nothanks-btn").click();
        } else {
            if(easyassist_show_feedback_form.caller.name == "easyassist_highlight_api_response_handler"){
                if(get_easyassist_cookie("easyassist_feedback_modal_shown") != "true"){
                    document.getElementById("easyassist-co-browsing-feedback-modal").style.display = "flex";
                    set_easyassist_cookie("easyassist_feedback_modal_shown", "true")
                } else {
                    document.getElementById("easyassist-feedback-nothanks-btn").click();
                }
            } else {
                document.getElementById("easyassist-co-browsing-feedback-modal").style.display = "flex";
            }
        }
    }

    function easyassist_hide_agent_joining_modal(el) {
        document.getElementById("easyassist_agent_joining_modal").style.display = "none";
    }

    function easyassist_show_agent_joining_modal(el) {
        document.getElementById("easyassist_agent_joining_modal").style.display = "flex";
    }

    function easyassist_hide_agent_information_modal(el) {
        document.getElementById("easyassist-agent-information-modal").style.display = "none";
    }

    function easyassist_show_pdf_render_modal(file_name,file_src,session_id){
        
        let split_array = file_src.split("/easy-assist")
        file_src = "/easy-assist" + split_array[1]

        if(file_name.length > 15) {
            file_name = file_name.substring(0, 8) + "..." + "pdf";  
        }

        if(session_id == ""){
            session_id = get_easyassist_cookie("easyassist_session_id")
        }
        easyassist_show_pdf_coview();
        easyassist_send_apply_event_listener_over_socket();
        document.getElementById("easyassist_pdf_render_modal_wrapper").classList.add('easyassist_pdf_render_modal_wrapper_show');
        document.getElementById("easyassist-pdf-title").innerHTML = '<p>'+file_name+'</p>'
        let download_file_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + file_src + "?session_id=" + session_id;
        file_src = file_src.replace('download-file','view-file')
        const url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + file_src + "?session_id=" + session_id;
        let pageNum = 1;
        let pageIsRendering = false;
        let pageNumIsPending = null;
        document.getElementById("easy_assist_pdf_render_current_page").value = pageNum;
        easyassist_show_hide_floating_page_number(pageNum)

        const scale = 1.5;

        let canvas = document.querySelector('#pdf-render');
        let ctx = canvas.getContext('2d');
        
        // Render the page
        const renderPage = num => {
        pageIsRendering = true;

        // Get page
        this.pdfDoc.getPage(num).then(page => {
            // Set scale
            const viewport = page.getViewport({ scale });
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderCtx = {
            canvasContext: ctx,
            viewport
            };

            page.render(renderCtx).promise.then(() => {
            pageIsRendering = false;
            
            let image = new Image();
            image.src = canvas.toDataURL("img/png");

            var d = document.querySelector('#myDiv')
            if(d.childNodes[0]){
            d.removeChild(d.childNodes[0]);   
            }
            d.appendChild(image)
            canvas.style.display="none";
            if (pageNumIsPending !== null) {
                renderPage(pageNumIsPending);
                pageNumIsPending = null;
            }
            });
            
        });
        };

        // Check for pages rendering
        const queueRenderPage = num => {
        if (pageIsRendering) {
            pageNumIsPending = num;
        } else {
            renderPage(num);
        }
        };

        // Show Prev Page
        const showPrevPage = () => {
            
        if(get_easyassist_cookie("easyassist_edit_access") == "true" && 
            !easyassist_check_current_tab_active()) {
            easyassist_send_tab_not_focus_over_socket("navigation");
            return;
        }

        if (pageNum <= 1) {
            return;
        }
        pageNum--;
        document.getElementById("easy_assist_pdf_render_current_page").value = pageNum;
        easyassist_show_hide_floating_page_number(pageNum)

        queueRenderPage(pageNum);
        };

        // Show Next Page
        const showNextPage = () => {

        if(get_easyassist_cookie("easyassist_edit_access") == "true" && 
            !easyassist_check_current_tab_active()) {
            easyassist_send_tab_not_focus_over_socket("navigation");
            return;
        }

        if (pageNum >= this.pdfDoc.numPages) {
            return;
        }
        
        pageNum++;

        document.getElementById("easy_assist_pdf_render_current_page").value = pageNum;
        easyassist_show_hide_floating_page_number(pageNum);

        queueRenderPage(pageNum);
        };

        const jump_to_page = () => {
        
        if(get_easyassist_cookie("easyassist_edit_access") == "true" && 
            !easyassist_check_current_tab_active()) {
            easyassist_send_tab_not_focus_over_socket("navigation");
            return;
        }
        
        if(!document.getElementById("easy_assist_pdf_render_current_page").value){
            return;
        }
        let curr_page = parseInt(document.getElementById("easy_assist_pdf_render_current_page").value)
        if (curr_page > this.pdfDoc.numPages) {
            pageNum = this.pdfDoc.numPages
        }
        else{
        pageNum = curr_page;
        }
        document.getElementById("easy_assist_pdf_render_current_page").value = pageNum
        document.getElementById("easy_assist_pdf_render_current_page_span").innerHTML = pageNum;
        queueRenderPage(pageNum);
        }
        
        const closeModal = () => {
            this.pdfDoc.destroy();
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            document.getElementById("easyassist_pdf_render_modal_wrapper").classList.remove('easyassist_pdf_render_modal_wrapper_show');
        }

        const download_file = () => {
            window.open(download_file_url)
        }

        // Get Document
        pdfjsLib
        .getDocument(url)
        .promise.then(pdfDoc_ => {
            if(this.pdfDoc){
                this.pdfDoc.destroy();
            }
            this.pdfDoc = pdfDoc_;
            document.querySelector('#coview_pdf_page_length_span').innerHTML = this.pdfDoc.numPages
            document.querySelector('#coview_pdf_page_length').innerHTML = this.pdfDoc.numPages;
            renderPage(pageNum);
        })


        // Button Events
        // document.querySelector('#pdf_download_svg').addEventListener('click', download_file);
        if(this.pdfDoc){
            // $('#easyassist-pdf-render-modal-close').click();
            document.querySelector('#prev-page').removeEventListener('click', showPrevPage);
            document.querySelector('#next-page').removeEventListener('click', showNextPage);
            document.querySelector('#prev-page-mobile').removeEventListener('click', showPrevPage);
            document.querySelector('#next-page-mobile').removeEventListener('click', showNextPage);                
        }
        
        document.querySelector('#prev-page').addEventListener('click', showPrevPage);
        document.querySelector('#next-page').addEventListener('click', showNextPage);
        document.querySelector('#prev-page-mobile').addEventListener('click', showPrevPage);
        document.querySelector('#next-page-mobile').addEventListener('click', showNextPage);                
        
        document.querySelector('#easyassist-pdf-render-modal-close').addEventListener('click', closeModal);
        document.querySelector('#easy_assist_pdf_render_current_page').addEventListener('change', jump_to_page);
    }

    function easyassist_show_agent_information_modal(show_dialog_on_startup=false) {
        if(show_dialog_on_startup) {
            document.getElementById("easyassist-agent-info-modal-header").innerText = "Agent has joined the session";
            document.getElementById("easyassist-agent-info-modal-close-btn").innerText = "Ok";
        } else {
            document.getElementById("easyassist-agent-info-modal-header").innerText = "Agent Details";
            document.getElementById("easyassist-agent-info-modal-close-btn").innerText = "Close";
        }
        document.getElementById("easyassist-agent-information-modal").style.display = "flex";
    }

    function hide_easyassist_cobrowsing_request_meeting_modal(el) {
        document.getElementById("easyassist-co-browsing-request-meeting-modal").style.display = "none";
    }
    
    function hide_easyassist_voip_with_video_calling_request_modal(el) {
        document.getElementById("easyassist-voip-video-calling-request-modal").style.display = "none";
    }

    function hide_easyassist_voip_calling_request_modal(el) {
        document.getElementById("easyassist-voip-calling-request-modal").style.display = "none";
    }

    function easyassist_add_request_assist_modal() {
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
	        				'<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:left;padding-top:0!important;">',
	        					EASYASSIST_COBROWSE_META.assist_message,
	        				'</div>',
	        				'<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;padding-top:0!important;">',
						    	'Please enter support code shared by the expert',
						    '</div>',
			    			'<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;">',
                                '<div style="border-color: #E6E6E6; display: flex; align-items: center; justify-content: center;">',
    			    				'<input class="easyassist-verfication-otp-input" type="number" onfocus="easyassist_verification_input_color_change(this);" autocomplete="off">',
    			    				'<input class="easyassist-verfication-otp-input" type="number" onfocus="easyassist_verification_input_color_change(this);" autocomplete="off">',
    			    				'<input class="easyassist-verfication-otp-input" type="number" onfocus="easyassist_verification_input_color_change(this);" autocomplete="off">',
    			    				'<input class="easyassist-verfication-otp-input" type="number" onfocus="easyassist_verification_input_color_change(this);" autocomplete="off">',
                                '</div>',
			    				'<label id="easyassist-request-assist-otp-error"></label>',
			    			'</div>',
	        			'</div>',
	        			'<div class="easyassist-customer-connect-modal-footer">',
	        				'<div style="padding-top: 1em; display: flex">',
		        				'<button class="easyassist-modal-cancel-btn" onclick="easyassist_update_agent_assistant_request(\'false\')" id="easyassist-verification-cancel-btn">Deny</button>',
		                		'<button class="easyassist-modal-primary-btn" onclick="easyassist_update_agent_assistant_request(\'true\')" id="easyassist-verify-button">Allow</button>',
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
	        				'<h6 style="padding-bottom:12px; text-align: center;">Connect with our experts</h6>',
        				'</div>',
	        			'<div class="easyassist-customer-connect-modal-body">',
	        				'<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:left;padding-top:0!important;">',
	        					EASYASSIST_COBROWSE_META.assist_message,
	        				'</div>',
	        			'</div>',
	        			'<div class="easyassist-customer-connect-modal-footer">',
	        				'<div style="padding-top: 1em; display:flex;">',
		        				'<button class="easyassist-modal-cancel-btn" onclick="easyassist_update_agent_assistant_request(\'false\')" id="easyassist-verification-cancel-btn">Deny</button>',
		                		'<button class="easyassist-modal-primary-btn" onclick="easyassist_update_agent_assistant_request(\'true\')" id="easyassist-verify-button">Allow</button>',
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

        var verify_inputs = easyassist_get_eles_by_class_name('easyassist-verfication-otp-input');
        for(let idx = 0; idx < verify_inputs.length; idx ++) {
            verify_inputs[idx].addEventListener('keyup', function(e) {
                if(e.key == 'Backspace') {
                    if(this.previousSibling) {
                        this.previousSibling.focus();
                    }
                    if(e.target != easyassist_get_eles_by_class_name('easyassist-verfication-otp-input')[0]) {
                        e.target.style.color = "inherit";
                        e.target.style.borderColor = "inherit";
                    }
                } else if(e.key >= '0' && e.key <= '9') {
                    let keys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
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
                } else if(e.key == "ArrowDown" || e.key == "ArrowUp") {
                    e.preventDefault();
                    e.stopPropagation();
                } else if(e.key == "-" || e.key == "_" || e.key == "+" || e.key == "=" || e.key == "e" || e.key == "E") {
                    e.preventDefault();
                    e.stopPropagation();
                }
            });

            verify_inputs[idx].addEventListener('paste', function(e) {
                var regex_code = /^[0-9]{4}$/g;
                var clipboard_data = e.clipboardData || e.originalEvent.clipboardData || window.clipboardData;
                var pasted_data = clipboard_data.getData('text');

                if(idx == 0) {
                    if(regex_code.test(pasted_data)){
                        for(let index = 0; index < verify_inputs.length; index ++) {
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

    function easyassist_add_request_meeting_modal() {
        var meeting_modal_html = [
            '<div id="easyassist-co-browsing-request-meeting-modal" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6 style="display: inline-flex; align-items: center;">',
                            '<span class="easyassist-svg-wrapper" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; margin-right: 1rem;">',
                                '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                    '<rect width="32" height="32" rx="7" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                    '<path d="M19 12.5C19 11.1193 17.8807 10 16.5 10H10.5C9.11929 10 8 11.1193 8 12.5V19.5C8 20.8807 9.11929 22 10.5 22H16.5C17.8807 22 19 20.8807 19 19.5V12.5Z" fill="white"/>',
                                    '<path d="M20 13.9308V18.0815L22.7642 20.4319C23.2512 20.8461 24 20.4999 24 19.8606V12.1931C24 11.5568 23.2575 11.2096 22.7692 11.6176L20 13.9308Z" fill="white"/>',
                                '</svg>',
                            '</span>',
                            'Connect with our experts',
                        '</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body" style="padding-top: 1.5em!important; min-height: 5em!important;">',
                        EASYASSIST_COBROWSE_META.meeting_message,
                        '<label id="easyassist-request-meeting-error"></label>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" onclick="easyassist_update_agent_meeting_request(\'false\')" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Decline</button>',
                        '<button class="easyassist-modal-primary-btn" onclick="easyassist_update_agent_meeting_request(\'true\')" id="easyassist-meeting-connect-button">Connect</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', meeting_modal_html);
        document.getElementById("easyassist-meeting-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }
    
    function easyassist_add_voice_call_initiate_modal() {
        var voip_modal_html = `
        <div class="main-wrapper">
        <div id="easyassist_agent_connect_modal" class="easyassist-agent-connect-modal" style="z-index: 2147483647 !important; display: none;">
        <div class="easyassist-agent-connect-modal-content">
            <div class="easyassist-agent-connect-modal-header">
                <div style="display: flex;align-items: center;padding-bottom: 1.5rem;">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="32" height="32" rx="7" fill=" ${EASYASSIST_COBROWSE_META.floating_button_bg_color} "></rect>
                        <path d="M23.12 19.0044C22.0266 19.0044 20.9688 18.8266 19.9822 18.5066C19.8277 18.4543 19.6615 18.4465 19.5027 18.4842C19.3439 18.522 19.199 18.6037 19.0844 18.72L17.6888 20.4712C15.1733 19.2712 12.8178 17.0044 11.5644 14.4L13.2978 12.9244C13.5378 12.6756 13.6089 12.3289 13.5111 12.0178C13.1822 11.0311 13.0133 9.97334 13.0133 8.88C13.0133 8.4 12.6133 8 12.1333 8H9.05778C8.57778 8 8 8.21333 8 8.88C8 17.1378 14.8711 24 23.12 24C23.7512 24 24 23.44 24 22.9512V19.8844C24 19.4044 23.6 19.0044 23.12 19.0044Z" fill="white"></path>
                    </svg>
                    <h6 class="modal-title pl-2" id="support_material_modal_label" style="font-weight: bold; font-size: 16px; font-style: normal; padding-left: 1rem !important; margin: 0 !important;">Connect with the agent over voice call</h6>
                    <div id="voip-cross-icon" style="display: none;">
                        <svg width="15" height="15" viewBox="0 0 10 9" fill="#262626" onclick="close_modal()" xmlns="http://www.w3.org/2000/svg" style="cursor: pointer;">
                            <path d="M8.6839 9L5.0029 5.3156L1.32186 9L0.5 8.1787L4.1868 4.5L0.5 0.82134L1.32186 0L5.0029 3.6844L8.6839 0.00578022L9.5 0.82134L5.819 4.5L9.5 8.1787L8.6839 9Z" fill="#262626"></path>
                        </svg>
                    </div>    
                </div>
            </div>
            <div class="easyassist-agent-connect-modal-body">
                <div class="easyassist-agent-connect-description">
                    <p>A request will be sent to the agent and once they accept the request you will be connected with them over a voice call</p>
                </div>
                <div id="request_meeting_error" style="color:green;"></div>
            </div>
            <div class="easyassist-agent-connect-modal-footer" id="request_meeting_button">
                <button class="easyassist-modal-cancel-btn" style="color: ${EASYASSIST_COBROWSE_META.floating_button_bg_color}!important;" onclick="close_modal()">Cancel</button>
                <button class="easyassist-modal-primary-btn" onclick="request_for_meeting()" style="background: ${EASYASSIST_COBROWSE_META.floating_button_bg_color}!important;">Request</button>
            </div>
        </div>
    </div>
    </div>
    `
    document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', voip_modal_html);
    }

    function easyassist_add_video_call_initiate_modal() {
        var voip_modal_html = `
        <div class="main-wrapper">
        <div id="easyassist_agent_connect_video_call_modal" class="easyassist-agent-connect-modal" style="z-index: 2147483647 !important; display: none;">
        <div class="easyassist-agent-connect-modal-content">
            <div style="align-self: flex-end; margin-top: 0.5rem; ">
                <svg width="15" height="15" viewBox="0 0 10 9" fill="none" onclick="close_modal()" xmlns="http://www.w3.org/2000/svg" style="cursor: pointer;">
                    <path d="M8.6839 9L5.0029 5.3156L1.32186 9L0.5 8.1787L4.1868 4.5L0.5 0.82134L1.32186 0L5.0029 3.6844L8.6839 0.00578022L9.5 0.82134L5.819 4.5L9.5 8.1787L8.6839 9Z" fill="#BFBFBF"></path>
                </svg>    
            </div>
            <div class="easyassist-agent-connect-modal-header">
                <div style="display: flex; align-items: center; padding-bottom: 1.5rem; ">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="32" height="32" rx="7" fill=" ${EASYASSIST_COBROWSE_META.floating_button_bg_color} "></rect>
                        <path d="M19 12.5C19 11.1193 17.8807 10 16.5 10H10.5C9.11929 10 8 11.1193 8 12.5V19.5C8 20.8807 9.11929 22 10.5 22H16.5C17.8807 22 19 20.8807 19 19.5V12.5Z" fill="white"></path>
                        <path d="M20 13.9308V18.0815L22.7642 20.4319C23.2512 20.8461 24 20.4999 24 19.8606V12.1931C24 11.5568 23.2575 11.2096 22.7692 11.6176L20 13.9308Z" fill="white"></path>
                    </svg>
                    <h6 class="modal-title pl-2">Connect with the Agent on Video Call</h6>
                </div>
            </div>
            <div class="easyassist-agent-connect-modal-body">
                <div class="easyassist-agent-connect-description">
                    <p>A request will be sent to the agent and you will be connected with him/her on virtual meeting.</p>
                </div>
                <div id="request_meeting_error_cobrowse_video_call" style="color:green;padding-top:10px;padding-left:10px;"></div>
            </div>
            <div class="easyassist-agent-connect-modal-footer" id="request_meeting_button_cobrowse_video_call">
                <button class="easyassist-modal-cancel-btn" style="color: ${EASYASSIST_COBROWSE_META.floating_button_bg_color}!important;" onclick="close_modal()">Cancel</button>
                <button class="easyassist-modal-primary-btn" onclick="request_for_meeting()" style="background: ${EASYASSIST_COBROWSE_META.floating_button_bg_color}!important;">Request</button>
            </div>
        </div>
    </div>
    </div>
    `
    document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', voip_modal_html);
    }

    function easyassist_add_voip_with_video_calling_request_modal() {
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
                    '<div class="easyassist-customer-connect-modal-body default-text"  style="padding-top: 1.5em!important; min-height: 5em!important;">',
                        EASYASSIST_COBROWSE_META.voip_with_video_calling_message,
                        '<label id="easyassist-voip-with-video-meeting-error"></label>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" onclick="easyassist_update_agent_meeting_request(\'false\')" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">No</button>',
                        '<button class="easyassist-modal-primary-btn" onclick="easyassist_update_agent_meeting_request(\'true\')"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Yes</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', meeting_modal_html);
    }

    function easyassist_add_voip_calling_request_modal() {
        var voip_modal_html = [
            '<div id="easyassist-voip-calling-request-modal" class="easyassist-customer-connect-modal eassyassist-custom-in-session-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>',
                            '<span class="easyassist-svg-wrapper" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; margin-right: 1rem !important;">',
                                '<svg width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                    '<path d="M13.7528 9.33678C12.7881 9.33678 11.8548 9.19851 10.9842 8.94962C10.8478 8.90887 10.7011 8.90282 10.561 8.93217C10.4209 8.96152 10.293 9.02507 10.192 9.11555L8.96064 10.4775C6.74103 9.54419 4.6626 7.78123 3.55672 5.75555L5.08613 4.60789C5.2979 4.41431 5.36064 4.14468 5.27437 3.90271C4.98417 3.1353 4.83515 2.31259 4.83515 1.46222C4.83515 1.08888 4.48221 0.777771 4.05868 0.777771H1.34495C0.921425 0.777771 0.411621 0.943697 0.411621 1.46222C0.411621 7.88493 6.47437 13.2222 13.7528 13.2222C14.3097 13.2222 14.5293 12.7867 14.5293 12.4064V10.0212C14.5293 9.64789 14.1763 9.33678 13.7528 9.33678Z" fill="white"/>',
                                '</svg>',
                            '</span>',
                            'Voice Call',
                        '</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body default-text">',
                        EASYASSIST_COBROWSE_META.voip_calling_message,
                        '<label id="easyassist-voip-meeting-error"></label>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" onclick="easyassist_update_agent_meeting_request(\'false\')" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">No</button>',
                        '<button class="easyassist-modal-primary-btn" onclick="easyassist_update_agent_meeting_request(\'true\')"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Yes</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', voip_modal_html);
    }

    function easyassist_add_request_edit_access_modal() {
    	var request_edit_access_modal_html = [
    		'<div id="easyassist-co-browsing-request-edit-access" class="easyassist-customer-connect-modal">',
    			'<div class="easyassist-customer-connect-modal-content">',
    				'<div class="easyassist-customer-connect-modal-body">',
    					'Our Customer Service Agent has requested Edit Access to help you in filling the form. You can revoke edit access from the navigation bar. Would you like to allow?',
    				'</div>',
    				'<div class="easyassist-customer-connect-modal-footer">',
    				'<button class="easyassist-modal-cancel-btn" id="easyassist-edit-access-cancel-btn" onclick="easyassist_update_agent_request_edit_access(\'false\')">Deny</button>',
    				'<button class="easyassist-modal-primary-btn" id="easyassist-edit-access-allow-button" onclick="easyassist_update_agent_request_edit_access(\'true\')">Allow</button>',
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

    function easyassist_add_feedback_form_modal() {
        var add_easyassist_feedback_form_html = [
            '<div id="easyassist-co-browsing-feedback-modal" class="easyassist-customer-feedback-modal" style="display: none;">',
                '<div class="easyassist-customer-feedback-modal-content">',
                    '<div class="easyassist-customer-feedback-modal-header">',
                        '<h6 style="padding-bottom: 1em!important; width:100%;" id="feedback-modal-header-text">Feedback</h6>',
                        '<div onclick="easyassist_hide_feedback_form(); easyassist_show_chat_bubble();" ea_visible="true" style="cursor: pointer">',
                            '<svg width="23" height="23" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M0 11.5C0 5.14873 5.14873 0 11.5 0C17.8513 0 23 5.14873 23 11.5C23 17.8513 17.8513 23 11.5 23C5.14873 23 0 17.8513 0 11.5ZM16.1434 6.80013C16.5075 7.16427 16.5075 7.75465 16.1434 8.11879L12.7904 11.4718L16.1434 14.8247C16.5075 15.1889 16.5075 15.7792 16.1434 16.1434C15.7792 16.5075 15.1889 16.5075 14.8247 16.1434L11.4718 12.7904L8.11879 16.1434C7.75465 16.5075 7.16427 16.5075 6.80013 16.1434C6.43599 15.7792 6.43599 15.1889 6.80013 14.8247L10.1531 11.4718L6.80013 8.11879C6.43599 7.75465 6.43599 7.16427 6.80013 6.80013C7.16427 6.43599 7.75465 6.43599 8.11879 6.80013L11.4718 10.1531L14.8247 6.80013C15.1889 6.43599 15.7792 6.43599 16.1434 6.80013Z" fill="#717274" />',
                            '</svg>',
                        '</div>',
                    '</div>',
                    '<div class="easyassist-customer-feedback-modal-body">',
                        '<label>',
                            '<p style="font-size: 15px; text-align: left;">On a scale of 0-10, how likely are you to recommend Cobrowse to a friend or colleague?</p>',
                            '<div class="easyassist-tickmarks">',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 0)" onmouseout="easyassist_feedback_icon_color_change(this)">0</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 1)" onmouseout="easyassist_feedback_icon_color_change(this)">1</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 2)" onmouseout="easyassist_feedback_icon_color_change(this)">2</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 3)" onmouseout="easyassist_feedback_icon_color_change(this)">3</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 4)" onmouseout="easyassist_feedback_icon_color_change(this)">4</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 5)" onmouseout="easyassist_feedback_icon_color_change(this)">5</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 6)" onmouseout="easyassist_feedback_icon_color_change(this)">6</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 7)" onmouseout="easyassist_feedback_icon_color_change(this)">7</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 8)" onmouseout="easyassist_feedback_icon_color_change(this)">8</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 9)" onmouseout="easyassist_feedback_icon_color_change(this)">9</span>',
                                '<span onclick="easyassist_rate_agent(this);" onmouseover="easyassist_show_emoji_on_rating_change(this, 10)" onmouseout="easyassist_feedback_icon_color_change(this)">10</span>',
                            '</div>',
                        '</label>',
                        '<textarea id="easyassist-client-feedback" class="easyassist-feedbackComments" property="comment" cols="30" rows="5" placeholder="Remarks"></textarea>',
                        '<label id="easyassist-feedback-error" style="display: none;color:red;padding-top: 0.5em;"></label>',
                    '</div>',
                    '<div class="easyassist-customer-feedback-modal-footer">',
                        '<button class="easyassist-modal-cancel-btn" id="easyassist-feedback-nothanks-btn" onclick="easyassist_submit_client_feedback(\'no_feedback\')" type="button" data-dismiss="easyassist-modal">',
                            'No Thanks',
                        '</button>',
                        '<button class="easyassist-modal-primary-btn" id="easyassist-feedback-submit-button" onclick="easyassist_submit_client_feedback(\'feedback\')">',
                            'Submit',
                        '</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form_html);
        document.getElementById("easyassist-feedback-submit-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-feedback-nothanks-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function easyassist_add_agent_joining_modal(){
        var div_model = document.createElement("div");
        div_model.id = "easyassist_agent_joining_modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
        	'<div class="easyassist-customer-connect-modal-content">',
        		'<div class="easyassist-customer-connect-modal-header">',
        			'<h6>Connect with our experts</h6>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-body">',
        			'Our Customer Support Agent will be connecting with you shortly. Please wait.',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-footer">',
        			'<button class ="easyassist-modal-primary-btn" onclick="easyassist_hide_agent_joining_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;" >OK</button>',
        		'</div>',
        	'</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }
    
    function easyassist_add_pdf_render_modal(){
        
        if(!EASYASSIST_COBROWSE_META.enable_preview_functionality) {
            return;
        }
        
        var div_model = document.createElement("div");
        div_model.id = "easyassist_pdf_render_modal_wrapper"
        div_model.className = "easyassist-pdf-render-modal-wrapper";
        div_model.style.display = "none";
        var modal_html = `
        <div class="easyassist-pdf-render-modal-container">
            <div class="easyassist-pdf-render-modal">
                <div class="easyassist-pdf-render-modal-menubar">
                    <div id="easyassist-pdf-title" class="heading"></div>
                    <div class="central-control-section">
                        <div class="page-count">
                            <input id="easy_assist_pdf_render_current_page" type="text" value="1" min="1" pattern="[0-9]+"/> 
                            <span style="color: #fff;">/</span>
                            <span id="coview_pdf_page_length"></span>
                        </div>
                        <div class="page-move" id="page-move">   
                            <button id="prev-page" class="page-move-btn">&#60;&nbsp; Previous</button>
                            <button id="next-page" class="page-move-btn">Next &nbsp;&#62;</button>
                        </div>
                        <div class="page-move-mobile" id="page-move-mobile">   
                            <button id="prev-page-mobile" class="page-move-btn">&#60;&nbsp;</button>
                            <button id="next-page-mobile" class="page-move-btn">&nbsp;&#62;</button>
                        </div>
                    </div>
                    <div id="easyassist-pdf-coview-cross-button" class="right-control-section" onclick="easyassist_hide_pdf_coview()">     
                        <svg id="easyassist-pdf-render-modal-close" width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" >
                            <path d="M0.183491 0.338713L0.256282 0.256282C0.571705 -0.0591417 1.06803 -0.0834054 1.41129 0.183491L1.49372 0.256282L7 5.76188L12.5063 0.256282C12.848 -0.085427 13.402 -0.085427 13.7437 0.256282C14.0854 0.597991 14.0854 1.15201 13.7437 1.49372L8.23812 7L13.7437 12.5063C14.0591 12.8217 14.0834 13.318 13.8165 13.6613L13.7437 13.7437C13.4283 14.0591 12.932 14.0834 12.5887 13.8165L12.5063 13.7437L7 8.23812L1.49372 13.7437C1.15201 14.0854 0.597991 14.0854 0.256282 13.7437C-0.085427 13.402 -0.085427 12.848 0.256282 12.5063L5.76188 7L0.256282 1.49372C-0.0591417 1.17829 -0.0834054 0.681968 0.183491 0.338713L0.256282 0.256282L0.183491 0.338713Z" fill="white"/>
                        </svg>                          
                    </div>   
                </div>
            </div>
            <div class="modal-body" id="render_pdf_div">
            <canvas id="pdf-render">
            </canvas>
            <div id="easyassist-floating-page-number" class="d-none">
                <span id="easy_assist_pdf_render_current_page_span"></span> 
                <span style="color: #fff;">/</span>
                <span id="coview_pdf_page_length_span"></span>
            </div>
            <div class="easyassist-pdf-render-div" id="myDiv">
            </div>
            </div>
        </div>
        `
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }


    function easyassist_create_navbar_menu() {
        var div_model = document.createElement("div");
        div_model.id = "cobrowse-mobile-navbar"
        div_model.style.display = "none";
        div_model.className = "";

        var sidenav_menu_html = `\
        <div class="easyassist-custom-${EASYASSIST_COBROWSE_META.floating_button_position}-nav-bar_wrapper"style="display:flex;">\
        <div class="easyassist-custom-${EASYASSIST_COBROWSE_META.floating_button_position}-nav-bar" >
        <div class="easyassist-customer-connect-modal-body" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">
        <ul id="ul_items">
        `

        sidenav_menu_html += `
        <li class="closebtn1">
            <div>
                <a id="previous_button" href="javascript:void(0)" class="closebtn1" style="margin: 0px">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.3936 7.41289L8.44584 11.0199C7.85139 11.563 7.85139 12.4404 8.44584 12.9835L12.3936 16.5905C13.3538 17.4679 15 16.8412 15 15.6017V8.38776C15 7.14829 13.3538 6.53552 12.3936 7.41289Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                    </svg>
                </a>
            </div>
        </li>`

        if (EASYASSIST_COBROWSE_META.enable_chat_functionality == true) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
            <div class="menu-item active-item">
                <a href="javascript:void(0)" onclick="easyassist_show_livechat_iframe();easyassist_hide_feedback_form()">\
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 24px !important; height: 24px !important;">\
                        <path d="M12 4C16.4182 4 20 7.58119 20 11.9988C20 16.4164 16.4182 19.9976 12 19.9976C10.6877 19.9976 9.42015 19.6808 8.28464 19.0844L4.85231 19.9778C4.48889 20.0726 4.11752 19.8547 4.02287 19.4913C3.99359 19.379 3.99359 19.261 4.02284 19.1486L4.91592 15.7184C4.31776 14.582 4 13.3128 4 11.9988C4 7.58119 7.58173 4 12 4ZM13.0014 12.7987H9.40001L9.3186 12.8041C9.02573 12.8439 8.80001 13.0949 8.80001 13.3986C8.80001 13.7023 9.02573 13.9533 9.3186 13.9931L9.40001 13.9985H13.0014L13.0828 13.9931C13.3757 13.9533 13.6014 13.7023 13.6014 13.3986C13.6014 13.0949 13.3757 12.8439 13.0828 12.8041L13.0014 12.7987ZM14.6 9.99911H9.40001L9.3186 10.0046C9.02573 10.0443 8.80001 10.2953 8.80001 10.599C8.80001 10.9027 9.02573 11.1538 9.3186 11.1935L9.40001 11.199H14.6L14.6815 11.1935C14.9743 11.1538 15.2 10.9027 15.2 10.599C15.2 10.2953 14.9743 10.0443 14.6815 10.0046L14.6 9.99911Z"\
                        fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                    </svg>\
                </a>\
            </div>\
            </li>`
        }
                    
        if(EASYASSIST_COBROWSE_META.customer_initiate_voice_call == true && EASYASSIST_COBROWSE_META.enable_voip_calling) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
            <div class="menu-item active-item">\
                <a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();open_invite_agent_modal();">\
                    <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"></path>
                    </svg>
                </a>\
            </div>\
            </li>`
            
        } else if (EASYASSIST_COBROWSE_META.customer_initiate_video_call == true && EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
            <div class="menu-item active-item">\
                <a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();open_invite_agent_modal();">\
                    <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"></path>\
                    </svg>\
                </a>\
            </div>
            </li>`;

        } else if (EASYASSIST_COBROWSE_META.customer_initiate_video_call_as_pip == true && EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
            <div class="menu-item active-item">\
                <a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();open_invite_agent_modal();">\
                    <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"></path>\
                    </svg>\
                </a>
            </div>
            </li>`;
        }

        sidenav_menu_html += `<li class="cobrowse-icons">\
        <div class="menu-item active-item">\
            <a href="javascript:void(0)" onclick="easyassist_revoke_edit_access();" id="revoke-edit-access-button">\
                <svg width="26" height="26" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M26.5384 1.46154L26.3251 1.2602C24.3656 -0.484696 21.3606 -0.417579 19.4814 1.46154L18.1281 2.81405L25.1856 9.8701L26.5384 8.5185C28.4176 6.63939 28.4847 3.63441 26.7398 1.67486L26.5384 1.46154ZM16.6499 4.29218L23.7074 11.3497L22.4615 12.5956C21.1193 11.5958 19.4967 11.0112 17.749 11.0112C13.128 11.0112 9.38214 15.0977 9.38214 20.1387C9.38214 21.7615 9.77038 23.2855 10.4511 24.606L9.84894 25.2081C9.46283 25.5942 8.98265 25.8729 8.45587 26.0165L1.32219 27.962C0.541473 28.175 -0.17491 27.4584 0.0380027 26.6779L1.98357 19.5442C2.12723 19.0174 2.40588 18.5373 2.79198 18.151L16.6499 4.29218ZM6.31113 12.659L4.21943 14.7507L1.04701 14.7513C0.469396 14.7513 0.00115825 14.2831 0.00115825 13.7055C0.00115825 13.1279 0.469396 12.6596 1.04701 12.6596L6.31113 12.659ZM11.8891 7.08116L9.79732 9.17287L1.04701 9.17345C0.469396 9.17345 0.00115825 8.70521 0.00115825 8.12759C0.00115825 7.54999 0.469396 7.08173 1.04701 7.08173L11.8891 7.08116ZM15.3752 3.59495L17.4669 1.50325L1.04701 1.50384C0.469396 1.50384 0.00115825 1.97208 0.00115825 2.5497C0.00115825 3.12732 0.469396 3.59556 1.04701 3.59556L15.3752 3.59495ZM26.2425 20.2021C26.2425 15.9662 22.8088 12.5324 18.573 12.5324C14.3371 12.5324 10.9034 15.9662 10.9034 20.2021C10.9034 24.4379 14.3371 27.8716 18.573 27.8716C22.8088 27.8716 26.2425 24.4379 26.2425 20.2021ZM19.5609 20.2023L22.0288 17.7357C22.3011 17.4634 22.3011 17.0219 22.0288 16.7496C21.7565 16.4775 21.3151 16.4775 21.0428 16.7496L18.5749 19.2162L16.1082 16.7495C15.8359 16.4773 15.3944 16.4773 15.1221 16.7495C14.8498 17.0218 14.8498 17.4633 15.1221 17.7356L17.5885 20.202L15.1221 22.6668C14.8498 22.9391 14.8498 23.3806 15.1221 23.6527C15.3944 23.9252 15.8359 23.9252 16.1082 23.6527L18.5746 21.188L21.0425 23.6559C21.3148 23.9282 21.7562 23.9282 22.0285 23.6559C22.3008 23.3836 22.3008 22.9422 22.0285 22.6699L19.5609 20.2023Z"\
                fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                </svg>\
            </a>
        </div>
        </li>`

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item active-item">\
                <a href="javascript:void(0)" onclick="easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();easyassist_show_agent_information_modal();" id="show-agent-details-button">\
                    <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M16.0001 0C24.8366 0 32 7.16344 32 16C32 24.8365 24.8366 32 16.0001 32C7.16347 32 0 24.8365 0 16C0 7.16344 7.16347 0 16.0001 0ZM16.2001 22.4C15.5374 22.4 15.0001 22.9373 15.0001 23.6C15.0001 24.2628 15.5374 24.8 16.2001 24.8C16.8627 24.8 17.4001 24.2628 17.4001 23.6C17.4001 22.9373 16.8627 22.4 16.2001 22.4ZM16.2001 7.19999C13.5092 7.19999 11.2 9.50767 11.2 12.2C11.2 12.7523 11.6477 13.2 12.2 13.2C12.6833 13.2 13.0864 12.8572 13.1797 12.4015L13.1948 12.3022L13.2044 12.047C13.2914 10.5229 14.6646 9.2 16.2001 9.2C17.7878 9.2 19.2 10.6107 19.2 12.2C19.2009 13.1496 18.8635 13.832 17.9044 14.9164L17.7387 15.1009L16.917 15.9792C15.6119 17.3974 15.0601 18.3762 15.0704 19.8071C15.0743 20.3594 15.5253 20.804 16.0774 20.8001C16.5262 20.7968 16.9039 20.4985 17.0275 20.0906L17.0515 19.9946L17.0659 19.8951L17.0704 19.7928L17.0728 19.6635C17.1016 19.0229 17.3881 18.4748 18.0978 17.6581L18.2453 17.4911L19.0572 16.6217C20.5852 14.9754 21.2017 13.8953 21.2 12.199C21.2 9.50569 18.8918 7.19999 16.2001 7.19999Z"\
                        fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                    </svg>\
                </a>
            </div>
        </li>`;

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item active-item">\
                <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();easyassist_show_feedback_form();easyassist_hide_agent_information_modal();easyassist_hide_livechat_iframe();" id="show-agent-details-button">\
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3.23041 3L14.7702 15" stroke="#D70000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M14.7699 3L3.23007 15" stroke="#D70000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </a>
            </div>
        </li>`

        sidenav_menu_html += `
        <li class="nexttabbtn">
            <div>
                <a id="next_button" href="javascript:void(0)" class="nexttabbtn" style="margin: 0px">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2341 16.5873L15.6179 12.9779C16.1274 12.4344 16.1274 11.5564 15.6179 11.0129L12.2341 7.40354C11.411 6.53952 10 7.1527 10 8.39299V15.5979C10 16.8521 11.411 17.4653 12.2341 16.5873Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                    </svg>
                </a>
            </div>
        </li>
        </ul>
        </div>`


    div_model.innerHTML = sidenav_menu_html;
    document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function update_navbar_buttons() {
        let ul_items_element = document.getElementById("ul_items")
        let scroll_left = ul_items_element.scrollLeft
        let window_width = window.innerWidth - 80
    
        if (scroll_left <= 0) {
            try {
                let previous_button_element = document.getElementById("previous_button");
                previous_button_element = previous_button_element.children[0].children[0];
                previous_button_element.style.setProperty("fill", "#CBCACA")
            } catch(err) {
                console.log(err);
            }
        } else {
            try {
                let previous_button_element = document.getElementById("previous_button");
                previous_button_element = previous_button_element.children[0].children[0];
                previous_button_element.style.setProperty("fill", "#4D4D4D")
            } catch (err) {
                console.log(err);
            }
        }
    
        if (scroll_left + window_width >= ul_items_element.scrollWidth) {
            try {
                let next_button_element = document.getElementById("next_button");
                next_button_element = next_button_element.children[0].children[0];
                next_button_element.style.setProperty("fill", "#CBCACA");
            } catch (err) {
                console.log(err)
            }
        } else {
            try {
                let next_button_element = document.getElementById("next_button");
                next_button_element = next_button_element.children[0].children[0];
                next_button_element.style.setProperty("fill", "#4D4D4D");
            } catch (err) {
                console.log(err)
            }
        }
    }

    function easyassist_add_floating_sidenav_menu() {
        var sidenav_menu = "";
        let sidenav_style = "";

        if (EASYASSIST_COBROWSE_META.floating_button_position == "left") {
            sidenav_style = "left: 0 !important;";
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            sidenav_style = "right: 0 !important;";
        }


        if (EASYASSIST_COBROWSE_META.is_mobile == true) {
            if (EASYASSIST_COBROWSE_META.floating_button_position == "top" ||
                EASYASSIST_COBROWSE_META.floating_button_position == "bottom") {
                easyassist_create_navbar_menu();

                let window_innerwidth = window.innerWidth;
                let options_width = window_innerwidth - 80;
                let icon_width = options_width / 3;
                let display_flex_counter = 0;

                let cobrowse_icons = document.getElementsByClassName('cobrowse-icons');
                document.getElementById('ul_items').style.width = options_width;

                for (let i = 0; i < cobrowse_icons.length; i++) {
                    cobrowse_icons[i].style.width = icon_width + "px";
                    if (cobrowse_icons[i].style.display != "none") {
                        display_flex_counter += 1;
                    }
                }

                try {
                    let previous_button_element = document.getElementById("previous_button");
                    previous_button_element = previous_button_element.children[0].children[0];
                    previous_button_element.style.setProperty("fill", "#CBCACA")
                } catch(err) {
                    console.log(err)
                }
        
                if (display_flex_counter <= 3) {
                    try {
                        let next_button_element = document.getElementById("next_button");
                        next_button_element = next_button_element.children[0].children[0];
                        next_button_element.style.setProperty("fill", "#CBCACA");
                    } catch (err) {
                        console.log(err)
                    }
                } else {
                    try {
                        let next_button_element = document.getElementById("next_button");
                        next_button_element = next_button_element.children[0].children[0];
                        next_button_element.style.setProperty("fill", "#4D4D4D");
                    } catch (err) {
                        console.log(err)
                    }
                }

                const left_button = document.querySelector('.closebtn1');
                left_button.onclick = function () {
                    document.getElementById('ul_items').scrollBy(-(window_innerwidth - 80), 0);
                };

                const next_button = document.querySelector('.nexttabbtn');
                next_button.onclick = function () {
                    document.getElementById('ul_items').scrollBy((window_innerwidth - 80), 0);
                };

                const easyassist_navbar_observer = new MutationObserver(function (mutations, observer) {
                    update_navbar_buttons();
                })

                easyassist_navbar_observer.observe(document.getElementById("ul_items"), { attributes: true, subtree: true })
                
                document.getElementById("ul_items").addEventListener("scroll", update_navbar_buttons);

            } else {
                sidenav_menu = '\
                <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar_wrapper" id="easyassist-sidenav-menu-id" style="display:none;' + sidenav_style + '">\
                    <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar" id="easyassist-maximise-sidenav-button">\
                        <a href="javascript:void(0)" onclick="easyassist_show_dialog_modal();">\
                        <svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M1.93418 -5.07244e-07L6.76934 5L11.6045 -8.45407e-08L13.5386 1L6.76934 8L0.000113444 0.999999L1.93418 -5.07244e-07Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        </svg>\
                        </a>\
                    </div>';
            }
        } else {
            sidenav_menu = '\
            <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar_wrapper" id="easyassist-sidenav-menu-id" style="display:none;' + sidenav_style + '">\
            <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar" id="easyassist-sidenav-submenu-id" onmouseover="easyassist_on_client_mouse_over_nav_bar(this)" onmouseout="easyassist_on_mouse_out_nav_bar(this)">\
                <a href="javascript:void(0)" onclick="easyassist_close_sidenav();" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">'

            if (EASYASSIST_COBROWSE_META.floating_button_position == "top" ||
                EASYASSIST_COBROWSE_META.floating_button_position == "bottom") {
                sidenav_menu += '<svg class="minimize-icon-rotate" width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">'
            } else {
                sidenav_menu += '<svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">'
            }

            sidenav_menu += '<path d="M11.6044 8L6.76923 3L1.93407 8L-4.37114e-08 7L6.76923 -2.95892e-07L13.5385 7L11.6044 8Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                </svg>\
                <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                    </svg>\
                    <span>Minimise</span>\
                </label>\
                </a>'


                if(EASYASSIST_COBROWSE_META.enable_chat_functionality && EASYASSIST_COBROWSE_META.enable_chat_bubble == false){
                    sidenav_menu += '<a href="javascript:void(0)" onclick="easyassist_show_livechat_iframe();easyassist_hide_feedback_form();" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"\
                          d="M11 1.83325C16.0625 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0625 20.1666 11 20.1666C9.49628 20.1666 8.04388 19.8035 6.74278 19.12L2.80991 20.1439C2.39349 20.2525 1.96797 20.0028 1.85951 19.5863C1.82597 19.4576 1.82596 19.3224 1.85948 19.1936L2.8828 15.2626C2.19741 13.9602 1.83331 12.5058 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM12.1474 11.9166H8.02081L7.92752 11.9228C7.59195 11.9684 7.33331 12.256 7.33331 12.6041C7.33331 12.9521 7.59195 13.2398 7.92752 13.2854L8.02081 13.2916H12.1474L12.2407 13.2854C12.5763 13.2398 12.8349 12.9521 12.8349 12.6041C12.8349 12.256 12.5763 11.9684 12.2407 11.9228L12.1474 11.9166ZM13.9791 8.70825H8.02081L7.92752 8.71453C7.59195 8.76005 7.33331 9.04769 7.33331 9.39575C7.33331 9.74381 7.59195 10.0315 7.92752 10.077L8.02081 10.0833H13.9791L14.0725 10.077C14.408 10.0315 14.6666 9.74381 14.6666 9.39575C14.6666 9.04769 14.408 8.76005 14.0725 8.71453L13.9791 8.70825Z"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                          </svg>\
                        <span>Chat with the Agent</span>\
                      </label>\
                    </a>'
                }

                if(EASYASSIST_COBROWSE_META.customer_initiate_voice_call == true && EASYASSIST_COBROWSE_META.enable_voip_calling){
                sidenav_menu += '<a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="open_invite_agent_modal()" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)" easyassist_avoid_sync="true">\
                    <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"\
                          d="M9.60979 10.3936C12.934 13.7169 13.6882 9.87218 15.8047 11.9873C17.8452 14.0272 19.018 14.4359 16.4327 17.0205C16.1089 17.2808 14.0514 20.4118 6.82051 13.183C-0.411222 5.95325 2.718 3.89362 2.97832 3.56988C5.5699 0.978123 5.97156 2.15774 8.01208 4.19769C10.1286 6.31366 6.28556 7.07026 9.60979 10.3936Z"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                          </svg>\
                        <span>Voice call</span>\
                      </label>\
                    </a>'
                }
                else if(EASYASSIST_COBROWSE_META.customer_initiate_video_call == true && EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting){
                sidenav_menu += '<a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="open_invite_agent_modal()" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)" easyassist_avoid_sync="true">\
                    <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" />\
                    </svg>\
                    <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        </svg>\
                    <span>Video call</span>\
                    </label>\
                </a>'
                } else if(EASYASSIST_COBROWSE_META.customer_initiate_video_call_as_pip == true && EASYASSIST_COBROWSE_META.enable_voip_with_video_calling){
                sidenav_menu += '<a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="open_invite_agent_modal()" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)" easyassist_avoid_sync="true">\
                    <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" />\
                    </svg>\
                    <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        </svg>\
                    <span>Video call</span>\
                    </label>\
                </a>'
                }
                sidenav_menu += '<a href="javascript:void(0)" onclick="easyassist_revoke_edit_access();" id="revoke-edit-access-button" style="display:none;" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" fill-rule="evenodd" clip-rule="evenodd" d="M19.2778 2.72247L19.1376 2.59012C17.8495 1.4431 15.8741 1.48722 14.6388 2.72247L13.7492 3.61155L18.3885 8.24989L19.2778 7.36141C20.5131 6.12616 20.5572 4.15082 19.4102 2.8627L19.2778 2.72247ZM12.7775 4.58321L17.4168 9.22249L16.5978 10.0415C15.7155 9.3843 14.6489 9 13.5 9C10.4624 9 8 11.6863 8 15C8 16.0668 8.25521 17.0686 8.70266 17.9366L8.30685 18.3324C8.05304 18.5862 7.73739 18.7694 7.39111 18.8638L2.70173 20.1427C2.18852 20.2827 1.7176 19.8117 1.85756 19.2986L3.13649 14.6092C3.23093 14.2629 3.4141 13.9473 3.66791 13.6934L12.7775 4.58321ZM5.98125 10.0832L4.60625 11.4582L2.52084 11.4586C2.14114 11.4586 1.83334 11.1508 1.83334 10.7711C1.83334 10.3914 2.14114 10.0836 2.52084 10.0836L5.98125 10.0832ZM9.64795 6.41656L8.27292 7.79156L2.52084 7.79194C2.14114 7.79194 1.83334 7.48414 1.83334 7.10444C1.83334 6.72475 2.14114 6.41694 2.52084 6.41694L9.64795 6.41656ZM11.9396 4.12488L13.3146 2.74989L2.52084 2.75028C2.14114 2.75028 1.83334 3.05808 1.83334 3.43778C1.83334 3.81748 2.14114 4.12528 2.52084 4.12528L11.9396 4.12488ZM19.0833 15.0417C19.0833 12.2572 16.8261 10 14.0417 10C11.2572 10 9 12.2572 9 15.0417C9 17.8261 11.2572 20.0833 14.0417 20.0833C16.8261 20.0833 19.0833 17.8261 19.0833 15.0417ZM14.6911 15.0418L16.3134 13.4204C16.4924 13.2414 16.4924 12.9512 16.3134 12.7722C16.1344 12.5933 15.8442 12.5933 15.6652 12.7722L14.0429 14.3936L12.4214 12.7721C12.2424 12.5932 11.9522 12.5932 11.7732 12.7721C11.5942 12.9511 11.5942 13.2413 11.7732 13.4203L13.3945 15.0416L11.7732 16.6619C11.5942 16.8409 11.5942 17.1311 11.7732 17.31C11.9522 17.4891 12.2424 17.4891 12.4214 17.31L14.0427 15.6898L15.665 17.3121C15.844 17.4911 16.1342 17.4911 16.3132 17.3121C16.4922 17.1331 16.4922 16.8429 16.3132 16.6639L14.6911 15.0418Z"/>\
                    </svg>\
                    <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                          </svg>\
                        <span>Revoke edit access</span>\
                    </label>\
                </a>\
                <a href="javascript:void(0)" onclick="easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();easyassist_show_agent_information_modal();" id="show-agent-details-button" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"\
                       d="M11 1.83325C16.0626 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0626 20.1666 11 20.1666C5.93737 20.1666 1.83331 16.0625 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM11.1146 14.6666C10.7349 14.6666 10.4271 14.9744 10.4271 15.3541C10.4271 15.7338 10.7349 16.0416 11.1146 16.0416C11.4942 16.0416 11.8021 15.7338 11.8021 15.3541C11.8021 14.9744 11.4942 14.6666 11.1146 14.6666ZM11.1146 5.95825C9.57291 5.95825 8.24998 7.28036 8.24998 8.82284C8.24998 9.13927 8.50646 9.39575 8.8229 9.39575C9.09978 9.39575 9.33073 9.19936 9.38417 8.93829L9.39283 8.88141L9.39833 8.73516C9.44816 7.86199 10.2349 7.10409 11.1146 7.10409C12.0242 7.10409 12.8333 7.91231 12.8333 8.82284C12.8338 9.36688 12.6405 9.75784 12.091 10.3791L11.9961 10.4848L11.5253 10.988C10.7776 11.8005 10.4615 12.3613 10.4674 13.1811C10.4696 13.4975 10.728 13.7522 11.0443 13.75C11.3014 13.7481 11.5178 13.5772 11.5886 13.3435L11.6024 13.2885L11.6106 13.2315L11.6132 13.1729L11.6146 13.0988C11.6311 12.7318 11.7952 12.4178 12.2018 11.9499L12.2863 11.8542L12.7515 11.3561C13.6269 10.4129 13.9801 9.79409 13.9791 8.82229C13.9791 7.27922 12.6567 5.95825 11.1146 5.95825Z"/>\
                  </svg>\
                  <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                          </svg>\
                        <span>Show agent details</span>\
                  </label>\
                </a>\
                 <hr style="color: black;width: 30px;margin: 0.3rem auto;border: 0;border-top: 1px solid rgba(0,0,0,.1);">\
                 <a href="javascript:void(0)" onclick="easyassist_show_feedback_form();" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                   <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                     <path fill="#D70000"\
                       d="M11 1.83325C16.0626 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0626 20.1666 11 20.1666C5.93737 20.1666 1.83331 16.0625 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM14.2361 7.76378L14.159 7.69722C13.9198 7.51971 13.5914 7.51751 13.35 7.69064L13.2638 7.76378L11 10.0273L8.73612 7.76378L8.65901 7.69722C8.41977 7.51971 8.0914 7.51751 7.84997 7.69064L7.76384 7.76378L7.69728 7.84089C7.51977 8.08013 7.51757 8.40849 7.6907 8.64993L7.76384 8.73605L10.0274 10.9999L7.76384 13.2638L7.69728 13.3409C7.51977 13.5801 7.51757 13.9085 7.6907 14.1499L7.76384 14.2361L7.84095 14.3026C8.08019 14.4801 8.40855 14.4823 8.64999 14.3092L8.73612 14.2361L11 11.9725L13.2638 14.2361L13.341 14.3026C13.5802 14.4801 13.9086 14.4823 14.15 14.3092L14.2361 14.2361L14.3027 14.1589C14.4802 13.9197 14.4824 13.5913 14.3093 13.3499L14.2361 13.2638L11.9726 10.9999L14.2361 8.73605L14.3027 8.65895C14.4802 8.41971 14.4824 8.09134 14.3093 7.8499L14.2361 7.76378L14.159 7.69722L14.2361 7.76378Z"/>\
                   </svg>\
                   <label style="background-color:#D70000">\
                        <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="#D70000"/>\
                          </svg>\
                        <span>End Session</span>\
                   </label>\
                 </a>\
              </div>'

            sidenav_menu += '<div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar" id="easyassist-maximise-sidenav-button" style="display:none;">\
                <a href="javascript:void(0)" onclick="easyassist_open_sidenav();" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">'

            if (EASYASSIST_COBROWSE_META.floating_button_position == "top" ||
                EASYASSIST_COBROWSE_META.floating_button_position == "bottom") {
                sidenav_menu += '<svg class="maximize-icon-rotate" width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">';
            } else {
                sidenav_menu += '<svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">';
            }

            sidenav_menu += '<path d="M1.93418 -5.07244e-07L6.76934 5L11.6045 -8.45407e-08L13.5386 1L6.76934 8L0.000113444 0.999999L1.93418 -5.07244e-07Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        </svg>\
                        <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                            </svg>\
                        <span>Maximise</span>\
                        </label>\
                    </a>\
                </div>'


        }

        sidenav_menu += '</div>';
        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            sidenav_menu += '\
                <div id="easyassist-cobrowse-voip-container" style="display: none;">\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-on-btn" type="button" onclick="easyassist_toggle_client_voice(this, true)" style="display: none;" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33597 0.721564C1.16629 0.55188 0.891186 0.551878 0.721503 0.721557C0.551819 0.891237 0.551816 1.16635 0.721496 1.33603L4.07021 4.68481V6.38759C4.07021 7.66741 5.10771 8.70491 6.38753 8.70491C6.87038 8.70491 7.31874 8.55723 7.6899 8.30457L8.35376 8.96844C7.84603 9.34868 7.2155 9.5739 6.53236 9.5739H6.2427L6.11733 9.57136C4.4957 9.50562 3.20122 8.17019 3.20122 6.53242V6.24276L3.19725 6.1838C3.16848 5.97172 2.98669 5.80826 2.76672 5.80826C2.52676 5.80826 2.33223 6.00279 2.33223 6.24276V6.53242L2.33458 6.66934C2.40339 8.66902 3.9736 10.2874 5.95304 10.4323L5.95303 11.7464L5.957 11.8053C5.98577 12.0174 6.16756 12.1809 6.38753 12.1809C6.62749 12.1809 6.82203 11.9864 6.82203 11.7464L6.82259 10.4323C7.63306 10.3728 8.3749 10.0663 8.97313 9.58783L11.439 12.0537C11.6086 12.2234 11.8837 12.2234 12.0534 12.0537C12.2231 11.884 12.2231 11.6089 12.0534 11.4392L1.33597 0.721564ZM7.05738 7.67204C6.85706 7.77672 6.62921 7.83591 6.38753 7.83591C5.58764 7.83591 4.93921 7.18748 4.93921 6.38759V5.55382L7.05738 7.67204Z" fill="white"/>\
                          <path d="M7.83585 2.91162V5.9926L8.66436 6.82113C8.69094 6.68069 8.70484 6.53576 8.70484 6.38759V2.91162C8.70484 1.6318 7.66735 0.594299 6.38753 0.594299C5.31701 0.594299 4.41603 1.32021 4.14997 2.30665L4.93921 3.0959V2.91162C4.93921 2.11173 5.58764 1.46329 6.38753 1.46329C7.18742 1.46329 7.83585 2.11173 7.83585 2.91162Z" fill="white"/>\
                          <path d="M9.39781 7.55459L10.0617 8.21848C10.306 7.70796 10.4428 7.13617 10.4428 6.53242V6.24276L10.4389 6.1838C10.4101 5.97172 10.2283 5.80826 10.0083 5.80826C9.76837 5.80826 9.57384 6.00279 9.57384 6.24276V6.53242L9.5713 6.65779C9.55859 6.97128 9.49843 7.27254 9.39781 7.55459Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn on microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-off-btn" type="button" onclick="easyassist_toggle_client_voice(this, false)" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M4.5 0C3.10203 0 1.96875 1.00736 1.96875 2.25001V6.25003C1.96875 7.49268 3.10203 8.50004 4.5 8.50004C5.89797 8.50004 7.03125 7.49268 7.03125 6.25003V2.25001C7.03125 1.00736 5.89797 0 4.5 0ZM2.8125 2.25001C2.8125 1.42158 3.56802 0.750004 4.5 0.750004C5.43198 0.750004 6.1875 1.42158 6.1875 2.25001V6.25003C6.1875 7.07846 5.43198 7.75004 4.5 7.75004C3.56802 7.75004 2.8125 7.07846 2.8125 6.25003V2.25001Z" fill="white"/>\
                          <path d="M0.84375 5.87527C0.84375 5.66817 0.65487 5.50027 0.421875 5.50027C0.18888 5.50027 0 5.66838 0 5.87548V6.24999C0 8.33268 1.79067 10.0436 4.07813 10.2327V11.625C4.07813 11.8321 4.26701 12 4.5 12C4.733 12 4.92188 11.8321 4.92188 11.625V10.2327C7.20934 10.0436 9 8.33268 9 6.24999V5.87528C9 5.66817 8.81112 5.50028 8.57812 5.50028C8.34513 5.50028 8.15625 5.6683 8.15625 5.8754V6.24999C8.15625 8.04492 6.51929 9.50001 4.5 9.50001C2.48071 9.50001 0.84375 8.04471 0.84375 6.24978V5.87527Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn off microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-end-btn" type="button" onclick="easyassist_end_cobrowse_video_meet()" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="13" height="5" viewBox="0 0 13 5" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M12.1528 3.3789L12.0384 3.97941C11.9313 4.54213 11.4055 4.92001 10.8098 4.86244L9.62424 4.74788C9.10762 4.69796 8.66745 4.33102 8.53601 3.84069L8.17026 2.47623C7.62889 2.25423 7.03222 2.15276 6.38025 2.17182C5.72828 2.19088 5.12184 2.32752 4.56093 2.58175L4.33437 3.85902C4.24849 4.34316 3.84901 4.70429 3.34307 4.75516L2.16441 4.87366C1.5763 4.93279 1.01242 4.55857 0.845229 3.99819L0.66606 3.39764C0.487718 2.79987 0.64687 2.17079 1.08386 1.74619C2.11552 0.743789 3.83556 0.241029 6.24398 0.237899C8.6559 0.234793 10.4295 0.734491 11.5648 1.73701C12.0424 2.15885 12.2661 2.78345 12.1528 3.3789Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" id="easyassist-icon-path-7-label">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>End Call</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn"  id="easyassist-client-meeting-video-on-btn" type="button" onclick="easyassist_toggle_client_video(this, true)" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33573 1.06458C1.16605 0.894898 0.890942 0.894895 0.721258 1.06457C0.551575 1.23425 0.551572 1.50936 0.721252 1.67905L1.62904 2.58685C1.01503 2.89701 0.593994 3.53357 0.593994 4.26846V9.19276C0.593994 10.2326 1.43696 11.0756 2.47681 11.0756H7.40111C8.13596 11.0756 8.77249 10.6546 9.08267 10.0406L11.4387 12.3967C11.6084 12.5664 11.8835 12.5664 12.0532 12.3967C12.2229 12.227 12.2229 11.9519 12.0532 11.7823L1.33573 1.06458ZM8.40133 9.35927C8.32189 9.83997 7.90431 10.2066 7.40111 10.2066H2.47681C1.91689 10.2066 1.46299 9.75268 1.46299 9.19276V4.26846C1.46299 3.76522 1.82965 3.34761 2.3104 3.26823L8.40133 9.35927Z" fill="white"/>\
                          <path d="M8.41494 6.91496V4.26846C8.41494 3.70854 7.96103 3.25463 7.40111 3.25463H4.75468L3.88571 2.38564H7.40111C8.44096 2.38564 9.28393 3.22861 9.28393 4.26846V4.36868L11.5224 3.0258C11.812 2.85192 12.1806 3.06052 12.1806 3.39831V10.0617C12.1806 10.2364 12.0821 10.3765 11.9469 10.447L11.3116 9.81166V4.16598L9.28393 5.38338V7.78397L8.41494 6.91496Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn on camera</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn"  id="easyassist-client-meeting-video-off-btn" type="button" onclick="easyassist_toggle_client_video(this, false)" style="display: none;" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="14" height="11" viewBox="0 0 14 11" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M8.225 0C9.48145 0 10.5 1.06705 10.5 2.38333V2.5102L13.2048 0.810331C13.5547 0.590233 14 0.854285 14 1.28187V9.71667C14 10.1442 13.5548 10.4082 13.2049 10.1883L10.5 8.48833V8.61667C10.5 9.93295 9.48145 11 8.225 11H2.275C1.01855 11 0 9.93295 0 8.61667V2.38333C0 1.06705 1.01855 0 2.275 0H8.225ZM8.225 1.1H2.275C1.59845 1.1 1.05 1.67457 1.05 2.38333V8.61667C1.05 9.32543 1.59845 9.9 2.275 9.9H8.225C8.90155 9.9 9.45 9.32543 9.45 8.61667V2.38333C9.45 1.67457 8.90155 1.1 8.225 1.1ZM12.95 2.25361L10.5 3.79463V7.20526L12.95 8.74526V2.25361Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn off camera</span>\
                       </label>\
                    </button>\
                    <button onclick="easyassist_toggle_meeting_iframe_visibility();" class="easyassist-show-cobrowse-meeting-btn">\
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
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-on-btn" type="button" onclick="easyassist_toggle_client_voice(this, true)" style="display: none;" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33597 0.721564C1.16629 0.55188 0.891186 0.551878 0.721503 0.721557C0.551819 0.891237 0.551816 1.16635 0.721496 1.33603L4.07021 4.68481V6.38759C4.07021 7.66741 5.10771 8.70491 6.38753 8.70491C6.87038 8.70491 7.31874 8.55723 7.6899 8.30457L8.35376 8.96844C7.84603 9.34868 7.2155 9.5739 6.53236 9.5739H6.2427L6.11733 9.57136C4.4957 9.50562 3.20122 8.17019 3.20122 6.53242V6.24276L3.19725 6.1838C3.16848 5.97172 2.98669 5.80826 2.76672 5.80826C2.52676 5.80826 2.33223 6.00279 2.33223 6.24276V6.53242L2.33458 6.66934C2.40339 8.66902 3.9736 10.2874 5.95304 10.4323L5.95303 11.7464L5.957 11.8053C5.98577 12.0174 6.16756 12.1809 6.38753 12.1809C6.62749 12.1809 6.82203 11.9864 6.82203 11.7464L6.82259 10.4323C7.63306 10.3728 8.3749 10.0663 8.97313 9.58783L11.439 12.0537C11.6086 12.2234 11.8837 12.2234 12.0534 12.0537C12.2231 11.884 12.2231 11.6089 12.0534 11.4392L1.33597 0.721564ZM7.05738 7.67204C6.85706 7.77672 6.62921 7.83591 6.38753 7.83591C5.58764 7.83591 4.93921 7.18748 4.93921 6.38759V5.55382L7.05738 7.67204Z" fill="white"/>\
                          <path d="M7.83585 2.91162V5.9926L8.66436 6.82113C8.69094 6.68069 8.70484 6.53576 8.70484 6.38759V2.91162C8.70484 1.6318 7.66735 0.594299 6.38753 0.594299C5.31701 0.594299 4.41603 1.32021 4.14997 2.30665L4.93921 3.0959V2.91162C4.93921 2.11173 5.58764 1.46329 6.38753 1.46329C7.18742 1.46329 7.83585 2.11173 7.83585 2.91162Z" fill="white"/>\
                          <path d="M9.39781 7.55459L10.0617 8.21848C10.306 7.70796 10.4428 7.13617 10.4428 6.53242V6.24276L10.4389 6.1838C10.4101 5.97172 10.2283 5.80826 10.0083 5.80826C9.76837 5.80826 9.57384 6.00279 9.57384 6.24276V6.53242L9.5713 6.65779C9.55859 6.97128 9.49843 7.27254 9.39781 7.55459Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn on microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-off-btn" type="button" onclick="easyassist_toggle_client_voice(this, false)" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M4.5 0C3.10203 0 1.96875 1.00736 1.96875 2.25001V6.25003C1.96875 7.49268 3.10203 8.50004 4.5 8.50004C5.89797 8.50004 7.03125 7.49268 7.03125 6.25003V2.25001C7.03125 1.00736 5.89797 0 4.5 0ZM2.8125 2.25001C2.8125 1.42158 3.56802 0.750004 4.5 0.750004C5.43198 0.750004 6.1875 1.42158 6.1875 2.25001V6.25003C6.1875 7.07846 5.43198 7.75004 4.5 7.75004C3.56802 7.75004 2.8125 7.07846 2.8125 6.25003V2.25001Z" fill="white"/>\
                          <path d="M0.84375 5.87527C0.84375 5.66817 0.65487 5.50027 0.421875 5.50027C0.18888 5.50027 0 5.66838 0 5.87548V6.24999C0 8.33268 1.79067 10.0436 4.07813 10.2327V11.625C4.07813 11.8321 4.26701 12 4.5 12C4.733 12 4.92188 11.8321 4.92188 11.625V10.2327C7.20934 10.0436 9 8.33268 9 6.24999V5.87528C9 5.66817 8.81112 5.50028 8.57812 5.50028C8.34513 5.50028 8.15625 5.6683 8.15625 5.8754V6.24999C8.15625 8.04492 6.51929 9.50001 4.5 9.50001C2.48071 9.50001 0.84375 8.04471 0.84375 6.24978V5.87527Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                              </svg>\
                            <span>Turn off microphone</span>\
                       </label>\
                    </button>\
                    <button class="easyassist-client-meeting-end-btn" type="button" onclick="easyassist_end_cobrowse_video_meet()" onmouseover="easyassist_show_tooltip(this)" onmouseout="easyassist_hide_tooltip(this)">\
                      <svg width="13" height="5" viewBox="0 0 13 5" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M12.1528 3.3789L12.0384 3.97941C11.9313 4.54213 11.4055 4.92001 10.8098 4.86244L9.62424 4.74788C9.10762 4.69796 8.66745 4.33102 8.53601 3.84069L8.17026 2.47623C7.62889 2.25423 7.03222 2.15276 6.38025 2.17182C5.72828 2.19088 5.12184 2.32752 4.56093 2.58175L4.33437 3.85902C4.24849 4.34316 3.84901 4.70429 3.34307 4.75516L2.16441 4.87366C1.5763 4.93279 1.01242 4.55857 0.845229 3.99819L0.66606 3.39764C0.487718 2.79987 0.64687 2.17079 1.08386 1.74619C2.11552 0.743789 3.83556 0.241029 6.24398 0.237899C8.6559 0.234793 10.4295 0.734491 11.5648 1.73701C12.0424 2.15885 12.2661 2.78345 12.1528 3.3789Z" fill="white"/>\
                      </svg>\
                      <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sidenav_menu);
        easyassist_initialize_drag_element();
    }

    function easyassist_initialize_drag_element() {
        try {
            var element = document.getElementById("easyassist-cobrowse-voip-container");
            if(!element) {
                return;
            }

            if(element.hasAttribute("data-easyassist-drag")) {
                return;
            }

            easyassist_drag_element = new EasyAssistDragElement(element);
        } catch(err) {
            console.log("easyassist_initialize_drag_element: ", err);
        }
    }

    function easyassist_initialize_drag_timer() {
        try {
            var element = document.getElementById("easyassist-minimized-connection-timer-modal-id");
            if(!element) {
                return;
            }

            if(element.hasAttribute("data-easyassist-drag")) {
                return;
            }

            easyassist_drag_element = new EasyAssistDragElement(element);
        } catch(err) {
            console.log("easyassist_initialize_drag_timer: ", err);
        }
    }

    function easyassist_relocate_drag_element() {
        try {
            easyassist_drag_element.relocate_element();
        } catch(err) {
            console.log("easyassist_relocate_drag_element: ", err);
        }
    }

    function easyassisst_add_dialog_modal() {
        var div_model = document.createElement("div");
        div_model.id = "cobrowse-mobile-modal"
        div_model.style = "transition: opacity 1s ease-out;";
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";

        var modal_html = ['<div class="easyassist-customer-connect-modal-content" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0" style="padding: 0px !important;">',
                '<div class="easyassist-customer-connect-modal-header" style="text-align: center; display: block !important; padding: 0.5rem 0.5rem 0 1rem!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<button type="button" id="mobile-modal-hide-btn" onclick="easyassist_hide_dialog_modal();" class="hide-modal-btn"><svg width="16" height="2" viewBox="0 0 16 2" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M15 2H1C0.734784 2 0.48043 1.89464 0.292893 1.70711C0.105357 1.51957 0 1.26522 0 1C0 0.734784 0.105357 0.48043 0.292893 0.292893C0.48043 0.105357 0.734784 0 1 0H15C15.2652 0 15.5196 0.105357 15.7071 0.292893C15.8946 0.48043 16 0.734784 16 1C16 1.26522 15.8946 1.51957 15.7071 1.70711C15.5196 1.89464 15.2652 2 15 2Z"',
                        'fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '</svg>',
                        '</button>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body" style="padding: 1rem 1.2rem!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<ul class="menu-items">',].join('');

                    if(EASYASSIST_COBROWSE_META.enable_chat_functionality == true){
                        modal_html += [
                        '<li>',
                            '<div class="menu-item active-item">',
                                '<a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();easyassist_show_livechat_iframe();easyassist_hide_feedback_form()">',
                                    '<svg width="26" height="26" viewBox="0 0 29 29" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M14.5001 0C22.508 0 29 6.49091 29 14.4978C29 22.5048 22.508 28.9957 14.5001 28.9957C12.1215 28.9957 9.82402 28.4215 7.76591 27.3404L1.54481 28.9598C0.886105 29.1316 0.213008 28.7367 0.0414436 28.0779C-0.0116107 27.8744 -0.0116264 27.6606 0.0413963 27.4569L1.66011 21.2396C0.575942 19.1798 0 16.8795 0 14.4978C0 6.49091 6.49189 0 14.5001 0ZM16.3151 15.9477H9.78752L9.63995 15.9575C9.10914 16.0296 8.70002 16.4845 8.70002 17.035C8.70002 17.5854 9.10914 18.0404 9.63995 18.1125L9.78752 18.1223H16.3151L16.4626 18.1125C16.9935 18.0404 17.4026 17.5854 17.4026 17.035C17.4026 16.4845 16.9935 16.0296 16.4626 15.9575L16.3151 15.9477ZM19.2125 10.8734H9.78752L9.63995 10.8833C9.10914 10.9553 8.70002 11.4102 8.70002 11.9607C8.70002 12.5112 9.10914 12.9662 9.63995 13.0382L9.78752 13.0481H19.2125L19.3602 13.0382C19.8909 12.9662 20.3 12.5112 20.3 11.9607C20.3 11.4102 19.8909 10.9553 19.3602 10.8833L19.2125 10.8734Z"',
                                        'fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                    '</svg>',
                                '</a>',
                            '</div>',
                            '<span>Chat with the Agent</span>',
                        '</li>',].join('');
                    }
                    
                    if(EASYASSIST_COBROWSE_META.customer_initiate_voice_call == true && EASYASSIST_COBROWSE_META.enable_voip_calling) {

                        modal_html += [
                        '<li>',
                            '<div class="menu-item active-item">',
                                '<a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="easyassist_hide_dialog_modal();easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();open_invite_agent_modal();">',
                                    '<svg width="26" height="26" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" d="M9.60979 10.3936C12.934 13.7169 13.6882 9.87218 15.8047 11.9873C17.8452 14.0272 19.018 14.4359 16.4327 17.0205C16.1089 17.2808 14.0514 20.4118 6.82051 13.183C-0.411222 5.95325 2.718 3.89362 2.97832 3.56988C5.5699 0.978123 5.97156 2.15774 8.01208 4.19769C10.1286 6.31366 6.28556 7.07026 9.60979 10.3936Z"/>',
                                    '</svg>',
                                '</a>',
                            '</div>',
                            '<span>Voice Call</span>',
                        '</li>',].join('');

                    } else if (EASYASSIST_COBROWSE_META.customer_initiate_video_call == true && EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {

                        modal_html += [
                            '<li>',
                                '<div class="menu-item active-item">',
                                    '<a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="easyassist_hide_dialog_modal();easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();open_invite_agent_modal();">',
                                        '<svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" />',
                                            '<path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                        '</svg>',
                                    '</a>',
                                '</div>',
                                '<span>Video Call</span>',
                            '</li>',].join('');
                    } else if (EASYASSIST_COBROWSE_META.customer_initiate_video_call_as_pip == true && EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {

                        modal_html += [
                            '<li>',
                                '<div class="menu-item active-item">',
                                    '<a href="javascript:void(0)" id="customer_side_call_initiate_icon" onclick="easyassist_hide_dialog_modal();easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();open_invite_agent_modal();">',
                                        '<svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                            '<path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" />',
                                            '<path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                        '</svg>',
                                    '</a>',
                                '</div>',
                                '<span>Video Call</span>',
                            '</li>',].join('');
                    }

                    modal_html += [
                        '<li>',
                            '<div class="menu-item">',
                                '<a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();easyassist_revoke_edit_access();" id="revoke-edit-access-button">',
                                    '<svg width="26" height="26" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path fill-rule="evenodd" clip-rule="evenodd" d="M26.5384 1.46154L26.3251 1.2602C24.3656 -0.484696 21.3606 -0.417579 19.4814 1.46154L18.1281 2.81405L25.1856 9.8701L26.5384 8.5185C28.4176 6.63939 28.4847 3.63441 26.7398 1.67486L26.5384 1.46154ZM16.6499 4.29218L23.7074 11.3497L22.4615 12.5956C21.1193 11.5958 19.4967 11.0112 17.749 11.0112C13.128 11.0112 9.38214 15.0977 9.38214 20.1387C9.38214 21.7615 9.77038 23.2855 10.4511 24.606L9.84894 25.2081C9.46283 25.5942 8.98265 25.8729 8.45587 26.0165L1.32219 27.962C0.541473 28.175 -0.17491 27.4584 0.0380027 26.6779L1.98357 19.5442C2.12723 19.0174 2.40588 18.5373 2.79198 18.151L16.6499 4.29218ZM6.31113 12.659L4.21943 14.7507L1.04701 14.7513C0.469396 14.7513 0.00115825 14.2831 0.00115825 13.7055C0.00115825 13.1279 0.469396 12.6596 1.04701 12.6596L6.31113 12.659ZM11.8891 7.08116L9.79732 9.17287L1.04701 9.17345C0.469396 9.17345 0.00115825 8.70521 0.00115825 8.12759C0.00115825 7.54999 0.469396 7.08173 1.04701 7.08173L11.8891 7.08116ZM15.3752 3.59495L17.4669 1.50325L1.04701 1.50384C0.469396 1.50384 0.00115825 1.97208 0.00115825 2.5497C0.00115825 3.12732 0.469396 3.59556 1.04701 3.59556L15.3752 3.59495ZM26.2425 20.2021C26.2425 15.9662 22.8088 12.5324 18.573 12.5324C14.3371 12.5324 10.9034 15.9662 10.9034 20.2021C10.9034 24.4379 14.3371 27.8716 18.573 27.8716C22.8088 27.8716 26.2425 24.4379 26.2425 20.2021ZM19.5609 20.2023L22.0288 17.7357C22.3011 17.4634 22.3011 17.0219 22.0288 16.7496C21.7565 16.4775 21.3151 16.4775 21.0428 16.7496L18.5749 19.2162L16.1082 16.7495C15.8359 16.4773 15.3944 16.4773 15.1221 16.7495C14.8498 17.0218 14.8498 17.4633 15.1221 17.7356L17.5885 20.202L15.1221 22.6668C14.8498 22.9391 14.8498 23.3806 15.1221 23.6527C15.3944 23.9252 15.8359 23.9252 16.1082 23.6527L18.5746 21.188L21.0425 23.6559C21.3148 23.9282 21.7562 23.9282 22.0285 23.6559C22.3008 23.3836 22.3008 22.9422 22.0285 22.6699L19.5609 20.2023Z"',
                                        'fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                        '</svg>',
                                '</a>',
                            '</div>',
                            '<span>Revoke edit access</span>',
                        '</li>',
                        '<li>',
                            '<div class="menu-item">',
                                '<a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();easyassist_hide_feedback_form();easyassist_hide_livechat_iframe();easyassist_show_agent_information_modal();" id="show-agent-details-button">',
                                    '<svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M16.0001 0C24.8366 0 32 7.16344 32 16C32 24.8365 24.8366 32 16.0001 32C7.16347 32 0 24.8365 0 16C0 7.16344 7.16347 0 16.0001 0ZM16.2001 22.4C15.5374 22.4 15.0001 22.9373 15.0001 23.6C15.0001 24.2628 15.5374 24.8 16.2001 24.8C16.8627 24.8 17.4001 24.2628 17.4001 23.6C17.4001 22.9373 16.8627 22.4 16.2001 22.4ZM16.2001 7.19999C13.5092 7.19999 11.2 9.50767 11.2 12.2C11.2 12.7523 11.6477 13.2 12.2 13.2C12.6833 13.2 13.0864 12.8572 13.1797 12.4015L13.1948 12.3022L13.2044 12.047C13.2914 10.5229 14.6646 9.2 16.2001 9.2C17.7878 9.2 19.2 10.6107 19.2 12.2C19.2009 13.1496 18.8635 13.832 17.9044 14.9164L17.7387 15.1009L16.917 15.9792C15.6119 17.3974 15.0601 18.3762 15.0704 19.8071C15.0743 20.3594 15.5253 20.804 16.0774 20.8001C16.5262 20.7968 16.9039 20.4985 17.0275 20.0906L17.0515 19.9946L17.0659 19.8951L17.0704 19.7928L17.0728 19.6635C17.1016 19.0229 17.3881 18.4748 18.0978 17.6581L18.2453 17.4911L19.0572 16.6217C20.5852 14.9754 21.2017 13.8953 21.2 12.199C21.2 9.50569 18.8918 7.19999 16.2001 7.19999Z"', 
                                        'fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                        '</svg>',
                                '</a>',
                            '</div>',
                            '<span>Show agent details</span>',
                        '</li>',
                    '</ul>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<div easyassist-data-scroll-x="0" easyassist-data-scroll-y="0"><button class="easyassist-modal-primary-btn end-session-btn" id="easyassist-co-browsing-connect-button" onclick="easyassist_hide_dialog_modal();easyassist_show_feedback_form();easyassist_hide_agent_information_modal();easyassist_hide_livechat_iframe();"',
                    'style="background-color:#D70000">End Session</button></div>',
                '</div>',
            '</div>'].join('')
            div_model.innerHTML = modal_html;
            document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_show_dialog_modal(){
        document.getElementById("cobrowse-mobile-modal").style.display = "flex";
        easyassist_hide_floating_sidenav_menu();
    }

    function easyassist_hide_dialog_modal() {
        document.getElementById("cobrowse-mobile-modal").style.display = "none";
        easyassist_show_floating_sidenav_menu();
    }

    function easyassist_show_floating_sidenav_menu() {
        if (document.getElementById("cobrowse-mobile-modal").style.display == "flex") {
            return
        }

        if (EASYASSIST_COBROWSE_META.is_mobile && (EASYASSIST_COBROWSE_META.floating_button_position == "top" || EASYASSIST_COBROWSE_META.floating_button_position == "bottom")) {
            document.getElementById("cobrowse-mobile-navbar").style.display = "flex";
        } else {
            document.getElementById("easyassist-sidenav-menu-id").style.display = "block";
        }
        
        if(EASYASSIST_COBROWSE_META.is_mobile == true){
            if (get_easyassist_cookie("easyassist_edit_access_granted") == "true") {
                document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "inherit";
            } else {
                document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "none";
            }
        }else{
            if (get_easyassist_cookie("easyassist_edit_access_granted") == "true") {
                document.getElementById("revoke-edit-access-button").style.display = "inherit";
            } else {
                document.getElementById("revoke-edit-access-button").style.display = "none";
            }
        }
        easyassist_create_close_nav_timeout();
        easyassist_hide_floating_sidenav_button();
        // easyassist_hide_greeting_bubble();
    }

    function easyassist_hide_floating_sidenav_menu() {
        try{
            document.getElementById("easyassist-sidenav-menu-id").style.display = "none";
        }catch(err){}
    }

    function easyassist_close_sidenav() {
        try {
            document.getElementById("easyassist-sidenav-submenu-id").style.display = "none";
            document.getElementById("easyassist-maximise-sidenav-button").style.display = "flex";
        } catch(err) {}
    }

    function easyassist_open_sidenav() {
        try {
            document.getElementById("easyassist-maximise-sidenav-button").style.display = "none";
            document.getElementById("easyassist-sidenav-submenu-id").style.display = "flex";
        } catch(err) {}
    }

    function easyassist_on_client_mouse_over_nav_bar() {
        easyassist_clear_close_nav_timeout();
    }

    function easyassist_on_mouse_out_nav_bar() { 
        easyassist_create_close_nav_timeout();
    }

    function easyassist_create_close_nav_timeout(){
        if(easyassist_close_nav_timeout == null){
            easyassist_close_nav_timeout = setTimeout(easyassist_close_sidenav, 15*1000);
        }
    }
    
    function easyassist_chat_bubble_css()
    {
        var css = ` <style>
                        .bg-grey{
                            background: grey;
                        }
                        
                        .bounce2 {
                            animation: bounce2 2s ;
                        }
                        
                        @keyframes bounce2 {
                            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
                            40% {transform: translateY(-40px);}
                            60% {transform: translateY(-25px);}
                        }

                        #chat-minimize-icon-wrapper{
                            position: fixed;
                            right: 50px;
                            bottom: 50px;
                            cursor:pointer;
                            z-index:20000;
                        }
                        
                        .minimize-chat-box-div{
                            width: 72px;
                            height: 72px;
                            position: fixed;
                            right: 50px;
                            bottom: 50px;
                            border-radius: 18px !important;
                            cursor: pointer;
                        }
                        .minimize-chat-box-div img{
                            max-width: 72px;
                            max-height: 72px;
                        }
                        
                        .minimize-chat-box-div .default-icon{
                            width: 100%;
                            height: 100%;
                            background: ${EASYASSIST_COBROWSE_META.floating_button_bg_color};
                            border: 2.5px solid #FFFFFF;
                            box-shadow: 0px 8px 8px rgba(0, 32, 51, 0.04), 0px 12px 28px rgba(0, 32, 51, 0.12) !important;
                            border-radius: 18px !important;
                            display: flex;
                            align-items:center;
                            justify-content: center;
                        }
                        
                        .chat-svg-icon{
                            height: 36px;
                            width: 36px;
                        }
                        
                        /* css for right side button/icon------- */
                        
                        #chat-minimize-icon-wrapper .chat-talk-bubble {
                            display: block;
                            width: 240px;
                            height: auto;
                            background-color: #ffffff;
                            position: fixed;
                            bottom: 120px;
                            right: 135px;
                        }
                        
                        #chat-minimize-icon-wrapper .border{
                            border: 2px solid ${EASYASSIST_COBROWSE_META.floating_button_bg_color} !important;
                        }

                        #chat-minimize-icon-wrapper{
                            overflow: visible !important;
                        }
                        
                        #chat-minimize-icon-wrapper .round{
                            border-radius: 10px !important;
                            -webkit-border-radius: 10px;
                            -moz-border-radius: 10px;
                        }
                        
                        #chat-minimize-icon-wrapper .tri-right.border.btm-right-in:before {
                            content: ' ';
                            position: absolute;
                            width: 0;
                            height: 0;
                            left: auto;
                            right: -16px;
                            bottom: -2px;
                            border: 14px solid;
                            border-color: transparent transparent ${EASYASSIST_COBROWSE_META.floating_button_bg_color} transparent;
                        }
                        #chat-minimize-icon-wrapper .tri-right.btm-right-in:after {
                            content: ' ';
                            position: absolute;
                            width: 0;
                            height: 0;
                            left: auto;
                            right: -11px;
                            top: auto;
                            bottom: 0px;
                            border: 12px solid;
                            border-color: transparent transparent #ffffff transparent;
                        }

                        #chat-minimize-icon-wrapper .tri-left.border.btm-left-in:before {
                            content: ' ';
                            position: absolute;
                            width: 0;
                            height: 0;
                            left: auto;
                            right: 222px;
                            bottom: -2px;
                            border: 14px solid;
                            border-color: transparent transparent ${EASYASSIST_COBROWSE_META.floating_button_bg_color} transparent;
                        }
                        #chat-minimize-icon-wrapper .tri-left.btm-left-in:after {
                            content: ' ';
                            position: absolute;
                            width: 0;
                            height: 0;
                            left: auto;
                            right: 222px;
                            top: auto;
                            bottom: 0px;
                            border: 12px solid;
                            border-color: transparent transparent #ffffff transparent;
                        }
                        
                        /* talk bubble contents */
                        #chat-minimize-icon-wrapper .talktext{
                            padding: 8px 12px;
                            text-align: left;
                            font-size: 15px;
                            color: ${EASYASSIST_COBROWSE_META.floating_button_bg_color};
                            display: flex;
                        }
                        #chat-minimize-icon-wrapper .talktext p{
                            /* remove webkit p margins */
                            -webkit-margin-before: 0em;
                            -webkit-margin-after: 0em;
                            word-break: break-all;
                            word-wrap: break-word;
                            hyphens: auto;
                        }
                        
                        #chat-minimize-icon-wrapper .close-bubble-container{
                            position: absolute;
                            width: 23px;
                            height: 23px;
                            right: -15px;
                            top: -32px;
                            border-radius: 13px !important;
                            display:flex !important;
                            align-items:center !important;
                            justify-content:center !important;
                            background: #ffffff;
                            border: 1px solid ${EASYASSIST_COBROWSE_META.floating_button_bg_color} !important;
                            cursor: pointer;
                        }
                        
                        
                        #chat-minimize-icon-wrapper .talk-bubble-icon {
                            display: block;
                            max-width: 247px !important;
                            height: auto;
                            background-color: #ffffff;
                            position: fixed;
                            bottom: 52%;
                            right: 60px;
                            margin-right: 1rem;
                        }
                        
                        @media (max-width:520px) {
                            .chat-svg-icon{
                                height: 36px;
                                width: 36px;
                            }
                            #chat-minimize-icon-wrapper .chat-talk-bubble{
                                bottom: 65px;
                                right: 70px;
                            }
                            
                            .minimize-chat-box-div{
                                right: 30px;
                                bottom: 40px;
                            }
                        }

                        .chat-talk-bubble{
                            overflow: visible !important;
                        }
                        
                        @media (max-width:440px) {
                            #chat-minimize-icon-wrapper .chat-talk-bubble {
                                max-width: 170px;
                            }
                        }
                        
                        /* @media (min-width:520px) and (max-height:800px) {
                        .minimize-chat-box-div{
                            width: 64px;
                            height: 64px;
                        }
                        
                        #chat-minimize-icon-wrapper .chat-talk-bubble{
                            bottom: 115px;
                            right: 130px;
                        }
                        } */
                        
                        .default-chat-icon{
                            width: 90px !important;
                            height: 90px !important;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            position: relative;
                            margin: 15px 0;
                        }
                        
                        .default-chat-icon img{
                            width: 90px;
                            height: 90px;
                            padding: 10px;
                        }
                        
                        #new-image-div img{
                            rsor: pointer;
                        }
                        
                        #new-image-div{
                            order: 1px solid #2F80ED;
                        }
                        
                        .remove-uploaded-icon{
                            width: 24px;
                            height: 24px;
                            display: flex;
                            align-items:center;
                            justify-content: center;
                            background: #f8f8f8;
                            filter: drop-shadow(0px 0px 2px rgba(0, 0, 0, 0.13));
                            border-radius: 12px !important;
                            cursor: pointer;
                            position: absolute;
                            top: -10px;
                            right: 27px;
                        /* display: none; */
                        }
                        
                        .minimize-chat-div{
                            width: 30px;
                            height: 30px;
                            border-radius: 15px !important;
                            background: #f8f8f8;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            position: absolute !important;
                            right: 20px;
                            bottom: 20px;
                            opacity: 1 !important;
                        }
                        
                        .agent-name{
                            width: 100px;
                        }
                        
                        .truncate {
                            display: inline-block;
                            white-space: nowrap;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            margin-bottom: 0;
                        }
                        
                        .animate__slideInUp {
                            -webkit-animation-name: slideInUp;
                            animation-name: slideInUp;
                        }
                        @keyframes slideInUp {
                        
                            0% {
                                -webkit-transform: translate3d(0,100%,0);
                                transform: translate3d(0,100%,0);
                                visibility: visible;
                            }

                            100% {
                                -webkit-transform: translateZ(0);
                                transform: translateZ(0);
                            }
                        }

                        .allincall-scale-out-br {
                            -webkit-animation: allincall-scale-out-br 1s cubic-bezier(0.550, 0.085, 0.680, 0.530) both;
                            animation: allincall-scale-out-br 1s cubic-bezier(0.550, 0.085, 0.680, 0.530) both;
                        }
                        
                        @keyframes allincall-scale-out-br {
                            0% {
                                -webkit-transform: scale(1);
                                transform: scale(1);
                                -webkit-transform-origin: 100% 100%;
                                transform-origin: 100% 100%;
                                opacity: 1;
                            }
                        
                            100% {
                                -webkit-transform: scale(0);
                                transform: scale(0);
                                -webkit-transform-origin: 85% 90%;
                                transform-origin: 85% 90%;
                                opacity: 1;
                            }
                        }

                        .allincall-scale-out-br-right-side {
                            -webkit-animation: allincall-scale-out-br-right-side 1s cubic-bezier(0.550, 0.085, 0.680, 0.530) both;
                            animation: allincall-scale-out-br-right-side 1s cubic-bezier(0.550, 0.085, 0.680, 0.530) both;            
                        }
                        
                        @keyframes allincall-scale-out-br-right-side {
                            0% {
                                -webkit-transform: scale(1);
                                transform: scale(1);
                                -webkit-transform-origin: -0% 100%;
                                transform-origin: 0% 100%;
                                opacity: 1;
                            }
                        
                            100% {
                                -webkit-transform: scale(0);
                                transform: scale(0);
                                -webkit-transform-origin: 15% 85%;
                                transform-origin:  15% 85%;
                                opacity: 1;
                            }
                        }
                    </style>`;

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', css);
    }

    function easyassist_add_chat_bubble_body() {
        if(EASYASSIST_COBROWSE_META.is_mobile || EASYASSIST_COBROWSE_META.enable_chat_bubble == false)
            return;

        let chat_bubble_style = ";";
        let icon_src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/" + EASYASSIST_COBROWSE_META.chat_bubble_icon_source

        if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            chat_bubble_style = "left:50px;"
        }

        var chat_bubble = `<div id="chat-minimize-icon-wrapper" class="chat-minimize-icon-wrapper" style="display:none; broder: 2px solid ${EASYASSIST_COBROWSE_META.floating_button_bg_color}!important;">
                            <div class="minimize-chat-box-div d-flex align-items-center justify-content-center" style=${chat_bubble_style} onclick="easyassist_show_livechat_iframe()" >`
        
        var chat_icon = ""
        if(EASYASSIST_COBROWSE_META.chat_bubble_icon_source){
            chat_icon = `<img  src="${icon_src}" alt="Chat Icon">`
        } else {
            chat_icon = `<div class="default-icon">
                            <svg class="chat-svg-icon" width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M11.7863 35.1339C9.27699 34.0647 5.99995 32.6685 6 28.663V12.7989C6 9.29217 9.16944 6 12.5454 6H36.4421C39.7148 6 42 9.17283 42 12.7989V28.663C42 30.9293 41.1273 35.4619 37.6364 35.4619H20.1819L14.7273 39.9945C9.73827 43.9669 10.5415 41.5381 12.0207 37.0651L12.0208 37.0649L12.0209 37.0645C12.1895 36.5547 12.3669 36.0184 12.5454 35.4619C12.3039 35.3544 12.0494 35.2459 11.7863 35.1339ZM14.7267 24.1303C15.9317 24.1303 16.9085 23.1156 16.9085 21.864C16.9085 20.6123 15.9317 19.5977 14.7267 19.5977C13.5218 19.5977 12.5449 20.6123 12.5449 21.864C12.5449 23.1156 13.5218 24.1303 14.7267 24.1303ZM34.3636 21.864C34.3636 23.1156 33.3868 24.1303 32.1818 24.1303C30.9768 24.1303 30 23.1156 30 21.864C30 20.6123 30.9768 19.5977 32.1818 19.5977C33.3868 19.5977 34.3636 20.6123 34.3636 21.864ZM23.4543 24.1303C24.6593 24.1303 25.6361 23.1156 25.6361 21.864C25.6361 20.6123 24.6593 19.5977 23.4543 19.5977C22.2493 19.5977 21.2725 20.6123 21.2725 21.864C21.2725 23.1156 22.2493 24.1303 23.4543 24.1303Z" fill="white"/>
                            </svg>
                        </div>`
        }

        chat_bubble += chat_icon
        chat_bubble += `</div>`

        if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            chat_bubble += `<div id="chat-talk-bubble" class="chat-talk-bubble tri-left border round btm-left-in" style="display:none; bottom:120px; left: 135px;">`
        } else {
            chat_bubble += `<div id="chat-talk-bubble" class="chat-talk-bubble tri-right border round btm-right-in" style="display:none;">`
        }
        
        chat_bubble += `<div class="talktext"  onclick="easyassist_show_livechat_iframe()" >
                                    <p id="talktext-p" class="mb-0"></p>
                                </div>
                                <div class="close-bubble-container " onclick='hide_chat_bubble_greeting_div()'>
                                    <span id="close-bubble">
                                        <svg width="9" height="9" viewBox="0 0 9 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M8.18294 8.2916L4.85662 4.96221L4.5029 4.60817L4.14919 4.96221L0.821579 8.29285L0.707617 8.17897L4.03996 4.85394L4.39469 4.5L4.03996 4.14606L0.70761 0.821061L0.821587 0.707156L4.14919 4.03779L4.50262 4.39155L4.85634 4.03807L8.1839 0.712656L8.29266 0.821344L4.96556 4.14633L4.61167 4.5L4.96556 4.85366L8.29391 8.17993L8.18294 8.2916Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" stroke="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                                        </svg>
                                    </span>
                                </div>
                            </div>
                        </div>`
           
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', chat_bubble);
    }

    function easyassist_show_chat_bubble() {
        if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
        }
    }

    function easyassist_clear_close_nav_timeout(){
        clearTimeout(easyassist_close_nav_timeout);
        easyassist_close_nav_timeout = null;
    }

    function easyassist_add_agent_information_modal(){
        var lighten_theme_color = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 60);

        var div_model = document.createElement("div");
        div_model.id = "easyassist-agent-information-modal"
        div_model.style.display = "none";
        div_model.style.cssText += 'z-index: 2147483647 !important';
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
        	'<div class="easyassist-customer-connect-modal-content">',
        		'<div class="easyassist-customer-connect-modal-header">',
        			'<div style="display:flex;align-items:center;flex-direction:column;">',
        				'<h6 style="padding-bottom:12px;" id="easyassist-agent-info-modal-header">Agent Details</h6>',
        				'<div class="agent-profile">',
                            '<svg class = "agent-profile-svg" width="76" height="70" viewBox="0 0 76 70" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<path d="M56.6469 21.6467V23.2422H52.5453V21.6467C52.5453 11.9725 44.6744 4.10156 35.0002 4.10156C25.326 4.10156 17.4551 11.9725 17.4551 21.6467V23.2422H13.3535V21.6467C13.3535 9.71113 23.0633 0 35.0002 0C46.9371 0 56.6469 9.71113 56.6469 21.6467Z" fill="' + lighten_theme_color + '"/>',
                            '<path d="M56.6467 21.6467V23.2422H52.5451V21.6467C52.5451 11.9725 44.6742 4.10156 35 4.10156V0C46.9369 0 56.6467 9.71113 56.6467 21.6467Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '<path d="M23.9653 33.9875H16.4496C14.5674 33.9875 13.0415 32.4616 13.0415 30.5794V24.5773C13.0415 22.6951 14.5674 21.1692 16.4496 21.1692H23.9653V33.9875Z" fill="' + lighten_theme_color + '"/>',
                            '<path d="M45.7607 33.9875H53.5502C55.4324 33.9875 56.9583 32.4616 56.9583 30.5794V24.5773C56.9583 22.6951 55.4324 21.1692 53.5502 21.1692H45.7607V33.9875Z" fill="' + lighten_theme_color + '"/>',
                            '<path d="M70 64.2017V69.9999H55.8783L53.8275 67.9492L51.7768 69.9999H18.2232L16.1725 67.9492L14.1217 69.9999H0V64.2017C0 61.6943 1.61055 59.4726 3.99219 58.6906L25.0004 51.8054H45.0584V51.8246L66.0078 58.6906C68.3895 59.4726 70 61.6943 70 64.2017Z" fill="' + lighten_theme_color + '"/>',
                            '<path d="M70 64.2017V69.9999H55.8783L53.8275 67.9492L51.7768 69.9999H35V51.8054H45.0584V51.8246L66.0078 58.6906C68.3895 59.4726 70 61.6943 70 64.2017Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '<path d="M45.0585 41.8811V51.8055C45.0585 51.8055 39.9999 56.8053 35.0001 56.8053C30.0003 56.8053 25.0005 51.8055 25.0005 51.8055V41.8811H45.0585Z" fill="#FDFEDC"/>',
                            '<path d="M45.0584 41.8811V51.8055C45.0584 51.8055 39.9998 56.8053 35 56.8053V41.8811H45.0584Z" fill="#FDFEDC"/>',
                            '<path d="M47.9498 20.8797V25.1836L46.6209 26.615H23.3787L22.0498 25.1836V20.8797C22.0498 17.3031 23.499 14.0656 25.8424 11.7223C28.1857 9.37891 31.4232 7.92969 34.9998 7.92969C42.1516 7.92969 47.9498 13.7279 47.9498 20.8797Z" fill="#4D4D4D"/>',
                            '<path d="M47.95 20.8797V25.1836L46.6211 26.615H35V7.92969C42.1518 7.92969 47.95 13.7279 47.95 20.8797Z" fill="#4D4D4D"/>',
                            '<path d="M47.9498 25.1916V34.0605C47.9498 34.9752 47.8664 35.868 47.7065 36.732C47.5766 37.4361 45.7609 38.7828 45.7609 38.7828C45.7609 38.7828 46.6277 40.1814 46.2805 40.8336C44.0588 45.0199 39.8397 47.8459 34.9998 47.8459C31.4232 47.8459 28.1857 46.3037 25.8424 43.8086C23.499 41.3135 22.0498 37.8682 22.0498 34.0605V25.1916H28.9568C31.2824 25.1916 33.4029 24.3084 34.9998 22.8592C36.8127 21.2131 37.9516 18.8383 37.9516 16.1982C37.9516 21.1652 41.9779 25.1916 46.9449 25.1916H47.9498Z" fill="#FDFEDC"/>',
                            '<path d="M47.95 25.1916V34.0605C47.95 34.9752 47.8666 35.868 47.7066 36.732C47.5768 37.4361 45.7611 38.7828 45.7611 38.7828C45.7611 38.7828 46.6279 40.1814 46.2807 40.8336C44.059 45.0199 39.8398 47.8459 35 47.8459V22.8592C36.8129 21.2131 37.9518 18.8383 37.9518 16.1982C37.9518 21.1652 41.9781 25.1916 46.9451 25.1916H47.95Z" fill="#FDFEDC"/>',
                            '<path d="M47.7058 36.7322C47.4364 38.1964 46.9483 39.5759 46.2798 40.8337H37.3521V36.7322H47.7058Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '<path d="M14.1211 63.7109H18.2227V70H14.1211V63.7109Z" fill="' + lighten_theme_color + '"/>',
                            '<path d="M51.7773 63.7109H55.8789V70H51.7773V63.7109Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '<path d="M76 52.5L73.3382 49.4443L73.7091 45.4029L69.7709 44.5048L67.7091 41L64 42.599L60.2909 41L58.2291 44.4938L54.2909 45.381L54.6618 49.4333L52 52.5L54.6618 55.5557L54.2909 59.6081L58.2291 60.5062L60.2909 64L64 62.39L67.7091 63.989L69.7709 60.4952L73.7091 59.5971L73.3382 55.5557L76 52.5ZM61.1418 56.8919L58.5455 54.2633C58.4443 54.162 58.3641 54.0417 58.3093 53.9092C58.2546 53.7767 58.2264 53.6346 58.2264 53.4912C58.2264 53.3477 58.2546 53.2057 58.3093 53.0732C58.3641 52.9407 58.4443 52.8204 58.5455 52.719L58.6218 52.6424C59.0473 52.2152 59.7455 52.2152 60.1709 52.6424L61.9273 54.4167L67.5455 48.7652C67.9709 48.3381 68.6691 48.3381 69.0945 48.7652L69.1709 48.8419C69.5964 49.269 69.5964 49.959 69.1709 50.3862L62.7127 56.8919C62.2655 57.319 61.5782 57.319 61.1418 56.8919Z" fill="#12DB00"/>',
                            '</svg>',
        				'</div>',
        			'</div>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-body">',
        			'<div class="easyassist-agent-information-text" id="easyassist-agent-information-agent-name">',
        			'</div>',
                    '<div class="easyassist-agent-information-text" style="display: none;" id="easyassist-agent-information-agent-email-id">',
        			'</div>',
        			'<div class="easyassist-agent-information-text" id="easyassist-agent-information-agent-location">',
        			'</div>',
        			'<div id="easyassist-agent-additional-details" style="display: none;">',
        			'</div>',
        			'<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align: center;">',
        				'<span class="easyassist-customer-connect-modal-small-text" style="font-size: 15px !important;"> You are connected to an official agent </span>',
        				'<svg width="15" height="15" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;">',
							'<path d="M13 6.5L11.5582 4.77286L11.7591 2.48857L9.62591 1.98095L8.50909 0L6.5 0.90381L4.49091 0L3.37409 1.97476L1.24091 2.47619L1.44182 4.76667L0 6.5L1.44182 8.22714L1.24091 10.5176L3.37409 11.0252L4.49091 13L6.5 12.09L8.50909 12.9938L9.62591 11.019L11.7591 10.5114L11.5582 8.22714L13 6.5ZM4.95182 8.98238L3.54545 7.49667C3.49068 7.4394 3.44722 7.37137 3.41756 7.29648C3.38791 7.22159 3.37265 7.14131 3.37265 7.06024C3.37265 6.97916 3.38791 6.89888 3.41756 6.82399C3.44722 6.74911 3.49068 6.68108 3.54545 6.62381L3.58682 6.58048C3.81727 6.33905 4.19545 6.33905 4.42591 6.58048L5.37727 7.58333L8.42045 4.38905C8.65091 4.14762 9.02909 4.14762 9.25955 4.38905L9.30091 4.43238C9.53136 4.67381 9.53136 5.06381 9.30091 5.30524L5.80273 8.98238C5.56045 9.22381 5.18818 9.22381 4.95182 8.98238Z" fill="#12DB00" fill-opacity="0.5"/>',
						'</svg>',
        			'</div>',
        		'</div>',
        		'<div class="easyassist-customer-connect-modal-footer" style="justify-content:center;">',
        			'<button class="easyassist-modal-primary-btn" id="easyassist-agent-info-modal-close-btn" onclick="easyassist_hide_agent_information_modal(this)">Close</button>',
        		'</div>',
        	'</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-agent-info-modal-close-btn").style.setProperty(
            'background', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
    }

    function easyassist_show_request_edit_access_form() {
        easyassist_hide_livechat_iframe();
        document.getElementById("easyassist-co-browsing-request-edit-access").style.display = "flex"
    }

    function easyassist_hide_request_edit_access_form() {
        document.getElementById("easyassist-co-browsing-request-edit-access").style.display = "none";
    }

    function easyassisst_add_edit_access_info_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-co-browsing-edit-access-info-modal"
        div_model.style = "transition: opacity 1s ease-out;";
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";

        var modal_html = ['<div class="easyassist-customer-connect-modal-content" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0" style="padding: 20px 10px !important;">',
        '<div class="easyassist-customer-connect-modal-header" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
            '<h6> Edit Access </h6>',
        '</div>',
        '<div class="easyassist-customer-connect-modal-body" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
            '<div class="easyassist-customer-connect-modal-content-wrapper" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                '<span style="font-size: 14px !important;"> If you want to Revoke the edit access at any moment just follow the below given steps -</span>',
            '</div>',
            '<div class="easyassist-customer-connect-modal-content-wrapper" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                '<ul class="edit_access_modal_images">',
                    '<li style="width: 29%; padding-left: 0;">',
                        '<svg class="edit_access_modal_images_ondesktop" width="54" height="232" viewBox="0 0 54 232" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<rect width="53.6029" height="232" rx="5" fill="white"/>',
                            '<rect x="0.5" y="92.5" width="53" height="46" rx="4.5" fill="white" stroke="#DEDEDE"/>',
                            '<path d="M26.9998 119C26.7661 119 26.5397 118.919 26.3598 118.77L20.3598 113.77C20.1556 113.6 20.0271 113.356 20.0028 113.092C19.9784 112.827 20.06 112.564 20.2298 112.36C20.3995 112.156 20.6434 112.027 20.9079 112.003C21.1723 111.979 21.4356 112.06 21.6398 112.23L26.9998 116.71L32.3598 112.39C32.4621 112.307 32.5798 112.245 32.7061 112.207C32.8325 112.17 32.9649 112.158 33.096 112.172C33.227 112.186 33.354 112.226 33.4696 112.289C33.5853 112.352 33.6873 112.437 33.7698 112.54C33.8614 112.643 33.9307 112.763 33.9735 112.894C34.0163 113.025 34.0316 113.163 34.0185 113.301C34.0053 113.438 33.964 113.57 33.8971 113.691C33.8303 113.811 33.7392 113.916 33.6298 114L27.6298 118.83C27.4447 118.956 27.2229 119.015 26.9998 119V119Z" fill="#0254D7"/>',
                        '</svg>',
                        '<svg class="edit_access_modal_images_onmobile" width="40" height="169" viewBox="0 0 40 169" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<rect width="39.0469" height="169" rx="5" fill="white"/>',
                            '<rect x="2.5" y="69.5" width="34.617" height="30" rx="4.5" fill="white" stroke="#DEDEDE"/>',
                            '<path d="M19.8083 86.8085C19.6542 86.8088 19.5048 86.7551 19.3861 86.6568L15.4287 83.3589C15.294 83.247 15.2093 83.0861 15.1932 82.9117C15.1771 82.7373 15.231 82.5636 15.343 82.4289C15.4549 82.2942 15.6158 82.2095 15.7902 82.1934C15.9646 82.1774 16.1383 82.2312 16.273 82.3432L19.8083 85.2981L23.3436 82.4487C23.4111 82.3939 23.4887 82.353 23.572 82.3283C23.6554 82.3036 23.7427 82.2956 23.8292 82.3048C23.9156 82.314 23.9993 82.3402 24.0756 82.3819C24.1519 82.4236 24.2192 82.4799 24.2736 82.5476C24.334 82.6155 24.3797 82.695 24.408 82.7813C24.4362 82.8677 24.4463 82.9589 24.4376 83.0493C24.429 83.1397 24.4017 83.2273 24.3576 83.3067C24.3135 83.3861 24.2534 83.4555 24.1813 83.5106L20.2238 86.6964C20.1017 86.7791 19.9554 86.8186 19.8083 86.8085V86.8085Z" fill="#0254D7"/>',
                        '</svg>',
                        '<p> Step 1: <br> <br> Click on the downward arrow icon</p>',
                    '</li>',
                    '<li style="width: 45%;">',
                        '<svg class="edit_access_modal_images_ondesktop revoke-access-icon" width="151" height="232" viewBox="0 0 151 232" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<rect x="0.5" y="0.5" width="52.6029" height="231" rx="4.5" fill="white" stroke="#DEDEDE"/>',
                            '<path d="M31.8268 25.9639C31.6311 25.9643 31.4414 25.8962 31.2907 25.7713L26.8015 22.0191L22.3039 25.6373C22.2182 25.7069 22.1196 25.7588 22.0138 25.7902C21.908 25.8215 21.797 25.8316 21.6873 25.82C21.5775 25.8083 21.4712 25.7751 21.3743 25.7221C21.2775 25.6692 21.192 25.5977 21.1229 25.5117C21.0534 25.426 21.0014 25.3274 20.9701 25.2216C20.9387 25.1158 20.9286 25.0048 20.9402 24.8951C20.9519 24.7853 20.9852 24.679 21.0381 24.5821C21.091 24.4853 21.1625 24.3998 21.2486 24.3307L26.2738 20.2854C26.4237 20.1622 26.6117 20.0948 26.8057 20.0948C26.9997 20.0948 27.1876 20.1622 27.3375 20.2854L32.3628 24.4731C32.4476 24.5434 32.5177 24.6298 32.5691 24.7272C32.6205 24.8247 32.6521 24.9313 32.6622 25.041C32.6724 25.1507 32.6607 25.2613 32.628 25.3665C32.5953 25.4717 32.5422 25.5694 32.4717 25.654C32.3937 25.7501 32.2955 25.8277 32.184 25.8813C32.0725 25.9349 31.9505 25.9631 31.8268 25.9639Z" fill="#0254D7"/>',
                            '<path fill-rule="evenodd" clip-rule="evenodd" d="M32.7587 99.5735L32.6502 99.4711C31.6538 98.5838 30.1257 98.618 29.1702 99.5735L28.482 100.261L32.0707 103.849L32.7587 103.162C33.7143 102.207 33.7484 100.678 32.8611 99.682L32.7587 99.5735ZM27.7303 101.013L31.3191 104.602L30.6856 105.235C30.0031 104.727 29.178 104.43 28.2893 104.43C25.9395 104.43 24.0347 106.508 24.0347 109.071C24.0347 109.896 24.2321 110.671 24.5782 111.343L24.2719 111.649C24.0756 111.845 23.8314 111.987 23.5636 112.06L19.936 113.049C19.539 113.158 19.1747 112.793 19.283 112.396L20.2723 108.769C20.3454 108.501 20.4871 108.257 20.6834 108.06L27.7303 101.013ZM22.4729 105.268L21.4093 106.331L19.7961 106.332C19.5024 106.332 19.2643 106.093 19.2643 105.8C19.2643 105.506 19.5024 105.268 19.7961 105.268L22.4729 105.268ZM25.3094 102.431L24.2457 103.495L19.7961 103.495C19.5024 103.495 19.2643 103.257 19.2643 102.963C19.2643 102.67 19.5024 102.431 19.7961 102.431L25.3094 102.431ZM27.0821 100.658L28.1458 99.5947L19.7961 99.595C19.5024 99.595 19.2643 99.8331 19.2643 100.127C19.2643 100.421 19.5024 100.659 19.7961 100.659L27.0821 100.658ZM32.6083 109.103C32.6083 106.949 30.8622 105.203 28.7083 105.203C26.5543 105.203 24.8082 106.949 24.8082 109.103C24.8082 111.257 26.5543 113.003 28.7083 113.003C30.8622 113.003 32.6083 111.257 32.6083 109.103ZM29.2106 109.103L30.4656 107.849C30.6041 107.711 30.6041 107.486 30.4656 107.348C30.3271 107.209 30.1027 107.209 29.9642 107.348L28.7092 108.602L27.4549 107.348C27.3165 107.209 27.092 107.209 26.9535 107.348C26.815 107.486 26.815 107.711 26.9535 107.849L28.2077 109.103L26.9535 110.357C26.815 110.495 26.815 110.72 26.9535 110.858C27.092 110.997 27.3165 110.997 27.4549 110.858L28.7091 109.605L29.9641 110.86C30.1025 110.998 30.327 110.998 30.4655 110.86C30.6039 110.721 30.6039 110.497 30.4655 110.358L29.2106 109.103Z" fill="#0254D7"/>',
                            '<path d="M27 144C22.5886 144 19 147.589 19 152C19 156.411 22.5886 160 27 160C31.4114 160 35 156.411 35 152C35 147.589 31.4114 144 27 144ZM27 156.667C26.632 156.667 26.3334 156.368 26.3334 156C26.3334 155.632 26.632 155.333 27 155.333C27.368 155.333 27.6666 155.632 27.6666 156C27.6666 156.368 27.368 156.667 27 156.667ZM28.0553 152.428C27.8193 152.537 27.6666 152.775 27.6666 153.034V153.333C27.6666 153.701 27.3687 154 27 154C26.6313 154 26.3334 153.701 26.3334 153.333V153.034C26.3334 152.256 26.7906 151.543 27.4967 151.217C28.176 150.904 28.6666 150.074 28.6666 149.667C28.6666 148.748 27.9193 148 27 148C26.0807 148 25.3334 148.748 25.3334 149.667C25.3334 150.035 25.0353 150.333 24.6666 150.333C24.298 150.333 24 150.035 24 149.667C24 148.013 25.3459 146.667 27 146.667C28.6541 146.667 30 148.013 30 149.667C30 150.567 29.2186 151.891 28.0553 152.428Z" fill="#0254D7"/>',
                            '<line x1="8.37549" y1="185.435" x2="45.2275" y2="185.435" stroke="#E6E6E6"/>',
                            '<path d="M26.8015 203.384C25.2831 203.384 23.7987 203.834 22.5361 204.678C21.2736 205.521 20.2895 206.72 19.7084 208.123C19.1273 209.526 18.9753 211.07 19.2715 212.559C19.5678 214.048 20.299 215.416 21.3727 216.49C22.4464 217.564 23.8144 218.295 25.3037 218.591C26.793 218.887 28.3367 218.735 29.7396 218.154C31.1425 217.573 32.3415 216.589 33.1851 215.327C34.0287 214.064 34.479 212.58 34.479 211.061C34.479 210.053 34.2804 209.055 33.8946 208.123C33.5088 207.192 32.9433 206.345 32.2303 205.632C31.5174 204.92 30.6711 204.354 29.7396 203.968C28.8081 203.582 27.8097 203.384 26.8015 203.384ZM28.8821 212.052C28.9541 212.123 29.0112 212.208 29.0502 212.302C29.0892 212.395 29.1092 212.495 29.1092 212.597C29.1092 212.698 29.0892 212.798 29.0502 212.892C29.0112 212.986 28.9541 213.071 28.8821 213.142C28.8108 213.214 28.7258 213.271 28.6323 213.31C28.5387 213.349 28.4384 213.369 28.337 213.369C28.2357 213.369 28.1353 213.349 28.0418 213.31C27.9482 213.271 27.8633 213.214 27.7919 213.142L26.8015 212.144L25.8111 213.142C25.7398 213.214 25.6548 213.271 25.5613 213.31C25.4677 213.349 25.3674 213.369 25.266 213.369C25.1647 213.369 25.0643 213.349 24.9708 213.31C24.8772 213.271 24.7923 213.214 24.7209 213.142C24.649 213.071 24.5918 212.986 24.5529 212.892C24.5139 212.798 24.4938 212.698 24.4938 212.597C24.4938 212.495 24.5139 212.395 24.5529 212.302C24.5918 212.208 24.649 212.123 24.7209 212.052L25.719 211.061L24.7209 210.071C24.5764 209.926 24.4951 209.73 24.4951 209.526C24.4951 209.321 24.5764 209.125 24.7209 208.981C24.8655 208.836 25.0616 208.755 25.266 208.755C25.4705 208.755 25.6666 208.836 25.8111 208.981L26.8015 209.979L27.7919 208.981C27.9365 208.836 28.1326 208.755 28.337 208.755C28.5415 208.755 28.7376 208.836 28.8821 208.981C29.0267 209.125 29.1079 209.321 29.1079 209.526C29.1079 209.73 29.0267 209.926 28.8821 210.071L27.8841 211.061L28.8821 212.052Z" fill="#0254D7"/>',
                            '<g clip-path="url(#clip0)">',
                            '<path d="M32.6555 55.3438C29.5307 52.219 24.4731 52.2185 21.3478 55.3438C18.835 57.8566 18.3602 61.5929 19.8458 64.5684L19.0222 68.1911C18.9151 68.662 19.3371 69.0842 19.8082 68.9772L23.4309 68.1535C28.6984 70.7834 34.9975 66.976 34.9975 60.9977C34.9975 58.862 34.1658 56.854 32.6555 55.3438ZM28.6696 62.9888H23.6658C23.303 62.9888 23.009 62.6947 23.009 62.332C23.009 61.9693 23.303 61.6753 23.6658 61.6753H28.6696C29.0323 61.6753 29.3264 61.9693 29.3264 62.332C29.3264 62.6947 29.0323 62.9888 28.6696 62.9888ZM30.3376 60.3201H23.6658C23.303 60.3201 23.009 60.026 23.009 59.6633C23.009 59.3006 23.303 59.0065 23.6658 59.0065H30.3376C30.7003 59.0065 30.9943 59.3006 30.9943 59.6633C30.9943 60.026 30.7003 60.3201 30.3376 60.3201Z" fill="#0254D7"/>',
                            '</g>',
                            '<rect x="63" y="87" width="88" height="38" rx="3" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                            '<path d="M79.6729 102V94.998H82.1729C82.8825 94.998 83.4521 95.1982 83.8818 95.5986C84.3115 95.9958 84.5264 96.5133 84.5264 97.1514C84.5264 97.6331 84.3945 98.0547 84.1309 98.416C83.8704 98.7773 83.5384 99.0312 83.1348 99.1777L84.7266 102H83.5059L82.0752 99.3389H80.752V102H79.6729ZM80.752 98.4014H82.124C82.5081 98.4014 82.819 98.2939 83.0566 98.0791C83.2943 97.8643 83.4131 97.555 83.4131 97.1514C83.4131 96.7965 83.2959 96.5052 83.0615 96.2773C82.8304 96.0462 82.5049 95.9307 82.085 95.9307H80.752V98.4014ZM85.5225 99.4023C85.5225 98.8587 85.6364 98.377 85.8643 97.957C86.0921 97.5339 86.403 97.2083 86.7969 96.9805C87.194 96.7526 87.64 96.6387 88.1348 96.6387C88.5319 96.6387 88.8932 96.7087 89.2188 96.8486C89.5443 96.9886 89.8128 97.1807 90.0244 97.4248C90.2393 97.6689 90.4036 97.9538 90.5176 98.2793C90.6348 98.6048 90.6934 98.9548 90.6934 99.3291V99.7197H86.5723C86.5918 100.179 86.7464 100.548 87.0361 100.828C87.3258 101.108 87.7083 101.248 88.1836 101.248C88.5156 101.248 88.8118 101.173 89.0723 101.023C89.3359 100.874 89.5199 100.672 89.624 100.418H90.6445C90.5078 100.932 90.2165 101.347 89.7705 101.663C89.3278 101.976 88.7891 102.132 88.1543 102.132C87.3763 102.132 86.7432 101.876 86.2549 101.365C85.7666 100.851 85.5225 100.197 85.5225 99.4023ZM86.5918 98.9092H89.6533C89.6208 98.4795 89.4629 98.141 89.1797 97.8936C88.8965 97.6429 88.5482 97.5176 88.1348 97.5176C87.7311 97.5176 87.3828 97.6478 87.0898 97.9082C86.7969 98.1686 86.6309 98.5023 86.5918 98.9092ZM91.2012 96.7705H92.3145L93.7207 100.73H93.7939L95.1904 96.7705H96.3232L94.3311 102H93.1934L91.2012 96.7705ZM96.792 99.3877C96.792 98.8701 96.9092 98.4014 97.1436 97.9814C97.3812 97.5615 97.7116 97.2327 98.1348 96.9951C98.5579 96.7575 99.0332 96.6387 99.5605 96.6387C100.088 96.6387 100.562 96.7591 100.981 97C101.405 97.2409 101.732 97.5713 101.963 97.9912C102.197 98.4079 102.314 98.8734 102.314 99.3877C102.314 99.902 102.196 100.369 101.958 100.789C101.724 101.206 101.395 101.535 100.972 101.775C100.549 102.013 100.075 102.132 99.5508 102.132C98.75 102.132 98.0892 101.873 97.5684 101.355C97.0508 100.835 96.792 100.179 96.792 99.3877ZM97.8613 99.3877C97.8613 99.9085 98.0192 100.338 98.335 100.677C98.654 101.012 99.0592 101.18 99.5508 101.18C100.046 101.18 100.451 101.01 100.767 100.672C101.086 100.333 101.245 99.9053 101.245 99.3877C101.245 98.8669 101.086 98.4388 100.767 98.1035C100.451 97.7682 100.046 97.6006 99.5508 97.6006C99.056 97.6006 98.6507 97.7699 98.335 98.1084C98.0192 98.4437 97.8613 98.8701 97.8613 99.3877ZM103.579 102V94.5H104.629V99.002H104.688L106.67 96.7705H107.979L106.157 98.748L108.11 102H106.919L105.439 99.5293L104.629 100.418V102H103.579ZM108.442 99.4023C108.442 98.8587 108.556 98.377 108.784 97.957C109.012 97.5339 109.323 97.2083 109.717 96.9805C110.114 96.7526 110.56 96.6387 111.055 96.6387C111.452 96.6387 111.813 96.7087 112.139 96.8486C112.464 96.9886 112.733 97.1807 112.944 97.4248C113.159 97.6689 113.324 97.9538 113.438 98.2793C113.555 98.6048 113.613 98.9548 113.613 99.3291V99.7197H109.492C109.512 100.179 109.666 100.548 109.956 100.828C110.246 101.108 110.628 101.248 111.104 101.248C111.436 101.248 111.732 101.173 111.992 101.023C112.256 100.874 112.44 100.672 112.544 100.418H113.564C113.428 100.932 113.136 101.347 112.69 101.663C112.248 101.976 111.709 102.132 111.074 102.132C110.296 102.132 109.663 101.876 109.175 101.365C108.687 100.851 108.442 100.197 108.442 99.4023ZM109.512 98.9092H112.573C112.541 98.4795 112.383 98.141 112.1 97.8936C111.816 97.6429 111.468 97.5176 111.055 97.5176C110.651 97.5176 110.303 97.6478 110.01 97.9082C109.717 98.1686 109.551 98.5023 109.512 98.9092ZM117.241 99.4023C117.241 98.8587 117.355 98.377 117.583 97.957C117.811 97.5339 118.122 97.2083 118.516 96.9805C118.913 96.7526 119.359 96.6387 119.854 96.6387C120.251 96.6387 120.612 96.7087 120.938 96.8486C121.263 96.9886 121.532 97.1807 121.743 97.4248C121.958 97.6689 122.122 97.9538 122.236 98.2793C122.354 98.6048 122.412 98.9548 122.412 99.3291V99.7197H118.291C118.311 100.179 118.465 100.548 118.755 100.828C119.045 101.108 119.427 101.248 119.902 101.248C120.234 101.248 120.531 101.173 120.791 101.023C121.055 100.874 121.239 100.672 121.343 100.418H122.363C122.227 100.932 121.935 101.347 121.489 101.663C121.047 101.976 120.508 102.132 119.873 102.132C119.095 102.132 118.462 101.876 117.974 101.365C117.485 100.851 117.241 100.197 117.241 99.4023ZM118.311 98.9092H121.372C121.34 98.4795 121.182 98.141 120.898 97.8936C120.615 97.6429 120.267 97.5176 119.854 97.5176C119.45 97.5176 119.102 97.6478 118.809 97.9082C118.516 98.1686 118.35 98.5023 118.311 98.9092ZM124.019 101.375C123.55 100.87 123.315 100.213 123.315 99.4023C123.315 98.5918 123.548 97.9294 124.014 97.415C124.479 96.8975 125.076 96.6387 125.806 96.6387C126.04 96.6387 126.26 96.6712 126.465 96.7363C126.67 96.8014 126.841 96.8861 126.978 96.9902C127.118 97.0944 127.228 97.1904 127.31 97.2783C127.391 97.363 127.459 97.4476 127.515 97.5322H127.588V94.5H128.638V102H127.607V101.258H127.544C127.131 101.84 126.567 102.132 125.854 102.132C125.103 102.132 124.491 101.88 124.019 101.375ZM124.385 99.3877C124.385 99.9281 124.533 100.363 124.829 100.691C125.129 101.017 125.521 101.18 126.006 101.18C126.494 101.18 126.885 101.009 127.178 100.667C127.471 100.325 127.617 99.8988 127.617 99.3877C127.617 98.8376 127.464 98.403 127.158 98.084C126.855 97.7617 126.468 97.6006 125.996 97.6006C125.521 97.6006 125.133 97.7682 124.834 98.1035C124.535 98.4355 124.385 98.8636 124.385 99.3877ZM129.99 95.2812C129.99 95.0892 130.055 94.9313 130.186 94.8076C130.316 94.6839 130.48 94.6221 130.679 94.6221C130.884 94.6221 131.051 94.6839 131.182 94.8076C131.315 94.9313 131.382 95.0892 131.382 95.2812C131.382 95.4798 131.315 95.641 131.182 95.7646C131.051 95.8883 130.884 95.9502 130.679 95.9502C130.477 95.9502 130.311 95.8883 130.181 95.7646C130.054 95.641 129.99 95.4798 129.99 95.2812ZM130.151 102V96.7705H131.201V102H130.151ZM132.28 97.6299V96.7803H132.969C133.06 96.7803 133.135 96.7493 133.193 96.6875C133.252 96.6257 133.281 96.5426 133.281 96.4385V95.291H134.268V96.7705H135.791V97.6299H134.268V100.311C134.268 100.844 134.521 101.111 135.029 101.111H135.737V102H134.868C134.347 102 133.942 101.858 133.652 101.575C133.363 101.289 133.218 100.877 133.218 100.34V97.6299H132.28ZM90.9277 117.375C90.459 116.87 90.2246 116.213 90.2246 115.402C90.2246 114.592 90.4574 113.929 90.9229 113.415C91.3883 112.897 91.9857 112.639 92.7148 112.639C92.9492 112.639 93.1689 112.671 93.374 112.736C93.5791 112.801 93.75 112.886 93.8867 112.99C94.0267 113.094 94.1374 113.19 94.2188 113.278C94.3001 113.363 94.3685 113.448 94.4238 113.532H94.4971V112.771H95.5469V118H94.5166V117.258H94.4531C94.0397 117.84 93.4766 118.132 92.7637 118.132C92.0117 118.132 91.3997 117.88 90.9277 117.375ZM91.2939 115.388C91.2939 115.928 91.4421 116.363 91.7383 116.691C92.0378 117.017 92.43 117.18 92.915 117.18C93.4033 117.18 93.7939 117.009 94.0869 116.667C94.3799 116.325 94.5264 115.899 94.5264 115.388C94.5264 114.838 94.3734 114.403 94.0674 114.084C93.7646 113.762 93.3773 113.601 92.9053 113.601C92.43 113.601 92.0426 113.768 91.7432 114.104C91.4437 114.436 91.2939 114.864 91.2939 115.388ZM96.6895 115.388C96.6895 114.877 96.8034 114.413 97.0312 113.996C97.2591 113.576 97.5798 113.246 97.9932 113.005C98.4098 112.761 98.8786 112.639 99.3994 112.639C100.028 112.639 100.576 112.818 101.045 113.176C101.517 113.534 101.812 114.009 101.929 114.602H100.85C100.758 114.302 100.581 114.061 100.317 113.879C100.057 113.693 99.7542 113.601 99.4092 113.601C98.9209 113.601 98.5254 113.77 98.2227 114.108C97.9199 114.447 97.7686 114.873 97.7686 115.388C97.7686 115.905 97.9232 116.333 98.2324 116.672C98.5417 117.01 98.9404 117.18 99.4287 117.18C99.764 117.18 100.063 117.089 100.327 116.906C100.591 116.724 100.768 116.485 100.859 116.188H101.929C101.815 116.778 101.523 117.25 101.055 117.604C100.586 117.956 100.037 118.132 99.4092 118.132C99.012 118.132 98.6426 118.062 98.3008 117.922C97.9622 117.779 97.6758 117.585 97.4414 117.341C97.207 117.093 97.0231 116.802 96.8896 116.467C96.7562 116.128 96.6895 115.769 96.6895 115.388ZM102.842 115.388C102.842 114.877 102.956 114.413 103.184 113.996C103.411 113.576 103.732 113.246 104.146 113.005C104.562 112.761 105.031 112.639 105.552 112.639C106.18 112.639 106.729 112.818 107.197 113.176C107.669 113.534 107.964 114.009 108.081 114.602H107.002C106.911 114.302 106.733 114.061 106.47 113.879C106.209 113.693 105.907 113.601 105.562 113.601C105.073 113.601 104.678 113.77 104.375 114.108C104.072 114.447 103.921 114.873 103.921 115.388C103.921 115.905 104.076 116.333 104.385 116.672C104.694 117.01 105.093 117.18 105.581 117.18C105.916 117.18 106.216 117.089 106.479 116.906C106.743 116.724 106.921 116.485 107.012 116.188H108.081C107.967 116.778 107.676 117.25 107.207 117.604C106.738 117.956 106.19 118.132 105.562 118.132C105.164 118.132 104.795 118.062 104.453 117.922C104.115 117.779 103.828 117.585 103.594 117.341C103.359 117.093 103.175 116.802 103.042 116.467C102.909 116.128 102.842 115.769 102.842 115.388ZM108.994 115.402C108.994 114.859 109.108 114.377 109.336 113.957C109.564 113.534 109.875 113.208 110.269 112.98C110.666 112.753 111.112 112.639 111.606 112.639C112.004 112.639 112.365 112.709 112.69 112.849C113.016 112.989 113.285 113.181 113.496 113.425C113.711 113.669 113.875 113.954 113.989 114.279C114.106 114.605 114.165 114.955 114.165 115.329V115.72H110.044C110.063 116.179 110.218 116.548 110.508 116.828C110.798 117.108 111.18 117.248 111.655 117.248C111.987 117.248 112.284 117.173 112.544 117.023C112.808 116.874 112.992 116.672 113.096 116.418H114.116C113.979 116.932 113.688 117.347 113.242 117.663C112.799 117.976 112.261 118.132 111.626 118.132C110.848 118.132 110.215 117.876 109.727 117.365C109.238 116.851 108.994 116.197 108.994 115.402ZM110.063 114.909H113.125C113.092 114.479 112.935 114.141 112.651 113.894C112.368 113.643 112.02 113.518 111.606 113.518C111.203 113.518 110.854 113.648 110.562 113.908C110.269 114.169 110.103 114.502 110.063 114.909ZM115.137 116.452H116.128C116.196 116.996 116.577 117.268 117.271 117.268C117.609 117.268 117.871 117.199 118.057 117.062C118.245 116.923 118.34 116.735 118.34 116.501C118.34 116.328 118.283 116.19 118.169 116.086C118.058 115.979 117.912 115.9 117.729 115.852C117.55 115.799 117.352 115.756 117.134 115.72C116.916 115.684 116.698 115.637 116.479 115.578C116.265 115.52 116.066 115.441 115.884 115.344C115.705 115.246 115.558 115.1 115.444 114.904C115.334 114.706 115.278 114.462 115.278 114.172C115.278 113.726 115.461 113.36 115.825 113.073C116.19 112.784 116.668 112.639 117.261 112.639C117.798 112.639 118.247 112.779 118.608 113.059C118.97 113.339 119.17 113.723 119.209 114.211H118.247C118.218 113.983 118.115 113.804 117.939 113.674C117.764 113.544 117.523 113.479 117.217 113.479C116.927 113.479 116.694 113.542 116.519 113.669C116.346 113.793 116.26 113.954 116.26 114.152C116.26 114.289 116.304 114.403 116.392 114.494C116.483 114.585 116.6 114.65 116.743 114.689C116.89 114.729 117.056 114.768 117.241 114.807C117.427 114.842 117.616 114.875 117.808 114.904C118.003 114.934 118.193 114.984 118.379 115.056C118.564 115.127 118.729 115.215 118.872 115.319C119.019 115.42 119.136 115.568 119.224 115.764C119.315 115.959 119.36 116.188 119.36 116.452C119.36 116.953 119.168 117.359 118.784 117.668C118.403 117.977 117.889 118.132 117.241 118.132C116.593 118.132 116.089 117.982 115.728 117.683C115.369 117.38 115.173 116.97 115.137 116.452ZM120.439 116.452H121.431C121.499 116.996 121.88 117.268 122.573 117.268C122.912 117.268 123.174 117.199 123.359 117.062C123.548 116.923 123.643 116.735 123.643 116.501C123.643 116.328 123.586 116.19 123.472 116.086C123.361 115.979 123.215 115.9 123.032 115.852C122.853 115.799 122.655 115.756 122.437 115.72C122.218 115.684 122 115.637 121.782 115.578C121.567 115.52 121.369 115.441 121.187 115.344C121.007 115.246 120.861 115.1 120.747 114.904C120.636 114.706 120.581 114.462 120.581 114.172C120.581 113.726 120.763 113.36 121.128 113.073C121.493 112.784 121.971 112.639 122.563 112.639C123.101 112.639 123.55 112.779 123.911 113.059C124.272 113.339 124.473 113.723 124.512 114.211H123.55C123.521 113.983 123.418 113.804 123.242 113.674C123.066 113.544 122.826 113.479 122.52 113.479C122.23 113.479 121.997 113.542 121.821 113.669C121.649 113.793 121.562 113.954 121.562 114.152C121.562 114.289 121.606 114.403 121.694 114.494C121.785 114.585 121.903 114.65 122.046 114.689C122.192 114.729 122.358 114.768 122.544 114.807C122.729 114.842 122.918 114.875 123.11 114.904C123.306 114.934 123.496 114.984 123.682 115.056C123.867 115.127 124.032 115.215 124.175 115.319C124.321 115.42 124.438 115.568 124.526 115.764C124.618 115.959 124.663 116.188 124.663 116.452C124.663 116.953 124.471 117.359 124.087 117.668C123.706 117.977 123.192 118.132 122.544 118.132C121.896 118.132 121.392 117.982 121.03 117.683C120.672 117.38 120.475 116.97 120.439 116.452Z" fill="white"/>',
                            '<path d="M58 105.718L65.0763 101.632V109.803L58 105.718Z" fill="#0254D7"/>',
                            '<defs>',
                            '<clipPath id="clip0">',
                                '<rect width="16" height="16" fill="white" transform="translate(19 53)"/>',
                            '</clipPath>',
                            '</defs>',
                        '</svg>',
                        '<svg class="edit_access_modal_images_onmobile" width="40" height="169" viewBox="0 0 40 169" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<rect x="0.5" y="0.5" width="38.0469" height="168" rx="4.5" fill="white" stroke="#DEDEDE"/>',
                            '<path d="M23.1842 18.9134C23.0416 18.9137 22.9035 18.864 22.7937 18.7731L19.5235 16.0398L16.2472 18.6754C16.1848 18.7261 16.113 18.764 16.0359 18.7868C15.9589 18.8096 15.878 18.817 15.7981 18.8085C15.7181 18.8 15.6407 18.7758 15.5701 18.7373C15.4996 18.6987 15.4373 18.6466 15.387 18.5839C15.3363 18.5215 15.2985 18.4497 15.2756 18.3726C15.2528 18.2956 15.2454 18.2147 15.2539 18.1348C15.2624 18.0548 15.2866 17.9774 15.3252 17.9068C15.3637 17.8363 15.4158 17.774 15.4785 17.7237L19.1392 14.7769C19.2483 14.6871 19.3853 14.6381 19.5266 14.6381C19.6679 14.6381 19.8048 14.6871 19.914 14.7769L23.5746 17.8274C23.6364 17.8786 23.6875 17.9415 23.7249 18.0125C23.7623 18.0835 23.7854 18.1612 23.7928 18.2411C23.8001 18.321 23.7917 18.4016 23.7679 18.4782C23.744 18.5548 23.7053 18.626 23.654 18.6876C23.5972 18.7576 23.5256 18.8142 23.4444 18.8532C23.3632 18.8922 23.2743 18.9128 23.1842 18.9134Z" fill="#0254D7"/>',
                            '<path d="M19.6679 104.897C16.4545 104.897 13.8403 107.511 13.8403 110.724C13.8403 113.938 16.4545 116.552 19.6679 116.552C22.8814 116.552 25.4955 113.938 25.4955 110.724C25.4955 107.511 22.8814 104.897 19.6679 104.897ZM19.6679 114.124C19.3998 114.124 19.1823 113.906 19.1823 113.638C19.1823 113.37 19.3998 113.152 19.6679 113.152C19.936 113.152 20.1535 113.37 20.1535 113.638C20.1535 113.906 19.936 114.124 19.6679 114.124ZM20.4366 111.036C20.2648 111.115 20.1535 111.288 20.1535 111.477V111.695C20.1535 111.963 19.9365 112.181 19.6679 112.181C19.3994 112.181 19.1823 111.963 19.1823 111.695V111.477C19.1823 110.911 19.5154 110.391 20.0297 110.154C20.5246 109.926 20.882 109.321 20.882 109.024C20.882 108.355 20.3376 107.81 19.6679 107.81C18.9982 107.81 18.4539 108.355 18.4539 109.024C18.4539 109.292 18.2367 109.51 17.9682 109.51C17.6996 109.51 17.4826 109.292 17.4826 109.024C17.4826 107.82 18.463 106.839 19.6679 106.839C20.8728 106.839 21.8533 107.82 21.8533 109.024C21.8533 109.681 21.2841 110.645 20.4366 111.036Z" fill="#0254D7"/>',
                            '<line x1="6.10107" y1="134.944" x2="32.9458" y2="134.944" stroke="#E6E6E6"/>',
                            '<path d="M19.5233 148.155C18.4172 148.155 17.3359 148.483 16.4162 149.097C15.4965 149.712 14.7797 150.585 14.3564 151.607C13.9331 152.629 13.8223 153.753 14.0381 154.838C14.2539 155.923 14.7866 156.92 15.5687 157.702C16.3509 158.484 17.3474 159.017 18.4323 159.232C19.5171 159.448 20.6416 159.337 21.6635 158.914C22.6855 158.491 23.5589 157.774 24.1735 156.854C24.788 155.935 25.116 154.853 25.116 153.747C25.116 153.013 24.9713 152.286 24.6903 151.607C24.4092 150.928 23.9973 150.312 23.4779 149.793C22.9586 149.273 22.3421 148.861 21.6635 148.58C20.985 148.299 20.2578 148.155 19.5233 148.155ZM21.0389 154.469C21.0914 154.521 21.133 154.583 21.1614 154.651C21.1897 154.719 21.2044 154.792 21.2044 154.866C21.2044 154.94 21.1897 155.013 21.1614 155.081C21.133 155.149 21.0914 155.211 21.0389 155.263C20.9869 155.315 20.9251 155.357 20.8569 155.385C20.7888 155.414 20.7157 155.428 20.6419 155.428C20.568 155.428 20.4949 155.414 20.4268 155.385C20.3586 155.357 20.2968 155.315 20.2448 155.263L19.5233 154.536L18.8019 155.263C18.7499 155.315 18.688 155.357 18.6199 155.385C18.5517 155.414 18.4786 155.428 18.4048 155.428C18.331 155.428 18.2579 155.414 18.1897 155.385C18.1216 155.357 18.0597 155.315 18.0077 155.263C17.9553 155.211 17.9137 155.149 17.8853 155.081C17.8569 155.013 17.8423 154.94 17.8423 154.866C17.8423 154.792 17.8569 154.719 17.8853 154.651C17.9137 154.583 17.9553 154.521 18.0077 154.469L18.7348 153.747L18.0077 153.026C17.9024 152.92 17.8432 152.778 17.8432 152.629C17.8432 152.48 17.9024 152.337 18.0077 152.232C18.113 152.126 18.2559 152.067 18.4048 152.067C18.5537 152.067 18.6966 152.126 18.8019 152.232L19.5233 152.959L20.2448 152.232C20.3501 152.126 20.4929 152.067 20.6419 152.067C20.7908 152.067 20.9336 152.126 21.0389 152.232C21.1442 152.337 21.2034 152.48 21.2034 152.629C21.2034 152.778 21.1442 152.92 21.0389 153.026L20.3119 153.747L21.0389 154.469Z" fill="#0254D7"/>',
                            '<g clip-path="url(#clip0)">',
                            '<path d="M23.7882 40.3151C21.5119 38.0388 17.8277 38.0385 15.5511 40.3151C13.7206 42.1455 13.3747 44.8672 14.4569 47.0347L13.857 49.6737C13.779 50.0167 14.0864 50.3243 14.4295 50.2463L17.0685 49.6463C20.9056 51.5621 25.4942 48.7885 25.4942 44.4336C25.4942 42.8779 24.8883 41.4152 23.7882 40.3151ZM20.8846 45.8841H17.2396C16.9754 45.8841 16.7612 45.6699 16.7612 45.4056C16.7612 45.1414 16.9754 44.9272 17.2396 44.9272H20.8846C21.1488 44.9272 21.363 45.1414 21.363 45.4056C21.363 45.6699 21.1488 45.8841 20.8846 45.8841ZM22.0997 43.94H17.2396C16.9754 43.94 16.7612 43.7258 16.7612 43.4616C16.7612 43.1974 16.9754 42.9832 17.2396 42.9832H22.0997C22.3639 42.9832 22.5781 43.1974 22.5781 43.4616C22.5781 43.7258 22.3639 43.94 22.0997 43.94Z" fill="#0254D7"/>',
                            '</g>',
                            '<rect x="5.82764" y="64.1035" width="28.4095" height="25.4957" rx="2" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'" fill-opacity="0.1"/>',
                            '<path fill-rule="evenodd" clip-rule="evenodd" d="M24.3993 71.9293L24.3203 71.8547C23.5944 71.2084 22.4813 71.2333 21.7852 71.9293L21.2839 72.4303L23.8981 75.044L24.3993 74.5434C25.0954 73.8473 25.1202 72.7342 24.4739 72.0083L24.3993 71.9293ZM20.7364 72.9779L23.3506 75.5921L22.8892 76.0535C22.3921 75.6832 21.791 75.4667 21.1437 75.4667C19.432 75.4667 18.0444 76.9804 18.0444 78.8477C18.0444 79.4488 18.1882 80.0133 18.4403 80.5024L18.2171 80.7256C18.0741 80.8686 17.8962 80.9718 17.7011 81.025L15.0586 81.7457C14.7694 81.8246 14.5041 81.5592 14.5829 81.27L15.3036 78.6275C15.3568 78.4324 15.46 78.2545 15.6031 78.1115L20.7364 72.9779ZM16.9066 76.0771L16.1318 76.852L14.9567 76.8522C14.7427 76.8522 14.5693 76.6787 14.5693 76.4648C14.5693 76.2508 14.7427 76.0774 14.9567 76.0774L16.9066 76.0771ZM18.9728 74.011L18.198 74.7858L14.9567 74.786C14.7427 74.786 14.5693 74.6125 14.5693 74.3986C14.5693 74.1846 14.7427 74.0112 14.9567 74.0112L18.9728 74.011ZM20.2642 72.7196L21.039 71.9448L14.9567 71.945C14.7427 71.945 14.5693 72.1184 14.5693 72.3324C14.5693 72.5464 14.7427 72.7198 14.9567 72.7198L20.2642 72.7196ZM24.2898 78.8713C24.2898 77.3023 23.0178 76.0303 21.4488 76.0303C19.8798 76.0303 18.6078 77.3023 18.6078 78.8713C18.6078 80.4404 19.8798 81.7123 21.4488 81.7123C23.0178 81.7123 24.2898 80.4404 24.2898 78.8713ZM21.8147 78.8714L22.7289 77.9577C22.8298 77.8569 22.8298 77.6933 22.7289 77.5925C22.628 77.4916 22.4645 77.4916 22.3637 77.5925L21.4495 78.5061L20.5358 77.5924C20.4349 77.4916 20.2714 77.4916 20.1705 77.5924C20.0697 77.6933 20.0697 77.8568 20.1705 77.9577L21.0841 78.8713L20.1705 79.7843C20.0697 79.8852 20.0697 80.0487 20.1705 80.1496C20.2714 80.2504 20.4349 80.2504 20.5358 80.1496L21.4494 79.2365L22.3636 80.1507C22.4644 80.2516 22.628 80.2516 22.7288 80.1507C22.8297 80.0499 22.8297 79.8863 22.7288 79.7854L21.8147 78.8714Z" fill="#0254D7"/>',
                            '<defs>',
                            '<clipPath id="clip0">',
                                '<rect width="11.6552" height="11.6552" fill="white" transform="translate(13.8403 38.6078)"/>',
                            '</clipPath>',
                            '</defs>',
                        '</svg>',
                        '<p class="revoke-access-text"> Step 2: <br> <br>Click on the Revoke edit access icon </p>',
                    '</li>',
                    '<li style="width: 29%;">',
                        '<svg class="edit_access_modal_images_ondesktop" width="54" height="232" viewBox="0 0 54 232" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<rect width="53.6029" height="232" rx="5" fill="white"/>',
                        '<rect x="0.5" y="42.5" width="53" height="189" rx="4.5" fill="white" stroke="#DEDEDE"/>',
                        '<path d="M31.8268 69.9638C31.6311 69.9642 31.4414 69.8961 31.2907 69.7712L26.8015 66.019L22.3039 69.6372C22.2182 69.7068 22.1196 69.7587 22.0138 69.7901C21.908 69.8214 21.797 69.8316 21.6873 69.8199C21.5775 69.8082 21.4712 69.775 21.3743 69.722C21.2775 69.6691 21.192 69.5976 21.1229 69.5116C21.0534 69.4259 21.0014 69.3273 20.9701 69.2215C20.9387 69.1157 20.9286 69.0047 20.9402 68.895C20.9519 68.7852 20.9852 68.6789 21.0381 68.582C21.091 68.4852 21.1625 68.3997 21.2486 68.3306L26.2738 64.2853C26.4237 64.1621 26.6117 64.0948 26.8057 64.0948C26.9997 64.0948 27.1876 64.1621 27.3375 64.2853L32.3628 68.473C32.4476 68.5433 32.5177 68.6297 32.5691 68.7271C32.6205 68.8246 32.6521 68.9312 32.6622 69.0409C32.6724 69.1506 32.6607 69.2612 32.628 69.3664C32.5953 69.4716 32.5422 69.5693 32.4717 69.654C32.3937 69.75 32.2955 69.8276 32.184 69.8812C32.0725 69.9348 31.9505 69.963 31.8268 69.9638Z" fill="#0254D7"/>',
                        '<path d="M26.0508 144C21.6394 144 18.0508 147.589 18.0508 152C18.0508 156.411 21.6394 160 26.0508 160C30.4622 160 34.0508 156.411 34.0508 152C34.0508 147.589 30.4622 144 26.0508 144ZM26.0508 156.667C25.6827 156.667 25.3842 156.368 25.3842 156C25.3842 155.632 25.6827 155.333 26.0508 155.333C26.4188 155.333 26.7174 155.632 26.7174 156C26.7174 156.368 26.4188 156.667 26.0508 156.667ZM27.1061 152.428C26.8701 152.537 26.7174 152.775 26.7174 153.034V153.333C26.7174 153.701 26.4194 154 26.0508 154C25.6821 154 25.3842 153.701 25.3842 153.333V153.034C25.3842 152.256 25.8414 151.543 26.5475 151.217C27.2268 150.904 27.7174 150.074 27.7174 149.667C27.7174 148.748 26.9701 148 26.0508 148C25.1315 148 24.3842 148.748 24.3842 149.667C24.3842 150.035 24.0861 150.333 23.7174 150.333C23.3488 150.333 23.0508 150.035 23.0508 149.667C23.0508 148.013 24.3967 146.667 26.0508 146.667C27.7048 146.667 29.0508 148.013 29.0508 149.667C29.0508 150.567 28.2694 151.891 27.1061 152.428Z" fill="#0254D7"/>',
                        '<line x1="8" y1="186.052" x2="44.852" y2="186.052" stroke="#E6E6E6"/>',
                        '<path d="M26.426 204.001C24.9076 204.001 23.4232 204.452 22.1606 205.295C20.8981 206.139 19.914 207.338 19.333 208.741C18.7519 210.144 18.5998 211.687 18.8961 213.177C19.1923 214.666 19.9235 216.034 20.9972 217.108C22.0709 218.181 23.4389 218.912 24.9282 219.209C26.4175 219.505 27.9612 219.353 29.3641 218.772C30.767 218.191 31.966 217.207 32.8096 215.944C33.6533 214.682 34.1035 213.197 34.1035 211.679C34.1035 210.671 33.9049 209.672 33.5191 208.741C33.1333 207.809 32.5678 206.963 31.8548 206.25C31.1419 205.537 30.2956 204.971 29.3641 204.586C28.4326 204.2 27.4343 204.001 26.426 204.001ZM28.5066 212.669C28.5786 212.741 28.6357 212.825 28.6747 212.919C28.7137 213.013 28.7337 213.113 28.7337 213.214C28.7337 213.316 28.7137 213.416 28.6747 213.51C28.6357 213.603 28.5786 213.688 28.5066 213.759C28.4353 213.831 28.3504 213.888 28.2568 213.927C28.1632 213.966 28.0629 213.986 27.9615 213.986C27.8602 213.986 27.7598 213.966 27.6663 213.927C27.5727 213.888 27.4878 213.831 27.4164 213.759L26.426 212.761L25.4356 213.759C25.3643 213.831 25.2794 213.888 25.1858 213.927C25.0922 213.966 24.9919 213.986 24.8905 213.986C24.7892 213.986 24.6888 213.966 24.5953 213.927C24.5017 213.888 24.4168 213.831 24.3454 213.759C24.2735 213.688 24.2164 213.603 24.1774 213.51C24.1384 213.416 24.1183 213.316 24.1183 213.214C24.1183 213.113 24.1384 213.013 24.1774 212.919C24.2164 212.825 24.2735 212.741 24.3454 212.669L25.3435 211.679L24.3454 210.688C24.2009 210.544 24.1196 210.348 24.1196 210.143C24.1196 209.939 24.2009 209.743 24.3454 209.598C24.49 209.454 24.6861 209.372 24.8905 209.372C25.095 209.372 25.2911 209.454 25.4356 209.598L26.426 210.596L27.4164 209.598C27.561 209.454 27.7571 209.372 27.9615 209.372C28.166 209.372 28.3621 209.454 28.5066 209.598C28.6512 209.743 28.7324 209.939 28.7324 210.143C28.7324 210.348 28.6512 210.544 28.5066 210.688L27.5086 211.679L28.5066 212.669Z" fill="#0254D7"/>',
                        '<g clip-path="url(#clip0)">',
                        '<path d="M31.6555 100.344C28.5307 97.219 23.4731 97.2185 20.3478 100.344C17.835 102.857 17.3602 106.593 18.8458 109.568L18.0222 113.191C17.9151 113.662 18.3371 114.084 18.8082 113.977L22.4309 113.154C27.6984 115.783 33.9975 111.976 33.9975 105.998C33.9975 103.862 33.1658 101.854 31.6555 100.344ZM27.6696 107.989H22.6658C22.303 107.989 22.009 107.695 22.009 107.332C22.009 106.969 22.303 106.675 22.6658 106.675H27.6696C28.0323 106.675 28.3264 106.969 28.3264 107.332C28.3264 107.695 28.0323 107.989 27.6696 107.989ZM29.3376 105.32H22.6658C22.303 105.32 22.009 105.026 22.009 104.663C22.009 104.301 22.303 104.007 22.6658 104.007H29.3376C29.7003 104.007 29.9943 104.301 29.9943 104.663C29.9943 105.026 29.7003 105.32 29.3376 105.32Z" fill="#0254D7"/>',
                        '</g>',
                        '<defs>',
                        '<clipPath id="clip0">',
                        '<rect width="16" height="16" fill="white" transform="translate(18 98)"/>',
                        '</clipPath>',
                        '</defs>',
                        '</svg>',
                        '<svg class="edit_access_modal_images_onmobile" width="40" height="169" viewBox="0 0 40 169" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<rect width="39.0469" height="169" rx="5" fill="white"/>',
                            '<rect x="0.5" y="32.5" width="37.9368" height="136" rx="4.5" fill="white" stroke="#DEDEDE"/>',
                            '<path d="M22.9488 52.1634C22.8077 52.1637 22.671 52.1145 22.5623 52.0245L19.3254 49.3189L16.0823 51.9279C16.0206 51.978 15.9495 52.0155 15.8732 52.0381C15.7969 52.0607 15.7169 52.068 15.6377 52.0596C15.5586 52.0512 15.4819 52.0272 15.4121 51.989C15.3423 51.9509 15.2807 51.8993 15.2308 51.8373C15.1806 51.7755 15.1432 51.7044 15.1206 51.6281C15.098 51.5518 15.0907 51.4718 15.0991 51.3927C15.1075 51.3135 15.1315 51.2369 15.1696 51.167C15.2078 51.0972 15.2594 51.0356 15.3214 50.9857L18.9449 48.0688C19.0529 47.98 19.1885 47.9315 19.3284 47.9315C19.4683 47.9315 19.6038 47.98 19.7119 48.0688L23.3353 51.0884C23.3965 51.1391 23.447 51.2014 23.4841 51.2716C23.5211 51.3419 23.544 51.4188 23.5513 51.4979C23.5586 51.577 23.5502 51.6567 23.5266 51.7326C23.503 51.8084 23.4647 51.8789 23.4139 51.9399C23.3577 52.0092 23.2868 52.0652 23.2064 52.1038C23.126 52.1424 23.038 52.1628 22.9488 52.1634Z" fill="#0254D7"/>',
                            '<path d="M18.784 105.547C15.6032 105.547 13.0156 108.135 13.0156 111.316C13.0156 114.497 15.6032 117.084 18.784 117.084C21.9649 117.084 24.5525 114.497 24.5525 111.316C24.5525 108.135 21.9649 105.547 18.784 105.547ZM18.784 114.681C18.5187 114.681 18.3034 114.465 18.3034 114.2C18.3034 113.935 18.5187 113.719 18.784 113.719C19.0494 113.719 19.2647 113.935 19.2647 114.2C19.2647 114.465 19.0494 114.681 18.784 114.681V114.681ZM19.545 111.624C19.3748 111.703 19.2647 111.874 19.2647 112.061V112.277C19.2647 112.543 19.0499 112.758 18.784 112.758C18.5182 112.758 18.3034 112.543 18.3034 112.277V112.061C18.3034 111.5 18.6331 110.986 19.1422 110.751C19.632 110.526 19.9858 109.927 19.9858 109.633C19.9858 108.971 19.4469 108.432 18.784 108.432C18.1212 108.432 17.5823 108.971 17.5823 109.633C17.5823 109.899 17.3674 110.114 17.1016 110.114C16.8357 110.114 16.6209 109.899 16.6209 109.633C16.6209 108.441 17.5914 107.47 18.784 107.47C19.9767 107.47 20.9472 108.441 20.9472 109.633C20.9472 110.283 20.3838 111.237 19.545 111.624Z" fill="#0254D7"/>',
                            '<line x1="5.76855" y1="135.73" x2="32.3408" y2="135.73" stroke="#E6E6E6"/>',
                            '<path d="M19.0544 148.811C17.9595 148.811 16.8892 149.136 15.9789 149.744C15.0685 150.353 14.3589 151.217 13.94 152.229C13.521 153.24 13.4113 154.353 13.6249 155.427C13.8385 156.501 14.3658 157.488 15.14 158.262C15.9142 159.036 16.9006 159.563 17.9744 159.777C19.0483 159.99 20.1614 159.881 21.1729 159.462C22.1845 159.043 23.0491 158.333 23.6574 157.423C24.2656 156.513 24.5903 155.442 24.5903 154.347C24.5903 153.62 24.4471 152.9 24.1689 152.229C23.8907 151.557 23.4829 150.947 22.9689 150.433C22.4548 149.919 21.8446 149.511 21.1729 149.233C20.5013 148.955 19.7814 148.811 19.0544 148.811V148.811ZM20.5547 155.061C20.6065 155.113 20.6477 155.174 20.6758 155.242C20.7039 155.309 20.7184 155.381 20.7184 155.454C20.7184 155.528 20.7039 155.6 20.6758 155.667C20.6477 155.735 20.6065 155.796 20.5547 155.848C20.5032 155.899 20.442 155.941 20.3745 155.969C20.3071 155.997 20.2347 156.011 20.1616 156.011C20.0885 156.011 20.0162 155.997 19.9487 155.969C19.8813 155.941 19.82 155.899 19.7686 155.848L19.0544 155.128L18.3403 155.848C18.2888 155.899 18.2276 155.941 18.1602 155.969C18.0927 155.997 18.0203 156.011 17.9473 156.011C17.8742 156.011 17.8018 155.997 17.7344 155.969C17.6669 155.941 17.6057 155.899 17.5542 155.848C17.5023 155.796 17.4611 155.735 17.433 155.667C17.4049 155.6 17.3905 155.528 17.3905 155.454C17.3905 155.381 17.4049 155.309 17.433 155.242C17.4611 155.174 17.5023 155.113 17.5542 155.061L18.2739 154.347L17.5542 153.633C17.45 153.529 17.3914 153.388 17.3914 153.24C17.3914 153.093 17.45 152.951 17.5542 152.847C17.6585 152.743 17.7998 152.684 17.9473 152.684C18.0947 152.684 18.2361 152.743 18.3403 152.847L19.0544 153.567L19.7686 152.847C19.8728 152.743 20.0142 152.684 20.1616 152.684C20.309 152.684 20.4504 152.743 20.5547 152.847C20.6589 152.951 20.7175 153.093 20.7175 153.24C20.7175 153.388 20.6589 153.529 20.5547 153.633L19.835 154.347L20.5547 155.061Z" fill="#0254D7"/>',
                            '<path d="M22.8259 74.0689C20.5727 71.8157 16.9259 71.8154 14.6724 74.0689C12.8606 75.8807 12.5182 78.5748 13.5894 80.7203L12.9955 83.3325C12.9183 83.672 13.2226 83.9765 13.5623 83.8993L16.1745 83.3054C19.9726 85.2017 24.5146 82.4563 24.5146 78.1456C24.5146 76.6057 23.9148 75.1579 22.8259 74.0689V74.0689ZM19.9518 79.5813H16.3438C16.0822 79.5813 15.8702 79.3693 15.8702 79.1078C15.8702 78.8462 16.0822 78.6342 16.3438 78.6342H19.9518C20.2134 78.6342 20.4254 78.8462 20.4254 79.1078C20.4254 79.3693 20.2134 79.5813 19.9518 79.5813ZM21.1545 77.657H16.3438C16.0822 77.657 15.8702 77.445 15.8702 77.1835C15.8702 76.922 16.0822 76.7099 16.3438 76.7099H21.1545C21.4161 76.7099 21.6281 76.922 21.6281 77.1835C21.6281 77.445 21.416 77.657 21.1545 77.657Z" fill="#0254D7"/>',
                        '</svg>',
                        '<p> Step 3: <br> <br> Edit Access has been revoked </p>',
                    '</li>',
                '</ul>',
            '</div>',
        '</div>',
        '<div class="easyassist-customer-connect-modal-footer" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
            '<div easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
            '<button class="easyassist-modal-primary-btn end-session-btn" id="easyassist-co-browsing-connect-button" onclick="easyassist_hide_edit_access_info_modal()" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; width: 95px !important;">OK</button>',
            '</div>',
        '</div>',
        '</div>'
        ].join('');
            div_model.innerHTML = modal_html;
            document.getElementsByTagName("body")[0].appendChild(div_model);
            var svg_paths = div_model.getElementsByTagName("path");
            
            for(let idx = 0; idx < svg_paths.length; idx ++) {
                if(svg_paths[idx].getAttribute('fill') == "#0254D7") {
                    svg_paths[idx].setAttribute("fill", EASYASSIST_COBROWSE_META.floating_button_bg_color);
                }
            }
    }

    function easyassist_show_edit_access_info_modal(){
        document.getElementById("easyassist-co-browsing-edit-access-info-modal").style.display = "flex";
    }

    function easyassist_hide_edit_access_info_modal() {
        document.getElementById("easyassist-co-browsing-edit-access-info-modal").style.display = "none";
    }

    function easyassist_show_floating_sidenav_button(play_greeting_bubble_sound) {

        if (get_easyassist_cookie("easyassist_session_id") != undefined) {
            if(EASYASSIST_COBROWSE_META.show_floating_button_after_lead_search == true){
                var easyassist_session_created_on = get_easyassist_cookie("easyassist_session_created_on");
                if(easyassist_session_created_on != undefined && easyassist_session_created_on != null){
                    if( easyassist_session_created_on == "request"){
                        return;
                    }
                }else{
                    return;
                }
            }else{
                return;
            }
        }

        if (EASYASSIST_COBROWSE_META.enable_proxy_cobrowsing) {
            let first_index = window.location.href.indexOf("cognoai-cobrowse");
            if (first_index > 0) {
                easyassist_initialize_proxy_cobrowsing();
                return;
            }
        }

        if (EASYASSIST_COBROWSE_META.allow_connect_with_drop_link == true) {
            var first_index = window.location.href.indexOf("eadKey");
            if (first_index > 0) {
                easyassist_initialize_cobrowsing_using_drop_link();
                return;
            }
        }

        if (EASYASSIST_COBROWSE_META.show_floating_easyassist_button == false && EASYASSIST_COBROWSE_META.show_easyassist_connect_agent_icon == false) {
            return;
        }
        if (EASYASSIST_COBROWSE_META.enable_waitlist == true && EASYASSIST_COBROWSE_META.show_floating_button_on_enable_waitlist == false) {
            return;
        }
        if (easyassist_time_to_show_support_button() == false) {
            EASYASSIST_COBROWSE_META.agents_available = false;
            if(EASYASSIST_COBROWSE_META.show_only_if_agent_available == true) {
                easyassist_hide_floating_sidenav_button();
                // easyassist_hide_greeting_bubble();
            } else {
                if(EASYASSIST_COBROWSE_META.enable_non_working_hours_modal_popup == true) {
                    if(document.getElementById("easyassist-non-working-hours-modal-id").style.display != "flex") {
                        document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("title", "");
                        document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_non_working_hour_modal(); easyassist_source_of_lead()");
                        easyassist_display_greeting_bubble();
                    }
                } else {
                    document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
                    document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("title", EASYASSIST_COBROWSE_META.message_on_non_working_hours);
                    document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_toast('" + EASYASSIST_COBROWSE_META.message_on_non_working_hours + "')");
                    easyassist_display_greeting_bubble();
                }
            }
            return;
        } else {
            EASYASSIST_COBROWSE_META.agents_available = undefined;
            document.getElementById("easyassist-side-nav-options-co-browsing").removeAttribute("title");
            document.getElementById("easyassist-side-nav-options-co-browsing").setAttribute("onclick", "easyassist_show_cobrowsing_modal(); easyassist_source_of_lead()");
        }
        if (document.getElementById("easyassist-co-browsing-modal-id").style.display == "flex") {
            return;
        }
        if (document.getElementById("easyassist-product-category-modal-id").style.display == "flex") {
            return;
        }
        if (document.getElementById("easyassist-conection-modal-id").style.display == "flex"){
            return;
        }
        if(document.getElementById("easyassist-non-working-hours-modal-id").style.display == "flex") {
            return;
        }
        if (EASYASSIST_COBROWSE_META.show_only_if_agent_available == true) {
            easyassist_check_agent_available_status();
        } else if (EASYASSIST_COBROWSE_META.disable_connect_button_if_agent_unavailable == true) {
            easyassist_check_agent_available_status();
        } else {
            document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
            if (play_greeting_bubble_sound != false) {
                easyassist_display_greeting_bubble();
            }
        }
    }

    function easyassist_hide_floating_sidenav_button() {
        document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "none";
        let talk_text_div = document.getElementById("talk_text_div");
        if(talk_text_div){
            talk_text_div.style.display = "none";
        }
    }

    function easyassist_display_greeting_bubble() {
        if (!is_greeting_bubble_closed) {
            let talk_text_div = document.getElementById("talk_text_div");
            if (talk_text_div) {
                if (talk_text_div.style.display == "none") {
                    easyassist_play_greeting_bubble_popup();
                }
                talk_text_div.style.display = "inline-block";
            }
        }
    }

    function easyassist_add_payment_consent_modal() {

        let consent_element = document.querySelector("#easyassist-co-browsing-payment-consent-modal");
        if (consent_element != undefined && consent_element != null) {
            consent_element.remove();
        }
        const request_modal_html = '<div id="easyassist-co-browsing-payment-consent-modal" style="display: none;">\
          <div id="easyassist-co-browsing-modal-content" style="padding: 2em; text-align: center;">\
          <h4>Co-browsing Alert*</h4><hr>\
          <p style="text-align: justify;">Upon clicking on Pay button, you will be directed to payment gateway page to complete your transaction. For your security reasons, please note your co-browsing session will be paused during this session and our sales agent will not be able to view your details.</p><br>\
          <div style="display: flex;justify-content: center;">\
              <button onclick="easyassist_hide_payment_consent_modal(this)" style="background-color: #1b5e20; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em !important; border-style: none; float: right; margin-right: 5%;outline:none;">Ok</button>\
          </div>\
          </div>\
        </div>';
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', request_modal_html);
    }

    function easyassist_hide_payment_consent_modal(element) {
        document.getElementById("easyassist-co-browsing-payment-consent-modal").style.display = "none";
    }

    function easyassist_show_payment_consent_modal(element) {
        document.getElementById("easyassist-co-browsing-payment-consent-modal").style.display = "block";
    }

    function easyassist_add_agent_disconnected_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-agent-disconnected-modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-body">',
                    "Looks like we are not receiving any updates from the agent side. Kindly check your internet connectivity or check whether the agent is still connected or not.",
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class="easyassist-modal-primary-btn" onclick="easyassist_hide_agent_disconnected_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">OK</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_show_agent_disconnected_modal(element) {
        if(get_easyassist_cookie("easyassist_session_id") != undefined && get_easyassist_cookie("easyassist_session_id") != null) {
            document.getElementById("easyassist-agent-disconnected-modal").style.display = "flex";
        }
    }

    function easyassist_hide_agent_disconnected_modal(element) {
        document.getElementById("easyassist-agent-disconnected-modal").style.display = "none";
    }

    function easyassist_add_function_fail_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist_function_fail_modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-body">',
                    '<div id="easyassist_function_fail_code"> Ooops! </div>',
                    '<div id="easyassist_function_fail_message"> OK </div>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class="easyassist-modal-primary-btn" onclick="easyassist_hide_function_fail_modal(this)" style="background-color: transparent; color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;margin-right: 10px;">Cancel</button>',
                    '<button class="easyassist-modal-primary-btn" onclick="window.location.reload()" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">Refresh</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_add_drawing_canvas() {
        if(EASYASSIST_COBROWSE_META.enable_cobrowsing_annotation == false) {
            return;
        }

        var easyassist_canvas = document.createElement("canvas");
        easyassist_canvas.id = "easyassist-drawing-canvas";
        easyassist_canvas.style.pointerEvents = "none";
        easyassist_canvas.style.position = "fixed";
        easyassist_canvas.width = window.innerWidth;
        easyassist_canvas.height = window.innerHeight;
        easyassist_canvas.style.top = "0";
        easyassist_canvas.style.left = "0";
        easyassist_canvas.style.zIndex = "2147483647";

        document.getElementsByTagName("body")[0].appendChild(easyassist_canvas);

        easyassist_drawing_canvas = new EasyAssistCanvas(easyassist_canvas, EASYASSIST_COBROWSE_META.floating_button_bg_color, 7);
    }

    function easyassist_show_function_fail_modal(code=EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE, message=EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE) {
        var current_time = Date.now();
        var difference = (current_time - easyassist_function_fail_time) / 1000;

        if(difference < 30) {
            return;
        } else if(difference >= 300) {
            easyassist_function_fail_count = 0;
        }

        if(message == null) {
            message = EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE;
        }

        if(easyassist_function_fail_count <= 6) {
            if(code != null) {
                message = message + " [" + code + "]"
            }
            document.getElementById("easyassist_function_fail_message").innerHTML = message;
            easyassist_display_function_fail_modal();
        }

        easyassist_function_fail_count++;
        easyassist_function_fail_time = Date.now();
    }

    function easyassist_display_function_fail_modal(){
        document.getElementById("easyassist_function_fail_modal").style.display = "flex";
    }
    function easyassist_hide_function_fail_modal() {
        document.getElementById("easyassist_function_fail_modal").style.display = "none";
    }

    function easyassist_add_agent_weak_internet_connection() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-agent-weak-internet-connection-modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header" style="justify-content: center;align-items: center;">',
                    '<svg width="106" height="100" viewBox="0 0 106 100" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M96.8752 30.7418C105.787 47.6841 104.912 68.6831 95.6816 81.9665C86.3722 95.2499 68.5489 100.738 53.3514 99.3065C38.1539 97.7952 25.5026 89.2843 14.9201 75.285C4.33751 61.2857 -4.17627 41.798 2.18918 26.2875C8.47505 10.7769 29.6402 -0.756642 49.5322 0.0387729C69.4242 0.754646 87.9635 13.7199 96.8752 30.7418Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" fill-opacity="0.1"/>',
                        '<path d="M10.7551 35.3876C10.7551 32.8966 8.73192 30.8747 6.23445 30.8747C3.73698 30.8747 1.71606 32.8966 1.71606 35.3876C1.71606 37.8785 3.73919 39.9004 6.23666 39.9004C8.73413 39.9004 10.7551 37.8785 10.7551 35.3876ZM4.04807 35.414C4.07013 34.2775 5.09162 33.3106 6.25872 33.3238C7.41921 33.3371 8.42967 34.3502 8.40761 35.4756C8.38554 36.6099 7.35964 37.579 6.19474 37.5658C5.03646 37.5548 4.026 36.5416 4.04807 35.414Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M91.5333 22.3094C89.038 22.3094 87.0127 24.3291 87.0127 26.8223C87.0127 29.3155 89.0358 31.3351 91.5333 31.3351C94.0308 31.3351 96.0539 29.3155 96.0539 26.8223C96.0539 24.3291 94.0286 22.3094 91.5333 22.3094ZM91.6392 28.9433C90.4169 28.9785 89.3447 27.9962 89.3557 26.8487C89.3668 25.6858 90.3287 24.7167 91.487 24.6991C92.6408 24.6815 93.6689 25.6351 93.7087 26.7584C93.7484 27.9279 92.8173 28.9102 91.6392 28.9433Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M13.1146 75.6662C10.4429 75.6574 7.77111 75.6574 5.09935 75.6662C3.96092 75.6706 3.39171 76.1419 3.36744 77.0537C3.34318 77.9656 3.91239 78.4589 5.0464 78.4699C6.38118 78.4831 7.71816 78.4721 9.05294 78.4721C10.3877 78.4721 11.7247 78.4787 13.0595 78.4699C14.2839 78.4611 14.8465 78.0008 14.8311 77.0405C14.8201 76.1177 14.2751 75.6706 13.1146 75.6662Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M105.252 54.8154H103.829V53.3838C103.829 52.9719 103.491 52.6371 103.081 52.6371C102.671 52.6371 102.333 52.9741 102.333 53.3838V54.8154H100.886C100.473 54.8154 100.138 55.1524 100.138 55.562C100.138 55.9739 100.475 56.3087 100.886 56.3087H102.333V57.7403C102.333 58.1521 102.671 58.4869 103.081 58.4869C103.491 58.4869 103.829 58.1499 103.829 57.7403V56.3087H105.252C105.665 56.3087 106 55.9717 106 55.562C106 55.1502 105.665 54.8154 105.252 54.8154Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M18.1115 19.9945C18.1115 20.5979 18.6057 21.0891 19.208 21.0891C19.8125 21.0891 20.3045 20.5957 20.3045 19.9945V17.8933H22.3916C22.9961 17.8933 23.4881 17.4 23.4881 16.7987C23.4881 16.1952 22.9939 15.7041 22.3916 15.7041H20.3045V13.6007C20.3045 12.9972 19.8103 12.5061 19.208 12.5061C18.6035 12.5061 18.1115 12.9994 18.1115 13.6007V15.7019H15.9891C15.3846 15.7019 14.8926 16.1952 14.8926 16.7965C14.8926 17.4 15.3868 17.8911 15.9891 17.8911H18.1115V19.9945Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M14.1647 60.522H12.7372V59.0838C12.7372 58.6719 12.3997 58.335 11.9871 58.335C11.5746 58.335 11.237 58.6719 11.237 59.0838V60.522H9.78308C9.37051 60.522 9.03296 60.859 9.03296 61.2709C9.03296 61.6827 9.37051 62.0197 9.78308 62.0197H11.237V63.4579C11.237 63.8698 11.5746 64.2067 11.9871 64.2067C12.3997 64.2067 12.7372 63.8698 12.7372 63.4579V62.0197H14.1647C14.5773 62.0197 14.9148 61.6827 14.9148 61.2709C14.917 60.859 14.5795 60.522 14.1647 60.522Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<g clip-path="url(#clip0)">',
                        '<path d="M25.0308 7.1517L65.259 8.04566L78.9664 25.6269L80.4564 78.6686H25.0308V7.1517Z" fill="white"/>',
                        '<path d="M75.0925 77.4767V28.5898L80.4563 25.6269V77.4767H75.0925Z" fill="#E6EEFB"/>',
                        '<path d="M58.1074 60.1934C64.6631 60.7894 64.0672 53.9357 63.1732 51.2538L66.4511 51.5518L67.047 52.4458C66.9477 54.1344 66.7491 57.5711 66.7491 57.8095C66.7491 58.0479 65.7558 59.8954 65.2591 60.7894C64.0672 61.286 59.5378 61.3854 58.1074 60.1934Z" fill="#E6EEFB"/>',
                        '<path d="M25.0308 7.172C25.5185 7.172 25.9092 7.172 26.2998 7.172C39.1869 7.172 52.074 7.18552 64.9588 7.15173C66.3475 7.14723 67.3908 7.68779 68.1788 8.6991C72.108 13.7241 76.0032 18.7717 79.8984 23.8237C80.734 24.9071 81.0546 26.1707 81.0523 27.5288C81.0365 38.9213 81.0207 50.316 81.0094 61.7084C81.0049 66.9046 81.0072 72.103 81.0072 77.2992C81.0072 77.7249 81.0072 78.1506 81.0072 78.6687C62.3552 78.6687 43.7438 78.6687 25.0308 78.6687C25.0308 54.904 25.0308 31.1101 25.0308 7.172ZM27.7111 9.86357C27.7111 32.0381 27.7111 54.0864 27.7111 76.1573C44.6493 76.1573 61.5061 76.1573 78.3494 76.1573C78.3494 60.3637 78.3494 44.6468 78.3494 28.7969C73.8377 28.7969 69.4366 28.7969 64.9475 28.7969C64.9475 28.2789 64.9475 27.8937 64.9475 27.5086C64.9475 22.952 64.9497 18.3933 64.9475 13.8367C64.9475 10.9289 63.8726 9.86357 60.9303 9.86357C50.2584 9.86132 39.5843 9.86357 28.9125 9.86357C28.5308 9.86357 28.1492 9.86357 27.7111 9.86357Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M54.1107 50.7779C50.9651 51.0076 47.9799 51.1315 45.0172 51.4671C41.4652 51.868 38.0035 52.7262 34.6818 54.0776C33.5776 54.5258 32.8528 54.3411 32.5005 53.546C32.1505 52.7577 32.5457 52.0595 33.6296 51.6113C37.3125 50.0887 41.1649 49.2148 45.1076 48.7373C53.0877 47.771 60.9866 48.1224 68.75 50.3432C70.0146 50.7058 71.2543 51.1698 72.4804 51.6473C73.5282 52.0527 73.8714 52.7307 73.5418 53.519C73.2098 54.3141 72.4917 54.5236 71.4756 54.1407C70.4143 53.742 69.3484 53.3591 68.0907 52.8996C68.0907 54.2668 68.1245 55.4628 68.0839 56.6543C67.9665 60.2693 65.3674 63.0668 61.7905 63.4654C58.4237 63.8416 55.2488 61.6793 54.3726 58.3346C54.1604 57.5215 54.14 56.6475 54.1197 55.7984C54.0836 54.2353 54.1107 52.6721 54.1107 50.7779ZM56.8723 51.0482C56.8723 53.1992 56.7052 55.2668 56.9175 57.294C57.1478 59.4945 59.2298 60.9653 61.4292 60.8122C63.597 60.6613 65.3064 58.8616 65.3764 56.643C65.3945 56.0754 65.3809 55.5056 65.3809 54.938C65.3809 52.037 65.3809 52.037 62.4747 51.6766C62.407 51.6676 62.337 51.6991 62.1563 51.7329C62.1563 53.305 62.2038 54.8997 62.1247 56.4899C62.1021 56.9404 61.8244 57.5507 61.4654 57.776C60.7857 58.2039 60.0608 57.6048 60.045 56.6475C60.0179 54.911 60.0382 53.1721 60.0382 51.3185C58.9521 51.2239 57.9427 51.1383 56.8723 51.0482Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M40.3565 41.4892C39.5436 40.6468 38.9791 40.0634 38.3287 39.3922C39.4668 38.3584 40.6117 37.3155 41.8672 36.1736C40.5033 34.9325 39.3562 33.8897 38.2249 32.8604C39.0333 32.1013 39.6452 31.527 40.3565 30.8603C41.2823 31.8851 42.3233 33.0383 43.4885 34.3244C44.7305 32.9797 45.7805 31.8423 46.8644 30.6688C47.5735 31.4346 48.1402 32.0495 48.7906 32.7523C47.7609 33.7478 46.6476 34.8244 45.4915 35.9438C46.7109 37.0858 47.8196 38.1286 49.0345 39.2661C48.199 39.9215 47.5396 40.4396 46.8531 40.9756C46.0086 40.0589 44.9586 38.9215 43.834 37.7029C42.5446 39.1084 41.4969 40.2481 40.3565 41.4892Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '<path d="M57.2625 39.189C58.2696 38.2408 59.3784 37.1934 60.6203 36.0245C59.3806 34.905 58.229 33.8644 57.1338 32.8757C57.8835 32.0806 58.4616 31.4679 59.1887 30.6954C60.2071 31.8486 61.239 33.0176 62.4517 34.3915C63.6665 33.0198 64.7007 31.8531 65.7801 30.6368C66.4824 31.3846 67.0401 31.9792 67.6702 32.6504C66.5682 33.655 65.4211 34.7001 64.1994 35.815C65.5656 37.0718 66.7082 38.1237 67.8779 39.198C67.0695 39.9976 66.4711 40.59 65.7417 41.3107C64.7052 40.1598 63.662 39.0043 62.5262 37.7408C61.3136 39.0516 60.2748 40.1756 59.1977 41.34C58.5248 40.5922 57.967 39.9706 57.2625 39.189Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '</g>',
                        '<defs>',
                        '<clipPath id="clip0">',
                        '<rect width="56.0216" height="71.5169" fill="white" transform="translate(25.0308 7.1517)"/>',
                        '</clipPath>',
                        '</defs>',
                    '</svg>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body" style="text-align:center;padding-top: 2em!important;">',
                    "Looks like the agent is facing internet connectivity issues",
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class="easyassist-modal-primary-btn" onclick="easyassist_hide_agent_weak_internet_connection(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">OK</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_show_agent_weak_internet_connection(element) {
        if(get_easyassist_cookie("easyassist_session_id") != undefined && get_easyassist_cookie("easyassist_session_id") != null) {
            easyassist_hide_client_weak_internet_connection();
            document.getElementById("easyassist-agent-weak-internet-connection-modal").style.display = "flex";
        }
    }

    function easyassist_hide_agent_weak_internet_connection(element) {
        document.getElementById("easyassist-agent-weak-internet-connection-modal").style.display = "none";
    }

    function easyassist_add_client_weak_internet_connection() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-client-weak-internet-connection-modal"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header" style="justify-content:center;align-items:center;">',
                   '<svg width="106" height="100" viewBox="0 0 106 100" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M96.8752 30.7418C105.787 47.6841 104.912 68.6831 95.6816 81.9665C86.3722 95.2499 68.5489 100.738 53.3514 99.3065C38.1539 97.7952 25.5026 89.2843 14.9201 75.285C4.33751 61.2857 -4.17627 41.798 2.18918 26.2875C8.47505 10.7769 29.6402 -0.756642 49.5322 0.0387729C69.4242 0.754646 87.9635 13.7199 96.8752 30.7418Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'" fill-opacity="0.1"/>',
                        '<path d="M10.7548 35.3876C10.7548 32.8966 8.73168 30.8747 6.23421 30.8747C3.73674 30.8747 1.71582 32.8966 1.71582 35.3876C1.71582 37.8785 3.73895 39.9004 6.23642 39.9004C8.73389 39.9004 10.7548 37.8785 10.7548 35.3876ZM4.04782 35.414C4.06988 34.2775 5.09138 33.3106 6.25848 33.3238C7.41896 33.3371 8.42942 34.3502 8.40736 35.4756C8.3853 36.6099 7.3594 37.579 6.1945 37.5658C5.03622 37.5548 4.02576 36.5416 4.04782 35.414Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M91.5332 22.3094C89.0379 22.3094 87.0126 24.3291 87.0126 26.8223C87.0126 29.3155 89.0357 31.3351 91.5332 31.3351C94.0306 31.3351 96.0538 29.3155 96.0538 26.8223C96.0538 24.3291 94.0284 22.3094 91.5332 22.3094ZM91.6391 28.9433C90.4168 28.9785 89.3446 27.9962 89.3556 26.8487C89.3666 25.6858 90.3286 24.7167 91.4868 24.6991C92.6407 24.6815 93.6688 25.6351 93.7085 26.7584C93.7482 27.9279 92.8172 28.9102 91.6391 28.9433Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M13.1144 75.6662C10.4426 75.6574 7.77087 75.6574 5.0991 75.6662C3.96068 75.6706 3.39147 76.1419 3.3672 77.0537C3.34293 77.9656 3.91214 78.4589 5.04615 78.4699C6.38093 78.4831 7.71792 78.4721 9.05269 78.4721C10.3875 78.4721 11.7245 78.4787 13.0592 78.4699C14.2837 78.4611 14.8463 78.0008 14.8309 77.0405C14.8198 76.1177 14.2749 75.6706 13.1144 75.6662Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M105.252 54.8154H103.829V53.3838C103.829 52.9719 103.491 52.6371 103.081 52.6371C102.671 52.6371 102.333 52.9741 102.333 53.3838V54.8154H100.886C100.473 54.8154 100.138 55.1524 100.138 55.562C100.138 55.9739 100.475 56.3087 100.886 56.3087H102.333V57.7403C102.333 58.1521 102.671 58.4869 103.081 58.4869C103.491 58.4869 103.829 58.1499 103.829 57.7403V56.3087H105.252C105.664 56.3087 106 55.9717 106 55.562C106 55.1502 105.664 54.8154 105.252 54.8154Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M18.1114 19.9945C18.1114 20.5979 18.6056 21.0891 19.2079 21.0891C19.8124 21.0891 20.3044 20.5957 20.3044 19.9945V17.8933H22.3915C22.996 17.8933 23.488 17.4 23.488 16.7987C23.488 16.1952 22.9938 15.7041 22.3915 15.7041H20.3044V13.6007C20.3044 12.9972 19.8102 12.5061 19.2079 12.5061C18.6034 12.5061 18.1114 12.9994 18.1114 13.6007V15.7019H15.989C15.3844 15.7019 14.8925 16.1952 14.8925 16.7965C14.8925 17.4 15.3867 17.8911 15.989 17.8911H18.1114V19.9945Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M14.1646 60.522H12.7371V59.0838C12.7371 58.6719 12.3996 58.335 11.987 58.335C11.5744 58.335 11.2369 58.6719 11.2369 59.0838V60.522H9.78296C9.37039 60.522 9.03284 60.859 9.03284 61.2709C9.03284 61.6827 9.37039 62.0197 9.78296 62.0197H11.2369V63.4579C11.2369 63.8698 11.5744 64.2067 11.987 64.2067C12.3996 64.2067 12.7371 63.8698 12.7371 63.4579V62.0197H14.1646C14.5771 62.0197 14.9147 61.6827 14.9147 61.2709C14.9169 60.859 14.5793 60.522 14.1646 60.522Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M53 78C37.5603 78 25 65.4397 25 50C25 34.5603 37.5603 22 53 22C68.4397 22 81 34.5603 81 50C81 65.4397 68.4397 78 53 78ZM53 26.6667C40.134 26.6667 29.6667 37.134 29.6667 50C29.6667 62.866 40.134 73.3333 53 73.3333C65.866 73.3333 76.3333 62.866 76.3333 50C76.3333 37.134 65.866 26.6667 53 26.6667Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M34.856 70.4773C34.2587 70.4773 33.6613 70.2487 33.2063 69.7937C32.294 68.8813 32.294 67.4067 33.2063 66.4943L69.4943 30.2063C70.4067 29.294 71.8813 29.294 72.7937 30.2063C73.706 31.1187 73.706 32.5957 72.7937 33.5057L36.5057 69.7937C36.0483 70.251 35.451 70.4773 34.856 70.4773Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M55.7393 53.8617L48.156 61.445C49.115 63.146 50.9163 64.3127 53 64.3127C56.0777 64.3127 58.586 61.7997 58.586 58.7127C58.586 56.6267 57.4287 54.8253 55.7393 53.8617Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M43.1627 53.171C43.4077 52.926 43.6667 52.6997 43.9257 52.4757L51.95 44.4513C47.386 44.708 43.1207 46.598 39.8564 49.8787C38.9464 50.7933 38.951 52.2703 39.8657 53.1803C40.7757 54.088 42.2574 54.0833 43.1627 53.171Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M62.534 47.067L59.1017 50.4993C60.4644 51.1713 61.729 52.0603 62.8374 53.171C63.2924 53.6283 63.892 53.857 64.4917 53.857C65.0867 53.857 65.684 53.6307 66.1367 53.178C67.0514 52.268 67.056 50.791 66.146 49.8763C65.0494 48.775 63.829 47.8487 62.534 47.067Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M68.8083 40.7927L65.4717 44.1293C66.7177 44.9623 67.8913 45.9237 68.9717 47.0087C69.4267 47.466 70.0264 47.6947 70.626 47.6947C71.221 47.6947 71.8184 47.4683 72.271 47.0133C73.1857 46.1033 73.1904 44.6287 72.2804 43.714C71.2 42.629 70.0287 41.67 68.8083 40.7927Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                        '<path d="M37.026 47.0086C41.296 42.7176 46.9683 40.3563 53 40.3563C53.9613 40.3563 54.9086 40.438 55.8466 40.557L59.8203 36.5833C57.6153 36.014 55.3356 35.6896 53 35.6896C45.72 35.6896 38.8716 38.541 33.7173 43.7163C32.8073 44.631 32.812 46.1056 33.7266 47.0156C34.639 47.9256 36.1206 47.921 37.026 47.0086Z" fill="'+ EASYASSIST_COBROWSE_META.floating_button_bg_color +'"/>',
                    '</svg>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body" style="text-align: center;">',
                    '<h6 style="padding: 1em 0!important;">Weak connection detected!</h6>',
                    "The quality and user experience of the session may be affected due to low bandwidth",
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<button class="easyassist-modal-primary-btn" onclick="easyassist_hide_client_weak_internet_connection(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">OK</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_show_client_weak_internet_connection(element) {
        if(get_easyassist_cookie("easyassist_session_id") != undefined && get_easyassist_cookie("easyassist_session_id") != null) {
            easyassist_hide_agent_weak_internet_connection();
            document.getElementById("easyassist-client-weak-internet-connection-modal").style.display = "flex";
        }
    }

    function easyassist_hide_client_weak_internet_connection(element) {
        document.getElementById("easyassist-client-weak-internet-connection-modal").style.display = "none";
    }

    function easyassist_auto_fetch_details(el) {
        var auto_fetch_fields = EASYASSIST_COBROWSE_META.auto_fetch_fields;
        for (let index = 0; index < auto_fetch_fields.length; index++) {
            var fetch_element = document.querySelectorAll('[' + auto_fetch_fields[index].fetch_field_key + '="' + auto_fetch_fields[index].fetch_field_value + '"]');
            var modal_element = document.querySelectorAll('[' + auto_fetch_fields[index].modal_field_key + '="' + auto_fetch_fields[index].modal_field_value + '"]');
            if (fetch_element != null && modal_element != null && fetch_element.length > 0 && modal_element.length > 0) {
                fetch_element = fetch_element[0];
                modal_element = modal_element[0];
                modal_element.value = fetch_element.value;
            }
        }
    }

    function easyassist_modal_event_handler(event) {
        var key = event.key || event.keyCode;
        if (key === 'Enter' || key === 'enter' || key === 13) {
            document.getElementById('easyassist-client-mobile-number').focus();
            document.getElementById('easyassist-client-mobile-number').select();
        }
    }

    function easyassist_show_browsing_modal(el, clicked_on) {

        if(clicked_on == 'greeting_bubble'){
            is_request_from_greeting_bubble = true;
            is_request_from_exit_intent = false;
            is_request_from_inactivity_popup = false;
            is_request_from_button = false;
        } else {
            is_request_from_greeting_bubble = false;
        }

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

        easyassist_auto_fetch_details();
        if (EASYASSIST_COBROWSE_META.choose_product_category == true && clicked_on == 'greeting_bubble') {
            easyassist_show_product_category_modal();
        } else {
            document.getElementById("easyassist-co-browsing-modal-id").style.display = "flex";
        }

        document.getElementById('easyassist-client-name').focus();
        document.getElementById('easyassist-client-name').select();
        document.addEventListener('keydown', easyassist_modal_event_handler);
        easyassist_hide_floating_sidenav_button();
        // easyassist_hide_greeting_bubble();
    }

    function easyassist_close_browsing_modal(el) {
        document.removeEventListener('keydown',easyassist_modal_event_handler);
        document.getElementById("easyassist-co-browsing-modal-id").style.display = "none";
        easyassist_show_floating_sidenav_button();
    }

    function easyassist_show_connection_modal(){
        document.getElementById("easyassist-conection-modal-id").style.display = "flex";
        setTimeout(function(){
            document.getElementById("easyassist-conection-modal-id").style.display = "none";
        },10000);
    }

    function easyassist_close_connection_modal(el) {
        document.getElementById("easyassist-conection-modal-id").style.display = "none";
    }

    function easyassist_show_connection_timer_reset_modal() {
        document.getElementById("easyassist-conection-timer-reset-modal").style.display = "flex";
        setTimeout(function() {
            easyassist_close_connection_timer_reset_modal();
        }, 10000);
    }

    function easyassist_close_connection_timer_reset_modal(el) {
        document.getElementById("easyassist-conection-timer-reset-modal").style.display = "none";
    }
    
    function easyassist_show_product_category_modal() {
    	document.getElementById("easyassist-product-category-modal-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
        document.getElementById("easyassist-product-category-modal-error").innerHTML = "";
        document.getElementById("easyassist-product-category-modal-id").style.display = "flex";
        easyassist_hide_floating_sidenav_button();
        // easyassist_hide_greeting_bubble();
        document.getElementById("easyassist-co-browsing-modal-id").style.display = "none";
    }

    function easyassist_close_product_category_modal(play_greeting_bubble_sound=true) {
        document.getElementById("easyassist-product-category-modal-id").style.display = "none";
        easyassist_show_floating_sidenav_button(play_greeting_bubble_sound);
    }

    function easyassist_accept_location_request(pos) {
        latitude = pos.coords.latitude;
        longitude = pos.coords.longitude;
    }

    function easyassist_cancel_location_request(pos) {
        latitude = null;
        longitude = null;
    }

    function easyassist_initialize_cobrowsing_using_drop_link() {
        var first_index = window.location.href.indexOf("eadKey");
        if (first_index <= 0) return;
        // var drop_link_key = window.location.href.substring(first_index);

        try{
            var drop_link_key = decodeURIComponent(window.location.href.substring(first_index));
        } catch(err) {

            var drop_link_key = window.location.href.substring(first_index);
        }
        drop_link_key = drop_link_key.substring(drop_link_key.indexOf("=")+1).trim();
        if (drop_link_key == "") return;

        var url = window.location.href;
        url = url.substring(0, first_index-1);
        var title = url;
        if (document.querySelector("title") &&  document.querySelector("title").innerText.trim() != "") {
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

        let json_string = JSON.stringify({
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

        let encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/initialize-using-droplink/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {
                    create_easyassist_local_storage_object(response.session_id);
                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    if(EASYASSIST_COBROWSE_META.show_verification_code_modal == false) {
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                        if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse) {
                            easyassist_go_to_sceensharing_tab(EASYASSIST_COBROWSE_META);
                        }
                    } else {
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }

                    window.location.href = url;

                } else {
                    easyassist_show_function_fail_modal(code=633);
                    // easyassist_show_toast("Cobrowsing session could not be initialized. Please try again.");
                }
            } else if (this.readyState == 4) {
                easyassist_show_function_fail_modal(code=634);
            }
        }
        xhttp.send(params);
    }

    function easyassist_set_product_category() {
        window.EASYASSIST_PRODUCT_CATEGORY = "";
        let selected_product_category = "None";
        selected_product_category = document.getElementById("easyassist-inline-form-input-product-category").value;

        if (selected_product_category == "None" || selected_product_category == "") {
        	document.getElementById("easyassist-product-category-modal-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            document.getElementById("easyassist-product-category-modal-error").innerHTML = "Please select a category";
            return;
        }
        window.EASYASSIST_PRODUCT_CATEGORY = selected_product_category;
        easyassist_close_product_category_modal(false);
        easyassist_show_browsing_modal();
    }

    function easyassist_connect_with_agent(event) {
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
        
        var virtual_agent_code = null;
        if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code) {
            virtual_agent_code = document.getElementById("easyassist-client-agent-virtual-code").value.toString().trim();
            if(virtual_agent_code != "" && !REGEX_AGENT_CODE.test(virtual_agent_code)) {
                let error_message = "Please enter a valid agent code";
                if (!EASYASSIST_COBROWSE_META.connect_with_virtual_agent_code_mandatory) {
                    error_message = "Please enter a valid agent code or continue without a code";
                }
                document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = error_message;
                return;
            }
            virtual_agent_code = sanitize_input_string(virtual_agent_code);
            if (virtual_agent_code == "" && EASYASSIST_COBROWSE_META.connect_with_virtual_agent_code_mandatory) {
            	document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = "Please enter a valid agent code";
                return;
            }
        }

        var title = window.location.href;
        if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
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

        let selected_product_category = -1;
        if (window.EASYASSIST_PRODUCT_CATEGORY != null && window.EASYASSIST_PRODUCT_CATEGORY != undefined && window.EASYASSIST_PRODUCT_CATEGORY.length > 0) {
            selected_product_category = window.EASYASSIST_PRODUCT_CATEGORY;
        }
        document.getElementById("easyassist-co-browsing-connect-button").disabled = true;

        var browsing_time_before_connect_click = get_easyassist_cookie("easyassist_customer_browsing_time");
        if(browsing_time_before_connect_click == null || browsing_time_before_connect_click == undefined){
            browsing_time_before_connect_click = 0;
        }

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
            "browsing_time_before_connect_click": browsing_time_before_connect_click,
            "is_request_from_greeting_bubble": is_request_from_greeting_bubble,
            "is_request_from_exit_intent": is_request_from_exit_intent,
            "is_request_from_button": is_request_from_button,
            "is_request_from_inactivity_popup": is_request_from_inactivity_popup,
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
                easyassist_clear_local_storage();

                if (response.status == 200) {

                    set_easyassist_cookie("easyassist_session_created_on", "request");
                    if(get_easyassist_cookie("easyassist_session_id") != undefined){
                        easyassist_terminate_cobrowsing_session(show_message=false)
                    }

                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    set_easyassist_cookie("easyassist_request_timestamp", Date.now())

                    create_easyassist_local_storage_object(response.session_id);

                    if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code == true || EASYASSIST_COBROWSE_META.show_verification_code_modal == false) {
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                        if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse) {
                            easyassist_go_to_sceensharing_tab(EASYASSIST_COBROWSE_META);
                        }
                    }else{
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }

                    if(EASYASSIST_COBROWSE_META.no_agent_connects_toast) {
                        easyassist_initiate_connection_with_timer_modal();
                    } else {
                        if (EASYASSIST_COBROWSE_META.show_connect_confirmation_modal) {
                            easyassist_show_connection_modal();
                        }    
                    }
                    easyassist_close_browsing_modal();

                } else if (response.status == 103) {
                    document.getElementById("modal-cobrowse-virtual-agent-code-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("modal-cobrowse-virtual-agent-code-error").innerHTML = response.message;
                } else if (response.status == 104) {
                    document.getElementById("modal-cobrowse-customer-number-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            		document.getElementById("modal-cobrowse-customer-number-error").innerHTML = "Please enter valid 10-digit mobile number";
                } else if (response.status == 105) {
                    document.getElementById("modal-cobrowse-customer-name-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("modal-cobrowse-customer-name-error").innerHTML = "Please enter valid name";
                } else {
                    easyassist_close_browsing_modal();
                    easyassist_show_function_fail_modal(code=635);
                    console.error(response);
                }
            } else if (this.readyState == 4) {
                easyassist_close_browsing_modal();
                easyassist_show_function_fail_modal(code=636);
            }
            document.getElementById("easyassist-co-browsing-connect-button").disabled = false;
        }
        xhttp.send(params);
    }

    function easyassist_save_non_working_hour_customer_details(event) {

        document.getElementById("modal-non-working-connect-error").innerHTML = "";
        if(document.getElementById("modal-non-working-customer-name-error")) {
            document.getElementById("modal-non-working-customer-name-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-non-working-customer-name-error").innerHTML = "";
        }
        if(document.getElementById("modal-non-working-customer-number-error")) {
            document.getElementById("modal-non-working-customer-number-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
            document.getElementById("modal-non-working-customer-number-error").innerHTML = "";
        }
        if(document.getElementById("easyassist-non-working-hours-product-category-error")) {
        	document.getElementById("easyassist-non-working-hours-product-category-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
			document.getElementById("easyassist-non-working-hours-product-category-error").innerHTML = "";
        }
        if(document.getElementById("easyassist-non-working-hours-language-error")) {
        	document.getElementById("easyassist-non-working-hours-language-error").previousSibling.classList.remove('easyassist-customer-connect-input-error');
			document.getElementById("easyassist-non-working-hours-language-error").innerHTML = "";
        }
        if(document.getElementById("virtual-agent-code-error-non-working-hours")) {
            document.getElementById("virtual-agent-code-error-non-working-hours").previousSibling.classList.remove('easyassist-customer-connect-input-error');
			document.getElementById("virtual-agent-code-error-non-working-hours").innerHTML = "";
        }

        var full_name = document.getElementById("modal-non-working-client-name").value;
        var mobile_number = "None";
        var regName = /^[a-zA-Z]+[a-zA-Z ]+$/;
        var regMob = /^[6-9]{1}[0-9]{9}$/;
        if (!regName.test(full_name)) {
            document.getElementById("modal-non-working-customer-name-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
            document.getElementById("modal-non-working-customer-name-error").innerHTML = "Please enter valid name";
            return;
        }

        if (EASYASSIST_COBROWSE_META.ask_client_mobile == true || EASYASSIST_COBROWSE_META.ask_client_mobile == "true" || EASYASSIST_COBROWSE_META.ask_client_mobile == "True") {
            mobile_number = document.getElementById("modal-non-working-client-mobile-number").value;
            if (EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == true || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "true" || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "True") {
                if (!regMob.test(mobile_number)) {
                    document.getElementById("modal-non-working-customer-number-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("modal-non-working-customer-number-error").innerHTML = "Please enter valid 10-digit mobile number";
                    return;
                }
            } else {
                if (mobile_number.trim() != "" && !regMob.test(mobile_number)) {
                    document.getElementById("modal-non-working-customer-number-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("modal-non-working-customer-number-error").innerHTML = "Please enter valid 10-digit mobile number";
                    return;
                }
            }
        }

        var selected_product_category = -1;
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            selected_product_category = document.getElementById("easyassist-non-working-hours-product-category").value;
            if (selected_product_category == "None" || selected_product_category == "") {
                document.getElementById("easyassist-non-working-hours-product-category-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("easyassist-non-working-hours-product-category-error").innerHTML = "Please select a category";
                return;
            }
        }

        var selected_language = -1;
        if (EASYASSIST_COBROWSE_META.allow_language_support == "true" || EASYASSIST_COBROWSE_META.allow_language_support == true || EASYASSIST_COBROWSE_META.allow_language_support == "True") {
            selected_language = document.getElementById("easyassist-non-working-hours-preferred-language").value;
            if (selected_language == "None" || selected_language == "") {
                document.getElementById("easyassist-non-working-hours-language-error").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("easyassist-non-working-hours-language-error").innerHTML = "Please select the preferred language";
                return;
            }
        }

        let virtual_agent_code = null;
        if (EASYASSIST_COBROWSE_META.allow_connect_with_virtual_agent_code) {
            virtual_agent_code = document.getElementById("easyassist-non-working-hours-agent-virtual-code").value.toString().trim();
            if(virtual_agent_code != "" && !REGEX_AGENT_CODE.test(virtual_agent_code)) {
                let error_message = "Please enter a valid agent code";
                if (!EASYASSIST_COBROWSE_META.connect_with_virtual_agent_code_mandatory) {
                    error_message = "Please enter a valid agent code or continue without a code";
                }
                document.getElementById("virtual-agent-code-error-non-working-hours").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("virtual-agent-code-error-non-working-hours").innerHTML = error_message;
                return;
            }
            virtual_agent_code = sanitize_input_string(virtual_agent_code);
            if (virtual_agent_code == "" && EASYASSIST_COBROWSE_META.connect_with_virtual_agent_code_mandatory) {
            	document.getElementById("virtual-agent-code-error-non-working-hours").previousSibling.classList.add('easyassist-customer-connect-input-error');
                document.getElementById("virtual-agent-code-error-non-working-hours").innerHTML = "Please enter a valid agent code";
                return;
            }
        }

        var title = window.location.href;
        if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
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

        document.getElementById("modal-non-working-connect-button").disabled = true;

        json_string = JSON.stringify({
            "request_id": request_id,
            "name": full_name,
            "mobile_number": mobile_number,
            "longitude": longitude,
            "latitude": latitude,
            "active_url": window.location.href,
            "customer_id": easyassist_customer_id,
            "selected_product_category": selected_product_category,
            "selected_language": selected_language,
            "is_request_from_greeting_bubble": is_request_from_greeting_bubble,
            "is_request_from_exit_intent": is_request_from_exit_intent,
            "is_request_from_button": is_request_from_button,
            "is_request_from_inactivity_popup": is_request_from_inactivity_popup,
            "virtual_agent_code": virtual_agent_code,
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
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/save-non-working-hour-customer-details/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {
                    easyassist_show_toast(EASYASSIST_COBROWSE_META.auto_response);
                    easyassist_close_non_working_hour_browsing_modal();
                } else if (response.status == 103) {
                    document.getElementById("virtual-agent-code-error-non-working-hours").previousSibling.classList.add('easyassist-customer-connect-input-error');
                    document.getElementById("virtual-agent-code-error-non-working-hours").innerHTML = response.message;
                } else {
                    easyassist_close_non_working_hour_browsing_modal();
                    easyassist_show_function_fail_modal(code=637);
                    console.error(response);
                }
            } else if (this.readyState == 4) {
                easyassist_close_non_working_hour_browsing_modal();
                easyassist_show_function_fail_modal(code=638);
            }
            document.getElementById("modal-non-working-connect-button").disabled = false;
        }
        xhttp.send(params);
    }

    function easyassist_set_new_user() {
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
        if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
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
            "is_request_from_greeting_bubble": is_request_from_greeting_bubble,
            "is_request_from_button": is_request_from_button,
            "is_request_from_exit_intent": is_request_from_exit_intent,
            "is_request_from_inactivity_popup": is_request_from_inactivity_popup,
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
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/set-easyassist-customer/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    if (response.status == 200) {
                        var customer_id = response.customer_id;
                        set_easyassist_cookie("easyassist_customer_id", customer_id);
                    } else {
                        console.error(response);
                    }
                }
            }
        }
        xhttp.send(params);
    }

    function easyassist_show_toast(message) {
        var x = document.getElementById("easyassist-snackbar");
        x.innerHTML = message;
        x.className = "show";
        setTimeout(function() {
            x.className = x.className.replace("show", "");
        }, EASYASSIST_COBROWSE_META.toast_timeout);
    }

    function easyassist_copy_text_to_clipboard_sharable_link() {
        var copyText = document.getElementById("easychat_share_link_Model-content_link_wrapper");
        copyText.select();
        document.execCommand("copy");
        alert("Copied the text: " + copyText.value);
    }

    function easyassist_ascii_to_hexa(str) {

        var temp_arr = [];
        for (let n = 0, l = str.length; n < l; n++) {
            var hex = Number(str.charCodeAt(n)).toString(16);
            temp_arr.push(hex);
        }
        return temp_arr.join('');
    }

    function easyassist_check_new_lead_data(title, description, url, easyassist_sync_data) {

        var meta_data = {
            "product_details": {
                "title": title,
                "description": description,
                "url": url
            },
            "easyassist_sync_data": easyassist_sync_data
        }

        let old_encrypted_meta_data = easyassist_ascii_to_hexa(JSON.stringify(meta_data));
        let encrypted_meta_data = get_easyassist_cookie("encrypted_meta_data");
        return encrypted_meta_data == old_encrypted_meta_data
    }

    function easyassist_update_meta_data(title, description, url, easyassist_sync_data) {

        var meta_data = {
            "product_details": {
                "title": title,
                "description": description,
                "url": url
            },
            "easyassist_sync_data": easyassist_sync_data
        }

        let encrypted_meta_data = easyassist_ascii_to_hexa(JSON.stringify(meta_data));
        set_easyassist_cookie("encrypted_meta_data", encrypted_meta_data);
    }

    function easyassist_sync_client_lead_data_at_server() {

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            easyassist_session_id = "None";
        }

        var title = window.location.href;
        if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        var url = window.location.href;

        let primary_sync_elements = document.querySelectorAll("[easyassist-sync-element=\"primary\"]");
        if (primary_sync_elements.length <= 0) {
            return;
        }

        let primary_value_list = [];

        for (let index = 0; index < primary_sync_elements.length; index++) {

            let primary_value = primary_sync_elements[index].value.trim();

            if (primary_value != "") {
                let primary_value_obj = {
                    "value": primary_value,
                    "label": primary_sync_elements[index].getAttribute("easyassist-sync-element-label"),
                }

                primary_value_list.push(primary_value_obj)
            }
        }
        if (primary_value_list.length <= 0) {
            return;
        }

        let easyassist_sync_elements = document.querySelectorAll("[easyassist-sync-element]");
        if (easyassist_sync_elements.length == 0) {
            return;
        }

        var easyassist_sync_data = [];
        for (let index = 0; index < easyassist_sync_elements.length; index++) {
            easyassist_sync_data.push({
                "value": easyassist_sync_elements[index].value,
                "sync_type": easyassist_sync_elements[index].getAttribute("easyassist-sync-element"),
                "name": easyassist_sync_elements[index].getAttribute("easyassist-sync-element-label")
            });
        }

        if (easyassist_check_new_lead_data(title, description, url, easyassist_sync_data) && lead_capture_initialted) {

            return;
        }

        let selected_product_category = get_easyassist_cookie("easyassist_product_category");
        if (selected_product_category == null || selected_product_category == undefined || selected_product_category.length <=0 ) {
            selected_product_category = "-1"
        }

        lead_capture_initialted = true;

        easyassist_update_meta_data(title, description, url, easyassist_sync_data);

        var request_id = easyassist_request_id();

        json_string = JSON.stringify({
            "request_id": request_id,
            "primary_value_list": primary_value_list,
            "session_id": easyassist_session_id,
            "selected_product_category": selected_product_category,
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
                    create_easyassist_local_storage_object(response.session_id);
                    if (easyassist_session_id == "None") {
                        set_easyassist_cookie("easyassist_session_id", response.session_id);
                        set_easyassist_cookie("easyassist_session_created_on", "lead");
                        if(EASYASSIST_COBROWSE_META.show_verification_code_modal == false) {
                            set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                            if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse) {
                                easyassist_go_to_sceensharing_tab(EASYASSIST_COBROWSE_META);
                            }
                        } else {
                            set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                        }
                    } else if(response.cobrowsing_new_sesion) {
                        delete_easyassist_cookie("easyassist_session_id");
                        set_easyassist_cookie("easyassist_session_id", response.session_id);
                        set_easyassist_cookie("easyassist_session_created_on", "lead");
                        if(EASYASSIST_COBROWSE_META.show_verification_code_modal == false) {
                            set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                            if(EASYASSIST_COBROWSE_META.allow_screen_sharing_cobrowse) {
                                easyassist_go_to_sceensharing_tab(EASYASSIST_COBROWSE_META);
                            }
                        } else {
                            set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                        }
                    }
                } else {
                    console.error(response);
                }
            }
        }
        xhttp.send(params);
    }

    function easyassist_add_search_field_tag() {
        for (let search_tag in search_html_field) {
            let form_elements = document.querySelectorAll(search_tag);
            for (let element_index = 0; element_index < form_elements.length; element_index++) {
                var element_id = form_elements[element_index].getAttribute("id");
                var element_name = form_elements[element_index].getAttribute("name");
                var element_react_id = form_elements[element_index].getAttribute("data-reactid");

                if (form_elements[element_index].type == "hidden") {
                    continue;
                }
                for (let search_index = 0; search_index < search_html_field[search_tag].length; search_index++) {
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

        easyassist_sync_client_lead_data_at_server();
    }

    function easyassist_create_cobrowsing_lead(primary_value, primary_name) {

        var easyassist_sync_data = [];

        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if (easyassist_session_id == null || easyassist_session_id == undefined) {
            easyassist_session_id = "None";
        }

        var title = window.location.href;
        if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
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
                        create_easyassist_local_storage_object(response.session_id);
                        set_easyassist_cookie("easyassist_session_id", response.session_id);
                        window.EASYASSIST_COBROWSE_META.is_lead_generated = true;
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }
                } else {
                    console.error(response);
                }
            }
        }
        xhttp.send(params);
    }

    function easyassist_create_livechat_iframe() {
        let iframe = document.createElement("iframe");
        iframe.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/sales-ai/client/livechat/?access_token=" + EASYASSIST_COBROWSE_META.access_token;
        iframe.id = "easyassist-livechat-iframe";
        iframe.setAttribute("allow", "microphone *");
        iframe.style.display = "none";

        if (EASYASSIST_COBROWSE_META.is_mobile == false && EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            iframe.style.setProperty("left", "1em", "important");
        }

        document.querySelector("body").appendChild(iframe);
    }

    function easyassist_add_agent_mouse_pointer() {
        var agent_mouse_pointer = document.createElement("img");
        agent_mouse_pointer.id = "agent-mouse-pointer";
        agent_mouse_pointer.style.top = "0%";
        agent_mouse_pointer.style.right = "0%";
        agent_mouse_pointer.style.position = "fixed";
        agent_mouse_pointer.style.width = "80px";
        agent_mouse_pointer.style.zIndex = "2147483647";
        agent_mouse_pointer.style.display = "none";
        if(window.EASYASSIST_COBROWSE_META.DEVELOPMENT == true){
            agent_mouse_pointer.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/static/EasyAssistApp/img/Agent_cursor.svg"
        }else{
            agent_mouse_pointer.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/static/EasyAssistApp/img/" + EASYASSIST_COBROWSE_META.access_token + "/Agent_cursor.svg"
        }
        document.body.appendChild(agent_mouse_pointer);
    }

    function easyassist_show_livechat_iframe(show_chat_bubble=true) {
        if(show_chat_bubble == false) {
            return;
        }    
        if(EASYASSIST_COBROWSE_META.enable_chat_functionality) {
            let livechat_iframe = document.getElementById("easyassist-livechat-iframe");
            let livechat_iframe_window = livechat_iframe.contentWindow;
            if (livechat_iframe != null && livechat_iframe != undefined) {

                if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
                    if(livechat_iframe.classList.contains("allincall-scale-out-br")) {
                        livechat_iframe.classList.remove("allincall-scale-out-br");
                    }

                    if(livechat_iframe.classList.contains("allincall-scale-out-br-right-side")) {
                        livechat_iframe.classList.remove("allincall-scale-out-br-right-side");
                    }
                    
                    livechat_iframe.style.display = "block";
                    livechat_iframe.classList.add("animate__animated");
                    livechat_iframe.classList.add("animate__slideInUp");
                } else {
                    document.getElementById("easyassist-livechat-iframe").style.display = "block";
                }
                set_easyassist_current_session_local_storage_obj("new_message_seen","true");
                set_easyassist_current_session_local_storage_obj("last_message","");
                if(livechat_iframe.style.display != "none" && document.getElementById("chat-minimize-icon-wrapper")){
                    document.getElementById("chat-minimize-icon-wrapper").style.display  = "none";
                }
                let allincall_chatbot_window = document.getElementById("allincall-popup");
                if (allincall_chatbot_window != null && allincall_chatbot_window != undefined) {
                    document.getElementById("allincall-popup").style.display = "none";
                    document.getElementById("allincall-chat-box").style.display = "none";
                }
            }
            livechat_iframe_window.postMessage(JSON.stringify({
              "focus_textbox": "focus-textbox"
            }),EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST);
        }
    }
    
    function easyassist_hide_livechat_iframe() {
        try{
            livechat_iframe = document.getElementById("easyassist-livechat-iframe");
            if (livechat_iframe != null && livechat_iframe != undefined) {
                if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false ) {
                    if(livechat_iframe.classList.contains("animate__slideInUp")) {
                        livechat_iframe.classList.remove("animate__slideInUp");
                    }

                    if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
                        livechat_iframe.classList.add("allincall-scale-out-br-right-side");
                    } else {
                        livechat_iframe.classList.add("allincall-scale-out-br");   
                    }
                    
                } else {
                    livechat_iframe.style.display = "none";
                }
                allincall_chatbot_window = document.getElementById("allincall-popup");
                if (allincall_chatbot_window != null && allincall_chatbot_window != undefined) {
                    document.getElementById("allincall-popup").style.display = "block";
                    document.getElementById("allincall-chat-box").style.display = "none";
                }
            }
        }catch(err){}
    }
    
    function easyassist_refresh_livechat_iframe() {
        try{
            livechat_iframe = document.getElementById("easyassist-livechat-iframe");
            if (livechat_iframe != null && livechat_iframe != undefined) {
                livechat_iframe.src = livechat_iframe.src;
            }
        }catch(err){}
    }

    function hide_chat_bubble_greeting_div() {
        document.querySelector(".chat-talk-bubble").style.display = none;
    }

    function easyassist_show_cobrowsing_modal() {
        if (EASYASSIST_COBROWSE_META.choose_product_category == true) {
            easyassist_show_product_category_modal();
        } else {
            easyassist_show_browsing_modal();
        }
    }

    function easyassist_play_greeting_bubble_popup() {
        let livechat_iframe = document.getElementById("easyassist-livechat-iframe");

        if (livechat_iframe && livechat_iframe.classList.contains("animate__slideInUp")) {
            return;
        }

        easyassist_chat_notification_sound();
    }

    function easyassist_chat_notification_sound(){
        let greeting_bubble_popup_sound_element = document.getElementById("easyassist-greeting-bubble-popup-sound");
    
            if (!greeting_bubble_popup_sound_element) {
                return;
            }
    
            try {
                if (greeting_bubble_popup_sound_element.paused) {
                    greeting_bubble_popup_sound_element.play();
                } else {
                    greeting_bubble_popup_sound_element.currentTime = 0;
                }
            } catch (err) {
                console.log(err)
            }
    }

    function add_greeting_bubble(nav_div, is_icon){
        let lighten_theme_color = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 60);
        let talk_text_div_class = "talk-bubble tri-right border round btm-right-in bounce2";
        let talk_text_div_position = "";

        if (EASYASSIST_COBROWSE_META.floating_button_position == "left" || EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            talk_text_div_position = EASYASSIST_COBROWSE_META.floating_button_left_right_position + 50;
        }
        else {
            talk_text_div_position = EASYASSIST_COBROWSE_META.floating_button_left_right_position + 60;
        }
    
        if(is_icon){
            talk_text_div_class = "talk-bubble-icon tri-right border round btm-right-in bounce2";
            talk_text_div_position = EASYASSIST_COBROWSE_META.floating_button_left_right_position + 70;
        }
        let talk_text_div_style = "";
        if (EASYASSIST_COBROWSE_META.floating_button_position == "left"){
            talk_text_div_class = "talk-bubble tri-right border round btm-left-in bounce2";
            if(is_icon){
                talk_text_div_class = "talk-bubble-icon tri-right border round btm-left-in bounce2";
            }
            talk_text_div_style = `left:${talk_text_div_position}px`
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            talk_text_div_class = "talk-bubble tri-right border round btm-right-in bounce2";
            if(is_icon){
                talk_text_div_class = "talk-bubble-icon tri-right border round btm-right-in bounce2";
            }
            talk_text_div_style = `right:${talk_text_div_position}px`
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "top") {
            talk_text_div_class = "talk-bubble tri-right border round btm-top-in bounce2";
            if(is_icon){
                talk_text_div_class = "talk-bubble-icon tri-right border round btm-top-in bounce2";
            }
            talk_text_div_style = `top:${talk_text_div_position}px`
        }
        else {
            talk_text_div_class = "talk-bubble tri-right border round btm-bottom-in bounce2";
            if(is_icon){
                talk_text_div_class = "talk-bubble-icon tri-right border round btm-bottom-in bounce2";
            }
            talk_text_div_style = `bottom:${talk_text_div_position}px`
        }

        let greeting_bubble_onclick = `easyassist_show_browsing_modal(undefined, 'greeting_bubble');`
        if (easyassist_time_to_show_support_button() == false) {
            if(EASYASSIST_COBROWSE_META.enable_non_working_hours_modal_popup == true) {
                greeting_bubble_onclick = `easyassist_show_non_working_hour_modal('greeting_bubble');`
            } else {
                greeting_bubble_onclick = `easyassist_show_toast('${EASYASSIST_COBROWSE_META.message_on_non_working_hours}');`
            }
        }
    
        let talk_text_div = `<div id="talk_text_div" class="${talk_text_div_class}" style="${talk_text_div_style}; border: 2px solid ${lighten_theme_color} !important; z-index: 2147483646;">
                                <div class="talktext" onclick="${greeting_bubble_onclick}" style="color:${lighten_theme_color} !important; cursor: pointer;">
                                    <p style="color:${lighten_theme_color} !important;">${EASYASSIST_COBROWSE_META.greeting_bubble_text}</p>
                                </div>
                                <div class="close-bubble-container" onclick="document.querySelector('#talk_text_div').style.display = 'none';is_greeting_bubble_closed=true;" style="border: 1px solid ${lighten_theme_color};">
                                    <span id="close-bubble" style="display: flex; align-items: center;justify-content: center;margin-top: 5px;">
                                        <svg width="10" height="9" viewBox="0 0 10 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M8.6839 9L5.0029 5.3156L1.32186 9L0.5 8.1787L4.1868 4.5L0.5 0.82134L1.32186 0L5.0029 3.6844L8.6839 0.00578022L9.5 0.82134L5.819 4.5L9.5 8.1787L8.6839 9Z" fill="${lighten_theme_color}"/>
                                        </svg>
                                    </span>
                                </div>
                            </div>`;
        nav_div.innerHTML += talk_text_div;
        easyassist_play_greeting_bubble_popup();

        if(document.getElementById("easyassist-co-browsing-modal-id").style.display == "flex"){
            document.getElementById('talk_text_div').style.display = 'none';
        }
        let element = document.querySelector(".tri-right.border.btm-right-in")
        if(element){
            element.style.setProperty('--talkbubble-theme', `transparent transparent ${lighten_theme_color} transparent`);
        }
        element = document.querySelector(".tri-right.border.btm-left-in")
        if(element){
            element.style.setProperty('--talkbubble-theme', `transparent transparent ${lighten_theme_color} transparent`);
        }
        element = document.querySelector(".tri-right.border.btm-top-in")
        if(element){
            element.style.setProperty('--talkbubble-theme', `transparent transparent ${lighten_theme_color} transparent`);
        }
        element = document.querySelector(".tri-right.border.btm-bottom-in")
        if(element){
            element.style.setProperty('--talkbubble-theme', `${lighten_theme_color} transparent transparent transparent`);
        }

    }

    function easyassist_initialize_proxy_cobrowsing() {
        let first_index = window.location.href.indexOf("proxy-key");
        if (first_index <= 0) 
            return;
        let proxy_key = ""
        try{
            proxy_key = decodeURIComponent(window.location.href.substring(first_index));
        } catch(err) {

            proxy_key = window.location.href.substring(first_index);
        }
        proxy_key = proxy_key.substring(proxy_key.indexOf("/")+1).trim();
        if (proxy_key == "") return;

        let title = document.getElementById('proxy-iframe').contentWindow.document.title;

        let description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }
        
        let easyassist_customer_id = get_easyassist_cookie("easyassist_customer_id");
        if (easyassist_customer_id == null || easyassist_customer_id == undefined) {
            easyassist_customer_id = "None";
        }

        let json_string = JSON.stringify({
            "proxy_key": proxy_key,
            "longitude": longitude,
            "latitude": latitude,
            "meta_data": {
                "product_details": {
                    "title": sanitize_input_string(title),
                    "description": sanitize_input_string(description),
                    "url": window.proxy_active_url,
                }
            }
        });

        let encrypted_data = easyassist_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };
        let params = JSON.stringify(encrypted_data);

        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/cognoai-cobrowse/start-proxy-cobrowsing/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-AccessToken', window.EASYASSIST_COBROWSE_META.access_token);
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = easyassist_custom_decrypt(response.Response);
                response = JSON.parse(response);

                if (response.status == 200) {
                    SESSION_ID = response.session_id;
                    create_easyassist_local_storage_object(response.session_id);
                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    if(EASYASSIST_COBROWSE_META.show_verification_code_modal == false) {
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                    } else {
                        set_easyassist_cookie("easyassist_cobrowsing_allowed", "false");
                    }
                } else {
                    easyassist_show_function_fail_modal(code=633);
                }
            } else if (this.readyState == 4) {
                easyassist_show_function_fail_modal(code=634);
            }
        }
        xhttp.send(params);
    }

    function easyassist_show_hide_floating_page_number(page_number) {
        if(screen.width <= 600) {
            document.getElementById("easy_assist_pdf_render_current_page_span").innerHTML = page_number;
            document.getElementById("easyassist-floating-page-number").classList.remove("d-none");
            document.getElementById("easyassist-floating-page-number").classList.add("easyassist-coview-show-animation");
            setTimeout(function () {
                if(!document.getElementById("easyassist-floating-page-number").classList.contains("d-none")) {
                    document.getElementById("easyassist-floating-page-number").classList.add("d-none");
                    document.getElementById("easyassist-floating-page-number").classList.remove("easyassist-coview-show-animation");
                }
            }, 2000);
        }
    }

    exports.easyassist_play_greeting_bubble_popup = easyassist_play_greeting_bubble_popup
    exports.easyassist_close_connection_modal = easyassist_close_connection_modal;
    exports.easyassist_show_ripple_effect = easyassist_show_ripple_effect;
    exports.easyassist_hide_ripple_effect = easyassist_hide_ripple_effect;
    exports.easyassist_hide_floating_sidenav_button = easyassist_hide_floating_sidenav_button;
    exports.easyassist_show_floating_sidenav_button = easyassist_show_floating_sidenav_button;
    exports.easyassist_show_browsing_modal = easyassist_show_browsing_modal;
    exports.easyassist_close_browsing_modal = easyassist_close_browsing_modal;
    exports.easyassist_show_product_category_modal = easyassist_show_product_category_modal;
    exports.easyassist_close_product_category_modal = easyassist_close_product_category_modal;
    exports.easyassist_set_product_category = easyassist_set_product_category;
    exports.easyassist_connect_with_agent = easyassist_connect_with_agent;
    exports.easyassist_show_toast = easyassist_show_toast;
    exports.easyassist_copy_text_to_clipboard_sharable_link = easyassist_copy_text_to_clipboard_sharable_link;
    exports.easyassist_hide_feedback_form = easyassist_hide_feedback_form;
    exports.easyassist_hide_cobrowse_mobile_navbar_menu = easyassist_hide_cobrowse_mobile_navbar_menu;
    exports.easyassist_show_feedback_form = easyassist_show_feedback_form;
    exports.easyassist_hide_agent_joining_modal = easyassist_hide_agent_joining_modal;
    exports.easyassist_show_agent_joining_modal = easyassist_show_agent_joining_modal;
    exports.easyassist_hide_agent_information_modal = easyassist_hide_agent_information_modal;
    exports.easyassist_show_agent_information_modal = easyassist_show_agent_information_modal;
    exports.easyassist_show_floating_sidenav_menu = easyassist_show_floating_sidenav_menu;
    exports.easyassist_hide_floating_sidenav_menu = easyassist_hide_floating_sidenav_menu;
    exports.easyassist_add_search_field_tag = easyassist_add_search_field_tag;
    exports.easyassist_show_payment_consent_modal = easyassist_show_payment_consent_modal;
    exports.easyassist_hide_payment_consent_modal = easyassist_hide_payment_consent_modal;
    exports.easyassist_create_cobrowsing_lead = easyassist_create_cobrowsing_lead;
    exports.easyassist_create_livechat_iframe = easyassist_create_livechat_iframe;
    exports.easyassist_show_livechat_iframe = easyassist_show_livechat_iframe;
    exports.easyassist_hide_livechat_iframe = easyassist_hide_livechat_iframe;
    exports.easyassist_show_pdf_render_modal = easyassist_show_pdf_render_modal;
    exports.easyassist_refresh_livechat_iframe = easyassist_refresh_livechat_iframe;
    exports.easyassist_show_request_edit_access_form = easyassist_show_request_edit_access_form;
    exports.easyassist_hide_request_edit_access_form = easyassist_hide_request_edit_access_form;
    exports.easyassist_show_connection_modal = easyassist_show_connection_modal;
    exports.easyassist_show_connection_timer_reset_modal = easyassist_show_connection_timer_reset_modal;
    exports.easyassist_close_connection_timer_reset_modal = easyassist_close_connection_timer_reset_modal;
    exports.easyassist_close_connection_modal = easyassist_close_connection_modal;
    exports.easyassist_open_sidenav = easyassist_open_sidenav;
    exports.easyassist_close_sidenav = easyassist_close_sidenav;
    exports.easyassist_on_client_mouse_over_nav_bar = easyassist_on_client_mouse_over_nav_bar;
    exports.easyassist_on_mouse_out_nav_bar = easyassist_on_mouse_out_nav_bar;
    exports.easyassist_clear_close_nav_timeout = easyassist_clear_close_nav_timeout;
    exports.easyassist_create_close_nav_timeout = easyassist_create_close_nav_timeout;
    exports.easyassist_show_non_working_hour_modal = easyassist_show_non_working_hour_modal;
    exports.easyassist_close_non_working_hour_browsing_modal = easyassist_close_non_working_hour_browsing_modal;
    exports.easyassist_save_non_working_hour_customer_details = easyassist_save_non_working_hour_customer_details;
    exports.easyassist_show_dialog_modal = easyassist_show_dialog_modal;
    exports.easyassist_hide_dialog_modal = easyassist_hide_dialog_modal;
    exports.easyassist_show_cobrowsing_modal = easyassist_show_cobrowsing_modal;
    exports.easyassist_show_agent_weak_internet_connection = easyassist_show_agent_weak_internet_connection;
    exports.easyassist_hide_agent_weak_internet_connection = easyassist_hide_agent_weak_internet_connection;
    exports.easyassist_show_agent_disconnected_modal = easyassist_show_agent_disconnected_modal;
    exports.easyassist_hide_agent_disconnected_modal = easyassist_hide_agent_disconnected_modal;
    exports.easyassist_show_client_weak_internet_connection = easyassist_show_client_weak_internet_connection;
    exports.easyassist_hide_client_weak_internet_connection = easyassist_hide_client_weak_internet_connection;
    exports.easyassist_show_edit_access_info_modal = easyassist_show_edit_access_info_modal;
    exports.easyassist_hide_edit_access_info_modal = easyassist_hide_edit_access_info_modal;
    exports.easyassist_show_function_fail_modal = easyassist_show_function_fail_modal;
    exports.easyassist_hide_function_fail_modal = easyassist_hide_function_fail_modal;
    exports.easyassist_display_function_fail_modal = easyassist_display_function_fail_modal;
    exports.easyassist_relocate_drag_element = easyassist_relocate_drag_element;
    exports.easyassist_initiate_connection_with_timer_modal = easyassist_initiate_connection_with_timer_modal;
    exports.easyassist_show_connection_with_timer_modal = easyassist_show_connection_with_timer_modal;
    exports.easyassist_hide_connection_with_timer_modal = easyassist_hide_connection_with_timer_modal;
    exports.easyassist_show_minimized_timer_modal = easyassist_show_minimized_timer_modal;
    exports.easyassist_hide_minimized_timer_modal = easyassist_hide_minimized_timer_modal;
    exports.easyassist_clear_local_storage = easyassist_clear_local_storage;
    exports.easyassist_add_pdf_render_modal = easyassist_add_pdf_render_modal;
    exports.easyassist_show_chat_bubble = easyassist_show_chat_bubble;
    exports.easyassist_hide_pdf_coview = easyassist_hide_pdf_coview;
    exports.easyassist_show_pdf_coview = easyassist_show_pdf_coview;
    exports.easyassist_chat_notification_sound = easyassist_chat_notification_sound;
    
    easyassist_add_ripple_animation_frame();
    easyassist_add_floating_sidenav_button();
    easyassist_add_non_working_hour_modal();
    easyassist_add_product_category_modal();
    easyassist_add_floating_sidenav_menu();
    easyassist_add_feedback_form_modal();
    easyassist_add_agent_joining_modal();
    easyassist_add_pdf_render_modal();
    easyassist_add_request_assist_modal();
    easyassist_add_request_meeting_modal();
    easyassist_add_voip_with_video_calling_request_modal();
    easyassist_add_voip_calling_request_modal();
    easyassist_add_payment_consent_modal();
    easyassist_add_connection_modal();
    easyassist_create_livechat_iframe();
    easyassist_add_chat_bubble_body();
    easyassist_add_request_edit_access_modal();
    easyassist_add_agent_mouse_pointer();
    easyassist_add_agent_information_modal();
    easyassisst_add_dialog_modal();
    easyassist_add_agent_weak_internet_connection();
    easyassist_add_agent_disconnected_modal();
    easyassist_add_client_weak_internet_connection();
    easyassisst_add_edit_access_info_modal();
    easyassist_add_function_fail_modal();
    easyassist_add_drawing_canvas();
    easyassist_add_root_style_variable();
    easyassist_add_voice_call_initiate_modal();
    easyassist_add_video_call_initiate_modal();
    easyassist_chat_bubble_css();
    set_easyassist_cookie("page_leave_status", "None");
    easyassist_add_connection_timer_reset_modal();
    easyassist_add_connection_with_timer_modal();
    easyassist_add_minimized_timer_modal();

    setInterval(function(e) {
        if (document.getElementById("easyassist-co-browsing-modal-id").style.display == "flex") {
            easyassist_set_new_user();
        }
    }, 5000);

    if (EASYASSIST_COBROWSE_META.lead_generation) {
        setInterval(function(e) {
            easyassist_add_search_field_tag();
        }, 5000);
        easyassist_add_search_field_tag();
    }
    
    if(get_easyassist_cookie("easyassist_agent_connected") == "true") {
        if(document.getElementById("chat-minimize-icon-wrapper")){
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
        }
    }

    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    
    if(local_storage_obj && local_storage_obj.hasOwnProperty("new_message_seen")) {
        if(local_storage_obj["new_message_seen"] == "false" && document.getElementById("chat-minimize-icon-wrapper")) {
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
            try {
                document.getElementById("talktext-p").innerHTML = local_storage_obj["last_message"];
            } catch (err) {
                console.log(err)
            }
            document.querySelector(".chat-talk-bubble").style.display = "block";
            document.querySelector(".chat-talk-bubble").classList.add("bounce2");
            easyassist_play_greeting_bubble_popup();
        }
    }

    setInterval(function(e) {
        easyassist_show_floating_sidenav_button();    
    }, 10000);

    if(get_easyassist_cookie("easyassist_page_visited") == undefined || get_easyassist_cookie("easyassist_page_visited") != window.location.href) {
        set_easyassist_cookie_with_path("easyassist_page_visited",window.location.href);
    }

    easyassist_get_eles_by_class_name("easychat_share_link_Model-content-close_button")[0].onclick = function() {
        document.getElementById("easychat_share_link_Model").style.display = "none";
    }

    customer_browsing_interval = setInterval(easyassist_set_customer_browsing_time, CUSTOMER_BROWSING_INTERVAL_TIME*1000)

})(window);
