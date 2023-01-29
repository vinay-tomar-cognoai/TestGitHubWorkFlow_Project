window.onload = get_cogno_meet_audit_trail_data;

$(document).ready(function () {
    create_or_update_cognomeet_agent();
});

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

function get_client_agent_chats_dyte(session_id) {

    var json_string = JSON.stringify({
        "session_id": session_id
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/get-chat-for-session/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let message_history = response["message_history"]
                var chat_html = '<div class="chat-area"><div class="chat-message-wrapper">';

                for (const element of message_history) {
                    let sender = element["sender"];
                    let message = element["message"]
                    let datetime = element["time"]
                    let type = element["attachment_file_name"] == null ? "chat" : "attachment";
                    let attachment_link = element["attachment_file_path"];
                    let sender_name = element["sender_name"];
                    
                    if(sender == "system"){
                        chat_html += `<p class="easyassist-chat-bubble"> ${message} </p>`;
                    } else if (sender == "client") {
                        if (type == "attachment") {
                            chat_html += ['<div class="chat-client-message-wrapper">',
                                '<div class="chat-client-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-client-message-bubble">',
                                '<div class="client-name-div">' + sender_name + '</div>',
                                '<div class="file-upload-img-div-client">',
                                '<svg width="19" height="26" viewBox="0 0 19 26" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M11.0832 0V6.73434C11.0832 7.38877 11.6109 7.91654 12.2654 7.91654H18.9997V24.1507C18.9997 24.8052 18.4719 25.3329 17.8175 25.3329H1.1822C0.527768 25.3329 0 24.8052 0 24.1507V1.1822C0 0.527769 0.527768 0 1.1822 0H11.0832ZM13.8067 0.337772L18.6411 5.19325C18.8733 5.42547 19 5.72102 19 6.03768V6.33323H12.6668V0H12.9623C13.279 0 13.5745 0.126665 13.8067 0.337772Z" fill="url(#paint0_linear)"/>',
                                '<defs>',
                                '<linearGradient id="paint0_linear" x1="1.89293" y1="2.37496" x2="18.5174" y2="25.3331" gradientUnits="userSpaceOnUse">',
                                '<stop stop-color="#0254D7"/>',
                                '<stop offset="1" stop-color="#4A8DF8"/>',
                                '</linearGradient>',
                                '</defs>',
                                '</svg>',
                                // '<div class="file-name-div-client">',
                                //     attachment_file_name,
                                // '</div>',
                                `<a href="${attachment_link}" download>File Attachment</a>`,
                                '</div>',
                                '</div>',
                                '<div class="chat-client-message-time">' + datetime + '</div>',
                                '</div>'
                            ].join('');
                        } else {
                            chat_html += ['<div class="chat-client-message-wrapper">',
                                '<div class="chat-client-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-client-message-bubble">',
                                '<div class="client-name-div">' + sender_name + '</div>',
                                message,
                                '</div>',
                                '<div class="chat-client-message-time">' + datetime + '</div>',
                                '</div>'
                            ].join('');
                        }
                    } else {
                        if (type == "attachment") {
                            chat_html += ['<div class="chat-agent-message-wrapper">',
                                '<div class="chat-agent-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-agent-message-bubble">',
                                '<div class="agent-name-div">' + sender_name + '</div>',
                                '<div class="file-upload-img-div-agent">',
                                '<svg width="19" height="26" viewBox="0 0 19 26" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path fill-rule="evenodd" clip-rule="evenodd" d="M11.0832 0V6.73434C11.0832 7.38877 11.6109 7.91654 12.2654 7.91654H18.9997V24.1507C18.9997 24.8052 18.4719 25.3329 17.8175 25.3329H1.1822C0.527768 25.3329 0 24.8052 0 24.1507V1.1822C0 0.527769 0.527768 0 1.1822 0H11.0832ZM13.8067 0.337772L18.6411 5.19325C18.8733 5.42547 19 5.72102 19 6.03768V6.33323H12.6668V0H12.9623C13.279 0 13.5745 0.126665 13.8067 0.337772Z" fill="white"/>',
                                '<defs>',
                                '<linearGradient id="paint0_linear" x1="1.89293" y1="2.37496" x2="18.5174" y2="25.3331" gradientUnits="userSpaceOnUse">',
                                '<stop stop-color="#0254D7"/>',
                                '<stop offset="1" stop-color="#4A8DF8"/>',
                                '</linearGradient>',
                                '</defs>',
                                '</svg>',
                                // '<div class="file-name-div-agent">',
                                //     attachment_file_name,
                                // '</div>',
                                `<a href="${attachment_link}" download>File Attachment</a>`,
                                '</div>',
                                '</div>',
                                '<div class="chat-agent-message-time">',
                                datetime,
                                '</div>',
                                '</div>'
                            ].join('');

                        } else {
                            chat_html += ['<div class="chat-agent-message-wrapper">',
                                '<div class="chat-agent-image"><svg width="9" height="12" viewBox="0 0 9 12" fill="none" xmlns="http://www.w3.org/2000/svg">',
                                '<path d="M4.50001 0.571426C3.17682 0.571426 2.10417 1.79731 2.10417 3.30952C2.10417 4.82173 3.17682 6.04762 4.50001 6.04762C5.82319 6.04762 6.89584 4.82173 6.89584 3.30952C6.89584 1.79731 5.82319 0.571426 4.50001 0.571426Z" fill="white"/>',
                                '<path d="M1.68487 7.14285C1.12266 7.14285 0.666677 7.66344 0.666672 8.30624L0.666672 8.5119C0.666672 9.54021 1.13186 10.31 1.84546 10.8065C2.54718 11.2947 3.49042 11.5238 4.50001 11.5238C5.50959 11.5238 6.45283 11.2947 7.15455 10.8065C7.86815 10.31 8.33334 9.54021 8.33334 8.5119L8.33334 8.3062C8.33333 7.66341 7.87735 7.14285 7.31516 7.14285H1.68487Z" fill="white"/>',
                                '</svg>',
                                '</div>',
                                '<div class="chat-agent-message-bubble">',
                                '<div class="agent-name-div">' + sender_name + '</div>',
                                message,
                                '</div>',
                                '<div class="chat-agent-message-time">',
                                datetime,
                                '</div>',
                                '</div>'
                            ].join('');
                        }
                    }

                }
                chat_html += "</div></div>"
                document.getElementById("client-agent-chat-history").innerHTML = chat_html
            } else if (response["status"] == 301) {
                show_easyassist_toast("No Chat Record Found.")
            } else {
                show_easyassist_toast("Something went wrong!!");
            }
        }
    }
    xhttp.send(params);
}

