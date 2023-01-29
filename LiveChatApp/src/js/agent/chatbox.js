import { add_mic_functionality, auto_resize, is_url, check_if_sentence_valid } from "./chatbox_input";
import {
    get_session_id,
    get_theme_color,
    getCsrfToken,
    set_session_id,
    set_prev_session_id,
    show_customer_status,
    get_icons,
    get_agent_name,
    append_message_in_chat_icon,
    showToast,
    update_customer_list,
    go_to_chat,
    update_document_title,
    reset_inactivity_timer,
    remove_inactivity_timer,
    remove_message_diffrentiator,
    get_agent_username,
    get_max_guest_agent,
    get_guest_agent_timer,
    update_guest_agent_status,
    remove_current_guest_session,
    get_voip_info,
    is_primary_agent,
    is_rtl_language,
    get_cobrowsing_info,
    set_cobrowsing_info,
    check_chat_escalation_status,
    get_current_customer_tab,
    check_is_email_session,
    send_transcript,
    show_custom_notification,
    hide_mics_for_iOS
} from "./console";

import {
    EncryptVariable,
    custom_decrypt,
    encrypt_variable,
    stripHTML,
    is_excel,
    is_video,
    is_txt,
    is_pdf,
    is_image,
    is_docs,
    get_image_path_html,
    get_video_path_html,
    get_doc_path_html,
    is_mobile,
    get_unread_message_diffrentiator_html,
    strip_unwanted_characters,
    is_valid_date,
    validate_name,
    validate_email,
    validate_phone_number,
    get_params,
    validate_number_input_value,
    stripHTMLtags,
    remove_special_characters_from_str,
} from "../utils";

import {
    get_data_present,
    get_message_history_store,
    get_customer_details_store,
    get_chat_info_store,
    add_message_to_local_db,
    is_indexed_db_supported,
    save_message_to_local,
    delete_messages_from_local,
    update_customer_details_in_local,
    get_messages_from_local,
} from "./local_db";

import {
    clear_customer_there_interval,
    create_websocket,
    send_message_to_socket,
    redirect_to_internal_chat,
} from "./livechat_chat_socket";

import { send_message_to_guest_agent_socket } from "./livechat_agent_socket";
import {
    change_date,
    generate_option_map,
    get_field_html_based_input_type,
    set_form_state,
    update_dependent_inputs,
} from "../admin/form_preview";
import { get_default_raise_ticket_form } from "../admin/form_builder";
import { connect_voip_call, send_voip_request_to_customer, set_voip_status } from "./voip/voip";
import { generate_video_meet_link, handle_vc_status_for_guest_agent, send_vc_request_to_customer } from "./vc/livechat_vc";

import { get_translated_text } from "./language_translation";
import axios from "axios";
import { connect_agent_to_cobrowsing, go_to_cobrowsing_page, send_cobrowsing_request_to_customer, set_cobrowsing_status, start_cobrowsing_timer } from "./cobrowsing/manage_cobrowsing";

import { initialize_country_code_selector, destroy_country_code_component } from "./country_code";

const state = {
    max_suggestions: 100,
    chat_data: {
        channel: "",
        bot_id: "",
        customer_name: "",
        easychat_user_id: "",
        category_enabled: "",
        closing_category: "",
        all_categories: "",
        is_form_enabled: false,
        form: {},
        is_external: false,
        raise_ticket_form: {},
    },
    timer_var: null,
    cannned_response: window.CANNED_ARR,
    blacklisted_keywords: window.BLACKLISTED_KEYWORD,
    customer_blacklisted_keywords: window.CUSTOMER_BLACKLISTED_KEYWORD,

    chat_history: {},
    user_in_other_tab: false,
    time_customer_ping: {},
    show_alert_if_customer_is_not_online_bool: false,
    customer_left_chat: {},
    bot_theme_color: "263238",
    is_message_diffrentiator_present: {},
    user_unseen_message: {},
    chat_history: {
        agent_username: "",
    },
    agent_options_list: [],
    agent_check_list: [],
    agent_pending_list: [],
    original_name: "",
    original_email: "",
    original_phone: "",
    country_code_error_map: ["Please enter a valid number", "Invalid country code", "The entered number is too short", "The entered number is too long", "Please enter a valid number"],
    country_codes: [{ "name": "Israel", "dial_code": "+972", "code": "IL" }, { "name": "Afghanistan", "dial_code": "+93", "code": "AF" }, { "name": "Albania", "dial_code": "+355", "code": "AL" }, { "name": "Algeria", "dial_code": "+213", "code": "DZ" }, { "name": "AmericanSamoa", "dial_code": "+1 684", "code": "AS" }, { "name": "Andorra", "dial_code": "+376", "code": "AD" }, { "name": "Angola", "dial_code": "+244", "code": "AO" }, { "name": "Anguilla", "dial_code": "+1 264", "code": "AI" }, { "name": "Antigua and Barbuda", "dial_code": "+1268", "code": "AG" }, { "name": "Argentina", "dial_code": "+54", "code": "AR" }, { "name": "Armenia", "dial_code": "+374", "code": "AM" }, { "name": "Aruba", "dial_code": "+297", "code": "AW" }, { "name": "Australia", "dial_code": "+61", "code": "AU" }, { "name": "Austria", "dial_code": "+43", "code": "AT" }, { "name": "Azerbaijan", "dial_code": "+994", "code": "AZ" }, { "name": "Bahamas", "dial_code": "+1 242", "code": "BS" }, { "name": "Bahrain", "dial_code": "+973", "code": "BH" }, { "name": "Bangladesh", "dial_code": "+880", "code": "BD" }, { "name": "Barbados", "dial_code": "+1 246", "code": "BB" }, { "name": "Belarus", "dial_code": "+375", "code": "BY" }, { "name": "Belgium", "dial_code": "+32", "code": "BE" }, { "name": "Belize", "dial_code": "+501", "code": "BZ" }, { "name": "Benin", "dial_code": "+229", "code": "BJ" }, { "name": "Bermuda", "dial_code": "+1 441", "code": "BM" }, { "name": "Bhutan", "dial_code": "+975", "code": "BT" }, { "name": "Bosnia and Herzegovina", "dial_code": "+387", "code": "BA" }, { "name": "Botswana", "dial_code": "+267", "code": "BW" }, { "name": "Brazil", "dial_code": "+55", "code": "BR" }, { "name": "British Indian Ocean Territory", "dial_code": "+246", "code": "IO" }, { "name": "Bulgaria", "dial_code": "+359", "code": "BG" }, { "name": "Burkina Faso", "dial_code": "+226", "code": "BF" }, { "name": "Burundi", "dial_code": "+257", "code": "BI" }, { "name": "Cambodia", "dial_code": "+855", "code": "KH" }, { "name": "Cameroon", "dial_code": "+237", "code": "CM" }, { "name": "Canada", "dial_code": "+1", "code": "CA" }, { "name": "Cape Verde", "dial_code": "+238", "code": "CV" }, { "name": "Cayman Islands", "dial_code": "+ 345", "code": "KY" }, { "name": "Central African Republic", "dial_code": "+236", "code": "CF" }, { "name": "Chad", "dial_code": "+235", "code": "TD" }, { "name": "Chile", "dial_code": "+56", "code": "CL" }, { "name": "China", "dial_code": "+86", "code": "CN" }, { "name": "Christmas Island", "dial_code": "+61", "code": "CX" }, { "name": "Colombia", "dial_code": "+57", "code": "CO" }, { "name": "Comoros", "dial_code": "+269", "code": "KM" }, { "name": "Congo", "dial_code": "+242", "code": "CG" }, { "name": "Cook Islands", "dial_code": "+682", "code": "CK" }, { "name": "Costa Rica", "dial_code": "+506", "code": "CR" }, { "name": "Croatia", "dial_code": "+385", "code": "HR" }, { "name": "Cuba", "dial_code": "+53", "code": "CU" }, { "name": "Cyprus", "dial_code": "+537", "code": "CY" }, { "name": "Czech Republic", "dial_code": "+420", "code": "CZ" }, { "name": "Denmark", "dial_code": "+45", "code": "DK" }, { "name": "Djibouti", "dial_code": "+253", "code": "DJ" }, { "name": "Dominica", "dial_code": "+1 767", "code": "DM" }, { "name": "Dominican Republic", "dial_code": "+1 849", "code": "DO" }, { "name": "Ecuador", "dial_code": "+593", "code": "EC" }, { "name": "Egypt", "dial_code": "+20", "code": "EG" }, { "name": "El Salvador", "dial_code": "+503", "code": "SV" }, { "name": "Equatorial Guinea", "dial_code": "+240", "code": "GQ" }, { "name": "Eritrea", "dial_code": "+291", "code": "ER" }, { "name": "Estonia", "dial_code": "+372", "code": "EE" }, { "name": "Ethiopia", "dial_code": "+251", "code": "ET" }, { "name": "Faroe Islands", "dial_code": "+298", "code": "FO" }, { "name": "Fiji", "dial_code": "+679", "code": "FJ" }, { "name": "Finland", "dial_code": "+358", "code": "FI" }, { "name": "France", "dial_code": "+33", "code": "FR" }, { "name": "French Guiana", "dial_code": "+594", "code": "GF" }, { "name": "French Polynesia", "dial_code": "+689", "code": "PF" }, { "name": "Gabon", "dial_code": "+241", "code": "GA" }, { "name": "Gambia", "dial_code": "+220", "code": "GM" }, { "name": "Georgia", "dial_code": "+995", "code": "GE" }, { "name": "Germany", "dial_code": "+49", "code": "DE" }, { "name": "Ghana", "dial_code": "+233", "code": "GH" }, { "name": "Gibraltar", "dial_code": "+350", "code": "GI" }, { "name": "Greece", "dial_code": "+30", "code": "GR" }, { "name": "Greenland", "dial_code": "+299", "code": "GL" }, { "name": "Grenada", "dial_code": "+1 473", "code": "GD" }, { "name": "Guadeloupe", "dial_code": "+590", "code": "GP" }, { "name": "Guam", "dial_code": "+1 671", "code": "GU" }, { "name": "Guatemala", "dial_code": "+502", "code": "GT" }, { "name": "Guinea", "dial_code": "+224", "code": "GN" }, { "name": "Guinea-Bissau", "dial_code": "+245", "code": "GW" }, { "name": "Guyana", "dial_code": "+595", "code": "GY" }, { "name": "Haiti", "dial_code": "+509", "code": "HT" }, { "name": "Honduras", "dial_code": "+504", "code": "HN" }, { "name": "Hungary", "dial_code": "+36", "code": "HU" }, { "name": "Iceland", "dial_code": "+354", "code": "IS" }, { "name": "India", "dial_code": "+91", "code": "IN" }, { "name": "Indonesia", "dial_code": "+62", "code": "ID" }, { "name": "Iraq", "dial_code": "+964", "code": "IQ" }, { "name": "Ireland", "dial_code": "+353", "code": "IE" }, { "name": "Israel", "dial_code": "+972", "code": "IL" }, { "name": "Italy", "dial_code": "+39", "code": "IT" }, { "name": "Jamaica", "dial_code": "+1 876", "code": "JM" }, { "name": "Japan", "dial_code": "+81", "code": "JP" }, { "name": "Jordan", "dial_code": "+962", "code": "JO" }, { "name": "Kazakhstan", "dial_code": "+7 7", "code": "KZ" }, { "name": "Kenya", "dial_code": "+254", "code": "KE" }, { "name": "Kiribati", "dial_code": "+686", "code": "KI" }, { "name": "Kuwait", "dial_code": "+965", "code": "KW" }, { "name": "Kyrgyzstan", "dial_code": "+996", "code": "KG" }, { "name": "Latvia", "dial_code": "+371", "code": "LV" }, { "name": "Lebanon", "dial_code": "+961", "code": "LB" }, { "name": "Lesotho", "dial_code": "+266", "code": "LS" }, { "name": "Liberia", "dial_code": "+231", "code": "LR" }, { "name": "Liechtenstein", "dial_code": "+423", "code": "LI" }, { "name": "Lithuania", "dial_code": "+370", "code": "LT" }, { "name": "Luxembourg", "dial_code": "+352", "code": "LU" }, { "name": "Madagascar", "dial_code": "+261", "code": "MG" }, { "name": "Malawi", "dial_code": "+265", "code": "MW" }, { "name": "Malaysia", "dial_code": "+60", "code": "MY" }, { "name": "Maldives", "dial_code": "+960", "code": "MV" }, { "name": "Mali", "dial_code": "+223", "code": "ML" }, { "name": "Malta", "dial_code": "+356", "code": "MT" }, { "name": "Marshall Islands", "dial_code": "+692", "code": "MH" }, { "name": "Martinique", "dial_code": "+596", "code": "MQ" }, { "name": "Mauritania", "dial_code": "+222", "code": "MR" }, { "name": "Mauritius", "dial_code": "+230", "code": "MU" }, { "name": "Mayotte", "dial_code": "+262", "code": "YT" }, { "name": "Mexico", "dial_code": "+52", "code": "MX" }, { "name": "Monaco", "dial_code": "+377", "code": "MC" }, { "name": "Mongolia", "dial_code": "+976", "code": "MN" }, { "name": "Montenegro", "dial_code": "+382", "code": "ME" }, { "name": "Montserrat", "dial_code": "+1664", "code": "MS" }, { "name": "Morocco", "dial_code": "+212", "code": "MA" }, { "name": "Myanmar", "dial_code": "+95", "code": "MM" }, { "name": "Namibia", "dial_code": "+264", "code": "NA" }, { "name": "Nauru", "dial_code": "+674", "code": "NR" }, { "name": "Nepal", "dial_code": "+977", "code": "NP" }, { "name": "Netherlands", "dial_code": "+31", "code": "NL" }, { "name": "Netherlands Antilles", "dial_code": "+599", "code": "AN" }, { "name": "New Caledonia", "dial_code": "+687", "code": "NC" }, { "name": "New Zealand", "dial_code": "+64", "code": "NZ" }, { "name": "Nicaragua", "dial_code": "+505", "code": "NI" }, { "name": "Niger", "dial_code": "+227", "code": "NE" }, { "name": "Nigeria", "dial_code": "+234", "code": "NG" }, { "name": "Niue", "dial_code": "+683", "code": "NU" }, { "name": "Norfolk Island", "dial_code": "+672", "code": "NF" }, { "name": "Northern Mariana Islands", "dial_code": "+1 670", "code": "MP" }, { "name": "Norway", "dial_code": "+47", "code": "NO" }, { "name": "Oman", "dial_code": "+968", "code": "OM" }, { "name": "Pakistan", "dial_code": "+92", "code": "PK" }, { "name": "Palau", "dial_code": "+680", "code": "PW" }, { "name": "Panama", "dial_code": "+507", "code": "PA" }, { "name": "Papua New Guinea", "dial_code": "+675", "code": "PG" }, { "name": "Paraguay", "dial_code": "+595", "code": "PY" }, { "name": "Peru", "dial_code": "+51", "code": "PE" }, { "name": "Philippines", "dial_code": "+63", "code": "PH" }, { "name": "Poland", "dial_code": "+48", "code": "PL" }, { "name": "Portugal", "dial_code": "+351", "code": "PT" }, { "name": "Puerto Rico", "dial_code": "+1 939", "code": "PR" }, { "name": "Qatar", "dial_code": "+974", "code": "QA" }, { "name": "Romania", "dial_code": "+40", "code": "RO" }, { "name": "Rwanda", "dial_code": "+250", "code": "RW" }, { "name": "Samoa", "dial_code": "+685", "code": "WS" }, { "name": "San Marino", "dial_code": "+378", "code": "SM" }, { "name": "Saudi Arabia", "dial_code": "+966", "code": "SA" }, { "name": "Senegal", "dial_code": "+221", "code": "SN" }, { "name": "Serbia", "dial_code": "+381", "code": "RS" }, { "name": "Seychelles", "dial_code": "+248", "code": "SC" }, { "name": "Sierra Leone", "dial_code": "+232", "code": "SL" }, { "name": "Singapore", "dial_code": "+65", "code": "SG" }, { "name": "Slovakia", "dial_code": "+421", "code": "SK" }, { "name": "Slovenia", "dial_code": "+386", "code": "SI" }, { "name": "Solomon Islands", "dial_code": "+677", "code": "SB" }, { "name": "South Africa", "dial_code": "+27", "code": "ZA" }, { "name": "South Georgia and the South Sandwich Islands", "dial_code": "+500", "code": "GS" }, { "name": "Spain", "dial_code": "+34", "code": "ES" }, { "name": "Sri Lanka", "dial_code": "+94", "code": "LK" }, { "name": "Sudan", "dial_code": "+249", "code": "SD" }, { "name": "Suriname", "dial_code": "+597", "code": "SR" }, { "name": "Swaziland", "dial_code": "+268", "code": "SZ" }, { "name": "Sweden", "dial_code": "+46", "code": "SE" }, { "name": "Switzerland", "dial_code": "+41", "code": "CH" }, { "name": "Tajikistan", "dial_code": "+992", "code": "TJ" }, { "name": "Thailand", "dial_code": "+66", "code": "TH" }, { "name": "Togo", "dial_code": "+228", "code": "TG" }, { "name": "Tokelau", "dial_code": "+690", "code": "TK" }, { "name": "Tonga", "dial_code": "+676", "code": "TO" }, { "name": "Trinidad and Tobago", "dial_code": "+1 868", "code": "TT" }, { "name": "Tunisia", "dial_code": "+216", "code": "TN" }, { "name": "Turkey", "dial_code": "+90", "code": "TR" }, { "name": "Turkmenistan", "dial_code": "+993", "code": "TM" }, { "name": "Turks and Caicos Islands", "dial_code": "+1 649", "code": "TC" }, { "name": "Tuvalu", "dial_code": "+688", "code": "TV" }, { "name": "Uganda", "dial_code": "+256", "code": "UG" }, { "name": "Ukraine", "dial_code": "+380", "code": "UA" }, { "name": "United Arab Emirates", "dial_code": "+971", "code": "AE" }, { "name": "United Kingdom", "dial_code": "+44", "code": "GB" }, { "name": "United States", "dial_code": "+1", "code": "US" }, { "name": "Uruguay", "dial_code": "+598", "code": "UY" }, { "name": "Uzbekistan", "dial_code": "+998", "code": "UZ" }, { "name": "Vanuatu", "dial_code": "+678", "code": "VU" }, { "name": "Wallis and Futuna", "dial_code": "+681", "code": "WF" }, { "name": "Yemen", "dial_code": "+967", "code": "YE" }, { "name": "Zambia", "dial_code": "+260", "code": "ZM" }, { "name": "Zimbabwe", "dial_code": "+263", "code": "ZW" }, { "name": "land Islands", "dial_code": "", "code": "AX" }, { "name": "Antarctica", "dial_code": null, "code": "AQ" }, { "name": "Bolivia, Plurinational State of", "dial_code": "+591", "code": "BO" }, { "name": "Brunei Darussalam", "dial_code": "+673", "code": "BN" }, { "name": "Cocos (Keeling) Islands", "dial_code": "+61", "code": "CC" }, { "name": "Congo, The Democratic Republic of the", "dial_code": "+243", "code": "CD" }, { "name": "Cote d'Ivoire", "dial_code": "+225", "code": "CI" }, { "name": "Falkland Islands (Malvinas)", "dial_code": "+500", "code": "FK" }, { "name": "Guernsey", "dial_code": "+44", "code": "GG" }, { "name": "Holy See (Vatican City State)", "dial_code": "+379", "code": "VA" }, { "name": "Hong Kong", "dial_code": "+852", "code": "HK" }, { "name": "Iran, Islamic Republic of", "dial_code": "+98", "code": "IR" }, { "name": "Isle of Man", "dial_code": "+44", "code": "IM" }, { "name": "Jersey", "dial_code": "+44", "code": "JE" }, { "name": "Korea, Democratic People's Republic of", "dial_code": "+850", "code": "KP" }, { "name": "Korea, Republic of", "dial_code": "+82", "code": "KR" }, { "name": "Lao People's Democratic Republic", "dial_code": "+856", "code": "LA" }, { "name": "Libyan Arab Jamahiriya", "dial_code": "+218", "code": "LY" }, { "name": "Macao", "dial_code": "+853", "code": "MO" }, { "name": "Macedonia, The Former Yugoslav Republic of", "dial_code": "+389", "code": "MK" }, { "name": "Micronesia, Federated States of", "dial_code": "+691", "code": "FM" }, { "name": "Moldova, Republic of", "dial_code": "+373", "code": "MD" }, { "name": "Mozambique", "dial_code": "+258", "code": "MZ" }, { "name": "Palestinian Territory, Occupied", "dial_code": "+970", "code": "PS" }, { "name": "Pitcairn", "dial_code": "+872", "code": "PN" }, { "name": "Réunion", "dial_code": "+262", "code": "RE" }, { "name": "Russia", "dial_code": "+7", "code": "RU" }, { "name": "Saint Barthélemy", "dial_code": "+590", "code": "BL" }, { "name": "Saint Helena, Ascension and Tristan Da Cunha", "dial_code": "+290", "code": "SH" }, { "name": "Saint Kitts and Nevis", "dial_code": "+1 869", "code": "KN" }, { "name": "Saint Lucia", "dial_code": "+1 758", "code": "LC" }, { "name": "Saint Martin", "dial_code": "+590", "code": "MF" }, { "name": "Saint Pierre and Miquelon", "dial_code": "+508", "code": "PM" }, { "name": "Saint Vincent and the Grenadines", "dial_code": "+1 784", "code": "VC" }, { "name": "Sao Tome and Principe", "dial_code": "+239", "code": "ST" }, { "name": "Somalia", "dial_code": "+252", "code": "SO" }, { "name": "Svalbard and Jan Mayen", "dial_code": "+47", "code": "SJ" }, { "name": "Syrian Arab Republic", "dial_code": "+963", "code": "SY" }, { "name": "Taiwan, Province of China", "dial_code": "+886", "code": "TW" }, { "name": "Tanzania, United Republic of", "dial_code": "+255", "code": "TZ" }, { "name": "Timor-Leste", "dial_code": "+670", "code": "TL" }, { "name": "Venezuela, Bolivarian Republic of", "dial_code": "+58", "code": "VE" }, { "name": "Viet Nam", "dial_code": "+84", "code": "VN" }, { "name": "Virgin Islands, British", "dial_code": "+1 284", "code": "VG" }, { "name": "Virgin Islands, U.S.", "dial_code": "+1 340", "code": "VI" }],
};

// js for day/date ui

Date.prototype.getMonthText = function() {
    var months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ];
    return months[this.getMonth()];
};

var now = new Date();
var month = now.getMonthText();
var scrollTimeout = null;
var scrollendDelay = 1000; // ms
var indicator_date = "01-Jan-1984";
var todays_date = now.getDate() + "-" + month + "-" + now.getFullYear();
var fixed_date_string = "";
var initialized_date = 0;
var previous_session_id = "";
const RESPONSE_SENTENCE_SEPARATOR = '$$$';

function scrollbeginHandler() {
    $(".live-chat-day-date-indicator").animate({
        top: "15px",
    });

}

function scrollendHandler() {
    $(".live-chat-day-date-indicator").animate({
        top: "-130px",
    });

    scrollTimeout = null;
}
//js for day.date ui end

function hide_prev_chat(session_id) {
    const chat_div = document.getElementById(`style-2_${session_id}`);

    if (chat_div != undefined && chat_div != null) {
        chat_div.style.display = "none";
    }
}

function show_console() {
    try {
        show_alert_if_customer_is_not_online_bool = false;
        clear_customer_there_interval();
    } catch (err) {}

    if (!is_mobile()) {
        document.getElementById(
            "live-chat-customer-details-sidebar"
        ).style.display = "block";
    } else {
        var currElement = document.getElementById(
            "live-chat-active-customers-sidebar"
        );
        if (getComputedStyle(currElement).display === "block")
            currElement.style.display = "none";
        else currElement.style.display = "block";
    }

    document.getElementById("live-chat-no-chat-opened").style.display = "none";
    document.getElementById("livechat-main-console").style.display = "block";

    if (previous_session_id != "") {
        if ($("#live-chat-indicator-" + previous_session_id).length)
            $("#live-chat-indicator-" + previous_session_id).css(
                "display",
                "none"
            );

        if ($("#load-more-chats-" + previous_session_id).length) {
            $("#load-more-chats-" + previous_session_id)
                .parent()
                .css("display", "none");
        }
    }

    const session_id = get_session_id();
    previous_session_id = session_id;
    if (
        document.getElementsByClassName(
            "live-chat-message-day-time-div-" + session_id
        )[0]
    ) {
        fixed_date_string = document.getElementsByClassName(
            "live-chat-message-day-time-div-" + session_id
        )[0].innerHTML;
    } else {
        fixed_date_string = "";
    }
    if ($("#live-chat-indicator-" + session_id).length)
        $("#live-chat-indicator-" + session_id).css("display", "flex");

    const chat_div = document.getElementById(`style-2_${session_id}`);
    if (
        $("#load-more-chats-" + session_id).length &&
        chat_div != undefined &&
        chat_div != null
    ) {
        $("#load-more-chats-" + session_id)
            .parent()
            .css("display", "block");
    }

    scrollendHandler();
    if (chat_div == undefined || chat_div == null) {
        const parent_chat_div =
            document.getElementsByClassName("live-chat-area")[0];
        const html = ` <div class="loader-custom" id="chat_loader"><div id="loader-inside-div">
            <div>
            </div>
            <div>
            </div>
            <div>
            </div>
            <div>
            </div>
        </div>
    </div>
    <div class="live-chat-new-message-reply-comment-notification-div" id="live-chat-new-message-reply-comment-notification-${session_id}" style="display: none;">
        <svg width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.5 2C14.9183 2 18.5 5.58172 18.5 10C18.5 14.4183 14.9183 18 10.5 18C9.22679 18 7.99591 17.7018 6.88669 17.1393L6.766 17.075L3.12109 17.9851C2.81127 18.0625 2.52622 17.8369 2.50131 17.5438L2.50114 17.4624L2.51493 17.3787L3.425 13.735L3.36169 13.6153C2.9066 12.7186 2.62433 11.7422 2.53275 10.7283L2.50738 10.3463L2.5 10C2.5 5.58172 6.08172 2 10.5 2ZM10.5 3C6.63401 3 3.5 6.13401 3.5 10C3.5 11.217 3.81054 12.3878 4.39352 13.4249C4.44046 13.5084 4.4621 13.603 4.45692 13.6973L4.44274 13.7912L3.687 16.812L6.71104 16.0583C6.77294 16.0429 6.83662 16.0396 6.89873 16.0479L6.9903 16.0691L7.07701 16.1075C8.11362 16.6898 9.2837 17 10.5 17C14.366 17 17.5 13.866 17.5 10C17.5 6.13401 14.366 3 10.5 3ZM11 11C11.2761 11 11.5 11.2239 11.5 11.5C11.5 11.7455 11.3231 11.9496 11.0899 11.9919L11 12H8C7.72386 12 7.5 11.7761 7.5 11.5C7.5 11.2545 7.67688 11.0504 7.91012 11.0081L8 11H11ZM13 8C13.2761 8 13.5 8.22386 13.5 8.5C13.5 8.74546 13.3231 8.94961 13.0899 8.99194L13 9H8C7.72386 9 7.5 8.77614 7.5 8.5C7.5 8.25454 7.67688 8.05039 7.91012 8.00806L8 8H13Z" fill="#2D2D2D"/>
        </svg>
        <span id="supervisor-comment-notif-${session_id}"></span>
        <button type="button" onclick="hide_message_reply_notification_function();" class="live-chat-new-message-reply-comment-notification-div-hide-btn">
            <svg width="13" height="12" viewBox="0 0 13 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.39705 2.05379L2.46967 1.96967C2.73594 1.7034 3.1526 1.6792 3.44621 1.89705L3.53033 1.96967L6.5 4.939L9.46967 1.96967C9.76256 1.67678 10.2374 1.67678 10.5303 1.96967C10.8232 2.26256 10.8232 2.73744 10.5303 3.03033L7.561 6L10.5303 8.96967C10.7966 9.23594 10.8208 9.6526 10.6029 9.94621L10.5303 10.0303C10.2641 10.2966 9.8474 10.3208 9.55379 10.1029L9.46967 10.0303L6.5 7.061L3.53033 10.0303C3.23744 10.3232 2.76256 10.3232 2.46967 10.0303C2.17678 9.73744 2.17678 9.26256 2.46967 8.96967L5.439 6L2.46967 3.03033C2.2034 2.76406 2.1792 2.3474 2.39705 2.05379L2.46967 1.96967L2.39705 2.05379Z" fill="#212121"/>
            </svg>
        </button>
    </div>
    <div class="live-chat-day-date-indicator" id="live-chat-indicator-${session_id}">Today</div> <div class="load-more-chats-div-wrapper" style="
    position: fixed;
    width: 47%;
    background: white;
    height: 30px;
    z-index: 100;
    display: block;
"><div class="load-more-chats-div" style="display: block" id="load-more-chats-${session_id}"><a href="javascript:void(0)" onclick="on_chat_history_div_scroll_chat_area(this,'${session_id}','true')">Load more chats </a></div></div> <div class="live-chat-message-wrapper" onscroll="on_chat_history_div_scroll_chat_area(this,'${session_id}','false')" id="style-2_${session_id}" ></div><input id="hidden_current_session_id_${session_id}" type="hidden"  value = "${session_id}"><input id="top_reached_${session_id}" type="hidden"  value = "0">`;
        $(parent_chat_div).prepend(html);
    } else {
        chat_div.style.display = "block";
    }

    document.getElementById("query").value = localStorage.getItem(
        `user_input-${session_id}`
    );
    document.getElementById("query").oninput = () => {
        localStorage.setItem(
            `user_input-${session_id}`,
            document.getElementById("query").value
        );
        reset_inactivity_timer(session_id, state.chat_data.bot_id, "agent");
    };

    auto_resize();
}

if (!("webkitSpeechRecognition" in window)) {
    if (
        typeof document.getElementById("livechat-mic") !== "undefined" &&
        document.getElementById("livechat-mic") != null
    ) {
        document.getElementById("livechat-mic").style.display = "none";
    }
} else {
    add_mic_functionality();
}

