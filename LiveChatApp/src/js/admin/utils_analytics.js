import {
    change_date_format_original,
    is_valid_date,
    custom_decrypt,
    EncryptVariable,
    showToast,
    getCsrfToken,
} from "../utils";

import {
    render_chat_termination_graph,
    render_source_statistics_graph,
} from "./analytics";


function update_chat_report_widgets_data(total_entered_chat, total_closed_chat, denied_chats, abandon_chats, customer_declined_chats, voice_calls_initiated, avg_call_duration, avg_video_call_duration, total_tickets_raised, avg_cobrowsing_duration, total_customers_reported, followup_leads_via_email, avg_first_time_response){

    document.getElementById("total_entered_chat").innerHTML = total_entered_chat
    document.getElementById("total_closed_chat").innerHTML = total_closed_chat
    document.getElementById("denied_chats").innerHTML = denied_chats
    document.getElementById("abandon_chats").innerHTML = abandon_chats
    document.getElementById("customer_declined_chats").innerHTML = customer_declined_chats
    
    if (document.getElementById('voice_calls_initiated')) {
        document.getElementById('voice_calls_initiated').innerHTML = voice_calls_initiated;
    }

    if (document.getElementById('avg_call_duration')) {
        document.getElementById('avg_call_duration').innerHTML = avg_call_duration;
    }

    if (document.getElementById('avg_video_call_duration')) {
        document.getElementById('avg_video_call_duration').innerHTML = avg_video_call_duration;
    }

    if (document.getElementById('avg_cobrowsing_duration')) {
        document.getElementById('avg_cobrowsing_duration').innerHTML = avg_cobrowsing_duration;
    }

    if(document.getElementById("total_tickets_raised")) {
        document.getElementById("total_tickets_raised").innerHTML = total_tickets_raised;
    }

    if(document.getElementById("total_customers_reported")) {
        document.getElementById("total_customers_reported").innerHTML = total_customers_reported;
    }

    if(document.getElementById("followup-leads-via-email")) {
        document.getElementById("followup-leads-via-email").innerHTML = followup_leads_via_email;
    }

    if(document.getElementById("average_first_time_response")) {
        document.getElementById("average_first_time_response").innerHTML = avg_first_time_response;
    }
}

