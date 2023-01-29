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

    $('.tms-tooltip').tooltip();

    $(".positive_numeric").on("keypress input", function(event) {
        var keyCode = event.which;
     
        if ( (keyCode != 8 || keyCode ==32 ) && (keyCode < 48 || keyCode > 57)) { 
            return false;
        }

        var self = $(this);
        self.val(self.val().replace(/\D/g, ""));
    });

    $(".mobile_number").on("keypress", tms_mobile_number_validation);

    window.CONSOLE_THEME_COLOR = getComputedStyle(document.body).getPropertyValue('--color_rgb');

    $('#selected-agent-filter').multiselect({
        nonSelectedText: 'Select Agent',
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        includeSelectAllOption: true
    });

    initialize_agent_comment_editor();

}

function process_agent_comment(agent_comment){
    var regex = /&lt;|&gt;/g;
    agent_comment = agent_comment.replace(regex, "");
    return agent_comment;
}

function get_agent_comment_html(process){
    let agent_comment = $("#agent_comment_editor").trumbowyg('html');
    if(process == true){
        agent_comment = process_agent_comment(agent_comment)
    }
    return agent_comment;
}

function get_agent_comment_text(process){
    let agent_comment = document.querySelector("#agent_comment_editor").innerText;
    if(process == true){
        agent_comment = process_agent_comment(agent_comment)
    }
    return agent_comment;
}

function clear_agent_comment_editor(){
    $("#agent_comment_editor").trumbowyg('empty')
}

function initialize_agent_comment_editor(){
    let agent_comment_editor = document.querySelector("#agent_comment_editor");
    $(agent_comment_editor).trumbowyg({
        autogrow: true,
        tagsToKeep: [],
        allowTagsFromPaste: {
            allowedTags: ['h4', 'p', 'br']
        },
        btns: [
            // ['viewHTML'],
            ['undo', 'redo'], // Only supported in Blink browsers
            ['formatting'],
            ['strong', 'em', 'del'],
            ['superscript', 'subscript'],
            // ['link'],
            // ['insertImage'],
            ['justifyLeft', 'justifyCenter', 'justifyRight', 'justifyFull'],
            ['unorderedList', 'orderedList'],
            // ['horizontalRule'],
            // ['removeformat'],
            // ['fullscreen']
        ]
    });

    agent_comment_editor.removeEventListener("keydown", agent_comment_input_action);
    agent_comment_editor.addEventListener("keydown", agent_comment_input_action);
}

function agent_comment_input_action(event){
    if(['<', '>'].indexOf(event.key) >= 0){
        event.preventDefault();
    }
}

function tms_mobile_number_validation(event){
    var element = event.target;
    var value = element.value;
    var count = value.length;

    if ((event.keyCode >= 48 && event.keyCode <= 57) || (event.keyCode >= 96 && event.keyCode <= 105)) { 
        if(count >= 10){
            event.preventDefault();
        }
    }
}

function window_resize() {
    tooltip_utility_change();
}

function window_pop_state_listener(){
    if(window.TMS_ACTIVE_TICKETS_TABLE){
        window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
    }
}

document.querySelector("#content-wrapper").addEventListener(
    "scroll", 
    function(){
        var datepicket_dropdown = document.querySelector(".datepicker-dropdown");
        if(datepicket_dropdown){
            document.body.removeChild(datepicket_dropdown);
        }
    }
)

/****************************** TMS SIDE BAR ******************************/

function change_sales_logo_property() {
    var is_sidebar_toggled = false;
    if (document.getElementById("accordionSidebar").getAttribute("class").indexOf("toggled") != -1) {
        set_cookie("sidebar-tms", "", path = "/");
        if (window.matchMedia("(min-width: 720px)")) {
            $('#accordianSidebar').css({
                "position": "fixed"
            });
        }
    } else {
        set_cookie("sidebar-tms", "toggled", path = "/");
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
}

function adjust_sidebar() {
    if (get_cookie("sidebar-tms") == "") {
        document.getElementById("accordionSidebar").classList.remove("toggled");
    } else if (get_cookie("sidebar-tms") == "toggled") {
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

        document.addEventListener("click", function(event) {
            var parent = $(event.target).closest("#accordionSidebar, #sidebarToggleTop");
            if (parent.length === 0) {
                if (document.getElementById("accordionSidebar").classList.contains('toggled')) {
                    document.getElementById("sidebarToggleTop").click();
                }
            }
        });
    }

}

function change_active_sidenav_option(){
    let nav_items = document.getElementsByClassName("nav-item-menu");

    let index = 0;
    for(index=0; index< nav_items.length; index++){
        nav_items[index].classList.remove("active");
    }

    for(index=0; index< nav_items.length; index++){
        if(nav_items[index].children[0].pathname==window.location.pathname){
            nav_items[index].classList.add("active");

            if($(nav_items[index]).closest('.nav-item-submenu')) {
              $(nav_items[index]).closest('.collapse').collapse();
            }
        }
    }
}

/****************************** TMS CONSOLE TOOLTIP ******************************/

function tooltip_utility_change() {
    if (window.innerWidth <= 767) {
        $('.tooltip-navbar').tooltip('dispose');
        $('.tooltip-navbar').css('width', '');
    } else {
        if (get_cookie("sidebar-tms") == "toggled") {
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

/****************************** TMS CONSOLE TOAST ******************************/

function show_desk_toast(message) {
    var element = document.getElementById("cognodesk-snackbar");
    element.innerHTML = message;
    element.className = "show";
    setTimeout(function() {
        element.className = element.className.replace("show", "");
    }, 5000);
}

function cognoai_celebrate(){
    document.querySelector(".cogno-celebration").style.display = "flex";
    setTimeout(function(){
        document.querySelector(".cogno-celebration").style.display = "none";
    }, 4000);
}

/****************************** TMS CONSOLE COOKIE ******************************/

function get_cookie(cookiename) {
    var cookie_name = cookiename + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var cookie_array = decodedCookie.split(';');
    for (let i = 0; i < cookie_array.length; i++) {
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
    } catch (err) {}

    var regex = /(<([^>]+)>)/ig;
    return text.replace(regex, "");
}

function remove_special_characters_from_str(text) {
    var regex = /:|;|'|"|=|-|\$|\*|%|!|`|~|&|\^|\(|\)|\[|\]|\{|\}|\[|\]|#|<|>|\/|\\/g;
    text = text.replace(regex, "");
    return text;
}

function get_url_multiple_vars() {
    let vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        if (!(key in vars)) {
            vars[key] = [];
        }
        vars[key].push(value);
    });
    return vars;
}

/****************************** GET ACTIVE AGENT SPECIFIC SETTINGS ******************************/


function get_active_agent_console_settings() {

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/active-agent-metadata/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var active_agent_metadata = response.agent_metadata;
                window.ACTIVE_AGENT_METADATA = active_agent_metadata;

                window.AGENT_SERVER_WEBSOCKET = new CognoAIWebsocket(window.ACTIVE_AGENT_METADATA.active_agent_details.agent_username, "agent");

                window.TMS_TICKET_DISPLAY_MANAGER = new TMSTicketDisplayManager();

                if(window.location.pathname.indexOf("/tms/dashboard") == 0){
                    initialize_lead_data_metadata_update_modal();
                    window.TMS_ACTIVE_TICKETS_TABLE = new TMSActiveTicketsTable(document.querySelector("#active_users_table"));
                }

                if(window.location.pathname.indexOf("/tms/notifications") == 0){
                    window.TMS_USER_NOTIFICATION_MANAGER = new TMSNotificationManager();
                }
            }
        }
    }
    xhttp.send("{}");
}

get_active_agent_console_settings();

class TMSBase {
    update_table_attribute(table_elements) {
        for (let idx = 0; idx < table_elements.length; idx++) {
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
            for (let row_index = 0; row_index < tbody_el.rows.length; row_index++) {
                if (tbody_el.rows[row_index].children.length != thead_el.rows[0].children.length) {
                    continue;
                }
                for (let col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
                    var column_element = tbody_el.rows[row_index].children[col_index];
                    var th_text = thead_el.rows[0].children[col_index].innerText;
                    column_element.setAttribute("data-content", th_text);
                }
            }
        }
    }

    fetch_ticket_detail(ticket_id, call_back) {
        var request_params = {
            "ticket_id": ticket_id,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/get-ticket-details/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    var ticket_details = response.ticket_details;
                    call_back(ticket_details);
                } else {
                    show_desk_toast("Something went wrong");
                    console.log("RESPONSE get-ticket-details : ", response);
                }
            }
        }
        xhttp.send(params);
    }

}

/************************************************************ TMS SIGNAL STARTS ************************************************************/

var CognoAIWebsocket = (function () {
    function CognoAIWebsocket(websocket_token, sender) {
        this.websocket_token = CryptoJS.MD5(websocket_token).toString();
        this.sender = sender;
        this.websocket = null;
        this.websocket_open = false;
        this.heartbeat_timer = null;

        this.create_websocket();
    }
    CognoAIWebsocket.prototype.create_websocket = function(){
        var _this = this;

        var ws_scheme = window.location.protocol == "http:" ? "ws" : "wss";
        var url = ws_scheme + '://' + window.location.host + '/ws/tms-signal/' + _this.websocket_token + '/' + _this.sender + "/";
        if (_this.websocket == null) {
            _this.websocket = new WebSocket(url);
            _this.websocket.onmessage = function(event){
                _this.on_message(event);
            };
            _this.websocket.onerror = function(event){
                _this.on_error(event);
            };
            _this.websocket.onopen = function(event){
                _this.on_open(event);
            };
            _this.websocket.onclose = function(event){
                _this.on_close(event);
            };
        }
    }
    CognoAIWebsocket.prototype.on_error = function(event){
        var _this = this;

        // console.error("WebSocket error observed:", e);
        try {
            _this.websocket.close();
            clearInterval(_this.heartbeat_timer);
        } catch (err) {
            _this.websocket.onmessage = null;
            _this.websocket = null;
            setTimeout(function() {
                _this.create_websocket();
            }, 1000)
        }

        console.log("on_error = ", event);
    }
    CognoAIWebsocket.prototype.on_open = function(event){
        var _this = this;

        console.log("web socket connected successfully");

        _this.websocket_open = true;
        if (_this.heartbeat_timer == null) {
            _this.heartbeat_timer = setInterval(function(e) {
                _this.send_heartbeat();
            }, 5000);
        }
    }
    CognoAIWebsocket.prototype.send_message = function(message){
        var _this = this;

        if (_this.websocket_open && _this.websocket != null) {
            _this.websocket.send(JSON.stringify({
                "message": {
                    "header": {
                        "sender": _this.sender
                    },
                    "body": message
                }
            }));
        }
    }
    CognoAIWebsocket.prototype.send_heartbeat = function(){
        var _this = this;

        var json_string = JSON.stringify({
            "type": "heartbeat",
        });

        var encrypted_data = tms_custom_encrypt(json_string);
        encrypted_data = {
            "Request": encrypted_data
        };

        _this.send_message(encrypted_data);
    }
    CognoAIWebsocket.prototype.on_close = function(){
        var _this = this;

        _this.websocket_open = false;
        if (_this.websocket == null) {
            return;
        }
        _this.websocket = null;
        clearInterval(_this.heartbeat_timer);
        setTimeout(function() {
            _this.create_websocket();
        }, 1000);
    }
    CognoAIWebsocket.prototype.on_message = function(event){
        var _this = this;

        var data = JSON.parse(event.data);
        var message = JSON.parse(data.message);
        var data_packet = message.body.Request;

        data_packet = tms_custom_decrypt(data_packet);
        data_packet = JSON.parse(data_packet);

        if (message.header.sender == "server") {
            if (data_packet.type == "notification") {
                _this.send_notification(data_packet.data.notification_message);
            } else if (data_packet.type == "data_changed") {
                var server_message = data_packet.data;
                console.log("server_message = ", server_message);

                var action_name = server_message.action_name
                var action_info = server_message.action_info;
                var ticket_id = action_info.ticket_id;
                
                try{
                    fetch_and_update_user_notification_count(true);
                } catch(err){}

                try{
                    if(action_info.send_notification == true){
                        _this.send_notification(action_info.notification_message);
                    }
                } catch(err){}

                if(action_name == "new_ticket_assigned"){
                    // window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
                    try{
                        if(window.TMS_ACTIVE_TICKETS_TABLE){
                            window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data('page', 1);
                        }
                    } catch(err){}
                } else if (action_name == "new_user_notification"){
                    // nothing to do as of now
                    if(window.TMS_TICKET_DISPLAY_MANAGER){
                        window.TMS_TICKET_DISPLAY_MANAGER.fetch_ticket_details_and_update(ticket_id, false);
                    }
                    if(window.TMS_ACTIVE_TICKETS_TABLE){
                        window.TMS_ACTIVE_TICKETS_TABLE.fetch_and_update_ticket_details(ticket_id);
                    }
                } else if (action_name == "removed_from_assignee"){
                    // will check if this ticket is visible on desktop then remove it
                    window.TMS_ACTIVE_TICKETS_TABLE.remove_if_showing(ticket_id);
                }
            }
        } else {
            return;
        }
    }
    CognoAIWebsocket.prototype.send_notification = function(notification_message){
        send_desktop_notification(notification_message);
    }
    return CognoAIWebsocket;
})();



const register_service_worker = async () => {
    await navigator.serviceWorker.register('/service-worker-cobrowse.js').then(function() {
            return navigator.serviceWorker.ready;
        })
        .then(function(registration) {
            // adding log for testing purpose
            console.log(registration); // service worker is ready and working...
        });
};


const request_notification_permission = async () => {
    if (Notification.permission !== "granted") {
        await window.Notification.requestPermission();
        // value of permission can be 'granted', 'default', 'denied'
        // granted: user has accepted the request
        // default: user has dismissed the notification permission popup by clicking on x
        // denied: user has denied the request.
    }
};

const setup_service_worker = async () => {
    try {
        await request_notification_permission();
        await register_service_worker();
    } catch (err) {}
};

if ('serviceWorker' in navigator) {
    window.addEventListener('load', async function() {
        setup_service_worker();
    });
}

var last_notification_played_timestamp = null;

function play_notification_sound() {
    if (last_notification_played_timestamp != null) {
        var temp_seconds = parseInt((Date.now() - last_notification_played_timestamp) / 1000)
        if (temp_seconds <= 1) {
            return
        }
    }
    last_notification_played_timestamp = Date.now()
    // let audio_src = 'https://www.soundjay.com/button/sounds/beep-24.mp3';
    try {
        let audio_src = '/files/sounds/notification.mp3';
        let audio_obj = new Audio(audio_src);
        audio_obj.play();
    } catch (err) {
        setTimeout(play_notification_sound, 1000);
    }
}

function send_desktop_notification(notification_message) {

    if (!("Notification" in window)) {

        show_desk_toast("This browser does not support desktop notification");

    } else if (Notification.permission === "granted") {

        var notification = new Notification('Cogno Desk', {
            body: notification_message
        });
        notification.onclick = function() {
            window.location.href = "/tms/dashboard/"
        }

    } else if (Notification.permission !== "denied") {

        Notification.requestPermission().then(function(permission) {
            if (permission === "granted") {
                var notification_obj = new Notification('Cogno Desk', {
                    body: notification_message
                });
                notification_obj.onclick = function() {
                    window.location.href = "/tms/dashboard/"
                }
            }
        });

    }
}

async function send_notification(notification_message) {
    try {
        await navigator.serviceWorker.ready.then(function(serviceWorker) {
            serviceWorker.showNotification("Cogno Desk", {
                body: notification_message
            });
        }, function() {
            send_desktop_notification(notification_message);
        });
    } catch (err) {
        send_desktop_notification(notification_message);
    }
}

/************************************************************ TMS SIGNAL END ************************************************************/

/************************************************************ DASHBOARD SETTINGS STARTS ************************************************************/

/*
    TMSActiveTicketsTable 

    Description :
        - This class is used to do manage active ticket table in dashboard

    Required Parameters : 

        lead_data_cols : column confogurations 
            - received in console meta data - get_active_agent_console_settings
            - window.ACTIVE_AGENT_METADATA.lead_data_cols
        ticket_data : list of ticket information object
            - received in fetch_active_tickets response
        table : active lead table
            - tms_active_lead_table

    initialization : 
        - This is initialized in fetch_active_tickets api response
        - window.TMS_ACTIVE_TICKETS_TABLE
*/

class TMSActiveTicketsTable extends TMSBase {
    constructor(table_container) {
        super();
        this.table_container = table_container;
        this.searchbar_element = document.querySelector("#ticket-details-search-bar");
        this.table = null;
        this.data_table_obj = null;

        this.ticket_data = [];

        this.active_agents = [];

        // key : ticket_id & value : ticket dom reference
        this.ticket_map = {};

        // custome select appled object
        this.ticket_priority_select_objs = [];
        this.ticket_category_select_objs = [];
        this.ticket_assigned_agent_select_objs = [];

        // for which ticket id ticket-status model is opened
        this.status__active_ticket = null;
        // for which ticket id ticket-detail model is opened
        this.details__active_ticket = null;

        this.active_agent_metadata = null;

        this.data_checklist = {
            'active_agent_metadata': false,
            'ticket_data': false,
            'active_agents': false,
        }

        this.options = {
            enable_select_rows: true,
        }

        this.pagination_container = document.getElementById("tms_active_lead_table_pagination_div");

        this.init();
    }

