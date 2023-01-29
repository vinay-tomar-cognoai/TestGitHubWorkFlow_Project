/****************************** ACTIONS ON DOCUMENT & WINDOW EVENT ******************************/
$(document).ready(document_ready);
window.addEventListener("resize", window_resize);
window.addEventListener('popstate', window_pop_state_listener)

var channels;
SELECTED_DATE_FILTER = '4'
CHECKED_STATUS = ''
START_DATE = ''
END_DATE = ''
ACTIVE_CHANNELS = []
IN_PROGRESS_SELECTED = false
SEARCHED_CAMPAIGN = ""
IS_DOWNLOAD_IN_PROGRESS = false
CURRENT_TAB = "all_campaigns"


////////////////////////////// Debounce //////////////////////////
// Debounce function makes sure that the code is only triggered once per user input
// Delay implies after how many mil seconds of user action the function should be triggered
// To know more check out this link - https://www.geeksforgeeks.org/debouncing-in-javascript/

const debounce = (func, delay = 500) => {
    let clearTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(clearTimer);
        clearTimer = setTimeout(() => func.apply(context, args), delay);
    }
}

//////////////////////////////////////////////////////////////////


function document_ready() {
    adjust_sidebar();
    change_active_sidenav_option();

    try {
        channels = CHANNELS;
    } catch(err) {
        channels = [];
    }

    $('.datepicker').datepicker({
        endDate: '+0d',
    });

    $('.campaign-tooltip').tooltip();

    $(".positive_numeric").on("keypress input", function (event) {
        var keyCode = event.which;

        if ((keyCode != 8 || keyCode == 32) && (keyCode < 48 || keyCode > 57)) {
            return false;
        }

        var self = $(this);
        self.val(self.val().replace(/\D/g, ""));
    });

    $(".mobile_number").on("keypress", campaign_mobile_number_validation);

    // window.CONSOLE_THEME_COLOR = getComputedStyle(document.body).getPropertyValue('--color_rgb');

    $('#select-agent-username-dropdown').multiselect({
        nonSelectedText: 'Select Channel',
        enableFiltering: false,
        enableCaseInsensitiveFiltering: false,
        selectAll: false,
        includeSelectAllOption: false,
        onChange: function() {
            var selected = this.$select.val();
            channels = selected;
            if(window.location.href.includes("channels") && channels != []){
                let new_channles = []
                channels.forEach(res=>{
                    new_channles.push(res.replace(" ","_"))
                })
                const new_url = window.location.href.split("channels=")[0] + "channels=" + new_channles.join("+")
                window.history.pushState({ path: new_url }, '', new_url);
            }
            initialize_active_campaign_table(applied_filter[0], applied_filter[1], applied_filter[2], applied_filter[3], channels);
        }
    }).multiselect('selectAll', false)
    .multiselect('updateButtonText'); 

    // Initialize Campaign Dashboard table
    initialize_active_campaign_table('4', '', '', '', channels);

    if (window.location.pathname.includes('dashboard')) {
        refresh_data_dynamically();
    }

    $('.sidebar-toggle-btn').on('click', function() {
        show_collapsed_sidebar();
    });

    if(window.location.pathname.includes('review')) {
        set_campaign_body ();
    }

    if (window.location.href.includes('api-documentation')) {
        setTimeout(function() {
            document.getElementById('api_documentation_link').classList.add('active');
        }, 100)
    }
}

function refresh_data_dynamically() {
    setInterval(function () {
        let filters = get_url_multiple_vars();
        var delete_btn = document.getElementById(filters.tab[0] == "all_campaigns" ? "delete_campaign_btn" : "delete_campaign_schedule_btn");
        var is_select_checked = !delete_btn.disabled;

        var is_dropdown_open = false;
        if (!is_select_checked) {
            var dropdown_elems = document.getElementsByClassName('campaign-dropdown-menu');

            for (elem of dropdown_elems) {
                if (elem.classList.contains('show')) {
                    is_dropdown_open = true;
                    break;
                }
            }
        }

        let clone_popup = document.getElementsByClassName('duplicate-campaign-modal-class');
        for (elem of clone_popup) {
            if (elem.style.display != '' && elem.style.display != 'none') {
                return;
            }
        }

        let popup_elems = document.getElementsByClassName('overview-menu-list');
        for (elem of popup_elems) {
            if (elem.style.display != 'none') {
                return;
            }
        }

        var is_search_empty = document.getElementById('campaign-search-bar').value.trim() == "";
        if (filters.tab && filters.tab[0] == "schedules") {
            var is_search_empty = document.getElementById('campaign-schedule-search-bar').value.trim() == "";
        }

        var detail_dropdowns = document.getElementsByClassName('toggle-table-dropdown-arrow');
        var is_detail_dropdown_open = false;

        if (detail_dropdowns.length > 0) {
            is_detail_dropdown_open = true;
        }

        if (is_content_refresh_allowed && !is_select_checked && !is_dropdown_open && is_search_empty && !is_detail_dropdown_open && !IN_PROGRESS_SELECTED) {
            if (applied_filter.length > 0) {
                window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns(applied_filter[0], applied_filter[1], applied_filter[2], applied_filter[3], channels);
            } else {
                window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns('4', '', '', '', channels);
            }
        }
    }, 10000)
}

var campaign_details = {};

function campaign_mobile_number_validation(event) {
    var element = event.target;
    var value = element.value;
    var count = value.length;

    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) {
        if (count >= 10) {
            event.preventDefault();
        }
    }
}

function window_resize() {
    tooltip_utility_change();
}

function window_pop_state_listener() {
    if (window.ACTIVE_CAMPAIGN_TABLE) {
        window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns();
    }
}

document.querySelector("#content-wrapper").addEventListener(
    "scroll",
    function () {
        var datepicket_dropdown = document.querySelector(".datepicker-dropdown");
        if (datepicket_dropdown) {
            document.body.removeChild(datepicket_dropdown);
            $('.datepicker').blur();
        }
    }
)

var is_content_refresh_allowed = true;

function disable_content_refresh() {
    is_content_refresh_allowed = false;
}

function enable_content_refresh() {
    is_content_refresh_allowed = true;
}

$('#campaign_meta_data_table').on('hidden.bs.modal', function (e) {
    enable_content_refresh();
})

/****************************** TMS SIDE BAR ******************************/

function change_sales_logo_property() {
    var sales_logo = document.getElementById("sales-ai-logo");
    var is_sidebar_toggled = false;
    if (document.getElementById("accordionSidebar").getAttribute("class").indexOf("toggled") != -1) {
        set_cookie("sales-ai-accordion-sidebar", "", path = "/");
        if (window.matchMedia("(min-width: 720px)")) {
            $('#accordianSidebar').css({
                "position": "fixed"
            });
        }
        is_sidebar_toggled = false;
    } else {
        set_cookie("sales-ai-accordion-sidebar", "toggled", path = "/");
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
    if (get_cookie("sales-ai-accordion-sidebar") == "") {
        document.getElementById("accordionSidebar").classList.remove("toggled");
    } else if (get_cookie("sales-ai-accordion-sidebar") == "toggled") {
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
            var parent = $(event.target).closest("#accordionSidebar, #sidebarToggleTop");
            if (parent.length === 0) {
                if (document.getElementById("accordionSidebar").classList.contains('toggled')) {
                    document.getElementById("sidebarToggleTop").click();
                }
            }
        });
    }

}

