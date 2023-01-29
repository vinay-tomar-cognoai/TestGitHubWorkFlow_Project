// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';
var agent_nps_analytics_page = 1;
var page_wise_analytics_page = 1;
window.IS_INVITE_AGENT_ENABLED = false;
window.IS_SESSION_TRANSFER_ENABLED = false;

function load_agent_basic_analytics(start_date, end_date, title) {
	if(document.getElementById("outbound-proxy-select-option")) {
		hide_proxy_outbound_analytics_div();
		show_search_lead_analytics_div();
	}

	let request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"title": title
	};
	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/basic-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			document.getElementById("div-total-sr-closed").innerHTML = response["total_sr_closed"];
			document.getElementById("div-total-sr-closed-url").innerHTML = response["total_sr_closed_by_url"];
			if (document.getElementById("div-repeated-customer") != undefined){
				document.getElementById("div-repeated-customer").innerHTML = response["repeated_customers"]
			}
			if (document.getElementById("div-unique-customers") != undefined){
				document.getElementById("div-unique-customers").innerHTML = response["unique_customers"] 
			}
			if (document.getElementById("div-total-sr-attended") != undefined){
				document.getElementById("div-total-sr-attended").innerHTML = response["total_sr_attended"];
			}
			if (document.getElementById("div-agent-nps") != undefined) {
				document.getElementById("div-agent-nps").innerHTML = response["nps"];
			}
			if (document.getElementById("div-total-sr-lead-captured") != undefined) {
				document.getElementById("div-total-sr-lead-captured").innerHTML = response["total_sr_lead_captured"];
				document.getElementById("outbound-capture-leads-download-icon").style.display = "";
			}

			document.getElementById("div-total-sr-customer-denied").innerHTML = response["total_sr_customer_denied"];

			if (document.getElementById("div-conversion-rate") != undefined) {
				document.getElementById("div-conversion-rate").innerHTML = response["conversion_rate"];
				document.getElementById("div-conversion-rate-text").innerHTML = '%';
			}

			var avg_session_duration = response["avg_session_duration"];
			if (avg_session_duration < 1) {
				avg_session_duration = Math.round(avg_session_duration * 60)
				document.getElementById("div-avg-session-duration-text").innerHTML = "sec"
			} else {
				avg_session_duration = Math.round(avg_session_duration)
				document.getElementById("div-avg-session-duration-text").innerHTML = "min"
			}
			document.getElementById("div-avg-session-duration").innerHTML = avg_session_duration;

			var avg_wait_time = response["avg_wait_time"];
			if (avg_wait_time < 1) {
				avg_wait_time = Math.round(avg_wait_time * 60)
				document.getElementById("div-avg-wait-time-text").innerHTML = "sec"
			} else {
				avg_wait_time = Math.round(avg_wait_time)
				document.getElementById("div-avg-wait-time-text").innerHTML = "min"
			}
			document.getElementById("div-avg-session-duration").innerHTML = avg_session_duration;
			document.getElementById("div-avg-wait-time").innerHTML = avg_wait_time;

			var avg_wait_time_unattended = response["avg_wait_time_unattended"]
			if (avg_wait_time_unattended < 1) {
				avg_wait_time_unattended = Math.round(avg_wait_time_unattended * 60)
				document.getElementById("div-avg-wait-time-text-unattended").innerHTML = "sec"
			} else {
				avg_wait_time_unattended = Math.round(avg_wait_time_unattended)
				document.getElementById("div-avg-wait-time-text-unattended").innerHTML = "min"
			}
			document.getElementById("div-avg-wait-time-unattended").innerHTML = avg_wait_time_unattended;

			let total_sr = response["total_sr"]
			document.getElementById("div-total-sr").innerHTML = total_sr;
		}
	}
	xhttp.send(params);
}