export function get_text_data(field, field_id) {
    let filled_value = document
        .getElementById(`input-element_${field_id.split("_")[1]}`)
        .value.trim();

    filled_value = stripHTML(filled_value);
    filled_value = strip_unwanted_characters(filled_value);

    if (field.optional) {
        if (filled_value == "") {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }

    if (filled_value == "") {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    }

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}

export function get_mobile_data(field, field_id) {
    let filled_value = document
        .getElementById(`input-element_${field_id.split("_")[1]}`)
        .value.trim();

    filled_value = stripHTML(filled_value);
    filled_value = strip_unwanted_characters(filled_value);

    if (field.optional) {
        if (filled_value == "") {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }

    if (filled_value == "") {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    } else {
        
        let is_valid = $(`#input-element_${field_id.split('_')[1]}`).intlTelInput("isValidNumber");       
        if (!is_valid) {
            return {
                is_valid: false,
                error: "Enter valid mobile number"
            }
        }

        if($(`#input-element_${field_id.split('_')[1]}`).intlTelInput("getSelectedCountryData").dialCode == "91") {

            if (!validate_phone_number(`input-element_${field_id.split('_')[1]}`)) {
                return {
                    is_valid: false,
                    error: "Enter valid mobile number"
                }
            }
        } else {
            if (!validate_number_input_value(filled_value)) {
                return {
                    is_valid: false,
                    error: "Enter valid mobile number"
                }
            }
        }
    }

    const code = $(`#input-element_${field_id.split('_')[1]}`).intlTelInput("getSelectedCountryData").dialCode;

    filled_value = code + filled_value;

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}

export function get_email_data(field, field_id) {
    let filled_value = document
        .getElementById(`input-element_${field_id.split("_")[1]}`)
        .value.trim();

    filled_value = stripHTML(filled_value);

    if (field.optional) {
        if (filled_value == "") {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }

    if (filled_value == "") {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    } else {
        if (!validate_email(`input-element_${field_id.split('_')[1]}`)) {
            return {
                is_valid: false,
                error: "Please enter valid Email ID",
            }
        }
    }

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}


export function get_dropdown_data(field, field_id) {
    const filled_value = document.getElementById(
        `input-element_${field_id.split("_")[1]}`
    ).value;

    if (field.optional) {
        if (filled_value == "0") {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }

    if (filled_value == "0") {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    }

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}

export function get_radio_data(field, field_id) {
    const filled_value = $(
        `input[type='radio'][name="radio_${field_id.split("_")[1]}"]:checked`
    ).val();

    if (field.optional) {
        if (!filled_value || filled_value == "") {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }

    if (!filled_value || filled_value == "") {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    }

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}

export function get_checkbox_data(field, field_id) {
    const elems = document.getElementsByClassName(
        `livechat-form-checkbox_${field_id.split("_")[1]}`
    );

    let filled_value = [];
    Array.from(elems).forEach((elem) => {
        if (elem.checked) {
            filled_value.push(elem.value);
        }
    });

    if (field.optional) {
        if (filled_value.length == 0) {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }

    if (filled_value.length == 0) {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    }

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}

function get_date_in_selected_format(selected_date, format) {
    const [day, month, year] = selected_date.split("/");

    if (format == "%d-%m-%y") {
        return `${day}-${month}-${year}`;
    }

    if (format == "%m-%d-%y") {
        return `${month}-${day}-${year}`;
    }

    if (format == "%y-%d-%m") {
        return `${year}-${day}-${month}`;
    }

    if (format == "%y-%m-%d") {
        return `${year}-${month}-${day}`;
    }
}

export function get_datepicker_data(field, field_id) {
    let filled_value = document
        .getElementById(`livechat-form-datepicker_${field_id.split("_")[1]}`)
        .value.trim();

    if (field.optional) {
        if (filled_value == "") {
            return {
                label: field.label_name,
                value: "*No Data filled*",
            };
        }
    }


    if (!is_valid_date(filled_value)) {
        return {
            is_valid: false,
            error: "Please enter valid date",
        };
    }

    if (filled_value == "") {
        return {
            is_valid: false,
            error: "Please fill mandatory fields.",
        };
    }

    filled_value = get_date_in_selected_format(filled_value, field.date_format);

    return {
        type: field.type,
        label: field.label_name,
        optional: field.optional,
        value: filled_value,
    };
}

export async function get_form_filled_data(type) {
    let form_filled = [];
    let form = state.chat_data.form;

    if (type == 'ticket') {
        form = state.chat_data.raise_ticket_form;
    }
    const fields = form.field_order;
    let is_form_filled = true;
    for (let field_id of fields) {
        const field = form[field_id];

        let res = {};
        if (field.type == "1" || field.type == "5") {
            res = get_text_data(field, field_id);
        } else if (field.type == "2") {
            res = get_radio_data(field, field_id);
        } else if (field.type == "3") {
            res = get_checkbox_data(field, field_id);
        } else if (field.type == "4") {
            res = get_datepicker_data(field, field_id);
        } else if (field.type == "6") {
            res = get_dropdown_data(field, field_id);
        } else if (field.type == "7") {
            res = await get_attachment_data(field, field_id);
        } else if (field.type == "8") {
            res = get_mobile_data(field, field_id);
        } else if (field.type == "9") {
            res = get_email_data(field, field_id);
        }

        if ("is_valid" in res && res.is_valid == false) {
            showToast(res.error, 2000);
            is_form_filled = false;
            return;
        }

        form_filled.push(res);
    }

    if (!is_form_filled) return [];

    return form_filled;
}

export function get_attachment_data(field, field_id) {
    return new Promise((resolve, reject) => {
        const attachment_data = document.querySelector(`#drag-drop-input-boxpreview_${field_id.split("_")[1]}`).files[0];

        if (field.optional) {
            if (!attachment_data) {
                resolve({
                    label: field.label_name,
                    value: "*No Data filled*",
                });
            }
        }

        let filename = "";
        let file_base64_str = "";

        var reader = new FileReader();
        reader.readAsDataURL(attachment_data);
        reader.onload = function() {
            filename = attachment_data.name
            file_base64_str = reader.result.split(",")[1];

            resolve({
                type: field.type,
                label: field.label_name,
                optional: field.optional,
                filename: filename,
                file_base64_str: file_base64_str,
                value: filename
            });
        };

        reader.onerror = function(error) {
            console.log('Error: ', error);
            resolve({
                type: field.type,
                label: field.label_name,
                optional: field.optional,
                filename: filename,
                file_base64_str: file_base64_str,
                value: filename
            });

        };
    });
}

async function mark_chat_session_expired() {
    let curr_session_id = get_session_id();
    const voip_info = get_voip_info();

    if (voip_info.session_id == curr_session_id && voip_info.request_status == 'ongoing') {
        showToast('Please end the ongoing call', 2000);

        return;
    }

    let show_cancel_meet_popup = false;
    if ((voip_info.session_id == curr_session_id && voip_info.request_status != 'none') || voip_info.customer_requests.includes(curr_session_id)) {
        show_cancel_meet_popup = true;
    }

    const cobrowsing_info = get_cobrowsing_info();
    if (cobrowsing_info.session_id == curr_session_id) {
        if (cobrowsing_info.status != 'ongoing') {
            set_cobrowsing_info({
                meeting_id: null,
                session_id: null,
                status: 'none',
            })
        }
    }

    let form_filled = [];
    if (state.chat_data.is_form_enabled) {
        form_filled = await get_form_filled_data('resolve');

        if (form_filled.length == 0) return;
    }

    let sender = "agent_end_session";
    let sentence = JSON.stringify({
        message: JSON.stringify({
            text_message: "",
            type: "text",
            channel: state.chat_data.channel,
            path: "",
            bot_id: state.chat_data.bot_id,
            show_cancel_meet_popup: show_cancel_meet_popup,
        }),
        sender: sender,
    });

    // for category not enabled, closing_category_pk = -1
    let closing_category_pk = -1;
    try {
        closing_category_pk = document.getElementById(
            "category-closing-priority"
        ).value;
    } catch (err) {}

    send_message_to_socket(sentence);
    let message =
        "SessionExpired_" +
        curr_session_id +
        "_ClosingCategory_" +
        closing_category_pk;

    const session_id = curr_session_id;
    var json_string = JSON.stringify({
        session_id: curr_session_id,
        closing_category_pk: closing_category_pk,
        bot_id: state.chat_data.bot_id,
        form_filled: form_filled,
    });
    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/end-chat-session/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let message = "Agent resolved the chat";
            let guest_message = message;

            let message_id = save_system_message(message, "CHAT_RESOLVED_BY_AGENT", curr_session_id);

            message = JSON.stringify({
                message: JSON.stringify({
                    text_message: message,
                    text_message_customer: message,
                    type: "text",
                    channel: state.chat_data.channel,
                    path: "",
                    event_type: "PRIMARY_AGENT_RESOLVED",
                    session_id: curr_session_id,
                    message_id: message_id,
                }),
                sender: "System",
            });

            send_transcript();
            send_message_to_socket(message);
            update_customer_list();
            remove_inactivity_timer(curr_session_id);
            go_to_chat(curr_session_id, true);
            localStorage.setItem(`auto_disposal-${session_id}`, false);
        }
    };
    xhttp.send(params);

    $("#end-chat-session").modal("hide");

    remove_session_local_variables(curr_session_id);

    if (is_indexed_db_supported()) {
        let message_history = get_message_history_store();
        let chat_info = get_chat_info_store();
        let customer_details = get_customer_details_store();

        delete_messages_from_local(message_history.name);
        delete_messages_from_local(chat_info.name);
        delete_messages_from_local(customer_details.name);
    }
}

function mark_all_message_seen(session_id) {
    var easychat_doubletick_list = document.getElementsByClassName(
        `doubletick_livechat_agent-${session_id}`
    );

    for (var itr = 0; itr < easychat_doubletick_list.length; itr++) {
        easychat_doubletick_list[itr].style.fill = "#0254D7";
    }
}

function get_image_path_html_attach(attached_file_src) {
    attached_file_src = attached_file_src.includes(window.location.origin) ? attached_file_src : window.location.origin + attached_file_src;
    var html =
        '<img onclick="preview_livechat_attachment_image(this.src)" src="' +    
        attached_file_src +
        '" style="height: 129px;width: 100%;border-radius: 1em;object-fit: cover;cursor:pointer;">';

    return html;
}

function get_file_to_agent_html_sent_customer(
    attached_file_src,
    sender_name,
    thumbnail_url,
    is_guest_agent_message = false,
    message_id = "",
    time = return_time()
) {
    let html = "";
    var len = attached_file_src.split("/").length;
    var message_bubble = "";
    var sender_name_html =
        '<div class="live-chat-client-name-with-message">' +
        sender_name +
        "</div>";
    if (is_guest_agent_message)
        message_bubble =
        '<div class="live-chat-client-message-bubble file-attachement-download live-chat-client-message-bubble-blue-border">';
    else
        message_bubble =
        '<div class="live-chat-client-message-bubble file-attachement-download">';
    if (is_pdf(attached_file_src)) {
        html =
            '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                        <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            "</div>" +
            sender_name_html +
            message_bubble +
            '<div style="    width: 50px; height: 45px; display: inline-block;"><svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M31.6312 2.71948L38.934 10.332V39.2805H11.6537V39.375H39.0272V10.4278L31.6312 2.71948Z" fill="#909090"></path>\
                            <path d="M31.5406 2.625H11.5604V39.2805H38.9339V10.3333L31.5393 2.625" fill="#F4F4F4"></path>\
                            <path d="M11.3596 4.59375H2.97272V13.5542H29.354V4.59375H11.3596Z" fill="#7A7B7C"></path>\
                            <path d="M29.4943 13.4019H3.14328V4.43494H29.4943V13.4019Z" fill="#DD2025"></path>\
                            <path d="M11.8808 5.95087H10.1653V12.2509H11.5146V10.1259L11.8125 10.143C12.102 10.138 12.3888 10.0862 12.6617 9.98943C12.901 9.90713 13.1211 9.77721 13.3088 9.60749C13.4997 9.44582 13.6503 9.24177 13.7485 9.01162C13.8801 8.62902 13.9271 8.22241 13.8863 7.81987C13.8781 7.53231 13.8277 7.24752 13.7367 6.97462C13.6538 6.77762 13.5308 6.60003 13.3756 6.45315C13.2204 6.30627 13.0362 6.19332 12.835 6.12149C12.6609 6.05849 12.4811 6.01277 12.2982 5.98499C12.1596 5.96361 12.0197 5.95221 11.8795 5.95087H11.8808ZM11.6314 8.96174H11.5146V7.01924H11.7679C11.8797 7.01118 11.9919 7.02834 12.0962 7.06946C12.2004 7.11058 12.2941 7.17461 12.3703 7.2568C12.5283 7.46814 12.6126 7.72537 12.6105 7.98918C12.6105 8.31205 12.6105 8.60474 12.3192 8.8108C12.1092 8.92626 11.8703 8.97824 11.6314 8.96043" fill="#464648"></path>\
                            <path d="M16.4495 5.93381C16.3038 5.93381 16.162 5.94431 16.0623 5.94825L15.7499 5.95612H14.7262V12.2561H15.931C16.3915 12.2687 16.8499 12.1907 17.2803 12.0264C17.6267 11.889 17.9334 11.6676 18.1728 11.382C18.4056 11.0938 18.5727 10.7583 18.6624 10.3989C18.7655 9.99189 18.8158 9.57326 18.812 9.15337C18.8374 8.65745 18.7991 8.16032 18.6978 7.67419C18.6017 7.31635 18.4217 6.98656 18.1728 6.71212C17.9775 6.49052 17.7384 6.31177 17.4706 6.18712C17.2406 6.0807 16.9987 6.00227 16.75 5.9535C16.6512 5.93716 16.551 5.9297 16.4508 5.93119L16.4495 5.93381ZM16.2119 11.0985H16.0807V7.077H16.0977C16.3683 7.04587 16.6421 7.09469 16.8852 7.21744C17.0633 7.35961 17.2084 7.53874 17.3105 7.74244C17.4207 7.95681 17.4842 8.1921 17.4969 8.43281C17.5087 8.72156 17.4969 8.95781 17.4969 9.15337C17.5022 9.37865 17.4877 9.60395 17.4535 9.82669C17.4131 10.0554 17.3383 10.2766 17.2317 10.4829C17.1111 10.6748 16.9481 10.8364 16.7553 10.9554C16.5934 11.0602 16.4016 11.109 16.2093 11.0946" fill="#464648"></path>\
                            <path d="M22.8769 5.95612H19.6875V12.2561H21.0367V9.75712H22.743V8.58637H21.0367V7.12687H22.8742V5.95612" fill="#464648"></path>\
                            <path d="M28.5875 26.5847C28.5875 26.5847 32.7717 25.8261 32.7717 27.2554C32.7717 28.6847 30.1795 28.1033 28.5875 26.5847ZM25.4939 26.6936C24.8291 26.8405 24.1812 27.0556 23.5606 27.3355L24.0856 26.1542C24.6106 24.9729 25.1553 23.3625 25.1553 23.3625C25.7817 24.4169 26.5106 25.4069 27.3314 26.3183C26.7124 26.4106 26.099 26.5367 25.4939 26.6963V26.6936ZM23.8375 18.1624C23.8375 16.9168 24.2405 16.5769 24.5541 16.5769C24.8678 16.5769 25.2209 16.7278 25.2327 17.8093C25.1305 18.8968 24.9028 19.9688 24.5541 21.004C24.0766 20.1349 23.8294 19.158 23.8362 18.1663L23.8375 18.1624ZM17.7357 31.9646C16.4521 31.1968 20.4277 28.833 21.1482 28.7569C21.1443 28.7582 19.0797 32.7679 17.7357 31.9646ZM33.9936 27.4247C33.9805 27.2935 33.8624 25.8405 31.2768 25.9022C30.199 25.8848 29.1218 25.9608 28.0572 26.1293C27.0259 25.0903 26.1378 23.9184 25.4165 22.6446C25.8709 21.3313 26.146 19.9627 26.2342 18.5758C26.1961 17.0008 25.8194 16.0978 24.6119 16.111C23.4044 16.1241 23.2285 17.1806 23.3873 18.753C23.5429 19.8096 23.8363 20.8413 24.2601 21.8216C24.2601 21.8216 23.7023 23.5581 22.9647 25.2853C22.2271 27.0126 21.7231 27.9182 21.7231 27.9182C20.4404 28.3358 19.2329 28.9561 18.1465 29.7557C17.065 30.7624 16.6253 31.5354 17.195 32.3085C17.6858 32.9753 19.4039 33.1262 20.9395 31.1141C21.7555 30.0749 22.5009 28.9822 23.1708 27.8434C23.1708 27.8434 25.5123 27.2016 26.2407 27.0257C26.9691 26.8498 27.8498 26.7107 27.8498 26.7107C27.8498 26.7107 29.9879 28.8619 32.0498 28.7858C34.1118 28.7096 34.012 27.5533 33.9989 27.4273" fill="#DD2025"></path>\
                            <path d="M31.4397 2.72607V10.4344H38.833L31.4397 2.72607Z" fill="#909090"></path>\
                            <path d="M31.5408 2.625V10.3333H38.9341L31.5408 2.625Z" fill="#F4F4F4"></path>\
                            <path d="M11.7797 5.84982H10.0642V12.1498H11.4187V10.0262L11.718 10.0433C12.0075 10.0383 12.2943 9.98642 12.5672 9.8897C12.8064 9.80737 13.0265 9.67745 13.2142 9.50776C13.4038 9.34565 13.553 9.14164 13.65 8.91189C13.7816 8.52929 13.8286 8.12268 13.7878 7.72014C13.7796 7.43258 13.7292 7.14778 13.6382 6.87489C13.5553 6.67789 13.4324 6.5003 13.2771 6.35342C13.1219 6.20654 12.9378 6.09359 12.7365 6.02176C12.5617 5.95815 12.381 5.91198 12.1971 5.88395C12.0585 5.86257 11.9186 5.85116 11.7784 5.84982H11.7797ZM11.5303 8.8607H11.4135V6.9182H11.6681C11.7799 6.91014 11.8921 6.9273 11.9964 6.96842C12.1006 7.00954 12.1943 7.07356 12.2706 7.15576C12.4285 7.36709 12.5128 7.62433 12.5107 7.88814C12.5107 8.21101 12.5107 8.5037 12.2194 8.70976C12.0095 8.82521 11.7705 8.8772 11.5316 8.85939" fill="white"></path>\
                            <path d="M16.3486 5.83277C16.203 5.83277 16.0612 5.84327 15.9615 5.8472L15.653 5.85508H14.6293V12.1551H15.8341C16.2946 12.1677 16.7531 12.0897 17.1834 11.9254C17.5298 11.788 17.8365 11.5665 18.0759 11.281C18.3087 10.9928 18.4758 10.6573 18.5655 10.2979C18.6686 9.89085 18.7189 9.47222 18.7151 9.05233C18.7405 8.55641 18.7022 8.05928 18.6009 7.57314C18.5048 7.21531 18.3248 6.88551 18.0759 6.61108C17.8806 6.38948 17.6415 6.21073 17.3737 6.08608C17.1437 5.97966 16.9018 5.90122 16.6531 5.85245C16.5543 5.83612 16.4541 5.82865 16.3539 5.83014L16.3486 5.83277ZM16.115 10.9975H15.9838V6.97595H16.0008C16.2714 6.94482 16.5452 6.99364 16.7883 7.11639C16.9664 7.25857 17.1115 7.43769 17.2136 7.64139C17.3238 7.85577 17.3873 8.09106 17.4 8.33177C17.4118 8.62052 17.4 8.85677 17.4 9.05233C17.4053 9.2776 17.3908 9.50291 17.3566 9.72564C17.3162 9.95432 17.2414 10.1756 17.1348 10.3819C17.0142 10.5737 16.8512 10.7354 16.6584 10.8544C16.4965 10.9591 16.3047 11.008 16.1124 10.9935" fill="white"></path>\
                            <path d="M22.7758 5.85507H19.5864V12.1551H20.9356V9.65607H22.6419V8.48532H20.9356V7.02582H22.7731V5.85507" fill="white"></path>\
                            </svg></div>\
                            <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
                            <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                            <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                            ' +
            get_doc_path_html(attached_file_src) +
            '\
                            </div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                        </div>\
                    </div>";
    } else if (is_txt(attached_file_src)) {
        html =
            '<div class="live-chat-agent-message-wrapper" id=' + message_id + '>\
                            <div class="live-chat-agent-image">' +
            get_user_initial(sender_name) +
            "</div>" +
            sender_name_html +
            message_bubble +
            '<div style="    width: 50px; height: 45px; display: inline-block;"><svg width="32" height="42" viewBox="0 0 32 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M9.1875 18.375C8.8394 18.375 8.50556 18.5133 8.25942 18.7594C8.01328 19.0056 7.875 19.3394 7.875 19.6875C7.875 20.0356 8.01328 20.3694 8.25942 20.6156C8.50556 20.8617 8.8394 21 9.1875 21H22.3125C22.6606 21 22.9944 20.8617 23.2406 20.6156C23.4867 20.3694 23.625 20.0356 23.625 19.6875C23.625 19.3394 23.4867 19.0056 23.2406 18.7594C22.9944 18.5133 22.6606 18.375 22.3125 18.375H9.1875ZM7.875 24.9375C7.875 24.5894 8.01328 24.2556 8.25942 24.0094C8.50556 23.7633 8.8394 23.625 9.1875 23.625H22.3125C22.6606 23.625 22.9944 23.7633 23.2406 24.0094C23.4867 24.2556 23.625 24.5894 23.625 24.9375C23.625 25.2856 23.4867 25.6194 23.2406 25.8656C22.9944 26.1117 22.6606 26.25 22.3125 26.25H9.1875C8.8394 26.25 8.50556 26.1117 8.25942 25.8656C8.01328 25.6194 7.875 25.2856 7.875 24.9375ZM7.875 30.1875C7.875 29.8394 8.01328 29.5056 8.25942 29.2594C8.50556 29.0133 8.8394 28.875 9.1875 28.875H14.4375C14.7856 28.875 15.1194 29.0133 15.3656 29.2594C15.6117 29.5056 15.75 29.8394 15.75 30.1875C15.75 30.5356 15.6117 30.8694 15.3656 31.1156C15.1194 31.3617 14.7856 31.5 14.4375 31.5H9.1875C8.8394 31.5 8.50556 31.3617 8.25942 31.1156C8.01328 30.8694 7.875 30.5356 7.875 30.1875Z" fill="black"/>\
                                <path d="M19.6875 0H5.25C3.85761 0 2.52226 0.553124 1.53769 1.53769C0.553123 2.52226 0 3.85761 0 5.25V36.75C0 38.1424 0.553123 39.4777 1.53769 40.4623C2.52226 41.4469 3.85761 42 5.25 42H26.25C27.6424 42 28.9777 41.4469 29.9623 40.4623C30.9469 39.4777 31.5 38.1424 31.5 36.75V11.8125L19.6875 0ZM19.6875 2.625V7.875C19.6875 8.91929 20.1023 9.92081 20.8408 10.6592C21.5792 11.3977 22.5807 11.8125 23.625 11.8125H28.875V36.75C28.875 37.4462 28.5984 38.1139 28.1062 38.6062C27.6139 39.0984 26.9462 39.375 26.25 39.375H5.25C4.55381 39.375 3.88613 39.0984 3.39384 38.6062C2.90156 38.1139 2.625 37.4462 2.625 36.75V5.25C2.625 4.55381 2.90156 3.88613 3.39384 3.39384C3.88613 2.90156 4.55381 2.625 5.25 2.625H19.6875Z" fill="black"/>\
                                </svg></div>\
                                <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
                                <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                                <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                                ' +
            get_doc_path_html(attached_file_src) +
            '\
                                </div>\
                            </div>\
                            <div class="live-chat-agent-message-time">\
                                ' +
            time +
            "\
                                " +
            blue_ticks +
            "\
                            </div>\
                        </div>";
    } else if (is_docs(attached_file_src)) {
        html =
            '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                        <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            "</div>" +
            sender_name_html +
            message_bubble +
            '<div style="    width: 50px; height: 45px; display: inline-block;">\
                        <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                            <path d="M37.8079 3.9375H12.7378C12.5324 3.93733 12.3289 3.97763 12.139 4.05609C11.9491 4.13455 11.7766 4.24965 11.6312 4.39481C11.4858 4.53996 11.3704 4.71233 11.2916 4.90208C11.2128 5.09183 11.1722 5.29524 11.172 5.50069V12.4688L25.7001 16.7344L39.375 12.4688V5.50069C39.3748 5.29513 39.3341 5.09161 39.2553 4.90178C39.1764 4.71194 39.0609 4.53951 38.9154 4.39434C38.7698 4.24917 38.5971 4.1341 38.4071 4.05571C38.2171 3.97733 38.0134 3.93716 37.8079 3.9375Z" fill="#41A5EE"/>\
                            <path d="M39.375 12.4688H11.172V21L25.7001 23.5594L39.375 21V12.4688Z" fill="#2B7CD3"/>\
                            <path d="M11.172 21V29.5312L24.8456 31.2375L39.375 29.5312V21H11.172Z" fill="#185ABD"/>\
                            <path d="M12.7378 38.0625H37.8066C38.0122 38.063 38.216 38.023 38.4062 37.9447C38.5964 37.8664 38.7692 37.7513 38.9149 37.6061C39.0606 37.4609 39.1762 37.2884 39.2552 37.0985C39.3341 36.9086 39.3748 36.705 39.375 36.4993V29.5312H11.172V36.4993C11.1722 36.7048 11.2128 36.9082 11.2916 37.0979C11.3704 37.2877 11.4858 37.46 11.6312 37.6052C11.7766 37.7504 11.9491 37.8654 12.139 37.9439C12.3289 38.0224 12.5324 38.0627 12.7378 38.0625Z" fill="#103F91"/>\
                            <path opacity="0.1" d="M21.5696 10.7625H11.172V32.0906H21.5696C21.9839 32.0886 22.3808 31.9234 22.6741 31.6308C22.9674 31.3382 23.1336 30.9418 23.1368 30.5275V12.3257C23.1336 11.9114 22.9674 11.515 22.6741 11.2224C22.3808 10.9298 21.9839 10.7646 21.5696 10.7625Z" fill="black"/>\
                            <path opacity="0.2" d="M20.7152 11.6156H11.172V32.9438H20.7152C21.1295 32.9417 21.5263 32.7765 21.8196 32.4839C22.113 32.1913 22.2792 31.7949 22.2823 31.3806V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                            <path opacity="0.2" d="M20.7152 11.6156H11.172V31.2375H20.7152C21.1295 31.2354 21.5263 31.0702 21.8196 30.7776C22.113 30.485 22.2792 30.0886 22.2823 29.6743V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                            <path opacity="0.2" d="M19.8607 11.6156H11.172V31.2375H19.8607C20.2751 31.2354 20.6719 31.0702 20.9652 30.7776C21.2585 30.485 21.4248 30.0886 21.4279 29.6743V13.1788C21.4248 12.7645 21.2585 12.3681 20.9652 12.0755C20.6719 11.7829 20.2751 11.6177 19.8607 11.6156Z" fill="black"/>\
                            <path d="M4.19212 11.6156H19.8608C20.2758 11.6153 20.674 11.7797 20.9679 12.0729C21.2617 12.366 21.4272 12.7638 21.4279 13.1788V28.8212C21.4272 29.2362 21.2617 29.634 20.9679 29.9272C20.674 30.2203 20.2758 30.3847 19.8608 30.3844H4.19212C3.98656 30.3847 3.78295 30.3446 3.59291 30.2662C3.40288 30.1878 3.23016 30.0727 3.08462 29.9275C2.93909 29.7824 2.82358 29.6099 2.74472 29.4201C2.66585 29.2303 2.62517 29.0268 2.625 28.8212V13.1788C2.62517 12.9733 2.66585 12.7697 2.74472 12.5799C2.82358 12.3901 2.93909 12.2176 3.08462 12.0725C3.23016 11.9273 3.40288 11.8122 3.59291 11.7338C3.78295 11.6555 3.98656 11.6153 4.19212 11.6156Z" fill="url(#paint0_linear)"/>\
                            <path d="M9.05627 23.6093C9.08645 23.8508 9.10745 24.0608 9.11664 24.2406H9.15339C9.16651 24.0699 9.19539 23.8639 9.2387 23.6237C9.28201 23.3835 9.32008 23.1801 9.35551 23.0134L11.0027 15.9167H13.1342L14.8405 22.9071C14.9398 23.3395 15.0109 23.7779 15.0531 24.2196H15.082C15.1133 23.7896 15.1725 23.3622 15.2591 22.9399L16.6228 15.9075H18.5614L16.1674 26.0768H13.9007L12.2771 19.3489C12.2299 19.1546 12.1765 18.9018 12.117 18.5903C12.0575 18.2788 12.0208 18.0513 12.0068 17.9078H11.9792C11.9608 18.0731 11.9241 18.3186 11.869 18.6441C11.8138 18.9709 11.7705 19.2111 11.7377 19.3686L10.2113 26.0807H7.90652L5.49939 15.9167H7.46814L8.95258 23.0278C8.99688 23.2198 9.03149 23.4138 9.05627 23.6093Z" fill="white"/>\
                            <defs>\
                            <linearGradient id="paint0_linear" x1="5.89837" y1="10.3871" x2="18.1545" y2="31.6129" gradientUnits="userSpaceOnUse">\
                            <stop stop-color="#2368C4"/>\
                            <stop offset="0.5" stop-color="#1A5DBE"/>\
                            <stop offset="1" stop-color="#1146AC"/>\
                            </linearGradient>\
                            </defs>\
                        </svg>\
                            </div>\
                            <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
            attached_file_src.split("/")[len - 1] +
            '</span><br>\
                        <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                        <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                        ' +
            get_doc_path_html(attached_file_src) +
            '\
                        </div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                        </div>\
                    </div>";
    } else if (is_image(attached_file_src)) {
        if (is_guest_agent_message)
            message_bubble =
            '<div class="live-chat-client-message-bubble-image-attachment live-chat-client-message-bubble-blue-border">';
        else
            message_bubble =
            '<div class="live-chat-client-message-bubble-image-attachment">';
        html =
            '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            "</div>" +
            sender_name_html +
            message_bubble +
            get_image_path_html(attached_file_src, thumbnail_url) +
            '\
                        <div class="file-attach-name-area">\
                            <h5 id="custom-text-attach-img">' +
            attached_file_src.split("/")[len - 1] +
            '</h5>\
                            <a href="' +
            attached_file_src +
            '" target="_blank" download><span style="position: absolute; top: 0.6rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>\
                                <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>\
                                <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>\
                                <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>\
                                <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>\
                                </svg>\
                                </span></a>\
                        </div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                            </div>\
                    </div>";
    } else if (is_video(attached_file_src)) {
        if (is_guest_agent_message)
            message_bubble =
            '<div class="live-chat-client-message-bubble-image-attachment live-chat-client-message-bubble-blue-border">';
        else
            message_bubble =
            '<div class="live-chat-client-message-bubble-image-attachment">';

        html =
            '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-client-image">' +
            get_user_initial(sender_name) +
            "</div>" +
            sender_name_html +
            message_bubble +
            get_video_path_html(attached_file_src) +
            '\
                        <div class="file-attach-name-area">\
                            <h5 id="custom-text-attach-img">' +
            attached_file_src.split("/")[len - 1] +
            '</h5>\
                            <a href="' +
            attached_file_src +
            '" target="_blank" download><span style="position: absolute; top: 0.6rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>\
                                <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>\
                                <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>\
                                <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>\
                                <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>\
                                </svg>\
                                </span></a>\
                        </div></div>\
                        <div class="live-chat-client-message-time">\
                            ' +
            time +
            "\
                            </div>\
                    </div>";
    }

    return html;
}

function save_customer_chat() {
    var json_string = JSON.stringify({
        message: "Customer left the chat",
        sender: "System",
        attached_file_src: "",
        thumbnail_url: "",
        session_id: get_session_id(),
        ended_by_customer: true,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-agent-chat/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = this.response;
            response = JSON.parse(response);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200 || response["status"] == "200") {
                console.log("customer chat ender and saved");
            }
        }
    };
    xhttp.send(params);
}

function clear_user_data() {
    save_customer_chat();
    var json_string = JSON.stringify({
        user_id: state.chat_data.easychat_user_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", CLEAR_API_URL, true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            console.log("clear data");
        }
    };
    xhttp.send(params);
}

var timer_to_hide_typing;

function show_customer_typing_in_chat(sender) {
    clearTimeout(timer_to_hide_typing);
    timer_to_hide_typing = setTimeout(hide_customer_typing_in_chat, 2000);

    const elem = document.getElementById("livechat-customer-typing");

    if (sender) {
        elem.innerHTML = `<p>${sender} is typing...</p>`;
    } else {
        elem.innerHTML = `<p>Typing...</p>`;
    }
}

function hide_customer_typing_in_chat() {
    const elem = document.getElementById("livechat-customer-typing");
    elem.innerHTML = ``;
}

function append_livechat_category() {
    show_preloader();

    var json_string = JSON.stringify({
        bot_id: state.chat_data.bot_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-livechat-category/", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status_code"] == "200") {
                let category_list = response["category_list"];

                var value = "-1";

                $("#modal-content-category-switch-selected").css(
                    "height",
                    "fit-content"
                );
                document.getElementById("category-switch-selected").innerHTML =
                    "";
                newOption = new Option("Choose one", "", false, false);
                $("#category-switch-selected")
                    .append(newOption)
                    .trigger("change");

                for (var i = 0; i < category_list.length; i++) {
                    var newOption = new Option(
                        category_list[i]["title"],
                        category_list[i]["pk"],
                        false,
                        false
                    );
                    $("#category-switch-selected")
                        .append(newOption)
                        .trigger("change");
                }
            }
            hide_preloader();
        }
    };
    xhttp.send(params);
}

function append_category_for_group_chat() {
    show_preloader();

    var json_string = JSON.stringify({
        bot_id: state.chat_data.bot_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-livechat-category/", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status_code"] == "200") {
                let category_list = response["category_list"];

                var value = "-1";

                $("#modal-content-category-switch-selected").css(
                    "height",
                    "fit-content"
                );
                document.getElementById(
                    "add-agent-category-switch-selected"
                ).innerHTML = "";
                newOption = new Option("Choose one", "", false, false);
                $("#add-agent-category-switch-selected")
                    .append(newOption)
                    .trigger("change");

                for (var i = 0; i < category_list.length; i++) {
                    var newOption = new Option(
                        category_list[i]["title"],
                        category_list[i]["pk"],
                        false,
                        false
                    );
                    $("#add-agent-category-switch-selected")
                        .append(newOption)
                        .trigger("change");
                }
            }
            hide_preloader();
        }
    };
    xhttp.send(params);
}

function append_livechat_agents(selected_category) {
    show_preloader();
    var json_string = JSON.stringify({
        selected_category: selected_category,
        bot_id: state.chat_data.bot_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-livechat-agents/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                let agent_list = response["agent_list"];
                let current_agent_pk = response["current_agent_pk"];

                var value = "-1";
                var newOption = null;

                document.getElementById("list-of-all-agents").innerHTML = "";
                newOption = new Option("Choose one", "", false, false);
                $("#list-of-all-agents").append(newOption).trigger("change");
                newOption = new Option("Auto assign", "-1", false, false);
                $("#list-of-all-agents").append(newOption).trigger("change");
                for (var i = 0; i < agent_list.length; i++) {
                    if (current_agent_pk != agent_list[i]["pk"]) {
                        newOption = new Option(
                            agent_list[i]["name"] +
                            " (" +
                            agent_list[i]["username"] +
                            ") ",
                            agent_list[i]["pk"],
                            false,
                            false
                        );
                    }
                    $("#list-of-all-agents")
                        .append(newOption)
                        .trigger("change");
                }
            }
            hide_preloader();
        }
    };
    xhttp.send(params);
}

function append_agents_for_group_chat(selected_category) {
    show_preloader();
    var json_string = JSON.stringify({
        selected_category: selected_category,
        bot_id: state.chat_data.bot_id,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/get-agents-group-chat/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                let agent_list = response["agent_list"];
                let current_agent_pk = response["current_agent_pk"];
                render_guest_agents_data(agent_list, current_agent_pk);
            }
            hide_preloader();
        }
    };
    xhttp.send(params);
}

function render_guest_agents_data(agent_list, current_agent_pk) {
    var guest_agents_container = document.getElementById(
        "add-agent-list-of-all-agents"
    );
    guest_agents_container.innerHTML = "";
    var is_agent_list_null = true;

    for (var i = 0; i < agent_list.length; i++) {
        if (current_agent_pk != agent_list[i]["pk"]) {
            is_agent_list_null = false;
            document.getElementById(
                "livechat-add-guest-agent-container"
            ).style.pointerEvents = "all";

            var agent_input =
                '<input type="checkbox" style="width: 10% !important;height: 0.8rem !important " class="item-checkbox guest-agent-input" name="agent-checkbox" value="' +
                agent_list[i]["pk"] +
                '" id="agent_' +
                agent_list[i]["pk"] +
                '"><span class="checkmark"></span>';
            if (agent_list[i]["session_ids"].includes(get_session_id())) {
                agent_input =
                    '<input type="checkbox" style="width: 10% !important;height: 0.8rem !important " class="item-checkbox guest-agent-input" name="agent-checkbox" value="' +
                    agent_list[i]["pk"] +
                    '" id="agent_' +
                    agent_list[i]["pk"] +
                    '" checked disabled ><span class="checkmark"></span>';
            }

            var html =
                '<label for="agent_' +
                agent_list[i]["pk"] +
                '" style="margin: 0px; display: block;">\
                            <div class="option agent-option">\
                                <p>' +
                agent_list[i]["name"] +
                "( " +
                agent_list[i]["username"] +
                ")</p>" +
                agent_input +
                "</div>\
                        </label>";

            guest_agents_container.innerHTML += html;
        }
    }

    if (!is_agent_list_null) {
        guest_agents_container.innerHTML +=
            '<div class="no-elem" id="agent-not-found-div" style="display: none;">No such agent found</div>';
        state.agent_options_list = document.querySelectorAll(
            ".livechat-add-agent-container .option"
        );
        state.agent_check_list = document.querySelectorAll(
            ".livechat-add-agent-container .item-checkbox"
        );
        render_guest_agent_checkboxes(state.agent_check_list);
        $(":checkbox[name='agent-checkbox']").change(handle_checked_agents);
        handle_checked_agents();
    } else {
        document.getElementById(
            "livechat-add-guest-agent-container"
        ).style.pointerEvents = "none";
    }
}

function render_guest_agent_checkboxes(check_list) {
    $(check_list).each(function() {
        $(this).change(function() {
            if ($(this).is(":checked")) {
                $("#livechat-agent-list-area")
                    .append(`<div id="agent_${this.id}" class="livechat-agent-list-item">    
            <div class="livechat-agent-list-name-area">
                ${this.previousElementSibling.innerText}
            </div>

            <div class="livechat-agent-list-delete-icon">
                <svg class="remove-tentative-member" width="22" height="22" viewBox="0 0 25 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.0885 5.70999C18.9017 5.52273 18.6481 5.4175 18.3835 5.4175C18.119 5.4175 17.8654 5.52273 17.6785 5.70999L12.7885 10.59L7.89854 5.69999C7.71171 5.51273 7.45806 5.4075 7.19354 5.4075C6.92903 5.4075 6.67538 5.51273 6.48854 5.69999C6.09854 6.08999 6.09854 6.71999 6.48854 7.10999L11.3785 12L6.48854 16.89C6.09854 17.28 6.09854 17.91 6.48854 18.3C6.87854 18.69 7.50854 18.69 7.89854 18.3L12.7885 13.41L17.6785 18.3C18.0685 18.69 18.6985 18.69 19.0885 18.3C19.4785 17.91 19.4785 17.28 19.0885 16.89L14.1985 12L19.0885 7.10999C19.4685 6.72999 19.4685 6.08999 19.0885 5.70999Z" fill="black" fill-opacity="0.54"></path>
                </svg>
            </div>

        </div>`);

                handle_delete_items_from_agent_list();
            } else {
                $(`#agent_${this.id}`).remove();
            }
        });
    });
}

