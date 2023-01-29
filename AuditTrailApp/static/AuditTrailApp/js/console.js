/****************************** ACTIONS ON DOCUMENT & WINDOW EVENT ******************************/
$(document).ready(document_ready);
window.addEventListener("resize", window_resize);
window.addEventListener('popstate', window_pop_state_listener)

function document_ready() {
    adjust_sidebar();
    change_active_sidenav_option();

    $('.datepicker').datepicker({
        endDate: '+0d',
    });

    $(".positive_numeric").on("keypress input", function (event) {
        let keyCode = event.which;

        if ((keyCode !== 8 || keyCode === 32) && (keyCode < 48 || keyCode > 57)) {
            return false;
        }

        let self = $(this);
        self.val(self.val().replace(/\D/g, ""));
    });

    // Initialize Audit Trail Dashboard table
    initialize_audit_trail_table();

    $('.sidebar-toggle-btn').on('click', function() {
        show_collapsed_sidebar();
    });
}

function window_resize() {
    tooltip_utility_change();
}

function window_pop_state_listener() {
    if (window.AUDIT_TRAIL_TABLE) {
        window.AUDIT_TRAIL_TABLE.fetch_table_data();
        show_filters_from_url();
    }
}

document.querySelector("#content-wrapper").addEventListener(
    "scroll",
    function () {
        let datepicket_dropdown = document.querySelector(".datepicker-dropdown");
        if (datepicket_dropdown) {
            document.body.removeChild(datepicket_dropdown);
            $('.datepicker').blur();
        }
    }
)

let is_content_refresh_allowed = true;

function disable_content_refresh() {
    is_content_refresh_allowed = false;
}

function enable_content_refresh() {
    is_content_refresh_allowed = true;
}

$('#campaign_meta_data_table').on('hidden.bs.modal', function () {
    enable_content_refresh();
})

/****************************** TMS SIDE BAR ******************************/

function change_sales_logo_property() {
    let is_sidebar_toggled = false;
    if (document.getElementById("accordionSidebar").getAttribute("class").indexOf("toggled") !== -1) {
        set_cookie("sidebar-audit-trail", "not_toggled", path = "/");
        if (window.matchMedia("(min-width: 720px)")) {
            $('#accordianSidebar').css({
                "position": "fixed"
            });
        }
    } else {
        set_cookie("sidebar-audit-trail", "toggled", path = "/");
        if ((window.matchMedia("(min-width: 720px)"))) {
            $('#accordianSidebar').css({
                "position": "relative"
            });
        }
        is_sidebar_toggled = true;
    }

    if (is_sidebar_toggled) {
        $(".tooltip-navbar").tooltip({

            boundary: 'window',
            placement: "right",
            container: 'body',
            trigger: 'hover'
        });
        $('.tooltip-navbar').tooltip('enable');
        $('.tooltip-navbar').css('width', '100%');
    } else {
        $('.tooltip-navbar').tooltip('dispose');
        $('.tooltip-navbar').css('width', '');
    }
    show_collapsed_sidebar();
}

function show_collapsed_sidebar() {
    setTimeout(function() {
        $(".sidebar .collapse").collapse("show")
    }, 100);
}

function adjust_sidebar() {
    document.getElementById("accordionSidebar").classList.remove("toggled");

    if(get_cookie("sidebar-audit-trail") == ""){
        set_cookie("sidebar-audit-trail", "toggled", path = "/");
    }

    if (get_cookie("sidebar-audit-trail") === "toggled") {
        document.getElementById("accordionSidebar").classList.add("toggled");
        $(".tooltip-navbar").tooltip({
            boundary: 'window',
            placement: "right",
            container: 'body',
            trigger: 'hover'
        });
        $('.tooltip-navbar').tooltip('enable');
        $('.tooltip-navbar').css('width', '100%');
    }

    if (window.innerWidth <= 767) {
        $('.tooltip-navbar').tooltip('dispose');
        $('.tooltip-navbar').css('width', '');

        document.addEventListener("click", function (event) {
            let parent = $(event.target).closest("#accordionSidebar, #sidebarToggleTop");
            if (parent.length === 0) {
                if (document.getElementById("accordionSidebar").classList.contains('toggled')) {
                    document.getElementById("sidebarToggleTop").click();
                }
            }
        });
    }

}

function change_active_sidenav_option() {
    var nav_items = document.getElementsByClassName("nav-item-menu");

    for (let index = 0; index < nav_items.length; index++) {
        nav_items[index].classList.remove("active");
    }

    for (let index = 0; index < nav_items.length; index++) {
        if (nav_items[index].children[0].pathname === window.location.pathname) {
            nav_items[index].classList.add("active");

            if ($(nav_items[index]).closest('.nav-item-submenu')) {
                $(nav_items[index]).closest('.collapse').collapse();
            }
        }
    }
}

/****************************** Campaign CONSOLE TOOLTIP ******************************/

function tooltip_utility_change() {
    if (window.innerWidth <= 767) {
        $('.tooltip-navbar').tooltip('dispose');
        $('.tooltip-navbar').css('width', '');
    } else {
        if (get_cookie("sidebar-audit-trail") === "toggled") {
            document.getElementById("accordionSidebar").classList.add("toggled");
            $(".tooltip-navbar").tooltip({
                boundary: 'window',
                placement: "right",
                container: 'body',
                trigger: 'hover'
            });
            $('.tooltip-navbar').tooltip('enable');
            $('.tooltip-navbar').css('width', '100%');
        }
    }
}


/****************************** Campaign CONSOLE TOAST ******************************/

