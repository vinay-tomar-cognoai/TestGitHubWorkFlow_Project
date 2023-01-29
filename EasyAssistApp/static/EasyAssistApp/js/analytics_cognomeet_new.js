// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


function create_or_update_cognomeet_agent() {

    let json_string = JSON.stringify({
        "cogno_meet_access_token": COGNOMEET_ACCESS_TOKEN,
        "agent_role": agent_role
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/create-or-update-cognomeet-agent", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] != 200) {
                console.log('Filed to create or update cognomeet agent')
            }
        }
    };
    xhttp.send(params);
}

// fetch analytics from CognoMeetApp
function get_cognomeet_analytics() {

    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    let start_date_formatted = get_iso_formatted_date(start_date);
    let end_date_formatted = get_iso_formatted_date(end_date);

    let start_date_obj = new Date(start_date_formatted);
    let end_date_obj = new Date(end_date_formatted);

    if (!start_date.length) {
        show_easyassist_toast(EMPTY_START_DATE_ERROR_TOAST);
        return;
    } else if (!end_date.length) {
        show_easyassist_toast(EMPTY_END_DATE_ERROR_TOAST);
        return;
    } else if (start_date_obj.getTime() > end_date_obj.getTime()) {
        show_easyassist_toast("Start date cannot be greater than the end date");
        return;
    }

    get_cognomeet_basic_analytics(start_date, end_date);
    show_daily_cogno_meeting_analytics();
    get_daily_call_time_trend();
    if(document.getElementById("cogno-meet-agent-wise-analytics")) {
        show_agent_wise_cogno_meet_analytics();
    }
}

function get_cognomeet_basic_analytics(start_date, end_date) {
    let request_params = {
        "start_date": start_date,
        "end_date": end_date,
        "agents_usernames_list": window.AGENTS_USERNAMES_LIST,
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN
    }
    
    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/get-basic-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if(response.status == 200) {
                document.getElementById("cogno-meet-total-meeting-scheduled").innerHTML = response.total_meeting_scheduled_count;
                document.getElementById("cogno-meet-total-meeting-completed").innerHTML = response.total_meeting_completed_count;
                document.getElementById("cogno-meet-total-ongoing-meeting").innerHTML = response.total_ongoing_meetings_count;
                document.getElementById("cogno-meet-avg-call-duration").innerHTML = response.average_call_duration_in_min;

                update_session_initiated_in_chart(response.total_meeting_scheduled_count);
            }
        }
    }
    xhttp.send(params);
}

function update_session_initiated_in_chart(total_meetings_scheduled_count, cobrowsing_request_count=0) {
    // As of now development is happening for only scheduled meeting.
    // When we integrate Cobrowsing and Dyte, we would have to create 
    // a dedicated API to update this chart.

    Chart.helpers.each(Chart.instances, function(instance) {
        if (instance.chart.canvas.id == "session-initiated-in-pie-chart") {
            instance.destroy();
        }
    });

    let canvas_element = document.getElementById("session-initiated-in-pie-chart");
    let myPieChart = new Chart(canvas_element, {
        type: 'doughnut',
        data: {
            datasets: [{
                fill: true,
                backgroundColor: ["rgba(128, 110, 243, 1)", "rgb(22, 161, 170, 1)"],
                data: [cobrowsing_request_count, total_meetings_scheduled_count]
            }],
            labels: ['Cobrowsing', 'Video Conference']
        },
        options: {
            responsive: true,
        }
    });
}

function show_daily_cogno_meeting_analytics() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    get_timeline_based_analytics(start_date, end_date, "daily");
}

function show_weekly_cogno_meeting_analytics() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    get_timeline_based_analytics(start_date, end_date, "weekly");
}

function show_monthly_cogno_meeting_analytics() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    get_timeline_based_analytics(start_date, end_date, "monthly");
}

