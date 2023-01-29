let update_meeting_data = null;

$(document).ready(function () {
    fetch_meeting_data();
    get_cogno_meet_meeting_view_data();
    create_or_update_cognomeet_agent();

});

function fetch_meeting_data() {
    update_meeting_data = setInterval(get_cogno_meet_meeting_view_data, 5000);
}

function create_or_update_cognomeet_agent() {

    let json_string = JSON.stringify({
        "cogno_meet_access_token": COGNOMEET_ACCESS_TOKEN,
        "agent_role": AGENT_ROLE
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


function get_cogno_meet_meeting_view_data() {
    let page_number = parseInt(window.localStorage.getItem("customer_meeting_current_page"));

    if (!page_number) {
        page_number = 1;
    }

    var json_string = JSON.stringify({
        "username": username,
        "agents_list": AGENTS_LIST,
        "agent_vs_supervisor_map": AGENT_VS_SUPERVISOR_MAP,
        "cogno_meet_access_token": COGNOMEET_ACCESS_TOKEN,
        "page_number": page_number
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/get-meeting-view-data/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200 && response.meeting_agent_data && response.meeting_agent_data.length != 0) {
                // update_meeting_pagination(response.pagination_data, response.start_point, response.end_point, response.totoal_requested_data);
                empty_meeting_table();
                update_meeting_table(response.meeting_agent_data);
                
            }
            else {
                empty_meeting_table();
            }
        }
    };
    xhttp.send(params);
}

function update_meeting_view_api(id, type = null) {
    clearInterval(update_meeting_data);

    if (type == 'assign_meeting') {
        id = '#assign_meeting-' + id;
    } else {
        id = '#edit_meeting-' + id;
    }

    $(id).on('hide.bs.modal', function () {
        fetch_meeting_data();
    });
}

function update_meeting_table(meeting_data) {

    let meeting_table_div = document.getElementById('meeting_data');
    let modal_table_div = document.getElementById('modal-table-div');
    if(meeting_table_div){
        meeting_table_div.innerHTML = '';
    }
    if(modal_table_div){
        modal_table_div.innerHTML = '';
    }

    let html = '';
    let modal_html = '';
    for (data of meeting_data) {
        html += [` <tr>
        <td>
            ${data.customer_name == '' ? '-' : data.customer_name}
            <div class="tooltip-textarea" style="display: inline-flex;">
                                        
                <a data-toggle="modal" data-target="#assign_meeting-${data.cogno_meet_pk}" style="margin-right: 1rem;cursor: pointer;" onclick="update_meeting_view_api('${data.cogno_meet_pk}','assign_meeting')">
                    <svg class="svg-hide-on-desktop" width="18" height="17" viewBox="0 0 18 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4.8126 6.4684H4.2573C3.49951 6.44102 2.74418 6.56966 2.03818 6.84635C1.33218 7.12304 0.690574 7.54187 0.153186 8.07686L0 8.25558V13.5405H2.60416V10.5406L2.95522 10.1449L3.11478 9.95977C3.94577 9.10608 4.98032 8.47788 6.12106 8.1343C5.54993 7.69972 5.09949 7.12624 4.8126 6.4684Z" fill="#757575"></path>
                        <path d="M17.1569 8.05773C16.6196 7.52275 15.978 7.10391 15.272 6.82722C14.566 6.55053 13.8106 6.42189 13.0528 6.44928C12.8204 6.44994 12.5882 6.46272 12.3571 6.48757C12.0648 7.10473 11.6267 7.64144 11.0806 8.05135C12.2984 8.38826 13.4016 9.05018 14.2719 9.96618L14.4315 10.1449L14.7762 10.5406V13.5469H17.291V8.23645L17.1569 8.05773Z" fill="#757575"></path>
                        <path d="M4.23808 5.22378H4.43595C4.34401 4.43439 4.48252 3.63526 4.83476 2.92286C5.187 2.21045 5.73791 1.61523 6.42099 1.20903C6.17338 0.830755 5.83177 0.52327 5.42962 0.316686C5.02747 0.110101 4.57856 0.0114991 4.12685 0.0305345C3.67515 0.04957 3.23613 0.18559 2.85278 0.425276C2.46944 0.664962 2.15491 1.0001 1.94001 1.39786C1.7251 1.79563 1.61718 2.24239 1.62681 2.69439C1.63645 3.1464 1.7633 3.58815 1.99496 3.9764C2.22662 4.36465 2.55514 4.68608 2.94835 4.90921C3.34156 5.13235 3.78597 5.24954 4.23808 5.24931V5.22378Z" fill="#757575"></path>
                        <path d="M12.7465 4.74507C12.7542 4.89177 12.7542 5.03878 12.7465 5.18548C12.869 5.20489 12.9927 5.21556 13.1167 5.21739H13.2379C13.6881 5.19339 14.1243 5.05325 14.5042 4.8106C14.8841 4.56796 15.1946 4.23109 15.4057 3.83279C15.6167 3.43449 15.721 2.98832 15.7085 2.53774C15.6959 2.08715 15.5669 1.6475 15.334 1.26159C15.101 0.87567 14.7721 0.55664 14.3793 0.335558C13.9865 0.114476 13.5431 -0.00112567 13.0924 8.26235e-06C12.6416 0.0011422 12.1988 0.118973 11.8071 0.342029C11.4154 0.565085 11.0882 0.885765 10.8572 1.27285C11.4349 1.65003 11.9099 2.16471 12.2396 2.77073C12.5694 3.37675 12.7435 4.05515 12.7465 4.74507Z" fill="#757575"></path>
                        <path d="M8.55939 7.60452C10.1351 7.60452 11.4125 6.32715 11.4125 4.75143C11.4125 3.17571 10.1351 1.89834 8.55939 1.89834C6.98367 1.89834 5.7063 3.17571 5.7063 4.75143C5.7063 6.32715 6.98367 7.60452 8.55939 7.60452Z" fill="#757575"></path>
                        <path d="M8.7126 9.12363C7.87904 9.08997 7.04729 9.2253 6.26739 9.52147C5.48749 9.81763 4.77557 10.2685 4.17446 10.847L4.01489 11.0257V15.066C4.01738 15.1976 4.04578 15.3274 4.09845 15.448C4.15113 15.5687 4.22705 15.6777 4.32189 15.769C4.41672 15.8603 4.52861 15.932 4.65116 15.98C4.77372 16.028 4.90453 16.0515 5.03613 16.0489H12.3699C12.5015 16.0515 12.6323 16.028 12.7549 15.98C12.8774 15.932 12.9893 15.8603 13.0842 15.769C13.179 15.6777 13.2549 15.5687 13.3076 15.448C13.3603 15.3274 13.3887 15.1976 13.3912 15.066V11.0385L13.238 10.847C12.6408 10.2667 11.9313 9.81458 11.1532 9.51824C10.375 9.2219 9.5445 9.08762 8.7126 9.12363Z" fill="#757575"></path>
                    </svg>
                </a>
                
                <a data-toggle="modal" data-target="#edit_meeting-${data.cogno_meet_pk}" style="cursor: pointer;margin-right: 1rem;" onclick="update_meeting_view_api('${data.cogno_meet_pk}')">
                    <svg class="svg-hide-on-desktop" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15.36 14.48H0.64C0.286 14.48 0 14.766 0 15.12V15.84C0 15.928 0.072 16 0.16 16H15.84C15.928 16 16 15.928 16 15.84V15.12C16 14.766 15.714 14.48 15.36 14.48ZM2.914 12.8C2.954 12.8 2.994 12.796 3.034 12.79L6.398 12.2C6.438 12.192 6.476 12.174 6.504 12.144L14.982 3.666C15.0005 3.6475 15.0153 3.62552 15.0253 3.60133C15.0353 3.57713 15.0405 3.55119 15.0405 3.525C15.0405 3.49881 15.0353 3.47287 15.0253 3.44867C15.0153 3.42448 15.0005 3.4025 14.982 3.384L11.658 0.058C11.62 0.02 11.57 0 11.516 0C11.462 0 11.412 0.02 11.374 0.058L2.896 8.536C2.866 8.566 2.848 8.602 2.84 8.642L2.25 12.006C2.23054 12.1131 2.2375 12.2234 2.27025 12.3273C2.30301 12.4311 2.36059 12.5254 2.438 12.602C2.57 12.73 2.736 12.8 2.914 12.8Z" fill="#757575"></path>
                    </svg>
                </a>
                
                <a href="/cogno-meet/meeting/${data.cogno_meet_pk}" target="_blank">
                    <svg class="svg-hide-on-desktop" width="17" height="16" viewBox="0 0 17 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M0.229248 14C0.229248 14.5304 0.439962 15.0391 0.815034 15.4142C1.19011 15.7893 1.69882 16 2.22925 16L14.2292 16C14.7597 16 15.2684 15.7893 15.6435 15.4142C16.0185 15.0391 16.2292 14.5304 16.2292 14L16.2292 2C16.2292 1.46957 16.0185 0.96086 15.6435 0.585787C15.2684 0.210715 14.7597 3.18529e-07 14.2292 3.41715e-07L2.22925 8.66252e-07C1.69881 8.89437e-07 1.19011 0.210715 0.815034 0.585788C0.439961 0.96086 0.229247 1.46957 0.229247 2L0.229248 14ZM11.2292 9.5L11.2292 5.5C11.2292 5.36739 11.1766 5.24021 11.0828 5.14645C10.989 5.05268 10.8619 5 10.7292 5L6.72925 5C6.59664 5 6.46946 5.05268 6.37569 5.14645C6.28193 5.24022 6.22925 5.36739 6.22925 5.5C6.22925 5.63261 6.28193 5.75979 6.37569 5.85355C6.46946 5.94732 6.59664 6 6.72925 6L9.52225 6L5.37525 10.146C5.28136 10.2399 5.22862 10.3672 5.22862 10.5C5.22862 10.6328 5.28136 10.7601 5.37525 10.854C5.46913 10.9479 5.59647 11.0006 5.72925 11.0006C5.86202 11.0006 5.98936 10.9479 6.08325 10.854L10.2292 6.707L10.2292 9.5C10.2292 9.63261 10.2819 9.75979 10.3757 9.85355C10.4695 9.94732 10.5966 10 10.7292 10C10.8619 10 10.989 9.94732 11.0828 9.85355C11.1766 9.75979 11.2292 9.63261 11.2292 9.5Z" fill="#757575"></path>
                    </svg>
                </a>
            </div>
        </td>
        
       
        <td>${data.mobile_number == '' ? '-' : data.mobile_number}</td>        
        <td>${data.customer_email == '' ? '-' : data.customer_email}</td>        
        <td>${data.meeting_title}</td>
        <td>${data.meeting_start_date}</td>
        <td>${data.meeting_start_time}</td>
        <td>${data.meeting_end_time}</td>                
        <td class="td-hide-on-small-device">${data.meeting_password == '' ? '-' : data.meeting_password}</td>`].join('');
        
        // agent name
        if(AGENT_ROLE == 'supervisor' && username == data.agent){
            html += [`<td>Self</td>`].join('');
        }
        else if((AGENT_ROLE == 'admin' || AGENT_ROLE == 'admin_ally')&& SUPERVISOR_LIST.includes(data.agent)){
            html += [`<td>-</td>`].join('');
        }
        else if(AGENT_ROLE != 'agent'){
            html += [`<td>${data.agent}</td>`].join('');
        }
        
        // Supervisor's name
        if((AGENT_ROLE == 'admin' || AGENT_ROLE == 'admin_ally')&& SUPERVISOR_LIST.includes(data.agent)){
            html += [`<td>${data.agent}</td>`].join('');
        }
        else if(AGENT_ROLE != 'supervisor' && AGENT_ROLE != 'agent'){
            html +=[`<td>${get_supervisor_for_agent(data.agent)}</td>`].join('');                     
        }
        
        if(AGENT_ROLE == 'supervisor'){
        html += [`
        <td class="td-hide-on-small-device">
                <a data-toggle="modal" data-target="#assign_meeting-${data.cogno_meet_pk}" style="cursor: pointer;" onclick="update_meeting_view_api('${data.cogno_meet_pk}','assign_meeting'); get_agent_under_supervisor('${data.cogno_meet_pk}');">
                    <i class="fas fa-fw fa-users"></i>
                </a>            
        </td>`].join('')
        }
        
        // edit meeting 
        if(AGENT_ROLE == 'agent'){
        html+=[`<td class="td-hide-on-small-device">            
                <a data-toggle="modal" data-target="#edit_meeting-${data.cogno_meet_pk}" style="cursor: pointer;" onclick="update_meeting_view_api('${data.cogno_meet_pk}')"><i class="fas fa-fw fa-edit"></i></a>            
        </td>`].join('');
        }

        // Join meet
        if((AGENT_ROLE == 'supervisor' && data.agent == username) || AGENT_ROLE == 'agent'){
            html +=[`
            <td class="td-hide-on-small-device">           
            <a class="btn" href="/cogno-meet/meeting/${data.cogno_meet_pk}" target="_blank"><i class="fas fa-fw fa-external-link-square-alt"></i></a>            
            </td>
            `].join('');
        }
        else if(AGENT_ROLE == 'supervisor'){
            html +=[`
            <td class="td-hide-on-small-device">           
            -
            </td>
            `].join('');
        }           
        html +=[`</tr>`].join('');

        


        modal_html += [`
    <div class="modal fade" id="edit_meeting-${data.cogno_meet_pk}" tabindex="-1" role="dialog" aria-labelledby="edit_meeting_label" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="edit_meeting_label">Edit Meeting Details</h5>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Customer Full Name</span>
                            </div>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" id="client-full-name-${data.cogno_meet_pk}" value="${data.customer_name}">
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Customer Mobile Number</span>
                            </div>
                            <input type="number" class="form-control positive_numeric mobile_number" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" id="client-modile-number-${data.cogno_meet_pk}" value="${data.mobile_number}">
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Customer Email</span>
                            </div>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" id="client-email-id-${data.cogno_meet_pk}" value="${data.customer_email}">
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Meeting Description</span>
                            </div>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" id="client-meeting-description-${data.cogno_meet_pk}" value="${data.meeting_title}">
                        </div>
                    </div>
                    <div class="col-md-6 col-sm-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Meeting Date</span>
                            </div>
                            <input class="form-control datepicker" aria-label="Sizing example input" autocomplete="off"  aria-describedby="inputGroup-sizing-sm" id="client-meeting-start-date-${data.cogno_meet_pk}" data-date-format="dd-mm-yyyy" value="${data.meeting_start_date_unformatted}">
                        </div>
                    </div>
                    <div class="col-md-6 col-sm-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Meeting Password</span>
                            </div>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" autocomplete="off" id="client-meeting-password-${data.cogno_meet_pk}" value="${data.meeting_password}">
                        </div>
                    </div>
                    <div class="col-md-6 col-sm-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Meeting Start Time</span>
                            </div>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" id="client-meeting-start-time-${data.cogno_meet_pk}" value="${data.meeting_start_time}" onkeypress="return meeting_time_input_validate(event)">
                        </div>
                    </div>
                    <div class="col-md-6 col-sm-12">
                        <div class="input-group input-group-sm mb-3">
                            <div class="input-group-prepend">
                                <span class="input-group-text" id="inputGroup-sizing-sm">Meeting End Time</span>
                            </div>
                            <input type="text" class="form-control" aria-label="Sizing example input" aria-describedby="inputGroup-sizing-sm" id="client-meeting-end-time-${data.cogno_meet_pk}" value="${data.meeting_end_time}" onkeypress="return meeting_time_input_validate(event)">
                        </div>
                    </div>`].join('');
        modal_html+=[`<div class="col-12">
                        <div style="margin-top: 1em;">
                            <div class="tab-content">
                                <div class="tab-pane fade show active" role="tabpanel" aria-labelledby="pills-video-conferencing-tab" style="padding:1em 1em 0em 1em;">
                                    <div class="">
                                        <div class="input-group input-group-sm mb-3">
                                            <input type="text" class="form-control" value="https://${META_HTTP}/cogno-meet/meeting/${data.cogno_meet_pk}" readonly>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <p style="color:green;" id="generate-link-details-error-${data.cogno_meet_pk}"></p>
                    </div>`].join('');

        modal_html+=[`
            </div>

            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancel</button>
                <button class="btn btn-success" onclick="save_meeting_link_for_dyte(this, '${data.cogno_meet_pk}')"><i class="fas fa-fw fa-check"></i>Save</button>
            </div>
        </div>
    </div>
</div>
<div class="modal fade" id="assign_meeting-${data.cogno_meet_pk}" tabindex="-1" role="dialog" aria-labelledby="assign_meeting_label" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="assign_meeting_label">Transfer Meeting To Another Agent</h5>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-12">
                        <select id="select-assign-agent-${data.cogno_meet_pk}" class="form-control" style="width:50%;">
                          <option value="">Select Agent</option> 
                            
                            <option value="${data.cogno_meet_pk}">${data.agent}</option>
                            
                        </select>
                        <div id="assign-meeting-session-error-${data.cogno_meet_pk}" style="color: red;" class="mt-4"></div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancel</button>
                <button class="btn btn-primary" id="assign-meeting-btn-${data.cogno_meet_pk}" onclick="assign_meeting_to_another_cogno_meet_agent(this, '${data.cogno_meet_pk}')">Transfer</button>
            </div>
        </div>
    </div>
</div>
<script type="text/javascript">
    $('#client-meeting-start-time-${data.cogno_meet_pk}').timepicker({ 
        'step': {{ meeting_end_time }},
        'scrollDefault': 'now',
        "timeFormat": 'h:iA'
    });
    $('#client-meeting-end-time-${data.cogno_meet_pk}').timepicker({ 
        'step': {{ meeting_end_time }},
        'scrollDefault': 'now',
        "timeFormat": 'h:iA'
    });
</script>`].join('')

    }
    
    if (meeting_table_div) {
        meeting_table_div.innerHTML = html;
    }
    if (modal_table_div) {
        modal_table_div.innerHTML = modal_html;
    }

}

function empty_meeting_table() {
    let meeting_table_div = document.getElementById('meeting_data');
    if (meeting_table_div) {
        meeting_table_div.innerHTML = '<tr class="odd"><td colspan="11" class="dataTables_empty" valign="top">No data available in table</td></tr>';
    }
}

function get_supervisor_for_agent(agent) {
    if (AGENT_VS_SUPERVISOR_MAP[agent] != undefined && AGENT_VS_SUPERVISOR_MAP[agent] != null) {
        return AGENT_VS_SUPERVISOR_MAP[agent];
    }
    else {
        return '-';
    }
}

function get_scheduled_meeting_list_for_dyte() {
    var json_string = JSON.stringify({
        "username": username,
        "agents_list": AGENTS_LIST,
        "agent_vs_supervisor_map": AGENT_VS_SUPERVISOR_MAP,
        "cogno_meet_access_token": COGNOMEET_ACCESS_TOKEN,
        "today_data": true
        // "page_number": page_number
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/get-meeting-view-data/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let html = '';
                let is_data_available = true;
                let meeting_list = response.meeting_list;
                if (meeting_list.length == 0) {
                    is_data_available = false;
                    html += "<div class=\"text-center\">";
                    html += "No Scheduled Meeting";
                    html += "</div>";
                    $('#todays_meeting_modal #todays_meeting_modal_body').html(html);
                } else {
                    html+=[`<div class="modal-dialog modal-lg" role="document">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="generate_link_modal_label">Scheduled Meetings</h5>
                                </div>
                                <div class="modal-body">
                                    <div class="table-responsive">
                                        <table class="table table-bordered" id="dataTable" width="100%" cellspacing="0">
                                            <thead>
                                                <tr>
                                                    <th>Meeting</th>
                                                    <th>Meeting Date</th>
                                                    <th> Start Time</th>
                                                    <th>End Time</th>`].join('');
                                                    if(AGENT_ROLE == 'admin_ally' || AGENT_ROLE=='admin'){
                                                    html+=[`<th>Agent</th>
                                                        <th>Supervisor</th>`].join('');
                                                    }else if(AGENT_ROLE == 'supervisor'){
                                                        html+=[`<th>Agent</th>`].join('');
                                                    }
                                                    if(AGENT_ROLE=='agent' || AGENT_ROLE=='supervisor'){
                                                        html+=[`
                                                        <th><span class="ml-3">Status</span></th>`].join('');
                                                    }


                                                html+=[`</tr>
                                            </thead>
                                            <tbody>`].join('');

                    for (let meeting_obj of meeting_list){                        
                        html+=[`
                                <tr>
                                    <td data-content="Meeting">${meeting_obj.description}</td>
                                    <td data-content="Meeting Date">${meeting_obj.start_date}</td>
                                    <td data-content=" Start Time">${meeting_obj.start_time}</td>
                                    <td data-content="End Time">${meeting_obj.end_time}</td>`].join('');

                            // agent name 
                            if(AGENT_ROLE == 'admin' || AGENT_ROLE=='admin_ally'){
                                if(SUPERVISOR_LIST.includes(meeting_obj.agent)){
                                    html+=[`<td data-content="Agent">-</td>
                                    <td data-content="Supervisor">${meeting_obj.agent}</td>`].join('');
                                }else{
                                    html+=[`<td data-content="Agent">${meeting_obj.agent}</td>
                                    <td data-content="Supervisor">${get_supervisor_for_agent(meeting_obj.agent)}</td>`].join('');
                                }

                            }else if(AGENT_ROLE=='supervisor'){
                                if(meeting_obj.agent != username){
                                    html+=[`<td data-content="Agent">${meeting_obj.agent}</td>`].join('');
                                }else{
                                    html+=[`<td data-content="Agent">Self</td>`].join('');
                                }
                                
                            }


                            if(AGENT_ROLE=='agent' || (AGENT_ROLE=='supervisor' && meeting_obj.agent == username)){
                                html+=[`
                                <td data-content="Status"><a class="btn btn-info ml-3"
                                    href="/cogno-meet/meeting/${meeting_obj.id}"
                                    target="_blank"
                                    style="color:#fff!important;cursor:pointer;">Join</a>
                                </td>`].join('');
                            }
                            else if(AGENT_ROLE=='supervisor'){
                                html+=[`
                                <td data-content="Status" style="text-align:center;">-</td>`].join('');
                            }

                            html+=[`</tr>`].join('');
                                        
                    }
                    html+=[`</tbody>
                                        </table>
                                    </div>
                                    
                                </div>
                            </div>
                        </div>`].join('');
                }
                if(is_data_available){
                    document.getElementById('todays_meeting_modal').innerHTML = html;
                }
                $('#todays_meeting_modal').modal('show');
            }
            else {
                empty_meeting_table();
            }
        }
    };
    xhttp.send(params);
}

function save_meeting_link_for_dyte(element, meeting_id) {

    let error_message_element = document.getElementById("generate-link-details-error-" + meeting_id);
    error_message_element.innerHTML = "";

    let full_name = document.getElementById("client-full-name-" + meeting_id).value;
    let mobile_number = document.getElementById("client-modile-number-" + meeting_id).value;
    let email = document.getElementById("client-email-id-" + meeting_id).value;

    const regName = /^[a-zA-Z ]+$/;
    const regMob = /^[6-9]{1}\d{9}$/;
    if (email != "") {
        if (!regEmail.test(email)) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Please enter valid Email id.";
            return;
        }

        if (email.length > 50) {
            error_message_element.style.color = "red";
            error_message_element.innerHTML = "Email ID should not be more than 50 characters.";
            return;
        }
    }

    if (!regName.test(full_name)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter full name";
        return;
    }

    if (!regMob.test(mobile_number)) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter valid 10-digit mobile number";
        return;
    }

    let meeting_description = document.getElementById("client-meeting-description-" + meeting_id).value;
    meeting_description = stripHTML(meeting_description);
    meeting_description = remove_special_characters_from_str(meeting_description);
    if (meeting_description == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting description.";
        return;
    }

    let meeting_start_date = document.getElementById("client-meeting-start-date-" + meeting_id).value;
    if (meeting_start_date == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the meeting date.";
        return;
    }

    meeting_start_date = get_iso_formatted_date(meeting_start_date);
    let meet_date_year = meeting_start_date.split("-")[0]
    let meet_date_month = meeting_start_date.split("-")[1]
    let meet_date_date = meeting_start_date.split("-")[2]

    if (meet_date_year < new Date().getFullYear()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month < (new Date().getMonth() + 1)) {
        error_message_element.innerHTML = "Please enter a valid meeting date.";
        error_message_element.style.color = "red";
        return;
    } else if (meet_date_year == new Date().getFullYear() && meet_date_month == (new Date().getMonth() + 1) && meet_date_date < new Date().getDate()) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter a valid meeting date."
        return;
    }

    var current_time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });

    let meeting_start_time = document.getElementById("client-meeting-start-time-" + meeting_id).value;
    if (meeting_start_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the start time.";
        return;
    }

    meeting_start_time = convertTime12to24(meeting_start_time)

    if (meeting_start_time == null) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter start time in valid format.";
        return;
    }

    if (meeting_start_time < current_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid start time.";
        return;
    }

    let meeting_end_time = document.getElementById("client-meeting-end-time-" + meeting_id).value;
    if (meeting_end_time == "") {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter the end time.";
        return;
    }
    meeting_end_time = convertTime12to24(meeting_end_time)

    if (meeting_end_time == null) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Please enter end time in valid format.";
        return;
    }

    if (meeting_end_time < current_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "You have entered a time in the past. Please enter a valid end time.";
        return;
    }

    if (meeting_start_time >= meeting_end_time) {
        error_message_element.style.color = "red";
        error_message_element.innerHTML = "Start time should be less than end time.";
        return;

    }
    let meeting_password = document.getElementById("client-meeting-password-" + meeting_id).value;
    let request_params = {
        "meeting_id": meeting_id,
        "full_name": full_name,
        "mobile_number": mobile_number,
        "meeting_description": meeting_description,
        "meeting_start_date": meeting_start_date.split("/").reverse().join("/"),
        "meeting_end_time": meeting_end_time,
        "meeting_start_time": meeting_start_time,
        "meeting_password": meeting_password,
        "email": email
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Saving...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/update-cogno-meet/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                window.location = window.location.href;
            } else {
                error_message_element.style.color = "red";
                error_message_element.innerHTML = "Unable to save video meeting";
            }
            element.innerHTML = "Save";
        }
    }
    xhttp.send(params);
}

