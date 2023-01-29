var campaign_stats_chart = null;
var success_ratio_chart = null;
var channel_campaign_stats_chart = null;

$(document).ready(function() {
    initialize_multiselect_channel_campaign_filter();

    load_analytics_data();

    $("#campaign-analytics-filter-btn").on("click", function () {
        load_analytics_data();
        $("#campaign-select-dropdown").multiselect('rebuild');
        $("#campaigns_filter_multiselect_dropdown .multiselect-container").scrollTop(0);
    });

    $("#campaign-select-channel-dropdown-analytics").on("change", function () {
        load_analytics_data();
    });

    const accordionBtns = document.querySelectorAll(".campaign-display-table-content");
    const accordionTable = document.querySelector(".analytics-channel-stats-value-table");
    


    accordionBtns.forEach((acc) => acc.addEventListener("click", toggleAcc));

        function toggleAcc() {
        

        // toggle active class on current item
        if (this.classList != "rotate-svg") {
            this.classList.toggle("rotate-svg");
        }

        if (this.classList != "hide-table") {
            this.classList.toggle("hide-table");
        }
        
        
        }
})

function load_analytics_data() {
    load_basic_campaign_details();
    load_campaign_chart();
    load_success_ratio_chart();
    load_campaign_stats_chart();
}

function initialize_multiselect_channel_campaign_filter() {

    $('#campaign-select-channel-dropdown-analytics').multiselect({
        nonSelectedText: 'Select Channel',
        enableFiltering: false,
        container: 'body',
        selectAll: false,
        includeSelectAllOption: false,

    }).multiselect('selectAll', false)
    .multiselect('updateButtonText');

    $('#campaign-select-dropdown').multiselect({
        nonSelectedText: 'Search Campaign',
        enableFiltering: true,
        enableCaseInsensitiveFiltering: true,
        container: 'body',
        includeSelectAllOption: true,
        onDropdownShow: function(event) {
            var campaign_list_empty = this.$ul.find('li').hasClass('no-campaign-found');
            if( campaign_list_empty == true ) {
                $(".multiselect-all").hide();
                $(".multiselect-item.filter").hide();
            }
            else{
                $(".multiselect-all").show();
                $(".multiselect-search").show();
            }
        },   
    });
}
 
