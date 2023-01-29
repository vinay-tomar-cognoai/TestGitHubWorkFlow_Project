AUDIO = new Audio("");
check_and_update_audio_running_time_interval = null;
audio_player = null;
FILTER_DATE_TYPE = "4";
START_DATE = "";
END_DATE = "";
STATUS_FILTER = [];


$(document).ready(function() {
    document.getElementById('campaign-navbar-submenu-1').click();
    $(".play_now_btn").click(function(e) {
        e.stopPropagation();
        $(".voice-disposition-recording-wrapper").hide();
        $(this).siblings(".voice-disposition-recording-wrapper").toggle();
        // $(this).siblings(".voice-disposition-recording-wrapper").toggle('show');
    });

    $('.audio-player-cross-btn').click(function() {

        $(".voice-disposition-recording-wrapper").hide();

    });

    $(function() {
        $("#select-voice-campaign-dropdown").multiselect({
            nonSelectedText: 'Select Campaign',
            enableFiltering: true,
            enableCaseInsensitiveFiltering: true,
            selectAll: false,
            includeSelectAllOption: false,
           
            searchOptions: {
                'default': 'Search Here'
            },
        });
    });
    initialize_campaign_template_table();
});

function apply_voice_history_filter() {
    var filter_date_type = $("input[type='radio'][name='voice-history-date-filter']:checked").val();

    var start_date = "";
    var end_date = "";

    if (filter_date_type == "5") {
        start_date = document.getElementById("voice_history_filter_custom_start_date").value;
        if (!start_date) {
            show_campaign_toast("Please select valid start date.");
            return;
        }

         end_date = document.getElementById("voice_history_filter_custom_end_date").value;

        if (!end_date) {
            show_campaign_toast("Please select valid end date.");
            return;
        }

        var today = new Date();
        today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + "-" + String(today.getDate()).padStart(2, '0');

        if (start_date > today) {
            show_campaign_toast("Start date cannot be greater than today's date.");
            return;
        }

        if (end_date > today) {
            show_campaign_toast("End date cannot be greater than today's date.");
            return;
        }

        if (start_date > end_date) {
            show_campaign_toast('Start date cannot be greater than end date.');
            return;
        }
    }

    var status_checkboxes = document.querySelectorAll('[name="voice-history-filter-status"]');
    var status_filter = [];

    for (var i=0; i<status_checkboxes.length; i++) {
        if (status_checkboxes[i].checked) {
            status_filter.push(status_checkboxes[i].value);
        }
    }

    FILTER_DATE_TYPE = filter_date_type;
    START_DATE = start_date;
    END_DATE = end_date;
    STATUS_FILTER = status_filter;

    var filters = get_url_multiple_vars();
    filters["page"] = "1"
    window.VOICE_CAMPAIGN_DETAILS_TABLE.update_url_with_filters(filters);
    window.VOICE_CAMPAIGN_DETAILS_TABLE.get_voice_campaign_data();

    $("#campaign_custom_filter_modal").modal("hide");
}

function clear_voice_history_filter() {
    document.getElementById("campaign_overview_beg").checked = true;

    var status_checkboxes = document.querySelectorAll('[name="voice-history-filter-status"]')
    for (var i=0; i<status_checkboxes.length; i++) {
        status_checkboxes[i].checked = false;
    }

    FILTER_DATE_TYPE = "4";
    START_DATE = "";
    END_DATE = "";
    STATUS_FILTER = [];

    window.VOICE_CAMPAIGN_DETAILS_TABLE.get_voice_campaign_data();
}