function show_captured_screenshots_dyte(element_id) {

    hide_all_active_modal();
    let screenshots = $('#meeting-screencapture-' + element_id).val();
    let screen_shot = document.getElementById(`meeting-screencapture-${element_id}`).value;
    screenshots = JSON.parse(screen_shot)["items"];

    if (screenshots.length == 0) {
        var html = [
            '<td colspan="2" class="text-center">',
            'No captured screenshot',
            '</td>'
        ].join('');
        document.getElementById("tbody-captured-screenshot-details").innerHTML = html;
        update_table_attribute();
        $('#meeting-screencapture-details').modal('show');
        return;
    }

    var tbody_html = "";
    for (var index = 0; index < screenshots.length; index++) {
        tbody_html += [
            '<tr>',
            '<td><span>Screenshot</span></td>',
            '<td><a href="/cogno-meet/download-file/' + screenshots[index]['screenshot'] + '" download><i class="fas fa-fw fa-file-download"></i></a></td>',
            '</tr>'
        ].join('');
    }
    document.getElementById("tbody-captured-screenshot-details").innerHTML = tbody_html;
    update_table_attribute();
    $('#meeting-screencapture-details').modal('show');
}


function get_cogno_meet_audit_trail_data() {
    let page_number = parseInt(window.localStorage.getItem("meeting_support_history_current_page"));

    if (!page_number) {
        page_number = 1;
    }

    var json_string = JSON.stringify({
        "username": username,
        "agents_list": agents_list,
        "support_history_filters": support_history_filters,
        "page_number": page_number,
        "cogno_meet_access_token":window.COGNOMEET_ACCESS_TOKEN
    });

    var encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/get-audit-trail-data/", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.setRequestHeader("X-CSRFToken", get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response["status"] == 200 && response.meeting_history && response.meeting_history.length != 0) {
                let export_and_filter_div = document.getElementById('export-filter-div');
                if(export_and_filter_div){
                    export_and_filter_div.style.display='block';
                }

                update_pagination(response.pagination_data, response.start_point, response.end_point, response.totoal_requested_data);
                update_support_history_table(response.meeting_history);
            }
        }
    };
    xhttp.send(params);
}

