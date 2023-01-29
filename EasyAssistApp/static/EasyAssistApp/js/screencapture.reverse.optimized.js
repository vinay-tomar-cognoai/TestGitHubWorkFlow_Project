var lead_capture_initialted = false;
var longitude = null;
var latitude = null;
var easyassist_tickmarks_clicked=new Array(11).fill(false);
var is_recursive_call_ended = true;
var is_all_nodes_visited_for_first_time = false;
var document_readystate_interval = null;
window.check_meeting_status_interval = null;
window.auto_msg_popup_on_client_call_declined = false;
window.easyassist_drawing_canvas = null;
window.easyassist_drag_element = null;

var EASYASSIST_FUNCTION_FAIL_DEFAULT_CODE = 500;
var EASYASSIST_FUNCTION_FAIL_DEFAULT_MESSAGE = "Due to some network issue, we are unable to process your request. Please Refresh the page.";
var easyassist_function_fail_time = 0;
var easyassist_function_fail_count = 0;
const EASYASSIST_GENERATE_LINK_TEXT = 'Please provide customer details to generate cobrowsing link and share with the customer';

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

window.EASYASSIST_HTML_ID_TO_REMOVE = [
    "easyassist-agent-information-modal",
    "easyassist-livechat-iframe",
    "easyassist-sidenav-menu-id",
    "easyassist-ripple_effect",
    "easyassist-co-browsing-modal-id",
    "easyassist-product-category-modal-id",
    "easyassist_share_link_Model",
    "easyassist-side-nav-options-co-browsing",
    "easyassist-co-browsing-request-assist-modal",
    "easyassist-co-browsing-request-meeting-modal",
    "easyassist-voip-video-calling-request-modal",
    "easyassist-voip-calling-request-modal",
    "easyassist_agent_joining_modal",
    "agent-mouse-pointer",
    "easyassist-snackbar",
    "easyassist-iframe",
    "easyassist-co-browsing-feedback-modal",
    "easyassist-conection-modal-id",
    "easyassist-co-browsing-request-edit-access",
    "easyassist-co-browsing-payment-consent-modal",
    "easyassist-tooltip",
    "cobrowsing-voip-ringing-sound",
    "cobrowse-mobile-modal",
    "easyassist-agent-disconnected-modal",
    "easyassist-agent-weak-internet-connection-modal",
    "easyassist-client-weak-internet-connection-modal",
    "easyassist_function_fail_modal",
    "easyassist-capture-screenshot-request-modal",
    "easyassist-captured-screenshot-view-modal",
    "easyassist-invite-agent-modal",
    "report_problem_icon",
    "easyassist-co-browsing-report-problem-modal-id",
    "easyassist-support-document-modal",
    "easyassist-drawing-canvas",
    "easyassist-cobrowse-voip-container",
    "chat-minimize-icon-wrapper",
    "cobrowse-mobile-navbar",
    "cobrowse-mobile-navbar-temp",
];

/***************** EasyAssist Custom Select ***********************/

// class EasyassistCustomSelect {
//     constructor(selector, placeholder, background_color) {
//         this.placeholder = placeholder;
//         background_color = background_color;

//         var select_element = document.querySelector(selector);
//         var selected_list_class = "easyassist-option-selected";
//         var show_option_container_class = "easyassist-dropdown-show";
//         var custom_dropdown_selected_option = "";
//         var dropdown_option_selected = false;

//         var custom_dropdown_wrapper = "";
//         var custom_dropdown_option_container = "";
//         var custom_dropdown_options = "";
//         var custom_dropdown_selected_option_wrapper = "";

//         // Create elements
//         custom_dropdown_wrapper = create_element('div', 'easyassist-custom-dropdown-container');
//         custom_dropdown_option_container = create_element('ul', 'easyassist-custom-dropdown-option-container');
//         custom_dropdown_selected_option_wrapper = create_element('div', 'easyassist-dropdown-selected');
//         // select_element.wrap(custom_dropdown_wrapper);
//         select_element.style.display = "none";

//         select_element.parentNode.insertBefore(custom_dropdown_wrapper, select_element);
//         custom_dropdown_wrapper.appendChild(select_element)

//         if(this.placeholder){
//             select_element.selectedIndex = -1;
//         }

//         for(let idx = 0; idx < select_element.children.length; idx ++) {
//             let option_el = select_element.children[idx];
//             let option_text = option_el.text.trim();
//             let option_value = option_el.value;

//             if(option_el.selected) {
//                 dropdown_option_selected = true;
//                 custom_dropdown_selected_option = option_text;
//                 custom_dropdown_options += [
//                     '<li  class="' + selected_list_class + '">',
//                         '<span>' + option_text + '</span>',
//                         '<input type="hidden" value="' + option_value + '">',
//                     '</li>',
//                 ].join('');
//             } else {
//                 custom_dropdown_options += [
//                     '<li>',
//                         '<span>' + option_text + '</span>',
//                         '<input type="hidden" value="' + option_value + '">',
//                     '</li>',
//                 ].join('');
//             }
//         }

//         custom_dropdown_option_container.innerHTML = custom_dropdown_options;
//         select_element.insertAdjacentElement('afterend', custom_dropdown_option_container)

//         if(dropdown_option_selected) {
//             custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
//         } else if(this.placeholder) { 
//             custom_dropdown_selected_option_wrapper.innerHTML = this.placeholder;
//         } else {
//             custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
//         }

//         select_element.insertAdjacentElement('afterend', custom_dropdown_selected_option_wrapper);

//         // Add eventlistener
//         document.addEventListener('click', function(e) {
//             if(e.target == custom_dropdown_selected_option_wrapper) {
//                 custom_dropdown_option_container.classList.toggle(show_option_container_class);
//             } else {
//                 custom_dropdown_option_container.classList.remove(show_option_container_class);
//             }
//         });

//         for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
//             let li_element = custom_dropdown_option_container.children[idx];
//             li_element.addEventListener('click', function(e) {
//                 let selected_option_text = this.innerHTML;
//                 reset_dropdown();
//                 li_element.classList.add(selected_list_class);
//                 li_element.style.setProperty('background-color', background_color, 'important');
//                 custom_dropdown_selected_option_wrapper.innerHTML = selected_option_text;
//                 custom_dropdown_option_container.classList.toggle(show_option_container_class);

//                 // Update selecte drodown
//                 let option_value = li_element.children[1].value;
//                 select_element.value = option_value;
//                 var change_event = new Event('change');
//                 select_element.dispatchEvent(change_event);
//             });

//             li_element.addEventListener('mouseover', function(e) {
//                 li_element.style.setProperty('background-color', background_color, 'important');
//             });

//             li_element.addEventListener('mouseout', function(e) {
//                 if(!li_element.classList.contains(selected_list_class)) {
//                     li_element.style.removeProperty('background-color');
//                 }
//             })
//         }

//         function reset_dropdown() {
//             for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
//                 custom_dropdown_option_container.children[idx].classList.remove(selected_list_class);
//                 custom_dropdown_option_container.children[idx].style.removeProperty('background-color');
//             }
//         }

//         function create_element(html_tag, css_class) {
//             let html_element = document.createElement(html_tag);
//             html_element.className = css_class;
//             return html_element;
//         }
//     }
// }

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

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element)

        if(this.placeholder){
            select_element.selectedIndex = -1;
        }

        var select_option_records = get_custom_dropdown_option_html();
        dropdown_option_selected = select_option_records.dropdown_option_selected;
        custom_dropdown_selected_option = select_option_records.dropdown_selected_option;

        custom_dropdown_option_container.innerHTML = select_option_records.option_html;
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

        custom_dropdown_add_event_listener();

        var _this = this;
        Object.defineProperty(select_element, 'reinitialize', {
            value: function() {
                select_option_records = get_custom_dropdown_option_html();
                dropdown_option_selected = select_option_records.dropdown_option_selected;
                custom_dropdown_selected_option = select_option_records.dropdown_selected_option;

                custom_dropdown_option_container.innerHTML = select_option_records.option_html;

                if(dropdown_option_selected) {
                    custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
                } else if(_this.placeholder) { 
                    custom_dropdown_selected_option_wrapper.innerHTML = _this.placeholder;
                } else {
                    custom_dropdown_selected_option_wrapper.innerHTML = custom_dropdown_selected_option;
                }
                custom_dropdown_add_event_listener();
            }
        });

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

        function get_custom_dropdown_option_html() {
            custom_dropdown_options = "";
            dropdown_option_selected = false;
            custom_dropdown_selected_option = "";

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
            return {
                option_html: custom_dropdown_options,
                dropdown_option_selected: dropdown_option_selected,
                dropdown_selected_option: custom_dropdown_selected_option,
            };
        }

        function custom_dropdown_add_event_listener() {
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
        }
    }
}

/***************** EasyAssist Canvas ***********************/

class EasyAssistCanvas {
    constructor(canvas_element, color, line_width) {
        this.canvas = canvas_element;
        this.reset_canvas_timer = null;

        this.canvas.setAttribute("data-canvas", "easyassist-canvas");
        this.ctx = this.canvas.getContext("2d");
        this.color = color;
        this.line_width = line_width;

        this.prevX = 0;
        this.currX = 0;
        this.prevY = 0;
        this.currY = 0;

        var _this = this;

        _this.canvas.addEventListener("mousemove", function(e) {
            _this.findxy('move', e);
        });

        _this.canvas.addEventListener("mousedown", function(e) {
            _this.findxy('down', e);
        });

        _this.canvas.addEventListener("mouseup", function(e) {
            _this.findxy('up', e);
        });

        _this.canvas.addEventListener("mouseout", function(e) {
            _this.findxy('out', e);
        });

        _this.canvas.addEventListener("touchmove", function(e) {
            var data = {
                clientX: e.touches[0].clientX,
                clientY: e.touches[0].clientY,
            }
            _this.findxy('move', data);
        });

        _this.canvas.addEventListener("touchstart", function(e) {
            var data = {
                clientX: e.touches[0].clientX,
                clientY: e.touches[0].clientY,
            }
            _this.findxy('down', data);
        });

        _this.canvas.addEventListener("touchend", function(e) {
            _this.findxy('out', e);
        });
    }

    findxy(direction, e) {
        if (direction == 'down') {
            this.prevX = e.clientX - this.canvas.offsetLeft;
            this.prevY = e.clientY - this.canvas.offsetTop;
            this.currX = e.clientX - this.canvas.offsetLeft;
            this.currY = e.clientY - this.canvas.offsetTop;

            this.is_drawing = true;
            this.draw_dot();
            this.reset_clear_canvas_interval();
        }

        if (direction == 'up' || direction == "out") {
            this.is_drawing = false;
            this.start_clear_canvas_interval();
        }

        if (direction == 'move') {
            if (this.is_drawing) {
                this.prevX = this.currX;
                this.prevY = this.currY;
                this.currX = e.clientX - this.canvas.offsetLeft;
                this.currY = e.clientY - this.canvas.offsetTop;
                this.draw_line();
            }
        }
    }

    draw_dot() {
        this.draw_dot_utils(this.currX, this.currY);

        easyassist_send_canvas_coordinates_to_socket(
            this.prevX, this.prevY, this.currX, this.currY, this.line_width, 'dot');
    }

    draw_dot_utils(curr_x, curr_y) {
        this.ctx.beginPath();
        this.ctx.fillStyle = this.color;
        this.ctx.arc(curr_x, curr_y, this.line_width / 2, 0, 2 * Math.PI, true);
        this.ctx.fill();
        this.ctx.closePath();
    }

    draw_line() {
        this.draw_line_utils(this.prevX, this.prevY, this.currX, this.currY)

        easyassist_send_canvas_coordinates_to_socket(
            this.prevX, this.prevY, this.currX, this.currY, this.line_width, 'line');
    }

    draw_line_utils(prev_x, prev_y, curr_x, curr_y) {
        this.ctx.lineCap = "round";
        this.ctx.beginPath();
        this.ctx.moveTo(prev_x, prev_y);
        this.ctx.lineTo(curr_x, curr_y);
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = this.line_width;
        this.ctx.stroke(); 
        this.ctx.closePath();
    }

    start_clear_canvas_interval() {
        var _this = this;

        _this.reset_clear_canvas_interval();

        _this.reset_canvas_timer = setTimeout(function() {
            _this.clear_drawing();
        }, 2000);
    }

    reset_clear_canvas_interval() {
        var _this = this;

        if(_this.reset_canvas_timer != null) {
            clearTimeout(_this.reset_canvas_timer);
            _this.reset_canvas_timer = null;
        }
    }


    clear_drawing() {
        var _this = this;
        _this.ctx.clearRect(0, 0, _this.canvas.width, _this.canvas.height);

        _this.reset_clear_canvas_interval();

        easyassist_send_reset_canvas_over_socket();
    }

    resize_canvas(width, height) {
        this.canvas.width = width;
        this.canvas.height = height;
    }
}

/***************** EasyAssist Drag Element ***********************/

class EasyAssistDragElement {
    constructor(element) {
        this.element = element;
        this.element.setAttribute("data-easyassist-drag", "true");
        this.element.style.cursor = "move";
        this.horizontal_flip_selector_list = ["span", "svg", "iframe"];

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
            var data = {
                movementX: e.touches[0].clientX - _this.prevX,
                movementY: e.touches[0].clientY - _this.prevY,
            }
            _this.prevX = e.touches[0].clientX;
            _this.prevY = e.touches[0].clientY;
            _this.drag_element('move', data);
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

        var _this = this;
        _this.drag_container.addEventListener("mousemove", function(e) {
            _this.drag_element('move', e);
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

        if (direction == 'move') {
            event.preventDefault()
            if (this.is_dragging) {

                let originalStyles = window.getComputedStyle(this.element);
                this.currX = e.movementX + parseInt(originalStyles.left);
                this.currY = e.movementY + parseInt(originalStyles.top)

                this.drag();
            }
        }
    }

    drag(horizontal_flip = false) {
        this.currX = Math.max(this.currX, 0);

        this.element.style.left = this.currX + "px";
        this.element.style.top = this.currY + "px";

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
            var tooltip_spans = this.element.getElementsByTagName(selector);
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

            if(left == 0) {
                flip_horizontal = false;
            } else {
                flip_horizontal = true;
            }
        } else {
            left = 0;
            flip_horizontal = false;
        }

        this.currX = left;
        this.currY = top;
        this.drag(flip_horizontal);
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
        for(let i = 0; i <= current_hover_value; i++) {
            if (el.children[i] != undefined) {
                el.children[i].style.color = "black"
                el.children[i].style.backgroundColor = "white"
            }
        }
    }
}

function change_color_rating_z_bar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for(let i = current_hover_value; i <= current_hover_value; i++) {
        if (el.parentElement.children[i] != undefined) {
            el.parentElement.children[i].style.color = "black"
            el.parentElement.children[i].style.backgroundColor = "white"
        }
    }
}