    init(){
        var _this = this;
        _this.fetch_active_tickets();
        _this.fetch_active_agents();
        _this.fetch_active_agent_metadata();

        window.TMS_TICKET_DISPLAY_MANAGER.register_callback_function('status_change', function(ticket_obj){
            _this.fetch_and_update_ticket_details(ticket_obj.ticket_id);
        });
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="tms_active_lead_table" width="100%" cellspacing="0"></table>';
        _this.table = _this.table_container.querySelector("table");

        if(!_this.table) return;
        if(_this.active_agent_metadata.lead_data_cols == 0) return;

        if(_this.active_agent_metadata.active_agent_details.role != "agent"){
            _this.options.enable_select_rows = (_this.ticket_data.length > 0);
        } else {
            _this.options.enable_select_rows = false;
        }

        _this.initialize_head();
        _this.initialize_body();
        _this.add_event_listeners();
        _this.add_event_listeners_in_rows();
        _this.apply_custom_select();
        _this.update_table_attribute([_this.table]);

        document.getElementById("assign-ticket-btn").style.display = "none";
        /*
            ------- saved for future reference -------
            $(_this.table).DataTable().clear().draw();
            $(_this.table).DataTable().destroy(true);
        */
    }

    initialize_head() {
        var _this = this;
        const {enable_select_rows} = _this.options;

        var th_html = "";
        _this.active_agent_metadata.lead_data_cols.forEach((column_info_obj) => {
            if(column_info_obj.selected == false) return;
            var name = column_info_obj.name;
            var display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '">' + display_name + '</th>'
        });

        var select_rows_html = "";
        if(enable_select_rows) {
            select_rows_html = [
                '<th>',
                    '<input type="checkbox" class="ticket_select_all_rows_cb" />',
                '</th>',
            ].join('');
        }

        var  thead_html = [
            '<thead>',
                '<tr>',
                    select_rows_html,
                    th_html,
                '</tr>',
            '</thead>',
        ].join('');

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        var _this = this;

        var ticket_data_list = this.get_rows();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": ticket_data_list,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": true,
            'columnDefs': [{
                    "targets": 0, 
                    "className": "text-center",
                    "width": "4%"
                },
            ],

            initComplete: function(settings) {
                $(_this.table).colResizable({ 
                    disable : true 
                });
                $(_this.table).colResizable({
                    liveDrag:true,
                    minWidth:100,
                    postbackSafe:true,
                });
                _this.apply_pagination();
                _this.show_filter_div();
                _this.add_filter_event_listener();
            },
            createdRow: function( row, data, dataIndex) {
                row.setAttribute("ticket_id", _this.ticket_data[dataIndex].ticket_id);
            },
        });        
    }

    apply_pagination(){
        var _this = this;

        if(_this.ticket_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        var metadata = _this.pagination_metadata;

        var html = "";

        var filter_default_text = "Showing " + metadata.start_point + " to " + metadata.end_point + " of " + metadata.total_count + " entries";

        html += ['<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text=\'' + filter_default_text + '\'>',
                    filter_default_text,
                '</div>'
                ].join('');

        html += ['<div class="col-md-6 col-sm-12">',
                    '<div class="d-flex justify-content-end">',
                        '<nav aria-label="Page navigation example">',
                          '<ul class="pagination">'
                ].join('');

        if(metadata.has_previous){

            html += [
                '<li class="page-item">',
                    '<a class="page-link previous_button" onclick="window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\'page\', ' + metadata.previous_page_number + ')" href="javascript:void(0)" aria-label="Previous">',
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

        if( (metadata.number - 4) > 1 ){
            html += '<li class="page-item"><a class="page-link" onclick="window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\'page\', ' + (metadata.number - 5) + ')" href="javascript:void(0)">&hellip;</a></li>';
        }

        for(let index=metadata.page_range[0]; index<metadata.page_range[1]; index++){
            if(metadata.number == index){
                html += '<li class="active purple darken-3 page-item"><a onclick="window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\'page\', ' + index + ');" href="javascript:void(0)" class="page-link">' + index + '</a></li>'
            } else if(index > (metadata.number-5) && index < (metadata.number+5) ){
                html += '<li class="page-item"><a href="javascript:void(0)" onclick="window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\'page\', ' + index + ');" class="page-link">' + index + '</a></li>';
            }
        }

        if(metadata.num_pages > (metadata.number+4)){
            html += '<li class="page-item"><a href="javascript:void(0)" onclick="window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\'page\', ' + (metadata.number+5) + ');" class="page-link">&hellip;</a></li>';
        }

        if(metadata.has_next){

            html += [
                '<li class="page-item">',
                    '<a class="page-link next_button" onclick="window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\'page\', ' + metadata.next_page_number + ')" href="javascript:void(0)" aria-label="Previous">',
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

        html += [
                  '</ul>',
                '</nav>',
            '</div>',
        '</div>',
        ].join('');

        _this.pagination_container.innerHTML = html;
    }

    add_filter_event_listener(){
        var _this = this;

        // Event listener in searchbar element
        _this.searchbar_element.addEventListener("input", function(event){
            var value = event.target.value;

            if (!_this.data_table_obj) {
                return;
            }

            _this.data_table_obj.search(value).draw();

            var pagination_entry_container = _this.pagination_container.querySelector(".show-pagination-entry-container");

            if(pagination_entry_container){
                var showing_entry_count = _this.table.querySelectorAll("tbody tr[role='row']").length;
                var total_entry = _this.pagination_metadata.end_point - _this.pagination_metadata.start_point + 1;

                if(value.length != 0){
                    var text = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
                    pagination_entry_container.innerHTML = text;
                } else {
                    pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
                }  
            }
        });
    }

    show_filter_div(){
        update_applied_filter();
    }

    update_url_with_filters(filters){
        var key_value = "";
        for(let filter_key in filters){
            var filter_data = filters[filter_key];
            for(let index = 0; index < filter_data.length; index ++) {
                key_value += filter_key + "=" + filter_data[index] + "&";
            }
        }

        var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
        window.history.pushState({path:newurl},'',newurl);
    }

    add_filter_and_fetch_data(key, value){
        var _this = this;
        var filters = get_url_multiple_vars();

        if(key == "page"){
            filters.page = [value];
        } else if(key == "bots"){
            filters.bots = [value];
        } else if(key == "bot_channels"){
            filters.bot_channels = [value];
        }

        _this.update_url_with_filters(filters);
        _this.fetch_active_tickets();
    }

    remove_filter_and_fetch_data(key, value){
        var _this = this;

        var filters = get_url_multiple_vars();

        if(key in filters){
            delete filters[key];
        }

        _this.update_url_with_filters(filters);
        _this.fetch_active_tickets();
    }

    update_ticket_map(){
        var _this = this;

        _this.ticket_data.forEach((ticket_data_obj, index)=>{
            _this.ticket_map[ticket_data_obj.ticket_id] = ticket_data_obj;
        })
    }

    check_and_initialize_table(){
        var _this = this;
        
        if(_this.data_checklist.ticket_data == false) return false;
        if(_this.data_checklist.active_agents == false) return false;
        if(_this.data_checklist.active_agent_metadata == false) return false;

        _this.initialize_table();        
    }

    set_ticket_data(ticket_data){
        var _this = this;
        if(ticket_data){
            _this.ticket_data = ticket_data;
            _this.update_ticket_map();
            this.data_checklist.ticket_data = true;
        }

        _this.check_and_initialize_table();
    }

    set_active_agents(active_agents){
        var _this = this;
        if(active_agents){
            _this.active_agents = active_agents;
            this.data_checklist.active_agents = true;
        }

        _this.check_and_initialize_table();
    }

    set_active_agent_metadata(active_agent_metadata){
        var _this = this;
        if(active_agent_metadata){
            _this.active_agent_metadata = active_agent_metadata;

            _this.active_agent_metadata.lead_data_cols.sort((obj1, obj2) => {
                return obj1.index - obj2.index;
            });
            this.data_checklist.active_agent_metadata = true;
        }

        _this.check_and_initialize_table();
    }

    get_row_html(name, ticket_data_obj){
        var _this = this;

        var data = ticket_data_obj[name];

        var html = "";
        try{
            if(name == "ticket_id") {
                html += '<a href="javascript:void(0)" data-toggle="modal" data-target="#ticket_details" ticket_id="' + ticket_data_obj.ticket_id + '">' + data + '</a>'
            } else if (name == "ticket_status") {
                var ticket_status_obj = ticket_data_obj.ticket_status;

                if(ticket_status_obj){
                    if(ticket_data_obj.is_resolved == false){
                        html += '<a href="javascript:void(0)" class="ticket_status_modal_button" ticket_id="' + ticket_data_obj.ticket_id + '">' + ticket_status_obj.name + '    <svg width="12" height="12" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="svg-theme-color">\
                                <path d="M13.2692 0.730772C14.2436 1.70513 14.2436 3.28489 13.2692\
                                4.25925L4.92447 12.604C4.73142 12.7971 4.49134 12.9364 4.22794\
                                 13.0082L0.661097 13.981C0.270732 14.0875 -0.0874597 13.7293 0.0190035\
                                  13.3389L0.99178 9.77206C1.06361 9.50867 1.20294 9.26858 1.39599 9.07553L9.74075\
                                  0.730772C10.7151 -0.243591 12.2949 -0.243591 13.2692 0.730772ZM9.06478\
                                   2.88586L2.13552 9.81506C2.07117 9.87941 2.02473 9.95944 2.00078\
                                    10.0472L1.26879 12.7312L3.95276 11.9992C4.04056 11.9753 4.12059\
                                     11.9288 4.18494 11.8645L11.114 4.93504L9.06478 2.88586ZM10.4803 \
                                     1.4703L9.80385 2.1461L11.853 4.19597L12.5297 3.51972C13.0956 2.95379 \
                                     13.0956 2.03623 12.5297 1.4703C11.9638 0.904373 11.0462 0.904373 10.4803 \
                                     1.4703Z" fill="#0254D7"></path>\
                            </svg></a>'
                    } else {
                        html += '<a href="javascript:void(0)" class="ticket_status_modal_button" ticket_id="' + ticket_data_obj.ticket_id + '">' + ticket_status_obj.name + '</a>'
                    }
                }else{
                    html += '-';
                }

            } else if (name == "ticket_priority") {
                let possible_priorities = _this.active_agent_metadata.ticket_priorities;
                let selected_obj = ticket_data_obj.ticket_priority;

                if(possible_priorities.length > 0 || selected_obj){
                    if(ticket_data_obj.is_resolved == false){

                        let option_html = "";
                        let selected_pk = -1;

                        possible_priorities.forEach((ticket_priority_obj)=>{
                            if(selected_obj && ticket_priority_obj.pk == selected_obj.pk){
                                option_html += '<option value="' + ticket_priority_obj.pk + '" selected> ' + ticket_priority_obj.name + '</option>';
                                selected_pk = ticket_priority_obj.pk;
                            } else {
                                option_html += '<option value="' + ticket_priority_obj.pk + '"> ' + ticket_priority_obj.name + '</option>';
                            }
                        });

                        if(selected_obj && selected_pk == -1){
                            option_html += '<option value="' + selected_obj.pk + '" selected> ' + selected_obj.name + '</option>';
                            selected_pk = selected_obj.pk;
                        }

                        html += '<select class="form-control ticket_priority_select" ticket_id="' + ticket_data_obj.ticket_id + '" data-select="' + selected_pk + '">';
                        html += option_html;
                        html += "</select>";

                    } else if(selected_obj){
                        html += selected_obj.name;
                    } else {
                        html += "-";
                    }
                } else {
                    html += "-";
                }
            } else if (name == "ticket_category") {
                let possible_categories = _this.active_agent_metadata.ticket_categories;
                let selected_obj = ticket_data_obj.ticket_category;
                let bot_obj = ticket_data_obj.bot;

                if((possible_categories.length > 0 || selected_obj) && bot_obj){
                    if(ticket_data_obj.is_resolved == false){

                        let option_html = "";
                        let selected_pk = -1;

                        possible_categories.forEach((ticket_category_obj)=>{
                            if(ticket_category_obj.is_deleted == false && ticket_category_obj.bot.pk == bot_obj.pk){
                                if(selected_obj && (ticket_category_obj.pk == selected_obj.pk)){
                                    option_html += '<option value="' + ticket_category_obj.pk + '" selected> ' + ticket_category_obj.ticket_category + '</option>';
                                    selected_pk = ticket_category_obj.pk;
                                } else {
                                    option_html += '<option value="' + ticket_category_obj.pk + '"> ' + ticket_category_obj.ticket_category + '</option>';
                                }
                            }
                        });

                        if(selected_obj && selected_pk == -1){
                            option_html += '<option value="' + selected_obj.pk + '" selected> ' + selected_obj.ticket_category + '</option>';
                            selected_pk = selected_obj.pk;
                        }
                        html += '<select class="form-control ticket_category_select" ticket_id="' + ticket_data_obj.ticket_id + '" data-select="' + selected_pk + '">';
                        html += option_html;
                        html += "</select>";
                    } else if(selected_obj) {
                        html += selected_obj.ticket_category;
                    } else {
                        html += "-";
                    }
                } else {
                    html += "-";
                }
            } else if (name == "bot") {
                let bot_obj = ticket_data_obj.bot;

                if(bot_obj){
                    html += "<a href='javascript:void(0)' onclick='window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\"bots\", " + bot_obj.pk + ")'>" + bot_obj.name + "</a>";
                } else {
                    html += "-";
                }
            } else if (name == "bot_channel") {
                var bot_channel_obj = ticket_data_obj.bot_channel;

                if(bot_channel_obj){
                    if(bot_channel_obj.name == "Web"){
                        html += "<a href='javascript:void(0)' onclick='window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\"bot_channels\", \"Web\")'><img height='40px' src='/static/EasyTMSApp/img/web_channel.png'></a>"
                    }else if(bot_channel_obj.name == 'WhatsApp'){
                        html += "<a href='javascript:void(0)' onclick='window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\"bot_channels\", \"WhatsApp\")'><svg width='40' height='40' viewBox='0 0 516 500' fill='none' xmlns='http://www.w3.org/2000/svg'><g filter='url(#filter0_f)'><g filter='url(#filter1_d)'><path d='M23.8265 251.749C23.8113 291.614 34.6369 330.528 55.2143 364.829L21.852 482.033L146.514 450.582C180.861 468.605 219.533 478.102 258.887 478.117H258.989C388.591 478.117 494.093 376.638 494.148 251.932C494.169 191.492 469.731 134.662 425.335 91.9103C380.932 49.1591 321.891 25.6033 258.989 25.5766C129.365 25.5766 23.878 127.04 23.8265 251.749V251.749Z' fill='black'/></g><path d='M23.8265 251.749C23.8113 291.614 34.6369 330.528 55.2143 364.829L21.852 482.033L146.514 450.582C180.861 468.605 219.533 478.102 258.887 478.117H258.989C388.591 478.117 494.093 376.638 494.148 251.932C494.169 191.492 469.731 134.662 425.335 91.9103C380.932 49.1591 321.891 25.6033 258.989 25.5766C129.365 25.5766 23.878 127.04 23.8265 251.749V251.749Z' fill='black' fill-opacity='0.2'/></g><path d='M32.2653 249.394C32.2535 287.734 42.693 325.172 62.5455 358.17L30.366 470.92L150.606 440.666C183.734 457.992 221.032 467.135 258.991 467.148H259.092C384.095 467.148 485.85 369.536 485.902 249.563C485.927 191.426 462.355 136.761 419.528 95.6341C376.709 54.5077 319.759 31.847 259.084 31.821C134.067 31.821 32.316 129.425 32.2653 249.394' fill='#4dcb5a'/><path d='M24.167 249.318C24.1517 289.042 34.9681 327.819 55.5269 362L22.1941 478.789L146.748 447.45C181.064 465.408 219.701 474.873 259.022 474.887H259.123C388.611 474.887 494.02 373.766 494.075 249.501C494.097 189.273 469.68 132.645 425.323 90.0431C380.96 47.4427 321.97 23.9713 259.123 23.9437C129.613 23.9437 24.2185 125.048 24.1661 249.318H24.167ZM98.3394 356.114L93.69 349.028C74.1408 319.2 63.8204 284.73 63.8373 249.333C63.8787 146.044 151.478 62.0128 259.197 62.0128C311.361 62.0331 360.386 81.544 397.261 116.952C434.131 152.358 454.42 199.427 454.405 249.486C454.359 352.779 366.757 436.822 259.124 436.822H259.048C224 436.804 189.629 427.775 159.653 410.704L152.518 406.647L78.6061 425.242L98.3394 356.114Z' fill='url(#paint1_linear)'/><path fill-rule='evenodd' clip-rule='evenodd' d='M200.4 155.1C196.002 145.719 191.373 145.531 187.189 145.366C183.768 145.226 179.85 145.235 175.939 145.235C172.025 145.235 165.664 146.645 160.285 152.283C154.903 157.92 139.736 171.547 139.736 199.263C139.736 226.983 160.775 253.764 163.707 257.526C166.642 261.283 204.321 319.977 263.991 342.558C313.583 361.324 323.675 357.591 334.438 356.653C345.202 355.714 369.172 343.028 374.064 329.873C378.957 316.72 378.957 305.447 377.489 303.09C376.021 300.742 372.107 299.334 366.236 296.516C360.364 293.699 331.502 280.068 326.12 278.191C320.738 276.313 316.824 275.374 312.911 281.014C308.996 286.649 297.753 299.334 294.326 303.091C290.902 306.855 287.478 307.324 281.606 304.507C275.734 301.682 256.826 295.739 234.396 276.548C216.944 261.617 205.163 243.177 201.736 237.538C198.312 231.903 201.37 228.851 204.315 226.043C206.951 223.519 210.187 219.468 213.122 216.178C216.051 212.888 217.03 210.54 218.987 206.784C220.944 203.022 219.965 199.732 218.498 196.916C217.03 194.098 205.621 166.238 200.4 155.1' fill='white'/><defs><filter id='filter0_f' x='18.4383' y='22.1629' width='479.124' height='463.284' filterUnits='userSpaceOnUse' color-interpolation-filters='sRGB'><feFlood flood-opacity='0' result='BackgroundImageFix'/><feBlend mode='normal' in='SourceGraphic' in2='BackgroundImageFix' result='shape'/><feGaussianBlur stdDeviation='1.70686' result='effect1_foregroundBlur'/></filter><filter id='filter1_d' x='0.516268' y='0.827131' width='514.968' height='499.128' filterUnits='userSpaceOnUse' color-interpolation-filters='sRGB'><feFlood flood-opacity='0' result='BackgroundImageFix'/><feColorMatrix in='SourceAlpha' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0'/><feOffset dy='-3.41372'/><feGaussianBlur stdDeviation='10.6679'/><feColorMatrix type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.21 0'/><feBlend mode='normal' in2='BackgroundImageFix' result='effect1_dropShadow'/><feBlend mode='normal' in='SourceGraphic' in2='effect1_dropShadow' result='shape'/></filter><linearGradient id='paint0_linear' x1='258.133' y1='470.92' x2='258.133' y2='31.8206' gradientUnits='userSpaceOnUse'><stop stop-color='#20B038'/><stop offset='1' stop-color='#60D66A'/></linearGradient><linearGradient id='paint1_linear' x1='258.136' y1='478.79' x2='258.136' y2='23.944' gradientUnits='userSpaceOnUse'><stop stop-color='#F9F9F9'/><stop offset='1' stop-color='white'/></linearGradient></defs></svg></a>"
                    }else{
                        html += "<a href='javascript:void(0)' onclick='window.TMS_ACTIVE_TICKETS_TABLE.add_filter_and_fetch_data(\"bot_channels\", \"" + bot_channel_obj.name + "\")'>" + bot_channel_obj.name + "</a>"
                    }
                } else {
                    html += "-";
                }

            } else if (name == "query_attachment") {
                var query_attachment_obj = ticket_data_obj.query_attachment;

                if(query_attachment_obj){
                    html += "<a href='" + query_attachment_obj + "' target='_self'> Click to download </a>"
                    // html += '<a href="' + query_attachment_obj + '" download=""><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"></path><path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"></path><path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"></path><path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"></path><path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"></path></svg></a>';
                } else {
                    html += "-"
                }

            } else if (name == "query_description") {
                var query_description = ticket_data_obj.query_description;

                var total_chars = query_description.length;
                query_description = query_description.substring(0, 15);
                if(total_chars > query_description.length){
                    query_description += "...";
                }

                html += [
                    '<div class="issue-description-tooltip" data-toggle="tooltip" title="Click on Ticket ID to see more details" data-placement="bottom" style="white-space: nowrap;">',
                        query_description,
                    '</div>'
                ].join('');
            } else if (name == "agent_name") {
                let agent_details = ticket_data_obj["agent_details"];

                if(agent_details || _this.active_agents.length>0){
                    if(ticket_data_obj.is_resolved == false){

                        let option_html = "";
                        let selected_agent_pk = -1;
                        let agent_pk = undefined;

                        if(agent_details){
                            agent_pk = agent_details.pk;
                        }

                        _this.active_agents.forEach((agent_obj)=>{
                            if(agent_obj.pk == agent_pk){
                                option_html += '<option value="' + agent_obj.pk + '" selected> ' + agent_obj.agent_username + '</option>';
                                selected_agent_pk = agent_obj.pk;
                            } else {
                                option_html += '<option value="' + agent_obj.pk + '"> ' + agent_obj.agent_username + '</option>';
                            }
                        });

                        if(agent_details && selected_agent_pk == -1){
                            option_html += '<option value="' + agent_details.pk + '" selected> ' + agent_details.agent_username + '</option>';
                            selected_agent_pk = agent_details.pk;
                        }

                        html += '<select class="form-control ticket_assigned_agent" ticket_id="' + ticket_data_obj.ticket_id + '" data-select="' + selected_agent_pk + '">';
                        html += option_html;
                        html += "</select>";
                    } else if(agent_details){
                        html += agent_details.agent_username;
                    } else {
                        html += "-";
                    }
                } else {
                    html += "-";
                }
            } else {
                html += data;
            }

            if(html == undefined){
                console.log("ERROR get_row_html : html undefined");
                html = "";
            }
        }catch(err){
            console.log("ERROR get_row_html : ", err);
            html = "";
        }
        return html;
    }

    get_select_row_html(ticket_data_obj) {
        var _this = this;
        const {enable_select_rows} = _this.options;

        if(!enable_select_rows) {
            return "";
        }

        var select_row_html = '<input class="ticket_select_row_cb" type="checkbox" ticket_id="' + ticket_data_obj.ticket_id + '" />';
        return select_row_html;
    }

    get_row(ticket_data_obj) {
        var _this = this;
        const {enable_select_rows} = _this.options;

        var ticket_data_list = [];

        var select_row_html = _this.get_select_row_html(ticket_data_obj);
        if(enable_select_rows) {
            ticket_data_list.push(select_row_html);
        }

        _this.active_agent_metadata.lead_data_cols.forEach((column_info_obj) => {
            try{
                if(column_info_obj.selected == false) return;
                var name = column_info_obj.name;
                if (name in ticket_data_obj) {
                    ticket_data_list.push(_this.get_row_html(name, ticket_data_obj));
                } else {
                    ticket_data_list.push("-");
                }
            }catch(err){
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        })

        return ticket_data_list;
    }

    get_rows() {
        var _this = this;
        var ticket_data_list = [];
        _this.ticket_data.forEach((ticket_data_obj) => {
            ticket_data_list.push(_this.get_row(ticket_data_obj));
        })
        return ticket_data_list;
    }

    update_ticket_details(ticket_details){
        var _this = this;

        if(!ticket_details) return;

        _this.ticket_map[ticket_details.ticket_id] = ticket_details;
        if(document.querySelector("#ticket_details").style.display == "block" && _this.details__active_ticket == ticket_details.ticket_id){
            _this.ticket_detail_modal_open_listener();
        }

        var updated_row_element = _this.table.querySelector("tbody tr[ticket_id='" + ticket_details.ticket_id + "']");
        if(updated_row_element){
            var row_data_list = _this.get_row(ticket_details);
            $(_this.table).DataTable().row(updated_row_element._DT_RowIndex).data(row_data_list).draw();

            _this.add_event_listeners_in_rows(updated_row_element);
            _this.apply_custom_select(updated_row_element);
        }
    }

    fetch_and_update_ticket_details(ticket_id){
        var _this = this;

        if(!(ticket_id in _this.ticket_map)) return;

        _this.fetch_ticket_detail(ticket_id, function(ticket_details){
            _this.update_ticket_details(ticket_details);
        })
    }

    remove_if_showing(ticket_id){
        var _this = this;

        if( !(ticket_id in _this.ticket_map) ) return;

        _this.fetch_active_tickets();
    }

    ticket_priority_change_listener(event){
        var _this = this;
        var target = event.target;
        var ticket_id = target.getAttribute("ticket_id");
        var selected_priority_pk = target.value;

        var request_params = {
            "ticket_id": ticket_id,
            "selected_priority_pk": selected_priority_pk,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/update-ticket-priority/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    show_desk_toast("Priority Changed");
                    _this.fetch_and_update_ticket_details(ticket_id);
                } else {
                    console.log("ticket_priority_change_listener : ", response)
                    show_desk_toast("Priority Not Changed");
                }
            }
        }
        xhttp.send(params);
    }

    ticket_category_change_listener(event){
        var _this = this;

        var target = event.target;
        var ticket_id = target.getAttribute("ticket_id");
        var selected_category_pk = target.value;

        var request_params = {
            "ticket_id": ticket_id,
            "selected_category_pk": selected_category_pk,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/update-ticket-category/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    show_desk_toast("Category Changed");
                    _this.fetch_and_update_ticket_details(ticket_id);
                } else {
                    console.log("ticket_category_change_listener : ", response)
                    show_desk_toast("Category Not Changed")
                }
            }
        }
        xhttp.send(params);
    }

    assigned_agent_change_listener(event){
        var _this = this;
        var target = event.target;
        var ticket_id = target.getAttribute("ticket_id");
        var selected_agent_pk = target.value;

        var request_params = {
            "ticket_ids": [ticket_id],
            "selected_agent_pk": selected_agent_pk,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/assign-agent/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    show_desk_toast("Agent Assigned");
                    _this.fetch_and_update_ticket_details(ticket_id);
                    // setTimeout(function(){window.location.reload()}, 1000);
                } else {
                    console.log("assigned_agent_change_listener : ", response)
                    show_desk_toast("Agent Not Assigned")
                }
            }
        }
        xhttp.send(params);
    }

    fetch_active_tickets() {
        var _this = this;

        var filters = get_url_multiple_vars();

        var request_params = {
            'page': ( (filters["page"] && filters["page"][0]) || 1),
            'bots': (filters["bots"] || []),
            'bot_channels': (filters["bot_channels"] || []),
            'ticket_status': (filters["ticket_status"] || []),
            'ticket_category': (filters["ticket_category"] || []),
            'ticket_priority': (filters["ticket_priority"] || []),
            'selected_date_filter': ( (filters["selected_date_filter"] && filters["selected_date_filter"][0]) || ''),
            'start_date': ((filters["start_date"] && filters["start_date"][0]) || DEFAULT_START_DATE),
            'end_date': ((filters["end_date"] && filters["end_date"][0]) || DEFAULT_END_DATE),
            'agent_id_list': (filters["agent_id_list"] || []),
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/get-active-tickets/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_ticket_data(response.active_tickets);
                }
            }
        }
        xhttp.send(params);
    }

    fetch_active_agent_metadata() {
        var _this = this;

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/active-agent-metadata/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.set_active_agent_metadata(response.agent_metadata);
                }
            }
        }
        xhttp.send("{}");
    }

    fetch_active_agents() {
        var _this = this;

        var request_params = {};

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/get-mapped-agents/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                     _this.set_active_agents(response.mapped_agents);
                }
            }
        }
        xhttp.send(params);
    }

    ticket_status_modal_open_listener(){
        var _this = this;
        var ticket_obj = _this.ticket_map[_this.status__active_ticket];
        window.TMS_TICKET_DISPLAY_MANAGER.update_ticket_details(ticket_obj, true);
    }

    ticket_detail_modal_open_listener(){
        var _this = this;

        var ticket_obj = _this.ticket_map[_this.details__active_ticket];

        var ticket_status_modal = document.querySelector("#ticket_details");
        var ticket_id = ticket_status_modal.querySelector(".ticket_id");
        var issue_date_time = ticket_status_modal.querySelector(".issue_date_time");
        var customer_name = ticket_status_modal.querySelector(".customer_name");
        var customer_email_id = ticket_status_modal.querySelector(".customer_email_id");
        var customer_mobile_number = ticket_status_modal.querySelector(".customer_mobile_number");
        var query_description = ticket_status_modal.querySelector(".query_description");
        var query_attachment = ticket_status_modal.querySelector(".query_attachment");
        var agent_name = ticket_status_modal.querySelector(".agent_name");
        var ticket_priority = ticket_status_modal.querySelector(".ticket_priority");
        var ticket_category = ticket_status_modal.querySelector(".ticket_category");
        var bot = ticket_status_modal.querySelector(".bot");
        var bot_channel = ticket_status_modal.querySelector(".bot_channel");

        ticket_id.innerHTML = "<p><b> " + "Ticket ID" + " </b> : " + ticket_obj["ticket_id"] + " </p>";
        issue_date_time.innerHTML = "<p><b> " + "Ticket Issue Date" + " </b> : " + ticket_obj["issue_date_time"] + " </p>";

        if(ticket_obj["customer_name"]){
            customer_name.innerHTML = "<p><b> " + "Customer Name" + " </b> : " + ticket_obj["customer_name"] + " </p>";
        } else {
            customer_name.innerHTML = "<p><b> " + "Customer Name" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["customer_email_id"]){
            customer_email_id.innerHTML = "<p><b> " + "Customer Email Id" + " </b> : " + ticket_obj["customer_email_id"] + " </p>";
        } else {
            customer_email_id.innerHTML = "<p><b> " + "Customer Email Id" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["customer_mobile_number"]){
            customer_mobile_number.innerHTML = "<p><b> " + "Customer Mobile Number" + " </b> : " + ticket_obj["customer_mobile_number"] + " </p>";
        } else {
            customer_mobile_number.innerHTML = "<p><b> " + "Customer Mobile Number" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["query_description"]){
            query_description.innerHTML = "<p><b> " + "Issue description" + " </b> : " + ticket_obj["query_description"] + " </p>";
        } else {
            query_description.innerHTML = "<p><b> " + "Issue description" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["query_attachment"]){
            query_attachment.innerHTML = "<p><b> " + "Issue Attachment" + " </b> : " + "<a href='" + ticket_obj["query_attachment"] + "' target='_self'>  Click to download </a>" + " </p>";
        } else {
            query_attachment.innerHTML = "<p><b> " + "Issue Attachment" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["agent_details"]){
            agent_name.innerHTML = "<p><b> " + "Agent" + " </b> : " + ticket_obj["agent_details"]["name"] + " </p>";
        } else {
            agent_name.innerHTML = "<p><b> " + "Agent" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["ticket_priority"]){
            ticket_priority.innerHTML = "<p><b> " + "Ticket Priority" + " </b> : " + ticket_obj["ticket_priority"]["name"] + " </p>";
        } else {
            ticket_priority.innerHTML = "<p><b> " + "Ticket Priority" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["ticket_category"]){
            ticket_category.innerHTML = "<p><b> " + "Ticket Category" + " </b> : " + ticket_obj["ticket_category"]["ticket_category"] + " </p>";
        } else {
            ticket_category.innerHTML = "<p><b> " + "Ticket Category" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["bot"]){
            bot.innerHTML = "<p><b> " + "Bot" + " </b> : " + ticket_obj["bot"]["name"] + " </p>";            
        } else {
            bot.innerHTML = "<p><b> " + "Bot" + " </b> : " + "-" + " </p>";            
        }

        if(ticket_obj["bot_channel"]){
            bot_channel.innerHTML = "<p><b> " + "Channel" + " </b> : " + ticket_obj["bot_channel"]["name"] + " </p>";
        } else{
            bot_channel.innerHTML = "<p><b> " + "Channel" + " </b> : " + "-" + " </p>";
        }
    }

    select_row_checkbox_change_listener(event) {
        var _this = this;
        var select_all_rows_cb = _this.table.querySelector(".ticket_select_all_rows_cb");
        var select_row_cbs = _this.table.querySelectorAll(".ticket_select_row_cb");
        var is_any_selected_ticket_resolved = false;
        var ticket_id = null;

        var total_rows_checked = 0;
        select_row_cbs.forEach((select_row_cb) => {
            if(select_row_cb.checked) {
                total_rows_checked += 1;
                ticket_id = select_row_cb.getAttribute("ticket_id");
                if (document.querySelector('[ticket_id="' + ticket_id + '"][class="ticket_status_modal_button"]').innerText == "RESOLVED") {
                    is_any_selected_ticket_resolved = true;
                }
            }
        });

        if(total_rows_checked == select_row_cbs.length) {
            select_all_rows_cb.checked = true;
        } else {
            select_all_rows_cb.checked = false;
        }

        if(total_rows_checked > 0 && !is_any_selected_ticket_resolved) {
            document.getElementById("assign-ticket-btn").style.display = "";
        } else {
            document.getElementById("assign-ticket-btn").style.display = "none";
        }
    }
    add_event_listeners_in_rows(container=null){
        var _this = this;
        if(container == null) container = _this.table;

        // select row checkbox event listener
        var select_row_cbs = container.querySelectorAll(".ticket_select_row_cb");
        select_row_cbs.forEach((select_row_cb) => {
            select_row_cb.addEventListener("change", (event) => {
                _this.select_row_checkbox_change_listener(event);
            });
        });

        // Ticket Priority Change Event Listner
        var ticket_priority_select_eles = container.querySelectorAll('.ticket_priority_select');
        ticket_priority_select_eles.forEach((ticket_priority_select_ele)=>{
            ticket_priority_select_ele.addEventListener("change", (event)=>{
                _this.ticket_priority_change_listener(event);
            })
        });

        // Ticket Category Change Event Listner
        var ticket_category_select_eles = container.querySelectorAll('.ticket_category_select');
        ticket_category_select_eles.forEach((ticket_category_select_ele)=>{
            ticket_category_select_ele.addEventListener("change", (event)=>{
                _this.ticket_category_change_listener(event);
            })
        });

        // Assigned Agent Change Event Listner
        var ticket_assigned_agent_select_eles = container.querySelectorAll('.ticket_assigned_agent');
        ticket_assigned_agent_select_eles.forEach((ticket_assigned_agent_select_ele)=>{
            ticket_assigned_agent_select_ele.addEventListener("change", (event)=>{
                _this.assigned_agent_change_listener(event);
            })
        });

        // on ticket status click
        var ticket_status_modal_buttons = container.querySelectorAll(".ticket_status_modal_button");
        ticket_status_modal_buttons.forEach((ticket_status_modal_button)=>{
            ticket_status_modal_button.addEventListener("click", (event)=>{
                var triggerElement = event.target;
                triggerElement = triggerElement.closest(".ticket_status_modal_button");
                _this.status__active_ticket = triggerElement.getAttribute("ticket_id");
                _this.ticket_status_modal_open_listener();
            })
        });
    }
    add_event_listeners(){
        var _this = this;

        // Select all row checkbox event listener
        var select_all_rows_cb = _this.table.querySelector(".ticket_select_all_rows_cb");
        if(select_all_rows_cb){
            select_all_rows_cb.addEventListener("change", function() {
                var select_row_cbs = _this.table.querySelectorAll(".ticket_select_row_cb");
                var all_rows_selected = this.checked;
                var is_any_selected_ticket_resolved = false;
                var ticket_id = null;

                select_row_cbs.forEach((select_row_cb) => {
                    if(all_rows_selected) {
                        select_row_cb.checked = true;
                        ticket_id = select_row_cb.getAttribute("ticket_id");
                        if (document.querySelector('[ticket_id="' + ticket_id + '"][class="ticket_status_modal_button"]').innerText == "RESOLVED") {
                            is_any_selected_ticket_resolved = true;
                        }
                    } else {
                        select_row_cb.checked = false;
                    }
                })

                if(all_rows_selected && !is_any_selected_ticket_resolved) {
                    document.getElementById("assign-ticket-btn").style.display = "";
                } else {
                    document.getElementById("assign-ticket-btn").style.display = "none";
                }
            });
        }

        // On ticket id click
        $('#ticket_details').on('shown.bs.modal', function (event) {
            var triggerElement = event.relatedTarget;
            _this.details__active_ticket = triggerElement.getAttribute("ticket_id");
            _this.ticket_detail_modal_open_listener();
        });
    }

    apply_custom_select(container=null){
        var _this = this;
        if(container == null) container = _this.table;

        // Ticket Priority apply custom select
        var ticket_priority_select_eles = container.querySelectorAll('.ticket_priority_select');
        ticket_priority_select_eles.forEach((ticket_priority_select_ele)=>{
            if(ticket_priority_select_ele.getAttribute("data-select") == "-1") {
                ticket_priority_select_ele.selectedIndex = -1;
            }
            var ticket_priority_select_obj = new EasyassistCustomSelect(ticket_priority_select_ele, "Set Priority", window.CONSOLE_THEME_COLOR);
            _this.ticket_priority_select_objs.push(ticket_priority_select_obj);
        });

        // Ticket Category apply custom select
        var ticket_category_select_eles = container.querySelectorAll('.ticket_category_select');
        ticket_category_select_eles.forEach((ticket_category_select_ele)=>{
            if(ticket_category_select_ele.getAttribute("data-select") == "-1") {
                ticket_category_select_ele.selectedIndex = -1;
            }
            var ticket_category_select_obj = new EasyassistCustomSelect(ticket_category_select_ele, "Select Category", window.CONSOLE_THEME_COLOR);
            _this.ticket_category_select_objs.push(ticket_category_select_obj);
        });

        // Assigned Agent apply custom select
        var ticket_assigned_agent_select_eles = container.querySelectorAll('.ticket_assigned_agent');
        ticket_assigned_agent_select_eles.forEach((ticket_assigned_agent_select_ele)=>{
            if(ticket_assigned_agent_select_ele.getAttribute("data-select") == "-1") {
                ticket_assigned_agent_select_ele.selectedIndex = -1;
            }
            var ticket_assigned_agent_select_obj = new EasyassistCustomSelect(ticket_assigned_agent_select_ele, "Select Agent", window.CONSOLE_THEME_COLOR);
            _this.ticket_assigned_agent_select_objs.push(ticket_assigned_agent_select_obj);
        });

        $(".issue-description-tooltip").tooltip();
    }
}

