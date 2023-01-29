// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';
var agent_nps_analytics_page = 1;
var page_wise_analytics_page = 1;

function number_format(number, decimals, dec_point, thousands_sep) {
    // *     example: number_format(1234.56, 2, ',', ' ');
    // *     return: '1 234,56'
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
        let prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        s = '',
        toFixedFix = function(n, prec) {
            var k = Math.pow(10, prec);
            return '' + Math.round(n * k) / k;
        };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}


function show_cogno_meet_analysis() {
    let start_date = document.getElementById("start-date").value;
    let end_date = document.getElementById("end-date").value;
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; 
    var yyyy = today.getFullYear();

    if(dd < 10) {
        dd='0'+dd;
    } 

    if(mm<10) {
        mm = '0' + mm;
    }

    let today = yyyy + '-' + mm + '-' + dd;

    var start_date_yyyymmdd = start_date.split("/");
    start_date_yyyymmdd = start_date_yyyymmdd[2]+'-'+start_date_yyyymmdd[1]+'-'+start_date_yyyymmdd[0];
    var end_date_yyyymmdd = end_date.split("/");
    end_date_yyyymmdd = end_date_yyyymmdd[2]+'-'+end_date_yyyymmdd[1]+'-'+end_date_yyyymmdd[0];
    
    // if(end_date_yyyymmdd>today) {
    //     alert("Please enter a valid End date");
    //     return;
    // }
    // if(end_date_yyyymmdd<start_date_yyyymmdd) {
    //     alert("Please enter a valid start date");
    //     return;
    // }
    load_cogno_meet_basic_analytics(start_date, end_date);
    load_cogno_meet_analytics(start_date, end_date, "daily");
    load_cogno_meet_daily_time_trend();
    load_cobrowsing_cogno_meet_analytics();
    if(document.getElementById('cogno-meet-agent-wise-analytics')) {
        show_agent_wise_cogno_meet_analytics();
    }
}

function load_cogno_meet_basic_analytics(start_date, end_date) {
    let request_params = {
        "start_date": start_date,
        "end_date": end_date
    };
    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/cogno-meet-basic-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            document.getElementById("cogno-meet-total-meeting-scheduled").innerHTML = 148;
            document.getElementById("cogno-meet-total-meeting-completed").innerHTML = 130;
            document.getElementById("cogno-meet-total-ongoing-meeting").innerHTML = 5;
        }
    }
    xhttp.send(params);
}

function show_daily_cogno_meeting_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    load_cogno_meet_analytics(start_date, end_date, "daily");
}

function show_weekly_cogno_meeting_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    load_cogno_meet_analytics(start_date, end_date, "weekly");
}

function show_monthly_cogno_meeting_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    load_cogno_meet_analytics(start_date, end_date, "monthly");
}

function load_cogno_meet_analytics(start_date, end_date, timeline) {

    request_params = {
        "start_date": start_date,
        "end_date": end_date,
        "timeline": timeline,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/cogno-meet-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                let label_list = [];
                let meeting_completed_list = [31,21,10,23,10,31,48,21,15,10];
                let meeting_scheduled_list = [37,45,42,28,39,35,54,42,42,28];
                let meeting_ongoing_list =   [1,0,0,1,1,1,0,0,0,1];
                let  not_initiated_message = "Video Conferencing Not Initiated";


                for (var i = 0; i < response["cogno_meet_analytics"].length; i++) {
                    label_list.push(response["cogno_meet_analytics"][i]["label"]);
                    // total_meeting_completed = response["cogno_meet_analytics"][i]["total_meeting_completed"];
                    // total_meeting_scheduled = response["cogno_meet_analytics"][i]["total_meeting_scheduled"];
                    // total_meeting_ongoing = response["cogno_meet_analytics"][i]["total_ongoing_meeting"];

                    // meeting_completed_list.push(total_meeting_completed);
                    // meeting_scheduled_list.push(total_meeting_scheduled);
                    // meeting_ongoing_list.push(total_meeting_ongoing);
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

                // Area Chart Example
                var ctx = document.getElementById("cogno-meet-analytics");
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

function load_cogno_meet_daily_time_trend() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/cogno-meet-daily-time-trend-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                // label_list = [{'label': '10 AM-11 AM', 'total_ongoing_meeting': 16}, {'label': '11 AM-12 PM', 'total_ongoing_meeting': 22}, {'label': '12 PM-1 PM', 'total_ongoing_meeting': 19}, {'label': '1 PM-2 PM', 'total_ongoing_meeting': 4}, {'label': '2 PM-3 PM', 'total_ongoing_meeting': 8}, {'label': '3 PM-4 PM', 'total_ongoing_meeting': 14}, {'label': '4 PM-5 PM', 'total_ongoing_meeting': 17}];
                // meeting_ongoing_list =   [16,22,19,4,8,14,17];
                label_list=[["10 AM","11 AM"],["11 AM","12 PM"],["12 PM","1 PM"],["1 PM","2 PM"],["2 PM","3 PM"],["3 PM","4 PM"],["4 PM","5 PM"]];
                meeting_ongoing_list=[16,22,19,4,8,14,17];
                // for (var i = 0; i < response["cogno_meet_daily_time_trend"].length; i++) {
                //     label_list.push(response["cogno_meet_daily_time_trend"][i]["label"].split('-'));
                //      total_ongoing_meeting = response["cogno_meet_daily_time_trend"][i]["total_ongoing_meeting"];

                //     meeting_ongoing_list.push(total_ongoing_meeting);
                // }
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
                    data: meeting_ongoing_list,
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
    xhttp.send(null);
}

function show_agent_wise_cogno_meet_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    let agent_id = document.getElementById("cogno-meet-select-agent").value;
    load_agent_wise_cogno_meet_analytics(start_date, end_date, agent_id, "daily");
}

function show_daily_agent_wise_cogno_meet_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    agent_id = document.getElementById("cogno-meet-select-agent").value;
    load_agent_wise_cogno_meet_analytics(start_date, end_date, agent_id, "daily");
}

