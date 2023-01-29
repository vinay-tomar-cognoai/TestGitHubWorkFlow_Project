/***************** EasyAssist Custom Select ***********************/

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this._placeholder = "Select";
        this._bg_color = "";
        this._selected_list_class = "easyassist-option-selected";
        this._show_option_container_class = "easyassist-dropdown-show";
        if (placeholder != null) {
            this._placeholder = placeholder;
        }
        if (background_color != null) {
            this._bg_color = background_color;
        }
        this._select_element = this.get_select_element(selector);
        this.initialize();
    }
    get_select_element(selector) {
        var select_element = selector;
        try {
            select_element = document.querySelector(selector);
        } catch(err) {}

        return select_element;
    }
    initialize() {
        let _this = this;
        _this.create_and_add_dropdown_elements();
        _this.add_dropdown_wrapper_to_dom();
        _this.add_event_listeners();
        _this.add_element_properties();
        if (_this._placeholder) {
            _this._select_element.selectedIndex = -1;
        }
    }
    create_and_add_dropdown_elements() {
        let _this = this;
        _this.create_dropdown_wrapper();
        _this.create_dropdown_option_container();
        _this.create_dropdown_selected_value_wrapper();
        _this._dropdown_wrapper.insertAdjacentElement("beforeend", _this._dropdown_selected_value_wrapper);
        _this._dropdown_wrapper.insertAdjacentElement("beforeend", _this._dropdown_option_container);
    }
    create_dropdown_wrapper() {
        let _this = this;
        let tag_name = "div";
        let tag_class = "easyassist-custom-dropdown-container";
        _this._dropdown_wrapper = _this.create_element(tag_name, tag_class);
    }
    create_dropdown_option_container() {
        let _this = this;
        let tag_name = "ul";
        let tag_class = "easyassist-custom-dropdown-option-container";
        _this._dropdown_option_container = _this.create_element(tag_name, tag_class);
        let option_html = _this.get_dropdown_options_html();
        _this._dropdown_option_container.innerHTML = option_html;
    }
    get_dropdown_options_html() {
        let _this = this;
        const get_dropdown_option_html = (text, value, is_selected) => {
            let bg_color = "";
            let selected_list_class = "";
            if (is_selected) {
                selected_list_class = _this._selected_list_class;
                bg_color = _this._bg_color;
            }
            let html = [
                `<li  class="${selected_list_class}" style="background-color:${bg_color}!important;" data-original-value="${value}">`,
                `<span>${text}</span>`,
                `</li>`
            ].join('');
            return html;
        };
        let select_element = _this._select_element;
        let options = select_element.querySelectorAll('option');
        let option_html = "";
        options.forEach((option) => {
            let option_text = option.text.trim();
            let option_value = option.value;
            let is_selected = (option.getAttribute("selected") != null);
            option_html += get_dropdown_option_html(option_text, option_value, is_selected);
        });
        return option_html;
    }
    set_selected_option_value() {
        var _this = this;
        var _a;
        let selected_value = _this._select_element.value;
        let option_text = _this._placeholder;
        if (selected_value) {
            let option_element = _this._select_element.querySelector(`option[value='${selected_value}']`);
            option_text = ((_a = option_element === null || option_element === void 0 ? void 0 : option_element.textContent) === null || _a === void 0 ? void 0 : _a.trim()) || "";
        }
        _this.update_selected_value_wrapper(option_text);
    }
    create_dropdown_selected_value_wrapper() {
        let _this = this;
        let tag_name = "div";
        let tag_class = "easyassist-dropdown-selected";
        _this._dropdown_selected_value_wrapper = _this.create_element(tag_name, tag_class);
        _this.set_selected_option_value();
    }
    add_dropdown_wrapper_to_dom() {
        var _a;
        let _this = this;
        let select_element = _this._select_element;
        if (_this.check_select_element_hidden()) {
            _this._dropdown_wrapper.style.display = "none";
        }
        select_element.style.display = "none";
        (_a = select_element.parentNode) === null || _a === void 0 ? void 0 : _a.prepend(_this._dropdown_wrapper);
        _this._dropdown_wrapper.appendChild(select_element);
    }
    add_event_listeners(only_options=false) {
        let _this = this;
        let dropdown_option_container = _this._dropdown_option_container;
        let options = dropdown_option_container.querySelectorAll('li');

        options.forEach((option) => {
            option.addEventListener('click', function () {
                _this.option_click_event_handler(this);
            });
        });

        if(!only_options) {
            document.addEventListener('click', function (e) {
                let target_element = e.target;
                _this.document_click_event_handler(target_element);
            });
        }
    }
    option_click_event_handler(option_element) {
        function set_selected_element_property() {
            option_element.classList.add(selected_list_class);
            option_element.style.setProperty('background-color', bg_color, 'important');
        }
        let _this = this;
        let selected_list_class = _this._selected_list_class;
        let bg_color = _this._bg_color;
        _this.reset_dropdown();
        set_selected_element_property();
        let option_text = option_element.innerText.trim();
        _this.update_selected_value_wrapper(option_text);
        _this.toggle_option_container();
        // Update selecte drodown
        let option_value = option_element.getAttribute("data-original-value");
        option_value = (option_value || "");
        _this.set_select_element_value(option_value);
    }
    update_selected_value_wrapper(option_text) {
        let _this = this;
        _this._dropdown_selected_value_wrapper.innerHTML = option_text;
    }
    document_click_event_handler(target_element) {
        let _this = this;
        if (target_element == _this._dropdown_selected_value_wrapper) {
            _this._dropdown_option_container.classList.toggle(_this._show_option_container_class);
        }
        else if (target_element.parentElement == _this._dropdown_selected_value_wrapper) {
            _this._dropdown_option_container.classList.toggle(_this._show_option_container_class);
        }
        else {
            _this._dropdown_option_container.classList.remove(_this._show_option_container_class);
        }
    }
    set_select_element_value(option_value) {
        let _this = this;
        _this._select_element.value = option_value;
        var change_event = new Event('change');
        _this._select_element.dispatchEvent(change_event);
    }
    create_element(html_tag, css_class) {
        let html_element = document.createElement(html_tag);
        html_element.className = css_class;
        return html_element;
    }
    show_custom_dropdown() {
        let _this = this;
        _this._dropdown_wrapper.style.display = "";
    }
    hide_custom_dropdown() {
        let _this = this;
        _this._dropdown_wrapper.style.display = "none";
    }
    update_value(option=null) {
        let _this = this;
        _this.reset_dropdown();

        let wrapper_text = _this._placeholder;
        let li_option = _this._dropdown_option_container.querySelector(`[data-original-value='${option}']`);
        
        if(li_option) {
            li_option.click();
        } else {
            _this.update_selected_value_wrapper(wrapper_text);
            _this._select_element.selectedIndex = -1;
        }
    }
    get_value() {
        let _this = this;
        let value = _this._select_element.value;
        return value;
    }
    check_select_element_hidden() {
        let _this = this;
        let element = _this._select_element;
        if (element.style.display == "none") {
            return true;
        }
        return false;
    }
    reset_dropdown() {
        let _this = this;
        let dropdown_option_container = _this._dropdown_option_container;
        let options = dropdown_option_container.querySelectorAll('li');
        let selected_list_class = _this._selected_list_class;
        options.forEach((option) => {
            option.classList.remove(selected_list_class);
            option.style.removeProperty("background-color");
        });
    }
    toggle_option_container() {
        let _this = this;
        let show_option_container_class = _this._show_option_container_class;
        _this._dropdown_option_container.classList.toggle(show_option_container_class);
    }
    add_element_properties() {
        let _this = this;
        Object.defineProperty(_this._select_element, 'reinitialize', {
            value: function() {
                var option_html = _this.get_dropdown_options_html();
                _this._dropdown_option_container.innerHTML = option_html;
                _this.set_selected_option_value();
                _this.add_event_listeners(true);
            }
        });
    }
}

