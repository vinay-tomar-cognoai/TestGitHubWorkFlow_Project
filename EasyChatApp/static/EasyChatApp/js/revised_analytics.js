(function ($) {
    $(function () {

        $('.sidenav').sidenav();
        $('.dropdown-trigger').dropdown();
        $('.tooltipped').tooltip();
        $('.collapsible').collapsible();
        $('.modal').modal();
        $('.tooltipped').tooltip({
            position: "top"
        });
        $("#web_visit_count li").tooltip({
            position: "top",
            backgroundColor: "black"
        });
        $("#bot_visit_count li").tooltip({
            position: "top"
        });
        $('.tabs').tabs();
        $('select:not(.non-select2)').select2({width: "100%"});
        $('.datepicker').datepicker();

    }); // end of document ready
})(jQuery); // end of jQuery name space


$(document).ready(function () {
    create_custom_dropdowns();
    $(".select-all-item-checkbox").change(() => {
        if ($(".select-all-item-checkbox").prop("checked")) {
            $(".item-checkbox").prop("checked", true).change();
        } else {
            $(".item-checkbox").prop("checked", false).change();
        }
    });
    $(".item-checkbox").change(() => {
        if (($(".item-checkbox:checked").length == $(".item-checkbox").length)) {
            $(".select-all-item-checkbox").prop("checked", true);
        } else {
            $(".select-all-item-checkbox").prop("checked", false);
        }
    });
});

var most_frequenct_intent_page = 0;
var least_frequenct_intent_page = 0;
var recently_unanswered_message_page = 0;
var trending_website_page = 0;
var form_assist_intent_page = 0
var category_wise_most_frequenct_intent_page = 0;
var category_wise_most_frequenct_individual_page = 0;
var category_wise_most_frequent_history = []
var category_wise_most_intent_end_flag = false
var flow_analytics_page = 0
var intuitive_questions_page = 0
var user_analytics_filter = 1
var channel_wise_supported_language_map = {}
var master_language_list = []
var channel_usage_analytics_card = null
var user_analytics_card = null
var message_analytics_card = null
var device_specific_analytics_card = null
var whatsapp_catalogue_analytics_card = null;
var hour_wise_analytics_card = null
var category_usage_analytics_card = null
var channel_analytics_response = []
var category_usage_response = []
var category_analytics_colors = {}
var channel_color_dict = {}
var form_assist_user_assisted = null
var form_assist_user_find_helpful = null
var form_assist_helpful_percentage = null
let is_revised_filter_applied = false

/////////////////////////////// Debounce //////////////////////////
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

/////////////////////////////// Encryption And Decription //////////////////////////

function CustomEncrypt(msgString, key) {

    // msgString is expected to be Utf8 encoded
    var iv = EasyChatCryptoJS.lib.WordArray.random(16);
    var encrypted = EasyChatCryptoJS.AES.encrypt(msgString, EasyChatCryptoJS.enc.Utf8.parse(key), {
        iv: iv
    });
    var return_value = key;
    return_value += "." + encrypted.toString();
    return_value += "." + EasyChatCryptoJS.enc.Base64.stringify(iv);
    return return_value;
}

function generateRandomString(length) {

    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

function getRandomColor() {

    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
function disable_future_date(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var maxDate = year + '-' + month + '-' + day;
    $("[type='date']").attr("max", maxDate)
}
function getColorlistforcategory(categories) {

    const default_list = ["#334BCA", "#7E73CC", "#bc5090", "#ff6361", "#ffa600"]
    const color_list = []
    for (var i = 0; i < categories.length; i++) {
        if (i < 5) {
            color_list[categories[i]] = default_list[i]
        } else {
            color_list[categories[i]] = getRandomColor();
        }
    }
    return color_list
}

function getColorlistforchannel(channels) {

    const default_list = ['#007AFF', '#54CC61', '#34ABDF', '#FF7B45', '#A4C639', '#EFCA00', '#4165BD', '#4CAF50', '#8E24AA', '#00CAFF', '#26A5D0', '#0E8F82', '#2580E3', '#000000', '#6264A7', '#3573a6']
    const color_list = []
    for (var i = 0; i < channels.length; i++) {
        if (i < 16) {
            color_list[channels[i]] = default_list[i]
        } else {
            color_list[channels[i]] = getRandomColor();
        }
    }
    return color_list
}


function EncryptVariable(data) {

    utf_data = EasyChatCryptoJS.enc.Utf8.parse(data);
    encoded_data = utf_data;
    // encoded_data = EasyChatCryptoJS.enc.Base64.stringify(utf_data);
    random_key = generateRandomString(16);
    // console.log(random_key)
    encrypted_data = CustomEncrypt(encoded_data, random_key);

    return encrypted_data;
}

////////////////////////////////////////////////////////////////////////////////////


function reset_charts() {

    Chart.helpers.each(Chart.instances, function (instance) {
        instance.destroy()
    })
}

function get_url_vars() {

    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    });
    return vars;
}

$(document).on("change", "#selected-bot-for-analytics", function (e) {

    selected_bot_id = document.getElementById("selected-bot-for-analytics").value;
    bot_id = get_url_vars
    if (selected_bot_id != bot_id) {
        window.location.href = window.location.origin + window.location.pathname + "?bot_id=" + selected_bot_id;
    }

    load_all_analytics();
});

$(document).on("change", "#modal-message-default-settings-type", function (e) {

    var filter_type = document.getElementById("modal-message-default-settings-type").value
    document.getElementById("modal-message-default-settings-custom").style.display = "none"
    elems = document.getElementsByClassName("message-default-start-date")
    if (filter_type == "last_month") {
        document.getElementsByClassName("message-default-start-date")[elems.length - 1].value = document.getElementsByClassName("message-default-start-date")[elems.length - 1].getAttribute("value_last_month")

    } else if (filter_type == "last_3_months") {
        document.getElementsByClassName("message-default-start-date")[elems.length - 1].value = document.getElementsByClassName("message-default-start-date")[elems.length - 1].getAttribute("value_last3")

    } else if (filter_type == "since_go_live") {
        document.getElementsByClassName("message-default-start-date")[elems.length - 1].value = document.getElementsByClassName("message-default-start-date")[elems.length - 1].getAttribute("value_golive")

    } else if (filter_type == "custom_date") {
        document.getElementById("modal-message-default-settings-custom").style.display = "block"
        document.getElementsByClassName("message-default-start-date")[elems.length - 1].value = document.getElementsByClassName("message-default-start-date")[elems.length - 1].getAttribute("value")
    }
});

$(function () {
    if (window.location.href.indexOf("chat/nps-analytics/") == -1) {
        update_language_select_dropdown()
    }
});

// A $( document ).ready() block.
function update_channel_language_map() {
    try {
        let channels_string_list = LANGUAGE_CHANNEL_MAPPER.split("$$$")

        for (let i = 0; i < channels_string_list.length; i++) {
            let channel_str = channels_string_list[i]
            const channel_name = channel_str.split("###")[0]
            const list_of_languages = channel_str.split("###")[1].split(",")
            channel_wise_supported_language_map[channel_name] = list_of_languages
            master_language_list = master_language_list.concat(list_of_languages)
        }
        master_language_list = [...new Set(master_language_list)]
    } catch (err) {
        console.log(err)
    }
}

$(document).ready(async function () {

    $("#combine_loader").show()
    $(".easychat-content-wrapper")[0].style.overflow = "hidden"
    await load_all_analytics();
    update_channel_language_map();
    $("#combine_loader").hide()
    $(".easychat-content-wrapper")[0].style.overflow = "auto"

});

async function load_all_analytics() {

    most_frequenct_intent_page = 0;
    least_frequenct_intent_page = 0;
    recently_unanswered_message_page = 0;
    trending_website_page = 0;
    form_assist_intent_page = 0
    category_wise_most_frequenct_intent_page = 0;
    category_wise_most_frequenct_individual_page = 0;
    category_wise_most_frequent_history = []
    category_wise_most_intent_end_flag = false
    flow_analytics_page = 0;
    intuitive_questions_page = 0
    
    $("#conversion_intent_custom_start_date").attr("current_applied_date", $("#conversion_intent_custom_start_date").val())
    $("#conversion_intent_custom_end_date").attr("current_applied_date", $("#conversion_intent_custom_end_date").val())

    await load_first_analytics();
    await load_next_analytics();
    load_last_analytics();
}

function load_first_analytics() {
    if (window.location.href.indexOf("chat/nps-analytics/") == -1) {

        return new Promise(async function (resolve, reject) {
            load_basic_analytics();
            load_session_analytics();
            await load_message_analytics();

            resolve();
        })

    }

}

function load_next_analytics() {

    if (window.location.href.indexOf("chat/nps-analytics/") == -1) {

        return new Promise(async function (resolve, reject) {
            load_form_assist_analytics();
            load_category_analytics();
            load_user_analytics();
            load_hour_wise_analytics();
            await load_channel_analytics();
            await load_device_specific_analytics()

            resolve();
        })
    }
}

function load_last_analytics() {
    if (window.location.href.indexOf("chat/nps-analytics/") == -1) {
        load_next_most_frequenct_intent();
        load_next_least_frequenct_intent();
        load_next_recently_unanswered_messages();
        load_wordcloud_analytics();
        load_next_category_wise_most_frequenct_intent();
        load_next_most_frequent_intent_flow_analytics();
        load_next_intuitive_questions_intent();
        load_user_nudge_analytics(1);
        load_whatsapp_catalogue_analytics();

    }

}

function set_start_end_date(start_date, end_date) {
    $("#conversion_intent_custom_start_date").attr("current_applied_date", start_date)
    $("#conversion_intent_custom_end_date").attr("current_applied_date", end_date)
    document.getElementById("message-analytics-start-date").value = start_date;
    document.getElementById("message-analytics-end-date").value = end_date;

    document.getElementById("user-analytics-start-date").value = start_date;
    document.getElementById("user-analytics-end-date").value = end_date;

    document.getElementById("channel-analytics-start-date").value = start_date;
    document.getElementById("channel-analytics-end-date").value = end_date;

    document.getElementById("session-analytics-start-date").value = start_date;
    document.getElementById("session-analytics-end-date").value = end_date;

    document.getElementById("bot-accuracy-start-date").value = start_date;
    document.getElementById("bot-accuracy-end-date").value = end_date;

    document.getElementById("form-assist-analytics-start-date").value = start_date;
    document.getElementById("form-assist-analytics-end-date").value = end_date;

    document.getElementById("category-analytics-start-date").value = start_date;
    document.getElementById("category-analytics-end-date").value = end_date;

    document.getElementById("wordcloud-analytics-start-date").value = start_date;
    document.getElementById("wordcloud-analytics-end-date").value = end_date;

    // document.getElementById("trending-analytics-start-date").value = start_date;
    // document.getElementById("trending-analytics-end-date").value = end_date;

    document.getElementById("trending-most-frequent-questions-start-date").value = start_date
    document.getElementById("trending-most-frequent-questions-end-date").value = end_date

    document.getElementById("trending-least-frequent-questions-start-date").value = start_date
    document.getElementById("trending-least-frequent-questions-end-date").value = end_date

    document.getElementById("trending-intent-wise-flow-start-date").value = start_date
    document.getElementById("trending-intent-wise-flow-end-date").value = end_date

    document.getElementById("trending-category-wise-start-date").value = start_date
    document.getElementById("trending-category-wise-end-date").value = end_date

    document.getElementById("unanswered-question-wise-start-date").value = start_date
    document.getElementById("unanswered-question-end-date").value = end_date

    document.getElementById("intuitive-question-wise-start-date").value = start_date
    document.getElementById("intuitive-question-wise-end-date").value = end_date

    document.getElementById("user-nudge-analytics-start-date").value = start_date
    document.getElementById("user-nudge-analytics-end-date").value = end_date

    document.getElementById("device-analytics-start-date").value = start_date
    document.getElementById("device-analytics-end-date").value = end_date

    document.getElementById("hour-wise-custom-start-date").value = start_date
    document.getElementById("hour-wise-custom-end-date").value = end_date

    document.getElementById("catalogue_custom_start_date").value = start_date
    document.getElementById("catalogue_custom_end_date").value = end_date
}

function load_default_analytics() {

    if (document.getElementById("check-analytics-filter-select").value == "") {
        M.toast({
            "html": "Atleast one filter should be selected"
        });
    } else {

        elems = document.getElementsByClassName("message-default-start-date")
        start_date = document.getElementsByClassName("message-default-start-date")[elems.length - 1].value;
        end_date = document.getElementsByClassName("message-default-end-date")[elems.length - 1].value;

        if (new Date(start_date).getTime() <= new Date(end_date).getTime()) {
            if (new Date().setHours(0, 0, 0, 0) >= new Date(end_date).setHours(0, 0, 0, 0)) {
                $('#modal-message-default-settings').modal("close");
                
                set_start_end_date(start_date, end_date)

                load_all_analytics();
            } else {
                M.toast({
                    "html": "End Date should not be Future Date"
                });
            }
        } else {
            M.toast({
                "html": "Start Date should be smaller than End Date"
            });
        }
    }
}

function reset_analytics_filter(modal_type) {

    if (modal_type == 'global') {
        let bot_id = get_url_vars()["bot_id"]
        var dropdown_language = get_url_vars()["selected_language"]
        window.location = "/chat/revised-analytics/?bot_id=" + bot_id + "&selected_language=en";
        is_revised_filter_applied = false
    } else if (modal_type == 'hour_wise') {
        let interval_filter = document.getElementsByName("hour-wise-analytics-interval");
        for(var i=1;i<interval_filter.length;i++)
            interval_filter[i].checked = false;
        interval_filter[0].checked = true;

        let time_format_filter = document.getElementsByName("hour-wise-analytics-time-format");
        time_format_filter[0].checked = true
        time_format_filter[1].checked = false

        let date_filter = document.getElementsByName("hour_wise_analytics_date_filter");
        for(var i=0;i<date_filter.length;i++)
            date_filter[i].checked = false;
        document.getElementById("hour-wise-custom-date-select-area").style.display = "none"
        
        load_hour_wise_analytics()
    }
    
}

function get_bot_id() {
    var selected_bot_pk = window.location.href.split("/")[6];

    if (!selected_bot_pk) {
        selected_bot_pk = get_url_vars()["bot_pk"];
    }

    if (!selected_bot_pk) {
        selected_bot_pk = get_url_vars()["bot_id"];
    }

    if (!selected_bot_pk) {
        selected_bot_pk = $("#selected-bot-for-analytics").val();
    }

    return selected_bot_pk;
}

function get_selected_bot_id() {

    return get_bot_id();
}

function get_current_default_channel() {

    if (document.getElementById("default-channel-for-analytics")) {
        return document.getElementById("default-channel-for-analytics").innerText
    }
}

function get_current_default_category() {

    if (document.getElementById("default-category-for-analytics")) {
        return document.getElementById("default-category-for-analytics").innerText
    }
}

function get_current_default_language() {

    if (document.getElementById("default-language-for-analytics")) {
        return document.getElementById("default-language-for-analytics").innerText
    }

}

function load_basic_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        category_name = get_current_default_category()
        selected_language = get_current_default_language()
        bot_pk = get_selected_bot_id();
        document.getElementById("bot-nps-score").innerHTML = "0";
        document.getElementById("bot-no-answered-query").innerHTML = "0";
        document.getElementById("bot-no-messages-today").innerHTML = "0";
        document.getElementById("bot-no-users-today").innerHTML = "0";
        var xhttp = new XMLHttpRequest();
        var params = '';
        xhttp.open("GET", "/chat/get-basic-analytics/?bot_pk=" + bot_pk + "&channel_name=" + channel_value + "&category_name=" + category_name + "&selected_language=" + selected_language, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    document.getElementById("bot-no-messages-today").innerHTML = response["number_of_messages_today"];
                    document.getElementById("bot-no-users-today").innerHTML = response["number_of_users_today"];
                    document.getElementById("bot-no-answered-query").innerHTML = response["number_of_answered_queries"];
                    csat_compatible_channels = ["All",'Web', 'WhatsApp','GoogleBusinessMessages',"Android", "iOS", "Viber"]
                    if(csat_compatible_channels.includes(channel_value)){

                        positive_feedback = response["promoter_feedback"];
                        negative_feedback = response["demoter_feedback"];
                        total_feedback = response["total_feedback"];
                        if (total_feedback != 0) {
                            positive_feedback = Math.ceil(((positive_feedback) * 100) / total_feedback);
                        }
                        document.getElementById("bot-nps-score").innerHTML = positive_feedback;
                        if (channel_value != "All") {
                            document.getElementById("redirect-to-csat-analytics").href = "/chat/nps-analytics/?bot_pk=" + SELECTED_BOT_ID + "&page=1&channels=" + channel_value;
                            document.getElementById("redirect-to-csat-analytics").style.cursor = "pointer";
                        } else {
                            document.getElementById("redirect-to-csat-analytics").href = "/chat/nps-analytics/?bot_pk=" + SELECTED_BOT_ID + "&page=1"
                        }
                    } else {
                        document.getElementById("bot-nps-score").innerHTML = "<span style='font-size:12px;'>Not available</span>";
                        document.getElementById("redirect-to-csat-analytics").href = "javascript:void(0)";
                        document.getElementById("redirect-to-csat-analytics").style.cursor = "auto";
                    }

                    resolve('success');
                }
            }
        }
        xhttp.send(params);
    })
}

function create_category_usage_options() {
    let option_html = ""
    var i = 0;
    for (const category in category_usage_response["category_dict"]) {
        i += 1
        option_html += `
        <li class="graph-legend-item-div">
            <div class="easychat-user-custom-checkbox-div">

                <input class="user-chat-history-checkbox" type="checkbox" id="category_${i}"
                    value="${category}" checked>

                <label for="category_${i}">
                    <span>${category.substring(0, 25)}</span>
                </label>
            </div>
        </li>
        `
        $(`<style>.easychat-user-custom-checkbox-div #category_${i}:checked~label::before{background-color: ${category_analytics_colors[category]}; border-color: ${category_analytics_colors[category]};}</style>`).appendTo('head');
    }
    option_html += `
        <div class="graph-legend-noresult-found" id="graph_legend_noresult_found_category"
            style="display: none;">No result found</div>
    `
    $("#category-usage-options").html(option_html)
}

function update_category_analytics() {
    category_usage_analytics_card && category_usage_analytics_card.destroy()

    const checked_categories = $("#category-usage-options input:checked")

    let category_list = [];
    let message_count_list = [];
    let color_list = []

    for (const elm of checked_categories) {
        const category = elm.value
        category_list.push(category);
        message_count_list.push(category_usage_response["category_dict"][category]);
        color_list.push(category_analytics_colors[category])
    }

    var options = {
        series: message_count_list,
        labels: category_list,
        colors: color_list,
    
        chart: {
            width: '100%',
            height: '75%',
            type: 'donut',
        },
    
        dataLabels: {
            enabled: false
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: 200
                },
                legend: {
                    show: false
                }
            }
        }],
        legend: {
            position: 'right',
            offsetY: 0,
            height: 230,
            show: false,
    
        }
    };
    
    channel_usage_analytics_card = new ApexCharts(document.querySelector("#category_usage_analytics_graph"), options);
    channel_usage_analytics_card.render();
}

function load_category_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        selected_language = get_current_default_language()
        
        category_usage_analytics_card && category_usage_analytics_card.destroy()
        $("#category-analytics-div").hide()
        $("#no-category-analytics-div").hide()

        bot_pk = get_selected_bot_id();
        start_date = document.getElementById("category-analytics-start-date").value;
        end_date = document.getElementById("category-analytics-end-date").value;
        if (start_date > end_date) {
            showToast("Start Date should be smaller than End Date");
            document.getElementById("category-analytics-start-date").value = $("#category-analytics-start-date").attr("current_applied_date");
            document.getElementById("category-analytics-end-date").value = $("#category-analytics-end-date").attr("current_applied_date");
            return;
        }
        $("#category-analytics-start-date").attr("current_applied_date", start_date)
        $("#category-analytics-end-date").attr("current_applied_date", end_date)
        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            channel: channel_value,
            selected_language: selected_language
        });

        json_string = EncryptVariable(json_string)
        json_string = encodeURIComponent(json_string);

        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string;
        xhttp.open("POST", "/chat/get-category-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            $("#no-category-analytics-div").show()
            if (start_date == end_date) {
                $("#category-analytics-date-range").html(`<span></span> ${convert_date_format(start_date)}`)
            } else {
                $("#category-analytics-date-range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
            }
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                category_usage_response = response
                if (response["status"] == 200) {

                    category_list = [];
                    message_count_list = [];

                    for (var category in response["category_dict"]) {
                        category_list.push(category);
                        message_count_list.push(response["category_dict"][category]);
                    }

                    category_analytics_colors = getColorlistforcategory(category_list)

                    if (message_count_list.every(function(elm) {return elm === 0})) {
                        $("#category-analytics-div").hide()
                        $("#no-category-analytics-div").css("display", "flex")
                        return
                    }

                    $("#category-analytics-div").css("display", "flex")
                    $("#no-category-analytics-div").hide()

                    var options = {
                        series: message_count_list,
                        labels: category_list,
                        colors: Object.values(category_analytics_colors),
                    
                        chart: {
                            width: '100%',
                            height: '75%',
                            type: 'donut',
                        },
                        dataLabels: {
                            enabled: false
                        },
                        responsive: [{
                            breakpoint: 480,
                            options: {
                                chart: {
                                    width: 200
                                },
                                legend: {
                                    show: false
                                }
                            }
                        }],
                        legend: {
                            position: 'right',
                            offsetY: 0,
                            height: 230,
                            show: false,
                        }
                    };
                    
                    category_usage_analytics_card = new ApexCharts(document.querySelector("#category_usage_analytics_graph"), options);
                    category_usage_analytics_card.render();

                    create_category_usage_options()

                    resolve();
                }
            }
        }
        xhttp.send(params);
    })
}

function convert_date_format(date) {
    const splitted_date = date.split("-")
    if (splitted_date.length < 3) {
        M.toast({
            html: "Error formatting the Date."
        }, 2000)
    } else {
        return splitted_date.reverse().join("/")
    }
}

const search_most_frequent_intents = debounce(function() {
    load_next_most_frequent_intents_date_filter()
})

function load_next_most_frequent_intents_date_filter() {

    most_frequenct_intent_page = 0
    load_next_most_frequenct_intent()
}

const search_least_frequent_intents = debounce(function() {
    load_next_least_frequent_intents_date_filter()
})

function load_next_least_frequent_intents_date_filter() {

    least_frequenct_intent_page = 0
    load_next_least_frequenct_intent()
}