function hide_chat_reports_percentage_diff(){
    try{
        $('.chat-report-card-data-rate').hide();
    }catch(err){}
}
function hide_customer_reports_percentage_diff(){
    try{
        $('.customer-report-card-data-rate').hide();
    }catch(err){}
}
function livechat_chat_history_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present){

    var json_string = JSON.stringify({
        start_date:start_date,
        end_date:end_date,
        is_filter_present:is_filter_present,
        channel: channel,
        category_pk_list: category_pk_list,
        supervisors_list: supervisors_list,
    });
    document.getElementById("livechat_analytics_chat_report_loader").style.display="block";
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/get-chart-report-analytics/",
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
            
                add_livechat_report_chart(response["livechat_history_list"])
                document.getElementById("livechat_analytics_chat_report_loader").style.display="none";
                if(is_filter_present){
                    update_chat_report_widgets_data(response["total_entered_chat"],response["total_closed_chat"],
                    response['denied_chats'], response['abandon_chats'], response['customer_declined_chats'], response['voice_calls_initiated'], 
                    response['avg_call_duration'], response['avg_video_call_duration'], response['total_tickets_raised'], 
                    response['avg_cobrowsing_duration'], response['total_customers_reported'], response['followup_leads_via_email'], response['avg_first_time_response'])
                    hide_chat_reports_percentage_diff()
                }
                if(document.getElementById("combined_analytics_chat_termination_graph")) {
                    render_chat_termination_graph("combined_analytics_chat_termination_graph", response["chat_termination_data"], "combined");
                }
                render_source_statistics_graph("combined_analytics_source_statistics_graph", response["source_of_incoming_request_data"]);
            }

        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
   
    
}
function livechat_avg_nps_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present){

    document.getElementById("livechat_analytics_avg_nps_loader").style.display="block";
    var json_string = JSON.stringify({
        start_date:start_date,
        end_date:end_date,
        is_filter_present:is_filter_present,
        channel: channel,
        category_pk_list: category_pk_list,
        supervisors_list: supervisors_list,
    });
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/get-avg-nps-analytics/",
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
            
             add_nps_report_chart(response["livechat_avg_nps_list"])
             document.getElementById("livechat_analytics_avg_nps_loader").style.display="none";
             if(is_filter_present){
                document.getElementById("nps_avg").innerHTML = response["avg_nps"]
                hide_customer_reports_percentage_diff();
             }

            }

        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function livechat_avg_handle_time_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present){

    document.getElementById("livechat_avg_handle_time_loader").style.display="block";
    
    var json_string = JSON.stringify({
        start_date:start_date,
        end_date:end_date,
        is_filter_present:is_filter_present,
        channel: channel,
        category_pk_list: category_pk_list,
        supervisors_list: supervisors_list,
    });
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/get-avg-handle-time-analytics/",
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
             add_livechat_avg_handle_time_chart(response["livechat_avg_handle_time_list"])
             document.getElementById("livechat_avg_handle_time_loader").style.display="none";
             if(is_filter_present){
                document.getElementById("average_handle_time").innerHTML = response["avg_handle_time"]
                hide_customer_reports_percentage_diff();
             }
            }

        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function livechat_avg_queue_time_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present){

    document.getElementById("livechat_waittime_graph_loader").style.display="block";
    
    var json_string = JSON.stringify({
        start_date:start_date,
        end_date:end_date,
        is_filter_present:is_filter_present,
        channel: channel,
        category_pk_list: category_pk_list,
        supervisors_list: supervisors_list,
    });
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/get-avg-queue-time-analytics/",
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
             add_livechat_avg_queue_time_chart(response["livechat_avg_queue_time_list"]);
             document.getElementById("livechat_waittime_graph_loader").style.display="none";
             if(is_filter_present){
                document.getElementById("customer_waittime").innerHTML = response["average_queue_time_live"];
                hide_customer_reports_percentage_diff();
             }
            }

        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}
function livechat_interactions_per_chat_report_update(start_date, end_date, channel, category_pk_list, supervisors_list, is_filter_present){

    document.getElementById("livechat_interactions_per_chat_loader").style.display="block";       

    var json_string = JSON.stringify({
        start_date:start_date,
        end_date:end_date,
        is_filter_present:is_filter_present,
        channel: channel,
        category_pk_list: category_pk_list,
        supervisors_list: supervisors_list,
    });
    json_string = EncryptVariable(json_string);
    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/get-interactions-per-chat-analytics/",
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

             add_interaction_per_chat_chart(response["livechat_interactions_per_chat_list"])
             document.getElementById("livechat_interactions_per_chat_loader").style.display="none";

             if(is_filter_present){
                document.getElementById("average_interactions").innerHTML = response["interactions_per_chat"]
                hide_customer_reports_percentage_diff();
             }
            }

        },
        error: function (xhr, textstatus, errorthrown) {
            console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
        },
    });
}