class EasyassistCustomSelectMultiple {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.selected_values = new Set();
        this.selected_data = new Set();
        var self = this;

        var select_element = selector;
        try {
            select_element = document.querySelector(selector);
        } catch(err) {}

        var select_element_id = "";
        if(select_element.id) {
            select_element_id = select_element.id;
        } else {
            select_element_id = generate_id(10);
        }

        var custom_dropdown_wrapper = "";
        var custom_dropdown_option_container = "";
        var custom_dropdown_options = "";
        var custom_dropdown_selected_option = "";
        var custom_dropdown_selected_option_list = [];
        var custom_dropdown_selected_option_wrapper = "";
        var dropdown_option_selected = false;
        var custom_dropdown_selected_value_list = [];

        custom_dropdown_wrapper = create_element('div', 'dropdown easyassist-custom-select-multiple');
        custom_dropdown_option_container = create_element('div', 'dropdown-menu');
        custom_dropdown_selected_option_wrapper = create_element('button', 'btn dropdown-toggle');

        custom_dropdown_selected_option_wrapper.setAttribute('data-toggle', 'dropdown');
        custom_dropdown_selected_option_wrapper.setAttribute('aria-haspopup', 'true');
        custom_dropdown_selected_option_wrapper.setAttribute('aria-expanded', 'false');

