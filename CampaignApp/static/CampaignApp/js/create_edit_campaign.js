$(document).ready(function() {
    $('input[name="campaign_channel_cb"]').on('change', function(event) {
        var target = event.target;
        
        update_campaign_progress_bar(target.value);
    });

    var selected_channel = $('input[name="campaign_channel_cb"]:checked').attr('value');

    if (selected_channel) {
        update_campaign_progress_bar(selected_channel);
    }
});

function update_campaign_sidebar(page_id) {
    var sidebar_options = [
        "campaign-cb-info",
        "campaign-cb-audience",
        "campaign-cb-template",
        "campaign-cb-review",
    ]
    for(var idx = 0; idx < sidebar_options.length; idx ++) {
        var option_id = sidebar_options[idx];
        var current_page_id = "campaign-cb-" + page_id;
        var option_element = document.getElementById(option_id);
        var parent_element = option_element.parentElement;
        parent_element.classList.remove("active");

        if(option_id == current_page_id) {
            parent_element.classList.add("active");
            break;
        } else {
            option_element.checked = true;
        }
    }
}

function isValidURL(url) {
    var https_pattern = /^https:\/\/?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/;
    var http_pattern = /^http:\/\/?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$/;
    if (https_pattern.test(url) || http_pattern.test(url)) {
        return true;
    }
    // files stored in data drive have the url of the form :
    // /chat/download-file
    if (url.indexOf('download-file') != -1) {
        return true;
    }
    return false;
}