function convertTime12to24(time12h) {
    const [time, modifier] = time12h.split(' ');

    let [hours, minutes] = time.split(':');

    if (hours === '12') {
        hours = '00';
    }

    if (modifier === 'PM') {
        hours = parseInt(hours, 10) + 12;
    }

    return `${hours}:${minutes}`;
}

// function get_active_meeting_agent(){

// }

function get_agent_under_supervisor(meeting_id) {

    var assign_agent_error = document.getElementById('assign-meeting-session-error-' + meeting_id);
    assign_agent_error.style.display = 'none';
    let json_string = JSON.stringify({});

    let encrypted_data = easyassist_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/easy-assist/agent-under-supervisor/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                var select_agent_inner_html = '<option value="">Select Agent</option>';
                let support_agents = response.support_agents;
                if (support_agents.length > 0) {
                    for (const agent of support_agents) {
                        select_agent_inner_html += '<option value="' + agent + '"> ' + agent + '</option>';
                    }
                    document.getElementById('assign-meeting-btn-' + meeting_id).removeAttribute('disabled');
                } else {
                    assign_agent_error.innerHTML = 'Currently agents are not available. Please try again after sometime.';
                    assign_agent_error.style.display = 'block';
                    document.getElementById('assign-meeting-btn-' + meeting_id).setAttribute('disabled', 'disabled');
                }
                document.getElementById('select-assign-agent-' + meeting_id).innerHTML = select_agent_inner_html;
            }
        }
    }
    xhttp.send(params);
}