function handle_checked_agents() {
    if (
        $(":checkbox[name='agent-checkbox']:checked").length ==
        get_max_guest_agent()
    ) {
        $(":checkbox:not(:checked)").prop("disabled", true);
    } else {
        $(":checkbox:not(:checked)").prop("disabled", false);
    }
}

function handle_delete_items_from_agent_list() {
    $(".livechat-agent-list-delete-icon").click(function() {
        $(this).parent().remove();
        const id_of_parent_checkbox = $(this).parent().attr("id").substr(6);
        $("#" + id_of_parent_checkbox).prop("checked", false);

        handle_checked_agents();
    });
}

function open_request_status_modal() {
    $("#livechat-request-status-modal").modal("show");
}

function guest_agent_filter_list(search_term) {
    search_term = search_term.toLowerCase();
    let flag = 0;
    var agent_not_found_div = document.getElementById("agent-not-found-div");

    if (agent_not_found_div) {
        agent_not_found_div.style.display = "none";
    }

    state.agent_options_list.forEach((option) => {
        let label = option.firstElementChild.innerText.toLowerCase();

        if (label.indexOf(search_term) != -1) {
            flag = 1;
            option.style.display = "block";
        } else {
            option.style.display = "none";
        }
    });
    if (flag === 0) {
        if (agent_not_found_div) {
            agent_not_found_div.style.display = "block";
        }
    }
}

$(document).on("change", "#category-switch-selected", function(e) {
    var selected_category = $("#category-switch-selected").val();
    if (selected_category == "") {
        $("#modal-content-category-switch-selected").css(
            "height",
            "fit-content"
        );
        document.getElementById("transfer-chat-submit").style.display = "none";
        document.getElementById("list-of-all-agents").innerHTML = "";
        var newOption = new Option("Choose one", "", false, false);
        $("#list-of-all-agents").append(newOption).trigger("change");
        $("#list-of-all-agents-div").hide();
    } else {
        $("#modal-content-category-switch-selected").css(
            "height",
            "fit-content"
        );
        $("#list-of-all-agents-div").show();
        document.getElementById("list-of-all-agents").innerHTML = "";
        var newOption = new Option("Choose one", "", false, false);
        $("#list-of-all-agents").append(newOption).trigger("change");
        append_livechat_agents(selected_category);
        document.getElementById("transfer-chat-submit").style.display =
            "inline-block";
        try {
            if (is_mobile() == false) {
                // $('#list-of-all-agents').select2({
                //     dropdownParent: $('#transfer-chat'),
                //     dropdownPosition: 'below'
                // });
            } else {
                // $('#list-of-all-agents').select2({
                //     dropdownParent: $('#transfer-chat-div'),
                //     dropdownPosition: 'below'
                // });
            }
        } catch (err) {
            console.log(err);
        }
    }
});

$(document).on("change", "#add-agent-category-switch-selected", function(e) {
    var selected_category = $("#add-agent-category-switch-selected").val();
    document.getElementById("livechat-agent-list-area").innerHTML = "";
    if (selected_category == "") {
        $("#modal-content-category-switch-selected").css(
            "height",
            "fit-content"
        );
        document.getElementById("add-agent-submit").style.display = "none";
        document.getElementById("add-agent-list-of-all-agents").innerHTML = "";
    } else {
        $("#modal-content-category-switch-selected").css(
            "height",
            "fit-content"
        );
        document.getElementById("add-agent-list-of-all-agents").innerHTML = "";
        append_agents_for_group_chat(selected_category);
        document.getElementById("add-agent-submit").style.display =
            "inline-block";
    }
});

function transfer_chat_to_another_agent() {
    var selected_category = "-1";

    var category_dropdown = document.getElementById("category-switch-selected");
    if (category_dropdown != null && category_dropdown != undefined) {
        selected_category = category_dropdown.value;
    }

    var selected_agent = $("#list-of-all-agents").val();
    if (selected_agent == "") {
        showToast("Please select a valid option.", 5000);
        return;
    }
    transfer_chat_modal_close();

    const session_id = get_session_id();
    const cust_last_app_time = localStorage.getItem(
        `cust_last_app_time_${session_id}`
    );

    var json_string = JSON.stringify({
        selected_category: selected_category,
        selected_agent: selected_agent,
        bot_pk: state.chat_data.bot_id,
        session_id: get_session_id(),
        cust_last_app_time: cust_last_app_time,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/transfer-chat/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token); 
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                set_session_id(response.session_id);
                const new_agent_websocket_token =
                    response["new_agent_websocket_token"];
                showToast("Chat transfered!", 2000);
                let message =
                    response["assigned_agent"] + " has joined the chat.";
                let message_to_customer = response['message_to_customer']

                let message_history = get_message_history_store();
                let chat_info = get_chat_info_store();
                let customer_details = get_customer_details_store();

                delete_messages_from_local(message_history.name);
                delete_messages_from_local(chat_info.name);
                delete_messages_from_local(customer_details.name);

                const session_id = get_session_id();
                let message_id = save_system_message(message, "CHAT_TRANSFERRED", session_id);

                message = JSON.stringify({
                    message: JSON.stringify({
                        text_message_customer: message_to_customer,
                        type: "text",
                        channel: state.chat_data.channel,
                        path: "",
                        event_type: "CHAT_TRANSFERRED",
                        session_id: session_id,
                        new_agent_websocket_token: new_agent_websocket_token,
                        message_id: message_id,
                    }),
                    sender: "System",
                });
                send_message_to_socket(message);
                update_customer_list();
                go_to_chat(session_id, true);
                remove_inactivity_timer(session_id);
            } else {
                showToast(
                    "Unable to transfer-chat due to unavailability of agents.",
                    3000
                );
            }

            $("#transfer-chat").modal("hide");
        }
    };
    xhttp.send(params);
}

function invite_guest_agent_to_chat() {
    var selected_category = "-1";

    var category_dropdown = document.getElementById(
        "add-agent-category-switch-selected"
    );
    if (category_dropdown != null && category_dropdown != undefined) {
        selected_category = category_dropdown.value;
    }

    var guest_agents = [];
    var selected_agent = $("#add-agent-list-of-all-agents").val();
    var guest_agent_checkboxes =
        document.querySelectorAll(".guest-agent-input");

    for (let i = 0; i < guest_agent_checkboxes.length; i++) {
        if (guest_agent_checkboxes[i].checked) {
            guest_agents.push(guest_agent_checkboxes[i].value);
        }
    }

    if (guest_agents.length == 0) {
        showToast("Please select a valid option.", 5000);
        return;
    }
    add_agent_modal_close();

    const session_id = get_session_id();
    const cust_last_app_time = localStorage.getItem(
        `cust_last_app_time_${session_id}`
    );

    var json_string = JSON.stringify({
        selected_category: selected_category,
        guest_agents: guest_agents,
        bot_pk: state.chat_data.bot_id,
        session_id: get_session_id(),
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/invite-guest-agent/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status_code"] == "200") {
                //Checking unavailable agents and showing relevant toast
                var guest_agents_data = response["guest_agents_data"];
                var unavailable_agents = "";
                var agent_pending_list = [];
                for (let i = 0; i < guest_agents_data.length; i++) {
                    if (guest_agents_data[i][0]["status"] == "unavailable") {
                        unavailable_agents +=
                            " " + guest_agents_data[i][0]["name"];
                    } else {
                        // initializing timer once request is sent to guest agent
                        localStorage.setItem(
                            `guest_agent_timer-${guest_agents_data[i][0]["username"]}-${session_id}`,
                            get_guest_agent_timer()
                        );

                        agent_pending_list.push(
                            guest_agents_data[i][0]["username"]
                        );
                    }
                }
                set_agent_pending_list(agent_pending_list);

                if (unavailable_agents != "") {
                    showToast(
                        unavailable_agents + " is/are unavailable.",
                        5000
                    );
                }

                //guest session initiated by primary agent
                document.getElementById(
                    "primary-guest-agent-status"
                ).style.display = "block";
                localStorage.setItem("is_guest_session-" + session_id, "true");

                $("#agent-request-sent-success-modal").modal("show");
                setTimeout(function() {
                    $("#agent-request-sent-success-modal").modal("hide");
                }, 2000);
                document.getElementById(
                    "livechat-transfer-chat-btn"
                ).style.pointerEvents = "none";
                document.getElementById(
                    "livechat-transfer-chat-btn"
                ).style.cursor = "default";
                document.getElementById(
                    "livechat-transfer-chat-btn"
                ).style.opacity = "0.3";

                let message =
                    get_agent_name() + " has requested to join the chat.";

                message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: message,
                        agent_name: get_agent_name(),
                        type: "text",
                        channel: state.chat_data.channel,
                        path: "",
                        event_type: "GUEST_AGENT_JOIN_REQUEST",
                        session_id: session_id,
                        guest_agent_timer: response["guest_agent_timer"],
                    }),
                    sender: "System",
                });

                send_message_to_guest_agent_socket(message);
            } else {
                showToast("Unable to add agent!", 3000);
            }
        }
    };
    xhttp.send(params);
}

function show_preloader() {
    $("#preloader-transfer-chat-bot").show();
}

function hide_preloader() {
    $("#preloader-transfer-chat-bot").hide();
}

function transfer_chat_modal_open() {
    const session_id = get_session_id();

    const voip_info = get_voip_info();
    if (voip_info.request_status && voip_info.session_id == session_id && voip_info.request_status != 'none' && voip_info.request_status != 'rejected') {
        showToast("Please end the ongoing call.", 2000);
        return;
    }

    const cobrowsing_info = get_cobrowsing_info();
    if (cobrowsing_info.session_id == session_id && cobrowsing_info.status != 'none' && cobrowsing_info.status != 'rejected') {
        showToast("Please end the ongoing cobrowsing session.", 2000);
        return;
    }

    if (
        state.customer_left_chat[session_id] !== undefined &&
        state.customer_left_chat[session_id] == true
    ) {
        showToast("Customer has left the chat. Cannot Transfer Chat now", 2000);
    } else {
        $("#transfer-chat").modal("show");
        if (
            state.chat_data.category_enabled == "False" ||
            state.chat_data.category_enabled == false
        ) {
            document.getElementById(
                "transfer-chat-category-div"
            ).style.display = "none";
            append_livechat_agents("-1");
        } else {
            append_livechat_category();
        }
    }
}

function add_agent_modal_open() {
    const session_id = get_session_id();

    // to remove the chips of previously selected agents
    document.getElementById("livechat-agent-list-area").innerHTML = "";

    if (
        state.customer_left_chat[session_id] !== undefined &&
        state.customer_left_chat[session_id] == true
    ) {
        showToast("Customer has left the chat. Cannot add agent now", 2000);
    } else {
        $("#add-agent-modal").modal("show");
        if (
            state.chat_data.category_enabled == "False" ||
            state.chat_data.category_enabled == false
        ) {
            document.getElementById("add-agent-category-div").style.display =
                "none";
            append_agents_for_group_chat("-1");
        } else {
            append_category_for_group_chat();
        }
    }
}

function transfer_chat_modal_close() {
    $("#transfer-chat").modal("hide");
    console.log("Chat Transferred");
}

function add_agent_modal_close() {
    $("#add-agent-modal").modal("hide");
}

function save_system_message(message, event_type, session_id, for_guest_agent = false) {

    let agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
    let customer_language = localStorage.getItem(`customer_language-${session_id}`);

    let to_translate_message = false;
    if(agent_preferred_language != customer_language) {
        to_translate_message = true;
    }

    var message_id = "";
    var json_string = {
        message: message,
        sender: "System",
        attached_file_src: "",
        thumbnail_url: "",
        session_id: session_id,
        to_translate_message: to_translate_message,
    };

    if (event_type == 'VOICE_CALL') {
        json_string['voice_call_notification'] = true;
    }
    
    if (event_type == 'VIDEO_CALL') {
        json_string['video_call_notification'] = true;
    }

    if (event_type == 'COBROWSING') {
        json_string['cobrowsing_notification'] = true;
    }

    if (event_type == 'CUSTOMER_WARNING_MESSAGE') {
        json_string['is_customer_warning_message'] = true;
    }

    if (event_type == 'CUSTOMER_REPORT_MESSAGE_NOTIF') {
        json_string['is_customer_report_message_notification'] = true;
    }

    if (event_type == 'WHATSAPP_REINITIATING_REQUEST') {
        json_string['sender_name'] = 'system';
        json_string['is_whatsapp_reinitiating_request'] = true;
    }

    if (for_guest_agent) {
        json_string['for_guest_agent'] = true;
    }
    
    if (event_type == 'INACTIVITY_CHAT') {
        json_string['inactivity_chat'] = true;
    }

    json_string = JSON.stringify(json_string);
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/save-agent-chat/", false);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                message_id = response["message_id"];
                console.log("chat send by system saved");
            }
        }
    };
    xhttp.send(params);

    if (
        event_type != "GUEST_AGENT_EXIT" &&
        event_type != "GUEST_AGENT_JOINED" &&
        event_type != "GUEST_AGENT_REJECT" &&
        event_type != "CHAT_RESOLVED_BY_AGENT" &&
        event_type != "CUSTOMER_WARNING_MESSAGE" &&
        event_type != "CUSTOMER_WARNING_MESSAGE_NOTIF" &&
        event_type != "CUSTOMER_REPORT_MESSAGE" &&
        event_type != "CUSTOMER_REPORT_MESSAGE_NOTIF"
    ) {
        var message = JSON.stringify({
            message: JSON.stringify({
                text_message: message,
                type: "text",
                channel: state.chat_data.channel,
                path: "",
                event_type: event_type,
                session_id: session_id,
                message_id: message_id,
            }),
            sender: "System",
        });
        send_message_to_socket(message);
    }

    return message_id;
}

function reverse_list(array) {
    return array.map((item, idx) => array[array.length - 1 - idx]);
}

function openHistory(session_id, chat_hist_agent_username = "") {
    set_chat_history_agent_username(chat_hist_agent_username);
    $(`#style-2-${session_id}`).animate({ scrollTop: 999999 }, 300);
}

function on_chat_history_div_scroll(
    elem,
    client_id,
    original_session_id,
    joined_date,
    audit_obj_active_url
) {

    var dateLabels = document.querySelectorAll(
        ".live-chat-message-day-time-div-" + original_session_id
    );
    let currentLabel = null;
    dateLabels.forEach((dateLabel) => {
        if (elem.scrollTop >= dateLabel.offsetTop - 10) {
            currentLabel = dateLabel;
        }
    });
    if (currentLabel) {
        indicator_date = currentLabel.innerHTML + "";
        if (indicator_date.trim() != "")
            $("#live-chat-indicator-" + original_session_id).html(
                indicator_date
            );
    } else {
        indicator_date = joined_date;
        if (indicator_date.trim() != "")
            $("#live-chat-indicator-" + original_session_id).html(
                indicator_date
            );
    }



    var child_to_be_focused = elem.firstChild;
    if (scrollTimeout === null) {
        scrollbeginHandler();
    } else {
        clearTimeout(scrollTimeout);
    }
    scrollTimeout = setTimeout(scrollendHandler, scrollendDelay);

    if ($(elem).scrollTop() == 0) {
        document.getElementById(
            "chat_loader-" + original_session_id
        ).style.display = "flex";
        var element = elem.getElementsByTagName("input");
        var cust_obj_pk = element[0].value;
        var html = "";

        var json_string = JSON.stringify({
            cust_obj_pk: cust_obj_pk,
            client_id: client_id,
        });

        json_string = EncryptVariable(json_string);
        var CSRF_TOKEN = getCsrfToken();

        $.ajax({
            url: "/livechat/get-previous-session-message/",
            type: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN
            },
            data: {
                json_string: json_string,
            },
            success: function(response) {
                response = custom_decrypt(response);
                response = JSON.parse(response);

                if (response["status_code"] == "300") {
                    try {
                        var top_fixed_element = document.getElementsByClassName(
                            "live-chat-message-day-time-div-" +
                            original_session_id
                        )[0];
                        if (
                            document.getElementById(
                                "load-more-chats-" + original_session_id
                            )
                        )
                            document
                            .getElementById(
                                "load-more-chats-" + original_session_id
                            )
                            .parentElement.remove();
                        if (fixed_date_string == "")
                            fixed_date_string = joined_date;
                        else {
                            var top_fixed_element =
                                document.getElementsByClassName(
                                    "live-chat-message-day-time-div-" +
                                    original_session_id
                                )[0];
                            if (top_fixed_element) {
                                fixed_date_string = top_fixed_element.innerHTML;
                            } else {
                                fixed_date_string = joined_date;
                            }
                        }

                        if (fixed_date_string.trim() != "") {
                            if (fixed_date_string == todays_date.trim()) {
                                fixed_date_html =
                                    '<div class="live-chat-message-day-time-div-' +
                                    original_session_id +
                                    '">' +
                                    "Today" +
                                    "</div>";
                            } else {
                                fixed_date_html =
                                    '<div class="live-chat-message-day-time-div-' +
                                    original_session_id +
                                    '">' +
                                    fixed_date_string +
                                    "</div>";
                            }

                            if (element[1].value == 0) {
                                $("#" + elem.id).prepend(fixed_date_html);
                                element[1].value = 1;
                            }
                            fixed_date_string = updated_date.trim();
                            fixed_date_html =
                                '<div class="live-chat-message-day-time-div-' +
                                original_session_id +
                                '" style="display: none">' +
                                fixed_date_string +
                                "</div>";
                            $("#" + elem.id).prepend(fixed_date_html);
                        }
                    } catch (err) {
                        console.log(err);
                    }

                    document.getElementById(
                        "chat_loader-" + original_session_id
                    ).style.display = "none";
                }
                if (response["status_code"] == "200") {
                    var message_list = response["message_list"];
                    message_list = reverse_list(message_list);
                    element[0].value = response["new_obj_pk"];
                    var cust_obj_active_url = response["cust_obj_active_url"];
                    var updated_date = response["updated_date"];
                    var appended = 0;
                    try {
                        if (fixed_date_string == "")
                            fixed_date_string = joined_date;
                        else {
                            var top_fixed_element =
                                document.getElementsByClassName(
                                    "live-chat-message-day-time-div-" +
                                    original_session_id
                                )[0];
                            if (top_fixed_element) {
                                fixed_date_string = top_fixed_element.innerHTML;
                            } else {
                                fixed_date_string = joined_date;
                            }
                        }

                        if (fixed_date_string.trim() != "") {
                            if (
                                updated_date.trim() != fixed_date_string.trim()
                            ) {
                                var fixed_date_html;
                                if (fixed_date_string == todays_date.trim()) {
                                    fixed_date_html =
                                        '<div class="live-chat-message-day-time-div-' +
                                        original_session_id +
                                        '">' +
                                        "Today" +
                                        "</div>";
                                } else {
                                    fixed_date_html =
                                        '<div class="live-chat-message-day-time-div-' +
                                        original_session_id +
                                        '">' +
                                        fixed_date_string +
                                        "</div>";
                                }

                                var elements = document.getElementsByClassName(
                                    "live-chat-message-day-time-div-" +
                                    original_session_id
                                );
                                if (elements.length > 1) {
                                    var elements =
                                        document.getElementsByClassName(
                                            "live-chat-message-day-time-div-" +
                                            original_session_id
                                        );
                                    elements[0].parentNode.removeChild(
                                        elements[0]
                                    );
                                }
                                $("#" + elem.id).prepend(fixed_date_html);
                                fixed_date_string = updated_date.trim();
                                fixed_date_html =
                                    '<div class="live-chat-message-day-time-div-' +
                                    original_session_id +
                                    '" style="display: none">' +
                                    fixed_date_string +
                                    "</div>";
                                $("#" + elem.id).prepend(fixed_date_html);
                            }
                        }
                    } catch (err) {
                        console.log(err);
                    }

                    for (var i = 0; i < message_list.length; i++) {
                        if (message_list[i]["sender"] == "Agent") {
                            if (message_list[i]["is_video_call_message"]) continue;
                            if (message_list[i].is_guest_agent_message) {
                                if (
                                    message_list[i][
                                        "attachment_file_path"
                                    ].trim() != ""
                                ) {
                                    html = append_file_to_agent_attach(
                                        message_list[i]["attachment_file_path"],
                                        message_list[i]["text_message"],
                                        message_list[i]["message_time"],
                                        message_list[i]["sender_name"],
                                        message_list[i]["sender"],
                                        cust_obj_pk,
                                        false,
                                        false,
                                        true,
                                        true,
                                        true
                                    );
                                    $(elem).prepend(html);
                                    appended = 1;
                                } else {
                                    html = prepend_customer_message(
                                        message_list[i]["text_message"],
                                        message_list[i]["sender_name"],
                                        message_list[i]["message_time"],
                                        cust_obj_pk,
                                        true,
                                        message_list[i]["message_id"],
                                        false,
                                    );
                                    $(elem).prepend(html);
                                    appended = 1;
                                }
                            } else {
                                if (
                                    message_list[i][
                                        "attachment_file_path"
                                    ].trim() != ""
                                ) {
                                    html = append_file_to_agent_attach(
                                        message_list[i]["attachment_file_path"],
                                        message_list[i]["text_message"],
                                        message_list[i]["message_time"],
                                        message_list[i]["sender_name"],
                                        message_list[i]["sender"],
                                        cust_obj_pk,
                                        false,
                                        false,
                                        true
                                    );
                                    $(elem).prepend(html);
                                    appended = 1;
                                } else {
                                    html = prepend_agent_message(
                                        message_list[i]["text_message"],
                                        message_list[i]["sender_name"][0],
                                        message_list[i]["message_time"],
                                        cust_obj_pk,
                                        message_list[i]["message_id"],
                                        false,
                                    );
                                    $(elem).prepend(html);
                                    appended = 1;
                                }
                            }
                        } else if (message_list[i]["sender"] == "Customer") {
                            if (
                                message_list[i][
                                    "attachment_file_path"
                                ].trim() != ""
                            ) {
                                html = append_file_to_agent_attach(
                                    message_list[i]["attachment_file_path"],
                                    message_list[i]["text_message"],
                                    message_list[i]["message_time"],
                                    message_list[i]["sender_name"],
                                    message_list[i]["sender"],
                                    cust_obj_pk,
                                    false,
                                    false,
                                    true,
                                    true,
                                    true
                                );
                                $(elem).prepend(html);
                                appended = 1;
                            } else {
                                html = prepend_customer_message(
                                    message_list[i]["text_message"],
                                    message_list[i]["sender_name"],
                                    message_list[i]["message_time"],
                                    cust_obj_pk,
                                    true,
                                    message_list[i]["message_id"],
                                    false,
                                );
                                $(elem).prepend(html);
                                appended = 1;
                            }
                        } else if (message_list[i]["sender"] == "System") {
                            if (message_list[i]["is_video_call_message"] || message_list[i]["is_cobrowsing_message"] || message_list[i]["is_voice_call_message"]) {
                                html = get_video_call_text_response(message_list[i]["text_message"]);
                            } else if (message_list[i]["text_message"].includes("Customer details updated") || message_list[i]["text_message"].includes("Reinitiating Request Sent")) {
                                html = `<div class="live-chat-customer-details-update-message-div">
                                                ${message_list[i]["text_message"]}
                                            </div>`;
                            } else if (message_list[i]["is_customer_warning_message"]) {
                                html = get_customer_warning_system_text_html(message_list[i]["text_message"]);
                            } else if (message_list[i]["is_customer_report_message_notification"]) {
                                html = get_report_message_notif_html(message_list[i]["text_message"]);
                            } else {
                                html = get_system_text_response_html(
                                    message_list[i]["text_message"],
                                    message_list[i]["message_time"]
                                );
                            }
                            $(elem).prepend(html);
                            appended = 1;
                        } else if (message_list[i]["sender"] == "Bot") {
                            html = prepend_agent_message(
                                message_list[i]["text_message"],
                                message_list[i]["sender_name"][0],
                                message_list[i]["message_time"],
                                cust_obj_pk,
                                message_list[i]["message_id"],
                                false,
                            );
                            $(elem).prepend(html);
                            appended = 1;
                        }
                    }

                    if (appended == 1) {
                        if (
                            child_to_be_focused != null &&
                            child_to_be_focused != undefined
                        ) {
                            if (child_to_be_focused.previousSibling) {
                                var scrollDiv =
                                    child_to_be_focused.previousSibling.offsetTop;
                                elem.scrollTo({ top: scrollDiv });
                            }
                        } // child_to_be_focused.previousSibling.scrollIntoView()
                        document.getElementById(
                            "chat_loader-" + original_session_id
                        ).style.display = "none";
                    }
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log(
                    "Please report this error: " +
                    errorthrown +
                    xhr.status +
                    xhr.responseText
                );
                show_custom_notification("Your chats might be loading slower than usual. We recommend that you reload the page, if the problem still persists.", 10000);
            },
            timeout: 5000
        });
    }
}