function update_pagination(pagination, start, end, total_objs) {
    let html = `<div class="row mt-3">`

    if (pagination.number) {
        html += `<div class="col-md-6 col-sm-12 show-pagination-entry-container" filter_default_text="Showing 1 to 20 of 22 entries" start_point="1" end_point="20">
                Showing ${start} to ${end} entries out of ${total_objs}
                </div>
                <div class="col-md-6 col-sm-12">
                <div class="d-flex justify-content-end">
                <nav aria-label="Page navigation example">
                    <ul class="pagination">
                    <li id="previous-button" class="disabled page-item">
                        <span>
                            <a class="previous-button page-link" href="javascript:void(0)" aria-label="Previous">
                                <span aria-hidden="true">Previous</span>
                                <span class="sr-only">Previous</span>
                            </a>
                        </span>
                    </li>`;

        for (let page = 1; page < pagination.page_range; ++page) {
            if (pagination.number == page) {
                if (page == 1) {
                    html += `<li class="purple darken-3 active page-item" id="page-${page}" ><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                } else if (pagination.num_pages == page) {
                    html += `<li class="purple darken-3 page-item active" id="page-${page}" style="border-radius: 0 6px 6px 0;"><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                } else {
                    html += `<li class="active purple darken-3 page-item" style="border-radius: 0px;" id="page-${page}"><a data-page="${page}" class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)">${page}</a></li>`;
                }
            } else if (page > pagination.number - 5 && page < pagination.number + 5) {
                html += `<li class="purple darken-3 page-item" id="page-${page}"><a class="queue-pagination purple darken-3 page-item page-link" href="javascript:void(0)" data-page="${page}">${page}</a></li>`;
            }
        }
        html += `<li id="next-button" class="page-item">
                    <a class="next-button page-link" href="javascript:void(0)" aria-label="Next">
                        <span aria-hidden="true">Next</span>
                        <span class="sr-only">Next</span>
                    </a>
                </li>
                </ul>
                </nav>
                </div>
                </div>`;
    } else {
        html += `</div>`
    }
    let pagination_div = document.getElementById("pagination-div");
    if(pagination_div){
        document.getElementById("pagination-div").innerHTML = html;
    }
    
    events_for_pagination(pagination.page_range);

    // add_pagination_events();
}

function empty_support_history_table() {
    let history_table_div = document.getElementById('support_history_table');
    let side_bar_div = document.getElementById('custom-side-nav-bar');
    if (side_bar_div && history_table_div) {
        side_bar_div.innerHTML = '';
        history_table_div.innerHTML = '';
    }
}

