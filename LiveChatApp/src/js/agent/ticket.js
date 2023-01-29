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
    is_mobile,
} from "../utils";

import { get_form_filled_data } from "./chatbox";

import { get_session_id } from "./console";

export async function livechat_raise_ticket() {

    let form_filled = [];
    form_filled = await get_form_filled_data('ticket');
    if (form_filled.length == 0) return;

    let json_string = {
        form_filled: form_filled,
        session_id: get_session_id(),
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/livechat-raise-ticket/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                $('#raise-ticket-error-message').css('display','none');
                $('#livechat-raise-ticket-modal').modal('hide');
                $('#ticket-id-span').text(response.ticket_id);
                $('#ticket-submit-modal').modal('show');

            } else if (response.status == 500) {

                $('#raise-ticket-error-message').css('display','block');

            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

export function livechat_search_ticket() {

    let ticket_id = document.getElementById("livechat-ticket-id").value;

    let json_string = {
        ticket_id: ticket_id,
        session_id: get_session_id(),
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/livechat-search-ticket/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                render_ticket_info_data(response.ticket_info);

            } else {

                $("#ticket-details-container").html('');
                $('#ticket-details-container').css('display','none');
                showToast( response.status_message, 2000 );
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}	

function render_ticket_info_data(ticket_info) {

    let html = '';

    for (var key of Object.keys(ticket_info)) {

        html += `<div class="livechat-ticket-details-item">
                    <div class="livechat-ticket-details-heading-label">
                        ${key} :
                    </div>
                    <div class="livechat-ticket-details-data-label">
                        ${ticket_info[key]}
                    </div>
                </div>`;
    }

    $("#ticket-details-container").html(html);
    $('#ticket-details-container').css('display','block');
}

export function livechat_get_previous_tickets() {

    let json_string = {
        session_id: get_session_id(),
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/livechat-get-previous-tickets/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if(response.status == 200) {

                let ticket_info_list = response.ticket_info_list;

                if (ticket_info_list.length == 0) {
                    showToast( "No previous tickets available for this customer!", 2000 );
                }
                else {
                    render_ticket_info_list(ticket_info_list);
                }

            } else {

                showToast( response.status_message, 2000 );
            }
        })        
        .catch((err) => {
            console.log(err);
        });
}

function render_ticket_info_list(ticket_info_list) {

    let html = '';

    for (let i = 0; i < ticket_info_list.length; i++) {
        let ticket_info = ticket_info_list[i];

        html += '<div class="livechat-ticket-details-container">'

        for (var key of Object.keys(ticket_info)) {

            if (key == 'Ticket Number') {

                html += ` <a href="#collapseCard${i}" class="d-block collapsed" data-toggle="collapse" role="button" aria-expanded="true" aria-controls="collapseCardExample">
                            <div class="livechat-ticket-details-item">
                                <div class="livechat-ticket-details-heading-label">
                                    ${key} :
                                </div>
                                <div class="livechat-ticket-details-data-label">
                                    ${ticket_info[key]}
                                </div>

                            </div>
                          </a>
                          <div class="collapse" id="collapseCard${i}">`

            } else {

                html += `<div class="livechat-ticket-details-item">
                            <div class="livechat-ticket-details-heading-label">
                                ${key} :
                            </div>
                            <div class="livechat-ticket-details-data-label">
                                ${ticket_info[key]}
                            </div>

                        </div>`;
            }
        }

        html += '</div></div>';

    }    

    $('#livechat-view-ticket-modal').modal('hide');
    $('#ticket-info-container').html(html);
    $('#livechat-previous-raised-ticket-modal').modal('show');
}

export function show_tms_enablement_toast(el) {
    if(el.checked) {
        showToast( "TMS Alert: Make sure you've enabled TMS in the EasyChat if you're using Cogno Desk", 2000 );
    }
}