function load_service_request_analytics(start_date, end_date, title, timeline) {
	
	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"timeline": timeline,
		"title": title
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/service-request-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			if (response["status"] == 200) {

				let label_list = [];
				let total_sr_list = [];
				let total_sr_closed_list = [];
                let total_sr_attended_list = [];
                let total_sr_lead_captured_list = [];
                let total_sr_customer_denied_list = [];

				let min_messages = 1;
				let max_messages = 1;

				for (var i = 0; i < response["service_request_analytics"].length; i++) {
					label_list.push(response["service_request_analytics"][i]["label"]);
					total_sr = response["service_request_analytics"][i]["total_sr"];
					let total_sr_closed = response["service_request_analytics"][i]["total_sr_closed"];
                    let total_sr_attended = response["service_request_analytics"][i]["total_sr_attended"];
                    let total_sr_lead_captured = response["service_request_analytics"][i]["total_sr_lead_captured"];
                    let total_sr_customer_denied = response["service_request_analytics"][i]["total_sr_customer_denied"];

					total_sr_list.push(total_sr);
					total_sr_closed_list.push(total_sr_closed);
                    total_sr_attended_list.push(total_sr_attended);
                    total_sr_lead_captured_list.push(total_sr_lead_captured);
                    total_sr_customer_denied_list.push(total_sr_customer_denied);
                    
					min_messages = Math.min(min_messages, total_sr);
					max_messages = Math.max(max_messages, total_sr);
				}

				let dataset_list = []
				let active_agent_role = response["active_agent_role"];
				if (["admin", "supervisor", "admin_ally"].indexOf(active_agent_role) != -1) {
					dataset_list = [{
						label: "Leads Captured",
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
						data: total_sr_lead_captured_list,
					}, {
						label: "Cobrowsing Request Attended",
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
						data: total_sr_attended_list,
					}, {
						label: "Customers Converted",
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
						data: total_sr_closed_list,
					}, {
						label: "Cobrowsing Request denied by Customer",
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
						data: total_sr_customer_denied_list,
					}];
				} else {
					dataset_list = [{
						label: "Cobrowsing Request Attended",
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
						data: total_sr_attended_list,
					}, {
						label: "Customers Converted",
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
						data: total_sr_closed_list,
					}, {
						label: "Cobrowsing Request denied by Customer",
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
						data: total_sr_customer_denied_list,
					}];
				}

				let min_step_size = Math.max(5, Math.ceil((max_messages - min_messages) / 5));

				Chart.helpers.each(Chart.instances, function(instance) {
					if (instance.chart.canvas.id == "service-request-analytics") {
						instance.destroy();
					}
				});

				// Area Chart Example
				var ctx = document.getElementById("service-request-analytics");
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
	let title = document.getElementById("visited-title-select-option").value;
	if(document.getElementById("outbound-proxy-select-option")) {
		if(document.getElementById("outbound-proxy-select-option").value == "search-lead") {
			load_service_request_analytics(start_date, end_date, title, "daily");
		} else {
			load_proxy_service_request_analytics(start_date, end_date, title, "daily");
		}
	} else {
		load_service_request_analytics(start_date, end_date, title, "daily");
	}	
}

function show_weeekly_service_request_analytics() {
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	if(document.getElementById("outbound-proxy-select-option")) {
		if(document.getElementById("outbound-proxy-select-option").value == "search-lead") {
			load_service_request_analytics(start_date, end_date, title, "weekly");
		} else {
			load_proxy_service_request_analytics(start_date, end_date, title, "weekly");
		}
	} else {
		load_service_request_analytics(start_date, end_date, title, "weekly");
	}
}

function show_monthly_service_request_analytics() {
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	if(document.getElementById("outbound-proxy-select-option")) {
		if(document.getElementById("outbound-proxy-select-option").value == "search-lead") {
			load_service_request_analytics(start_date, end_date, title, "monthly");
		} else {
			load_proxy_service_request_analytics(start_date, end_date, title, "monthly");
		}
	} else {
		load_service_request_analytics(start_date, end_date, title, "monthly");
	}
}

function show_agent_analysis() {
	if(document.getElementById("outbound-proxy-select-option")) {
		window.sessionStorage.removeItem("outbound-analytics-filter-value");
	}

	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; 
	var yyyy = today.getFullYear();
	if(dd<10) 
	{
	    dd='0'+dd;
	} 

	if(mm<10) 
	{
	    mm='0'+mm;
	} 
	today = yyyy+'-'+mm+'-'+dd;
	
	var start_date_yyyymmdd = start_date.split("/");
	start_date_yyyymmdd = start_date_yyyymmdd[2]+'-'+start_date_yyyymmdd[1]+'-'+start_date_yyyymmdd[0];
	var end_date_yyyymmdd = end_date.split("/");
	end_date_yyyymmdd = end_date_yyyymmdd[2]+'-'+end_date_yyyymmdd[1]+'-'+end_date_yyyymmdd[0];
	
	if(end_date_yyyymmdd>today)
	{
		show_easyassist_toast("Please enter a valid end date.");
		return;
	}
	if(end_date_yyyymmdd<start_date_yyyymmdd)
	{
		show_easyassist_toast("Start Date should be less than end date.");
		return;
	}
	load_agent_basic_analytics(start_date, end_date, title);
	load_service_request_analytics(start_date, end_date, title, "daily");
	load_agent_wise_request_analytics(start_date, end_date, title);
	load_agent_wise_nps_analytics(start_date, end_date, title, 1);
	load_page_wise_analytics(start_date, end_date, title, 1);
}

function load_agent_wise_request_analytics(start_date, end_date, title) {
	
	if(document.getElementById("agent-wise-request-analytics")==null){
		return;
	}

	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"title": title
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/agent-wise-request-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			if (response.status == 200) {
				let html_table = "";
				let html_table_body = "";
				
				$('#agent-session-analytics-data-table').dataTable().fnClearTable();
                $('#agent-session-analytics-data-table').DataTable().destroy();

				if(response["agent_request_analytics_list"].length > 0) {
					for (var i = 0; i < response["agent_request_analytics_list"].length; i++) {
						html_table_body += [
							'<tr>',
								'<td>' + response["agent_request_analytics_list"][i]["agent"] + '</td>',
						].join('');

						if(window.EASYASSIST_AGENT_ROLE == "admin_ally"){
							let supervisor_text = response["agent_request_analytics_list"][i]["supervisor"];
							let supervisor_text_short = supervisor_text;
							if(supervisor_text.length > 40){
								supervisor_text_short = supervisor_text_short.substring(0, 40) + "...";
							}
							html_table_body += ['<td data-toggle="tooltip" title="' + supervisor_text + '" data-placement="bottom">' + supervisor_text_short + '</td>'].join("");
						}

						html_table_body += ['<td>' + response["agent_request_analytics_list"][i]["total_sr"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr_attended"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr_closed"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr_customer_denied"] + '</td>',
						].join('');

						if(response["agent_request_analytics_list"][i].hasOwnProperty("group_cobrowse_request_initiated")) {
							window.IS_INVITE_AGENT_ENABLED = true;
							html_table_body += [
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_initiated"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_received"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_connected"] + '</td>',
							].join('');

							if(response["agent_request_analytics_list"][i].hasOwnProperty("transferred_agents_requests_received")) {
								window.IS_SESSION_TRANSFER_ENABLED = true;
								html_table_body += [
									'<td>' + response["agent_request_analytics_list"][i]["transferred_agents_requests_received"] + '</td>',
									'<td>' + response["agent_request_analytics_list"][i]["transferred_agents_requests_connected"] + '</td>',
									'<td>' + response["agent_request_analytics_list"][i]["transferred_agents_requests_rejected"] + '</td>',
								].join('');
							} else {
								window.IS_SESSION_TRANSFER_ENABLED = false;
								html_table_body += [
									'</tr>'
								].join('');
							}

						} else {
							window.IS_INVITE_AGENT_ENABLED = false;
							html_table_body += [
								'</tr>'
							].join('');
						}
					}
				} else {
					html_table_body += [
							'<tr>',
								'<td class="text-center" colspan="5">No data available in table</td>',
							'</tr>'
						].join('');
				}
				html_table += [
					'<table class="table table-bordered" id="agent-session-analytics-data-table" width="100%" cellspacing="0">',
						'<thead>',
							'<tr>',
								'<th>Agent</th>',
				].join('');

				if(window.EASYASSIST_AGENT_ROLE == "admin_ally"){
					html_table += [
						'<th>Supervisors</th>',
					].join('');
				}

				if(window.IS_INVITE_AGENT_ENABLED) {
					html_table += [
									'<th>Leads Captured</th>',
									'<th>Request Attended</th>',
									'<th>Customers Converted</th>',
									'<th>Request denied by Customer</th>',
									'<th>Group Cobrowse Request Initiated</th>',
									'<th>Group Cobrowse Request Received</th>',
									'<th>Group Cobrowse Request Connected</th>',
								].join('');
					if(window.IS_SESSION_TRANSFER_ENABLED){
					html_table += [
									'<th>Transfer Requests Received</th>',
									'<th>Transfer Requests Connected</th>',
									'<th>Transfer Requests Not Connected</th>',
									'</tr>',
								'</thead>',
							'<tbody>',
								html_table_body,
							'</tbody>',
						'</table>'
						].join("");
					} else {
						html_table += [
								'</tr>',
								'</thead>',
							'<tbody>',
								html_table_body,
							'</tbody>',
						'</table>'
					].join("");
					}
				} else {
					html_table += [
									'<th>Leads Captured</th>',
									'<th>Request Attended</th>',
									'<th>Customers Converted</th>',
									'<th>Request denied by Customer</th>',
								'</tr>',
							'</thead>',
							'<tbody>',
								html_table_body,
							'</tbody>',
						'</table>'
					].join('');
				}
				

				document.getElementById("agent-wise-request-analytics").innerHTML = html_table;
				update_table_attribute();

				$("#agent-session-analytics-data-table").dataTable({
				    "bJQueryUI":true,
				    "bSort":true,
				    "bPaginate":true,
				    "sPaginationType":"simple_numbers",
				    "iDisplayLength": 10
				});
				$('[data-toggle="tooltip"]').tooltip();
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}



function load_agent_wise_nps_analytics(start_date, end_date, title, page) {
	
	if(document.getElementById("agent-wise-nps-body")==null){return;}

	agent_nps_analytics_page = page;

	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"page": page,
		"title": title
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/agent-wise-nps-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			if (response.status == 200) {
				var nps_analytics = "";
				let agent_nps_analytics_list = response["agent_nps_analytics_list"];

				for (var index = 0; index < agent_nps_analytics_list.length; index++) {

					let background_color = "bg-danger";
					var nps = agent_nps_analytics_list[index]["nps"];
					var agent = agent_nps_analytics_list[index]["agent"];

					if (nps >= -100 && nps <= 0) {
						background_color = "#FC4545";
					} else if (nps > 0 && nps <= 30) {
						background_color = "#FFA800";
					} else if (nps > 30 && nps <= 70) {
						background_color = "#0EE872";
					} else if (nps > 70) {
						background_color = "#05D289";
					}
					let background_color_light = get_color_with_alpha(background_color, 0.25);

					nps_analytics += '<div class="small font-weight-bold" style="display: flex;justify-content:space-between;"><span class="float-left">' + -100 + '</span><span class="float-center">' + agent + '</span><span class="float-right">' + 100 + '</span></div>\
                                    <div class="progress mb-4" data-toggle="tooltip" title="' + nps + '" style="background-color:' + background_color_light + '">\
                                        <div class="progress-bar" role="progressbar" style="width: ' + (nps+100)/2 + '%;background-color:' + background_color + ';" aria-valuenow="' + nps + '" aria-valuemin="-100" aria-valuemax="100"></div>\
                                    </div>';
				}

				if(page!=1){
					nps_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_agent_nps_analytics()"><i class="fas fa-chevron-left"></i></button>';					
				}

				if (!response.is_last_page) {
					nps_analytics += '<button class="btn btn-light" onclick="load_next_agent_nps_analytics()"><i class="fas fa-chevron-right"></i></button>';
				}
				nps_analytics += '</div>';

				document.getElementById("agent-wise-nps-body").innerHTML = nps_analytics;
				$('[data-toggle="tooltip"]').tooltip();
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_next_agent_nps_analytics(is_proxy_analytics=false) {
	agent_nps_analytics_page += 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	if(is_proxy_analytics) {
		load_agent_wise_proxy_nps_analytics(start_date, end_date, title, agent_nps_analytics_page);
	} else {
		load_agent_wise_nps_analytics(start_date, end_date, title, agent_nps_analytics_page);
	}
}

function load_previous_agent_nps_analytics(is_proxy_analytics=false) {
	if (agent_nps_analytics_page == 1) {
		return;
	}
	agent_nps_analytics_page -= 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	if(is_proxy_analytics) {
		load_agent_wise_proxy_nps_analytics(start_date, end_date, title, agent_nps_analytics_page);
	} else {
		load_agent_wise_nps_analytics(start_date, end_date, title, agent_nps_analytics_page);
	}
}


function load_page_wise_analytics(start_date, end_date, title, page) {
	page_wise_analytics_page = page;

	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"page": page,
		"title": title
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/query-page-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			if (response.status == 200) {
				var page_wise_analytics = "";
				let query_pages = response["query_pages"];
				let total_pages = response["total_pages"];

				for (var index = 0; index < query_pages.length; index++) {

					let background_color = "bg-danger";
					var total = query_pages[index]["total"];
					var active_url = query_pages[index]["active_url"];
					let title = query_pages[index]["title"];

					total = Math.floor(total*100/total_pages);

					if (total > 20 && total <= 40) {
						background_color = "bg-warning";
					} else if (total > 40 && total <= 60) {
						background_color = "bg-primary";
					} else if (total > 60 && total <= 80) {
						background_color = "bg-info";
					} else if (total > 80) {
						background_color = "bg-success";
					}

					page_wise_analytics += '<h4 class="small font-weight-bold"><a href="'+active_url+'" target="_blank">' + title + '</a><span class="float-right">' + total + '%</span></h4>\
                                <div class="progress mb-4">\
                                    <div class="progress-bar ' + background_color + '" role="progressbar" style="width: ' + total + '%" aria-valuenow="' + total + '" aria-valuemin="0" aria-valuemax="100"></div>\
                                </div>';
				}

				if(page!=1){
					page_wise_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_page_wise_analytics()"><i class="fas fa-chevron-left"></i></button>';					
				}

				if (!response.is_last_page) {
					page_wise_analytics += '<button class="btn btn-light" onclick="load_next_page_wise_analytics()"><i class="fas fa-chevron-right"></i></button>';
				}

				page_wise_analytics += '</div>';
				document.getElementById("page-wise-analytics-body").innerHTML = page_wise_analytics;
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_next_page_wise_analytics(is_proxy_analytics=false) {
	page_wise_analytics_page += 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	if(is_proxy_analytics) {
		load_page_wise_proxy_analytics(start_date, end_date, title, page_wise_analytics_page);
	} else {
		load_page_wise_analytics(start_date, end_date, title, page_wise_analytics_page);
	}
}

function load_previous_page_wise_analytics(is_proxy_analytics=false) {
	if (page_wise_analytics_page == 1) {
		return;
	}
	page_wise_analytics_page -= 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	if(is_proxy_analytics) {
		load_page_wise_proxy_analytics(start_date, end_date, title, page_wise_analytics_page);
	} else {
		load_page_wise_analytics(start_date, end_date, title, page_wise_analytics_page);
	}
}

function get_visited_page_title_list() {
	request_params = {};
	json_params = JSON.stringify(request_params);
	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);
	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/get-visited-page-title-list-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			if(response.status==200){
				if(response.query_pages.length>0){
					query_pages = response.query_pages;
					var select_html = '<option value="all">All visited pages</option>';
					for(var index=0;index < query_pages.length; index++){
						select_html += '<option value="'+query_pages[index]+'">'+query_pages[index]+'</option>';
					}
					document.getElementById("visited-title-select-option").innerHTML = select_html;
					let applied_filter = window.sessionStorage.getItem("outbound-analytics-filter-value");
					if(applied_filter) {
						load_proxy_outbound_analytics();
					} else {
						show_agent_analysis();
					}
				}
			}else{
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function get_color_with_alpha(color, alpha) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    return 'rgba(' + R +', ' + G +', ' + B + ', ' + alpha + ')';
}

window.onload = function(e) {
	activate_analytics_sidebar();
	get_visited_page_title_list();
	let applied_filter = window.sessionStorage.getItem("outbound-analytics-filter-value");
	if(applied_filter) {
		document.getElementById("outbound-proxy-select-option").value = "proxy-cobrowsing";
		hide_search_lead_analytics_div();
		show_proxy_outbound_analytics_div();
	} else {
		hide_proxy_outbound_analytics_div();
		show_search_lead_analytics_div();
	}
}

function update_table_attribute() {
  var table_elements = document.getElementsByTagName('table');
  for(var idx = 0; idx < table_elements.length; idx ++) {
    var thead_el = table_elements[idx].getElementsByTagName('thead');
    if(thead_el.length == 0) {
      continue;
    }
    thead_el = thead_el[0];
    var tbody_el = table_elements[idx].getElementsByTagName('tbody');
    if(tbody_el.length == 0) {
      continue;
    }

    tbody_el = tbody_el[0];
    for (var row_index = 0; row_index < tbody_el.rows.length; row_index ++) {
      for (var col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
          var column_element = tbody_el.rows[row_index].children[col_index];
          var th_text = thead_el.rows[0].children[col_index].innerText;
          column_element.setAttribute("data-content", th_text);
      }
    }
  }
}

function download_outbound_leads_converted_by_url() {
	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"title": title,
		"cobrowsing_type": "outbound"
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-conversions-by-url/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if(response.status == 200 && response["export_path"] != null) {
				let export_path = response["export_path"];
				window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
			} else {
				show_easyassist_toast("Unable to download analytics for outbound cobrowsing URL conversions");
			}

		}
	}
	xhttp.send(params);
}

function download_outbound_unique_customers() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);
	let title = document.getElementById("visited-title-select-option").value;
	
	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title),
	};

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	
	const params = JSON.stringify(encrypted_data);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-unique-customers-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			if(response.status == 200 && response["export_path"] != null) {
				let export_path = response["export_path"];
				window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
			} else if(response.status == 301 && response["export_path"] == "") {
				$('#export-unique-customer-modal').modal('show');
			} else {
				show_easyassist_toast("Unable to download analytics for outbound unique customers");
			}
		}
	}
	xhttp.send(params);
}