function assign_meeting_to_another_cogno_meet_agent(element,meeting_id){
    let assign_agent_element = document.getElementById("select-assign-agent-" + meeting_id);
    let agent_name = assign_agent_element.value;
    
    let request_params = {
        "meeting_id": meeting_id,
        "agent_name": agent_name,
        "access_token":COGNOMEET_ACCESS_TOKEN
    };

    let json_params = JSON.stringify(request_params);

    let encrypted_data = easyassist_custom_encrypt(json_params);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);
    element.innerHTML = "Assigning...";
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/assign-cogno-meet-agent/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            
            if (response["status"] == 200) {
                // agent_email = assign_agent_element.options[assign_agent_element.selectedIndex].text;
                var notification_obj = {
                    "notification_message": 'A meeting has been assigned to ' + agent_name + ".",
                    "product_name": response.product_name
                }
                send_notification(notification_obj);
                play_notification_sound();
                setTimeout('', 1000);
            }
            element.innerHTML = "Assigned";
            window.location.reload()
        }
    }
    xhttp.send(params);
}


// function update_meeting_pagination(pagination, start, end, total_objs) {
//     let html = `<div class="row mt-3">`

//     if (pagination.has_other_pages) {
//         html += `<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text="Showing 1 to 20 of 22 entries" start_point="1" end_point="20">
//                 Showing ${start} to ${end} entries out of ${total_objs}
//                 </div>
//                 <div class="col-md-6 col-sm-12">
//                 <div class="d-flex justify-content-end">
//                 <nav aria-label="Page navigation example">
//                     <ul class="pagination">
//                     <li id="previous-button" class="disabled page-item">
//                         <span>
//                             <a class="previous-button page-link" href="javascript:void(0)" aria-label="Previous">
//                                 <span aria-hidden="true">Previous</span>
//                                 <span class="sr-only">Previous</span>
//                             </a>
//                         </span>
//                     </li>`;

//         for (let page = 1; page < pagination.page_range; ++page) {
//             if (pagination.number == page) {
//                 if (page == 1) {
//                     html += `<li class="purple darken-3 active page-item" id="page-${page}" ><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
//                 } else if (pagination.num_pages == page) {
//                     html += `<li class="purple darken-3 page-item active" id="page-${page}" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
//                 } else {
//                     html += `<li class="active purple darken-3 page-item" style="border-radius: 0px;" id="page-${page}"><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
//                 }
//             } else if (page > pagination.number - 5 && page < pagination.number + 5) {
//                 html += `<li class="purple darken-3 page-item" id="page-${page}"><a class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
//             }
//         }
//         html += `<li id="next-button" class="page-item">
//                     <a class="next-button page-link" href="javascript:void(0)" aria-label="Next">
//                         <span aria-hidden="true">Next</span>
//                         <span class="sr-only">Next</span>
//                     </a>
//                 </li>
//                 </ul>
//                 </nav>
//                 </div>
//                 </div>`;
//     } else {
//         html += `</div>`
//     }

//     document.getElementById("pagination-div").innerHTML = html;
//     events_for_pagination(pagination.page_range);

//     // add_pagination_events();
    
// }