function load_next_most_frequenct_intent() {

    channel_value = get_current_default_channel()
    category_name = get_current_default_category()
    selected_language = get_current_default_language()
    dropdown_language = get_url_vars()["selected_language"]
    if (typeof dropdown_language == 'undefined'){
        dropdown_language = "en"
    } 

    // document.getElementById("most-frequenct-intents-loader").style.display = "block";
    // document.getElementById("most-frequenct-intents").innerHTML = ""

    start_date = document.getElementById("trending-most-frequent-questions-start-date").value
    end_date = document.getElementById("trending-most-frequent-questions-end-date").value
    if (start_date > end_date) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("trending-most-frequent-questions-start-date").value = $("#trending-most-frequent-questions-start-date").attr("current_applied_date");
        document.getElementById("trending-most-frequent-questions-end-date").value = $("#trending-most-frequent-questions-end-date").attr("current_applied_date");
        return;
    }
    $("#trending-most-frequent-questions-start-date").attr("current_applied_date", start_date)
    $("#trending-most-frequent-questions-end-date").attr("current_applied_date", end_date)
    $("#no-frequent-questions-div").hide()
    $("#frequent-questions-div").hide()
    bot_pk = get_selected_bot_id();
    most_frequenct_intent_page += 1;
    var xhttp = new XMLHttpRequest();
    var params = '';
    let search_term = $("#most_frequent_search").val()

    xhttp.open("GET", "/chat/get-frequent-intent/?bot_pk=" + bot_pk + "&reverse=true&channel_name=" + channel_value + "&page=" + most_frequenct_intent_page + "&start_date=" + start_date + "&end_date=" + end_date + "&category_name=" + category_name + "&selected_language=" + selected_language + "&search=" + search_term + "&dropdown_language=" + dropdown_language, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-frequent-questions-div").show()
        if (this.readyState == 4 && (this.status == 200 || this.status == 300)) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == 300) {
                if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                    document.getElementById("most-frequenct-intents").classList.add("language-right-to-left-wrapper")
                    $("#most-frequent-searchbar-div span").addClass("right-to-left-search-span")
                    $("#most-frequent-searchbar-div input").addClass("right-to-left-search-input")
                } else {
                    document.getElementById("most-frequenct-intents").classList.remove("language-right-to-left-wrapper")
                }
                intent_html = "";
                var i = 0;

                if (response["intent_frequency_list"].length === 0) {
                    $("#frequent-questions-div").hide()
                    $("#no-frequent-questions-div").css("display", "flex")
                    return
                }

                $("#frequent-questions-div").show()
                $("#no-frequent-questions-div").hide()

                for (i = 0; i < 5; i++) {
                    let fetched_intent_name;
                    let fetched_intent_frequency;
                    if (i >= response["intent_frequency_list"].length) {
                        intent_html += '<li class="easychat-session-analytics-item"></li>'
                        continue
                    }
                    else if (response["status"] == 200) {
                        fetched_intent_frequency = response["intent_frequency_list"][i]["frequency"]
                        fetched_intent_name = response["intent_frequency_list"][i]["multilingual_name"]
                    } else {
                        fetched_intent_frequency = response["intent_frequency_list"][i]["frequency"]
                        fetched_intent_name = response["intent_frequency_list"][i]["intent_name"]
                    }
                    fetched_intent_name = sanitize_html(fetched_intent_name)
                    intent_html += `
                        <li class="easychat-session-analytics-item intent-list-item">
                            <div class="easychat-analytics-data-card-content-div">
                                <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <rect width="24" height="24" rx="4" fill="#EFF2F5" />
                                    </svg>
                                </div>
                                <div class="easychat-analytics-data-card-item-text">
                                    ${fetched_intent_name}
                                </div>
                            </div>
                            <div class="easychat-analytics-data-card-value">
                                ${fetched_intent_frequency}
                            </div>
                        </li>
                    `
                }

                if (response["is_last_page"] == false) {
                    $("#most_frequent_right").css("display", "inline")
                } else {
                    $("#most_frequent_right").css("display", "none")
                }

                if (response["is_single_page"] == false) {
                    if (most_frequenct_intent_page === 1) {
                        $("#most_frequent_left").hide()
                    } else {
                        $("#most_frequent_left").show()
                    }
                } else {
                    $("#most_frequent_left").css("display", "none")
                }

                // document.getElementById("most-frequenct-intents-loader").style.display = "none";
                document.getElementById("most-frequenct-intents").innerHTML = intent_html;
                if(response["status"]==300){
                    document.getElementById("translation_api_toast_container").style.display = "flex";
                    setTimeout(api_fail_message_none, 4000);
                }
            }
        }
    }
    xhttp.send(params);
}

function load_previous_most_frequenct_intent() {

    most_frequenct_intent_page -= 2;

    if (most_frequenct_intent_page < 0) {
        most_frequenct_intent_page = 0;
    }
    
    load_next_most_frequenct_intent()
}

function load_next_least_frequenct_intent() {

    channel_value = get_current_default_channel()
    category_name = get_current_default_category()
    selected_language = get_current_default_language()
    dropdown_language = get_url_vars()["selected_language"]
    if (typeof dropdown_language == 'undefined'){
        dropdown_language = "en"
    } 

    // document.getElementById("least-frequenct-intents-loader").style.display = "block";
    // document.getElementById("least-frequenct-intents").innerHTML = ""

    start_date = document.getElementById("trending-least-frequent-questions-start-date").value
    end_date = document.getElementById("trending-least-frequent-questions-end-date").value
    if (start_date > end_date) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("trending-least-frequent-questions-start-date").value = $("#trending-least-frequent-questions-start-date").attr("current_applied_date");
        document.getElementById("trending-least-frequent-questions-end-date").value = $("#trending-least-frequent-questions-end-date").attr("current_applied_date");
        return;
    }
    $("#trending-least-frequent-questions-start-date").attr("current_applied_date", start_date)
    $("#trending-least-frequent-questions-end-date").attr("current_applied_date", end_date)
    $("#no-least-frequent-div").hide()
    $("#least-frequent-div").hide()
    bot_pk = get_selected_bot_id();
    least_frequenct_intent_page += 1;
    var xhttp = new XMLHttpRequest();
    var params = '';
    let search_term = $("#least_frequent_search").val()

    xhttp.open("GET", "/chat/get-frequent-intent/?bot_pk=" + bot_pk + "&reverse=false&channel_name=" + channel_value + "&page=" + least_frequenct_intent_page + "&start_date=" + start_date + "&end_date=" + end_date + "&category_name=" + category_name + "&selected_language=" + selected_language + "&search=" + search_term + "&dropdown_language=" + dropdown_language, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-least-frequent-div").show()
        if (this.readyState == 4 && (this.status == 200 || this.status == 300)) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == 300) {
                if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                    document.getElementById("least-frequent-intents").classList.add("language-right-to-left-wrapper")
                    $("#least-frequent-searchbar-div span").addClass("right-to-left-search-span")
                    $("#least-frequent-searchbar-div input").addClass("right-to-left-search-input")
                } else {
                    document.getElementById("least-frequent-intents").classList.remove("language-right-to-left-wrapper")
                }
                intent_html = "";
                var i = 0;

                if (response["intent_frequency_list"].length === 0) {
                    $("#least-frequent-div").hide()
                    $("#no-least-frequent-div").css("display", "flex")
                    return
                }

                $("#least-frequent-div").show()
                $("#no-least-frequent-div").hide()

                for (i = 0; i < 5; i++) {
                    let least_frequent_intent_name;
                    let least_frequenct_intent_frequency;
                    if (i >= response["intent_frequency_list"].length) {
                        intent_html += '<li class="easychat-session-analytics-item"></li>'
                        continue
                    }
                    else if (response["status"] == 200) {
                        least_frequent_intent_name = response["intent_frequency_list"][i]["multilingual_name"]
                        least_frequent_intent_frequency = response["intent_frequency_list"][i]["frequency"]
                    } else {
                        least_frequent_intent_name = response["intent_frequency_list"][i]["intent_name"]
                        least_frequent_intent_frequency = response["intent_frequency_list"][i]["frequency"]
                    }
                    least_frequent_intent_name = sanitize_html(least_frequent_intent_name)

                    intent_html += `
                        <li class="easychat-session-analytics-item intent-list-item">
                            <div class="easychat-analytics-data-card-content-div">
                                <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <rect width="24" height="24" rx="4" fill="#EFF2F5" />
                                    </svg>
                                </div>
                                <div class="easychat-analytics-data-card-item-text">
                                    ${least_frequent_intent_name}
                                </div>
                            </div>
                            <div class="easychat-analytics-data-card-value">
                                ${least_frequent_intent_frequency}
                            </div>
                        </li>
                    `
                }

                if (response["is_last_page"] == false) {
                    $("#least_frequent_right").css("display", "inline")
                } else {
                    $("#least_frequent_right").css("display", "none")
                }

                if (response["is_single_page"] == false) {
                    if (least_frequenct_intent_page === 1) {
                        $("#least_frequent_left").hide()
                    } else {
                        $("#least_frequent_left").show()
                    }
                } else {
                    $("#least_frequent_left").css("display", "none")
                }

                // document.getElementById("least-frequenct-intents-loader").style.display = "none"
                document.getElementById("least-frequent-intents").innerHTML = intent_html;
                if(response["status"]==300){
                document.getElementById("translation_api_toast_container").style.display = "flex";
                setTimeout(api_fail_message_none, 4000);
                }
            }
        }
    }
    xhttp.send(params);
}

function load_previous_least_frequenct_intent() {


    least_frequenct_intent_page -= 2;
    if (least_frequenct_intent_page < 0) {
        least_frequenct_intent_page = 0;
    }

    load_next_least_frequenct_intent()
    
}

const search_unanswered_wise_intents = debounce(function() {
    load_unanswered_wise_intents()
})

function load_unanswered_wise_intents() {

    recently_unanswered_message_page = 0
    load_next_recently_unanswered_messages()
}

function load_next_recently_unanswered_messages() {

    channel_value = get_current_default_channel()
    selected_language = get_current_default_language()

    // document.getElementById("recently-unanswered-messages-loader").style.display = "block";
    // document.getElementById("recently-unanswered-messages").innerHTML = "";

    bot_pk = get_selected_bot_id();
    recently_unanswered_message_page += 1;
    start_date = document.getElementById("unanswered-question-wise-start-date").value
    end_date = document.getElementById("unanswered-question-end-date").value
    if (start_date > end_date) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("unanswered-question-wise-start-date").value = $("#unanswered-question-wise-start-date").attr("current_applied_date");
        document.getElementById("unanswered-question-end-date").value = $("#unanswered-question-end-date").attr("current_applied_date");
        return;
    }
    $("#unanswered-question-wise-start-date").attr("current_applied_date", start_date)
    $("#unanswered-question-end-date").attr("current_applied_date", end_date)
    $("#no-unanswered-questions-div").hide()
    $("#unanswered-questions-div").hide()
    var xhttp = new XMLHttpRequest();
    var params = '';
    let search_term = $("#unanswered_question_search").val()

    xhttp.open("GET", "/chat/get-recently-unanswered-message/?bot_pk=" + bot_pk + "&channel_name=" + channel_value + "&page=" + recently_unanswered_message_page + "&start_date=" + start_date + "&end_date=" + end_date + "&selected_language=" + selected_language + "&search=" + search_term, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-unanswered-questions-div").show()
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == 300) {
                intent_html = "";
                var i = 0;

                if (response["unanswered_message_list"].length === 0) {
                    $("#unanswered-questions-div").hide()
                    $("#no-unanswered-questions-div").css("display", "flex")
                    return
                }

                $("#unanswered-questions-div").show()
                $("#no-unanswered-questions-div").hide()

                for (i = 0; i < 5; i++) {
                    let unanswered_intent_name;
                    let unanswered_intent_frequency;
                    if (i >= response["unanswered_message_list"].length) {
                        intent_html += '<li class="easychat-session-analytics-item"></li>'
                        continue
                    } else {
                        unanswered_intent_name = response["unanswered_message_list"][i][0]
                        unanswered_intent_frequency = response["unanswered_message_list"][i][1]
                    }

                    unanswered_intent_name = sanitize_html(unanswered_intent_name)

                    intent_html += `
                        <li class="easychat-session-analytics-item intent-list-item">
                            <div class="easychat-analytics-data-card-content-div">
                                <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <rect width="24" height="24" rx="4" fill="#EFF2F5" />
                                    </svg>
                                </div>
                                <div class="easychat-analytics-data-card-item-text">
                                    ${unanswered_intent_name}
                                </div>
                            </div>
                            <div class="easychat-analytics-data-card-value">
                                ${unanswered_intent_frequency}
                            </div>
                        </li>
                    `
                }

                if (response["is_last_page"] == false) {
                    $("#unanswered-questions-right").css("display", "inline")
                } else {
                    $("#unanswered-questions-right").css("display", "none")
                }

                if (response["is_single_page"] == false) {
                    if (recently_unanswered_message_page === 1) {
                        $("#unanswered-questions-left").hide()
                    } else {
                        $("#unanswered-questions-left").show()
                    }
                } else {
                    $("#unanswered-questions-left").css("display", "none")
                }

                // document.getElementById("recently-unanswered-messages-loader").style.display = "none";
                document.getElementById("recently-unanswered-messages").innerHTML = intent_html;
            }
        }
    }
    xhttp.send(params);
}

function load_previous_recently_unanswered_messages() {

    recently_unanswered_message_page -= 2;

    if (recently_unanswered_message_page < 0) {
        recently_unanswered_message_page = 0;
    }
    
    load_next_recently_unanswered_messages()
}

function load_wordcloud_analytics() {

    channel_value = get_current_default_channel()
    category_name = get_current_default_category()
    selected_language = get_current_default_language()
    bot_pk = get_selected_bot_id();
    start_date = document.getElementById("wordcloud-analytics-start-date").value;
    end_date = document.getElementById("wordcloud-analytics-end-date").value;
    if (start_date > end_date) {
        showToast("Start Date should be smaller than End Date");
        document.getElementById("wordcloud-analytics-start-date").value = $("#wordcloud-analytics-start-date").attr("current_applied_date");
        document.getElementById("wordcloud-analytics-end-date").value = $("#wordcloud-analytics-end-date").attr("current_applied_date");
        return;
    }
    $("#wordcloud-analytics-start-date").attr("current_applied_date", start_date)
    $("#wordcloud-analytics-end-date").attr("current_applied_date", end_date)
    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        start_date: start_date,
        end_date: end_date,
        channel: channel_value,
        category_name: category_name,
        selected_language: selected_language
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    // var canvas_small = document.getElementById("word_cloud_small_loading_data"),
    // ctx = canvas_small.getContext("2d")
    // ctx.fillStyle = "#227E39";
    // ctx.font = '20px Arial, Helvetica, sans-serif';
    // var textString = "Loading Wordcloud...",
    //     textWidth = ctx.measureText(textString).width;
    // ctx.fillText(textString, (canvas_small.width / 2) - (textWidth / 2), 100);
    // $("#word_cloud_small_loading_data").show()
    $("#word_cloud_small_no_data").hide()
    $("#word_cloud_small").hide()
    $("#open-wordcloud-full-window").hide()

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", "/chat/get-word-cloud/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#word_cloud_small_no_data").show()
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                make_wordcloud(response["wordcloud_data"])
                // $("#download-word-cloud-data").show()
            }
            document.getElementById("wordcloud-time-range").innerHTML = `<span>Range :</span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`;
            document.getElementById("wordcloud-big-time-range").innerHTML = `<span>(Range: </span>${convert_date_format(start_date)} - ${convert_date_format(end_date)})`;
        }
    }
    xhttp.send(params);
}

function make_wordcloud(data_list) {

    if (data_list.length === 0) {
        $("#word_cloud_small_no_data").css('display', 'flex');
        $("#word_cloud_small").hide()
        $("#open-wordcloud-full-window").hide()
        // $("#word_cloud_small_loading_data").hide()
        return
    }
    // $("#word_cloud_small_loading_data").hide()
    $("#word_cloud_small_no_data").hide()
    $("#word_cloud_small").show()
    $("#open-wordcloud-full-window").show()
    list = [];
    // frequency_list is used to store orignal frequency
    const frequency_map = new Map();

    for (var i in data_list) {
        frequency_map.set(data_list[i]["word"], data_list[i]["freq"]);
        // in this if condition we set maximum frequency so word font wont exceed
        if (data_list[i]["freq"]>5){
            list.push([data_list[i]["word"], "5"])
        }
        else{
        list.push([data_list[i]["word"], data_list[i]["freq"]])
    }
    }
    const wordCanvas = $('#word_cloud_small');
    wordCanvas.attr('width', '800').attr('height', '400');
    WordCloud.minFontSize = "15px"
    weightFactor = 32
    
    WordCloud(document.getElementById('word_cloud_small'), {
        list: list,
        gridSize: 16,
        weightFactor: weightFactor,
        fontFamily: 'Silka, Helvetica, sans-serif',
        fontWeight: '500',
        color: '#1E293B',
        hover: window.drawBox,
        // hover: function (item) {
        //     try {
        //         document.getElementById("wordcloud-freq-info").innerHTML = "<medium style='font-size:medium'>" + item[0] + ': ' + item[1] + "</medium>";
        //     } catch (err) {
        //         $("#wordcloud-freq-info").hide();
        //     }
        // },
        backgroundColor: '#F8FDFD'
    });

    WordCloud(document.getElementById('word_cloud_big'), {
        list: list,
        gridSize: 16,
        weightFactor: weightFactor,
        rotateRatio: 0.5,
        rotationSteps: 2,
        fontFamily: 'Silka, Helvetica, sans-serif',
        color: '#1E293B',
        hover: window.drawBox,
        hover: function (bigitem) {
            try {  
                document.getElementById("wordcloud-big-freq-info").innerHTML = `<div><span>Word: </span>${bigitem[0]}<br><span>Freq: </span>${frequency_map.get(bigitem[0])}</div>`;
                $("#wordcloud-big-freq-info").show()
                
            } catch (err) {
                document.getElementById("wordcloud-big-freq-info").innerHTML = "<div><span>Word: </span><br><span>Freq: </span></div>";
            }
        },
        backgroundColor: 'transparent'
    });
}

