import axios from "axios";

import {
    change_date_format_original,
    is_valid_date,
    custom_decrypt,
    EncryptVariable,
    showToast,
    validate_email,
    get_url_vars,
    is_equal_json,
    getCsrfToken,
    get_params,
} from "../utils";

import {
    livechat_chat_history_report_update,
    livechat_avg_nps_report_update,
    livechat_avg_handle_time_report_update,
    livechat_avg_queue_time_report_update,
    livechat_interactions_per_chat_report_update,
} from "./utils_analytics";
import { category_checkbox_click } from "./livechat_category";

(function ($) {
    $(function () {
        $(".dropdown-trigger").dropdown({
            constrainWidth: false,
            alignment: "left",
        });

        $(".tooltipped").tooltip({
            position: "top",
        });

        $(".readable-pro-tooltipped").tooltip({
            position: "top",
        });

        $(".tooltipped").tooltip();
        $(".tooltipped").tooltip({
            position: "top",
        });
        if (screen.width < 680) {
            $("#web-switch").hide();
            $("#mobile-switch").show();
        }
        apply_event_listeners();

    }); // end of document ready
})(jQuery); // end of jQuery name space

const state = {
    live_chat_termination_data: {},
    live_chat_termination_graph: null,
    combined_chat_termination_graph: null,
    filter_params: {},
    selected_agent_pk: 0,
    is_initial_refresh: true,
    selected_live_analytics_supervisor: [],
    selected_combined_analytics_supervisor: [],
    daily_peak_hour_analytics_graph: null,
    cumulative_peak_hours_analytics_graph: null
};

//////////////////////////////// Livechat Parameters/Event Listeners Initialization /////////////////////////////////////////

function update_filter_params() {

    let channel = localStorage.getItem(`livechat_analytics_channel`);
    if(channel) {
        $("#livechat-analytics-channel").val(channel);
    }

    channel = localStorage.getItem(`livechat_live_analytics_channel`);
    if(channel) {
        $("#livechat-live-analytics-channel").val(channel);
    }

    let category = localStorage.getItem(`livechat_live_analytics_category`);
    if(category){
        category = category.toString().split(',');
        category.forEach(element => {
            $('#category-select-dropdown-analytics option[value="'+element+'"]').prop('selected', true)
        });
    } else {
        $('#category-select-dropdown-analytics option').prop('selected', true)
    }

    category = localStorage.getItem(`livechat_analytics_category`);
    if(category){
        category = category.toString().split(',');
        category.forEach(element => {
            $('#category-select-dropdown-combined-analytics option[value="'+element+'"]').prop('selected', true)
        });
    } else {
        $('#category-select-dropdown-combined-analytics option').prop('selected', true)
    }

    let supervisors_list = localStorage.getItem(`livechat_live_analytics_supervisors_list`);
    if(supervisors_list){
        supervisors_list = supervisors_list.toString().split(',');
        supervisors_list.forEach(element => {
            $('#supervisor-select-dropdown-analytics option[value="'+element+'"]').prop('selected', true)
        });
    }

    supervisors_list = localStorage.getItem(`livechat_analytics_supervisors_list`);
    if(supervisors_list){
        supervisors_list = supervisors_list.toString().split(',');
        supervisors_list.forEach(element => {
            $('#supervisor-select-dropdown-combined-analytics option[value="'+element+'"]').prop('selected', true)
        });
    }

}

function apply_event_listeners() {

    if(String(window.location.href).includes('analytics')){

        update_filter_params();

        if(window.USER_STATUS != '1') return;

        $("#supervisor-select-dropdown-analytics, #supervisor-select-dropdown-combined-analytics").on("change", function (e) {
            get_and_update_categories_dropdown(e.target);
        });

        $("#category-select-dropdown-analytics, #category-select-dropdown-combined-analytics").on("change", function (e) {
            get_and_update_supervisors_dropdown(e.target);
        });

        setTimeout(() => {document.getElementById('supervisor-select-dropdown-analytics').dispatchEvent(new Event('change'));}, 500);
        setTimeout(() => {document.getElementById('supervisor-select-dropdown-combined-analytics').dispatchEvent(new Event('change'));}, 500);
    }
    else if(String(window.location.href).includes('agent-performance-report') && window.USER_STATUS == '1'){

        $("#supervisor-select-dropdown-performance").on("change", function (e) {
            get_and_update_agents_dropdown(e.target);
        });

        setTimeout(() => {document.getElementById('supervisor-select-dropdown-performance').dispatchEvent(new Event('change'));}, 500);
    }
    else if(String(window.location.href).includes('agent-not-ready-report') && window.USER_STATUS == '1'){

        if(window.USER_STATUS != '1') return;
        $("#supervisor-select-dropdown-not-ready").on("change", function (e) {
            get_and_update_agents_dropdown(e.target, false);
        });

        state.selected_agent_pk = window.SELECTED_AGENT_PK;
        setTimeout(() => { document.getElementById('supervisor-select-dropdown-not-ready').dispatchEvent(new Event('change')); }, 500);
    }
    else if(String(window.location.href).includes('login-logout-report') && window.USER_STATUS == '1'){

        $("#supervisor-select-dropdown-login-logout").on("change", function (e) {
            get_and_update_agents_dropdown(e.target, false);
        });

        state.selected_agent_pk = window.SELECTED_AGENT_PK;
        setTimeout(() => { document.getElementById('supervisor-select-dropdown-login-logout').dispatchEvent(new Event('change')); }, 500);
    }  
}
 
//////////////////////////////// Livechat continous start /////////////////////////////////////////

function livechat_continous_update() {

    let channel = localStorage.getItem(`livechat_live_analytics_channel`);
    let category = localStorage.getItem(`livechat_live_analytics_category`);
    let supervisors_list = localStorage.getItem(`livechat_live_analytics_supervisors_list`);

    let json_string = JSON.stringify({
        channel: channel,
        category: category,
        supervisors_list: supervisors_list,
    });

    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/analytics-continous/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {

                document.getElementById("loggen_in_agents").innerHTML =
                    response["loggen_in_agents"];
                document.getElementById("ready_agents").innerHTML = response["ready_agents"];
                document.getElementById("not_ready_agents").innerHTML =
                    response["not_ready_agents"];
                document.getElementById("ongoing_chats").innerHTML = response["ongoing_chats"];
                document.getElementById("stop_interaction_agents").innerHTML =
                    response["stop_interaction_agents"];
                document.getElementById("current_capacity").innerHTML =
                    response["current_capacity"];
                document.getElementById("chats_in_queue").innerHTML = response["chats_in_queue"];
                document.getElementById("average_queue_time").innerHTML =
                    response["average_queue_time"];
                update_customer_wait_time_per_change(response["avg_queue_time_percentage_change"])

                if(document.getElementById("followup_leads")) {
                    document.getElementById("followup_leads").innerHTML = response["followup_leads"];
                }

                if(document.getElementById("live_analytics_chat_termination_graph")) {
                    render_chat_termination_graph("live_analytics_chat_termination_graph", response["chat_termination_data"], "live");
                }

                if(document.getElementById("customers_reported")) {
                    document.getElementById("customers_reported").innerHTML = response["customers_reported"];
                }

                if (document.getElementById("first-time-response")) {
                    document.getElementById("first-time-response").innerHTML = response["average_first_time_response_time"];
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

export function render_source_statistics_graph(graph_id, source_data) {

    var ctx = document.getElementById(graph_id).getContext("2d");
    let chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ["Desktop", "Mobile", "Others"],
            datasets: [{
                data: [source_data['Desktop'], source_data['Mobile'], source_data['Others']],
                backgroundColor: ["#1264E7", "#54CC61","#FFC700"]
            }]
        },
        options: {
            responsive: true, 
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    mode: 'index',
                    position: 'average',
                    yAlign: 'top',
                    backgroundColor: '#FFF',
                    titleFont: {
                        size: 14,
                    },
                    titleColor: '#000',
                    bodyColor: '#000',
                    bodyFont: {
                        size: 14,
                    },
                    displayColors: true,
                    borderColor: '#000',
                    borderWidth: 0.1,
                },
                legend: {
                    position: 'right',
                    labels: {
                        align: 'start',
                        fontColor: '#333',
                        padding: 20,
                        boxWidth: 15,
                        boxHeight: 15,
                        generateLabels: function(chart) {
                        const data = chart.data;
                        if (data.labels.length && data.datasets.length) {
                        const {
                            labels: {
                                pointStyle
                            }
                        } = chart.legend.options;
                        const max = data.datasets[0].data.reduce((a, b) => (a + b), 0);
                        return data.labels.map((label, i) => {
                            const meta = chart.getDatasetMeta(0);
                            const style = meta.controller.getStyle(i);
                            return {
                                text: `${label} (${(data.datasets[0].data[i])}%)`,
                                fillStyle: style.backgroundColor,
                                strokeStyle: style.borderColor,
                                lineWidth: style.borderWidth,
                            };
                        });
                        }
                        return [];
                        }
                    },
                }
            }
        }
    });
}

