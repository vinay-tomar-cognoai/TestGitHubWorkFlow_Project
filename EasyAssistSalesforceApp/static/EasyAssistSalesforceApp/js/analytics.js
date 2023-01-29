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
		prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
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

function load_agent_basic_analytics(start_date, end_date, title) {
	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"title": title
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/basic-analytics/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);
			document.getElementById("div-total-sr").innerHTML = response["total_sr"];
			document.getElementById("div-total-sr-closed").innerHTML = response["total_sr_closed"];
			if (document.getElementById("div-total-sr-attended") != undefined){
				document.getElementById("div-total-sr-attended").innerHTML = response["total_sr_attended"];
			}
			if (document.getElementById("div-total-sr-not-closed") != undefined){
				document.getElementById("div-total-sr-not-closed").innerHTML = response["total_sr_not_closed"];
			}
			if (document.getElementById("div-total-sr-not-initiated-after-request") != undefined) {
				document.getElementById("div-total-sr-not-initiated-after-request").innerHTML = response["total_sr_not_initiated_after_request"];
			}
			if (document.getElementById("div-total-sr-not-initiated-after-assigned") != undefined){
				document.getElementById("div-total-sr-not-initiated-after-assigned").innerHTML = response["total_sr_not_initiated_after_assigned"];
			}
			if (document.getElementById("div-agent-nps") != undefined) {
				document.getElementById("div-agent-nps").innerHTML = response["nps"];
			}
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

	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/service-request-analytics/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);

			if (response["status"] == 200) {

				label_list = [];
				total_sr_list = [];
				total_sr_closed_list = [];
				total_remaining_sr_list = [];
				total_sr_attended_list = [];
				total_sr_not_initiated_after_request_list = [];
				total_sr_not_initiated_after_assigned_list = [];
				not_initiated_message = "Cobrowsing Request Not Initiated";

				min_messages = 1;
				max_messages = 1;

				for (var i = 0; i < response["service_request_analytics"].length; i++) {
					label_list.push(response["service_request_analytics"][i]["label"]);
					total_sr = response["service_request_analytics"][i]["total_sr"];
					total_sr_closed = response["service_request_analytics"][i]["total_sr_closed"];
					total_remaining_sr = response["service_request_analytics"][i]["total_remaining_sr"];
					total_sr_attended = response["service_request_analytics"][i]["total_sr_attended"];
					total_sr_not_initiated_after_request = response["service_request_analytics"][i]["total_sr_not_initiated_after_request"];
					total_sr_not_initiated_after_assigned = response["service_request_analytics"][i]["total_sr_not_initiated_after_assigned"];

					total_sr_list.push(total_sr);
					total_sr_closed_list.push(total_sr_closed);
					total_remaining_sr_list.push(total_remaining_sr);
					total_sr_attended_list.push(total_sr_attended);
					total_sr_not_initiated_after_request_list.push(total_sr_not_initiated_after_request);
					total_sr_not_initiated_after_assigned_list.push(total_sr_not_initiated_after_assigned);
					min_messages = Math.min(min_messages, total_sr);
					max_messages = Math.max(max_messages, total_sr);
				}

				if (document.getElementById("div-total-sr-not-initiated-after-request") == undefined) {
					total_sr_not_initiated_after_request_list = total_sr_not_initiated_after_assigned_list;
					not_initiated_message = "Cobrowsing Request Unattended"
				}

				dataset_list = []
				active_agent_role = response["active_agent_role"];
				if (active_agent_role == "admin" || active_agent_role == "supervisor") {
					dataset_list = [{
						label: "Cobrowsing Request Initiated",
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
						data: total_sr_list,
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
						label: not_initiated_message,
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
						data: total_sr_not_initiated_after_request_list,
					}];
				} else {
					dataset_list = [{
						label: "Cobrowsing Request Initiated",
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
						data: total_sr_list,
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
						label: "Customers Not Converted",
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
						data: total_remaining_sr_list,
					}, {
						label: not_initiated_message,
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
						data: total_sr_not_initiated_after_request_list,
					}];
				}

				min_step_size = Math.max(5, Math.ceil((max_messages - min_messages) / 5));

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
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_service_request_analytics(start_date, end_date, title, "daily");
}

function show_weeekly_service_request_analytics() {
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_service_request_analytics(start_date, end_date, title, "weekly");
}

function show_monthly_service_request_analytics() {
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_service_request_analytics(start_date, end_date, title, "monthly");
}