function download_outbound_repeated_customers() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);
	let title = document.getElementById("visited-title-select-option").value;
	
	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title),
	};

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	
	const params = JSON.stringify(encrypted_data);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-repeated-customers-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if(response.status == 200 && response["export_path"] != null) {
				let export_path = response["export_path"];
				window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
			} else if(response.status == 301 && response["export_path"] == "") {
				$('#export-repeated-customer-modal').modal('show');
			} else {
				show_easyassist_toast("Unable to download analytics for outbound repeated customers.");
			}

		}
	}
	xhttp.send(params);
}

function cron_request_outbound_unique_customers() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);
	let title = document.getElementById("visited-title-select-option").value;
	let email = document.getElementById("export-email-input");
	
	if (email) {
		let email_value_list = email.value;
		email_value_list = email_value_list.split(",");

        if (!email_value_list.length) {
            $(".error-text-div ").text("Please enter valid Email Id")
            $(".error-text-div ").css('display', 'flex');
            $(".error-text-div ").css('color', 'red');
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {

            if (!check_valid_email(email_value_list[index].trim())) {
                $(".error-text-div ").text("Please enter valid Email Id")
	            $(".error-text-div ").css('display', 'flex');
	            $(".error-text-div ").css('color', 'red');
	            return;
            }
        }
	}

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title),
		"email": email.value,
	};

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	
	const params = JSON.stringify(encrypted_data);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-cron-request-unique-customers-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if(response.status == 200) {
				$(".error-text-div ").text("Your request has been received. You shall receive the report in the provided email id within the next 24 hours.");
				$(".error-text-div ").css('display', 'flex');
				$(".error-text-div ").css("color", "#10B981");
				setTimeout(function () {
					$('#export-unique-customer-modal').modal('hide');
				}, 5000);
			} else if(response.status == 300) {
				$(".error-text-div ").text("Please enter valid Email Id")
				$(".error-text-div ").css('display', 'flex');
				$(".error-text-div ").css('color', 'red');
			} else {
				show_easyassist_toast("Unable to place download request for outbound unique customers.");
			}

		}
	}
	xhttp.send(params);
}