function change_active_sidenav_option() {
    nav_items = document.getElementsByClassName("nav-item-menu");

    for (var index = 0; index < nav_items.length; index++) {
        nav_items[index].classList.remove("active");
    }

    for (var index = 0; index < nav_items.length; index++) {
        if (nav_items[index].children[0].pathname == window.location.pathname || (nav_items[index].children[0].pathname == "/campaign/dashboard/" && window.location.pathname == "/campaign/voice-bot-campaign-details/")) {
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
        if (get_cookie("sales-ai-accordion-sidebar") == "toggled") {
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

function show_campaign_toast(message, timeout=5000) {
    var element = document.getElementById("campaign-snackbar");
    element.innerHTML = message;
    element.className = "show";
    if (timeout != 5000) {
        $('#campaign-snackbar.show').css("-webkit-animation","campaign-fadein 0.5s, campaign-fadeout 0.5s " + (timeout/1000 + 1)+ "s" );
        $('#campaign-snackbar.show').css("animation","campaign-fadein 0.5s, campaign-fadeout 0.5s " + (timeout/1000 + 1) + "s");
    }
    setTimeout(function () {
        element.className = element.className.replace("show", "");
    }, timeout);
}

function show_campaign_toast_short(message) {
    var element = document.getElementById("campaign-snackbar");
    element.innerHTML = message;
    element.className = "show";
    setTimeout(function () {
        element.className = element.className.replace("show", "");
    }, 2000);
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
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (var i = 0; i < cookie_array.length; i++) {
        var c = cookie_array[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(cookie_name) == 0) {
            return c.substring(cookie_name.length, c.length);
        }
    }
    return "";
}

function set_cookie(cookiename, cookievalue, path = "") {
    var domain = window.location.hostname.substring(window.location.host.indexOf(".") + 1);

    if (window.location.hostname.split(".").length == 2 || window.location.hostname == "127.0.0.1") {
        domain = window.location.hostname;
    }

    if (path == "") {
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

    var regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function remove_special_characters_from_batch_name(text) {
    let regex = /:|;|'|"|=|\$|\*|%|!|`|~|&|\^|\{|\}|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function test_special_characters_in_batch_name(text) {
    let specialCharRegex = /:|;|'|"|=|\$|\*|%|!|`|~|&|\^|\{|\}|#|<|>|\/|\\/g;
    let alphaNumRegex = /[a-zA-Z0-9]/g;
    return specialCharRegex.test(text) || !alphaNumRegex.test(text);
}

function remove_special_char_from_str(text) {
    let regex = /:|;|'|"|=|-|\$|\*|%|`|~|\^|\[|\]|\{|\}|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function check_all_speical_chars(text) {
    let pattern = /^[^a-zA-Z0-9]+$/;
    return (pattern.test(text));
}

function get_url_multiple_vars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        if (!(key in vars)) {
            vars[key] = [];
        }
        vars[key].push(value);
    });
    return vars;
}

function campaign_chars_limit_validation(event, label, is_numeric=false) {
    var element = event.target;
    var value = element.value;
    var count = value.length;
    if(!label) {
        label = "Text";
    }

    var allowed_maximum_characters = 100;
    if(is_numeric) {
        allowed_maximum_characters = 4;
    }

    if(count >= allowed_maximum_characters){
        event.preventDefault();
        show_campaign_toast(label + " should not be more than " + allowed_maximum_characters + " characters");
    }
}

function campaign_chars_limit_validataion_on_paste(event, label, is_numeric) {
    var element = event.target;
    var value = element.value;

    var clipboard_data = event.clipboardData || event.originalEvent.clipboardData || window.clipboardData;
    var pasted_data = clipboard_data.getData('text') + value;
    var count = pasted_data.length;

    if(!label) {
        label = "Text";
    }

    var allowed_maximum_characters = 100;
    if(is_numeric) {
        allowed_maximum_characters = 4;
    }

    if(count > allowed_maximum_characters){
        event.preventDefault();
        show_campaign_toast(label + " should not be more than " + allowed_maximum_characters + " characters");
    }
}

$(document).ready(function() {
    var text_elements = [
        // Text field
        ["campaign-name", "Campaign Name"],
        ["campaign_template_name", "Template Name"],
        ["campaign_cta_link", "CTA Link"],
        ["campaign_cta_text", "CTA Text"],
        ["new-batch-name", "Batch Name"]
    ];

    text_elements.forEach(function(element_detail) {
        var element_id = element_detail[0];
        var label = element_detail[1];

        var input_element = document.getElementById(element_id);
        if(input_element) {
            var is_numeric = false;
            if(input_element.getAttribute("type") == "number") {
                is_numeric = true;
            }
            input_element.addEventListener("keypress", function(event) {
                campaign_chars_limit_validation(event, label, is_numeric);
            });

            input_element.addEventListener("paste", function(event) {
                campaign_chars_limit_validataion_on_paste(event, label, is_numeric);
            });
        }
    });
});


function check_file_extension(filename) {
    var fileExtension = "";
    if (filename.lastIndexOf(".") > 0) {
        fileExtension = filename.substring(filename.lastIndexOf(".") + 1, filename.length);
    }
    fileExtension = fileExtension.toLowerCase();
    var allowed_files = ['xls', 'xlsx', 'csv', 'psv'];

    if (allowed_files.includes(fileExtension)) return true;

    return false;
}

function check_malicious_file(file_name) {
    var response = {
        'status': false,
        'message': 'OK'
    }
    if (file_name.split('.').length != 2) {
        response.status = true;
        response.message = 'We do not allow . (dot) in the file name except for the extension. Please remove the dot and Re-upload the file.';
        return response;
    }

    var allowed_files_list = [
        "png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "doc", "docx",
        "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip", "csv", "psv"
    ];

    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if (allowed_files_list.includes(file_extension) == false) {
        response.status = true;
        response.message = '.' + file_extension + ' files are not allowed'
        return response;
    }
    return response;
}

function is_url_valid(url_str, is_http_check_required=false) {
    var url_pattern;
    if (is_http_check_required) {
        url_pattern = /(http(s)?:\/\/.)[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;
    } else {
        url_pattern = /[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;
        if (url_str.includes("http://") || url_str.includes("https://")) {
            return false;
        }
    }
    var result = url_str.match(url_pattern);
    if (result == null) {
        return false;
    } else {
        return true;
    }
}

/****************************** Bootstrap Dropdown Script ******************************/

(function () {
    // hold onto the drop down menu                                             
    var dropdownMenu;

    // and when you show it, move it to the body                                     
    $(window).on('show.bs.dropdown', function (e) {

        // grab the menu        
        dropdownMenu = $(e.target).find('.campaign-dropdown-menu');

        // detach it and append it to the body
        $('body').append(dropdownMenu.detach());

        // grab the new offset position
        var eOffset = $(e.target).offset();

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


/****************************** CAMPAIGN BASE TABLE ******************************/

class CampaignBase {
    update_table_attribute(table_elements) {
        for (var idx = 0; idx < table_elements.length; idx++) {
            var table_el = table_elements[idx];
            var thead_el = table_elements[idx].getElementsByTagName('thead');
            if (thead_el.length == 0) {
                continue;
            }
            thead_el = thead_el[0];
            var tbody_el = table_elements[idx].getElementsByTagName('tbody');
            if (tbody_el.length == 0) {
                continue;
            }

            tbody_el = tbody_el[0];
            for (var row_index = 0; row_index < tbody_el.rows.length; row_index++) {
                if (tbody_el.rows[row_index].children.length != thead_el.rows[0].children.length) {
                    continue;
                }
                for (var col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
                    var column_element = tbody_el.rows[row_index].children[col_index];
                    var th_text = thead_el.rows[0].children[col_index].innerText;
                    column_element.setAttribute("data-content", th_text);
                }
            }
        }
    }

    apply_pagination(pagination_container, pagination_metadata, onclick_handler, target_obj) {
        var metadata = pagination_metadata;
        var html = "";

        var filter_default_text = "Showing " + metadata.start_point + " to " + metadata.end_point + " of " + metadata.total_count + " entries";

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

        for (var index = metadata.page_range[0]; index < metadata.page_range[1]; index++) {
            if (metadata.number == index) {
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
            '<div class="col-md-6 col-sm-12 show-pagination-entry-container dataTables_info" filter_default_text=\'' + filter_default_text + '\'>',
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

        var pagination_links = pagination_container.querySelectorAll('a.page-link');

        pagination_links.forEach((pagination_link_element) => {
            var page_number = pagination_link_element.getAttribute('data-page');
            if (page_number != null && page_number != undefined) {
                pagination_link_element.addEventListener('click', function (event) {
                    onclick_handler('page', page_number, target_obj);
                })
            }
        });
    }
};

/************************************************************ DASHBOARD SETTINGS STARTS ************************************************************/

/*
    ActiveCampaignsTable 

    Description :
        - This class is used to do manage active campaign table in dashboard

    Required Parameters : 

        lead_data_cols : column confogurations 
            - received in console meta data - get_active_agent_console_settings
            - window.ACTIVE_AGENT_METADATA.lead_data_cols
        campaign_data : list of campaign information object
            - received in fetch_active_campaign response
        table : active lead table
            - tms_active_lead_table

    initialization : 
        - This is initialized in fetch_active_campaign api response
        - window.ACTIVE_CAMPAIGN_TABLE
*/

class ActiveCampaignsTable extends CampaignBase {
    constructor(table_container, searchbar_element, pagination_container, selected_date_filter, checked_status, start_date, end_date, channels) {
        super();
        this.table_container = table_container;
        this.table = null;
        let filters = get_url_multiple_vars();
        this.options = {
            enable_select_rows: true,
            enable_campaign_details: (filters["tab"] && filters["tab"][0] == "schedules") ? false : true,
        }

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;
        this.searchbar_element = searchbar_element;

        this.data_checklist = {
            'campaign_data': false,
        };
        this.data_table_obj = null;
        ACTIVE_CHANNELS = channels;
        SELECTED_DATE_FILTER = selected_date_filter;
        CHECKED_STATUS = checked_status;
        START_DATE = start_date;
        END_DATE = end_date;
        this.init(selected_date_filter, checked_status, start_date, end_date, channels);
    }

    init(selected_date_filter, checked_status, start_date, end_date, channels) {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.fetch_active_campaigns(selected_date_filter, checked_status, start_date, end_date, channels);
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="campaign_table" width="100%" cellspacing="0"></table>';
        _this.table = _this.table_container.querySelector("table");

        if (!_this.table) return;
        if (_this.active_user_metadata.lead_data_cols.length == 0) return;
        if(_this.campaign_data.length == 0) {
            _this.options.enable_select_rows = false;
        } else {
            _this.options.enable_select_rows = true;
        }

        _this.initialize_head();
        _this.initialize_body();
        _this.add_event_listeners();
        _this.add_event_listeners_in_rows();
        _this.update_table_attribute([_this.table]);

        // document.getElementById("assign-campaign-btn").style.display = "none";
        /*
            ------- saved for future reference -------
            $(_this.table).DataTable().clear().draw();
            $(_this.table).DataTable().destroy(true);
        */
    }

    initialize_head() {
        var _this = this;
        const { enable_select_rows, enable_campaign_details } = _this.options;

        var th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            var name = column_info_obj.name;
            var display_name = column_info_obj.display_name;
            var width = column_info_obj.width;
            th_html += '<th name="' + name + '" rowspan="1" colspan="1" style="width: ' + width + '">' + display_name + '</th>'
        });

        var select_rows_html = "";
        let filters = get_url_multiple_vars();
        let select_row_width = (filters["tab"] && filters["tab"][0] == "schedules") ? "20px;" : "17.9972px;"
        if (enable_select_rows) {
            select_rows_html = [
                '<th class="sorting_disabled position-rel schdeule_checkbox" rowspan="1" colspan="1" style="width: ' + select_row_width + '">',
                '<input type="checkbox" class="campaign_select_all_rows_cb">',
                '</th>',
            ].join('');
        }

        var campaign_details_html = "";
        if (enable_campaign_details) {
            campaign_details_html = [
                '<th class="sorting_disabled text-left text-md-center" rowspan="1" colspan="1" style="width: 33.2955px;">',
                '</th>',
            ].join('');
        }

        var thead_html = [
            '<thead>',
            '<tr role="row">',
            campaign_details_html,
            select_rows_html,
            th_html,
            '</tr>',
            '</thead>',
        ].join('');

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        var _this = this;

        var campaign_data_list = this.get_rows();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": campaign_data_list,
            "ordering": false,
            "bPaginate": false,
            "autoWidth": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": false,
            'columnDefs': [{
                "targets": 0,
                "className": "text-left text-md-center",
                // "width": "4%"
            }
            ],
           
            "drawCallback": function (settings) {
                $('[data-toggle="tooltip"]').tooltip({
                    container: 'body',
                    boundary: 'window',
                    delay: { "show": 500 }
                });

                if($(this).find('.dataTables_empty').length == 1) {
                    $(this).parent().hide();
                    $('#table_no_data_found').css("display","flex");
                    $('#schedule_table_no_data_found').css("display","flex");
                }
                else{
                    $('#table_no_data_found').hide();
                    $('#schedule_table_no_data_found').hide();
                }
            },


            initComplete: function (settings) {
                // $(_this.table).colResizable({
                //     disable: true
                // });
                // $(_this.table).colResizable({
                //     liveDrag: true,
                //     minWidth: 100,
                //     postbackSafe: true,
                // });
                _this.apply_table_pagination();
            },
            createdRow: function (row, data, dataIndex) {
                row.setAttribute("campaign_id", _this.campaign_data[dataIndex].campaign_id);
                if (! _this.campaign_data[dataIndex].is_source_dashboard){
                    // $(row).children().css('opacity','0.45');
                    $(row).children().find('#action_dropdown_menu_btn').css('pointer-events','none');
                    $(row).children().find('#action_btn_tooltip_div').css('opacity','0.45');
                    $(row).children().find('#action_btn_tooltip_div').addClass('cursor-not-allowed');
                    $(row).children().find('#action_btn_tooltip_div').attr({
                        'data-toggle':'tooltip',
                        'title':'This option cannot be selected for the Campaign if it is created via API'
                    });
                }
            }, 
          
        });
        $('.campaign-tooltip').tooltip();
    }

    update_url_with_filters(filters) {
        var key_value = "";
        for (var filter_key in filters) {
            var filter_data = filters[filter_key];
            for (var index = 0; index < filter_data.length; index++) {
                key_value += filter_key + "=" + filter_data[index] + "&";
            }
        }

        var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
        window.history.pushState({ path: newurl }, '', newurl);
    }

    add_filter_and_fetch_data(key, value, target_obj = null) {
        var _this = this;
        if (target_obj) {
            _this = target_obj;
        }

        var filters = get_url_multiple_vars();
        if (key == "page") {
            filters.page = [value];
        }

        _this.update_url_with_filters(filters);
        active_campaign_data_loader()
        _this.fetch_active_campaigns(SELECTED_DATE_FILTER, CHECKED_STATUS, START_DATE, END_DATE, ACTIVE_CHANNELS, true);
    }

    apply_table_pagination() {
        var _this = this;
        if(_this.campaign_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        var container = _this.pagination_container;
        var metadata = _this.pagination_metadata;
        var onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    fetch_active_campaigns(selected_date_filter, checked_status, start_date, end_date, channels, pagination_clicked = false) {
        if (window.location.href.indexOf("campaign/dashboard") == -1) {
            return
        }
        var _this = this;

        var scroll_pos = document.getElementById('content-wrapper').scrollTop;
        var filters = get_url_multiple_vars();

        var request_params = {
            'page': ((filters["page"] && filters["page"][0]) || 1),
            'bot_pk': filters["bot_pk"][0],
            'channels': ACTIVE_CHANNELS,
            'searched_campaign': SEARCHED_CAMPAIGN,
            'filter_date_type': selected_date_filter,
            'tab': ((filters["tab"] && filters["tab"][0]) || "all_campaigns"),
        };

        if (filters['filter_date_type'] == "5" && filters['start_date'] && start_date == '' && end_date == '') {
            request_params['start_date'] = filters['start_date'][0];
            request_params['end_date'] = filters['end_date'][0];
        }

        if (checked_status != '') {
            request_params['selected_status'] = checked_status
        }

        if (start_date && start_date != '') {
            request_params['start_date'] = start_date;
            request_params['end_date'] = end_date;
        }

        var json_params = JSON.stringify(request_params);
        var encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/get-active-campaign/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                $(".tooltip").tooltip('dispose');
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    if ("messages_in_sqs_queue" in response) {
                        document.getElementById('sqs-msg-count').innerText = response["messages_in_sqs_queue"];
                    }
                    _this.set_campaign_data(response.active_campaigns);
                    CURRENT_TAB = request_params['tab']
                    document.getElementById('content-wrapper').scrollTop = scroll_pos;
                    if (pagination_clicked) {
                        $('#content-wrapper').animate({
                            scrollTop: $('#content-wrapper').offset().top,
                        });
                    }
                    let changed_channels = []
                    request_params['channels'].forEach(res=>{
                        changed_channels.push(res.replace(' ','_'))
                    })
                    channels = request_params['channels']
                    let newurl = "";

                    if(request_params['filter_date_type'] && request_params['selected_status']){
                        applied_filter = [request_params['filter_date_type'], request_params['selected_status'], start_date, end_date]
                        if (request_params['searched_campaign'] && request_params['start_date'] && 'start_date' in request_params) {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&searched_campaign=' + request_params['searched_campaign'] + '&filter_date_type=' + request_params['filter_date_type'] + '&selected_status=' + request_params['selected_status'].join("+") + '&start_date=' + request_params['start_date'] + '&end_date=' + request_params['end_date'] + '&channels=' + changed_channels.join("+");
                        } else if (request_params['searched_campaign']) {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&searched_campaign=' + request_params['searched_campaign'] + '&filter_date_type=' + request_params['filter_date_type'] + '&selected_status=' + request_params['selected_status'].join("+") + '&channels=' + changed_channels.join("+");
                        } else if (request_params['filter_date_type'] == "5") {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&filter_date_type=' + request_params['filter_date_type'] + '&selected_status=' + request_params['selected_status'].join("+") + '&start_date=' + request_params['start_date'] + '&end_date=' + request_params['end_date'] + '&channels=' + changed_channels.join("+");
                        } else {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&filter_date_type=' + request_params['filter_date_type'] + '&selected_status=' + request_params['selected_status'].join("+") + '&channels=' + changed_channels.join("+");
                        }
                    } else if (request_params['filter_date_type']) {
                        applied_filter = [request_params['filter_date_type'], '', start_date, end_date]
                        if (request_params['searched_campaign'] && request_params['start_date'] && 'start_date' in request_params) {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&searched_campaign=' + request_params['searched_campaign'] + '&filter_date_type=' + request_params['filter_date_type'] + '&start_date=' + request_params['start_date'] + '&end_date=' + request_params['end_date'] + '&channels=' + changed_channels.join("+");
                        } else if (request_params['searched_campaign']) {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&searched_campaign=' + request_params['searched_campaign'] + '&filter_date_type=' + request_params['filter_date_type'] + '&channels=' + changed_channels.join("+");
                        } else if (request_params['filter_date_type'] == "5" && request_params['searched_campaign']) {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&searched_campaign=' + request_params['searched_campaign'] + '&filter_date_type=' + request_params['filter_date_type'] + '&start_date=' + request_params['start_date'] + '&end_date=' + request_params['end_date'] + '&channels=' + changed_channels.join("+");
                        } else if (request_params['filter_date_type'] == "5") {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&filter_date_type=' + request_params['filter_date_type'] + '&start_date=' + request_params['start_date'] + '&end_date=' + request_params['end_date'] + '&channels=' + changed_channels.join("+");
                        } else {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&filter_date_type=' + request_params['filter_date_type'] + '&channels=' + changed_channels.join("+");
                        }
                    } else {
                        if (request_params['searched_campaign']) {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&searched_campaign=' + request_params['searched_campaign'] + '&channels=' + changed_channels.join("+");
                        } else {
                            newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?bot_pk=' + request_params['bot_pk'] + '&tab=' + request_params['tab'] + '&page=' + request_params['page'] + '&channels=' + changed_channels.join("+");
                        }
                    }
                    window.history.pushState({ path: newurl }, '', newurl);
                }
            } else if(this.readyState == 4 && this.status == 403){
                $("#delete_campaign_modal").modal("hide");
                $('.campaign-delete-modal-content-text').hide()
                trigger_session_time_out_modal();
            }
            // deactive_campaign_data_loader();
        }
        xhttp.send(params);
    }

    set_campaign_data(campaign_data) {
        var _this = this;
        if (campaign_data) {
            _this.campaign_data = campaign_data;
            _this.data_checklist.campaign_data = true;

            set_campaign_details_obj(campaign_data);
        }

        _this.check_and_initialize_table();
        deactive_campaign_data_loader();
    }

    check_and_initialize_table() {
        var _this = this;

        if (_this.data_checklist.campaign_data == false) return false;

        _this.initialize_table();
    }

    get_row_html(name, campaign_data_obj) {
        var _this = this;
        var data = campaign_data_obj[name];
        if(data == null || data == undefined) {
            data = "-";
        }
        var campaign_id = campaign_data_obj.campaign_id;
        var bot_pk = get_url_multiple_vars()['bot_pk'][0];

        var html = "";
        switch (name) {
            case "name":
                let status_name = campaign_data_obj["status"].toLowerCase()
                html = data;
                if (campaign_data_obj["channel_value"].trim() == "voicebot" && status_name != "draft" && campaign_data_obj["total_audience"] > 0) {
                    html = `<a href='/campaign/voice-bot-campaign-details/?bot_pk=` + get_url_multiple_vars()["bot_pk"][0] + `&campaign_id=` + campaign_data_obj["campaign_id"] + `'>` + data + `</a>`
                }
                
                let status_list = ["partially_completed", "completed", "failed", "ongoing", "processed"];
                if (campaign_data_obj["channel_value"].trim() == "whatsapp" && (status_list.includes(status_name) && campaign_data_obj["total_audience"] > 0 || status_name == "draft" && campaign_data_obj['times_campaign_tested'] > 0)) {
                    html = `<a href='/campaign/whatsapp-campaign-details/?bot_pk=` + get_url_multiple_vars()["bot_pk"][0] + `&campaign_id=` + campaign_data_obj["campaign_id"] + `' target="_blank" >` + data + `</a>`
                }
                break;

            case "status":
                var status = data.toLowerCase();
                if(status == "partially_completed") {
                    html = `<span class="campaign-tooltip" data-toggle="tooltip" data-placement="top" data-original-title="The campaign is completed but some messages have failed to send. Please check the reports to understand the reason for the failure." style="color:#2741FA">Completed <span style="color: #FF281A">!</span></span>`;
                } else if(status == "completed") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="All the messages are sent successfully to the targeted audience for this campaign." style="color:#40C351">Completed</span>`;
                } else if(status == "in_progress") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="The messages are being sent now. Please wait until the campaign is completed." style="color:#0254D7;">In Progress</span>`
                } else if(status == "draft") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="The campaign is not yet sent and you can continue by clicking on the edit icon. If there are any test campaigns sent, the details can be viewed by clicking on the campaign name." style="color:#000000">Draft</span>`
                } else if (status == "scheduled") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="This campaign has been scheduled and will run at the set time. Click on the Schedule icon to see the upcoming schedules." style="color:#000000">Scheduled</span>`
                } else if (status == "schedule_completed") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="All the schedules in this campaign are completed. Click on the Schedule icon to add new schedules." style="color:green">Schedule Completed</span>`
                }else if (status == "failed") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="All the messages have failed in this campaign. Please check the reports to understand the reason for the failure." style="color:#FF281A">Failed</span>`
                }else if (status == "ongoing") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="This campaign is triggered using an API and the messages can be sent again in the same campaign." style="color:#F18B0B">Ongoing</span>`
                }else if (status == "processed") {
                    html = `<span data-toggle="tooltip" data-placement="top" data-original-title="The messages have been sent to WhatsApp and the process of sending has already started. Please wait until the count gets updated." style="color:#17B4CB">Submitted</span>`
                }
                 else {
                    html = `<span>${data}</span>`
                }
                
                break;

            case "total_audience":
                html = data;
                break;

            case "create_datetime":
                html = data;
                break;
            
            case "channel":
                html = data;
                break;

            case "action":
                var campaign_status = campaign_data_obj.status;
                var channel = campaign_data_obj.channel;
                var html = `<td class="d-flex channels-btn-data-wrapper">
                <div class="d-flex channels-btn-data-wrapper" id="action_btn_tooltip_div">
                <div id="action_dropdown_menu_btn" style="position: relative; cursor: pointer;" class="overview-menu-wrapper-div">
                 <a class="btn btn-lg dots-btn action-btn" data-toggle="popover" data-trigger="focus">
                     <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                         <g filter="url(#filter0_d_77_8519)">
                         <rect x="2" y="2" width="24" height="24" rx="4" fill="#FAFAFA" shape-rendering="crispEdges"/>
                         <circle cx="14" cy="14" r="1.33333" fill="#2D2D2D"/>
                         <circle cx="9.33333" cy="14" r="1.33333" fill="#2D2D2D"/>
                         <circle cx="18.6666" cy="14" r="1.33333" fill="#2D2D2D"/>
                         </g>
                         <defs>
                         <filter id="filter0_d_77_8519" x="0" y="0" width="28" height="28" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
                         <feFlood flood-opacity="0" result="BackgroundImageFix"/>
                         <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
                         <feOffset/>
                         <feGaussianBlur stdDeviation="1"/>
                         <feComposite in2="hardAlpha" operator="out"/>
                         <feColorMatrix type="matrix" values="0 0 0 0 0.0416667 0 0 0 0 0.0416667 0 0 0 0 0.0416667 0 0 0 0.15 0"/>
                         <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_77_8519"/>
                         <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_77_8519" result="shape"/>
                         </filter>
                         </defs>
                      </svg>
                 </a>
                 <div class="overview-menu-list" style="display: none;">
                    <ul class="list-group custom-popover"> 
                 `;

                if (channel == 'Whatsapp Business' && "draft" != campaign_status && campaign_data_obj.is_source_dashboard == true ) {
                    html += `
                    <a class="menu-list-btn" href="javascript:open_clone_modal(${campaign_id})">
                        <li class="list-group-item group-data">
                            <span>Duplicate</span>
                            <span class="group-data-logo copy"> </span>
                        </li>
                    </a>`;
                }
                
                if ((channel == 'Whatsapp Business' || channel == "RCS") && !(["failed", "draft", "in_progress", "processed", "completed", "partially_completed", "ongoing"].includes(campaign_status))) {
                    html +=`
                        <a class="menu-list-btn" href="javascript:go_to_schedule_page('${campaign_id}')">
                            <li class="list-group-item group-data">
                                <span>Schedule</span>
                                <span class="group-data-logo schedule"> </span>
                            </li>
                        </a>`;

                }
                        
                if (["draft", "scheduled"].includes(campaign_status)) {
                   html += `
                        <a class="menu-list-btn" href="/campaign/edit/?bot_pk=${bot_pk}&campaign_id=${campaign_id}" target="_blank">
                            <li class="list-group-item group-data">
                                <span>Edit</span>
                                <span class="group-data-logo edit"> </span>
                            </li>
                        </a>`;
                }
                
                if (["draft"].includes(campaign_status) || ('in_progress' == campaign_status && channel == 'Voice Bot')) {

                    html += `
                        <a class="menu-list-btn" href="javascript:show_delete_camapaign_modal('${campaign_id}')">
                            <li class="list-group-item group-data">
                                <span>Delete</span>
                                <span class="group-data-logo delete"> </span>
                            </li>
                        </a>`;

                }

                html += `</ul>
                        </div>
                        </div>
                        </div>
                        </td>`;
                
                if (channel == 'Whatsapp Business' && "draft" != campaign_status && campaign_data_obj.is_source_dashboard == true ) {
                    html += `
                        <div class="modal fade custom_modal duplicate-campaign-modal-class" id="duplicate-campaign-modal-${campaign_id}" role="dialog">
                            <div class="modal-dialog" role="document">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <div class="row d-flex">
                                            <div class="col-11 duplicate-campaign-modal-header">
                                                <span>
                                                    <svg width="33" height="32" viewBox="0 0 33 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                    <path d="M3.74534 28.8686L5.54134 22.3119C4.43334 20.3933 3.85067 18.2159 3.85134 15.9859C3.85467 9.00925 9.532 3.33325 16.5093 3.33325C19.8953 3.33459 23.0727 4.65259 25.4627 7.04392C27.852 9.43592 29.168 12.6146 29.1667 15.9959C29.164 22.9726 23.4853 28.6493 16.5093 28.6493C16.5087 28.6493 16.5093 28.6493 16.5093 28.6493H16.504C14.386 28.6486 12.304 28.1173 10.4553 27.1086L3.74534 28.8686Z" fill="white"/>
                                                    <path d="M3.74533 29.202C3.65733 29.202 3.572 29.1673 3.50867 29.1033C3.42533 29.0187 3.39267 28.8953 3.424 28.7813L5.18333 22.3573C4.09267 20.42 3.51733 18.22 3.51867 15.9867C3.52133 8.82533 9.34867 3 16.5093 3C19.9827 3.00133 23.246 4.354 25.6987 6.80867C28.1513 9.264 29.5013 12.5267 29.5 15.996C29.4973 23.1567 23.6693 28.9827 16.5093 28.9827C14.3833 28.982 12.28 28.4573 10.4133 27.4647L3.83 29.1907C3.802 29.1987 3.774 29.202 3.74533 29.202Z" fill="white"/>
                                                    <path d="M16.5093 3.33341C19.8953 3.33475 23.0727 4.65275 25.4627 7.04408C27.852 9.43608 29.168 12.6147 29.1667 15.9961C29.164 22.9727 23.4853 28.6494 16.5093 28.6494H16.504C14.386 28.6487 12.304 28.1174 10.4553 27.1087L3.74533 28.8687L5.54133 22.3121C4.43333 20.3934 3.85067 18.2161 3.85133 15.9861C3.85467 9.00941 9.532 3.33341 16.5093 3.33341ZM16.5093 2.66675C9.16533 2.66675 3.188 8.64141 3.18467 15.9861C3.184 18.2307 3.75067 20.4427 4.82533 22.4007L3.102 28.6934C3.03933 28.9234 3.10333 29.1687 3.27133 29.3381C3.398 29.4661 3.56933 29.5361 3.74533 29.5361C3.802 29.5361 3.85867 29.5287 3.91467 29.5141L10.3727 27.8207C12.258 28.7994 14.3713 29.3161 16.504 29.3167C23.8533 29.3167 29.8307 23.3414 29.834 15.9967C29.8353 12.4374 28.4507 9.09075 25.9353 6.57341C23.4187 4.05541 20.0713 2.66808 16.5093 2.66675Z" fill="#CFD8DC"/>
                                                    <path d="M23.9507 8.5547C21.964 6.5667 19.3233 5.47137 16.5127 5.4707C10.71 5.4707 5.99067 10.188 5.988 15.9867C5.98733 17.974 6.54333 19.9087 7.59667 21.584L7.84733 21.982L6.784 25.8627L10.766 24.8187L11.1507 25.0467C12.7653 26.0054 14.6173 26.512 16.5053 26.5127H16.5093C22.308 26.5127 27.0273 21.7947 27.0293 15.9954C27.03 13.1854 25.9373 10.5427 23.9507 8.5547Z" fill="#40C351"/>
                                                    <path fill-rule="evenodd" clip-rule="evenodd" d="M13.3453 10.6966C13.1087 10.1699 12.8593 10.1593 12.6333 10.1499C12.4487 10.1419 12.238 10.1426 12.0273 10.1426C11.8167 10.1426 11.474 10.2219 11.184 10.5386C10.894 10.8553 10.0767 11.6199 10.0767 13.1759C10.0767 14.7319 11.21 16.2359 11.368 16.4466C11.526 16.6573 13.556 19.9526 16.7707 21.2206C19.442 22.2739 19.986 22.0646 20.566 22.0119C21.146 21.9593 22.4373 21.2473 22.7007 20.5086C22.964 19.7699 22.964 19.1373 22.8853 19.0053C22.806 18.8733 22.5953 18.7946 22.2793 18.6359C21.9633 18.4773 20.408 17.7126 20.118 17.6073C19.828 17.5019 19.6173 17.4493 19.406 17.7659C19.1953 18.0819 18.5893 18.7946 18.4047 19.0053C18.22 19.2166 18.0353 19.2433 17.7193 19.0846C17.4033 18.9259 16.3847 18.5926 15.176 17.5153C14.236 16.6773 13.6013 15.6419 13.4167 15.3253C13.232 15.0093 13.3967 14.8379 13.5553 14.6799C13.6973 14.5379 13.8713 14.3106 14.03 14.1259C14.188 13.9413 14.2407 13.8093 14.346 13.5986C14.4513 13.3873 14.3987 13.2026 14.3193 13.0446C14.2413 12.8859 13.6267 11.3219 13.3453 10.6966Z" fill="white"/>
                                                    </svg>
                                                    </span>
                                                <h5 class="modal-title">Duplicate Campaign Name</h5>

                                            </div>

                                            <div class="col-1" style="text-align: right;">
                                                <button class="btn" id="close-clone-modal-${campaign_id}" type="button" data-dismiss="modal" style="padding: 0!important">
                                                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                        <path d="M13.4931 0.710017C13.3063 0.522765 13.0526 0.417532 12.7881 0.417532C12.5236 0.417532 12.2699 0.522765 12.0831 0.710017L7.19309 5.59002L2.30309 0.700017C2.11625 0.512765 1.8626 0.407532 1.59809 0.407532C1.33357 0.407532 1.07992 0.512765 0.893086 0.700017C0.503086 1.09002 0.503086 1.72002 0.893086 2.11002L5.78309 7.00002L0.893086 11.89C0.503086 12.28 0.503086 12.91 0.893086 13.3C1.28309 13.69 1.91309 13.69 2.30309 13.3L7.19309 8.41002L12.0831 13.3C12.4731 13.69 13.1031 13.69 13.4931 13.3C13.8831 12.91 13.8831 12.28 13.4931 11.89L8.60309 7.00002L13.4931 2.11002C13.8731 1.73002 13.8731 1.09002 13.4931 0.710017Z" fill="black"></path>
                                                    </svg>
                                                </button>
                                            </div>

                                        </div>
                                    </div>
                                    <div class="modal-body" style="text-align: left;">
                                        
                                        <div class="col-sm-12 duplicate-campaign-sub-text-wrapper mb-3">
                                            <p class="duplicate-campaign-sub-text">Your Campaign has been copied from ${campaign_data_obj.name}. Please enter a unique Campaign name to continue.</p>
                                        </div>
                                        <div class="col-sm-12 duplicate-campaign-input-wrapper" style="margin-bottom: 8px;">
                                            <p class="duplicate-campaign-sub-text input-heading">Campaign name:</p>
                                            <div class="duplicate-campaign-input-wrapper-div">
                                            <input type="text" id="cloned-campaign-name-${campaign_id}" class="campaign-input-name" placeholder="Enter Campaign Name" autocomplete="off" value='${campaign_data_obj.name}_copy'>
                                            <p class="campaign-error-note" id="cloned-campaign-error-note-${campaign_id}"></p>
                                            </div>
                                        </div>
                                        
                                        <div class="align-center duplicate-campaign-note-wrapper">
                                            <p class="duplicate-campaign-note"><span style="font-weight: 700;";>Note:</span> By duplicating a campaign all the details from Audience batch and Template file will be copied, you can change the details in the next steps if required.</p>
                                        </div>
    
                                    </div>
                                    <div class="modal-footer">
                                        <button class="btn btn-primary btn-width-100" type="button" onclick="create_clone_campaign('${campaign_id}')">Next</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        `;
                }
                let filters = get_url_multiple_vars();
                if (filters['tab'] && filters['tab'][0] == "schedules") {
                    html = `<td data-content="Action">
                    <div class="schedules-action-btn-wrapper">
                    <a href="javascript:go_to_schedule_page('${campaign_id}')"style="text-decoration: none;">
                        <span class="action-cal campaign-tooltip" data-toggle="tooltip" data-placement="top" title="" data-original-title="Schedule">
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11.375 2.1875H2.625C2.38338 2.1875 2.1875 2.38338 2.1875 2.625V11.375C2.1875 11.6166 2.38338 11.8125 2.625 11.8125H11.375C11.6166 11.8125 11.8125 11.6166 11.8125 11.375V2.625C11.8125 2.38338 11.6166 2.1875 11.375 2.1875Z" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M9.625 1.09375V2.1875" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M4.375 1.09375V2.1875" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M2.1875 4.8125H11.8125" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>

                        </span>
                    </a>
                    `
                    if (campaign_data_obj['times_campaign_tested'] <= 0) {
                        html += `
                        <a class="campaign-overview-download-report-btn-disabled-test-svg campaign-tooltip" style="text-decoration: none;" data-toggle="tooltip" data-placement="top" title="" data-original-title="The Test Campaign Report is not available as no test campaign messages were sent before scheduling it.">
                            <span class="action-cal">
                            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7 1.75V9.625" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M3.0625 5.6875L7 9.625L10.9375 5.6875" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M2.1875 11.8125H11.8125" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            </span>
                        </a>
                        `
                    }
                    else {
                        html += `
                        <a class="campaign-tooltip"  href="javascript:void(0)" style="text-decoration: none;" onclick="open_single_export_modal(${campaign_id}, true)" data-toggle="tooltip" data-placement="top" title="" data-original-title="Download Test Campaign Report">
                            <span class="action-cal">
                            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7 1.75V9.625" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M3.0625 5.6875L7 9.625L10.9375 5.6875" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M2.1875 11.8125H11.8125" stroke="#525252" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            </span>
                        </a>
                        `
                    }

                html += `
                    </div>
                  </td>`
                }
                break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_select_row_html(campaign_data_obj) {
        var _this = this;
        const { enable_select_rows } = _this.options;

        if (!enable_select_rows) {
            return "";
        }
        let select_row_html = '';
        if (campaign_data_obj['status'] == 'in_progress'){
            select_row_html = '<input class="in_progress_campaign_select_row_cb" type="checkbox" campaign_id="' + campaign_data_obj.campaign_id + '" />';
        }else{
            select_row_html = '<input class="campaign_select_row_cb" type="checkbox" campaign_id="' + campaign_data_obj.campaign_id + '" />';
        }
        return select_row_html;
    }

    get_campaign_details_html(campaign_data_obj) {
        var _this = this;
        const { enable_campaign_details } = _this.options;

        if (!enable_campaign_details) {
            return "";
        }

        var campaign_details_html = `
                                    <button class="campaign-table-tr-data-dropdown-btn campaign-display-table-content" data-id=${campaign_data_obj.campaign_id}>
                                        <svg class="down-arrow-svg" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M2.21967 4.96967C2.51256 4.67678 2.98744 4.67678 3.28033 4.96967L6 7.68934L8.71967 4.96967C9.01256 4.67678 9.48744 4.67678 9.78033 4.96967C10.0732 5.26256 10.0732 5.73744 9.78033 6.03033L6.53033 9.28033C6.23744 9.57322 5.76256 9.57322 5.46967 9.28033L2.21967 6.03033C1.92678 5.73744 1.92678 5.26256 2.21967 4.96967Z" fill="#7B7A7B"></path>
                                        </svg>
                                        <svg class="up-arrow-svg" width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path d="M2.21967 8.03033C2.51256 8.32322 2.98744 8.32322 3.28033 8.03033L6 5.31066L8.71967 8.03033C9.01256 8.32322 9.48744 8.32322 9.78033 8.03033C10.0732 7.73744 10.0732 7.26256 9.78033 6.96967L6.53033 3.71967C6.23744 3.42678 5.76256 3.42678 5.46967 3.71967L2.21967 6.96967C1.92678 7.26256 1.92678 7.73744 2.21967 8.03033Z" fill="#2D2D2D"></path>
                                        </svg>
                                    </button>
                                `;

        return campaign_details_html;
    }

    get_row(campaign_data_obj) {
        var _this = this;
        const { enable_select_rows, enable_campaign_details } = _this.options;

        var campaign_data_list = [];

        var campaign_details_html = _this.get_campaign_details_html(campaign_data_obj);
        if (enable_campaign_details) {
            campaign_data_list.push(campaign_details_html);
        }

        var select_row_html = _this.get_select_row_html(campaign_data_obj);
        if (enable_select_rows) {
            campaign_data_list.push(select_row_html);
        }

        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected == false) return;
                var name = column_info_obj.name;
                campaign_data_list.push(_this.get_row_html(name, campaign_data_obj));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return campaign_data_list;
    }

    get_rows() {
        var _this = this;
        var campaign_data_list = [];
        _this.campaign_data.forEach((campaign_data_obj) => {
            campaign_data_list.push(_this.get_row(campaign_data_obj));
        })
        return campaign_data_list;
    }

    select_row_checkbox_change_listener(event) {
        var _this = this;
        var select_all_rows_cb = _this.table.querySelector(".campaign_select_all_rows_cb");
        var select_row_cbs = _this.table.querySelectorAll(".campaign_select_row_cb");
        let in_progress_select_row_cbs = _this.table.querySelectorAll(".in_progress_campaign_select_row_cb");
        let is_in_progress_checked = 0;

        var total_rows_checked = 0;
        select_row_cbs.forEach((select_row_cb) => {
            if (select_row_cb.checked) {
                total_rows_checked += 1;
            }
        });
        in_progress_select_row_cbs.forEach((in_progress_select_row_cb) => {
            if (in_progress_select_row_cb.checked) {
                total_rows_checked += 1;
                is_in_progress_checked += 1;
                IN_PROGRESS_SELECTED = true;
            }
        });
        
        let in_progress_select_row_cbs_length = in_progress_select_row_cbs.length
        
        if (is_in_progress_checked == 0){
            IN_PROGRESS_SELECTED = false;
        }

        if (total_rows_checked == (select_row_cbs.length + in_progress_select_row_cbs_length)) {
            select_all_rows_cb.checked = true;
        } else {
            select_all_rows_cb.checked = false;
        }

        let filters = get_url_multiple_vars();
        if(total_rows_checked > 0 && (total_rows_checked != is_in_progress_checked)) {
            document.getElementById(filters.tab[0] == "all_campaigns" ? "delete_campaign_btn" : "delete_campaign_schedule_btn").disabled = false;
        } else {
            document.getElementById(filters.tab[0] == "all_campaigns" ? "delete_campaign_btn" : "delete_campaign_schedule_btn").disabled = true;
        }
    }

    add_event_listeners_in_rows(container = null) {
        var _this = this;
        if (container == null) container = _this.table;

        // select row checkbox event listener
        var select_row_cbs = container.querySelectorAll(".campaign_select_row_cb");
        let in_progress_select_row_cbs = container.querySelectorAll(".in_progress_campaign_select_row_cb")
        select_row_cbs.forEach((select_row_cb) => {
            select_row_cb.addEventListener("change", (event) => {
                _this.select_row_checkbox_change_listener(event);
            });
        });

        in_progress_select_row_cbs.forEach((in_progress_select_row_cb) => {
            in_progress_select_row_cb.addEventListener("change", (event) => {
                _this.select_row_checkbox_change_listener(event);
            });
        });
    }

    add_event_listeners() {
        var _this = this;

        // Select all row checkbox event listener
        var select_all_rows_cb = _this.table.querySelector(".campaign_select_all_rows_cb");
        if (select_all_rows_cb) {
            select_all_rows_cb.addEventListener("change", function () {
                var select_row_cbs = _this.table.querySelectorAll(".campaign_select_row_cb");
                let in_progress_select_row_cbs = _this.table.querySelectorAll(".in_progress_campaign_select_row_cb");
                let number_of_in_progress_checked = 0;
                var all_rows_selected = this.checked;
                let total_checked = 0;
                select_row_cbs.forEach((select_row_cb) => {
                    if (all_rows_selected) {
                        select_row_cb.checked = true;
                        total_checked += 1;
                    } else {
                        select_row_cb.checked = false;
                    }
                })
                
                in_progress_select_row_cbs.forEach((in_progress_select_row_cb) => {
                    if (all_rows_selected) {
                        in_progress_select_row_cb.checked = true;
                        number_of_in_progress_checked += 1;
                        total_checked += 1;
                    } else {
                        in_progress_select_row_cb.checked = false;
                    }
                })

                let filters = get_url_multiple_vars()
                if(all_rows_selected && number_of_in_progress_checked != total_checked) {
                    document.getElementById(filters.tab[0] == "all_campaigns" ? "delete_campaign_btn" : "delete_campaign_schedule_btn").disabled = false;
                } else {
                    document.getElementById(filters.tab[0] == "all_campaigns" ? "delete_campaign_btn" : "delete_campaign_schedule_btn").disabled = true;
                }
            });
        }

        $("#campaign_dashboard_table tbody tr .campaign-display-table-content").click(function() {
            var parent = $(this).parent().parent();

            $(parent).after(``)
            $(this).parent().closest("tr").next(".campaign-overview-table-hidden-data-wrapper").toggleClass("campaign-show-table-data-details");
            
            if ($(this).parent().hasClass("toggle-table-dropdown-arrow")) {
                $(parent).next().remove();
            } else {
                var campaign_detail = campaign_details[$(this).data('id')];
                if (campaign_detail.channel == 'Voice Bot') {
                    $(parent).after(get_call_details_html($(this).data('id')));
                } else if (campaign_detail.channel == 'RCS') {
                    $(parent).after(get_rcs_campaign_details($(this).data('id')));
                } else {
                    $(parent).after(get_whatsapp_campaign_details($(this).data('id')));
                }

                setTimeout(() => {
                    $('[data-toggle="tooltip"]').tooltip()
                }, 300);
                $(this).parent().parent().css('background','#F8F8F8')
            }

            $(this).parent().toggleClass("toggle-table-dropdown-arrow")
        });
    }

    initialize_lead_data_metadata_update_modal() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols;
        var container = document.querySelector("#lead_dala_table_meta_div");
        var selected_values = [];
        var unselected_values = [];
        lead_data_cols.forEach((obj) => {
            if (obj.selected == true) {
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
        var _this = this;
        _this.active_user_metadata.lead_data_cols = lead_data_cols;

        _this.save_table_meta_data();
        _this.initialize_table();
    }

    save_table_meta_data() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols
        window.localStorage.setItem("campaign_table_meta_data", JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = window.localStorage.getItem("campaign_table_meta_data");

        if (lead_data_cols == null) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
            
            var is_old_table_present = false;
            lead_data_cols.forEach(col => {
                if (col.name == 'name') {
                    is_old_table_present = true;
                    return;
                }
            })

            if (is_old_table_present) {
                lead_data_cols = _this.get_default_meta_data();
            }
        }
        return lead_data_cols;
    }

    get_default_meta_data() {
        var lead_data_cols = [
            ['name', 'Name', true, "453px;"],
            ['status', 'Status', true, "174px;"],
            ['total_audience', 'Total Audience', true, "174px;"],
            ['create_datetime', 'Created On', true, "190px;"],
            // ['channel', 'Channel', true],
            ['action', 'Action', true, "45.0568px;"]
        ]

        var lead_data_cols_schedule = [
            ['name', 'Name', true, "613px;"],
            ['status', 'Status', true, "240px;"],
            ['create_datetime', 'Created On', true, "190px;"],
            // ['channel', 'Channel', true],
            ['action', 'Action', true, "72px;"]
        ]

        let filters = get_url_multiple_vars()
        var default_lead_data_cols = [];
        if (!filters.tab || filters.tab[0] != "schedules") {
            default_lead_data_cols = get_meta_data_columns(lead_data_cols);
        } else {
            default_lead_data_cols = get_meta_data_columns(lead_data_cols_schedule);
        }
        return default_lead_data_cols;
    }
}

function get_meta_data_columns(lead_data_cols) {
    let default_cols = []
    lead_data_cols.forEach((lead_data_col, index) => {
        default_cols.push({
            name: lead_data_col[0],
            display_name: lead_data_col[1],
            index: index,
            selected: lead_data_col[2],
            width: lead_data_col[3],
        });
    });
    return default_cols;
}

function initialize_active_campaign_table(selected_date_filter, checked_status, start_date, end_date, channels) {
    if (window.location.pathname.indexOf("/campaign/dashboard") != 0) {
        return;
    }

    var campaign_table_container = document.querySelector("#campaign_dashboard_table");
    var campaign_searchbar = document.querySelector("#campaign-search-bar");
    var pagination_container = document.getElementById("campaign_table_pagination_div");
    document.getElementById("delete_campaign_btn").disabled = true;
    document.getElementById("delete_campaign_schedule_btn").disabled = true;

    let filters = get_url_multiple_vars();

    if (filters.tab && filters.tab[0]) {
        setActiveTab()
        document.getElementById(filters.tab[0]).style.display = "block";
        if (filters.tab[0] == "all_campaigns") {
            document.getElementById("all_campaigns_tab").className += " active";
        } else {
            document.getElementById("schedules_tab").className += " active";
            campaign_table_container = document.querySelector("#campaign_Schedules_table");
            campaign_searchbar = document.querySelector("#campaign-schedules-search-bar");
            pagination_container = document.getElementById("campaign_schedule_table_pagination_div");
        }
        CURRENT_TAB = filters.tab[0]
    }
    if(filters['selected_status']){
        filters['selected_status'] = filters['selected_status'][0].split('+');
    } 

    if (filters['searched_campaign']) {
        if (filters.tab && filters.tab[0] == "all_campaigns") {
            document.getElementById("campaign-search-bar").value = filters['searched_campaign'][0];
        } else {
            document.getElementById("campaign-schedule-search-bar").value = filters['searched_campaign'][0];
        }
        SEARCHED_CAMPAIGN = filters['searched_campaign'][0];
    }

    if (filters['start_date']) {
        if (filters.tab && filters.tab[0] == "all_campaigns") {
            document.getElementById('campaign_filter_custom_start_date').value = filters['start_date'];
            document.getElementById('campaign_filter_custom_end_date').value = filters['end_date'];
            document.getElementById('campaign-custom-date-select-area-flow').style.display = 'flex';
        } else {
            document.getElementById('campaign_schedule_filter_custom_start_date').value = filters['start_date'];
            document.getElementById('campaign_schedule_filter_custom_end_date').value = filters['end_date'];
            document.getElementById('campaign-schedule-custom-date-select-area-flow').style.display = 'flex';
        }
    }

    if (filters['channels']){
        filters['channels'] = filters['channels'][0].split("+");
        let changed_channels = [];
        filters['channels'].forEach(res=>{
            changed_channels.push(res.replace('_',' '));
        })
        channels = changed_channels;

        $('#select-agent-username-dropdown ').multiselect("clearSelection");
        channels.forEach(res=>{
            $('#select-agent-username-dropdown ').multiselect('select', res);
        })
    }

    if (filters['filter_date_type']) {
        if (filters.tab[0] == "all_campaigns") {
            switch (filters['filter_date_type'][0]) {
                case '1': document.getElementById("campaign_overview_week").checked = true;
                    break;

                case '2': document.getElementById("campaign_overview_month").checked = true;
                    break;

                case '3': document.getElementById("campaign_overview_three_month").checked = true;
                    break;

                case '4': document.getElementById("campaign_overview_beg").checked = true;
                    break;

                case '5': document.getElementById("campaign_overview_custom_date_btn").checked = true;
                    break;

                default: document.getElementById("campaign_overview_beg").checked = true;
            }
        } else {
            switch (filters['filter_date_type'][0]) {
                case '1': document.getElementById("campaign_schedule_overview_week").checked = true;
                    break;

                case '2': document.getElementById("campaign_schedule_overview_month").checked = true;
                    break;

                case '3': document.getElementById("campaign_schedule_overview_three_month").checked = true;
                    break;

                case '4': document.getElementById("campaign_schedule_overview_beg").checked = true;
                    break;

                case '5': document.getElementById("campaign_schedule_overview_custom_date_btn").checked = true;
                    break;

                default: document.getElementById("campaign_schedule_overview_beg").checked = true;
            }
        }
        selected_date_filter = filters['filter_date_type'][0];
    }

    if(filters['selected_status']){
        for (const status of filters['selected_status']){
            if (status == 'completed') {
                document.getElementById("campaign_status_completed").checked = true;
            } else if (status == 'in_progress') {
                document.getElementById("campaign_status_progress").checked = true;
            } else if (status == 'draft') {
                document.getElementById("campaign_status_draft").checked = true;
            } else if (status == 'scheduled') {
                document.getElementById("campaign_schedule_status_scheduled").checked = true;
            } else if (status == 'failed') {
                document.getElementById("campaign_status_failed").checked = true;
            } else if (status == 'partially_completed') {
                document.getElementById("campaign_status_partially_completed").checked = true;
            } else if (status == 'ongoing') {
                document.getElementById("campaign_status_ongoing").checked = true;
            } else if (status == 'processed') {
                document.getElementById("campaign_status_processed").checked = true;
            } else if (status == 'schedule_completed') {
                document.getElementById("campaign_status_scheduled_completed").checked = true;
            }
        }
        checked_status = filters['selected_status'];
    }

 
    window.ACTIVE_CAMPAIGN_TABLE = new ActiveCampaignsTable(
        campaign_table_container, campaign_searchbar, pagination_container, selected_date_filter, checked_status, start_date, end_date, channels);
}

function save_lead_data_table_metadata() {

    var lead_data_cols = window.ACTIVE_CAMPAIGN_TABLE.active_user_metadata.lead_data_cols;

    var selected_values = [];
    var unselected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj) => {
        selected_values.push(obj.key);
    });
    window.LEAD_DATA_METADATA_INPUT.unselected_values.filter((obj) => {
        unselected_values.push(obj.key);
    });


    if (selected_values.length < 2) {
        show_campaign_toast("Atleast two columns needs to be selected.");
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

    window.ACTIVE_CAMPAIGN_TABLE.update_table_meta_deta(lead_data_cols)
}

function initialize_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

function show_delete_camapaign_modal(campaign_id) {
    var campaign_detail = campaign_details[campaign_id]

    if (campaign_detail.channel == 'Voice Bot' && campaign_detail.status == 'in_progress') {
        $('#text-in-progress-campaign').show();
        $('#text-completed-campaign').hide();
    } else {
        $('#text-in-progress-campaign').hide();
        $('#text-completed-campaign').show();
    }

    $("#delete_campaign_modal .modal-footer .btn-danger").attr("onclick", `delete_specific_campaign(this, '${campaign_id}')`);
    let error_element = delete_campaign_modal.querySelector('.error_element');
    error_element.innerHTML = "";
    $("#delete_campaign_modal").modal("show");
}

function go_to_schedule_page(campaign_id) {
    var request_params = {
        "campaign_id": campaign_id,
        "bot_pk": get_url_multiple_vars()['bot_pk'][0],
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/check-schedule-exists/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (response["channel"] == "Whatsapp Business") {
                    response["channel"] = "WhatsApp"
                }
                var template_url = window.location.origin + '/campaign/schedule/?bot_pk=' + get_url_multiple_vars()['bot_pk'][0] + '&campaign_id=' + campaign_id + '&channel=' + response["channel"]

                if (response["channel"] == "WhatsApp") {
                    template_url  += '&bot_wsp_id=' + response["bot_wsp_id"];
                }
                window.location.href = template_url;
         
            } else if(response["status"] == 401) {
                show_campaign_toast(response["status_message"]);
            } else {
                var error_message = "Not able to open schedule page. Please try again";
                var error_element = delete_campaign_modal.querySelector('.error_element');
                show_campaign_toast(error_element, error_message);
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);
}

function delete_campaigns(element, campaign_id_list) {
    var delete_campaign_modal = element.closest('.modal');
    var error_element = delete_campaign_modal.querySelector('.error_element');
    error_element.innerHTML = "";

    var request_params = {
        "campaign_ids": campaign_id_list,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/delete-campaigns/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let error_message = '';
                if (IN_PROGRESS_SELECTED){
                    error_message = "Selected campaigns deleted successfully! In-Progress campaigns cannot be deleted."
                    IN_PROGRESS_SELECTED = false
                } else{
                    error_message = "Successfully deleted campaigns."
                }
                show_campaign_error_message(error_element, error_message, false);

                setTimeout(function(){
                    $(delete_campaign_modal).modal('hide');
                }, 1000);
                window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns(SELECTED_DATE_FILTER, CHECKED_STATUS, START_DATE, END_DATE, ACTIVE_CHANNELS);
                document.getElementById("delete_campaign_btn").disabled = true;
                document.getElementById("delete_campaign_schedule_btn").disabled = true;
            } else if(response["status"] == 401) {
                var campaign_list = response["campaigns"];
                var error_message = "Not able to delete campaign(s) because below campaigns are in progress state\n"
                for(var idx = 0; idx < campaign_list.length; idx ++) {
                    error_message += String(idx +1) + ". " + campaign_list[idx] + "\n";
                }

                show_campaign_error_message(error_element, error_message);
            } else {
                var error_message = "Not able to delete campaign(s). Please try again";
                show_campaign_error_message(error_element, error_message);
            }
        } else if(this.readyState == 4 && this.status == 403){
            $("#delete_campaign_modal").modal("hide");
            $('.campaign-delete-modal-content-text').hide()
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);
}

function delete_specific_campaign(element, campaign_id) {
    delete_campaigns(element, [campaign_id])
}

function delete_selected_campaigns(element) {
    var select_campaign_cbs = document.querySelectorAll(".campaign_select_row_cb");
    let in_progress_select_campaign_cbs = document.querySelectorAll(".in_progress_campaign_select_row_cb");
    var campaign_ids = [];

    for(var idx = 0; idx < select_campaign_cbs.length; idx ++) {
        if(select_campaign_cbs[idx].checked) {
            var campaign_id = select_campaign_cbs[idx].getAttribute("campaign_id");
            campaign_ids.push(campaign_id);
        }
    }
    for(let idx = 0; idx < in_progress_select_campaign_cbs.length; idx ++) {
        if(in_progress_select_campaign_cbs[idx].checked) {
            IN_PROGRESS_SELECTED = true;
        }
    }

    delete_campaigns(element, campaign_ids);
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
        var _this = this;
        _this.initialize();
    }

    add_event_listeners() {
        var _this = this;
        var delete_buttons = _this.button_display_div.querySelectorAll(".tag_delete_button");
        delete_buttons.forEach((delete_button) => {
            delete_button.addEventListener('click', function (event) {
                _this.tag_delete_button_click_listner(event)
            });
        });

        var select_element = _this.select_element;
        select_element.addEventListener("change", function (event) {
            _this.tag_select_listnet(event);
        })
    }

    tag_delete_button_click_listner(event) {
        var _this = this;
        var target = event.target;
        var key = target.previousElementSibling.getAttribute("key");
        var index = _this.find_index_of_element(key, _this.selected_values);
        if (index != -1) {
            var target_obj = _this.selected_values[index];
            if (_this.selected_values.length == 2) {
                show_campaign_toast("Atleast two columns must be selected at a moment.");
                return;
            }
            _this.selected_values.splice(index, 1);
            _this.unselected_values.push(target_obj);
            _this.initialize();
        }
    }

    tag_select_listnet(event) {
        var _this = this;
        var target = event.target;
        var key = target.value;
        var index = _this.find_index_of_element(key, _this.unselected_values);
        if (index != -1) {
            var target_obj = _this.unselected_values[index];
            _this.selected_values.push(target_obj);
            _this.unselected_values.splice(index, 1);
            _this.initialize();
        }
    }

    find_index_of_element(key, list) {
        for (var index = 0; index < list.length; index++) {
            if (list[index].key == key) return index;
        }
        return -1;
    }

    find_unselected_element_by_key(key) {
        var _this = this;
        var target_obj = null;
        _this.unselected_values.forEach((obj) => {
            if (obj.key == key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    find_selected_element_by_key(key) {
        var _this = this;
        var target_obj = null;
        _this.selected_values.forEach((obj) => {
            if (obj.key == key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    onmouseover_tag = function (element) {
        var handler = element.querySelector("svg");
        handler.style.display = "";
    }

    onmouseout_tag = function (element) {
        var handler = element.querySelector("svg");
        handler.style.display = "none";
    }

    get_tag_input_html() {
        var _this = this;
        var tag_input_html = '<ul class="cognoai-custom-tag-input mt-3">';

        _this.selected_values.forEach((obj, index) => {
            tag_input_html += [
                '<li class="bg-primary">',
                '<svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 2px; display:flex;">',
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
        var _this = this;
        var tag_select_html = '<select class="form-control">';
        tag_select_html += '<option disabled selected> Choose column name </option>';

        _this.unselected_values.forEach((obj, index) => {
            tag_select_html += '<option value="' + obj.key + '"> ' + obj.value + '</option>';
        });

        tag_select_html += '</select>';
        return tag_select_html;
    }

    initialize() {
        var _this = this;
        var html = "";
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
        var _this = this;

        var elements = _this.button_display_div.children;
        var new_list = [];
        for (var idx = 0; idx < elements.length; idx++) {
            var element = elements[idx];
            var value_display_span = element.querySelector(".value_display_span");
            var key = value_display_span.getAttribute("key");
            var index = _this.find_index_of_element(key, _this.selected_values);
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

        var _this = this;

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
        var _this = this;
        var elements = _this.container.querySelectorAll(".drag-handle");
        if (elements.length == 0) {
            elements = _this.container.children;
        }
        for (var index = 0; index < elements.length; index++) {
            var element = elements[index];
            var target_element = _this.get_target_element(element);

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
                var data = {
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
        var _this = this;
        var handle = element;
        while (handle.parentElement != _this.container)
            handle = handle.parentElement;
        return handle;
    }

    drag_element(direction, e) {
        var _this = this;
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

                var left = _this.element.offsetLeft;
                var top = _this.element.offsetTop;

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
        var _this = this;
        // _this.currX = Math.max(_this.currX, 0);

        _this.element.style.left = _this.currX + "px";
        _this.element.style.top = _this.currY + "px";
    }

    compute() {
        var _this = this;

        _this.element.hidden = true;
        let elemBelow = document.elementFromPoint(_this.clientX, _this.clientY);
        _this.element.hidden = false;

        try {
            var target_element = _this.get_target_element(elemBelow);
            if (target_element) {

                var pWidth = $(target_element).innerWidth(); //use .outerWidth() if you want borders
                var pOffset = $(target_element).offset();
                var x = _this.pageX - pOffset.left;
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

var applied_filter = ['4','','','']

function show_custom_date(el) {
    if (el.id == 'campaign_overview_custom_date_btn') {
        document.getElementById('campaign-custom-date-select-area-flow').style.display = 'flex';
    } else {
        document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';
    }
}

function show_schedule_custom_date(el) {
    if (el.id == 'campaign_schedule_overview_custom_date_btn') {
        document.getElementById('campaign-schedule-custom-date-select-area-flow').style.display = 'flex';
    } else {
        document.getElementById('campaign-schedule-custom-date-select-area-flow').style.display = 'none';
    }
}

function apply_campaign_filter() {
    active_campaign_data_loader();
    var selected_date_filter = $("input[type='radio'][name='campaign-overview-filter']:checked").val();
    var status_elems = document.getElementsByName('campaign-overview-filter-status');

    if (!selected_date_filter) {
        show_campaign_toast('Please select date range');
        return;
    }

    var start_date, end_date;
    if (selected_date_filter == '5') {
        start_date = document.getElementById('campaign_filter_custom_start_date').value;
        end_date = document.getElementById('campaign_filter_custom_end_date').value;

        let date_validation_message = check_date_range_validation(start_date,end_date);
        if (date_validation_message != ""){
            show_campaign_toast(date_validation_message);
            return;
        }
    }

    var checked_status = []
    for (elem of status_elems) {
        if (elem.checked) checked_status.push(elem.value);
    }

    applied_filter = [selected_date_filter, checked_status, start_date, end_date];
    let filters = get_url_multiple_vars();
    clear_filters = {}

    clear_filters['bot_pk'] = filters['bot_pk'];
    clear_filters['channels'] = filters['channels'];
    clear_filters['tab'] = filters['tab'];
    if (filters['searched_campaign']) {
        clear_filters['searched_campaign'] = filters['searched_campaign'][0];
    }
    clear_filters['filter_date_type'] = selected_date_filter;

    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(clear_filters)
    initialize_active_campaign_table(selected_date_filter, checked_status, start_date, end_date, channels);
    $("#campaign_custom_filter_modal").modal("hide");
}

function apply_campaign_schedule_filter() {
    active_campaign_data_loader();
    var selected_date_filter = $("input[type='radio'][name='campaign-schedule-overview-filter']:checked").val();
    var status_elems = document.getElementsByName('campaign-schedule-overview-filter-status');

    if (!selected_date_filter) {
        show_campaign_toast('Please select date range');
        return;
    }

    var start_date, end_date;
    if (selected_date_filter == '5') {
        start_date = document.getElementById('campaign_schedule_filter_custom_start_date').value;
        end_date = document.getElementById('campaign_schedule_filter_custom_end_date').value;

        let date_validation_message = check_date_range_validation(start_date, end_date);
        if (date_validation_message != "") {
            show_campaign_toast(date_validation_message);
            return;
        }
    }

    var checked_status = []
    for (elem of status_elems) {
        if (elem.checked) checked_status.push(elem.value);
    }

    applied_filter = [selected_date_filter, checked_status, start_date, end_date];
    let filters = get_url_multiple_vars();
    clear_filters = {}

    clear_filters['bot_pk'] = filters['bot_pk'];
    clear_filters['channels'] = filters['channels'];
    clear_filters['tab'] = filters['tab'];
    if (filters['searched_campaign']) {
        clear_filters['searched_campaign'] = filters['searched_campaign'][0];
    }
    clear_filters['filter_date_type'] = selected_date_filter;

    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(clear_filters)
    initialize_active_campaign_table(selected_date_filter, checked_status, start_date, end_date, channels);
    $("#campaign_custom_filter_modal_schedules").modal("hide");
}

function clear_filter() {
    active_campaign_data_loader();
    document.getElementById('campaign_overview_beg').checked = true;
    document.getElementById('campaign_filter_custom_start_date').value = DEFAULT_START_DATE;
    document.getElementById('campaign_filter_custom_end_date').value = DEFAULT_END_DATE;
    document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';

    var status_elems = document.getElementsByName('campaign-overview-filter-status');
    for (elem of status_elems) {
        elem.checked = false;
    }

    let filters = get_url_multiple_vars();

    clear_filters = {}
    applied_filter = []
    clear_filters['bot_pk'] = filters['bot_pk']
    clear_filters['tab'] = filters['tab']
    if (filters['searched_campaign']) {
        clear_filters['searched_campaign'] = filters['searched_campaign'][0];
    }
    clear_filters['channels'] = filters['channels']

    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(clear_filters);
    initialize_active_campaign_table('4', '', '', '', channels);
}

function clear_schedule_filter() {
    active_campaign_data_loader();
    document.getElementById('campaign_schedule_overview_beg').checked = true;
    document.getElementById('campaign_schedule_filter_custom_start_date').value = DEFAULT_START_DATE;
    document.getElementById('campaign_schedule_filter_custom_end_date').value = DEFAULT_END_DATE;
    document.getElementById('campaign-schedule-custom-date-select-area-flow').style.display = 'none';

    var status_elems = document.getElementsByName('campaign-schedule-overview-filter-status');
    for (elem of status_elems) {
        elem.checked = false;
    }

    let filters = get_url_multiple_vars();

    clear_filters = {}
    applied_filter = []
    clear_filters['bot_pk'] = filters['bot_pk']
    clear_filters['tab'] = filters['tab']
    if (filters['searched_campaign']) {
        clear_filters['searched_campaign'] = filters['searched_campaign'][0];
    }
    clear_filters['channels'] = filters['channels']

    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(clear_filters);
    initialize_active_campaign_table('4', '', '', '', channels);
}

function check_select_date_range(el, export_type) {
    var selected_range = el.value;

    if(selected_range == '4') {
        document.getElementById('from-date-div-'+export_type).style.display = 'block';
        document.getElementById('to-date-div-'+export_type).style.display = 'block';
    } else {
        document.getElementById('from-date-div-'+export_type).style.display = 'none';
        document.getElementById('to-date-div-'+export_type).style.display = 'none';
    }

}

function validate_email(email) {
    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

    return regEmail.test(email);
}

function export_multi_request(el) {
    var bot_id = get_url_multiple_vars()['bot_pk'][0];

    var start_date, end_date, campaign_id;
    request_date_type = document.getElementById('select-date-range-2').value;

    if (request_date_type == '0') {
        show_campaign_toast('Please select a date range');
        return;
    }

    if (request_date_type == '4') {
        start_date = document.getElementById('startdate').value;
        end_date = document.getElementById('enddate').value;
        if (is_valid_date(start_date) && is_valid_date(end_date)) {
            start_date = change_date_format_original(start_date);
            end_date = change_date_format_original(end_date);

            let date_validation_message = check_date_range_validation(start_date,end_date)

            if (date_validation_message != ""){
                show_campaign_toast(date_validation_message);
                return;
            }
        } else {
            show_campaign_toast('Please enter a valid start and end date.');
            return;
        }
       
    }

    var email_id = document.getElementById('filter-data-email-2').value;

    if (email_id == '') {
        show_campaign_toast('Please enter your Email ID');
        return;
    }

    if (!validate_email(email_id)) {
        show_campaign_toast('Please enter a valid Email ID');
        return;
    }

    send_export_request_to_server(bot_id, email_id, '2', request_date_type, campaign_id, start_date, end_date);
}

function open_single_export_modal(campaign_id, is_test_report=false) {
    var campaign_detail = campaign_details[campaign_id]
    let total_count = campaign_detail.message_sent + campaign_detail.message_unsuccessful

    if (is_test_report == true) {
        var bot_id = get_url_multiple_vars()['bot_pk'][0];
        let total_test_count = campaign_detail.test_failed + campaign_detail.test_sent
        send_export_request_to_server(bot_id, '', '4', '', campaign_id, '', '', true, total_test_count);
    }
    else if (total_count <= 5000){
        var bot_id = get_url_multiple_vars()['bot_pk'][0];
        send_export_request_to_server(bot_id, '', '1', '', campaign_id, '', '', true, total_count);
    } else {
        document.getElementById('single_request_btn').dataset.id = campaign_id;

        $('#campaign_single_export_modal').modal('show');
    }
}

function export_single_request(el) {
    var bot_id = get_url_multiple_vars()['bot_pk'][0];
    var campaign_id = el.dataset.id;

    var email_id = document.getElementById('filter-data-email-1').value;

    if (email_id == '') {
        show_campaign_toast('Please enter your Email ID');
        return;
    }

    if (!validate_email(email_id)) {
        show_campaign_toast('Please enter valid Email ID');
        return;
    }

    send_export_request_to_server(bot_id, email_id, '1', '', campaign_id, '', '');
}

function send_export_request_to_server(bot_id, email_id, export_type, request_date_type, campaign_id, start_date, end_date, is_instant_download=false, total_count=0) {
    if (export_type == 1 || export_type == 4){
        if (is_instant_download && total_count > 500){
            IS_DOWNLOAD_IN_PROGRESS = true;
            $(".campaign-overview-download-report-btn").addClass("campaign-overview-download-report-btn-disabled")
            show_campaign_toast('The file download will begin shortly, please wait for some time.', 7000);
            $('.download_report_div').tooltip($(function () {
                $('[data-toggle="tooltip"]').tooltip()
              }))
        }
    }
    var request_params = {
        'bot_id': bot_id,
        'email_id': email_id,
        'export_type': export_type,
        'campaign_id': campaign_id,
        'start_date': start_date,
        'end_date': end_date,
        'request_date_type': request_date_type,
        'is_instant_download': is_instant_download,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/export-campaign-report/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (is_instant_download){
                    if (total_count <= 500) {
                        show_campaign_toast('Downloading the requested report.');
                    } else{
                        $(".campaign-overview-download-report-btn").removeClass("campaign-overview-download-report-btn-disabled");
                        $('.download_report_div').tooltip($(function () {
                            $('[data-toggle="tooltip"]').tooltip('dispose')
                          }))
                        IS_DOWNLOAD_IN_PROGRESS = false;
                    }
                    window.location.href = window.location.origin + '/' + response['file_path'];
                } else{
                    show_campaign_toast('You will receive the campaign report data dump on the above email ID within 24 hours.');

                    $('#campaign_multi_export_modal').modal('hide');
                    $('#campaign_single_export_modal').modal('hide');
                }

            } else if (response["status"] == 400){
                show_campaign_toast(response.message);
            } else {
                show_campaign_toast(response.message);
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);
}

function change_date_format_original(date)
{
    var dateParts = date.split("-");
    date = dateParts[2]+"-"+dateParts[1]+"-"+dateParts[0];  
    return date.trim();
}

function is_valid_date(date) {
    var date2 = change_date_format_original(date)
    date = new Date(date);
    date2 = new Date(date2);
    var check_date = date instanceof Date && !isNaN(date)
    var check_date2 =date2 instanceof Date && !isNaN(date2)
    return check_date || check_date2;
}

/* Campaign Filter Functions Ends */
function validation_to_save_attachment(){
    if (TEMPLATE_TYPE != 'text'){
        if (!IS_STATIC){
            let dynamic_attactment_column = $('#custom_url_options_selected').val();
            if (dynamic_attactment_column == 'none'){
                successful_save_close();
                $('#is_single_vendor_toaster').css({"display":"none"});
                $('#unsuccessful_save').text("Please provide the required media details before sending the campaign.");
                $('#unsuccessfully_credentials').css({"display":"block"});
                document.getElementById("save_and_confirm_btn").disabled = true;
                return false;
            }
        }
        let attachment_text_field = $('#attachment_text_field').val().trim();
        successful_save_close();
        if (attachment_text_field.length < 1 && IS_STATIC){
            $('#is_single_vendor_toaster').css({"display":"none"});
            $('#unsuccessful_save').text("The media field cannot be empty, please fill in the required details and click on Save and Confirm to proceed.")
            $('#unsuccessfully_credentials').css({"display":"block"});
            $('#media_url_text_field').css("border","1px solid #ff0000");
            return false;
        }
        if (!SAVE_ATTACHMENT && EDITED){
            $('#is_single_vendor_toaster').css({"display":"none"});
            $('#unsuccessful_save').text("The changes done in the Media Details are not saved, please click on Save and Confirm to proceed.")
            $('#unsuccessfully_credentials').css({"display":"block"});
            return false;
        }else if (!EDITED){
            save_attachment_details(false);
        }
    }
    return true;
}


function send_campaign(el) {
    if (!validation_to_save_attachment()){
        return;
    }
    var bot_id = get_url_multiple_vars()['bot_pk'][0];
    var bot_wsp_id = null;

    if (!document.getElementById("campaign-list-select")) {
        show_campaign_toast('No BSP’s are currently configured, please configure a BSP inside “API integration".');
        return;
    } else {
        bot_wsp_id = document.getElementById("campaign-list-select").value;
        if (bot_wsp_id == "none") {
            show_campaign_toast('Please select WhatsApp BSP.');
            return;
        }
    }
    var request_params = {
        'bot_pk': bot_id,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
        'bot_wsp_id': bot_wsp_id,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    document.getElementById("send-campaign-button").disabled = true;
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/send-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                show_campaign_toast('Campaign Sending Process has started');

                setTimeout(function() {
                    window.location.href = window.location.origin + '/campaign/dashboard/?bot_pk=' + bot_id;
                }, 2000)
            } else {
                show_campaign_toast(response.message);
                document.getElementById("send-campaign-button").disabled = false;
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);   
}


function open_clone_modal(campaign_id){
    $(".overview-menu-list").hide();
    $("#duplicate-campaign-modal-"+campaign_id).modal("show");
}


function create_clone_campaign(campaign_id) {
    let cloned_campaign_name = document.getElementById("cloned-campaign-name-" + campaign_id).value;
    cloned_campaign_name = stripHTML(cloned_campaign_name);
    cloned_campaign_name = remove_special_char_from_str(cloned_campaign_name);

    document.getElementById("cloned-campaign-name-" + campaign_id).value = cloned_campaign_name;

    if(check_all_speical_chars(cloned_campaign_name)) {
        document.getElementById('cloned-campaign-error-note-' + campaign_id).innerHTML = 'Campaign name with only special characters are not allowed.'
        document.getElementById("cloned-campaign-name-" + campaign_id).classList.add("error-input-fild");
        return;
    }

    if(cloned_campaign_name.length == 0) {
        document.getElementById('cloned-campaign-error-note-' + campaign_id).innerHTML = "Please enter a valid campaign name.";
        document.getElementById("cloned-campaign-name-" + campaign_id).classList.add("error-input-fild");
        return;
    }

    let request_params = {
        'cloned_campaign_name': cloned_campaign_name,
        'bot_id': BOT_ID,
        'campaign_id': campaign_id,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    let params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/create-clone-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let campaign_id = response["campaign_id"]
                window.location.href = window.location.origin + '/campaign/tag-audience/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id;
            } else if (response["status"] == 301 ){
                document.getElementById('cloned-campaign-error-note-' + campaign_id).innerHTML =response["status_message"]
                document.getElementById("cloned-campaign-name-" + campaign_id).classList.add("error-input-fild");
                return;
            } else {
                show_campaign_toast(response["status_message"]);
            }
            document.getElementById("cloned-campaign-name-" + campaign_id).value = "";
            $("#close-clone-modal-" + campaign_id).click()

        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

$(document).on('click','.dots-btn', function(e) {
    if($(this).siblings(".overview-menu-list").css('display') == 'none'){
        $(".overview-menu-list").hide();
        $(this).siblings(".overview-menu-list").show();
    }
    else{
        $(this).siblings(".overview-menu-list").hide();
    }
});
$(document).mouseup(function(e) {
    const container = $(".overview-menu-wrapper-div");
    if (container.length != 0 && !container.is(e.target) && container.has(e.target).length === 0){
        const language_div = $('.overview-menu-list').length;
        $(".overview-menu-list").hide();
    }
});

function send_rcs_campaign(el) {
    var bot_id = get_url_multiple_vars()['bot_pk'][0];

    var request_params = {
        'bot_pk': bot_id,
        'campaign_id': get_url_multiple_vars()['campaign_id'][0],
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    document.getElementById("send-campaign-button").disabled = true;
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/send-rcs-campaign/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                show_campaign_toast('Campaign Sending Process has started');

                setTimeout(function() {
                    window.location.href = window.location.origin + '/campaign/dashboard/?bot_pk=' + bot_id;
                }, 2000)
            } else {
                show_campaign_toast(response.message);
                document.getElementById("send-campaign-button").disabled = false;
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        } 
    }
    xhttp.send(params);   
}


function set_campaign_body () {
    var el = document.getElementById('template_body');

    if (el) {
        var value = el.innerHTML;
        
        var itr = 0;
        value.match(/\{\{(.*?)\}\}/g).forEach(function(element) {
            value = value.replace(element, `{{${VARIABLES[itr].replace('*', '')}}}`);
            ++itr;
        })

        el.innerHTML = value;
    }
}

function format_am_pm(date) {
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var am_pm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0'+minutes : minutes;
  var str_time = hours + ':' + minutes + ' ' + am_pm;
  return str_time;
}

function get_call_details_html(campaign_id) {
    var campaign_detail = campaign_details[campaign_id];

    var status_str = '';
    for (var i=0; i<campaign_detail.on_status.length; ++i) {
        status_str += campaign_detail.on_status[i];

        if (i < campaign_detail.on_status.length - 1) {
            status_str += ', ';
        }
    }

    return `
    <tr role="row" class="campaign-overview-table-hidden-data-wrapper campaign-show-table-data-details">
    <td colspan="8">
        <div class="row" style="background-color: #ffffff; margin: 0px;">
            <div class="col-md-4 col-sm-12" style="text-align: left; padding: 24px;">
                <div class="campaign-overview-table-hidden-data-heading-div">
                    Call Details :
                     
                    <a class="campaign-tooltip" data-toggle="tooltip" data-placement="top" data-original-title="The call details will be refreshed after every 15 seconds.">
                        <svg class="campaign-tooltip-svg ml-2" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                        </svg>
                    </a>                                                                              
                </div>
                <div class="d-flex mb-3">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Scheduled -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.call_scheduled == undefined ? 'NA': campaign_detail.call_scheduled} </div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Failed -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.call_failed == undefined ? 'NA': campaign_detail.call_failed} </div>

                    </div>

                </div>
                <div class="d-flex mb-3">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Initiated -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.call_initiated == undefined ? 'NA': campaign_detail.call_initiated} </div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">In progress -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.call_in_progress == undefined ? 'NA': campaign_detail.call_in_progress} </div>

                    </div>

                </div>
                <div class="d-flex">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Completed -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.call_completed == undefined ? 'NA': campaign_detail.call_completed} </div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Invalid -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.call_invalid == undefined ? 'NA': campaign_detail.call_invalid} </div>

                    </div>

                </div>
            </div>
            <div class="col-md-6 col-sm-12 table-hidden-campaign-details-wrapper" style="text-align: left; padding: 24px;">
                <div class="campaign-overview-table-hidden-data-heading-div">
                    Campaign Details :
                    <a class="campaign-tooltip ml-2" data-toggle="tooltip" data-placement="top" data-original-title="The campaign details will be refreshed after every 15 seconds.">
                        <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                        </svg>
                    </a>
                </div>
                <div class="d-flex mb-3">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Retry Mechanism -</div>
                        <div class="campaign-overview-table-hidden-data-value" style="text-transform: capitalize;">${campaign_detail.retry_mechanism == undefined ? 'NA': campaign_detail.retry_mechanism}</div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Caller ID -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.caller_id == undefined ? 'NA': campaign_detail.caller_id} </div>

                    </div>
                </div>
                <div class="d-flex mb-3">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Number of retries -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.no_of_retries == undefined ? 'NA': campaign_detail.no_of_retries} </div>

                    </div>
                    
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">App ID -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.app_id == undefined ? 'NA': campaign_detail.app_id} </div>

                    </div>

                </div>
                <div class="d-flex">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Retry Intervals (mins) -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.retry_interval == undefined ? 'NA': campaign_detail.retry_interval}</div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Start Date Time -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.start_date == undefined ? 'NA': campaign_detail.start_date}, ${campaign_detail.start_time == undefined ? 'NA': campaign_detail.start_time} </div>

                    </div>

                </div>

                <div class="d-flex mt-3">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">On Status -</div>
                        <div class="campaign-overview-table-hidden-data-value">${status_str}</div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">End Date Time -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.end_date == undefined ? 'NA': campaign_detail.end_date}, ${campaign_detail.end_time == undefined ? 'NA': campaign_detail.end_time} </div>

                    </div>

                </div>
            </div>
            <div class="col-md-2 col-sm-12" style="text-align: left; padding: 28px; position: relative;">
                <a 
                    ${!['completed', 'partially_completed'].includes(campaign_detail.status) ? 'class="campaign-overview-download-report-btn campaign-overview-download-report-btn-disabled"' : 'class="campaign-overview-download-report-btn"'} 
                     href="javascript:void(0)" onclick="open_single_export_modal(${campaign_id})">Download Report</a></div>

        </div>
    </td>
