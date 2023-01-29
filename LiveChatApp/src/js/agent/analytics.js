import axios from "axios";

import {
    custom_decrypt,
    get_params,
    showToast,
    stripHTML,
    strip_unwanted_characters,
    EncryptVariable,
    encrypt_variable,
    getCsrfToken,
    change_date_format_original,
    is_valid_date,
} from "../utils";


export function submit_agent_analytics_filter() {

    let start_date = $("#livechat-analytics-start-date").val().trim();
    let end_date = $("#livechat-analytics-end-date").val().trim();
    let channel = $("#livechat-analytics-channel").val().trim();

    start_date = change_date_format_original(start_date);
    end_date = change_date_format_original(end_date);

    if (start_date == "" || end_date == "" || !is_valid_date(start_date) || !is_valid_date(end_date)) {
        showToast("Please enter valid dates", 4000);
        return;
    }

    if(!channel) {
        showToast("Please select channel", 4000);
        return;        
    }

    var start_datetime = new Date(start_date);
    var end_datetime = new Date(end_date);
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
    load_agent_analytics(start_date, end_date, channel);
    set_livechat_filter_in_local_storage(start_date, end_date, channel);

}

export function load_agent_analytics_by_filter() {
	let is_filter_applied = localStorage.getItem(`livechat_agent_analytics_filter`);

	if(is_filter_applied && is_filter_applied == 'true') {
	    let start_date = localStorage.getItem(`livechat_agent_analytics_start_date`);
	    let end_date = localStorage.getItem(`livechat_agent_analytics_end_date`);
	    let channel = localStorage.getItem(`livechat_agent_analytics_channel`);

	    if(start_date && end_date) {
	        let start_datetime = change_date_format_original(start_date);
	        let end_datetime = change_date_format_original(end_date);

	        setTimeout(() => {$('#livechat-analytics-start-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(start_datetime.trim());}, 200);
	        setTimeout(() => {$('#livechat-analytics-end-date').datepicker({ dateFormat: 'dd-mm-yy', prevText: "Previous" }).val(end_datetime.trim());}, 200);
	    }

	    if(channel) {
	    	document.getElementById("livechat-analytics-channel").value = channel;

	    	setTimeout(() => {$('#livechat-analytics-channel').selectpicker('refresh');}, 200);
	    }

	    load_agent_analytics(start_date, end_date, channel);
	}
}

function load_agent_analytics(start_date, end_date, channel) {

    let json_string = JSON.stringify({
    	start_date: start_date,
    	end_date: end_date,
        channel: channel,
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/get-agent-analytics/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);
            if(response.status == 200) {
              	
              	let is_filter_applied = localStorage.getItem(`livechat_agent_analytics_filter`);
	        	if(is_filter_applied && is_filter_applied == 'true'){

	            	update_widgets_data(response['total_closed_chats'], response['avg_interactions'], response['avg_handle_time'],
	            	response['avg_nps'], response['followup_leads'], response['total_tickets_raised'], response['avg_call_duration'],
	            	response['avg_video_call_duration'], response['avg_cobrowsing_duration'])
	            	hide_chat_reports_percentage_diff();
	         	}

            }
        })       
        .catch((err) => {
            console.log(err);
        });

}

function update_widgets_data(total_closed_chats, avg_interactions, avg_handle_time, avg_nps, followup_leads, total_tickets_raised, avg_call_duration, avg_video_call_duration, avg_cobrowsing_duration) {

	document.getElementById("total_closed_chats").innerHTML = total_closed_chats;
	document.getElementById("average_interactions").innerHTML = avg_interactions;
	document.getElementById("average_handle_time").innerHTML = avg_handle_time;
	document.getElementById("average_nps").innerHTML = avg_nps;

    if (document.getElementById('followup_leads')) {
        document.getElementById('followup_leads').innerHTML = followup_leads;
    }	

    if(document.getElementById("total_tickets_raised")) {
        document.getElementById("total_tickets_raised").innerHTML = total_tickets_raised;
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


}

function hide_chat_reports_percentage_diff(){
    try{
        $('.chat-report-card-data-rate').hide();
    }catch(err){}
}

function set_livechat_filter_in_local_storage(start_date, end_date, channel){
    localStorage.setItem(`livechat_agent_analytics_start_date`, start_date);
    localStorage.setItem(`livechat_agent_analytics_end_date`, end_date);
    localStorage.setItem(`livechat_agent_analytics_channel`, channel);
    localStorage.setItem(`livechat_agent_analytics_filter`, 'true');
}

export function unset_agent_analytics_filter_in_local_storage(){
    localStorage.removeItem(`livechat_agent_analytics_start_date`);
    localStorage.removeItem(`livechat_agent_analytics_end_date`);
    localStorage.removeItem(`livechat_agent_analytics_channel`);
    localStorage.removeItem(`livechat_agent_analytics_filter`);
} 