class TMSTicketDisplayManager extends TMSBase {
    constructor() {
        super();
        this.modal = document.querySelector("#ticket_status_modal");
        this.ticket_obj = null;
        this.add_event_listeners();
        this.consumer_callback_functions = {
            'comment': [],
            'status_change': [],
        }
    }
    set_ticket_detials(ticket_obj){
        var _this = this;
        _this.ticket_obj = ticket_obj;
        _this.update_modal_details();
    }
    update_ticket_details(ticket_obj, show=false){
        var _this = this;

        _this.set_ticket_detials(ticket_obj);
        if(show == true){
            $(_this.modal).modal("show");
        }
    }
    fetch_ticket_details_and_update(ticket_id, show=false){
        var _this = this;

        _this.fetch_ticket_detail(ticket_id, function(ticket_details){
            _this.set_ticket_detials(ticket_details);
            if(show == true){
                $(_this.modal).modal("show");
            }
        })
    }
    register_callback_function(type, callback_function){
        var _this = this;

        if(_this.consumer_callback_functions[type].indexOf(callback_function) == -1){
            _this.consumer_callback_functions[type].push(callback_function);
        }
    }
    update_modal_details(){
        var _this = this;
        var ticket_obj = _this.ticket_obj;

        _this.get_ticket_audit_trail();
        var ticket_status_modal = _this.modal;
        var ticket_id = ticket_status_modal.querySelector(".ticket_id");
        var issue_date_time = ticket_status_modal.querySelector(".issue_date_time");
        var customer_name = ticket_status_modal.querySelector(".customer_name");
        var customer_email_id = ticket_status_modal.querySelector(".customer_email_id");
        var customer_mobile_number = ticket_status_modal.querySelector(".customer_mobile_number");
        var query_description = ticket_status_modal.querySelector(".query_description");
        var query_attachment = ticket_status_modal.querySelector(".query_attachment");
        var agent_name = ticket_status_modal.querySelector(".agent_name");
        var ticket_priority = ticket_status_modal.querySelector(".ticket_priority");
        var ticket_category = ticket_status_modal.querySelector(".ticket_category");
        var bot = ticket_status_modal.querySelector(".bot");
        var bot_channel = ticket_status_modal.querySelector(".bot_channel");
        var ticket_resolved_div = ticket_status_modal.querySelector(".ticket_resolved_div");
        var comment_input_area = ticket_status_modal.querySelector(".comment_input_area");

        ticket_id.innerHTML = "<p><b> " + "Ticket ID" + " </b> : " + ticket_obj["ticket_id"] + " </p>";
        issue_date_time.innerHTML = "<p><b> " + "Ticket Issue Date" + " </b> : " + ticket_obj["issue_date_time"] + " </p>";

        if(ticket_obj["customer_name"]){
            customer_name.innerHTML = "<p><b> " + "Customer Name" + " </b> : " + ticket_obj["customer_name"] + " </p>";
        } else {
            customer_name.innerHTML = "<p><b> " + "Customer Name" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["customer_email_id"]){
            customer_email_id.innerHTML = "<p><b> " + "Customer Email Id" + " </b> : " + ticket_obj["customer_email_id"] + " </p>";
        } else {
            customer_email_id.innerHTML = "<p><b> " + "Customer Email Id" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["customer_mobile_number"]){
            customer_mobile_number.innerHTML = "<p><b> " + "Customer Mobile Number" + " </b> : " + ticket_obj["customer_mobile_number"] + " </p>";
        } else {
            customer_mobile_number.innerHTML = "<p><b> " + "Customer Mobile Number" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["query_description"]){
            query_description.innerHTML = "<p><b> " + "Issue description" + " </b> : " + ticket_obj["query_description"] + " </p>";
        } else {
            query_description.innerHTML = "<p><b> " + "Issue description" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["query_attachment"]){
            query_attachment.innerHTML = "<p><b> " + "Issue Attachment" + " </b> : " + "<a href='" + ticket_obj["query_attachment"] + "' target='_self'>  Click to download </a>" + " </p>";
        } else {
            query_attachment.innerHTML = "<p><b> " + "Issue Attachment" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["agent_details"]){
            agent_name.innerHTML = "<p><b> " + "Agent" + " </b> : " + ticket_obj["agent_details"]["name"] + " </p>";
        } else {
            agent_name.innerHTML = "<p><b> " + "Agent" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["ticket_priority"]){
            ticket_priority.innerHTML = "<p><b> " + "Ticket Priority" + " </b> : " + ticket_obj["ticket_priority"]["name"] + " </p>";
        } else {
            ticket_priority.innerHTML = "<p><b> " + "Ticket Priority" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["ticket_category"]){
            ticket_category.innerHTML = "<p><b> " + "Ticket Category" + " </b> : " + ticket_obj["ticket_category"]["ticket_category"] + " </p>";
        } else {
            ticket_category.innerHTML = "<p><b> " + "Ticket Category" + " </b> : " + "-" + " </p>";
        }

        if(ticket_obj["bot"]){
            bot.innerHTML = "<p><b> " + "Bot" + " </b> : " + ticket_obj["bot"]["name"] + " </p>";            
        } else {
            bot.innerHTML = "<p><b> " + "Bot" + " </b> : " + "-" + " </p>";            
        }

        if(ticket_obj["bot_channel"]){
            bot_channel.innerHTML = "<p><b> " + "Channel" + " </b> : " + ticket_obj["bot_channel"]["name"] + " </p>";
        } else{
            bot_channel.innerHTML = "<p><b> " + "Channel" + " </b> : " + "-" + " </p>";
        }

        var is_resolved = ticket_obj["is_resolved"];
        if(is_resolved == false){
            ticket_resolved_div.style.display = "";
            comment_input_area.style.display = "flex";
        } else {
            ticket_resolved_div.style.display = "none";
            comment_input_area.style.display = "none";
        }
    }