function cron_request_outbound_repeated_customers() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);
	let title = document.getElementById("visited-title-select-option").value;
	let email = document.getElementById("export-email-input-repeated");
	
	if (email != null) {
		let email_value_list = email.value;
		email_value_list = email_value_list.split(",");

        if (email_value_list.length == 0) {
            $(".error-text-repeated-div").text("Please enter valid Email Id")
            $(".error-text-repeated-div").css('display', 'flex');
            $(".error-text-repeated-div").css('color', 'red');
            return;
        }

        for (let index = 0; index < email_value_list.length; index++) {
        	if (!check_valid_email(email_value_list[index].trim())) {
                $(".error-text-repeated-div").text("Please enter valid Email Id");
	            $(".error-text-repeated-div").css('display', 'flex');
	            $(".error-text-repeated-div").css('color', 'red');
	            return;
            }
        }
	}

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title),
		"email": email.value,
	};

	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	
	const params = JSON.stringify(encrypted_data);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-cron-request-repeated-customers-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if(response.status == 200) {
				$(".error-text-repeated-div").text("Your request has been received. You shall receive the report in the provided email id within the next 24 hours.");
				$(".error-text-repeated-div").css('display', 'flex');
				$(".error-text-repeated-div").css("color", "#10B981");
				setTimeout(function () {
					$('#export-repeated-customer-modal').modal('hide');
				}, 5000);
			} else if(response.status == 300) {
				$(".error-text-repeated-div").text("Please enter valid Email Id")
				$(".error-text-repeated-div").css('display', 'flex');
				$(".error-text-repeated-div").css('color', 'red');
			} else {
				show_easyassist_toast("Unable to place download request for outbound repeated customers.");
			}

		}
	}
	xhttp.send(params);
}