function load_previous_most_frequenct_website_url() {

    document.getElementById("trending-time-range-loader").style.display = "block";
    document.getElementById("trending-time-range").innerHTML = "";
    bot_pk = get_selected_bot_id();
    start_date = document.getElementById("trending-analytics-start-date").value;
    end_date = document.getElementById("trending-analytics-end-date").value;
    channel_value = get_current_default_channel()

    trending_website_page -= 1;
    if (trending_website_page <= 0) {
        trending_website_page = 1;
    }
    var xhttp = new XMLHttpRequest();
    var params = '';
    xhttp.open("GET", "/chat/get-frequent-window-location/?bot_pk=" + bot_pk + "&reverse=true&channel=" + channel_value + "&page=" + trending_website_page + "&start_date=" + start_date + "&end_date=" + end_date, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                website_html = "";

                var i = 0;
                for (i = 0; i < response["web_pages_name"].length; i++) {
                    window_location = response["web_pages_name"][i];
                    web_page_visited_count = response["web_page_visited_count"][i]
                    bot_clicked_count = response["bot_clicked_count"][i]
                    website_html += '<ul class="tabs tabs-fixed-width" style="overflow:unset;line-height:0.7;height:55px !important"><li class="col s7"><a href="' + window_location + '" target="_blank" class="black-text">' + window_location.substring(0, 40) + '</a></li>'
                    website_html += '<li class="col s2 tab tooltip"><span class="tooltiptext" style="padding: 10px;line-height: normal;text-transform: none;">Web page visit count</span><a class="active" style="display: flex;justify-content: center;padding-right: 0px; border: unset !important; background: rgba(50, 93, 188, 0.1) !important;"><svg style="margin-left: -2em ;margin-bottom: -0.2em; margin-top: 0.9em;" width="20" height="18" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0 8.70753V8.68207C0.225941 5.72885 1.28033 3.51393 3.11297 2.1137C4.9205 0.688004 6.87866 0.000616046 9.01255 0.000616046C11.2469 -0.0248428 13.3305 0.738922 15.1883 2.26645C17.0711 3.76852 18 6.0089 18 8.9112V9.08941C18 12.0172 17.0711 14.2066 15.1883 15.7087C13.3054 17.2362 11.2218 18 8.98745 18H8.88703C6.70293 17.9745 4.69456 17.2108 2.83682 15.6832C0.979079 14.1812 0.0251046 11.8644 0 8.70753ZM8.46025 4.7105V0.688004H7.85774C7.73222 0.840757 7.6318 1.01897 7.53138 1.17172C7.43096 1.32447 7.33054 1.47723 7.23013 1.65544C7.12971 1.80819 7.00418 2.01186 6.92887 2.16462C6.82845 2.31737 6.75314 2.47012 6.67782 2.64833C6.5272 2.90292 6.40167 3.15751 6.30126 3.38664C6.17573 3.61577 6.07531 3.8449 6 4.04857C6.15063 4.1504 6.32636 4.2777 6.5272 4.35407C6.75314 4.43045 6.97908 4.50683 7.20502 4.55774C7.45607 4.60866 7.68201 4.63412 7.88285 4.65958C8.10879 4.68504 8.30962 4.7105 8.46025 4.7105ZM9.51464 0.688004V4.68504C9.64017 4.68504 9.7908 4.7105 9.94142 4.68504C10.0921 4.68504 10.2678 4.65958 10.4184 4.63412C10.6946 4.5832 11.0209 4.50683 11.272 4.43045C11.5481 4.32862 11.7992 4.20132 11.9749 4.04857C11.6736 3.31026 11.3473 2.72471 11.0209 2.16462C10.6946 1.60452 10.318 1.1208 9.91632 0.713463V0.688004H9.51464ZM6.80335 0.917133V0.891675C6.62761 0.968051 6.45188 1.09535 6.25105 1.17172C6.07531 1.2481 5.84937 1.34993 5.67364 1.45177C5.32218 1.62998 4.97071 1.83365 4.61925 2.06278C4.29289 2.29191 3.96653 2.5465 3.69038 2.80109C3.7908 2.90292 3.91632 3.00476 4.01674 3.08113C4.11716 3.15751 4.24268 3.25934 4.3682 3.36118C4.46862 3.4121 4.59414 3.48847 4.71967 3.59031C4.84519 3.66669 4.99582 3.76852 5.14644 3.87036C5.34728 3.4121 5.54812 2.92838 5.79916 2.49558C6.05021 2.03732 6.32636 1.60452 6.60251 1.22264C6.62761 1.17172 6.65272 1.1208 6.70293 1.06989C6.72803 1.04443 6.75314 0.968051 6.80335 0.917133ZM14.4854 2.80109V2.77563C13.8577 2.29191 13.3054 1.88457 12.7531 1.62998C12.2008 1.37539 11.6485 1.1208 11.1464 0.917133C11.5481 1.32447 11.8996 1.83365 12.1255 2.31737C12.3766 2.82655 12.6276 3.36118 12.8285 3.87036C12.9289 3.81944 13.0544 3.76852 13.205 3.66669C13.3305 3.59031 13.5063 3.51393 13.6569 3.43756C13.8075 3.33572 13.9331 3.23389 14.0837 3.13205C14.2343 3.00476 14.3849 2.90292 14.4854 2.80109ZM14.0586 8.4784H16.9456C16.9456 7.53643 16.7448 6.64537 16.3682 5.72885C16.0167 4.83779 15.5146 4.09949 14.887 3.46302V3.43756C14.7615 3.64123 14.5858 3.81944 14.41 3.94673C14.2092 4.07403 14.0335 4.17586 13.8326 4.2777C13.7071 4.35407 13.5816 4.45591 13.4561 4.50683C13.3305 4.5832 13.1548 4.63412 13.0293 4.7105C13.1297 4.91417 13.2301 5.1433 13.3305 5.34697C13.4059 5.5761 13.5314 5.83069 13.5816 6.05981C13.7322 6.46716 13.8326 6.89996 13.9331 7.33276C14.0084 7.71464 14.0586 8.12198 14.0586 8.4784ZM4.97071 4.7105V4.68504C4.76987 4.5832 4.54393 4.50683 4.3682 4.40499C4.19247 4.2777 4.01674 4.1504 3.86611 4.04857C3.71548 3.97219 3.56485 3.87036 3.43933 3.76852C3.31381 3.66669 3.21339 3.56485 3.11297 3.46302C2.46025 4.09949 1.98326 4.81233 1.68201 5.65247C1.35565 6.49261 1.12971 7.43459 1.02929 8.45294H4.11716C4.11716 7.7401 4.21757 7.05271 4.39331 6.36532C4.54393 5.65247 4.76987 5.11784 4.97071 4.7105ZM8.46025 8.45294V5.52518C8.25941 5.55064 8.00837 5.55064 7.78243 5.52518C7.53138 5.49972 7.28033 5.42334 7.05439 5.34697C6.85356 5.29605 6.60251 5.24513 6.40167 5.16876C6.17573 5.11784 5.94979 5.016 5.77406 4.91417C5.62343 5.16876 5.49791 5.47426 5.39749 5.80523C5.27197 6.11073 5.19665 6.4417 5.12134 6.7472C5.07113 7.05271 5.04603 7.38367 5.02092 7.66372C4.99582 7.94377 4.97071 8.22381 4.97071 8.45294H8.46025ZM9.51464 5.5761V8.45294H13.2301C13.2301 8.30019 13.2301 8.12198 13.205 7.91831C13.1548 7.7401 13.1297 7.51097 13.1046 7.3073C13.0293 7.00179 12.954 6.67083 12.8536 6.36532C12.7531 6.08527 12.6527 5.80523 12.5272 5.5761C12.477 5.4488 12.4268 5.29605 12.3766 5.19421C12.3013 5.06692 12.2259 4.99054 12.1757 4.91417C11.8996 5.11784 11.523 5.24513 11.0711 5.34697C10.6444 5.4488 10.1423 5.55064 9.69038 5.5761H9.51464ZM4.11716 9.29309H1.02929C1.02929 9.72588 1.1046 10.2096 1.23013 10.7952C1.35565 11.4062 1.60669 11.9663 1.88285 12.5773C2.00837 12.8828 2.159 13.1883 2.30962 13.4938C2.48536 13.7738 2.68619 14.0793 2.88703 14.3594C3.03766 14.2576 3.18828 14.1812 3.31381 14.1048C3.46444 14.0284 3.64017 13.9266 3.7908 13.8502C3.96653 13.7738 4.14226 13.6975 4.3431 13.5956C4.51883 13.5192 4.74477 13.4174 4.97071 13.3156C4.76987 12.6791 4.54393 12.0681 4.39331 11.3807C4.21757 10.7188 4.11716 10.0568 4.11716 9.31854V9.29309ZM8.46025 12.2718V9.29309H4.97071C4.97071 9.49676 4.99582 9.80226 5.04603 10.1078C5.07113 10.4133 5.14644 10.7442 5.19665 11.0752C5.29707 11.4316 5.37239 11.788 5.4728 12.0936C5.57322 12.3991 5.67364 12.6536 5.77406 12.8828C6.22594 12.7046 6.67782 12.5773 6.97908 12.5009C7.30544 12.3991 7.60669 12.3227 7.90795 12.2972H8.1841C8.28452 12.2718 8.38494 12.2718 8.46025 12.2718ZM9.51464 9.29309V12.2463C9.69038 12.2718 9.89121 12.2972 10.0921 12.3227C10.318 12.3481 10.5941 12.3991 10.8201 12.45L11.1967 12.5264C11.3222 12.5773 11.4728 12.6027 11.5983 12.6282C11.749 12.6791 11.8996 12.7046 12.0502 12.7555C12.1757 12.8064 12.3013 12.8319 12.4017 12.8828C12.728 12.0426 12.9289 11.3552 13.0544 10.7697C13.1799 10.2096 13.2301 9.72588 13.2301 9.31854V9.29309H9.51464ZM16.9456 9.31854V9.29309H14.0586V9.44584C14.0335 9.92955 13.9582 10.4896 13.8577 11.0752C13.7573 11.6353 13.5314 12.2972 13.2301 13.1119C13.6318 13.3156 14.0084 13.5192 14.3096 13.7229C14.6109 13.9266 14.887 14.1557 15.0879 14.3594C15.5146 13.9266 15.8912 13.341 16.2176 12.5773C16.5439 11.839 16.7699 11.0752 16.8954 10.2605C16.9205 10.1078 16.9205 9.95501 16.9456 9.80226V9.31854ZM8.46025 17.058V13.0864C7.83264 13.1883 7.30544 13.3156 6.90377 13.4174C6.50209 13.5192 6.20084 13.6211 6 13.7229C6.15063 14.1048 6.30126 14.4358 6.45188 14.7413C6.60251 15.0213 6.77824 15.3268 6.92887 15.5814C6.97908 15.6832 7.0795 15.7851 7.15481 15.9124C7.23013 16.0142 7.28033 16.1415 7.35565 16.2433C7.43096 16.3706 7.50628 16.5234 7.58159 16.6761C7.68201 16.8034 7.75732 16.9562 7.85774 17.058H8.46025ZM9.51464 17.058H10.0921C10.318 16.8798 10.5439 16.6252 10.7197 16.3452C10.9205 16.0651 11.1464 15.7342 11.2971 15.4541C11.4728 15.1232 11.6485 14.8176 11.7992 14.5121C11.9498 14.2066 12.0753 13.9266 12.1757 13.7229C11.8996 13.6211 11.523 13.5192 11.1464 13.4174C10.7699 13.3156 10.2427 13.2137 9.51464 13.1119V17.058ZM14.4854 14.9704V14.9449C14.4351 14.8686 14.3347 14.7667 14.2594 14.6904C14.1841 14.614 14.0586 14.5121 13.9331 14.4358C13.8326 14.3594 13.7071 14.283 13.5565 14.2066C13.4059 14.1303 13.205 14.0284 13.0293 13.9266C12.9289 14.1303 12.7531 14.4867 12.5021 14.9704C12.2762 15.4541 11.8745 16.0397 11.3724 16.6761C12 16.5743 12.5523 16.3452 13.0544 16.0397C13.6067 15.7596 14.0837 15.3777 14.4854 14.9704ZM5.14644 14.1557V14.1303C4.97071 14.2321 4.69456 14.3594 4.41841 14.4867C4.11716 14.614 3.7908 14.7667 3.48954 14.9704C3.66527 15.1232 3.841 15.2759 3.99163 15.3777C4.14226 15.505 4.31799 15.6069 4.46862 15.7087C4.74477 15.8869 5.07113 16.0651 5.39749 16.2179C5.72385 16.3706 6.12552 16.5234 6.62761 16.6761C6.45188 16.4725 6.32636 16.2179 6.20084 16.0142C6.07531 15.8105 5.92469 15.6069 5.79916 15.4032C5.67364 15.1995 5.57322 14.9704 5.4728 14.7667C5.34728 14.5631 5.24686 14.3594 5.14644 14.1557Z" fill="#325DBC"/></svg>' + web_page_visited_count + '</a></li>'
                    website_html += '<li class="col s2 tab tooltip"><span class="tooltiptext" style="padding: 10px;line-height: normal;text-transform: none;">Bot visit count</span><a class="active" style="display: flex;justify-content: center;padding-right: 0px; border: unset !important; background: rgba(50, 93, 188, 0.1) !important;"><svg style="margin-left: -2em ;margin-bottom: -0.2em; margin-top: 0.9em;" width="20" height="18" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 18C13.9706 18 18 13.9706 18 9C18 4.02944 13.9706 0 9 0C4.02944 0 0 4.02944 0 9C0 13.9706 4.02944 18 9 18Z" fill="url(#paint0_linear)"/><path fill-rule="evenodd" clip-rule="evenodd" d="M13.4746 11.3044C13.4746 10.6 12.9035 10.029 12.1992 10.029H5.68053C4.97612 10.029 4.40509 10.6 4.40509 11.3044V11.8187C4.40509 12.4381 4.67529 13.0269 5.145 13.4306C6.03094 14.1923 7.30003 14.5646 8.93798 14.5646C10.5762 14.5646 11.8461 14.1921 12.7335 13.4303C13.2039 13.0264 13.4746 12.4375 13.4746 11.8175V11.3044ZM8.93815 3.22697L8.88047 3.23085C8.67296 3.259 8.51302 3.43688 8.51302 3.65211L8.51257 4.0767L6.52882 4.07698C5.82441 4.07698 5.25338 4.64801 5.25338 5.35241V7.90589C5.25338 8.6103 5.82441 9.18133 6.52882 9.18133H11.3471C12.0515 9.18133 12.6225 8.6103 12.6225 7.90589V5.35241C12.6225 4.64801 12.0515 4.07698 11.3471 4.07698L9.36286 4.0767L9.36331 3.65211L9.35942 3.59442C9.33127 3.3869 9.1534 3.22697 8.93815 3.22697ZM6.95396 6.48573C6.95396 6.09462 7.27101 5.77756 7.66213 5.77756C8.05324 5.77756 8.3703 6.09462 8.3703 6.48573C8.3703 6.87685 8.05324 7.1939 7.66213 7.1939C7.27101 7.1939 6.95396 6.87685 6.95396 6.48573ZM9.50072 6.48573C9.50072 6.09462 9.81777 5.77756 10.2089 5.77756C10.6 5.77756 10.9171 6.09462 10.9171 6.48573C10.9171 6.87685 10.6 7.1939 10.2089 7.1939C9.81777 7.1939 9.50072 6.87685 9.50072 6.48573ZM9.6539 7.82121C9.6539 8.21666 9.33332 8.53724 8.93787 8.53724C8.54241 8.53724 8.22183 8.21666 8.22183 7.82121H9.6539Z" fill="white"/><defs><linearGradient id="paint0_linear" x1="9" y1="0" x2="9" y2="18" gradientUnits="userSpaceOnUse"><stop stop-color="#3871F0"/><stop offset="1" stop-color="#0F3A9A"/></linearGradient></defs></svg>' + bot_clicked_count + '</a></li></ul>'

                }

                if (i < 6) {
                    for (i; i < 5; i++) {
                        website_html += '<li>...</li>';
                    }
                }

                if (response["is_last_page"] == false) {
                    website_html += '<li style="display:block">\
                        <a href="javascript:void(0)" class="right" style="color:#F56565" onclick="load_next_most_frequenct_website_url()">\
                            <i class="material-icons">chevron_right</i>\
                        </a>';
                } else {
                    website_html += '<li style="display:block">';
                }

                if (response["is_single_page"] == false) {
                    website_html += '<a href="javascript:void(0)" class="right " style="color:#F56565" onclick="load_previous_most_frequenct_website_url()">\
                        <i class="material-icons">chevron_left</i>\
                    </a>\
                </li>';
                } else {

                    website_html += '</li>';
                }

                document.getElementById("trending-time-range-loader").style.display = "none";
                document.getElementById("trending-website").innerHTML = website_html;
                document.getElementById("trending-time-range").innerHTML = "<medium>" + response["start_date"] + " to " + response["end_date"] + "</medium>";
            }
        }
    }
    xhttp.send(params);
}

var dynamicColors = function () {

    var r = Math.floor(Math.random() * 255);
    var g = Math.floor(Math.random() * 255);
    var b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
};


function create_channel_analytics_options() {
    let option_html = ""
    for (const channel in channel_analytics_response["channel_dict"]) {
        option_html += `
        <li class="graph-legend-item-div">
            <div class="easychat-user-custom-checkbox-div">
                <input class="user-chat-history-checkbox" type="checkbox" id="${channel}_channel"
                    value="${channel}" checked>
                <label for="${channel}_channel">
                    <span>${channel}</span>
                </label>
            </div>
        </li>
        `
        $(`<style>.easychat-user-custom-checkbox-div #${channel}_channel:checked~label::before{background-color: ${channel_color_dict[channel]}; border-color: ${channel_color_dict[channel]};}</style>`).appendTo('head');
    }
    option_html += `
        <div class="graph-legend-noresult-found" id="graph_legend_noresult_found"
            style="display: none;">No result found</div>
    `
    $("#channel_analytics_options").html(option_html)
}


function update_channel_analytics() {
    channel_usage_analytics_card && channel_usage_analytics_card.destroy()

    const checked_channels = $("#channel_analytics_options input:checked")

    let channel_list = [];
    let message_count_list = [];
    let color_list = []

    for (const elm of checked_channels) {
        const channel = elm.value
        channel_list.push(channel);
        message_count_list.push(channel_analytics_response["channel_dict"][channel]);
        color_list.push(channel_color_dict[channel])
    }

    var options = {
        series: message_count_list,
        labels: channel_list,
        colors: color_list,
    
        chart: {
            width: '100%',
            height: '75%',
            type: 'donut',
        },
    
        dataLabels: {
            enabled: false
        },
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: 200
                },
                legend: {
                    show: false
                }
            }
        }],
        legend: {
            position: 'right',
            offsetY: 0,
            height: 230,
            show: false,
    
        }
    };
    
    channel_usage_analytics_card = new ApexCharts(document.querySelector("#channel_usage_analytics_graph"), options);
    channel_usage_analytics_card.render();
}


function load_channel_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel();
        category_name = get_current_default_category();
        selected_language = get_current_default_language();

        bot_pk = get_selected_bot_id();
        var filter = $("input[name='channel-analytics-frequency']:checked").val();
        start_date = document.getElementById("channel-analytics-start-date").value;
        end_date = document.getElementById("channel-analytics-end-date").value;
        if (start_date > end_date) {
            showToast("Start Date should be smaller than End Date");
            document.getElementById("channel-analytics-start-date").value = $("#channel-analytics-start-date").attr("current_applied_date");
            document.getElementById("channel-analytics-end-date").value = $("#channel-analytics-end-date").attr("current_applied_date");
            return;
        }
        $("#channel-analytics-start-date").attr("current_applied_date", start_date)
        $("#channel-analytics-end-date").attr("current_applied_date", end_date)
        channel_usage_analytics_card && channel_usage_analytics_card.destroy()
        $("#channel-analytics-div").hide()
        $("#no-channel-analytics-div").hide()
        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            channel: channel_value,
            category_name: category_name,
            filter: filter,
            selected_language: selected_language,
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string;
        xhttp.open("POST", "/chat/get-channel-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (start_date == end_date) {
                $("#channel-analytics-range").html(`<span></span> ${convert_date_format(start_date)}`)
            } else {
                $("#channel-analytics-range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
            }
            $("#no-channel-analytics-div").css("display", "flex")
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                channel_analytics_response = response
                if (response["status"] == 200) {
                    if (filter == "Users") {
                        document.getElementsByClassName("channel-subhead")[0].innerHTML = "(Number Of Users)";
                    } else if (filter == "Messages") {
                        document.getElementsByClassName("channel-subhead")[0].innerHTML = "(Number Of Messages)";
                    }
                    channel_list = [];
                    message_count_list = [];
                    for (var channel in response["channel_dict"]) {
                        channel_list.push(channel);
                        message_count_list.push(response["channel_dict"][channel]);
                    }

                    channel_color_dict = getColorlistforchannel(channel_list)

                    label = "Channel Usage (" + response["start_date"] + " to " + response["end_date"] + ")";

                    if (message_count_list.every(function(elm) {return elm == 0})) {
                        $("#no-channel-analytics-div").css("display", "flex")
                        $("#channel-analytics-div").hide()
                        return
                    }

                    $("#no-channel-analytics-div").hide()
                    $("#channel-analytics-div").css("display", "flex")

                    var options = {
                        series: message_count_list,
                        labels: channel_list,
                        colors: Object.values(channel_color_dict),
                    
                        chart: {
                            width: '100%',
                            height: '75%',
                            type: 'donut',
                        },
                    
                        dataLabels: {
                            enabled: false
                        },
                        responsive: [{
                            breakpoint: 480,
                            options: {
                                chart: {
                                    width: 200
                                },
                                legend: {
                                    show: false
                                }
                            }
                        }],
                        legend: {
                            position: 'right',
                            offsetY: 0,
                            height: 230,
                            show: false,
                    
                        }
                    };
                    
                    channel_usage_analytics_card = new ApexCharts(document.querySelector("#channel_usage_analytics_graph"), options);
                    channel_usage_analytics_card.render();

                    create_channel_analytics_options()

                    resolve();
                }
            }
        }
        resolve();
        xhttp.send(params);
    })
}

function load_user_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        selected_language = get_current_default_language()
        // reset_charts();

        bot_pk = get_selected_bot_id();
        filter_type = $("input[name='user-analytics-frequency']:checked").val();
        user_analytics_filter = filter_type
        start_date = document.getElementById("user-analytics-start-date").value;
        end_date = document.getElementById("user-analytics-end-date").value;
        if (start_date > end_date) {
            showToast("Start Date should be smaller than End Date", 2000);
            document.getElementById("user-analytics-start-date").value = $("#user-analytics-start-date").attr("current_applied_date");
            document.getElementById("user-analytics-end-date").value = $("#user-analytics-end-date").attr("current_applied_date");
            return;
        }
        $("#user-analytics-start-date").attr("current_applied_date", start_date)
        $("#user-analytics-end-date").attr("current_applied_date", end_date)
        user_analytics_card && user_analytics_card.destroy()
        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            filter_type: filter_type,
            channel: channel_value,
            selected_language: selected_language
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string;
        xhttp.open("POST", "/chat/get-user-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (start_date == end_date) {
                $("#user-analytics-range").html(`<span></span> ${convert_date_format(start_date)}`)
            } else {
                $("#user-analytics-range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
            }
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    label_list = [];
                    no_users_list = [];
                    no_of_sessions_list = [];
                    no_of_business_initiated_list = [];

                    average_users = []
                    average_users_point_radius = []
                    var sum_total_users = 0;
                    total_days = response["total_days"]

                    //no_repeated_users_list = [];
                    min_users = 1;
                    max_users = 1;
                    for (var i = 0; i < response["user_analytics_list"].length; i++) {
                        var dateSplit = response["user_analytics_list"][i]["label"].split("-");
                        let objDate;    
                        if (dateSplit.length !== 3) {
                            if (filter_type == 3) {
                                objDate = dateSplit[0] + " " + dateSplit[1].slice(2)
                            } else {
                                let first_range = dateSplit[0].split("/")
                                let first_date = new Date(first_range.reverse().join("/"))
                                let second_range = dateSplit[1].split("/")
                                let second_date = new Date(second_range.reverse().join("/"))
                                objDate = first_date.toLocaleString("default", {month: "short"}) + " " + first_date.getDate() + " - " + second_date.toLocaleString("default", {month: "short"}) + " " + second_date.getDate()
                            }
                        } else {
                            if (response["user_analytics_list"].length <= 3) {
                                objDate = dateSplit[1] + " " + dateSplit[0] + " '" + dateSplit[2]
                            } else {
                                objDate = new Date(dateSplit[1] + " " + dateSplit[0] + ", " + dateSplit[2]).getTime();
                            }
                        } 
                        label_list.push(objDate);
                        count = response["user_analytics_list"][i]["count"];
                        session_count = response["user_analytics_list"][i]["session_count"]
                        business_initiated_count = response["user_analytics_list"][i]["business_initiated_sessions"]
                        //repeat_count = response["user_analytics_list"][i]["repeat_count"];

                        if (count != null)
                            sum_total_users = sum_total_users + parseInt(count.toString())

                        no_users_list.push(count);
                        if(channel_value == 'WhatsApp') {
                            session_count = session_count - business_initiated_count
                        }
                        no_of_sessions_list.push(session_count)
                        no_of_business_initiated_list.push(business_initiated_count)
                        //no_repeated_users_list.push(repeat_count);
                        //min_users = Math.min(min_users, count, repeat_count);
                        //max_users = Math.max(max_users, count, repeat_count);
                    }

                    if (parseInt(total_days) != 0) {
                        for (var days = 0; days < response["user_analytics_list"].length; days++) {
                            average_users.push(Math.round(sum_total_users / parseInt(total_days)))

                            if (days == response["user_analytics_list"].length - 1 || days == 0) {
                                average_users_point_radius.push(2)
                            } else {
                                average_users_point_radius.push(0)
                            }
                        }
                    }

                    min_step_size = Math.max(5, Math.ceil((max_users - min_users) / 5));
                    // label = "Number of users";

                    let chart_category;
                    let tick_amount = undefined;

                    if (label_list.length > 3) {
                        chart_category = "datetime"
                    } else {
                        chart_category = "category"
                    }

                    if (dateSplit.length !== 3) {
                        chart_category = "category"
                        tick_amount = 5
                    }
                    
                    var options = {
                        series: [{
                                name: "Number of total users",
                                data: no_users_list
                            },
                            {
                                name: "Average Number of users",
                                data: average_users
                            },
                            {
                                name: "Number of unique sessions",
                                data: no_of_sessions_list
                            }
                        ],
                        colors: ['#3751FF', '#37D4F6', '#FF9040', '#A4C639'],
                        chart: {
                            height: 350,
                            type: 'line',
                            zoom: {
                                enabled: false
                            },
                            toolbar: {
                                show: false,
                            }
                        },
                        grid: {
                            show: true,
                            borderColor: '#f1f1f1',
                            strokeDashArray: 0,
                            position: 'back',
                            xaxis: {
                                lines: {
                                    show: true
                                }
                            },
                            yaxis: {
                                lines: {
                                    show: true
                                },
                            },
                            row: {
                                colors: '#C4C4C4',
                                opacity: 0
                            },
                            column: {
                                colors: '#C4C4C4',
                                opacity: 0
                            },
                            padding: {
                                top: 0,
                                right: 0,
                                bottom: 0,
                                left: 10
                            },
                        },
                        dataLabels: {
                            enabled: false
                        },
                        stroke: {
                            width: 2,
                            curve: "smooth",
                        },
                        title: {
                            enabled: false
                        },
                        xaxis: {
                            categories: label_list,
                            type: chart_category,
                            labels: {
                                datetimeUTC: false,
                                datetimeFormatter: {
                                    day: "dd MMM 'yy",
                                },
                                rotate: 0,
                            },
                            tickAmount: tick_amount,
                        },
                        yaxis: {
                            style: {
                                marginRighnt: '20px',
                            },
                            labels: {
                            formatter: function(val) {
                                if (val != undefined)
                                return val.toFixed(0)
                            }
                            },
                        }
                    };

                    if(channel_value=='WhatsApp') {
                        options['series'][2] = {name: "Business Initiated Conversation", data: no_of_business_initiated_list}
                        options['series'].push({name: "Customer Initiated Conversation", data: no_of_sessions_list})
                    }
                    
                    user_analytics_card = new ApexCharts(document.querySelector("#user_analytics_graph"), options);
                    user_analytics_card.render();
                    
                    resolve();
                }
            }
        }
        xhttp.send(params);
    })
}