function save_campaign_basic_detail(element, is_next_clicked=false) {
    var error_message_element = document.getElementById("save-campaign-error-message");
    error_message_element.innerText = "";

    var campaign_name = document.getElementById("campaign-name").value;
    campaign_name = stripHTML(campaign_name);
    campaign_name = remove_special_char_from_str(campaign_name);

    document.getElementById("campaign-name").value = campaign_name;

    if(check_all_speical_chars(campaign_name)) {
        show_campaign_toast("Campaign name with only special characters are not allowed");
        return;
    }

    var selected_channel_id = $('input[name="campaign_channel_cb"]:checked').attr("channel_id");
    var campaign_id_element = document.getElementById("campaign_id");
    var campaign_id = (campaign_id_element.value || null);

    if(campaign_name.length == 0) {
        var error_message = "Please enter valid campaign name";
        show_campaign_toast(error_message);
        return;
    }

    if(selected_channel_id == null || selected_channel_id == undefined) {
        var error_message = "Please select a campaign channel";
        show_campaign_toast(error_message);
        return;
    }

    if (!is_next_clicked) {
        element.innerText = "Saving...";
    }

    var request_params = {
        'campaign_name': campaign_name,
        'channel_id': selected_channel_id,
        'bot_id': BOT_ID,
        'campaign_id': campaign_id,
    };

    var json_params = JSON.stringify(request_params);
    var encrypted_data = campaign_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/campaign/create/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var campaign_id = response["campaign_id"]
                campaign_id_element.value = campaign_id;
                if (is_next_clicked) {
                    window.location.href = window.location.origin + '/campaign/tag-audience/?bot_pk=' + BOT_ID + '&campaign_id=' + campaign_id;
                } else {
                    window.location.href = window.location.origin + '/campaign/dashboard/?bot_pk=' + BOT_ID;
                }

                var error_message = "Campaign has been saved successfully";
                show_campaign_toast(error_message);

            } else if(response["status"] == 400){
                show_campaign_toast(response["status_message"]);
                
            } else if(response["status"] == 401) {
                var error_message = "Not able to save campaign. Campaign is in progress state";
                show_campaign_toast(error_message);

            } else if(response["status"] == 301) {
                var error_message = "Campaign with the same name already exist.";
                show_campaign_toast(error_message);

            } else if(response["status"] == 402) {
                var error_message = "Please setup RCS Channel for the bot.";
                show_campaign_toast(error_message);
            } else {
                var error_message = "Not able to save campaign. Please try again";
                show_campaign_toast(error_message);
            }

            if (is_next_clicked) {
                element.innerText = 'Next'
            } else {
                element.innerText = "Save as Draft";
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function campaign_update_url(campaign_id) {
    var query_parameters = [
        "bot_pk=" + BOT_ID,
        "campaign_id=" + campaign_id
    ].join('&')
    var newurl = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + query_parameters;
    window.history.pushState({ path: newurl }, '', newurl);
}

class IphoneSimulator {
    constructor() {
        var _this = this;
        _this.home_time	= document.querySelector(".date_time .time");
        _this.home_date = document.querySelector(".date_time .date");
        _this.whatsapp_time = document.querySelector(".iphone_whatsapp .time");
        _this.months = ["January", "Feburary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        _this.days = ["Sunday", "Monday", "Tuesday", "WednesDay", "Thursday", "Friday", "Saturday"];
        _this.iphone = document.querySelector(".iphone_p");
        _this.lock_icon = document.querySelector(".date_time .lock");
        _this.home_icon = document.querySelector(".home_icon");
        _this.bottom_icon = document.querySelector(".bottom_icon");
        _this.nav_time 	= document.querySelector(".top_nav .time");
        _this.whatsapp = document.querySelector('.iphone_whatsapp');
        _this.home_screen = document.querySelector('.iphone_p .iphone_front');
        _this.whatsapp_back_btn = document.querySelector('.whatsapp_back_btn');
        _this.whatsapp_icon_btn = document.querySelector('.whatsapp-icon-btn');

        _this.date_time();
        _this.add_event_listeners();
        // _this.show_home_screen();
        _this.show_whatsapp();

        setInterval(function() {
            _this.date_time();
        }, 10000);
    }

    show_whatsapp() {
        var _this = this;
        _this.home_screen.classList.remove("show");
        _this.whatsapp.classList.add("show");
    }

    unlockPhone () {
        var _this = this;
        _this.home_icon.classList.add("unlock");
        _this.lock_icon.classList.add("unlock");
        _this.bottom_icon.classList.add("unlock");
    }

    date_time() {
        var _this = this;
        let date = new Date();
        let hr = date.getHours();
        let min 	= date.getMinutes();
        let sec 	= date.getSeconds();
        let month 	= date.getMonth();
        let day 	= date.getDay();
        let dateNow = date.getDate();
        let am_pm 	= (hr < 12 && hr != 12) ? "AM" : "PM";
        let hrMod 	= hr % 12 || 12;
        let hrReMod = (hr < 10 && hr != 0) ? "0" : "";
        let minMod 	= (min < 10) ? "0" : "";
        
        if(_this.home_date) {
            _this.home_date.textContent 	= `${_this.days[day]}, ${_this.months[month]} ${dateNow}`;
        }
        _this.nav_time.textContent 	= `${hrReMod}${hrMod}:${minMod}${min} ${am_pm}`;
        if(_this.home_time) {
            _this.home_time.textContent = `${hrReMod}${hrMod}:${minMod}${min} ${am_pm}`;
        }

        if(_this.whatsapp_time) {
            _this.whatsapp_time.textContent = `${hrReMod}${hrMod}:${minMod}${min} ${am_pm}`;
        }
    }

    add_event_listeners() {
        var _this = this;
        if(_this.lock_icon) {
            _this.lock_icon.onclick = function(event) {
                if (!_this.home_icon.classList.contains('unlock') &&
                    !_this.lock_icon.classList.contains('unlock') && !_this.bottom_icon.classList.contains('unlock')) {
    
                    _this.unlockPhone();
                }
            }
        }

        if(_this.whatsapp_back_btn) {
            _this.whatsapp_back_btn.onclick = function(event) {
                _this.show_home_screen();
            }
        }

        if(_this.whatsapp_icon_btn) {
            _this.whatsapp_icon_btn.onclick = function(event) {
                _this.show_whatsapp();
            }
        }
    }

    show_home_screen() {
        var _this = this;
        _this.home_screen.classList.add("show");
        _this.whatsapp.classList.remove("show");
        _this.unlockPhone();
    }
}

function update_campaign_progress_bar(checked_element_id) {

    var option = "Message Template";
    if (checked_element_id == 'Voice Bot') {
        option = "Trigger Settings";
    }

    var progress_bar =  document.getElementById('campaign_vertical_progress_bar');

    if (progress_bar) {

        progress_bar.innerHTML = `
                    <div class="campaign-cb-round active">
                        <input type="checkbox" id="campaign-cb-info"/>
                        <label for="campaign-cb-info"></label>
                        <span>Basic Information</span>
                        <div class= "campaign-vertical"></div>
                    </div>
                   
                    

                    <div class="campaign-cb-round">
                        <input type="checkbox" id="campaign-cb-audience" />
                        <label for="campaign-cb-audience"></label>
                        <span>Tag Audience</span>
                        <div class= "campaign-vertical"></div>
                    </div>
                   
               

                    <div class="campaign-cb-round">
                        <input type="checkbox" id="campaign-cb-template" />
                        <label for="campaign-cb-template"></label>
                        <span>${option}</span>
                        <div class="campaign-vertical"></div>
                    </div>
                  
                   

                    <div class="campaign-cb-round">
                        <input type="checkbox" id="campaign-cb-review" />
                        <label for="campaign-cb-review"></label>
                        <span>Review</span>
                    </div>
                   
        `
    }
}

function select_channel(el) {
    var id = el.id;
    id = id.split('-')[1];

    var inp_el = document.getElementById(id);
    
    inp_el.checked = true;
    update_campaign_progress_bar(inp_el.value);
    $(".save-draft-campaign").css("opacity", 1);
    $(".save-draft-campaign").css("pointer-events", "auto");

    $('#next-btn').removeClass('disabled-btn-colored');
    $('.campaign_channel_card').children().css('border', 'none');
    $(el).children().children().css('border-radius', 'none');
    if (inp_el.value == 'Whatsapp Business') {
        $(el).children().children().css('border', '1px solid #9ff7a8');
        $(el).children().children().css('border-radius', '8px');
    }
    else if (inp_el.value == 'Voice Bot') {
        $(el).children().children().css('border', '1px solid #92DEFF');
        $(el).children().children().css('border-radius', '8px');
    }
    else if (inp_el.value == 'RCS') {
        $(el).children().children().css('border', '1px solid #185ABC');
        $(el).children().children().css('border-radius', '8px');
    }
}