function download_outbound_capture_leads() {

	var startdate_obj = new Date(start_date);
	var enddate_obj = new Date(end_date);

	if (!start_date.length) {
		show_easyassist_toast(EMPTY_START_DATE_ERROR_TOAST);
		return;
	} else if (!end_date.length) {
		show_easyassist_toast(EMPTY_END_DATE_ERROR_TOAST);
		return;
	} else if (startdate_obj.getTime() > enddate_obj.getTime()) {
		show_easyassist_toast("Start date cannot be greater than the end date");
		return;
	}

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
	}

	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-captured-leads/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response.status == 200 && response["export_path"] != null) {
				let export_path = response["export_path"];
				window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;
			} else if (response.status == 103) {
				$("#modal-capture-leads").modal("show");
			} else if (response.status == 300 && response.message) {
				show_easyassist_toast(response.message);
			} else {
				show_easyassist_toast("something went wrong")
			}
		}
	}
	xhttp.send(params);
}

function email_outbound_capture_leads(el) {
	let general_error_message_popup = document.getElementById("general-error-message-popup");
	general_error_message_popup.style.color = "red";
	general_error_message_popup.innerHTML = "";

	const regEmail = /^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;

	let capture_leads_email = document.getElementById("capture-leads-email")

	if (capture_leads_email != null) {
		let email_value_list = capture_leads_email.value;
		email_value_list = email_value_list.split(",");

        if (email_value_list.length == 0) {
            general_error_message_popup.innerHTML = "Please enter valid Email ID";
            return;
        }
		
        for (let index = 0; index < email_value_list.length; index++) {

            if (!regEmail.test(email_value_list[index].trim())) {
                general_error_message_popup.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
	}

	var startdate_obj = new Date(start_date);
	var enddate_obj = new Date(end_date);

	if (!start_date.length) {
		general_error_message_popup.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
		return;
	} else if (!end_date.length) {
		general_error_message_popup.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
		return;
	} else if (startdate_obj.getTime() > enddate_obj.getTime()) {
		general_error_message_popup.innerHTML = "Start date cannot be greater than the end date";
		return;
	}

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"email_id_list": capture_leads_email.value,
	};

	json_params = JSON.stringify(request_params);

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	el.innerHTML = "Exporting...";
	el.disabled = true;

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/email-captured-leads/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response.status == 200) {
				general_error_message_popup.style.color = "green";
				general_error_message_popup.innerHTML = "Your request has been received. You shall receive the report in the provided email id within the next 24 hours.";

				setTimeout(function () {
					$("#modal-capture-leads").modal("hide");
				}, 5000);
			} else if (response.status == 300 && response.message) {
				general_error_message_popup.style.color = "red";
				general_error_message_popup.innerHTML = response.message;
			} else {
				general_error_message_popup.style.color = "red";
				general_error_message_popup.innerHTML = "Unable to download Captured Leads";
			}
			el.innerHTML = "Export";
			el.disabled = false;
		}
	}
	xhttp.send(params);
}

// Proxy Outbound Analytics

function load_proxy_outbound_analytics() {
	
	window.sessionStorage.setItem("outbound-analytics-filter-value", "outbound-proxy");
	hide_search_lead_analytics_div();
	show_proxy_outbound_analytics_div();

	let analytics_card = document.querySelectorAll('.card-cobrowse');
	let canvas_card = document.querySelector(".chart-area");
	let table_card = document.getElementById('agent-wise-proxy-request-analytics');
	let nps_body = document.querySelector("#agent-proxy-wise-nps-body");
	let page_wise_analytics_body = document.querySelector("#page-wise-proxy-analytics-body");

	analytics_card.forEach((elem) => {
		elem.classList.add('skeletel-loading');
	})

	canvas_card.classList.add('skeletel-loading');

	if(table_card) {
		table_card.classList.add('table-skeletel-loading');
	}

	if(nps_body) {
		nps_body.classList.add('bar-skeletel-loader');
	}
	
	if(page_wise_analytics_body) {
		page_wise_analytics_body.classList.add('bar-skeletel-loader');
	}

	let start_date_value = document.getElementById("start-date").value;
	let end_date_value = document.getElementById("end-date").value;
	let title = document.getElementById("visited-title-select-option").value;
	let today_date_obj = new Date();
	let date = today_date_obj.getDate();
	let month = today_date_obj.getMonth() + 1;
	let year = today_date_obj.getFullYear();

	if (date < 10) {
		date = '0' + date;
	}

	if (month < 10) {
		month = '0' + month;
	}

	let today_date = year + '-' + month + '-' + date;

	let start_date = start_date_value.split("/");
	start_date = start_date[2] + '-' + start_date[1] + '-' + start_date[0];

	let end_date = end_date_value.split("/");
	end_date = end_date[2] + '-' + end_date[1] + '-' + end_date[0];

	if (end_date > today_date) {
		show_easyassist_toast("Please enter a valid end date.");
		return;
	}

	if (end_date < start_date) {
		show_easyassist_toast("Start Date should be less than end date.");
		return;
	}

	load_agent_basic_proxy_analytics(start_date, end_date, title);
	load_proxy_service_request_analytics(start_date, end_date, title, "daily");
	load_agent_wise_proxy_request_analytics(start_date, end_date, title);
	load_agent_wise_proxy_nps_analytics(start_date, end_date, title, 1);
	load_page_wise_proxy_analytics(start_date, end_date, title, 1);
}