function load_message_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        category_name = get_current_default_category()
        selected_language = get_current_default_language()
        // reset_charts();
        bot_pk = get_selected_bot_id();
        filter_type = $("input[name='message-analytics-frequency']:checked").val();
        message_analytics_filter = filter_type
        start_date = document.getElementById("message-analytics-start-date").value;
        end_date = document.getElementById("message-analytics-end-date").value;
        if (start_date > end_date) {
            M.toast({
                "html": "Start Date should be smaller than End Date"
            });
            document.getElementById("message-analytics-start-date").value = $("#message-analytics-start-date").attr("current_applied_date");
            document.getElementById("message-analytics-end-date").value = $("#message-analytics-end-date").attr("current_applied_date");
            return;
        }
        if (new Date().setHours(0, 0, 0, 0) < new Date(end_date).setHours(0, 0, 0, 0)) {
            M.toast({
                "html": "End Date should not be future date"
            });
            return
        }
        $("#message-analytics-start-date").attr("current_applied_date", start_date)
        $("#message-analytics-end-date").attr("current_applied_date", end_date)
        message_analytics_card && message_analytics_card.destroy()

        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            filter_type: filter_type,
            channel: channel_value,
            category_name: category_name,
            selected_language: selected_language
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string;
        xhttp.open("POST", "/chat/get-message-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (start_date == end_date) {
                $("#message-analytics-range").html(`<span></span> ${convert_date_format(start_date)}`)
            } else {
                $("#message-analytics-range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
            }
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    label_list = [];
                    total_messages_list = [];
                    total_answered_messages_list = [];
                    total_unanswered_messages_list = [];
                    total_intuitive_messages_list = [];
                    predicted_messages_no_list = [];
                    average_messages = []
                    // false_positive_messages_list = []
                    var sum_total_messages = 0;

                    percentage_change = "None"
                    percentage_change_type = ""
                    total_days = response["total_days"]

                    for (var i = 0; i < response["message_analytics_list"].length; i++) {
                        var dateSplit = response["message_analytics_list"][i]["label"].split("-");
                        let objDate;
                        if (dateSplit.length !== 3) {
                            if (response.percentage_change_type === "Since last 30 days") {
                                objDate = dateSplit[0] + " " + dateSplit[1].slice(2)
                            } else {
                                let first_range = dateSplit[0].split("/")
                                let first_date = new Date(first_range.reverse().join("/"))
                                let second_range = dateSplit[1].split("/")
                                let second_date = new Date(second_range.reverse().join("/"))
                                objDate = first_date.toLocaleString("default", {month: "short"}) + " " + first_date.getDate() + " - " + second_date.toLocaleString("default", {month: "short"}) + " " + second_date.getDate()
                            }
                        } else {
                            if (response["message_analytics_list"].length <= 3) {
                                objDate = dateSplit[1] + " " + dateSplit[0] + " '" + dateSplit[2];
                            } else {
                                objDate = new Date(dateSplit[1] + " " + dateSplit[0] + ", " + dateSplit[2]).getTime();
                            }
                        }   
                        label_list.push(objDate);
                        total_messages = response["message_analytics_list"][i]["total_messages"];
                        total_answered_messages = response["message_analytics_list"][i]["total_answered_messages"];
                        total_unanswered_messages = response["message_analytics_list"][i]["total_unanswered_messages"];
                        total_intuitive_messages= response["message_analytics_list"][i]["total_intuitive_messages"];
                        predicted_messages_no = response["message_analytics_list"][i]["predicted_messages_no"];
                        // false_positive_messages = response["message_analytics_list"][i]["false_positive_messages"];

                        if (total_messages != null)
                            sum_total_messages = sum_total_messages + parseInt(total_messages)

                        total_messages_list.push(total_messages);
                        total_answered_messages_list.push(total_answered_messages);
                        total_unanswered_messages_list.push(total_unanswered_messages);
                        total_intuitive_messages_list.push(total_intuitive_messages);
                        predicted_messages_no_list.push(predicted_messages_no);
                        // false_positive_messages_list.push(false_positive_messages)
                    }

                    if (parseInt(total_days) != 0) {
                        for (var days = 0; days < response["message_analytics_list"].length; days++) {

                            average_messages.push(Math.round(sum_total_messages / parseInt(total_days)))

                        }
                    }

                    percentage_change = response["percentage_change"];
                    percentage_change_type = response["percentage_change_type"];
                    if (percentage_change == "None") {
                        document.getElementById('message-analytics-percentage-change').innerHTML = ""
                    } else if (percentage_change < 0) {
                        document.getElementById('message-analytics-percentage-change').innerHTML = '<div style="display: inline-block;color: #F56565;"> ' + Math.abs(percentage_change) + '% <i class="material-icons" style="transform: rotate(90deg); position: relative; top: 1px;vertical-align: sub; font-size:large">play_arrow</i></div> ' + percentage_change_type
                    } else if (percentage_change > 0) {
                        document.getElementById('message-analytics-percentage-change').innerHTML = '<div style="display: inline-block;color: green;"> ' + Math.abs(percentage_change) + '% <i class="material-icons" style="transform: rotate(-90deg); position: relative; top: 2px;vertical-align: sub; font-size:large;">play_arrow</i></div> ' + percentage_change_type
                    } else {
                        document.getElementById('message-analytics-percentage-change').innerHTML = '<div style="display: inline-block;"> ' + Math.abs(percentage_change) + '%</div> ' + percentage_change_type
                    }         

                    let chart_category;
                    let tick_amount = undefined;

                    if (label_list.length > 3) {
                        chart_category = "datetime"
                    } else {
                        chart_category = "category"
                    }

                    if (dateSplit.length !== 3) {
                        chart_category = "category"
                        tick_amount = 5
                    }

                    var options = {
                        series: [{
                                name: "Total",
                                data: total_messages_list
                            },
                            {
                                name: "Answered",
                                data: total_answered_messages_list
                            },
                            {
                                name: "Unanswered",
                                data: total_unanswered_messages_list
                            },
                            {
                                name: "Intuitive",
                                data: total_intuitive_messages_list
                            },
                            {
                                name: "Projected",
                                data: predicted_messages_no_list
                            },
                            {
                                name: "Average Messages",
                                data: average_messages
                            },
                            // {
                            //     name: "False Positive",
                            //     data: false_positive_messages_list
                            // }
                        ],
                        colors: ['#3751FF', '#10B981', '#E53E3E', '#37D4F6', '#9B51E0', '#FCD34D'],
                        chart: {
                            height: 350,
                            type: 'line',
                            zoom: {
                                enabled: false
                            },
                            toolbar: {
                                show: false,
                            }
                        },
                        dataLabels: {
                            enabled: false
                        },
                        stroke: {
                            width: 2,
                            curve: "smooth",
                        },
                        title: {
                            show: false
                        },
                        grid: {
                            show: true,
                            borderColor: '#f1f1f1',
                            strokeDashArray: 0,
                            position: 'back',
                            xaxis: {
                                lines: {
                                    show: true
                                }
                            },
                            yaxis: {
                                lines: {
                                    show: true
                                },
                            },
                            row: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            column: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            padding: {
                                top: 0,
                                right: 0,
                                bottom: 0,
                                left: 10
                            },
                        },
                    
                        xaxis: {
                            categories: label_list,
                            type: chart_category,
                            labels: {
                                datetimeUTC: false,
                                datetimeFormatter: {
                                    day: "dd MMM 'yy",
                                },
                                rotate: 0,
                            },
                            tickAmount: tick_amount,
                        },
                        yaxis: {
                            style: {
                                marginRighnt: '20px',
                            },
                            labels: {
                            formatter: function(val) {
                                if (val != undefined)
                                return val.toFixed(0)
                            }
                            },
                        }
                    };

                    message_analytics_card = new ApexCharts(document.querySelector("#message-analytics-graph"), options);
                    message_analytics_card.render();

                    resolve();
                }
            }
        }
        xhttp.send(params);
    })
}


function load_device_specific_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        
        // Adding this below lines because device specific analytics is Web channel specific.
        if (channel_value.toLowerCase().trim() == "all"){
            channel_value = "Web";
        }
        category_name = get_current_default_category()
        selected_language = get_current_default_language()
        bot_pk = get_selected_bot_id();

        filter_type = $("input[name='device-analytics-frequency']:checked").val();
        device_analytics_filter = filter_type
        start_date = document.getElementById("device-analytics-start-date").value;
        end_date = document.getElementById("device-analytics-end-date").value;
        if (start_date > end_date) {
            M.toast({
                "html": "Start Date should be smaller than End Date"
            });
            document.getElementById("device-analytics-start-date").value = $("#device-analytics-start-date").attr("current_applied_date");
            document.getElementById("device-analytics-end-date").value = $("#device-analytics-end-date").attr("current_applied_date");
            return;
        }
        if (new Date().setHours(0, 0, 0, 0) < new Date(end_date).setHours(0, 0, 0, 0)) {
            M.toast({
                "html": "End Date should not be future date"
            });
            return
        }
        $("#device-analytics-start-date").attr("current_applied_date", start_date)
        $("#device-analytics-end-date").attr("current_applied_date", end_date)
        $("#no-device-specific-analytics-div").hide()
        $("#device-specific-analytics-graph").hide()

        if (device_specific_analytics_card != undefined) {
            device_specific_analytics_card && device_specific_analytics_card.destroy()
        }

        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            filter_type: filter_type,
            channel: channel_value,
            category_name: category_name,
            selected_language: selected_language
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string;

        xhttp.open("POST", "/chat/get-device-specific-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            if (start_date == end_date) {
                $("#device-analytics-range").html(`<span></span> ${convert_date_format(start_date)}`)
            } else {
                $("#device-analytics-range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
            }
            $("#no-device-specific-analytics-div").css("display", "flex")
            if (this.readyState == 4 && this.status == 200) {
                
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    label_list = [];

                    total_answered_messages_desktop_list = []
                    total_answered_messages_mobile_list = []
                    total_messages_desktop_list = []
                    total_messages_mobile_list = []
                    total_unanswered_messages_desktop_list = []
                    total_unanswered_messages_mobile_list = []
                    total_intuitive_messages_desktop_list = []
                    total_intuitive_messages_mobile_list = []
                    total_users_mobile_list = []
                    total_users_desktop_list = []
                    
                    total_days = response["total_days"]

                    for (var i = 0; i < response["device_specific_analytics_list"].length; i++) {
                        var dateSplit = response["device_specific_analytics_list"][i]["label"].split("-");
                        let objDate;
                        if (dateSplit.length !== 3) {
                            if (filter_type === "3") {
                                objDate = dateSplit[0] + " " + dateSplit[1].slice(2)
                            } else {
                                let first_range = dateSplit[0].split("/")
                                let first_date = new Date(first_range.reverse().join("/"))
                                let second_range = dateSplit[1].split("/")
                                let second_date = new Date(second_range.reverse().join("/"))
                                objDate = first_date.toLocaleString("default", {month: "short"}) + " " + first_date.getDate() + " - " + second_date.toLocaleString("default", {month: "short"}) + " " + second_date.getDate()
                            }
                        } else {
                            if (response["device_specific_analytics_list"].length <= 3) {
                                objDate = dateSplit[1] + " " + dateSplit[0] + " '" + dateSplit[2];
                            } else {
                                objDate = new Date(dateSplit[1] + " " + dateSplit[0] + ", " + dateSplit[2]).getTime();
                            }
                        }        
                        label_list.push(objDate);
                        try {
                            total_answered_messages_desktop_list.push(response["device_specific_analytics_list"][i].total_answered_messages_desktop || 0);
                            total_answered_messages_mobile_list.push(response["device_specific_analytics_list"][i].total_answered_messages_mobile || 0);
                            total_messages_desktop_list.push(response["device_specific_analytics_list"][i].total_messages_desktop || 0);
                            total_messages_mobile_list.push(response["device_specific_analytics_list"][i].total_messages_mobile || 0);
                            total_unanswered_messages_desktop_list.push(response["device_specific_analytics_list"][i].total_unanswered_messages_desktop || 0);
                            total_unanswered_messages_mobile_list.push(response["device_specific_analytics_list"][i].total_unanswered_messages_mobile || 0);                            total_users_mobile_list.push(response["device_specific_analytics_list"][i].total_users_mobile || 0);
                            total_intuitive_messages_desktop_list.push(response["device_specific_analytics_list"][i].total_intuitive_messages_desktop || 0);
                            total_intuitive_messages_mobile_list.push(response["device_specific_analytics_list"][i].total_intuitive_messages_mobile || 0);

                            total_users_desktop_list.push(response["device_specific_analytics_list"][i].total_users_desktop || 0)
                        } catch(err) {
                            console.log(err)
                        }
                        
                    }

                    let chart_category;
                    let tick_amount = undefined;

                    if (label_list.length > 3) {
                        chart_category = "datetime"
                    } else {
                        chart_category = "category"
                    }

                    if (dateSplit.length !== 3) {
                        chart_category = "category"
                        tick_amount = 5
                    }

                    $("#no-device-specific-analytics-div").hide()
                    $("#device-specific-analytics-graph").css("display", "flex")

                    var options = {
                        series: [
                            {
                                name: "Mobile Users",
                                data: total_users_mobile_list
                            },
                            {
                                name: "Desktop Users",
                                data: total_users_desktop_list
                            },
                            {
                                name: "Queries Asked(Mobile)",
                                data: total_messages_mobile_list
                            },
                            {
                                name: "Queries Asked(Desktop)",
                                data: total_messages_desktop_list
                            },
                            
                            {
                                name: "Queries Answered(Mobile)",
                                data: total_answered_messages_mobile_list
                            },
                            {
                                name: "Queries Answered(Desktop)",
                                data: total_answered_messages_desktop_list
                            },
                            {
                                name: "Queries Unanswered(Mobile)",
                                data: total_unanswered_messages_mobile_list
                            },
                            {
                                name: "Queries Unanswered(Desktop)",
                                data: total_unanswered_messages_desktop_list
                            },
                            {
                                name: "Queries Intuitive(Mobile)",
                                data: total_intuitive_messages_mobile_list
                            },
                            {
                                name: "Queries Intuitive(Desktop)",
                                data: total_intuitive_messages_desktop_list
                            },
                        ],
                        colors: ['#3751FF', '#FF9040', '#37D4F6', '#9B51E0', '#A70303', '#DAC400', '#45FB18', '#37AB00'],
                        chart: {
                            height: 390,
                            type: 'line',
                            zoom: {
                                enabled: false
                            },
                            toolbar: {
                                show: false,
                            }
                        },
                        legend: {
                            show:true,
                            position: 'bottom',
                            floating: false,
                            verticalAlign: 'bottom',
                            align:'center',
                            horizontalAlign: 'center', 
                            offsetX: 0,
                            offsetY:10,
                          },
                        dataLabels: {
                            enabled: false
                        },
                        stroke: {
                            width: 2,
                            curve: "smooth",
                        },
                        title: {
                            show: false
                        },
                        grid: {
                            show: true,
                            borderColor: '#f1f1f1',
                            strokeDashArray: 0,
                            position: 'back',
                            xaxis: {
                                lines: {
                                    show: true
                                }
                            },
                            yaxis: {
                                lines: {
                                    show: true
                                },
                            },
                            row: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            column: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            padding: {
                                top: 0,
                                right: 0,
                                bottom: 0,
                                left: 20
                            },
                        },
                    
                        xaxis: {
                            categories: label_list,
                            type: chart_category,
                            labels: {
                                datetimeUTC: false,
                                datetimeFormatter: {
                                    day: "dd MMM 'yy",
                                },
                                rotate: 0,
                            },
                            tickAmount: tick_amount,
                        },
                        yaxis: {
                            style: {
                                marginRighnt: '20px',
                            },
                            labels: {
                            formatter: function(val) {
                                if (val != undefined)
                                return val.toFixed(0)
                            }
                            },
                        }
                    };

                    device_specific_analytics_card = new ApexCharts(document.querySelector("#device-specific-analytics-graph"), options);
                    device_specific_analytics_card.render();

                } else if(response["status"] == 422) {
                    
                    $("#no-device-specific-analytics-div").css("display", "flex")
                    
                }
                resolve();
            }
        }
        xhttp.send(params);
    })
}


async function capture_screenshot(element, bot_name) {

    element.style.display = "none";
    M.toast({
        "html": "Exporting"
    });
    const canvas_ele = document.getElementById("capture-html-to-canvas");
    canvas_ele.style.backgroundColor = "#edf1f7";

    html2canvas(canvas_ele,{
        scale: 2, background: '#FFFFFF',
        height: canvas_ele.scrollHeight
        })
    .then(function (canvas) {
        var a = document.createElement('a');
        // toDataURL defaults to png, so we need to request a jpeg, then convert for file download.
        a.href = canvas.toDataURL("image/jpeg");
        a.download = bot_name + '_screenshot.jpg';
        a.click();
        canvas_ele.style.backgroundColor = "transparent";
    });

    element.style.display = "flex";
}

function download_easychat_nps_excel() {

    bot_pk = get_selected_bot_id();
    var json_string = JSON.stringify({
        bot_pk: bot_pk
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/export-easychat-nps-excel/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            var file_url = response["file_url"];
            if (response["status"] == 200 && response["file_url"] != null) {
                window.open(file_url);
            } else {
                M.toast({
                    "html": "Internal server error please report error."
                });
            }
        }
    }
    xhttp.send(params);
}

// function export_most_frequent_questions(){
//     bot_pk = get_selected_bot_id();
//     var json_string = JSON.stringify({
//         bot_pk: bot_pk,
//         reverse: true,
//     });
//     json_string = EncryptVariable(json_string);
//     json_string = encodeURIComponent(json_string);
//     var xhttp = new XMLHttpRequest();
//     var params = 'json_string='+json_string
//     xhttp.open("POST", "/chat/export-frequent-intent/", true);
//     xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             response = JSON.parse(this.responseText);
//             response = custom_decrypt(response)
//             response = JSON.parse(response);
//             var file_url = response["file_url"];
//             if(response["status"]==200 && response["file_url"] != null){
//                 window.open(file_url);
//             }else{
//                 M.toast({
//                     "html": "Internal server error please report error."
//                 });
//             }
//         }
//     }
//     xhttp.send(params);
// }

// function export_least_frequent_questions(){
//     bot_pk = get_selected_bot_id();
//     var json_string = JSON.stringify({
//         bot_pk: bot_pk,
//         reverse: false,
//     });
//     json_string = EncryptVariable(json_string);
//     json_string = encodeURIComponent(json_string);
//     var xhttp = new XMLHttpRequest();
//     var params = 'json_string='+json_string
//     xhttp.open("POST", "/chat/export-frequent-intent/", true);
//     xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             response = JSON.parse(this.responseText);
//             response = custom_decrypt(response)
//             response = JSON.parse(response);
//             var file_url = response["file_url"];
//             if(response["status"]==200 && response["file_url"] != null){
//                 window.open(file_url);
//             }else{
//                 M.toast({
//                     "html": "Internal server error please report error."
//                 });
//             }
//         }
//     }
//     xhttp.send(params);
// }

function export_most_used_form_assist_intent(open_modal) {

    bot_pk = get_selected_bot_id();
    selected_language = get_current_default_language()
    dropdown_language = get_url_vars()["selected_language"]
    var start_date = document.getElementById("form-assist-analytics-start-date").value;
    var end_date = document.getElementById("form-assist-analytics-end-date").value;
    email_id = window.user_email

    let ed_date = new Date(end_date)
    let st_date = new Date(start_date)
    diff_in_no_of_days = (ed_date.getTime() - st_date.getTime()) / (1000 * 3600 * 24)// 1000 miliseconds in 1 secon 3600 second in 1 hour 24 hours in one day

    if (diff_in_no_of_days > 30) {
        email_id = document.getElementById("export-data-email-form-assist").value

        if (!open_modal) {
            $('#modal-email-for-export-form-assist').modal('open');
            return
        }
        if (!validate_email(email_id)) {
            M.toast({"html": 'Please enter valid Email address'}, 4000, "rounded");
            return
        }
    }

    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        start_date: start_date,
        end_date: end_date,
        selected_language: selected_language,
        dropdown_language: dropdown_language,
        email_id: email_id,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/export-form-assist-intent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            var file_url = response["file_url"];
            if (response["status"] == 200) {
                console.log(response)
                if ("file_url" in response) {
                    var file_url = response["file_url"];
                    window.open(file_url);
                } else if ("email_id" in response) {
                    var email_id = response["email_id"];
                    setTimeout(function (e) {
                        M.toast({
                            "html": "You will receive the mail of the requested data soon on this address: " + email_id
                        });
                    }, 1000)
                }
            } else {
                M.toast({
                    "html": "Internal server error please report error."
                });
            }
        }
    }
    xhttp.send(params);
}

function export_unanswered_questions() {

    bot_pk = get_selected_bot_id();
    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        reverse: false,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/export-unanswered-intent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            var file_url = response["file_url"];
            if (response["status"] == 200 && response["file_url"] != null) {
                window.open(file_url);
            } else {
                M.toast({
                    "html": "Internal server error please report error."
                });
            }
        }
    }
    xhttp.send(params);
}

function load_session_analytics(filter_type = "global") {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        selected_language = get_current_default_language()

        if (filter_type == "global" || filter_type == "avg_session_analytics") {
            start_date = document.getElementById("session-analytics-start-date").value;
            end_date = document.getElementById("session-analytics-end-date").value;
        } else if (filter_type == "global" || filter_type == "bot_accuracy") {
            start_date = document.getElementById("bot-accuracy-start-date").value;
            end_date = document.getElementById("bot-accuracy-end-date").value;
        }

        if (start_date > end_date) {
            showToast("Start Date should be smaller than End Date", 2000);
            if (filter_type == "global" || filter_type == "avg_session_analytics") {
                document.getElementById("session-analytics-start-date").value = $("#session-analytics-start-date").attr("current_applied_date");
                document.getElementById("session-analytics-end-date").value = $("#session-analytics-end-date").attr("current_applied_date");
            } else if (filter_type == "global" || filter_type == "bot_accuracy") {
                document.getElementById("bot-accuracy-start-date").value = $("#bot-accuracy-start-date").attr("current_applied_date");
                document.getElementById("bot-accuracy-end-date").value = $("#bot-accuracy-end-date").attr("current_applied_date");
            }
            return;
        }

        // if (channel_value == 'All' || channel_value == 'Web') {
        if (filter_type == "global" || filter_type == "avg_session_analytics") {
            document.getElementById('no-session-analytics-div').style.visibility = 'hidden'
            document.getElementById('session-analytics-div').style.visibility = 'hidden'
            $("#session-analytics-start-date").attr("current_applied_date", start_date)
            $("#session-analytics-end-date").attr("current_applied_date", end_date)
        }
        if (filter_type == "global" || filter_type == "bot_accuracy") {
            document.getElementById('no-bot-accuracy-div').style.visibility = "hidden"
            document.getElementById('bot-accuracy-div').style.visibility = "hidden"
            document.getElementById('no-bot-accuracy-div').style.display = 'none'
            document.getElementById('bot-accuracy-div').style.display = 'block'
            $("#bot-accuracy-start-date").attr("current_applied_date", start_date)
            $("#bot-accuracy-end-date").attr("current_applied_date", end_date)
        }
        bot_pk = get_selected_bot_id();

        // document.getElementById("percentage-of-likes").innerHTML="...";
        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            channel_name: channel_value,
            filter_type: filter_type,
            selected_language: selected_language
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string
        xhttp.open("POST", "/chat/get-session-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            document.getElementById('no-bot-accuracy-div').style.visibility = "visible"
            document.getElementById('bot-accuracy-div').style.visibility = "visible"
            document.getElementById('no-session-analytics-div').style.visibility = 'visible'
            document.getElementById('session-analytics-div').style.visibility = 'visible'
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    if (filter_type == "global" || filter_type == "avg_session_analytics") {
                        document.getElementById("ave-no-of-messages-per-session").innerHTML = "...";
                        document.getElementById("ave-session-time").innerHTML = "...";
                        document.getElementById("no-of-likes").innerHTML = "...";
                        $("#no-of-unique-sessions").html("...")
                        document.getElementById("ave-no-of-messages-per-session").innerHTML = "&nbsp;" + response["ave_number_of_messages_per_session"];
                        document.getElementById("ave-session-time").innerHTML = "&nbsp;" + response["ave_time_spent_time_user"]

                        total_messages = response["total_messages"];
                        no_of_likes = response["no_of_likes"];
                        no_of_dislikes = response["no_of_dislikes"];
                        percentage_likes = 0;

                        if (total_messages != 0) {
                            percentage_likes = Math.round(((total_messages - no_of_dislikes) * 100) / total_messages);
                        }
                        if (no_of_likes == 0) {
                            percentage_likes = 0;
                        }
                        document.getElementById("no-of-likes").innerHTML = "&nbsp;" + response["no_of_likes"];
                        // document.getElementById("percentage-of-likes").innerHTML="&nbsp;"+percentage_likes +"%";
                        // document.getElementById("session-time-range").innerHTML = response["start_date"] + " to " + response["end_date"];

                        $("#no-of-unique-sessions").html("&nbsp;" + response["no_of_unique_sessions"])

                        if (total_messages == 0) {
                            document.getElementById('no-session-analytics-div').style.display = 'flex'
                            document.getElementById('session-analytics-div').style.display = 'none'
                        } else {
                            document.getElementById('no-session-analytics-div').style.display = 'none'
                            document.getElementById('session-analytics-div').style.display = 'block'
                        }
                    }

                    if (filter_type == "global" || filter_type == "bot_accuracy") {
                        bot_accuracy = response["bot_accuracy"]
                        if (bot_accuracy.toString().indexOf("No") != -1) {
                            document.getElementById('no-bot-accuracy-div').style.display = 'flex'
                            document.getElementById('bot-accuracy-div').style.display = 'none'
                        } else {
                            document.getElementById("bot-accuracy-value").innerHTML = bot_accuracy + "%"
                        }
                    }

                    resolve();
                }
            }
        }
        xhttp.send(params);
        // }
        // else {
        //     document.getElementById('no-session-analytics-div').style.display = 'block'
        //     document.getElementById('session-analytics-div').style.display = 'none'

        //     resolve();
        // }
    })
}