export function render_chat_termination_graph(graph_id, chat_termination_data, type) {

    let chart = state.combined_chat_termination_graph;
    if(type == "live") {

        if( is_equal_json(chat_termination_data, state.live_chat_termination_data) && Object.keys(chat_termination_data).length) {
            return;   
        } 
        
        state.live_chat_termination_data = chat_termination_data;
        chart = state.live_chat_termination_graph;
    }

    if(chart) chart.destroy();

    let system_termination_count = 0, agent_termination_count = 0, customer_termination_count = 0;

    if(chat_termination_data['System']) {
        system_termination_count = chat_termination_data['System'];
    }

    if(chat_termination_data['Agent']) {
        agent_termination_count = chat_termination_data['Agent'];
    }

    if(chat_termination_data['Customer']) {
        customer_termination_count = chat_termination_data['Customer'];
    }

    var ctx = document.getElementById(graph_id).getContext("2d");
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ["Chats"],

            datasets: [{
                label: 'Customer',
                data: [customer_termination_count],
                backgroundColor: "#0254D7",
                borderColor: '#ffffff',
            }, {
                label: 'Agent',
                data: [agent_termination_count],
                borderColor: '#ffffff',
                backgroundColor: "#2F80ED",
            }, {
                label: 'System',
                data: [system_termination_count],
                borderColor: '#fff',
                backgroundColor: "#93C5FD",
            }]
        },

        options: {
            indexAxis: 'y',
            responsive: true, // Instruct chart js to respond nicely.
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        zeroLineWidth: 0,
                        color: "rgba(0, 0, 0, 0)",
                        offset: true
                    },
                    ticks: {
                        fontFamily: "'Open Sans Bold', sans-serif",
                        fontSize: 11
                    },
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                     ticks: {
                       
                        fontFamily: "'Open Sans Bold', sans-serif",
                        fontSize: 11,
                    },

                    grid: {
                        color: "rgba(0, 0, 0, 0)",
                        offset: true
                    },
                   

                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    position: 'average',
                    yAlign: 'top',
                    backgroundColor: '#FFF',
                    titleFont: {
                        size: 14,
                    },
                    titleColor: '#000',
                    bodyColor: '#000',
                    bodyFont: {
                        size: 14,
                    },
                    displayColors: true,
                    borderColor: '#000',
                    borderWidth: 0.1,
    
                },
                legend: {
                    display: true,
                    position: 'bottom',
    
    
                    labels: {
                        align: 'start',
                        usePointStyle: true,
                        fontColor: '#333',
                        padding: 20,
                        align: 'start',
                        boxWidth: 9
                    }
                },
            }
          

        },
    });
    
    if(type == "live") {
        state.live_chat_termination_graph = chart;
    } else {
        state.combined_chat_termination_graph = chart;
    }
}

function update_customer_wait_time_per_change(avg_q_time_per_change){
    try{
        let prev_value = parseInt(document.getElementById("percentage_change_average_queue_time").innerHTML)
        avg_q_time_per_change = parseInt(avg_q_time_per_change)
        if(prev_value == avg_q_time_per_change){
            return
        }
        if(isNaN(avg_q_time_per_change)){
            if(document.getElementById("average_queue_time_data_rate")){
                document.getElementById("average_queue_time_data_rate").innerHTML = ""
                document.getElementById("average_queue_time_data_rate").style.display = "none";
            }
            document.getElementById("percentage_change_average_queue_time").innerHTML = "No Data Available"
            document.getElementById("percentage_change_average_queue_time").style.setProperty('color', '#4b4949', 'important');
            document.getElementById("percentage_change_average_queue_time").style.paddingLeft = "0px";
        }else{
        
            if(avg_q_time_per_change > 0){
                const svg_html = '<path d="M0.542775 5.49894C0.665352 5.49923 0.783377 5.4437 0.872648 5.34372L2.99164 2.97803C3.05471 2.90701 3.15385 2.90878 3.21511 2.982L3.92789 3.83078C4.37335 4.33696 5.07443 4.33696 5.51988 3.83078L6.71296 2.41073C6.72798 2.39279 6.74838 2.38271 6.76966 2.38271C6.79094 2.38271 6.81135 2.39279 6.82637 2.41073L7.39139 3.08085C7.45173 3.15233 7.5334 3.19244 7.61853\
                     3.19241C7.79608 3.19219 7.94003 3.02104 7.9404 2.80971V0.522231C7.94021 0.310806 7.79616 0.139529 7.61853 0.139529H5.68899C5.55834 0.138927 5.44037 0.23248 5.39053 0.376223C5.34068 0.519967 5.36887 0.685317 5.46185 0.794569L6.02887 1.46946C6.04398 1.48748 6.05249 1.51188 6.05255 1.53734C6.05263 1.56272 6.04409 1.58706 6.02887 1.60483L4.83746 3.02329C4.77443 3.09746 4.673 3.09746 4.60998\
                      3.02329L3.89687 2.17452C3.4692 1.66036 2.77507 1.64592 2.33256 2.14196L0.212902 4.50566C0.0691068 4.66698 0.0224499 4.91632 0.0951386 5.13502C0.167827 5.35371 0.345177 5.49758 0.542775 5.49815V5.49894Z" fill="#00B051"/>'
                   
                document.getElementById("average_queue_time_data_rate").innerHTML = svg_html;
                document.getElementById("percentage_change_average_queue_time").innerHTML = "+"+ avg_q_time_per_change + "%";
                document.getElementById("percentage_change_average_queue_time").style.setProperty('color', '#00B051', 'important');
                document.getElementById("average_queue_time_data_rate").style.display = "unset";
                   
            }else if(avg_q_time_per_change == 0){
                
                document.getElementById("percentage_change_average_queue_time").innerHTML = avg_q_time_per_change + "%";
                document.getElementById("percentage_change_average_queue_time").style.setProperty('color', '#4b4949', 'important');
                document.getElementById("average_queue_time_data_rate").innerHTML = "";
                document.getElementById("average_queue_time_data_rate").style.display = "none";
                   
            }else{
                const svg_html = '<path d="M0.681343 0.76671C0.810606 0.766402 0.935069 0.824969 1.02921 0.930401L3.26378 3.42512C3.33029 3.50002 3.43484 3.49816 3.49944 3.42094L4.2511 2.52587C4.72085 1.99207 5.46017 1.99207 5.92993 2.52587L7.18808 4.02337C7.20392 4.04229 7.22544 4.05292 7.24788 4.05292C7.27032 4.05292 7.29184 4.04229 7.30767 4.02337L7.90351 3.31669C7.96714 3.24132 8.05327 3.19902 8.14304\
                 3.19905C8.33029 3.19928 8.48208 3.37977 8.48247 3.60263V6.01488C8.48228 6.23783 8.33037 6.41845 8.14304 6.41845H6.10826C5.97048 6.41909 5.84608 6.32043 5.79352 6.16885C5.74096 6.01727 5.77068 5.8429 5.86873 5.72769L6.46668 5.01598C6.48261 4.99698 6.49159 4.97125 6.49165 4.9444C6.49173 4.91763 6.48272 4.89197 6.46668 4.87323L5.21028 3.3774C5.14382 3.29918 5.03686 3.29918 4.9704 3.3774L4.21839\
                  4.27247C3.76739 4.81467 3.0354 4.8299 2.56875 4.30679L0.333477 1.81417C0.181838 1.64406 0.132637 1.38111 0.20929 1.15049C0.285944 0.919858 0.472967 0.768142 0.681343 0.767548V0.76671Z" fill="#C9291F"/>'
                                    
                document.getElementById("average_queue_time_data_rate").innerHTML = svg_html;
                document.getElementById("percentage_change_average_queue_time").innerHTML = avg_q_time_per_change + "%";
                document.getElementById("percentage_change_average_queue_time").style.setProperty('color', '#C9291F', 'important');
                document.getElementById("average_queue_time_data_rate").style.display = "unset";
                    
            }
        }
        }catch(err){
            console.log(err)
        }
        
}

