/***************** EasyAssist Custom Select ***********************/

class EasyassistCustomSelect {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.background_color = background_color;

        var select_element = "";
        if(typeof(selector) == "object"){
            select_element = selector;
        } else {
            select_element = document.querySelector(selector);
        }

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

        if(select_element.style.display == "none") {
            custom_dropdown_wrapper.style.display = "none";
        }

        select_element.parentNode.prepend(custom_dropdown_wrapper);
        custom_dropdown_wrapper.appendChild(select_element)

        // if(this.placeholder){
        //     select_element.selectedIndex = -1;
        // }

        for(let idx = 0; idx < select_element.children.length; idx ++) {
            let option_el = select_element.children[idx];
            let option_text = option_el.text.trim();
            let option_value = option_el.value;

            if(option_el.getAttribute("selected") != null) { 
                dropdown_option_selected = true;
                custom_dropdown_selected_option = option_text;
                custom_dropdown_options += [
                    '<li  class="' + selected_list_class + '" style="background-color: ' + background_color + '!important;">',
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
            } else if(e.target.parentElement == custom_dropdown_selected_option_wrapper) {
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
                if(select_element.value != option_value){
                    select_element.value = option_value;
                    var change_event = new Event('change');
                    select_element.dispatchEvent(change_event);
                }
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

        this.show_custom_dropdown = function() {
            custom_dropdown_wrapper.style.display = 'flex';
        }

        this.hide_custom_dropdown = function() {
            custom_dropdown_wrapper.style.display = 'none';
        }

        this.update_value = function(option_value) {
            var options = custom_dropdown_option_container.getElementsByTagName("li");
            for(let idx = 0; idx < options.length; idx ++) {
                var current_option_value = options[idx].querySelector('input[type="hidden"]').value;
                if(current_option_value == option_value) {
                    options[idx].click();
                }
            }
        }
    }
}


class EasyassistCustomSelectMultiple {
    constructor(selector, placeholder, background_color) {
        this.placeholder = placeholder;
        this.selected_values = new Set();
        this.selected_data = new Set();
        var self = this;

        var select_element = document.querySelector(selector);
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
        var custom_dropdown_selected_option_wrapper = "";
        var dropdown_option_selected = false;
        var custom_dropdown_selected_value = "";

        custom_dropdown_wrapper = create_element('div', 'dropdown easyassist-custom-select-multiple');
        custom_dropdown_option_container = create_element('div', 'dropdown-menu');
        custom_dropdown_selected_option_wrapper = create_element('button', 'btn dropdown-toggle');

        custom_dropdown_selected_option_wrapper.setAttribute('data-toggle', 'dropdown');
        custom_dropdown_selected_option_wrapper.setAttribute('aria-haspopup', 'true');
        custom_dropdown_selected_option_wrapper.setAttribute('aria-expanded', 'false');

        if(select_element.style.display == "none") {
            custom_dropdown_wrapper.style.display = "none";
        }

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
                custom_dropdown_selected_option = option_text;
                custom_dropdown_selected_value = option_value;
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

                if(self.get_value().length > 0) {
                    custom_dropdown_selected_option_wrapper.children[0].innerText = self.get_value().join(',');
                } else {
                    custom_dropdown_selected_option_wrapper.children[0].innerText = self.placeholder;
                }
            }

            li_element.addEventListener("click", function(e) {
                e.stopPropagation();
            });
        }

        if(dropdown_option_selected) {
            self.selected_values.add(custom_dropdown_selected_value);
            self.selected_data.add(custom_dropdown_selected_option);
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
            var arr = new Uint8Array((len || 30) / 2)
            window.crypto.getRandomValues(arr)
            return Array.from(arr, dec_2_hex).join('')
        }
    }
}