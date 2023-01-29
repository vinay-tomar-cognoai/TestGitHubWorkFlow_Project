function show_general_analysis() {
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
	load_general_analytics(start_date, end_date, title);
}

function load_general_analytics(start_date, end_date, title) {
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
	xhttp.open("POST", "/easy-assist/agent/general-analytics/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			let response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);

			let console_theme_color = getComputedStyle(document.body).getPropertyValue('--color_rgb');
			let console_theme_color_light = getComputedStyle(document.body).getPropertyValue('--color_rgba_60');
			if(console_theme_color.length == 0) {
				console_theme_color = '#0254D7';
				console_theme_color_light = get_color_with_alpha(console_theme_color, 0.6);
			}

			Chart.helpers.each(Chart.instances, function(instance) {
				if (instance.chart.canvas.id == "general-analytics-pie-chart" || instance.chart.canvas.id == "general-analytics-bar-graph") {
					instance.destroy();
				}
			});

			let inbound_analytics = response['total_inbound_request_attended']
			let outbound_analytics = response['total_outbound_request_attended']
			let inbound_analytics_initiated = response['total_inbound_request_initiated']
			let outbound_analytics_initiated = response['total_outbound_request_initiated']
			// Area Chart Example
			var ctx_pie = document.getElementById("general-analytics-pie-chart");
			var ctx_bar = document.getElementById("general-analytics-bar-graph");
			if(inbound_analytics == 0 && outbound_analytics == 0) {
				ctx_pie.style.display = "none";
				
				document.getElementById('no-data-img-pie').style.display = "flex";

			} else {
				
				ctx_pie.width = "100%";
				ctx_pie.height = "100%";
				var myPieChart = new Chart(ctx_pie, {
					type: 'pie',
					plugins: [ChartDataLabels],
					font: {
						family: "Silka"
					},
					data: {
						datasets: [{
							fill: true,
							backgroundColor: [console_theme_color, console_theme_color_light],
							hoverBackgroundColor: [console_theme_color, console_theme_color_light],
							data: [inbound_analytics, outbound_analytics]
						}],
						labels: ['Inbound Analytics', 'Outbound Analytics']
					},
					options: {
						plugins: {
							// Change options for ALL labels of THIS CHART
							datalabels: {
								formatter: (value, ctx) => {
						 
								  let datasets = ctx.chart.data.datasets;
						 
								  if (datasets.indexOf(ctx.dataset) === datasets.length - 1) {
									let sum = datasets[0].data.reduce((a, b) => a + b, 0);
									let percentage = Math.round((value / sum) * 100);
									if(percentage < 10)
										return "";
									return percentage + '%';
								  } else {
									return percentage+ '%';
								  }
								},
								color: '#fff',
								font: {
									weight: 'bold',
									size: 20,
									family: 'Silka',
									style: 'normal'
								  },
								align: 'centre',
							},
						},
						legend: {
							labels: { 
							  fontFamily: 'Silka'
							},
							onClick: function(event, legendItem) {}
						}
					}
				});
				ctx_pie.style.display = "block";
				document.getElementById('no-data-img-pie').style.display = "none";
			}
			if(inbound_analytics_initiated == 0 && outbound_analytics_initiated == 0)
			{
				ctx_bar.style.display = "none";
				document.getElementById('no-data-img-bar').style.display = "flex";

			} else {
				var bar_graph_data_inbound = [
										response['total_inbound_request_initiated'],
										response['total_inbound_request_attended'],
										response['total_inbound_request_converted']
									]
				var bar_graph_data_outbound = [
					response['total_outbound_request_initiated'],
					response['total_outbound_request_attended'],
					response['total_outbound_request_converted']
				]
				ctx_bar.width = "100%";
				ctx_bar.height = "100%";
				var data = {
					labels: ["Requests initiated", "Requests attended", "Customers converted"],
					datasets: [
						{
							label: "Inbound Analytics",
							backgroundColor: console_theme_color,
							hoverBackgroundColor: console_theme_color,
							data: bar_graph_data_inbound
						},
						{
							label: "Outbound Analytics",
							backgroundColor: console_theme_color_light,
							hoverBackgroundColor: console_theme_color_light,
							data: bar_graph_data_outbound
						},
					]
				};
				var myBarGraph = new Chart(ctx_bar, {
					type: 'bar',
					data: data,
					options : {
						scales: {
							xAxes: [{
								gridLines: {
									display:false
								},
								fontFamily: "Silka"
							}],
						},
						scales: {
							yAxes: [{
								ticks: {
									beginAtZero: true
								}
							}]
						},
						legend: {
							labels: { 
							  fontFamily: 'Silka'
							}
						}
					}
				});
				ctx_bar.style.display = "block";
				
				document.getElementById('no-data-img-bar').style.display = "none";
			}

            let nps_analytics = "";
            var nps_score = [response['inbound_nps_score'], response['outbound_nps_score']]
            for (var index = 0; index < 2; index++) {

                var bg_color = "bg-danger";
                var nps = nps_score[index];
                let title = "";
                if(index == 0 )
                    title = "Inbound Analytics";
                else
                    title = "Outbound Analytics";

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
                nps_analytics += '<div class="small font-weight-bold" style="display: flex;justify-content:space-between;padding-top:1.33em"><span class="float-left">' + -100 + '</span><span class="float-center">' + title + '</span><span class="float-right">' + 100 + '</span></div>\
                                <div class="progress mb-4 progress-analytics" data-toggle="tooltip" title="' + nps + '" style="background-color:' + bg_color_light + '">\
                                    <div class="progress-bar" role="progressbar" style="width: ' + (nps+100)/2 + '%;background-color:' + bg_color + ';" aria-valuenow="' + nps + '" aria-valuemin="-100" aria-valuemax="100"></div>\
                                </div>';
            }
            document.getElementById("general-analytics-nps-body").innerHTML = nps_analytics;
			$('[data-toggle="tooltip"]').tooltip();
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

function get_visited_page_title_list() {
	request_params = {};
	json_params = JSON.stringify(request_params);
	encrypted_data = easyassist_custom_encrypt(json_params);
	encrypted_data = {
		"Request": encrypted_data
	};
	const params = JSON.stringify(encrypted_data);
	var xhttp = new XMLHttpRequest();
	xhttp.open("POST", "/easy-assist/agent/get-general-visited-page-title-list/", true);
	xhttp.setRequestHeader('Content-Type', 'application/json');
	xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			response = JSON.parse(this.responseText);
			response = easyassist_custom_decrypt(response.Response);
			response = JSON.parse(response);
			if(response.status==200){
				if(response.query_pages.length>0){
					let query_pages = response.query_pages;
					var select_html = '<option value="all">All visited pages</option>';
					for(var index=0;index < query_pages.length; index++){
						select_html += '<option value="'+query_pages[index]+'">'+query_pages[index]+'</option>';
					}
					document.getElementById("visited-title-select-option").innerHTML = select_html;

					show_general_analysis();
				}
			}else{
				console.error(response);
			}
		}
	}
	xhttp.send(params);
}

window.onload = function(e) {
	activate_analytics_sidebar();
	Chart.plugins.unregister(ChartDataLabels);
	get_visited_page_title_list();
}
