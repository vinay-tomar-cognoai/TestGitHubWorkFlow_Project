// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';
var agent_nps_analytics_page = 1;
var page_wise_analytics_page = 1;
var page_count_analytics_page = 1;
window.IS_INVITE_AGENT_ENABLED = false;

function show_daily_service_request_analytics() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	let title = document.getElementById("visited-title-select-option").value;
	load_service_request_analytics(start_date, end_date, title, "daily");
}

function show_weeekly_service_request_analytics() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	let title = document.getElementById("visited-title-select-option").value;
	load_service_request_analytics(start_date, end_date, title, "weekly");
}

function show_monthly_service_request_analytics() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	let title = document.getElementById("visited-title-select-option").value;
	load_service_request_analytics(start_date, end_date, title, "monthly");
}

function show_agent_analysis() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	let title = document.getElementById("visited-title-select-option").value;
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
		show_easyassist_toast("Please enter a valid End date.");
		return;
	}
	if(end_date_yyyymmdd<start_date_yyyymmdd)
	{
		show_easyassist_toast("Start Date should be less than End Date.");
		return;
	}
	load_agent_basic_analytics(start_date, end_date, title);
	load_service_request_analytics(start_date, end_date, title, "daily");
	load_agent_wise_request_analytics(start_date, end_date, title);
	load_agent_wise_nps_analytics(start_date, end_date, title, 1);
	load_page_wise_analytics(start_date, end_date, title, 1);
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

window.onload = function(e) {
	activate_analytics_sidebar();
	get_visited_page_title_list();
}

function get_color_with_alpha(color, alpha) {
    var R = parseInt(color.substring(1,3),16);
    var G = parseInt(color.substring(3,5),16);
    var B = parseInt(color.substring(5,7),16);

    return 'rgba(' + R +', ' + G +', ' + B + ', ' + alpha + ')';
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

/******************** START OF API *********************/

function load_agent_basic_analytics(start_date, end_date, title) {
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
	xhttp.open("POST", "/easy-assist/agent/basic-analytics-reverse/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			document.getElementById("div-total-sr").innerHTML = response["total_sr"];
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

			if(document.getElementById("div-avg-session-duration-text")) {
				var avg_session_duration = response["avg_session_duration"];
				if (avg_session_duration < 1) {
					avg_session_duration = Math.round(avg_session_duration * 60)
					document.getElementById("div-avg-session-duration-text").innerHTML = "sec"
				} else {
					avg_session_duration = Math.round(avg_session_duration)
					document.getElementById("div-avg-session-duration-text").innerHTML = "min"
				}
				document.getElementById("div-avg-session-duration").innerHTML = avg_session_duration;
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

	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);

	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/cobrowse-request-analytics-reverse/", true);
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

				let min_messages = 1;
				let max_messages = 1;

				for (var i = 0; i < response["cobrowse_request_analytics"].length; i++) {
					label_list.push(response["cobrowse_request_analytics"][i]["label"]);
					let total_sr = response["cobrowse_request_analytics"][i]["total_sr"];
					let total_sr_closed = response["cobrowse_request_analytics"][i]["total_sr_closed"];
					let total_sr_attended = response["cobrowse_request_analytics"][i]["total_sr_attended"];

					total_sr_list.push(total_sr);
					total_sr_closed_list.push(total_sr_closed);
					total_sr_attended_list.push(total_sr_attended);

					min_messages = Math.min(min_messages, total_sr);
					max_messages = Math.max(max_messages, total_sr);
				}

				let dataset_list = []
				let active_agent_role = response["active_agent_role"];
				dataset_list = [{
					label: "Links Generated",
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
					label: "Sessions joined by the customer",
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
				}];

				let min_step_size = Math.max(5, Math.ceil((max_messages - min_messages) / 5));

				Chart.helpers.each(Chart.instances, function(instance) {
					if (instance.chart.canvas.id == "cobrowse-request-analytics") {
						instance.destroy();
					}
				});

				// Area Chart Example
				var ctx = document.getElementById("cobrowse-request-analytics");
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
	xhttp.open("POST", "/easy-assist/agent/agent-wise-request-analytics-reverse/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
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
						].join('');
						
						if(response["agent_request_analytics_list"][i].hasOwnProperty("group_cobrowse_request_initiated")) {
							window.IS_INVITE_AGENT_ENABLED = true;
							html_table += [
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_initiated"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_received"] + '</td>',
								'<td>' + response["agent_request_analytics_list"][i]["group_cobrowse_request_connected"] + '</td>',
							'</tr>'
							].join('');
						} else {
							window.IS_INVITE_AGENT_ENABLED = false;
							html_table += [
								'</tr>'
							].join('');
						}
					}
				} else {
					html_table += [
							'<tr>',
								'<td class="text-center" colspan="5">No data available in table</td>',
							'</tr>'
						].join('');
				}

				if(window.IS_INVITE_AGENT_ENABLED) {
					html_table = [
						'<table class="table table-bordered" id="agent-session-analytics-data-table" width="100%" cellspacing="0">',
							'<thead>',
								'<tr>',
									'<th>Agent</th>',
									'<th>Links Generated</th>',
									'<th>Sessions joined by the customer</th>',
									'<th>Customers Converted</th>',
									'<th>Group Cobrowse Request Initiated</th>',
									'<th>Group Cobrowse Request Received</th>',
									'<th>Group Cobrowse Request Connected</th>',
								'</tr>',
							'</thead>',
							'<tbody>',
								html_table,
							'</tbody>',
						'</table>'
					].join('');
				} else {
					html_table = [
						'<table class="table table-bordered" id="agent-session-analytics-data-table" width="100%" cellspacing="0">',
							'<thead>',
								'<tr>',
									'<th>Agent</th>',
									'<th>Links Generated</th>',
									'<th>Sessions joined by the customer</th>',
									'<th>Customers Converted</th>',
								'</tr>',
							'</thead>',
							'<tbody>',
								html_table,
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
	xhttp.open("POST", "/easy-assist/agent/agent-wise-nps-analytics-reverse/", true);
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

					var bg_color = "bg-danger";
					var nps = agent_nps_analytics_list[index]["nps"];
					var agent = agent_nps_analytics_list[index]["agent"];

					if (nps >= -100 && nps <= 0) {
						bg_color = "#FC4545";
					} else if (nps > 0 && nps <= 30) {
						bg_color = "#FFA800";
					} else if (nps > 30 && nps <= 70) {
						bg_color = "#0EE872";
					} else if (nps > 70) {
						bg_color = "#05D289";
					}
					let bg_color_light = get_color_with_alpha(bg_color, 0.25);
					nps_analytics += '<div class="small font-weight-bold" style="display: flex;justify-content:space-between;"><span class="float-left">' + -100 + '</span><span class="float-center">' + agent + '</span><span class="float-right">' + 100 + '</span></div>\
                                    <div class="progress mb-4 progress-analytics" data-toggle="tooltip" title="' + nps + '" style="background-color:' + bg_color_light + '">\
                                        <div class="progress-bar" role="progressbar" style="width: ' + (nps+100)/2 + '%;background-color:' + bg_color + ';" aria-valuenow="' + nps + '" aria-valuemin="-100" aria-valuemax="100"></div>\
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
				$('[data-toggle="tooltip"]').tooltip();
			} else {
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}


function load_page_wise_analytics(start_date, end_date, title, page) {

	if(document.getElementById("page-wise-analytics-body")==null){
		return;
	}
	
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
	xhttp.open("POST", "/easy-assist/agent/query-page-analytics-reverse/", true);
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

					var bg_color = "bg-danger";
					var total = query_pages[index]["total"];
					var active_url = query_pages[index]["active_url"];
					let title = query_pages[index]["title"];

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
					page_wise_analytics += '<div class="float-right"><br><button class="btn btn-light" onclick="load_previous_page_wise_analytics()" style="position: absolute;right: 20px;bottom: 15px"><i class="fas fa-chevron-left"></i></button>';					
				}

				if (response.is_last_page == false) {
					page_wise_analytics += '<button class="btn btn-light" onclick="load_next_page_wise_analytics()" style="position: absolute;left: 20px;bottom: 15px"><i class="fas fa-chevron-right"></i></button>';
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


function get_visited_page_title_list() {
	request_params = {};
	json_params = JSON.stringify(request_params);
	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);
	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/get-visited-page-title-list-reverse/", true);
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

					show_agent_analysis();
				}
			}else{
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

function download_reverse_leads_converted_by_url() {

	start_date = document.getElementById("start-date").value;
	end_date = document.getElementById("end-date").value;
	title = document.getElementById("visited-title-select-option").value;
	
	request_params = {
		"start_date": start_date,
		"end_date": end_date,
		"title": title,
		"cobrowsing_type": "reverse",
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
				show_easyassist_toast("Unable to download analytics for reverse cobrowsing URL conversions");
			}

		}
	}
	xhttp.send(params);
}