function show_cognoai_toast(message) {
    let element = document.getElementById("campaign-snackbar");
    element.innerHTML = message;
    element.className = "show";
    setTimeout(function () {
        element.className = element.className.replace("show", "");
    }, 5000);
}

function cognoai_celebrate() {
    document.querySelector(".cogno-celebration").style.display = "flex";
    setTimeout(function () {
        document.querySelector(".cogno-celebration").style.display = "none";
    }, 4000);
}

function show_campaign_error_message(error_element, message, is_error=true) {
    $(error_element).fadeTo(1, 0);

    error_element.innerText = message;
    if(is_error) {
        error_element.style.color = "red";
    } else {
        error_element.style.color = "green";
    }

    $(error_element).fadeTo(500, 1);

    setTimeout(function() {
        error_element.innerText = "";
        hide_campaign_error_message(error_element);
    }, 5000);
}

function hide_campaign_error_message(error_element) {
    $(error_element).fadeTo(1000, 0);
}

/****************************** Campaign CONSOLE COOKIE ******************************/

function get_cookie(cookiename) {
    let cookie_name = cookiename + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let cookie_array = decodedCookie.split(';');
    for (let i = 0; i < cookie_array.length; i++) {
        let c = cookie_array[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(cookie_name) === 0) {
            return c.substring(cookie_name.length, c.length);
        }
    }
    return "";
}

function set_cookie(cookiename, cookievalue, path = "") {
    let domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if (window.location.hostname.split(".").length === 2 || window.location.hostname === "127.0.0.1") {
        domain = window.location.hostname;
    }

    if (path === "") {
        document.cookie = cookiename + "=" + cookievalue + ";domain=" + domain;
    } else {
        document.cookie = cookiename + "=" + cookievalue + ";path=" + path + ";domain=" + domain;
    }
}

/****************************** STRING PROCESS ******************************/

function stripHTML(text) {
    try {
        text = text.trim();
    } catch (err) { }

    let regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function get_url_multiple_vars() {
    let vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        if (!(key in vars)) {
            vars[key] = [];
        }
        vars[key].push(value);
    });
    return vars;
}

function campaign_chars_limit_validation(event, label, is_numeric=false) {
    let element = event.target;
    let value = element.value;
    let count = value.length;
    if(!label) {
        label = "Text";
    }

    let allowed_maximum_characters = 100;
    if(is_numeric) {
        allowed_maximum_characters = 4;
    }

    if(count >= allowed_maximum_characters){
        event.preventDefault();
        show_cognoai_toast(label + " should not be more than " + allowed_maximum_characters + " characters");
    }
}

function campaign_chars_limit_validataion_on_paste(event, label, is_numeric) {
    let element = event.target;
    let value = element.value;

    let clipboard_data = event.clipboardData || event.originalEvent.clipboardData || window.clipboardData;
    let pasted_data = clipboard_data.getData('text') + value;
    let count = pasted_data.length;

    if(!label) {
        label = "Text";
    }

    let allowed_maximum_characters = 100;
    if(is_numeric) {
        allowed_maximum_characters = 4;
    }

    if(count > allowed_maximum_characters){
        event.preventDefault();
        show_cognoai_toast(label + " should not be more than " + allowed_maximum_characters + " characters");
    }
}

/****************************** Bootstrap Dropdown Script ******************************/

(function () {
    // hold onto the drop down menu
    let dropdownMenu;

    // and when you show it, move it to the body
    $(window).on('show.bs.dropdown', function (e) {

        // grab the menu
        dropdownMenu = $(e.target).find('.campaign-dropdown-menu');

        // detach it and append it to the body
        $('body').append(dropdownMenu.detach());

        // grab the new offset position
        let eOffset = $(e.target).offset();

        // make sure to place it where it would normally go (this could be improved)
        dropdownMenu.css({
            'display': 'block',
            'top': eOffset.top + $(e.target).outerHeight(),
            'left': eOffset.left
        });
    });

    // and when you hide it, reattach the drop down, and hide it normally
    $(window).on('hide.bs.dropdown', function (e) {
        $(e.target).append(dropdownMenu.detach());
        dropdownMenu.hide();
    });
})();

/****************************** CognoAI BASE TABLE ******************************/

class AuditTrailAppBase {
    update_table_attribute(table_elements) {
        for (let idx = 0; idx < table_elements.length; idx++) {
            let thead_el = table_elements[idx].getElementsByTagName('thead');
            if (thead_el.length == 0) {
                continue;
            }
            thead_el = thead_el[0];
            let tbody_el = table_elements[idx].getElementsByTagName('tbody');
            if (tbody_el.length == 0) {
                continue;
            }

            tbody_el = tbody_el[0];
            for (let row_index = 0; row_index < tbody_el.rows.length; row_index++) {
                if (tbody_el.rows[row_index].children.length != thead_el.rows[0].children.length) {
                    continue;
                }
                for (let col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
                    let column_element = tbody_el.rows[row_index].children[col_index];
                    let th_text = thead_el.rows[0].children[col_index].innerText;
                    column_element.setAttribute("data-content", th_text);
                }
            }
        }
    }