function get_timeline_based_analytics(start_date, end_date, timeline) {

    let request_params = {
        "start_date": start_date,
        "end_date": end_date,
        "timeline": timeline,
        "agents_usernames_list": window.AGENTS_USERNAMES_LIST,
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/get-timeline-based-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                let label_list = [];
                let meeting_completed_list = [];
                let meeting_scheduled_list = [];
                let meeting_ongoing_list = [];

                for (var i = 0; i < response["timeline_based_analytics"].length; i++) {
                    label_list.push(response["timeline_based_analytics"][i]["label"]);
                    let total_meeting_completed = response["timeline_based_analytics"][i]["total_meeting_completed"];
                    let total_meeting_scheduled = response["timeline_based_analytics"][i]["total_meeting_scheduled"];
                    let total_meeting_ongoing = response["timeline_based_analytics"][i]["total_ongoing_meeting"];

                    meeting_completed_list.push(total_meeting_completed);
                    meeting_scheduled_list.push(total_meeting_scheduled);
                    meeting_ongoing_list.push(total_meeting_ongoing);
                }

                let dataset_list = []
                dataset_list = [{
                    label: "Scheduled Meeting",
                    lineTension: 0.3,
                    backgroundColor: "rgba(128, 110, 243, 0.05)",
                    borderColor: "rgba(128, 110, 243, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(128, 110, 243, 1)",
                    pointBorderColor: "rgba(128, 110, 243, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(128, 110, 243, 1)",
                    pointHoverBorderColor: "rgba(128, 110, 243, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: meeting_scheduled_list,
                }, {
                    label: "Ongoing Meeting",
                    lineTension: 0.3,
                    backgroundColor: "rgb(22, 161, 170, 0.05)",
                    borderColor: "rgb(22, 161, 170, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgb(22, 161, 170, 1)",
                    pointBorderColor: "rgb(22, 161, 170, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgb(22, 161, 170, 1)",
                    pointHoverBorderColor: "rgb(22, 161, 170, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: meeting_ongoing_list,
                }, {
                    label: "Completed Meeting",
                    lineTension: 0.3,
                    backgroundColor: "rgba(28, 175, 6, 0.05)",
                    borderColor: "rgba(28, 175, 6, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(28, 175, 6, 1)",
                    pointBorderColor: "rgba(28, 175, 6, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(28, 175, 6, 1)",
                    pointHoverBorderColor: "rgba(28, 175, 6, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: meeting_completed_list,
                }];

                Chart.helpers.each(Chart.instances, function(instance) {
                    if (instance.chart.canvas.id == "cogno-meet-analytics") {
                        instance.destroy();
                    }
                });

                let ctx = document.getElementById("cogno-meet-analytics");
                let myLineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: label_list,
                        datasets: dataset_list
                    },
                    options: {
                        maintainAspectRatio: false,
                        layout: {
                            padding: {
                                left: 10,
                                right: 25,
                                top: 25,
                                bottom: 0
                            }
                        },
                        scales: {
                            xAxes: [{
                                time: {
                                    unit: 'date'
                                },
                                gridLines: {
                                    display: false,
                                    drawBorder: false
                                },
                                ticks: {
                                    maxTicksLimit: 7
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    maxTicksLimit: 5,
                                    padding: 10,
                                    beginAtZero: true,
                                    // Include a dollar sign in the ticks
                                    // callback: function(value, index, values) {
                                    //  return number_format(value);
                                    // }
                                    callback: function(value, index, values) {
                                        if (Math.floor(value) === value) {
                                            return value;
                                        }
                                    }
                                },
                                gridLines: {
                                    color: "rgb(234, 236, 244)",
                                    zeroLineColor: "rgb(234, 236, 244)",
                                    drawBorder: false,
                                    borderDash: [2],
                                    zeroLineBorderDash: [2]
                                }
                            }],
                        },
                        legend: {
                            display: true
                        },
                        tooltips: {
                            backgroundColor: "rgb(255,255,255)",
                            bodyFontColor: "#858796",
                            titleMarginBottom: 10,
                            titleFontColor: '#6e707e',
                            titleFontSize: 14,
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 15,
                            yPadding: 15,
                            displayColors: false,
                            intersect: false,
                            mode: 'index',
                            caretPadding: 10,
                            callbacks: {
                                label: function(tooltipItem, chart) {
                                    var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                                    return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
                                }
                            }
                        }
                    }
                });
            } else {
                console.error(response);
            }
        }
    }
    xhttp.send(params);
}