function load_basic_campaign_details() {

    var analytics_filter_obj = check_analytics_filter();
    if (analytics_filter_obj == undefined) return;

    var selected_campaigns = analytics_filter_obj.selected_campaigns;
    var selected_date_filter = analytics_filter_obj.selected_date_filter;
    var start_date = analytics_filter_obj.start_date;
    var end_date = analytics_filter_obj.end_date;
    var channel_list = analytics_filter_obj.channel_list;

    var json_string = {
        bot_id: get_url_multiple_vars()['bot_pk'][0],
        selected_date_filter: selected_date_filter,
        selected_campaigns: selected_campaigns,
        start_date: start_date,
        end_date: end_date,
        channel_list: channel_list,
    }

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/get-campaign-basic-analytics/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                $('#campaign_analytics_filter_modal').modal('hide');
                document.getElementById('total_campaigns').innerHTML = response.total_campaigns;
                document.getElementById('avg_open_rate').innerHTML = response.avg_open_rate.toFixed(2) + '%';
                document.getElementById('total_launched_campaigns').innerHTML = response.total_launched_campaigns;

                $('#total_messages_sent').html(response.total_messages_sent);
                $('#total_messages_read').html(response.total_messages_read);
                $('#total_messages_delivered').html(response.total_messages_delivered);
                $('#total_messages_unsuccessful').html(response.total_messages_unsuccessful);
                $('#total_messages_replied').html(response.total_messages_replied);
                $('#total_messages_processed').html(response.total_messages_processed);
                $('#test_message_sent').html(response.test_message_sent);
                $('#test_message_unsuccessful').html(response.test_message_unsuccessful);

                $('.total_calls_created').html(response.total_calls_created);
                $('.total_calls_scheduled').html(response.total_calls_scheduled);
                $('.total_calls_initiated').html(response.total_calls_initiated);
                $('.total_calls_in_progress').html(response.total_calls_in_progress);
                $('.total_calls_retry').html(response.total_calls_retry);
                $('.total_calls_failed').html(response.total_calls_failed);
                $('.total_calls_completed').html(response.total_calls_completed);

                $('.rcs_submitted_value').html(response.total_rcs_messages_submitted);
                $('.rcs_sent_value').html(response.total_rcs_messages_sent);
                $('.rcs_delivered_value').html(response.total_rcs_messages_delivered);
                $('.rcs_read_value').html(response.total_rcs_messages_read);
                $('.rcs_failed_value').html(response.total_rcs_messages_failed);
                $('.rcs_replied_value').html(response.total_rcs_messages_replied);

                update_tooltip_and_handle_analytics_card(channel_list);

            } else {
                $('#campaign_analytics_filter_modal').modal('hide');
                show_campaign_toast(response.message)
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function update_tooltip_and_handle_analytics_card(channel_list) {

    $('.channel-stats-specific-card').attr("style", "display: none !important");
    if(channel_list.length == 1 && channel_list.includes('whatsapp')) {

        $("#total-campaigns-created-link").attr('data-original-title', 'Total number of campaigns created.');
        $("#total-campaigns-launched-link").attr('data-original-title', 'Number of campaigns that have been launched.');
        $('#whatsapp-stats-card').attr("style", "display: flex !important");
        $('#whatsapp-stats-toggle-card').click();

    } else if (channel_list.length == 1 && channel_list.includes('voicebot')) {

        $("#total-campaigns-created-link").attr('data-original-title', 'Total number of Voice Bot campaigns created on this bot.');
        $("#total-campaigns-launched-link").attr('data-original-title', 'Total number of Voice Bot campaigns launched on this bot.');
        $('#voicebot-stats-card').attr("style", "display: flex !important");
        $('#voicebot-stats-toggle-card').click();

    } else if (channel_list.length == 1 && channel_list.includes('rcs')) {

        $("#total-campaigns-created-link").attr('data-original-title', 'Total number of RCS campaigns created on this bot.');
        $("#total-campaigns-launched-link").attr('data-original-title', 'Total number of RCS campaigns launched on this bot.');
        $('#rcs-stats-card').attr("style", "display: flex !important");
        $('#rcs-stats-toggle-card').click();

    } else {
        $("#total-campaigns-created-link").attr('data-original-title', 'Total number of campaigns created across all channels on this bot.');
        $("#total-campaigns-launched-link").attr('data-original-title', 'Total number of campaigns launched across all channels on this bot.');
        $('.channel-stats-specific-card').attr("style", "display: flex !important");

        if( channel_list.includes('whatsapp') == false ) {
            $('#whatsapp-stats-card').attr("style", "display: none !important");
        }
        if( channel_list.includes('voicebot') == false ) {
            $('#voicebot-stats-card').attr("style", "display: none !important");
        }
        if( channel_list.includes('rcs') == false ) {
            $('#rcs-stats-card').attr("style", "display: none !important");
        }
    }

}

function load_campaign_chart() {
    document.getElementById('campaign_analytics_loader').style.display = 'block';

    var analytics_filter_obj = check_analytics_filter();
    if (analytics_filter_obj == undefined){
        document.getElementById('campaign_analytics_loader').style.display = 'none';
    };

    var selected_campaigns = analytics_filter_obj.selected_campaigns;
    var selected_date_filter = analytics_filter_obj.selected_date_filter;
    var start_date = analytics_filter_obj.start_date;
    var end_date = analytics_filter_obj.end_date;
    var channel_list = analytics_filter_obj.channel_list;

    var json_string = {
        bot_id: get_url_multiple_vars()['bot_pk'][0],
        selected_date_filter: selected_date_filter,
        selected_campaigns: selected_campaigns,
        start_date: start_date,
        end_date: end_date,
        channel_list: channel_list,
    }

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/get-campaign-detailed-analytics/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                $('#campaign_analytics_filter_modal').modal('hide');
                if(campaign_stats_chart != null) campaign_stats_chart.destroy(); 
                load_chart(response, channel_list);
                document.getElementById('campaign_analytics_loader').style.display = 'none';

            } else {
                $('#campaign_analytics_filter_modal').modal('hide');
                show_campaign_toast(response.message)
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function load_success_ratio_chart() {

    var analytics_filter_obj = check_analytics_filter();
    if (analytics_filter_obj == undefined) return;

    var selected_campaigns = analytics_filter_obj.selected_campaigns;
    var selected_date_filter = analytics_filter_obj.selected_date_filter;
    var start_date = analytics_filter_obj.start_date;
    var end_date = analytics_filter_obj.end_date;
    var channel_list = analytics_filter_obj.channel_list;

    var json_string = {
        bot_id: get_url_multiple_vars()['bot_pk'][0],
        selected_date_filter: selected_date_filter,
        selected_campaigns: selected_campaigns,
        start_date: start_date,
        end_date: end_date,
        channel_list: channel_list,
    }

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/get-campaign-success-ratio-analytics/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                $('#campaign_analytics_filter_modal').modal('hide');
                if(success_ratio_chart != null) success_ratio_chart.destroy();
                if (response.sent_data + response.failed_data === 0) {
                    let pieChartDiv = document.getElementById("pieDiv");
                    pieChartDiv.style.display = "none"; 
                    $("#no-session-analytics-div").hide();
                    $("#no-session-analytics-div").show("slow");
                }
                else {
                    let pieChartDiv = document.getElementById("pieDiv");
                    pieChartDiv.style.display = ""; 
                    let noDataDiv = document.getElementById("no-session-analytics-div");
                    noDataDiv.style.display = "none"; 
                    render_success_ratio_chart(response);
                }

            } else {
                $('#campaign_analytics_filter_modal').modal('hide');
                show_campaign_toast(response.message)
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);
}

function load_campaign_stats_chart() {
    var analytics_filter_obj = check_analytics_filter();
    if (analytics_filter_obj == undefined) return;

    var selected_campaigns = analytics_filter_obj.selected_campaigns;
    var selected_date_filter = analytics_filter_obj.selected_date_filter;
    var start_date = analytics_filter_obj.start_date;
    var end_date = analytics_filter_obj.end_date;
    var channel_list = analytics_filter_obj.channel_list;

    var json_string = {
        bot_id: get_url_multiple_vars()['bot_pk'][0],
        selected_date_filter: selected_date_filter,
        selected_campaigns: selected_campaigns,
        start_date: start_date,
        end_date: end_date,
        channel_list: channel_list,
    }

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/get-channel-campaign-stats-analytics/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response["status"] == 200) {
                $('#campaign_analytics_filter_modal').modal('hide');
                if(channel_campaign_stats_chart != null) channel_campaign_stats_chart.destroy(); 
                // render_campaign_stats_chart(response);  commenting since channel wise chart is not needed after hiding rcs and voicebot

            } else {
                $('#campaign_analytics_filter_modal').modal('hide');
                show_campaign_toast(response.message)
            }
        } else if(this.readyState == 4 && this.status == 403){
            trigger_session_time_out_modal();
        }
    }
    xhttp.send(params);    
}