function change_color_rating_v_bar(el) {
    current_hover_value = parseInt(el.getAttribute("value"));
    for(let i = 0; i < current_hover_value; i++) {
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
    for(let j = current_hover_value; j <= el.parentElement.childElementCount; j++) {
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
        }else if(data.event_id == "open_pdf_render_modal"){
            easyassist_show_chat_bubble();
            easyassist_show_pdf_render_modal(data.file_name,data.file_src,data.session_id);
        } else if (data.event_id == "close-bot") {
            hide_easyassist_livechat_iframe();
            if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
                document.querySelector(".chat-talk-bubble").style.display = "none";
                document.getElementById("chat-minimize-icon-wrapper").style.display = "none";
            }
        } else if (data.event_id == "cobrowsing-client-chat-message") {
            message = data.data.message;
            attachment = data.data.attachment;
            attachment_file_name = data.data.attachment_file_name;
            send_livechat_message_to_agent(message, attachment, attachment_file_name, "chat_message");
        } else if (event.data.event_id === "livechat-typing") {
            easyassist_send_livechat_typing_indication()
            return
        } else if(data.event_id == "minimize-chatbot") {
            document.querySelector(".chat-talk-bubble").style.display = "none";
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
        }

        if(event.data.event == "voip_function_error") {
            easyassist_show_function_fail_modal(code=event.data.error_code);
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

/******************************* Custom EasyAssist Utils Functions *******************************************/

function easyassist_get_eles_by_class_name(clsName){
    var retVal = [];
    try {
        retVal = document.getElementsByClassName(clsName);
    } catch(err) {
        retVal = new Array();
        var elements = document.getElementsByTagName("*");
        for ( var i = 0; i < elements.length; i++) {
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

function feedback_easyassist_modal(el) {
    el.parentElement.setAttribute("zQPK", "true")
    contentvalue = parseInt(el.getAttribute("value"));
    window.EASYASSIST_CLIENT_FEEDBACK = contentvalue;
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

function easyassist_prevent_non_numeric_characters(event) {
    var blacklisted_keycode = [69, 107, 109, 110, 187, 189, 190];
    if(blacklisted_keycode.includes(event.keyCode)) {
        event.preventDefault();
    }
}

function easyassist_phone_number_paste_handler(event) {
    let easyassist_pasted_data = (event.clipboardData || window.clipboardData).getData('text');
    if(easyassist_pasted_data.indexOf('.') > -1) {
        event.preventDefault();
    }
}

(function(exports) {

    window.EASYASSIST_TAG_VALUE = "easyassist-tag-value";

    var search_html_field = window.EASYASSIST_COBROWSE_META.search_html_field;
    var obfuscated_fields = window.EASYASSIST_COBROWSE_META.obfuscated_fields;
    // var easyassist_id_count = 0;
    window.easyassist_close_nav_timeout = null;
    var custom_select_removed_fields = window.EASYASSIST_COBROWSE_META.custom_select_removed_fields;
    window.easyassist_visited_nodes_map = {};
    window.easyassist_element_id_counter = 0;
    window.parse_dom_tree_interval = null;
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

    function add_easyassist_event_listner_into_element(html_element, event_type, target_function){
        html_element.removeEventListener(event_type, target_function);
        html_element.addEventListener(event_type, target_function);
    }

    function remove_easyassist_event_listner_into_element(html_element, event_type, target_function){
        html_element.removeEventListener(event_type, target_function);
    }

    function obfuscate_data_using_recursion(element) {

        if (!element.children.length) {

            element.innerHTML = easyassist_obfuscate(element.innerHTML);
            return;
        }

        for(let index = 0; index < element.children.length; index++) {

            obfuscate_data_using_recursion(element.children[index]);
        }

        var child_objects = element.children;

        var inner_text = element.innerText;
        if (inner_text.length > 0 && inner_text[0] != 'X') {

            element.innerHTML = "XXXXXXXXXX";
            for (index = 0; index < child_objects.length; index++) {

                element.appendChild(child_objects[index]);
            }
            return;
        }
        return;
    }

    function easyassist_obfuscated_element_check(element) {

        var is_obfuscated_element = false;
        for(let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            element_value = element.getAttribute(obfuscated_fields[mask_index]["key"]);
            if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                return [true, obfuscated_fields[mask_index]["masking_type"]];
            }
        }
        return [false, ""];
    }

    function is_custom_select_removed(element) {

        try {
            for(let index = 0; index < custom_select_removed_fields.length; index++) {
                element_value = element.getAttribute(custom_select_removed_fields[index]["key"]);
                if (element_value != null && element_value != undefined && element_value == custom_select_removed_fields[index]["value"]) {
                    return true;
                }
            }
            return false;
        } catch(err) {
            return false;
        }
    }

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

    function easyassist_set_event_listeners(elements = null) {
        if(elements == null) {
            elements = document.getElementsByTagName("*");
        }


        for(let idx = 0; idx < elements.length; idx ++) {
            var tag_name = elements[idx].tagName;

            if(tag_name in EASYASSIST_ATTACH_EVENT_LISTENERS) {
                EASYASSIST_ATTACH_EVENT_LISTENERS[tag_name](elements[idx]);
            }

            add_easyassist_event_listner_into_element(elements[idx], "scroll", easyassist_sync_scroll_position_inside_div);
        }

        set_easyassist_masked_field_attr();
    }

    function create_easyassist_value_attr_into_document() {

        set_easyassist_masked_field_attr();

        document_input_tag_list = document.querySelectorAll("input");

        for(let d_index = 0; d_index < document_input_tag_list.length; d_index++) {

            add_easyassist_event_listner_into_element(document_input_tag_list[d_index], "change", easyassist_sync_html_element_value_change)

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

            var is_obfuscated_element = easyassist_obfuscated_element_check(document_input_tag_list[d_index]);

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

        document_textarea_tag_list = document.querySelectorAll("textarea");
        for (d_index = 0; d_index < document_textarea_tag_list.length; d_index++) {

            add_easyassist_event_listner_into_element(document_textarea_tag_list[d_index], "scroll", easyassist_sync_scroll_position_inside_div);
            is_active_element = false;
            if (document.activeElement == document_textarea_tag_list[d_index]) {
                is_active_element = true;
            }

            document_textarea_tag_list[d_index].removeAttribute("easyassist-active");
            if (is_active_element) {
                document_textarea_tag_list[d_index].setAttribute("easyassist-active", "true");
            }

            is_numeric = false;
            if (isNaN(parseInt(document_textarea_tag_list[d_index].value)) == false) {
                is_numeric = true;
            }

            is_obfuscated_element = easyassist_obfuscated_element_check(document_textarea_tag_list[d_index]);
            if (is_obfuscated_element[0]) {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value, is_obfuscated_element[1]));
            } else if (is_numeric) {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, easyassist_obfuscate(document_textarea_tag_list[d_index].value));
            } else {
                document_textarea_tag_list[d_index].setAttribute(EASYASSIST_TAG_VALUE, document_textarea_tag_list[d_index].value);
            }
        }

        document_select_tag_list = document.querySelectorAll("select");

        easyassist_apply_custom_select(document_select_tag_list);
        for (d_index = 0; d_index < document_select_tag_list.length; d_index++) {

            add_easyassist_event_listner_into_element(document_select_tag_list[d_index], "change", easyassist_sync_html_element_value_change);
            
            is_active_element = false;
            if (document.activeElement == document_select_tag_list[d_index]) {
                is_active_element = true;
            }

            document_select_tag_list[d_index].removeAttribute("easyassist-active");
            if (is_active_element) {
                document_select_tag_list[d_index].setAttribute("easyassist-active", "true");
            }

            is_obfuscated_element = easyassist_obfuscated_element_check(document_select_tag_list[d_index]);

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

        document_table_tag_list = document.querySelectorAll("table");
        for (d_index = 0; d_index < document_table_tag_list.length; d_index++) {

            is_obfuscated_element = false;
            for(let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
                element_value = document_table_tag_list[d_index].getAttribute(obfuscated_fields[mask_index]["key"]);
                if (element_value != null && element_value != undefined && element_value == obfuscated_fields[mask_index]["value"]) {
                    is_obfuscated_element = true;
                    break;
                }
            }

            if (!is_obfuscated_element) {

                continue;
            }
            for(let row_index = 0; row_index < document_table_tag_list[d_index].tBodies[0].rows.length; row_index++) {

                for(let col_index = 0; col_index < document_table_tag_list[d_index].tBodies[0].rows[row_index].children.length; col_index++) {

                    var table_element = document_table_tag_list[d_index].tBodies[0].rows[row_index].children[col_index];
                    add_easyassist_event_listner_into_element(table_element, "change", easyassist_sync_html_element_value_change)
                }
            }
        }

        document_a_tag_list = document.querySelectorAll("a");
        for (index = 0; index < document_a_tag_list.length; index++) {
            document_a_tag_list[index].classList.add("easyassist-click-element");
        }

        document_button_tag_list = document.querySelectorAll("button");
        for(let index = 0; index < document_button_tag_list.length; index++) {
            document_button_tag_list[index].classList.add("easyassist-click-element");
        }
    }


    function set_value_attr_into_screenshot(screenshot) {
        var easyassist_edit_access = get_easyassist_cookie("easyassist_edit_access");
        screenshot_input_tag_list = screenshot.querySelectorAll("input");
        for(let s_index = 0; s_index < screenshot_input_tag_list.length; s_index++) {
            // if (easyassist_edit_access != "true") {
            //     screenshot_input_tag_list[s_index].style.pointerEvents = 'none';
            // }
            attr_type = screenshot_input_tag_list[s_index].getAttribute("type");
            easyassist_tag_value = screenshot_input_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
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

        screenshot_textarea_tag_list = screenshot.querySelectorAll("textarea");
        for (let s_index = 0; s_index < screenshot_textarea_tag_list.length; s_index++) {
            // if (easyassist_edit_access != "true") {
            //     screenshot_textarea_tag_list[s_index].style.pointerEvents = 'none';
            // }
            easyassist_tag_value = screenshot_textarea_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
            screenshot_textarea_tag_list[s_index].value = easyassist_tag_value;
            screenshot_textarea_tag_list[s_index].innerHTML = easyassist_tag_value;
            screenshot_textarea_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);
        }

        screenshot_select_tag_list = screenshot.querySelectorAll("select");
        for (let s_index = 0; s_index < screenshot_select_tag_list.length; s_index++) {
            // if (easyassist_edit_access != "true") {
            //     screenshot_select_tag_list[s_index].style.pointerEvents = 'none';
            // }
            easyassist_tag_value = screenshot_select_tag_list[s_index].getAttribute(EASYASSIST_TAG_VALUE);
            screenshot_select_tag_list[s_index].setAttribute("value", easyassist_tag_value);
            screenshot_select_tag_list[s_index].removeAttribute(EASYASSIST_TAG_VALUE);

            if (easyassist_tag_value == "XXXXX") {
                var obfuscated_option = document.createElement("option");
                obfuscated_option.value = "XXXXX";
                obfuscated_option.innerHTML = "XXXXX";
                screenshot_select_tag_list[s_index].appendChild(obfuscated_option);
            }

            for(let option_index = 0; option_index < screenshot_select_tag_list[s_index].options.length; option_index++) {
                screenshot_select_tag_list[s_index].options[option_index].removeAttribute("selected");
                if (screenshot_select_tag_list[s_index].options[option_index].innerHTML == easyassist_tag_value) {
                    screenshot_select_tag_list[s_index].options[option_index].setAttribute("selected", "selected");
                }
            }
        }

        screenshot_table_tag_list = screenshot.querySelectorAll("table");

        for(let d_index = 0; d_index < screenshot_table_tag_list.length; d_index++) {

            var is_obfuscated_element = easyassist_obfuscated_element_check(screenshot_table_tag_list[d_index]);
            if (!is_obfuscated_element[0]) {

                continue;
            }
            for(let row_index = 0; row_index < screenshot_table_tag_list[d_index].tBodies[0].rows.length; row_index++) {

                for(let col_index = 0; col_index < screenshot_table_tag_list[d_index].tBodies[0].rows[row_index].children.length; col_index++) {

                    var table_element = screenshot_table_tag_list[d_index].tBodies[0].rows[row_index].children[col_index];
                    obfuscate_data_using_recursion(table_element);
                }
            }
        }

        screenshot_label_tag_list = screenshot.querySelectorAll("label");
        for (let d_index = 0; d_index < screenshot_label_tag_list.length; d_index++) {
            // if (easyassist_edit_access != "true") {
            //     screenshot_label_tag_list[d_index].style.pointerEvents = 'none';
            // }
            label_id = screenshot_label_tag_list[d_index].getAttribute("id");
            if (label_id == null || label_id == undefined) {
                continue;
            }
            
            let is_obfuscated_element = easyassist_obfuscated_element_check(screenshot_label_tag_list[d_index]);
            if (!is_obfuscated_element[0]) {

                continue;
            }
            screenshot_label_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_label_tag_list[d_index].innerHTML);
        }

        screenshot_li_tag_list = screenshot.querySelectorAll("li");
        for(let d_index = 0; d_index < screenshot_li_tag_list.length; d_index++) {

            li_id = screenshot_li_tag_list[d_index].getAttribute("id");
            if (li_id == null || li_id == undefined) {
                continue;
            }

            if (!easyassist_obfuscated_element_check(screenshot_li_tag_list[d_index])[0]) {

                continue;
            }
            screenshot_li_tag_list[d_index].innerHTML = easyassist_obfuscate(screenshot_li_tag_list[d_index].innerHTML);
        }

        screenshot_p_tag_list = screenshot.querySelectorAll("p");

        for(let p_index = 0; p_index < screenshot_p_tag_list.length; p_index++) {
            let is_obfuscated_element = false;
            for(let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
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

        for(let div_index = 0; div_index < screenshot_div_tag_list.length; div_index++) {
            screenshot_div_tag_list[div_index].onscroll = sync_mouse_position
            let is_obfuscated_element = false;
            for (let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
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
        for(let d_index = 0; d_index < document_span_tag_list.length; d_index++) {
            let is_obfuscated_element = easyassist_obfuscated_element_check(document_span_tag_list[d_index]);
            if (is_obfuscated_element[0]) {
                easyassist_tag_value = document_span_tag_list[d_index].getAttribute(EASYASSIST_TAG_VALUE);
                document_span_tag_list[d_index].innerHTML = easyassist_tag_value;
                document_span_tag_list[d_index].removeAttribute(EASYASSIST_TAG_VALUE);
            }
            if(document_span_tag_list[d_index].className == "easyassist-tooltiptext")
                document_span_tag_list[d_index].style.display = "none";
        }

        // screenshot_a_tag_list = screenshot.querySelectorAll("a");
        // for(let index = 0; index < screenshot_a_tag_list.length; index++) {
        //     if (easyassist_edit_access != "true") {
        //         screenshot_a_tag_list[index].style.pointerEvents = 'none';
        //     }
        // }

        // screenshot_button_tag_list = screenshot.querySelectorAll("button");
        // for(let index = 0; index < screenshot_button_tag_list.length; index++) {
        //     if (easyassist_edit_access != "true") {
        //         screenshot_button_tag_list[index].style.pointerEvents = 'none';
        //     }
        // }

        screenshot_custom_select_elements = screenshot.querySelectorAll(".easyassist-dropdown-selected2")
        for(let index = 0; index < screenshot_custom_select_elements.length; index++) {
            is_obfuscated = easyassist_obfuscated_element_check(screenshot_custom_select_elements[index]);
            if(is_obfuscated[0])
                screenshot_custom_select_elements[index].innerText = easyassist_obfuscate(screenshot_custom_select_elements[index].innerText, is_obfuscated[1]);
        }

        screenshot_custom_select_li_item = screenshot.querySelector(".easyassist-custom-dropdown-option-container2")
        if(screenshot_custom_select_li_item) {
            is_obfuscated = easyassist_obfuscated_element_check(screenshot_custom_select_li_item);
            if(is_obfuscated[0])
                obfuscate_data_using_recursion(screenshot_custom_select_li_item);
        }
    }

    function set_easyassist_blur_fields(){
        try{
            var obfuscated_elements = document.querySelectorAll("[easyassist-obfuscate]")
            for(let index=0 ; index<obfuscated_elements.length ; index++){
                try{
                    var obfuscated_element = obfuscated_elements[index];
                    if(obfuscated_element){
                        obfuscated_element.classList.add('easyassist-blured-element');
                        obfuscated_element.disabled = true;
                    }
                } catch (err) {}
            }
        } catch (err) {}
    }

    function remove_easyassist_blur_fields(){
        try{
            var obfuscated_elements = document.querySelectorAll("[easyassist-obfuscate]")
            for(let index=0 ; index<obfuscated_elements.length ; index++){
                try{
                    var obfuscated_element = obfuscated_elements[index];
                    if(obfuscated_element){
                        obfuscated_element.classList.remove('easyassist-blured-element');
                        obfuscated_element.disabled = false;
                    }
                } catch (err) {}
            }
        } catch (err) {}
    }

    function set_easyassist_masked_field_attr(){
        for(let mask_index = 0; mask_index < obfuscated_fields.length; mask_index++) {
            var query = '[' + obfuscated_fields[mask_index]['key'] + '="' + obfuscated_fields[mask_index]['value'] + '"]';
            var obfuscated_elements = document.querySelectorAll(query);
            for(let index = 0; index < obfuscated_elements.length; index++) {
                obfuscated_elements[index].setAttribute("easyassist-obfuscate", obfuscated_fields[mask_index]['masking_type']);
            }

        }
        set_easyassist_blur_fields();
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

    function screenshot_page() {
        create_easyassist_value_attr_into_document();
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

    function add_connection_easyassist_modal() {
        var div_model = document.createElement("div");
        div_model.id = "easyassist-conection-modal-id"
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";
        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header">',
                    '<h6>Connect with the Customer</h6>',
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
        let email_input_html = "";

        if (EASYASSIST_COBROWSE_META.ask_client_mobile == true || EASYASSIST_COBROWSE_META.ask_client_mobile == "true" || EASYASSIST_COBROWSE_META.ask_client_mobile == "True") {
            if (EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == true || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "true" || EASYASSIST_COBROWSE_META.is_client_mobile_mandatory == "True") {
                mobile_input_html += [
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row; border-radius:30px !important;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                            '<input type="number" autocomplete="off" name="easyassist-client-mobile-number" id="easyassist-client-mobile-number" onpaste="easyassist_phone_number_paste_handler(event);" onkeydown="easyassist_prevent_non_numeric_characters(event);easyassist_word_limit(event, this, 10);" placeholder="Enter mobile number" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
                        '</div>',
                        '<label id="modal-cobrowse-customer-number-error"></label>',
                    '</div>',
                ].join('');
            } else {
                mobile_input_html += [
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div style="display:flex;flex-direction:row;border-radius:30px !important;">',
                            '<span class="easyassist-customer-connect-span-prepend">+91</span>',
                            '<input type="number" autocomplete="off" name="easyassist-client-mobile-number" id="easyassist-client-mobile-number" onpaste="easyassist_phone_number_paste_handler(event);" onkeydown="easyassist_prevent_non_numeric_characters(event);easyassist_word_limit(event, this, 10);" placeholder="Enter mobile Number (optional)" style="border-radius: 0 30px 30px 0!important;margin-left: -1px;" >',
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

        email_input_html +=[`
        <div class="easyassist-customer-connect-modal-content-wrapper"  >
            <input type="text" autocomplete="off" name="easyassist-client-agent-email-id" id="easyassist-client-agent-email-id" placeholder="Enter email address (Optional)"   />
            <label id="modal-cobrowse-virtual-agent-email-id"  ></label>
        </div>
        `].join('');

        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content">',
                '<div class="easyassist-customer-connect-modal-header" style="text-align: center;">',
                    '<h6>Connect with the Customer</h6>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-body">',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<span class="note-text">'+EASYASSIST_GENERATE_LINK_TEXT+'</span>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<input type="text" autocomplete="off" name="easyassist-client-name" id="easyassist-client-name" placeholder="Enter full name">',
                        '<label id="modal-cobrowse-customer-name-error"></label>',
                    '</div>',
                    mobile_input_html,
                    virtual_agent_code_html,
                    email_input_html,
                    lang_dropdown_html,                                       
                    '<label id="modal-cobrowse-connect-error"></label>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer">',
                    '<div style="padding-top: 1em; display: flex">',
                        '<button class ="easyassist-modal-cancel-btn" id="easyassist-co-browsing-connect-cancel-btn" onclick="close_easyassist_browsing_modal()">Cancel</button>',
                        '<button class ="easyassist-modal-primary-btn" id="easyassist-co-browsing-connect-button"  onclick="connect_with_easyassist_customer()">Generate Link</button>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        div_model.innerHTML = modal_html;

        var sharable_link = [
            '<div id="easyassist_share_link_Model" class="easyassist-customer-connect-modal" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
            '<div class="easyassist-customer-connect-modal-content" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                '<div class="easyassist-customer-connect-modal-header" easyassist-data-scroll-x="0"',
                    'easyassist-data-scroll-y="0">',
                    '<h6  ><span class="easyassist-svg-wrapper"',
                            'style="background-color: #fff!important"  >',
                            '<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<rect width="36" height="36" rx="18" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                '<path d="M16.3334 18.8333C16.6913 19.3118 17.1478 19.7077 17.6722 19.9941C18.1965 20.2806 18.7763 20.4509 19.3722 20.4936C19.9682 20.5363 20.5664 20.4503 21.1262 20.2415C21.686 20.0327 22.1943 19.7059 22.6167 19.2833L25.1167 16.7833C25.8757 15.9975 26.2957 14.945 26.2862 13.8525C26.2767 12.76 25.8385 11.715 25.066 10.9424C24.2934 10.1699 23.2484 9.7317 22.1559 9.7222C21.0634 9.71271 20.0109 10.1327 19.225 10.8917L17.7917 12.3167" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '<path d="M19.6667 17.1667C19.3088 16.6882 18.8522 16.2923 18.3279 16.0059C17.8036 15.7194 17.2238 15.5491 16.6278 15.5064C16.0319 15.4637 15.4337 15.5497 14.8739 15.7585C14.3141 15.9673 13.8058 16.2941 13.3834 16.7167L10.8834 19.2167C10.1244 20.0025 9.70441 21.055 9.7139 22.1475C9.7234 23.24 10.1616 24.285 10.9341 25.0576C11.7067 25.8301 12.7517 26.2683 13.8442 26.2778C14.9367 26.2873 15.9892 25.8673 16.775 25.1083L18.2 23.6833" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '</svg>',
                                
                            '</span><span  >Co-browsing link</span></h6>',
                '</div>',                
                '<div class="easyassist-customer-connect-modal-body" style="padding: 0.5em 0em 0em 0em!important; min-height: 5em!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<div class="easyassist-customer-connect-modal-content-wrapper">',
                        '<div class="easyassist-customer-connect-input-div">',
                        '<input type="text" id="easyassist_share_link_Model-content_link_wrapper" disabled autocomplete="off">',
                        '</div>',
                        '<div class="easyassist-customer-connect-copy-link-btn-div">',
                        '<button id="cobrowse-share-link-copy-btn" onclick="copy_text_to_clipboard_sharable_link_easyassist()" onmouseover="easyassist_change_background_color(this)" onmouseout="easyassist_remove_background_color(this)" style="color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + ';">Copy link</button>',
                        '</div>',
                    '</div>',
                    '<div id="generate_link_comment">',
                        '<div class="easyassist-customer-connect-modal-content-wrapper">',
                            '<p>Copy the above generated link and share with the customer.</p>',
                        '</div>',
                    '</div>',
                '</div>',
                '<div class="easyassist-customer-connect-modal-footer" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0" style="padding: 0px !important;">',
                    '<button class="easyassist_share_link_Model-content-close_button" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;">Close</button>',
                '</div>',
            '</div>',
            '</div>'
        ].join('');


        document.getElementsByTagName("body")[0].appendChild(div_model);
        document.getElementById("easyassist-co-browsing-connect-cancel-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-co-browsing-connect-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', sharable_link);

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
            for(let index = 0; index < EASYASSIST_COBROWSE_META.product_category_list.length; index++) {
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
          nav_span.style.left = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
          nav_span.style.top = "40%";
          nav_span.style.setProperty("border-radius", "10px 0px 0px 10px", "important");
        } else if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
          nav_span.style.right = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
          nav_span.style.top = "40%";
          nav_span.style.setProperty("border-radius", "0px 10px 10px 0px", "important");
        } else if (
          EASYASSIST_COBROWSE_META.floating_button_position == "top") {
          nav_span.style.top = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
          nav_span.style.setProperty(
            "transform",
            "rotate(0deg) translateX(-50%)",
            "important"
          );
          nav_span.style.setProperty("padding", "5px 10px 5px 10px");
          nav_span.style.setProperty("writing-mode", "horizontal-tb", "important")
          nav_span.style.left = "50%";
        } else {
          nav_span.style.bottom = (EASYASSIST_COBROWSE_META.floating_button_left_right_position).toString() +"px";
          nav_span.style.left = "50%";
          nav_span.style.setProperty("writing-mode", "horizontal-tb", "important")
          nav_span.style.setProperty(
            "transform",
            "rotate(0deg) translateX(-50%)",
            "important"
          );
          nav_span.style.padding = "5px 10px 5px 10px";
          nav_span.style.setProperty("border-radius", "10px 10px 0px 0px", "important");
        }
        nav_span.textContent = "Generate Support Link";
        nav_span.setAttribute("onclick", "show_easyassist_browsing_modal()");

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
        easychat_popup_image.setAttribute("onclick", "show_easyassist_browsing_modal()");
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

    function show_easyassist_feedback_form(el) {

        easyassist_check_is_lead_converted();
        hide_easyassist_video_calling_request_modal();
        easyassist_hide_pdf_coview();
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
                            '<div style="padding-top: 1em; display:flex;">',
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
                            '<h6 style="padding-bottom:12px; text-align: center;">Connect with our experts</h6>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body">',
                            '<div class="easyassist-customer-connect-modal-content-wrapper" style="text-align:center;padding-top:0!important;">',
                                EASYASSIST_COBROWSE_META.assist_message,
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer">',
                            '<div style="padding-top: 1em; display:flex;">',
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

    function add_easyassist_request_meeting_modal() {
        var meeting_modal_html = [
            '<div id="easyassist-co-browsing-request-meeting-modal" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>Connect with the Customer</h6>',
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
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>Edit Access</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body" style="min-height: 7em!important;">',
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
        let meeting_modal_html = "";
        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            meeting_modal_html = [
                '<div id="easyassist-voip-video-calling-request-modal" class="easyassist-customer-connect-modal eassyassist-custom-in-session-modal">',
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
                        '<div class="easyassist-customer-connect-modal-body">',
                            'A request will be sent to the customer and you will be connected with him/her on virtual meeting',
                            '<label id="easyassist-video-meeting-error"></label>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Request</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
        } else if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            meeting_modal_html = [
                '<div id="easyassist-voip-video-calling-request-modal" class="easyassist-customer-connect-modal eassyassist-custom-in-session-modal">',
                    '<div class="easyassist-customer-connect-modal-content">',
                        '<div class="easyassist-customer-connect-modal-header">',
                            '<h6>',
                                '<span class="easyassist-svg-wrapper" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">',
                                    '<svg width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                        '<path d="M13.7528 9.33678C12.7881 9.33678 11.8548 9.19851 10.9842 8.94962C10.8478 8.90887 10.7011 8.90282 10.561 8.93217C10.4209 8.96152 10.293 9.02507 10.192 9.11555L8.96064 10.4775C6.74103 9.54419 4.6626 7.78123 3.55672 5.75555L5.08613 4.60789C5.2979 4.41431 5.36064 4.14468 5.27437 3.90271C4.98417 3.1353 4.83515 2.31259 4.83515 1.46222C4.83515 1.08888 4.48221 0.777771 4.05868 0.777771H1.34495C0.921425 0.777771 0.411621 0.943697 0.411621 1.46222C0.411621 7.88493 6.47437 13.2222 13.7528 13.2222C14.3097 13.2222 14.5293 12.7867 14.5293 12.4064V10.0212C14.5293 9.64789 14.1763 9.33678 13.7528 9.33678Z" fill="white"/>',
                                    '</svg>',
                                '</span>',
                                'Voice Call',
                            '</h6>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-body default-text">',
                            'A request will be sent to the customer and once they accept the request you will be connected with them over a voice call',
                            '<label id="easyassist-video-meeting-error"></label>',
                        '</div>',
                        '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Request</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
        } else if(EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {
            meeting_modal_html = [
                '<div id="easyassist-voip-video-calling-request-modal" class="easyassist-customer-connect-modal eassyassist-custom-in-session-modal">',
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
                        '<div class="easyassist-customer-connect-modal-body">',
                            'A request will be sent to the customer and you will be connected with him/her on virtual meeting',
                            '<label id="easyassist-video-meeting-error"></label>',
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

    function add_easyassist_capture_screenshot_modal() {
        var screenshot_modal_html = [
            '<div id="easyassist-capture-screenshot-request-modal" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>',
                            'Ready to capture screenshot?',
                        '</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body screenshot-capture-modal" style="min-height: unset !important;">',
                        'Select "Capture" below to capture a screenshot.',
                        '<label id="easyassist-capture-screenshot-error" style="margin: 1em -1em !important"></label>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                        '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_capture_screenshot_modal()" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                        '<button class="easyassist-modal-primary-btn" onclick="easyassist_capture_client_screenshot()"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Capture</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', screenshot_modal_html);
    }

    function show_easyassist_capture_screenshot_modal(){
        try {
            document.getElementById("easyassist-capture-screenshot-request-modal").style.display = "flex";
        } catch(err) {}
    }

    function hide_easyassist_capture_screenshot_modal(){
        try {
            document.getElementById("easyassist-capture-screenshot-request-modal").style.display = "none";
        } catch(err) {}
    }

    function add_easyassist_captured_screenshot_view_modal() {
        var screenshot_modal_html = [
            '<div id="easyassist-captured-screenshot-view-modal" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>',
                            'Captured Screenshots',
                        '</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body" style="min-height: unset !important;">',
                        '<label id="easyassist-captured-screenshot-view-error"></label>',
                        '<div id="easyassist-captured-screenshot-view-table-div" class="easyassist-table-responsive" style="display: none;">',
                            '<table>',
                                '<thead>',
                                    '<tr>',
                                      '<th>Name</th>',
                                      '<th>Time</th>',
                                      '<th style="text-align: center;">Download</th>',
                                    '</tr>',
                                '</thead>',
                                '<tbody id="easyassist-captured-screenshot-view-table-body">',
                                '</tbody>',
                            '</table>',
                        '</div>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button">',
                        '<button class="easyassist-modal-primary-btn" id="easyassist-captured-screenshot-view-button" onclick="hide_easyassist_captured_screenshot_view_modal()"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', screenshot_modal_html);
    }

    function show_easyassist_captured_screenshot_view_modal(){
        try {
            document.getElementById("easyassist-captured-screenshot-view-modal").style.display = "flex";
        } catch(err) {}
    }

    function hide_easyassist_captured_screenshot_view_modal(){
        try {
            document.getElementById("easyassist-captured-screenshot-view-modal").style.display = "none";
        } catch(err) {}
    }

    function add_easyassist_support_document_modal() {
        let support_document_style = "";

        if (!EASYASSIST_COBROWSE_META.is_mobile) {
            support_document_style = "width: 500px !important"
        }

        var screenshot_modal_html = [
            '<div id="easyassist-support-document-modal" class="easyassist-customer-connect-modal">',
                '<div class="easyassist-customer-connect-modal-content" style="' + support_document_style + '">',
                    '<div class="easyassist-customer-connect-modal-header">',
                        '<h6>',
                            'Support Document',
                        '</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body" style="min-height: unset !important;">',
                        '<label id="easyassist-support-document-error" style="margin: 1em -1em !important"></label>',
                        '<div id="easyassist-support-document-div" class="easyassist-table-responsive" style="display: none;">',
                            '<table>',
                                '<thead>',
                                    '<tr>',
                                      '<th>Document</th>',
                                      '<th>Your Message</th>',
                                      '<th style="text-align: center;">Action</th>',
                                    '</tr>',
                                '</thead>',
                                '<tbody>',
                                '</tbody>',
                            '</table>',
                        '</div>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer">',
                        '<button class="easyassist-modal-primary-btn" onclick="hide_easyassist_support_document_modal()"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                    '</div>',
                '</div>',
            '</div>',
        ].join('');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', screenshot_modal_html);
    }

    function show_easyassist_support_document_modal(){
        try {
            document.getElementById("easyassist-support-document-modal").style.display = "flex";
        } catch(err) {}
    }

    function hide_easyassist_support_document_modal(){
        try {
            document.getElementById("easyassist-support-document-modal").style.display = "none";
        } catch(err) {}
    }

    function add_easyassist_report_bug_modal(){

        var button_html = [
            '<button id="report_problem_icon" onclick="show_easyassist_report_bug_modal();" onmousedown="easyassist_capture_screenshot()" style="display: none;">',
                '<svg data-toggle="tooltip" title="" data-placement="left" data-original-title="Report a problem" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">',
                  '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />',
                '</svg>',
            '</button>',
        ].join('');

        var modal_html = [
            '<div id="easyassist-co-browsing-report-problem-modal-id" class="easyassist-customer-connect-modal" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                '<div class="easyassist-customer-connect-modal-content" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<div class="easyassist-customer-connect-modal-header" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<h6>Report an Issue</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body" style="padding: 1rem 0rem!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<div class="easyassist-customer-connect-modal-content-wrapper" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0" style="margin-bottom: 0px; padding-bottom: 5px !important;">',
                            '<textarea id="bug-description" aria-label="Describe your issue in detail. We will get back to you as soon as possible. Also, mention what are the steps we need to take to reproduce this issue?." autofocus="" placeholder="Describe your issue in detail. We will get back to you as soon as possible. Also, mention what are the steps we need to take to reproduce this issue?"',
                                'required="" rows="1"></textarea>',
                        '</div>',
                        // '<div class="easyassist-customer-connect-modal-content-wrapper" style="padding-bottom: 0px !important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                            '<div class="easyassist-checkbox-include-screenshot">',
                                '<label class="cam">',
                                  '<input type="checkbox" id="checkbox-include-screenshot-text" name="" value="" checked>',
                                  '<span class="checkmark"></span>',
                                  '<span class="easyassist-noselect">Include screenshot</span>',
                                '</label>',
                            '</div>',
                        // '</div>',
                        '<div class="easyassist-customer-connect-modal-content-wrapper" id="screen-capture-img-div" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                            '<div class="screen-capture-img-div">',
                                '<img class="easyassist-noselect" src="data:image/gif;base64,R0lGODlhLAEsAQAAACH5BAEAAAAALAAAAAAsASwBgwAAAL3I3Ft2p/T2+cjR4rK/1p2tymZ/rai20N7k7X+UunGIs9Pa55KkxFBtoent8wT/QE5a7cVZb979B0NxJEvzRFN1ZVv3hWN5pmv7xnN953v/BwaFQ2LReEQmlUtm0/mERqVTatV6xWa1W27X+wWHxWNy2XxGp9Vrdtv9hsflc3rdfsfn9Xt+3/8HDBQcJCw0PERMVFxkbHR8hIyUnKSstLzEzNTc5Oz0/AQNFR0lLTU9RU1VXWVtdX2FjZWdpa21vcXN1d3l7fX9BQ4WHiYuNj5GTlZeZm52foaOlp6mrra+xs7W3ubu9v4GDxcfJy83P0dPV19nb3d/h4+Xn6evt7/Hz9ff5+/3/wcYUOBAggUNHkSYUOFChg0dPoT4kIACigrQBahoMUsDBx01TmDQ/7Ejgm4KRC7QskCkgQoFRDog0O1lgywDXsakYFLkA24hRQbIQuDlgAoHRB7ohuAlTywGTlpAEBUBUG46HSDNorIjy3MCRNIU8aBAg4oIcG5gEABBRgUIEnxIsLbs25dUJzxgkJeBBbx53wIgYKAsUw4E5FJ0CyCBXqKsErwsEOKB1ZdX/15wWbnygcsYCBjVfHVpBY4dUVaw2iAA6Mp2MawOLVpk51SZO9LeYDs2TAyUd+OWMMD3bqwUWHOlsFvz2QrClb8U4Mpq9A+lnwsgnPy5xwsDtG53AHaCTZHMAfgEf7r59+0fV3nl7kG3g8QDAsDfauGxgwUGCDB9QKmXLv+g7IAAmEqgANYccA2woSoQ8KUDEMjLqQHXk/BACRhQ8CWSWHkAMg/260gA2hLAr7i7EMiOAgs7guolBRqjAD0HaHtRRQkKbNA6B1p8MTwaJyDRgb1YCeClIzmYDjgfh+RAtwoewE+9lkSijoLvxJsAPy4niNCBCmz8cgIpW/HRAxs/tCBJkZbEYIC8CljrKQqsw643kdwDgLyOGiwSuDBROwrKCazjMxXWEsUAT0M3VPKCuIZ7Cbk+8bO0Avwio0Cona4ssVE7JQjxpwxYY1OVUkfywMsMbIQTANi2Y87Njlok8iXaItQRAKsYBeA7S3V7FIBVjWzF045ixaBI8yj/GHQ8SmMb0rpezbwwpz0twC/V8W7SNr4LbHWg2FKC9IBcXA/FUkvNDmjLLKusBIC1MtkVdwIRKTiWWQdFGrLbDKyjN5XvCsYgWgwWBRM6FgnNTztWFxbJWxtpIzfhUSXwMANhW/HTgUwzUFi/urrEEriTJaYPg34hbJe0bQn8qoKOuwOXFWV566BkmUtszMYGIf2UZW8nyBhiBxJFFYOV9a3YswdZCdNcmGe7gMyGAb4gRwsq1TNfCQTmN1ILbGzxJYQT+O5ataTyV1apzHpt7qH/mPcDrStAEUsaw2xxspm+LnRKyjItMtadH+XVggW5nKiye1vDAL+WL1hw5D8k/5y7c7hRjjq4AixnTrcF/mLAxz8tYE+BvwhQnWdsRbLgRYR9rbmCIB0QgCLLTR2zMuCKRJavyp71w0bw7AqTd4o085b453Cd7zkof2V9pcpF4pSCAX5XDtcws6yAXDEv2LlcQprfLjv2Yus+3O2uDRY8/rgN/dvyJNVVUvBPOgrNZmYBHwErSLfrw7RiQ74+KfAAcfNObASTO/287yvHmZLZJrCzddmGgfzyjQAaILiO3Mty8TPOzbKnPULQyXMvjMrdUseaBTQAed5DwHcUUACevI1CGRhAAeZlAJ7MLVYBkgqUGDA3DCwxhhzQC4ByBqG5rQsAnbNi5+JWEK9FhP8G5LqbF0XQgAMY4IhhQqAYQbAgeClgQbyzoho/cKzdmEiOJzBfaBpgtTt2YACGUQB74MXDPhbSkIdEZCIVuUhGNtKRj4RkJCU5yStMBlhXkBMD+AgN87kOaUv7gk+YssQtNoMjvdNKngDAkaNlASMfMckNnWGUD+2HU0Yp5RY6sslklGpJJiFJqTr1K8JMBD6960wBdHiWBDQAPgvYIkbsQpYjCUcBPJnMophDkbcEQCsVmYabUgiUJH3klAZAgFGKc8rnXWUCJpmQAYwCFjc1oE4/0tiHfPIhl2jETb67FalgBAB5XoUimmMGRz7iEgEQhZUSUMoeg+OVIyWARp7/kkA5oQWUkCyAMMDMpwRAwxWjUOUBhCHPkTS6I9lNY54MgN3q6oWsEB1gSCaBE0wRwBGsKIVRRumMUlp5npYlySsWEYqOFhOVgK7ycgDYZTXoyDuTDrR6n0rAcMDiqQM0gJCK2U0YQ4KA793ofiahygCcuZkJ4BJSaWSGm6RCABqt1CT29BxRwxOAvaB1g+whST9faMWQoFNkUP2ROy+1tAJoMqICPd8VD1sNhYrqQzjFgEri19Qa6USyQ22iaBpaP5ASFJTvZFBGT4s7WTaDlhQ70l2nRJSBSsAlWMmL93gHgNs2J44k4pRORou7Je2HKQ/lWPGm4csLCFO14SHA/xJVwhOPcEgrYHFKA94iOJaUSgF8FWJqM9CR4giITSZZAAEwQt62KreEHIpjMsQ5rtWalq32LZFXqBI75NynMnYcr3IFdNHNhAey8lNfNPACHGMxIHAuDEBnnEjXxdBILDFskX2i0lgowklOtEHigfDClA97722tpWSKVbxiFrfYxS+GcYxlPGMa19jGN8ZxjnW8Yx732Mc/BnKQhTxkIhfZyEdGcpKVvGQmN9nJT4ZylKU8ZSpX2cpXxnKWtbxlLnfZy18Gc5jFPGYyl9nMZ0ZzmtW8Zja32c1vhnOc5TxnOtfZznfGc571vGc+99nPfwZ0oAU9aEIX2tCHRnSiFRa9aEY32tGPhnSkJT1pSlfa0pe2RAQAADs=">',
                            '</div>',
                        '</div>',
                        '<p id="easyassist-report-bug-error"></p>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<div style="padding-top: 1em;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<button class="easyassist-modal-cancel-btn easyassist-click-element" onclick="hide_easyassist_report_bug_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">Cancel</button>',
                        '<button class="easyassist-modal-primary-btn easyassist-click-element" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" onclick="easyassist_report_bug(this);">Submit</button>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', modal_html);
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', button_html);
    }

    function show_easyassist_report_bug_modal(){
        try {
            document.getElementById("easyassist-co-browsing-report-problem-modal-id").style.display = "flex";
        } catch(err) {}
    }

    function hide_easyassist_report_bug_modal(){
        try {
            document.getElementById("easyassist-co-browsing-report-problem-modal-id").style.display = "none";
            var error_element = document.getElementById("easyassist-report-bug-error")
            error_element.innerHTML = ""
            error_element.style.color = "red";
            var bug_description_element = document.getElementById("bug-description");
            bug_description_element.value = "";
        } catch(err) {}
    }

    function add_easyassist_invite_agent_modal() {
        var modal_html = [ 
            '<div id="easyassist-invite-agent-modal" class="easyassist-customer-connect-modal" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                '<div class="easyassist-customer-connect-modal-content" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<div class="easyassist-customer-connect-modal-header" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<h6>',
                            'Invite an Agent to this session',
                        '</h6>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-body" style="padding-top: 1.5em!important; min-height: 5em!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<div id="easyassist-invite-agent-list-div" class="easyassist-dropdown savedSearches">',
                            '<button id="easyassist-invite-agent-button" class="btn1">Select Agent</button>',
                            '<ul id="easyassist-invite-agent-list-content">',
                            '</ul>',
                        '</div>',
                        '<p id="easyassist-invite-agent-error" style="margin: 1em 0.1em !important;"></p>',
                    '</div>',
                    '<div class="easyassist-customer-connect-modal-footer" id="easyassist_request_meeting_button" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                        '<button class="easyassist-modal-cancel-btn easyassist-click-element" onclick="hide_easyassist_invite_agent_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">Cancel</button>',
                        '<button class="easyassist-modal-primary-btn easyassist-click-element" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" onclick="easyassit_share_cobrowsing_session(this)">Invite</button>',
                    '</div>',
                '</div>',
            '</div>'
        ].join('');

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', modal_html);

        document.getElementById("easyassist-invite-agent-button").addEventListener('click', function(){
            document.getElementById("easyassist-invite-agent-search-box").focus();
        });

        document.getElementById("easyassist-invite-agent-modal").addEventListener('click', function(e) {
            var button_element = document.getElementById("easyassist-invite-agent-button");
            var input_box = document.getElementById("easyassist-invite-agent-search-box");
            if(e.target == button_element) {
                toggle_easyassist_invite_agent_list();
            } else if(e.target.parentElement == button_element) {
                toggle_easyassist_invite_agent_list();
            } else {
                if(e.target != input_box){
                    document.getElementById("easyassist-invite-agent-list-content").style.display = "none";
                }
            }
        });

    }

    function show_easyassist_invite_agent_modal(){
        try {
            document.getElementById("easyassist-invite-agent-modal").style.display = "flex";
        } catch(err) {}
    }

    function hide_easyassist_invite_agent_modal(){
        try {
            document.getElementById("easyassist-invite-agent-button").innerHTML = "Select Agent";
            document.getElementById("easyassist-invite-agent-modal").style.display = "none";
        } catch(err) {}
    }

    function toggle_easyassist_invite_agent_list(){
        try {
            var agent_list_div = document.getElementById("easyassist-invite-agent-list-content");
            if(agent_list_div.style.display == "none"){
                agent_list_div.style.display = "block";
            }else{
                agent_list_div.style.display = "none";
            }
        } catch(err) {}
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

    function show_comments_textbox(element){
        document.getElementById("close-session-remarks-error").style.display = "none";
        document.getElementById("close-session-text-error").style.display = "none";
        document.getElementById("easyassist-close-session-remarks").removeAttribute("disabled");
        setTimeout(function () {
            document.getElementById("easyassist-close-session-remarks").focus();
        }, 100);
    }

    function set_remarks_in_textbox(element) {
        document.getElementById('easyassist-close-session-remarks').value = element.innerHTML;
        var button_list = easyassist_get_eles_by_class_name("predefined-remarks-button")
        for(let index=0; index < button_list.length ; index++){
            button_list[index].classList.remove("predefined-remarks-button-clicked")
        }
        element.classList.add('predefined-remarks-button-clicked');
        document.getElementById("close-session-text-error").style.display = "none";
    }

    function get_color_with_alpha(color, alpha) {
        var R = parseInt(color.substring(1,3),16);
        var G = parseInt(color.substring(3,5),16);
        var B = parseInt(color.substring(5,7),16);

        return 'rgba(' + R +', ' + G +', ' + B + ', ' + alpha + ')';
    }

    function add_floating_button_color_to_class(){
        var root_style = ['<style>',
            ':root {',
                '--easyassist_color_rgb:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + ';',
                '--easyassist_font_family:' + EASYASSIST_COBROWSE_META.easyassist_font_family + ';',
            '}',
            '</style>',
        ].join('')

        var style_to_elements = ['<style>',
            '.predefined-remarks-button {',
                'color: var(--easyassist_color_rgb) !important;',
            '}',
            '.predefined-remarks-button-clicked {',
                'background-color: var(--easyassist_color_rgb) !important;',
                'color: #fff !important;',
            '}',
            '#easyassist-invite-agent-modal .easyassist-dropdown ul li:hover:not(:first-child){',
                'background-color: var(--easyassist_color_rgb) !important;',
                'color: #fff !important;',
            '}',
            '.ea-theme-bg{',
                'background-color: var(--easyassist_color_rgb) !important;',
                'color: #fff !important;',
            '}',
            '.ea-theme-color{',
                'color: var(--easyassist_color_rgb) !important;',
            '}',
            '.easyassist-checkbox-include-screenshot .cam input:checked~.checkmark {',
                'color: var(--easyassist_color_rgb) !important;',
                'background-color: var(--easyassist_color_rgb) !important;',
                'border-color: var(--easyassist_color_rgb) !important;',
            '}',
        '</style>'].join('')

        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', root_style + style_to_elements);
    }

    function add_easyassist_feedback_form() {
        if(window.EASYASSIST_COBROWSE_META.enable_predefined_remarks == true){

            var predefined_subremarks_html = "";
            var label_html = "";
            if(EASYASSIST_COBROWSE_META.enable_predefined_subremarks) {
                if(EASYASSIST_COBROWSE_META.predefined_remarks_optional) {
                    label_html += [
                        '<label for="easyassist-close-session-subremarks" style="margin-bottom:10px !important;">',
                            'Sub-Remarks',
                        '</label>'
                    ].join('');
                } else {
                    label_html += [
                        '<label for="easyassist-close-session-subremarks" style="margin-bottom:10px !important;">',
                            'Sub-Remarks<sup style="color: red;">*</sup>',
                        '</label>'
                    ].join('');
                }

                predefined_subremarks_html += [
                    '<div class="easyassist-subremarks-container" style="display: none">',
                        label_html,
                        '<div>',
                            '<select id="easyassist-close-session-subremarks">',
                                '<option value="None">None</option>',
                            '</select>',
                        '</div>',
                    '</div>',
                ].join('');

            }

            var dropdown_option_html = "";
            label_html = "";

            if(EASYASSIST_COBROWSE_META.predefined_remarks_optional) {
                label_html += [
                    '<label for="easyassist-close-session-remarks" style="margin-bottom:10px !important;">',
                        'Remarks',
                    '</label>'
                ].join('');
            } else {
                label_html += [
                    '<label for="easyassist-close-session-subremarks" style="margin-bottom:10px !important;">',
                        'Remarks<sup style="color: red!important;">*</sup>',
                    '</label>'
                ].join('');
            }

            var predefined_remarks = window.EASYASSIST_COBROWSE_META.predefined_remarks;
            for(let index=0 ; index < predefined_remarks.length ; index++){
                dropdown_option_html += '<option value="' + predefined_remarks[index].remark + '">' + predefined_remarks[index].remark + '</option>'
            }
            dropdown_option_html += '<option value="others">Others</option>';

            let remarks_text_area = '<textarea id="easyassist-close-session-remarks" class="easyassist-feedbackComments" property="comment" cols="30" rows="5" disabled></textarea>';

            if(EASYASSIST_COBROWSE_META.predefined_remarks_optional) {
                remarks_text_area = '<textarea id="easyassist-close-session-remarks" class="easyassist-feedbackComments" property="comment" cols="30" rows="5"></textarea>';
            }

            var predefined_remarks_html = [
                label_html,
                '<div>',
                    '<select id="close-session-remarks" onchange="show_comments_textbox(this)">',
                        dropdown_option_html,
                    '</select>',
                '<div>',
            ].join('');

            let add_easyassist_feedback_form = [
                '<div id="easyassist-co-browsing-feedback-modal" class="easyassist-customer-feedback-modal" style="display: none;">',
                    '<div class="easyassist-customer-feedback-modal-content" style="width: 430px !important">',
                        '<div class="easyassist-customer-feedback-modal-header">',
                            '<h6 style="padding-bottom: 1em!important;width:100%; cursor:pointer">Ready to end the session?</h6>',
                        '</div>',
                        '<div class="easyassist-customer-feedback-modal-body">',
                            '<label style="margin-bottom:15px !important;">',
                                '<div class="easyassist-checkbox-btn-container-item">',
                                    '<input type="checkbox" id="easyassist-mask-successfull-cobrowsing-session" checked>',
                                    '<label for="easyassist-mask-successfull-cobrowsing-session">',
                                        '<span>' + EASYASSIST_COBROWSE_META.lead_conversion_checkbox_text + '</span>',
                                    '</label>',
                                '</div>',
                            '</label>',
                            '<br>',
                            predefined_remarks_html,
                            '<br>',
                            predefined_subremarks_html,
                            '<span class="close-session-error" id="close-session-remarks-error" style="margin-left: 1em;"></span>',
                            '<div style="margin-top:20px;">',
                                '<label for="easyassist-close-session-remarks" style="margin-bottom:10px !important;">Comments</label>',
                                remarks_text_area,
                                '<span class="close-session-error" id="close-session-text-error"></span>',
                            '</div>',
                            '<div style="margin: 1rem 0 0 0;">',
                            '<span class="modal-end-session-text">Click on "End Session" to close the session</span>',
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-feedback-modal-footer">',
                            '<button class="easyassist-modal-cancel-btn" id="easyassist-feedback-nothanks-btn" onclick="hide_easyassist_feedback_form()" type="button" data-dismiss="easyassist-modal">',
                                'Cancel',
                            '</button>',
                            '<button class="easyassist-modal-primary-btn" id="easyassist-feedback-submit-button" onclick="submit_agent_feedback(\'feedback\')">',
                                'End Session',
                            '</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
            document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form);
            document.getElementById("close-session-remarks").selectedIndex = -1;

            new EasyassistCustomSelect(
                "#close-session-remarks",
                "Select One",
                EASYASSIST_COBROWSE_META.floating_button_bg_color);

            var close_session_subremarks_element = document.getElementById("easyassist-close-session-subremarks");
            if(close_session_subremarks_element) {
                close_session_subremarks_element.selectedIndex = -1;
                new EasyassistCustomSelect(
                    "#easyassist-close-session-subremarks",
                    "Select one",
                    EASYASSIST_COBROWSE_META.floating_button_bg_color);

                document.getElementById("close-session-remarks").addEventListener('change', function() {
                    var val = this.value;
                    let predefined_remarks = EASYASSIST_COBROWSE_META.predefined_remarks;
                    var subremark_list = [];
                    for(let idx = 0; idx < predefined_remarks.length; idx++) {
                        if (predefined_remarks[idx].remark == val) {
                            subremark_list = predefined_remarks[idx].subremark;
                            break;
                        }
                    }

                    var option_html = `<option value="None">None</option>`;
                    for(let idx = 0; idx < subremark_list.length; idx++) {
                        var ele = subremark_list[idx].remark;
                        option_html += `<option value="${ele}">${ele}</option>`;
                    }

                    var close_session_subremarks = document.getElementById("easyassist-close-session-subremarks");
                    close_session_subremarks.innerHTML = option_html;
                    close_session_subremarks.selectedIndex = -1;
                    close_session_subremarks.reinitialize();

                    close_session_subremarks.closest(".easyassist-subremarks-container").style.display = "";
                });
            }

        }else if(window.EASYASSIST_COBROWSE_META.enable_predefined_remarks_with_buttons == true){
            let predefined_remarks = window.EASYASSIST_COBROWSE_META.predefined_remarks_with_buttons;
            var drop_down = '<ul id="predefined-remarks-buttons-list">';
            for(let index=0 ; index < predefined_remarks.length ; index++){
                drop_down += '<li class="predefined-remarks-list-item">'
                drop_down += '<button class="btn predefined-remarks-button" onclick="set_remarks_in_textbox(this)">' + predefined_remarks[index] + '</button>'
                drop_down += '</li>'
            }
            drop_down += '</ul>'

            let add_easyassist_feedback_form = [
                '<div id="easyassist-co-browsing-feedback-modal" class="easyassist-customer-feedback-modal" style="display: none;">',
                    '<div class="easyassist-customer-feedback-modal-content" style="width: 430px !important">',
                        '<div class="easyassist-customer-feedback-modal-header">',
                            '<h6 style="padding-bottom: 1em!important;width:100%; cursor:pointer">Ready to end the session?</h6>',
                        '</div>',
                        '<div class="easyassist-customer-feedback-modal-body">',
                            '<label style="margin-bottom:15px !important;">',
                                '<div class="easyassist-checkbox-btn-container-item">',
                                    '<input type="checkbox" id="easyassist-mask-successfull-cobrowsing-session" checked>',
                                    '<label for="easyassist-mask-successfull-cobrowsing-session">',
                                        '<span>' + EASYASSIST_COBROWSE_META.lead_conversion_checkbox_text + '</span>',
                                    '</label>',
                                '</div>',
                            '</label>',
                            '<br>',
                            label_html,
                            '<textarea id="easyassist-close-session-remarks" class="easyassist-feedbackComments" property="comment" cols="30" rows="5" placeholder="Remarks"></textarea>',
                            '<span class="close-session-error" id="close-session-text-error"></span>',
                            '<label class="col-12 mt-3" style="margin: 0.5rem 0 !important;">Suggestions</label>',
                            drop_down,
                            '<div style="margin: 1rem 0 0 0;">',
                            '<span class="modal-end-session-text">Click on "End Session" to close the session</span>',
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-feedback-modal-footer">',
                            '<button class="easyassist-modal-cancel-btn" id="easyassist-feedback-nothanks-btn" onclick="hide_easyassist_feedback_form()" type="button" data-dismiss="easyassist-modal">',
                                'Cancel',
                            '</button>',
                            '<button class="easyassist-modal-primary-btn" id="easyassist-feedback-submit-button" onclick="submit_agent_feedback(\'feedback\')">',
                                'End Session',
                            '</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
            document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form);

            document.getElementById("easyassist-close-session-remarks").addEventListener("keyup", function(event) {
                var input_text = event.target.value;
                let predefined_remarks_list = document.getElementById("predefined-remarks-buttons-list").children;
                for(let idx = 0; idx < predefined_remarks_list.length; idx ++) {
                  var predefined_remarks = predefined_remarks_list[idx];
                  var button_element = predefined_remarks.getElementsByTagName("button")[0];
                  if(button_element.innerHTML.toLowerCase().indexOf(input_text.toLowerCase()) >= 0){
                    predefined_remarks.style.display = "inline-block";
                  } else{
                    predefined_remarks.style.display = "none";
                  }
                  button_element.classList.remove("predefined-remarks-button-clicked")
                }
            });
            
            var button_list = easyassist_get_eles_by_class_name("predefined-remarks-button");
            for(let index=0 ; index<button_list.length ; index++){
                button_list[index].style.setProperty('background', get_color_with_alpha(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.07));
            }

        }else{
            let add_easyassist_feedback_form = [
                '<div id="easyassist-co-browsing-feedback-modal" class="easyassist-customer-feedback-modal" style="display: none;">',
                    '<div class="easyassist-customer-feedback-modal-content" style="width: 430px !important">',
                        '<div class="easyassist-customer-feedback-modal-header">',
                            '<h6 style="padding-bottom: 1em!important;width:100%; cursor:pointer">Ready to end the session?</h6>',
                        '</div>',
                        '<div class="easyassist-customer-feedback-modal-body">',
                            '<label style="margin-bottom:15px !important;">',
                                '<div class="easyassist-checkbox-btn-container-item">',
                                    '<input type="checkbox" id="easyassist-mask-successfull-cobrowsing-session" checked>',
                                    '<label for="easyassist-mask-successfull-cobrowsing-session">',
                                        '<span>' + EASYASSIST_COBROWSE_META.lead_conversion_checkbox_text + '</span>',
                                    '</label>',
                                '</div>',
                            '</label>',
                            '<br>',
                            label_html,
                            '<textarea id="easyassist-close-session-remarks" class="easyassist-feedbackComments" property="comment" cols="30" rows="5" placeholder="Remarks"></textarea>',
                            '<span class="close-session-error" id="close-session-text-error"></span>',
                            '<div style="margin: 1rem 0 0 0;">',
                            '<span class="modal-end-session-text">Click on "End Session" to close the session</span>',
                            '</div>',
                        '</div>',
                        '<div class="easyassist-customer-feedback-modal-footer">',
                            '<button class="easyassist-modal-cancel-btn" id="easyassist-feedback-nothanks-btn" onclick="hide_easyassist_feedback_form()" type="button" data-dismiss="easyassist-modal">',
                                'Cancel',
                            '</button>',
                            '<button class="easyassist-modal-primary-btn" id="easyassist-feedback-submit-button" onclick="submit_agent_feedback(\'feedback\')">',
                                'End Session',
                            '</button>',
                        '</div>',
                    '</div>',
                '</div>',
            ].join('');
            document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', add_easyassist_feedback_form);
        }

        document.getElementById("easyassist-feedback-submit-button").style.setProperty(
            'background-color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');
        document.getElementById("easyassist-feedback-nothanks-btn").style.setProperty(
            'color', EASYASSIST_COBROWSE_META.floating_button_bg_color, 'important');

        var css_root = document.querySelector(':root');
        css_root.style.setProperty(
            "--easyassist_theme_color", EASYASSIST_COBROWSE_META.floating_button_bg_color);
    }

    function add_easyassist_agent_joining_modal(){
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
                    '<button class ="easyassist-modal-primary-btn" onclick="hide_easyassist_agent_joining_modal(this)" style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important;" >OK</button>',
                '</div>',
            '</div>',
        ].join('');
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_reverse_create_navbar_menu_temp() {
        let div_modal = document.createElement("div");
        div_modal.id = "cobrowse-mobile-navbar-temp";
        div_modal.style.display = "none";
        div_modal.style.width = "100%";
        div_modal.className = `easyassist-custom-${EASYASSIST_COBROWSE_META.floating_button_position}-mobile-nav-bar_wrapper`;

        let sidenav_menu_html = `
        <div class="easyassist-custom-${EASYASSIST_COBROWSE_META.floating_button_position}-nav-bar" style="align-items: center;">
            <ul id="ul_items_temp">`;


        sidenav_menu_html += `
            <li class="closebtn1">
                <div>
                    <a href="javascript:void(0)" class="closebtn1">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12.3936 7.41289L8.44584 11.0199C7.85139 11.563 7.85139 12.4404 8.44584 12.9835L12.3936 16.5905C13.3538 17.4679 15 16.8412 15 15.6017V8.38776C15 7.14829 13.3538 6.53552 12.3936 7.41289Z" fill="#CBCACA"/>
                        </svg>
                    </a>
                </div>
            </li>`

        sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();show_sharable_link_dialog_box();">
                        <svg width="22" height="22" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve">
                            <g>
                                <g>
                                    <path fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124 c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90 0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59 C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806 l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90 C496,372.371,455.629,332,406,332z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"></path>
                                </g>
                            </g>
                            <g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g>
                        </svg>
                    </a>
                </div>
            </li>`

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">
                <a href="javascript:void(0)" id="easyassist-co-browsing-connect-button" onclick="easyassist_hide_dialog_modal();show_easyassist_feedback_form();hide_easyassist_livechat_iframe();">\
                    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 15px !important; height: 15px !important;">
                        <path d="M2.00029 0.317885L7.50014 5.8172L13 0.334549C13.1083 0.224379 13.2382 0.137874 13.3817 0.0805049C13.5251 0.0231361 13.6789 -0.0038486 13.8333 0.00125733C14.1363 0.0208622 14.4218 0.150057 14.6364 0.364719C14.8511 0.579381 14.9803 0.864835 14.9999 1.16778C15.0014 1.31673 14.9727 1.46444 14.9154 1.60194C14.8581 1.73944 14.7734 1.86387 14.6666 1.96768L9.15009 7.50032L14.6666 13.033C14.8833 13.2429 15.0033 13.5329 14.9999 13.8329C14.9803 14.1358 14.8511 14.4213 14.6364 14.6359C14.4218 14.8506 14.1363 14.9798 13.8333 14.9994C13.6789 15.0045 13.5251 14.9775 13.3817 14.9201C13.2382 14.8628 13.1083 14.7763 13 14.6661L7.50014 9.18345L2.01695 14.6661C1.90867 14.7763 1.7787 14.8628 1.63526 14.9201C1.49182 14.9775 1.33804 15.0045 1.18364 14.9994C0.875017 14.9833 0.583284 14.8535 0.364758 14.635C0.146231 14.4165 0.0164056 14.1248 0.00034112 13.8162C-0.00116684 13.6673 0.0276004 13.5195 0.0848979 13.382C0.142195 13.2445 0.226829 13.1201 0.333665 13.0163L5.85018 7.50032L0.316999 1.96768C0.213171 1.86247 0.131618 1.73741 0.0772107 1.59997C0.0228039 1.46253 -0.00333999 1.31554 0.00034112 1.16778C0.0199479 0.864835 0.149156 0.579381 0.363839 0.364719C0.578521 0.150057 0.864002 0.0208622 1.16698 0.00125733C1.32018 -0.00601838 1.47323 0.0183407 1.6166 0.0728159C1.75997 0.127291 1.89058 0.210715 2.00029 0.317885Z" fill="#D70000"></path>
                    </svg>
                </a>
            </div>
        </li>`

        sidenav_menu_html += `
        <li class="nexttabbtn">
            <div>
                <a href="javascript:void(0)" class="nexttabbtn">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2341 16.5873L15.6179 12.9779C16.1274 12.4344 16.1274 11.5564 15.6179 11.0129L12.2341 7.40354C11.411 6.53952 10 7.1527 10 8.39299V15.5979C10 16.8521 11.411 17.4653 12.2341 16.5873Z" fill="#CBCACA"/>
                    </svg>
                </a>
            </div>
        </li>
        </ul>
    </div>`

        div_modal.innerHTML = sidenav_menu_html
        document.getElementsByTagName("body")[0].appendChild(div_modal);
    }


    function easyassist_reverse_create_navbar_menu() {
        var div_model = document.createElement("div");
        div_model.id = "cobrowse-mobile-navbar"
        div_model.style.display = "none";
        div_model.style.width = "100%";
        div_model.className = `easyassist-custom-${EASYASSIST_COBROWSE_META.floating_button_position}-nav-bar_wrapper`;

        var sidenav_menu_html = `\
        <div class="easyassist-custom-${EASYASSIST_COBROWSE_META.floating_button_position}-nav-bar" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0" style="padding: 0px !important; width: 100%;">`

        sidenav_menu_html += '<div style="width: 100%; height: 100%; align-self: center;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">';
        sidenav_menu_html += '<ul id="ul_items">';

        sidenav_menu_html += `
        <li class="closebtn1">
            <div>
                <a id="previous_button" href="javascript:void(0)" class="closebtn1">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.3936 7.41289L8.44584 11.0199C7.85139 11.563 7.85139 12.4404 8.44584 12.9835L12.3936 16.5905C13.3538 17.4679 15 16.8412 15 15.6017V8.38776C15 7.14829 13.3538 6.53552 12.3936 7.41289Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                    </svg>
                </a>
            </div>
        </li>`

        if (EASYASSIST_COBROWSE_META.enable_screenshot_agent) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item active-item">
                    <a href="javascript:void(0)" onclick="show_easyassist_capture_screenshot_modal();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();">
                        <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17.9972 6.32756V3.13421C17.9972 2.57182 17.7742 2.03237 17.3771 1.63411C16.9801 1.23584 16.4413 1.01125 15.8789 1.00956L12.6855 1" stroke="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M17.9972 12.7015V15.8885C17.9972 16.4519 17.7733 16.9924 17.3749 17.3908C16.9764 17.7893 16.436 18.0131 15.8725 18.0131H12.6855" stroke="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M6.31162 1L3.11828 1.00956C2.55589 1.01125 2.01711 1.23584 1.62004 1.63411C1.22297 2.03237 0.999997 2.57182 1 3.13421V6.32756" stroke="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M6.31162 18.0131H3.12465C2.56116 18.0131 2.02074 17.7893 1.6223 17.3908C1.22385 16.9924 1 16.4519 1 15.8885V12.7015" stroke="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M10.5557 4.50183C10.9945 4.50183 11.4004 4.73023 11.6227 5.10213L12.0707 5.85176H13.2096C14.1968 5.85176 14.9971 6.63841 14.9971 7.6088V12.7448C14.9971 13.7152 14.1968 14.5018 13.2096 14.5018H5.78457C4.79736 14.5018 3.99707 13.7152 3.99707 12.7448V7.6088C3.99707 6.63841 4.79736 5.85176 5.78457 5.85176H6.9288L7.40982 5.08174C7.63491 4.72141 8.03421 4.50183 8.46438 4.50183H10.5557ZM9.49707 7.47365C8.13017 7.47365 7.02207 8.56286 7.02207 9.90648C7.02207 11.2501 8.13017 12.3393 9.49707 12.3393C10.864 12.3393 11.9721 11.2501 11.9721 9.90648C11.9721 8.56286 10.864 7.47365 9.49707 7.47365ZM9.49707 8.28459C10.4083 8.28459 11.1471 9.01074 11.1471 9.90648C11.1471 10.8022 10.4083 11.5284 9.49707 11.5284C8.5858 11.5284 7.84707 10.8022 7.84707 9.90648C7.84707 9.01074 8.5858 8.28459 9.49707 8.28459Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color} "/>
                        </svg>
                    </a>
                </div>
            </li>`

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item active-item">
                    <a href="javascript:void(0)" onclick="fetch_cobrowsing_meta_information();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();";>
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9.62372 3.6659C9.44222 4.10083 9.31086 4.56187 9.2367 5.04183L5.72917 5.04175C4.84321 5.04175 4.125 5.75996 4.125 6.64592V12.8334H8.25C8.59806 12.8334 8.8857 13.0921 8.93122 13.4276L8.9375 13.5209C8.9375 14.66 9.86095 15.5834 11 15.5834C12.1391 15.5834 13.0625 14.66 13.0625 13.5209C13.0625 13.1412 13.3703 12.8334 13.75 12.8334H17.875L17.876 11.245C18.381 10.9817 18.8436 10.6481 19.2507 10.2572L19.25 17.1876C19.25 18.8329 17.9162 20.1667 16.2708 20.1667H5.72917C4.08381 20.1667 2.75 18.8329 2.75 17.1876V6.64592C2.75 5.00056 4.08381 3.66675 5.72917 3.66675L9.62372 3.6659ZM15.125 0.916748C17.9095 0.916748 20.1667 3.17398 20.1667 5.95842C20.1667 8.74285 17.9095 11.0001 15.125 11.0001C12.3405 11.0001 10.0833 8.74285 10.0833 5.95842C10.0833 3.17398 12.3405 0.916748 15.125 0.916748ZM15.3227 3.28962L15.2592 3.34266L15.2062 3.40613C15.098 3.56243 15.098 3.77106 15.2062 3.92737L15.2592 3.99084L16.7677 5.50008H11.9167L11.8343 5.50747C11.6472 5.54142 11.4997 5.68894 11.4658 5.87603L11.4583 5.95842L11.4658 6.04081C11.4997 6.22789 11.6472 6.37541 11.8343 6.40936L11.9167 6.41675H16.7677L15.2592 7.92599L15.2062 7.98946C15.0825 8.1681 15.1002 8.41507 15.2592 8.57417C15.4183 8.73328 15.6653 8.75095 15.8439 8.62721L15.9075 8.57417L18.2371 6.23892L18.2674 6.19533L18.2987 6.13354L18.3181 6.07589L18.3314 6.00085L18.3333 5.95842L18.3308 5.90947L18.3181 5.84095L18.2905 5.76463L18.2519 5.69748L18.2101 5.64571L15.9075 3.34266L15.8439 3.28962C15.6877 3.18135 15.479 3.18135 15.3227 3.28962Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" />
                        </svg>
                    </a>
                </div>
            </li>`
        }

        if (EASYASSIST_COBROWSE_META.enable_invite_agent_in_cobrowsing) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item active-item">
                    <a href="javascript:void(0)" onclick="easyassist_get_list_of_support_agents();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();";>
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                            <path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                                <path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                        </svg>
                    </a>
                </div>
            </li>`
        }

        if (EASYASSIST_COBROWSE_META.allow_support_documents) {

            sidenav_menu_html += `
                <li class="cobrowse-icons">
                    <div class="menu-item active-item">
                        <a href="javascript:void(0)" onclick="easyassist_get_support_material();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();">
                            <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg" >
                                <path d="M7.5 0V6C7.5 6.82843 8.17157 7.5 9 7.5H15V16.5C15 17.3284 14.3284 18 13.5 18H1.5C0.671573 18 0 17.3284 0 16.5V1.5C0 0.671573 0.671573 0 1.5 0H7.5Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                                <path d="M8.625 0.375V6C8.625 6.20711 8.79289 6.375 9 6.375H14.625L8.625 0.375Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                            </svg>
                        </a>
                    </div>
                </li>`
        }

        if (EASYASSIST_COBROWSE_META.enable_chat_functionality) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item active-item">
                    <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();show_easyassist_livechat_iframe();hide_easyassist_feedback_form();";>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 24px !important; height: 24px !important;">
                            <path d="M12 4C16.4182 4 20 7.58119 20 11.9988C20 16.4164 16.4182 19.9976 12 19.9976C10.6877 19.9976 9.42015 19.6808 8.28464 19.0844L4.85231 19.9778C4.48889 20.0726 4.11752 19.8547 4.02287 19.4913C3.99359 19.379 3.99359 19.261 4.02284 19.1486L4.91592 15.7184C4.31776 14.582 4 13.3128 4 11.9988C4 7.58119 7.58173 4 12 4ZM13.0014 12.7987H9.40001L9.3186 12.8041C9.02573 12.8439 8.80001 13.0949 8.80001 13.3986C8.80001 13.7023 9.02573 13.9533 9.3186 13.9931L9.40001 13.9985H13.0014L13.0828 13.9931C13.3757 13.9533 13.6014 13.7023 13.6014 13.3986C13.6014 13.0949 13.3757 12.8439 13.0828 12.8041L13.0014 12.7987ZM14.6 9.99911H9.40001L9.3186 10.0046C9.02573 10.0443 8.80001 10.2953 8.80001 10.599C8.80001 10.9027 9.02573 11.1538 9.3186 11.1935L9.40001 11.199H14.6L14.6815 11.1935C14.9743 11.1538 15.2 10.9027 15.2 10.599C15.2 10.2953 14.9743 10.0443 14.6815 10.0046L14.6 9.99911Z" 
                            fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                        </svg>
                    </a>
                </div>
            </li>`
        }

        sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();revoke_easyassist_edit_access();" id="revoke-edit-access-button">
                        <svg width="26" height="26" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M26.5384 1.46154L26.3251 1.2602C24.3656 -0.484696 21.3606 -0.417579 19.4814 1.46154L18.1281 2.81405L25.1856 9.8701L26.5384 8.5185C28.4176 6.63939 28.4847 3.63441 26.7398 1.67486L26.5384 1.46154ZM16.6499 4.29218L23.7074 11.3497L22.4615 12.5956C21.1193 11.5958 19.4967 11.0112 17.749 11.0112C13.128 11.0112 9.38214 15.0977 9.38214 20.1387C9.38214 21.7615 9.77038 23.2855 10.4511 24.606L9.84894 25.2081C9.46283 25.5942 8.98265 25.8729 8.45587 26.0165L1.32219 27.962C0.541473 28.175 -0.17491 27.4584 0.0380027 26.6779L1.98357 19.5442C2.12723 19.0174 2.40588 18.5373 2.79198 18.151L16.6499 4.29218ZM6.31113 12.659L4.21943 14.7507L1.04701 14.7513C0.469396 14.7513 0.00115825 14.2831 0.00115825 13.7055C0.00115825 13.1279 0.469396 12.6596 1.04701 12.6596L6.31113 12.659ZM11.8891 7.08116L9.79732 9.17287L1.04701 9.17345C0.469396 9.17345 0.00115825 8.70521 0.00115825 8.12759C0.00115825 7.54999 0.469396 7.08173 1.04701 7.08173L11.8891 7.08116ZM15.3752 3.59495L17.4669 1.50325L1.04701 1.50384C0.469396 1.50384 0.00115825 1.97208 0.00115825 2.5497C0.00115825 3.12732 0.469396 3.59556 1.04701 3.59556L15.3752 3.59495ZM26.2425 20.2021C26.2425 15.9662 22.8088 12.5324 18.573 12.5324C14.3371 12.5324 10.9034 15.9662 10.9034 20.2021C10.9034 24.4379 14.3371 27.8716 18.573 27.8716C22.8088 27.8716 26.2425 24.4379 26.2425 20.2021ZM19.5609 20.2023L22.0288 17.7357C22.3011 17.4634 22.3011 17.0219 22.0288 16.7496C21.7565 16.4775 21.3151 16.4775 21.0428 16.7496L18.5749 19.2162L16.1082 16.7495C15.8359 16.4773 15.3944 16.4773 15.1221 16.7495C14.8498 17.0218 14.8498 17.4633 15.1221 17.7356L17.5885 20.202L15.1221 22.6668C14.8498 22.9391 14.8498 23.3806 15.1221 23.6527C15.3944 23.9252 15.8359 23.9252 16.1082 23.6527L18.5746 21.188L21.0425 23.6559C21.3148 23.9282 21.7562 23.9282 22.0285 23.6559C22.3008 23.3836 22.3008 22.9422 22.0285 22.6699L19.5609 20.2023Z"
                            fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>
                        </svg>
                    </a>
                </div>
            </li>`

        sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();show_sharable_link_dialog_box();">
                        <svg width="22" height="22" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve">
                            <g>
                                <g>
                                    <path fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124 c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90 0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59 C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806 l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90 C496,372.371,455.629,332,406,332z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"></path>
                                </g>
                            </g>
                            <g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g>
                        </svg>
                    </a>
                </div>
            </li>`

        if (EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" id="show-voip-modal-btn" onclick="easyassist_hide_dialog_modal();show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();">\
                    <svg width="21" height="22" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                    </svg>\
                    </a>\
                </div>\
            </li>`
        } else if (EASYASSIST_COBROWSE_META.enable_voip_calling) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" id="show-voip-modal-btn" onclick="easyassist_hide_dialog_modal();show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();">\
                      <svg width="21" height="22" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-call-icon">\
                        <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                      </svg>\
                      <svg width="19" height="19" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-calling-icon" style="display: none;">\
                        <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                        <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                      </svg>\
                    </a>\
                </div>\
            </li>`
        } else if (EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" id="show-voip-modal-btn" onclick="easyassist_hide_dialog_modal();show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();">\
                      <svg width="21" height="22" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}"/>\
                      </svg>\
                    </a>\
                </div>\
            </li>`
        }

        if (EASYASSIST_COBROWSE_META.enable_cobrowsing_annotation) {

            sidenav_menu_html += `
            <li class="cobrowse-icons">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();easyassist_activate_canvas(this);hide_easyassist_feedback_form();" id="easyassist-toggle-canvas-btn">\
                      <svg width="20" height="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="${EASYASSIST_COBROWSE_META.floating_button_bg_color}">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path>
                    </svg>
                    </a>\
                </div>\
                <span style="display: none;" id="easyassist-toggle-canvas-label">Enter Drawing Mode</span>\
            </li>`
        }

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">
                <a href="javascript:void(0)" id="easyassist-co-browsing-connect-button" onclick="easyassist_hide_dialog_modal();show_easyassist_feedback_form();hide_easyassist_livechat_iframe();">\
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
                <a id="next_button" href="javascript:void(0)" class="nexttabbtn">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.2341 16.5873L15.6179 12.9779C16.1274 12.4344 16.1274 11.5564 15.6179 11.0129L12.2341 7.40354C11.411 6.53952 10 7.1527 10 8.39299V15.5979C10 16.8521 11.411 17.4653 12.2341 16.5873Z" fill="#4D4D4D"/>
                    </svg>
                </a>
            </div>
        </li>`

        sidenav_menu_html += `
            </ul>
        </div>
    </div>`

        div_model.innerHTML = sidenav_menu_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function update_navbar_buttons() {
        let ul_items_element = document.getElementById("ul_items")
        let scroll_left = ul_items_element.scrollLeft
        let window_width = window.innerWidth - 80

        if (ul_items_element.scrollWidth <= 0) {
            return;
        }
    
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

    function add_sidenav_floating_menu() {
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

                easyassist_reverse_create_navbar_menu();
                easyassist_reverse_create_navbar_menu_temp();

                let window_innerwidth = window.innerWidth;
                let options_width = window_innerwidth - 80;
                let icon_width = options_width / 3;
                let display_flex_counter = 0;

                let cobrowse_icons = document.getElementsByClassName('cobrowse-icons');
                document.getElementById('ul_items').style.width = options_width;
                document.getElementById('ul_items_temp').style.width = options_width;

                for (let i = 0; i < cobrowse_icons.length; i++) {
                    cobrowse_icons[i].style.width = icon_width + "px";
                    if (cobrowse_icons[i].style.display != "none") {
                        display_flex_counter += 1;
                    }
                }

                document.getElementById("ul_items").addEventListener("scroll", update_navbar_buttons);

                const easyassist_navbar_observer = new MutationObserver(function (mutations, observer) {
                    update_navbar_buttons();
                })
    
                easyassist_navbar_observer.observe(document.getElementById("ul_items"), { attributes: true, subtree: true })

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

            } else {
                sidenav_menu = '<div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar_wrapper" id="easyassist-sidenav-menu-id" style="display:none;">\
                <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar" id="easyassist-maximise-sidenav-button">\
                    <a href="javascript:void(0)" onclick="easyassist_show_dialog_modal();">\
                    <svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M1.93418 -5.07244e-07L6.76934 5L11.6045 -8.45407e-08L13.5386 1L6.76934 8L0.000113444 0.999999L1.93418 -5.07244e-07Z"\
                        fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                    </svg>\
                    </a>\
                </div>';
            }
        } else {
            sidenav_menu = '\
                        <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar_wrapper" id="easyassist-sidenav-menu-id" style="display:none;' + sidenav_style + '">\
                        <div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar" id="easyassist-sidenav-submenu-id" onmouseover="on_easyassist_client_mouse_over_nav_bar(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                            <a href="javascript:void(0)" onclick="close_easyassist_sidenav();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="on_easyassist_mouse_out_nav_bar(this)">'

            if (EASYASSIST_COBROWSE_META.floating_button_position == "top" ||
                EASYASSIST_COBROWSE_META.floating_button_position == "bottom") {

                sidenav_menu += '<svg class="minimize-icon-rotate" width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">';
            } else {
                sidenav_menu += '<svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">';
            }

            sidenav_menu += '<path d="M11.6044 8L6.76923 3L1.93407 8L-4.37114e-08 7L6.76923 -2.95892e-07L13.5385 7L11.6044 8Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                            </svg>\
                            <label style="background-color:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                                <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                                </svg>\
                                <span>Minimise</span>\
                            </label>\
                            </a>';


            if(EASYASSIST_COBROWSE_META.enable_screenshot_agent) {
                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" onclick="show_easyassist_capture_screenshot_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M17.9972 6.32756V3.13421C17.9972 2.57182 17.7742 2.03237 17.3771 1.63411C16.9801 1.23584 16.4413 1.01125 15.8789 1.00956L12.6855 1" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\
                    <path d="M17.9972 12.7015V15.8885C17.9972 16.4519 17.7733 16.9924 17.3749 17.3908C16.9764 17.7893 16.436 18.0131 15.8725 18.0131H12.6855" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\
                    <path d="M6.31162 1L3.11828 1.00956C2.55589 1.01125 2.01711 1.23584 1.62004 1.63411C1.22297 2.03237 0.999997 2.57182 1 3.13421V6.32756" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\
                    <path d="M6.31162 18.0131H3.12465C2.56116 18.0131 2.02074 17.7893 1.6223 17.3908C1.22385 16.9924 1 16.4519 1 15.8885V12.7015" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\
                    <path d="M10.5557 4.50183C10.9945 4.50183 11.4004 4.73023 11.6227 5.10213L12.0707 5.85176H13.2096C14.1968 5.85176 14.9971 6.63841 14.9971 7.6088V12.7448C14.9971 13.7152 14.1968 14.5018 13.2096 14.5018H5.78457C4.79736 14.5018 3.99707 13.7152 3.99707 12.7448V7.6088C3.99707 6.63841 4.79736 5.85176 5.78457 5.85176H6.9288L7.40982 5.08174C7.63491 4.72141 8.03421 4.50183 8.46438 4.50183H10.5557ZM9.49707 7.47365C8.13017 7.47365 7.02207 8.56286 7.02207 9.90648C7.02207 11.2501 8.13017 12.3393 9.49707 12.3393C10.864 12.3393 11.9721 11.2501 11.9721 9.90648C11.9721 8.56286 10.864 7.47365 9.49707 7.47365ZM9.49707 8.28459C10.4083 8.28459 11.1471 9.01074 11.1471 9.90648C11.1471 10.8022 10.4083 11.5284 9.49707 11.5284C8.5858 11.5284 7.84707 10.8022 7.84707 9.90648C7.84707 9.01074 8.5858 8.28459 9.49707 8.28459Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Capture Screenshot</span>\
                  </label>\
                </a>';

                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" onclick="fetch_cobrowsing_meta_information();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path\
                      d="M9.62372 3.6659C9.44222 4.10083 9.31086 4.56187 9.2367 5.04183L5.72917 5.04175C4.84321 5.04175 4.125 5.75996 4.125 6.64592V12.8334H8.25C8.59806 12.8334 8.8857 13.0921 8.93122 13.4276L8.9375 13.5209C8.9375 14.66 9.86095 15.5834 11 15.5834C12.1391 15.5834 13.0625 14.66 13.0625 13.5209C13.0625 13.1412 13.3703 12.8334 13.75 12.8334H17.875L17.876 11.245C18.381 10.9817 18.8436 10.6481 19.2507 10.2572L19.25 17.1876C19.25 18.8329 17.9162 20.1667 16.2708 20.1667H5.72917C4.08381 20.1667 2.75 18.8329 2.75 17.1876V6.64592C2.75 5.00056 4.08381 3.66675 5.72917 3.66675L9.62372 3.6659ZM15.125 0.916748C17.9095 0.916748 20.1667 3.17398 20.1667 5.95842C20.1667 8.74285 17.9095 11.0001 15.125 11.0001C12.3405 11.0001 10.0833 8.74285 10.0833 5.95842C10.0833 3.17398 12.3405 0.916748 15.125 0.916748ZM15.3227 3.28962L15.2592 3.34266L15.2062 3.40613C15.098 3.56243 15.098 3.77106 15.2062 3.92737L15.2592 3.99084L16.7677 5.50008H11.9167L11.8343 5.50747C11.6472 5.54142 11.4997 5.68894 11.4658 5.87603L11.4583 5.95842L11.4658 6.04081C11.4997 6.22789 11.6472 6.37541 11.8343 6.40936L11.9167 6.41675H16.7677L15.2592 7.92599L15.2062 7.98946C15.0825 8.1681 15.1002 8.41507 15.2592 8.57417C15.4183 8.73328 15.6653 8.75095 15.8439 8.62721L15.9075 8.57417L18.2371 6.23892L18.2674 6.19533L18.2987 6.13354L18.3181 6.07589L18.3314 6.00085L18.3333 5.95842L18.3308 5.90947L18.3181 5.84095L18.2905 5.76463L18.2519 5.69748L18.2101 5.64571L15.9075 3.34266L15.8439 3.28962C15.6877 3.18135 15.479 3.18135 15.3227 3.28962Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color +'" />\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                    </svg>\
                    <span>View Screenshot</span>\
                  </label>\
                </a>';
            }

            if(EASYASSIST_COBROWSE_META.enable_invite_agent_in_cobrowsing) {
                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" onclick="easyassist_get_list_of_support_agents();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">\
                      <path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      <path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      <path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                    </svg>\
                    <span>Invite an Agent</span>\
                  </label>\
                </a>';
            }

            if(EASYASSIST_COBROWSE_META.allow_support_documents){
                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" onclick="easyassist_get_support_material();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg" >\
                    <path d="M7.5 0V6C7.5 6.82843 8.17157 7.5 9 7.5H15V16.5C15 17.3284 14.3284 18 13.5 18H1.5C0.671573 18 0 17.3284 0 16.5V1.5C0 0.671573 0.671573 0 1.5 0H7.5Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                    <path d="M8.625 0.375V6C8.625 6.20711 8.79289 6.375 9 6.375H14.625L8.625 0.375Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Documents</span>\
                  </label>\
                </a>';
            }

            if(EASYASSIST_COBROWSE_META.enable_chat_functionality && EASYASSIST_COBROWSE_META.enable_chat_bubble == false){
            sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" onclick="show_easyassist_livechat_iframe();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"\
                      d="M11 1.83325C16.0625 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0625 20.1666 11 20.1666C9.49628 20.1666 8.04388 19.8035 6.74278 19.12L2.80991 20.1439C2.39349 20.2525 1.96797 20.0028 1.85951 19.5863C1.82597 19.4576 1.82596 19.3224 1.85948 19.1936L2.8828 15.2626C2.19741 13.9602 1.83331 12.5058 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM12.1474 11.9166H8.02081L7.92752 11.9228C7.59195 11.9684 7.33331 12.256 7.33331 12.6041C7.33331 12.9521 7.59195 13.2398 7.92752 13.2854L8.02081 13.2916H12.1474L12.2407 13.2854C12.5763 13.2398 12.8349 12.9521 12.8349 12.6041C12.8349 12.256 12.5763 11.9684 12.2407 11.9228L12.1474 11.9166ZM13.9791 8.70825H8.02081L7.92752 8.71453C7.59195 8.76005 7.33331 9.04769 7.33331 9.39575C7.33331 9.74381 7.59195 10.0315 7.92752 10.077L8.02081 10.0833H13.9791L14.0725 10.077C14.408 10.0315 14.6666 9.74381 14.6666 9.39575C14.6666 9.04769 14.408 8.76005 14.0725 8.71453L13.9791 8.70825Z"\
                      fill="#2B2B2B" />\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Chat with the Customer</span>\
                  </label>\
                </a>';
            }

            if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" id="show-voip-modal-btn" onclick="show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Video Call</span>\
                  </label>\
                </a>';
            } else if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" id="show-voip-modal-btn" onclick="show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-call-icon">\
                    <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <svg width="19" height="19" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-calling-icon" style="display: none;">\
                    <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                    <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Voice Call</span>\
                  </label>\
                </a>';
            } else if(EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {
                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" id="show-voip-modal-btn" onclick="show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                  <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                  </svg>\
                  <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Video Call</span>\
                  </label>\
                </a>';
            }

            sidenav_menu += '<a href="javascript:void(0)" onclick="revoke_easyassist_edit_access();" id="revoke-edit-access-button" style="display:none;" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" fill-rule="evenodd" clip-rule="evenodd" d="M19.2778 2.72247L19.1376 2.59012C17.8495 1.4431 15.8741 1.48722 14.6388 2.72247L13.7492 3.61155L18.3885 8.24989L19.2778 7.36141C20.5131 6.12616 20.5572 4.15082 19.4102 2.8627L19.2778 2.72247ZM12.7775 4.58321L17.4168 9.22249L16.5978 10.0415C15.7155 9.3843 14.6489 9 13.5 9C10.4624 9 8 11.6863 8 15C8 16.0668 8.25521 17.0686 8.70266 17.9366L8.30685 18.3324C8.05304 18.5862 7.73739 18.7694 7.39111 18.8638L2.70173 20.1427C2.18852 20.2827 1.7176 19.8117 1.85756 19.2986L3.13649 14.6092C3.23093 14.2629 3.4141 13.9473 3.66791 13.6934L12.7775 4.58321ZM5.98125 10.0832L4.60625 11.4582L2.52084 11.4586C2.14114 11.4586 1.83334 11.1508 1.83334 10.7711C1.83334 10.3914 2.14114 10.0836 2.52084 10.0836L5.98125 10.0832ZM9.64795 6.41656L8.27292 7.79156L2.52084 7.79194C2.14114 7.79194 1.83334 7.48414 1.83334 7.10444C1.83334 6.72475 2.14114 6.41694 2.52084 6.41694L9.64795 6.41656ZM11.9396 4.12488L13.3146 2.74989L2.52084 2.75028C2.14114 2.75028 1.83334 3.05808 1.83334 3.43778C1.83334 3.81748 2.14114 4.12528 2.52084 4.12528L11.9396 4.12488ZM19.0833 15.0417C19.0833 12.2572 16.8261 10 14.0417 10C11.2572 10 9 12.2572 9 15.0417C9 17.8261 11.2572 20.0833 14.0417 20.0833C16.8261 20.0833 19.0833 17.8261 19.0833 15.0417ZM14.6911 15.0418L16.3134 13.4204C16.4924 13.2414 16.4924 12.9512 16.3134 12.7722C16.1344 12.5933 15.8442 12.5933 15.6652 12.7722L14.0429 14.3936L12.4214 12.7721C12.2424 12.5932 11.9522 12.5932 11.7732 12.7721C11.5942 12.9511 11.5942 13.2413 11.7732 13.4203L13.3945 15.0416L11.7732 16.6619C11.5942 16.8409 11.5942 17.1311 11.7732 17.31C11.9522 17.4891 12.2424 17.4891 12.4214 17.31L14.0427 15.6898L15.665 17.3121C15.844 17.4911 16.1342 17.4911 16.3132 17.3121C16.4922 17.1331 16.4922 16.8429 16.3132 16.6639L14.6911 15.0418Z" fill="#2B2B2B"/>\
                </svg>\
                <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Revoke edit access</span>\
                </label>\
            </a>\
            <a href="javascript:void(0)" onclick="show_sharable_link_dialog_box();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                <svg width="22" height="22" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve"><g><g>\
                    <path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124\
                        c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90\
                        c0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59\
                        C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806\
                        l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90\
                        C496,372.371,455.629,332,406,332z"/>\
                </g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g></svg>\
                <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    <span>Get Shareable link</span>\
                </label>\
            </a>'

            if(EASYASSIST_COBROWSE_META.enable_cobrowsing_annotation) {

                sidenav_menu += '<a href="javascript:void(0)" class="easyassist-option" onclick="easyassist_activate_canvas(this);" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)" id="easyassist-toggle-canvas-btn">\
                    <svg width="20" height="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />\
                      </svg>\
                    <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                          </svg>\
                        <span id="easyassist-toggle-canvas-label">Enter Drawing Mode</span>\
                    </label>\
                </a>';
            }

            sidenav_menu += '<hr style="color: black;width: 30px;margin: 0.3em auto;border: 0;border-top: 1px solid rgba(0,0,0,.1);">\
            <a href="javascript:void(0)" onclick="show_easyassist_feedback_form();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
               <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">\
                 <path fill="#D70000" d="M11 1.83325C16.0626 1.83325 20.1666 5.93731 20.1666 10.9999C20.1666 16.0625 16.0626 20.1666 11 20.1666C5.93737 20.1666 1.83331 16.0625 1.83331 10.9999C1.83331 5.93731 5.93737 1.83325 11 1.83325ZM14.2361 7.76378L14.159 7.69722C13.9198 7.51971 13.5914 7.51751 13.35 7.69064L13.2638 7.76378L11 10.0273L8.73612 7.76378L8.65901 7.69722C8.41977 7.51971 8.0914 7.51751 7.84997 7.69064L7.76384 7.76378L7.69728 7.84089C7.51977 8.08013 7.51757 8.40849 7.6907 8.64993L7.76384 8.73605L10.0274 10.9999L7.76384 13.2638L7.69728 13.3409C7.51977 13.5801 7.51757 13.9085 7.6907 14.1499L7.76384 14.2361L7.84095 14.3026C8.08019 14.4801 8.40855 14.4823 8.64999 14.3092L8.73612 14.2361L11 11.9725L13.2638 14.2361L13.341 14.3026C13.5802 14.4801 13.9086 14.4823 14.15 14.3092L14.2361 14.2361L14.3027 14.1589C14.4802 13.9197 14.4824 13.5913 14.3093 13.3499L14.2361 13.2638L11.9726 10.9999L14.2361 8.73605L14.3027 8.65895C14.4802 8.41971 14.4824 8.09134 14.3093 7.8499L14.2361 7.76378L14.159 7.69722L14.2361 7.76378Z">\
               </svg>\
               <label style="background:#D70000 !important">\
                    <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="#D70000"/>\
                      </svg>\
                    <span>End Session</span>\
               </label>\
             </a>\
          </div>'

            sidenav_menu += '<div class="easyassist-custom-' + EASYASSIST_COBROWSE_META.floating_button_position + '-nav-bar" id="easyassist-maximise-sidenav-button" style="display:none;">\
                    <a href="javascript:void(0)" onclick="open_easyassist_sidenav();" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">';

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
            </div>';

            }

        sidenav_menu += '</div>';

        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            sidenav_menu += '\
                <div id="easyassist-cobrowse-voip-container" style="display: none;">\
                    <button class="easyassist-client-meeting-mic-btn" id="easyassist-client-meeting-mic-on-btn" type="button" onclick="toggle_client_voice(this, true)" style="display: none;" onmouseover="easyassist_change_tooltipshow(this)" onmouseout="easyassist_change_tooltiphide(this)">\
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M1.33597 0.721564C1.16629 0.55188 0.891186 0.551878 0.721503 0.721557C0.551819 0.891237 0.551816 1.16635 0.721496 1.33603L4.07021 4.68481V6.38759C4.07021 7.66741 5.10771 8.70491 6.38753 8.70491C6.87038 8.70491 7.31874 8.55723 7.6899 8.30457L8.35376 8.96844C7.84603 9.34868 7.2155 9.5739 6.53236 9.5739H6.2427L6.11733 9.57136C4.4957 9.50562 3.20122 8.17019 3.20122 6.53242V6.24276L3.19725 6.1838C3.16848 5.97172 2.98669 5.80826 2.76672 5.80826C2.52676 5.80826 2.33223 6.00279 2.33223 6.24276V6.53242L2.33458 6.66934C2.40339 8.66902 3.9736 10.2874 5.95304 10.4323L5.95303 11.7464L5.957 11.8053C5.98577 12.0174 6.16756 12.1809 6.38753 12.1809C6.62749 12.1809 6.82203 11.9864 6.82203 11.7464L6.82259 10.4323C7.63306 10.3728 8.3749 10.0663 8.97313 9.58783L11.439 12.0537C11.6086 12.2234 11.8837 12.2234 12.0534 12.0537C12.2231 11.884 12.2231 11.6089 12.0534 11.4392L1.33597 0.721564ZM7.05738 7.67204C6.85706 7.77672 6.62921 7.83591 6.38753 7.83591C5.58764 7.83591 4.93921 7.18748 4.93921 6.38759V5.55382L7.05738 7.67204Z" fill="white"/>\
                          <path d="M7.83585 2.91162V5.9926L8.66436 6.82113C8.69094 6.68069 8.70484 6.53576 8.70484 6.38759V2.91162C8.70484 1.6318 7.66735 0.594299 6.38753 0.594299C5.31701 0.594299 4.41603 1.32021 4.14997 2.30665L4.93921 3.0959V2.91162C4.93921 2.11173 5.58764 1.46329 6.38753 1.46329C7.18742 1.46329 7.83585 2.11173 7.83585 2.91162Z" fill="white"/>\
                          <path d="M9.39781 7.55459L10.0617 8.21848C10.306 7.70796 10.4428 7.13617 10.4428 6.53242V6.24276L10.4389 6.1838C10.4101 5.97172 10.2283 5.80826 10.0083 5.80826C9.76837 5.80826 9.57384 6.00279 9.57384 6.24276V6.53242L9.5713 6.65779C9.55859 6.97128 9.49843 7.27254 9.39781 7.55459Z" fill="white"/>\
                      </svg>\
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
                      <label style="background:' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
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
        if(document.getElementById("easyassist-icon-path-1")){
            document.getElementById("easyassist-icon-path-1").style.fill = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        }

        easyassist_change_options_visiblity();
        easyassist_initialize_drag_element();
    }

    function easyassist_chat_bubble_css()
    {
        var css = `<style>
                    .bounce2 {
                        animation: bounce2 2s ;
                    }
                    
                    @keyframes bounce2 {
                        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
                        40% {transform: translateY(-40px);}
                        60% {transform: translateY(-25px);}
                    }

                    .bg-grey{
                        background: grey;
                    }
                    
                    #chat-minimize-icon-wrapper{
                        position: fixed;
                        right: 50px;
                        bottom: 50px;
                        cursor:pointer;
                        z-index: 200000;
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
                        box-shadow: 0px 8px 8px rgba(0, 32, 51, 0.04), 0px 12px 28px rgba(0, 32, 51, 0.12);
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
                        word-wrap: break-all;
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
                        border: 1px solid ${EASYASSIST_COBROWSE_META.floating_button_bg_color};
                        cursor: pointer;
                    }
                    
                    #chat-minimize-icon-wrapper .talk-bubble-icon {
                        display: block;
                        max-width: 247px;
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
                    
                    @media (max-width:440px) {
                        #chat-minimize-icon-wrapper .chat-talk-bubble {
                            max-width: 170px;
                        }
                    }
                    
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
                        cursor: pointer;
                    }
                    
                    #new-image-div{
                        border: 1px solid #2F80ED;
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
                        /* width: 10px; */
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        margin-bottom: 0;
                    }
                    /* open chat */
                    
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

                    /* close chat */
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
                        transform-origin: 15% 85%;
                        opacity: 1;
                        }
                    }
                                                
                </style>`;

            document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', css);
    }

    function easyassist_show_chat_bubble() {
        if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
        }
    }

    function easyassist_add_chat_bubble_body() {
        if(EASYASSIST_COBROWSE_META.is_mobile || EASYASSIST_COBROWSE_META.enable_chat_bubble == false)
            return

        let chat_bubble_style = ";";
        let icon_src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/" + EASYASSIST_COBROWSE_META.chat_bubble_icon_source

        if (EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            chat_bubble_style = "left:50px;"
        }

        var chat_bubble = `<div id="chat-minimize-icon-wrapper" class="chat-minimize-icon-wrapper easyassist-option" style="display: none; broder: 2px solid ${EASYASSIST_COBROWSE_META.floating_button_bg_color}!important;">
                            <div class="minimize-chat-box-div d-flex align-items-center justify-content-center" style="${chat_bubble_style}" onclick="show_easyassist_livechat_iframe()">`
        
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
            chat_bubble += `<div id="chat-talk-bubble" class="chat-talk-bubble tri-left border round btm-left-in" style="display:none; bottom:120px; left:135px;">`
        } else {
            chat_bubble += `<div id="chat-talk-bubble" class="chat-talk-bubble tri-right border round btm-right-in" style="display:none;">`
        }
        
        chat_bubble += `<div class="talktext" onclick="show_easyassist_livechat_iframe()">
                                <p id="talktext-p" class="mb-0"></p>
                            </div>
                            <div class="close-bubble-container" onclick='hide_chat_bubble_greeting_div()'">
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

    function easyassist_change_options_visiblity(){
        if(get_easyassist_cookie("ea_cust_connected") != "true"){
            var elements = easyassist_get_eles_by_class_name("easyassist-option");
            for(element of elements){
                element.style.display = "none";
            }
        } else {
            var elements = easyassist_get_eles_by_class_name("easyassist-option");
            for(element of elements){
                element.style.display = "";
            }
        }
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

    function easyassist_relocate_drag_element() {
        try {
            easyassist_drag_element.relocate_element();
        } catch(err) {
            console.log("easyassist_relocate_drag_element: ", err);
        }
    }

    function show_floating_sidenav_menu() {
        easyassist_change_options_visiblity();

        if(document.getElementById("cobrowse-mobile-modal").style.display == "flex") {
            return
        }

        if (EASYASSIST_COBROWSE_META.is_mobile && (EASYASSIST_COBROWSE_META.floating_button_position == "top" || EASYASSIST_COBROWSE_META.floating_button_position == "bottom")) {
            if (get_easyassist_cookie("ea_cust_connected") == "true") {
                document.getElementById("cobrowse-mobile-navbar-temp").style.display = "none";
                document.getElementById("cobrowse-mobile-navbar").style.display = "flex";
            } else {
                document.getElementById("cobrowse-mobile-navbar-temp").style.display = "flex";
            }
        } else {
            document.getElementById("easyassist-sidenav-menu-id").style.display = "block";
        }

        if(EASYASSIST_COBROWSE_META.is_mobile == true) {
            if (EASYASSIST_COBROWSE_META.floating_button_position == "left" || EASYASSIST_COBROWSE_META.floating_button_position == "right") {
                if (get_easyassist_cookie("easyassist_edit_access") == "true") {
                    document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "inherit";
                } else {
                    document.getElementById("revoke-edit-access-button").parentElement.parentElement.style.display = "none";
                }
            } else {
                if (get_easyassist_cookie("easyassist_edit_access") == "true") {
                    document.getElementById("revoke-edit-access-button").parentNode.parentNode.style.display = "none";
                } else {
                    document.getElementById("revoke-edit-access-button").parentNode.parentNode.style.display = "none";
                }
            }
        }else{
            if (get_easyassist_cookie("easyassist_edit_access") == "true") {
                document.getElementById("revoke-edit-access-button").style.display = "inherit";
            } else {
                document.getElementById("revoke-edit-access-button").style.display = "none";
            }
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
        try{
            document.getElementById("easyassist-sidenav-menu-id").style.display = "none";
        }catch(err){}
    }
    
    function hide_floating_mobile_sidenav_menu() {
        try{
            document.getElementById("cobrowse-mobile-navbar").style.display = "none";
        }catch(err){}
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
        try{
            easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
            if (easyassist_session_id == undefined || EASYASSIST_SESSION_ID == null) {
                document.getElementById("easyassist-side-nav-options-co-browsing").style.display = "inline-block";
            }
        }catch(err){}
    }

    function easyassisst_add_dialog_modal() {
        var div_model = document.createElement("div");
        div_model.id = "cobrowse-mobile-modal"
        div_model.style = "transition: opacity 1s ease-out;";
        div_model.style.display = "none";
        div_model.className = "easyassist-customer-connect-modal";

        var modal_html = [
            '<div class="easyassist-customer-connect-modal-content" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0" style="padding: 0px !important;">',
                '<div class="easyassist-customer-connect-modal-header" style="text-align: center; display: block !important; padding: 0.5rem 0.5rem 0 1rem!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<button type="button" id="mobile-modal-hide-btn" onclick="easyassist_hide_dialog_modal();" class="hide-modal-btn"><svg width="16" height="2" viewBox="0 0 16 2" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M15 2H1C0.734784 2 0.48043 1.89464 0.292893 1.70711C0.105357 1.51957 0 1.26522 0 1C0 0.734784 0.105357 0.48043 0.292893 0.292893C0.48043 0.105357 0.734784 0 1 0H15C15.2652 0 15.5196 0.105357 15.7071 0.292893C15.8946 0.48043 16 0.734784 16 1C16 1.26522 15.8946 1.51957 15.7071 1.70711C15.5196 1.89464 15.2652 2 15 2Z"',
                        'fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                        '</svg>',
                    '</button>',
                '</div>',
        ].join('');

        modal_html += '<div class="easyassist-customer-connect-modal-body" style="padding: 1rem 1.2rem!important;" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">';
        modal_html += '<ul class="menu-items">';

        if(EASYASSIST_COBROWSE_META.enable_screenshot_agent) {
            modal_html += [
                '<li class="easyassist-option">',
                    '<div class="menu-item active-item">',
                        '<a href="javascript:void(0)" onclick="show_easyassist_capture_screenshot_modal();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();";>',
                            '<svg width="26" height="26" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M17.9972 6.32756V3.13421C17.9972 2.57182 17.7742 2.03237 17.3771 1.63411C16.9801 1.23584 16.4413 1.01125 15.8789 1.00956L12.6855 1" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '<path d="M17.9972 12.7015V15.8885C17.9972 16.4519 17.7733 16.9924 17.3749 17.3908C16.9764 17.7893 16.436 18.0131 15.8725 18.0131H12.6855" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '<path d="M6.31162 1L3.11828 1.00956C2.55589 1.01125 2.01711 1.23584 1.62004 1.63411C1.22297 2.03237 0.999997 2.57182 1 3.13421V6.32756" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '<path d="M6.31162 18.0131H3.12465C2.56116 18.0131 2.02074 17.7893 1.6223 17.3908C1.22385 16.9924 1 16.4519 1 15.8885V12.7015" stroke="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
                                '<path d="M10.5557 4.50183C10.9945 4.50183 11.4004 4.73023 11.6227 5.10213L12.0707 5.85176H13.2096C14.1968 5.85176 14.9971 6.63841 14.9971 7.6088V12.7448C14.9971 13.7152 14.1968 14.5018 13.2096 14.5018H5.78457C4.79736 14.5018 3.99707 13.7152 3.99707 12.7448V7.6088C3.99707 6.63841 4.79736 5.85176 5.78457 5.85176H6.9288L7.40982 5.08174C7.63491 4.72141 8.03421 4.50183 8.46438 4.50183H10.5557ZM9.49707 7.47365C8.13017 7.47365 7.02207 8.56286 7.02207 9.90648C7.02207 11.2501 8.13017 12.3393 9.49707 12.3393C10.864 12.3393 11.9721 11.2501 11.9721 9.90648C11.9721 8.56286 10.864 7.47365 9.49707 7.47365ZM9.49707 8.28459C10.4083 8.28459 11.1471 9.01074 11.1471 9.90648C11.1471 10.8022 10.4083 11.5284 9.49707 11.5284C8.5858 11.5284 7.84707 10.8022 7.84707 9.90648C7.84707 9.01074 8.5858 8.28459 9.49707 8.28459Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '</svg>',
                        '</a>',
                    '</div>',
                    '<span>Capture Screenshot</span>',
                '</li>',
            ].join('');

            modal_html += [
                '<li class="easyassist-option">',
                    '<div class="menu-item active-item">',
                        '<a href="javascript:void(0)" onclick="fetch_cobrowsing_meta_information();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();";>',
                            '<svg width="26" height="26" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M9.62372 3.6659C9.44222 4.10083 9.31086 4.56187 9.2367 5.04183L5.72917 5.04175C4.84321 5.04175 4.125 5.75996 4.125 6.64592V12.8334H8.25C8.59806 12.8334 8.8857 13.0921 8.93122 13.4276L8.9375 13.5209C8.9375 14.66 9.86095 15.5834 11 15.5834C12.1391 15.5834 13.0625 14.66 13.0625 13.5209C13.0625 13.1412 13.3703 12.8334 13.75 12.8334H17.875L17.876 11.245C18.381 10.9817 18.8436 10.6481 19.2507 10.2572L19.25 17.1876C19.25 18.8329 17.9162 20.1667 16.2708 20.1667H5.72917C4.08381 20.1667 2.75 18.8329 2.75 17.1876V6.64592C2.75 5.00056 4.08381 3.66675 5.72917 3.66675L9.62372 3.6659ZM15.125 0.916748C17.9095 0.916748 20.1667 3.17398 20.1667 5.95842C20.1667 8.74285 17.9095 11.0001 15.125 11.0001C12.3405 11.0001 10.0833 8.74285 10.0833 5.95842C10.0833 3.17398 12.3405 0.916748 15.125 0.916748ZM15.3227 3.28962L15.2592 3.34266L15.2062 3.40613C15.098 3.56243 15.098 3.77106 15.2062 3.92737L15.2592 3.99084L16.7677 5.50008H11.9167L11.8343 5.50747C11.6472 5.54142 11.4997 5.68894 11.4658 5.87603L11.4583 5.95842L11.4658 6.04081C11.4997 6.22789 11.6472 6.37541 11.8343 6.40936L11.9167 6.41675H16.7677L15.2592 7.92599L15.2062 7.98946C15.0825 8.1681 15.1002 8.41507 15.2592 8.57417C15.4183 8.73328 15.6653 8.75095 15.8439 8.62721L15.9075 8.57417L18.2371 6.23892L18.2674 6.19533L18.2987 6.13354L18.3181 6.07589L18.3314 6.00085L18.3333 5.95842L18.3308 5.90947L18.3181 5.84095L18.2905 5.76463L18.2519 5.69748L18.2101 5.64571L15.9075 3.34266L15.8439 3.28962C15.6877 3.18135 15.479 3.18135 15.3227 3.28962Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color +'" />',
                            '</svg>',
                        '</a>',
                    '</div>',
                    '<span>View Screenshot</span>',
                '</li>',
            ].join('');
        }

        if(EASYASSIST_COBROWSE_META.enable_invite_agent_in_cobrowsing){
            modal_html += [
                '<li class="easyassist-option">',
                    '<div class="menu-item active-item">',
                        '<a href="javascript:void(0)" onclick="easyassist_get_list_of_support_agents();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();";>',
                            '<svg width="26" height="26" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                '<path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                '<path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '</svg>',
                        '</a>',
                    '</div>',
                    '<span>Invite an Agent</span>',
                '</li>',
            ].join('');
        }

        if(EASYASSIST_COBROWSE_META.allow_support_documents){
            modal_html += [
                '<li class="easyassist-option">',
                    '<div class="menu-item active-item">',
                        '<a href="javascript:void(0)" onclick="easyassist_get_support_material();easyassist_hide_dialog_modal();hide_easyassist_feedback_form();">',
                            '<svg width="26" height="26" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg" >',
                                '<path d="M7.5 0V6C7.5 6.82843 8.17157 7.5 9 7.5H15V16.5C15 17.3284 14.3284 18 13.5 18H1.5C0.671573 18 0 17.3284 0 16.5V1.5C0 0.671573 0.671573 0 1.5 0H7.5Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                                '<path d="M8.625 0.375V6C8.625 6.20711 8.79289 6.375 9 6.375H14.625L8.625 0.375Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '</svg>',
                        '</a>',
                    '</div>',
                    '<span>Documents</span>',
                '</li>',
            ].join('');
        }

        if(EASYASSIST_COBROWSE_META.enable_chat_functionality){
            modal_html += [
                '<li>',
                    '<div class="menu-item active-item">',
                        '<a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();show_easyassist_livechat_iframe();hide_easyassist_feedback_form();";>',
                            '<svg width="26" height="26" viewBox="0 0 29 29" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M14.5001 0C22.508 0 29 6.49091 29 14.4978C29 22.5048 22.508 28.9957 14.5001 28.9957C12.1215 28.9957 9.82402 28.4215 7.76591 27.3404L1.54481 28.9598C0.886105 29.1316 0.213008 28.7367 0.0414436 28.0779C-0.0116107 27.8744 -0.0116264 27.6606 0.0413963 27.4569L1.66011 21.2396C0.575942 19.1798 0 16.8795 0 14.4978C0 6.49091 6.49189 0 14.5001 0ZM16.3151 15.9477H9.78752L9.63995 15.9575C9.10914 16.0296 8.70002 16.4845 8.70002 17.035C8.70002 17.5854 9.10914 18.0404 9.63995 18.1125L9.78752 18.1223H16.3151L16.4626 18.1125C16.9935 18.0404 17.4026 17.5854 17.4026 17.035C17.4026 16.4845 16.9935 16.0296 16.4626 15.9575L16.3151 15.9477ZM19.2125 10.8734H9.78752L9.63995 10.8833C9.10914 10.9553 8.70002 11.4102 8.70002 11.9607C8.70002 12.5112 9.10914 12.9662 9.63995 13.0382L9.78752 13.0481H19.2125L19.3602 13.0382C19.8909 12.9662 20.3 12.5112 20.3 11.9607C20.3 11.4102 19.8909 10.9553 19.3602 10.8833L19.2125 10.8734Z"',
                                'fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>',
                            '</svg>',
                        '</a>',
                    '</div>',
                    '<span>Chat with the Customer</span>',
                '</li>',
            ].join('');
        }
        modal_html += [
            '<li>',
                '<div class="menu-item">',
                    '<a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();revoke_easyassist_edit_access();" id="revoke-edit-access-button">',
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
                    '<a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();show_sharable_link_dialog_box();">',
                        '<svg width="26" height="26" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve">',
                            '<g>',
                                '<g>',
                                    '<path fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124 c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90 0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59 C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806 l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90 C496,372.371,455.629,332,406,332z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"></path>',
                                '</g>',
                            '</g>',
                            '<g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g>',
                        '</svg>',
                    '</a>',
                '</div>',
                '<span>Get Shareable Link</span>',
            '</li>',
        ].join('');

        if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
            modal_html += '\
            <li class="easyassist-option">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" id="show-voip-modal-btn" onclick="easyassist_hide_dialog_modal();show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();">\
                      <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    </a>\
                </div>\
                <span>Video Call</span>\
            </li>';
        } else if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            modal_html += '\
            <li class="easyassist-option">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" id="show-voip-modal-btn" onclick="easyassist_hide_dialog_modal();show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();">\
                      <svg width="26" height="26" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-call-icon">\
                        <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                      <svg width="19" height="19" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="easyassist-voip-calling-icon" style="display: none;">\
                        <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    </a>\
                </div>\
                <span>Voice Call</span>\
            </li>';
        } else if(EASYASSIST_COBROWSE_META.allow_cobrowsing_meeting) {
            modal_html += '\
            <li class="easyassist-option">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" id="show-voip-modal-btn" onclick="easyassist_hide_dialog_modal();show_easyassist_video_calling_request_modal();hide_easyassist_feedback_form();">\
                      <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                        <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '"/>\
                      </svg>\
                    </a>\
                </div>\
                <span>Video Call</span>\
            </li>';
        }

        if(EASYASSIST_COBROWSE_META.enable_cobrowsing_annotation) {
            modal_html += '\
            <li class="easyassist-option">\
                <div class="menu-item">\
                    <a href="javascript:void(0)" onclick="easyassist_hide_dialog_modal();easyassist_activate_canvas(this);hide_easyassist_feedback_form();" id="easyassist-toggle-canvas-btn">\
                      <svg width="26" height="26" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">\
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />\
                      </svg>\
                    </a>\
                </div>\
                <span id="easyassist-toggle-canvas-label">Enter Drawing Mode</span>\
            </li>';
        }

        modal_html += [
            '</ul>',
            '</div>',
                '<div class="easyassist-customer-connect-modal-footer" easyassist-data-scroll-x="0" easyassist-data-scroll-y="0">',
                    '<div easyassist-data-scroll-x="0" easyassist-data-scroll-y="0"><button class="easyassist-modal-primary-btn end-session-btn" id="easyassist-co-browsing-connect-button" onclick="easyassist_hide_dialog_modal();show_easyassist_feedback_form();"',
                    'style="background-color: #D70000">End Session</button></div>',
                '</div>',
            '</div>'
        ].join('')
        div_model.innerHTML = modal_html;
        document.getElementsByTagName("body")[0].appendChild(div_model);
    }

    function easyassist_show_dialog_modal(){
        document.getElementById("cobrowse-mobile-modal").style.display = "flex";
        hide_floating_sidenav_menu();
    }

    function easyassist_hide_dialog_modal() {
        document.getElementById("cobrowse-mobile-modal").style.display = "none";
        show_floating_sidenav_menu();
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
          <button onclick="hide_payment_consent_modal(this)" style="background-color: #1b5e20; color: white; font-size: 0.8em; padding: 1.0em 2.0em 1.0em 2.0em; border-radius: 2em !important; border-style: none; float: right; margin-right: 5%;outline:none;">Ok</button>\
      </div>\
      </div>\
    </div>';
        document.getElementsByTagName("body")[0].insertAdjacentHTML('beforeend', request_modal_html);
    }

    function show_sharable_link_dialog_box(){
        var share_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client/" + get_easyassist_cookie("easyassist_session_id");
        document.getElementById("easyassist_share_link_Model-content_link_wrapper").value = share_url;
        document.getElementById("easyassist_share_link_Model").style.display = "flex";

        let is_email_send = get_easyassist_cookie('easyassist_is_email_send');
        if(is_email_send && is_email_send=='true'){
            let client_email = get_easyassist_cookie('easyassist_client_email');
            if(client_email){
                document.getElementById('generate_link_comment').innerHTML = `
                <div class="email-note-message"  >
                    <p>Co-browsing link has been shared with customer on ${client_email}.</p>
                </div>`;
            }
        }
    }

    function hide_payment_consent_modal(element) {
        document.getElementById("easyassist-co-browsing-payment-consent-modal").style.display = "none";
    }

    function show_payment_consent_modal(element) {
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
                    "Looks like we are not receiving any updates from the customer side. Kindly check your internet connectivity or check whether the customer is still connected or not.",
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
        document.getElementById("easyassist-agent-disconnected-modal").style.display = "flex";
    }

    function easyassist_hide_agent_disconnected_modal(element) {
        document.getElementById("easyassist-agent-disconnected-modal").style.display = "none";
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
                    "Looks like the customer is facing internet connectivity issues",
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
        easyassist_hide_client_weak_internet_connection();
        document.getElementById("easyassist-agent-weak-internet-connection-modal").style.display = "flex";
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
        easyassist_hide_agent_weak_internet_connection();
        document.getElementById("easyassist-client-weak-internet-connection-modal").style.display = "flex";
    }

    function easyassist_hide_client_weak_internet_connection(element) {
        document.getElementById("easyassist-client-weak-internet-connection-modal").style.display = "none";
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

    function auto_fetch_details(el) {
        var auto_fetch_fields = EASYASSIST_COBROWSE_META.auto_fetch_fields;
        for(let index = 0; index < auto_fetch_fields.length; index++) {
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

        if(document.getElementById("modal-cobrowse-virtual-agent-email-id")){
            let email_input = document.getElementById('easyassist-client-agent-email-id');
            if(email_input){
                email_input.setAttribute("style", "border: 1px solid #EBEBEB !important;");
                    email_input.value = "";
            }
            document.getElementById("modal-cobrowse-virtual-agent-email-id").innerHTML = "";
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
        easyassist_canvas.style.zIndex = "1039";

        document.getElementsByTagName("body")[0].appendChild(easyassist_canvas);

        var cursor_icon = [
            '<svg width="30" height="30" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '">',
                '<path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />',
            '</svg>',
        ].join('');
        var encoded_cursor_icon = "data:image/svg+xml;base64," + btoa(cursor_icon);
        easyassist_canvas.style.cursor = "url('" + encoded_cursor_icon + "') 5 25, default";

        easyassist_drawing_canvas = new EasyAssistCanvas(easyassist_canvas, EASYASSIST_COBROWSE_META.floating_button_bg_color, 7);
    }

    function easyassist_activate_canvas(element) {
        try {
            // document.body.style.overflow = "hidden";
            if(EASYASSIST_COBROWSE_META.is_mobile == false) { 
                element.style.backgroundColor = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.4, 300);
            } else {
                if (EASYASSIST_COBROWSE_META.floating_button_position == "top" || EASYASSIST_COBROWSE_META.floating_button_position == "bottom") {
                    element.parentElement.parentElement.style.backgroundColor = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.4, 300);
                } else {
                    element.parentElement.style.backgroundColor = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.4, 300);
                }
            }
            var easyassist_canvas_element = document.getElementById("easyassist-drawing-canvas");
            easyassist_canvas_element.style.pointerEvents = "";
            
            if(!easyassist_canvas_element.getAttribute("data-canvas")) {
                window.easyassist_drawing_canvas = new EasyAssistCanvas(
                    easyassist_canvas_element, FLOATING_BUTTON_BG_COLOR, 7);
            }
            element.setAttribute("onclick", "easyassist_deactivate_canvas(this);easyassist_hide_dialog_modal()");
            document.getElementById("easyassist-toggle-canvas-label").innerHTML = "Exit Drawing Mode";

        } catch(err) {
            console.log("easyassist_activate_canvas: ", err);
        }
    }

    function easyassist_deactivate_canvas(element) {
        try {
            // document.body.style.overflow = "";   
            if(EASYASSIST_COBROWSE_META.is_mobile == false) {
                element.style.backgroundColor = "";
            } else {
                if (EASYASSIST_COBROWSE_META.floating_button_position == "top" || EASYASSIST_COBROWSE_META.floating_button_position == "bottom") {
                    element.parentElement.parentElement.style.backgroundColor = "";
                } else {
                    element.parentElement.style.backgroundColor = "";
                }
            }
            
            var easyassist_canvas_element = document.getElementById("easyassist-drawing-canvas");
            easyassist_canvas_element.style.pointerEvents = "none";
            
            element.setAttribute("onclick", "easyassist_activate_canvas(this);easyassist_hide_dialog_modal()");
            document.getElementById("easyassist-toggle-canvas-label").innerHTML = "Enter Drawing Mode";
         
            easyassist_drawing_canvas.clear_drawing();

        } catch(err) {
            console.log("easyassist_deactivate_canvas: ", err);
        }
    }

    function easyassist_reset_canvas() {
        try {
            var toggle_canvas_btn = document.getElementById("easyassist-toggle-canvas-btn");
            easyassist_deactivate_canvas(toggle_canvas_btn);
        } catch(err) {
            console.log("easyassist_reset_canvas: ", err)
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

        delete_easyassist_cookie("easyassist_is_email_send");
        delete_easyassist_cookie("easyassist_client_email");

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

        if(document.getElementById("modal-cobrowse-virtual-agent-email-id")){
            let email_input = document.getElementById('easyassist-client-agent-email-id');
            if(email_input){
                email_input.setAttribute("style","border: 1px solid #EBEBEB !important;");                
            }
            document.getElementById("modal-cobrowse-virtual-agent-email-id").innerHTML = "";
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
        if (document.querySelector("title") && document.querySelector("title").innerText.trim() != "") {
            title = document.querySelector("title").innerHTML;
        }
        var description = "";
        if (document.querySelector("meta[name=description]") != null && document.querySelector("meta[name=description]") != undefined) {
            description = document.querySelector("meta[name=description]").content;
        }

        let email_input = document.getElementById('easyassist-client-agent-email-id');
        if(email_input && email_input.value.trim() != ""){
            let email_val = email_input.value.trim();
            
            if (!check_valid_email(email_val)) {
                email_input.setAttribute("style", "border: 1px solid #EC2828 !important;");                
                document.getElementById('modal-cobrowse-virtual-agent-email-id').innerHTML = 'Please enter a valid Email ID';
                return;
            }else{
                document.getElementById('generate_link_comment').innerHTML = `
                <div class="email-note-message"  >
                    <p>Co-browsing link has been shared with customer on ${email_val}.</p>
                </div>`;
                set_easyassist_cookie('easyassist_is_email_send', 'true');
                set_easyassist_cookie('easyassist_client_email', email_val);
            }            
        }else{
            document.getElementById('generate_link_comment').innerHTML = `
            <div class="easyassist-customer-connect-modal-content-wrapper">
                <p>Copy the above generated link and share with the customer.</p>
            </div>`;
        }

        var url = window.location.href;
        var request_id = easyassist_request_id();

        json_string = JSON.stringify({
            "request_id": request_id,
            "name": full_name,
            "mobile_number": mobile_number,
            "virtual_agent_code": virtual_agent_code,
            "client_email":email_input.value.trim(),
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

                    set_easyassist_cookie("easyassist_session_id", response.session_id);
                    
                    try {
                        document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
                    } catch(err) {
                        console.log(err);
                    }
                    easyassist_create_local_storage_obj();
                    set_easyassist_cookie("easyassist_cobrowsing_allowed", "true");
                    document.getElementById("easyassist-co-browsing-connect-button").disabled = false;

                    var share_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/client/" + response.session_id;
                    var message = share_url;
                    document.getElementById("easyassist_share_link_Model-content_link_wrapper").value = message;
                    document.getElementById("easyassist_share_link_Model").style.display = "flex";

                    show_floating_sidenav_menu();
                    close_easyassist_browsing_modal();
                    
                } else if (response.status == 101) {

                    document.getElementById("modal-cobrowse-connect-error").innerHTML = "Please enter valid agent code"; 

                } else if (response.status == 103) {

                    document.getElementById("modal-cobrowse-connect-error").innerHTML = "Please enter code shared by our agent";

                }else if (response.status == 104) {

                    document.getElementById("modal-cobrowse-connect-error").innerHTML = "Please enter valid Email address";

                } else{

                    close_easyassist_browsing_modal();
                    easyassist_show_function_fail_modal(code=631);
                    console.error(response);

                }
            } else if (this.readyState == 4) {

                close_easyassist_browsing_modal();
                easyassist_show_function_fail_modal(code=632);

                description = "Initiate lead API (/easy-assist/initialize/) failed with status code " + this.status.toString();
                document.getElementById("easyassist-co-browsing-connect-button").disabled = false;
                // save_easyassist_system_audit_trail("api_failure", description);
            }
        }
        xhttp.send(params);
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

    function show_easyassist_toast(message) {
        var x = document.getElementById("easyassist-snackbar");
        x.innerHTML = message;
        x.className = "show";
        setTimeout(function() {
            x.className = x.className.replace("show", "");
        }, EASYASSIST_COBROWSE_META.toast_timeout);
    }

    window.Clipboard = (function(window, document, navigator) {
        var textArea,
            copy;

        function isOS() {
            return navigator.userAgent.match(/ipad|iphone/i);
        }

        function createTextArea(text) {
            textArea = document.createElement('textArea');
            textArea.value = text;
            document.body.appendChild(textArea);
        }

        function selectText() {
            var range,
                selection;

            if (isOS()) {
                range = document.createRange();
                range.selectNodeContents(textArea);
                selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                textArea.setSelectionRange(0, 999999);
            } else {
                textArea.select();
            }
        }

        function copyToClipboard() {
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }

        copy = function(text) {
            createTextArea(text);
            selectText();
            copyToClipboard();
        };

        return {
            copy: copy
        };
    })(window, document, navigator);

    function copy_text_to_clipboard_sharable_link_easyassist() {
        var copyText = document.getElementById("easyassist_share_link_Model-content_link_wrapper");
        var copyButton = document.getElementById('cobrowse-share-link-copy-btn');
        copyButton.classList.add('cobrowse-share-link-copy-btn-active');
        copyButton.style.background = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.1);
        copyButton.removeAttribute("onmouseout");

        Clipboard.copy(copyText.value);
        show_easyassist_toast("Shareable link has been copied");
    }

    function check_element_is_hidden(element) {
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
        } catch(err) {}

        if(element.offsetParent == null) {
            return true;
        }
        return false;
    }

    function easyassist_apply_custom_select(document_select_tag_list) {
        if(EASYASSIST_COBROWSE_META.enable_custom_cobrowse_dropdown == false) {
            return;
        }

        for(let d_index = 0; d_index < document_select_tag_list.length; d_index++) {
            var s_element = document_select_tag_list[d_index];
            if(!check_element_is_hidden(s_element)&&!is_custom_select_removed(s_element)) {
                var obfuscated_field = easyassist_obfuscated_element_check(s_element);
                new EasyassistCustomSelect2(s_element, null, null, obfuscated_field);
            }
        }
    
        easyassist_custom_dropdown_applied = true;
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
        iframe.setAttribute("allow", "microphone *");
        iframe.style.display = "none";

        if (EASYASSIST_COBROWSE_META.is_mobile == false && EASYASSIST_COBROWSE_META.floating_button_position == "right") {
            iframe.style.setProperty("left", "1em", "important");
        }
        
        document.querySelector("body").appendChild(iframe);
        update_livechat_iframe_source();
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
            
            if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
                if(livechat_iframe.classList.contains("allincall-scale-out-br")) {
                    livechat_iframe.classList.remove("allincall-scale-out-br");
                }

                if (livechat_iframe.classList.contains("allincall-scale-out-br-right-side")) {
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
            if(document.getElementById("chat-minimize-icon-wrapper")){
                document.getElementById("chat-minimize-icon-wrapper").style.display = "none";
            }
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
        try{
            livechat_iframe = document.getElementById("easyassist-livechat-iframe");
            if (livechat_iframe != null && livechat_iframe != undefined) {
                if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
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
                    document.getElementById('allincall-popup').style.display = "none";
                    document.getElementById('allincall-chat-box').style.display = "none";
                }
            }
        }catch(err){}
    }

    function refresh_easyassist_livechat_iframe() {
        try{
            livechat_iframe = document.getElementById("easyassist-livechat-iframe");
            if (livechat_iframe != null && livechat_iframe != undefined) {
                livechat_iframe.src = livechat_iframe.src;
            }
        }catch(err){}
    }

    function play_greeting_bubble_popup_sound() {

        let livechat_iframe = document.getElementById("easyassist-livechat-iframe");
    
        if (livechat_iframe.classList.contains("animate__slideInUp")) {
            return;
        }
    
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

    function update_livechat_iframe_source(){
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
        let iframe_element = document.getElementById("easyassist-livechat-iframe");
        if(easyassist_session_id && iframe_element) {
            iframe_element.src = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/sales-ai/client/livechat/?access_token=" + EASYASSIST_COBROWSE_META.access_token +"&session_id=" + easyassist_session_id;
        }
    }

    exports.play_greeting_bubble_popup_sound = play_greeting_bubble_popup_sound
    exports.hide_floating_mobile_sidenav_menu = hide_floating_mobile_sidenav_menu;
    exports.close_connection_modal = close_connection_modal;
    exports.screenshot_page = screenshot_page;
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
    exports.show_payment_consent_modal = show_payment_consent_modal;
    exports.hide_payment_consent_modal = hide_payment_consent_modal;
    exports.get_easyassist_session_details = get_easyassist_session_details;
    exports.update_easyassist_url_history = update_easyassist_url_history;
    exports.create_easyassist_hidden_iframe = create_easyassist_hidden_iframe;
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
    exports.easyassist_check_dom_node = easyassist_check_dom_node;
    exports.obfuscate_data_using_recursion = obfuscate_data_using_recursion;
    exports.set_value_attr_into_screenshot = set_value_attr_into_screenshot;
    exports.convert_urls_to_absolute = convert_urls_to_absolute;
    exports.easyassist_obfuscated_element_check = easyassist_obfuscated_element_check;
    exports.show_comments_textbox = show_comments_textbox;
    exports.set_remarks_in_textbox = set_remarks_in_textbox;
    exports.remove_easyassist_event_listner_into_element = remove_easyassist_event_listner_into_element;
    exports.add_easyassist_event_listner_into_element = add_easyassist_event_listner_into_element;
    exports.easyassist_show_dialog_modal = easyassist_show_dialog_modal;
    exports.easyassist_hide_dialog_modal = easyassist_hide_dialog_modal;
    exports.easyassist_show_agent_weak_internet_connection = easyassist_show_agent_weak_internet_connection;
    exports.easyassist_hide_agent_weak_internet_connection = easyassist_hide_agent_weak_internet_connection;
    exports.easyassist_show_agent_disconnected_modal = easyassist_show_agent_disconnected_modal;
    exports.easyassist_hide_agent_disconnected_modal = easyassist_hide_agent_disconnected_modal;
    exports.easyassist_show_client_weak_internet_connection = easyassist_show_client_weak_internet_connection;
    exports.easyassist_hide_client_weak_internet_connection = easyassist_hide_client_weak_internet_connection;
    exports.easyassist_show_function_fail_modal = easyassist_show_function_fail_modal;
    exports.easyassist_hide_function_fail_modal = easyassist_hide_function_fail_modal;
    exports.add_easyassist_capture_screenshot_modal = add_easyassist_capture_screenshot_modal;
    exports.show_easyassist_capture_screenshot_modal = show_easyassist_capture_screenshot_modal;
    exports.hide_easyassist_capture_screenshot_modal = hide_easyassist_capture_screenshot_modal;
    exports.add_easyassist_captured_screenshot_view_modal = add_easyassist_captured_screenshot_view_modal;
    exports.show_easyassist_captured_screenshot_view_modal = show_easyassist_captured_screenshot_view_modal;
    exports.hide_easyassist_captured_screenshot_view_modal = hide_easyassist_captured_screenshot_view_modal;
    exports.set_easyassist_blur_fields = set_easyassist_blur_fields;
    exports.remove_easyassist_blur_fields = remove_easyassist_blur_fields;
    exports.add_easyassist_invite_agent_modal = add_easyassist_invite_agent_modal;
    exports.show_easyassist_invite_agent_modal = show_easyassist_invite_agent_modal;
    exports.hide_easyassist_invite_agent_modal = hide_easyassist_invite_agent_modal;
    exports.toggle_easyassist_invite_agent_list = toggle_easyassist_invite_agent_list;
    exports.add_easyassist_support_document_modal = add_easyassist_support_document_modal;
    exports.show_easyassist_support_document_modal = show_easyassist_support_document_modal;
    exports.hide_easyassist_support_document_modal = hide_easyassist_support_document_modal;
    exports.add_easyassist_report_bug_modal = add_easyassist_report_bug_modal;
    exports.show_easyassist_report_bug_modal = show_easyassist_report_bug_modal;
    exports.hide_easyassist_report_bug_modal = hide_easyassist_report_bug_modal;
    exports.easyassist_set_event_listeners = easyassist_set_event_listeners;
    exports.easyassist_activate_canvas = easyassist_activate_canvas;
    exports.easyassist_deactivate_canvas = easyassist_deactivate_canvas;
    exports.easyassist_reset_canvas = easyassist_reset_canvas;
    exports.easyassist_change_options_visiblity = easyassist_change_options_visiblity;
    exports.easyassist_relocate_drag_element = easyassist_relocate_drag_element;
    exports.easyassist_show_pdf_render_modal = easyassist_show_pdf_render_modal;
    exports.easyassist_show_chat_bubble = easyassist_show_chat_bubble;
    exports.easyassist_hide_pdf_coview = easyassist_hide_pdf_coview;
    exports.easyassist_show_pdf_coview = easyassist_show_pdf_coview;
    
    easyassist_add_ripple_animation_frame();
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
    easyassist_add_function_fail_modal();
    set_easyassist_cookie("page_leave_status", "None");
    add_floating_button_color_to_class()
    easyassisst_add_dialog_modal();
    easyassist_add_agent_weak_internet_connection();
    easyassist_add_agent_disconnected_modal();
    easyassist_add_client_weak_internet_connection();
    add_easyassist_capture_screenshot_modal();
    add_easyassist_captured_screenshot_view_modal();
    add_easyassist_invite_agent_modal();
    add_easyassist_support_document_modal();
    add_easyassist_report_bug_modal();
    easyassist_add_drawing_canvas();
    easyassist_add_avoid_sync_class();
    easyassist_chat_bubble_css();
    easyassist_add_chat_bubble_body();
    easyassist_add_pdf_render_modal();

    easyassist_get_eles_by_class_name("easyassist_share_link_Model-content-close_button")[0].onclick = function() {
        var copyButton = document.getElementById('cobrowse-share-link-copy-btn');
        copyButton.classList.remove('cobrowse-share-link-copy-btn-active');
        easyassist_remove_background_color(copyButton);
        copyButton.setAttribute("onmouseout","easyassist_remove_background_color(this)");
        document.getElementById("easyassist_share_link_Model").style.display = "none";
    }

    var local_storage_obj = get_easyassist_current_session_local_storage_obj();
    
    if(get_easyassist_cookie("ea_cust_connected") == "true") {
        if(document.getElementById("chat-minimize-icon-wrapper")){
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
        }
    }

    if(local_storage_obj && local_storage_obj.hasOwnProperty("new_message_seen")) {
        if(local_storage_obj["new_message_seen"] == "false" && document.getElementById("chat-minimize-icon-wrapper")) {
            document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
            document.getElementById("talktext-p").innerHTML = local_storage_obj["last_message"]
            document.querySelector(".chat-talk-bubble").style.display = "block";
            document.querySelector(".chat-talk-bubble").classList.add("bounce2");
            play_greeting_bubble_popup_sound();
        }
    }

})(window);

function easyassist_change_background_color(element) {
    element.style.background = easyassist_find_light_color(EASYASSIST_COBROWSE_META.floating_button_bg_color, 0.1);
}

function easyassist_remove_background_color(element) {
    element.style.background = "none";
}

function easyassist_find_light_color(color, opacity, percent=0) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);
    
    R = (R<255)?R:255;
    G = (G<255)?G:255;
    B = (B<255)?B:255;

    var rgba_color = "rgba(" + R + "," + G + "," + B + "," + opacity + ")"
    return rgba_color;
}

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
    for(let index = 0; index < rating_spans.length; index ++) {
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

    var rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");

    var show_default_emoji = true;
    for(let index = 0; index < rating_spans.length; index ++) {
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
    var rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    var user_rating = parseInt(element.innerHTML);

    window.EASYASSIST_CLIENT_FEEDBACK = user_rating;

    for(let index = 0; index <= user_rating; index ++) {
        let current_rating = parseInt(rating_spans[index].innerHTML);
        rating_spans[index].style.background = EASYASSIST_COBROWSE_META.floating_button_bg_color;
        rating_spans[index].style.color = "#fff";
        easyassist_tickmarks_clicked[current_rating] = true;
    }

    for(let index = user_rating + 1; index < rating_spans.length; index ++) {
        var current_rating = parseInt(rating_spans[index].innerHTML);
        rating_spans[index].style.background = "unset"
        rating_spans[index].style.color = "initial";
        easyassist_tickmarks_clicked[current_rating] = false;
    }
}

function reset_easyassist_rating_bar() {
    var rating_bar = easyassist_get_eles_by_class_name("easyassist-tickmarks")[0];
    var rating_spans = rating_bar.querySelectorAll("span");
    for(let index = 0; index < rating_spans.length; index++) {
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

    send_invited_agent_meeting_request();

    var is_cobrowse_meeting_active = get_easyassist_cookie("is_cobrowse_meeting_active");
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(is_cobrowse_meeting_active == easyassist_session_id) {
        show_easyassist_toast("Meeting request has been sent.");
        hide_easyassist_video_calling_request_modal();
        return;
    }

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
            show_easyassist_toast("An voice call has been initiated to the customer.");
        }
        document.getElementById("easyassist-voip-call-icon").style.display = 'none';
        document.getElementById("easyassist-voip-calling-icon").style.display = 'block';
        setTimeout(function() {
            toggle_voip_ringing_sound(true);
        }, 2000);
        // send_call_initiate_notification();
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
                request_meeting_error.innerHTML = "Request has been sent to customer";
                request_meeting_error.style.setProperty('color', 'green', "important");

                if(check_meeting_status_interval != null) {
                    clearInterval(check_meeting_status_interval);
                    check_meeting_status_interval = null;
                }

                check_meeting_status_interval = setInterval(function() {
                    check_easyassist_meeting_status(session_id)
                }, 5000)
                el.innerText = "Request";

            } else {
                request_meeting_error.innerHTML = "Due to some internal server, we are unable to process your request. Please try again.";
                request_meeting_error.style.setProperty('color', 'red', "important");
            }
        } else if (this.readyState == 4) {
            request_meeting_error.innerHTML = "Due to some network issue, we are unable to process your request. Please try again.";
            request_meeting_error.style.setProperty('color', 'red', "important");
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
                        easyassist_voip_connect_with_client();
                        hide_easyassist_video_calling_request_modal();

                        request_meeting_error.innerHTML = "";
                        request_meeting_error.style.color = 'green';

                        var html = document.getElementById("easyassist_request_meeting_button");
                        var button = [
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_voip_connect_with_client(this)" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; margin-right: 1em!important;">Connect</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; font-size: 13px!important;">Resend Request</button>',
                        ].join('');
                        html.innerHTML = button;

                        toggle_voip_ringing_sound(false);
                        document.getElementById("easyassist-voip-calling-icon").style.display = 'none';
                        document.getElementById("easyassist-voip-call-icon").style.display = 'block';
                    } else {
                        set_easyassist_cookie("is_cobrowse_meeting_active", session_id);
                        request_meeting_error.innerHTML = "Meeting request has been accepted by the customer. Please click on 'Connect' to join the meeting."
                        request_meeting_error.style.setProperty('color', 'green', "important");

                        let html = document.getElementById("easyassist_request_meeting_button");
                        let button = [
                            '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_connect_with_client(this)" style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important; margin-right: 1em!important;">Connect</button>',
                            '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Resend Request</button>',
                        ].join('');
                        html.innerHTML = button;
                        easyassist_connect_with_client();
                    }

                    if(check_meeting_status_interval != null) {
                        clearInterval(check_meeting_status_interval);
                        check_meeting_status_interval = null;
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
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    show_easyassist_toast("Customer declined the call");
                                }
                                request_meeting_error.innerHTML = "The voice call request has been rejected by the customer"
                                request_meeting_error.style.color = 'red';
                            }
                        } else if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling == true) {
                            toggle_voip_ringing_sound(false);
                            toggle_voip_beep_sound(true);
                            if(auto_msg_popup_on_client_call_declined == true) {
                                show_easyassist_toast("Customer declined the call");
                            } else {
                                if(request_meeting_error.offsetParent == null) {
                                    show_easyassist_toast("Customer declined the call");
                                }
                                request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                                request_meeting_error.style.color = 'red';
                            }
                        } else {
                            request_meeting_error.innerHTML = "Meeting request has been rejected by customer."
                            request_meeting_error.style.setProperty('color', 'red', "important");
                            var html = document.getElementById("easyassist_request_meeting_button");
                            let button = [
                                '<button class="easyassist-modal-cancel-btn" onclick="hide_easyassist_video_calling_request_modal(this)" style="color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Cancel</button>',
                                '<button class="easyassist-modal-primary-btn" onclick="easyassist_request_for_meeting(this)"  style="background-color: ' + EASYASSIST_COBROWSE_META.floating_button_bg_color + '!important">Resend Request</button>',
                            ].join('');
                            html.innerHTML = button;
                        }
                        auto_msg_popup_on_client_call_declined = false;
                        if(check_meeting_status_interval != null) {
                            clearInterval(check_meeting_status_interval);
                            check_meeting_status_interval = null;
                        }
                    }
                }
            }
        } else if (this.readyState == 4) {
            request_meeting_error.innerHTML = "Due to some network issue, we are unable to process your request. Please refresh the page and try again."
            request_meeting_error.style.color = 'red';
        }
    }
    xhttp.send(params);
}

function easyassist_voip_connect_with_client() {
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(easyassist_session_id == undefined) {
        return;
    }

    var url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + "/easy-assist/agent-cobrowse-meeting/" + easyassist_session_id;
    window.open(url, "_blank",);
}

function show_cobrowse_meeting_option() {
    if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
        return;
    }

    if (get_easyassist_cookie("easyassist_session_id") == undefined) {
        return;
    }

    set_easyassist_cookie("is_cobrowse_meeting_on", "true");
    var cobrowse_meeting_id = get_easyassist_cookie("cobrowse_meeting_id");
    var easyassist_session_id = get_easyassist_cookie("easyassist_session_id");
    if(cobrowse_meeting_id == easyassist_session_id) {
        try {
            if(EASYASSIST_COBROWSE_META.is_mobile) {
                document.getElementById("show-voip-modal-btn").parentElement.parentElement.style.display = 'none';
            } else {
                document.getElementById("show-voip-modal-btn").style.display = 'none';
            }
        } catch(err) {}

        if(document.getElementById("easyassist-cobrowse-voip-container").style.display == 'none') {
            send_client_meeting_joined_over_socket();
            document.getElementById("easyassist-voip-loader").style.display = 'flex';
            document.getElementById("easyassist-cobrowse-voip-container").style.display = '';
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
            document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = '';
        } else if(element.id == "easyassist-client-meeting-mic-off-btn") {
            document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = 'none';
            document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = '';
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
            document.getElementById("easyassist-client-meeting-video-off-btn").style.display = '';
        } else if(element.id == "easyassist-client-meeting-video-off-btn") {
            document.getElementById("easyassist-client-meeting-video-off-btn").style.display = 'none';
            document.getElementById("easyassist-client-meeting-video-on-btn").style.display = '';
        }
    } catch(err) {
        console.log(err);
    }
}

function end_cobrowse_video_meet(auto_end_meeting=false) {
    try {
        if(EASYASSIST_COBROWSE_META.enable_voip_calling) {
            return;
        }

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
    set_easyassist_cookie("is_cobrowse_meeting_active", "");
    delete_easyassist_cookie("is_meeting_audio_muted");
    delete_easyassist_cookie("is_agent_voip_meeting_joined");

    try {
        if(EASYASSIST_COBROWSE_META.is_mobile) {
            document.getElementById("show-voip-modal-btn").parentElement.parentElement.style.display = "";
        } else {
            document.getElementById("show-voip-modal-btn").style.display = 'flex';
        }
    } catch(err) {}

    document.getElementById("easyassist-cobrowse-meeting-iframe-container").style.display = 'none';
    document.getElementById("easyassist-cobrowse-voip-container").style.display = 'none';
    document.getElementById("easyassist-client-meeting-mic-on-btn").style.display = 'none';
    document.getElementById("easyassist-client-meeting-mic-off-btn").style.display = '';
    if(EASYASSIST_COBROWSE_META.enable_voip_with_video_calling) {
        document.getElementById("easyassist-client-meeting-video-on-btn").style.display = '';
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
        <div class="modal-body">
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

function easyassist_show_pdf_render_modal(file_name,file_src,session_id){
    hide_easyassist_livechat_iframe();
    let split_array = file_src.split("/easy-assist")
    file_src = "/easy-assist" + split_array[1]

    if(session_id == ""){
        session_id = get_easyassist_cookie("easyassist_session_id")
    }
    
    if(file_name.length > 15) {
        file_name = file_name.substring(0, 8) + "..." + "pdf";  
    }

    easyassist_show_pdf_coview();
    easyassist_send_apply_event_listener_over_socket();
    document.getElementById("easyassist_pdf_render_modal_wrapper").classList.add('easyassist_pdf_render_modal_wrapper_show');
    document.getElementById("easyassist-pdf-title").innerHTML = '<p>'+file_name+'</p>';
    download_file_url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + file_src + "?session_id=" + session_id;
    file_src = file_src.replace('download-file','view-file')
    const url = EASYASSIST_HOST_PROTOCOL + "://" + EASYASSIST_COBROWSE_HOST + file_src + "?session_id=" + session_id;
    let pageNum = 1;
    let pageIsRendering = false;
    let pageNumIsPending = null;
    document.getElementById("easy_assist_pdf_render_current_page").value = pageNum;

    easyassist_show_hide_floating_page_number(pageNum);

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
    document.getElementById("easy_assist_pdf_render_current_page").value = pageNum
    
    easyassist_show_hide_floating_page_number(pageNum);

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
        document.querySelector('#coview_pdf_page_length').innerHTML = this.pdfDoc.numPages
        renderPage(pageNum);
    })


    // Button Events
    // document.querySelector('#pdf_download_svg').addEventListener('click', download_file);
    if(this.pdfDoc){
        // $('#easyassist-pdf-render-modal-close').click();
        console.log("already open pdf")
        document.querySelector('#prev-page').removeEventListener('click', showPrevPage);
        document.querySelector('#next-page').removeEventListener('click', showNextPage);
        document.querySelector('#prev-page-mobile').removeEventListener('click', showPrevPage);
        document.querySelector('#next-page-mobile').removeEventListener('click', showNextPage);                
    }
    console.log("add listener")
    document.querySelector('#prev-page').addEventListener('click', showPrevPage);
    document.querySelector('#next-page').addEventListener('click', showNextPage);
    document.querySelector('#prev-page-mobile').addEventListener('click', showPrevPage);
    document.querySelector('#next-page-mobile').addEventListener('click', showNextPage);                
    document.querySelector('#easyassist-pdf-render-modal-close').addEventListener('click', closeModal);
    document.querySelector('#easy_assist_pdf_render_current_page').addEventListener('change', jump_to_page);
}

document_readystate_interval = setInterval(function() {
    if(document.readyState == "complete" && client_websocket_open) {
        easyassist_sync_html_data();
        clearInterval(document_readystate_interval);
    }
}, 1000);

function get_easyassist_current_session_local_storage_obj() {
    try {
        let local_storage_obj = null;
        let easyassist_session_id = get_easyassist_cookie("easyassist_session_id");

        if(localStorage.getItem("easyassist_session") != null) {
            local_storage_obj = localStorage.getItem("easyassist_session");
            local_storage_obj = JSON.parse(local_storage_obj);
            if(local_storage_obj.hasOwnProperty(easyassist_session_id)) {
                local_storage_obj = local_storage_obj[easyassist_session_id];
            } else {
                return null; 
            }
        }
        return local_storage_obj;
    } catch (error) {
        return null;
    }
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

function easyassist_show_chat_bubble() {
    if(EASYASSIST_COBROWSE_META.enable_chat_bubble && EASYASSIST_COBROWSE_META.is_mobile == false) {
        document.getElementById("chat-minimize-icon-wrapper").style.display = "block";
    }
}

function hide_chat_bubble_greeting_div() {
    document.querySelector(".chat-talk-bubble").style.display = "none";
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