function is_filter_applied() {
    let start_datetime = get_url_vars()['start_date'];

    if (start_datetime) return true;

    return  false;
}

//////////////////////////////// Livechat continous end /////////////////////////////////////////

//////////////////////////////// Livechat Hourly Interaction Analytics start /////////////////////////////////////////

function submit_hourly_interaction_report_filter() {

    let selected_bot_pk = $("#select-bot-name").val();
    let selected_channel = $("#livechat-hourly-analytics-select-channel").val();
    let selected_category = $("#livechat-hourly-analytics-select-category").val();
    let selected_source = $("#livechat-hourly-analytics-select-source").val();
    if(!selected_channel || selected_channel.length == 0) {
        showToast("Please select atleast one channel", 4000);
        return;        
    }
    if(!selected_category || selected_category.length == 0){
        showToast("Please select atleast one category", 4000);
        return;        
    }
    if(!selected_source || selected_source.length == 0){
        showToast("Please select atleast one source", 4000);
        return;        
    }

    $("#apply-filter-interaction-report").modal("hide");

    set_livechat_hourly_interaction_filter_in_local_storage(selected_bot_pk, selected_channel, selected_category, selected_source);
    livechat_hourly_interactions_update();
}

function set_livechat_hourly_interaction_filter_in_local_storage(selected_bot_pk, selected_channel, selected_category, selected_source){
    localStorage.setItem(`livechat_hourly_interaction_bot`, selected_bot_pk);
    localStorage.setItem(`livechat_hourly_interaction_channel`, selected_channel);
    localStorage.setItem(`livechat_hourly_interaction_category`, selected_category);
    localStorage.setItem(`livechat_hourly_interaction_source`, selected_source);
}

function unset_livechat_hourly_interaction_filter_in_local_storage(){
    localStorage.removeItem(`livechat_hourly_interaction_bot`);
    localStorage.removeItem(`livechat_hourly_interaction_channel`);
    localStorage.removeItem(`livechat_hourly_interaction_category`);
    localStorage.removeItem(`livechat_hourly_interaction_source`);
}

function livechat_hourly_interactions_update() {

    update_cumulative_peak_hours_analytics_graph();
    update_daily_peak_hour_analytics_graph_and_data_table();
}

export function update_cumulative_peak_hours_analytics_graph(){

    let bot_pk = localStorage.getItem(`livechat_hourly_interaction_bot`);
    let channel = localStorage.getItem(`livechat_hourly_interaction_channel`);
    let category = localStorage.getItem(`livechat_hourly_interaction_category`);
    let source = localStorage.getItem(`livechat_hourly_interaction_source`);
    let range_start_date = $("#cumulative-peak-hours-analytic-start-date").val().trim();
    let range_end_date = $("#cumulative-peak-hours-analytic-end-date").val().trim();

    range_start_date = change_date_format_original(range_start_date)
    range_end_date = change_date_format_original(range_end_date)

    if (
        range_start_date == "" ||
        range_end_date == "" ||
        !is_valid_date(range_start_date) ||
        !is_valid_date(range_end_date)
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    let range_start_datetime = new Date(range_start_date);
    let range_end_datetime = new Date(range_end_date);
    if (range_start_datetime > range_end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    let curr_date = new Date();

    if (range_start_datetime.setHours(0,0,0,0) > curr_date.setHours(0,0,0,0)){
        showToast("Start Date should be less than Current Date", 4000);
        return;
    }

    if (range_end_datetime.setHours(0,0,0,0) > curr_date.setHours(0,0,0,0)){
        showToast("End Date should be less than Current Date", 4000);
        return;
    }
    
    if (range_start_datetime.setHours(0,0,0,0) == curr_date.setHours(0,0,0,0) && 
        range_end_datetime.setHours(0,0,0,0) == curr_date.setHours(0,0,0,0)
    ){
        showToast("For only current date, please refer Daily Peak Hours Analytics graph", 4000);
        return;
    }

    let json_string = JSON.stringify({
        bot_pk: bot_pk,
        channel: channel,
        category: category,
        source: source,
        range_start_date: range_start_date,
        range_end_date: range_end_date
    });

    json_string = EncryptVariable(json_string);
    let CSRF_TOKEN = getCsrfToken();
    Chart.helpers.each(Chart.instances, function (instance) {
        if (instance.canvas.id === "cumulative-peak-hours-analytics-graph") {
            instance.destroy();
            return;
        }
    });
    document.getElementById("cumulative-peak-hour-analytic-selected-days").style.display="none";
    document.getElementById("livechat_average_peak_hours_graph_loader").style.display="block";
    
    $.ajax({
        url: "/livechat/hourly-interaction-cumulative-count-by-date-range/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                render_cumulative_peak_hours_analytics_graph("cumulative-peak-hours-analytics-graph", response["peak_hours_cumulative_graph_data"]);
                document.getElementById("livechat_average_peak_hours_graph_loader").style.display="none";
                document.getElementById("cumulative-peak-hour-analytic-selected-days").style.display="block";
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

export function update_daily_peak_hour_analytics_graph_and_data_table(change="NA"){

    let bot_pk = localStorage.getItem(`livechat_hourly_interaction_bot`);
    let channel = localStorage.getItem(`livechat_hourly_interaction_channel`);
    let category = localStorage.getItem(`livechat_hourly_interaction_category`);
    let source = localStorage.getItem(`livechat_hourly_interaction_source`);
    
    let selected_date = $("#peak-hours-analytic-date-input").val().trim();
    selected_date = change_date_format_original(selected_date);

    if (
        selected_date == "" ||
        !is_valid_date(selected_date)
    ) {
        showToast("Please enter valid date", 4000);
        return;
    }

    let selected_datetime = new Date(selected_date);
    let curr_date = new Date();

    if (selected_datetime.setHours(0,0,0,0) > curr_date.setHours(0,0,0,0)){
        showToast("Selected Date should be less than Current Date", 4000);
        return;
    }

    let json_string = JSON.stringify({
        bot_pk: bot_pk,
        channel: channel,
        category: category,
        source: source,
        selected_date: selected_date,
    });

    json_string = EncryptVariable(json_string);
    let CSRF_TOKEN = getCsrfToken();
    Chart.helpers.each(Chart.instances, function (instance) {
        if (instance.canvas.id === "peak-hours-analytics-graph") {
            instance.destroy();
            return;
        }
    });
    document.getElementById("livechat_daily_peak_hours_graph_loader").style.display="block";

    $.ajax({
        url: "/livechat/hourly-interaction-count-by-date/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                render_daily_peak_hours_analytics_graph("peak-hours-analytics-graph", response["peak_hours_daily_graph_data"]);
                document.getElementById("livechat_daily_peak_hours_graph_loader").style.display="none";
                render_daily_interaction_count_data_table("hourly-interaction-report-table", response["peak_hours_daily_table_data"]);
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

export function render_daily_peak_hours_analytics_graph(graph_id, daily_graph_data) {

    let chart = state.daily_peak_hour_analytics_graph;
    if(chart) chart.destroy();
    
    let data_list = [];
    let index;
    for (index = 0; index < daily_graph_data['interaction_count_daily_graph_count_data'].length; index++) {
        data_list.push(
            {
                "x": daily_graph_data['interaction_count_daily_graph_label_data'][index],
                "y": daily_graph_data['interaction_count_daily_graph_count_data'][index]
            }
        )

    }
    
    let ctx = document.getElementById(graph_id).getContext('2d');
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: daily_graph_data["interaction_count_daily_graph_label_data"],
            datasets: [{
                label: "Total number of hourly interaction counts",
                data: data_list,
                borderColor: '#10B981',
                borderWidth: 1,
                pointHoverBackgroundColor: "#10B981",
                pointRadius: 0,
                pointHoverRadius: 5,
                pointBorderColor: '#10B981',
                pointBackgroundColor: '#10B981',
                pointBorderWidth: 1
            }]
        },

        options: {
            interaction: {
                mode: 'index',
                intersect: false,
            },
            tension: 0.5,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context){
                            return "Count" + ": " + context.formattedValue
                        }
                    },
                    backgroundColor: '#FFF',
                    titleFont: {
                        size: 12,
                    },
                    titleColor: '#000',
                        bodyColor: '#000',
                    bodyFont: {
                        size: 12,
                    },
                    displayColors: true,
                    borderColor: '#000',
                        borderWidth: 0.1,
                },
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        align: 'start',
                        usePointStyle: true,
                        fontColor: '#333',
                        padding: 20,
                        align: 'start',
                        boxWidth: 9,
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        size: 100,
                        color: '#7B7A7B',
                        fontFamily: "'DM Sans', sans-serif",
                        lineHeight: 13,
                        stepSize: 10,
                    },
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Interaction Count',
                        color: '#7B7A7B',
                        font: {
                        family: "'DM Sans', sans-serif",
                        size: 9,
                        lineHeight: 1.2
                        },
                        padding: 10,
                    },
                    grid: {
                        display: true,
                        color: "#EBEBEB "

                    }
                },
                x: {
                    type: "time",
                
                    time: {
                        minUnit: 'hour',
                        displayFormats: {
                            // hour: 'H' ,      // for 24hr format
                            hour: 'h a',        // for 12hr format
                        },
                        tooltipFormat: 'hh:mm a',
                    },
                    ticks: {
                        source: 'labels',
                        size: 10,
                        color: '#7B7A7B',
                        fontFamily: "'DM Sans', sans-serif",
                        lineHeight: 13
                    },
                
                    grid: {
                        display: true,
                        color: "#EBEBEB "
                    }
                },
                xAxis2: {
                    labels: [daily_graph_data["selected_date"],daily_graph_data["selected_date"]],
                    
                    grid: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                        drawBorder: false,
                        display: false,
                    },
                    ticks: {
                        size: 10,
                        color: ' #000000',
                        fontFamily: "'DM Sans', sans-serif",
                    },
                    title: {
                        display: true,
                        text: 'Time (24hr)',
                        color: '#7B7A7B',
                        font: {
                        family: "'DM Sans', sans-serif",
                        size: 9,
                        lineHeight: 1.2
                        },
                        padding: 10,
                    },
                }
            },

            responsive: true, 
            maintainAspectRatio: false,
        }
    });

    state.daily_peak_hour_analytics_graph = chart;
}