function load_chart(data, channel_list) {
    var ctx = document.getElementById("campaign_analytics_graph").getContext('2d');

    let whatsapp_data = {
                    label: data.whatsapp.label, // Name the series
                    data: data.whatsapp.data, // Specify the data values array

                    pointHoverBackgroundColor: '#fff', 
                    pointHoverBorderColor: '#109618',
                    borderColor: '#109618', // Add custom color border (Line)
                    backgroundColor: 'rgba(242, 201, 56, 10%)', // Add custom color background (Points and Fill)
                    // borderDash: [10, 5],
                    borderWidth: 2 // Specify bar border width
                    }

    let voice_data = {
                    label: data.voicebot.label, // Name the series
                    data: data.voicebot.data, // Specify the data values array

                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#990099',
                    borderColor: '#990099', // Add custom color border (Line)
                    backgroundColor: 'rgba(146, 168, 206, 20%) ', // Add custom color background (Points and Fill)
                    // borderDash: [10, 5],
                    borderWidth: 2 // Specify bar border width   
                    }

    let rcs_data = {
                    label: data.rcs.label, // Name the series
                    data: data.rcs.data, // Specify the data values array

                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#FF9900',
                    borderColor: '#FF9900', // Add custom color border (Line)
                    backgroundColor: 'rgba(146, 168, 206, 20%) ', // Add custom color background (Points and Fill)
                    // borderDash: [10, 5],
                    borderWidth: 2 // Specify bar border width   
                    }

    let channel_dataset = []
    if(channel_list.length == 0 || (channel_list.length > 0 && channel_list.includes("whatsapp"))) {
        channel_dataset.push(whatsapp_data);
    }
    if(channel_list.length == 0 || (channel_list.length > 0 && channel_list.includes("voicebot"))) {
        channel_dataset.push(voice_data);
    }

    if(channel_list.length == 0 || (channel_list.length > 0 && channel_list.includes("rcs"))) {
        channel_dataset.push(rcs_data);
    }

    campaign_stats_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: channel_dataset
        },
        options: {
            elements: {
                point: {
                    radius: 0,
                }
            },
            scales:{
                y:{
                    grid:{
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Campaign Count',
                        color: '#757375',
                        font: {
                          family: "'DM Sans', sans-serif",
                          size: 12,
                          lineHeight: 1.2
                        },
                        padding: 15,
                    },
                },
                x:{
                    grid:{
                        display: false
                    }
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            
            plugins:{
                legend: {
                    display: true,
                    position: 'bottom',
            
                    labels: {
                        usePointStyle: true,
                        pointStyle:'circle',
                        padding: 26,
                        boxWidth: 9,
                    },
                },
                
                tooltip: {
                    backgroundColor: 'rgb(255, 255, 255)',
                    titleFontSize: 14,
                    titleColor: 'rgb(0,0,0)',
                    bodyColor: 'rgb(0,0,0)',
                    displayColors: false,
                    titleFont: 'bold',
                    yAlign: 'top',
                    position:'average',
                    
                }  
            },
            
        },
    });

}