function save_voice_campaign_history_request_data(email_id) {

    var url_params = get_url_multiple_vars();

    var options = document.getElementById("select-voice-campaign-dropdown").options;
    var campaign_ids = [];

    for (var i=0; i<options.length; i++) {
        if (options[i].selected) {
            campaign_ids.push(options[i].value);
        }
    }

    var request_params = {
        "bot_pk": url_params["bot_pk"][0],
        "campaign_ids": campaign_ids,
        "filter_date_type": FILTER_DATE_TYPE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "status_filter": STATUS_FILTER,
        "email_id": email_id
    }

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/save-export-voice-campaign-history-request/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            console.log(response);
            if (response["status"] == 200) {
                show_campaign_toast("You will receive the voice campaign history report data dump on the above email ID within 24 hours.")
                document.getElementById('filter-data-email-2').value = "";
                $("#campaign_multi_export_modal").modal("hide");
            } else {
                show_campaign_toast(response["message"])
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}


function get_time_code_from_num(num) {
    let seconds = parseInt(num);
    let minutes = parseInt(seconds / 60);
    seconds -= minutes * 60;
    const hours = parseInt(minutes / 60);
    minutes -= hours * 60;

    if (hours === 0) {
        return `${minutes}:${String(seconds % 60).padStart(2, 0)}`;
    }

    return `${String(hours).padStart(2, 0)}:${minutes}:${String(seconds % 60).padStart(2, 0)}`;

}

//toggle between playing and pausing on button click
function toggle_between_playing_and_pausing(play_btn, audio) {
    if (audio.paused) {
        play_btn.classList.remove("play");
        play_btn.classList.add("pause");
        audio.play();
    } else {
        play_btn.classList.remove("pause");
        play_btn.classList.add("play");
        audio.pause();
    }
}


function set_play_recoreder(voice_campaign_user_id) {
    audio_player = document.getElementById("audio-player-" + voice_campaign_user_id + "");
    AUDIO.setAttribute("src", document.getElementById("user_call_recording_download_src_" + voice_campaign_user_id).href);

    AUDIO.addEventListener("loadeddata", () => {
        audio_player.querySelector(".time .length").textContent = get_time_code_from_num(AUDIO.duration);
        AUDIO.volume = .75;
    },
        false
    );

    let timeline = audio_player.querySelector(".timeline");
    timeline.addEventListener("click", e => {
        let timelineWidth = window.getComputedStyle(timeline).width;
        let timeToSeek = e.offsetX / parseInt(timelineWidth) * AUDIO.duration;
        AUDIO.currentTime = timeToSeek;
    }, false);

    var play_button = audio_player.querySelector(".toggle-play");
    play_button.addEventListener("click", () => {
        toggle_between_playing_and_pausing(play_button, AUDIO);
    },
        false
    );

    clearInterval(check_and_update_audio_running_time_interval);
    check_and_update_audio_running_time_interval = setInterval(function () {
        let progressBar = audio_player.querySelector(".progress");
        progressBar.style.width = AUDIO.currentTime / AUDIO.duration * 100 + "%";
        audio_player.querySelector(".time .current").textContent = get_time_code_from_num(
            AUDIO.currentTime
        );
    }, 500);
}


function open_audio_player(voice_campaign_user_id) {
    
    if (document.getElementById("voice-disposition-recording-wrapper-" + voice_campaign_user_id).style.display == "block"){
        return;
    }
    var audio_players = document.getElementsByClassName("voice-disposition-recording-wrapper");
    for (var i=0; i<audio_players.length; i++){
        if (audio_players[i].style.display == "block") {
            close_audio_player(audio_players[i].id.split("-")[audio_players[i].id.split("-").length-1]);
        }
    }

    document.getElementById("voice-disposition-recording-wrapper-" + voice_campaign_user_id).style.display = "block";
    set_play_recoreder(voice_campaign_user_id);
}

function close_audio_player(voice_campaign_user_id) {
    var audio_player_div = document.getElementById("voice-disposition-recording-wrapper-" + voice_campaign_user_id);
    audio_player_div.style.display = "none";
    AUDIO.setAttribute("src", "");

    // Reset audio player modal while closing
    var play_button = audio_player_div.querySelector(".toggle-play");
    play_button.classList.remove("pause");
    play_button.classList.add("play");
    AUDIO.pause();
    audio_player_div.querySelector(".time .length").textContent = "0:00";
    audio_player_div.querySelector(".time .current").textContent = "0:00";
    audio_player_div.querySelector(".progress").style.width = "0%";

    play_button.replaceWith(play_button.cloneNode(true));

    var timeline = audio_player_div.querySelector(".timeline");
    timeline.replaceWith(timeline.cloneNode(true));

    clearInterval(check_and_update_audio_running_time_interval);
}

function search_campaigns() {
    var voice_history_datas = document.getElementsByClassName("voice-history-data");
    var search_value = document.getElementById("voice-history-search-bar").value.toLowerCase();

    for (var i=0; i<voice_history_datas.length; i++) {
        if (search_value == "" || voice_history_datas[i].getAttribute("search-value").includes(search_value)) {
            voice_history_datas[i].style.display = "table-row";
        } else {
            voice_history_datas[i].style.display = "none";
        }
    }
}

function update_voice_campaign_data() {
    var search_input = document.getElementById("voice-history-search-bar").value;

    if (search_input != "") {
        return;
    }

    var recording_players = document.getElementsByClassName("voice-disposition-recording-wrapper");
    for (var i=0; i<recording_players.length; i++) {
        if (recording_players[i].style.display == "block") {
            return;
        }
    }

    window.VOICE_CAMPAIGN_DETAILS_TABLE.get_voice_campaign_data();
}

window.onload = function() {
    if (window.location.href.includes("/campaign/voice-bot-campaign-details/")) {
        setInterval(update_voice_campaign_data, 30000);
    }
}


function export_voice_campaign_history_request(el) {

    var email_id = document.getElementById('filter-data-email-2').value;

    if (email_id == '') {
        document.getElementById('general-error-message-2').innerHTML = 'Please enter your Email ID';
        return;
    } else {
        document.getElementById('general-error-message-2').innerHTML = '';
    }

    if (!validate_email(email_id)) {
        document.getElementById('general-error-message-2').innerHTML = 'Please enter valid Email ID';
        return;
    } else {
        document.getElementById('general-error-message-2').innerHTML = '';
    }

    save_voice_campaign_history_request_data(email_id);

}

class VoiceDetailsTable extends CampaignBase {
    constructor(table_container, searchbar_element, pagination_container) {
        super();
        this.table_container = table_container;
        this.table = null;
        this.options = {
            enable_select_rows: false,
        }

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;
        this.searchbar_element = searchbar_element;

        this.data_checklist = {
            'campaign_data': false,
        };

        this.data_table_obj = null;

        this.init();
    }

    init() {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.get_voice_campaign_data();
        
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="voice_bot_campaign_details_table" width="100%" cellspacing="0"></table>';
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
    }

    initialize_head() {
        var _this = this;
        const { enable_select_rows } = false;
        var th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            var name = column_info_obj.name;
            var display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '">' + display_name + '</th>'
        });

        var select_rows_html = "";
        if (enable_select_rows) {
            select_rows_html = [
                '<th>',
                '</th>',
            ].join('');
        }

        var thead_html = [
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

        var campaign_data_list = this.get_rows();

        _this.data_table_obj = $(_this.table).DataTable({
            "data": campaign_data_list,
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
                // _this.show_filter_div();
                // _this.add_filter_event_listener();
            },
            createdRow: function (row, data, dataIndex) {
                row.setAttribute("batch_id", _this.campaign_data[dataIndex].batch_id);
            },
        });
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
        _this.get_voice_campaign_data();
    }

    lead_data_table_meta_div() {
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

    get_voice_campaign_data(){
        var _this = this;
        document.getElementById("voice-history-search-bar").value = "";
        var url_params = get_url_multiple_vars();
    
        var options = document.getElementById("select-voice-campaign-dropdown").options;
        var campaign_ids = [];
    
        for (var i=0; i<options.length; i++) {
            if (options[i].selected) {
                campaign_ids.push(options[i].value);
            }
        }
        let filters = get_url_multiple_vars();
        var request_params = {
            "bot_pk": url_params["bot_pk"][0],
            "campaign_ids": campaign_ids,
            "filter_date_type": FILTER_DATE_TYPE,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "status_filter": STATUS_FILTER,
            'page': ((filters["page"] && filters["page"][0]) || 1)
        }
    
        var json_params = JSON.stringify(request_params);
        var encrypted_data = campaign_custom_encrypt(json_params);
        encrypted_data = {
            "Request": encrypted_data
        };
        var params = JSON.stringify(encrypted_data);
    
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/campaign/get-voice-campaign-details/", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                response = campaign_custom_decrypt(response.Response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_campaign_data(response["data"])
                } else {
                    show_campaign_toast(response["message"])
                }
            } else if(this.readyState == 4 && this.status == 403){
                trigger_session_time_out_modal();
            }
        }
        xhttp.send(params);
    }

    set_campaign_data(campaign_data) {
        var _this = this;
        if (campaign_data) {
            _this.campaign_data = campaign_data;
            _this.data_checklist.campaign_data = true;
        }

        _this.check_and_initialize_table();
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

        var html = "";
        switch (name) {
            case "campaign_name":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "date_created":
                html = data;
                break;

            case "status":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "type":
                html = `<span class="text-capitalize">${data}</span>`;
                break;
    
            case "disposition_code":
                if (campaign_data_obj["disposition_intent"] && campaign_data_obj["disposition_tree"]) {
                    html = `<a target="_blank" href="/chat/edit-tree/?intent_pk=` + campaign_data_obj["disposition_intent"] + `&parent_pk=` + campaign_data_obj["disposition_parent_tree"] + `&tree_pk=` + campaign_data_obj["disposition_tree"] + `&selected_language=en">` + data + `</a>`;
                } else {
                    html = `<span class="text-capitalize">${data}</span>`;
                }
                break;
            
            case "duration":
                html = `<span class="text-capitalize">${data}</span>`;
                break;

            case "transcript":
                if (data != "N/A") {
                    html = `<a target="_blank" class="click_here_btn" href="/chat/user-filtered/?bot_id=` + get_url_multiple_vars()["bot_pk"][0] + `&user_id=` + data + `">Click here</a>`
                } else {
                    html = data;
                }
                break;

            case "phone_number":
                html = `<span class="text-capitalize">${data}</span>`;
                break;               

            case "recording":
                if (data == "N/A") {
                    html = data;
                    break;
                } else {
                    html = `<div style="position: absolute;"><a class="play_now_btn" onclick=open_audio_player("` + campaign_data_obj["voice_campaign_user_id"] + `")><div>Play Now</div></a>
                    <div class="voice-disposition-recording-wrapper" id="voice-disposition-recording-wrapper-` + campaign_data_obj["voice_campaign_user_id"] + `" style="display: none;">
                        <audio controls="" style="display: none;">
                            <source id="easychat_user_call_recording_source" src="" type="audio/mp3">
                        </audio>
            
                        <div class="audio-player" id="audio-player-` + campaign_data_obj["voice_campaign_user_id"] + `">
                            <div class="play-container">
                                <div class="toggle-play play">
                                </div>
                            </div>
                            <div class="time">
                                <div class="current">0:00</div>
                            </div>
                            <div class="timeline">
                                <div class="progress" style="width: 0%;">
                                </div>
                            </div>
                            <div class="time">
                                <div class="length">0:00</div>
                            </div>
                            <button class="audio-player-download-btn">
                                <a href="` + data + `" target="_blank" id="user_call_recording_download_src_` + campaign_data_obj["voice_campaign_user_id"] + `" download="">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M10.5295 4.45395C10.5295 3.65096 11.1871 3 11.9982 3C12.8094 3 13.467 3.65096 13.467 4.45395V11.2521C13.467 11.3556 13.5518 11.4395 13.6564 11.4395H15.6705C15.9582 11.4396 16.2194 11.606 16.3388 11.8652C16.4581 12.1244 16.4136 12.4287 16.225 12.6438L12.5527 16.8249C12.4133 16.984 12.211 17.0754 11.9982 17.0754C11.7855 17.0754 11.5832 16.984 11.4438 16.8249L7.77149 12.6438C7.58282 12.4287 7.53834 12.1244 7.65768 11.8652C7.77702 11.606 8.03822 11.4396 8.32597 11.4395H10.3401C10.4447 11.4395 10.5295 11.3556 10.5295 11.2521V4.45395ZM19.1601 16.6096C19.1601 16.1077 19.5711 15.7008 20.0781 15.7008C20.3223 15.6998 20.5568 15.7951 20.7298 15.9657C20.9028 16.1362 21 16.368 21 16.6096V18.0006C21 19.6571 19.6435 21 17.9701 21H6.02613C4.35423 20.9979 3 19.6557 3 18.0006V16.6096C3 16.1077 3.41103 15.7008 3.91807 15.7008C4.4251 15.7008 4.83613 16.1077 4.83613 16.6096V18.0006C4.83697 18.6507 5.36938 19.1775 6.02613 19.1779H17.9701C18.6268 19.1775 19.1592 18.6507 19.1601 18.0006V16.6096Z" fill="white"></path>
                                    </svg>
                                </a>
                            </button>
                            <button class="audio-player-cross-btn" onclick=close_audio_player("` + campaign_data_obj["voice_campaign_user_id"] + `")>
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M7.23022 6L18.7701 18" stroke="#7B7A7B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                                    <path d="M18.7698 6L7.22995 18" stroke="#7B7A7B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
                                    </svg>
                            </button>
                        </div>
                    </div>
                </div><div>`
                    break;
                }    

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_select_row_html(campaign_data_obj) {
        return ""
    }

    get_row(campaign_data_obj) {
        var _this = this;
        const { enable_select_rows } = false;

        var campaign_data_list = [];

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

    show_filtered_results(event) {
        var _this = this;
        var value = event.target.value;

        if (!_this.data_table_obj) {
            return;
        }

        _this.data_table_obj.search(value).draw();

        var pagination_entry_container = _this.pagination_container.querySelector(".show-pagination-entry-container");

        if (pagination_entry_container) {
            var showing_entry_count = _this.table.querySelectorAll("tbody tr[role='row']").length;
            var total_entry = _this.pagination_metadata.end_point - _this.pagination_metadata.start_point + 1;

            if (value.length != 0) {
                var text = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
                pagination_entry_container.innerHTML = text;
            } else {
                pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
            }
        }
    }

    add_event_listeners_in_rows(container = null) {
        var _this = this;
        if (container == null) container = _this.table;

        // Event listener in searchbar element
        _this.searchbar_element.onkeyup = function (event) {
            _this.show_filtered_results(event);
        }
    }

    add_event_listeners() {
        var _this = this;
    }

    initialize_lead_data_metadata_update_modal() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols;
        var container = document.querySelector("#lead_data_table_meta_div");
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

        initialize_template_custom_tag_input(selected_values, unselected_values, container)
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
        window.localStorage.setItem("voice_campaign_details_table_meta_data", JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = window.localStorage.getItem("voice_campaign_details_table_meta_data");
        if (!lead_data_cols) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {

    var lead_data_cols = [
        ['phone_number', 'Phone Number', true],
        ['status', 'Status', true],
        ['campaign_name', 'Campaign Name', true],
        ['date_created', 'Date Created', true],
        ['type', 'Type', true],
        ['duration', 'Duration', true],
        ['disposition_code', 'Disposition Code', true],
        ['recording', 'Recording', true],
        ['transcript', 'Transcript', true]
    ]
        

    var default_lead_data_cols = [];
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

function initialize_campaign_template_table() {
    if (window.location.pathname.indexOf("/campaign/voice-bot-campaign-details") != 0) {
        return;
    }
    var campaign_table_container = document.querySelector("#voice_history_table_container");
    var campaign_searchbar = document.querySelector("#voice-history-search-bar");
    var pagination_container = document.getElementById("voice_history_table_pagination_div");

    window.VOICE_CAMPAIGN_DETAILS_TABLE = new VoiceDetailsTable(
        campaign_table_container, campaign_searchbar, pagination_container);
}

function initialize_template_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

function save_voice_campaign_details_table_metadata() {

    var lead_data_cols = window.VOICE_CAMPAIGN_DETAILS_TABLE.active_user_metadata.lead_data_cols;

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

    window.VOICE_CAMPAIGN_DETAILS_TABLE.update_table_meta_deta(lead_data_cols)
}

function go_back() {
    window.location.href = "/campaign/dashboard/?bot_pk=" + get_url_multiple_vars()["bot_pk"][0];
}