function add_livechat_report_chart(chat_history_list){

    let labels = [];
    let total_chat_raised = [];
    let total_chats_resolved = [];
    let total_declined_chats = [];
    let offline_chats = [];
    let abandoned_chats = [];
    let point_radius= 0;
    for(let i =0 ;i <chat_history_list.length;i++ ){
        labels.push(chat_history_list[i]['label'])
        total_chat_raised.push(chat_history_list[i]['total_entered_chat'])
        total_chats_resolved.push(chat_history_list[i]['total_closed_chat'])
        total_declined_chats.push(chat_history_list[i]['customer_declined_chats'])
        offline_chats.push(chat_history_list[i]['denied_chats'])
        abandoned_chats.push(chat_history_list[i]['abandon_chats'])
    }  
    if(chat_history_list.length == 1){
        point_radius = 2;
    }
    let min_rotation =  0;
    if(chat_history_list.length>12){
        min_rotation = 10;// if data points were 12 ,13 the x axis labels were a bit conjusted so for that case added some angle in labels
    }
    var ctx = document.getElementById("chats_report_graph").getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                    label: 'Total Chats Raised', // Name the series
                    data: total_chat_raised,
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(18, 100, 231, 1)',
                    borderColor: 'rgba(18, 100, 231, 1)', // Add custom color border (Line)
                    backgroundColor: "rgba(55, 81, 255, 10%)", // Add custom color background (Points and Fill)
                    fill: true,
                    borderWidth: 2, // Specify bar border width
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5,
                    
    
                },
                {
                    label: 'Total Chats Resolved ', // Name the series
                    data:  total_chats_resolved, // Specify the data values array
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#1BBD66',
                    borderColor: '#1BBD66', // Add custom color border (Line)
                    backgroundColor: "rgba(0, 200, 92, 10%)", // Add custom color background (Points and Fill)
                    fill: true,
                    borderWidth: 2 ,// Specify bar border width
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5
                },
                {
                    label: 'Abandoned Chats', // Name the series
                    data: total_declined_chats, // Specify the data values array
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#FF0000',
                    borderColor: '#FF0000', // Add custom color border (Line)
                    backgroundColor: "rgba(229, 53, 53, 10%)", // Add custom color background (Points and Fill)
                    fill: true,
                    borderWidth: 2 ,// Specify bar border width
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5
                },
                {
                    label: 'Missed Chats', // Name the series
                    data: offline_chats, // Specify the data values array
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#FFC700',
                    borderColor: '#FFC700', // Add custom color border (Line)
                    backgroundColor: 'rgba(242, 201, 56, 10%)',
                    fill: true,  // Add custom color background (Points and Fill)
                    borderDash: [10, 5],
                    borderWidth: 2 ,// Specify bar border width
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5
                },
                {
                    label: 'Offline Chats', // Name the series
                    data: abandoned_chats, // Specify the data values array
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#00C2FF',
                    borderColor: '#00C2FF', // Add custom color border (Line)
                    backgroundColor: 'rgba(146, 168, 206, 20%) ', // Add custom color background (Points and Fill)
                    fill: true, 
                    borderDash: [10, 5],
                    borderWidth: 2 ,// Specify bar border width
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5
                } 
            ]
        },
        options: {
            tension: 0.5,
            plugins: {
                tooltip: {
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
                }  
            },
            
            scales: {
                y: {
                    min: 0,
                    ticks: {
                        precision: 0,
                        // stepSize: 0
                    },
                    grid: {
                        display: true,
                        color: "#FAFAFA "
                    },
                },
                x: {
                    ticks: {
                        padding: 20,
                        minRotation: min_rotation,
    
                    },
                    grid: {
                        display: true,
                        color: "#FAFAFA "
                    }
    
                }
    
            },
            responsive: true, // Instruct chart js to respond nicely.
            maintainAspectRatio: false,
        }
    });
    
}
function add_interaction_per_chat_chart(interaction_per_chat_list){
    let labels = [];
    let avg_interactions_per_chat_raised = [];
    let point_radius= 0;
    for(let i =0 ;i <interaction_per_chat_list.length;i++ ){
        labels.push(interaction_per_chat_list[i]['label'])
        avg_interactions_per_chat_raised.push(interaction_per_chat_list[i]['average_interactions'])
    }  
    if(interaction_per_chat_list.length == 1){
        point_radius = 2;
    }
    let min_rotation =  0;
    if(interaction_per_chat_list.length>12){
        min_rotation = 10;// if data points were 12 ,13 the x axis labels were a bit conjusted so for that case added some angle in labels
    }
    var ctxInteractionPerchat = document.getElementById("customer_report_interaction_perchat_graph").getContext('2d');

        var myChartInteractionPerchat = new Chart(ctxInteractionPerchat, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                        label: ["Interactions Per Chat "], // Name the series
                        data: avg_interactions_per_chat_raised, // Specify the data values array
                        borderColor: '#1264E7', // Add custom color border (Line)
                        backgroundColor: '#ffffff', // Add custom color background (Points and Fill)
                        fill: '#ffffff', 
                        borderWidth: 2,
                        pointHitRadius: 5,
                        pointRadius: point_radius,
                        pointHoverRadius: 5

                    }
                ]
            },

            options: {
                tension: 0.5,
                plugins: {
                    tooltip: {
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
                        display: false,
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            fontColor: '#333',
    
                            textAlign: 'left',
                        }
                    }  
                },
                scales: {
                    y: {
                        min: 0,
                        ticks: {
                            padding: 20,
                            precision: 0,
                        },
                        title: {
                            display: true,
                            text: 'Interactions Per Chat',
                            color: '#D1D2D4',
                            font: {
                              family: "'DM Sans', sans-serif",
                              size: 12,
                            },
                            padding: 10,
                        },
                        grid: {
                            display: false,
                            color: "#FAFAFA "
                        }
                    },
                    x: {
                        ticks: {
                            padding: 20,
                            minRotation:min_rotation,
                        },
                        grid: {

                            color: "#FAFAFA "
                        }
                    }

                },
                responsive: true, // Instruct chart js to respond nicely.
                maintainAspectRatio: false,
            }
        });
   
}
function add_nps_report_chart(avg_nps_list){
   
    let labels = [];
    let avg_nps = [];
    let point_radius = 0;
    for(let i =0 ;i <avg_nps_list.length;i++ ){
        labels.push(avg_nps_list[i]['label'])
        avg_nps.push(avg_nps_list[i]['avg_nps'])
    }  
    if(avg_nps_list.length == 1){
        point_radius = 2
    }
    let min_rotation =  0;
    if(avg_nps_list.length>12){
        min_rotation = 10;// if data points were 12 ,13 the x axis labels were a bit conjusted so for that case added some angle in labels
    }
    var ctxAverageNps = document.getElementById("customer_report_average_nps_graph").getContext('2d');

    var myChartAverageNps = new Chart(ctxAverageNps, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                    label: ["Average NPS"], // Name the series
                    data: avg_nps, // Specify the data values array

                    borderColor: '#1264E7', // Add custom color border (Line)
                    backgroundColor: '#ffffff', // Add custom color background (Points and Fill)
                    borderWidth: 2,
                    fill: "#ffffff",
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            tension: 0.5,
            plugins: {
                tooltip: {
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
                display: false,
                position: 'bottom',

                labels: {
                    usePointStyle: true,
                    fontColor: '#333',

                    textAlign: 'left'

                }
            }
        },
            scales: {
                y: {
                    padding: 20,
                    min: -100,
                    max: 100,
                    ticks: {
                        // fontSize: 12,
                        // fontColor: '#D1D2D4',
                        // fontFamily: "'DM Sans', sans-serif",
                    },
                    title: {
                        display: true,
                        text: 'Average NPS',
                        color: '#D1D2D4',
                        font: {
                          family: "'DM Sans', sans-serif",
                          size: 12,
                          lineHeight: 1.2
                        },
                        padding: 10,
                    },
                    grid: {
                        display: false,
                        color: "#FAFAFA "

                    }
                },
                x: {
                   
                    ticks: {
                        padding: 20,
                        minRotation:min_rotation,
                    },
                    grid: {

                        color: "#FAFAFA "
                    }
                }

            },

            responsive: true, // Instruct chart js to respond nicely.
            maintainAspectRatio: false,
        }
    });
}
function add_livechat_avg_handle_time_chart(avg_handle_time_list){

    let labels = [];
    let avg_handle_time = [];
    let point_radius= 0;
    for(let i =0 ;i <avg_handle_time_list.length;i++ ){
        labels.push(avg_handle_time_list[i]['label'])
        avg_handle_time.push(avg_handle_time_list[i]['avg_handle_time'])
    }  
    if(avg_handle_time_list.length == 1){
        point_radius=2;
    }
    let min_rotation =  0;
    if(avg_handle_time_list.length>12){
        min_rotation = 10;// if data points were 12 ,13 the x axis labels were a bit conjusted so for that case added some angle in labels
    }
    var ctxAverageHandletime = document.getElementById("livechat_customer_report_average_handletime_graph").getContext('2d');

    var myChartAverageHandletime = new Chart(ctxAverageHandletime, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                    label: ["Average Handle Time"], 
                    data: avg_handle_time, 

                    borderColor: '#1264E7', // Add custom color border (Line)
                    backgroundColor: '#ffffff', // Add custom color background (Points and Fill)
                    borderWidth: 2,
                    fill: "#ffffff",
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5

                }

            ]


        },
        options: {
            tension: 0.5,
            plugins: {
                tooltip: {
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
                    display: false,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        fontColor: '#333',
    
                        textAlign: 'left',
                    }
                } 
        },
            scales: {
                y: {
                    min:0,
                    ticks: {
                        padding: 20,
                        precision: 0,

                    },
                    title: {
                        display: true,
                        text: 'Minutes',
                        color: '#D1D2D4',
                        font: {
                          family: "'DM Sans', sans-serif",
                          size: 12,
                          lineHeight: 1.2
                        },
                        padding: 10,
                    },
                    grid: {
                        display: false,
                        color: "#FAFAFA "
                    }
                },
                x: {
                    ticks: {
                        padding: 20,
                        minRotation:min_rotation,
                       

                    },
                    grid: {

                        color: "#FAFAFA "
                    }
                }

            },
            responsive: true, // Instruct chart js to respond nicely.
            maintainAspectRatio: false
        }
    });

}