function show_weekly_agent_wise_cogno_meet_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    agent_id = document.getElementById("cogno-meet-select-agent").value;
    load_agent_wise_cogno_meet_analytics(start_date, end_date, agent_id, "weekly");
}

function show_monthly_agent_wise_cogno_meet_analytics() {
    start_date = document.getElementById("start-date").value;
    end_date = document.getElementById("end-date").value;
    agent_id = document.getElementById("cogno-meet-select-agent").value;
    load_agent_wise_cogno_meet_analytics(start_date, end_date, agent_id, "monthly");
}

function load_agent_wise_cogno_meet_analytics(start_date, end_date, agent_id, timeline) {

    request_params = {
        "start_date": start_date,
        "end_date": end_date,
        "timeline": timeline,
        "agent_id": agent_id,
    };
    console.log(request_params)
    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/cogno-meet-agent-wise-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {

                label_list = [];
                meeting_completed_list = [31,21,10,23,10,31,48,21,15,10];
                meeting_scheduled_list = [37,45,42,28,39,35,54,42,42,28];

                for (var i = 0; i < response["cogno_meet_agent_wise_analytics"].length; i++) {
                    label_list.push(response["cogno_meet_agent_wise_analytics"][i]["label"]);
                    // total_meeting_completed = response["cogno_meet_agent_wise_analytics"][i]["total_meeting_completed"];
                    // total_meeting_scheduled = response["cogno_meet_agent_wise_analytics"][i]["total_meeting_scheduled"];

                    // meeting_completed_list.push(total_meeting_completed);
                    // meeting_scheduled_list.push(total_meeting_scheduled);
                }

                dataset_list = []
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
                var ctx = document.getElementById("cogno-meet-agent-wise-analytics");
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

function load_cobrowsing_cogno_meet_analytics() {

    request_params = {
        "start_date": start_date,
        "end_date": end_date,
    };

    json_params = JSON.stringify(request_params);

    encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/easy-assist/agent/cogno-meet-cobrowse-video-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {
                // cobrowsing_request_count = response["cogno_meet_cobrowsing_analytics"]["cobrowsing_request_count"]
                // meeting_request_count = response["cogno_meet_cobrowsing_analytics"]["meeting_request_count"]
                let cobrowsing_request_count = 45;
                let meeting_request_count = 55;

                Chart.helpers.each(Chart.instances, function(instance) {
                    if (instance.chart.canvas.id == "cogno-meet-cobrowse-pie-chart") {
                        instance.destroy();
                    }
                });

                // Area Chart Example
                var ctx = document.getElementById("cogno-meet-cobrowse-pie-chart");
                var myPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        datasets: [{
                            fill: true,
                            backgroundColor: ["rgba(128, 110, 243, 1)", "rgb(22, 161, 170, 1)"],
                            data: [cobrowsing_request_count, meeting_request_count]
                        }],
                        labels: ['Cobrowsing', 'Video Conference']
                    },
                });
            } else {
                console.error(response);
            }
        }
    }
    xhttp.send(params);
}

window.onload = function(e) {
    show_cogno_meet_analysis();
}