const search_form_assist_intents = debounce(function() {
    load_form_assist_analytics(true)
})

function load_form_assist_analytics(filter_flag) {

    return new Promise(function (resolve, reject) {
        bot_pk = get_selected_bot_id();
        if (filter_flag == 'true') {
            form_assist_intent_page = 1
        } else {
            form_assist_intent_page += 1
        }
        $("#empty-search").hide()
        $("#no-form-assist-div").hide()
        $("#no-form-assist-intents-div").hide()
        $("#form-assist-intents-div").hide()
        start_date = document.getElementById("form-assist-analytics-start-date").value;
        end_date = document.getElementById("form-assist-analytics-end-date").value;
        if (start_date > end_date) {
            M.toast({
                "html": "Start Date should be smaller than End Date"
            });
            document.getElementById("form-assist-analytics-start-date").value = $("#form-assist-analytics-start-date").attr("current_applied_date");
            document.getElementById("form-assist-analytics-end-date").value = $("#form-assist-analytics-end-date").attr("current_applied_date");
            return;
        }
        $("#form-assist-analytics-start-date").attr("current_applied_date", start_date)
        $("#form-assist-analytics-end-date").attr("current_applied_date", end_date)
        selected_language = get_current_default_language();
        dropdown_language = get_url_vars()["selected_language"]
        let search_term = $("#form_assist_intents_search").val()
        if (typeof dropdown_language == 'undefined'){
            dropdown_language = "en"
        }
        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            form_assist_intent_page: form_assist_intent_page,
            start_date: start_date,
            end_date: end_date,
            selected_language: selected_language,
            dropdown_language: dropdown_language,
            search: search_term,
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string
        xhttp.open("POST", "/chat/get-form-assist-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.onreadystatechange = function () {
            $("#no-form-assist-intents-div").show()
            if (this.readyState == 4 && (this.status == 200 || this.status==300)) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);

                if (response["status"] == 200 || response["status"] == 300) {
                    if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                        document.getElementById("form-assist-intent-used").classList.add("language-right-to-left-wrapper")
                        $("#form-assist-searchbar-div span").addClass("right-to-left-search-span")
                        $("#form-assist-searchbar-div input").addClass("right-to-left-search-input")  
                    } else {
                        document.getElementById("form-assist-intent-used").classList.remove("language-right-to-left-wrapper")
                    }

                    // document.getElementById("form-assist-analytics-div").style.display = 'block';
                    // document.getElementById("form-assist-analytics-div-intent").style.display = 'block';
                    
                    if (form_assist_user_assisted !== response["no-of-users-assisted"] ||
                        form_assist_user_find_helpful !== response["no-user-find-helpful"] ||
                        form_assist_helpful_percentage !== response["form_assist_helpful_percentage"]
                    ) {
                        $("#num-users-assisted").html(response["no-of-users-assisted"])
                        $("#num-user-helpful").html(response["no-user-find-helpful"])
                        $("#assisted-percentage").html(response["form_assist_helpful_percentage"])

                        form_assist_user_assisted = response["no-of-users-assisted"]
                        form_assist_user_find_helpful = response["no-user-find-helpful"]
                        form_assist_helpful_percentage = response["form_assist_helpful_percentage"]
                    }
                    
                    $("#device-specific-analytics-wrapper").css("width", "100%");
                    if (response["intent_data"].length === 0) {
                        $("#form-assist-intents-div").hide()
                        $("#no-form-assist-intents-div").css("display", "flex")
                        return
                    }

                    $("#form-assist-intents-div").show()
                    $("#no-form-assist-intents-div").hide()

                    intent_html = ""
                    intent_name = ""
                    intent_user_assisted = ""

                    for (i = 0; i < 5; i++) {
                        if (i >= response["intent_data"].length) {
                            intent_html += '<li class="easychat-session-analytics-item"></li>'
                            continue
                        }
                        intent_name = sanitize_html(response["intent_data"][i]["intent"])
                        intent_user_assisted = response["intent_data"][i]["user_assisted"]

                        intent_html += `
                            <li class="easychat-session-analytics-item intent-list-item">
                                <div class="easychat-analytics-data-card-content-div">
                                    <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <rect width="24" height="24" rx="4" fill="#EFF2F5" />
                                    </svg>
                                    </div>
                                    <div>
                                        <div class="easychat-analytics-data-card-item-text">
                                            ${intent_name}
                                        </div>
                                        <div class="easychat-analytics-form-assist-value-div"><span>${intent_user_assisted}</span> mes</div>
                                    </div>
                                </div>
                            </li>
                        `
                    }

                    if (response["is_last_page"] == false) {
                        $("#form-assist-intents-right").show()
                    } else {
                        $("#form-assist-intents-right").hide()
                    }

                    if (response["is_single_page"] == false) {
                        if (form_assist_intent_page === 1) {
                            $("#form-assist-intents-left").hide()
                        } else {
                            $("#form-assist-intents-left").show()
                        }
                    } else {
                        $("#form-assist-intents-left").hide()
                    }
                    document.getElementById("form-assist-intent-used").innerHTML = intent_html

                    resolve();
                    if (response["status"]== 300){
                        document.getElementById("translation_api_toast_container").style.display = "flex";
                        setTimeout(api_fail_message_none, 4000);
                    }
                } else if (response["status"] == 301) {
                    document.getElementById("form-assist-analytics-div").style.display = 'none';
                    document.getElementById("form-assist-analytics-div-intent").style.display = 'none';
                    
                    move_device_specific_div_after_nudge()
                    
                    // $("#device-specific-analytics").append("#revised-analytics-row-6")

                    resolve();
                }
            }
        }
        xhttp.send(params);
    })
}

function move_device_specific_div_after_nudge() {
    if ($("#revised-analytics-row-6 #device-specific-analytics-wrapper").length == 0) {
        $("#device-specific-analytics-wrapper").detach().appendTo('#revised-analytics-row-6')
    }
    if (!$("#device-specific-analytics-wrapper").hasClass("easychat-analytics-middle-card-div")) {
        $("#device-specific-analytics-wrapper").addClass("easychat-analytics-middle-card-div")
        $("#nudge-analytics-div-wrapper").removeClass("easychat-analytics-right-side-card-div")
        $("#nudge-analytics-div-wrapper").addClass("easychat-analytics-left-side-card-div")
    }
}


function load_previous_form_assist_analytics() {

    form_assist_intent_page -= 2
    if (form_assist_intent_page < 0){
        form_assist_intent_page = 0
    }
    
    load_form_assist_analytics()
}

function load_intent_wise_category_intent() {

    category_wise_most_frequenct_intent_page = 0
    category_wise_most_frequenct_individual_page = 0
    load_next_category_wise_most_frequenct_intent()
}

const search_category_wise_most_frequenct_intents = debounce(function() {
    load_next_category_wise_most_frequenct_intent(false, true)
})

function load_next_category_wise_most_frequenct_intent(stack=false, is_search=false) {

    channel_value = get_current_default_channel()
    category_name = get_current_default_category()
    selected_language = get_current_default_language()
    dropdown_language = get_url_vars()["selected_language"]
    if (typeof dropdown_language == 'undefined'){
        dropdown_language = "en"
    }

    bot_pk = get_selected_bot_id();
    if (stack) {
        category_wise_most_frequent_history.push({
            category_wise_most_frequenct_intent_page: category_wise_most_frequenct_intent_page,
            category_wise_most_frequenct_individual_page: category_wise_most_frequenct_individual_page,
        })
    }
    if (category_wise_most_intent_end_flag && stack) {
        category_wise_most_frequenct_individual_page = 0
        category_wise_most_intent_end_flag = false
    }
    if (category_wise_most_frequenct_individual_page === 0 && !is_search) {
        category_wise_most_frequenct_intent_page += 1;
    }
    if (!is_search) {
        category_wise_most_frequenct_individual_page += 1
    }
    start_date = document.getElementById("trending-category-wise-start-date").value
    end_date = document.getElementById("trending-category-wise-end-date").value
    if (start_date > end_date) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("trending-category-wise-start-date").value = $("#trending-category-wise-start-date").attr("current_applied_date");
        document.getElementById("trending-category-wise-end-date").value = $("#trending-category-wise-end-date").attr("current_applied_date");
        return;
    }
    $("#trending-category-wise-start-date").attr("current_applied_date", start_date)
    $("#trending-category-wise-end-date").attr("current_applied_date", end_date)
    $("#no-category-most-frequent-div").hide()
    $("#category-most-frequent-div").hide()
    var xhttp = new XMLHttpRequest();
    var params = '';
    let search_term = $("#category-most-frequent-search").val()
    if (is_search) {
        category_wise_most_frequenct_individual_page = 1
    }
    xhttp.open("GET", "/chat/get-category-wise-frequent-intent/?bot_pk=" + bot_pk + "&reverse=true&channel=" + channel_value + "&page=" + category_wise_most_frequenct_intent_page + "&intent_page=" + category_wise_most_frequenct_individual_page + "&start_date=" + start_date + "&end_date=" + end_date + "&global_category=" + category_name + "&selected_language=" + selected_language + "&search=" + search_term + "&dropdown_language=" + dropdown_language, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-category-most-frequent-div").show()
        if (this.readyState == 4 && (this.status == 200 || this.status == 300)) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == 300) {
                if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                    document.getElementById("category-wise-most-frequenct-intents").classList.add("language-right-to-left-wrapper")
                    $("#most-category-searchbar-div span").addClass("right-to-left-search-span")
                    $("#most-category-searchbar-div input").addClass("right-to-left-search-input")  
                } else {
                    document.getElementById("category-wise-most-frequenct-intents").classList.remove("language-right-to-left-wrapper")
                }
                intent_html = "";
                $("#category-most-frequent-name").html("( Category: " + response["category_name"].substring(0, 25) + " )")
                var i = 0;
                var len = response["intent_frequency_list"].length; 

                if (response["no_pages"] !== 1 || response["intent_num_pages"] !== 1) {
                    if (response["is_last_page"] == false || response["is_intent_last_page"] == false) {
                        $("#category-most-frequent-right").show()
                    } else {
                        $("#category-most-frequent-right").hide()
                    }
                    if (category_wise_most_frequenct_intent_page === 1 && category_wise_most_frequenct_individual_page === 1) {
                        $("#category-most-frequent-left").hide()
                    } else {
                        $("#category-most-frequent-left").show()
                    }
                } else {
                    $("#category-most-frequent-left").hide()
                    $("#category-most-frequent-right").hide()
                }

                if (response["intent_num_pages"] == category_wise_most_frequenct_individual_page) {
                    category_wise_most_intent_end_flag = true
                } else {
                    category_wise_most_intent_end_flag = false
                }

                if (len === 0) {
                    $("#category-most-frequent-div").hide()
                    $("#no-category-most-frequent-div").css("display", "flex")
                    return
                }

                $("#category-most-frequent-div").show()
                $("#no-category-most-frequent-div").hide()

                for (i = 0; i < 5; i++) {
                    let category_most_frequent_intent;
                    let category_most_frequent_frequency;
                    if (i >= len) {
                        intent_html += '<li class="easychat-session-analytics-item"></li>'
                        continue
                    }
                    else if(response["status"]==200) {
                        category_most_frequent_intent = response["intent_frequency_list"][i]["multilingual_name"]
                        category_most_frequent_frequency = response["intent_frequency_list"][i]["frequency"]
                    }
                    else{
                        category_most_frequent_intent = response["intent_frequency_list"][i]["intent_name"]
                        category_most_frequent_frequency = response["intent_frequency_list"][i]["frequency"]
                    }

                    category_most_frequent_intent = sanitize_html(category_most_frequent_intent)

                    intent_html += `
                        <li class="easychat-session-analytics-item intent-list-item">
                            <div class="easychat-analytics-data-card-content-div">
                                <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <rect width="24" height="24" rx="4" fill="#EFF2F5" />
                                    </svg>
                                </div>
                                <div class="easychat-analytics-data-card-item-text">
                                    ${category_most_frequent_intent}
                                </div>
                            </div>
                            <div class="easychat-analytics-data-card-value">
                                ${category_most_frequent_frequency}
                            </div>
                        </li>
                    `
                }

                document.getElementById("category-wise-most-frequenct-intents").innerHTML = intent_html;
                if (response["status"]== 300){
                        document.getElementById("translation_api_toast_container").style.display = "flex";
                        setTimeout(api_fail_message_none, 4000);
                }

            }
        }
    }
    xhttp.send(params);
}

function load_previous_category_wise_most_frequenct_intent() {

    if (category_wise_most_frequent_history.length === 0) {
        return
    }
    var history_obj = category_wise_most_frequent_history.pop()
    category_wise_most_frequenct_individual_page = history_obj.category_wise_most_frequenct_individual_page - 1
    category_wise_most_frequenct_intent_page = history_obj.category_wise_most_frequenct_intent_page - 1
    if (category_wise_most_frequenct_individual_page === 0) {
        category_wise_most_frequenct_intent_page = history_obj.category_wise_most_frequenct_intent_page - 1
    } else {
        category_wise_most_frequenct_intent_page = history_obj.category_wise_most_frequenct_intent_page
    }

    load_next_category_wise_most_frequenct_intent(false)
}

function show_nps_information() {

    $("#modal-nps-information").modal("open");
}


function update_language_select_dropdown() {
    $('#select-language-type').multiselect({
        columns: 1,
        placeholder: 'Select Language',
        search: true,
        selectAll: true
    });
}

function get_list_of_supported_languages() {

    if (get_current_default_language() == "All") {
        return []
    } else {
        return get_current_default_language().split(", ")
    }
}

function handle_language_filter_based_on_channel(channel_value) {

    let lang_filter_value = get_current_default_language()

    document.getElementById("div-analytics-language").innerText = "";

    let lang_dropdown_html = '<br><select name="basic[]" multiple="multiple" id="select-language-type">'

    if (channel_value == "All") {
        list_of_languages = master_language_list
    } else {
        list_of_languages = channel_wise_supported_language_map[channel_value]
    }

    for (let i = 0; i < list_of_languages.length; i++) {
        is_selected = true

        lang_code = list_of_languages[i].split("-")[0]

        if (lang_filter_value != "All" && !get_list_of_supported_languages().includes(lang_code)) {
            is_selected = false
        }

        lang_name = list_of_languages[i].split("-")[1]

        if (is_selected) {
            lang_dropdown_html += "<option value='" + lang_code + "' selected>" + lang_name + "</option>";
        } else {
            lang_dropdown_html += "<option value='" + lang_code + "'>" + lang_name + "</option>";
        }

    }

    lang_dropdown_html += "</select>"

    document.getElementById("div-analytics-language").innerHTML = lang_dropdown_html

    update_language_select_dropdown()

    if (lang_filter_value != "All") {

        let checked_languages = $("#select-language-type option:selected")
        let selected_languages_list = $("#select-language-type").val()
        let selected_languages_text = ""
        let language_filter_text = ""
        for (let i = 0; i < checked_languages.length; i++) {
            language_filter_text += checked_languages[i].innerText
            selected_languages_text += selected_languages_list[i]
            if (i != checked_languages.length - 1) {
                language_filter_text += ", "
                selected_languages_text += ", "
            }
        }
        if (selected_languages_text == "") {
            delete_analytics_language_filter_option()
            showToast("Selected Languages are not enabled for " + channel_value + " please select the language again", 2000);

        } else {
            document.getElementById("default-language-for-analytics").innerText = selected_languages_text
            document.getElementById("add-analytics-language-value").value = language_filter_text
        }

    }

}

function revised_filter() {
    let start_date = $("input[name=conversion_intent_analytics_date_filter]:checked")[0].getAttribute("start_date_value")
    let end_date = $("input[name=conversion_intent_analytics_date_filter]:checked")[0].getAttribute("end_date_value")
    date_filter_selected = $("input[name=conversion_intent_analytics_date_filter]:checked")[0].getAttribute("date-filter");
    let selected_channel = $("input[name=intent-analytics-channel]:checked")
    let selected_lang_text = ""
    let selected_language_elms = $(".item-checkbox:checked")
    let not_selected_language_elms = $(".item-checkbox:not(:checked)")
    is_revised_filter_applied = true

    if (not_selected_language_elms.length === 0) {
        selected_lang_text += "All"
    } else {
        for (const elm of selected_language_elms) {
            selected_lang_text += elm.value
            selected_lang_text += ", "
        }
    }
    if(selected_lang_text.trim() == "") {
        showToast("Please select at least one language");
        return;
    }

    selected_lang_text = selected_lang_text.replace(/, $/, "")
    selected_category = $(".easychat_analytics_select_category_dropdown").val()

    $("#default-channel-for-analytics").html(selected_channel.val())
    $("#default-category-for-analytics").html(selected_category)
    $("#default-language-for-analytics").html(selected_lang_text)

    $("#easychat-analytics-filter-modal").modal("close");

    if (new Date(start_date).getTime() <= new Date(end_date).getTime()) {
        if (new Date().setHours(0, 0, 0, 0) >= new Date(end_date).setHours(0, 0, 0, 0)) {
            set_start_end_date(start_date, end_date)
            load_all_analytics();
        } else {
            M.toast({
                "html": "End Date should not be Future Date"
            });
        }
    } else {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("conversion_intent_custom_start_date").value = $("#conversion_intent_custom_start_date").attr("current_applied_date");
        document.getElementById("conversion_intent_custom_end_date").value = $("#conversion_intent_custom_end_date").attr("current_applied_date");
    }

}