    apply_pagination(pagination_container, pagination_metadata, onclick_handler, target_obj) {
        let metadata = pagination_metadata;
        let html = "";

        let filter_default_text = "Showing " + metadata.start_point + " to " + metadata.end_point + " of " + metadata.total_count + " entries";

        if (metadata.has_previous) {
            html += [
                '<li class="page-item">',
                '<a class="page-link previous_button" data-page="' + metadata.previous_page_number + '" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Previous</span>',
                '<span class="sr-only">Previous</span>',
                '</a>',
                '</li>'
            ].join('');
        } else {
            html += [
                '<li class="page-item disabled">',
                '<a class="page-link previous_button" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Previous</span>',
                '<span class="sr-only">Previous</span>',
                '</a>',
                '</li>'
            ].join('');
        }

        if ((metadata.number - 4) > 1) {
            html += '<li class="page-item"><a class="page-link" data-page="' + (metadata.number - 5) + '" href="javascript:void(0)">&hellip;</a></li>';
        }

        for (let index = metadata.page_range[0]; index < metadata.page_range[1]; index++) {
            if (metadata.number === index) {
                html += [
                    '<li class="active purple darken-3 page-item">',
                    '<a data-page="' + index + '" href="javascript:void(0)" class="page-link">' + index + '</a>',
                    '</li>',
                ].join('');
            } else if (index > (metadata.number - 5) && index < (metadata.number + 5)) {
                html += [
                    '<li class="page-item">',
                    '<a href="javascript:void(0)" data-page="' + index + '" class="page-link">' + index + '</a>',
                    '</li>',
                ].join('');
            }
        }

        if (metadata.num_pages > (metadata.number + 4)) {
            html += [
                '<li class="page-item">',
                '<a href="javascript:void(0)" data-page="' + (metadata.number + 5) + '" class="page-link">&hellip;</a>',
                '</li>',
            ].join('');
        }

        if (metadata.has_next) {
            html += [
                '<li class="page-item">',
                '<a class="page-link next_button" data-page="' + metadata.next_page_number + '" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Next</span>',
                '<span class="sr-only">Next</span>',
                '</a>',
                '</li>'
            ].join('');
        } else {
            html += [
                '<li class="page-item disabled">',
                '<a class="page-link next_button" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Next</span>',
                '<span class="sr-only">Next</span>',
                '</a>',
                '</li>'
            ].join('');
        }

        html = [
            '<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text=\'' + filter_default_text + '\'>',
            filter_default_text,
            '</div>',
            '<div class="col-md-6 col-sm-12">',
            '<div class="d-flex justify-content-end">',
            '<nav aria-label="Page navigation example">',
            '<ul class="pagination">',
            html,
            '</ul>',
            '</nav>',
            '</div>',
            '</div>',
        ].join('');

        pagination_container.innerHTML = html;

        let pagination_links = pagination_container.querySelectorAll('a.page-link');

        pagination_links.forEach((pagination_link_element) => {
            let page_number = pagination_link_element.getAttribute('data-page');
            if (page_number != null && page_number != undefined) {
                pagination_link_element.addEventListener('click', function (event) {
                    onclick_handler('page', page_number, target_obj);
                })
            }
        });
    }
}

/************************************************************ DASHBOARD SETTINGS STARTS ************************************************************/

class AuditTrailAppTable extends AuditTrailAppBase {
    constructor(table_container, searchbar_element, pagination_container) {
        super();

        this.table_container = table_container;
        this.table = null;

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;
        this.searchbar_element = searchbar_element;

        this.data_table_obj = null;

        this.init();
    }

    init() {
        let _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.fetch_table_data();
    }