    get_ticket_audit_trail(){
        try{
            var _this = this;
            var ticket_obj = _this.ticket_obj;

            var ticket_id = ticket_obj.ticket_id;

            var request_params = {
                "ticket_id": ticket_id,
            };

            var json_params = JSON.stringify(request_params);
            var encrypted_data = tms_custom_encrypt(json_params);
            encrypted_data = {
                "Request": encrypted_data
            };
            var params = JSON.stringify(encrypted_data);

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/tms/get-ticket-audit-trail/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    var response = JSON.parse(this.responseText);
                    response = tms_custom_decrypt(response.Response);
                    response = JSON.parse(response);
                    if (response["status"] == 200) {
                        var audit_trail = response.audit_trail;
                        var audit_trail_html = "";
                        if(audit_trail.length > 0){
                            // audit_trail_html = "<div> <b>audit_trail</b> </div>";
                            audit_trail.forEach((comment)=>{
                                if(comment.action_type == "AGENT_COMMENT"){
                                    audit_trail_html += '<div class="ticket-comment-card">';

                                    audit_trail_html += [
                                        '<div class="ticket-header-and-time-div row">',
                                            '<div class="comment-header col-lg-9"> <p>' + comment.agent_detail.name + " ( " + comment.agent_detail.role + " )" + ' </p> </div>',
                                            '<div class="comment-datetime col-lg-3"> <p class="float-right">' + comment.datetime + '</p> </div>',
                                        '</div>'
                                    ].join("")

                                    if(comment.is_sent_to_customer == true){
                                        audit_trail_html += [
                                            '<div class="comment-message-div row">',
                                                '<div class="normal-comment col-lg-9"> <p> ' + comment.description + ' </p> </div>',
                                                '<div class="special-message col-lg-3"> <p class="float-right"> sent to customer </p> </div>',
                                            '</div>'
                                        ].join("")
                                    }else{
                                        audit_trail_html += '<p> ' + comment.description + ' </p>';
                                    }
                                    audit_trail_html += '</div>';
                                } else if (comment.action_type == "RESOLVED_COMMENT"){
                                    audit_trail_html += '<div class="ticket-comment-card">';

                                    audit_trail_html += [
                                        '<div class="ticket-header-and-time-div row">',
                                            '<div class="comment-header col-lg-9"> <p>' + comment.agent_detail.name + " ( " + comment.agent_detail.role + " )" + ' </p> </div>',
                                            '<div class="comment-datetime col-lg-3"> <p class="float-right">' + comment.datetime + '</p> </div>',
                                        '</div>'
                                    ].join("")

                                    audit_trail_html += [
                                        '<div class="comment-message-div row">',
                                            '<div class="normal-comment col-lg-9"> <p> ' + comment.description + ' </p> </div>',
                                            '<div class="special-message col-lg-3"> <p class="float-right"> resolved comment </p> </div>',
                                        '</div>'
                                    ].join("");
                                    audit_trail_html += '</div>';
                                } else if (comment.action_type == "CUSTOMER_COMMENT") {
                                    let description_dict = JSON.parse(comment.description);
                                    audit_trail_html += '<div class="ticket-comment-card">';

                                    audit_trail_html += [
                                        '<div class="ticket-header-and-time-div row">',
                                            '<div class="comment-header col-lg-9"> <p>' + comment.customer_details.customer_name + " ( customer ) " + ' </p> </div>',
                                            '<div class="comment-datetime col-lg-3"> <p class="float-right">' + comment.datetime + '</p> </div>',
                                        '</div>'
                                    ].join("");

                                    audit_trail_html += [
                                        '<div class="comment-message-div row">',
                                            '<div class="normal-comment col-lg-9"> <p> ' + description_dict.customer_message + ' </p> </div>',
                                        '</div>'
                                    ].join("");

                                    if(description_dict.attachment){
                                        audit_trail_html += [
                                            '<div class="comment-attachment-container">',
                                                '<div class="attachment-div">',
                                                    '<img src="' + description_dict.attachment + '">',
                                                '</div>',
                                                '<div class="attachment-name-div">',
                                                    '<span>',
                                                        "Attachment",
                                                    '</span>',
                                                    '<a href="' + description_dict.attachment + '" target="_blank">',
                                                        '<svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"></path><path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"></path><path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"></path><path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"></path><path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"></path></svg>',
                                                    '</a>',
                                                '</div>',
                                            '</div>',
                                        ].join("");                                        
                                    }

                                    audit_trail_html += '</div>';
                                } else {
                                    audit_trail_html += '<div class="ticket-action-card">';
                                    audit_trail_html += '<p> ' + comment.description + '<label style="float: right;padding-right:1%;">'+ comment.datetime  +'</label></p></div>';
                                }
                            });
                        } else {
                            audit_trail_html = "<div class='no_comment_div'> No Activity </div>";
                        }

                        var comment_div = _this.modal.querySelector(".comment_div");
                        comment_div.innerHTML = audit_trail_html;

                        setTimeout(function(){
                            $(comment_div).animate({scrollTop:comment_div.scrollHeight}, 'slow');
                        }, 300)
                    } else {
                        console.log("ERROR get_ticket_audit_trail response -> ", response);
                        show_desk_toast("Comments not loaded please try again")
                    }
                }
            }
            xhttp.send(params);
        }catch(err){
            console.log("ERROR get_ticket_audit_trail err -> ", err);
        }
    }

    refresh_ticket_options(){
        var _this = this;

        let ticket_resolved_input_ele = _this.modal.querySelector("#ticket_resolved_input");
        if(ticket_resolved_input_ele){
            ticket_resolved_input_ele.checked = false;
        }

        let customer_query_ask_info_ele = _this.modal.querySelector("#customer_query_ask_info");
        if(customer_query_ask_info_ele){
            customer_query_ask_info_ele.checked = false;
        }
    }

    save_agent_comments(){
        try{
            var _this = this;
            var ticket_obj = _this.ticket_obj;

            var ticket_status_modal = _this.modal;
            var comment = get_agent_comment_html(true);
            var comment_text = get_agent_comment_text(true);

            if(comment_text == ""){
                setTimeout(function(){
                    clear_agent_comment_editor();
                }, 50);
                show_desk_toast("Comment can not be empty.");
                return;
            }

            if(comment_text.length > 2000){
                show_desk_toast("Comment should not be more than 2000 characters");
                return;
            }

            var ticket_id = ticket_obj.ticket_id;
            var ticket_resolved_input = ticket_status_modal.querySelector("#ticket_resolved_input");
            var is_resolved = ticket_resolved_input.checked;

            var customer_query_ask_info = ticket_status_modal.querySelector("#customer_query_ask_info");
            var send_to_customer = customer_query_ask_info.checked;

            var request_params = {
                "ticket_id": ticket_obj.ticket_id,
                "comment": comment,
                "is_resolved": is_resolved,
                "send_to_customer": send_to_customer,
            };

            var json_params = JSON.stringify(request_params);
            var encrypted_data = tms_custom_encrypt(json_params);
            encrypted_data = {
                "Request": encrypted_data
            };
            var params = JSON.stringify(encrypted_data);

            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/tms/save-agent-comments/", true);
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    var response = JSON.parse(this.responseText);
                    response = tms_custom_decrypt(response.Response);
                    response = JSON.parse(response);
                    if (response["status"] == 200) {
                        if(is_resolved){
                            if(window.ACTIVE_AGENT_METADATA.cognoai_celebration == true){
                                cognoai_celebrate();
                            }
                            _this.fetch_ticket_detail(ticket_id, function(ticket_details){
                                _this.set_ticket_detials(ticket_details);
                                // _this.update_modal_details();
                                for(let index=0; index<_this.consumer_callback_functions['status_change'].length; index++){
                                    _this.consumer_callback_functions['status_change'][index](_this.ticket_obj);
                                }
                            })
                        } else {
                            _this.get_ticket_audit_trail();
                            clear_agent_comment_editor();
                        }

                        for(let index=0; index<_this.consumer_callback_functions['comment'].length; index++){
                            _this.consumer_callback_functions['comment'][index]();
                        }

                        _this.refresh_ticket_options();
                    } else if(response["status"] == 302){
                        clear_agent_comment_editor();
                    }else {
                        console.log("ERROR save_agent_comments response -> ", response);
                        show_desk_toast("Comment not saved");
                    }
                } else if (this.readyState == 4){
                    show_desk_toast("Internal server error");
                }
            }
            xhttp.send(params);
        }catch(err){
            console.log("ERROR save_agent_comments err -> ", err);
        }
    }

    add_event_listeners(){
        var _this = this;
        var ticket_status_modal = _this.modal;

        var comment_send_btn = ticket_status_modal.querySelector("#comment_send_btn");
        comment_send_btn.addEventListener('click', function(event){
            _this.save_agent_comments();
        })

        $(ticket_status_modal).on('hidden.bs.modal', function (event) {
            clear_agent_comment_editor();
            
            ticket_status_modal.querySelector(".ticket_resolved_div").style.display = "none";
            ticket_status_modal.querySelector("#ticket_resolved_input").checked = false;

            var comment_div = ticket_status_modal.querySelector(" .comment_div");
            comment_div.innerHTML = "";

            ticket_status_modal.querySelector(".comment_input_area").style.display = "none";
        });
    }
}