function show_agent_analysis() {
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
		alert("Please enter a valid End date");
		return;
	}
	if(end_date_yyyymmdd<start_date_yyyymmdd)
	{
		alert("Please enter a valid start date");
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

	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/agent-wise-request-analytics/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);
			if (response.status == 200) {
				var html_table = "";

				if(response["agent_request_analytics_list"].length > 0) {
					for (var i = 0; i < response["agent_request_analytics_list"].length; i++) {
						html_table += [
							'<tr>',
								'<td>' + response["agent_request_analytics_list"][i]["agent"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr_attended"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr_closed"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["total_sr_not_attended"] + '</td>',
							'</tr>'
						].join('');
					}
				} else {
					html_table += [
							'<tr>',
								'<td class="text-center" colspan="5">No data available in table</td>',
							'</tr>'
						].join('');
				}
				html_table = [
					'<table class="table table-bordered" id="agent-session-analytics-data-table" width="100%" cellspacing="0">',
						'<thead>',
							'<tr>',
								'<th>Agent</th>',
								'<th>Cobrowsing Request Initiated</th>',
								'<th>Cobrowsing Request Attended</th>',
								'<th>Customers Converted</th>',
								'<th>Cobrowsing Request Unattended</th>',
							'</tr>',
						'</thead>',
						'<tbody>',
							html_table,
						'</tbody>',
					'</table>'
				].join('');

				document.getElementById("agent-wise-request-analytics").innerHTML = html_table;
				$("#agent-session-analytics-data-table").dataTable({
				    "bJQueryUI":true,
				    "bSort":false,
				    "bPaginate":true,
				    "sPaginationType":"simple_numbers",
				    "iDisplayLength": 10
				});
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

	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/agent-wise-nps-analytics/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);
			if (response.status == 200) {
				var nps_analytics = "";
				agent_nps_analytics_list = response["agent_nps_analytics_list"];

				for (var index = 0; index < agent_nps_analytics_list.length; index++) {

					var bg_color = "bg-danger";
					var nps = agent_nps_analytics_list[index]["nps"];
					var agent = agent_nps_analytics_list[index]["agent"];

					if (nps > 20 && nps <= 40) {
						bg_color = "bg-warning";
					} else if (nps > 40 && nps <= 60) {
						bg_color = "bg-primary";
					} else if (nps > 60 && nps <= 80) {
						bg_color = "bg-info";
					} else if (nps > 80) {
						bg_color = "bg-success";
					}

					nps_analytics += '<h4 class="small font-weight-bold">' + agent + ' <span class="float-right">' + nps + '%</span></h4>\
                                    <div class="progress mb-4">\
                                        <div class="progress-bar ' + bg_color + '" role="progressbar" style="width: ' + nps + '%" aria-valuenow="' + nps + '" aria-valuemin="0" aria-valuemax="100"></div>\
                                    </div>';
				}

				if(page!=1){
					nps_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_agent_nps_analytics()"><i class="fas fa-chevron-left"></i></button>';					
				}

				if (response.is_last_page == false) {
					nps_analytics += '<button class="btn btn-light" onclick="load_next_agent_nps_analytics()"><i class="fas fa-chevron-right"></i></button>';
				}
				nps_analytics += '</div>';

				document.getElementById("agent-wise-nps-body").innerHTML = nps_analytics;
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function load_next_agent_nps_analytics() {
	agent_nps_analytics_page += 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_agent_wise_nps_analytics(start_date, end_date, title, agent_nps_analytics_page);
}

function load_previous_agent_nps_analytics() {
	if (agent_nps_analytics_page == 1) {
		return;
	}
	agent_nps_analytics_page -= 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_agent_wise_nps_analytics(start_date, end_date, title, agent_nps_analytics_page);
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

	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/query-page-analytics/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);
			if (response.status == 200) {
				var page_wise_analytics = "";
				query_pages = response["query_pages"];
				total_pages = response["total_pages"];

				for (var index = 0; index < query_pages.length; index++) {

					var bg_color = "bg-danger";
					var total = query_pages[index]["total"];
					var active_url = query_pages[index]["active_url"];
					var title = query_pages[index]["title"];

					total = Math.floor(total*100/total_pages);

					if (total > 20 && total <= 40) {
						bg_color = "bg-warning";
					} else if (total > 40 && total <= 60) {
						bg_color = "bg-primary";
					} else if (total > 60 && total <= 80) {
						bg_color = "bg-info";
					} else if (total > 80) {
						bg_color = "bg-success";
					}

					page_wise_analytics += '<h4 class="small font-weight-bold"><a href="'+active_url+'" target="_blank">' + title + '</a><span class="float-right">' + total + '%</span></h4>\
                                <div class="progress mb-4">\
                                    <div class="progress-bar ' + bg_color + '" role="progressbar" style="width: ' + total + '%" aria-valuenow="' + total + '" aria-valuemin="0" aria-valuemax="100"></div>\
                                </div>';
				}

				if(page!=1){
					page_wise_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_page_wise_analytics()"><i class="fas fa-chevron-left"></i></button>';					
				}

				if (response.is_last_page == false) {
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

function load_next_page_wise_analytics() {
	page_wise_analytics_page += 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_page_wise_analytics(start_date, end_date, title, page_wise_analytics_page);
}

function load_previous_page_wise_analytics() {
	if (page_wise_analytics_page == 1) {
		return;
	}
	page_wise_analytics_page -= 1;
	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	load_page_wise_analytics(start_date, end_date, title, page_wise_analytics_page);
}

function get_visited_page_title_list() {
	request_params = {};
	json_params = JSON.stringify(request_params);
	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);
	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/get-visited-page-title-list/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);
			if(response.status==200){
				if(response.query_pages.length>0){
					query_pages = response.query_pages;
					var select_html = '<option value="all">All visited pages</option>';
					for(var index=0;index < query_pages.length; index++){
						select_html += '<option value="'+query_pages[index]+'">'+query_pages[index]+'</option>';
					}
					document.getElementById("visited-title-select-option").innerHTML = select_html;
					show_agent_analysis();
				}
			}else{
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

window.onload = function(e) {
	get_visited_page_title_list();
}

function download_not_initiated_customer_details() {
	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"title": title
	};
	json_params = JSON.stringify(request_params);

	encrypted_data = custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist-salesforce/agent/export-not-initiated-customer-details/?salesforce_token=" + window.SALESFORCE_TOKEN, true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = custom_decrypt(response.Response);
			response = JSON.parse(response);
			
			export_path = response["export_path"];
			window.location = window.location.protocol + "//" + window.location.host + "/" + export_path;

		}
	}
	xhttp.send(params);
}