function download_reverse_unique_customers() {
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
	xhttp.open("POST", "/easy-assist/agent/export-unique-customers-reverse/", true);
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
				show_easyassist_toast("Unable to download analytics for reverse unique customers.");
			}

		}
	}
	xhttp.send(params);
}

function download_reverse_repeated_customers(){
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
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
	xhttp.open("POST", "/easy-assist/agent/export-repeated-customers-reverse/", true);
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
				show_easyassist_toast("Unable to download analytics for reverse repeated customers.");
			}

		}
	}
	xhttp.send(params);
}

function cron_request_reverse_unique_customers() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);
	let title = document.getElementById("visited-title-select-option").value;
	let email = document.getElementById("export-email-input");
	
	if (email) {
		let email_value_list = email.value;
		email_value_list = email_value_list.split(",");

        if (email_value_list.length == 0) {
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
	xhttp.open("POST", "/easy-assist/agent/export-cron-request-unique-customers-reverse/", true);
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
				show_easyassist_toast("Unable to place download request for reverse unique customers.");
			}

		}
	}
	xhttp.send(params);
}

function cron_request_reverse_repeated_customers() {
	let start_date = document.getElementById("start-date").value;
	let end_date = document.getElementById("end-date").value;
	start_date = get_iso_formatted_date(start_date);
    end_date = get_iso_formatted_date(end_date);
	let title = document.getElementById("visited-title-select-option").value;
	let email = document.getElementById("export-email-input-repeated");
	
	if (email) {
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
              	$(".error-text-repeated-div").text("Please enter valid Email Id")
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

	let json_params = JSON.stringify(request_params);

	let encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	
	const params = JSON.stringify(encrypted_data);

	let xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/export-cron-request-repeated-customers-reverse/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);

			if(response.status == 200) {
				$(".error-text-repeated-div ").text("Your request has been received. You shall receive the report in the provided email id within the next 24 hours.");
				$(".error-text-repeated-div ").css('display', 'flex');
				$(".error-text-repeated-div ").css("color", "#10B981");
				setTimeout(function () {
					$('#export-repeated-customer-modal').modal('hide');
				}, 5000);
			} else if(response.status == 300) {
				$(".error-text-repeated-div ").text("Please enter valid Email Id")
	            $(".error-text-repeated-div ").css('display', 'flex');
	            $(".error-text-repeated-div ").css('color', 'red');	
			} else {
				show_easyassist_toast("Unable to place download request for reverse repeated customers.");
			}

		}
	}
	xhttp.send(params);
}