function load_agent_basic_proxy_analytics(start_date, end_date, title) {

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title)
	};
	
	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	
	const params = JSON.stringify(encrypted_data);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/basic-proxy-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			if(response["status"] == 200) {
				document.getElementById("proxy-total-linked-generated").innerHTML = response["total_links_generated"];
				document.getElementById("proxy-total-session-join-by-customer").innerHTML = response["total_customer_joined"];
				
				if(document.getElementById("proxy-nps")) {
					document.getElementById("proxy-nps").innerHTML = response["nps"]
				}

				let avg_session_duration = response["avg_session_duration"];
				if (avg_session_duration < 1) {
					avg_session_duration = Math.round(avg_session_duration * 60)
					document.getElementById("proxy-avg-session-time-text").innerHTML = "sec"
				} else {
					avg_session_duration = Math.round(avg_session_duration)
					document.getElementById("proxy-avg-session-time-text").innerHTML = "min"
				}
				document.getElementById("proxy-avg-session-time").innerHTML = avg_session_duration;
				
				let avg_wait_time = response["avg_wait_time"];
				if (avg_wait_time < 1) {
					avg_wait_time = Math.round(avg_wait_time * 60)
					document.getElementById("proxy-avg-waiting-time-attended-lead-text").innerHTML = "sec"
				} else {
					avg_wait_time = Math.round(avg_wait_time)
					document.getElementById("proxy-avg-waiting-time-attended-lead-text").innerHTML = "min"
				}
				document.getElementById("proxy-avg-waiting-time-attended-lead").innerHTML = avg_wait_time;

				let avg_wait_time_unattended = response["avg_wait_time_unattended"]
				if (avg_wait_time_unattended < 1) {
					avg_wait_time_unattended = Math.round(avg_wait_time_unattended * 60)
					document.getElementById("proxy-avg-wait-time-unattended-text").innerHTML = "sec";
				} else {
					avg_wait_time_unattended = Math.round(avg_wait_time_unattended)
					document.getElementById("proxy-avg-wait-time-unattended-text").innerHTML = "min";
				}
				document.getElementById("proxy-avg-wait-time-unattended").innerHTML = avg_wait_time_unattended;
				
				document.getElementById("proxy-total-customer-converted").innerHTML = response["total_customer_converted"];
				document.getElementById("proxy-customer-converted-url").innerHTML = response["total_customer_converted_by_url"];
				
				if(document.getElementById("proxy-unique-customer")) {
					document.getElementById("proxy-repeated-customer").innerHTML = response["total_repeated_customers"];
					document.getElementById("proxy-unique-customer").innerHTML = response["total_unique_customers"];
				}

				let analytics_card = document.querySelectorAll('.card-cobrowse');
				analytics_card.forEach((elem) => {
					setTimeout(() => {
						elem.classList.remove('skeletel-loading');
					},1500)        
				})
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_agent_wise_proxy_request_analytics(start_date, end_date, title) {
	
	if(!document.getElementById("agent-wise-proxy-request-analytics")){
		return;
	}

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title)
	};

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};

	const params = JSON.stringify(encrypted_data);
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/agent-wise-proxy-request-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			if (response.status == 200) {
				let html_table = "";
				let html_table_body = "";

				$('#agent-session-analytics-data-table-proxy').dataTable().fnClearTable();
                $('#agent-session-analytics-data-table-proxy').DataTable().destroy();
				
				if(response["agent_request_analytics_list"].length > 0) {
					for (let i = 0; i < response["agent_request_analytics_list"].length; i++) {
						html_table_body += [
							'<tr>',
								'<td>' + response["agent_request_analytics_list"][i]["agent"] + '</td>',
						].join('');

						if(window.EASYASSIST_AGENT_ROLE == "admin_ally"){
							let supervisor_text = response["agent_request_analytics_list"][i]["supervisor"];
							let supervisor_text_short = supervisor_text;
							if(supervisor_text.length > 40){
								supervisor_text_short = supervisor_text_short.substring(0, 40) + "...";
							}
							html_table_body += ['<td data-toggle="tooltip" title="' + supervisor_text + '" data-placement="bottom">' + supervisor_text_short + '</td>'].join("");
						}

						html_table_body += ['<td>' + response["agent_request_analytics_list"][i]["total_links_generated"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_customers_joined"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_customers_converted"] + '</td>',
						].join('');

						if(response["agent_request_analytics_list"][i].hasOwnProperty("group_cobrowse_request_initiated")) {
							window.IS_INVITE_AGENT_ENABLED = true;
							html_table_body += [
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_initiated"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_received"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_connected"] + '</td>',
							].join('');

							if(response["agent_request_analytics_list"][i].hasOwnProperty("transferred_agents_requests_received")) {
								window.IS_SESSION_TRANSFER_ENABLED = true;
								html_table_body += [
									'<td>' + response["agent_request_analytics_list"][i]["transferred_agents_requests_received"] + '</td>',
									'<td>' + response["agent_request_analytics_list"][i]["transferred_agents_requests_connected"] + '</td>',
									'<td>' + response["agent_request_analytics_list"][i]["transferred_agents_requests_rejected"] + '</td>',
								].join('');
							} else {
								window.IS_SESSION_TRANSFER_ENABLED = false;
								html_table_body += [
									'</tr>'
								].join('');
							}

						} else {
							window.IS_INVITE_AGENT_ENABLED = false;
							html_table_body += [
								'</tr>'
							].join('');
						}
					}
				} else {
					html_table_body += [
							'<tr>',
								'<td class="text-center" colspan="5">No data available in table</td>',
							'</tr>'
						].join('');
				}
				html_table += [
					'<table class="table table-bordered" id="agent-session-analytics-data-table-proxy" width="100%" cellspacing="0">',
						'<thead>',
							'<tr>',
								'<th>Agent</th>',
				].join('');

				if(window.EASYASSIST_AGENT_ROLE == "admin_ally"){
					html_table += [
						'<th>Supervisors</th>',
					].join('');
				}

				if(window.IS_INVITE_AGENT_ENABLED) {
					html_table += [
									'<th>Links Generated</th>',
									'<th>Sessions joined by the customers</th>',
									'<th>Customers Converted</th>',
									'<th>Group Cobrowse Request Initiated</th>',
									'<th>Group Cobrowse Request Received</th>',
									'<th>Group Cobrowse Request Connected</th>',
								].join('');
					if(window.IS_SESSION_TRANSFER_ENABLED){
					html_table += [
									'<th>Transfer Requests Received</th>',
									'<th>Transfer Requests Connected</th>',
									'<th>Transfer Requests Not Connected</th>',
									'</tr>',
								'</thead>',
							'<tbody>',
								html_table_body,
							'</tbody>',
						'</table>'
						].join("");
					} else {
						html_table += [
								'</tr>',
								'</thead>',
							'<tbody>',
								html_table_body,
							'</tbody>',
						'</table>'
					].join("");
					}
				} else {
					html_table += [
								'<th>Links Generated</th>',
								'<th>Sessions joined by the customers</th>',
								'<th>Customers Converted</th>',
								'<th>Request denied by Customer</th>',
								'</tr>',
							'</thead>',
							'<tbody>',
								html_table_body,
							'</tbody>',
						'</table>'
					].join('');
				}
				

				document.getElementById("agent-wise-proxy-request-analytics").innerHTML = html_table;
				update_table_attribute();

				$("#agent-session-analytics-data-table-proxy").dataTable({
				    "bJQueryUI":true,
				    "bSort":true,
				    "bPaginate":true,
				    "sPaginationType":"simple_numbers",
				    "iDisplayLength": 10
				});
				$('[data-toggle="tooltip"]').tooltip();

				let table_card = document.getElementById('agent-wise-proxy-request-analytics')
				
				setTimeout(() => {
					table_card.classList.remove('table-skeletel-loading');
				},1500)        
				
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_proxy_service_request_analytics(start_date, end_date, title, timeline) {

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title),
		"timeline": stripHTML(timeline),
	};

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};

	const params = JSON.stringify(encrypted_data);
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/service-proxy-request-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response["status"] == 200) {
				let label_list = [];
				let total_links_generated_list = [];
				let total_customers_joined_list = [];
				let total_customers_converted_list = [];
				let total_links_generated = 0;
				let total_customers_joined = 0;
				let total_customers_converted = 0;
				let min_messages = 1;
				let max_messages = 1;

				for (let i = 0; i < response["service_request_analytics"].length; i++) {
					label_list.push(response["service_request_analytics"][i]["label"]);
					total_links_generated = response["service_request_analytics"][i]["total_links_generated"];
					total_customers_joined = response["service_request_analytics"][i]["total_customers_joined"];
					total_customers_converted = response["service_request_analytics"][i]["total_customers_converted"];

					total_links_generated_list.push(total_links_generated);
					total_customers_joined_list.push(total_customers_joined);
					total_customers_converted_list.push(total_customers_converted);
					min_messages = Math.min(min_messages, total_links_generated);
					max_messages = Math.max(max_messages, total_links_generated);
				}

				let dataset_list = [{
					label: "Links generated",
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
					data: total_links_generated_list,
				}, {
					label: "Sessions joined by customers",
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
					data: total_customers_joined_list,
				}, {
					label: "Customers converted",
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
					data: total_customers_converted_list,
				}];

				Chart.helpers.each(Chart.instances, function (instance) {
					if (instance.chart.canvas.id == "service-request-analytics-proxy") {
						instance.destroy();
					}
				});

				let service_analytics_proxy_element = document.getElementById("service-request-analytics-proxy");
				
				let line_chart_obj = new Chart(service_analytics_proxy_element, {
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
									callback: function (value, index, values) {
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
								label: function (tooltipItem, chart) {
									let datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
									return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
								}
							}
						}
					}
				});

				let chart_area_element = document.querySelectorAll('.chart-area');
				chart_area_element.forEach((element) => {
					setTimeout(() => {
						element.classList.remove('skeletel-loading');
					},1500)        
				})

			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_agent_wise_proxy_nps_analytics(start_date, end_date, title, page) {
	
	if (!document.getElementById("agent-proxy-wise-nps-body")) { 
		return; 
	}

	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"title": stripHTML(title),
		"page": page,
	};

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};

	const params = JSON.stringify(encrypted_data);
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/agent-wise-proxy-nps-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response.status == 200) {
				let nps_analytics = "";
				let agent_nps_analytics_list = response["agent_nps_analytics_list"];

				for (let index = 0; index < agent_nps_analytics_list.length; index++) {

					let background_color = "bg-danger";
					let nps = agent_nps_analytics_list[index]["nps"];
					let agent = agent_nps_analytics_list[index]["agent"];

					if (nps >= -100 && nps <= 0) {
						background_color = "#FC4545";
					} else if (nps > 0 && nps <= 30) {
						background_color = "#FFA800";
					} else if (nps > 30 && nps <= 70) {
						background_color = "#0EE872";
					} else if (nps > 70) {
						background_color = "#05D289";
					}
					let background_color_light = get_color_with_alpha(background_color, 0.25);

					nps_analytics += '<div class="small font-weight-bold" style="display: flex;justify-content:space-between;"><span class="float-left">' + -100 + '</span><span class="float-center">' + agent + '</span><span class="float-right">' + 100 + '</span></div>\
                                    <div class="progress mb-4" data-toggle="tooltip" title="' + nps + '" style="background-color:' + background_color_light + '">\
                                        <div class="progress-bar" role="progressbar" style="width: ' + (nps + 100) / 2 + '%;background-color:' + background_color + ';" aria-valuenow="' + nps + '" aria-valuemin="-100" aria-valuemax="100"></div>\
                                    </div>';
				}

				if (page != 1) {
					nps_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_agent_nps_analytics()"><i class="fas fa-chevron-left"></i></button>';
				}

				if (!response.is_last_page) {
					nps_analytics += '<button class="btn btn-light" onclick="load_next_agent_nps_analytics(true)"><i class="fas fa-chevron-right"></i></button>';
				}
				nps_analytics += '</div>';

				let nps_body = document.getElementById("agent-proxy-wise-nps-body");
				nps_body.innerHTML = nps_analytics;
				$('[data-toggle="tooltip"]').tooltip();

				setTimeout(() => {
					nps_body.classList.remove('bar-skeletel-loader');
				},1500);

			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_page_wise_proxy_analytics(start_date, end_date, title, page) {
	
	let request_params = {
		"start_date": stripHTML(start_date),
		"end_date": stripHTML(end_date),
		"page": page,
		"title": stripHTML(title)
	};
	
	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};

	const params = JSON.stringify(encrypted_data);
	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/query-page-proxy-analytics-outbound/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function () {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response.status == 200) {
				let page_wise_analytics = "";
				let query_pages = response["query_pages"];
				let total_pages = response["total_pages"];

				for (let index = 0; index < query_pages.length; index++) {

					let background_color = "bg-danger";
					let total = query_pages[index]["total"];
					let active_url = query_pages[index]["active_url"];
					let title = query_pages[index]["title"];

					total = Math.floor(total * 100 / total_pages);

					if (total > 20 && total <= 40) {
						background_color = "bg-warning";
					} else if (total > 40 && total <= 60) {
						background_color = "bg-primary";
					} else if (total > 60 && total <= 80) {
						background_color = "bg-info";
					} else if (total > 80) {
						background_color = "bg-success";
					}

					page_wise_analytics += '<h4 class="small font-weight-bold"><a href="' + active_url + '" target="_blank">' + title + '</a><span class="float-right">' + total + '%</span></h4>\
                                <div class="progress mb-4">\
                                    <div class="progress-bar ' + background_color + '" role="progressbar" style="width: ' + total + '%" aria-valuenow="' + total + '" aria-valuemin="0" aria-valuemax="100"></div>\
                                </div>';
				}

				if (page != 1) {
					page_wise_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_page_wise_analytics()"><i class="fas fa-chevron-left"></i></button>';
				}

				if (!response.is_last_page) {
					page_wise_analytics += '<button class="btn btn-light" onclick="load_next_page_wise_analytics(true)"><i class="fas fa-chevron-right"></i></button>';
				}

				page_wise_analytics += '</div>';
				let page_wise_analytics_body = document.getElementById("page-wise-proxy-analytics-body")
				page_wise_analytics_body.innerHTML = page_wise_analytics;

				setTimeout(() => {
					page_wise_analytics_body.classList.remove('bar-skeletel-loader');
				},1500);

			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_outbound_analytics() {
	let select_element = document.getElementById("outbound-proxy-select-option")
	if(select_element) {
		if(select_element.value == "search-lead"){
			show_agent_analysis();	
		} else {
			load_proxy_outbound_analytics();
		}
	} else {
		show_agent_analysis();
	}
}

function hide_search_lead_analytics_div() {
	let search_lead_div = document.getElementById("search-lead-div");
	let service_request_analytics_div = document.getElementById("service-request-analytics");
	let agent_wise_nps_body = document.getElementById("agent-wise-nps-body");
	let page_wise_analytics_body = document.getElementById("page-wise-analytics-body");
	let agent_wise_request_analytics = document.getElementById("agent-wise-request-analytics");
	
	if(search_lead_div && !search_lead_div.classList.contains("d-none")){
		search_lead_div.classList.add("d-none");
	}

	if(service_request_analytics_div && !service_request_analytics_div.classList.contains("d-none")){
		service_request_analytics_div.classList.add("d-none");
	}

	if(agent_wise_nps_body && !agent_wise_nps_body.classList.contains("d-none")){
		agent_wise_nps_body.classList.add("d-none");
	}

	if(page_wise_analytics_body && !page_wise_analytics_body.classList.contains("d-none")){
		page_wise_analytics_body.classList.add("d-none");
	}

	if(agent_wise_request_analytics && !agent_wise_request_analytics.classList.contains("d-none")){
		agent_wise_request_analytics.classList.add("d-none");
	}	
}

function show_search_lead_analytics_div() {
	let search_lead_div = document.getElementById("search-lead-div");
	let service_request_analytics_div = document.getElementById("service-request-analytics");
	let agent_wise_nps_body = document.getElementById("agent-wise-nps-body");
	let page_wise_analytics_body = document.getElementById("page-wise-analytics-body");
	let agent_wise_request_analytics = document.getElementById("agent-wise-request-analytics");
	
	if(search_lead_div && search_lead_div.classList.contains("d-none")){
		search_lead_div.classList.remove("d-none");
	}

	if(service_request_analytics_div && service_request_analytics_div.classList.contains("d-none")){
		service_request_analytics_div.classList.remove("d-none");
	}

	if(agent_wise_nps_body && agent_wise_nps_body.classList.contains("d-none")){
		agent_wise_nps_body.classList.remove("d-none");
	}

	if(page_wise_analytics_body && page_wise_analytics_body.classList.contains("d-none")){
		page_wise_analytics_body.classList.remove("d-none");
	}

	if(agent_wise_request_analytics && agent_wise_request_analytics.classList.contains("d-none")){
		agent_wise_request_analytics.classList.remove("d-none");
	}

}

function show_proxy_outbound_analytics_div() {
	let proxy_analytics_div = document.getElementById("proxy-analytics-div");
	let service_request_analytics_div = document.getElementById("service-request-analytics-proxy");
	let agent_wise_nps_body = document.getElementById("agent-proxy-wise-nps-body");
	let page_wise_analytics_body = document.getElementById("page-wise-proxy-analytics-body");
	let agent_wise_request_analytics = document.getElementById("agent-wise-proxy-request-analytics");

	if(proxy_analytics_div && proxy_analytics_div.classList.contains("d-none")){
		proxy_analytics_div.classList.remove("d-none");
	}

	if(service_request_analytics_div && service_request_analytics_div.classList.contains("d-none")){
		service_request_analytics_div.classList.remove("d-none");
	}

	if(agent_wise_nps_body && agent_wise_nps_body.classList.contains("d-none")){
		agent_wise_nps_body.classList.remove("d-none");
	}

	if(page_wise_analytics_body && page_wise_analytics_body.classList.contains("d-none")){
		page_wise_analytics_body.classList.remove("d-none");
	}

	if(agent_wise_request_analytics && agent_wise_request_analytics.classList.contains("d-none")){
		agent_wise_request_analytics.classList.remove("d-none");
	}
}

function hide_proxy_outbound_analytics_div() {
	let proxy_analytics_div = document.getElementById("proxy-analytics-div");
	let service_request_analytics_div = document.getElementById("service-request-analytics-proxy");
	let agent_wise_nps_body = document.getElementById("agent-proxy-wise-nps-body");
	let page_wise_analytics_body = document.getElementById("page-wise-proxy-analytics-body");
	let agent_wise_request_analytics = document.getElementById("agent-wise-proxy-request-analytics");

	if(proxy_analytics_div && !proxy_analytics_div.classList.contains("d-none")){
		proxy_analytics_div.classList.add("d-none");
	}

	if(service_request_analytics_div && !service_request_analytics_div.classList.contains("d-none")){
		service_request_analytics_div.classList.add("d-none");
	}

	if(agent_wise_nps_body && !agent_wise_nps_body.classList.contains("d-none")){
		agent_wise_nps_body.classList.add("d-none");
	}

	if(page_wise_analytics_body && !page_wise_analytics_body.classList.contains("d-none")){
		page_wise_analytics_body.classList.add("d-none");
	}

	if(agent_wise_request_analytics && !agent_wise_request_analytics.classList.contains("d-none")){
		agent_wise_request_analytics.classList.add("d-none");
	}
}

function export_outbound_analytics(el) {
	if(document.getElementById("outbound-proxy-select-option")) {
		let selected_value = document.getElementById("outbound-proxy-select-option").value
		if(selected_value == "search-lead") {
			export_outbound_search_lead_analytics(el);
		} else {
			export_outbound_proxy_analytics(el);
		}
	} else {
		export_outbound_search_lead_analytics(el);
	}
}

function export_outbound_proxy_analytics(el) {

    let general_error_message = document.getElementById("general-error-message");
    general_error_message.style.color = "red";
    general_error_message.innerHTML = "";

    let selected_filter_value = document.getElementById("select-date-range").value;

    if (selected_filter_value == "0") {
        general_error_message.innerHTML = "Please select valid date range filter";
        return;
    }

    let start_date = $('#startdate').val();
    let end_date = $('#enddate').val();
    start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);

    let email_field = document.getElementById('filter-data-email');

    let start_date_obj = new Date(start_date);
    let end_date_obj = new Date(end_date);
    let today_date = new Date();
    if (selected_filter_value == "4") {
        if (!start_date.length) {
            general_error_message.innerHTML = EMPTY_START_DATE_ERROR_TOAST;
            return;
        } else if (!end_date.length) {
            general_error_message.innerHTML = EMPTY_END_DATE_ERROR_TOAST;
            return;
        } else if (start_date_obj.getTime() > end_date_obj.getTime()) {
            general_error_message.innerHTML = "Start date cannot be greater than the end date";
            return;
        } else if (end_date_obj.getTime() > today_date.getTime()) {
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

        for (let index = 0; index < email_value_list.length; index++) {

            if (!check_valid_email(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    let json_string = JSON.stringify({
        "selected_filter_value": stripHTML(selected_filter_value),
        "startdate": stripHTML(start_date),
        "enddate": stripHTML(end_date),
        "email": stripHTML(email_field.value),
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/sales-ai/export-outbound-proxy-analytics/", true);
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
            } else if (response.status == 300) {
                general_error_message.style.color = "green";
                general_error_message.innerHTML = "Your request has been recorded. You will get the email in next 24 hrs.";
                setTimeout(function() {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else {
                show_easyassist_toast("Unable to download outbound proxy analytics");
            }
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}