function add_livechat_avg_queue_time_chart(avg_queue_time_list){

    let labels = [];
    let avg_queue_time = [];
    let point_radius= 0;
    for(let i =0 ;i <avg_queue_time_list.length;i++ ){
        labels.push(avg_queue_time_list[i]['label'])
        avg_queue_time.push(avg_queue_time_list[i]['average_queue_time'])
    }  
    if(avg_queue_time_list.length == 1){
        point_radius=2;
    }
    let min_rotation =  0;
    if(avg_queue_time_list.length>12){
        min_rotation = 10;// if data points were 12 ,13 the x axis labels were a bit conjusted so for that case added some angle in labels
    }
    var ctxAverageQueuetime = document.getElementById("customer_report_customer_waittime_graph").getContext('2d');

    var myChartAverageQueuetime = new Chart(ctxAverageQueuetime, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                    label: ["Average Queue Time"], 
                    data: avg_queue_time, 

                    borderColor: '#1264E7', // Add custom color border (Line)
                    backgroundColor: '#ffffff', // Add custom color background (Points and Fill)
                    borderWidth: 2,
                    fill: "#ffffff",
                    pointHitRadius: 5,
                    pointRadius: point_radius,
                    pointHoverRadius: 5

                }

            ]


        },
        options: {
            tension: 0.5,
            plugins: {
                tooltip: {
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
                    display: false,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        fontColor: '#333',
    
                        textAlign: 'left',
                    }
                } 
        },
            scales: {
                y: {
                    min:0,
                    ticks: {
                        padding: 20,
                       
                        precision: 0,

                    },
                    title: {
                        display: true,
                        text: 'Seconds',
                        color: '#D1D2D4',
                        font: {
                          family: "'DM Sans', sans-serif",
                          size: 12,
                          lineHeight: 1.2
                        },
                        padding: 10,
                    },
                    grid: {
                        display: false,
                        color: "#FAFAFA "
                    }
                },
                x: {
                    ticks: {
                        padding: 20,
                        minRotation:min_rotation,
                       

                    },
                    grid: {

                        color: "#FAFAFA "
                    }

                    // display: true,
                    // scaleLabel: {
                    //     display: true,
                    //     labelString: 'Date'
                    // }
                }

            },
            responsive: true, // Instruct chart js to respond nicely.
            maintainAspectRatio: false,
            // elements: {
            //     point: {
            //         hitRadius: 5,
            //         radius: point_radius,
            //         hoverRadius: 5
            //     }
            // },

            // Add to prevent default behaviour of full-width/height 
        }
    });

}