function on_chat_history_div_scroll_chat_area(
    elem,
    original_session_id,
    load_more_chats
) {
    var dateLabels = document.querySelectorAll(
        ".live-chat-message-day-time-div-" + original_session_id
    );
    let currentLabel = null;
    if (load_more_chats == "true") {
        elem = document.getElementById("style-2_" + original_session_id);
        document
            .getElementById("load-more-chats-" + original_session_id)
            .parentElement.remove();
    }
    dateLabels.forEach((dateLabel) => {
        if (elem.scrollTop >= dateLabel.offsetTop - 10) {
            currentLabel = dateLabel;
        }
    });

    if (currentLabel) {
        indicator_date = currentLabel.innerHTML + "";
        $("#live-chat-indicator-" + original_session_id).html(indicator_date);
    }

    var child_to_be_focused = elem.firstChild;
    if (scrollTimeout === null) {
        scrollbeginHandler();
    } else {
        clearTimeout(scrollTimeout);
    }
    scrollTimeout = setTimeout(scrollendHandler, scrollendDelay);
    if ($(elem).scrollTop() == 0 || load_more_chats == "true") {
        document.getElementById("chat_loader").style.display = "flex";
        var element = document.getElementById(
            "hidden_current_session_id_" + original_session_id
        );
        var top_reached = document.getElementById(
            "top_reached_" + original_session_id
        );
        var cust_obj_pk = element.value;
        var session_id = element.value;
        var html = "";
        var json_string = JSON.stringify({
            session_id: session_id,
        });
        json_string = EncryptVariable(json_string);
        var CSRF_TOKEN = getCsrfToken();
        $.ajax({
            url: "/livechat/get-previous-session-message/",
            type: "POST",
            headers: {
                "X-CSRFToken": CSRF_TOKEN
            },
            data: {
                json_string: json_string,
            },
            success: function(response) {
                response = custom_decrypt(response);
                response = JSON.parse(response);

                if (response["status_code"] == "300") {
                    try {
                        if (top_reached.value == 0) {
                            if (
                                document.getElementById(
                                    "load-more-chats-" + original_session_id
                                )
                            ) {
                                document
                                    .getElementById(
                                        "load-more-chats-" + original_session_id
                                    )
                                    .parentElement.remove();
                            }

                            if (load_more_chats == "true") {
                                showToast("No previous chat data", 2000);
                            }

                            top_reached.value = 1;
                            var fixed_date_html;
                            if (fixed_date_string.trim() != "") {
                                if (fixed_date_string == todays_date.trim()) {
                                    fixed_date_html =
                                        '<div class="live-chat-message-day-time-div-' +
                                        original_session_id +
                                        '">' +
                                        "Today" +
                                        "</div>";
                                } else {
                                    fixed_date_html =
                                        '<div class="live-chat-message-day-time-div-' +
                                        original_session_id +
                                        '">' +
                                        fixed_date_string +
                                        "</div>";
                                }

                                $("#" + elem.id).prepend(fixed_date_html);
                                fixed_date_string = updated_date.trim();
                                fixed_date_html =
                                    '<div class="live-chat-message-day-time-div-' +
                                    original_session_id +
                                    '" style="display: none">' +
                                    fixed_date_string +
                                    "</div>";
                                $("#" + elem.id).prepend(fixed_date_html);
                            }
                        }
                        document.getElementById("chat_loader").style.display =
                            "none";
                    } catch (err) {
                        document.getElementById("chat_loader").style.display =
                            "none";
                        console.log(err);
                    }
                }
                if (response["status_code"] == "200") {
                    var message_list = response["message_list"];
                    message_list = reverse_list(message_list);
                    element.value = response["new_obj_pk"];
                    var cust_obj_active_url = response["cust_obj_active_url"];
                    var updated_date = response["updated_date"];
                    var appended = 0;
                    try {
                        if (fixed_date_string.trim() != "") {
                            if (
                                updated_date.trim() != fixed_date_string.trim()
                            ) {
                                var fixed_date_html;
                                if (fixed_date_string == todays_date.trim()) {
                                    fixed_date_html =
                                        '<div class="live-chat-message-day-time-div-' +
                                        original_session_id +
                                        '">' +
                                        "Today" +
                                        "</div>";
                                } else {
                                    fixed_date_html =
                                        '<div class="live-chat-message-day-time-div-' +
                                        original_session_id +
                                        '">' +
                                        fixed_date_string +
                                        "</div>";
                                }

                                var elements = document.getElementsByClassName(
                                    "live-chat-message-day-time-div-" +
                                    original_session_id
                                );
                                if (elements.length > 1) {
                                    var elements =
                                        document.getElementsByClassName(
                                            "live-chat-message-day-time-div-" +
                                            original_session_id
                                        );
                                    elements[0].parentNode.removeChild(
                                        elements[0]
                                    );
                                }
                                $("#" + elem.id).prepend(fixed_date_html);
                                fixed_date_string = updated_date.trim();

                                fixed_date_html =
                                    '<div class="live-chat-message-day-time-div-' +
                                    original_session_id +
                                    '" style="display: none">' +
                                    fixed_date_string +
                                    "</div>";
                                $("#" + elem.id).prepend(fixed_date_html);
                            }
                        }
                    } catch (err) {
                        console.log(err);
                    }
                    for (var i = 0; i < message_list.length; i++) {
                        if (message_list[i]["sender"] == "Agent") {
                            if (message_list[i]["is_video_call_message"]) continue;
                            if (message_list[i].is_guest_agent_message) {
                                if (
                                    message_list[i][
                                        "attachment_file_path"
                                    ].trim() != ""
                                ) {
                                    html = append_file_to_agent_attach(
                                        message_list[i]["attachment_file_path"],
                                        message_list[i]["text_message"],
                                        message_list[i]["message_time"],
                                        message_list[i]["sender_name"],
                                        message_list[i]["sender"],
                                        cust_obj_pk,
                                        false,
                                        false,
                                        true,
                                        true,
                                        true
                                    );
                                    $("#" + elem.id).prepend(html);
                                    appended = 1;
                                } else {
                                    html = prepend_customer_message(
                                        message_list[i]["text_message"],
                                        message_list[i]["sender_name"],
                                        message_list[i]["message_time"],
                                        cust_obj_pk,
                                        true,
                                        message_list[i]["message_id"],
                                        false
                                    );
                                    $("#" + elem.id).prepend(html);
                                    appended = 1;
                                }
                            } else {
                                {
                                    if (
                                        message_list[i][
                                            "attachment_file_path"
                                        ].trim() != ""
                                    ) {
                                        html = append_file_to_agent_attach(
                                            message_list[i][
                                                "attachment_file_path"
                                            ],
                                            message_list[i]["text_message"],
                                            message_list[i]["message_time"],
                                            message_list[i]["sender_name"],
                                            message_list[i]["sender"],
                                            cust_obj_pk,
                                            false,
                                            false,
                                            true
                                        );

                                        $("#" + elem.id).prepend(html);
                                        appended = 1;
                                    } else {
                                        html = prepend_agent_message(
                                            message_list[i]["text_message"],
                                            message_list[i]["sender_name"][0],
                                            message_list[i]["message_time"],
                                            cust_obj_pk,
                                            message_list[i]["message_id"],
                                            false
                                        );
                                        $("#" + elem.id).prepend(html);
                                        appended = 1;
                                    }
                                }
                            }
                        } else if (message_list[i]["sender"] == "Customer") {
                            if (
                                message_list[i][
                                    "attachment_file_path"
                                ].trim() != ""
                            ) {
                                html = append_file_to_agent_attach(
                                    message_list[i]["attachment_file_path"],
                                    message_list[i]["text_message"],
                                    message_list[i]["message_time"],
                                    message_list[i]["sender_name"],
                                    message_list[i]["sender"],
                                    cust_obj_pk,
                                    false,
                                    false,
                                    true
                                );
                                $("#" + elem.id).prepend(html);
                                appended = 1;
                            } else {
                                html = prepend_customer_message(
                                    message_list[i]["text_message"],
                                    message_list[i]["sender_name"],
                                    message_list[i]["message_time"],
                                    cust_obj_pk,
                                    false,
                                    message_list[i]["message_id"],
                                    false
                                );
                                $("#" + elem.id).prepend(html);
                                appended = 1;
                            }
                        } else if (message_list[i]["sender"] == "System") {
                            if (message_list[i]["is_video_call_message"] || message_list[i]["is_cobrowsing_message"] || message_list[i]["is_voice_call_message"]) {
                                html = get_video_call_text_response(message_list[i]["text_message"]);
                            } else if (message_list[i]["text_message"].includes("Customer details updated") || message_list[i]["text_message"].includes("Reinitiating Request Sent")) {
                                html = `<div class="live-chat-customer-details-update-message-div">
                                            ${message_list[i]["text_message"]}
                                        </div>`;
                            } else if (message_list[i]["is_customer_warning_message"]) {
                                html = get_customer_warning_system_text_html(message_list[i]["text_message"]);
                            } else if (message_list[i]["is_customer_report_message_notification"]) {
                                html = get_report_message_notif_html(message_list[i]["text_message"]);
                            } else {
                                html = get_system_text_response_html(
                                    message_list[i]["text_message"],
                                    message_list[i]["message_time"]
                                );
                            }
                            $("#" + elem.id).prepend(html);
                            appended = 1;
                        } else if (message_list[i]["sender"] == "Bot") {
                            html = prepend_agent_message(
                                message_list[i]["text_message"],
                                message_list[i]["sender_name"][0],
                                message_list[i]["message_time"],
                                cust_obj_pk,
                                message_list[i]["message_id"],
                                false
                            );
                            $("#" + elem.id).prepend(html);
                            appended = 1;
                        }

                        if (appended == 1) {
                            if (
                                child_to_be_focused != null &&
                                child_to_be_focused != undefined
                            ) {
                                if (child_to_be_focused.previousSibling) {
                                    var scrollDiv =
                                        child_to_be_focused.previousSibling
                                        .offsetTop;
                                    elem.scrollTo({ top: scrollDiv });
                                }
                            }
                            document.getElementById(
                                "chat_loader"
                            ).style.display = "none";
                            if (
                                document.getElementById(
                                    "load-more-chats-" + original_session_id
                                )
                            )
                                document
                                .getElementById(
                                    "load-more-chats-" + original_session_id
                                )
                                .parentElement.remove();
                        }
                    }
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                show_custom_notification("Your chats might be loading slower than usual. We recommend that you reload the page, if the problem still persists.", 10000);
                console.log(
                    "Please report this error: " +
                    errorthrown +
                    xhr.status +
                    xhr.responseText
                );
            },
            timeout: 5000
        });
    }
}


export function prepend_customer_message(message, sender_name, time = return_time(), pk, is_guest_agent_message = false, message_id = "", reply_private_container = true) {
    message = get_masked_message(message);
    message = stripHTML(message);
    message = livechat_linkify(message);
    message = message.trim();

    var reply_private_container = get_reply_private_html(reply_private_container, "client");

    var message_bubble = "";
    if (is_guest_agent_message)
        message_bubble = '<div class="live-chat-client-message-bubble live-chat-client-message-bubble-blue-border">'
    else
        message_bubble = '<div class="live-chat-client-message-bubble">'

    const html = '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                  <div class="live-chat-client-image">' + get_user_initial(sender_name) + '</div>\
                <div class="live-chat-client-name-with-message">' + sender_name +
        '</div>' +
        reply_private_container[0] +
        message_bubble +
        message +
        '</div>' +
        reply_private_container[1] +
        '<div class="live-chat-client-message-time">' + time + '</div>' +
        reply_private_container[2] +
        '</div>'

    return html;
}

export function prepend_agent_message(message, sender_initial, time = return_time(), pk, message_id = "", reply_private_container = true) {

    message = message.replace(new RegExp("\r?\n", "g"), "<br/>");
    message = livechat_linkify(message);
    message = message.trim();

    var reply_private_container = get_reply_private_html(reply_private_container, "agent");

    const html = `<div class="live-chat-agent-message-wrapper" id="${message_id}">
                  <div class="live-chat-agent-image">${sender_initial}</div>` +
        reply_private_container[0] +
        `<div class="live-chat-agent-message-bubble">
                    ${message}
                  </div>` +
        reply_private_container[1] +
        `<div class="live-chat-agent-message-time">
                    ${time}
                  </div>` +
        reply_private_container[2] +
        `</div>`

    return html;
}

export function append_file_to_agent_attach(
    attached_file_src,
    message,
    time = return_time(),
    sender_name,
    sender,
    pk,
    is_blue_tick = false,
    is_ongoing_chat = false,
    returnresponse = false,
    is_guest_agent_message = false,
    is_blue_border = false,
    message_id = "",
    reply_private_container = false,
) {
    var len = attached_file_src.split("/").length;
    let html = "";
    const icons = get_icons();
    var sender_name_html = "";
    var message_bubble = "";
    if (sender == "Customer" || (sender == "Agent" && is_guest_agent_message))
        sender_name_html =
        '<div class="live-chat-client-name-with-message">' +
        sender_name +
        "</div>";
    if (is_guest_agent_message && is_blue_border)
        message_bubble =
        '<div class="live-chat-client-message-bubble file-attachement-download live-chat-client-message-bubble-blue-border" style="margin-left: 0px">';
    else
        message_bubble =
        '<div class="live-chat-client-message-bubble file-attachement-download" style="margin-left: 0px">';
    var blue_ticks = "";

    if (is_ongoing_chat) {
        var blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path class="doubletick_livechat_agent-' +
            pk +
            '" d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                              <path class="doubletick_livechat_agent-' +
            pk +
            '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                              </svg>';

        if (is_blue_tick) {
            blue_ticks =
                '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                              <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                              </svg>';
        }
    }

    if (sender == "Customer" || (sender == "Agent" && is_guest_agent_message)) {
        var reply_private_container = get_reply_private_html(reply_private_container, "client");
        if (is_pdf(attached_file_src)) {
            html =
                '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                      <div class="live-chat-client-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                message_bubble +
                '<div style="    width: 50px; height: 45px; display: inline-block;"><svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M31.6312 2.71948L38.934 10.332V39.2805H11.6537V39.375H39.0272V10.4278L31.6312 2.71948Z" fill="#909090"></path>\
                          <path d="M31.5406 2.625H11.5604V39.2805H38.9339V10.3333L31.5393 2.625" fill="#F4F4F4"></path>\
                          <path d="M11.3596 4.59375H2.97272V13.5542H29.354V4.59375H11.3596Z" fill="#7A7B7C"></path>\
                          <path d="M29.4943 13.4019H3.14328V4.43494H29.4943V13.4019Z" fill="#DD2025"></path>\
                          <path d="M11.8808 5.95087H10.1653V12.2509H11.5146V10.1259L11.8125 10.143C12.102 10.138 12.3888 10.0862 12.6617 9.98943C12.901 9.90713 13.1211 9.77721 13.3088 9.60749C13.4997 9.44582 13.6503 9.24177 13.7485 9.01162C13.8801 8.62902 13.9271 8.22241 13.8863 7.81987C13.8781 7.53231 13.8277 7.24752 13.7367 6.97462C13.6538 6.77762 13.5308 6.60003 13.3756 6.45315C13.2204 6.30627 13.0362 6.19332 12.835 6.12149C12.6609 6.05849 12.4811 6.01277 12.2982 5.98499C12.1596 5.96361 12.0197 5.95221 11.8795 5.95087H11.8808ZM11.6314 8.96174H11.5146V7.01924H11.7679C11.8797 7.01118 11.9919 7.02834 12.0962 7.06946C12.2004 7.11058 12.2941 7.17461 12.3703 7.2568C12.5283 7.46814 12.6126 7.72537 12.6105 7.98918C12.6105 8.31205 12.6105 8.60474 12.3192 8.8108C12.1092 8.92626 11.8703 8.97824 11.6314 8.96043" fill="#464648"></path>\
                          <path d="M16.4495 5.93381C16.3038 5.93381 16.162 5.94431 16.0623 5.94825L15.7499 5.95612H14.7262V12.2561H15.931C16.3915 12.2687 16.8499 12.1907 17.2803 12.0264C17.6267 11.889 17.9334 11.6676 18.1728 11.382C18.4056 11.0938 18.5727 10.7583 18.6624 10.3989C18.7655 9.99189 18.8158 9.57326 18.812 9.15337C18.8374 8.65745 18.7991 8.16032 18.6978 7.67419C18.6017 7.31635 18.4217 6.98656 18.1728 6.71212C17.9775 6.49052 17.7384 6.31177 17.4706 6.18712C17.2406 6.0807 16.9987 6.00227 16.75 5.9535C16.6512 5.93716 16.551 5.9297 16.4508 5.93119L16.4495 5.93381ZM16.2119 11.0985H16.0807V7.077H16.0977C16.3683 7.04587 16.6421 7.09469 16.8852 7.21744C17.0633 7.35961 17.2084 7.53874 17.3105 7.74244C17.4207 7.95681 17.4842 8.1921 17.4969 8.43281C17.5087 8.72156 17.4969 8.95781 17.4969 9.15337C17.5022 9.37865 17.4877 9.60395 17.4535 9.82669C17.4131 10.0554 17.3383 10.2766 17.2317 10.4829C17.1111 10.6748 16.9481 10.8364 16.7553 10.9554C16.5934 11.0602 16.4016 11.109 16.2093 11.0946" fill="#464648"></path>\
                          <path d="M22.8769 5.95612H19.6875V12.2561H21.0367V9.75712H22.743V8.58637H21.0367V7.12687H22.8742V5.95612" fill="#464648"></path>\
                          <path d="M28.5875 26.5847C28.5875 26.5847 32.7717 25.8261 32.7717 27.2554C32.7717 28.6847 30.1795 28.1033 28.5875 26.5847ZM25.4939 26.6936C24.8291 26.8405 24.1812 27.0556 23.5606 27.3355L24.0856 26.1542C24.6106 24.9729 25.1553 23.3625 25.1553 23.3625C25.7817 24.4169 26.5106 25.4069 27.3314 26.3183C26.7124 26.4106 26.099 26.5367 25.4939 26.6963V26.6936ZM23.8375 18.1624C23.8375 16.9168 24.2405 16.5769 24.5541 16.5769C24.8678 16.5769 25.2209 16.7278 25.2327 17.8093C25.1305 18.8968 24.9028 19.9688 24.5541 21.004C24.0766 20.1349 23.8294 19.158 23.8362 18.1663L23.8375 18.1624ZM17.7357 31.9646C16.4521 31.1968 20.4277 28.833 21.1482 28.7569C21.1443 28.7582 19.0797 32.7679 17.7357 31.9646ZM33.9936 27.4247C33.9805 27.2935 33.8624 25.8405 31.2768 25.9022C30.199 25.8848 29.1218 25.9608 28.0572 26.1293C27.0259 25.0903 26.1378 23.9184 25.4165 22.6446C25.8709 21.3313 26.146 19.9627 26.2342 18.5758C26.1961 17.0008 25.8194 16.0978 24.6119 16.111C23.4044 16.1241 23.2285 17.1806 23.3873 18.753C23.5429 19.8096 23.8363 20.8413 24.2601 21.8216C24.2601 21.8216 23.7023 23.5581 22.9647 25.2853C22.2271 27.0126 21.7231 27.9182 21.7231 27.9182C20.4404 28.3358 19.2329 28.9561 18.1465 29.7557C17.065 30.7624 16.6253 31.5354 17.195 32.3085C17.6858 32.9753 19.4039 33.1262 20.9395 31.1141C21.7555 30.0749 22.5009 28.9822 23.1708 27.8434C23.1708 27.8434 25.5123 27.2016 26.2407 27.0257C26.9691 26.8498 27.8498 26.7107 27.8498 26.7107C27.8498 26.7107 29.9879 28.8619 32.0498 28.7858C34.1118 28.7096 34.012 27.5533 33.9989 27.4273" fill="#DD2025"></path>\
                          <path d="M31.4397 2.72607V10.4344H38.833L31.4397 2.72607Z" fill="#909090"></path>\
                          <path d="M31.5408 2.625V10.3333H38.9341L31.5408 2.625Z" fill="#F4F4F4"></path>\
                          <path d="M11.7797 5.84982H10.0642V12.1498H11.4187V10.0262L11.718 10.0433C12.0075 10.0383 12.2943 9.98642 12.5672 9.8897C12.8064 9.80737 13.0265 9.67745 13.2142 9.50776C13.4038 9.34565 13.553 9.14164 13.65 8.91189C13.7816 8.52929 13.8286 8.12268 13.7878 7.72014C13.7796 7.43258 13.7292 7.14778 13.6382 6.87489C13.5553 6.67789 13.4324 6.5003 13.2771 6.35342C13.1219 6.20654 12.9378 6.09359 12.7365 6.02176C12.5617 5.95815 12.381 5.91198 12.1971 5.88395C12.0585 5.86257 11.9186 5.85116 11.7784 5.84982H11.7797ZM11.5303 8.8607H11.4135V6.9182H11.6681C11.7799 6.91014 11.8921 6.9273 11.9964 6.96842C12.1006 7.00954 12.1943 7.07356 12.2706 7.15576C12.4285 7.36709 12.5128 7.62433 12.5107 7.88814C12.5107 8.21101 12.5107 8.5037 12.2194 8.70976C12.0095 8.82521 11.7705 8.8772 11.5316 8.85939" fill="white"></path>\
                          <path d="M16.3486 5.83277C16.203 5.83277 16.0612 5.84327 15.9615 5.8472L15.653 5.85508H14.6293V12.1551H15.8341C16.2946 12.1677 16.7531 12.0897 17.1834 11.9254C17.5298 11.788 17.8365 11.5665 18.0759 11.281C18.3087 10.9928 18.4758 10.6573 18.5655 10.2979C18.6686 9.89085 18.7189 9.47222 18.7151 9.05233C18.7405 8.55641 18.7022 8.05928 18.6009 7.57314C18.5048 7.21531 18.3248 6.88551 18.0759 6.61108C17.8806 6.38948 17.6415 6.21073 17.3737 6.08608C17.1437 5.97966 16.9018 5.90122 16.6531 5.85245C16.5543 5.83612 16.4541 5.82865 16.3539 5.83014L16.3486 5.83277ZM16.115 10.9975H15.9838V6.97595H16.0008C16.2714 6.94482 16.5452 6.99364 16.7883 7.11639C16.9664 7.25857 17.1115 7.43769 17.2136 7.64139C17.3238 7.85577 17.3873 8.09106 17.4 8.33177C17.4118 8.62052 17.4 8.85677 17.4 9.05233C17.4053 9.2776 17.3908 9.50291 17.3566 9.72564C17.3162 9.95432 17.2414 10.1756 17.1348 10.3819C17.0142 10.5737 16.8512 10.7354 16.6584 10.8544C16.4965 10.9591 16.3047 11.008 16.1124 10.9935" fill="white"></path>\
                          <path d="M22.7758 5.85507H19.5864V12.1551H20.9356V9.65607H22.6419V8.48532H20.9356V7.02582H22.7731V5.85507" fill="white"></path>\
                          </svg></div>\
                          <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
                attached_file_src.split("/")[len - 1] +
                '</span><br>\
                          <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                          <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                          ' +
                get_doc_path_html(attached_file_src) +
                '\
                          </div>\
                      </div>' +
                reply_private_container[1] +
                '<div class="live-chat-client-message-time">\
                          ' +
                time +
                "\
                      </div>" + reply_private_container[2] + "</div>";
        } else if (is_txt(attached_file_src)) {
            html =
                '<div class="live-chat-agent-message-wrapper" id=' + message_id + '>\
                          <div class="live-chat-agent-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                message_bubble +
                '<div style="    width: 50px; height: 45px; display: inline-block;"><svg width="32" height="42" viewBox="0 0 32 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path d="M9.1875 18.375C8.8394 18.375 8.50556 18.5133 8.25942 18.7594C8.01328 19.0056 7.875 19.3394 7.875 19.6875C7.875 20.0356 8.01328 20.3694 8.25942 20.6156C8.50556 20.8617 8.8394 21 9.1875 21H22.3125C22.6606 21 22.9944 20.8617 23.2406 20.6156C23.4867 20.3694 23.625 20.0356 23.625 19.6875C23.625 19.3394 23.4867 19.0056 23.2406 18.7594C22.9944 18.5133 22.6606 18.375 22.3125 18.375H9.1875ZM7.875 24.9375C7.875 24.5894 8.01328 24.2556 8.25942 24.0094C8.50556 23.7633 8.8394 23.625 9.1875 23.625H22.3125C22.6606 23.625 22.9944 23.7633 23.2406 24.0094C23.4867 24.2556 23.625 24.5894 23.625 24.9375C23.625 25.2856 23.4867 25.6194 23.2406 25.8656C22.9944 26.1117 22.6606 26.25 22.3125 26.25H9.1875C8.8394 26.25 8.50556 26.1117 8.25942 25.8656C8.01328 25.6194 7.875 25.2856 7.875 24.9375ZM7.875 30.1875C7.875 29.8394 8.01328 29.5056 8.25942 29.2594C8.50556 29.0133 8.8394 28.875 9.1875 28.875H14.4375C14.7856 28.875 15.1194 29.0133 15.3656 29.2594C15.6117 29.5056 15.75 29.8394 15.75 30.1875C15.75 30.5356 15.6117 30.8694 15.3656 31.1156C15.1194 31.3617 14.7856 31.5 14.4375 31.5H9.1875C8.8394 31.5 8.50556 31.3617 8.25942 31.1156C8.01328 30.8694 7.875 30.5356 7.875 30.1875Z" fill="black"/>\
                              <path d="M19.6875 0H5.25C3.85761 0 2.52226 0.553124 1.53769 1.53769C0.553123 2.52226 0 3.85761 0 5.25V36.75C0 38.1424 0.553123 39.4777 1.53769 40.4623C2.52226 41.4469 3.85761 42 5.25 42H26.25C27.6424 42 28.9777 41.4469 29.9623 40.4623C30.9469 39.4777 31.5 38.1424 31.5 36.75V11.8125L19.6875 0ZM19.6875 2.625V7.875C19.6875 8.91929 20.1023 9.92081 20.8408 10.6592C21.5792 11.3977 22.5807 11.8125 23.625 11.8125H28.875V36.75C28.875 37.4462 28.5984 38.1139 28.1062 38.6062C27.6139 39.0984 26.9462 39.375 26.25 39.375H5.25C4.55381 39.375 3.88613 39.0984 3.39384 38.6062C2.90156 38.1139 2.625 37.4462 2.625 36.75V5.25C2.625 4.55381 2.90156 3.88613 3.39384 3.39384C3.88613 2.90156 4.55381 2.625 5.25 2.625H19.6875Z" fill="black"/>\
                              </svg></div>\
                              <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
                attached_file_src.split("/")[len - 1] +
                '</span><br>\
                              <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                              <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                              ' +
                get_doc_path_html(attached_file_src) +
                '\
                              </div>\
                          </div>' +
                reply_private_container[1] +
                '<div class="live-chat-agent-message-time">\
                              ' +
                time +
                "\
                              " +
                blue_ticks +
                "\
                          </div>" + reply_private_container[2] + "</div>";
        } else if (is_docs(attached_file_src)) {
            html =
                '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                      <div class="live-chat-client-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                message_bubble +
                '<div style="    width: 50px; height: 45px; display: inline-block;">\
                      <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">\
                          <path d="M37.8079 3.9375H12.7378C12.5324 3.93733 12.3289 3.97763 12.139 4.05609C11.9491 4.13455 11.7766 4.24965 11.6312 4.39481C11.4858 4.53996 11.3704 4.71233 11.2916 4.90208C11.2128 5.09183 11.1722 5.29524 11.172 5.50069V12.4688L25.7001 16.7344L39.375 12.4688V5.50069C39.3748 5.29513 39.3341 5.09161 39.2553 4.90178C39.1764 4.71194 39.0609 4.53951 38.9154 4.39434C38.7698 4.24917 38.5971 4.1341 38.4071 4.05571C38.2171 3.97733 38.0134 3.93716 37.8079 3.9375Z" fill="#41A5EE"/>\
                          <path d="M39.375 12.4688H11.172V21L25.7001 23.5594L39.375 21V12.4688Z" fill="#2B7CD3"/>\
                          <path d="M11.172 21V29.5312L24.8456 31.2375L39.375 29.5312V21H11.172Z" fill="#185ABD"/>\
                          <path d="M12.7378 38.0625H37.8066C38.0122 38.063 38.216 38.023 38.4062 37.9447C38.5964 37.8664 38.7692 37.7513 38.9149 37.6061C39.0606 37.4609 39.1762 37.2884 39.2552 37.0985C39.3341 36.9086 39.3748 36.705 39.375 36.4993V29.5312H11.172V36.4993C11.1722 36.7048 11.2128 36.9082 11.2916 37.0979C11.3704 37.2877 11.4858 37.46 11.6312 37.6052C11.7766 37.7504 11.9491 37.8654 12.139 37.9439C12.3289 38.0224 12.5324 38.0627 12.7378 38.0625Z" fill="#103F91"/>\
                          <path opacity="0.1" d="M21.5696 10.7625H11.172V32.0906H21.5696C21.9839 32.0886 22.3808 31.9234 22.6741 31.6308C22.9674 31.3382 23.1336 30.9418 23.1368 30.5275V12.3257C23.1336 11.9114 22.9674 11.515 22.6741 11.2224C22.3808 10.9298 21.9839 10.7646 21.5696 10.7625Z" fill="black"/>\
                          <path opacity="0.2" d="M20.7152 11.6156H11.172V32.9438H20.7152C21.1295 32.9417 21.5263 32.7765 21.8196 32.4839C22.113 32.1913 22.2792 31.7949 22.2823 31.3806V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                          <path opacity="0.2" d="M20.7152 11.6156H11.172V31.2375H20.7152C21.1295 31.2354 21.5263 31.0702 21.8196 30.7776C22.113 30.485 22.2792 30.0886 22.2823 29.6743V13.1788C22.2792 12.7645 22.113 12.3681 21.8196 12.0755C21.5263 11.7829 21.1295 11.6177 20.7152 11.6156Z" fill="black"/>\
                          <path opacity="0.2" d="M19.8607 11.6156H11.172V31.2375H19.8607C20.2751 31.2354 20.6719 31.0702 20.9652 30.7776C21.2585 30.485 21.4248 30.0886 21.4279 29.6743V13.1788C21.4248 12.7645 21.2585 12.3681 20.9652 12.0755C20.6719 11.7829 20.2751 11.6177 19.8607 11.6156Z" fill="black"/>\
                          <path d="M4.19212 11.6156H19.8608C20.2758 11.6153 20.674 11.7797 20.9679 12.0729C21.2617 12.366 21.4272 12.7638 21.4279 13.1788V28.8212C21.4272 29.2362 21.2617 29.634 20.9679 29.9272C20.674 30.2203 20.2758 30.3847 19.8608 30.3844H4.19212C3.98656 30.3847 3.78295 30.3446 3.59291 30.2662C3.40288 30.1878 3.23016 30.0727 3.08462 29.9275C2.93909 29.7824 2.82358 29.6099 2.74472 29.4201C2.66585 29.2303 2.62517 29.0268 2.625 28.8212V13.1788C2.62517 12.9733 2.66585 12.7697 2.74472 12.5799C2.82358 12.3901 2.93909 12.2176 3.08462 12.0725C3.23016 11.9273 3.40288 11.8122 3.59291 11.7338C3.78295 11.6555 3.98656 11.6153 4.19212 11.6156Z" fill="url(#paint0_linear)"/>\
                          <path d="M9.05627 23.6093C9.08645 23.8508 9.10745 24.0608 9.11664 24.2406H9.15339C9.16651 24.0699 9.19539 23.8639 9.2387 23.6237C9.28201 23.3835 9.32008 23.1801 9.35551 23.0134L11.0027 15.9167H13.1342L14.8405 22.9071C14.9398 23.3395 15.0109 23.7779 15.0531 24.2196H15.082C15.1133 23.7896 15.1725 23.3622 15.2591 22.9399L16.6228 15.9075H18.5614L16.1674 26.0768H13.9007L12.2771 19.3489C12.2299 19.1546 12.1765 18.9018 12.117 18.5903C12.0575 18.2788 12.0208 18.0513 12.0068 17.9078H11.9792C11.9608 18.0731 11.9241 18.3186 11.869 18.6441C11.8138 18.9709 11.7705 19.2111 11.7377 19.3686L10.2113 26.0807H7.90652L5.49939 15.9167H7.46814L8.95258 23.0278C8.99688 23.2198 9.03149 23.4138 9.05627 23.6093Z" fill="white"/>\
                          <defs>\
                          <linearGradient id="paint0_linear" x1="5.89837" y1="10.3871" x2="18.1545" y2="31.6129" gradientUnits="userSpaceOnUse">\
                          <stop stop-color="#2368C4"/>\
                          <stop offset="0.5" stop-color="#1A5DBE"/>\
                          <stop offset="1" stop-color="#1146AC"/>\
                          </linearGradient>\
                          </defs>\
                      </svg>\
                          </div>\
                          <div style="width: 120px; height: 50px; display: inline-block;"><span id="custom-text-attach">' +
                attached_file_src.split("/")[len - 1] +
                '</span><br>\
                      <a href="' + attached_file_src + '" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>\
                      <div style="width: 30px;cursor: pointer; height: 35px; display: inline-block;">\
                      ' +
                get_doc_path_html(attached_file_src) +
                '\
                      </div></div>' +
                reply_private_container[1] +
                '<div class="live-chat-client-message-time">\
                          ' +
                time +
                "\
                      </div>" + reply_private_container[2] + "</div>";
        } else if (is_image(attached_file_src)) {
            if (is_guest_agent_message && is_blue_border)
                message_bubble =
                '<div class="live-chat-client-message-bubble-image-attachment live-chat-client-message-bubble-blue-border">';
            else
                message_bubble =
                '<div class="live-chat-client-message-bubble-image-attachment">';
            html =
                '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-client-image">' +
                get_user_initial(sender_name) +
                "</div>" +
                sender_name_html +
                reply_private_container[0] +
                message_bubble +
                get_image_path_html_attach(attached_file_src) +
                '\
                        <div class="file-attach-name-area">\
                            <h5 id="custom-text-attach-img">' +
                attached_file_src.split("/")[len - 1] +
                '</h5>\
                            <a href="' +
                attached_file_src +
                '" target="_blank" download><span style="position: absolute; top: 0.6rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>\
                                <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>\
                                <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>\
                                <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>\
                                <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>\
                                </svg>\
                                </span></a>\
                        </div></div>' +
                reply_private_container[1] +
                '<div class="live-chat-client-message-time">\
                            ' +
                time +
                "\
                            </div>" + reply_private_container[2] + "</div>";
        }
    } else {
        var reply_private_container = get_reply_private_html(reply_private_container, "agent");

        if (is_pdf(attached_file_src)) {
            html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>` +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
          <div style="width: 50px;  display: inline-block;">
          ${icons.pdf}
          </div>
          <div class="file-attachment-path"><span id="custom-text-attach">${
              attached_file_src.split("/")[len - 1]
          }</span><br>
          <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
          <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
          ${get_doc_path_html(attached_file_src)}
          </div>`;

            if (message != "") {
                html += `<div class="upload-file-text-area">${message}</div>`;
            }

            html +=
                `</div>` + reply_private_container[1] + `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>` + reply_private_container[2] + `</div>`;
        } else if (is_txt(attached_file_src)) {
            html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>` +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
          <div style="width: 50px;  display: inline-block;">
          ${icons.txt}
          </div>
          <div class="file-attachment-path"><span id="custom-text-attach">${
              attached_file_src.split("/")[len - 1]
          }</span><br>
          <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
          <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
          ${get_doc_path_html(attached_file_src)}
          </div>`;

            if (message != "") {
                html += `<div class="upload-file-text-area">${message}</div>`;
            }

            html +=
                `</div>` + reply_private_container[1] + `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>` + reply_private_container[2] + `</div>`;
        } else if (is_docs(attached_file_src)) {
            html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>` +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
          <div style="width: 50px;  display: inline-block;">
          ${icons.doc}
          </div>
          <div class="file-attachment-path"><span id="custom-text-attach">${
              attached_file_src.split("/")[len - 1]
          }</span><br>
          <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
          <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
          ${get_doc_path_html(attached_file_src)}
          </div>`;

            if (message != "") {
                html += `<div class="upload-file-text-area">${message}</div>`;
            }

            html +=
                `</div>` + reply_private_container[1] + `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>` + reply_private_container[2] + `</div>`;
        } else if (is_excel(attached_file_src)) {
            html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>` +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble file-attachement-download">
          <div style="width: 50px;  display: inline-block;">
          ${icons.excel}
          </div>
          <div class="file-attachment-path"><span id="custom-text-attach">${
              attached_file_src.split("/")[len - 1]
          }</span><br>
          <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
          <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
          ${get_doc_path_html(attached_file_src)}
          </div>`;

            if (message != "") {
                html += `<div class="upload-file-text-area">${message}</div>`;
            }

            html +=
                `</div>` + reply_private_container[1] + `<div class="live-chat-agent-message-time">
                ${time}` +
                blue_ticks +
                `</div>` + reply_private_container[2] + `</div>`;
        } else if (is_image(attached_file_src)) {
            html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>` +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble-image-attachment">
          <div class="slideshow-container" value="1">
              <div class="mySlides livechat-slider-card">
                  ${get_image_path_html_attach(attached_file_src)}
                  <div style="text-align: left;">
                      <h5 style="overflow-wrap: break-word; ">${
                          attached_file_src.split("/")[len - 1]
                      }</h5><a href="${attached_file_src}" target="_blank" download><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>
                      <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>
                      <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>
                      <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>
                      <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>
                      </svg>
                      </span></a>`;

            if (message != "") {
                html += `<p style="overflow-wrap: break-word;">${message}</p>`;
            }

            html +=
                `</div>
        </div>
      </div>

      </div>` +
                reply_private_container[1] +
                `<div class="live-chat-agent-message-time">
      ${time}` +
                blue_ticks +
                `</div>` + reply_private_container[2] + `</div>`;
        } else if (is_video(attached_file_src)) {
            html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
      <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>` +
                reply_private_container[0] +
                `<div class="live-chat-agent-message-bubble-image-attachment">
          <div class="slideshow-container" value="1">
              <div class="mySlides livechat-slider-card">
                  ${get_video_path_html(attached_file_src)}
                  <div style="text-align: left;">
                      <h5 style="overflow-wrap: break-word; ">${
                          attached_file_src.split("/")[len - 1]
                      }</h5>`;

            if (message != "") {
                html += `<p style="overflow-wrap: break-word;">${message}</p>`;
            }

            html +=
                `</div>
        </div>
      </div>

      </div>` +
                reply_private_container[1] +
                `<div class="live-chat-agent-message-time">
      ${time}` +
                blue_ticks +
                `</div>` + reply_private_container[2] + `</div>`;
        }
    }

    if (returnresponse != true)
        document.getElementById("style-2-" + pk).innerHTML += html;
    else return html;
}

function append_file_to_agent(
    attached_file_src,
    message,
    is_blue_tick,
    img_file,
    language,
    time = return_time()
) {
    const session_id = get_session_id();
    var len = attached_file_src.split("/").length;
    var blue_ticks =
        '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
    <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
    <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
    </svg>';

    if (is_blue_tick) {
        blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
        <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
        <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
        </svg>';
    }

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${session_id}`) == "true" && message != "") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_translated_text(this);>View Translated</a>\
                                  </div>';
    }

    message = livechat_linkify(message);

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    let html = "";
    const icons = get_icons();
    if (is_pdf(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial()}</div>
                    <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
                        <div style="width: 50px;  display: inline-block;">
                        ${icons.pdf}
                        </div>
                        <div class="file-attachment-path"><span id="custom-text-attach">${
                            attached_file_src.split("/")[len - 1]
                        }</span><br>
                        <a href="${attached_file_src}" style="text-decoration: unset"><b  id="click-to-view-text-attachment">Click to view</b></a></div>
                        <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
                        ${get_doc_path_html(attached_file_src)}
                        </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                    ${time}
                    ${blue_ticks}
                ${view_translation_html}</div></div>`;
    } else if (is_txt(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.txt}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div>`;
    } else if (is_docs(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.doc}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div>`;
    } else if (is_excel(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.excel}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div>`;
    } else if (is_image(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial()}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment live-chat-attachment-div">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_image_path_html(
                                        attached_file_src,
                                        img_file
                                    )}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>
                                        <a href="${attached_file_src}" target="_blank" download><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>
                                        <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>
                                        <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>
                                        <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>
                                        <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>
                                        </svg>
                                        </span></a>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word; text-align: ${text_direction};" class="live-chat-attachment-text">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
                ${view_translation_html}</div></div>`;
    } else if (is_video(attached_file_src)) {
        html = `<div class="live-chat-agent-image">${get_user_initial()}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment live-chat-attachment-div">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_video_path_html(attached_file_src)}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word; text-align: ${text_direction};" class="live-chat-attachment-text">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
                ${view_translation_html}</div></div>`;
    }

    return html;
}

function append_temp_file_to_agent(name) {
    let message = $("#query-file").val();
    message = stripHTML(message);
    message = strip_unwanted_characters(message);
    let html = "";
    const icons = get_icons();
    if (is_pdf(name)) {
        html = `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.pdf}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_txt(name)) {
        html = `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.txt}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_docs(name)) {
        html = `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.doc}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_excel(name)) {
        html = `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
        <div class="live-chat-agent-image">${get_user_initial()}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download">
            <div style="width: 50px;  display: inline-block;">
            ${icons.excel}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${name}</span><br>
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area">${message}</div>`;
        }

        html += `</div><div class="live-chat-agent-message-time">
                    sending...
                </div></div>`;
    } else if (is_image(name)) {
        html = `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
                    <div class="live-chat-agent-image">${get_user_initial()}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_image_path_html(name)}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${name}</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="live-chat-agent-message-time">
                sending...
                </div></div>`;
    } else if (is_video(name)) {
        html = `<div class="live-chat-agent-message-wrapper live-chat-temp-file">
                    <div class="live-chat-agent-image">${get_user_initial()}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_video_path_html(name)}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${name}</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word;">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="live-chat-agent-message-time">
                sending...
                </div></div>`;
    }
    const session_id = get_session_id();
    $(`#style-2_${session_id}`).append(html);
    remove_message_diffrentiator(session_id);
    scroll_to_bottom();
}