</tr>
    `
}

function get_whatsapp_campaign_details(campaign_id) {
    var campaign_detail = campaign_details[campaign_id];

    let html =  `<tr role="row" class="campaign-overview-table-hidden-data-wrapper campaign-show-table-data-details">
    <td colspan="8">
        <div class="row" style="background-color: #ffffff; margin: 0px; position: relative;">
            <div class="col-md-6 col-sm-12" style="text-align: left; padding: 24px 32px 24px 24px">
                <div class="campaign-overview-table-hidden-data-heading-div"style="    justify-content: space-between;">
                  <div class="campaign-tooltip"data-toggle="tooltip" data-placement="top" data-original-title="The message details will be refreshed after every 15 seconds."> Campaign Statistics : 
                 </div>
                 <div class="total-messages-submitted-overview-page mb-0">
                <div class="d-flex"> <h1 class="total-messages-submitted-heading-overview mb-0">Total Messages Submitted -<span class="campaign-tooltip" data-toggle="tooltip" data-placement="top" title="" data-original-title="Total number of messages submitted to WhatsApp. This count includes the Campaign Messages and Test Messages.">
                     <svg class="campaign-overview-icon" width="10" height="11" viewBox="0 0 10 11" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <g clip-path="url(#clip0_1_3627)">
                        <path d="M5 0.5C7.7615 0.5 10 2.739 10 5.5C10 8.261 7.7615 10.5 5 10.5C2.2385 10.5 0 8.261 0 5.5C0 2.739 2.2385 0.5 5 0.5ZM5 1.3335C2.7025 1.3335 0.8335 3.2025 0.8335 5.5C0.8335 7.7975 2.7025 9.6665 5 9.6665C7.2975 9.6665 9.1665 7.7975 9.1665 5.5C9.1665 3.2025 7.2975 1.3335 5 1.3335ZM5 7.25C5.27614 7.25 5.5 7.47383 5.5 7.75C5.5 8.02617 5.27614 8.25 5 8.25C4.72386 8.25 4.5 8.02617 4.5 7.75C4.5 7.47383 4.72386 7.25 5 7.25ZM5 2.875C5.75939 2.875 6.375 3.49061 6.375 4.25C6.375 4.75538 6.22622 5.03702 5.84944 5.42929L5.76517 5.51517C5.45422 5.82611 5.375 5.95814 5.375 6.25C5.375 6.45711 5.20711 6.625 5 6.625C4.79289 6.625 4.625 6.45711 4.625 6.25C4.625 5.74462 4.77377 5.46298 5.15057 5.07071L5.23483 4.98483C5.54578 4.67389 5.625 4.54186 5.625 4.25C5.625 3.90482 5.34518 3.625 5 3.625C4.67639 3.625 4.41023 3.87094 4.37823 4.18609L4.375 4.25C4.375 4.45711 4.20711 4.625 4 4.625C3.79289 4.625 3.625 4.45711 3.625 4.25C3.625 3.49061 4.24061 2.875 5 2.875Z" fill="#737373"/>
                        </g>
                        <defs>
                        <clipPath id="clip0_1_3627">
                        <rect width="10" height="10" fill="white" transform="translate(0 0.5)"/>
                        </clipPath>
                        </defs>
                        </svg>
                     </span></h1></div>
                 <span class="total-messages-submitted-count-overview"id="total_processed_value">${campaign_detail.message_processed}</span>
                </div>
                </div>
                <div class="campaign-overview-table-hidden-data-subheading-div">Campaign Messages</div>
                <div class="d-flex mb-3 gap-10">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Sent -
                            <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="This is the number of messages sent to the audience batch file. This count does not include the Test Messages sent.">
                                <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                                </svg>
                            </a>
                        </div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.message_sent}</div>


                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                    <div class="campaign-overview-table-hidden-data-label">Delivered -
                        <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="This is the number of messages delivered to the audience batch file.">
                            <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                            </svg>
                        </a>
                    </div>
                    <div class="campaign-overview-table-hidden-data-value">${campaign_detail.message_delivered}</div>

                </div>


                </div>
                <div class="d-flex mb-3 gap-10">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Failed -
                            <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="Total number of messages that failed to reach the users. This count does not include the Test Messages failed.">
                                <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                                </svg>
                            </a>
                        </div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.message_unsuccessful} </div>

                    </div>

                    <div class="d-flex campaign-table-hidden-data-container">
                    <div class="campaign-overview-table-hidden-data-label">Read -
                        <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title='Total number of messages that have been read by people in the audience batch file. Note that if the user has disabled "Read Receipts", their count will be excluded.'>
                            <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                            </svg>
                        </a>
                    </div>
                    <div class="campaign-overview-table-hidden-data-value">${campaign_detail.message_read} </div>

                </div>

                </div>
                <div class="d-flex gap-10">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Replied -
                            <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="This is the number of messages replied by recipients in the audience batch file by clicking on the quick reply buttons.">
                                <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                                </svg>
                            </a>
                        </div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.message_replied} </div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                    <div class="campaign-overview-table-hidden-data-label">
                    </div>
                    <div class="campaign-overview-table-hidden-data-value"></div>

                </div>

                </div>
                <div class="d-flex">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label"></div>
                        <div class="campaign-overview-table-hidden-data-value"> </div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label"></div>
                        <div class="campaign-overview-table-hidden-data-value"></div>

                    </div>

                </div>
                <div class="campaign-overview-table-hidden-data-subheading-div" style="margin-top:24px;">Test Messages</div>
                <div class="d-flex gap-10">

                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Sent -
                            <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="Total number of messages sent as a part of the Test Campaign.">
                                <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                                </svg>


                            </a>
                        </div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.test_sent}</div>

                    </div>
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Failed -
                            <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="Total number of messages that failed to reach the users as a part of the Test Campaign.">
                                <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                                </svg>


                            </a>
                        </div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.test_failed} </div>

                    </div>

                </div>
            </div>
            <div class="col-md-6 col-sm-12 table-hidden-campaign-details-wrapper" style="text-align: left; padding: 28px 12px 38px 1px;">
                <div style="width:max-content;"class="campaign-overview-table-hidden-data-heading-div campaign-tooltip"data-toggle="tooltip" data-placement="top" data-original-title="The campaign details will be refreshed after every 15 seconds.">
                    Campaign Details :
                </div>
                <div class="campaign-overview-table-hidden-data-subheading-div">Basic Information</div>

                <div class="d-flex mb-3">

                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Started On -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.start_datetime} </div>

                    </div>

                    <div class="d-flex campaign-table-hidden-data-container"style="width:65%;">
                        <div class="campaign-overview-table-hidden-data-label">Total Audience -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.total_audience} </div>

                    </div>
                </div>

                <div class="d-flex mb-3">

                    <div class="d-flex campaign-table-hidden-data-container">
                    <div class="campaign-overview-table-hidden-data-label">Submitted On -</div>
                    <div class="campaign-overview-table-hidden-data-value">${campaign_detail.processed_datetime} </div>

                </div>
                  

                    <div class="d-flex campaign-table-hidden-data-container"style="width:65%;">
                    <div class="campaign-overview-table-hidden-data-label width-open-rate">Open Rate - <a class="campaign-tooltip" style="text-decoration: none;position: relative;top: -1px;" data-toggle="tooltip" data-placement="top" data-original-title="This measures the percentage of recipients who opened and read the messages after it was delivered to them">
                    <svg class="campaign-tooltip-svg" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"></path>
                    </svg>
                </a></div>
                    <div class="campaign-overview-table-hidden-data-value">${campaign_detail.open_rate}%</div>

                </div>

                </div>
                <div class="d-flex mb-3">
                <div class="d-flex campaign-table-hidden-data-container">
                <div class="campaign-overview-table-hidden-data-label">Batch Name - </div>
                <div class="campaign-overview-table-hidden-data-value">${campaign_detail.batch_name}</div>
                </div>
                 </div>
                 <div class="d-flex mb-3">
                    <div class="d-flex campaign-table-hidden-data-container">
                        <div class="campaign-overview-table-hidden-data-label">Template -</div>
                        <div class="campaign-overview-table-hidden-data-value">${campaign_detail.template_name}</div>

                    </div>



                </div>
            </div>
            <div style="position: absolute; right: 160px; bottom: 15px;" class="download_report_div campaign-tooltip" data-toggle="tooltip" data-placement="top" data-original-title="You can export this report once the requested campaign report download is completed.">
            <div
                ${campaign_detail.times_campaign_tested == 0 ? 'class="campaign-overview-download-report-btn campaign-overview-download-report-btn-disabled"' : 'class="campaign-overview-download-report-btn"'}
                  onclick="open_single_export_modal(${campaign_id}, true)"><span class="cloud-svg">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 1.75V9.625" stroke="#0254D7" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M3.0625 5.6875L7 9.625L10.9375 5.6875" stroke="#0254D7" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2.1875 11.8125H11.8125" stroke="#0254D7" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                 </span>Test Campaign Report</div>

             </div>
            <div style="position: absolute; right: 24px; bottom: 15px;" class="download_report_div campaign-tooltip" data-toggle="tooltip" data-placement="top" data-original-title="You can export this report once the requested campaign report download is completed.">
            <div
                ${!['completed', 'partially_completed', 'failed', 'processed', 'ongoing'].includes(campaign_detail.status) || IS_DOWNLOAD_IN_PROGRESS ? 'class="campaign-overview-download-report-btn campaign-overview-download-report-btn-disabled"' : 'class="campaign-overview-download-report-btn"'}
                  onclick="open_single_export_modal(${campaign_id})"><span class="cloud-svg">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 1.75V9.625" stroke="#0254D7" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M3.0625 5.6875L7 9.625L10.9375 5.6875" stroke="#0254D7" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2.1875 11.8125H11.8125" stroke="#0254D7" stroke-width="1.3125" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                 </span>Campaign Report</div>

            </div>   
    </td>