class TMSNotificationManager extends TMSBase {
    constructor() {
        super();
        this.container = document.querySelector("#unchecked_notification_container");
        this.load_more_button = document.querySelector("#load_more_notifications");
        this.no_notification_div_quote = document.querySelector("#no_notification_div_quote");
        this.no_notification_div_message = document.querySelector("#no_notification_div_message");
        this.notification_data = {}
        this.page = 0;
        this.is_checked = false;
        this.datetime_limit = "";
        this.pagination_metadata = null;
        this.initialize();
    }
    initialize(){
        var _this = this;
        _this.notification_data = {};
        _this.page = 0;
        _this.container.innerHTML = "";
        _this.fetch_notifications();
        _this.add_event_listeners();
    }
    reinitialize(){
        var _this = this;
        _this.notification_data = {};
        _this.page = 0;
        _this.container.innerHTML = "";
        _this.datetime_limit = "";
        _this.fetch_notifications();
    }
    add_event_listeners(){
        var _this = this;
        _this.load_more_button.addEventListener("click", function(){
            _this.fetch_notifications();
        })
    }
    display_quote(){
        var _this = this;
        var random_number = Math.floor((Math.random() * 10000000) + 1);
        random_number = random_number % window.COGNOAI_QUOTES.length;
        var quote = window.COGNOAI_QUOTES[random_number][1];
        var author = window.COGNOAI_QUOTES[random_number][0];
        _this.no_notification_div_quote.querySelector("#tms-no-notification-quote").innerHTML = quote + '<cite _ngcontent-nut-c840="" class="ng-tns-c840-107">' + author + '</cite>';
    }
    manage_display(){
        var _this = this;
        if(Object.keys(_this.notification_data).length == 0){
            if(window.ACTIVE_AGENT_METADATA.cognoai_quote == true){
                if(!window.COGNOAI_QUOTES){
                    $.getJSON(window.location.origin + "/static/EasyTMSApp/cognoai_quotes.json", function(data){
                        window.COGNOAI_QUOTES = data;
                        _this.display_quote();
                    })
                } else {
                    _this.display_quote();
                }
            }

            if(window.ACTIVE_AGENT_METADATA.cognoai_quote == true)
                _this.no_notification_div_quote.style.display = "";
            else
                _this.no_notification_div_message.style.display = "";

            _this.container.style.display = "none";
        } else {
            if(window.ACTIVE_AGENT_METADATA.cognoai_quote == true)
                _this.no_notification_div_quote.style.display = "none";
            else
                _this.no_notification_div_message.style.display = "none";
            _this.container.style.display = "";
        }
    }
    add_user_notification(notification_list){
        var _this = this;
        var updated_ticket_list = [];

        notification_list.forEach((notification_obj)=>{
            var ticket_id = notification_obj.ticket_id;
            _this.notification_data[ticket_id] = [];
        })

        notification_list.forEach((notification_obj)=>{
            var ticket_id = notification_obj.ticket_id;
            if(ticket_id in _this.notification_data){
                _this.notification_data[ticket_id].push(notification_obj);
            } else {
                _this.notification_data[ticket_id] = [notification_obj];
            }
            if(updated_ticket_list.indexOf(ticket_id) == -1){
                updated_ticket_list.push(ticket_id);
            }
        })
        _this.add_notifications_html(updated_ticket_list);

        _this.manage_display();
        fetch_and_update_user_notification_count();
    }
    remove_user_notification(ticket_id){
        var _this = this;

        if(ticket_id in _this.notification_data){
            delete _this.notification_data[ticket_id];
        }

        var notification_container = _this.container.querySelector(".notification_continer[ticket_id=\'" + ticket_id + "\']");
        if(notification_container){
            // $(notification_container.querySelector('[data-toggle="tooltip"]')).tooltip('dispose');
            $('.tooltip').remove();
            notification_container.parentElement.removeChild(notification_container);
        }

        console.log("Object.keys(_this.notification_data).length = ", Object.keys(_this.notification_data).length);
        if(Object.keys(_this.notification_data).length == 0){
            console.log("_this.pagination_metadata = ", _this.pagination_metadata, _this.pagination_metadata.has_next);
            if(_this.pagination_metadata && _this.pagination_metadata.has_next == true){
                _this.page=0;
                _this.fetch_notifications();
            } else {
                if(window.ACTIVE_AGENT_METADATA.cognoai_celebration == true){
                    cognoai_celebrate();
                }
                _this.manage_display();
            }
        }

        fetch_and_update_user_notification_count();
    }
    get_notification_body_inner_html(ticket_id){
        var notification_list = this.notification_data[ticket_id];
        var html = "";

        html += '<div class="row">'

        var total_notification_count = notification_list.length;
        var part_a_start = 0, part_a_end=Math.min(total_notification_count-1, 3);
        var part_b_start = 4, part_b_end=total_notification_count-1;

        while(part_a_start <= part_a_end){
            let notification_obj = notification_list[part_a_start];
            html += [
                '<div class="notification_row col-md-12" notification_pk=\'' + notification_obj.pk + '\'>',
                    notification_obj.description,
                    '<label style="font-size: 12px;float: right;">'+ notification_obj.datetime  +'</label>',
                '</div>'
            ].join('');
            part_a_start++;
        }

        if(part_b_start <= part_b_end){
            html += [
                '<div class="col-md-12" style="text-align: right;">',
                    '<svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 view_more_notf_ticket_wise" data-toggle="tooltip" title="View more" data-placement="bottom" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>',
                '</div>',
            ].join('');
            while(part_b_start <= part_b_end){
                let notification_obj = notification_list[part_b_start];
                html += [
                    '<div class="notification_row col-md-12 hidden_notification_row" style="display: none;" notification_pk=\'' + notification_obj.pk + '\'>',
                        notification_obj.description,
                        '<label style="font-size: 12px;float: right;">'+ notification_obj.datetime  +'</label>',
                    '</div>'
                ].join('');
                part_b_start++;
            }
            html += [
                '<div class="col-md-12" style="text-align: right; display: none;">',
                    '<svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 view_less_notf_ticket_wise" data-toggle="tooltip" title="View Less" data-placement="bottom" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" /></svg>',
                '</div>',
            ].join('');
        }

        html += '</div>';

        return html;
    }
    get_notification_options_html(ticket_id){
        var _this = this;
        var is_checked = _this.is_checked;

        var html = "";
        if(is_checked == false){
            html += [
                '<div class="col-sm-6 notification_options">',
                    '<a class="clear_notification" data-toggle="tooltip" title="Clear notification" data-placement="bottom" style="cursor: pointer;">',
                        '<svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" fill-rule="evenodd" clip-rule="evenodd"><path d="M24 6.278l-11.16 12.722-6.84-6 1.319-1.49 5.341 4.686 9.865-11.196 1.475 1.278zm-22.681 5.232l6.835 6.01-1.314 1.48-6.84-6 1.319-1.49zm9.278.218l5.921-6.728 1.482 1.285-5.921 6.756-1.482-1.313z"/></svg>',
                    '</a>',
                '</div>'
            ].join('');
        } else {
            html += [
                '<div class="col-sm-6 notification_options"></div>'
            ].join('');
        }
        return html;
    }
    get_notification_container_node(ticket_id){
        var _this = this;
        var notification_list = this.notification_data[ticket_id];
        var html_node = document.createElement("div");
        html_node.className = "notification_continer card shadow";
        html_node.setAttribute("ticket_id", ticket_id);

        var html = "";

        var query_description = notification_list[0]['query_description'];
        var total_chars = query_description.length;
        query_description = query_description.substring(0, 50);
        if(total_chars > query_description.length){
            query_description += "...";
        }

        query_description = ticket_id + " : " + query_description
        html = [
            '<div class="notification_header card-header">',
                '<div class="row">',
                    '<div class="col-sm-6">',
                        '<a href="javascript:void(0)" class="ticket_status_modal_button" ticket_id=\'' + ticket_id + '\' data-toggle="tooltip" title="Click to see more details" data-placement="bottom">',
                            query_description,
                        '</a>',
                    '</div>',
                    _this.get_notification_options_html(ticket_id),
                '</div>',
            '</div>',
            '<div class="notification_body card-body">',
                _this.get_notification_body_inner_html(ticket_id),
            '</div>',
        ].join('');

        html_node.innerHTML = html

        return html_node;
    }
    add_notifications_html(updated_ticket_list){
        var _this = this;
        updated_ticket_list.forEach((ticket_id)=>{
            var notification_container_old = _this.container.querySelector(".notification_continer[ticket_id=\'" + ticket_id + "\']");
            var notification_container_new = _this.get_notification_container_node(ticket_id);
            _this.container.insertAdjacentElement("beforeEnd", notification_container_new);
            if(notification_container_old){
                notification_container_old.parentElement.removeChild(notification_container_old);
            }
            _this.add_event_listeners_notification_container(notification_container_new);
        });
        $(".clear_notification").tooltip();
    }
    fetch_notifications() {
        var _this = this;

        _this.page = _this.page + 1;
        var request_params = {
            'page': _this.page,
            'is_checked': _this.is_checked,
            'datetime_limit': _this.datetime_limit,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/fetch-user-notification/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    var notification_list = response.notification_list;
                    var pagination_metadata = response.pagination_metadata;
                    _this.datetime_limit = response.datetime_limit;
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.add_user_notification(notification_list);
                    _this.change_load_more_button_property(pagination_metadata);
                } else {
                    show_desk_toast("Something went wrong");
                    console.log("RESPONSE fetch-user-notification : ", response);
                }
            }
        }
        xhttp.send(params);
    }
    change_load_more_button_property(pagination_metadata){
        var _this = this;
        if(pagination_metadata.has_next == false){
            _this.load_more_button.parentElement.style.display = "none";
        } else {
            _this.load_more_button.parentElement.style.display = "";
        }
    }
    add_event_listeners_notification_container(notification_container){

        console.log("notification_container = ", notification_container);

        var _this = this;
        var clear_notifications_buttons = notification_container.querySelectorAll(".clear_notification");
        clear_notifications_buttons.forEach((clear_notifications_button)=>{
            clear_notifications_button.addEventListener("click", function(event){
                _this.clear_notifications(event);
            })
        })

        // on ticket status click
        var ticket_status_modal_buttons = notification_container.querySelectorAll(".ticket_status_modal_button");
        ticket_status_modal_buttons.forEach((ticket_status_modal_button)=>{
            $(ticket_status_modal_button).tooltip();
            ticket_status_modal_button.addEventListener("click", (event)=>{
                $('.tooltip').remove();
                var triggerElement = event.target;
                var ticket_id = triggerElement.getAttribute("ticket_id");
                window.TMS_TICKET_DISPLAY_MANAGER.fetch_ticket_details_and_update(ticket_id, true);
            })
        });

        // view more notifications button
        var view_more_notf_button = notification_container.querySelector(".view_more_notf_ticket_wise");
        if(view_more_notf_button){
            $(view_more_notf_button).tooltip();
            view_more_notf_button.addEventListener("click", function(event){
                $('.tooltip').remove();
                var target = event.target;
                var notification_continer = target.closest(".notification_continer");
                notification_continer.querySelector(".view_less_notf_ticket_wise").parentElement.style.display = "";
                notification_continer.querySelector(".view_more_notf_ticket_wise").parentElement.style.display = "none";
                $(notification_continer.querySelectorAll(".hidden_notification_row")).css("display","");
            });
        }

        // view less notifications button
        var view_less_notf_button = notification_container.querySelector(".view_less_notf_ticket_wise");
        if(view_less_notf_button){
            $(view_less_notf_button).tooltip();
            view_less_notf_button.addEventListener("click", function(event){
                $('.tooltip').remove();
                var target = event.target;
                var notification_continer = target.closest(".notification_continer");
                notification_continer.querySelector(".view_less_notf_ticket_wise").parentElement.style.display = "none";
                notification_continer.querySelector(".view_more_notf_ticket_wise").parentElement.style.display = "";
                $(notification_continer.querySelectorAll(".hidden_notification_row")).css("display","none");
            });
        }
    }
    clear_notifications(event){
        var _this = this;
        var target = event.target;

        target = target.closest(".notification_continer");

        if(target){
            var ticket_id = target.getAttribute("ticket_id");
            var notification_pk_elements = target.querySelectorAll('.notification_row[notification_pk]');
            var notification_pk_list = [];

            notification_pk_elements.forEach((notification_pk_element)=>{
                notification_pk_list.push(notification_pk_element.getAttribute("notification_pk"));
            })
        }

        var request_params = {
            'notifiction_pk_list': notification_pk_list,
        };

        var json_params = JSON.stringify(request_params);
        var encrypted_data = tms_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/tms/clear-user-notification/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.remove_user_notification(ticket_id);
                } else {
                    show_desk_toast("Something went wrong");
                    console.log("RESPONSE clear-user-notification : ", response);
                }
            }
        }
        xhttp.send(params);
    }
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

    init(){
        var _this = this;
        _this.initialize();
    }

    add_event_listeners(){
        var _this = this;
        var delete_buttons = _this.button_display_div.querySelectorAll(".tag_delete_button");
        delete_buttons.forEach((delete_button)=>{
            delete_button.addEventListener('click', function(event){
                _this.tag_delete_button_click_listner(event)
            });
        });

        var select_element = _this.select_element;
        select_element.addEventListener("change", function(event){
            _this.tag_select_listnet(event);
        })
    }

    tag_delete_button_click_listner(event){
        var _this = this;
        var target = event.target;
        var key = target.previousElementSibling.getAttribute("key");
        var index = _this.find_index_of_element(key, _this.selected_values);
        if(index != -1){
            var target_obj = _this.selected_values[index];
            _this.selected_values.splice(index, 1);
            _this.unselected_values.push(target_obj);
            _this.initialize();
        }
    }

    tag_select_listnet(event){
        var _this = this;
        var target = event.target;
        var key = target.value;
        var index = _this.find_index_of_element(key, _this.unselected_values);
        if(index != -1){
            var target_obj = _this.unselected_values[index];
            _this.selected_values.push(target_obj);
            _this.unselected_values.splice(index, 1);
            _this.initialize();
        }
    }

    find_index_of_element(key, list){
        for(let index=0; index<list.length; index++){
            if(list[index].key == key) return index;
        }
        return -1;
    }

    find_unselected_element_by_key(key){
        var _this = this;
        var target_obj = null;
        _this.unselected_values.forEach((obj)=>{
            if(obj.key == key && target_obj == null){
                target_obj = obj;
            }
        });
        return target_obj;
    }

    find_selected_element_by_key(key){
        var _this = this;
        var target_obj = null;
        _this.selected_values.forEach((obj)=>{
            if(obj.key == key && target_obj == null){
                target_obj = obj;
            }
        });
        return target_obj;
    }

    onmouseover_tag = function(element){
        var handler = element.querySelector("svg");
        handler.style.display = "";
    }

    onmouseout_tag = function(element){
        var handler = element.querySelector("svg");
        handler.style.display = "none";
    }

    get_tag_input_html(){
        var _this = this;
        var tag_input_html = '<ul class="cognoai-custom-tag-input mt-3">';

        _this.selected_values.forEach((obj, index)=>{
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

    get_tag_select_html(){
        var _this = this;
        var tag_select_html = '<select class="form-control">';
        tag_select_html += '<option disabled selected> Choose column name </option>';

        _this.unselected_values.forEach((obj, index)=>{
            tag_select_html += '<option value="' + obj.key + '"> ' + obj.value + '</option>';
        });

        tag_select_html += '</select>';
        return tag_select_html;
    }

    initialize(){
        var _this = this;
        var html = "";
        html += _this.get_tag_input_html();
        html += _this.get_tag_select_html();
        _this.container.innerHTML = html;

        _this.button_display_div = _this.container.querySelector("ul");
        _this.select_element = _this.container.querySelector("select");
        _this.add_event_listeners();
        _this.select_element_obj = new EasyassistCustomSelect(_this.select_element, null, window.CONSOLE_THEME_COLOR);
        _this.drag_obj = new CognoAiDragableTagInput(_this.button_display_div, function(event){
            _this.drag_finish_callback(event)
        });
    }
    drag_finish_callback = function(event){
        var _this = this;

        var elements = _this.button_display_div.children;
        var new_list = [];
        for(let idx=0; idx<elements.length; idx++){
            var element = elements[idx];
            var value_display_span = element.querySelector(".value_display_span");
            var key = value_display_span.getAttribute("key");
            var index = _this.find_index_of_element(key, _this.selected_values);
            new_list.push(_this.selected_values[index]);
        }

        _this.selected_values = new_list;
    }
}

/****************************** Lead Data Metadata Update Model ******************************/

function initialize_lead_data_metadata_update_modal(){
    var lead_data_cols = window.ACTIVE_AGENT_METADATA.lead_data_cols;
    var container = document.querySelector("#lead_dala_table_meta_div");
    var selected_values = [];
    var unselected_values = [];
    lead_data_cols.forEach((obj)=>{
        if(obj.selected == true) {
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
    })
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

function save_lead_data_table_metadata(){
    
    var lead_data_cols = window.ACTIVE_AGENT_METADATA.lead_data_cols;

    var selected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj)=>{
        selected_values.push(obj.key);
    });

    if(selected_values.length < 2){
        show_desk_toast("Atleast two columns needs to be selected.");
        return;
    }

    lead_data_cols.forEach((item, index)=>{
        if(selected_values.indexOf(item.name) >= 0){
            item.selected = true;
            item.index=selected_values.indexOf(item.name);
        } else {
            item.selected = false;
            item.index=window.LEAD_DATA_METADATA_INPUT.selected_values.length;
        }
    })

    lead_data_cols.sort((obj1, obj2) => {
        return obj1.index - obj2.index;
    });

    var request_params = {
        "lead_data_cols": lead_data_cols
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/save-agent-lead-table-metadata/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_agent_metadata();
            }
        }
    }
    xhttp.send(params);
}