function download_cognomeet_recording(session_id) {
    
    if(window.COGNOMEET_ACCESS_TOKEN == "" || window.COGNOMEET_ACCESS_TOKEN == undefined) {
        return;
    }

    let cognomeet_request_params = {
        "cognomeet_access_token": window.COGNOMEET_ACCESS_TOKEN,
        "session_id": session_id
    }

    let json_params = JSON.stringify(cognomeet_request_params);
    let encrypted_data = easyassist_custom_encrypt(json_params);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/cogno-meet/download-meeting-recording/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = easyassist_custom_decrypt(response.Response);
            response = JSON.parse(response);
            if (response.status == 200) {
                window.location = window.location.protocol + "//" + window.location.host + "/" + response.export_path;
            } else {
                show_easyassist_toast(response.message);
            }
        }
    }
    
    xhttp.send(params);
}

function update_support_history_table(_data) {
    let html = '';
    let details_html = '';
    let history_table_div = document.getElementById('support_history_table');
    let side_bar_div = document.getElementById('custom-side-nav-bar');
    if (side_bar_div && history_table_div) {
        side_bar_div.innerHTML = '';
        history_table_div.innerHTML = '';
        for (const data of _data) {
            html += [`        
            <tr>
                <td>
                    Name: 
                    ${data.customer_name == "" ? '-' : data.customer_name}
                    <br> Mobile Number: 
                        ${data.customer_mobile == "" ? '-' : data.customer_mobile}
                    <br>Initiated:             
                            -
                </td>
                <td>
                    ${data.meeting_start_date}
                </td>`].join('');

            if (agent_role != 'agent') {
                html += [`
                    <td>
                    ${data.cogno_meet_agent}
                    </td>`].join('');
            }


            html += [`
                <td>                
                    ${call_duration(data.total_call_duration)}
                </td>`].join('');
                
            if(enable_meeting_recording == 'True'){
            html+=[`<td>
                    <a class="btn btn-info" href="javascript:void(0)" onclick="download_cognomeet_recording('${data.session_id}')">Download</a>
                </td>`].join('');
            }
                
            html+=[`<td>                
                    ${data.actual_status}
                </td>
                <td>
                    <button type="button" onclick="show_right_sidenav('${data.audit_trail_pk}')" class="right-sidenav-session-btn btn btn-info btn-icon-split request-cobrowsing-btn-md">
                        <span class="icon text-white-50">
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 0C4.02991 0 0 4.02991 0 9C0 13.9701 4.02991 18 9 18C13.9701 18 18 13.9701 18 9C18 4.02991 13.9701 0 9 0ZM9.64286 13.3393C9.64286 13.4277 9.57054 13.5 9.48214 13.5H8.51786C8.42946 13.5 8.35714 13.4277 8.35714 13.3393V7.875C8.35714 7.78661 8.42946 7.71429 8.51786 7.71429H9.48214C9.57054 7.71429 9.64286 7.78661 9.64286 7.875V13.3393ZM9 6.42857C8.74766 6.42342 8.5074 6.31956 8.33076 6.13929C8.15413 5.95901 8.0552 5.71667 8.0552 5.46429C8.0552 5.2119 8.15413 4.96956 8.33076 4.78929C8.5074 4.60901 8.74766 4.50515 9 4.5C9.25234 4.50515 9.4926 4.60901 9.66924 4.78929C9.84587 4.96956 9.9448 5.2119 9.9448 5.46429C9.9448 5.71667 9.84587 5.95901 9.66924 6.13929C9.4926 6.31956 9.25234 6.42342 9 6.42857Z" fill="rgba(255,255,255,.5)"></path>
                            </svg>
                        </span>
                        <span class="text">Meeting Details</span>
                    </button>
                    <button type="button" onclick="show_right_sidenav('${data.audit_trail_pk}')" class="right-sidenav-session-btn btn btn-info request-cobrowsing-btn">
                        <div class="sessiondetail-icon">
                            <svg style="    margin-top: 12px;" width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M9 0C4.02991 0 0 4.02991 0 9C0 13.9701 4.02991 18 9 18C13.9701 18 18 13.9701 18 9C18 4.02991 13.9701 0 9 0ZM9.64286 13.3393C9.64286 13.4277 9.57054 13.5 9.48214 13.5H8.51786C8.42946 13.5 8.35714 13.4277 8.35714 13.3393V7.875C8.35714 7.78661 8.42946 7.71429 8.51786 7.71429H9.48214C9.57054 7.71429 9.64286 7.78661 9.64286 7.875V13.3393ZM9 6.42857C8.74766 6.42342 8.5074 6.31956 8.33076 6.13929C8.15413 5.95901 8.0552 5.71667 8.0552 5.46429C8.0552 5.2119 8.15413 4.96956 8.33076 4.78929C8.5074 4.60901 8.74766 4.50515 9 4.5C9.25234 4.50515 9.4926 4.60901 9.66924 4.78929C9.84587 4.96956 9.9448 5.2119 9.9448 5.46429C9.9448 5.71667 9.84587 5.95901 9.66924 6.13929C9.4926 6.31956 9.25234 6.42342 9 6.42857Z" fill="white"></path>
                            </svg>
                        </div>
                        <span class="text">Meeting Details</span>
                    </a>
                </td>
            </tr>`].join('');



            details_html += [`
            <div class="navbar-nav bg-gradient-light sidebar sidebar-dark accordion product-session-details" id="accordionSidebar-${data.audit_trail_pk}" style="overflow-y: scroll;max-height: 100vh;display: none;">
            <a class="sidebar-brand" href="javascript:void(0)">
                <div class="text-dark mx-3">Meeting Details<i class="fas fa-window-close text-dark" style="float:right;" onclick="hide_right_sidenav(this)"></i></div>
            </a>
            <div style="padding:0.5em 0.5em 1em 0.5em;">
                <strong>Meeting Id:</strong>
                <br>
                <a href="/easy-assist/sales-ai/meeting-audit-trail/?meeting_id=${data.session_id}">${data.session_id}</a>
                <hr>
                <div><strong>Customer Details</strong>
                </div>
                <br>
                <p><b>Name:</b> 
                ${data.customer_name == "" ? '-' : data.customer_name}
                </p>
                <p><b>Mobile Number:</b>
                ${data.customer_mobile == "" ? '-' : data.customer_mobile}
                </p>
                <p><b>Email Id:</b>
                ${data.customer_email == "" ? '-' : data.customer_email}
                </p>`].join('');

            if (data.location_available == 'True') {
                details_html += [`
                    <p><b>Location Details:</b> <a class="btn btn-info" href="#" data-toggle="modal" data-target="#client_location_details" onclick="show_client_location_details('${data.audit_trail_pk}');hide_right_sidenav_by_id('${data.audit_trail_pk}');">
                        Location Details</a>
                        <input type="hidden" value='${data.customer_location_details}' id='client-location-details-data-${data.audit_trail_pk}'>
                    </p>`].join('');
            }
            else {
                details_html += [`<p><b>Location Details:</b> No details</p>`].join('');
            }


            details_html += [`
                <p><b>Session Initiated By:</b> 
                    -
                </p>
                
                <hr>
                <div>
                    <strong>Meeting Details</strong>
                </div>
                <br>
                <p><b>Agent:</b> 
                    ${data.cogno_meet_agent}
                </p>`].join('')
            
            details_html += [`
            <p><b>Auto assigned agent:</b> 
                NA
            </p>
            `].join('');

            if(invite_agent_in_meeting == 'True'){
                details_html+=[`            
                <p><b>Support Agents:</b>
                    ${data.support_agents_invited}
                </p>
                    <p><b>Support Agents Connected:</b>
                    ${data.support_agents_joined}
                </p>`].join('');
            }

            details_html += [`            
                <p><b>Meeting Description:</b> ${data.meeting_title}</p>
                <p><b>Date:</b> ${data.meeting_start_date}</p>            
                <p><b>Initiated by:</b> NA </p>
                <p><b>Start Time:</b> ${data.meeting_start_time}</p>            
                <p><b>End Time:</b> ${data.meeting_end_time}</p>            
                <p><b>Agent Joined:</b> ${data.agent_joined_time != 'None' || data.agent_joined_time != "" ? data.agent_joined_time : '-'}</p>
                <p> <b>Total Time Spent (in HH:MM:SS): </b> ${call_duration(data.total_call_duration, true)}</p>`].join('');

            if (data.agent_notes != "None") {
                details_html += [`
                    <b>Agent Notes:</b>
                    <p style="overflow: auto;max-height: 150px;"> ${data.agent_notes} </p>`].join('');
            }
            else {
                details_html += [`
                    <p> <b>Agent Notes:</b> No Notes</p>`].join('');
            }

            details_html += [`
                <p><b>Status: </b>
                ${data.actual_status}`].join('');

            details_html += [`            
                ${data.agent_rating == 'None' ? '<p><b>NPS:</b> Not provided</p>' : '<p><b>NPS:</b>' + data.agent_rating + '</p>'}                
                ${(data.meeting_feedback_agent == 'None' || data.meeting_feedback_agent == null)? '<p><b>Comments:</b> Not provided</p>' : '<p><b>Comments:</b>' + data.meeting_feedback_agent + '</p>'}
                <p><b>Agent Comment:</b> Not provided</p>
                <hr>`].join('');

            details_html += [`
                <div>
                    <strong>Meeting Data</strong>
                </div>
                <br>`].join('');

            if (data.is_chat_available == 'True') {
                details_html += [`<p><b>Chat history:</b> <a class="btn btn-info" href="#" data-toggle="modal" data-target="#agent_chat_history" onclick="get_client_agent_chats_dyte('${data.session_id}');hide_right_sidenav_by_id('${data.audit_trail_pk}');">Show chat history</a></p>`].join('');
            }
            else {
                details_html += [`<p><b>Chat history:</b> No chat found</p>`];
            }


            if (data.is_screen_shot_available == 'True') {
                details_html += [`
                <p><b>Screenshot:</b> <button class="btn btn-info" data-toggle="modal" data-target="#see_captured_screenshot" onclick="show_captured_screenshots_dyte(${data.audit_trail_pk}); hide_right_sidenav_by_id(${data.audit_trail_pk})">Captured Screenshot</button></p>
                <input type="hidden" id="meeting-screencapture-${data.audit_trail_pk}" value='${data.meeting_screenshorts_urls}'>`].join('');
            }
            else {
                details_html += [`<p><b>Screenshot:</b> No screenshot captured</p>`].join('');
            }

            details_html += [`            
                </div>
                </div>`]

        }
        history_table_div.innerHTML = html;
        side_bar_div.innerHTML = details_html;
    }
}