        if(select_element.style.display == "none") {
            custom_dropdown_wrapper.style.display = "none";
        }

        select_element.style.display = "none";

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element);

        if(this.placeholder){
            select_element.selectedIndex = -1;
        }

        for(let idx = 0; idx < select_element.children.length; idx ++) {
            let option_el = select_element.children[idx];
            let option_text = option_el.text.trim();
            let option_value = option_el.value;

            if(option_el.selected) {
                dropdown_option_selected = true;
                // custom_dropdown_selected_option = option_text;
                custom_dropdown_selected_option_list.push(option_text);
                // custom_dropdown_selected_value = option_value;
                custom_dropdown_selected_value_list.push(option_value);
                custom_dropdown_options += [
                    '<li  class="dropdown-item">',
                        '<label class="dropdown-item-text" for="dropdown-item-' + select_element_id + '-' + idx + '">',
                            option_text,
                            '<input type="hidden" name="dropdown_item_' + select_element_id + '-' + idx + '" value="' + option_value + '">',
                        '</label>',
                        '<div class="dropdown-item-checkbox">',
                            '<input type="checkbox" id="dropdown-item-' + select_element_id + '-' + idx + '" checked />',
                        '</div>',
                    '</li>',
                ].join('');
            } else {
                custom_dropdown_options += [
                    '<li  class="dropdown-item">',
                        '<label class="dropdown-item-text" for="dropdown-item-' + select_element_id + '-' + idx + '">',
                            option_text,
                            '<input type="hidden" name="dropdown_item_' + select_element_id + '-' + idx + '" value="' + option_value + '">',
                        '</label>',
                        '<div class="dropdown-item-checkbox">',
                            '<input type="checkbox" id="dropdown-item-' + select_element_id + '-' + idx + '" />',
                        '</div>',
                    '</li>',
                ].join('');
            }
        }

        custom_dropdown_selected_option = custom_dropdown_selected_option_list.join(',');


        custom_dropdown_option_container.innerHTML = custom_dropdown_options;
        select_element.insertAdjacentElement('afterend', custom_dropdown_option_container)

        for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
            let li_element = custom_dropdown_option_container.children[idx];

            li_element.children[1].children[0].onchange = function() {
                if(this.checked) {
                    self.selected_data.add(li_element.children[0].innerText);
                    self.selected_values.add(li_element.children[0].children[0].value);
                } else {
                    self.selected_data.delete(li_element.children[0].innerText);
                    self.selected_values.delete(li_element.children[0].children[0].value);
                }

                if(self.get_data().length > 0) {
                    custom_dropdown_selected_option_wrapper.children[0].innerText = self.get_data().join(',');
                } else {
                    custom_dropdown_selected_option_wrapper.children[0].innerText = self.placeholder;
                }
            }

            li_element.addEventListener("click", function(e) {
                e.stopPropagation();
            });
        }

        if(dropdown_option_selected) {
            self.selected_values = new Set(custom_dropdown_selected_value_list);
            self.selected_data = new Set(custom_dropdown_selected_option_list);
            // self.selected_values.add(custom_dropdown_selected_value);
            // self.selected_data.add(custom_dropdown_selected_option);
            custom_dropdown_selected_option_wrapper.innerHTML = '<span>' + custom_dropdown_selected_option + '</span>';
        } else if(this.placeholder) { 
            custom_dropdown_selected_option_wrapper.innerHTML = '<span>' + this.placeholder + '</span>';
        } else {
            custom_dropdown_selected_option_wrapper.innerHTML = '<span>' + custom_dropdown_selected_option + '</span>';
        }

        select_element.insertAdjacentElement('afterend', custom_dropdown_selected_option_wrapper);

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

        this.show_custom_dropdown = function() {
            custom_dropdown_wrapper.style.display = 'flex';
        }

        this.hide_custom_dropdown = function() {
            custom_dropdown_wrapper.style.display = 'none';
        }

        this.get_value = function() {
            return Array.from(self.selected_values);
        }

        this.get_data = function() {
            return Array.from(self.selected_data);
        }

        this.update_value = function(updated_value) {
            var updated_value_set = new Set(updated_value);

            for(let idx = 0; idx < custom_dropdown_option_container.children.length; idx ++) {
                let li_element = custom_dropdown_option_container.children[idx];

                if(updated_value_set.has(li_element.children[0].children[0].value)) {
                    if(!li_element.children[1].children[0].checked) {
                        li_element.children[1].children[0].click();
                    }
                } else {
                    if(li_element.children[1].children[0].checked) {
                        li_element.children[1].children[0].click();
                    }
                }
            }
        }

        function dec_2_hex (dec) {
            return dec.toString(16).padStart(2, "0")
        }

        function generate_id (len) {
            var arr = new Uint8Array((len || 30) / 2);
            window.crypto.getRandomValues(arr);
            return Array.from(arr, dec_2_hex).join('');
        }
    }
}