export function render_cumulative_peak_hours_analytics_graph(graph_id, cumulative_graph_data) {

    let cumulative_chart = state.cumulative_peak_hours_analytics_graph;
    if(cumulative_chart) cumulative_chart.destroy();
    
    let top_seven_peak_hours = [];
    let mid_nine_peak_hours = [];
    let least_eight_peak_hours = [];
    let index;
    for (index = 0; index < cumulative_graph_data['interaction_count_cumulative_graph_count_data'].length; index++) {
        if(index >= 0 && index < 7){
            top_seven_peak_hours.push(
                {
                    "x": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["x_axis"],
                    "y": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["y_axis"],
                    "average": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["average"],
                    "count": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["count"],
                    "start_time": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["start_time"],
                    "end_time": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["end_time"]
                }
            )
        }
        else if(index >= 7 && index < 16){
            mid_nine_peak_hours.push(
                {
                    "x": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["x_axis"],
                    "y": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["y_axis"],
                    "average": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["average"],
                    "count": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["count"],
                    "start_time": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["start_time"],
                    "end_time": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["end_time"]
                }
            )
        }
        else if(index >= 16 && index < 24){
            least_eight_peak_hours.push(
                {
                    "x": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["x_axis"],
                    "y": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["y_axis"],
                    "average": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["average"],
                    "count": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["count"],
                    "start_time": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["start_time"],
                    "end_time": cumulative_graph_data['interaction_count_cumulative_graph_count_data'][index]["end_time"]
                }
            )
        }
    }

    
    let ctx = document.getElementById(graph_id).getContext('2d');
    
    cumulative_chart = new Chart(ctx, {
        type: 'bubble',
        data: {
            labels: cumulative_graph_data["interaction_count_cumulative_graph_label_data"],
            datasets: [{
                label: `Top  7 Peak Hours`,
                data: top_seven_peak_hours,
                backgroundColor: '#4991E8',
                hoverRadius: 2,
                clip: false,
                radius: 25
            },
            {
                label: `Mid 9 Peak Hours`,
                data: mid_nine_peak_hours,
                backgroundColor: '#E65932',
                hoverRadius: 2,
                clip: false,
                radius: 20
            },
            {
                label: `Least 8 Peak Hours`,
                data: least_eight_peak_hours,
                backgroundColor: '#EDBF40',
                hoverRadius: 2,
                clip: false,
                radius: 10
            }]
        },
        options: {
            tension: 0.5,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context){
                            let multi_line_tooltip_text = [];
                            multi_line_tooltip_text.push(`Average: ${context.raw.average}`)
                            multi_line_tooltip_text.push(`Count: ${context.raw.count}`)
                            multi_line_tooltip_text.push(`Slot: ${context.raw.start_time} - ${context.raw.end_time}`)
                            return multi_line_tooltip_text;
                        }
                    },
                    backgroundColor: '#FFF',
                    titleFont: {
                        size: 12,
                    },
                    titleColor: '#000',
                        bodyColor: '#000',
                    bodyFont: {
                        size: 12,
                    },
                    displayColors: true,
                    borderColor: '#000',
                        borderWidth: 0.1,
                },
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        align: 'start',
                        usePointStyle: true,
                        fontColor: '#333',
                        padding: 20,
                        align: 'start',
                        boxWidth: 9,
                    }
                }
            },
            scales: {
                x: {
                    min: 0,
                    max: 24,
                    display: false,
                    
                    ticks: {
                        size: 100,
                        color: '#7B7A7B',
                        fontFamily: "'DM Sans', sans-serif",
                        lineHeight: 13,
                        stepSize: 10,
                    },
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Interaction Count',
                        color: '#7B7A7B',
                        font: {
                        family: "'DM Sans', sans-serif",
                        size: 9,
                        lineHeight: 1.2
                        },
                        padding: 10,
                    },
                    grid: {
                        display: true,
                        color: "#EBEBEB "

                    }
                },
                y: {
                    type: "time",
                    display: false,
                
                    time: {
                        minUnit: 'hour',
                        displayFormats: {
                            // hour: 'H' ,      // for 24hr format
                            hour: 'h a',        // for 12hr format
                        },
                        tooltipFormat: 'hh:mm a',
                    },
                    ticks: {
                        source: 'labels',
                        size: 10,
                        color: '#7B7A7B',
                        fontFamily: "'DM Sans', sans-serif",
                        lineHeight: 13
                    },
                
                    grid: {
                        display: true,
                        color: "#EBEBEB "
                    }
                }
            },

            responsive: true, 
            maintainAspectRatio: false,
        }
    });

    let no_of_days = document.getElementById("cumulative-peak-hour-analytic-selected-days");
    no_of_days.innerHTML = `<span>Note: Above graph is calculated on the basis of average for the selected ${cumulative_graph_data["no_of_days_in_range"]} day(s)</span>`
    
    state.cumulative_peak_hours_analytics_graph = cumulative_chart;
}