function call_duration(value, string_format = false) {
    const sec = parseInt(value, 10); // convert value to number if it's string
    let hours = Math.floor(sec / 3600); // get hours
    let minutes = Math.floor((sec - (hours * 3600)) / 60); // get minutes
    let seconds = sec - (hours * 3600) - (minutes * 60); //  get seconds
    // add 0 if value < 10; Example: 2 => 02
    if (hours < 10) { hours = "0" + hours; }
    if (minutes < 10) { minutes = "0" + minutes; }
    if (seconds < 10) { seconds = "0" + seconds; }

    if (string_format) {
        return hours + ':' + minutes + ':' + seconds;
    }
    else {

        if (hours == 0 && minutes == 0) {
            return `${seconds} secs`;
        }
        if (hours == 0) {
            return `${minutes} mins`;
        }
        else {
            return `${hours} hour ${minutes} mins`;
        }
    }
}

function export_meeting_support_history_dyte(el) {

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

    var startdate_obj = new Date(startdate);
    var enddate_obj = new Date(enddate);
    var today_date = new Date();
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
            general_error_message.innerHTML = "End date cannot be past today's date";
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

            if (!regEmail.test(email_value_list[index])) {
                general_error_message.innerHTML = "Please enter valid Email ID";
                return;
            }
        }
    }

    el.innerHTML = "Exporting...";
    el.disabled = false;

    var json_string = JSON.stringify({
        "selected_filter_value": selected_filter_value,
        "startdate": startdate,
        "enddate": enddate,
        "email": email_field.value,
        "start_point": start_point,
        "end_point": end_point,
        "agents_list": agents_list,
        'cognomeet_access_token': window.COGNOMEET_ACCESS_TOKEN,
        "agent_role": window.agent_role
    });

    let encrypted_data = easyassist_custom_encrypt(json_string);
    encrypted_data = {
        "Request": encrypted_data
    };
    const params = JSON.stringify(encrypted_data);

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", window.location.protocol + "//" + window.location.host + "/cogno-meet/stats/export-meeting-support-history/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
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
                setTimeout(function () {
                    $('#modal-mis-filter').modal('hide');
                }, 2000);
            } else if(esponse.status == 401){
                show_easyassist_toast("Due to an invalid user role meeting support history could not be downloaded");
            } else {
                show_easyassist_toast("Unable to download meeting support history");
            } 
            el.innerHTML = "Export";
            el.disabled = false;
        }
    }
    xhttp.send(params);
}