class EasyassistCustomGroupSelectMultiple {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.selected_values = {}
        this.selected_data = [];

        this.select_element = this.get_select_element(selector);
        this.select_element_id = this.get_select_element_id();

        this.custom_dropdown_wrapper = null;
        this.custom_dropdown_option_container = null;
        this.custom_dropdown_selected_option_wrapper = null;

        this.custom_dropdown_wrapper = create_element('div', 'dropdown easyassist-custom-group-select-multiple easyassist-custom-select-multiple');
        this.custom_dropdown_option_container = create_element('div', 'dropdown-menu');

        this.custom_dropdown_selected_option_wrapper = create_element('button', 'btn dropdown-toggle');
        this.custom_dropdown_selected_option_wrapper.setAttribute('data-toggle', 'dropdown');
        this.custom_dropdown_selected_option_wrapper.setAttribute('aria-haspopup', 'true');
        this.custom_dropdown_selected_option_wrapper.setAttribute('aria-expanded', 'false');
        this.custom_dropdown_selected_option_wrapper.innerHTML += "<span></span>";

        if(this.select_element.style.display == "none") {
            this.custom_dropdown_wrapper.style.display = "none";
        }

        this.select_element.style.display = "none";
        this.select_element.parentNode.prepend(this.custom_dropdown_wrapper);
        this.custom_dropdown_wrapper.appendChild(this.select_element);


        var custom_dropdown_options_html = this.get_option_group_html();
        this.custom_dropdown_option_container.innerHTML = custom_dropdown_options_html;
        this.custom_dropdown_wrapper.appendChild(this.custom_dropdown_option_container);
        this.custom_dropdown_wrapper.appendChild(this.custom_dropdown_selected_option_wrapper);

        this.add_event_listeners();
        this.initialize_selected_values();

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

    initialize_selected_values() {
        var _this = this;
        var li_elements = _this.custom_dropdown_option_container.querySelectorAll("li");

        _this.selected_values = {};
        _this.selected_data = [];

        li_elements.forEach(function(li_element) {
            var option_text = li_element.querySelector("span").innerText.trim();

            var option_cb = li_element.querySelector("input[type='checkbox']");
            var is_option_header = li_element.classList.contains("dropdown-item-header");

            if(!option_cb.checked) {
                return;
            }
            if(is_option_header) {
                let option_header_value = option_cb.getAttribute("data-value");
                _this.selected_values[option_header_value] = new Set();
                _this.selected_data.push(option_text);
            } else {

                var option_value = option_cb.getAttribute("data-value");
                let option_header_value = option_cb.getAttribute("data-header-value");
                _this.selected_values[option_header_value].add(option_value);
            }
        });

        _this.update_selected_option_text();
    }

    update_selected_option_text() {
        var _this = this;
        var selected_option_headers = _this.get_option_header_text();
        var selected_text = _this.placeholder;
        if(selected_option_headers.length > 0) {
            selected_text = selected_option_headers.join(',');                    
        }

        _this.custom_dropdown_selected_option_wrapper.children[0].innerText = selected_text;
    }

    option_change_event_listener(option_cb) {
        var _this = this;
        _this.initialize_selected_values();
    }

    option_header_change_event_listener(option_cb) {
        var _this = this;
        var option_header_value = option_cb.getAttribute("data-value");

        if(!option_cb.checked) {
            delete _this.selected_values[option_header_value];
            _this.hide_child_options(option_header_value);
        } else {
            _this.show_child_options(option_header_value);
        }

        _this.initialize_selected_values();
    }

    hide_child_options(option_header_value) {
        var _this = this;
        var options = _this.custom_dropdown_option_container.querySelectorAll(`[data-header-value="${option_header_value}"]`);
        options.forEach(function(option) {
            option.checked = false;
            option.closest("li").style.display = "none";
        });
    }

    show_child_options(option_header_value) {
        var _this = this;
        var options = _this.custom_dropdown_option_container.querySelectorAll(`[data-header-value="${option_header_value}"]`);
        options.forEach(function(option) {
            option.closest("li").style.display = "";
        });
    }