    initialize_table_header_metadata() {
        let _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    update_url_with_filters(filters) {
        let key_value = "";
        for (let filter_key in filters) {
            let filter_data = filters[filter_key];
            for (let index = 0; index < filter_data.length; index++) {
                key_value += filter_key + "=" + filter_data[index] + "&";
            }
        }

        let newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
        window.history.pushState({ path: newurl }, '', newurl);
    }

    add_filter_and_fetch_data(key, value, target_obj = null) {
        let _this = this;
        if (target_obj) {
            _this = target_obj;
        }

        let filters = get_url_multiple_vars();
        if (key == "page") {
            filters.page = [value];
        }

        _this.update_url_with_filters(filters);
        _this.fetch_table_data();
    }

    fetch_table_data() {
        let _this = this;

        let scroll_pos = document.getElementById('content-wrapper').scrollTop;
        let filters = get_url_multiple_vars();

        let request_params = {
            'page': ((filters["page"] && filters["page"][0]) || 1)
        };

        if("selected_date_filter" in filters) {
            request_params['filter_date_type'] = filters["selected_date_filter"][0]
        }

        if ("selected_apps" in filters) {
            request_params['selected_apps'] = filters["selected_apps"]
        }

        if ("start_date" in filters && "end_date" in filters) {
            request_params['start_date'] = filters["start_date"][0];
            request_params['end_date'] = filters["end_date"][0];
        }

        let json_params = JSON.stringify(request_params);
        let encrypted_data = cognoai_audit_trail_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        let params = JSON.stringify(encrypted_data);

        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/audit-trail/get-audit-trail/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = cognoai_audit_trail_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_target_data_list(response.audit_trail_list);
                    document.getElementById('content-wrapper').scrollTop = scroll_pos;
                }
            }
        }
        xhttp.send(params);
    }

    set_target_data_list(new_target_data_list) {
        console.log("new_target_data_list = ", new_target_data_list);
        let _this = this;
        if (new_target_data_list) {
            _this.target_data_list = new_target_data_list;
        }
        _this.initialize_table();
    }

    get_target_data_list() {
        let _this = this;
        return _this.target_data_list;
    }

    get_audit_trail_detail(audit_trail_id){
        let _this = this;
        for(let index=0; _this.target_data_list.length; index++){
            if(_this.target_data_list[index]["id"] == audit_trail_id) return _this.target_data_list[index];
        }
        return null;
    }

    initialize_table() {
        let _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="campaign_table" width="100%" cellspacing="0"></table>';
        _this.table = _this.table_container.querySelector("table");

        if (!_this.table) return;
        if (_this.active_user_metadata.lead_data_cols.length === 0) return;

        _this.initialize_head();
        _this.initialize_body();
        _this.update_table_attribute([_this.table]);
        _this.add_event_listeners_in_rows();
    }

    initialize_head() {
        let _this = this;

        let th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            let name = column_info_obj.name;
            let display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '">' + display_name + '</th>'
        });

        let thead_html = [
            '<thead>',
            '<tr>',
            th_html,
            '</tr>',
            '</thead>',
        ].join('');

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        let _this = this;

        let row_wise_data = this.get_all_row_data();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": row_wise_data,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": true,
            'columnDefs': [{
                "targets": 0,
                "className": "text-left text-md-center",
                "width": "4%"
            },
            ],

            initComplete: function (settings) {
                $(_this.table).colResizable({
                    disable: true
                });
                $(_this.table).colResizable({
                    liveDrag: true,
                    minWidth: 100,
                    postbackSafe: true,
                });
                _this.apply_table_pagination();
                $(".show-more-button").tooltip();
            },
        });
    }

    add_event_listeners_in_rows() {
        var _this = this;

        // Event listener in searchbar element
        _this.searchbar_element.onkeyup = function (event) {
            _this.show_filtered_results(event);
        }
    }

    apply_table_pagination() {
        let _this = this;
        if(_this.target_data_list.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        let container = _this.pagination_container;
        let metadata = _this.pagination_metadata;
        let onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    get_target_row_html(name, target_row_data) {
        let data = target_row_data[name];
        if(data == null) {
            data = "-";
        }

        let html = "";
        switch (name) {
            case "app_name":
                html = data
                break;

            case "user":
                html = data
                break;

            case "datetime":
                html = data
                break;

            case "action_type":
                html = data
                break;

            case "description":
                html = data
                break;

            case "request_data_dump":
                data = data.substr(0, 20);
                html = '<a style="color: #4e73df;cursor: pointer;" data-toggle="modal" data-target="#audit_trail_info_modal" onclick="show_audit_trail_data_in_modal(' + target_row_data['id'] + ')">' + data + '</a>';
                break;

            case "api_end_point":
                html = data
                break;

            case "ip_address":
                html = data
                break;

            case "more_details":
                html = [
                    '<div style="text-align: center;" class="show-more-button" data-toggle="tooltip" title="Show more details" data-placement="bottom">',
                        '<a style="color: #4e73df;cursor: pointer;margin-left: 12px;" data-toggle="modal" data-target="#audit_trail_info_modal" onclick="show_audit_trail_data_in_modal(' + target_row_data['id'] + ')">',
                            '<svg width="20" height="19" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="#2755cb">',
                                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>',
                            '</svg>',
                        '</a>',
                    '</div>'
                ].join('');
                break;
                
            // case "more_details":
            //     html = [
            //         '<div style="text-align: center;" class="show-more-button" data-toggle="tooltip" title="Show more details" data-placement="bottom">',
            //             '<a style="color: #4e73df;cursor: pointer;margin-left: 12px;" data-toggle="modal" data-target="#audit_trail_info_modal" onclick="show_audit_trail_data_in_modal(' + target_row_data['id'] + ')">',
            //                 '<svg width="20" height="19" viewBox="0 0 20 19" fill="none" xmlns="http://www.w3.org/2000/svg">',
            //                     '<path d="M15.1785 16.1922H2.6428V5.80688H5.14513C5.14513 5.80688 5.80952 4.77297 7.23763 3.49904H1.67852C1.42277 3.49904 1.1775 3.62061 0.996666 3.83701C0.815828 4.05342 0.714233 4.34692 0.714233 4.65296L0.714233 17.3461C0.714233 17.6521 0.815828 17.9456 0.996666 18.162C1.1775 18.3784 1.42277 18.5 1.67852 18.5H16.1428C16.3986 18.5 16.6438 18.3784 16.8247 18.162C17.0055 17.9456 17.1071 17.6521 17.1071 17.3461V13.0235L15.1785 14.9217V16.1922ZM13.5981 8.17242V12.27L19.9999 6.26845L13.5981 0.5V4.11292C5.82495 4.11292 5.82495 13.3074 5.82495 13.3074C8.02545 8.98247 9.3793 8.17242 13.5981 8.17242Z" fill="#2755cb"></path>',
            //                 '</svg>',
            //             '</a>',
            //         '</div>'
            //     ].join('');
            //     break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_target_row_data(target_row_data) {
        let _this = this;

        let row_data_list = [];
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected === false) return;
                let name = column_info_obj.name;
                row_data_list.push(_this.get_target_row_html(name, target_row_data));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return row_data_list;
    }

    get_all_row_data() {
        let _this = this;
        let rows = [];
        _this.target_data_list.forEach((target_row_data) => {
            rows.push(_this.get_target_row_data(target_row_data));
        })
        return rows;
    }

    show_filtered_results(event) {
        let _this = this;
        let value = event.target.value;

        if (!_this.data_table_obj) {
            return;
        }

        _this.data_table_obj.search(value).draw();

        let pagination_entry_container = _this.pagination_container.querySelector(".show-pagination-entry-container");

        if (pagination_entry_container) {
            let showing_entry_count = _this.table.querySelectorAll("tbody tr[role='row']").length;
            let total_entry = _this.pagination_metadata.end_point - _this.pagination_metadata.start_point + 1;

            if (value.length !== 0) {
                pagination_entry_container.innerHTML = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
            } else {
                pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
            }
        }
    }

    initialize_lead_data_metadata_update_modal() {
        let _this = this;
        let lead_data_cols = _this.active_user_metadata.lead_data_cols;
        let container = document.querySelector("#lead_dala_table_meta_div");
        let selected_values = [];
        let unselected_values = [];
        lead_data_cols.forEach((obj) => {
            if (obj.selected === true) {
                selected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            } else {
                unselected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            }
        });

        initialize_custom_tag_input(selected_values, unselected_values, container)
    }

    update_table_meta_deta(lead_data_cols) {
        let _this = this;
        _this.active_user_metadata.lead_data_cols = lead_data_cols;

        _this.save_table_meta_data();
        _this.initialize_table();
    }

    save_table_meta_data() {
        let _this = this;
        let lead_data_cols = _this.active_user_metadata.lead_data_cols
        window.localStorage.setItem("audit_trail_table_meta_data", JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        let _this = this;
        let lead_data_cols = window.localStorage.getItem("audit_trail_table_meta_data");

        if (lead_data_cols == null) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {
        let lead_data_cols = [
            ['app_name', 'App Type', true],
            ['user', 'User', true],
            ['datetime', 'Time Stamp', true],
            ['action_type', 'Event Category', true],
            ['description', 'Change Summary', true],
            ['more_details', 'Details', true],
            // ['request_data_dump', 'Change Object', true],
            ['api_end_point', 'API end point', false],
            ['ip_address', 'IP Address', false],
        ]

        let default_lead_data_cols = [];
        lead_data_cols.forEach((lead_data_col, index) => {
            default_lead_data_cols.push({
                name: lead_data_col[0],
                display_name: lead_data_col[1],
                index: index,
                selected: lead_data_col[2],
            });
        });
        return default_lead_data_cols;
    }
}

function initialize_audit_trail_table() {
    if (window.location.pathname.indexOf("/audit-trail/dashboard") !== 0) {
        return;
    }

    let table_container = document.querySelector("#audit_trail_dashboard_table");
    let searchbar = document.querySelector("#audit-trail-search-bar");
    let pagination_container = document.getElementById("audit_trail_table_pagination_div");

    window.AUDIT_TRAIL_TABLE = new AuditTrailAppTable(
        table_container, searchbar, pagination_container);
    show_filters_from_url();
}

function show_audit_trail_data_in_modal(audit_trail_id){
    let audit_trail_data = window.AUDIT_TRAIL_TABLE.get_audit_trail_detail(audit_trail_id);
    let request_data_dump = audit_trail_data["request_data_dump"];
    let api_end_point = audit_trail_data["api_end_point"];
    let ip_address = audit_trail_data["ip_address"];

    new JsonEditor('#audit_trail_info_modal .change-object', JSON.parse(request_data_dump));
    document.querySelector("#audit_trail_info_modal .ip-address").innerHTML=ip_address;
    document.querySelector("#audit_trail_info_modal .api-end-point").innerHTML=api_end_point;
}

/****************************** CognoAI Custom Tag Input ******************************/

/*
    CognoAICustomTagInput

    Description :
        - class to maintain tags input

    Required Parameters :
        container : container in which this tag input will be added
        selected_values : selected value will be shown as a tag button
        unselected_values : not selected value will be shown as select

    initialization :
        - in initialize_lead_data_metadata_update_modal function
        - called after receiving console meta data
        - window.LEAD_DATA_METADATA_INPUT
*/

function initialize_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

function save_lead_data_table_metadata() {

    let lead_data_cols = window.AUDIT_TRAIL_TABLE.active_user_metadata.lead_data_cols;

    let selected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj) => {
        selected_values.push(obj.key);
    });

    if (selected_values.length < 2) {
        show_cognoai_toast("Atleast two columns needs to be selected.");
        return;
    }

    lead_data_cols.forEach((item, index) => {
        if (selected_values.indexOf(item.name) >= 0) {
            item.selected = true;
            item.index = selected_values.indexOf(item.name);
        } else {
            item.selected = false;
            item.index = window.LEAD_DATA_METADATA_INPUT.selected_values.length;
        }
    })

    lead_data_cols.sort((obj1, obj2) => {
        return obj1.index - obj2.index;
    });

    window.AUDIT_TRAIL_TABLE.update_table_meta_deta(lead_data_cols)
}

class CognoAICustomTagInput {
    constructor(container, selected_values, unselected_values) {
        this.container = container;
        this.selected_values = selected_values;
        this.unselected_values = unselected_values;
        this.button_display_div = null;
        this.drag_obj = null;
        this.init();
    }

    init() {
        let _this = this;
        _this.initialize();
    }

    add_event_listeners() {
        let _this = this;
        let delete_buttons = _this.button_display_div.querySelectorAll(".tag_delete_button");
        delete_buttons.forEach((delete_button) => {
            delete_button.addEventListener('click', function (event) {
                _this.tag_delete_button_click_listner(event)
            });
        });

        let select_element = _this.select_element;
        select_element.addEventListener("change", function (event) {
            _this.tag_select_listnet(event);
        })
    }

    tag_delete_button_click_listner(event) {
        let _this = this;
        let target = event.target;
        let key = target.previousElementSibling.getAttribute("key");
        let index = _this.find_index_of_element(key, _this.selected_values);
        if (index !== -1) {
            let target_obj = _this.selected_values[index];
            _this.selected_values.splice(index, 1);
            _this.unselected_values.push(target_obj);
            _this.initialize();
        }
    }

    tag_select_listnet(event) {
        let _this = this;
        let target = event.target;
        let key = target.value;
        let index = _this.find_index_of_element(key, _this.unselected_values);
        if (index !== -1) {
            let target_obj = _this.unselected_values[index];
            _this.selected_values.push(target_obj);
            _this.unselected_values.splice(index, 1);
            _this.initialize();
        }
    }

    find_index_of_element(key, list) {
        for (let index = 0; index < list.length; index++) {
            if (list[index].key === key) return index;
        }
        return -1;
    }

    find_unselected_element_by_key(key) {
        let _this = this;
        let target_obj = null;
        _this.unselected_values.forEach((obj) => {
            if (obj.key === key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    find_selected_element_by_key(key) {
        let _this = this;
        let target_obj = null;
        _this.selected_values.forEach((obj) => {
            if (obj.key === key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    onmouseover_tag = function (element) {
        let handler = element.querySelector("svg");
        handler.style.display = "";
    }

    onmouseout_tag = function (element) {
        let handler = element.querySelector("svg");
        handler.style.display = "none";
    }

    get_tag_input_html() {
        let _this = this;
        let tag_input_html = '<ul class="cognoai-custom-tag-input mt-3">';

        _this.selected_values.forEach((obj, index) => {
            tag_input_html += [
                '<li class="bg-primary" onmouseover="window.LEAD_DATA_METADATA_INPUT.onmouseover_tag(this)" onmouseout="window.LEAD_DATA_METADATA_INPUT.onmouseout_tag(this)">',
                '<svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 2px; display: none;">',
                '<path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167 6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="white"/>',
                '</svg>',
                '<span key=' + obj.key + ' class="value_display_span">',
                obj.value,
                '</span>',
                '<span class="tag_delete_button" index=' + index + '>',
                'x',
                '</span>',
                '</li>',
            ].join('');
        });

        tag_input_html += '</ul>';
        return tag_input_html;
    }

    get_tag_select_html() {
        let _this = this;
        let tag_select_html = '<select class="form-control">';
        tag_select_html += '<option disabled selected> Choose column name </option>';

        _this.unselected_values.forEach((obj, index) => {
            tag_select_html += '<option value="' + obj.key + '"> ' + obj.value + '</option>';
        });

        tag_select_html += '</select>';
        return tag_select_html;
    }

    initialize() {
        let _this = this;
        let html = "";
        html += _this.get_tag_input_html();
        html += _this.get_tag_select_html();
        _this.container.innerHTML = html;

        _this.button_display_div = _this.container.querySelector("ul");
        _this.select_element = _this.container.querySelector("select");
        _this.add_event_listeners();
        _this.select_element_obj = new EasyassistCustomSelect(_this.select_element, null, window.CONSOLE_THEME_COLOR);
        _this.drag_obj = new CognoAiDragableTagInput(_this.button_display_div, function (event) {
            _this.drag_finish_callback(event)
        });
    }

    drag_finish_callback = function (event) {
        let _this = this;

        let elements = _this.button_display_div.children;
        let new_list = [];
        for (let idx = 0; idx < elements.length; idx++) {
            let element = elements[idx];
            let value_display_span = element.querySelector(".value_display_span");
            let key = value_display_span.getAttribute("key");
            let index = _this.find_index_of_element(key, _this.selected_values);
            new_list.push(_this.selected_values[index]);
        }

        _this.selected_values = new_list;
    }
}

class CognoAiDragableTagInput {
    constructor(container, drag_finish_callback) {
        this.container = container
        this.element = null;
        this.currX = 0;
        this.currY = 0;
        this.clientX = 0;
        this.clientY = 0;
        this.pageX = 0;
        this.offset = 12;
        this.is_dragging = false;
        this.drag_container = null;
        this.prevX = 0;
        this.prevY = 0;
        this.drag_finish_callback = drag_finish_callback;

        let _this = this;

        document.addEventListener("mouseleave", function (e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.drag_container = document;

        _this.drag_container.addEventListener("mousemove", function (e) {
            _this.drag_element('move', e);
        });

        _this.drag_container.addEventListener("mouseup", function (e) {
            _this.drag_element('up', e);
        });

        _this.initialize();
    }

    initialize() {
        let _this = this;
        let elements = _this.container.querySelectorAll(".drag-handle");
        if (elements.length == 0) {
            elements = _this.container.children;
        }
        for (let index = 0; index < elements.length; index++) {
            let element = elements[index];
            let target_element = _this.get_target_element(element);

            element.addEventListener("mousedown", function (e) {
                _this.drag_element('down', e);
            });

            element.addEventListener("mouseup", function (e) {
                _this.drag_element('up', e);
            });

            target_element.addEventListener("touchstart", function (e) {
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('down', e);
            });

            target_element.addEventListener("touchmove", function (e) {
                let data = {
                    movementX: e.touches[0].clientX - _this.prevX,
                    movementY: e.touches[0].clientY - _this.prevY,
                    clientX: e.touches[0].clientX,
                    clientY: e.touches[0].clientY,
                }
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('move', data);
            });

            target_element.addEventListener("touchend", function (e) {
                _this.prevX = 0;
                _this.prevY = 0;
                _this.drag_element('out', e);
            });

            element.style.cursor = "move";
        }
    }

    get_target_element(element) {
        let _this = this;
        let handle = element;
        while (handle.parentElement != _this.container)
            handle = handle.parentElement;
        return handle;
    }

    drag_element(direction, e) {
        let _this = this;
        if (direction == 'down') {
            _this.is_dragging = true;
            _this.element = _this.get_target_element(e.target);
            if (!_this.dummy_element) {
                _this.dummy_element = document.createElement("span");
                _this.dummy_element.className = "cognoai-drag-dummy-element";
            }
        }

        if (direction == 'up' || direction == "out") {
            if (_this.is_dragging == false) {
                return;
            }

            _this.dummy_element.insertAdjacentElement("beforebegin", _this.element);
            _this.element.classList.remove("cognoai-drag-helper");
            _this.element.style.top = "";
            _this.element.style.left = "";
            _this.currX = 0;
            _this.currY = 0;
            _this.offset = 12;
            _this.is_dragging = false;
            _this.drag_container = null;
            _this.prevX = 0;
            _this.prevY = 0;
            _this.is_dragging = false;

            _this.element = null;
            if (_this.dummy_element.parentElement) {
                _this.dummy_element.parentElement.removeChild(_this.dummy_element);
            }
            _this.dummy_element = null;

            if (_this.drag_finish_callback) {
                try {
                    _this.drag_finish_callback()
                } catch (err) { }
            }
        }

        if (direction == 'move') {
            if (_this.is_dragging) {

                let left = _this.element.offsetLeft;
                let top = _this.element.offsetTop;

                _this.element.classList.add("cognoai-drag-helper");
                _this.currX = e.movementX + left;
                _this.currY = e.movementY + top;

                _this.clientX = e.clientX;
                _this.clientY = e.clientY;

                _this.pageX = e.pageX;

                _this.drag();
                _this.compute();
            }
        }
    }

    drag() {
        let _this = this;
        // _this.currX = Math.max(_this.currX, 0);

        _this.element.style.left = _this.currX + "px";
        _this.element.style.top = _this.currY + "px";
    }

    compute() {
        let _this = this;

        _this.element.hidden = true;
        let elemBelow = document.elementFromPoint(_this.clientX, _this.clientY);
        _this.element.hidden = false;

        try {
            let target_element = _this.get_target_element(elemBelow);
            if (target_element) {

                let pWidth = $(target_element).innerWidth(); //use .outerWidth() if you want borders
                let pOffset = $(target_element).offset();
                let x = _this.pageX - pOffset.left;
                if (pWidth / 2 > x) {
                    target_element.insertAdjacentElement("beforebegin", _this.dummy_element);
                } else {
                    target_element.insertAdjacentElement("afterend", _this.dummy_element);
                }
            }
        } catch (err) { }
    }
}

/* Campaign Filter Functions */

function show_custom_date(el) {
    if (el.id === 'campaign_overview_custom_date_btn') {
        document.getElementById('campaign-custom-date-select-area-flow').style.display = 'flex';
    } else {
        document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';
    }
}

function apply_campaign_filter() {
    let selected_date_filter = $("input[type='radio'][name='campaign-overview-filter']:checked").val();
    let status_elems = document.getElementsByName('campaign-overview-filter-status');
    let filters = get_url_multiple_vars();

    if (!selected_date_filter) {
        show_cognoai_toast('Please select date range');
        return;
    }

    let start_date, end_date;
    if (selected_date_filter === '5') {
        start_date = document.getElementById('campaign_filter_custom_start_date').value;

        if (!start_date) {
            show_cognoai_toast('Please select start date');
            return;
        }

        end_date = document.getElementById('campaign_filter_custom_end_date').value;

        if (!end_date) {
            show_cognoai_toast('Please select end date');
            return;
        }

        if(Date.parse(start_date) > Date.parse(end_date)){
            show_cognoai_toast('Start date cannot be less than end date.')
            return;
        }
        filters["start_date"] = [start_date];
        filters["end_date"] = [end_date];
    } else {
        filters["start_date"] = [];
        filters["end_date"] = [];
    }

    filters["selected_date_filter"] = [selected_date_filter]

    let selected_apps = [];
    for (let elem of status_elems) {
        if (elem.checked){
            selected_apps.push(elem.value);
        }
    }
    filters["selected_apps"] = selected_apps;

    window.AUDIT_TRAIL_TABLE.update_url_with_filters(filters);
    window.AUDIT_TRAIL_TABLE.fetch_table_data();
}

function clear_filter() {
    document.getElementById('campaign_overview_week').checked = true;
    document.getElementById('campaign_filter_custom_start_date').value = DEFAULT_START_DATE;
    document.getElementById('campaign_filter_custom_end_date').value = DEFAULT_END_DATE;
    document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';

    let filters = {}

    window.AUDIT_TRAIL_TABLE.update_url_with_filters(filters);
    window.AUDIT_TRAIL_TABLE.fetch_table_data();
    show_filters_from_url();
}

function show_filters_from_url(){
    let status_elems = document.getElementsByName('campaign-overview-filter-status');
    let filters = get_url_multiple_vars();

    for (let elem of status_elems) {
        let selected_apps = [];
        if("selected_apps" in filters)
            selected_apps = filters["selected_apps"];
        if(selected_apps.indexOf(elem.value) !== -1)
            elem.checked = true;
        else
            elem.checked = false;
    }

    if("start_date" in filters){
        document.getElementById('campaign_filter_custom_start_date').value = filters["start_date"][0];
    }

    if("end_date" in filters){
        document.getElementById('campaign_filter_custom_end_date').value = filters["end_date"][0];
    }

    if("selected_date_filter" in filters){
        let selected_date_filter = filters["selected_date_filter"][0];

        document.getElementById('campaign_overview_week').checked = false;
        document.getElementById('campaign_overview_month').checked = false;
        document.getElementById('campaign_overview_three_month').checked = false;
        document.getElementById('campaign_overview_beg').checked = false;
        document.getElementById('campaign_overview_custom_date_btn').checked = false;

        if(selected_date_filter === "5"){
            document.getElementById('campaign_overview_custom_date_btn').checked = true;
            document.getElementById('campaign-custom-date-select-area-flow').style.display = 'flex';
        } else {
            if(selected_date_filter === "1") document.getElementById('campaign_overview_week').checked = true;
            if(selected_date_filter === "2") document.getElementById('campaign_overview_month').checked = true;
            if(selected_date_filter === "3") document.getElementById('campaign_overview_three_month').checked = true;
            if(selected_date_filter === "4") document.getElementById('campaign_overview_beg').checked = true;
            document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';
        }
    }
}

function check_select_date_range(el, export_type="2") {
    let selected_range = el.value;

    if(selected_range == '4') {
        document.getElementById('from-date-div-'+export_type).style.display = 'block';
        document.getElementById('to-date-div-'+export_type).style.display = 'block';
        document.getElementById('email-id-div-'+export_type).style.display = 'block';
    } else {
        document.getElementById('from-date-div-'+export_type).style.display = 'none';
        document.getElementById('to-date-div-'+export_type).style.display = 'none';
        document.getElementById('email-id-div-'+export_type).style.display = 'none';
    }
}

function validate_email(email_ids) {
    let emain_id_list = email_ids.split(",");
    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

    for(let index=0; index<emain_id_list.length; index++){
        if(!regEmail.test(emain_id_list[index])) return false;
    }
    return true;
}

function export_multi_request(el) {
    let start_date, end_date;
    let email_ids = document.getElementById('filter-data-email-2').value;
    let request_date_type = document.getElementById('select-date-range-2').value;

    if (request_date_type == '0') {
        document.getElementById('general-error-message-2').innerHTML = 'Please select date range';
        return;
    } else {
        document.getElementById('general-error-message-2').innerHTML = '';
    }

    if (request_date_type == '4') {
        start_date = document.getElementById('startdate').value;

        if (!start_date) {
            document.getElementById('general-error-message-2').innerHTML = 'Please select a start date';
            return;
        } else {
            document.getElementById('general-error-message-2').innerHTML = '';
        }

        if (!is_valid_date(start_date)) {
            document.getElementById('general-error-message-2').innerHTML = 'Please select valid start date';
            return;
        } else {
            document.getElementById('general-error-message-2').innerHTML = '';
        }

        end_date = document.getElementById('enddate').value;

        if (!end_date) {
            document.getElementById('general-error-message-2').innerHTML = 'Please select a end date';
            return;
        } else {
            document.getElementById('general-error-message-2').innerHTML = '';
        }

        if (!is_valid_date(end_date)) {
            document.getElementById('general-error-message-2').innerHTML = 'Please select valid end date';
            return;
        } else {
            document.getElementById('general-error-message-2').innerHTML = '';
        }

        if(Date.parse(start_date) > Date.parse(end_date)){
            document.getElementById('general-error-message-2').innerHTML = 'Start date must be less than end date.';
            return;
        } else {
            document.getElementById('general-error-message-2').innerHTML = '';
        }

        start_date = change_date_format_original(start_date);
        end_date = change_date_format_original(end_date);

        if (email_ids === '') {
            document.getElementById('general-error-message-2').innerHTML = 'Please enter your Email ID';
            return;
        } else {
            email_ids = email_ids.replace(/\s/g, "");
            document.getElementById('general-error-message-2').innerHTML = '';
        }

        if (!validate_email(email_ids)) {
            document.getElementById('general-error-message-2').innerHTML = 'Please enter valid Email ID';
            return;
        } else {
            document.getElementById('general-error-message-2').innerHTML = '';
        }
    }

    send_export_request_to_server(email_ids, request_date_type, start_date, end_date);
}

function send_export_request_to_server(email_id, request_date_type, start_date, end_date) {
    let request_params = {
        'email_id': email_id,
        'start_date': start_date,
        'end_date': end_date,
        'request_date_type': request_date_type,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = cognoai_audit_trail_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    let params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/audit-trail/export-audit-trail/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            let response = JSON.parse(this.responseText);
            response = cognoai_audit_trail_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                show_cognoai_toast('You will receive the audit trail data dump on the above email ID within 24 hours.');
                setTimeout(function() {
                    $('#campaign_multi_export_modal').modal('hide');
                }, 2000);
            } else {
                show_cognoai_toast("Unable to download support history");
            }
        }
    }
    xhttp.send(params);
}

function change_date_format_original(date) {
    let dateParts = date.split("-");
    date = dateParts[2]+"-"+dateParts[1]+"-"+dateParts[0];
    return date.trim();
}

function is_valid_date(date) {
    let date2 = change_date_format_original(date)
    date = new Date(date);
    date2 = new Date(date2);
    let check_date = date instanceof Date && !isNaN(date)
    let check_date2 =date2 instanceof Date && !isNaN(date2)
    return check_date || check_date2;
}

/* Campaign Filter Functions Ends */


function export_support_history() {

    var general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    var selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    var startdate = $('#startdate').val();
    var enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);

    var email_field = document.getElementById('filter-data-email');

    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)
    var today_date = new Date()
    if (selected_filter_value == "4") {
        if (startdate == "" || enddate == "") {
            general_error_message.innerHTML = "Please enter valid dates";
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "End date cannot be past today's date";
            return;
        }
    }

    if (selected_filter_value == "4") {
        var email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid email ID";
            return;
        }

        for (var index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid email ID";
                return;
            }
        }
    }

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-support-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] != "None") {
                var export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the Email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                general_error_message.style.color = "red";
                general_error_message.innerHTML = "Unable to download support history";
            }
        }
    }
    xhttp.send(params);
}