export function render_daily_interaction_count_data_table(table_id, interaction_count_data) {

    let table_content = document.getElementById(table_id);

    let table_entries = ``;
    let index;
    for (index = 0; index < interaction_count_data.length; index++) {
        table_entries+=`
            <tr role="row">
                <td role="cell">
                ${interaction_count_data[index]["date"]}
                </td>
                <td role="cell">
                ${interaction_count_data[index]["start_time"]}
                </td>
                <td role="cell">
                ${interaction_count_data[index]["end_time"]}
                </td>
                <td role="cell">
                ${interaction_count_data[index]["bot_name"]}
                </td>
                <td role="cell">
                ${interaction_count_data[index]["frequency"]}
                </td>
            </tr

        `
    }

    table_content.innerHTML = 
    `
    <thead role="rowgroup">
              <tr role="row">
                  <th role="columnheader">Date </th>
                  <th role="columnheader">Start Time </th>
                  <th role="columnheader">End Time </th>
                  <th role="columnheader">Bot Name</th>
                  <th role="columnheader">
                    <div class="interaction-count-column-header reorder">
                    Interaction Count
                    <span class="default-sort-icon" id="sorter">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M4.39197 4.60897L6.48447 2.51647C6.62697 2.37397 6.86697 2.37397 7.00947 2.51647L9.10197 4.60897C9.34197 4.84147 9.17697 5.24647 8.83947 5.24647H7.49697V9.75397C7.49697 10.1665 7.15947 10.504 6.74697 10.504C6.33447 10.504 5.99697 10.1665 5.99697 9.75397V5.24647H4.65447C4.31697 5.24647 4.15197 4.84147 4.39197 4.60897ZM11.997 8.25347V12.761H13.347C13.677 12.761 13.8495 13.166 13.6095 13.3985L11.517 15.4835C11.367 15.626 11.1345 15.626 10.9845 15.4835L8.892 13.3985C8.652 13.166 8.817 12.761 9.1545 12.761H10.497V8.25347C10.497 7.84097 10.8345 7.50347 11.247 7.50347C11.6595 7.50347 11.997 7.84097 11.997 8.25347Z" fill="#4D4D4D"/>
                        </svg> 
                    </span>
                    <span class="sort-desc-icon" >
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <g clip-path="url(#clip0_2_6475)">
                            <path d="M4.91842 10.7958V4.7551C4.91842 4.2023 4.55997 3.75 4.12187 3.75C3.68377 3.75 3.32532 4.2023 3.32532 4.7551V10.7958H1.8995C1.54105 10.7958 1.36581 11.3385 1.6207 11.6501L3.84308 14.4443C4.00239 14.6352 4.24932 14.6352 4.40863 14.4443L6.631 11.6501C6.8859 11.3385 6.70269 10.7958 6.35221 10.7958H4.91842Z" fill="#4D4D4D"/>
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M8.25 6C7.975 6 7.5 5.6625 7.5 5.25C7.5 4.8375 7.975 4.5 8.25 4.5H15.75C16.025 4.5 16.5 4.8375 16.5 5.25C16.5 5.6625 16.025 6 15.75 6H8.25ZM8.25 9.75H12.75C12.9333 9.75 13.5 9.4125 13.5 9C13.5 8.5875 12.9333 8.25 12.75 8.25H8.25C8.06667 8.25 7.5 8.5875 7.5 9C7.5 9.4125 8.06667 9.75 8.25 9.75ZM8.25 13.5H10.5C10.6146 13.5 11.25 13.1625 11.25 12.75C11.25 12.3375 10.6146 12 10.5 12H8.25C8.13542 12 7.5 12.3375 7.5 12.75C7.5 13.1625 8.13542 13.5 8.25 13.5Z" fill="#4D4D4D"/>
                            </g>
                            <defs>
                            <clipPath id="clip0_2_6475">
                            <rect width="18" height="18" fill="white"/>
                            </clipPath>
                            </defs>
                        </svg>
                    </span>
                    <span class="sort-asc-icon">
                        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <g clip-path="url(#clip0_2_6550)">
                            <path d="M3.33832 7.53842L3.3131 13.579C3.31079 14.1318 3.66735 14.5856 4.10545 14.5874C4.54355 14.5893 4.90388 14.1385 4.90619 13.5857L4.9314 7.54507L6.35721 7.55103C6.71566 7.55252 6.89316 7.0105 6.63957 6.69786L4.42888 3.89443C4.27037 3.7028 4.02344 3.70177 3.86334 3.89207L1.62932 6.67695C1.37312 6.98746 1.55406 7.53097 1.90454 7.53244L3.33832 7.53842Z" fill="#4D4D4D"/>
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M15.7349 12.0189C16.0099 12.0203 16.4832 12.3602 16.4811 12.7727C16.479 13.1852 16.0023 13.5203 15.7273 13.5189L8.2274 13.481C7.9524 13.4797 7.47911 13.1398 7.4812 12.7273C7.48328 12.3148 7.95998 11.9797 8.23498 11.9811L15.7349 12.0189ZM12.7576 8.2766L8.25764 8.25387C8.07431 8.25294 7.50595 8.58758 7.50386 9.00007C7.50178 9.41257 8.06673 9.75292 8.25007 9.75385L12.75 9.77658C12.9333 9.7775 13.5017 9.44287 13.5038 9.03037C13.5059 8.61788 12.9409 8.27752 12.7576 8.2766ZM10.5039 4.87128L8.25392 4.85992C8.13933 4.85934 7.50222 5.19363 7.50014 5.60612C7.49806 6.01862 8.13176 6.35932 8.24634 6.3599L10.4963 6.37126C10.6109 6.37184 11.248 6.03756 11.2501 5.62506C11.2522 5.21257 10.6185 4.87186 10.5039 4.87128Z" fill="#4D4D4D"/>
                            </g>
                            <defs>
                            <clipPath id="clip0_2_6550">
                            <rect width="18" height="18" fill="white"/>
                            </clipPath>
                            </defs>
                        </svg>
                    </span>
                    
                    </div>
                </th>

              </tr>
          </thead>
          <tbody role="rowgroup">
                    ${table_entries}
          </tbody>
    `

    $('#hourly-interaction-report-table').DataTable({
        // for sorting 
        columnDefs: [{ 
            orderable: true, 
            className: 'reorder',
            targets: 4 
        },
        { 
            orderable: false, 
            targets: '_all' 
        }],
        "language": {
          searchPlaceholder: 'Search',
          search: "",
          "info": `Showing _START_ to _END_ entries out of total ${interaction_count_data.length} entries`,
          "infoEmpty": "No records available",
          "infoFiltered": "(filtered from _MAX_ total records)",
        },
        "bPaginate": false,
        "bDestroy": true,
        "infoCallback": function( settings, start, end, max, total, pre ) {
            if (settings.oPreviousSearch["sSearch"] != ""){
                return pre;
            }
            return `Showing ${interaction_count_data.length} entries out of ${interaction_count_data.length}`;
          }
    });

    let table = $('#hourly-interaction-report-table').DataTable();

    $('#hourly-interaction-report-table-search').keyup(function() {
      let value = this.value;
      table.search(value).draw();
    })

    try {
      document.getElementsByClassName('dataTables_empty')[0].innerHTML = 'No record found';
    } catch (err) {}
    
}

//////////////////////////////// Livechat Hourly Interaction Analytics end /////////////////////////////////////////

//////////////////////////////// Download Livechat Transcripts ///////////////////////////////////

function download_chat_transcript(el) {
    let id = el;
    if (el.dataset) {
        id = el.dataset.id;
    }

    window.location = "/livechat/download-chat-transcript/?pk=" + id;
}

//////////////////////////////  END Livechat Transcripts ///////////////////////////////////////

///////////////////////////// Chat History /////////////////////////////////////////////////////