function send_message_to_user_with_file(
    attached_file_src,
    thumbnail_url,
    channel_file_url,
    img_file = ""
) {
    if (true || $("#query-file").val().length < 3000) {
        var sentence = $("#query-file").val();
        sentence = $($.parseHTML(sentence)).text().trim();
        var translated_text = "";
        $("#query-file").val("");

        var message_id = "";

        if (!is_url(sentence)) {
            sentence = stripHTMLtags(sentence);
            if (!is_special_character_allowed_in_chat()) {
                sentence = remove_special_characters_from_str(sentence);
            }
        }

        const chat_data = get_chat_data();

        if(sentence) {
            if(!check_if_sentence_valid(sentence, chat_data.channel)) {
                if(chat_data.channel == 'Facebook' || chat_data.channel == 'Instagram') {
                    showToast("You have exceeded the character limit for this channel.", 3000);
                } else {
                    showToast("Seems like we have exceeded the maximum permissible character limit.", 3000);
                }
                return;
            }
        }

        const session_id = get_session_id();
        const guest_session = localStorage.getItem(
            `guest_session-${session_id}`
        );
        const guest_session_status = localStorage.getItem(
            `guest_session_status-${session_id}`
        );
        var is_guest_session = false;
        if (guest_session == "true") is_guest_session = true;

        let agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
        let customer_language = localStorage.getItem(`customer_language-${session_id}`);

        let to_translate_message = false;
        if (agent_preferred_language != customer_language) {
            to_translate_message = true;
        }

        var json_string = JSON.stringify({
            message: sentence,
            sender: "Agent",
            attached_file_src: attached_file_src,
            thumbnail_url: thumbnail_url,
            channel_file_url: channel_file_url,
            session_id: session_id,
            is_guest_agent_message: is_guest_session,
            sender_name: get_agent_name(),
            sender_username: get_agent_username(),
            to_translate_message: to_translate_message,
        });
        json_string = encrypt_variable(json_string);
        json_string = encodeURIComponent(json_string);

        var csrf_token = getCsrfToken();
        var xhttp = new XMLHttpRequest();
        var params = "json_string=" + json_string;

        let save_data_url = "/livechat/save-agent-chat/";
        if (check_is_email_session(session_id)) {
            save_data_url = "/livechat/save-agent-email-chat/";
        }

        xhttp.open("POST", save_data_url, false);
        xhttp.setRequestHeader("X-CSRFToken", csrf_token);
        xhttp.setRequestHeader(
            "Content-Type",
            "application/x-www-form-urlencoded"
        );
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status_code"] == "200") {
                    console.log("chat send by agent saved");
                    message_id = response["message_id"];
                    translated_text = response["translated_text"];
                }
            }
        };
        xhttp.send(params);

        if (check_is_email_session(session_id)) {
            send_mail_to_customer(session_id, message_id, channel_file_url);
        }

        if (!agent_preferred_language)
            agent_preferred_language = "en";

        let html = append_file_to_agent(
            attached_file_src,
            sentence,
            false,
            img_file,
            agent_preferred_language
        );

        const elem = document.getElementsByClassName("live-chat-temp-file")[0];
        elem.classList.remove("live-chat-temp-file");
        elem.innerHTML = html;
        elem.setAttribute('id', message_id);

        let msg = {
            sender: "Agent",
            text_message: sentence,
            is_attachment: "True",
            is_guest_agent_message: is_guest_session,
        };
        let attachment_name = attached_file_src.split("/");
        msg.attachment_name = attachment_name[attachment_name.length - 1];
        append_message_in_chat_icon(session_id, msg);
        scroll_to_bottom();

        var is_guest_agent_message = "false";
        if (guest_session == "true" && guest_session_status == "accept")
            is_guest_agent_message = "true";
        var file_path = JSON.stringify({
            message: JSON.stringify({
                text_message: sentence,
                type: "file",
                channel: chat_data.channel,
                path: attached_file_src,
                thumbnail: thumbnail_url,
                is_guest_agent_message: is_guest_agent_message,
                agent_name: get_agent_name(),
                session_id: session_id,
                sender_username: get_agent_username(),
                message_id: message_id,
                language: agent_preferred_language,
                translated_text: translated_text,
            }),
            sender: "Agent",
        });

        send_message_to_socket(file_path);

        send_message_to_guest_agent_socket(file_path);

        save_message_to_local({
            message: sentence,
            attached_file_src: attached_file_src,
            sender: "Agent",
            sender_name: get_agent_name(),
            session_id: session_id,
            file: img_file,
            is_guest_agent_message: is_guest_session,
            sender_username: get_agent_username(),
            message_id: message_id,
            language: agent_preferred_language,
        });
    }
}

export function send_mail_to_customer(session_id, message_id, channel_file_url) {

    if (session_id == "" || message_id == "") return;

    let json_string = {
        session_id: session_id,
        message_id: message_id,
        channel_file_url: channel_file_url,
    };

    json_string = JSON.stringify(json_string);
    const params = get_params(json_string);

    let config = {
        headers: {
            'X-CSRFToken': getCsrfToken(),
        }
    }

    axios
        .post("/livechat/send-livechat-email-to-customer/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                console.log("Mail sent to customer successfully.")
            } else if (response.status == 403) {
                showToast(response["status_message"], 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });

}

function update_message_history(refresh_customer_details) {
    if (!refresh_customer_details && get_data_present() && get_chat_data().channel != "Email") {
        return;
    }

    if (refresh_customer_details) {
        const customer_details = get_customer_details_store();
        delete_messages_from_local(customer_details.name);
        document.getElementById(
            "refresh_customer_details_btn"
        ).style.pointerEvents = "none";
    }

    const all_details_div = document.getElementById(
        "livechat-customer-all-details"
    );

    if (all_details_div) {
        all_details_div.innerHTML = `<div style="display: flex; align-items: center; justify-content: center;"><img id="loading-image" src="/static/LiveChatApp/img/waiting1.gif" style="height: 4em;"></div>`;
    }

    const session_id = get_session_id();
    let is_email_session = check_is_email_session(session_id);
    var json_string = JSON.stringify({
        session_id: session_id,
        refresh_customer_details: refresh_customer_details,
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/update-message-history/", true);
    xhttp.timeout = 5000;
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.ontimeout = function () {
        show_custom_notification("Your chats might be loading slower than usual. We recommend that you reload the page, if the problem still persists.", 10000);
    };
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                if (!refresh_customer_details) {
                    let message_history = response.message_history;
                    state.chat_history[session_id] = message_history;
                    let cust_last_app_time = response.cust_last_app_time;

                    update_customer_last_app_time(
                        session_id,
                        cust_last_app_time
                    );

                    let messages = state.chat_history[session_id];

                    append_message_history(message_history, cust_last_app_time);
                    localStorage.setItem(`ongoing_chat-${session_id}`, true);

                    if (is_indexed_db_supported() && !is_email_session) {
                        for (let message of messages) {
                            message["session_id"] = session_id;
                            let message_history = get_message_history_store();
                            add_message_to_local_db(
                                message,
                                message_history.name
                            );
                        }
                    }
                }

                let customer_details_obj = get_customer_details(response);
                if (is_indexed_db_supported() && !is_email_session) {
                    let customer_details = get_customer_details_store();
                    add_message_to_local_db(
                        customer_details_obj,
                        customer_details.name
                    );
                }
            } else {
                let html = `<div class="live-chat-customer-details-todo">`;

                html += `<div class="live-chat-customer-name">
                            <div class="live-chat-mobile-display back-arrow">
                                <img src="/static/LiveChatApp/img/mobile-back.svg" alt="Back arrow" id="live-chat-customer-details-closer" onclick="close_customer_details()">
                            </div>`;

                html += `<div class="live-chat-client-image"> </div>
                        <p> </p>
                        <button class="customer-details-refresh-button" id="refresh_customer_details_btn">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"/>
                            </svg>
                        </button>
                    </div><br><div id="livechat-customer-all-details"><p>Failed to load customer details.</p></div>`;

                document.getElementById(
                    "live-chat-customer-details-sidebar"
                ).innerHTML = html;

                console.log("error");
            }

            document.getElementById(
                "refresh_customer_details_btn"
            ).style.pointerEvents = "auto";
        }
    };
    xhttp.send(params);
}

async function append_message_history(message_history, cust_last_app_time = 0, to_check_translated_message = true) {
    const session_id = get_session_id();
    if (cust_last_app_time == 0) {
        cust_last_app_time = localStorage.getItem(
            "cust_last_app_time_" + session_id
        );

        if (!cust_last_app_time) cust_last_app_time = 0;
    }

    var html = "";
    const unread_message_count = localStorage.getItem(
        `unread_message_count-${session_id}`
    );
    const is_ongoing_chat = localStorage.getItem(`ongoing_chat-${session_id}`);
    const guest_session = localStorage.getItem(`guest_session-${session_id}`);
    const guest_session_status = localStorage.getItem(
        `guest_session_status-${session_id}`
    );

    let bot_language = "en";
    if (localStorage.getItem(`agent_language-${session_id}`)) {
        bot_language = localStorage.getItem(`agent_language-${session_id}`);
    } else if (localStorage.getItem(`customer_language-${session_id}`)) {
        bot_language = localStorage.getItem(`customer_language-${session_id}`);
    }

    for (var item = 0; item < message_history.length; item++) {
        if (
            item == message_history.length - parseInt(unread_message_count) &&
            is_ongoing_chat == "true"
        ) {
            html += get_unread_message_diffrentiator_html(
                unread_message_count,
                session_id
            );
            // adding message diffrentiator before unread messages
        }
        let message = message_history[item];

        let text_message = message.message;
        if (localStorage.getItem(`is_translated-${session_id}`) == "true" && to_check_translated_message && message.sender != "Agent") {
            text_message = await get_translated_text(message.message_id, text_message, session_id, message.sender_username);

        }

        if (message.sender == "Agent") {
            if (message.original_message && message.original_message.length) {
                text_message = message.original_message;
            }
            if (message.is_video_call_message) continue;

            if (message.sender_username != get_agent_username()) {
                if (message.attached_file_src != "") {
                    html += get_file_to_agent_html_sent_customer(
                        message.attached_file_src,
                        message.sender_name,
                        message.file,
                        true,
                        message.message_id,
                        message.time
                    );
                }
                if (message.message != "") {
                    html += get_response_server_html(
                        text_message,
                        message.sender_name,
                        true,
                        message.time,
                        message.message_id,
                        message.language,
                    );
                }
            } else {
                var flag_not_seen = true;
                if (
                    parseInt(cust_last_app_time) <
                    parseInt(message.time_in_minisec)
                ) {
                    flag_not_seen = false;
                }
                if (message.attached_file_src != "") {
                    html += get_file_to_agent_html(
                        message.attached_file_src,
                        text_message,
                        message.sender_name,
                        flag_not_seen,
                        message.file,
                        session_id,
                        message.message_id,
                        message.time,
                        message.language
                    );
                } else {
                    html += get_response_user_html(
                        text_message,
                        message.sender_name,
                        flag_not_seen,
                        session_id,
                        message.time,
                        message.message_id,
                        message.language,
                    );
                }
            }
        } else if (message.sender == "Customer") {
            if (message.attached_file_src != "") {
                html += get_file_to_agent_html_sent_customer(
                    message.attached_file_src,
                    message.sender_name,
                    message.file,
                    false,
                    message.message_id,
                    message.time
                );
            }
            if (message.message != "") {
                html += get_response_server_html(
                    text_message,
                    message.sender_name,
                    false,
                    message.time,
                    message.message_id,
                    message.language
                );
            }
        } else if (message.sender == "Bot") {
            
            let message_list = text_message.split(RESPONSE_SENTENCE_SEPARATOR);
            for (const msg of message_list) {
                html += get_response_user_html(msg, message.sender_name, true, session_id, message.time, "", bot_language);
            }

        } else if (message.sender == "System") {

            let original_message = message.message;
            if (!to_check_translated_message) {
                original_message = message.original_message;
            }
            if (message.is_file_not_support_message) {
                continue;
            }
            if (message.is_video_call_message || message.is_cobrowsing_message || message.is_voice_call_message || message.is_transcript_message) {
                if ((is_primary_agent(session_id) && message.message_for == 'primary_agent') || (message.message_for == 'guest_agent' && message.sender_username == get_agent_username())) {
                    html += get_video_call_text_response(original_message, text_message);
                }
            } else if (original_message.includes("Customer details updated") || original_message.includes("Reinitiating Request Sent")) {
                html += `<div class="live-chat-customer-details-update-message-div">
                            ${text_message}
                        </div>`;
            } else if (message.is_customer_report_message_notification) {

                html += get_report_message_notif_html(text_message);

            } else if(!message.is_customer_warning_message){
                html += get_system_text_response_html(
                    text_message,
                    message.time
                );
            }

            if (
                message.message.includes("Customer left the chat") ||
                message.message.includes("Due to inactivity chat has ended") ||
                message.is_customer_report_message_notification
            ) {
                if (state.customer_left_chat[session_id] == undefined) {
                    state.customer_left_chat[session_id] = true;
                    check_edit_customer_info_btn();
                }
            }
        }
    }
    $(`#style-2_${session_id}`).html("");
    $(`#style-2_${session_id}`).append(html);
    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        check_appended_messages_alignment(session_id);
    }

    //Appending supervisor/admin's reply messages
    for (var item = 0; item < message_history.length; item++) {
        let message = message_history[item];
        if (message.sender == "Supervisor") {

            let text_message = message.message;
            if (message.attached_file_src != '' || message.message != '') {
                if (localStorage.getItem(`is_translated-${session_id}`) == "true" && to_check_translated_message) {
                    text_message = await get_translated_text(message.message_id, text_message, session_id, message.sender_username);
                }
            }

            if (message.attached_file_src != '') {
                append_supervisor_file(message.attached_file_src, session_id, message.file, text_message, message.reply_message_id, message.sender_username, message.time);
            } else if (text_message != '') {
                append_supervisor_message(text_message, session_id, message.sender_name, message.reply_message_id, message.sender_username, message.time);
            }
        }
    }
    $(`#style-2_${session_id}`).prepend(get_scroll_to_bottom_html());
    scroll_to_bottom();

}

function check_appended_messages_alignment(session_id) {
    let agent_language = localStorage.getItem(`agent_language-${session_id}`);

    if (is_rtl_language(agent_language)) {
        $('.live-chat-agent-message-bubble').css('text-align', 'right');
        $('.live-chat-client-message-bubble').css('text-align', 'right');
        $('.live-chat-attachment-text').css('text-align', 'right');
    } else {
        $('.live-chat-agent-message-bubble').css('text-align', 'left');
        $('.live-chat-client-message-bubble').css('text-align', 'left');
        $('.live-chat-attachment-text').css('text-align', 'left');
    }
}

function get_system_text_response_html(text_response, time) {
    var html = `<div class="easychat-system-message-div" ><div class="easychat-system-message easychat-system-message-line" style="color:${state.bot_theme_color}" >${text_response}<br><span class="message-time-bot">${time}</span></div></div>`;
    return html;
}

export function get_customer_warning_system_text_html(text_response) {
    var html = `<div class="easychat-system-message-div">
                    <div class="easychat-system-message easychat-system-message-line" style="color:#4D4D4D; background-color: #FEF2F2;border: 1px solid #E89E9E;">${text_response}</div>
                </div>`;
    return html;
}

export function get_report_message_notif_html(text_response) {
    var html = `<div class="easychat-system-message-div">
                    <div class="easychat-system-message easychat-system-message-line" style="color: #E53E3E;background: #FEF2F2; border: none; border-radius: 2px;">${text_response}</div>
                </div>`;
    return html;
}

function get_file_to_agent_html(
    attached_file_src,
    message,
    sender_name,
    is_blue_tick,
    img_file,
    session_id,
    message_id = "",
    time = return_time(),
    language = "en"
) {
    var len = attached_file_src.split("/").length;
    var blue_ticks =
        '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                        <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                        </svg>';

    if (is_blue_tick) {
        blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                        <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                    </svg>';
    }

    message = stripHTML(message);
    message = livechat_linkify(message);

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${session_id}`) == "true" && message != "") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_translated_text(this);>View Translated</a>\
                                  </div>';
    }

    const icons = get_icons();
    let html = "";
    if (is_pdf(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.pdf}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div></div>`;
    } else if (is_txt(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.txt}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div></div>`;
    } else if (is_docs(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.doc}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div></div>`;
    } else if (is_excel(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}><div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
        <div class="live-chat-agent-message-bubble file-attachement-download live-chat-attachment-div">
            <div style="width: 50px;  display: inline-block;">
            ${icons.excel}
            </div>
            <div class="file-attachment-path"><span id="custom-text-attach">${
                attached_file_src.split("/")[len - 1]
            }</span><br>
            <a href="${attached_file_src}" style="text-decoration: unset"><b id="click-to-view-text-attachment">Click to view</b></a></div>
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">
            ${get_doc_path_html(attached_file_src)}
            </div>`;

        if (message != "") {
            html += `<div class="upload-file-text-area live-chat-attachment-text" style="text-align: ${text_direction}">${message}</div>`;
        }

        html += `</div><div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
            ${view_translation_html}</div></div></div>`;
    } else if (is_image(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
                        <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment live-chat-attachment-div">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_image_path_html(
                                        attached_file_src,
                                        img_file
                                    )}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>
                                        <a href="${attached_file_src}" target="_blank" download><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"/>
                                        <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"/>
                                        <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"/>
                                        <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"/>
                                        <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"/>
                                        </svg>
                                        </span></a>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word; text-align: ${text_direction};" class="live-chat-attachment-text" >${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
                ${view_translation_html}</div></div>
                </div>`;
    } else if (is_video(attached_file_src)) {
        html = `<div class="live-chat-agent-message-wrapper" id=${message_id}>
                        <div class="live-chat-agent-image">${get_user_initial(sender_name)}</div>
                        <div class="live-chat-agent-message-bubble-image-attachment live-chat-attachment-div">
                            <div class="slideshow-container" value="1">
                                <div class="mySlides livechat-slider-card">
                                    ${get_video_path_html(
                                        attached_file_src,
                                        img_file
                                    )}
                                    <div style="text-align: left;">
                                        <h5 style="overflow-wrap: break-word; ">${
                                            attached_file_src.split("/")[
                                                len - 1
                                            ]
                                        }</h5>`;

        if (message != "") {
            html += `<p style="overflow-wrap: break-word; text-align: ${text_direction};" class="live-chat-attachment-text">${message}</p>`;
        }

        html += `</div>
                    </div>
                </div>
                
                </div>
                <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">
                ${time}
                ${blue_ticks}
                ${view_translation_html}</div></div>
                </div>`;
    }

    return html;
}

function livechat_linkify(inputText) {
    //inputText.replace(/&nbsp;/g, '');
    var replacedText,
        replacePattern1,
        replacePattern2,
        replacePattern3,
        replacePattern4;

    var anchor_tag_pattern = /<a[\s]+([^>]+)>((?:.(?!\<\/a\>))*.)<\/a>/gim;

    var is_matched = anchor_tag_pattern.test(inputText);

    replacedText = inputText;
    if (!is_matched) {
        //URLs starting with http://, https://, or ftp://
        replacePattern1 =
            /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=_|!:,.;]*[-A-Z0-9+&@#\/%=_|])/gim;
        replacedText = replacedText.replace(
            replacePattern1,
            '<a href="$1" target="_blank">$1</a>'
        );

        //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
        replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
        replacedText = replacedText.replace(
            replacePattern2,
            '$1<a href="http://$2" target="_blank">$2</a>'
        );
    }

    // Change email addresses to mailto:: links.
    replacePattern3 =
        /(([a-zA-Z0-9\-\_\.])+@[a-zA-Z\_]+?(\.[a-zA-Z]{2,6})+)/gim;
    replacedText = replacedText.replace(
        replacePattern3,
        '<a href="mailto:$1">$1</a>'
    );

    // Change mobile numbers to tel:: links.
    replacePattern4 = /(^[6-9][0-9]{9}(\s)*(?!.))/g;
    replacedText = replacedText.replace(replacePattern4, function(number) {
        return '<a href="tel:' + number + '">' + number + "</a>";
    });

    return replacedText;
}

function get_response_user_html(
    sentence,
    sender_name,
    is_blue_tick,
    session_id,
    time = return_time(),
    message_id = "",
    language = "en"
) {
    // sentence = stripHTML(sentence);
    sentence = sentence.replace(new RegExp("\r?\n", "g"), "<br>");
    sentence = livechat_linkify(sentence);

    var blue_ticks =
        '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path class="doubletick_livechat_agent-' +
        session_id +
        '"  d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                              <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                              </svg>';

    if (is_blue_tick) {
        blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                              <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                              </svg>';
    }

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_translated_text(this);>View Translated</a>\
                                  </div>';
    }

    var html =
        '<div class="live-chat-agent-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-agent-image">' +
        get_user_initial(sender_name) +
        '</div>\
                    <div class="live-chat-agent-message-bubble" style="text-align: ' + text_direction + '">\
                        ' +
        sentence +
        '\
                    </div>\
                    <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">\
                        ' +
        time +
        "\
                        " +
        blue_ticks +
        "\
                    </div>" +
        view_translation_html + "</div></div>";

    return html;
}

function get_response_server_html(sentence, sender_name, is_guest_agent_message = false, time = return_time(), message_id = "", language = "en") {


    sentence = sentence.replace("<p>", "");
    sentence = sentence.replace("</p>", "");
    sentence = sentence.replace("<strong>", "<b>");
    sentence = sentence.replace("</strong>", "</b>");
    sentence = sentence.replace("<em>", "<i>");
    sentence = sentence.replace("</em>", "</i>");
    sentence = sentence.replace("background-color:#ffffff; color:#000000", "");
    sentence = sentence.replace("background-color:#ffffff;", "");
    sentence = stripHTML(sentence);
    sentence = livechat_linkify(sentence);

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    var message_bubble = "";
    if (is_guest_agent_message)
        message_bubble =
        '<div class="live-chat-client-message-bubble live-chat-client-message-bubble-blue-border" style="text-align: ' + text_direction + '">';
    else message_bubble = '<div class="live-chat-client-message-bubble" style="text-align: ' + text_direction + '">';

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${get_session_id()}`) == "true") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_original_text(this);>View Original</a>\
                                  </div>';
    }

    var html =
        '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-client-image">' +
        get_user_initial(sender_name) +
        "</div>" +
        '<div class="live-chat-client-name-with-message">' +
        sender_name +
        "</div>" +
        message_bubble +
        sentence +
        '\
                    </div>\
                    <div class="livechat-client-message-translate-wrapper"><div class="live-chat-client-message-time">' +
        time +
        "</div>" +
        view_translation_html + "</div></div>";
    return html;
}

function append_response_user(sentence, is_blue_tick, message_id, language, time = return_time()) {
    sentence = stripHTML(sentence);
    sentence = sentence.replace(new RegExp("\r?\n", "g"), "<br/>");
    sentence = livechat_linkify(sentence);

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    const session_id = get_session_id();
    var blue_ticks =
        '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#4d4d4d"/>\
                              <path class="doubletick_livechat_agent-' +
        session_id +
        '" d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#4d4d4d"/>\
                              </svg>';

    if (is_blue_tick) {
        blue_ticks =
            '<svg style="margin:-5px 5px 0px 5px;" width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">\
                              <path d="M3.45714 6.51434L1.07304 4.18025C0.827565 3.93994 0.429579 3.93994 0.184102 4.18025C-0.0613675 4.42056 -0.0613675 4.81022 0.184102 5.05053L3.01268 7.81976C3.25815 8.06007 3.65614 8.06007 3.90161 7.81976L10.8159 1.05053C11.0614 0.810204 11.0614 0.420567 10.8159 0.18024C10.5704 -0.0600801 10.1724 -0.0600801 9.92697 0.18024L3.45714 6.51434Z" fill="#0254D7"/>\
                              <path d="M5.6412 8.51434L5.07684 7.99999C4.83137 7.75969 4.42956 8.27404 4.18409 8.51434C3.93862 8.75465 3.93864 8.62614 4.18411 8.86645L5.19673 9.81976C5.44221 10.0601 5.8402 10.0601 6.08567 9.81976L13 3.05053C13.2454 2.8102 13.2454 2.42057 13 2.18024C12.7545 1.93992 12.3565 1.93992 12.111 2.18024L5.6412 8.51434Z" fill="#0254D7"/>\
                              </svg>';
    }

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_translated_text(this);>View Translated</a>\
                                  </div>';
    }

    var html =
        '<div class="live-chat-agent-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-agent-image">' +
        get_user_initial() +
        '</div>\
                    <div class="live-chat-agent-message-bubble" style="text-align: ' + text_direction + '">\
                        ' +
        sentence +
        '\
                    </div>\
                    <div class="livechat-agent-message-translate-wrapper"><div class="live-chat-agent-message-time">\
                        ' +
        time +
        "\
                        " +
        blue_ticks +
        "\
                    </div>" +
        view_translation_html + "</div></div>";

    $(`#style-2_${session_id}`).append(html);

    scroll_to_bottom();
}

function update_canned_response_arr_and_blacklisted_keywords(
    canned_arr,
    blacklisted_keywords,
    customer_blacklisted_keywords,
) {
    state.cannned_response = canned_arr;
    state.blacklisted_keywords = blacklisted_keywords;
    state.customer_blacklisted_keywords = customer_blacklisted_keywords;
}

function append_response_server(
    sentence,
    session_id,
    message_id = "",
    language,
    livechat_customer_name = state.chat_data.customer_name,
    time = return_time()
) {
    sentence = sentence.replace("<p>", "");
    sentence = sentence.replace("</p>", "");
    sentence = sentence.replace("<strong>", "<b>");
    sentence = sentence.replace("</strong>", "</b>");
    sentence = sentence.replace("<em>", "<i>");
    sentence = sentence.replace("</em>", "</i>");
    sentence = sentence.replace("background-color:#ffffff; color:#000000", "");
    sentence = sentence.replace("background-color:#ffffff;", "");
    sentence = stripHTML(sentence);
    sentence = livechat_linkify(sentence);

    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        language = localStorage.getItem(`agent_language-${session_id}`)
    }

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_original_text(this);>View Original</a>\
                                  </div>';
    }

    var html =
        '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-client-image">' +
        get_user_initial(livechat_customer_name) +
        "</div>" +
        '<div class="live-chat-client-name-with-message">' +
        livechat_customer_name +
        '</div><div class="live-chat-client-message-bubble" style="text-align: ' + text_direction + '">' +
        sentence +
        '\
                    </div>\
                    <div class="livechat-client-message-translate-wrapper"><div class="live-chat-client-message-time">' +
        time +
        "</div>" +
        view_translation_html + "</div></div>";

    check_and_update_message_diffrentiator(session_id);
    $(`#style-2_${session_id}`).append(html);
    hide_customer_typing_in_chat();
    scroll_to_bottom();
}

function append_supervisor_message(
    sentence,
    session_id,
    sender_name,
    reply_message_id,
    sender_username,
    time = return_time()
) {
    try {

        sentence = stripHTML(sentence);
        sentence = livechat_linkify(sentence);
        sentence = sentence.trim();

        var reply_message_for = document.getElementById(reply_message_id).classList[0].split("-")[2];
        var children_elements = document.getElementById(reply_message_id).children;

        var actual_message_pos = 1;
        if (reply_message_for == "client") {
            actual_message_pos = 2;
        }
        var reply_element = children_elements.item(actual_message_pos);
        var actual_message = reply_element.outerHTML;
        document.getElementById(reply_message_id).removeChild(reply_element);

        var time_html = '';

        if (reply_message_for == "client") {
            var time_element = children_elements.item(actual_message_pos);
            if (time_element) {
                time_html = time_element.outerHTML;
                document.getElementById(reply_message_id).removeChild(time_element);
            }
        }

        var reply_message = '<div class="live-chat-' + reply_message_for + '-message-bubble-reply-wrapper">' +
            actual_message +
            '<div class="live-chat-' + reply_message_for + '-message-reply-text-container livechat-reply-message" sender=' + sender_username + '>\
                                <div class="live-chat-' + reply_message_for + '-message-reply-text-hover-text-div livechat-reply-message" sender=' + sender_username + '>\
                                    *This message is only visible to Agents, Supervisors & Admin*\
                                </div>\
                                <div class="live-chat-' + reply_message_for + '-message-reply-text-bubble livechat-reply-message" sender=' + sender_username + '>' +
            sentence +
            '</div>\
                                <div class="live-chat-' + reply_message_for + '-message-reply-time-div livechat-reply-message" sender=' + sender_username + '>' +
            time +
            '</div>\
                            </div>' +
            time_html +
            '</div>'
        $("#" + reply_message_id + ">div:nth-child(" + actual_message_pos + ")").after(reply_message);

        $('.livechat-reply-message').on('click', function(e) {
            redirect_to_internal_chat(e.target);
        })
    } catch (err) {}
}

function append_supervisor_file(
    attached_file_src,
    session_id,
    thumbnail_url,
    message,
    reply_message_id,
    sender_username,
    time = return_time()
) {

    try {
        message = stripHTML(message);
        var attachment_html = get_attachment_html(attached_file_src, session_id, thumbnail_url, message, time);

        var reply_message_for = document.getElementById(reply_message_id).classList[0].split("-")[2];
        var children_elements = document.getElementById(reply_message_id).children;

        var actual_message_pos = 1;
        if (reply_message_for == "client") {
            actual_message_pos = 2;
        }
        var reply_element = children_elements.item(actual_message_pos);
        var actual_message = reply_element.outerHTML;
        document.getElementById(reply_message_id).removeChild(reply_element);

        var time_html = '';

        if (reply_message_for == "client") {
            var time_element = children_elements.item(actual_message_pos);
            time_html = time_element.outerHTML;
            document.getElementById(reply_message_id).removeChild(time_element);
        }

        var reply_message = '<div class="live-chat-' + reply_message_for + '-message-bubble-reply-wrapper">' +
            actual_message +
            '<div class="live-chat-' + reply_message_for + '-message-reply-text-container livechat-reply-message" sender=' + sender_username + '>\
                                <div class="live-chat-' + reply_message_for + '-message-reply-text-hover-text-div livechat-reply-message" sender=' + sender_username + '>\
                                    *This message is only visible to Agents, Supervisors & Admin*\
                                </div>\
                                <div class="live-chat-' + reply_message_for + '-message-reply-text-bubble livechat-reply-message" sender=' + sender_username + '>' +
            attachment_html +
            '</div>\
                                <div class="live-chat-' + reply_message_for + '-message-reply-time-div livechat-reply-message" sender=' + sender_username + '>' +
            time +
            '</div>\
                            </div>' +
            time_html +
            '</div>'
        $("#" + reply_message_id + ">div:nth-child(" + actual_message_pos + ")").after(reply_message);

        $('.livechat-reply-message').on('click', function(e) {
            redirect_to_internal_chat(e.target);
        })
    } catch (err) {}
}

function get_attachment_html(
    attached_file_src,
    session_id,
    thumbnail_url,
    message,
    time = return_time()
) {

    if (message.trim() != "") {
        message = stripHTML(message);
        message = livechat_linkify(message);
        message = message.trim();
    }

    var len = attached_file_src.split('/').length;
    var attachment_html = "";
    const icons = get_icons();
    if (is_image(attached_file_src)) {
        var attachment_msg_html = '';
        if (message != '') {
            attachment_msg_html = '<p style="overflow-wrap: break-word;">' + message + '</p>';
        }

        attachment_html = '<div class="live-chat-agent-message-bubble-image-attachment">\
        <div class="slideshow-container" value="1">\
            <div class="mySlides livechat-slider-card">' +
            get_image_path_html_attach(attached_file_src) +
            '<div style="text-align: left;">\
                    <h5 style="overflow-wrap: break-word; ">' + attached_file_src.split('/')[len - 1] + '</h5>\
                    <a href="' + attached_file_src + '" target="_blank" download><span style="position: absolute; top: 8.5rem; right: 8px;"><svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M11.875 11.25H3.125C2.77982 11.25 2.5 11.5298 2.5 11.875C2.5 12.2202 2.77982 12.5 3.125 12.5H11.875C12.2202 12.5 12.5 12.2202 12.5 11.875C12.5 11.5298 12.2202 11.25 11.875 11.25Z" fill="#757575"></path>\
                    <path d="M2.5 10.625V11.875C2.5 12.2202 2.77982 12.5 3.125 12.5C3.47018 12.5 3.75 12.2202 3.75 11.875V10.625C3.75 10.2798 3.47018 10 3.125 10C2.77982 10 2.5 10.2798 2.5 10.625Z" fill="#757575"></path>\
                    <path d="M11.25 10.625V11.875C11.25 12.2202 11.5298 12.5 11.875 12.5C12.2202 12.5 12.5 12.2202 12.5 11.875V10.625C12.5 10.2798 12.2202 10 11.875 10C11.5298 10 11.25 10.2798 11.25 10.625Z" fill="#757575"></path>\
                    <path d="M7.50003 9.375C7.37046 9.37599 7.24378 9.33667 7.13753 9.2625L4.63753 7.5C4.50279 7.40442 4.41137 7.25937 4.38326 7.09658C4.35515 6.93379 4.39264 6.76649 4.48753 6.63125C4.5349 6.56366 4.59518 6.50611 4.66491 6.46194C4.73463 6.41777 4.81242 6.38785 4.89377 6.37391C4.97512 6.35996 5.05843 6.36227 5.13889 6.38069C5.21934 6.39911 5.29535 6.43329 5.36253 6.48125L7.50003 7.975L9.62503 6.375C9.75764 6.27555 9.92432 6.23284 10.0884 6.25628C10.2525 6.27973 10.4006 6.36739 10.5 6.5C10.5995 6.63261 10.6422 6.7993 10.6187 6.96339C10.5953 7.12749 10.5076 7.27555 10.375 7.375L7.87503 9.25C7.76685 9.33114 7.63526 9.375 7.50003 9.375Z" fill="#757575"></path>\
                    <path d="M7.5 8.125C7.33424 8.125 7.17527 8.05915 7.05806 7.94194C6.94085 7.82473 6.875 7.66576 6.875 7.5V2.5C6.875 2.33424 6.94085 2.17527 7.05806 2.05806C7.17527 1.94085 7.33424 1.875 7.5 1.875C7.66576 1.875 7.82473 1.94085 7.94194 2.05806C8.05915 2.17527 8.125 2.33424 8.125 2.5V7.5C8.125 7.66576 8.05915 7.82473 7.94194 7.94194C7.82473 8.05915 7.66576 8.125 7.5 8.125Z" fill="#757575"></path>\
                    </svg>\
                    </span></a>' +
            attachment_msg_html +
            '</div>\
            </div>\
        </div>\
    </div>';

    } else if (is_video(attached_file_src)) {

        var attachment_msg_html = '';
        if (message != '') {
            attachment_msg_html = '<p style="overflow-wrap: break-word;">' + message + '</p>';
        }

        attachment_html = '<div class="live-chat-agent-message-bubble-image-attachment">\
        <div class="slideshow-container" value="1">\
            <div class="mySlides livechat-slider-card">' +
            get_video_path_html(attached_file_src) +
            '<div style="text-align: left;">\
                    <h5 style="overflow-wrap: break-word; ">' + attached_file_src.split('/')[len - 1] + '</h5>\
                    <p style="overflow-wrap: break-word;">' + attachment_msg_html + '</p>\
                </div>\
            </div>\
        </div>\
    </div>';
    } else if (is_pdf(attached_file_src)) {

        var attachment_msg_html = '';
        if (message != '') {
            attachment_msg_html = '<div class="upload-file-text-area">' + message + '</div>';
        }

        attachment_html = '<div class="file-attachement-download">\
            <div style="width: 50px;  display: inline-block;">' +
            icons.pdf +
            '</div>\
            <div class="file-attachment-path"><span id="custom-text-attach">' + attached_file_src.split('/')[len - 1] + '</span>\
            </div>\
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">' +
            get_doc_path_html(attached_file_src) +
            '</div>' +
            attachment_msg_html +
            '</div>';

    } else if (is_docs(attached_file_src)) {

        var attachment_msg_html = '';
        if (message != '') {
            attachment_msg_html = '<div class="upload-file-text-area">' + message + '</div>';
        }

        attachment_html = '<div class="file-attachement-download">\
            <div style="width: 50px;  display: inline-block;">' +
            icons.doc +
            '</div>\
            <div class="file-attachment-path"><span id="custom-text-attach">' + attached_file_src.split('/')[len - 1] + '</span>\
            </div>\
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">' +
            get_doc_path_html(attached_file_src) +
            '</div>' +
            attachment_msg_html +
            '</div>';

    } else if (is_txt(attached_file_src)) {

        var attachment_msg_html = '';
        if (message != '') {
            attachment_msg_html = '<div class="upload-file-text-area">' + message + '</div>';
        }

        attachment_html = '<div class="file-attachement-download">\
            <div style="width: 50px;  display: inline-block;">' +
            icons.txt +
            '</div>\
            <div class="file-attachment-path"><span id="custom-text-attach">' + attached_file_src.split('/')[len - 1] + '</span>\
            </div>\
            <div style="width: 30px;cursor: pointer;  display: inline-block; float: right; margin-top: 12px;">' +
            get_doc_path_html(attached_file_src) +
            '</div>' +
            attachment_msg_html +
            '</div>';

    }

    return attachment_html;

}