function get_daily_call_time_trend() {

    let request_params = {
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "agents_usernames_list": window.AGENTS_USERNAMES_LIST
    }
    
    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/get-daily-call-time-trend-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                let label_list = [];
                let completed_meeting_list = [];

                for (let i = 0; i < response["daily_time_trend"].length; i++) {
                    label_list.push(response["daily_time_trend"][i]["label"].split('-'));
                    let total_ongoing_meeting = response["daily_time_trend"][i]["total_meetings_count"];

                    completed_meeting_list.push(total_ongoing_meeting);
                }

                dataset_list = [{
                    label: "Completed Meeting",
                    lineTension: 0.3,
                    backgroundColor: "rgba(128, 110, 243, 0.05)",
                    borderColor: "rgba(128, 110, 243, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(128, 110, 243, 1)",
                    pointBorderColor: "rgba(128, 110, 243, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(128, 110, 243, 1)",
                    pointHoverBorderColor: "rgba(128, 110, 243, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: completed_meeting_list,
                }];

                Chart.helpers.each(Chart.instances, function(instance) {
                    if (instance.chart.canvas.id == "cogno-meet-daily-time-trend") {
                        instance.destroy();
                    }
                });

                // Area Chart Example
                var ctx = document.getElementById("cogno-meet-daily-time-trend");
                var myLineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: label_list,
                        datasets: dataset_list
                    },
                    options: {
                        maintainAspectRatio: false,
                        layout: {
                            padding: {
                                left: 10,
                                right: 25,
                                top: 25,
                                bottom: 0
                            }
                        },
                        scales: {
                            xAxes: [{
                                time: {
                                    unit: 'date'
                                },
                                gridLines: {
                                    display: false,
                                    drawBorder: false
                                },
                                ticks: {
                                    maxTicksLimit: 7,
                                    userCallback: function(label, index, labels) {
                                        return label[1];
                                    }
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    maxTicksLimit: 5,
                                    padding: 10,
                                    beginAtZero: true,
                                    // Include a dollar sign in the ticks
                                    // callback: function(value, index, values) {
                                    //  return number_format(value);
                                    // }
                                    callback: function(value, index, values) {
                                        if (Math.floor(value) === value) {
                                            return value;
                                        }
                                    }
                                },
                                gridLines: {
                                    color: "rgb(234, 236, 244)",
                                    zeroLineColor: "rgb(234, 236, 244)",
                                    drawBorder: false,
                                    borderDash: [2],
                                    zeroLineBorderDash: [2]
                                }
                            }],
                        },
                        legend: {
                            display: true
                        },
                        tooltips: {
                            backgroundColor: "rgb(255,255,255)",
                            bodyFontColor: "#858796",
                            titleMarginBottom: 10,
                            titleFontColor: '#6e707e',
                            titleFontSize: 14,
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 15,
                            yPadding: 15,
                            displayColors: false,
                            intersect: false,
                            mode: 'index',
                            caretPadding: 10,
                            callbacks: {
                                label: function(tooltipItem, chart) {
                                    var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                                    return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
                                },
                                title: function(tooltipItems, chart) {
                                    return chart.labels[tooltipItems[0].index].join(' - ');
                                }
                            }
                        }
                    }
                });
            } else {
                console.error(response);
            }
        }
    }
    xhttp.send(params);
}

function show_agent_wise_cogno_meet_analytics() {
    get_agentwise_daily_analytics();
}

function get_agentwise_daily_analytics() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    let agent_key = document.getElementById("cogno-meet-select-agent").value;
    get_agentwise_analytics(start_date, end_date, "daily", agent_key);
}

function get_agentwise_weekly_analytics() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    let agent_key = document.getElementById("cogno-meet-select-agent").value;
    get_agentwise_analytics(start_date, end_date, "weekly", agent_key);
}

function get_agentwise_monthly_analytics() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    let agent_key = document.getElementById("cogno-meet-select-agent").value;
    get_agentwise_analytics(start_date, end_date, "monthly", agent_key);
}