function submit_filter() {
    var agent_username = $("#select-agent-username").val();
    var chat_status = $("#select-chat-status").val();
    var channel_name = $("#select-channel").val()
    var selected_category_pk = $("#select-category").val()
    var start_date = document.getElementById("chat-history-default-start-date").value.trim();
    var end_date = document.getElementById("chat-history-default-end-date").value.trim();
    start_date = change_date_format_original(start_date)
    end_date = change_date_format_original(end_date)
    if (
        start_date == "" ||
        end_date == "" ||
        !is_valid_date(start_date) ||
        !is_valid_date(end_date)
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(start_date);
    var end_datetime = new Date(end_date);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    agent_username = JSON.stringify(agent_username);
    window.location.href =
        "?agent_username=" +
        agent_username +
        "&channel_name="+
        channel_name+
        "&selected_category_pk="+
        selected_category_pk+
        "&start_date=" +
        start_date +
        "&end_date=" +
        end_date +
        "&chat_status=" +
        chat_status;
}
function close_audit_trail_export_modal() {
    document.getElementById("modal-mis-filter").style.display = "none";
}

function export_mis_filter() {
    let selected_report_type = document.getElementById("select-chat-history-report-type").value;

    if (selected_report_type == "0") {
        alert("Please select valid report type");
        return;        
    }

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-filter-default-start-date").val().trim();
    let enddate = $("#export-filter-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email");
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if (
        (selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) &&
        validate_email("filter-data-email") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    var json_string = JSON.stringify({
        selected_report_type: selected_report_type,
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_report_type: selected_report_type,
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if(response["export_path"] == "request_saved") {
                    showToast("We have saved your request and will send data over provided email ID in a short period.", 5000);
                    close_audit_trail_export_modal();
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast(
                        "We haved saved your request and will send data over provided email ID within 24 hours.",
                        5000
                    );
                    close_audit_trail_export_modal();
                }else if(response["export_path"] == "request_saved_today") {
                    showToast("We have saved your request and will send data over provided email ID within 5 mins.", 5000);
                    close_audit_trail_export_modal();
                } else if (response["export_path"] == "conversation_request_saved") {
                    alert(
                        "We have saved your data and shall provide you with the enquired report within 1 hour over your email ID."
                    );
                    close_audit_trail_export_modal();
                } 
                else {
                    if (response["export_path_exist"]) {
                        
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                     }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function abandoned_chats_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;
    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if (
        (selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) &&
        validate_email("filter-data-email-export") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/offline-chats-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast(
                        "We have saved your request and will send data over provided email ID in a short period.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast(
                        "We haved saved your request and will send data over provided email ID within 24 hours.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email-export").value = "";
                    document.getElementById("select-date-range-export").value = "0";
                    $("#modal-report-filter").modal("hide");
                } else {
                    console.log(response["export_path_exist"])
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function total_declined_chats_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;
    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if (
        (selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) &&
        validate_email("filter-data-email-export") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/abandoned-chats-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast(
                        "We have saved your request and will send data over provided email ID in a short period.",
                        5000
                    );
                    
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast("We haved saved your request and will send data over provided email ID within 24 hours.", 5000);
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email-export").value = "";
                    document.getElementById("select-date-range-export").value = "0";
                    $("#modal-report-filter").modal("hide");
                } else {
                    console.log(response["export_path_exist"])
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function offline_message_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;
    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if (
        (selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) &&
        validate_email("filter-data-email-export") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/missed-chats-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast(
                        "We have saved your request and will send data over provided email ID in a short period.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast(
                        "We haved saved your request and will send data over provided email ID within 24 hours.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email-export").value = "";
                    document.getElementById("select-date-range-export").value = "0";
                    $("#modal-report-filter").modal("hide");
                }  else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

/////////////////////////////////// Chat history ends ///////////////////////////////////////////

/////////////////////////////////// Offline message history starts ///////////////////////////////////////////
function submit_offline_or_abandoned_or_declined_message_report_filter() {
    let startdate = $("#start-date").val().trim();
    let enddate = $("#end-date").val().trim();

    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate)) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    let selected_pk = $("#select-category").val();
    let channel_name = $("#select-channel").val();
    window.location.href =
        "?start_date=" +
        startdate +
        "&channel_name=" +
        channel_name +
        "&end_date=" +
        enddate +
        "&selected_category_pk=" +
        selected_pk;
}

/////////////////////////////////// Offline message history ends ///////////////////////////////////////////

function login_logout_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if (
        (selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) &&
        validate_email("filter-data-email-export") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/login-logout-report-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast("We have saved your request and will send data over provided email ID in a short period.", 5000);
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast("We haved saved your request and will send data over provided email ID within 24 hours.", 5000);
                    $("#modal-report-filter").modal("hide");
                } else if(response["export_path"] == "request_saved_today") {
                    showToast("We have saved your request and will send data over provided email ID within 5 mins.", 5000);
                    $("#modal-report-filter").modal("hide");
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email-export").value = "";
                    document.getElementById("select-date-range-export").value = "0";
                }  else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function apply_reports_filter() {
    let path = window.location.pathname;
    if (path == "/livechat/login-logout-report/") {
        submit_session_report_filter();
    } else if (path == "/livechat/agent-performance-report/") {
        submit_agent_performance_report_filter();
    } else if (path == "/livechat/daily-interaction-count/") {
        submit_daily_interaction_report_filter();
    } else if (path == "/livechat/hourly-interaction-count/") {
        submit_hourly_interaction_report_filter();
    } else if (path == "/livechat/agent-not-ready-report/") {
        submit_agent_not_ready_report_filter();
    }
}

function export_reports_filter() {
    let path = window.location.pathname;
    if (path == "/livechat/login-logout-report/") {
        login_logout_report_filter();
    } else if (path == "/livechat/agent-performance-report/") {
        agent_performance_report_filter();
    } else if (path == "/livechat/hourly-interaction-count/") {
        hourly_interaction_report_filter();
    } else if (path == "/livechat/agent-not-ready-report/") {
        agent_not_ready_report_filter();
    }
}

function submit_session_report_filter() {
    let startdate = $("#start-date").val().trim();
    let enddate = $("#end-date").val().trim();

    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate)) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    let selected_pk = $("#select-agent").val();

    let selected_supervisors = [];
    if(window.USER_STATUS == '1') {
        selected_supervisors = $("#supervisor-select-dropdown-login-logout").val();
    }
    selected_supervisors = JSON.stringify(selected_supervisors);

    window.location.href =
        "?start_date=" + startdate + "&end_date=" + enddate + "&selected_agent_pk=" + selected_pk + "&selected_supervisors=" + selected_supervisors;
}

// ********************   Agent not ready report  ******************************

function agent_not_ready_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if (
        (selected_filter_value == "4"  || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) &&
        validate_email("filter-data-email-export") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/agent-not-ready-report-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast("We have saved your request and will send data over provided email ID in a short period.", 5000);
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast("We haved saved your request and will send data over provided email ID within 24 hours.", 5000);
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email-export").value = "";
                    document.getElementById("select-date-range-export").value = "0";
                    $("#modal-report-filter").modal("hide");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function submit_agent_not_ready_report_filter() {
    let startdate = $("#start-date").val().trim();
    let enddate = $("#end-date").val().trim();

    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate)) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    let selected_pk = $("#select-agent").val();

    let selected_supervisors = [];
    if(window.USER_STATUS == '1') {
        selected_supervisors = $("#supervisor-select-dropdown-not-ready").val();
    }
    selected_supervisors = JSON.stringify(selected_supervisors);

    window.location.href =
        "?start_date=" + startdate + "&end_date=" + enddate + "&selected_agent_pk=" + selected_pk + "&selected_supervisors=" + selected_supervisors;
}

// ********************   Agent performance report  ******************************

function agent_performance_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if ((selected_filter_value == "4" || (selected_filter_value == "5" && !window.IS_REPORT_GENERATION_VIA_KAFKA_ENABLED)) && validate_email("filter-data-email-export") == false) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/agent-performance-report-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    showToast("We have saved your request and will send data over provided email ID in a short period.", 5000);
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast(
                        "We haved saved your request and will send data over provided email ID within 24 hours.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    document.getElementById("custom-range-filter-email").style.display = "none";
                    document.getElementById("filter-data-email-export").value = "";
                    document.getElementById("select-date-range-export").value = "0";
                    $("#modal-report-filter").modal("hide");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function submit_agent_performance_report_filter() {
    let startdate = $("#start-date").val().trim();
    let enddate = $("#end-date").val().trim();

    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    if (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate)) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    let selected_pk = $("#select-agent").val();
    selected_pk = JSON.stringify(selected_pk);

    let selected_supervisors = [];
    if(window.USER_STATUS == '1') {
        selected_supervisors = $("#supervisor-select-dropdown-performance").val(); 
    }
    selected_supervisors = JSON.stringify(selected_supervisors);

    window.location.href =
        "?start_date=" + startdate + "&end_date=" + enddate + "&selected_agent_pk=" + selected_pk + "&selected_supervisors=" + selected_supervisors;
}

// ********************   Agent Daily Interaction report  ******************************

function daily_interaction_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-daily").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-filter-daily-default-start-date").val().trim();
    let enddate = $("#export-filter-daily-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-daily");

    if (
        (selected_filter_value == "4" || selected_filter_value == "5") &&
        validate_email("filter-data-email-daily") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/dailey-interaction-count-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 24 hours.",
                        5000
                    );
                    $("#modal-daily-interaction-report-filter").modal("hide");
                }  else if (response["export_path"] == "request_saved_custom") {
                    showToast(
                        "We have saved your request and will send data over provided email ID in a short period.",
                        5000
                    );
                    $("#modal-daily-interaction-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        4000
                    );
                    $("#modal-daily-interaction-report-filter").modal("hide");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function submit_daily_interaction_report_filter() {
    let startdate = $("#interaction-report-start-date").val().trim();
    let enddate = $("#livechat-interaction-report-end-date").val().trim();

    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate)) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    let selected_pk = $("#select-bot-name").val();
    window.location.href =
        "?start_date=" + startdate + "&end_date=" + enddate + "&selected_bot_pk=" + selected_pk;
}