function get_reply_private_html(reply_private_container, message_for) {
    var reply_private_initial_container = '';
    var reply_private_middle_container = '';
    var reply_private_end_container = '';
    if (reply_private_container) {
        reply_private_initial_container = '<div class="live-chat-' + message_for + '-message-time-reply-bubble-container">';
        reply_private_middle_container = '<div class="live-chat-reply-privately-message-time-container">\
                                            <button class="live-chat-reply-privately-message-button" onclick="reply_on_message_function(this);">\
                                                <svg width="17" height="16" viewBox="0 0 17 16" fill="none" xmlns="http://www.w3.org/2000/svg">\
                                                    <path d="M14.7773 12.5C14.7773 12.5 13.6273 6 7.77734 6V3.5L2.77734 8L7.77734 12.2V9.31563C10.9523 9.31563 13.1211 9.59375 14.7773 12.5Z" fill="#CBCACA"/>\
                                                </svg>Reply Privately</button>';
        reply_private_end_container = '</div></div>';

    }
    return [reply_private_initial_container, reply_private_middle_container, reply_private_end_container];
}

function append_guest_agent_response(
    sentence,
    session_id,
    agent_name,
    language,
    message_id = "",
    time = return_time()
) {
    sentence = sentence.replace("<p>", "");
    sentence = sentence.replace("</p>", "");
    sentence = sentence.replace("<strong>", "<b>");
    sentence = sentence.replace("</strong>", "</b>");
    sentence = sentence.replace("<em>", "<i>");
    sentence = sentence.replace("</em>", "</i>");
    sentence = sentence.replace("background-color:#ffffff; color:#000000", "");
    sentence = sentence.replace("background-color:#ffffff;", "");
    sentence = stripHTML(sentence);
    sentence = livechat_linkify(sentence);

    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        language = localStorage.getItem(`agent_language-${session_id}`)
    }

    let text_direction = "left";
    if (is_rtl_language(language)) {
        text_direction = "right";
    }

    var view_translation_html = "";

    if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
        view_translation_html = '<div class="livechat-agent-message-translate-text-div">\
                                    <a onclick=show_original_text(this);>View Original</a>\
                                  </div>';
    }

    var html =
        '<div class="live-chat-client-message-wrapper" id=' + message_id + '>\
                    <div class="live-chat-client-image">' +
        get_user_initial(agent_name) +
        "</div>" +
        '<div class="live-chat-client-name-with-message">' +
        agent_name +
        '</div>\
                    <div class="live-chat-client-message-bubble live-chat-client-message-bubble-blue-border" style="text-align: ' + text_direction + '">\
                        ' +
        sentence +
        '\
                    </div>\
                    <div class="livechat-client-message-translate-wrapper"><div class="live-chat-client-message-time">' +
        time +
        "</div>" +
        view_translation_html + "</div></div>";

    check_and_update_message_diffrentiator(session_id);
    $(`#style-2_${session_id}`).append(html);
    hide_customer_typing_in_chat();
    scroll_to_bottom();
    if (document.getElementById("query")) {
        if (is_mobile() == false) {
            autocomplete(
                document.getElementById("query"),
                state.cannned_response
            );
        }
    }
}

function check_and_update_message_diffrentiator(session_id) {
    let user_unseen_message = get_user_unseen_message(session_id);
    set_user_unseen_message(session_id, user_unseen_message + 1);
    append_message_diffrentiator(session_id);
}

function append_message_diffrentiator(session_id) {
    const unread_message_count = localStorage.getItem(
        `unread_message_count-${session_id}`
    );
    const is_msg_diff_present =
        get_is_message_diffrentiator_present(session_id);
    if (is_msg_diff_present) {
        $(`#customer-unread-message-diffrentiator-${session_id}`).html(
            `${state.user_unseen_message[session_id]} Unread Messages`
        );
    } else {
        $(`#customer-unread-message-diffrentiator-${session_id}`).remove();
        state.user_unseen_message[session_id] = parseInt(unread_message_count);
        // removing the previous diffrentiator if in case already present so that thier wont be more than one diffrentiator at any time
        if (unread_message_count > 0) {
            const html = get_unread_message_diffrentiator_html(
                unread_message_count,
                session_id
            );
            $(`#style-2_${session_id}`).append(html);
            set_is_message_diffrentiator_present(session_id, true);
        }
    }
}

function set_user_unseen_message(session_id, count) {
    // for storing user_unseen message for a current chat
    //a user_message will be unseen untill a user reply or switch to another chat
    state.user_unseen_message[session_id] = count;
}

function get_user_unseen_message(session_id) {
    if (!(session_id in state.user_unseen_message) ||
        isNaN(state.user_unseen_message[session_id])
    ) {
        state.user_unseen_message[session_id] = 0;
    }
    return state.user_unseen_message[session_id];
}
async function append_system_text_response(text_response, time, session_id, message_id = "") {
    text_response = stripHTML(text_response);
    let html;
    if (text_response.includes('Customer details') || text_response.includes('Reinitiating Request Sent')) {

        let translated_text = text_response;
        if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
            translated_text = await get_translated_text(message_id, text_response, session_id);
        }

        html = `<div class="live-chat-customer-details-update-message-div">
                    ${translated_text}
                </div>`;
    } else if (text_response.includes('Video Call') || text_response.includes('Cobrowsing') || text_response.includes('Voice Call')) {

        let translated_text = text_response;
        if (localStorage.getItem(`is_translated-${session_id}`) == "true") {
            translated_text = await get_translated_text(message_id, text_response, session_id);
        }

        html = get_video_call_text_response(text_response, translated_text);
    } else {
        html = get_system_text_response_html(text_response, time);
    }

    $(`#style-2_${session_id}`).append(html);
    scroll_to_bottom();
}

export function get_video_call_text_response(text, translated_text = "") {

    if (translated_text == "") {
        translated_text = text;
    }

    if (text.includes('Sent')) {
        return `<div class="livechat-vc-request-send-agent-message-toast">
                    ${translated_text}
                </div>`
    } else if (text.includes('Rejected')) {
        return `<div class="livechat-vc-call-request-reject-message-toast">
                    ${translated_text}
                </div>`
    } else if (text.includes('Accepted')) {
        return `<div class="livechat-vc-request-accept-message-toast">
                    ${translated_text}
                </div>`
    } else if (text.includes('Started') || text.includes('Joined')) {
        return `<div class="livechat-vc-call-start-message-toast">
                    ${translated_text}
                </div>`
    } else if (text.includes('Ended')) {
        return `<div class="livechat-vc-call-end-message-toast">
                    ${translated_text}
                </div>`
    }
    else if(text.includes('Request has been sent')) {
        return '';
    }
}

function autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/

    try {
        inp.replaceWith(inp.cloneNode(true));
        let element_id = inp.getAttribute('id');
        inp = document.getElementById(element_id);
    }
    catch (err) { }
    
    inp.addEventListener("input", function(e) {
        var a,
            b,
            i,
            val = this.value;
        /*close any already open lists of autocompleted values*/
        close_all_list();
        const theme_color = get_theme_color();
        if (!val) {
            document.getElementById("fill-submit-btn").style.fill =
                theme_color.two;
            return false;
        }
        document
            .getElementById("fill-submit-btn")
            .style.setProperty("fill", theme_color.one, "important");
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        a.setAttribute(
            "style",
            "height:fit-content;max-height:220px;overflow-x:hidden;overflow-y:auto;"
        );
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/

        var max_element_to_show = 0;
        let arr_value_list = [];
        for (i = 0; i < arr.length; i++) {
            let arr_key = "/" + arr[i]["key"];
            let arr_value = arr[i]["value"];
            let arr_status = arr[i]["status"];

            if (max_element_to_show > state.max_suggestions) {
                break;
            }

            if (val[0] == "/") {
                /*check if the item starts with the same letters as the text field value:*/
                let val1;
                if (val.length > 1) {
                    val1 = val.slice(1);
                } else {
                    val1 = val;
                }
                if (arr_key.toUpperCase().indexOf(val1.toUpperCase()) != -1) {
                    /*create a DIV element for each matching element:*/
                    let b = document.createElement("DIV");
                    b.setAttribute("class", "row");
                    b.setAttribute(
                        "style",
                        "margin:0px !important;border-bottom:1px solid #d4d4d4;padding:5px;color: var(--color-grey-4D);border-radius:5px;word-break:break-all"
                    );
                    b.setAttribute(
                        "onMouseOver",
                        "this.style.background='#e9e9e9';"
                    );
                    b.setAttribute(
                        "onMouseOut",
                        "this.style.background='#fff';this.style.color='var(--color-grey-4D)'"
                    );
                    arr_value_list.push(arr_value);
                    let arr_value1;
                    if (arr_value.length > 37) {
                        arr_value1 = arr_value.slice(0, 37);
                        arr_value1 += " ...";
                    } else {
                        arr_value1 = arr_value;
                    }
                    let arr_key1;
                    if (arr_key.length > 15) {
                        arr_key1 = arr_key.slice(0, 15);
                        arr_key1 += " ...";
                    } else {
                        arr_key1 = arr_key;
                    }
                    /*make the matching letters bold:*/
                    b.innerHTML = "<strong>" + arr_value + "</strong>";
                    b.innerHTML =
                        `
                          <div class="col s3" style="padding:0em !important">
                              ` +
                        arr_key1 +
                        `
                          </div>
                          <div class="col s9" style="padding:0em !important">
                              ` +
                        arr_value1 +
                        `
                          </div>`;

                    /*insert a input field that will hold the current array item's value:*/

                    // problem here is when text has ' or """
                    b.innerHTML += '<input type="hidden" >';
                    b.getElementsByTagName("input")[0].value = arr_value;

                    /*execute a function when someone clicks on the item value (DIV element):*/
                    b.addEventListener("click", function(e) {
                        /*insert the value for the autocomplete text field:*/
                        inp.value = this.getElementsByTagName("input")[0].value;
                        /*close the list of autocompleted values,
                        (or any other open lists of autocompleted values:*/
                        auto_resize();
                        close_all_list();
                        inp.focus();
                    });

                    a.appendChild(b);

                    max_element_to_show += 1;
                }
            } else {
                try {
                    document.getElementById(
                        "queryautocomplete-list"
                    ).style.display = "none";
                } catch (err) {}
                return;
            }
        }

        if (max_element_to_show == 0) {
            document.getElementById("queryautocomplete-list").style.display =
                "none";
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function(e) {
        var current_div = document.getElementById(
            this.id + "autocomplete-list"
        );
        if (current_div)
            current_div = current_div.getElementsByClassName("row");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            if (currentFocus >= current_div.length) {
                currentFocus = 0;
            }
            current_div[currentFocus].scrollIntoView({
                behaviour: "smooth",
                block: "nearest",
            });
            add_active(current_div);
        } else if (e.keyCode == 38) {
            //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            if (currentFocus < 0) {
                currentFocus = current_div.length - 1;
            }
            current_div[currentFocus].scrollIntoView({
                behaviour: "smooth",
                block: "nearest",
            });
            /*and and make the current item more visible:*/

            add_active(current_div);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                inp.value = "";
                /*and simulate a click on the "active" item:*/
                setTimeout(function() {
                    if (current_div) current_div[currentFocus].click();
                    currentFocus = -1;
                }, 500);
            }
        }
    });

    function add_active(current_div) {
        /*a function to classify an item as "active":*/
        if (!current_div) return false;
        /*start by removing the "active" class on all items:*/
        remove_active(current_div);
        if (currentFocus >= current_div.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = current_div.length - 1;
        /*add class "autocomplete-active":*/
        current_div[currentFocus].classList.add("autocomplete-active");
    }

    function remove_active(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function close_all_list(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function(e) {
        close_all_list(e.target);
    });
}

function get_suggestion_list() {
    let input_el;
    if (is_mobile()) {
        input_el = document.getElementById("query-mobile");
    } else {
        input_el = document.getElementById("query");
    }

    autocomplete(input_el, state.cannned_response);
}

function return_time() {
    var d = new Date();
    var hours = d.getHours().toString();
    var minutes = d.getMinutes().toString();
    var flagg = "AM";
    if (parseInt(hours) == 12) {
        flagg = "PM";
    }

    if (parseInt(hours) > 12) {
        hours = parseInt(hours) - 12;
        flagg = "PM";
    }

    hours = hours.toString();

    if (hours.length == 1) {
        hours = "0" + hours;
    }
    if (minutes.length == 1) {
        minutes = "0" + minutes;
    }

    var time = hours + ":" + minutes + " " + flagg;
    return time;
}
$(document).on("keyup", "#query", function(e) {
    var key = e.which;
    if (key == 13) {
        if (e.shiftKey) {
            const pos = get_cursor_position($(e.target)[0]);

            e.target.value = e.target.value.substring(0, pos.start) + '\n' + e.target.value.substring(pos.start, e.target.value.length);

            set_cursor_position($(e.target)[0], pos.start + 1, pos.end + 1);
            auto_resize();
            $(e.target).scrollTop($(e.target)[0].scrollHeight);
        } else {
            $("#submit-response").click();
        }

        return false;
    }
});

$(document).on("keyup", '#query-mobile', function(e) {
    var key = e.keyCode || e.which;

    if (key == 13) {
        const pos = get_cursor_position($(e.target)[0]);

        e.target.value = e.target.value.substring(0, pos.start) + '\n' + e.target.value.substring(pos.start, e.target.value.length);

        set_cursor_position($(e.target)[0], pos.start + 1, pos.end + 1);
        auto_resize();
        $(e.target).scrollTop($(e.target)[0].scrollHeight);
    }
})

$(document).on("keyup", "#query-file", function(e) {
    var key = e.which;
    if (key == 13) {
        $("#submit-response-file").click();
        return false;
    }
});

$("#query-mobile").on("touchstart", function() {
    setTimeout(function() {
        scroll_to_bottom();
    }, 200);
});
$(window).focus(function() {
    state.user_in_other_tab = false;
});

$(window).blur(function() {
    state.user_in_other_tab = true;
});

function notification_sound() {
    var audio = new Audio("/static/LiveChatApp/img/swiftly.mp3");
    audio.play();
}

function send_notification(notification_msg) {
    
    if (!("Notification" in window)) {
        alert("This browser does not support desktop notification");
    } else if (Notification.permission === "granted") {
        notification_sound();
        var notification = new Notification(notification_msg);
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function(permission) {
            if (permission === "granted") {
                notification_sound();
                var notification = new Notification(notification_msg);
            }
        });
    }
}

function send_notification_for_chat_transfer(
    current_agent_name,
    agent,
    customer
) {
    var notification_msg =
        "Hi " +
        current_agent_name +
        "! " +
        agent +
        " has transferred a chat to you on LiveChat.";
    if (!("Notification" in window)) {
        alert("This browser does not support desktop notification");
    } else if (Notification.permission === "granted") {
        notification_sound();
        var notification = new Notification(notification_msg);
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function(permission) {
            if (permission === "granted") {
                notification_sound();
                var notification_msg = new Notification(notification_msg);
            }
        });
    }
}

function send_notification_message(notification_msg) {
    if (!("Notification" in window)) {
        alert("This browser does not support desktop notification");
    } else if (Notification.permission === "granted") {
        notification_sound();
        var notification = new Notification(notification_msg);
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(function(permission) {
            if (permission === "granted") {
                notification_sound();
                var notification = new Notification(notification_msg);
            }
        });
    }
}

async function send_notification_for_new_message(message) {
    let notification_msg = "You have new messages: " + message;
    try {
        await navigator.serviceWorker.ready.then(function(serviceWorker) {
            serviceWorker.showNotification("Cogno LiveChat", {
                body: notification_msg
            }); 
            notification_sound();
        });
        
    } catch (err) {
        send_notification_message(notification_msg);
    }
}

const register_service_worker = async () => {
    await navigator.serviceWorker.register('/service-worker-livechat.js').then(function() {
            return navigator.serviceWorker.ready;
        })
        .then(function(registration) {
            console.log(registration); // service worker is ready and working...
        });
};

const request_notification_permission = async () => {
    if (Notification.permission !== "granted") {
        await window.Notification.requestPermission();
        // value of permission can be 'granted', 'default', 'denied'
        // granted: user has accepted the request
        // default: user has dismissed the notification permission popup by clicking on x
        // denied: user has denied the request.
    }
};

const setup_service_worker = async () => {
    try {
        await request_notification_permission();
        await register_service_worker();
    } catch (err) {}
};

if ('serviceWorker' in navigator) {
    window.addEventListener('load', async function() {
        setup_service_worker();
    });
}

async function send_notification_for_new_assigned_customer(current_agent_name, notification_count) {
    
    let notification_msg = "";
    if (notification_count == 1) {
        notification_msg =
            "Hi " +
            current_agent_name +
            "! a customer has connected with you on LiveChat.";
    } else {
        notification_msg =
            "Hi " +
            current_agent_name +
            "! " +
            notification_count +
            " customers have connected with you on LiveChat.";
    }
    try {
        await navigator.serviceWorker.ready.then(function(serviceWorker) {
            serviceWorker.showNotification("Cogno LiveChat", {
                body: notification_msg
            }); 
            notification_sound();
        });
        
    } catch (err) {
        send_notification(notification_msg);
    }
}

function get_chat_info(session_id) {
    let json_string = JSON.stringify({
        session_id: session_id,
    });
    json_string = EncryptVariable(json_string);

    var CSRF_TOKEN = getCsrfToken();
    $.ajax({
        url: "/livechat/agent-bot/",
        type: "POST",
        headers: {
            "X-CSRFToken": CSRF_TOKEN
        },
        data: {
            json_string: json_string,
        },
        success: function(response) {
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == 200) {
                const category_enabled = response.category_enabled;
                const all_categories = response.all_categories_of_that_bot;
                const customer_obj = response.customer_obj;
                const is_form_enabled = response.is_form_enabled;
                const form = JSON.parse(response.form);
                const raise_ticket_form = JSON.parse(response.raise_ticket_form);

                if (category_enabled == false) {
                    document.getElementById(
                        "closing-category-div"
                    ).style.display = "none";
                }

                set_chat_data(
                    customer_obj.channel,
                    customer_obj.bot_pk,
                    customer_obj.username,
                    customer_obj.easychat_user_id,
                    category_enabled,
                    customer_obj.closing_category,
                    all_categories,
                    is_form_enabled,
                    form,
                    customer_obj.is_external,
                    raise_ticket_form,
                );

                document.getElementById("livechat-customer-name").innerHTML =
                    customer_obj.username;

                if (is_indexed_db_supported()) {
                    let chat_info = get_chat_info_store();

                    add_message_to_local_db({
                            channel: customer_obj.channel,
                            bot_id: customer_obj.bot_pk,
                            customer_name: customer_obj.username,
                            easychat_user_id: customer_obj.easychat_user_id,
                            category_enabled: category_enabled,
                            closing_category: customer_obj.closing_category,
                            all_categories: all_categories,
                            is_form_enabled: is_form_enabled,
                            form: form,
                            session_id: session_id,
                            is_external: customer_obj.is_external,
                            raise_ticket_form: raise_ticket_form,
                        },
                        chat_info.name
                    );
                }
                update_message_history(false);
                create_websocket();
                get_suggestion_list();
                set_end_chat_closing_category();
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            show_custom_notification("Your chats might be loading slower than usual. We recommend that you reload the page, if the problem still persists.", 10000);
            console.log(
                "Please report this error: " +
                errorthrown +
                xhr.status +
                xhr.responseText
            );
        },
        timeout: 5000
    });
}

function remove_chat(session_id, remove_session_id = true) {
    const chat_div = document.getElementById(`style-2_${session_id}`);

    if (chat_div != undefined) {
        chat_div.remove();
    }

    state.chat_history[session_id] = undefined;

    if (remove_session_id) {
        if (is_mobile()) {
            document.getElementById("query-mobile").value = "";
        } else {
            document.getElementById("query").value = "";
        }

        remove_saved_data_from_local_storage(session_id);

        set_session_id("");
    }
}

function remove_other_chat(session_id) {
    const chat_div = document.getElementById(`style-2_${session_id}`);

    if (chat_div != undefined) {
        chat_div.remove();
    }

    state.chat_history[session_id] = undefined;

    const unread_message_count = parseInt(
        localStorage.getItem(`unread_message_count-${session_id}`)
    );

    if (unread_message_count) {
        let unread_threads = localStorage.getItem(`unread_threads-${get_agent_username()}`);
        unread_threads =
            parseInt(unread_threads) > 0 ? parseInt(unread_threads) - 1 : 0;
        localStorage.setItem(`unread_threads-${get_agent_username()}`, unread_threads);

        update_document_title(unread_threads);
    }

    remove_saved_data_from_local_storage(session_id);
}

function remove_saved_data_from_local_storage(session_id) {
    localStorage.removeItem(`user_input-${session_id}`);
    localStorage.removeItem(`unread_message_count-${session_id}`);
    localStorage.removeItem(`customer_offline-${session_id}`);
    localStorage.removeItem(`ongoing_chat-${session_id}`);
    localStorage.removeItem(`cust_last_app_time_${session_id}`);

    localStorage.removeItem(`user_terminates_chat_dispose_${session_id}`);
    localStorage.removeItem(`session_inactivity_agent_${session_id}`);
    localStorage.removeItem(`session_inactivity_customer_${session_id}`);
    localStorage.removeItem(`session_inactivity_dispose_${session_id}`);
    localStorage.removeItem(`customer_faced_issue_${session_id}`);
    localStorage.removeItem(`auto_disposal-${session_id}`);
}

function open_customer_details() {
    document.getElementById(
        "live-chat-customer-details-sidebar"
    ).style.display = "block";
    document.getElementById("livechat-main-console").style.display = "none";
}

function close_customer_details() {
    document.getElementById(
        "live-chat-customer-details-sidebar"
    ).style.display = "none";
    document.getElementById("livechat-main-console").style.display = "block";
}

function close_livechat_console() {
    const session_id = get_session_id();
    set_prev_session_id(session_id);
    set_session_id("");
    document.getElementById("livechat-main-console").style.display = "none";
    document.getElementById(
        "live-chat-active-customers-sidebar"
    ).style.display = "block";
}

function set_end_chat_closing_category() {
    let value_of_closing_category = [];
    if (document.getElementById("category-closing-priority") != null) {
        value_of_closing_category = [];
        var select_options = document.getElementById(
            "category-closing-priority"
        );
        for (var i = 0; i < select_options.options.length; i++) {
            if (select_options.options[i].value) {
                value_of_closing_category.push({
                    id: parseInt(select_options.options[i].value),
                    name: select_options.options[i].innerHTML,
                });
            }
        }
    }
    const all_categories = state.chat_data.all_categories;
    if (
        JSON.stringify(value_of_closing_category) !=
        JSON.stringify(all_categories)
    ) {
        $("#category-closing-priority").html("");
        for (var i = 0; i < all_categories.length; ++i) {
            let newOption;
            if (
                all_categories[i].title == state.chat_data.closing_category.name
            ) {
                newOption = new Option(
                    all_categories[i].title,
                    all_categories[i].pk,
                    false,
                    true
                );
            } else {
                newOption = new Option(
                    all_categories[i].title,
                    all_categories[i].pk,
                    false,
                    false
                );
            }
            $("#category-closing-priority").append(newOption).trigger("change");
        }
    }
}

function get_user_initial(user_name = get_agent_name()) {
    try {
        return user_name.trim()[0].toUpperCase();
    } catch (err) {
        return "N";
    }
}

function format_time(seconds) {
    hours = parseInt(seconds / 3600);
    minutes = parseInt((seconds % 3600) / 60);
    seconds = parseInt(seconds % 60);
    var formatted_time = "";
    if (hours > 0) {
        formatted_time += hours.toString() + " : ";
    }
    if (minutes > 0) {
        if (minutes >= 10) {
            formatted_time += minutes.toString() + " : ";
        } else {
            formatted_time += "0" + minutes.toString() + " : ";
        }
    } else {
        formatted_time += "00 : ";
    }
    if (seconds > 0) {
        if (seconds >= 10) {
            formatted_time += seconds.toString();
        } else {
            formatted_time += "0" + seconds.toString();
        }
    } else {
        formatted_time += "00";
    }
    return formatted_time;
}

function get_customer_details_edit_btn(theme_color) {

    let session_id = get_session_id();

    if (IS_CUSTOMER_DETAILS_EDITING_ENABLED && (is_primary_agent(session_id)) && !has_customer_left_chat(session_id)) {
        let edit_btn_html = `<button id="livechat_customer_details_edit_btn" class="">
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="${theme_color.one}" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12.2417 6.58543L6.2702 12.5584C5.9498 12.8788 5.54835 13.1061 5.10877 13.216L2.81777 13.7887C2.45158 13.8803 2.11988 13.5486 2.21143 13.1824L2.78418 10.8914C2.89407 10.4518 3.12137 10.0504 3.44177 9.72996L9.41331 3.75701L12.2417 6.58543ZM13.6567 2.3435C14.4377 3.12455 14.4377 4.39088 13.6567 5.17193L12.9488 5.87833L10.1204 3.0499L10.8282 2.3435C11.6093 1.56245 12.8756 1.56245 13.6567 2.3435Z"></path>
                                </svg>
                            </button>`

        return edit_btn_html;
    }
    return '';
}

function get_voip_vc_button_html(voip_enabled, vc_enabled, theme_color) {

    let voip_html = `<button type="button" id="livechata_voip_call_initiate_btn" class="live-chat-voip-call-initiate-button">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M9.60982 10.3936C12.9341 13.7169 13.6882 9.87224 15.8047 11.9873C17.8453 14.0273 19.0181 14.436 16.4327 17.0206C16.1089 17.2808 14.0514 20.4119 6.82054 13.183C-0.411191 5.95331 2.71803 3.89368 2.97835 3.56994C5.56993 0.978184 5.97159 2.1578 8.01212 4.19775C10.1287 6.31373 6.28559 7.07032 9.60982 10.3936Z" fill="${theme_color.one}"/>
                        </svg>
                        Initiate Voice Call
                    </button>`

    let vc_html = `<button type="button" id="livechata_vc_call_initiate_btn" class="live-chat-voip-call-initiate-button">
                        <svg width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11.2705 11.8341C11.2705 13.079 10.2613 14.0882 9.01643 14.0882H4.50824C3.26334 14.0882 2.25415 13.079 2.25415 11.8341V6.19885C2.25415 4.95395 3.26334 3.94476 4.50824 3.94476H9.01643C10.2613 3.94476 11.2705 4.95395 11.2705 6.19885V11.8341Z" fill="${theme_color.one}"/>
                        <path d="M12.3976 10.8894V7.14349L14.3523 5.293C14.8911 4.78292 15.7787 5.1649 15.7787 5.90685V12.1261C15.7787 12.868 14.8911 13.25 14.3523 12.7399L12.3976 10.8894Z" fill="${theme_color.one}"/>
                        </svg>
    
                        Initiate Video Call
                    </button>`

    if (voip_enabled && vc_enabled) {

        return voip_html + vc_html;
    } else if (voip_enabled) {

        return voip_html;
    } else if (vc_enabled) {

        return vc_html;
    }

    return "";
}

function get_chat_report_button_html(IS_CHAT_ESCALATION_ENABLES, theme_color) {

    const guest_session = localStorage.getItem(`guest_session-${get_session_id()}`);

    if (!IS_CHAT_ESCALATION_ENABLED || guest_session == "true") {
        return "";
    } else {
        return `<button type="button" data-toggle="tooltip" data-target="#livechat-blacklist-report-modal" title="Report a customer to your supervisor for indecent behaviour. Be cautious as this will be evaluated properly!" class="btn" id="report-user-btn" style="border-color: ${theme_color.one}">
                    <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7.5 0.5C3.636 0.5 0.5 3.636 0.5 7.5C0.5 11.364 3.636 14.5 7.5 14.5C11.364 14.5 14.5 11.364 14.5 7.5C14.5 3.636 11.364 0.5 7.5 0.5ZM1.9 7.5C1.9 4.406 4.406 1.9 7.5 1.9C8.795 1.9 9.985 2.341 10.93 3.083L3.083 10.93C2.31424 9.95219 1.89747 8.74382 1.9 7.5ZM7.5 13.1C6.205 13.1 5.015 12.659 4.07 11.917L11.917 4.07C12.6858 5.04781 13.1025 6.25618 13.1 7.5C13.1 10.594 10.594 13.1 7.5 13.1Z" fill="${theme_color.one}"/>
                    </svg>                         
                    <span style="color: ${theme_color.one}">Report User</span>  
                </button>`;
    }
}

function get_transcript_btn_html(theme_color) {

   let transcript_option = localStorage.getItem(`transcript_option-${get_session_id()}`);
   const guest_session = localStorage.getItem(`guest_session-${get_session_id()}`);  
   
   if(!transcript_option) {
    localStorage.setItem(`transcript_option-${get_session_id()}`,true);
    transcript_option = 'true';
   }
   
   if (IS_AGENT_TRANSCRIPT_ENABLED && guest_session == "true") {
    return '';
   } else if(IS_AGENT_TRANSCRIPT_ENABLED && transcript_option == 'true'){
   return `<button type="button" id="transcript-button" class="livechat-vc-call-btns  live-chat-agent-sned-transcript-button " data-toggle="modal" data-target="#livechat-send-transcript-modal">
   <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
       <path d="M2.17688 14.3588L14.4604 8.30605C14.6586 8.20841 14.7401 7.96861 14.6425 7.77045C14.6035 7.69138 14.5395 7.6274 14.4604 7.58844L2.17713 1.53579C1.97897 1.43815 1.73917 1.51963 1.64152 1.7178C1.59882 1.80445 1.58893 1.90362 1.61366 1.997L2.83066 6.59275C2.87091 6.74473 2.99646 6.85905 3.15154 6.8849L8.6563 7.80275C8.72374 7.81399 8.7795 7.85851 8.8063 7.91903L8.8207 7.96714C8.83627 8.06053 8.78441 8.14958 8.70067 8.18455L8.6563 8.1973L3.12046 9.11994C2.96532 9.1458 2.83972 9.26018 2.79951 9.41224L1.61338 13.8977C1.55688 14.1113 1.6842 14.3302 1.89776 14.3867C1.99112 14.4114 2.09026 14.4015 2.17688 14.3588Z" fill="${theme_color.one}"/>
       </svg>
       <span style="color: ${theme_color.one}">Send Transcript</span>  
                </button>`;
   }
   else if(IS_AGENT_TRANSCRIPT_ENABLED && transcript_option == 'false')
   {
    return `<button type="button" id="transcript-button" class="livechat-vc-call-btns  live-chat-agent-sned-transcript-button disable-transcript-btn" data-toggle="modal" data-target="#livechat-send-transcript-modal">
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M2.17688 14.3588L14.4604 8.30605C14.6586 8.20841 14.7401 7.96861 14.6425 7.77045C14.6035 7.69138 14.5395 7.6274 14.4604 7.58844L2.17713 1.53579C1.97897 1.43815 1.73917 1.51963 1.64152 1.7178C1.59882 1.80445 1.58893 1.90362 1.61366 1.997L2.83066 6.59275C2.87091 6.74473 2.99646 6.85905 3.15154 6.8849L8.6563 7.80275C8.72374 7.81399 8.7795 7.85851 8.8063 7.91903L8.8207 7.96714C8.83627 8.06053 8.78441 8.14958 8.70067 8.18455L8.6563 8.1973L3.12046 9.11994C2.96532 9.1458 2.83972 9.26018 2.79951 9.41224L1.61338 13.8977C1.55688 14.1113 1.6842 14.3302 1.89776 14.3867C1.99112 14.4114 2.09026 14.4015 2.17688 14.3588Z" fill="${theme_color.one}"/>
        </svg>
        <span style="color: ${theme_color.one}">Send Transcript</span>  
                 </button>`;
   }
   return '';
}

function get_voip_vc_timer_icon(voip_info) {

    let voip_html = `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.60995 10.3936C12.9342 13.7169 13.6883 9.87224 15.8049 11.9873C17.8454 14.0273 19.0182 14.436 16.4329 17.0206C16.109 17.2808 14.0515 20.4119 6.82067 13.183C-0.411069 5.95331 2.71815 3.89368 2.97847 3.56994C5.57005 0.978184 5.97171 2.1578 8.01224 4.19775C10.1288 6.31373 6.28571 7.07032 9.60995 10.3936Z" fill="#10B981"/>
                    </svg>`

    let vc_html = `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11.2705 11.8341C11.2705 13.079 10.2613 14.0882 9.01643 14.0882H4.50824C3.26334 14.0882 2.25415 13.079 2.25415 11.8341V6.19885C2.25415 4.95395 3.26334 3.94476 4.50824 3.94476H9.01643C10.2613 3.94476 11.2705 4.95395 11.2705 6.19885V11.8341Z" fill="#10B981"/>
                    <path d="M12.3976 10.8894V7.14349L14.3523 5.293C14.8911 4.78292 15.7787 5.1649 15.7787 5.90685V12.1261C15.7787 12.868 14.8911 13.25 14.3523 12.7399L12.3976 10.8894Z" fill="#10B981"/>
                </svg>`
    if (voip_info.voip_type == 'video_call') {
        return vc_html;
    } else {
        return voip_html;
    }
}

