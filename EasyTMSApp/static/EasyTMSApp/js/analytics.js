// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito, -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

window.onload = function(e) {
	get_all_analytics();
	let export_date_range_element = document.getElementById("select-date-range");
	new EasyassistCustomSelect(export_date_range_element, null, window.CONSOLE_THEME_COLOR);
}

function number_format(number, decimals, dec_point, thousands_sep) {
	// *     example: number_format(1234.56, 2, ',', ' ');
	// *     return: '1 234,56'
	number = (number + '').replace(',', '').replace(' ', '');
	var n = !isFinite(+number) ? 0 : +number,
		prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
		sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
		dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
		s = '',
		toFixedFix = function(number, number_prec) {
			var k_index = Math.pow(10, number_prec);
			return '' + Math.round(number * k_index) / k_index;
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

function get_all_analytics(){
	var start_date = document.getElementById("start-date").value;
	var end_date = document.getElementById("end-date").value;

	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth() + 1;
	var yyyy = today.getFullYear();
	if (dd < 10) {
	    dd = '0' + dd;
	}

	if (mm < 10) {
	    mm = '0' + mm;
	}
	today = yyyy + '-' + mm + '-' + dd;

	var start_date_yyyymmdd = start_date.split("/");
	start_date_yyyymmdd = start_date_yyyymmdd[2] + '-' + start_date_yyyymmdd[1] + '-' + start_date_yyyymmdd[0];
	var end_date_yyyymmdd = end_date.split("/");
	end_date_yyyymmdd = end_date_yyyymmdd[2] + '-' + end_date_yyyymmdd[1] + '-' + end_date_yyyymmdd[0];

	if (end_date_yyyymmdd > today) {
	    alert("Please enter a valid End date");
	    return;
	}
	if (end_date_yyyymmdd < start_date_yyyymmdd) {
	    alert("Please enter a valid start date");
	    return;
	}

	load_card_analytics(start_date, end_date);
	load_service_request_analytics(start_date, end_date, "daily");
}

function load_card_analytics(start_date, end_date) {
	let request_params = {
		"start_date": start_date,
		"end_date": end_date,
	};
	let json_params = JSON.stringify(request_params);

	let encrypted_data = tms_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/tms/card-analytics/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			var response = JSON.parse(this.responseText);
			response = tms_custom_decrypt(response.Response);
			response = JSON.parse(response);
			var analytics_data = response.analytics_data;
			if (document.getElementById("div-total-tickets-generated") && ("TOTAL_TICKETS_GENERATED" in analytics_data)){
				document.getElementById("div-total-tickets-generated").innerHTML = analytics_data["TOTAL_TICKETS_GENERATED"];
			}
			if (document.getElementById("div-total-tickets-unassigned") && ("UNASSIGNED" in analytics_data)){
				document.getElementById("div-total-tickets-unassigned").innerHTML = analytics_data["UNASSIGNED"];
			}
			if (document.getElementById("div-total-tickets-pending") && ("PENDING" in analytics_data)){
				document.getElementById("div-total-tickets-pending").innerHTML = analytics_data["PENDING"];
			}
			if (document.getElementById("div-total-tickets-resolved") && ("RESOLVED" in analytics_data)){
				document.getElementById("div-total-tickets-resolved").innerHTML = analytics_data["RESOLVED"];
			}
		}
	}
	xhttp.send(params);
}

function load_service_request_analytics(start_date, end_date, timeline) {

	let request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"timeline": timeline,
	};
	let json_params = JSON.stringify(request_params);

	let encrypted_data = tms_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/tms/service-request-analytics/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = tms_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response["status"] == 200) {

				let label_list = [];
				let total_tickets_generated_list = []
				let unassigned_list = []
				let pending_list = []
				let resolved_list = []

				let min_messages = 1;
				let max_messages = 1;

				for (var i = 0; i < response["service_request_analytics"].length; i++) {
					label_list.push(response["service_request_analytics"][i]["label"]);
					total_tickets_generated_list.push(response["service_request_analytics"][i]["TOTAL_TICKETS_GENERATED"]);
					unassigned_list.push(response["service_request_analytics"][i]["UNASSIGNED"]);
					pending_list.push(response["service_request_analytics"][i]["PENDING"]);
					resolved_list.push(response["service_request_analytics"][i]["RESOLVED"]);
					min_messages = Math.min(min_messages, response["service_request_analytics"][i]["total_tickets_generated"]);
					max_messages = Math.max(max_messages, response["service_request_analytics"][i]["total_tickets_generated"]);
				}

				let dataset_list = []
				let active_agent_role = response["active_agent_role"];

				dataset_list.push({
					label: "Total Tickets",
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
					data: total_tickets_generated_list,
				})

				dataset_list.push({
					label: "Pending",
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
					data: pending_list,
				})

				dataset_list.push({
					label: "Resolved",
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
					data: resolved_list,
				})

				if(active_agent_role == "admin"){
					dataset_list.push({
						label: "Unassigned",
						lineTension: 0.3,
						backgroundColor: "rgb(255, 102, 0, 0.05)",
						borderColor: "rgb(255, 102, 0, 1)",
						pointRadius: 3,
						pointBackgroundColor: "rgb(255, 102, 0, 1)",
						pointBorderColor: "rgb(255, 102, 0, 1)",
						pointHoverRadius: 3,
						pointHoverBackgroundColor: "rgb(255, 102, 0, 1)",
						pointHoverBorderColor: "rgb(255, 102, 0, 1)",
						pointHitRadius: 10,
						pointBorderWidth: 2,
						data: unassigned_list,
					})
				}

				Chart.helpers.each(Chart.instances, function(instance) {
					if (instance.chart.canvas.id == "service-request-analytics") {
						instance.destroy();
					}
				});

				// Area Chart Example
				var ctx = document.getElementById("service-request-analytics");
				new Chart(ctx, {
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
									// 	return number_format(value);
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

function show_daily_service_request_analytics() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	load_service_request_analytics(start_date, end_date, "daily");
}

function show_weeekly_service_request_analytics() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	load_service_request_analytics(start_date, end_date, "weekly");
}

function show_monthly_service_request_analytics() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	load_service_request_analytics(start_date, end_date, "monthly");
}