function get_agentwise_analytics(start_date, end_date, timeline, agent_key) {

    let request_params = {
        "start_date": start_date,
        "end_date": end_date,
        "timeline": timeline,
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "agent_key": agent_key
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/get-agent-wise-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                let label_list = [];
                let meeting_completed_list = [];
                let meeting_scheduled_list = [];

                for (var i = 0; i < response["timeline_based_analytics"].length; i++) {
                    label_list.push(response["timeline_based_analytics"][i]["label"]);
                    let total_meeting_completed = response["timeline_based_analytics"][i]["total_meeting_completed"];
                    let total_meeting_scheduled = response["timeline_based_analytics"][i]["total_meeting_scheduled"];

                    meeting_completed_list.push(total_meeting_completed);
                    meeting_scheduled_list.push(total_meeting_scheduled);
                }

                let dataset_list = []
                dataset_list = [{
                    label: "Scheduled Meeting",
                    lineTension: 0.3,
                    backgroundColor: "rgba(128, 110, 243, 0.05)",
                    borderColor: "rgba(128, 110, 243, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(128, 110, 243, 1)",
                    pointBorderColor: "rgba(128, 110, 243, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(128, 110, 243, 1)",
                    pointHoverBorderColor: "rgba(128, 110, 243, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: meeting_scheduled_list,
                }, {
                    label: "Completed Meeting",
                    lineTension: 0.3,
                    backgroundColor: "rgba(28, 175, 6, 0.05)",
                    borderColor: "rgba(28, 175, 6, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(28, 175, 6, 1)",
                    pointBorderColor: "rgba(28, 175, 6, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(28, 175, 6, 1)",
                    pointHoverBorderColor: "rgba(28, 175, 6, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    data: meeting_completed_list,
                }];

                Chart.helpers.each(Chart.instances, function(instance) {
                    if (instance.chart.canvas.id == "cogno-meet-agent-wise-analytics") {
                        instance.destroy();
                    }
                });

                // Area Chart Example
                let ctx = document.getElementById("cogno-meet-agent-wise-analytics");
                let myLineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: label_list,
                        datasets: dataset_list
                    },
                    options: {
                        maintainAspectRatio: false,
                        layout: {
                            padding: {
                                left: 10,
                                right: 25,
                                top: 25,
                                bottom: 0
                            }
                        },
                        scales: {
                            xAxes: [{
                                time: {
                                    unit: 'date'
                                },
                                gridLines: {
                                    display: false,
                                    drawBorder: false
                                },
                                ticks: {
                                    maxTicksLimit: 7
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    maxTicksLimit: 5,
                                    padding: 10,
                                    beginAtZero: true,
                                    // Include a dollar sign in the ticks
                                    // callback: function(value, index, values) {
                                    //  return number_format(value);
                                    // }
                                    callback: function(value, index, values) {
                                        if (Math.floor(value) === value) {
                                            return value;
                                        }
                                    }
                                },
                                gridLines: {
                                    color: "rgb(234, 236, 244)",
                                    zeroLineColor: "rgb(234, 236, 244)",
                                    drawBorder: false,
                                    borderDash: [2],
                                    zeroLineBorderDash: [2]
                                }
                            }],
                        },
                        legend: {
                            display: true
                        },
                        tooltips: {
                            backgroundColor: "rgb(255,255,255)",
                            bodyFontColor: "#858796",
                            titleMarginBottom: 10,
                            titleFontColor: '#6e707e',
                            titleFontSize: 14,
                            borderColor: '#dddfeb',
                            borderWidth: 1,
                            xPadding: 15,
                            yPadding: 15,
                            displayColors: false,
                            intersect: false,
                            mode: 'index',
                            caretPadding: 10,
                            callbacks: {
                                label: function(tooltipItem, chart) {
                                    var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                                    return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
                                }
                            }
                        }
                    }
                });
            } else {
                console.error(response);
            }
        }
    }
    xhttp.send(params);
}

function export_meeting_analytics(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let startdate = $('#startdate').val();
    let enddate = $('#enddate').val();
    startdate = get_iso_formatted_date(startdate);
    enddate = get_iso_formatted_date(enddate);
    
    let email_field = document.getElementById('filter-data-email');

    let startdate_obj = new Date(startdate);
    let enddate_obj = new Date(enddate);
    let today_date = new Date();
    if (selected_filter_value == "4") {
        if (!startdate.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!enddate.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (startdate_obj.getTime() > enddate_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (enddate_obj.getTime() > today_date.getTime()) {
            general_error_message.innerHTML = "From Date and To Date cannot be a future date.";
            return;
        } else if(startdate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "Start date " + TODAY_DATE_ERROR_TOAST;
            return;
        } else if (enddate_obj.toLocaleDateString() == today_date.toLocaleDateString()) {
            general_error_message.innerHTML =  "End date " + TODAY_DATE_ERROR_TOAST;
            return;
        }
    }

    if (selected_filter_value == "4") {
        let email_value_list = email_field.value;
        email_value_list = email_value_list.split(",")
        if (email_value_list.length == 0) {
            general_error_message.innerHTML = "Please enter valid Email ID";
            return;
        }

        for (const element of email_value_list) {

            if (!regEmail.test(element.trim())) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    let json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "start_date": startdate,
        "end_date": enddate,
        "email_list": email_field.value,
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "agents_usernames_list": window.AGENTS_USERNAMES_LIST,
        "agent_role": agent_role
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/export-meeting-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
       
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            
            if (response.status == 200 && response["export_path"] != null) {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 301) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = response.message;
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if(response.status == 401){
                show_easyassist_toast("Due to an invalid user role meeting analytics could not be downloaded");
            } else {
                show_easyassist_toast("Unable to download meeting analytics");
            } 
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

window.onload = function () {
    create_or_update_cognomeet_agent();
    get_cognomeet_analytics();
}