function assign_multiple_tickets(element) {

    var error_element = document.getElementById("assign_agent_error");
    error_element.innerHTML = "";

    var select_ticket_cbs = document.querySelectorAll(".ticket_select_row_cb");
    var ticket_ids = [];

    for(let idx = 0; idx < select_ticket_cbs.length; idx ++) {
        if(select_ticket_cbs[idx].checked) {
            var ticket_id = select_ticket_cbs[idx].getAttribute("ticket_id");
            ticket_ids.push(ticket_id);
        }
    }

    var selected_agent_pk = document.getElementById("assign_agent_dropdown").value;
    if(selected_agent_pk == "") {
        error_element.innerHTML = "Please select an agent.";
        error_element.style.color = "red";
        return;
    }

    var request_params = {
        "ticket_ids": ticket_ids,
        "selected_agent_pk": selected_agent_pk,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/assign-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if(response["unassigned_tickets"].length > 0) {
                    error_element.innerHTML = "Some ticket(s) can not be assigned. Please try again.";
                    error_element.style.color = "red";
                } else {
                    error_element.innerHTML = "Successfully assigned agent.";
                    error_element.style.color = "green";
                }
                setTimeout(function(){
                    $('#assign_ticket_modal').modal('hide');
                }, 500);
                window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
                document.getElementById("assign-ticket-btn").style.display = "none";
            } else {
                console.log("assigned_agent_change_listener : ", response)
                show_desk_toast("Agent Not Assigned")
            }
        }
    }
    xhttp.send(params);
}

function fetch_and_update_user_notification_count(from_event=false){
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/fetch-user-notification-count/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let count = response.count;
                if (count > 0) {
                    let old_count = 0;
                    try{
                        old_count = parseInt(document.getElementById("total_notification_count").innerHTML);
                    }catch(err){
                        old_count = 0;
                    }
                    if(from_event && old_count < count && window.location.pathname.indexOf("/tms/notifications") == 0){
                        document.querySelector(".tms-new-notification").style.display = "";
                    }
                    document.getElementById("total_notification_count").innerHTML = count;
                    document.getElementById("total_notification_count").parentElement.style.display = '';
                    document.querySelector("#cogno_desk_title").innerHTML = response.cognodesk_title + " (" + count + ")";
                } else {
                    document.getElementById("total_notification_count").innerHTML = 0;
                    document.getElementById("total_notification_count").parentElement.style.display = "none";
                    document.querySelector("#cogno_desk_title").innerHTML = response.cognodesk_title;
                }
            }
        }
    }
    xhttp.send('{}');
}

fetch_and_update_user_notification_count(false);

/************************************************************ DASHBOARD SETTINGS ENDS ************************************************************/

/************************************************************ ACCESS MANAGEMENT STARTS ************************************************************/

function add_new_agent(element) {

    var error_message_element = document.getElementById("add-new-agent-error");
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("inline-form-input-agent-name").value.trim();
    full_name = stripHTML(full_name);
    full_name = remove_special_characters_from_str(full_name);

    var email = document.getElementById("inline-form-input-agent-email").value.trim();
    email = stripHTML(email);
    // email = remove_special_characters_from_str(email);

    var mobile = document.getElementById("inline-form-input-agent-mobile").value.trim();
    mobile = stripHTML(mobile);
    mobile = remove_special_characters_from_str(mobile);

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;
    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

    var platform_url = window.location.protocol + '//' + window.location.host;

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
    }

    if (mobile != null && mobile != "" && !regMob.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    var user_type = document.getElementById("inline-form-input-user-type");
    if (user_type != null && user_type != undefined) {
        if (user_type.value == "None") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please select valid user type";
            return;
        } else {
            user_type = user_type.value;
        }
    } else {
        user_type = "agent";
    }

    var selected_supervisor_pk_list = [];
    if (user_type == "agent")
        selected_supervisor_pk_list = $("#inline-form-input-supervisor-pk").val();
    if (selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];

    var selected_bot_pk_list = $("#tms-bot-select-element").val();

    if (selected_bot_pk_list == undefined || selected_bot_pk_list == null) {

        selected_bot_pk_list = [];
    }

    var selected_ticket_category_pk_list = $("#tms-ticket-category-select").val();

    if (selected_ticket_category_pk_list == undefined || selected_ticket_category_pk_list == null) {

        selected_ticket_category_pk_list = [];
    }

    var request_params = {
        "agent_name": full_name,
        "agent_email": email,
        "agent_mobile": mobile,
        "user_type": user_type,
        "platform_url": platform_url,
        "selected_supervisor_pk_list": selected_supervisor_pk_list,
        "selected_bot_pk_list": selected_bot_pk_list,
        "selected_ticket_category_pk_list": selected_ticket_category_pk_list,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/add-new-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                if (user_type == "agent") {
                    error_message_element.innerHTML = "Agent matching details already exists.";
                } else {
                    error_message_element.innerHTML = "Supervisor matching details already exists.";
                }
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function update_agent_details(element, pk) {

    var error_message_element = document.getElementById("save-agent-details-error-" + pk);
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("inline-form-input-agent-name-" + pk).value.trim();
    full_name = stripHTML(full_name);
    full_name = remove_special_characters_from_str(full_name);

    var email = document.getElementById("inline-form-input-agent-email-" + pk).value.trim();
    email = stripHTML(email);
    // email = remove_special_characters_from_str(email);

    var mobile = document.getElementById("inline-form-input-agent-mobile-" + pk).value.trim();
    mobile = stripHTML(mobile);
    mobile = remove_special_characters_from_str(mobile);

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;
    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

    var platform_url = window.location.protocol + '//' + window.location.host;

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name (only A-Z, a-z and space is allowed)";
        return;
    }

    if (!regEmail.test(email)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid email id.";
        return;
    }

    if (mobile != null && mobile != "" && !regMob.test(mobile)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    var user_type = document.getElementById("inline-form-input-user-type-" + pk);
    if (user_type != null && user_type != undefined) {
        if (user_type.value == "None") {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please select valid user type";
            return;
        } else {
            user_type = user_type.value;
        }
    } else {
        user_type = "agent";
    }

    var selected_supervisor_pk_list = [];
    if (user_type == "agent")
        selected_supervisor_pk_list = $("#inline-form-input-supervisor-pk-" + pk).val();
    if (selected_supervisor_pk_list.length == 0)
        selected_supervisor_pk_list = [-1];

    var selected_bot_pk_list = $("#tms-bot-select-element-" + pk).val();

    if (selected_bot_pk_list == undefined || selected_bot_pk_list == null) {

        selected_bot_pk_list = [];
    }

    var selected_ticket_category_pk_list = $("#tms-ticket-category-select-" + pk).val();

    if (selected_ticket_category_pk_list == undefined || selected_ticket_category_pk_list == null) {

        selected_ticket_category_pk_list = [];
    }

    var request_params = {
        "pk": pk,
        "agent_name": full_name,
        "agent_email": email,
        "agent_mobile": mobile,
        "user_type": user_type,
        "platform_url": platform_url,
        "selected_supervisor_pk_list": selected_supervisor_pk_list,
        "selected_bot_pk_list": selected_bot_pk_list,
        "selected_ticket_category_pk_list": selected_ticket_category_pk_list,
    };
    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/update-agent-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function(e) {
                    window.location.reload();
                }, 500);
            } else if (response.status == 301) {
                error_message_element.style.color = "orange";
                error_message_element.innerHTML = "Agent matching details already exists.";
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function delete_cobrowsing_agent(agent_pk) {

    var request_params = {
        "agent_pk": agent_pk,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/delete-tms-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location.reload();
            } else if (response.status == 300) {
                show_desk_toast("Unable to delete Agent. Agent does not exist.");
            } else {
                show_desk_toast("Unable to delete Agent. Please try again.");
            }
            $('#remove-agent-modal').modal('hide');
        }
    }
    xhttp.send(params);
}

$(document).on("change", ".user-checkbox-collection", function(e) {
    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    document.getElementById("button-deactivate-account").style.display = "none";
    document.getElementById("button-activate-account").style.display = "none";
    document.getElementById("button-present-account").style.display = "none";
    document.getElementById("button-absent-account").style.display = "none";

    var total_active_account = 0;
    var total_inactive_account = 0;
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked == false) {
            continue;
        }
        if (user_checkbox_collection[index].nextElementSibling.value == "True") {
            total_active_account = 1;
        } else {
            total_inactive_account = 1;
        }
        if (total_inactive_account && total_active_account) {
            break;
        }
    }

    if (total_inactive_account > 0) {
        document.getElementById("button-activate-account").style.display = "block";
    }
    if (total_active_account > 0) {
        document.getElementById("button-deactivate-account").style.display = "block";
    }

    var total_present_account = 0;
    var total_absent_account = 0;
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked == false) {
            continue;
        }
        if (user_checkbox_collection[index].nextElementSibling.nextElementSibling.value == "False") {
            total_present_account = 1;
        } else {
            total_absent_account = 1;
        }
        if (total_absent_account && total_present_account) {
            break;
        }
    }

    if (total_absent_account > 0) {
        document.getElementById("button-present-account").style.display = "block";
    }
    if (total_present_account > 0) {
        document.getElementById("button-absent-account").style.display = "block";
    }
});

function deactivate_user(element) {
    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    var agent_id_list = [];
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    var request_params = {
        "agent_id_list": agent_id_list,
        "activate": false
    };
    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/change-agent-activate-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 301) {
                show_desk_toast(response.message);
                return;
            }
            if (response.status != 200) {
                show_desk_toast("Unable to change agent activate status");
            }
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function activate_user(element) {

    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");

    var agent_id_list = [];

    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    var request_params = {
        "agent_id_list": agent_id_list,
        "activate": true
    };
    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/change-agent-activate-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status != 200) {
                show_desk_toast("Unable to change agent activate status");
            }
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function change_agent_absent_status(element, is_absent) {
    var user_checkbox_collection = document.getElementsByClassName("user-checkbox-collection");
    var agent_id_list = [];
    for (let index = 0; index < user_checkbox_collection.length; index++) {
        if (user_checkbox_collection[index].checked) {
            agent_id_list.push(user_checkbox_collection[index].id.split("-")[2]);
        }
    }

    if (agent_id_list.length == 0) {
        return;
    }

    if(is_absent == "true") is_absent = true;
    else is_absent = false;

    var request_params = {
        "agent_id_list": agent_id_list,
        "is_absent": is_absent
    };
    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/change-agent-absent-status/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 301) {
                show_desk_toast(response.message);
                return;
            }
            if (response.status != 200) {
                show_desk_toast("Unable to change agent absent status");
            }
            window.location.reload();
        }
    }
    xhttp.send(params);
}

function resend_password(pk) {

    var platform_url = window.location.protocol + '//' + window.location.host;

    var request_params = {
        "user_pk": pk,
        "platform_url": platform_url
    };
    var json_params = JSON.stringify(request_params);

    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/resend-account-password/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_desk_toast(response.message);
            } else {
                show_desk_toast("Could not send the password. Please try again.");
            }
        }
    }
    xhttp.send(params);
}

function get_url_vars() {
    var vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        vars[key] = value;
    });
    return vars;
}

function show_agent_details(status) {
    var request_params = get_url_vars();
    var updated_request_params = "";
    if ("pk" in request_params) {
        updated_request_params += "pk=" + request_params["pk"];
    }

    if (updated_request_params.length > 0) {
        updated_request_params += "&";
    }

    updated_request_params += filter_agent_status(status);

    if (updated_request_params.length > 0)
        window.location.href = window.location.pathname + "?" + updated_request_params;
    else
        window.location.href = window.location.pathname;
}

function filter_agent_status(status) {
    if (status == "online") {
        return "is_active=" + true;
    } else if (status == "offline") {
        return "is_active=" + false;
    } else if (status == "active") {
        return "is_account_active=" + true;
    } else if (status == "inactive") {
        return "is_account_active=" + false;
    } else if (status == "present") {
        return "is_absent=" + false;
    } else if (status == "absent") {
        return "is_absent=" + true;
    } else {
        return "";
    }
}

/************************************************************ ACCESS MANAGEMENT ENDS ************************************************************/