function get_raise_ticket_btn_html(IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED, theme_color) {

    if (IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED) {

        return `<div class="livechat-tms-btn-container">
                    <div class="livechat-info-heading-div">
                        Ticket Information
                    </div>
                <button type="button " id="livechat_raise_ticket_btn" class="live-chat-details-action-buttons" onclick="load_raise_ticket_form();">
                    <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M8.33948 0.0168475C5.73858 0.19202 3.48502 1.94001 2.62982 4.44557C2.38836 5.153 2.31914 5.59055 2.29865 6.53901L2.28048 7.37999L2.09717 7.43458C1.49363 7.61432 0.956703 8.19799 0.8087 8.83527C0.730487 9.17199 0.730415 11.4986 0.808593 11.8353C0.956738 12.4731 1.46065 13.0367 2.06165 13.2367C2.24956 13.2992 2.38207 13.3063 3.36269 13.3063H4.45454L4.59426 13.2073C4.67112 13.1528 4.77417 13.048 4.82326 12.9744L4.9125 12.8407L4.92325 10.4287C4.93067 8.75644 4.922 7.97488 4.89487 7.88025C4.84357 7.70138 4.66319 7.49647 4.48445 7.41404C4.36301 7.35807 4.24271 7.34796 3.68986 7.34727L3.03838 7.34647V6.78675C3.03838 5.83445 3.1842 5.0434 3.49441 4.31315C3.61164 4.03715 3.8108 3.6501 3.92739 3.47167C3.95523 3.42906 3.99607 3.45174 4.14375 3.59199C4.4132 3.84774 4.59833 3.92205 4.96605 3.92194C5.34045 3.92183 5.46814 3.86111 5.86809 3.49279C6.62453 2.7962 7.39263 2.44375 8.37253 2.34369C9.54167 2.22427 10.7251 2.64244 11.6415 3.49881C12.0267 3.85875 12.1597 3.92183 12.534 3.92194C12.9012 3.92205 13.0868 3.84774 13.3547 3.59348C13.5718 3.38733 13.5438 3.36483 13.8539 3.99519C14.2907 4.88287 14.4616 5.66982 14.4616 6.79302V7.34647H13.8179C13.1168 7.34647 13.0005 7.37067 12.8073 7.55672C12.7516 7.61044 12.6749 7.71558 12.637 7.79029C12.5708 7.92115 12.5685 8.01705 12.5779 10.3834L12.5875 12.8407L12.6767 12.9744C12.7258 13.048 12.8288 13.1528 12.9056 13.2073C13.0448 13.306 13.0474 13.3063 13.7566 13.3175L14.4681 13.3287L14.4549 13.861C14.439 14.5072 14.3819 14.6747 14.0834 14.9517C13.748 15.2627 13.7724 15.259 11.991 15.2725L10.4306 15.2844L10.3253 15.0728C10.1853 14.7913 9.96108 14.5696 9.67814 14.4329L9.4461 14.3208H8.75H8.0539L7.82186 14.4329C7.52696 14.5753 7.30521 14.8004 7.16485 15.0997C7.06664 15.309 7.05436 15.3715 7.05436 15.662C7.05436 15.9581 7.06539 16.0116 7.17124 16.2298C7.31649 16.5293 7.59839 16.8008 7.88444 16.9168C8.07253 16.9931 8.14457 17 8.75 17C9.36257 17 9.4259 16.9937 9.62459 16.9135C9.89079 16.806 10.2393 16.4662 10.3406 16.2154L10.4094 16.045L12.0518 16.0343C13.6639 16.0237 13.6983 16.022 13.9221 15.94C14.4783 15.7361 14.9103 15.3046 15.1133 14.75C15.1791 14.5703 15.1929 14.444 15.2039 13.9191L15.217 13.3002L15.4291 13.2357C16.0218 13.0555 16.542 12.4783 16.6914 11.8353C16.7696 11.4986 16.7695 9.17199 16.6913 8.83527C16.5433 8.19817 16.0064 7.61432 15.4032 7.43469L15.2202 7.3802L15.2006 6.53909C15.1791 5.62261 15.1326 5.29937 14.9236 4.61679C14.3987 2.90203 13.1906 1.47536 11.588 0.677864C10.8409 0.306072 10.1203 0.104923 9.26762 0.0301077C8.85192 -0.00637592 8.71362 -0.00833238 8.33948 0.0168475Z" fill="${theme_color.one}"/>
                    </svg>
                    Raise a Ticket
                </button>
                <button type="button " id="livechat_view_ticket_btn" class="live-chat-details-action-buttons" data-toggle="modal" data-target="#livechat-view-ticket-modal">
                    <svg width="17" height="16" viewBox="0 0 17 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M6.52465 0.028036C4.47032 0.259876 2.71162 1.37899 1.66003 3.12351C1.2285 3.83937 0.960921 4.57113 0.807149 5.45609C0.725194 5.92759 0.732704 7.02027 0.8212 7.50435C1.19727 9.56163 2.40996 11.2199 4.22346 12.1567C5.19362 12.6579 6.07182 12.8694 7.1802 12.8686C8.5302 12.8676 9.63708 12.5337 10.7622 11.7882L11.1367 11.54L13.3126 13.7104C14.7801 15.1743 15.5291 15.9 15.6136 15.9397C15.7831 16.0196 16.1353 16.0202 16.2864 15.941C16.6628 15.7435 16.8354 15.3382 16.709 14.9482C16.6572 14.7885 16.5396 14.6648 14.4658 12.5867L12.2772 10.3937L12.519 10.0364C13.6799 8.32063 13.9348 6.17558 13.2141 4.18743C12.9779 3.53581 12.5271 2.77871 12.0389 2.21373C11.2259 1.27301 10.0752 0.546258 8.89604 0.228804C8.17456 0.034576 7.19866 -0.0480342 6.52465 0.028036ZM7.64299 1.62348C8.83327 1.75381 9.76184 2.19568 10.5932 3.02738C11.441 3.87557 11.892 4.83823 12.0046 6.03993C12.1052 7.11414 11.8174 8.20845 11.1828 9.16428C10.9193 9.56122 10.3011 10.1794 9.90413 10.4429C8.29904 11.5084 6.32713 11.5645 4.69566 10.5909C3.51837 9.88838 2.69015 8.70608 2.41797 7.33938C2.31839 6.83934 2.31839 6.04153 2.41797 5.54148C2.69866 4.1321 3.56672 2.92984 4.81723 2.21849C5.653 1.7431 6.70746 1.52106 7.64299 1.62348Z" fill="${theme_color.one}"/>
                    </svg>
                    View Tickets
                </button>
                </div>`;
    } else {

        return '';
    }
}

function get_cobrowsing_btn_html(theme_color) {
    if (IS_COBROWSING_ENABLED) {

        return `
            <button type="button" class="livechat-vc-call-btns live-chat-cobrowse-session-initiate-button" data-toggle="tooltip" data-placement="bottom" title="Assist the customer by viewing their screen" id="livechat_send_cobrowsing_request_btn">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="${theme_color.one}"/>
                </svg>
                Send Cobrowsing Request
            </button>
            <button type="button" style="border: none !important; color: #cbcaca !important;" class="livechat-vc-call-btns live-chat-cobrowse-session-initiate-button" data-toggle="tooltip" data-placement="bottom" title="Your profile is not configured for Cobrowser. Contact your admin to get access." id="livechat_not_eligible_cobrowsing_request_btn">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="${theme_color.one}"/>
            </svg>
                Send Cobrowsing Request
            </button>
            <button type="button" class="live-chat-cobrowse-session-connect-button " id="livechat_connect_cobrowsing_btn" style="display: none;">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="#10B981"/>
                </svg>
                Connect Session 
            </button>
            <div class=" live-chat-cobrowse-session-ingoing-button" style="display: none; align-items: center; gap: 16px;" id="livechat_ongoing_cobrowsing_div">
                <div class="live-chat-cobrowse-session-ongoing-text-div" style="display: block;">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 2.5C14.1421 2.5 17.5 5.85786 17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5ZM9.37691 6.25C9.03173 6.25 8.75191 6.52982 8.75191 6.875V10.625C8.75191 10.9702 9.03173 11.25 9.37691 11.25H11.875C12.2202 11.25 12.5 10.9702 12.5 10.625C12.5 10.2798 12.2202 10 11.875 10H10.0019V6.875C10.0019 6.52982 9.72209 6.25 9.37691 6.25Z" fill="${theme_color.one}"/>
                    </svg>
                    <span class="time-elapsed-minutes" id="livechat_cobrowsing_time" style="color: ${theme_color.one}">0</span>
                </div>
                <button class="livechat-vc-call-btns " style="display: flex;" id="livechat_cobrowsing_reconnect_btn">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="${theme_color.one}"/>
                    </svg>
                    Reconnect
                </button>
            </div>
            <button type="button" class="live-chat-cobrowse-session-request-sent-button" style="display: none;" id="livechat_cobrowsing_request_sent_btn">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="#F59E0B"/>
                </svg>
                Request Sent
            </button>
            <button type="button" class="livechat-vc-call-btns live-chat-cobrowse-session-resend-button" id="livechat_resend_cobrowsing_request_btn" style="display: none;">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="${theme_color.one}"/>
                </svg>
                Resend Cobrowsing Request
            </button>
            <button type="button" style="border: none !important; color: #cbcaca !important;" class="livechat-vc-call-btns live-chat-cobrowse-session-initiate-button" data-toggle="tooltip" data-placement="bottom" title="Not supported for the end customer's channel" id="livechat-not-supported-cobrowsing-btn">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M2.5 5.16801C2.5 3.6946 3.6946 2.5 5.168 2.5H14.832C16.3054 2.5 17.5 3.6946 17.5 5.16801V14.832C17.5 16.3054 16.3054 17.5 14.832 17.5H5.168C3.6946 17.5 2.5 16.3054 2.5 14.832V5.16801ZM6.89532 11.8996H11.0622C12.0285 11.8996 12.8121 12.6832 12.8121 13.6496C12.8121 14.6161 12.0285 15.3996 11.0622 15.3996H6.89532C5.92894 15.3996 5.14534 14.6161 5.14534 13.6496C5.14534 12.6832 5.92894 11.8996 6.89532 11.8996ZM5.88053 10.3547C6.04389 10.4168 6.03872 10.6464 5.87275 10.7013L5.45157 10.8405L5.83838 11.2356C5.92201 11.3209 5.91958 11.457 5.83302 11.5395C5.74639 11.6219 5.60845 11.6196 5.52481 11.5342L5.11223 11.1128L4.88218 11.4693C4.79363 11.6065 4.58139 11.5716 4.5429 11.4134L4.20555 10.0274C4.17043 9.88304 4.31397 9.75911 4.45447 9.81246L5.88053 10.3547ZM10.2952 6.49945H14.462C15.4284 6.49945 16.212 7.28305 16.212 8.24946C16.212 9.21603 15.4284 9.99943 14.462 9.99943H10.2952C9.32881 9.99943 8.5452 9.21603 8.5452 8.24946C8.5452 7.28305 9.32881 6.49945 10.2952 6.49945ZM9.28041 4.95457C9.44374 5.01666 9.43859 5.2463 9.27262 5.30115L8.85145 5.44036L9.23824 5.83543C9.32188 5.92081 9.31945 6.05691 9.23289 6.13941C9.14626 6.22182 9.0083 6.21947 8.92466 6.13405L8.51208 5.71268L8.28205 6.06919C8.19347 6.20638 7.98124 6.17143 7.94277 6.01324L7.60539 4.62723C7.57028 4.4829 7.71384 4.35897 7.85431 4.41234L9.28041 4.95457Z" fill="${theme_color.one}"/>
                </svg>
                Send Cobrowsing Request
            </button>
        `
    }

    return '';
}

function get_chat_details_card(joined_time, joined_date, category) {
    return `<div class="livechat-details-card-div">
                <div class="livechat-chat-assign-details-container">
                    <div class="livechat-info-heading-div">
                        Chat Details

                    </div>
                <div class="livechat-chat-assign-details-text-wrapper">
                    <div class="livechat-chat-assign-details-item-wrapper">
                        <div class="livechat-chat-assign-details-heading-label">Chat initiated at :</div>
                        <div class="livechat-chat-assign-details-heading-data-label">${joined_time}</div>

                    </div>
                        </div>
                <div class="livechat-chat-assign-details-text-wrapper">
                    <div class="livechat-chat-assign-details-item-wrapper">
                        <div class="livechat-chat-assign-details-heading-label">Chat initiated on :</div>
                        <div class="livechat-chat-assign-details-heading-data-label">${joined_date}</div>
                    </div>
                </div>
                <div class="livechat-chat-assign-details-text-wrapper">
                    <div class="livechat-chat-assign-details-item-wrapper">
                        <div class="livechat-chat-assign-details-heading-label">Category :</div>
                        <div class="livechat-chat-assign-details-heading-data-label">${category}</div>
                    </div>
                </div>
            </div>
        </div>`;
}

function get_email_details_card(email_initiated_at, email_initiated_on, category) {
    return `<div class="livechat-details-card-div ">
                  <div class="livechat-chat-assign-details-container ">
                      <div class="livechat-info-heading-div ">
                        Email Details
  
                      </div>
                  <div class="livechat-chat-assign-details-text-wrapper ">
                      <div class="livechat-chat-assign-details-item-wrapper ">
                          <div class="livechat-chat-assign-details-heading-label ">1st Email initiated at :</div>
                          <div class="livechat-chat-assign-details-heading-data-label ">${email_initiated_at}</div>
  
                      </div>
                          </div>
                  <div class="livechat-chat-assign-details-text-wrapper ">
                      <div class="livechat-chat-assign-details-item-wrapper ">
                          <div class="livechat-chat-assign-details-heading-label ">Email initiated on :</div>
                          <div class="livechat-chat-assign-details-heading-data-label ">${email_initiated_on}</div>
                      </div>
                  </div>
                  <div class="livechat-chat-assign-details-text-wrapper ">
                      <div class="livechat-chat-assign-details-item-wrapper ">
                          <div class="livechat-chat-assign-details-heading-label ">Category :</div>
                          <div class="livechat-chat-assign-details-heading-data-label ">${category}</div>
                      </div>
                  </div>
              </div>
          </div>`;
}

function get_assignee_details_card(assigned_agent, previous_assigned_agent) {
    return `<div class="livechat-details-card-div">
    <div class="livechat-chat-assign-details-container">
        <div class="livechat-info-heading-div">
            Assignee details

        </div>
        <div class="livechat-chat-assign-details-text-wrapper">
            <div class="livechat-chat-assign-details-item-wrapper">
                <div class="livechat-chat-assign-details-heading-label">Currently assigned agent :</div>
                <div class="livechat-chat-assign-details-heading-data-label">${assigned_agent}</div>

            </div>
        </div>
        <div class="livechat-chat-assign-details-text-wrapper">
            <div class="livechat-chat-assign-details-item-wrapper">
                <div class="livechat-chat-assign-details-heading-label">Previously assigned agent :</div>
                <div class="livechat-chat-assign-details-heading-data-label">${previous_assigned_agent}</div>

            </div>
        </div>`;
}

function get_perform_actions_card(voip_info, VC_ENABLED, IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED, IS_CHAT_ESCALATION_ENABLED, theme_color) {
    return `<div class="livechat-details-card-div">
            <div class="live-chat-voip-call-initiate-container live-chat-action-btn-container-container">
            <div class="live-chat-voip-call-initiate-div" id="live_chat_voip_call_initiate_div" style="display: none;">
                <div class="livechat-info-heading-div">
                    Perform Actions
                </div>
                ${get_voip_vc_button_html(voip_info.is_enabled, VC_ENABLED, theme_color)}
                <div class="live-chat-voip-call-request-sent-text-div live-chat-voip-call-connect-div" id="live_chat_voip_call_request_sent_div">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.6097 10.3936C12.9339 13.7169 13.6881 9.87224 15.8046 11.9873C17.8451 14.0273 19.0179 14.436 16.4326 17.0206C16.1088 17.2808 14.0513 20.4119 6.82042 13.183C-0.411313 5.95331 2.71791 3.89368 2.97823 3.56994C5.56981 0.978184 5.97147 2.1578 8.01199 4.19775C10.1286 6.31373 6.28547 7.07032 9.6097 10.3936Z" fill="#F59E0B"/>
                    </svg> Request Sent
                </div>

                <div class="live-chat-voip-call-request-sent-text-div live-chat-voip-call-connect-div" id="live_chat_video_call_request_sent_div">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.5 13.125C12.5 14.5057 11.3807 15.625 10 15.625H5C3.61929 15.625 2.5 14.5057 2.5 13.125V6.875C2.5 5.49429 3.61929 4.375 5 4.375H10C11.3807 4.375 12.5 5.49429 12.5 6.875V13.125Z" fill="#F59E0B"/>
                        <path d="M13.75 12.0773V7.92269L15.918 5.87032C16.5156 5.30459 17.5 5.72825 17.5 6.55114V13.4488C17.5 14.2717 16.5156 14.6954 15.918 14.1297L13.75 12.0773Z" fill="#F59E0B"/>
                    </svg> Request Sent
                </div>
                
                <div class="live-chat-voip-call-connect-div" id="live_chat_voip_call_connect_div">
                    <div class="live-chat-voip-call-connect-text-div" id="live_chat_voip_call_connect_text_div">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.60995 10.3936C12.9342 13.7169 13.6883 9.87224 15.8049 11.9873C17.8454 14.0273 19.0182 14.436 16.4329 17.0206C16.109 17.2808 14.0515 20.4119 6.82067 13.183C-0.411069 5.95331 2.71815 3.89368 2.97847 3.56994C5.57005 0.978184 5.97171 2.1578 8.01224 4.19775C10.1288 6.31373 6.28571 7.07032 9.60995 10.3936Z" fill="#10B981"/>
                        </svg> Voice Call accepted
                    </div>
        
                    <button type="button" class="live-chat-voip-call-connect-button" id="livechat_voip_call_connect_btn">
                        Connect
                    </button>
                </div>

                <div style="padding: 0 !important;" class="live-chat-voip-call-connect-div" id="live_chat_video_call_connect_div">
                    <button type="button" class=" live-chat-video-call-connect-button " id="livechat_video_call_connect_btn">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.5 13.125C12.5 14.5057 11.3807 15.625 10 15.625H5C3.61929 15.625 2.5 14.5057 2.5 13.125V6.875C2.5 5.49429 3.61929 4.375 5 4.375H10C11.3807 4.375 12.5 5.49429 12.5 6.875V13.125Z" fill="#10B981"/>
                        <path d="M13.75 12.0773V7.92269L15.918 5.87032C16.5156 5.30459 17.5 5.72825 17.5 6.55114V13.4488C17.5 14.2717 16.5156 14.6954 15.918 14.1297L13.75 12.0773Z" fill="#10B981"/>
                        </svg>
                        
                        
                        Connect Video Call
                    </button>
                </div>
        
                <div class="live-chat-voip-call-connect-div" id="live_chat_voip_call_ongoing_div">
                    <div class="live-chat-voip-call-ongoing-text-div" id="live_chat_voip_call_ongoing_text_div">
                    ${get_voip_vc_timer_icon(voip_info)}
        
                        <span class="time-elapsed-minutes" id="voice_call_timer">00:00</span>
        
                    </div>
        
                    <div class="live-chat-voip-call-ongoing-button">
                        Ongoing...
                    </div>
                </div>
        
                <div class="live-chat-voip-call-connect-div" id="live_chat_voip_call_reject_div">
                    <div class="live-chat-voip-call-rejected-text-div" id="live_chat_voip_call_rejected_text_div">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M9.60946 10.3936C12.9337 13.7169 13.6878 9.87224 15.8044 11.9873C17.8449 14.0273 19.0177 14.436 16.4324 17.0206C16.1085 17.2808 14.051 20.4119 6.82018 13.183C-0.411557 5.95331 2.71766 3.89368 2.97798 3.56994C5.56956 0.978184 5.97123 2.1578 8.01175 4.19775C10.1283 6.31373 6.28522 7.07032 9.60946 10.3936Z" fill="#FF0000"/>
                            </svg>
                        <span>Request Rejected </span>
                    </div>

                    <button type="button" class="live-chat-voip-call-request-resend-button" id="voip_resend_request_btn">
                        Resend Request
                    </button>
                </div>
                <div class="live-chat-voip-call-connect-div" id="live_chat_video_call_reject_div" style="padding: 0 !important;">
                    <button type="button" class="livechat-vc-call-btns live-chat-video-call-resend-button" id="video_call_resend_request_btn" style="display: inline-flex;">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12.5 13.125C12.5 14.5057 11.3807 15.625 10 15.625H5C3.61929 15.625 2.5 14.5057 2.5 13.125V6.875C2.5 5.49429 3.61929 4.375 5 4.375H10C11.3807 4.375 12.5 5.49429 12.5 6.875V13.125Z" fill="${theme_color.one}"></path>
                            <path d="M13.75 12.0773V7.92269L15.918 5.87032C16.5156 5.30459 17.5 5.72825 17.5 6.55114V13.4488C17.5 14.2717 16.5156 14.6954 15.918 14.1297L13.75 12.0773Z" fill="${theme_color.one}"></path>
                        </svg> 
                        Resend Video Call
                    </button>
                </div>
                ${get_chat_report_button_html(IS_CHAT_ESCALATION_ENABLED, theme_color)}
                ${get_cobrowsing_btn_html(theme_color)}
                ${get_transcript_btn_html(theme_color)}
            </div>
            ${get_raise_ticket_btn_html(IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED, theme_color)}
        </div>
    </div>`;
}

function get_general_info_card(name, email, phone, client_id, country_img_src, theme_color) {

    let flag_image = "";
    if (country_img_src != "") {
        flag_image = `<img style="height: 15px;" id="country-code-flag" src="${country_img_src}">`;
    }

    return `<div style="display: flex; align-items: center;">
                <div class="live-chat-client-image"> ${get_user_initial(name)} </div>
            </div>
            <p class="live-chat-customer-name-text"> ${name} </p>
        </div>
            <button class="customer-details-refresh-button" id="refresh_customer_details_btn" style="pointer-events: auto;">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14.7015 5.29286C13.3432 3.93453 11.4182 3.15119 9.30154 3.36786C6.2432 3.67619 3.72654 6.15953 3.38487 9.21786C2.92654 13.2595 6.05154 16.6679 9.9932 16.6679C12.6515 16.6679 14.9349 15.1095 16.0015 12.8679C16.2682 12.3095 15.8682 11.6679 15.2515 11.6679C14.9432 11.6679 14.6515 11.8345 14.5182 12.1095C13.5765 14.1345 11.3182 15.4179 8.85154 14.8679C7.00154 14.4595 5.50987 12.9512 5.1182 11.1012C4.4182 7.86786 6.87654 5.00119 9.9932 5.00119C11.3765 5.00119 12.6099 5.57619 13.5099 6.48453L12.2515 7.74286C11.7265 8.26786 12.0932 9.16786 12.8349 9.16786H15.8265C16.2849 9.16786 16.6599 8.79286 16.6599 8.33453V5.34286C16.6599 4.60119 15.7599 4.22619 15.2349 4.75119L14.7015 5.29286Z" fill="#717171"/>
                </svg>
            </button>
            ${get_customer_details_edit_btn(theme_color)}
            </div>
            <div class="livechat-customer-personal-details-wrapper">
                <div class="livechat-customer-personal-details">
                    <form id='cust_details'>
                        <div class="livechat-customer-detail-items-wrapper">
                            <div class="livechat-customer-detail-icon-wrapper">
                                <div class="livechat-customer-detail-icon-div">
                                    <svg width="20" height="20" fill="${theme_color.one}" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.6 5C8.60588 5 7.8 5.80589 7.8 6.8C7.8 7.79411 8.60588 8.6 9.6 8.6C10.5941 8.6 11.4 7.79411 11.4 6.8C11.4 5.80589 10.5941 5 9.6 5ZM8.7 6.8C8.7 6.30294 9.10294 5.9 9.6 5.9C10.0971 5.9 10.5 6.30294 10.5 6.8C10.5 7.29705 10.0971 7.7 9.6 7.7C9.10294 7.7 8.7 7.29705 8.7 6.8Z" />
                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M11.85 9.49999L7.34998 9.49999C6.60441 9.49999 6 10.1044 6 10.85C6 11.8545 6.41307 12.6592 7.09093 13.2033C7.75807 13.7388 8.65223 14 9.59999 14C10.5478 14 11.4419 13.7388 12.1091 13.2033C12.7869 12.6592 13.2 11.8545 13.2 10.85C13.2 10.1044 12.5956 9.49999 11.85 9.49999ZM7.34998 10.4L11.85 10.4C12.0985 10.4 12.3 10.6015 12.3 10.85C12.3 11.5852 12.0079 12.1304 11.5457 12.5014C11.0728 12.881 10.3919 13.1 9.59999 13.1C8.80807 13.1 8.12722 12.881 7.65429 12.5014C7.19208 12.1304 6.9 11.5852 6.9 10.85C6.9 10.6015 7.10148 10.4 7.34998 10.4Z" />
                                        </svg>
                                </div>
                                <div class="livechat-customer-detail-label" style="display: none;">Customer Name </div>
                            </div>
                            <input type="text" id="customer-name-input" class="live-chat-content" value="${name}" readonly/>
                        </div>
                        <div class="livechat-customer-detail-items-wrapper">
                            <div class="livechat-customer-detail-icon-wrapper">
                                <div class="livechat-customer-detail-icon-div">
                                    <svg width="20" height="20" fill="${theme_color.one}" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                        <path d="M12.8553 6C13.6587 6 14.31 6.65129 14.31 7.45469V12.1097C14.31 12.9131 13.6587 13.5644 12.8553 13.5644H6.45469C5.65129 13.5644 5 12.9131 5 12.1097V7.45469C5 6.65129 5.65129 6 6.45469 6H12.8553ZM13.7281 8.30481L9.80251 10.6148C9.72664 10.6595 9.63557 10.6669 9.55463 10.6371L9.50749 10.6148L5.58188 8.30597V12.1097C5.58188 12.5917 5.97265 12.9825 6.45469 12.9825H12.8553C13.3374 12.9825 13.7281 12.5917 13.7281 12.1097V8.30481ZM12.8553 6.58187H6.45469C5.97265 6.58187 5.58188 6.97265 5.58188 7.45469V7.63041L9.655 10.0265L13.7281 7.62983V7.45469C13.7281 6.97265 13.3374 6.58187 12.8553 6.58187Z"/>
                                        </svg>
                                </div>
                                <div class="livechat-customer-detail-label" style="display: none;">Email </div>
                            </div>
                            <input type="email" id="customer-email-input" class="live-chat-content" value="${email}" readonly />
                        </div>
                        <div id="customer-phone-details-wrapper" class="livechat-customer-detail-items-wrapper customer-general-info-phoneno-div">
                            <div class="livechat-customer-detail-icon-wrapper">
                                <div class="livechat-customer-detail-icon-div">
                                    <svg width="20" height="20" fill="${theme_color.one}" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                        <path d="M8.64427 6.42965L8.32176 6.52686C7.73517 6.70367 7.30435 7.2046 7.21729 7.81104C7.08365 8.74196 7.38255 9.83008 8.10276 11.0775C8.82144 12.3223 9.6125 13.1245 10.4833 13.4754C11.0547 13.7056 11.7078 13.5816 12.155 13.1581L12.3992 12.9268C12.7266 12.6167 12.7741 12.1123 12.5102 11.7467L11.8998 10.9006C11.7307 10.6663 11.4313 10.5656 11.155 10.6501L10.2322 10.9322L10.2084 10.9369C10.1066 10.9517 9.87203 10.7317 9.57947 10.2249C9.2734 9.69481 9.20997 9.38484 9.29447 9.30493L9.76398 8.86711C10.1159 8.53899 10.2198 8.02327 10.0225 7.58445L9.72488 6.92233C9.53953 6.51002 9.07709 6.29918 8.64427 6.42965ZM9.31445 7.10684L9.6121 7.76896C9.73038 8.03206 9.66805 8.34127 9.45708 8.538L8.98642 8.9769C8.68533 9.26163 8.78506 9.74897 9.18976 10.4499C9.57055 11.1095 9.91795 11.4354 10.2912 11.3789L10.3472 11.3669L11.2866 11.0804C11.3787 11.0522 11.4785 11.0858 11.5348 11.1639L12.1453 12.01C12.2772 12.1928 12.2535 12.445 12.0898 12.6L11.8456 12.8313C11.5261 13.1339 11.0596 13.2224 10.6515 13.058C9.8874 12.7501 9.16524 12.0178 8.49247 10.8525C7.81832 9.68485 7.54549 8.69164 7.66272 7.87498C7.72491 7.44181 8.03264 7.08401 8.45163 6.95771L8.77414 6.8605C8.99055 6.79527 9.22177 6.90069 9.31445 7.10684Z" />
                                        </svg>
                                </div>
                                <div class="livechat-customer-detail-label" style="display: none;">Phone </div>
                            </div>
                            ${flag_image}
                            <input type="text" id="customer-phone-input" class="customer-phone-number live-chat-content" value="${!phone ? "Not provided" : phone}" readonly>
                        </div>
                        ${ !['Web', 'Android', 'iOS', 'WhatsApp', 'GoogleRCS', 'Email'].includes(state.chat_data.channel) ?
                        `<div class="livechat-customer-detail-items-wrapper">
                            <div class="livechat-customer-detail-icon-wrapper">
                                <div class="livechat-customer-detail-icon-div">
                                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="10" cy="10" r="10" fill="#F8F8F8"/>
                                <circle cx="6" cy="10" r="1" stroke="${theme_color.one}" stroke-width="0.5"/>
                                <circle cx="10" cy="10" r="1" stroke="${theme_color.one}" stroke-width="0.5"/>
                                <circle cx="14" cy="10" r="1" stroke="${theme_color.one}" stroke-width="0.5"/>
                                </svg>                                
                                </div>
                                <div class="livechat-customer-detail-label" style="display: none;">Other </div>
                            </div>
                            <input type="text" id="customer-other-input" class="live-chat-content" value="${client_id}" readonly/>
                        </div>` : '' }                      
                    </form>
                </div>
                <div class="customer-detail-cancel-save-btns" style="display: none;">
                    <button id="customer-detail-cancel-btn" class="customer-detail-cancel-btn" type="button">Cancel</button>
                    <button id="customer-detail-save-btn" class="customer-detail-save-btn" style="background-color:${theme_color.one}" type="submit">Save</button>
                </div>
            </div>
            <div class="live-chat-header">
                <p class="live-chat-content" id="alert_if_customer_is_not_online" style="display: none;">Looks like the customer is facing some connection issues.</p>
            </div>
        </div>`;
}

function get_customer_details(response) {
    let html = "";

    const {
        initial_time,
        joined_time,
        name,
        email,
        phone,
        category,
        assigned_agent,
        joined_date,
        previous_assigned_agent,
        show_details_from_processor,
        custom_data,
        client_id,
        phone_country_code,
    } = response;

    const theme_color = get_theme_color();

    if (fixed_date_string == "") fixed_date_string = joined_date;

    if (initialized_date == 0) {
        indicator_date = joined_date;

        if (indicator_date.trim() == todays_date.trim())
            $(".live-chat-day-date-indicator").html("Today");
        else $(".live-chat-day-date-indicator").html(indicator_date);
        initialized_date = 1;
    }

    html = `<div class="live-chat-customer-details-todo">`;

    html += `<div class="livechat-details-card-div">
                <div class="live-chat-customer-name">
                    <div class="livechat-info-heading-div">
                        General Info
                    </div>`;
    
    html += `<div style="display: flex; align-items: center;">
                <div class="live-chat-mobile-display back-arrow">
                    <img src="/static/LiveChatApp/img/mobile-back.svg" alt="Back arrow" id="live-chat-customer-details-closer" onclick="close_customer_details()">
                </div>`;

    let country_dict = {};
    let channel = state.chat_data.channel;
    let country_initial_code = "";

    if (name != "") {

        let phone_number_with_code = phone;
        let country_img_src = "";

        if(phone_country_code) {

            phone_number_with_code = "+" + phone_country_code + " " + phone;
            country_dict = state.country_codes.find( ({ dial_code }) => dial_code === "+" + phone_country_code );

            if(country_dict) {
                country_initial_code = country_dict['code'].toLowerCase();
                country_img_src = "/static/LiveChatApp/img/flags/"+country_initial_code+".svg";
            }
        } 

        html += get_general_info_card(name, email, phone_number_with_code, client_id, country_img_src, theme_color);
    } else {
        html += `</div>`;
    }

    html += `<div class="live-chat-header"><p class="live-chat-content" id="alert_if_customer_is_not_online" "href="#" data-toggle="tooltip" title="Seems like customer is facing some internal issues" style="margin-top: -0.8em;font-size: 15px;justify-content: space-evenly;display:none;color:red;"><b>Looks like the customer is facing some connection issues.</b></p></div>`;
    const voip_info = get_voip_info();

    let is_email_session = check_is_email_session(get_session_id());

    if (!is_email_session && (voip_info.is_enabled || VC_ENABLED || IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED || IS_COBROWSING_ENABLED || IS_AGENT_TRANSCRIPT_ENABLED || (IS_CHAT_ESCALATION_ENABLED && is_primary_agent(get_session_id())))) {
        html += get_perform_actions_card(voip_info, VC_ENABLED, IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED, IS_CHAT_ESCALATION_ENABLED, theme_color);
    } else if (is_email_session && IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED) {

        html += `<div class="livechat-details-card-div">
                    <div class="live-chat-voip-call-initiate-container live-chat-action-btn-container-container">
                    ${get_raise_ticket_btn_html(IS_AGENT_RAISE_TICKET_FUNCTIONALITY_ENABLED, theme_color)}
                    </div>
                </div>`;
    }

    if(is_email_session){
        html += get_email_details_card(response.email_initiated_at, response.email_initiated_on, category)
    } else {
        html += get_chat_details_card(joined_time, joined_date, category); 
    }

    html += get_assignee_details_card(assigned_agent, previous_assigned_agent);

        try {
            for (var i = 0; i < custom_data.length; i++) {
                html += `<div class="livechat-chat-assign-details-text-wrapper"> <div class="livechat-chat-assign-details-item-wrapper">`;
        
                html += `<div class="livechat-chat-assign-details-heading-label">${custom_data[i].key} :</div>
                            <div class="livechat-chat-assign-details-heading-data-label">${custom_data[i].value}</div>`;
                            
                html += `</div></div>`;
            }
        } catch (err) {
            console.log(err);
            console.log(
                "Please check the json format being returned in the processor."
            );
        }

    html += `</div></div></div></div>`;

    document.getElementById("live-chat-customer-details-sidebar").innerHTML =
        html;

    setTimeout(() => {
        set_voip_status();
        set_cobrowsing_status();
        check_chat_escalation_status();

        if(get_cobrowsing_info().status == 'ongoing' && get_cobrowsing_info().session_id == get_session_id()) {
            start_cobrowsing_timer(is_primary_agent(get_session_id()) ? "primary_agent" : "guest_agent");
        }
        handle_vc_status_for_guest_agent();

        $(function () {
            $('[data-toggle="tooltip"]').tooltip()
        })

        $("#refresh_customer_details_btn").on("click", () => {
            update_message_history(true);
        });
        $("#livechat_customer_details_edit_btn").click(function() {
            if(has_customer_left_chat(get_session_id())){
                showToast("Details can not be edited as customer has left the chat.", 2000);
                return;
            }

            $("#country-code-flag").css("display", "none");
            $("#customer-phone-details-wrapper").removeClass("customer-general-info-phoneno-div");

            initialize_country_code_selector(country_initial_code, 'customer-phone-input');

            $(this).addClass("livechat-customer-detail-edit-disabled-btn");
            $(".livechat-customer-personal-details-wrapper").addClass("livechat-customer-detail-edit-active");
            $(".livechat-customer-personal-details input").attr('readonly', false);
            $('#customer-other-input').addClass('livechat-disabled-input');

            if(state.chat_data.channel == 'WhatsApp' || state.chat_data.channel == 'GoogleRCS'){
                $("#customer-phone-input").attr('readonly', true);
                $("#customer-phone-input").click(function() {
                    showToast("For this channel, mobile number can not be changed.", 2000);
                });
            }
            
            state.original_name = $("#customer-name-input").val();
            state.original_email = $("#customer-email-input").val();
            state.original_phone = $("#customer-phone-input").val();
            $("#customer-name-input").focus().val('').val(state.original_name);
        });
        $(".customer-detail-cancel-save-btns button").click(function() {
            let btn_pressed = $(this).attr('id');
            if(btn_pressed == 'customer-detail-save-btn'){
                let updated_name = $("#customer-name-input").val();
                let updated_email = $("#customer-email-input").val();
                let updated_phone = $("#customer-phone-input").val();
                let phone_number = updated_phone;

                if (!validate_name('customer-name-input')){
                    showToast("Please enter a valid name", 2000);
                    return;      
                }
                if(!validate_email('customer-email-input')){
                    showToast("Please enter a valid email", 2000);
                    return;
                }
                if((state.chat_data.channel != 'WhatsApp' && state.chat_data.channel != 'GoogleRCS')){
                    // if(!validate_phone_number('customer-phone-input')){
                    //     showToast("Please enter a valid phone number", 2000);
                    //     return;
                    // }

                    let is_valid = $("#customer-phone-input").intlTelInput("isValidNumber");
                    let validation_err = $("#customer-phone-input").intlTelInput("getValidationError");
                    let error_text = "";
                    
                    if (!is_valid) {
                        if(state.country_code_error_map[validation_err] == undefined) {
                            validation_err = 0
                        }
                        error_text = state.country_code_error_map[validation_err]
                    
                    } else {
                        if ($("#customer-phone-input").intlTelInput("getSelectedCountryData").dialCode == "91") { 
                            if (error_text == "" && !validate_phone_number('customer-phone-input')) {
                                    error_text = state.country_code_error_map[0];
                            } else {
                                updated_phone = $("#customer-phone-input").intlTelInput("getNumber")
                            }
                        } else {
                            updated_phone = $("#customer-phone-input").intlTelInput("getNumber")
                        }
                        
                    }

                    if(error_text != "") {
                        showToast(error_text, 2000);
                        return;
                    }                    
                }
                if (updated_name == state.original_name && updated_email == state.original_email && updated_phone == state.original_phone){
                    showToast("Details are same", 2000);
                    return;
                }           
                update_customer_details(get_session_id(), updated_name, updated_email, updated_phone, phone_number);
            } else {

                reset_customer_details_editor(phone_country_code, phone, country_initial_code);
            }
        });

        $('#livechata_voip_call_initiate_btn').on('click', () => {
            send_voip_request_to_customer(false);
        })

        $('#voip_resend_request_btn').on('click', () => {
            send_voip_request_to_customer(true);
        })

        $('#livechat_voip_call_connect_btn').on('click', () => {
            connect_voip_call();
        })

        $('#livechat_video_call_connect_btn').on('click', () => {
            connect_voip_call();
        })

        $('#livechata_vc_call_initiate_btn').on('click', () => {
            send_vc_request_to_customer(false);
        })

        $('#video_call_resend_request_btn').on('click', () => {
            send_vc_request_to_customer(true);
        })

        $('#livechat_send_cobrowsing_request_btn').tooltip();
        $('#livechat_not_eligible_cobrowsing_request_btn').tooltip();

        $('#livechat_send_cobrowsing_request_btn').on('click', () => {
            send_cobrowsing_request_to_customer();
        })

        $('#livechat_resend_cobrowsing_request_btn').on('click', () => {
            send_cobrowsing_request_to_customer();
        })

        $('#livechat_connect_cobrowsing_btn').on('click', () => {
            connect_agent_to_cobrowsing();
        })

        $('#livechat_cobrowsing_reconnect_btn').on('click', () => {
            go_to_cobrowsing_page();
        })

        $("#report-user-btn").on('click', function(e) {
            $("#livechat-blacklist-report-modal").modal('show');
        })

    }, 200);

    ////////////// Temporary code
    try{
        var new_phone = phone
        new_phone = new_phone.substr(-10)
        Microsoft.CIFramework.searchAndOpenRecords("contact", `?$select=fullname,telephone1&$filter=mobilephone eq '${new_phone}'`, false ).then(
            function success(result) {
            res=JSON.parse(result);
                console.log(`The caller name is: ${res[0].fullname}, Telephone Number: ${res[0].telephone1}`);
                // perform operations on record retrieval and opening
            },
            function (error) {
                console.log(error.message);
                // handle error conditions
            }
        );
    } catch(err){}
    
    return {
        initial_time: initial_time,
        joined_time: joined_time,
        name: name,
        email: email,
        phone: phone,
        category: category,
        assigned_agent: assigned_agent,
        joined_date: joined_date,
        previous_assigned_agent: previous_assigned_agent,
        show_details_from_processor: show_details_from_processor,
        custom_data: custom_data,
        session_id: get_session_id(),
        client_id: client_id,
        phone_country_code: phone_country_code,
    };
}