function check_select_date_range(el) {
    let selected_range = el.value;

    if(selected_range === '4') {
        document.getElementById('from-date-div').style.display = 'block';
        document.getElementById('to-date-div').style.display = 'block';
        document.getElementById('email-id-div').style.display = 'block';
    } else {
        document.getElementById('from-date-div').style.display = 'none';
        document.getElementById('to-date-div').style.display = 'none';
        document.getElementById('email-id-div').style.display = 'none';
    }
}

function export_request() {
    let start_date, end_date;
    let email_ids = document.getElementById('filter-data-email').value;
    let request_date_type = document.getElementById('select-date-range').value;

    if (request_date_type === '0') {
        document.getElementById('general-error-message').innerHTML = 'Please select date range';
        return;
    } else {
        document.getElementById('general-error-message').innerHTML = '';
    }

    if (request_date_type === '4') {
        start_date = document.getElementById('startdate').value;

        if (!start_date) {
            document.getElementById('general-error-message').innerHTML = 'Please select a start date';
            return;
        } else {
            document.getElementById('general-error-message').innerHTML = '';
        }

        if (!is_valid_date(start_date)) {
            document.getElementById('general-error-message').innerHTML = 'Please select valid start date';
            return;
        } else {
            document.getElementById('general-error-message').innerHTML = '';
        }

        end_date = document.getElementById('enddate').value;

        if (!end_date) {
            document.getElementById('general-error-message').innerHTML = 'Please select a end date';
            return;
        } else {
            document.getElementById('general-error-message').innerHTML = '';
        }

        if (!is_valid_date(end_date)) {
            document.getElementById('general-error-message').innerHTML = 'Please select valid end date';
            return;
        } else {
            document.getElementById('general-error-message').innerHTML = '';
        }

        if(Date.parse(start_date) > Date.parse(end_date)){
            document.getElementById('general-error-message').innerHTML = 'Start date must be less than end date.';
            return;
        } else {
            document.getElementById('general-error-message').innerHTML = '';
        }

        start_date = change_date_format_original(start_date);
        end_date = change_date_format_original(end_date);

        if (email_ids === '') {
            document.getElementById('general-error-message').innerHTML = 'Please enter your Email ID';
            return;
        } else {
            email_ids = email_ids.replace(/\s/g, "");
            document.getElementById('general-error-message').innerHTML = '';
        }

        if (!validate_email(email_ids)) {
            document.getElementById('general-error-message').innerHTML = 'Please enter valid Email ID';
            return;
        } else {
            document.getElementById('general-error-message').innerHTML = '';
        }
    }

    send_export_request_to_server(email_ids, request_date_type, start_date, end_date);
}

function send_export_request_to_server(email_id, request_date_type, start_date, end_date) {
    let request_params = {
        'email_id': email_id,
        'start_date': start_date,
        'end_date': end_date,
        'request_date_type': request_date_type,
    };

    let json_params = JSON.stringify(request_params);
    let encrypted_data = tms_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    let params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/tms/export-analytics/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            let response = JSON.parse(this.responseText);
            response = tms_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200 && response["export_path_exist"] && response["export_path"] !== "None") {
                let export_path = response["export_path"];
                window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
            } else if (response.status == 300) {
                show_desk_toast('You will receive the audit trail data dump on the above email ID within 24 hours.');
                setTimeout(function() {
                    $('#campaign_multi_export_modal').modal('hide');
                }, 2000);
            } else {
                show_desk_toast("Unable to download support history");
            }
        }
    }
    xhttp.send(params);
}

function change_date_format_original(date) {
    let dateParts = date.split("-");
    date = dateParts[2]+"-"+dateParts[1]+"-"+dateParts[0];
    return date.trim();
}

function is_valid_date(date) {
    let date2 = change_date_format_original(date)
    date = new Date(date);
    date2 = new Date(date2);
    let check_date = date instanceof Date && !isNaN(date)
    let check_date2 =date2 instanceof Date && !isNaN(date2)
    return check_date || check_date2;
}

function validate_email(email_ids) {
    let emain_id_list = email_ids.split(",");
    const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

    for(let index=0; index<emain_id_list.length; index++){
        if(!regEmail.test(emain_id_list[index])) return false;
    }
    return true;
}