function save_admin_details(element) {
    var error_message_element = document.getElementById("save-details-error");
    error_message_element.innerHTML = "";

    var full_name = document.getElementById("admin-name").value;
    var old_password = document.getElementById("old-password").value;
    var new_password = document.getElementById("new-password").value;
    var confirm_password = document.getElementById("confirm-password").value;

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regPass = /^(((?=.*[a-z])(?=.*[A-Z]))|((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{8,})(?!.*[\s])/;

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name";
        return;
    }

    if (full_name.length > 30) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Maximum 30 characters are allowd in Full name";
        return;
    }

    if (old_password != "" || new_password != "") {
        if (!regPass.test(new_password)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Minimum length of password is 8 and must have at least one lowercase and one uppercase alphabetical character or has at least one lowercase and one numeric character or has at least one uppercase and one numeric character.";
            return;
        }
    }

    if(new_password != confirm_password) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "New Password and Confirm Password does not match.";
        return;
    }

    var request_params = {
        "agent_name": full_name,
        "old_password": old_password,
        "new_password": new_password
    };

    var json_params = JSON.stringify(request_params);

    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/agent/save-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                if (response.is_password_changed) {
                    error_message_element.innerHTML = "Password has been reset successfully. Please login again.";
                } else {
                    error_message_element.innerHTML = "Saved successfully.";
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else if (response.status == 101) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Your old password is incorrect. Kindly enter valid password.";
            } else if (response.status == 102) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Your new password is similar to your old password please use another strong password.";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}

function save_agent_details(element) {
    var error_message_element = document.getElementById("save-details-error");
    error_message_element.innerHTML = "";
    var full_name = document.getElementById("agent-name").value;
    var mobile_number = document.getElementById("agent-mobile-number").value;
    var old_password = document.getElementById("old-password").value;
    var new_password = document.getElementById("new-password").value;
    var agent_email = document.getElementById("agent-email").value;
    var confirm_password = document.getElementById("confirm-password").value;

    const regName = /^[^\s][a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}[0-9]{9}$/;
    const regPass = /^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[0-9])(?=.*[a-z]).{8,}/;

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name";
        return;
    }

    if (!regMob.test(mobile_number)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    if (old_password != "" || new_password != "") {
        if (!regPass.test(new_password)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Minimum length of password is 8 and must have at least one lower case alphabet, one upper case alphabet, one digit and one special character (a-z, A-Z, 0-9, Special characters)";
            return;
        }
        let agent_name = agent_email.split('@')[0];
        if (new_password.indexOf(agent_name) >= 0) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Your new password is too similar to your username please use strong password.";
            return
        }
    }

    if(new_password != confirm_password) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "New Password and Confirm Password does not match.";
        return;
    }

    var request_params = {
        "agent_name": full_name,
        "agent_mobile_number": mobile_number,
        "old_password": old_password,
        "new_password": new_password,
    };

    var json_params = JSON.stringify(request_params);

    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/agent/save-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.color = "green";
                if (response.is_password_changed) {
                    error_message_element.innerHTML = "Password has been reset successfully. Please login again.";
                } else {
                    error_message_element.innerHTML = "Saved successfully.";
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else if (response.status == 101) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Your old password is incorrect. Kindly enter valid password.";
            } else if (response.status == 102) {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Your new password is similar to your old password please use another strong password.";
            }
        }
        element.innerHTML = "Save";
    }
    xhttp.send(params);
}


function save_tms_meta_details_general(element, reset) {

    var error_message_element = document.getElementById("save-tms-meta-details-error");
    error_message_element.innerHTML = "";

    var request_params = {};

    if (reset == "false") {

        var tms_console_theme_color_el = document.getElementById("tms-console-theme-color");
        var console_theme_color = null;
        if (tms_console_theme_color_el.jscolor.toHEXString() != '#FFFFFF') {
            console_theme_color = {
                "red": tms_console_theme_color_el.jscolor.rgb[0],
                "green": tms_console_theme_color_el.jscolor.rgb[1],
                "blue": tms_console_theme_color_el.jscolor.rgb[2],
                "rgb": tms_console_theme_color_el.jscolor.toRGBString(),
                "hex": tms_console_theme_color_el.jscolor.toHEXString(),
            };
        }

        request_params = {
            "reset": "false",
            "tms_console_theme_color": console_theme_color,
        };
    } else {
        request_params = {
            "reset": "true",
        };
    }

    var json_params = JSON.stringify(request_params);
    var encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/agent/save-tms-meta-details/general/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                error_message_element.style.display = "block"
                error_message_element.style.color = "green";
                error_message_element.innerHTML = "Saved successfully.";
                setTimeout(function() {
                    error_message_element.style.display = "none"
                    window.location.href = window.location.href.replace( /[\?#].*|$/, "#pills-options-tab" );
                    window.location.reload();
                }, 1000);
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save the details";
            }
        }

        if (reset == "false") {
            element.innerHTML = "Save";
        } else {
            element.innerHTML = "Reset All";
        }
    }
    xhttp.send(params);
}

function delete_tms_logo() {
    var encrypted_data = "";
    var params = JSON.stringify(encrypted_data);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/delete-tms-logo/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                document.getElementById('tms-logo-image-data').innerHTML = 
                '<button data-toggle="modal" type="button" data-target="#tms_logo_upload_modal"\
                id="tms_logo_upload_button">Upload Logo</button>';
                document.getElementById("modal_tms_image_buttons").innerHTML = 
                    '<button class="btn btn-text-only" type="button" data-dismiss="modal"\
                    id="tms_logo_upload_modal_close">Cancel</button>\
                    <button class="btn btn-primary" onclick="upload_tms_logo(this)">Upload</button>';

                document.getElementById("cognoDeskLarge").src = window.location.origin + response.tms_default_logo[0];
                document.getElementById("cognoDeskSmall").src = window.location.origin + response.tms_default_logo[1];
                $('#tms_logo_upload_modal').modal('hide');
            } else {
                show_desk_toast("Something went wrong");
            }
        }
    }
    xhttp.send(params);
}

function upload_tms_logo(el) {
    var file = tms_logo_input_file_global;

    if (file == undefined || file == null) {
        show_desk_toast("Please choose a file.");
        return;
    }

    var malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_desk_toast(malicious_file_report.message)
        return false
    }

    if (check_image_file(file.name) == false) {
        return false;
    }

    if (file.size / 1000000 > 5) {
        show_desk_toast("File size cannot exceed 5 MB");
        $("#tms_logo_input")[0].value = "";
        return;
    }

    el.innerText = "Uploading..."
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        var base64_str = reader.result.split(",")[1];

        var json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        var encrypted_data = tms_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        var params = JSON.stringify(encrypted_data);

        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/upload-tms-logo/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                console.log()
                if(response["status"] == 200) {
                    document.getElementById('tms-logo-image-data').innerHTML =
                    '<div class="row">\
                        <div class="col-md-6 col-sm-12" style="padding-left: 0.7em;display: flex;align-items: center;">\
                            <button class="mb-2 mr-sm-2" data-toggle="modal" type="button"\
                            data-target="#tms_logo_upload_modal" id="tms_logo_upload_button">Change Logo\
                            </button>\
                        </div>\
                        <div class="col-md-6 col-sm-12">\
                            <img src="/'+ response.file_path +'" id="tms-logo-image"\
                            style="height: 9em; display: inline-box; width: 100%;">\
                        </div>\
                    </div>'

                    document.getElementById("tms_image_file_upload_bar").style.display = "none";
                    document.getElementById("modal_tms_image_buttons").innerHTML = 
                        '<button class="btn btn-outline-primary mr-auto" onclick="delete_tms_logo()"\
                        style="margin-right: auto !important;">Delete</button>\
                        <button class="btn btn-text-only" type="button" data-dismiss="modal"\
                        id="tms_logo_upload_modal_close">Cancel</button>\
                        <button class="btn btn-primary" onclick="upload_tms_logo(this)">Upload</button>';

                    document.getElementById("cognoDeskLarge").src = window.location.origin + '/' + response.file_path;
                    document.getElementById("cognoDeskSmall").src = window.location.origin + '/' + response.file_path;
                    document.getElementById("tms_logo_upload_modal_close").click();
                    el.innerText = "Change Logo";
                } else {
                    document.getElementById("tms_logo_upload_modal_close").click();
                    el.innerText = "Upload Logo";
                    show_desk_toast("Invalid file format");
                }
            }
        }
        xhttp.send(params);
    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };
}

function check_malicious_file(file_name) {
    var response = {
        'status': false,
        'message': 'OK'
    }
    if (file_name.split('.').length != 2) {
        response.status = true;
        response.message = 'Please do not use .(dot) except for extension';
        return response;
    }

    var allowed_files_list = [
        "png", "jpg", "jpeg", "bmp", "gif", "tiff", "exif", "jfif", "webm", "mpg",
        "mp2", "mpeg", "mpe", "mpv", "ogg", "mp4", "m4p", "m4v", "avi", "wmv", "mov", "qt", "doc", "docx",
        "flv", "swf", "avchd", "mp3", "aac", "pdf", "xls", "xlsx", "json", "xlsm", "xlt", "xltm", "zip"
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

function check_image_file(file_name) {
    var allowed_files_list = [
        "png", "jpg", "jpeg", "svg", "bmp", "gif", "tiff", "exif", "jfif"
    ];

    var file_extension = file_name.substring(file_name.lastIndexOf(".") + 1, file_name.length);
    file_extension = file_extension.toLowerCase();

    if (allowed_files_list.includes(file_extension) == false) {
        show_desk_toast("." + file_extension + " files are not allowed");
        return false;
    }
    return true;
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

        document.addEventListener("mouseleave", function(e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.drag_container = document;

        _this.drag_container.addEventListener("mousemove", function(e) {
            _this.drag_element('move', e);
        });

        _this.drag_container.addEventListener("mouseup", function(e) {
            _this.drag_element('up', e);
        });

        _this.initialize();
    }
    initialize(){
        var _this = this;
        var elements = _this.container.querySelectorAll(".drag-handle");
        if(elements.length == 0){
            elements = _this.container.children;
        }
        for(let index=0; index<elements.length; index++){
            var element = elements[index];
            var target_element = _this.get_target_element(element);

            element.addEventListener("mousedown", function(e) {
                _this.drag_element('down', e);
            });

            element.addEventListener("mouseup", function(e) {
                _this.drag_element('up', e);
            });

            target_element.addEventListener("touchstart", function(e) {
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('down', e);
            });

            target_element.addEventListener("touchmove", function(e) {
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

            target_element.addEventListener("touchend", function(e) {
                _this.prevX = 0;
                _this.prevY = 0;
                _this.drag_element('out', e);
            });

            element.style.cursor = "move";
        }
    }
    get_target_element(element){
        var _this = this;
        var handle = element;
        while(handle.parentElement != _this.container)
            handle = handle.parentElement;
        return handle;
    }
    drag_element(direction, e) {
        var _this = this;
        if (direction == 'down') {
            _this.is_dragging = true;
            _this.element = _this.get_target_element(e.target);
            if(!_this.dummy_element){
                _this.dummy_element = document.createElement("span");
                _this.dummy_element.className = "cognoai-drag-dummy-element";
            }
        }

        if (direction == 'up' || direction == "out") {
            if(_this.is_dragging == false) {
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
            if(_this.dummy_element.parentElement){
                _this.dummy_element.parentElement.removeChild(_this.dummy_element);
            }
            _this.dummy_element = null;

            if(_this.drag_finish_callback){
                try{
                    _this.drag_finish_callback()
                }catch(err){}
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

    compute(){
        var _this = this;

        _this.element.hidden = true;
        let elemBelow = document.elementFromPoint(_this.clientX, _this.clientY);
        _this.element.hidden = false;

        try{
            var target_element = _this.get_target_element(elemBelow);
            if(target_element){

                var pWidth = $(target_element).innerWidth(); //use .outerWidth() if you want borders
                var pOffset = $(target_element).offset(); 
                var x = _this.pageX - pOffset.left;
                if(pWidth/2 > x){
                    target_element.insertAdjacentElement("beforebegin", _this.dummy_element);
                } else {
                    target_element.insertAdjacentElement("afterend", _this.dummy_element);
                }
            }
        } catch(err){}
    }
}

function download_user_details_excel_template(element) {
    let params = "";

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/download-user-details-excel-template/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_desk_toast("Unable to download template");
            }
        }
    }
    xhttp.send(params);
}

function upload_user_excel_details(element) {
    let file = user_details_upload_input_file_global;
    let error_element = document.getElementById("user_details_upload_input_error");

    try {
        error_element.nextElementSibling.remove();
    } catch (err) {}

    if (file == undefined || file == null) {
        error_element.style.color = "red";
        error_element.innerHTML = "Please choose a file of excel format.";
        return;
    }

    let malicious_file_report = check_malicious_file(file.name)
    if (malicious_file_report.status == true) {
        show_desk_toast(malicious_file_report.message)
        return false
    }

    let filename = file.name;
    let fileExtension = "";
    if (filename.lastIndexOf(".") > 0) {
        fileExtension = filename.substring(filename.lastIndexOf(".") + 1, filename.length);
    }
    fileExtension = fileExtension.toLowerCase();
    let excel_extensions = ["xls", "xlsx", "xlsm", "xlt", "xltm"];
    if (!excel_extensions.includes(fileExtension)) {
        error_element.style.color = "red";
        error_element.innerHTML = "Please choose a file of excel format.";
        return;
    }

    element.innerText = "Uploading...";
    let reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function() {

        let base64_str = reader.result.split(",")[1];

        let json_string = {
            "filename": file.name,
            "base64_file": base64_str,
        };

        json_string = JSON.stringify(json_string);

        let encrypted_data = tms_custom_encrypt(json_string);

        encrypted_data = {
            "Request": encrypted_data
        };

        let params = JSON.stringify(encrypted_data);

        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/upload-user-details/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = tms_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response.status == 200) {
                    error_element.style.color = "green";
                    error_element.innerHTML = "Uploaded successfully.";
                    setTimeout(function() {
                        window.location.reload();
                    }, 1000);
                } else if (response["status"] == 300) {
                    error_element.style.color = "red";
                    error_element.innerHTML = "File format not supported. Please don't use .(dot) in filename except for extension."
                } else if (response["status"] == 301) {
                    error_element.style.color = "red";
                    error_element.innerHTML = "File is empty. Please add agent details to create agents."
                } else if (response["status"] == 302) {
                    error_element.style.color = "red";
                    error_element.innerHTML = "Some entries are incorrect. Please check the below given excel link for more information."
                    let html_error_file = [
                        '<a href="/' + response["file_path"] + '">',
                        '<svg width="19" height="17" viewBox="0 0 19 17" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M11.4584 0H5.38271C4.94133 0 4.58337 0.357958 4.58337 0.799333V4.12637H11.4584V0Z" fill="#169154"/>',
                        '<path d="M4.58337 12.3997V15.7006C4.58337 16.142 4.94133 16.5 5.38225 16.5H11.4584V12.3997H4.58337Z" fill="#18482A"/>',
                        '<path d="M4.58337 4.12637H11.4584V8.25229H4.58337V4.12637Z" fill="#0C8045"/>',
                        '<path d="M4.58337 8.25236H11.4584V12.4003H4.58337V8.25236Z" fill="#17472A"/>',
                        '<path d="M17.534 0H11.4584V4.12637H18.3334V0.799333C18.3334 0.357958 17.9754 0 17.534 0Z" fill="#29C27F"/>',
                        '<path d="M11.4584 12.3997V16.5H17.5345C17.9754 16.5 18.3334 16.142 18.3334 15.7011V12.4002H11.4584V12.3997Z" fill="#27663F"/>',
                        '<path d="M11.4584 4.12637H18.3334V8.25229H11.4584V4.12637Z" fill="#19AC65"/>',
                        '<path d="M11.4584 8.25236H18.3334V12.4003H11.4584V8.25236Z" fill="#129652"/>',
                        '<path d="M8.39621 12.8334H0.770458C0.345125 12.8334 0 12.4883 0 12.063V4.4372C0 4.01187 0.345125 3.66674 0.770458 3.66674H8.39621C8.82154 3.66674 9.16667 4.01187 9.16667 4.4372V12.063C9.16667 12.4883 8.82154 12.8334 8.39621 12.8334Z" fill="#0C7238"/>',
                        '<path d="M2.66157 5.95826H3.75515L4.64248 7.67884L5.58023 5.95826H6.60186L5.19432 8.24992L6.63394 10.5416H5.5564L4.58932 8.74034L3.62636 10.5416H2.53278L3.99623 8.24167L2.66157 5.95826Z" fill="white"/>',
                        '</svg>',
                        '<span class="error-file-text"> Error File</span>',
                        '</a>',
                    ].join('');
                    error_element.insertAdjacentHTML("afterend", html_error_file)
                } else {
                    error_element.style.color = "red";
                    error_element.innerHTML = "Could not upload the excel document. Please try again.";
                }
            } else {
                error_element.style.color = "red";
                error_element.innerHTML = "Could not upload the excel document. Please try again.";
            }
            element.innerText = "Upload";
        }
        xhttp.send(params);

    };

    reader.onerror = function(error) {
        console.log('Error: ', error);
    };

}

function export_user_excel_details(element) {
    const params = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/export-user-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_desk_toast("Unable to download agent details");
            }
        }
    }
    xhttp.send(params);
}