function reset_customer_details_editor(phone_country_code, phone, country_initial_code) {

    $("#customer-name-input").val(state.original_name);
    $("#customer-email-input").val(state.original_email);
    $("#customer-phone-input").val(state.original_phone);

    $("#livechat_customer_details_edit_btn").removeClass("livechat-customer-detail-edit-disabled-btn");
    $(".livechat-customer-personal-details-wrapper").removeClass("livechat-customer-detail-edit-active");
    $(".livechat-customer-personal-details input").attr('readonly', true);
    $("#customer-other-input").removeClass("livechat-disabled-input");

    destroy_country_code_component();
    if(country_initial_code) {
        $("#customer-phone-input").val("+" + phone_country_code + " " + phone);
    }
    $("#country-code-flag").css("display", "block");
    $("#customer-phone-input").css({"border" : "none"});
    $("#customer-phone-details-wrapper").addClass("customer-general-info-phoneno-div");

}

function resize_chat_window() {
    let session_id = get_session_id();
    var parent_elem_height = document.getElementById(
        "livechat-main-console"
    ).clientHeight;
    var input_elem_height = document.getElementsByClassName(
        "live-chat-text-box-wrapper"
    )[0].clientHeight;
    var target_elem = document.getElementById(`style-2_${session_id}`);

    let footer_height = 0;
    if (SHOW_VERSION_FOOTER == "True") {
        footer_height = 28;
    }
    try {
        if (is_mobile()) {
            target_elem.style.height =
                window.innerHeight -
                (input_elem_height + 52 + 20 + footer_height + 70 + 41) +
                "px";
        } else {
            target_elem.style.height =
                parent_elem_height -
                (input_elem_height + 52 + 20 + footer_height + 21) +
                "px";
        }
    } catch (err) {
        // console.log(err);
    }
    if (!is_mobile()) {
        scroll_to_bottom();
    }
}

function update_customer_last_app_time(
    session_id,
    time_in_millisecond = Date.parse(new Date())
) {
    localStorage.setItem(
        "cust_last_app_time_" + session_id,
        time_in_millisecond
    );
}

function update_customer_last_ping(session_id = get_session_id()) {
    state.time_customer_ping[session_id] = new Date().getTime();
}

function scroll_to_bottom() {
    const session_id = get_session_id();
    const elem = document.getElementById(`style-2_${session_id}`);
    if (elem) {
        $(elem).scrollTop($(elem)[0].scrollHeight);
    }
}

function check_and_update_time_customer_ping(session_id) {
    if (
        !(session_id in state.time_customer_ping) ||
        isNaN(state.time_customer_ping[session_id])
    ) {
        state.time_customer_ping[session_id] = 0;
    }
}
function get_is_message_diffrentiator_present(session_id) {
    if (!(session_id in state.is_message_diffrentiator_present)) {
        state.is_message_diffrentiator_present[session_id] = false;
    }

    return state.is_message_diffrentiator_present[session_id];
}
function set_is_message_diffrentiator_present(session_id, is_present) {
    state.is_message_diffrentiator_present[session_id] = is_present;
}

function customer_last_ping_greater_than_fifteen_sec() {
    const session_id = get_session_id();
    let time_current = new Date().getTime();
    check_and_update_time_customer_ping(session_id);

    if (time_current - state.time_customer_ping[session_id] >= 5 * 1000) {
        if (state.chat_data.channel == "Web" || state.chat_data.channel == "Android") {
            state.show_alert_if_customer_is_not_online_bool = true;
        }
        try {
            document.getElementById("typing-text").innerHTML = "";
        } catch (err) {}
    } else {
        if (state.chat_data.channel == "Web" || state.chat_data.channel == "Android") {
            state.show_alert_if_customer_is_not_online_bool = false;
        }
    }

    let customer_not_online_div = document.getElementById(
        "alert_if_customer_is_not_online"
    );
    if (customer_not_online_div) {
        if (state.customer_left_chat[session_id]) {
            customer_not_online_div.innerHTML = "<b>Customer left the chat</b>";
        }

        if (state.show_alert_if_customer_is_not_online_bool) {
            customer_not_online_div.style.display = "block";
            localStorage.setItem(`customer_offline-${session_id}`, true);
        } else {
            if (state.chat_data.channel == "Web" || state.chat_data.channel == "Android") {
                customer_not_online_div.style.display = "none";
                localStorage.setItem(`customer_offline-${session_id}`, false);
            }
        }

        show_customer_status(0, session_id);
    }
}

function update_unread_message_count(session_id, is_internal_chat) {
    let unread_message_count = localStorage.getItem(
        `unread_message_count-${session_id}`
    );
    if (!unread_message_count) {
        unread_message_count = 0;
    }

    if (!is_internal_chat) {
        if (unread_message_count == 0) {
            let unread_threads = localStorage.getItem(`unread_threads-${get_agent_username()}`);

            if (!unread_threads) unread_threads = 0;

            unread_threads = parseInt(unread_threads) + 1;
            localStorage.setItem(`unread_threads-${get_agent_username()}`, unread_threads);

            update_document_title(unread_threads);
        }
    }

    unread_message_count = parseInt(unread_message_count);
    unread_message_count += 1;
    localStorage.setItem(
        `unread_message_count-${session_id}`,
        unread_message_count
    );
    return unread_message_count;
}

function is_customer_facing_issues(session_id) {
    let time_current = new Date().getTime();
    check_and_update_time_customer_ping(session_id);

    let customer_facing_issue = false;
    if (time_current - state.time_customer_ping[session_id] > 5 * 1000) {
        localStorage.setItem(`customer_offline-${session_id}`, true);
        state.customer_left_chat[session_id] = true;

        customer_facing_issue = true;
    } else {
        localStorage.setItem(`customer_offline-${session_id}`, false);
    }

    show_customer_status(0, session_id);

    return customer_facing_issue;
}

function guest_agent_session_accept() {
    var session_id = get_session_id();
    var json_string = JSON.stringify({
        bot_pk: state.chat_data.bot_id,
        session_id: get_session_id(),
    });

    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/guest-agent-accept/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                localStorage.removeItem(`guest_agent_timer-${session_id}`);
                remove_current_guest_session(session_id);
                localStorage.setItem(
                    `guest_session_status-${session_id}`,
                    "accept"
                );
                localStorage.setItem("is_guest_session-" + session_id, "true");
                if (!is_mobile()) {
                    document.getElementById(
                        "livechat-secondary-agent-accept-reject-header"
                    ).style.display = "none";
                    document.getElementById(
                        "livechat-text-box-div"
                    ).style.display = "inline-flex";
                    document.getElementById(
                        "livechat-text-box-div"
                    ).style.visibility = "visible";
                    document.getElementById(
                        "livechat-secondary-agent-header"
                    ).style.display = "flex";
                } else {
                    document.getElementById(
                        "livechat-secondary-agent-accept-reject-header"
                    ).style.display = "none";
                    document.getElementById(
                        "livechat-text-box-div"
                    ).style.display = "inline-flex";
                    document.getElementById(
                        "livechat-text-box-div"
                    ).style.visibility = "visible";
                    document.getElementById(
                        "livechat-mobile-exit-btn"
                    ).style.display = "block";
                    document.getElementById(
                        "livechat-mobile-exit-div"
                    ).style.display = "block";
                }

                let message =
                    response["assigned_agent"] + " has joined the chat.";
                let guest_message = message;
                let message_id = save_system_message(message, "GUEST_AGENT_JOINED", session_id);

                // Getting Agent Preferred Language
                let agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
                if(!agent_preferred_language)
                    agent_preferred_language = "en";

                message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: message,
                        text_message_customer: response.message_to_customer,
                        type: "text",
                        channel: state.chat_data.channel,
                        path: "",
                        event_type: "GUEST_AGENT_JOINED",
                        session_id: session_id,
                        agent_name: response["assigned_agent"],
                        agent_username: response["assigned_agent_username"],
                        language: agent_preferred_language,
                        message_id: message_id,
                    }),
                    sender: "System",
                });
                send_message_to_socket(message);

                send_message_to_guest_agent_socket(message);
            }
        }
    };
    xhttp.send(params);
}

function guest_agent_session_reject() {
    var session_id = get_session_id();
    var json_string = JSON.stringify({
        session_id: get_session_id(),
        bot_id: state.chat_data.bot_id,
    });

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/guest-agent-reject/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                localStorage.removeItem(`guest_agent_timer-${session_id}`);
                remove_current_guest_session(session_id);
                localStorage.setItem(
                    `guest_session_status-${session_id}`,
                    "reject"
                );
                let message =
                    response["agent_name"] + " has rejected the chat.";
                let guest_message = message;

                // Getting Agent Preferred Language
                let agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
                if(!agent_preferred_language)
                    agent_preferred_language = "en";

                message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: message,
                        agent_name: response["agent_name"],
                        type: "text",
                        channel: state.chat_data.channel,
                        path: "",
                        event_type: "GUEST_AGENT_REJECT",
                        session_id: session_id,
                        agent_username: response["assigned_agent_username"],
                        language: agent_preferred_language,
                    }),
                    sender: "System",
                });
                send_message_to_socket(message);

                send_message_to_guest_agent_socket(message);

                update_customer_list();

                go_to_chat(get_session_id(), true);
            }
        }
    };
    xhttp.send(params);

    remove_session_local_variables(session_id);

    if (is_indexed_db_supported()) {
        let message_history = get_message_history_store();
        let chat_info = get_chat_info_store();
        let customer_details = get_customer_details_store();

        delete_messages_from_local(message_history.name);
        delete_messages_from_local(chat_info.name);
        delete_messages_from_local(customer_details.name);
    }
}

function guest_agent_exit_chat() {
    var session_id = get_session_id();
    var json_string = JSON.stringify({
        session_id: get_session_id(),
        bot_id: state.chat_data.bot_id,
    });

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);

    var csrf_token = getCsrfToken();
    var xhttp = new XMLHttpRequest();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/guest-agent-exit/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status_code"] == "200") {
                localStorage.removeItem(`guest_agent_timer-${session_id}`);
                remove_current_guest_session(session_id);
                localStorage.setItem(
                    `guest_session_status-${session_id}`,
                    "exit"
                );
                let message = response["agent_name"] + " has left the chat.";
                let guest_message = message;
                let message_id = save_system_message(message, "GUEST_AGENT_EXIT", session_id);

                // Getting Agent Preferred Language
                let agent_preferred_language = localStorage.getItem(`agent_language-${session_id}`);
                if(!agent_preferred_language)
                    agent_preferred_language = "en";

                message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: message,
                        text_message_customer: response.message_to_customer,
                        type: "text",
                        channel: state.chat_data.channel,
                        path: "",
                        event_type: "GUEST_AGENT_EXIT",
                        session_id: session_id,
                        language: agent_preferred_language,
                        message_id: message_id,
                    }),
                    sender: "System",
                });
                send_message_to_socket(message);

                send_message_to_guest_agent_socket(message);

                update_customer_list();

                go_to_chat(get_session_id(), true);
            }
        }
    };
    xhttp.send(params);

    setTimeout(function() { remove_session_local_variables(session_id); }, 500);

    if (is_indexed_db_supported()) {
        let message_history = get_message_history_store();
        let chat_info = get_chat_info_store();
        let customer_details = get_customer_details_store();

        delete_messages_from_local(message_history.name);
        delete_messages_from_local(chat_info.name);
        delete_messages_from_local(customer_details.name);
    }
}

function guest_agent_session_no_response(session_id) {
    var json_string = JSON.stringify({
        session_id: session_id,
        bot_id: state.chat_data.bot_id,
    });

    json_string = EncryptVariable(json_string);
    json_string = encodeURIComponent(json_string);
    var xhttp = new XMLHttpRequest();

    var csrf_token = getCsrfToken();
    var params = "json_string=" + json_string;
    xhttp.open("POST", "/livechat/guest-agent-no-response/", true);
    xhttp.setRequestHeader("X-CSRFToken", csrf_token);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);

            if (response["status_code"] == "200") {
                localStorage.removeItem(`guest_agent_timer-${session_id}`);
                remove_current_guest_session(session_id);
                localStorage.setItem(
                    `guest_session_status-${session_id}`,
                    "no_response"
                );
                update_customer_list();
                go_to_chat(session_id, true);
            }
        }
    };
    xhttp.send(params);
}

function update_customer_details(session_id, updated_name, updated_email, updated_phone, phone_number) {
    let json_string = JSON.stringify({
        session_id: session_id,
        bot_id: state.chat_data.bot_id,
        updated_name: updated_name,
        updated_email: updated_email,
        updated_phone: updated_phone,
        channel : state.chat_data.channel,
    });

    const params = get_params(json_string);

    let config = {
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        }

    axios
        .post("/livechat/update-customer-details/", params, config)
        .then((response) => {
            response = custom_decrypt(response.data);
            response = JSON.parse(response);

            if (response.status == 200) {
                $("#livechat_customer_details_edit_btn").removeClass("livechat-customer-detail-edit-disabled-btn");
                $(".livechat-customer-personal-details-wrapper").removeClass("livechat-customer-detail-edit-active");
    
                $(".livechat-customer-personal-details input").attr('readonly', true);
                let text = `Customer Name: ${updated_name} (Original: ${response.original_name}) | Agent Name: ${get_agent_name()}(${get_agent_username()})`;
                let message = JSON.stringify({
                    message: JSON.stringify({
                        text_message: text,
                        type: "text",
                        channel: state.chat_data.channel,
                        path: "",
                        event_type: "CUSTOMER_DETAILS_UPDATED",
                        session_id: session_id,
                        updated_name: updated_name,
                        updated_email: updated_email,
                        updated_phone: phone_number,
                        phone_country_code: response.phone_country_code,
                    }),
                    sender: "System",
                });
                send_message_to_guest_agent_socket(message);
                send_message_to_socket(message);
                text = 'Customer details updated';
                let message_id = save_system_message(text, '', session_id);
                append_system_text_response(text, null, session_id, message_id);
                save_message_to_local({
                    message: text,
                    sender: "System",
                    sender_name: "system",
                    session_id: session_id,
                    message_id: message_id,
                })
                update_customer_details_in_local({
                    name: updated_name,
                    email: updated_email,
                    phone: phone_number,
                    session_id: session_id,
                    phone_country_code: response.phone_country_code,
                });
                remove_chat(session_id, false);
                go_to_chat(session_id, false);
            } else if (response.status == 400) {
                showToast(response.status_message, 2000);
            }
        })
        .catch((err) => {
            console.log(err);
        });
}

export function load_resolve_chat_form() {
    const is_form_enabled = state.chat_data.is_form_enabled;

    $("#custom_dispose_chat_form").html("");

    if (!is_form_enabled) return;

    const form = state.chat_data.form;

    set_form_state(form);

    generate_option_map();

    const field_ids = form.field_order;

    let first_mobile_field = true, first_email_field = true;

    field_ids.forEach((field_id) => {
        const field = form[field_id];

        const html = get_field_html_based_input_type(
            field,
            field_id.split("_")[1]
        );

        $("#custom_dispose_chat_form").append(html);

        if (field.type == "4") {
            $(
                `#livechat-form-datepicker_${field_id.split("_")[1]}`
            ).datepicker();

            $(`#livechat-form-datepicker_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    change_date(e.target);
                }
            );
        } else if (field.type == "2") {
            $(`.livechat-form-radio-btn_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    update_dependent_inputs(field_id.split("_")[1]);
                }
            );
        } else if (field.type == "6") {
            $(`#input-element_${field_id.split("_")[1]}`).on("change", (e) => {
                update_dependent_inputs(field_id.split("_")[1]);
            });
        } else if (field.type == "3") {
            $(`.livechat-form-checkbox_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    update_dependent_inputs(field_id.split("_")[1]);
                }
            );
        } else if (field.type == '8') {
            let country_initial_code = null;
            let customer_phone = document.getElementById("customer-phone-input").value;
            if(customer_phone.toLowerCase() == "not provided") {
                customer_phone = ""
            }

            if (first_mobile_field && customer_phone && customer_phone != '' && customer_phone != '-') {
                customer_phone = customer_phone.split(' ');

                const country_dict = state.country_codes.find( ({ dial_code }) => dial_code === customer_phone[0] );
    
                if(country_dict) {
                    country_initial_code = country_dict['code'].toLowerCase();
                }    
            }

            initialize_country_code_selector(country_initial_code, `input-element_${field_id.split('_')[1]}`);

            if (first_mobile_field) {
                $(`#input-element_${field_id.split('_')[1]}`).val(customer_phone[1]);
            }

            first_mobile_field = false;

            $(`#input-element_${field_id.split('_')[1]}`).on('focusout', (e) => {
                
                let is_valid = $(`#input-element_${field_id.split('_')[1]}`).intlTelInput("isValidNumber");
                
                if (!is_valid) {
                    $(`#error-message_${field_id.split('_')[1]}`).show();

                } else {
                    if($(`#input-element_${field_id.split('_')[1]}`).intlTelInput("getSelectedCountryData").dialCode == "91") {

                        if (!validate_phone_number(`input-element_${field_id.split('_')[1]}`)) {
                            $(`#error-message_${field_id.split('_')[1]}`).show();
                        } else {
                            $(`#error-message_${field_id.split('_')[1]}`).hide();
                        }
                    } else {
                        if (!validate_number_input_value(e.target.value)) {
                            $(`#error-message_${field_id.split('_')[1]}`).show();
                        } else {
                            $(`#error-message_${field_id.split('_')[1]}`).hide();
                        }
                    }
                }
            })
        } else if (field.type == '9') {
            const customer_email = document.getElementById('customer-email-input').value;

            if (first_email_field && customer_email && customer_email != '' && customer_email != '-') {
                $(`#input-element_${field_id.split('_')[1]}`).val(customer_email);
            }

            first_email_field = false;

            $(`#input-element_${field_id.split('_')[1]}`).on('focusout', (e) => {
                console.log('here');
                if (!validate_email(`input-element_${field_id.split('_')[1]}`)) {
                    $(`#error-message_${field_id.split('_')[1]}`).show();
                } else {
                    $(`#error-message_${field_id.split('_')[1]}`).hide();
                }
            })   
        }
    });
}

export function load_raise_ticket_form() {

    $('#raise-ticket-error-message').css('display','none');
    $("#livechat-raise-ticket-form").html("");

    let form = state.chat_data.raise_ticket_form;

    if(Object.keys(form).length == 0) {
        form = get_default_raise_ticket_form();
        state.chat_data.raise_ticket_form = form;
    }

    set_form_state(form);

    generate_option_map();

    const field_ids = form.field_order;

    let first_mobile_field = true, first_email_field = true;
    field_ids.forEach((field_id) => {
        const field = form[field_id];

        const html = get_field_html_based_input_type(
            field,
            field_id.split("_")[1]
        );

        $("#livechat-raise-ticket-form").append(html);

        if (field.type == "4") {
            $(
                `#livechat-form-datepicker_${field_id.split("_")[1]}`
            ).datepicker();

            $(`#livechat-form-datepicker_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    change_date(e.target);
                }
            );
        } else if (field.type == "2") {
            $(`.livechat-form-radio-btn_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    update_dependent_inputs(field_id.split("_")[1]);
                }
            );
        } else if (field.type == "6") {
            $(`#input-element_${field_id.split("_")[1]}`).on("change", (e) => {
                update_dependent_inputs(field_id.split("_")[1]);
            });
        } else if (field.type == "3") {
            $(`.livechat-form-checkbox_${field_id.split("_")[1]}`).on(
                "change",
                (e) => {
                    update_dependent_inputs(field_id.split("_")[1]);
                }
            );
        } else if (field.type == '8') {
            let country_initial_code = null;
            let customer_phone = document.getElementById("customer-phone-input").value;

            if (first_mobile_field && customer_phone && customer_phone != '' && customer_phone != '-') {
                customer_phone = customer_phone.split(' ');

                const country_dict = state.country_codes.find( ({ dial_code }) => dial_code === customer_phone[0] );
    
                if(country_dict) {
                    country_initial_code = country_dict['code'].toLowerCase();
                }    
            }

            initialize_country_code_selector(country_initial_code, `input-element_${field_id.split('_')[1]}`);

            if (first_mobile_field) {
                $(`#input-element_${field_id.split('_')[1]}`).val(customer_phone[1]);
            }

            first_mobile_field = false;

            $(`#input-element_${field_id.split('_')[1]}`).on('focusout', (e) => {
                
                if (!is_valid) {
                    $(`#error-message_${field_id.split('_')[1]}`).show();   
                } else {
                    if($(`#input-element_${field_id.split('_')[1]}`).intlTelInput("getSelectedCountryData").dialCode == "91") {

                        if (!validate_phone_number(`input-element_${field_id.split('_')[1]}`)) {
                            $(`#error-message_${field_id.split('_')[1]}`).show();
                        } else {
                            $(`#error-message_${field_id.split('_')[1]}`).hide();
                        }
                    } else {
                        if (!validate_number_input_value(e.target.value)) {
                            $(`#error-message_${field_id.split('_')[1]}`).show();
                        } else {
                            $(`#error-message_${field_id.split('_')[1]}`).hide();
                        }
                    }
                }
            })
        } else if (field.type == '9') {
            const customer_email = document.getElementById('customer-email-input').value;

            if (first_email_field && customer_email && customer_email != '' && customer_email != '-') {
                $(`#input-element_${field_id.split('_')[1]}`).val(customer_email);
            }

            first_email_field = false;

            $(`#input-element_${field_id.split('_')[1]}`).on('focusout', (e) => {
                console.log('here');
                if (!validate_email(`input-element_${field_id.split('_')[1]}`)) {
                    $(`#error-message_${field_id.split('_')[1]}`).show();
                } else {
                    $(`#error-message_${field_id.split('_')[1]}`).hide();
                }
            })   
        }
    });

    pre_fill_customer_details(form, field_ids);

    $('#livechat-raise-ticket-modal').modal('show');
}

function pre_fill_customer_details(form, field_ids) {

    try {
        field_ids.forEach((field_id) => { 

            const field = form[field_id];
            if(field.label_name == "Name") {
                let customer_name = document.getElementById("customer-name-input").value;
                document.getElementById("input-element_"+field_id.split("_")[1]).value = customer_name;
            }

            if(field.label_name == "Email") {
                let customer_email = document.getElementById("customer-email-input").value;
                document.getElementById("input-element_"+field_id.split("_")[1]).value = customer_email;
            }

            if(field.label_name == "Phone No") {
                let customer_phone = document.getElementById("customer-phone-input").value;
                customer_phone = customer_phone.replace(/\s/g, '');
                document.getElementById("input-element_"+field_id.split("_")[1]).value = customer_phone;
            }

        });
    } catch (err) { console.log(err); }
}

function get_scroll_to_bottom_html() {
    return '<div class="live-chat-message-area-scroll-to-bottom-div" id="img-scroll-to-bottom" onclick="scroll_to_bottom();">\
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">\
                    <path d="M16.0003 2.66675C23.3603 2.66675 29.3337 8.64008 29.3337 16.0001C29.3337 23.3601 23.3603 29.3334 16.0003 29.3334C8.64033 29.3334 2.66699 23.3601 2.66699 16.0001C2.66699 8.64008 8.64033 2.66675 16.0003 2.66675ZM17.3337 16.0001V10.6667H14.667V16.0001H10.667L16.0003 21.3334L21.3337 16.0001H17.3337Z" fill="#475569"/>\
                </svg>\
            </div>';
}

function remove_session_local_variables(session_id) {
    localStorage.removeItem(`is_translated-${session_id}`);
    localStorage.removeItem(`agent_language-${session_id}`);
    localStorage.removeItem(`customer_language_display-${session_id}`);
    localStorage.removeItem(`to_show_language_translate_prompt-${session_id}`);
    localStorage.removeItem(`customer_language-${session_id}`);
    localStorage.removeItem(`customer_channel_name-${session_id}`)
}

/* Set/Get Functions Start */

function has_customer_left_chat(session_id) {
    return state.customer_left_chat[session_id] == true;
}

function set_customer_left_chat(session_id, val) {
    state.customer_left_chat[session_id] = val;
}

function get_chat_history() {
    return state.chat_history;
}

function set_chat_history(chat_history) {
    state.chat_history = chat_history;
}

function set_chat_data(
    channel,
    bot_id,
    customer_name,
    easychat_user_id,
    category_enabled,
    closing_category,
    all_categories,
    is_form_enabled,
    form,
    is_external,
    raise_ticket_form,
) {
    state.chat_data = {
        channel: channel,
        bot_id: bot_id,
        customer_name: customer_name,
        easychat_user_id: easychat_user_id,
        category_enabled: category_enabled,
        closing_category: closing_category,
        all_categories: all_categories,
        is_form_enabled: is_form_enabled,
        form: form,
        is_external: is_external,
        raise_ticket_form: raise_ticket_form,
    };
}

function get_chat_data() {
    return state.chat_data;
}

function get_blacklisted_keywords() {
    return state.blacklisted_keywords;
}

function get_customer_blacklisted_keywords() {
    return state.customer_blacklisted_keywords;
}

function is_user_in_other_tab() {
    return state.user_in_other_tab;
}

export function set_chat_history_agent_username(chat_hist_agent_username) {
    state.chat_history.agent_username = chat_hist_agent_username;
}

function get_chat_history_agent_username() {
    return state.chat_history.agent_username;
}
/* Set/Get Functions Ends */
function preview_livechat_attachment_image(elem) {
    $("#preview-livechat-customer-attachment-modal").modal("show");
    const img_src = elem;
    document.getElementById("preview-livechat-customer-attachment").src =
        img_src;
}
function close_livechat_attachment_image() {
    $("#preview-livechat-customer-attachment-modal").modal("hide");
}
function get_agent_pending_list() {
    return state.agent_pending_list;
}
function set_agent_pending_list(agent_pending_list) {
    state.agent_pending_list = agent_pending_list;
    localStorage.setItem(
        "agent_pending_list",
        JSON.stringify(agent_pending_list)
    );
}
export function check_edit_customer_info_btn(){
    if(has_customer_left_chat(get_session_id())){
        let edit_btn = document.getElementById("livechat_customer_details_edit_btn");
        if(edit_btn){
            edit_btn.style.display = "none";
        }
    }
}

function get_cursor_position(input) {
    console.log(input);
    if ("selectionStart" in input && document.activeElement == input) {
        return {
            start: input.selectionStart,
            end: input.selectionEnd
        };
    }
    else if (input.createTextRange) {
        var sel = document.selection.createRange();
        if (sel.parentElement() === input) {
            var rng = input.createTextRange();
            rng.moveToBookmark(sel.getBookmark());
            for (var len = 0;
                     rng.compareEndPoints("EndToStart", rng) > 0;
                     rng.moveEnd("character", -1)) {
                len++;
            }
            rng.setEndPoint("StartToStart", input.createTextRange());
            for (var pos = { start: 0, end: len };
                     rng.compareEndPoints("EndToStart", rng) > 0;
                     rng.moveEnd("character", -1)) {
                pos.start++;
                pos.end++;
            }
            return pos;
        }
    }
    return -1;
}

function set_cursor_position(input, start, end) {
    if (arguments.length < 3) end = start;
    if ("selectionStart" in input) {
        setTimeout(function() {
            input.selectionStart = start;
            input.selectionEnd = end;
        }, 1);
    }
    else if (input.createTextRange) {
        var rng = input.createTextRange();
        rng.moveStart("character", start);
        rng.collapse();
        rng.moveEnd("character", end - start);
        rng.select();
    }
}

function is_special_character_allowed_in_file_name() {
    return window.IS_SPECIAL_CHARACTER_ALLOWED_IN_FILE_NAME;
}

function is_special_character_allowed_in_chat(){
    return window.IS_SPECIAL_CHARACTER_ALLOWED_IN_CHAT;
}

function get_livechat_channels_char_limit() {
    return window.LIVECHAT_CHANNELS_CHAR_LIMIT;
}

export {
    hide_prev_chat,
    show_console,
    resize_chat_window,
    get_customer_details,
    get_suggestion_list,
    set_end_chat_closing_category,
    get_chat_info,
    get_chat_data,
    get_chat_history,
    set_chat_history,
    update_customer_last_ping,
    append_response_server,
    get_file_to_agent_html_sent_customer,
    scroll_to_bottom,
    update_customer_last_app_time,
    show_customer_typing_in_chat,
    hide_customer_typing_in_chat,
    append_system_text_response,
    customer_last_ping_greater_than_fifteen_sec,
    update_message_history,
    set_chat_data,
    append_message_history,
    has_customer_left_chat,
    set_customer_left_chat,
    append_response_user,
    return_time,
    append_temp_file_to_agent,
    send_message_to_user_with_file,
    transfer_chat_modal_open,
    add_agent_modal_open,
    transfer_chat_to_another_agent,
    invite_guest_agent_to_chat,
    mark_chat_session_expired,
    mark_all_message_seen,
    send_notification_for_new_message,
    remove_chat,
    send_notification_for_new_assigned_customer,
    send_notification_for_chat_transfer,
    open_customer_details,
    close_customer_details,
    close_livechat_console,
    update_canned_response_arr_and_blacklisted_keywords,
    get_blacklisted_keywords,
    is_user_in_other_tab,
    update_unread_message_count,
    set_is_message_diffrentiator_present,
    set_user_unseen_message,
    remove_other_chat,
    is_customer_facing_issues,
    save_system_message,
    check_and_update_message_diffrentiator,
    preview_livechat_attachment_image,
    close_livechat_attachment_image,
    on_chat_history_div_scroll,
    on_chat_history_div_scroll_chat_area,
    openHistory,
    guest_agent_session_accept,
    guest_agent_session_reject,
    guest_agent_exit_chat,
    append_guest_agent_response,
    livechat_linkify,
    get_response_user_html,
    get_response_server_html,
    get_file_to_agent_html,
    get_system_text_response_html,
    guest_agent_filter_list,
    guest_agent_session_no_response,
    open_request_status_modal,
    get_agent_pending_list,
    set_agent_pending_list,
    append_supervisor_message,
    append_supervisor_file,
    get_image_path_html_attach,
    get_attachment_html,
    get_reply_private_html,
    get_customer_blacklisted_keywords,
    is_special_character_allowed_in_file_name,
    is_special_character_allowed_in_chat,
    get_livechat_channels_char_limit,
    hide_mics_for_iOS
};