</tr>`
if (!['completed', 'partially_completed', 'failed', 'processed', 'ongoing'].includes(campaign_detail.status) && IS_DOWNLOAD_IN_PROGRESS){
$('.download_report_div').tooltip($(function () {
    $('[data-toggle="tooltip"]').tooltip()
  }))
} else{
    $('.download_report_div').tooltip($(function () {
        if(IS_DOWNLOAD_IN_PROGRESS){
            $('[data-toggle="tooltip"]').tooltip()
        }else{
            $('[data-toggle="tooltip"]').tooltip('dispose')
        }
      }))
}
return html;

}

function get_rcs_campaign_details(campaign_id) {
    
    var campaign_detail = campaign_details[campaign_id];
    return `
    <tr role="row" class="campaign-overview-table-hidden-data-wrapper campaign-show-table-data-details">
        <td colspan="8">
            <div class="row" style="background-color: #ffffff; margin: 0px;">
                <div class="col-md-5 col-sm-12" style="text-align: left; padding: 28px;">
                    <div class="campaign-overview-table-hidden-data-heading-div">
                        Message Details :
                        <!-- tooltip text is diffrent for whatsapp this is just dummy text -->
                        <a class="campaign-tooltip" data-toggle="tooltip" data-placement="top" data-original-title="The message details will be refreshed after every 15 seconds.">
                            <svg class="campaign-tooltip-svg ml-2" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                            </svg>
                        </a>
                    </div>
                    <div class="d-flex mb-3">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Submitted -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.submitted == undefined ? 'NA': campaign_detail.submitted}</div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Read -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.read == undefined ? 'NA': campaign_detail.read}</div>

                        </div>

                    </div>
                    <div class="d-flex mb-3">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Sent -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.sent == undefined ? 'NA': campaign_detail.sent}</div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Failed -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.failed == undefined ? 'NA': campaign_detail.failed}</div>

                        </div>

                    </div>
                    <div class="d-flex mb-3">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Delivered -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.delivered == undefined ? 'NA': campaign_detail.delivered}</div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container" style="visibility: hidden !important">
                            <div class="campaign-overview-table-hidden-data-label">Replied -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.replied == undefined ? 'NA': campaign_detail.replied}</div>

                        </div>

                    </div>
                    <div class="d-flex">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label"></div>
                            <div class="campaign-overview-table-hidden-data-value"> </div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label"></div>
                            <div class="campaign-overview-table-hidden-data-value"></div>

                        </div>

                    </div>
                </div>
                <div class="col-md-5 col-sm-12 table-hidden-campaign-details-wrapper" style="text-align: left; padding: 28px 28px 28px 10px;">
                    <div class="campaign-overview-table-hidden-data-heading-div">
                        Campaign Details :
                        <!-- tooltip text is diffrent for whatsapp this is just dummy text -->
                        <a class="campaign-tooltip" data-toggle="tooltip" data-placement="top" data-original-title="The campaign details will be refreshed after every 15 seconds.">
                            <svg class="campaign-tooltip-svg ml-2" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 0C13.9707 0 18 4.0302 18 9C18 13.9698 13.9707 18 9 18C4.0293 18 0 13.9698 0 9C0 4.0302 4.0293 0 9 0ZM9 1.5003C4.8645 1.5003 1.5003 4.8645 1.5003 9C1.5003 13.1355 4.8645 16.4997 9 16.4997C13.1355 16.4997 16.4997 13.1355 16.4997 9C16.4997 4.8645 13.1355 1.5003 9 1.5003ZM9 12.15C9.49706 12.15 9.9 12.5529 9.9 13.05C9.9 13.5471 9.49706 13.95 9 13.95C8.50294 13.95 8.1 13.5471 8.1 13.05C8.1 12.5529 8.50294 12.15 9 12.15ZM9 4.275C10.3669 4.275 11.475 5.3831 11.475 6.75C11.475 7.65968 11.2072 8.16664 10.529 8.87272L10.3773 9.0273C9.81759 9.587 9.675 9.82465 9.675 10.35C9.675 10.7228 9.37279 11.025 9 11.025C8.62721 11.025 8.325 10.7228 8.325 10.35C8.325 9.44032 8.59279 8.93336 9.27103 8.22727L9.4227 8.0727C9.98241 7.513 10.125 7.27535 10.125 6.75C10.125 6.12868 9.62132 5.625 9 5.625C8.41751 5.625 7.93842 6.06769 7.88081 6.63497L7.875 6.75C7.875 7.12279 7.57279 7.425 7.2 7.425C6.82721 7.425 6.525 7.12279 6.525 6.75C6.525 5.3831 7.6331 4.275 9 4.275Z" fill="#737373"/>
                            </svg>
                        </a>
                    </div>
                    <div class="d-flex mb-3">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Template Name -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.template_name == undefined ? 'NA': campaign_detail.template_name}</div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Start Date Time - </div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.start_date_time == undefined ? 'NA': campaign_detail.start_date_time}</div>

                        </div>

                    </div>
                    <div class="d-flex mb-3">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">Message Type -</div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.template_type == undefined ? 'NA': campaign_detail.template_type}</div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label">End Date Time - </div>
                            <div class="campaign-overview-table-hidden-data-value">${campaign_detail.end_date_time == undefined ? 'NA': campaign_detail.end_date_time}</div>

                        </div>
                        

                    </div>
                    <div class="d-flex">
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label"></div>
                            <div class="campaign-overview-table-hidden-data-value"></div>

                        </div>
                        <div class="d-flex campaign-table-hidden-data-container">
                            <div class="campaign-overview-table-hidden-data-label"></div>
                            <div class="campaign-overview-table-hidden-data-value"></div>

                        </div>

                    </div>
                </div>
                <div class="col-md-2 col-sm-12" style="text-align: left; padding: 28px; position: relative;">
                    <a 
                        ${!['completed', 'partially_completed', 'failed', 'processed'].includes(campaign_detail.status) ? 'class="campaign-overview-download-report-btn campaign-overview-download-report-btn-disabled"' : 'class="campaign-overview-download-report-btn"'}
                         href="javascript:void(0)" onclick="open_single_export_modal(${campaign_id})">Download Report</a></div>

            </div>
        </td>
    </tr>
    `
}

function set_campaign_details_obj(campaign_data) {
    for (var data of campaign_data) {
        campaign_details[data.campaign_id] = data;
    }
}

function sanitize_html(unsafe) {
    return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}

function trigger_session_time_out_modal(){
    $('#session_timeout_modal').show();

}
document.getElementById("campaign-search-bar")?.addEventListener("search", function(event) {
    apply_campaign_name_search()
});
document.getElementById("campaign-schedule-search-bar")?.addEventListener("search", function (event) {
    apply_campaign_schedule_name_search()
});

function apply_campaign_name_search() {
    active_campaign_data_loader();
    let searched_campaign = document.getElementById("campaign-search-bar").value.trim();
    document.getElementById("campaign-search-bar").value = searched_campaign;

    // Changed overview pagination on search input change.
    let filters = get_url_multiple_vars();
    if (searched_campaign == "" && 'searched_campaign' in filters) {
        filters['searched_campaign'][0] = "";
    }
    filters.page = ['1'];
    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(filters);

    if (searched_campaign != "") {
        SEARCHED_CAMPAIGN = searched_campaign
    } else {
        SEARCHED_CAMPAIGN = "";
    }
    if (applied_filter.length > 0) {
        window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns(applied_filter[0], applied_filter[1], applied_filter[2], applied_filter[3], channels);
    } else {
        window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns('4', '', '', '', channels);
    }
}
function apply_campaign_schedule_name_search() {
    active_campaign_data_loader();
    let searched_campaign = document.getElementById("campaign-schedule-search-bar").value.trim();
    document.getElementById("campaign-schedule-search-bar").value = searched_campaign;
    // Changed overview pagination on search input change.
    let filters = get_url_multiple_vars();
    if (searched_campaign == "" && 'searched_campaign' in filters) {
        filters['searched_campaign'][0] = "";
    }
    filters.page = ['1'];
    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(filters);

    if (searched_campaign != "") {
        SEARCHED_CAMPAIGN = searched_campaign
    } else {
        SEARCHED_CAMPAIGN = "";
    }
    if (applied_filter.length > 0) {
        window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns(applied_filter[0], applied_filter[1], applied_filter[2], applied_filter[3], channels);
    } else {
        window.ACTIVE_CAMPAIGN_TABLE.fetch_active_campaigns('4', '', '', '', channels);
    }
}
const search_campaign_name = debounce(function() {
    apply_campaign_name_search()
})

const search_schedule_campaign_name = debounce(function () {
    apply_campaign_schedule_name_search()
})

function active_campaign_data_loader(){
    $('#no-data-loader').show();
    $('#campaign_table_wrapper').hide();
    $('#campaign_table_pagination_div').hide();
    $('#table_no_data_found').hide();
    $('.custom_filter_btn').prop('disabled', true);
    $('.custom_metadata_btn').prop('disabled', true);
    $('.custom_export_btn').prop('disabled', true);
}

function deactive_campaign_data_loader(){
    $('#no-data-loader').hide();
    $('#campaign_table_wrapper').show();    
    $('#campaign_table_pagination_div').show();
    $('.custom_filter_btn').prop('disabled', false);
    $('.custom_metadata_btn').prop('disabled', false);
    $('.custom_export_btn').prop('disabled', false);
}

function opentab(evt, tabName) {
    setActiveTab()
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";

    var url_filter = get_url_multiple_vars()

    clear_filters = {}

    clear_filters['bot_pk'] = url_filter['bot_pk'];
    // clear_filters['channels'] = filters['channels'];
    clear_filters['tab'] = url_filter['tab'];
    clear_filters['filter_date_type'] = '4';
    clear_filters['selected_status'] = [];
    clear_filters['searched_campaign'] = '';
    SEARCHED_CAMPAIGN = ""

    url_filter.tab[0] = tabName
    window.ACTIVE_CAMPAIGN_TABLE.update_url_with_filters(clear_filters);
    initialize_active_campaign_table('4', '', '', '', channels);
}

function setActiveTab() {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById("campaign-search-bar").value = "";
    document.getElementById("campaign-schedule-search-bar").value = "";
}