function export_supervisor_excel_details(element) {
    const params = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/export-supervisor-details/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path"] != null) {
                export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else {
                show_desk_toast("Unable to download supervisor details");
            }
        }
    }
    xhttp.send(params);
}

function show_custom_date(el) {
    if (el.id === 'app_time_select_custom_date_btn') {
        document.getElementById('app-custom-date-select-area-flow').style.display = 'flex';
    } else {
        document.getElementById('app-custom-date-select-area-flow').style.display = 'none';
    }
}

function clear_filter() {
    document.getElementById('app_time_select_week').checked = true;
    document.getElementById('app_filter_custom_start_date').value = DEFAULT_START_DATE;
    document.getElementById('app_filter_custom_end_date').value = DEFAULT_END_DATE;
    document.getElementById('app-custom-date-select-area-flow').style.display = 'none';

    let filters = {}

    window.TMS_ACTIVE_TICKETS_TABLE.update_url_with_filters(filters);
    window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
}

function apply_tms_filter() {

    function get_bots(){
        let filtered_list = [];
        let bot_elems = document.getElementsByName('app-overview-filter-bot');
        for (let elem of bot_elems) {
            if (elem.checked){
                filtered_list.push(elem.value);
            }
        }
        return filtered_list;
    }

    function get_bot_channels(){
        let filtered_list = [];
        let channel_elems = document.getElementsByName('app-overview-filter-channel');
        for (let elem of channel_elems) {
            if (elem.checked){
                filtered_list.push(elem.value);
            }
        }
        return filtered_list;
    }

    function get_ticket_tickets(){
        let filtered_list = [];
        let status_elems = document.getElementsByName('app-overview-filter-status');
        for (let elem of status_elems) {
            if (elem.checked){
                filtered_list.push(elem.value);
            }
        }
        return filtered_list;
    }

    function get_ticket_category(){
        let filtered_list = [];
        let category_elems = document.getElementsByName('app-overview-filter-category');
        for (let elem of category_elems) {
            if (elem.checked){
                filtered_list.push(elem.value);
            }
        }
        return filtered_list;
    }

    function get_ticket_priority(){
        let filtered_list = [];
        let priority_elems = document.getElementsByName('app-overview-filter-priority');
        for (let elem of priority_elems) {
            if (elem.checked){
                filtered_list.push(elem.value);
            }
        }
        return filtered_list;
    }

    function get_agents(){
        let filtered_list = $("#selected-agent-filter").val();
        return filtered_list;
    }

    let selected_date_filter = $("input[type='radio'][name='app-overview-filter']:checked").val();
    let filters = get_url_multiple_vars();

    if (!selected_date_filter) {
        show_desk_toast('Please select date range');
        return;
    }

    let start_date, end_date;
    if (selected_date_filter === '5') {
        start_date = document.getElementById('app_filter_custom_start_date').value;

        if (!start_date) {
            show_desk_toast('Please select start date');
            return;
        }

        end_date = document.getElementById('app_filter_custom_end_date').value;

        if (!end_date) {
            show_desk_toast('Please select end date');
            return;
        }

        if(Date.parse(start_date) > Date.parse(end_date)){
            show_desk_toast('Start date cannot be less than end date.')
            return;
        }
        filters["start_date"] = [start_date];
        filters["end_date"] = [end_date];
    } else {
        filters["start_date"] = [];
        filters["end_date"] = [];
    }

    filters["selected_date_filter"] = [selected_date_filter]
    filters["ticket_status"] = get_ticket_tickets();
    filters["ticket_category"] = get_ticket_category();
    filters["ticket_priority"] = get_ticket_priority();
    filters["bots"] = get_bots();
    filters["bot_channels"] = get_bot_channels();
    filters["agent_id_list"] = get_agents();

    window.TMS_ACTIVE_TICKETS_TABLE.update_url_with_filters(filters);
    window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
}

function update_applied_filter() {

    function update_bot(){
        $("[name='app-overview-filter-bot']").prop("checked", false);
        if(filters.bots && filters.bots.length > 0) {
            let bot_elems = document.getElementsByName('app-overview-filter-bot');
            for (let elem of bot_elems) {
                elem.checked = false;
                if(filters.bots.indexOf(elem.value) >= 0){
                    elem.checked = true;
                }
            }
        }
    }

    function update_bot_channels(){
        $("[name='app-overview-filter-channel']").prop("checked", false);
        if(filters.bot_channels && filters.bot_channels.length > 0) {
            let bot_channel_elems = document.getElementsByName('app-overview-filter-channel');
            for (let elem of bot_channel_elems) {
                elem.checked = false;
                if(filters.bot_channels.indexOf(elem.value) >= 0){
                    elem.checked = true;
                }
            }
        }
    }

    function update_status(){
        $("[name='app-overview-filter-status']").prop("checked", false);
        if(filters.ticket_status && filters.ticket_status.length > 0) {
            let status_elems = document.getElementsByName('app-overview-filter-status');
            for (let elem of status_elems) {
                if(filters.ticket_status.indexOf(elem.value) >= 0){
                    elem.checked = true;
                }
            }
        }
    }

    function update_category(){
        $("[name='app-overview-filter-category']").prop("checked", false);
        if(filters.ticket_category && filters.ticket_category.length > 0) {
            let category_elems = document.getElementsByName('app-overview-filter-category');
            for (let elem of category_elems) {
                elem.checked = false;
                if(filters.ticket_category.indexOf(elem.value) >= 0){
                    elem.checked = true;
                }
            }
        }
    }

    function update_priority(){
        $("[name='app-overview-filter-priority']").prop("checked", false);
        if(filters.ticket_priority && filters.ticket_priority.length > 0) {
            let priority_elems = document.getElementsByName('app-overview-filter-priority');
            for (let elem of priority_elems) {
                elem.checked = false;
                if(filters.ticket_priority.indexOf(elem.value) >= 0){
                    elem.checked = true;
                }
            }
        }
    }

    function update_agent(){
        $("#selected-agent-filter").val([]).multiselect('refresh');
        if(filters.agent_id_list && filters.agent_id_list.length > 0) {
            $("#selected-agent-filter").val(filters.agent_id_list).multiselect('refresh');
        }
    }

    function update_date_range(){
        if("start_date" in filters){
            document.getElementById('app_filter_custom_start_date').value = filters["start_date"][0];
        }

        if("end_date" in filters){
            document.getElementById('app_filter_custom_end_date').value = filters["end_date"][0];
        }

        if("selected_date_filter" in filters){
            let selected_date_filter = filters["selected_date_filter"][0];

            document.getElementById('app_time_select_week').checked = false;
            document.getElementById('app_time_select_month').checked = false;
            document.getElementById('app_time_select_three_month').checked = false;
            document.getElementById('app_time_select_beg').checked = false;
            document.getElementById('app_time_select_custom_date_btn').checked = false;

            if(selected_date_filter === "5"){
                document.getElementById('app_time_select_custom_date_btn').checked = true;
                document.getElementById('app-custom-date-select-area-flow').style.display = 'flex';
            } else {
                if(selected_date_filter === "1") document.getElementById('app_time_select_week').checked = true;
                if(selected_date_filter === "2") document.getElementById('app_time_select_month').checked = true;
                if(selected_date_filter === "3") document.getElementById('app_time_select_three_month').checked = true;
                if(selected_date_filter === "4") document.getElementById('app_time_select_beg').checked = true;
                document.getElementById('app-custom-date-select-area-flow').style.display = 'none';
            }
        }
    }

    let filters = get_url_multiple_vars();
    update_date_range();
    update_bot();
    update_bot_channels();
    update_status();
    update_category();
    update_priority();
    update_agent();

    add_applied_filters_chips();
}

function revome_selected_filter_chip(el) {
    var selected_filter_parameters = $(el).closest('.filter-parameter-column')[0];
    var removed_value = $(el).closest('.filter-chip').find('span').html();
    var filter_key = selected_filter_parameters.getAttribute('filter-key');
    var filter_data = selected_filter_parameters.getAttribute('filter-data');
    filter_data = JSON.parse(filter_data);

    var new_filter_data = [];
    for (let idx = 0; idx < filter_data.length; idx++) {
        if (filter_data[idx] == removed_value) {
            continue;
        }
        new_filter_data.push(filter_data[idx]);
    }

    applied_filter_key_value_map[filter_key] = new_filter_data;

    if (filter_key == "title") {
        custom_title_filter_dropdown.update_value(new_filter_data);
    } else if (filter_key == "agent") {
        $("#selected-agent-filter").multiselect('deselect', removed_value);
    } else if (filter_key == "action") {
        custom_action_filter_dropdown.update_value(new_filter_data);
    }

    selected_filter_parameters.setAttribute('filter-data', JSON.stringify(new_filter_data));
    if (new_filter_data.length == 0) {
        $(selected_filter_parameters).find('.remove-filter-row-btn').click();
    } else {
        el.parentElement.remove();
    }
    var filter_chip_html = generate_filter_chips(filter_key, new_filter_data, true);
    selected_filter_parameters.getElementsByClassName('filter-chip-column')[0].innerHTML = filter_chip_html;
}

function add_applied_filters_chips() {

    function get_filter_key_display_name(filter_key){
        let display_name = filter_key;
        if(filter_key == "startdate") {
            display_name = "Start Date";
        } else if (filter_key == "enddate") {
            display_name = "End Date";
        } else if (filter_key == "bots") {
            display_name = "Bots";
        } else if (filter_key == "bot_channels") {
            display_name = "Bot Channel";
        } else if (filter_key == "ticket_status") {
            display_name = "Ticket Status";
        } else if (filter_key == "ticket_category") {
            display_name = "Ticket Category";
        } else if (filter_key == "ticket_priority") {
            display_name = "Ticket Priority";
        } else if (filter_key == "agent_id_list") {
            display_name = "Agents";
        } else if (filter_key == "selected_date_filter") {
            display_name = "Date Range";
        }
        return display_name;
    }

    let url_params = get_url_multiple_vars();
    let params_keys = Object.keys(url_params);
    let is_filter_applied = false;
    let filter_html = "";

    for (let idx = 0; idx < params_keys.length; idx++) {
        let filter_key = params_keys[idx];

        if (["page"].indexOf(filter_key) >= 0) {
            continue;
        }

        let display_name = get_filter_key_display_name(filter_key);

        is_filter_applied = true;

        let filter_values = url_params[filter_key];

        let html_filter_chip = "";

        for (let index = 0; index < filter_values.length; index++) {
            var value_display_name = decodeURI(filter_values[index]);

            var input_element = document.querySelector("#tms_custom_filter_modal [filter_key='" + filter_key + "'][value='" + decodeURI(filter_values[index]) + "']")

            if(input_element){
                value_display_name = input_element.getAttribute("display_name");
            }

            html_filter_chip += [
                ' <div class="filter-chip">',
                    '<span>' + value_display_name + '</span>',
                    '<button class="filter-chip-remove-icon" onclick=\'remove_applied_filter_by_value(\"' + decodeURI(filter_values[index]) + '\", \"' + filter_key + '\");\'>',
                        '<svg width="9" height="9" viewBox="0 0 9 9" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<path d="M5.38146 4.50006L8.06896 1.8188C8.18665 1.70112 8.25276 1.54149 8.25276 1.37505C8.25276 1.20862 8.18665 1.04899 8.06896 0.931305C7.95127 0.813615 7.79165 0.747498 7.62521 0.747498C7.45877 0.747498 7.29915 0.813615 7.18146 0.931305L4.50021 3.61881L1.81896 0.931305C1.70127 0.813615 1.54164 0.747498 1.37521 0.747498C1.20877 0.747498 1.04915 0.813615 0.931456 0.931305C0.813766 1.04899 0.747649 1.20862 0.747649 1.37505C0.747649 1.54149 0.813766 1.70112 0.931456 1.8188L3.61896 4.50006L0.931456 7.18131C0.872876 7.23941 0.826379 7.30853 0.794649 7.38469C0.762919 7.46086 0.746582 7.54255 0.746582 7.62506C0.746582 7.70756 0.762919 7.78925 0.794649 7.86542C0.826379 7.94158 0.872876 8.0107 0.931456 8.0688C0.989558 8.12739 1.05868 8.17388 1.13485 8.20561C1.21101 8.23734 1.2927 8.25368 1.37521 8.25368C1.45771 8.25368 1.5394 8.23734 1.61557 8.20561C1.69173 8.17388 1.76085 8.12739 1.81896 8.0688L4.50021 5.38131L7.18146 8.0688C7.23956 8.12739 7.30868 8.17388 7.38485 8.20561C7.46101 8.23734 7.5427 8.25368 7.62521 8.25368C7.70771 8.25368 7.78941 8.23734 7.86557 8.20561C7.94173 8.17388 8.01085 8.12739 8.06896 8.0688C8.12754 8.0107 8.17403 7.94158 8.20576 7.86542C8.23749 7.78925 8.25383 7.70756 8.25383 7.62506C8.25383 7.54255 8.23749 7.46086 8.20576 7.38469C8.17403 7.30853 8.12754 7.23941 8.06896 7.18131L5.38146 4.50006Z" fill="#0254D7"/>',
                        '</svg>',
                    '</button>',
                '</div>',
            ].join('');
        }

        filter_html += [
            '<div class="col-md-12 col-sm-12 filter-result-item">',
                '<div class="filter-name-text">',
                    '<span>' + display_name + '</span>',
                    '<button class="filter-remove-icon filter-show-on-mobile" onclick=\'remove_applied_filter(\"' + filter_key + '\");\'>',
                        '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                            '<path d="M1.5 1.5L10.5 10.5M1.5 10.5L10.5 1.5L1.5 10.5Z" stroke="#DC0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>',
                        '</svg>',
                    '</button>',
                '</div>',
                '<div class="chip-area">',
                    html_filter_chip,
                '</div>',
                '<button class="filter-remove-icon filter-hide-on-mobile" style="background: transparent !important;" onclick=\'remove_applied_filter("' + filter_key + '");\'>',
                    '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                        '<path d="M1.5 1.5L10.5 10.5M1.5 10.5L10.5 1.5L1.5 10.5Z" stroke="#DC0000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>',
                    '</svg>',
                '</button>',
            '</div>',
        ].join('');
    }

    filter_html += [
        '<div class="col-md-12 col-sm-12 mb-2 filter-padding-0" style="text-align: right;">',
        '<button class="clear-all-filter-btn" type="button" onclick="clear_filter()">Clear All</button>',
        '</div>',
    ].join('');

    if (is_filter_applied) {
        document.getElementById("applied-filter-result-container").innerHTML = filter_html;
        document.getElementById("applied-filter-div").style.display = 'flex';
    } else {
        document.getElementById("applied-filter-div").style.display = 'none';
    }
}

function remove_applied_filter(filter_key) {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);

    for (let idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == filter_key) {
            url_params[params_keys[idx]] = [];
            continue;
        }
    }

    window.TMS_ACTIVE_TICKETS_TABLE.update_url_with_filters(url_params);
    window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
}

function remove_applied_filter_by_value(target_filter_value, filter_key) {
    var url_params = get_url_multiple_vars();
    var params_keys = Object.keys(url_params);

    for (let idx = 0; idx < params_keys.length; idx++) {
        if (params_keys[idx] == filter_key) {
            var filter_values = url_params[params_keys[idx]];
            var new_filter_values = [];
            for (let index = 0; index < filter_values.length; index++) {
                var filter_value = decodeURI(filter_values[index]);
                if (filter_value == target_filter_value) {
                    continue;
                }
                new_filter_values.push(filter_value);
            }
            url_params[params_keys[idx]] = new_filter_values;
        }
    }

    window.TMS_ACTIVE_TICKETS_TABLE.update_url_with_filters(url_params);
    window.TMS_ACTIVE_TICKETS_TABLE.fetch_active_tickets();
}


/****************************** Developer Settings START ******************************/


function save_assign_task_process(el) {
    var process_id = document.getElementById("whatsapp-api-processor-id").value;
    var access_token_key = document.getElementById("admin_list_select").value;
    var processor_code = editor.getValue();

    if (!process_id || access_token_key == "none") {
        show_desk_toast("Please select an admin");
        return;
    }

    var json_string = JSON.stringify({
        "process_id": process_id,
        "access_token_key": access_token_key,
        "processor_code": processor_code,
    });

    var encrypted_data = tms_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    el.innerText = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/tms/save-whatsapp-api-processor-code/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                show_desk_toast("Successfully updated assign task process");
            } else if (response.status == 301) {
                show_desk_toast("Invalid assign task process");
            } else if (response.status == 401) {
                show_desk_toast("Assign task process does not belong to selected admin");
            } else {
                show_desk_toast("Something went wrong. Please try again.");
            }
            el.innerText = "Save";
        }
    }
    xhttp.send(params);
}

/****************************** Developer Settings END ******************************/