    add_event_listeners() {
        var _this = this;
        var li_elements = _this.custom_dropdown_option_container.querySelectorAll("li");

        li_elements.forEach(function(li_element) {
            var option_cb = li_element.querySelector("input[type='checkbox']");

            option_cb.onchange = function() {
                var is_option_header = li_element.classList.contains("dropdown-item-header");

                if(is_option_header) {
                    _this.option_header_change_event_listener(option_cb);
                } else {
                    _this.option_change_event_listener(option_cb);
                }
            }

            li_element.addEventListener("click", function(e) {
                e.stopPropagation();
            });
        });
    }

    get_select_element(selector) {
        var select_element = selector;
        try {
            select_element = document.querySelector(selector);
        } catch(err) {}

        return select_element;
    }

    get_select_element_id() {
        function generate_id (len) {
            var arr = new Uint8Array((len || 30) / 2)
            window.crypto.getRandomValues(arr)
            return Array.from(arr, dec_2_hex).join('')
        }

        function dec_2_hex (dec) {
            return dec.toString(16).padStart(2, "0")
        }

        var _this = this;
        var select_element_id = "";
        if(_this.select_element.id) {
            select_element_id = _this.select_element.id;
        } else {
            select_element_id = generate_id(10);
        }

        return select_element_id;
    }

    get_option_group_html() {
        var _this = this;
        var select_element = _this.select_element;
        var select_element_id = _this.select_element_id;

        var html = "";

        var option_groups = select_element.querySelectorAll("optgroup");
        for(let idx = 0; idx < option_groups.length; idx ++) {
            var option_text = option_groups[idx].getAttribute("data-label");
            var option_value = option_groups[idx].getAttribute("data-value");
            var option_header_selected = option_groups[idx].getAttribute("data-selected");
            option_header_selected = (option_header_selected == "true");

            var option_group_cb_status = "";
            if(option_header_selected) {
                option_group_cb_status = "checked";
            }

            html += `
                <li class="dropdown-item-header">
                    <label class="dropdown-item-text">
                        <span>${option_text}</span>
                        <input type="checkbox" ${option_group_cb_status} data-value="${option_value}"/>
                    </label>
                </li>`;

            var options = option_groups[idx].querySelectorAll("option");
            var option_html = _this.get_option_html(options, option_value, option_header_selected);
            html += option_html;
        }

        return html;
    }

    get_option_html(options, option_group_value, option_header_selected) {
        var _this = this;
        var select_element_id = _this.select_element_id;
        var html = "";
        for(let index = 0; index < options.length; index ++) {
            var option_text = options[index].text.trim();
            var option_value = options[index].value;
            var option_selected = options[index].selected;
            var option_cb_status = "";
            var option_display_status = "";
            if(!option_header_selected) {
                option_display_status = "none";
            }

            if(option_selected) {
                option_cb_status = "checked";
            }

            html +=`
                <li class="dropdown-item" style="display: ${option_display_status}">
                    <label class="dropdown-item-text">
                        <span>${option_text}</span>
                        <input type="checkbox" ${option_cb_status} data-value="${option_value}" data-header-value="${option_group_value}"/>
                    </label>
                </li>`;
        }

        return html;
    }

    get_value = function() {
        var _this = this;
        var selected_values = {};
        var selected_option_headers = _this.get_option_header_value();
        for(let idx = 0; idx < selected_option_headers.length; idx ++) {
            var option_header_key = selected_option_headers[idx];
            selected_values[option_header_key] = Array.from(_this.selected_values[option_header_key]);
        }

        return selected_values;
    }

    get_option_header_value() {
        var _this = this;
        return Object.keys(_this.selected_values);
    }

    get_option_header_text() {
        var _this = this;
        return _this.selected_data;
    }

    deselect_all() {
        var _this = this;
        var li_elements = _this.custom_dropdown_option_container.querySelectorAll("li");

        li_elements.forEach(function(li_element) {
            var option_cb = li_element.querySelector("input[type='checkbox']");
            option_cb.checked = false;
        });
    }

    refresh_multiselect() {
        var _this = this;
        _this.initialize_selected_values();
    }

    update_value(value_obj) {
        var _this = this;
        _this.deselect_all();

        var option_groups = Object.keys(value_obj);

        for(let idx = 0; idx < option_groups.length; idx ++) {
            var option_element = _this.custom_dropdown_option_container.querySelector(`[data-value='${option_groups[idx]}']`);
            option_element.checked = true;

            var options = value_obj[option_groups[idx]];
            options.forEach(function(option, idx) {
                var child_option_element = _this.custom_dropdown_option_container.querySelector(`[data-value='${option}']`);
                if(child_option_element) {
                    child_option_element.checked = true;
                }
            })
        }

        _this.refresh_multiselect();
    }
}