function check_analytics_filter() {

    var selected_campaigns = $("#campaign-select-dropdown").val();
    var selected_date_filter = $("input[type='radio'][name='campaign-overview-filter']:checked").val();
    var start_date = "", end_date = "";
    // var channel_list = $("#campaign-select-channel-dropdown-analytics").val();
    // adding only whatsapp in channel list by default as rcs and voicebot are removed from console
    var channel_list = ["whatsapp"];

    if (selected_date_filter == '5') {
        start_date = document.getElementById('campaign_filter_custom_start_date').value;
        end_date = document.getElementById('campaign_filter_custom_end_date').value;

        let date_validation_message = check_date_range_validation(start_date, end_date);
        if (date_validation_message != ""){
            show_campaign_toast(date_validation_message);
            return;
        }
    }

    return {
        selected_campaigns: selected_campaigns,
        selected_date_filter: selected_date_filter,
        start_date: start_date,
        end_date: end_date,
        channel_list: channel_list,
    }

}

function reset_campaign_analytics_filter() {

    document.getElementById('campaign_overview_beg').checked = true;
    document.getElementById('campaign-custom-date-select-area-flow').style.display = 'none';
    document.getElementById('campaign_filter_custom_start_date').value = DEFAULT_START_DATE
    document.getElementById('campaign_filter_custom_end_date').value = DEFAULT_END_DATE
   
    $("#campaign-select-dropdown").multiselect('clearSelection');
    $("#campaign-select-dropdown").multiselect('rebuild');
    $("#campaign-select-channel-dropdown-analytics").multiselect('clearSelection');
    $("#campaigns_filter_multiselect_dropdown .multiselect-container").scrollTop(0);
    load_analytics_data();
}