function add_analytics_filter_option() {
    var selOpts = [];

    var value = document.getElementById("check-analytics-filter-select").value;
    if (value == "") {
        showToast("Kindly select a valid filter", 2000);
        return;
    }
    if (value == "1") {
        channel_value = document.getElementById("select-analytics-channels-filter").value;
        if (channel_value == "") {
            showToast("Kindly select a valid filter", 2000);
            return;
        }

        var flag = false;
        try {
            val = document.getElementById("add-analytics-channels-key").value
            flag = false
        } catch {
            flag = true
        }
        if (flag == true) {
            if (value != "" && channel_value != "") {
                html = '<div class="row" id="analytics-filter-channels-div"><br><div class="col s4">'
                html += '<input id="add-analytics-channels-key" value="Filter by Channel" disabled>'
                html += '</div>'
                html += '<div class="col s4">'
                html += '<input id="add-analytics-channels-value" value= " ' + channel_value + ' " disabled>'
                html += '</div><a class="red-text text-darken-3" onclick="delete_analytics_channels_filter_option()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-analytics-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
                document.getElementById("default-channel-for-analytics").innerText = channel_value

                handle_language_filter_based_on_channel(channel_value);
            } else {
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        } else {
            showToast("This filter is already present.", 2000);
            return;
        }
    } else if (value == "2") {
        date_filter_value = document.getElementById("modal-message-default-settings-type").value;
        if (date_filter_value == "") {
            showToast("Kindly select a valid filter", 2000);
            return;
        }
        date_filter_text = $("#modal-message-default-settings-type option:selected").text()
        var start_date_elm = document.getElementsByClassName("message-default-start-date")[0]
        var start_date = start_date_elm.value;
        if (start_date == "") {
            showToast("Kindly enter a start date.", 2000);
            return;
        }
        var end_date_elm = document.getElementsByClassName("message-default-end-date")[0]
        var end_date = end_date_elm.value;
        if (end_date == "") {
            showToast("Kindly enter a end date.", 2000);
            return;
        }
        var flag = false;
        try {
            val = document.getElementById("add-analytics-date-key").value
            flag = false
        } catch {
            flag = true
        }
        value_last_month = start_date_elm.getAttribute('value_last_month')
        value_last3 = start_date_elm.getAttribute('value_last3')
        value_golive = start_date_elm.getAttribute('value_golive')
        if (flag == true) {
            if (value != "" && date_filter_value != "") {
                html = '<div class="row" id="analytics-filter-date-div"><br><div class="col s4">'
                html += '<input id="add-analytics-date-key" value="Filter by Date" disabled>'
                html += '</div>'
                html += '<div class="col s4"><input id="add-analytics-date-value" value= " ' + date_filter_text + ' " disabled></div> '
                if (date_filter_value == 'custom_date') {
                    html += '<div class="col s8">'
                    html += '<div class="col s6">Start Date <input type="date" disabled class="message-default-start-date" value="' + start_date + '" value_last_month="' + value_last_month + '" value_last3="' + value_last3 + '" value_golive="' + value_golive + '"></div>'
                    html += '<div class="col s6">End Date<input type="date" disabled class="message-default-end-date" value="' + end_date + '" value_last_month="' + end_date + '" value_last3="' + end_date + '" value_golive="' + end_date + '"></div>'
                    html += '</div>'
                }
                html += '<a class="red-text text-darken-3" onclick="delete_analytics_date_filter_option()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-analytics-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
            } else {
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        } else {
            showToast("This filter is already present.", 2000);
            return;
        }
    } else if (value == "3") {
        category_filter_value = document.getElementById("select-analytics-category-filter").value;
        if (category_filter_value == "") {
            showToast("Kindly select a valid filter", 2000);
            return;
        }
        category_filter_text = $("#select-analytics-category-filter option:selected").text()
        var flag = false;
        try {
            val = document.getElementById("add-analytics-category-key").value
            flag = false
        } catch {
            flag = true
        }
        if (flag == true) {
            if (value != "" && category_filter_value != "") {
                html = '<div class="row" id="analytics-filter-category-div"><br><div class="col s4">'
                html += '<input id="add-analytics-category-key" value="Filter by Category" disabled>'
                html += '</div>'
                html += '<div class="col s4"><input id="add-analytics-category-value" value= " ' + category_filter_text + ' " disabled></div> '
                html += '<a class="red-text text-darken-3" onclick="delete_analytics_category_filter_option()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-analytics-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
                document.getElementById("default-category-for-analytics").innerText = category_filter_text
            } else {
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        }
    } else if (value == "4") {
        language_filter_value = document.getElementById("select-language-type").value;
        if (language_filter_value == "") {
            showToast("Kindly select a valid filter", 2000);
            return;
        }
        let checked_languages = $("#select-language-type option:selected")
        let selected_languages_list = $("#select-language-type").val()
        let selected_languages_text = ""
        let language_filter_text = ""
        for (let i = 0; i < checked_languages.length; i++) {
            language_filter_text += checked_languages[i].innerText
            selected_languages_text += selected_languages_list[i]
            if (i != checked_languages.length - 1) {
                language_filter_text += ", "
                selected_languages_text += ", "
            }
        }
        var flag = false;
        try {
            val = document.getElementById("add-analytics-language-key").value
            flag = false
        } catch {
            flag = true
        }
        if (flag == true) {
            if (value != "" && language_filter_value != "") {
                html = '<div class="row" id="analytics-filter-language-div"><br><div class="col s4">'
                html += '<input id="add-analytics-language-key" value="Filter by Language" disabled>'
                html += '</div>'
                html += '<div class="col s4"><input id="add-analytics-language-value" value= "' + language_filter_text + '" disabled></div> '
                html += '<a class="red-text text-darken-3" onclick="delete_analytics_language_filter_option()"><i class="material-icons">delete</i></a></div>'
                div_html = document.getElementById("add-analytics-filter-buttons")
                div_html.insertAdjacentHTML('beforeend', html);
                document.getElementById("default-language-for-analytics").innerText = selected_languages_text
            } else {
                showToast("Kindly select a valid filter.", 2000);
                return;
            }
        } else {
            showToast("This filter is already present.", 2000);
            return;
        }
    }
}

function delete_analytics_date_filter_option() {

    div = document.getElementById("analytics-filter-date-div");
    div.parentNode.removeChild(div);
    // document.getElementById("modal-message-default-settings-type").value = ""
    // document.getElementById("default-channel-for-analytics").innerText = "All"
    document.getElementsByClassName("message-default-start-date")[0] = ""
    document.getElementsByClassName("message-default-end-date")[0] = ""
}


function delete_analytics_channels_filter_option() {

    div = document.getElementById("analytics-filter-channels-div");
    div.parentNode.removeChild(div);
    document.getElementById("default-channel-for-analytics").innerText = "All";
    handle_language_filter_based_on_channel("All")
}

function delete_analytics_category_filter_option() {

    div = document.getElementById("analytics-filter-category-div");
    div.parentNode.removeChild(div);
    document.getElementById("default-category-for-analytics").innerText = "All";
}

function delete_analytics_language_filter_option() {

    div = document.getElementById("analytics-filter-language-div");
    div.parentNode.removeChild(div);
    document.getElementById("default-language-for-analytics").innerText = "All";
}

function check_analytics_filter() {

    var value = document.getElementById("check-analytics-filter-select").value;
    if (value == "1") {
        document.getElementById("div-analytics-channels").style.display = "block"
        document.getElementById("div-analytics-date").style.display = "none"
        document.getElementById("modal-message-default-settings-custom").style.display = "none"
        document.getElementById("div-analytics-category").style.display = "none"
        document.getElementById("select-analytics-category-filter").style.display = "none"
        document.getElementById("div-analytics-language").style.display = "none"

    } else if (value == "2") {
        document.getElementById("div-analytics-channels").style.display = "none"
        document.getElementById("div-analytics-date").style.display = "block"
        document.getElementById("div-analytics-category").style.display = "none"
        document.getElementById("select-analytics-category-filter").style.display = "none"
        document.getElementById("div-analytics-language").style.display = "none"

    } else if (value == "3") {
        document.getElementById("div-analytics-channels").style.display = "none"
        document.getElementById("div-analytics-date").style.display = "none"
        document.getElementById("div-analytics-language").style.display = "none"
        document.getElementById("div-analytics-category").style.display = "block"
    } else if (value == "4") {
        document.getElementById("div-analytics-channels").style.display = "none"
        document.getElementById("div-analytics-date").style.display = "none"
        document.getElementById("div-analytics-category").style.display = "none"
        document.getElementById("div-analytics-language").style.display = "block"
    }
}

////////////////////////////////// NPS analytics /////////////////////////////////

// if (window.location.href.indexOf("/chat/nps-analytics/") != -1) {

//     $(document).ready(function() {
//         $('#nps_table').DataTable({
//             dom: 'Bfrtip',
//             "paging": false,
//             "ordering": true,
//             "bPaginate": false,
//             "order":[[0,'desc']],
//         });
//     });
// }

function open_nps_filter_modal(is_result_filtered) {

    $("#modal-nps-filter").modal("open");
}

function populate_nps_filter_type_options() {

    filter = document.getElementById("nps-filter-type").value;
    document.getElementById("nps-options-cell").style.display = "block";
    document.getElementById("extra-table-data").style.display = "block";
    document.getElementById("nps-filter-type-nps-span").style.display = "none";
    document.getElementById("nps-filter-type-date-span").style.display = "none";
    document.getElementById("nps-filter-type-date-value-span").style.display = "none";
    if (filter == "Date") {
        document.getElementById("nps-filter-type-date-span").style.display = "block";
    } else if (filter == "NPS") {
        document.getElementById("nps-filter-type-nps-span").style.display = "block";
    } else {
        document.getElementById("nps-filter-type-nps-span").style.display = "none";
        document.getElementById("nps-filter-type-date-span").style.display = "none";
        document.getElementById("nps-filter-type-date-value-span").style.display = "none";
    }
    document.getElementById("nps-filter-add-btn").style.display = "block";
}

function populate_nps_filter_table() {

    filter = document.getElementById("nps-filter-type").value;
    // var filter_objs = document.getElementsByClassName('nps_filter_chosen');
    // if(filter_objs.length != 0)
    // {
    //     for(var i=0 ; i<filter_objs.length; i++)
    //     {
    //         filter = filter_objs[i].getAttribute("filter_parameter").split(':')[0];
    //         if (filter == "start_date")
    //         {
    //             filter_objs[i].remove()
    //         }
    //         if (filter == "end_date")
    //         {
    //             filter_objs[i].remove()
    //         }
    //     }
    // }
    var html = "";
    if (filter == 'Date') {
        filter_option = document.getElementById("nps-filter-type-date").value;
        if (filter_option == "Week") {
            date_from = document.getElementById("nps-filter-type-date-from").getAttribute("value");
            date_to = document.getElementById("nps-filter-type-date-to").getAttribute("value");
        } else if (filter_option == "Month") {
            date_from = document.getElementById("nps-filter-type-date-from").getAttribute("value_month");
            date_to = document.getElementById("nps-filter-type-date-to").value;
        } else {
            date_from = document.getElementById("nps-filter-type-date-from").value;
            date_to = document.getElementById("nps-filter-type-date-to").value;
        }

        if (date_from == '' || date_to == '') {
            M.toast({
                "html": "Dates cannot be empty!"
            });
        } else if (new Date(date_from).getTime() > new Date(date_to).getTime()) {
            M.toast({
                "html": "From Date should be smaller than To Date!"
            });
        } else {
            //Below line to check filter is applied only once
            if (document.getElementById("nps_filter_chosen_start_date") == null && document.getElementById("nps_filter_chosen_end_date") == null) {

                html = "<tr style='border:0px;' class='nps_filter_chosen' id='nps_filter_chosen_start_date' filter_parameter=start_date:" + date_from + ">";
                html += "<td class='center' style='border:0px;background-color: inherit;'> Date From </td>";
                date_from = change_date_format(date_from)
                html += "<td class='center' style='border:0px;background-color: inherit;'>" + date_from + "</td>";
                html += '<td class="center" style="border:0px;background-color: inherit;"> <a class="waves-effect waves-light red-text text-darken-3" onclick="delete_filter_chosen(this)"><i class="material-icons">delete</i></a></td>';
                html += "</tr>";

                html += "<tr style='border:0px;' class='nps_filter_chosen' id='nps_filter_chosen_end_date' filter_parameter=end_date:" + date_to + ">";
                html += "<td class='center' style='border:0px;background-color: inherit;'> Date To </td>";
                date_to = change_date_format(date_to)
                html += "<td class='center' style='border:0px;background-color: inherit;'>" + date_to + "</td>";
                html += '<td class="center" style="border:0px;background-color: inherit;"> <a class="waves-effect waves-light red-text text-darken-3" onclick="delete_filter_chosen(this)"><i class="material-icons">delete</i></a></td>';
                html += "</tr>";

            }
        }
    } else {
        filter_option = document.getElementById("nps-filter-type-nps").value;
        if (document.getElementById('nps_filter_option_nps_score') == null) {
            html = "<tr style='border:0px;' class='nps_filter_chosen' id='nps_filter_option_nps_score' filter_parameter=nps_score:" + filter_option + ">";
            html += "<td class='center' style='border:0px;background-color: inherit;'> CSAT Score </td>";
            html += "<td class='center' style='border:0px;background-color: inherit;'>" + filter_option + "</td>";
            html += '<td class="center" style="border:0px;background-color: inherit;"> <a class="waves-effect waves-light red-text text-darken-3" onclick="delete_filter_chosen(this)"><i class="material-icons">delete</i></a></td>';
            html += "</tr>";
        }
    }
    document.getElementById("nps_filter_table_body").innerHTML += html;
}

function change_date_format(date) {

    var dateParts = date.split("-");
    date = dateParts[2] + "-" + dateParts[1] + "-" + dateParts[0];
    return date.trim();
}

function show_custom_date_span() {

    filter_option = document.getElementById("nps-filter-type-date").value;
    if (filter_option == "Custom") {
        document.getElementById("nps-filter-type-date-value-span").style.display = "block";
    } else {
        document.getElementById("nps-filter-type-date-value-span").style.display = "none";
    }
}

function delete_filter_chosen(ele) {

    ele.parentNode.parentNode.remove();
}

function apply_nps_filter() {

    var query_string = window.location.search.split('&')[0] + '&' + window.location.search.split('&')[1];
    var date_range_type = "";
    var start_date = "";
    var end_date = "";
    var channels = "";
    var nps_filter = "";

    if (document.getElementById("date_range_1").checked) {
        date_range_type = "1";
    } else if (document.getElementById("date_range_2").checked) {
        date_range_type = "2";
    } else if (document.getElementById("date_range_3").checked) {
        date_range_type = "3";
    } else if (document.getElementById("date_range_4").checked) {
        date_range_type = "4";
    } else if (document.getElementById("date_range_5").checked) {
        date_range_type = "5";
        start_date = document.getElementById("start_date").value;
        end_date = document.getElementById("end_date").value;
        if (start_date.trim() == "") {
            showToast("Please Enter a Start Date.");
            return;
        }
        if (end_date.trim() == "") {
            showToast("Please Enter a End Date");
            return;
        }
        var today = new Date();
        var today_date = today.getFullYear();

        var month = (today.getMonth() + 1).toString();
        if (month.length == 1) {
            month = "0" + month;
        }
        var day = today.getDate().toString();
        if (day.length == 1) {
            day = "0" + day;
        }

        today_date = today_date + "-" + month + "-" + day;

        if (!compare_dates(start_date, today_date)) {
            showToast("Start date cannot be greate than today's date.");
            return;
        }
        if (!compare_dates(end_date, today_date)) {
            showToast("End date cannot be greater than today's date.");
            return;
        }
        if (!compare_dates(start_date, end_date)) {
            showToast("Start Date should be smaller than End Date");
            return;
        }

    }

    if (document.getElementById("filter_csat_promoter").checked) {
        nps_filter = "Promoters";
    } else if (document.getElementById("filter_csat_demoter").checked) {
        nps_filter = "Demoters"
    } else if (document.getElementById("filter_csat_passive").checked) {
        nps_filter = "Passives"
    }
    
    if (document.getElementById("checkbox1").checked){
        if (channels != ""){
            channels += "+Android";
        }else{
            channels += "Android";
        }
    }

    if (document.getElementById("checkbox2").checked){
        if (channels != ""){
            channels += "+iOS";
        }else{
            channels += "iOS";
        }
    }

    if (document.getElementById("checkbox3").checked){
        if (channels != ""){
            channels += "+GoogleBusinessMessages";
        } else {
            channels += "GoogleBusinessMessages";
        }
    }
    // if (document.getElementById("checkbox4").checked){
    //     if (channels != ""){
    //         channels += "+Telegram";
    //     }else{
    //         channels += "Telegram";
    //     }
    // }
    // if (document.getElementById("checkbox5").checked){
    //     if (channels != ""){
    //         channels += "+Google_Home";
    //     }else{
    //         channels += "Google_Home";
    //     }
    // }
    if (document.getElementById("checkbox6").checked) {
        if (channels != "") {
            channels += "+Web";
        } else {
            channels += "Web";
        }
    }
    if (document.getElementById("checkbox7").checked){
        if (channels != ""){
            channels += "+Viber";
        }else{
            channels += "Viber";
        }
    }
    if (document.getElementById("checkbox8").checked) {
        if (channels != "") {
            channels += "+WhatsApp";
        } else {
            channels += "WhatsApp";
        }
    }
    // if (document.getElementById("checkbox9").checked){
    //     if (channels != ""){
    //         channels += "+Facebook";
    //     }else{
    //         channels += "Facebook";
    //     }
    // }
    // if (document.getElementById("checkbox10").checked){
    //     if (channels != ""){
    //         channels += "+Google_Chat";
    //     }else{
    //         channels += "Google_Chat";
    //     }
    // }
    if (date_range_type != "") {
        query_string += "&filter_type=" + date_range_type;
    }
    if (date_range_type == 5) {
        query_string += "&start_date=" + start_date;
        query_string += "&end_date=" + end_date;
    }
    if (nps_filter != "") {
        query_string += "&nps_score=" + nps_filter
    }
    if (channels != "") {
        query_string += "&channels=" + channels;
    }
    window.location = '/chat/nps-analytics/' + query_string;
}

///////////////////////////////// NPS Analytics END //////////////////////////////

//------ Intuitive Block----------
function close_other_suggestion_intents(id) {

    $(".suggestion-intent-content").each(function (index, element) {
        if (this.id != "suggestion-intent-content-" + id) {
            if ($(this).hasClass("is-active")) {
                $(this).removeClass("is-active");
            }
        }
    });
}

$('html').click(function () {
    close_other_suggestion_intents("");
});

function handle_intuitive_icon_click(e, id) {

    e.stopPropagation();
    var elem = document.getElementById('suggestion-intent-content-' + id);

    if ($('#suggestion-intent-content-' + id).hasClass("is-active")) {
        $('#suggestion-intent-content-' + id).removeClass("is-active")

    } else {
        $('#suggestion-intent-content-' + id).toggleClass("is-active")
    }

    close_other_suggestion_intents(id);
}

$(document).ready(function () {

    $('.suggestion-intent-dropdown-items').each(function (index, element) {
        $(this).click(function (e) {
            e.stopPropagation();
        })
    })
});

const search_intuitive_questions_intents = debounce(function() {
    load_intuitive_questions_intent()
})

function load_intuitive_questions_intent() {

    intuitive_questions_page = 0;
    load_next_intuitive_questions_intent();
}

function intuitive_intents_html_compriser(list_of_intents_per_query) {

    var temp_html = ""
    var temp_list = []
    list_of_intents_per_query.forEach(function (itm, index) {
        var intent_name = itm["name"]
        if(get_intitutive_api_status == 200){
            intent_name = itm["multilingual_intent_name"]
        }
        intent_name = sanitize_html(intent_name)
        if (!temp_list.includes(intent_name)) {
            temp_list.push(intent_name)
            if (itm["resolved"] == "false") {
                if (itm["deleted"] == "true")
                    temp_html += '<a title="Deleted" style="opacity: 0.3; cursor: text">\
                        <li class="easychat-analytics-data-card-intent-list-item">' + intent_name + '</li></a>'
                else
                    temp_html += '<a target="_blank" href="/chat/edit-intent/?intent_pk=' + itm["pk"] + '&selected_language=en" onclick="update_bot_based_on_selected_language(this)" >\
                    <li class="easychat-analytics-data-card-intent-list-item">' + intent_name + '</li></a>'

            } else {
                temp_html += '<a title="This is already resolved"><li class="easychat-analytics-data-card-intent-list-item">' + intent_name + '<div style="display: flex;align-items: center;" >\
                    <svg width="12" height="12" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M5.00016 0.833344C2.70433 0.833344 0.833496 2.70418 0.833496 5.00001C0.833496 7.29584 2.70433 9.16668 5.00016 9.16668C7.296 9.16668 9.16683 7.29584 9.16683 5.00001C9.16683 2.70418 7.296 0.833344 5.00016 0.833344ZM6.99183 4.04168L4.62933 6.40418C4.571 6.46251 4.49183 6.49584 4.4085 6.49584C4.32516 6.49584 4.246 6.46251 4.18766 6.40418L3.0085 5.22501C2.88766 5.10418 2.88766 4.90418 3.0085 4.78334C3.12933 4.66251 3.32933 4.66251 3.45016 4.78334L4.4085 5.74168L6.55016 3.60001C6.671 3.47918 6.871 3.47918 6.99183 3.60001C7.11266 3.72084 7.11266 3.91668 6.99183 4.04168Z" fill="#25B139"/>\
                    </svg>\
                    <span style="color: #25B139; font-size: 11px;">\
                    This is already resolved\
                    </span>\
                </div>\
                </li></a>'
            }
        }
    });
    return [temp_list, temp_html]
}

function load_next_intuitive_questions_intent() {
    channel_value = get_current_default_channel();
    selected_language = get_current_default_language();
    // document.getElementById("recently-intuitive-messages-loader").style.display = "block";
    // document.getElementById("intuitive-questions-analytics-chart").innerHTML = "";

    bot_pk = get_selected_bot_id();
    dropdown_language = get_url_vars()["selected_language"]
    if (typeof dropdown_language == 'undefined'){
        dropdown_language = "en"
    }
    intuitive_questions_page += 1;
    start_date = document.getElementById("intuitive-question-wise-start-date").value
    end_date = document.getElementById("intuitive-question-wise-end-date").value
    if (start_date > end_date) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("intuitive-question-wise-start-date").value = $("#intuitive-question-wise-start-date").attr("current_applied_date");
        document.getElementById("intuitive-question-wise-end-date").value = $("#intuitive-question-wise-end-date").attr("current_applied_date");
        return;
    }
    $("#intuitive-question-wise-start-date").attr("current_applied_date", start_date)
    $("#intuitive-question-wise-end-date").attr("current_applied_date", end_date)
    $("#no-intuitive_questions_div").hide()
    $("#intuitive_questions_div").hide()
    var xhttp = new XMLHttpRequest();
    var params = '';
    let search_term = $("#intuitive_questions_search").val()

    xhttp.open("GET", "/chat/get-intuitive-message/?bot_pk=" + bot_pk + "&channel_name=" + channel_value + "&page=" + intuitive_questions_page + "&start_date=" + start_date + "&end_date=" + end_date + "&selected_language=" + selected_language + "&search=" + search_term + "&dropdown_language=" + dropdown_language, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-intuitive_questions_div").show()
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            get_intitutive_api_status = response["status"]
            if (response["status"] == 200 || response["status"] == 300) {
                if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                    document.getElementById("intuitive-questions-analytics-chart").classList.add("language-right-to-left-wrapper")
                    $("#intuitive-searchbar-div span").addClass("right-to-left-search-span")
                    $("#intuitive-searchbar-div input").addClass("right-to-left-search-input")  
                } else {
                    document.getElementById("intuitive-questions-analytics-chart").classList.remove("language-right-to-left-wrapper")
                }
                var i = 0;
                intent_html = ""
                list_of_intents_per_query = response["list_of_intents_per_query"]

                if (response["intuitive_message_list"].length === 0) {
                    $("#intuitive_questions_div").hide()
                    $("#no-intuitive_questions_div").css("display", "flex")
                    return
                }

                $("#intuitive_questions_div").show()
                $("#no-intuitive_questions_div").hide()

                let num_undefined = 0

                for (i = 0; i < response["intuitive_message_list"].length; i++) {
                    if (list_of_intents_per_query[i] == undefined) {
                        num_undefined += 1
                        continue;
                    }
                    var list_and_html = intuitive_intents_html_compriser(list_of_intents_per_query[i])
                    var temp_list = list_and_html[0]
                    var temp_html = list_and_html[1]
                    // Tooltip will only appear when length of temp_list is 0, this happens only in case of PDF/G-Search/E-Search responses
                    let card_cursor_property = temp_list.length ? "pointer" : "default";
                    let tooltip_class = temp_list.length ? "" : "tooltipped no-popup-opener";

                    intent_html += `
                        <li class="easychat-session-analytics-item intent-list-item">
                            <div class="easychat-analytics-data-card-content-div">
                                <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <a data-position="top" data-tooltip="PDF/G-Search/E-Search Response" class="easychat-analytics-card-question-intent-btn ${tooltip_class}" style="cursor: ${card_cursor_property}">
                                        ${temp_list.length}
                                    </a>
                                    <ul class="easychat-analytics-data-card-intent-list">
                                        ${temp_html}
                                    </ul>
                                </div>
                                <div class="easychat-analytics-data-card-item-text">
                                    ${sanitize_html(response["intuitive_message_list"][i][0])}
                                </div>
                            </div>
                            <div class="easychat-analytics-data-card-value">
                                ${response["intuitive_message_list"][i][1]}
                            </div>
                        </li>
                    `
                }
                if (i < 6) {
                    for (i; i < 5+num_undefined; i++) {
                        intent_html += '<li class="easychat-session-analytics-item">';
                    }
                }
                if (response["is_last_page"] == false) {
                    $("#intuitive-questions-right").show()
                } else {
                    $("#intuitive-questions-right").hide()
                }

                if (response["is_single_page"] == false) {
                    if (intuitive_questions_page === 1) {
                        $("#intuitive-questions-left").hide()
                    } else {
                        $("#intuitive-questions-left").show()
                    }
                } else {
                    $("#intuitive-questions-left").hide()
                }

                // document.getElementById("recently-intuitive-messages-loader").style.display = "none";
                document.getElementById("intuitive-questions-analytics-chart").innerHTML = intent_html;
                $('.tooltipped').tooltip();
                if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                    $(".easychat-analytics-data-card-intent-list").css("left", "-320px")
                    $(".easychat-analytics-data-card-intent-list").css("right", "")
                } else {
                    $(".easychat-analytics-data-card-intent-list").css("right", "-350px")
                    $(".easychat-analytics-data-card-intent-list").css("left", "")
                }
                $(".easychat-analytics-card-question-intent-btn").click(function(e) {
                    if($(this).hasClass("no-popup-opener")) return;
                    e.stopPropagation();
                    $(".easychat-analytics-data-card-intent-list").hide();
                    $(this).siblings(".easychat-analytics-data-card-intent-list").show();
                });

                $('body').click(function() {

                    $(".easychat-analytics-data-card-intent-list").hide();
        
                });

                if (get_intitutive_api_status == 300){
                        document.getElementById("translation_api_toast_container").style.display = "flex";
                        setTimeout(api_fail_message_none, 4000);
                }
            }
        }
    }
    xhttp.send(params);

}