// ********************   Agent Hourly Interaction report  ******************************

function hourly_interaction_report_filter() {
    let selected_filter_value = document.getElementById("select-date-range-export").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    if (
        (selected_filter_value == "4" || selected_filter_value == "5") &&
        validate_email("filter-data-email-export") == false
    ) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
    });
    if (selected_filter_value == "5") {
        var json_string = JSON.stringify({
            selected_filter_value: selected_filter_value,
            email: email_field.value,
        });
    }
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/hourly-interaction-count-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved_custom_range") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 24 hours.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else if (response["export_path"] == "request_saved_custom") {
                    showToast(
                        "We have saved your request and will send data over provided email ID in a short period.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                }  else if (response["export_path"] == "request_saved_today") {
                    showToast(
                        "We have saved your request and will send data over provided email ID within 5 mins.",
                        5000
                    );
                    $("#modal-report-filter").modal("hide");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}



function submit_livechat_analytics_filter() {
    let startdate = $("#analytics-start-date").val().trim();
    let enddate = $("#analytics-end-date").val().trim();
    let channel = $("#livechat-analytics-channel").val().trim();
    let category_pk_list = $("#category-select-dropdown-combined-analytics").val();
    let supervisors_list = $("#supervisor-select-dropdown-combined-analytics").val();

    if(category_pk_list.length == 0){
        showToast("Please select atleast one category.", 2000);
        return;
    }

    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)

    if (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate)) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    if(!channel) {
        showToast("Please select channel", 4000);
        return;        
    }

    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    let curr_date = new Date();
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }
    if (end_datetime.setHours(0,0,0,0) > curr_date.setHours(0,0,0,0)){
        showToast("End Date should be less than Current Date", 4000);
        return;
    }
    $("#apply-filter-analytics").modal("hide");
    livechat_analytics_charts_update(startdate, enddate, channel, category_pk_list, supervisors_list, true)
    set_livechat_filter_in_local_storage(startdate, enddate, channel, category_pk_list, supervisors_list);
    
}
function load_livechat_analytics_all_charts(){
    let start_date = localStorage.getItem(`livechat_analytics_start_date`, start_date);
    let end_date = localStorage.getItem(`livechat_analytics_end_date`, end_date);
    let channel = localStorage.getItem(`livechat_analytics_channel`);
    let category_pk_list = localStorage.getItem(`livechat_analytics_category`);
    let supervisors_list = localStorage.getItem(`livechat_analytics_supervisors_list`);

    if(category_pk_list){
        category_pk_list = category_pk_list.toString().split(',');
    }

    if(supervisors_list){
        supervisors_list = supervisors_list.toString().split(',');
    }

    let is_filter_present = false
    if(start_date){
        is_filter_present = true
        let start_datetime = change_date_format_original(start_date)
        let end_datetime = change_date_format_original(end_date)
        $('#analytics-start-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(start_datetime.trim());
        $('#analytics-end-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(end_datetime.trim());
        $('#export-default-start-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(start_datetime.trim());
        $('#export-default-end-date').datepicker({ dateFormat: 'dd-mm-yy',prevText: "Previous" }).val(end_datetime.trim());
        livechat_analytics_charts_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present);
    }
    else{

        let start_date_initial = $("#analytics-start-date").val().trim();
        let end_date_initial = $("#analytics-end-date").val().trim();
        let channel_initial = $("#livechat-analytics-channel").val().trim();
        let category_pk_list_initial = $("#category-select-dropdown-combined-analytics").val();
        let supervisors_list_initial = $("#supervisor-select-dropdown-combined-analytics").val();
        start_date_initial = change_date_format_original(start_date_initial);
        end_date_initial = change_date_format_original(end_date_initial);    
        livechat_analytics_charts_update(start_date_initial, end_date_initial, channel_initial, category_pk_list_initial, supervisors_list_initial, true);
    }
    
}
function set_livechat_filter_in_local_storage(start_date, end_date, channel, category_pk_list, supervisors_list){
    localStorage.setItem(`livechat_analytics_start_date`, start_date);
    localStorage.setItem(`livechat_analytics_end_date`, end_date);
    localStorage.setItem(`livechat_analytics_channel`, channel);
    localStorage.setItem(`livechat_analytics_category`, category_pk_list);
    localStorage.setItem(`livechat_analytics_supervisors_list`, supervisors_list);
}
function unset_livechat_filter_in_local_storage(){
    localStorage.removeItem(`livechat_analytics_start_date`);
    localStorage.removeItem(`livechat_analytics_end_date`);
    localStorage.removeItem(`livechat_analytics_channel`);
    localStorage.removeItem(`livechat_analytics_category`);
    localStorage.removeItem(`livechat_analytics_supervisors_list`);
    localStorage.removeItem(`livechat_live_analytics_channel`);
    localStorage.removeItem(`livechat_live_analytics_category`);
    localStorage.removeItem(`livechat_live_analytics_supervisors_list`);
}

function analytics_filter() {
    
    let selected_filter_value = document.getElementById("select-date-range-export").value;

    if (selected_filter_value == "0") {
        alert("Please select valid date range filter");
        return;
    }

    let startdate = $("#export-default-start-date").val().trim();
    let enddate = $("#export-default-end-date").val().trim();
    let email_field = document.getElementById("filter-data-email-export");

    let category_pk_list = $("#category-select-dropdown-combined-analytics-export").val();

    if(selected_filter_value == "4" && category_pk_list.length == 0){
        showToast("Please select atleast one category.", 2000);
        return;
    }

    if (selected_filter_value == "4" && validate_email("filter-data-email-export") == false) {
        showToast("Please enter valid email ID", 4000);
        return;
    }

    if (
        selected_filter_value == "4" &&
        (startdate == "" || enddate == "" || !is_valid_date(startdate) || !is_valid_date(enddate))
    ) {
        showToast("Please enter valid dates", 4000);
        return;
    }
    startdate = change_date_format_original(startdate)
    enddate = change_date_format_original(enddate)
    var start_datetime = new Date(startdate);
    var end_datetime = new Date(enddate);
    if (start_datetime > end_datetime) {
        showToast("Start Date should be less than End Date", 4000);
        return;
    }

    var json_string = JSON.stringify({
        selected_filter_value: selected_filter_value,
        startdate: startdate,
        enddate: enddate,
        email: email_field.value,
        category_pk_list: category_pk_list,
    });
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();

    $.ajax({
        url: "/livechat/analytics-exportdata/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function (response) {
            var response = custom_decrypt(response);
            response = JSON.parse(response);
            if ((response["status"] = 200)) {
                if (response["export_path"] == null) {
                    alert("Sorry, unable to process your request. Kindly try again later.");
                } else if (response["export_path"] == "request_saved") {
                    alert(
                        "We haved saved your request and will send data over provided email ID within 24 hours."
                    );
                    $("#modal-report-filter").modal("hide");
                } else {
                    if (response["export_path_exist"]) {
                        window.open(response["export_path"], "_blank");
                    } else {
                        alert("Requested data doesn't exists. Kindly try again later.");
                    }
                }
            }
        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function destroy_previous_instances_of_combined_charts(){
    
    Chart.helpers.each(Chart.instances, function (instance) {
        if(instance.canvas.id != "live_analytics_chat_termination_graph") {  
            instance.destroy();
        }
    });
}
function livechat_analytics_charts_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present){
    destroy_previous_instances_of_combined_charts();
    livechat_chat_history_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present);
    livechat_avg_nps_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present);
    livechat_avg_handle_time_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present);
    livechat_avg_queue_time_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present);
    livechat_interactions_per_chat_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present);
}