function render_success_ratio_chart(data) {
    var ctx = document.getElementById("success-ratio").getContext('2d');

    success_ratio_chart = new Chart(ctx, {
        type: "doughnut",
        data : {
            labels : ["Sent","Failed"],
            datasets: [{
                data: [data.sent_data, data.failed_data],
                backgroundColor: [
                    "#109618",
                    "#DC3912",
                ]
            }],
        },
        options: {
            hover: {
                onHover: function(e) {
                  $("#canvas1").css("cursor", e[0] ? "pointer" : "default");
                }
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins:{
                legend: {
                    display: true,
                    position: 'bottom',
            
            
                    labels: {
                        usePointStyle: true,
                        padding: 26,
                        boxWidth: 9,
                    }
                },
                datalabels: {
                    formatter: (value, ctx) => {
                      const datapoints = ctx.chart.data.datasets[0].data
                      const total = datapoints.reduce((total, datapoint) => total + datapoint, 0)
                      const percentage = value / total * 100
                      return percentage.toFixed(2) + "%";
                    },
                    color: '#fff',
                  },
                tooltip: {
                    backgroundColor: 'rgb(255, 255, 255)',
                    titleFontSize: 14,
                    titleColor: 'rgb(0,0,0)',
                    bodyColor: 'rgb(0,0,0)',
                    displayColors: false,
                    titleFont: 'bold',
                    yAlign: 'top',
                    position:'average',
                    custom: function(tooltip) {
                        if (!tooltip.opacity) {
                          document.getElementById("canvas").style.cursor = 'default';
                          return;
                        }
                      }
                }  
            },
            
        },
        plugins:[ChartDataLabels]
    })
}

function render_campaign_stats_chart(data) {
    var ctx = document.getElementById("channel-campaign-status").getContext('2d');

    channel_campaign_stats_chart = new Chart(ctx, {
        
        type: "pie",
        data : {
            labels : data.channel_stats_label,
            datasets: [{
                data: data.channel_stats_data,
                backgroundColor: [
                    "#3366CC",
                    "#FF9900",
                    "#109618",
                    "#990099",
                    "#0099C6"
                ],
                hoverBorderColor:'#ffffff',
                borderWidth: 0,
                hoverBorderWidth: 5,
                hoverOffset: 5
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins:{
                legend: {
                    display: true,
                    position: 'right',
            
            
                    labels: {
                        usePointStyle: true,
                        padding: 26,
                        boxWidth: 9,
                    }
                },
                datalabels: {
                    formatter: (value, ctx) => {
                      const datapoints = ctx.chart.data.datasets[0].data
                       const total = datapoints.reduce((total, datapoint) => total + datapoint, 0)
                      const percentage = value / total * 100
                      return percentage.toFixed(2) + "%";
                    },
                    color: '#fff',
                  },
                  tooltip: {
                    backgroundColor: 'rgba(255, 255, 255)',
                    titleFontSize: 14,
                    titleColor: 'rgb(0,0,0)',
                    bodyColor: 'rgb(0,0,0)',
                    borderWidth:1,
                    displayColors: false,
                    titleFont: 'bold',
                    yAlign : 'top',
                    position:'average'
                }  
            },
            
        },
        plugins:[ChartDataLabels]
    })
}