function load_previous_intuitive_questions_intent() {


    intuitive_questions_page -= 2;

    if (intuitive_questions_page < 0) {
        intuitive_questions_page = 0;
    }

    load_next_intuitive_questions_intent()
}

//------ Intuitive Block End----------

const search_intent_wise_chartflow_intents = debounce(function() {
    load_intent_wise_chartflow_intent()
})

function load_intent_wise_chartflow_intent() {
    date_filter_selected = "date_range_5";
    flow_analytics_page = 0;
    load_next_most_frequent_intent_flow_analytics()
}


function load_next_most_frequent_intent_flow_analytics() {

    // document.getElementById("flow-analytics-chart").innerHTML = ""
    channel_name = get_current_default_channel()
    dropdown_language = get_url_vars()["selected_language"]
    if (typeof dropdown_language == 'undefined'){
        dropdown_language = "en"
    }
    category_name = get_current_default_category()
    selected_language = get_current_default_language()
    bot_pk = get_selected_bot_id();
    start_date = document.getElementById("trending-intent-wise-flow-start-date").value
    end_date = document.getElementById("trending-intent-wise-flow-end-date").value
    if (start_date > end_date) {
        M.toast({
            "html": "Start Date should be smaller than End Date"
        });
        document.getElementById("trending-intent-wise-flow-start-date").value = $("#trending-intent-wise-flow-start-date").attr("current_applied_date");
        document.getElementById("trending-intent-wise-flow-end-date").value = $("#trending-intent-wise-flow-end-date").attr("current_applied_date");
        return;
    }
    $("#trending-intent-wise-flow-start-date").attr("current_applied_date", start_date)
    $("#trending-intent-wise-flow-end-date").attr("current_applied_date", end_date)
    $("#no-flow-analytics-div").hide()
    $("#flow-analytics-div").hide()
    flow_analytics_page += 1;
    var xhttp = new XMLHttpRequest();
    var params = '';
    let search_term = $("#intent_chartflow_search").val()
    xhttp.open("GET", "/chat/get-flow-analytics-intent/?bot_pk=" + bot_pk + "&page=" + flow_analytics_page + "&start_date=" + start_date + "&end_date=" + end_date + "&channel_name=" + channel_name + "&category_name=" + category_name + "&selected_language=" + selected_language + "&search=" + search_term + "&dropdown_language=" + dropdown_language, true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-flow-analytics-div").show()
        if (this.readyState == 4 && (this.status == 200 || this.status == 300)) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == 300) {
                if (response["status"] == 200 && response["language_script_type"] == "rtl") {
                    document.getElementById("flow-analytics-chart").classList.add("language-right-to-left-wrapper")
                    $("#intent-flow-searchbar-div span").addClass("right-to-left-search-span")
                    $("#intent-flow-searchbar-div input").addClass("right-to-left-search-input") 
                } else {
                    document.getElementById("flow-analytics-chart").classList.remove("language-right-to-left-wrapper")
                }
                intent_html = "";
                var i = 0;

                if (response["intent_with_children_name_pk_occurences"].length === 0) {
                    $("#flow-analytics-div").hide()
                    $("#no-flow-analytics-div").css("display", "flex")
                    return
                }

                $("#flow-analytics-div").show()
                $("#no-flow-analytics-div").hide()

                for (i = 0; i < 5; i++) {
                    let flow_analytics_intent;
                    let flow_analytics_frequency;
                    let flow_analytics_link;
                    if (i >= response["intent_with_children_name_pk_occurences"].length) {
                        intent_html += '<li class="easychat-session-analytics-item"></li>'
                        continue
                    } else {
                        flow_analytics_intent = sanitize_html(response['intent_with_children_name_pk_occurences'][i][0])
                        flow_analytics_frequency = response['intent_with_children_name_pk_occurences'][i][2]
                        flow_analytics_link = `/chat/flow-analytics/?intent_pk=${response['intent_with_children_name_pk_occurences'][i][1]}&bot_pk=${bot_pk}&start_date=${start_date}&date_end=${end_date}&dropdown_language=${dropdown_language}&date_filter=${date_filter_selected}`                                               
                    }
                    intent_html += `
                        <a href="${flow_analytics_link}">
                        <li class="easychat-session-analytics-item intent-list-item">
                            <div class="easychat-analytics-data-card-content-div">
                                <div class="easychat-analytics-data-card-icon-wrapper">
                                    <div class="easychat-analytics-card-item-color-div"></div>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <rect width="24" height="24" rx="4" fill="#EFF2F5" />
                                    </svg>
                                </div>
                                <div class="easychat-analytics-data-card-item-text">
                                    ${flow_analytics_intent}
                                </div>
                            </div>
                            <div class="easychat-analytics-data-card-value">
                                ${flow_analytics_frequency}
                            </div>
                        </li>
                        </a>
                    `
                }

                if (response["is_last_page"] == false) {
                    $("#flow-analytics-right").css("display", "inline")
                } else {
                    $("#flow-analytics-right").css("display", "none")
                }

                if (response["is_single_page"] == false) {
                    if (flow_analytics_page === 1) {
                        $("#flow-analytics-left").hide()
                    } else {
                        $("#flow-analytics-left").show()
                    }
                } else {
                    $("#flow-analytics-left").css("display", "none")
                }

                document.getElementById("flow-analytics-chart").innerHTML = intent_html;
                if (response["status"]== 300){
                        document.getElementById("translation_api_toast_container").style.display = "flex";
                        setTimeout(api_fail_message_none, 4000);
                }
            }
        }
    }
    xhttp.send(params);
}

function load_previous_most_frequent_intent_flow_analytics() {

    flow_analytics_page -= 2;

    if (flow_analytics_page < 0) {
        flow_analytics_page = 0;
    }
    
    load_next_most_frequent_intent_flow_analytics()
}

function export_traffic_source() {

    bot_pk = get_selected_bot_id();
    start_date = document.getElementById("trending-analytics-start-date").value
    end_date = document.getElementById("trending-analytics-end-date").value
    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        start_date: start_date,
        end_date: end_date
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/export-traffic-source/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            var file_url = response["file_url"];
            if (response["status"] == 200 && response["file_url"] != null) {
                window.open(file_url);
            } else {
                M.toast({
                    "html": "Internal server error please report error."
                });
            }
        }
    }
    xhttp.send(params);
}

function validate_email_addresses(email_id, input_field_id) {
    let invalid_email_addresses = [];
    let find_duplicates = arr => arr.filter((item, index) => arr.indexOf(item) != index)
    let duplicate_email_addresses = [...new Set(find_duplicates(email_id.split(",")))];

    for (let id of email_id.split(",")) {
        if (!validate_email(id)) {
            invalid_email_addresses.push(id);
        }
    }
    let validation_error_message = "";
    let duplicate_error_message = "";

    if (!invalid_email_addresses.length && !duplicate_email_addresses.length) return true;
    if (email_id == "") {
        validation_error_message = `<span style="color: red;">Error:</span> Please enter a valid email address to proceed.`
    }
    else if (invalid_email_addresses.length == 1) {
        validation_error_message = `<span style="color: red;">Error:</span> The email address <span style="color: red;">${invalid_email_addresses.join(", ")}</span> provided is invalid. Please enter a valid email address to proceed.`
    } else if (invalid_email_addresses.length > 1) {
        validation_error_message = `<span style="color: red;">Error:</span> The email addresses <span style="color: red;">${invalid_email_addresses.join(", ")}</span> provided are invalid. Please enter valid email addresses to proceed.`
    }
    if (duplicate_email_addresses.length == 1) {
        duplicate_error_message = `<span style="color: red;">Error:</span> Duplicate email address <span style="color: red;">${duplicate_email_addresses.join(", ")}</span> added. Kindly remove the duplicate email address to proceed.`
    } else if (duplicate_email_addresses.length > 1) {
        duplicate_error_message = `<span style="color: red;">Error:</span> Duplicate email addresses <span style="color: red;">${duplicate_email_addresses.join(", ")}</span> added. Kindly remove the duplicate email addresses to proceed.`
    }
    if (invalid_email_addresses.length) {
        $("#" + input_field_id).siblings("p.email-validation-error").html(validation_error_message)
        $("#" + input_field_id).siblings("p.email-validation-error").show();
    } else {
        $("#" + input_field_id).siblings("p.email-validation-error").html('')
        $("#" + input_field_id).siblings("p.email-validation-error").hide();
    }

    if (duplicate_email_addresses.length) {
        $("#" + input_field_id).siblings("p.duplicate-email-error").html(duplicate_error_message)
        $("#" + input_field_id).siblings("p.duplicate-email-error").show();
    } else {
        $("#" + input_field_id).siblings("p.duplicate-email-error").html('')
        $("#" + input_field_id).siblings("p.duplicate-email-error").hide();
    }
    return false
}

function export_analytics_in_excel(type, open_modal) {

    bot_pk = get_selected_bot_id();
    channel_value = get_current_default_channel()
    category_name = get_current_default_category()
    selected_language = get_current_default_language()
    filter_type_particular = 1
    dropdown_language = get_url_vars()["selected_language"]
    email_id = window.user_email
    if (type == "message_analytics") {
        start_date = document.getElementById("message-analytics-start-date").value
        end_date = document.getElementById("message-analytics-end-date").value

        filter_type_particular = message_analytics_filter
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-message-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-message-analytics').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-message-analytics")) {
            return;
        }

    } else if (type == "user_analytics") {
        start_date = document.getElementById("user-analytics-start-date").value
        end_date = document.getElementById("user-analytics-end-date").value
        filter_type_particular = user_analytics_filter
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-user-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-user-analytics').modal('open');
            return
        }
        for (let id of email_id.split(",")) {
            if (!validate_email(id)) {
                M.toast({"html": 'Please enter valid Email address'}, 4000, "rounded");
                return
            }
        }

    } else if (type == "most_frequent_intents") {
        start_date = document.getElementById("trending-most-frequent-questions-start-date").value;
        end_date = document.getElementById("trending-most-frequent-questions-end-date").value;
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-most_frequent_intents").value.replace(/\s/g, '');

        if (!open_modal) {
            $('#modal-email-for-export-most_frequent_intents').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-most_frequent_intents")) {
            return;
        }

    } else if (type == "least_frequent_intents") {
        start_date = document.getElementById("trending-least-frequent-questions-start-date").value;
        end_date = document.getElementById("trending-least-frequent-questions-end-date").value;
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-least_frequent_intents").value.replace(/\s/g, '');

        if (!open_modal) {
            $('#modal-email-for-export-least_frequent_intents').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-least_frequent_intents")) {
            return;
        }


    } else if (type == "intent_wise_chartflow") {
        start_date = document.getElementById("trending-intent-wise-flow-start-date").value;
        end_date = document.getElementById("trending-intent-wise-flow-end-date").value;
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-intent_wise_chartflow").value.replace(/\s/g, '');

        if (!open_modal) {
            $('#modal-email-for-export-intent_wise_chartflow').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-intent_wise_chartflow")) {
            return;
        }

    } else if (type == "category_wise_frequent_questions") {
        start_date = document.getElementById("trending-category-wise-start-date").value
        end_date = document.getElementById("trending-category-wise-end-date").value
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-category-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-category-analytics').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-category-analytics")) {
            return;
        }
    } else if (type == "unanswered_questions") {
        start_date = document.getElementById("unanswered-question-wise-start-date").value;
        end_date = document.getElementById("unanswered-question-end-date").value;
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-unanswered-questions").value.replace(/\s/g, '');

        if (!open_modal) {
            $('#modal-email-for-export-unanswered-questions').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-unanswered-questions")) {
            return;
        }
    } else if (type == "intuitive_questions") {
        start_date = document.getElementById("intuitive-question-wise-start-date").value;
        end_date = document.getElementById("intuitive-question-wise-end-date").value;
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-intuitive-questions").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-intuitive-questions').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-intuitive-questions")) {
            return;
        }

    } else if (type == "device_specific_analytics") {
        start_date = document.getElementById("device-analytics-start-date").value
        end_date = document.getElementById("device-analytics-end-date").value

        filter_type_particular = device_analytics_filter
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-device-specific-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-device-specific-analytics').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-device-specific-analytics")) {
            return;
        }

    } else if (type == "hour_wise_analytics") {
        start_date = document.getElementById("hour-wise-custom-start-date").value;
        end_date = document.getElementById("hour-wise-custom-end-date").value;
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)
        interval_type = $("input[name='hour-wise-analytics-interval']:checked").val();
        time_format = $("input[name='hour-wise-analytics-time-format']:checked").val();
        filter_type_particular = interval_type + time_format

        email_id = document.getElementById("export-data-email-hour-wise-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-hour-wise-analytics').modal('open');
            return
        }

        if (!validate_email_addresses(email_id, "export-data-email-hour-wise-analytics")) {
            return;
        }
    } else if (type == "whatsapp_catalogue_analytics") {
        let selected_channel = get_current_default_channel().toLowerCase().trim();
        if(!['all', 'whatsapp'].includes(selected_channel)) {
            M.toast({"html": 'There is no data available to export for the selected channel'}, 3000, "rounded");
            return
        }
        start_date = document.getElementById("catalogue_custom_start_date").value
        end_date = document.getElementById("catalogue_custom_end_date").value

        filter_type_particular = catalogue_analytics_filter
        const st_date = new Date(start_date)
        const ed_date = new Date(end_date)

        email_id = document.getElementById("export-data-email-whatsapp-catalogue-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-whatsapp-catalogue-analytics').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-whatsapp-catalogue-analytics")) {
            return;
        }

    } else if (type == "most_used_form_assist_intents") {
        start_date = document.getElementById("form-assist-analytics-start-date").value;
        end_date = document.getElementById("form-assist-analytics-end-date").value;
    
        email_id = document.getElementById("export-data-email-form-assist").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-form-assist').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-form-assist")) {
            return;
        }
    } else if (type == "user_nudge_analytics") {
        start_date = document.getElementById("user-nudge-analytics-start-date").value;
        end_date = document.getElementById("user-nudge-analytics-end-date").value;
    
        email_id = document.getElementById("export-data-email-nudge-analytics").value.replace(/\s/g, '')

        if (!open_modal) {
            $('#modal-email-for-export-nudge-analytics').modal('open');
            return
        }
        if (!validate_email_addresses(email_id, "export-data-email-nudge-analytics")) {
            return;
        }
    }

    $("p.email-validation-error, p.duplicate-email-error").html('')
    $("p.email-validation-error, p.duplicate-email-error").hide();
    $('.modal').modal('close');

    var json_string = JSON.stringify({
        bot_pk: bot_pk,
        start_date: start_date,
        end_date: end_date,
        type: type,
        channel_value: channel_value,
        filter_type_particular: filter_type_particular,
        category_name: category_name,
        email_id: email_id,
        selected_language: selected_language,
        dropdown_language: dropdown_language
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/export-analytics-in-excel-individual/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            
            if (response["status"] == 200) {

                if ("export_file_path" in response) {
                    var file_url = response["export_file_path"];
                    window.open(file_url);
                } else if ("email_id" in response) {
                    var email_id = response["email_id"];
                    setTimeout(function (e) {
                        M.toast({
                            "html": "You will receive the dump over email in less than an hour on the email address(es) provided"
                        });
                    }, 1000)
                }

            } else if (response["status"] == 201) {
                let email_id = response["email_id"];
                M.toast({
                    "html": "You will receive the dump over email in 24 hours on the email address(es) provided"
                });
            } else {
                M.toast({
                    "html": "Internal server error please report error."
                });
            }
        }
    }
    xhttp.send(params);
}


function validate_email(id) {

    var regex = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    var ctrl = document.getElementById(id);
    if (ctrl.value != "" && regex.test(ctrl.value)) {
        return true;
    } else {
        return false;
    }
}

$("#export-analytics-filter").click(function () {

    selected_filter_value = $("input[name=analytics-export-filter]:checked").val();
    bot_pk = get_selected_bot_id();
    channel_value = get_current_default_channel()
    let timer;

    if (selected_filter_value == "0") {
        timer = setTimeout(function() {alert("Please select valid date range filter")}, 500);
        return;
    }
    if (selected_filter_value == "4") {
        document.getElementById("custom-range-filter-analytics").style.display = "block";
    }
    startdate = document.getElementById("analytics_export_excel_start_date").value
    enddate = document.getElementById("analytics_export_excel_end_date").value
    email_id = document.getElementById("filter-data-email-analytics").value.replace(/\s/g, '');
    var startdate_obj = new Date(startdate)
    var enddate_obj = new Date(enddate)

    if ((selected_filter_value == "4" && (startdate == "" || enddate == "")) || (selected_filter_value == "4" && startdate_obj.getTime() > enddate_obj.getTime())) {
        M.toast({"html": 'Please enter valid dates'}, 4000, "rounded");
        return
    }

    if (selected_filter_value == "4" && !validate_email_addresses(email_id, "filter-data-email-analytics")) {
        return;
    }

    $("p.email-validation-error, p.duplicate-email-error").html('')
    $("p.email-validation-error, p.duplicate-email-error").hide();
    $('.modal').modal('close');

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "bot_pk": bot_pk,
        "startdate": startdate,
        "enddate": enddate,
        "email_id": email_id
    })

    json_string = EncryptVariable(json_string);

    $.ajax({
        url: "/chat/exportdata-analytics/",
        type: "POST",
        data: {
            json_string: json_string
        },
        success: function (response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (response["export_path"] == null) {
                    timer = setTimeout(function() {alert("Sorry, unable to process your request. Kindly try again later.")}, 500);
                } else if (response["export_path"] == "request_saved") {
                    timer = setTimeout(function() {
                        alert("We haved saved your request and will send data over provided email ID within 24 hours.");
                        window.location.reload();
                    }, 500);
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        timer = setTimeout(function() {alert("Requested data doesn't exists. Kindly try again later.")}, 500);
                    }
                }
            } else if (response["status"] == 400) {
                M.toast({"html": response["message"]}, 4000, "rounded");
            } else {
                timer = setTimeout(function() {alert("Sorry, unable to process your request. Kindly try again later.")}, 500);
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        }
    });
    timer && clearTimeout(timer)
});


// Drop Down Code

function create_custom_dropdowns() {

    $(".easychat-console-select-drop").each(function (i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div id="' + this.id + "-select" + '" class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0"><span class="current" id="' + this.id + "-current-wrapper" + '"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();
            var options = $(select).find('span');
            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('.current').html(selected.data('display-text') || selected.text());
            options.each(function (j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });

            if (this.id == "easychat-console-lang-dropdown") {

                var url_string = window.location.href
                var url = new URL(url_string);
                var selected_language = url.searchParams.get("selected_language");
                if (selected_language == null){
                    selected_language = "en";
                }
                $("#easychat-console-lang-dropdown-select ul li[data-value='" + selected_language + "']").addClass('easychat-lang-selected');
                var default_select_lang_drop = $('#easychat-console-lang-dropdown-select ul li[data-value="' + selected_language + '"]').text();
                $('#easychat-console-lang-dropdown-select .current').html(default_select_lang_drop);

            } else {

                $("#" + this.id + "-select" + " ul li:first").addClass('easychat-lang-selected');
                var default_select_lang_drop = $('#' + this.id + "-select" + ' ul li:first').text();
                $('#' + this.id + "-select" + ' .current').html(default_select_lang_drop);

            }

        }

    });

    $('.easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue" autocomplete="off" placeholder="Search Language" onkeyup="filter()" class="dd-searchbox" type="text"></div>');

    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');

}

// Event listeners

// Open/close
$(document).on('click', '.easychat-dropdown-select-custom', function (event) {

    if ($(event.target).hasClass('dd-searchbox')) {
        return;
    }
    $('.easychat-dropdown-select-custom').not($(this)).removeClass('open');
    $(this).toggleClass('open');
    $('#txtSearchValue').val("");
    $(".easychat-dropdown-select-custom ul li").show();
    $('.custom-drop-nodata-found-div').hide();
    if ($(this).hasClass('open')) {
        $(this).find('.easychat-console-language-option').attr('tabindex', 0);
        $(this).find('.easychat-lang-selected').focus();
    } else {
        $(this).find('.easychat-console-language-option').removeAttr('tabindex');
        $(this).focus();
    }
});

// Close when clicking outside
$(document).on('click', function (event) {

    if ($(event.target).closest('.easychat-dropdown-select-custom').length === 0) {
        $('.easychat-dropdown-select-custom').removeClass('open');
        $('.easychat-dropdown-select-custom .option').removeAttr('tabindex');
    }
    event.stopPropagation();
});

function filter() {

    var valThis = $('#txtSearchValue').val();
    $('.easychat-dropdown-select-custom ul > li').each(function () {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show() : $(this).hide();

        if ($('.easychat-dropdown-select-custom ul').children(':visible').not('.custom-drop-nodata-found-div').length === 0) {
            $('.custom-drop-nodata-found-div').show();
        } else {
            $('.custom-drop-nodata-found-div').hide();
        }

    });
};
// Search

// Option click
$(document).on('click', '.easychat-dropdown-select-custom .easychat-console-language-option', function (event) {

    $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
    $(this).addClass('easychat-lang-selected');

    var text = $(this).data('display-text') || $(this).text();
    console.log($(this).data('value'))
    $(this).closest('.easychat-dropdown-select-custom').find('.current').text(text);
    $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');

    if (event.target.parentElement.parentElement.parentElement.id == "easychat-console-lang-dropdown-select") {
        var url_string = window.location.href
        var url = new URL(url_string);
        bot_id = url.searchParams.get("bot_id");
        changed_language = $(this).attr('data-value');
        $('#modal-language-change-loader').modal("open");
        setTimeout(function () {
            window.location = "/chat/revised-analytics/?bot_id=" + bot_id + "&selected_language=" + changed_language;
        },2000)
    }

});

// Keyboard events
$(document).on('keydown', '.easychat-dropdown-select-custom', function (event) {
    var focused_option = $($(this).find('.list .easychat-console-language-option:focus')[0] || $(this).find('.list .easychat-console-language-option.easychat-lang-selected')[0]);
    // Space or Enter
    //if (event.keyCode == 32 || event.keyCode == 13) {
    if (event.keyCode == 13) {
        if ($(this).hasClass('open')) {
            focused_option.trigger('click');
        } else {
            $(this).trigger('click');
        }
        return false;
        // Down
    } else if (event.keyCode == 40) {
        if (!$(this).hasClass('open')) {
            $(this).trigger('click');
        } else {
            focused_option.next().focus();
        }
        return false;
        // Up
    } else if (event.keyCode == 38) {
        if (!$(this).hasClass('open')) {
            $(this).trigger('click');
        } else {
            var focused_option = $($(this).find('.list .easychat-console-language-option:focus')[0] || $(this).find('.list .easychat-console-language-option.easychat-lang-selected')[0]);
            focused_option.prev().focus();
        }
        return false;
        // Esc
    } else if (event.keyCode == 27) {
        if ($(this).hasClass('open')) {
            $(this).trigger('click');
        }
        return false;
    }
});