function events_for_pagination(page_range) {
    let previous_button_ele = document.getElementById("previous-button");
    let next_button_ele = document.getElementById("next-button");
    $(".queue-pagination").on("click", (event) => {
        var current_page = event.target.dataset.page;
        if (document.getElementById('page-' + current_page.toString())) {
            $('#page-' + current_page.toString()).css({ "background": "black" });
        }
        if (current_page > 1) {
            if (document.getElementById('page-' + (current_page - 1).toString())) {
                document.getElementById('page-' + (current_page - 1).toString()).classList.remove("active");
            }
        }
        window.localStorage.setItem("meeting_support_history_current_page", current_page);
        if (parseInt(window.localStorage.getItem("meeting_support_history_current_page")) > 1) {
            if (previous_button_ele && previous_button_ele.classList.contains("disabled")) {
                previous_button_ele.classList.remove("disabled");
            }
        } else {
            if (previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
                document.getElementById("previous-button").classList.add("disabled");
            }
        }

        if (parseInt(window.localStorage.getItem("meeting_support_history_current_page")) < page_range - 1) {
            if (next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.remove("disabled");
            }
        } else {
            if (!next_button_ele && next_button_ele.classList.contains("disabled")) {
                document.getElementById("next-button").classList.add("disabled");
            }
        }
        get_cogno_meet_audit_trail_data();
    });

    if (parseInt(window.localStorage.getItem("meeting_support_history_current_page")) > 1) {
        if (previous_button_ele && previous_button_ele.classList.contains("disabled")) {
            previous_button_ele.classList.remove("disabled");
        }
        $(".previous-button").on("click", (event) => {
            let page_number = parseInt(window.localStorage.getItem("meeting_support_history_current_page")) - 1;
            window.localStorage.setItem("meeting_support_history_current_page", page_number);
            get_cogno_meet_audit_trail_data();
        });
    } else {
        if (previous_button_ele && !previous_button_ele.classList.contains("disabled")) {
            document.getElementById("previous-button").classList.add("disabled");
        }
    }

    if (parseInt(window.localStorage.getItem("meeting_support_history_current_page")) < page_range - 1) {
        if (next_button_ele && next_button_ele.classList.contains("disabled")) {
            document.getElementById("next-button").classList.remove("disabled");
        }
        $(".next-button").on("click", (event) => {
            let page_number = parseInt(window.localStorage.getItem("meeting_support_history_current_page")) + 1;
            window.localStorage.setItem("meeting_support_history_current_page", page_number);
            get_cogno_meet_audit_trail_data()
        });
    } else {
        if (next_button_ele && !next_button_ele.classList.contains("disabled")) {
            document.getElementById("next-button").classList.add("disabled");
        }
    }
}