function switch_from_nps_graph(){

    $("#interaction_perchat_card").removeClass("analytics-card-active");
    $("#average_handletime_card").removeClass("analytics-card-active");
    $("#average_customer_waittime_card").removeClass("analytics-card-active");
    $(".customer-report-average-nps-graph").css("display", "block");
    $(".customer-report-average-handletime-graph").css("display", "none");
    $(".customer-report-customer-waittime-graph").css("display", "none");
    $(".customer-report-interaction-perchat-graph").css("display", "none");
    $("#customer-report-graph-name-section-text").text("Average NPS");
    $("#average_nps_heading").css("color", "#000");
    $("#interaction_chat_heading").css("color", "#4d4d4d");

    $("#average_handletime_heading").css("color", "#4d4d4d");

}

function switch_from_inter_per_chat_graph(){

    $("#average_nps_card").removeClass("analytics-card-active");
    $("#average_handletime_card").removeClass("analytics-card-active");
    $("#average_customer_waittime_card").removeClass("analytics-card-active");
    $(".customer-report-average-nps-graph").css("display", "none");
    $(".customer-report-average-handletime-graph").css("display", "none");
    $(".customer-report-customer-waittime-graph").css("display", "none");
    $(".customer-report-interaction-perchat-graph").css("display", "block");
    $("#customer-report-graph-name-section-text").text("Interactions Per Chat");
    $("#average_nps_heading").css("color", "#4d4d4d");
    $("#interaction_chat_heading").css("color", "#000");
    $("#average_handletime_heading").css("color", "#4d4d4d");

}
function switch_from_avg_handle_time_graph(){
    $("#interaction_perchat_card").removeClass("analytics-card-active");
    $("#average_nps_card").removeClass("analytics-card-active");
    $("#average_customer_waittime_card").removeClass("analytics-card-active");

    $(".customer-report-average-nps-graph").css("display", "none");
    $(".customer-report-average-handletime-graph").css("display", "block");
    $(".customer-report-customer-waittime-graph").css("display", "none");
    $(".customer-report-interaction-perchat-graph").css("display", "none");
    $("#customer-report-graph-name-section-text").text("Average Handle Time");
    $("#average_nps_heading").css("color", "#4d4d4d");
    $("#interaction_chat_heading").css("color", "#4d4d4d");

    $("#average_handletime_heading").css("color", "#000");


}

function switch_from_avg_queue_time_graph(){
    $("#interaction_perchat_card").removeClass("analytics-card-active");
    $("#average_nps_card").removeClass("analytics-card-active");
    $("#average_handletime_card").removeClass("analytics-card-active");

    $(".customer-report-average-nps-graph").css("display", "none");
    $(".customer-report-average-handletime-graph").css("display", "none");
    $(".customer-report-customer-waittime-graph").css("display", "block");
    $(".customer-report-interaction-perchat-graph").css("display", "none");
    $("#customer-report-graph-name-section-text").text("Average Queue Time");
    $("#average_nps_heading").css("color", "#4d4d4d");
    $("#interaction_chat_heading").css("color", "#4d4d4d");

    $("#average_handletime_heading").css("color", "#000");


}

export {
    livechat_chat_history_report_update,
    livechat_avg_nps_report_update,
    livechat_avg_handle_time_report_update,
    livechat_avg_queue_time_report_update,
    livechat_interactions_per_chat_report_update,
    switch_from_nps_graph,
    switch_from_inter_per_chat_graph,
    switch_from_avg_handle_time_graph,
    switch_from_avg_queue_time_graph,
};