// Load user nudge analytics
function create_nudge_analytics_data_list(response) {

    var html = "";
    $("#nudge-analytics-div").show()
    $("#no-nudge-analytics-div").hide()

    if (response["user_nudge_analytics_data"].length) {

        for (var i = 0; i < 5; i++) {
            if (i >= response["user_nudge_analytics_data"].length) {
                html += '<li class="easychat-session-analytics-item"></li>'
                continue
            }
            html += `
                <li class="easychat-session-analytics-item analytics-card-green-li">
                    <div class="easychat-analytics-data-card-content-div">
                        <div class="easychat-analytics-data-card-icon-wrapper">
                            <div class="easychat-analytics-card-item-color-div"></div>
                            <span href="#" class="easychat-analytics-card-question-intent-btn">
                                ${response["user_nudge_analytics_data"][i]["count"]}
                            </span>
                        </div>
                        <div class="easychat-analytics-data-card-item-text">
                            ${sanitize_html(response["user_nudge_analytics_data"][i]["name"])}
                        </div>
                    </div>
                    <div class="easychat-analytics-data-card-value ${response["user_nudge_analytics_data"][i]["is_active"] ? "type-active" : "type-inactive"}">
                        ${response["user_nudge_analytics_data"][i]["is_active"] ? "Active" : "Inactive"}
                    </div>
                </li>
            `
        }

        if (response["is_next_page"]) {
            $("#nudge-analytics-right").show()
            $("#nudge-analytics-right").attr("onclick", "load_user_nudge_analytics(" + response["next_page_no"] + ")")
        } else {
            $("#nudge-analytics-right").hide()
        }

        if (response["is_previous_page"]) {
            $("#nudge-analytics-left").show()
            $("#nudge-analytics-left").attr("onclick", "load_user_nudge_analytics(" + response["previous_page_no"] + ")")
        } else {
            $("#nudge-analytics-left").hide()
        }

    } else {
        $("#nudge-analytics-div").hide()
        $("#no-nudge-analytics-div").css("display", "flex")
    }

    document.getElementById("user-nudge-analytics-chart").innerHTML = html;
}

const search_user_nudge_analytics = debounce(function() {
    load_user_nudge_analytics(1)
})

function load_user_nudge_analytics(page) {

    var category_name = get_current_default_category();
    var channel_name = get_current_default_channel();
    let selected_language = get_current_default_language();
    var bot_pk = get_selected_bot_id();
    var start_date = document.getElementById("user-nudge-analytics-start-date").value;
    var end_date = document.getElementById("user-nudge-analytics-end-date").value;
    var today = new Date();
    let search_term = $("#user_nudge_analytics_search").val()
    today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + String(today.getDate()).padStart(2, '0');

    if (start_date > today) {
        showToast("Start Date can not be greater than Today's Date", 2000);
        return;
    }
    if (end_date > today) {
        showToast("End Date can not be greater than Today's Date", 2000);
        return;
    }
    if (start_date > end_date) {
        showToast("Start Date should be smaller than End Date", 2000);
        document.getElementById("user-nudge-analytics-start-date").value = $("#user-nudge-analytics-start-date").attr("current_applied_date");
        document.getElementById("user-nudge-analytics-end-date").value = $("#user-nudge-analytics-end-date").attr("current_applied_date");
        return;
    }
    $("#user-nudge-analytics-start-date").attr("current_applied_date", start_date)
    $("#user-nudge-analytics-end-date").attr("current_applied_date", end_date)
    // document.getElementById("user-nudge-analytics-chart").innerHTML = "";
    $("#no-nudge-analytics-div").hide()
    $("#nudge-analytics-div").hide()

    var json_string = JSON.stringify({
        bot_id: bot_pk,
        start_date: start_date,
        end_date: end_date,
        page: page,
        category_name: category_name,
        channel_name: channel_name,
        selected_language: selected_language,
        search: search_term,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", "/chat/get-user-nudge-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        $("#no-nudge-analytics-div").show()
        if (this.readyState == 4 && this.status == 200) {

            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200) {
                create_nudge_analytics_data_list(response);
            } else {
                showToast("Error while loading User Nudge Analytics.", 2000);
            }
        }
    }
    xhttp.send(params);
}


function export_user_nudge_analytics(open_modal) {

    var category_name = get_current_default_category();
    var channel_name = get_current_default_channel();
    let selected_language = get_current_default_language();
    var bot_pk = get_selected_bot_id();
    var start_date = document.getElementById("user-nudge-analytics-start-date").value;
    var end_date = document.getElementById("user-nudge-analytics-end-date").value;
    var today = new Date();
    email_id = window.user_email
    today = today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, '0') + String(today.getDate()).padStart(2, '0');

    if (start_date > today) {
        showToast("Start Date can not be greater than Today's Date", 2000);
        return;
    }
    if (end_date > today) {
        showToast("End Date can not be greater than Today's Date", 2000);
        return;
    }
    if (start_date > end_date) {
        showToast("Start Date should be smaller than End Date", 2000);
        document.getElementById("user-nudge-analytics-start-date").value = $("#user-nudge-analytics-start-date").attr("current_applied_date");
        document.getElementById("user-nudge-analytics-end-date").value = $("#user-nudge-analytics-end-date").attr("current_applied_date");
        return;
    }
    $("#user-nudge-analytics-start-date").attr("current_applied_date", start_date)
    $("#user-nudge-analytics-end-date").attr("current_applied_date", end_date)

    let ed_date = new Date(end_date)
    let st_date = new Date(start_date)
    diff_in_no_of_days = (ed_date.getTime() - st_date.getTime()) / (1000 * 3600 * 24)// 1000 miliseconds in 1 secon 3600 second in 1 hour 24 hours in one day

    if (diff_in_no_of_days > 30) {
        email_id = document.getElementById("export-data-email-nudge-analytics").value

        if (!open_modal) {
            $('#modal-email-for-export-nudge-analytics').modal('open');
            return
        }
        if (!validate_email(email_id)) {
            M.toast({"html": 'Please enter valid Email address'}, 4000, "rounded");
            return
        }
    }

    var json_string = JSON.stringify({
        bot_id: bot_pk,
        start_date: start_date,
        end_date: end_date,
        category_name: category_name,
        channel_name: channel_name,
        selected_language: selected_language,
        email_id: email_id,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string;
    xhttp.open("POST", "/chat/export-user-nudge-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);

            if (response["status"] == 200) {
                if ("export_path" in response) {
                    var file_url = response["export_path"];
                    window.open(file_url);
                } else if ("email_id" in response) {
                    var email_id = response["email_id"];
                    setTimeout(function (e) {
                        M.toast({
                            "html": "You will receive the mail of the requested data soon on this address: " + email_id
                        });
                    }, 1000)
                }
            } else {
                showToast("Error while exporting User Nudge Analytics.", 2000);
            }
        }
    }
    xhttp.send(params);
}
function api_fail_message_none(){
    document.getElementById("translation_api_toast_container").style.display = "none";
}

function channel_usage_legends_search() {
    var input, filter, searchValue, i, txtValue;
    input = document.getElementById("channel_usage_graph_legend_search");
    filter = input.value.toUpperCase();
    searchValue = document.querySelectorAll('.channel-usage-legend-wrapper .graph-legend-item-div span');
    let count = 0
    for (i = 0; i < searchValue.length; i++) {

        txtValue = searchValue[i].textContent || searchValue[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            searchValue[i].parentElement.parentElement.parentElement.style.display = "";

            count++;

        } else {
            searchValue[i].parentElement.parentElement.parentElement.style.display = "none";
        }
    }
    if (count == 0) {

        document.getElementById('graph_legend_noresult_found').style.display = "block";
    } else {
        document.getElementById('graph_legend_noresult_found').style.display = "none";
    }
}

function category_wise_legends_search() {
    var input, filter, searchValue, i, txtValue;
    input = document.getElementById("category_wise_graph_legend_search");
    filter = input.value.toUpperCase();
    searchValue = document.querySelectorAll('.category-wise-legend-wrapper .graph-legend-item-div span');
    let count = 0
    for (i = 0; i < searchValue.length; i++) {

        txtValue = searchValue[i].textContent || searchValue[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            searchValue[i].parentElement.parentElement.parentElement.style.display = "";

            count++;

        } else {
            searchValue[i].parentElement.parentElement.parentElement.style.display = "none";
        }
    }
    if (count == 0) {

        document.getElementById('graph_legend_noresult_found_category').style.display = "block";
    } else {
        document.getElementById('graph_legend_noresult_found_category').style.display = "none";
    }
}

function search_from_table() {
    // Declare variables
    var input = document.getElementById("csat-search-bar");
    var filter = input.value.toUpperCase();
    var table = document.getElementById("nps-table");
    var trs = table.tBodies[0].getElementsByTagName("tr");

    var tds
    let tr_counter = trs.length;
    for (var i = 0; i < trs.length; i++) {
    tds = trs[i].getElementsByTagName("td");
        trs[i].style.display = "none";
        for (var i2 = 0; i2 < tds.length; i2++) {
            if (tds[i2].innerHTML.toUpperCase().indexOf(filter) > -1) {
                trs[i].style.display = "";
                tr_counter--;
                continue;
            }
        }
    }

    if(tr_counter == trs.length) {
        document.getElementById("no-nps-div").style.display = "flex";
        document.getElementById("nps-div").style.display = "none";
    }
    else {
        document.getElementById("no-nps-div").style.display = "none";
        document.getElementById("nps-div").style.display = "block";
    }
}


function check_hour_wise_analytics_filter(){
    let start_date =  $("input[name=conversion_intent_analytics_date_filter]:checked")[0].getAttribute("end_date_value");
    let end_date = start_date
    if (is_revised_filter_applied == true) {
        start_date = $("input[name=conversion_intent_analytics_date_filter]:checked")[0].getAttribute("start_date_value")
        end_date = $("input[name=conversion_intent_analytics_date_filter]:checked")[0].getAttribute("end_date_value")
        let date_filter = document.getElementsByName("hour_wise_analytics_date_filter");
        date_filter[3].checked = true;
        document.getElementById("hour-wise-custom-date-select-area").style.display = "block"
        is_revised_filter_applied = false
    } else {
        if(document.getElementById('hour_wise_month').checked){
            start_date = document.getElementById("hour_wise_month").getAttribute('start_date_value');
            end_date = document.getElementById("hour_wise_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('hour_wise_three_month').checked){
            start_date = document.getElementById("hour_wise_three_month").getAttribute('start_date_value');
            end_date = document.getElementById("hour_wise_three_month").getAttribute('end_date_value');
        }
        else if(document.getElementById('hour_wise_beg').checked){
            start_date = document.getElementById("hour_wise_beg").getAttribute('start_date_value');
            end_date = document.getElementById("hour_wise_beg").getAttribute('end_date_value');
        }
        else if(document.getElementById('hour_wise_analytics_filter_custom_date_btn').checked){
            start_date = document.getElementById("hour-wise-custom-start-date").value;
            end_date = document.getElementById("hour-wise-custom-end-date").value;
        }
    }

    document.getElementById("hour-wise-custom-start-date").value = start_date
    document.getElementById("hour-wise-custom-end-date").value = end_date

    return {
        start_date,
        end_date,
    };
}

function load_hour_wise_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        category_name = get_current_default_category()
        selected_language = get_current_default_language()
        // reset_charts();
        bot_pk = get_selected_bot_id();
        interval_type = $("input[name='hour-wise-analytics-interval']:checked").val();
        time_format = $("input[name='hour-wise-analytics-time-format']:checked").val();
        
        hour_wise_filter_result = check_hour_wise_analytics_filter();
        let start_date = hour_wise_filter_result.start_date;
        let end_date = hour_wise_filter_result.end_date;

        if (start_date > end_date) {
            M.toast({
                "html": "Start Date should be smaller than End Date"
            });
            document.getElementById("hour-wise-custom-start-date").value = $("#hour-wise-custom-start-date").attr("current_applied_date");
            document.getElementById("hour-wise-custom-end-date").value = $("#hour-wise-custom-end-date").attr("current_applied_date");
            return;
        }
        if (new Date().setHours(0, 0, 0, 0) < new Date(end_date).setHours(0, 0, 0, 0)) {
            M.toast({
                "html": "End Date should not be future date"
            });
            return
        }
        $("#hour-wise-custom-start-date").attr("current_applied_date", start_date)
        $("#hour-wise-custom-end-date").attr("current_applied_date", end_date)
        hour_wise_analytics_card && hour_wise_analytics_card.destroy()

        let json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            interval_type: interval_type,
            time_format: time_format,
            channel: channel_value,
            category_name: category_name,
            selected_language: selected_language
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        let xhttp = new XMLHttpRequest();
        let params = 'json_string=' + json_string;
        xhttp.open("POST", "/chat/get-hour-wise-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    if (start_date == end_date) {
                        $("#hour-wise-analytics-range").html(`<span></span> ${convert_date_format(start_date)}`)
                    } else {
                        $("#hour-wise-analytics-range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
                    }

                    const st_date = new Date(start_date)
                    const ed_date = new Date(end_date)
                    diff_in_no_of_days = (ed_date.getTime() - st_date.getTime()) / (1000 * 3600 * 24)// 1000 miliseconds in 1 secon 3600 second in 1 hour 24 hours in one day

                    if (diff_in_no_of_days > 0) {
                        document.getElementById("hour-wise-analytics-header-div").style.display = "block";
                    } else {
                        document.getElementById("hour-wise-analytics-header-div").style.display = "none";
                    }
                    
                    total_number_of_messages = response["hour_wise_analytics_list"][0]["total_message_count"]
                    total_number_of_users = response["hour_wise_analytics_list"][0]["total_users_count"]
                    interval_type = response["interval_type"]
                    time_format = response["time_format"]

                    if (time_format == "1"){
                        label_list = ['01 am', '02 am', '03 am', '04 am', '05 am', '06 am', '07 am', '08 am', '09 am', '10 am', '11 am', '12 pm', '01 pm', '02 pm', '03 pm', '04 pm', '05 pm', '06 pm', '07 pm', '08 pm', '09 pm', '10 pm', '11 pm', '12 am']
                        if (interval_type == "2"){
                            label_list = ['03 am', '06 am', '09 am', '12 pm', '03 pm', '06 pm', '09 pm', '12 am']
                        } else if (interval_type == "3"){
                            label_list = ['06 am', '12 pm', '06 pm', '12 am']
                        }
                    } else {
                        label_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09','10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
                        if (interval_type == "2"){
                            label_list = ['03', '06', '09', '12', '15', '18', '21', '24']
                        } else if (interval_type == "3"){
                            label_list = ['06', '12', '18', '24']
                        }
                    }
                

                    let options = {
                        series: [{
                                name: "Total number of users",
                                data: total_number_of_users
                            },
                            {
                                name: "Total number of messages",
                                data: total_number_of_messages
                            }
                        ],
                        colors: ['#3751FF', '#10B981'],
                        chart: {
                            height: 350,
                            type: 'line',
                            zoom: {
                                enabled: false
                            },
                            toolbar: {
                                show: false,
                            }
                        },
                        dataLabels: {
                            enabled: false
                        },
                        stroke: {
                            width: 2,
                            curve: "smooth",
                        },
                        title: {
                            show: false
                        },
                        grid: {
                            show: true,
                            borderColor: '#f1f1f1',
                            strokeDashArray: 0,
                            position: 'back',
                            xaxis: {
                                lines: {
                                    show: true
                                }
                            },
                            yaxis: {
                                lines: {
                                    show: false
                                },
                            },
                            row: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            column: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            padding: {
                                top: 0,
                                right: 0,
                                bottom: 0,
                                left: 10
                            },
                        },
                    
                        xaxis: {
                            type: 'time',
                            categories: label_list,
                        },
                        yaxis: {
                            style: {
                                marginRighnt: '20px',
                            },
                            labels: {
                            formatter: function(val) {
                                if (val != undefined)
                                return val.toFixed(0)
                            }
                            },
                        }
                    };
                    
                    hour_wise_analytics_card = new ApexCharts(document.querySelector("#hour-wise-analytics-graph"), options);
                    hour_wise_analytics_card.render();
                    resolve();
                    
                }
            }
        }
        xhttp.send(params);
    })

}

function load_whatsapp_catalogue_analytics() {

    return new Promise(function (resolve, reject) {
        channel_value = get_current_default_channel()
        category_name = get_current_default_category()
        selected_language = get_current_default_language()
        bot_pk = get_selected_bot_id();

        filter_type = $("input[name='whatsapp_catalogue_frequency']:checked").val();
        catalogue_analytics_filter = filter_type
        start_date = document.getElementById("catalogue_custom_start_date").value;
        end_date = document.getElementById("catalogue_custom_end_date").value;
        if (start_date > end_date) {
            M.toast({
                "html": "Start Date should be smaller than End Date"
            });
            document.getElementById("catalogue_custom_start_date").value = $("#catalogue_custom_start_date").attr("current_applied_date");
            document.getElementById("catalogue_custom_end_date").value = $("#catalogue_custom_end_date").attr("current_applied_date");
            return;
        }
        if (new Date().setHours(0, 0, 0, 0) < new Date(end_date).setHours(0, 0, 0, 0)) {
            M.toast({
                "html": "End Date should not be future date"
            });
            return
        }
        $("#catalogue_custom_start_date").attr("current_applied_date", start_date)
        $("#catalogue_custom_end_date").attr("current_applied_date", end_date)
        $("#no_catalogue_analytics_div").hide()
        $("#whatsapp_catalogue_graph").hide()
        if (whatsapp_catalogue_analytics_card != undefined) {
            whatsapp_catalogue_analytics_card && whatsapp_catalogue_analytics_card.destroy()
        }

        var json_string = JSON.stringify({
            bot_pk: bot_pk,
            start_date: start_date,
            end_date: end_date,
            filter_type: filter_type,
            channel: channel_value,
        });
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        var xhttp = new XMLHttpRequest();
        var params = 'json_string=' + json_string;

        xhttp.open("POST", "/chat/get-catalogue-combined-analytics/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (start_date == end_date) {
                $("#catalogue_analytics_range").html(`<span></span> ${convert_date_format(start_date)}`)
            } else {
                $("#catalogue_analytics_range").html(`<span>Range: </span> ${convert_date_format(start_date)} - ${convert_date_format(end_date)}`)
            }
            $("#no_catalogue_analytics_div").css("display", "flex")
            if (this.readyState == 4 && this.status == 200) {

                response = JSON.parse(this.responseText);
                response = custom_decrypt(response)
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    label_list = [];

                    total_carts = []
                    total_purchased_carts = []
                    total_conversion_ratio = []

                    total_days = response["total_days"]

                    for (var i = 0; i < response["catalogue_analytics_list"].length; i++) {
                        var dateSplit = response["catalogue_analytics_list"][i]["label"].split("-");
                        let objDate;
                        if (dateSplit.length !== 3) {
                            if (filter_type === "3") {
                                objDate = dateSplit[0] + " " + dateSplit[1].slice(2)
                            } else {
                                let first_range = dateSplit[0].split("/")
                                let first_date = new Date(first_range.reverse().join("/"))
                                let second_range = dateSplit[1].split("/")
                                let second_date = new Date(second_range.reverse().join("/"))
                                objDate = first_date.toLocaleString("default", {month: "short"}) + " " + first_date.getDate() + " - " + second_date.toLocaleString("default", {month: "short"}) + " " + second_date.getDate()
                            }
                        } else {
                            if (response["catalogue_analytics_list"].length <= 3) {
                                objDate = dateSplit[1] + " " + dateSplit[0] + " '" + dateSplit[2];
                            } else {
                                objDate = new Date(dateSplit[1] + " " + dateSplit[0] + ", " + dateSplit[2]).getTime();
                            }
                        }       
                        label_list.push(objDate);
                        try {
                            total_carts.push(response["catalogue_analytics_list"][i].total_carts || 0);
                            total_purchased_carts.push(response["catalogue_analytics_list"][i].total_purchased_carts || 0);
                            total_conversion_ratio.push(response["catalogue_analytics_list"][i].total_conversion_ratio || 0);
                        } catch (err) {
                            console.log(err)
                        }

                    }

                    let chart_category = "datetime";
                    let tick_amount = undefined;

                    if (label_list.length > 3) {
                        chart_category = "datetime"
                    } else {
                        chart_category = "category"
                    }

                    if (dateSplit.length !== 3) {
                        chart_category = "category"
                        tick_amount = 5
                    }

                    $("#no_catalogue_analytics_div").hide()
                    $("#whatsapp_catalogue_graph").css("display", "flex")

                    var options = {
                        series: [
                            {
                                name: "Cart",
                                data: total_carts
                            },
                            {
                                name: "Purchased",
                                data: total_purchased_carts
                            },
                            {
                                name: "Conversion Ratio",
                                data: total_conversion_ratio
                            }
                        ],
                        colors: ['#0254D7', '#10B981', '#F5C828'],
                        chart: {
                            height: 390,
                            type: 'line',
                            zoom: {
                                enabled: false
                            },
                            toolbar: {
                                show: false,
                            }
                        },
                        legend: {
                            show: true,
                            position: 'bottom',
                            floating: false,
                            verticalAlign: 'bottom',
                            align: 'center',
                            horizontalAlign: 'center',
                            offsetX: 0,
                            offsetY: 10,
                        },
                        tooltip: {
                            enabled: true,
                            y: {
                                formatter: function (value, opts) {
                                    if (opts.seriesIndex != 2) return value;
                                    return value + '%'
                                },
                            },
                        },
                        dataLabels: {
                            enabled: false
                        },
                        stroke: {
                            width: 2,
                            curve: "smooth",
                        },
                        title: {
                            show: false
                        },
                        grid: {
                            show: true,
                            borderColor: '#f1f1f1',
                            strokeDashArray: 0,
                            position: 'back',
                            xaxis: {
                                lines: {
                                    show: true
                                }
                            },
                            yaxis: {
                                lines: {
                                    show: true
                                },
                            },
                            row: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            column: {
                                colors: '#f1f1f1',
                                opacity: 0
                            },
                            padding: {
                                top: 0,
                                right: 0,
                                bottom: 0,
                                left: 20
                            },
                        },

                        xaxis: {
                            categories: label_list,
                            type: chart_category,
                            labels: {
                                datetimeUTC: false,
                                datetimeFormatter: {
                                    day: "dd MMM 'yy",
                                },
                                rotate: 0,
                            },
                            tickAmount: tick_amount,
                        },
                        yaxis: {
                            style: {
                                marginRighnt: '20px',
                            },
                            labels: {
                                formatter: function (val) {
                                    if (val != undefined)
                                        return val.toFixed(0)
                                }
                            },
                        }
                    };

                    whatsapp_catalogue_analytics_card = new ApexCharts(document.querySelector("#whatsapp_catalogue_graph"), options);
                    whatsapp_catalogue_analytics_card.render();

                } else if (response["status"] == 422) {

                    $("#no_catalogue_analytics_div").css("display", "flex")

                }
                resolve();
            }
        }
        xhttp.send(params);
    })
}

function resize_Textarea(id) {
    var textarea = document.getElementById(id);
    textarea.style.height = "";
    textarea.style.height = Math.min(textarea.scrollHeight, 100) + "px";
}