function submit_livechat_live_analytics_filter() {
    let channel = $("#livechat-live-analytics-channel").val().trim();

    let category = $("#category-select-dropdown-analytics").val();

    let supervisors_list = $("#supervisor-select-dropdown-analytics").val();

    if(!channel) {
        showToast("Please select channel", 4000);
        return;        
    }

    if(category.length == 0){
        showToast("Please select atleast one category.", 4000);
        return;        
    }

    $("#apply-filter-live-analytics").modal("hide");

    set_livechat_live_filter_in_local_storage(channel, category, supervisors_list);  
    livechat_continous_update();
}

function set_livechat_live_filter_in_local_storage(channel, category, supervisors_list){
    localStorage.setItem(`livechat_live_analytics_channel`, channel);
    localStorage.setItem(`livechat_live_analytics_category`, category);
    localStorage.setItem(`livechat_live_analytics_supervisors_list`, supervisors_list);
}

function get_and_update_categories_dropdown(elem) {
        let supervisors_list = $("#" + elem.id).val();
        let anaytics_type = $("#" + elem.id).data("analytics-type");
        let category_id = $("#" + elem.id).data("category-id");

        if (anaytics_type == "live") {
            state.selected_live_analytics_supervisor = supervisors_list;
        } else if (anaytics_type == "combined") {
            state.selected_combined_analytics_supervisor = supervisors_list;
        }

        let json_string = {
            supervisors_list: supervisors_list,
        };

        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-categories-from-supervisors/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                if(response.status == 200) {
                    
                    let elem = document.getElementById(category_id);
                    elem.innerHTML = "";

                    let category_data = response.category_data;
                    category_data.forEach(category => {
                        elem.append(new Option(category.name, category.pk));
                    });
                    
                    $(`#${category_id}`).multiselect('selectAll', false);
                    $(`#${category_id}`).multiselect('rebuild');
                    refresh_custom_checkbox_dropdown();
                }
            })       
            .catch((err) => {
                console.log(err);
            });

}

function get_and_update_agents_dropdown(elem, is_multiselect=true) {
        let supervisors_list = $("#" + elem.id).val();
        let agent_id = $("#" + elem.id).data("agent-id");

        let json_string = {
            supervisors_list: supervisors_list,
        };

        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-agents-from-supervisors/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                if(response.status == 200) {
                    
                    let elem = document.getElementById(agent_id);
                    elem.innerHTML = "";
                    
                    let agents_data = response.agents_data;
                    if(!is_multiselect && agents_data.length) {
                        elem.append(new Option('All', 0));
                    }

                    agents_data.forEach(agent => {
                        elem.append(new Option(agent.username, agent.pk));
                    });
                    
                    if(is_multiselect) {

                        if(state.is_initial_refresh) {
                            let selected_agents = JSON.parse(window.SELECTED_AGENTS);

                            selected_agents.forEach(agent => {
                                $('#select-agent option[value="'+agent+'"]').prop('selected', true);
                            });
                            state.is_initial_refresh = false;
                        }
                        $(`#${agent_id}`).multiselect('rebuild');
                        refresh_custom_checkbox_dropdown();

                    } else {
                        if(state.is_initial_refresh) {
                            document.getElementById(agent_id).value = state.selected_agent_pk;
                            state.is_initial_refresh = false;
                        }

                        $(`#${agent_id}`).selectpicker('refresh');
                    }                    

                }
            })       
            .catch((err) => {
                console.log(err);
            });

}

function get_and_update_supervisors_dropdown(elem) {
        let category_list = $("#" + elem.id).val();
        let anaytics_type = $("#" + elem.id).data("analytics-type");
        let supervisor_id = $("#" + elem.id).data("supervisor-id");

        let selected_supervisors = [];
        if (anaytics_type == "live") {
            selected_supervisors = state.selected_live_analytics_supervisor;
        } else if (anaytics_type == "combined") {
            selected_supervisors = state.selected_combined_analytics_supervisor;
        }

        let json_string = {
            category_list: category_list,
        };

        json_string = JSON.stringify(json_string);
        const params = get_params(json_string);

        let config = {
              headers: {
                'X-CSRFToken': getCsrfToken(),
              }
            }

        axios
            .post("/livechat/get-supervisors-from-categories/", params, config)
            .then((response) => {
                response = custom_decrypt(response.data);
                response = JSON.parse(response);
                if(response.status == 200) {
                    
                    let elem = document.getElementById(supervisor_id);
                    elem.innerHTML = "";

                    let supervisor_data = response.supervisor_data;
                    supervisor_data.forEach(supervisor => {
                        elem.append(new Option(supervisor.username, supervisor.pk));
                    });
                    
                    selected_supervisors.forEach(supervisor => {
                        $('#'+supervisor_id+' option[value="'+supervisor+'"]').prop('selected', true);
                    });
                    $(`#${supervisor_id}`).multiselect('rebuild');

                    refresh_custom_checkbox_dropdown();

                }
            })       
            .catch((err) => {
                console.log(err);
            });

}

function refresh_custom_checkbox_dropdown() {
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li>a>label").addClass("custom-checkbox-input");
    $(".livechat-multiselect-dropdown.livechat-multiselect-filter-dropdown .multiselect-container>li").find(".custom-checkbox-input").append("<span class='checkmark'></span>");
}

export {
    livechat_continous_update,
    download_chat_transcript,
    submit_filter,
    export_mis_filter,
    offline_message_report_filter,
    submit_offline_or_abandoned_or_declined_message_report_filter,
    login_logout_report_filter,
    apply_reports_filter,
    export_reports_filter,
    submit_session_report_filter,
    agent_not_ready_report_filter,
    submit_agent_not_ready_report_filter,
    agent_performance_report_filter,
    submit_agent_performance_report_filter,
    daily_interaction_report_filter,
    submit_daily_interaction_report_filter,
    hourly_interaction_report_filter,
    submit_hourly_interaction_report_filter,
    submit_livechat_analytics_filter,
    analytics_filter,
    load_livechat_analytics_all_charts,
    unset_livechat_filter_in_local_storage,
    abandoned_chats_report_filter,
    total_declined_chats_report_filter,
    submit_livechat_live_analytics_filter,
};
