function easyassist_create_custom_navbar() {
    if (window.IS_MOBILE == 'False') {
        return;
    }

    if (window.FLOATING_BUTTON_POSITION == "left" || window.FLOATING_BUTTON_POSITION == "right") {
        easyassist_create_sidenav_button()

        if (window.FLOATING_BUTTON_POSITION == "right") {
            document.getElementById("sidebar-mobile-modal-btn").style.borderRadius = "5px 0px 0px 5px";
        }
        
        let button_svg = `
        <svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1.93418 -5.07244e-07L6.76934 5L11.6045 -8.45407e-08L13.5386 1L6.76934 8L0.000113444 0.999999L1.93418 -5.07244e-07Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
        </svg>`

        document.getElementById("sidebar-mobile-modal-btn").innerHTML = button_svg
        easyassist_create_sidenav_modal();
    } else {
        easyassist_create_top_bottom_navbar_menu();

        let window_innerwidth = window.innerWidth;
        let options_width = window_innerwidth - 80;
        let icon_width = options_width / 3;

        let cobrowse_icons = document.getElementsByClassName('cobrowse-icons');
        document.getElementById('ul_items').style.width = options_width;
        let display_flex_counter = 0;

        for (let i = 0; i < cobrowse_icons.length; i++) {
            cobrowse_icons[i].style.width = icon_width + "px";
            if (cobrowse_icons[i].style.display != "none") {
                display_flex_counter += 1;
            }
        }
        
        try {
            let previous_button_element = document.getElementById("previous_button");
            previous_button_element = previous_button_element.children[0].children[0];
            previous_button_element.style.setProperty("fill", "#CBCACA")
        } catch(err) {
            console.log(err)
        }

        if (display_flex_counter <= 3) {
            try {
                let next_button_element = document.getElementById("next_button");
                next_button_element = next_button_element.children[0].children[0];
                next_button_element.style.setProperty("fill", "#CBCACA");
            } catch (err) {
                console.log(err)
            }
        } else {
            try {
                let next_button_element = document.getElementById("next_button");
                next_button_element = next_button_element.children[0].children[0];
                next_button_element.style.setProperty("fill", "#4D4D4D");
            } catch (err) {
                console.log(err)
            }
        }

        const left_button = document.querySelector('.closebtn1');
        left_button.onclick = function () {
            document.getElementById('ul_items').scrollBy(-(window_innerwidth - 80), 0);
        };

        const next_button = document.querySelector('.nexttabbtn');
        next_button.onclick = function () {
            document.getElementById('ul_items').scrollBy((window_innerwidth - 80), 0);
        };

        const easyassist_navbar_observer = new MutationObserver(function (mutations, observer) {
            update_navbar_buttons();
        })

        easyassist_navbar_observer.observe(document.getElementById("ul_items"), { subtree: true, attributes: true })
        document.getElementById("ul_items").addEventListener("scroll", update_navbar_buttons);
    }
}

function update_navbar_buttons() {
    let ul_items_element = document.getElementById("ul_items")
    let scroll_left = ul_items_element.scrollLeft
    let window_width = window.innerWidth - 80

    if (scroll_left <= 0) {
        try {
            let previous_button_element = document.getElementById("previous_button");
            previous_button_element = previous_button_element.children[0].children[0];
            previous_button_element.style.setProperty("fill", "#CBCACA")
        } catch(err) {
            console.log(err);
        }
    } else {
        try {
            let previous_button_element = document.getElementById("previous_button");
            previous_button_element = previous_button_element.children[0].children[0];
            previous_button_element.style.setProperty("fill", "#4D4D4D")
        } catch (err) {
            console.log(err);
        }
    }

    if (scroll_left + window_width >= ul_items_element.scrollWidth) {
        try {
            let next_button_element = document.getElementById("next_button");
            next_button_element = next_button_element.children[0].children[0];
            next_button_element.style.setProperty("fill", "#CBCACA");
        } catch (err) {
            console.log(err)
        }
    } else {
        try {
            let next_button_element = document.getElementById("next_button");
            next_button_element = next_button_element.children[0].children[0];
            next_button_element.style.setProperty("fill", "#4D4D4D");
        } catch (err) {
            console.log(err)
        }
    }
}

function easyassist_create_top_bottom_navbar_menu() {
    var div_model = document.createElement("div");
    div_model.id = "cobrowse-mobile-navbar"
    div_model.className = `easyassist-custom-${window.FLOATING_BUTTON_POSITION}-nav-bar`;
    div_model.style.justifyContent = "space-around";

    let sidenav_menu_html = `
    <div style="width: 100%; display: flex; align-items: center;">
    <div style="width: 100%; height: 100%;">
    <div style="width: 100%; height: 100%;">
    <ul id="ul_items">`

    sidenav_menu_html += `
    <li class="closebtn1">
        <div>
            <a id="previous_button" onclick="openNav()" href="javascript:void(0)" class="closebtn1" style="margin: 0px; height: 100%;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.3936 7.41289L8.44584 11.0199C7.85139 11.563 7.85139 12.4404 8.44584 12.9835L12.3936 16.5905C13.3538 17.4679 15 16.8412 15 15.6017V8.38776C15 7.14829 13.3538 6.53552 12.3936 7.41289Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                </svg>
            </a>
        </div>
    </li>`

    if (window.ENABLE_SCREENSHOT_AGENT == "True") {

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="#" data-toggle="modal" data-target="#capture_screenshot_confirm_modal" onclick="hide_cobrowsing_modals(this)">
                    <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.9972 6.32756V3.13421C17.9972 2.57182 17.7742 2.03237 17.3771 1.63411C16.9801 1.23584 16.4413 1.01125 15.8789 1.00956L12.6855 1" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M17.9972 12.7015V15.8885C17.9972 16.4519 17.7733 16.9924 17.3749 17.3908C16.9764 17.7893 16.436 18.0131 15.8725 18.0131H12.6855" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M6.31162 1L3.11828 1.00956C2.55589 1.01125 2.01711 1.23584 1.62004 1.63411C1.22297 2.03237 0.999997 2.57182 1 3.13421V6.32756" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M6.31162 18.0131H3.12465C2.56116 18.0131 2.02074 17.7893 1.6223 17.3908C1.22385 16.9924 1 16.4519 1 15.8885V12.7015" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M10.5557 4.50183C10.9945 4.50183 11.4004 4.73023 11.6227 5.10213L12.0707 5.85176H13.2096C14.1968 5.85176 14.9971 6.63841 14.9971 7.6088V12.7448C14.9971 13.7152 14.1968 14.5018 13.2096 14.5018H5.78457C4.79736 14.5018 3.99707 13.7152 3.99707 12.7448V7.6088C3.99707 6.63841 4.79736 5.85176 5.78457 5.85176H6.9288L7.40982 5.08174C7.63491 4.72141 8.03421 4.50183 8.46438 4.50183H10.5557ZM9.49707 7.47365C8.13017 7.47365 7.02207 8.56286 7.02207 9.90648C7.02207 11.2501 8.13017 12.3393 9.49707 12.3393C10.864 12.3393 11.9721 11.2501 11.9721 9.90648C11.9721 8.56286 10.864 7.47365 9.49707 7.47365ZM9.49707 8.28459C10.4083 8.28459 11.1471 9.01074 11.1471 9.90648C11.1471 10.8022 10.4083 11.5284 9.49707 11.5284C8.5858 11.5284 7.84707 10.8022 7.84707 9.90648C7.84707 9.01074 8.5858 8.28459 9.49707 8.28459Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                    </svg>
                </a>
            </div>
        </li>`

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="javascript:void(0)" data-toggle="modal" data-target="#captured_information_modal" onclick="fetch_cobrowsing_meta_information();hide_cobrowsing_modals(this)" >
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7.87391 2.9993C7.72545 3.35516 7.61796 3.73238 7.55733 4.12507L4.6875 4.125C3.96263 4.125 3.375 4.71263 3.375 5.4375V10.5H6.75C7.03477 10.5 7.27012 10.7116 7.30737 10.9862L7.3125 11.0625C7.3125 11.9945 8.06802 12.75 9 12.75C9.93198 12.75 10.6875 11.9945 10.6875 11.0625C10.6875 10.7518 10.9393 10.5 11.25 10.5H14.625L14.6258 9.20042C15.039 8.98496 15.4175 8.71203 15.7506 8.39223L15.75 14.0625C15.75 15.4087 14.6587 16.5 13.3125 16.5H4.6875C3.34131 16.5 2.25 15.4087 2.25 14.0625V5.4375C2.25 4.09131 3.34131 3 4.6875 3L7.87391 2.9993ZM12.375 0.75C14.6532 0.75 16.5 2.59683 16.5 4.875C16.5 7.15317 14.6532 9 12.375 9C10.0968 9 8.25 7.15317 8.25 4.875C8.25 2.59683 10.0968 0.75 12.375 0.75ZM12.5368 2.69144L12.4848 2.73484L12.4414 2.78677C12.3529 2.91465 12.3529 3.08535 12.4414 3.21323L12.4848 3.26516L13.719 4.5H9.75L9.68259 4.50604C9.52952 4.53382 9.40882 4.65452 9.38104 4.80759L9.375 4.875L9.38104 4.94241C9.40882 5.09548 9.52952 5.21618 9.68259 5.24396L9.75 5.25H13.719L12.4848 6.48483L12.4414 6.53677C12.3402 6.68292 12.3547 6.88499 12.4848 7.01517C12.615 7.14534 12.8171 7.1598 12.9632 7.05856L13.0152 7.01517L14.9213 5.1045L14.9461 5.06884L14.9717 5.01828L14.9875 4.97111L14.9984 4.90972L15 4.875L14.9979 4.83495L14.9875 4.7789L14.9649 4.71645L14.9334 4.6615L14.8992 4.61915L13.0152 2.73484L12.9632 2.69144C12.8353 2.60285 12.6647 2.60285 12.5368 2.69144Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                    </svg>
                </a>
            </div>
        </li>`;
    }

    if (window.ENABLE_INVITE_AGENT_IN_COBROWSING == "True" && window.IS_ADMIN_AGENT == "True") {
        if (window.ALLOW_LANGUAGE_SUPPORT == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" data-target="#askfor_support_modal" onclick="hide_cobrowsing_modals(this)">
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        } else {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" data-target="#askfor_support_modal" onclick="get_list_of_support_agents();hide_cobrowsing_modals(this)">
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        }
    }

    sidenav_menu_html += `
    <li class="cobrowse-icons">
        <div class="menu-item">
            <a href="#" onclick="hide_cobrowsing_modals(this);open_livechat_agent_window()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 24px !important; height: 24px !important;">
                    <path d="M12 4C16.4182 4 20 7.58119 20 11.9988C20 16.4164 16.4182 19.9976 12 19.9976C10.6877 19.9976 9.42015 19.6808 8.28464 19.0844L4.85231 19.9778C4.48889 20.0726 4.11752 19.8547 4.02287 19.4913C3.99359 19.379 3.99359 19.261 4.02284 19.1486L4.91592 15.7184C4.31776 14.582 4 13.3128 4 11.9988C4 7.58119 7.58173 4 12 4ZM13.0014 12.7987H9.40001L9.3186 12.8041C9.02573 12.8439 8.80001 13.0949 8.80001 13.3986C8.80001 13.7023 9.02573 13.9533 9.3186 13.9931L9.40001 13.9985H13.0014L13.0828 13.9931C13.3757 13.9533 13.6014 13.7023 13.6014 13.3986C13.6014 13.0949 13.3757 12.8439 13.0828 12.8041L13.0014 12.7987ZM14.6 9.99911H9.40001L9.3186 10.0046C9.02573 10.0443 8.80001 10.2953 8.80001 10.599C8.80001 10.9027 9.02573 11.1538 9.3186 11.1935L9.40001 11.199H14.6L14.6815 11.1935C14.9743 11.1538 15.2 10.9027 15.2 10.599C15.2 10.2953 14.9743 10.0443 14.6815 10.0046L14.6 9.99911Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                </svg>
            </a>
        </div>
    </li>`;

    if (window.ENABLE_EDIT_ACCESS == "True" && window.IS_ADMIN_AGENT == "True") {

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="#" id="easyassist-edit-access-icon" data-toggle="modal" data-target="#request_for_edit_access_modal">
                    <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.67131 0C0.752089 0 0 0.771429 0 1.71429V15.4286C0 16.3714 0.752089 17.1429 1.67131 17.1429H5.01393V15.5143L13.3705 6.94286V5.14286L8.35655 0H1.67131ZM7.52089 1.28571L12.117 6H7.52089V1.28571ZM13.454 9.42857C13.3705 9.42857 13.2033 9.51429 13.1198 9.6L12.2841 10.4571L14.039 12.2571L14.8747 11.4C15.0418 11.2286 15.0418 10.8857 14.8747 10.7143L13.7883 9.6C13.7047 9.51429 13.6212 9.42857 13.454 9.42857ZM11.7827 10.9714L6.68524 16.2V18H8.44011L13.5376 12.7714L11.7827 10.9714Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                    </svg>
                </a>
            </div>
        </li>`;
    }

    if (window.ALLOW_SUPPORT_DOCUMENTS == "True") {

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="#" data-toggle="modal" data-target="#support_material_modal" onclick="hide_cobrowsing_modals(this)">
                    <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg" >
                        <path d="M7.5 0V6C7.5 6.82843 8.17157 7.5 9 7.5H15V16.5C15 17.3284 14.3284 18 13.5 18H1.5C0.671573 18 0 17.3284 0 16.5V1.5C0 0.671573 0.671573 0 1.5 0H7.5Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        <path d="M8.625 0.375V6C8.625 6.20711 8.79289 6.375 9 6.375H14.625L8.625 0.375Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                    </svg>
                </a>
            </div>
        </li>`;
    }

    if (window.IS_ADMIN_AGENT == "True") {
        if (window.ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn" data-target="#request_meeting_modal" onclick="hide_cobrowsing_modals(this)">
                        <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        } else if (window.ENABLE_VOIP_CALLING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn" data-target="#request_meeting_modal" onclick="hide_cobrowsing_modals(this)">
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-call-icon">
                            <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                        <svg width="17" height="17" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-calling-icon" style="display: none;">
                            <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        } else if (window.ALLOW_COBROWSING_MEETING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn" data-target="#request_meeting_modal" onclick="hide_cobrowsing_modals(this)">
                        <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        }
    } else {
        if (window.ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                   <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        } else if (window.ENABLE_VOIP_CALLING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-call-icon">
                            <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                        <svg width="17" height="17" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-calling-icon" style="display: none;">
                            <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        } else if (window.ALLOW_COBROWSING_MEETING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        }
    }

    if (!window.IS_ADMIN_AGENT == "True") {
        if (window.ENABLE_VOIP_CALLING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="join-customer-voice-call-meeting-btn" onclick="hide_cobrowsing_modals(this);customer_init_open_call_joining_modal();">
                        <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        } else {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="join-customer-cobrowsing-video-call-meeting-btn" onclick="hide_cobrowsing_modals(this);customer_init_open_call_joining_modal();">
                        <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`;
        }
    }

    if (
        window.ENABLE_LOW_BANDWIDTH_COBROWSING == "True" &&
        window.ENABLE_MANUAL_SWITCHING == "True"
    ) {

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="javascript:void(0)" data-toggle="modal" data-target="#check_for_internet_modal" onclick="hide_cobrowsing_modals(this)" style="display: flex; flex-direction: column;">
                    <svg enable-background="new 0 0 512 512" height="18" viewBox="0 0 512 512" width="16" xmlns="http://www.w3.org/2000/svg">
                        <g>
                            <path d="m92.69 216c6.23 6.24 16.39 6.24 22.62 0l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69h284.69c26.47 0 48 21.53 48 48 0 13.23 10.77 24 24 24h16c13.23 0 24-10.77 24-24 0-61.76-50.24-112-112-112h-284.69l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69c-6.23-6.24-16.39-6.24-22.62 0l-90.35 90.34c-3.12 3.13-3.12 8.19 0 11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="m419.31 296c-6.23-6.24-16.38-6.24-22.62 0l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69h-284.69c-26.47 0-48-21.53-48-48 0-13.23-10.77-24-24-24h-16c-13.23 0-24 10.77-24 24 0 61.76 50.24 112 112 112h284.69l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69c6.241 6.241 16.38 6.24 22.62 0l90.35-90.34c3.12-3.13 3.12-8.19 0-11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </g>
                    </svg>
                    <span class="network-bandwidth-beta-text" style="color:${window.FLOATING_BUTTON_BG_COLOR}">Beta</span>
                </a>
            </div>
        </li>`

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="javascript:void(0)" data-toggle="modal" style="display: none;" data-target="#normal_mode_cobrowsing_toggle_modal" onclick="hide_cobrowsing_modals(this)" style="display: flex; flex-direction: column;">
                    <svg enable-background="new 0 0 512 512" height="18" viewBox="0 0 512 512" width="16" xmlns="http://www.w3.org/2000/svg">
                        <g>
                            <path d="m92.69 216c6.23 6.24 16.39 6.24 22.62 0l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69h284.69c26.47 0 48 21.53 48 48 0 13.23 10.77 24 24 24h16c13.23 0 24-10.77 24-24 0-61.76-50.24-112-112-112h-284.69l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69c-6.23-6.24-16.39-6.24-22.62 0l-90.35 90.34c-3.12 3.13-3.12 8.19 0 11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="m419.31 296c-6.23-6.24-16.38-6.24-22.62 0l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69h-284.69c-26.47 0-48-21.53-48-48 0-13.23-10.77-24-24-24h-16c-13.23 0-24 10.77-24 24 0 61.76 50.24 112 112 112h284.69l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69c6.241 6.241 16.38 6.24 22.62 0l90.35-90.34c3.12-3.13 3.12-8.19 0-11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </g>
                    </svg>
                    <span class="network-bandwidth-beta-text" style="color:${window.FLOATING_BUTTON_BG_COLOR}">Beta</span>
                </a>
            </div>
        </li>`;
    }

    if (window.ENABLE_COBROWSING_ANNOTATION == "True" && window.IS_ADMIN_AGENT == "True") {

        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="javascript:void(0)" id="drawing-mode" onclick="easyassist_activate_canvas(this);hide_cobrowsing_modals(this)">
                    <svg width="20" height="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="${window.FLOATING_BUTTON_BG_COLOR}">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                </a>
            </div>
            <span style="display: none;" id="easyassist-toggle-canvas-label">Enter Drawing Mode</span>
        </li>`;
    }

    if(window.COBROWSING_TYPE == "outbound-proxy-cobrowsing" && window.IS_ADMIN_AGENT == "True") {
        sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="javascript:void(0)" onclick="hide_all_cobrowsing_modals(); toggle_copy_link_modal_visibility()" onmouseover="easyassistChangeTooltipShow(this)" onmouseout="easyassistChangeTooltipHide(this)">
                        <svg width="22" height="22" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" fill="{{ floating_button_bg_color }}" xml:space="preserve"><g><g>
                            <path id="easyassist-icon-path-4" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124
                                c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90
                                c0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59
                                C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806
                                l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90
                                C496,372.371,455.629,332,406,332z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g></svg>
                        <label>
                            <svg width="8" height="12" viewBox="0 0 8 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M-2.62268e-07 6L7.5 0.803848L7.5 11.1962L-2.62268e-07 6Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                            <span id="sharable-link-span">Get shareable link</span>
                        </label>
                    </a>
                </div>
            </li>`;
    }

    sidenav_menu_html += `
    <li class="cobrowse-icons">
        <div class="menu-item">
            <a href="javascript:void(0)" onclick="hide_cobrowsing_modals(this);remove_onbeforeunload();open_close_session_modal();">\
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" onclick="hide_cobrowsing_modals(this);open_close_session_modal();">
                    <path d="M3.23041 3L14.7702 15" stroke="#D70000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M14.7699 3L3.23007 15" stroke="#D70000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </a>
        </div>
    </li>`


    sidenav_menu_html += `
    <li class="nexttabbtn">
        <div>
            <a id="next_button" onclick="openNav()" href="javascript:void(0)" class="nexttabbtn" style="margin: 0px; height: 100%;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.2341 16.5873L15.6179 12.9779C16.1274 12.4344 16.1274 11.5564 15.6179 11.0129L12.2341 7.40354C11.411 6.53952 10 7.1527 10 8.39299V15.5979C10 16.8521 11.411 17.4653 12.2341 16.5873Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                </svg>
            </a>
        </div>
    </li>`

    sidenav_menu_html += `
    </ul>
    </div>
    </div>
    </div>`

    div_model.innerHTML = sidenav_menu_html
    document.getElementsByClassName(`easyassist-custom-${window.FLOATING_BUTTON_POSITION}-nav-bar_wrapper`)[0].appendChild(div_model);
}

function easyassist_create_sidenav_button() {
    let button = document.createElement("div");
    button.id = "sidebar-mobile-modal-btn"
    button.className = "open-menu-btn";
    button.setAttribute("onclick", "hide_mobile_modal_btn(this);");
    button.setAttribute("data-toggle", "modal");
    button.setAttribute("data-target", "#cobrowse-mobile-modal");

    document.getElementsByClassName(`easyassist-custom-${window.FLOATING_BUTTON_POSITION}-nav-bar_wrapper`)[0].appendChild(button);
}

function easyassist_create_sidenav_modal() {
    let div = document.createElement("div");
    div.id = "cobrowse-mobile-modal";
    div.className = "modal fade left";

    let modal = `<div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" onclick="show_mobile_modal_btn();" id="mobile-modal-hide-btn">
                                <svg width="16" height="2" viewBox="0 0 16 2" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M15 2H1C0.734784 2 0.48043 1.89464 0.292893 1.70711C0.105357 1.51957 0 1.26522 0 1C0 0.734784 0.105357 0.48043 0.292893 0.292893C0.48043 0.105357 0.734784 0 1 0H15C15.2652 0 15.5196 0.105357 15.7071 0.292893C15.8946 0.48043 16 0.734784 16 1C16 1.26522 15.8946 1.51957 15.7071 1.70711C15.5196 1.89464 15.2652 2 15 2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                </svg>
                            </button>
                        </div>
                        <div class="modal-body">
                            <ul class="menu-items">`;

    if (window.ENABLE_SCREENSHOT_AGENT == "True") {
        modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" data-target="#capture_screenshot_confirm_modal" onclick="hide_cobrowsing_modals(this)">
                            <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M17.9972 6.32756V3.13421C17.9972 2.57182 17.7742 2.03237 17.3771 1.63411C16.9801 1.23584 16.4413 1.01125 15.8789 1.00956L12.6855 1" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M17.9972 12.7015V15.8885C17.9972 16.4519 17.7733 16.9924 17.3749 17.3908C16.9764 17.7893 16.436 18.0131 15.8725 18.0131H12.6855" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M6.31162 1L3.11828 1.00956C2.55589 1.01125 2.01711 1.23584 1.62004 1.63411C1.22297 2.03237 0.999997 2.57182 1 3.13421V6.32756" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M6.31162 18.0131H3.12465C2.56116 18.0131 2.02074 17.7893 1.6223 17.3908C1.22385 16.9924 1 16.4519 1 15.8885V12.7015" stroke="${window.FLOATING_BUTTON_BG_COLOR}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M10.5557 4.50183C10.9945 4.50183 11.4004 4.73023 11.6227 5.10213L12.0707 5.85176H13.2096C14.1968 5.85176 14.9971 6.63841 14.9971 7.6088V12.7448C14.9971 13.7152 14.1968 14.5018 13.2096 14.5018H5.78457C4.79736 14.5018 3.99707 13.7152 3.99707 12.7448V7.6088C3.99707 6.63841 4.79736 5.85176 5.78457 5.85176H6.9288L7.40982 5.08174C7.63491 4.72141 8.03421 4.50183 8.46438 4.50183H10.5557ZM9.49707 7.47365C8.13017 7.47365 7.02207 8.56286 7.02207 9.90648C7.02207 11.2501 8.13017 12.3393 9.49707 12.3393C10.864 12.3393 11.9721 11.2501 11.9721 9.90648C11.9721 8.56286 10.864 7.47365 9.49707 7.47365ZM9.49707 8.28459C10.4083 8.28459 11.1471 9.01074 11.1471 9.90648C11.1471 10.8022 10.4083 11.5284 9.49707 11.5284C8.5858 11.5284 7.84707 10.8022 7.84707 9.90648C7.84707 9.01074 8.5858 8.28459 9.49707 8.28459Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Capture Screenshot</span>
                </li>
                <li>
                    <div class="menu-item">
                        <a href="javascript:void(0)" data-toggle="modal" data-target="#captured_information_modal" onclick="fetch_cobrowsing_meta_information();hide_cobrowsing_modals(this)" >
                            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M7.87391 2.9993C7.72545 3.35516 7.61796 3.73238 7.55733 4.12507L4.6875 4.125C3.96263 4.125 3.375 4.71263 3.375 5.4375V10.5H6.75C7.03477 10.5 7.27012 10.7116 7.30737 10.9862L7.3125 11.0625C7.3125 11.9945 8.06802 12.75 9 12.75C9.93198 12.75 10.6875 11.9945 10.6875 11.0625C10.6875 10.7518 10.9393 10.5 11.25 10.5H14.625L14.6258 9.20042C15.039 8.98496 15.4175 8.71203 15.7506 8.39223L15.75 14.0625C15.75 15.4087 14.6587 16.5 13.3125 16.5H4.6875C3.34131 16.5 2.25 15.4087 2.25 14.0625V5.4375C2.25 4.09131 3.34131 3 4.6875 3L7.87391 2.9993ZM12.375 0.75C14.6532 0.75 16.5 2.59683 16.5 4.875C16.5 7.15317 14.6532 9 12.375 9C10.0968 9 8.25 7.15317 8.25 4.875C8.25 2.59683 10.0968 0.75 12.375 0.75ZM12.5368 2.69144L12.4848 2.73484L12.4414 2.78677C12.3529 2.91465 12.3529 3.08535 12.4414 3.21323L12.4848 3.26516L13.719 4.5H9.75L9.68259 4.50604C9.52952 4.53382 9.40882 4.65452 9.38104 4.80759L9.375 4.875L9.38104 4.94241C9.40882 5.09548 9.52952 5.21618 9.68259 5.24396L9.75 5.25H13.719L12.4848 6.48483L12.4414 6.53677C12.3402 6.68292 12.3547 6.88499 12.4848 7.01517C12.615 7.14534 12.8171 7.1598 12.9632 7.05856L13.0152 7.01517L14.9213 5.1045L14.9461 5.06884L14.9717 5.01828L14.9875 4.97111L14.9984 4.90972L15 4.875L14.9979 4.83495L14.9875 4.7789L14.9649 4.71645L14.9334 4.6615L14.8992 4.61915L13.0152 2.73484L12.9632 2.69144C12.8353 2.60285 12.6647 2.60285 12.5368 2.69144Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>View Screenshot</span>
                </li>`;
    }

    if (window.ENABLE_INVITE_AGENT_IN_COBROWSING == "True" && window.IS_ADMIN_AGENT == "True") {
        if (window.ALLOW_LANGUAGE_SUPPORT == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" data-target="#askfor_support_modal" onclick="hide_cobrowsing_modals(this)">
                            <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Invite an Agent</span>
                </li>`;
        } else {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" data-target="#askfor_support_modal" onclick="get_list_of_support_agents();hide_cobrowsing_modals(this)">
                            <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M7 0C4.79086 0 3 1.79086 3 4C3 6.20914 4.79086 8 7 8C9.20914 8 11 6.20914 11 4C11 1.79086 9.20914 0 7 0Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M2.00873 9C0.903151 9 0 9.88687 0 11C0 12.6912 0.83281 13.9663 2.13499 14.7966C3.41697 15.614 5.14526 16 7 16C7.41085 16 7.8155 15.9811 8.21047 15.9427C7.45316 15.0003 7 13.8031 7 12.5C7 11.1704 7.47182 9.95094 8.25716 9L2.00873 9Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M17 12.5C17 14.9853 14.9853 17 12.5 17C10.0147 17 8 14.9853 8 12.5C8 10.0147 10.0147 8 12.5 8C14.9853 8 17 10.0147 17 12.5ZM14.8532 12.854L14.8557 12.8514C14.9026 12.804 14.938 12.7495 14.9621 12.6914C14.9861 12.6333 14.9996 12.5697 15 12.503L15 12.5L15 12.497C14.9996 12.4303 14.9861 12.3667 14.9621 12.3086C14.9377 12.2496 14.9015 12.1944 14.8536 12.1464L12.8536 10.1464C12.6583 9.95118 12.3417 9.95118 12.1464 10.1464C11.9512 10.3417 11.9512 10.6583 12.1464 10.8536L13.2929 12H10.5C10.2239 12 10 12.2239 10 12.5C10 12.7761 10.2239 13 10.5 13H13.2929L12.1464 14.1464C11.9512 14.3417 11.9512 14.6583 12.1464 14.8536C12.3417 15.0488 12.6583 15.0488 12.8536 14.8536L14.8532 12.854Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Invite an Agent</span>
                </li>`;
        }
    }

    modal += `<li>
                <div class="menu-item">
                    <a href="#" onclick="hide_cobrowsing_modals(this);open_livechat_agent_window()">
                        <svg width="24" height="24" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M8.5 0C13.1944 0 17 3.80501 17 8.49873C17 13.1925 13.1944 16.9975 8.5 16.9975C7.10562 16.9975 5.75889 16.6609 4.55241 16.0271L0.905575 16.9765C0.519433 17.0771 0.124868 16.8456 0.0242893 16.4595C-0.00681194 16.3401 -0.00681557 16.2148 0.0242652 16.0954L0.973164 12.4509C0.337619 11.2433 0 9.89489 0 8.49873C0 3.80501 3.80558 0 8.5 0ZM9.56395 9.3486H5.7375L5.651 9.35442C5.33983 9.39663 5.1 9.66331 5.1 9.98601C5.1 10.3087 5.33983 10.5754 5.651 10.6176L5.7375 10.6234H9.56395L9.65045 10.6176C9.96162 10.5754 10.2014 10.3087 10.2014 9.98601C10.2014 9.66331 9.96162 9.39663 9.65045 9.35442L9.56395 9.3486ZM11.2625 6.37405H5.7375L5.651 6.37987C5.33983 6.42207 5.1 6.68876 5.1 7.01145C5.1 7.33415 5.33983 7.60083 5.651 7.64304L5.7375 7.64886H11.2625L11.349 7.64304C11.6602 7.60083 11.9 7.33415 11.9 7.01145C11.9 6.68876 11.6602 6.42207 11.349 6.37987L11.2625 6.37405Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"></path>
                        </svg>
                    </a>
                </div>
                <span>Chat with the Customer</span>
            </li>`;

    if (window.ENABLE_EDIT_ACCESS == "True" && window.IS_ADMIN_AGENT == "True") {
        modal += `<li>
                <div class="menu-item">
                    <a href="#" id="easyassist-edit-access-icon" data-toggle="modal" data-target="#request_for_edit_access_modal">
                        <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1.67131 0C0.752089 0 0 0.771429 0 1.71429V15.4286C0 16.3714 0.752089 17.1429 1.67131 17.1429H5.01393V15.5143L13.3705 6.94286V5.14286L8.35655 0H1.67131ZM7.52089 1.28571L12.117 6H7.52089V1.28571ZM13.454 9.42857C13.3705 9.42857 13.2033 9.51429 13.1198 9.6L12.2841 10.4571L14.039 12.2571L14.8747 11.4C15.0418 11.2286 15.0418 10.8857 14.8747 10.7143L13.7883 9.6C13.7047 9.51429 13.6212 9.42857 13.454 9.42857ZM11.7827 10.9714L6.68524 16.2V18H8.44011L13.5376 12.7714L11.7827 10.9714Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
                <span>Request for edit access</span>
            </li>`;
    }

    if (window.ALLOW_SUPPORT_DOCUMENTS == "True") {
        modal += `<li>
                <div class="menu-item">
                    <a href="#"  data-toggle="modal" data-target="#support_material_modal" onclick="hide_cobrowsing_modals(this)">
                        <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg" >
                            <path d="M7.5 0V6C7.5 6.82843 8.17157 7.5 9 7.5H15V16.5C15 17.3284 14.3284 18 13.5 18H1.5C0.671573 18 0 17.3284 0 16.5V1.5C0 0.671573 0.671573 0 1.5 0H7.5Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M8.625 0.375V6C8.625 6.20711 8.79289 6.375 9 6.375H14.625L8.625 0.375Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
                <span>Documents</span>
            </li>`;
    }

    if (window.IS_ADMIN_AGENT == "True") {
        if (window.ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn" data-target="#request_meeting_modal" onclick="hide_cobrowsing_modals(this)">
                            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Video Call</span>
                </li>`;
        } else if (window.ENABLE_VOIP_CALLING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn" data-target="#request_meeting_modal" onclick="hide_cobrowsing_modals(this)">
                            <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-call-icon">
                                <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                            <svg width="17" height="17" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-calling-icon" style="display: none;">
                                <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Voice Call</span>
                </li>`;
        } else if (window.ALLOW_COBROWSING_MEETING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn" data-target="#request_meeting_modal" onclick="hide_cobrowsing_modals(this)">
                            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Video Call</span>
                </li>`;
        }
    } else {
        if (window.ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Video Call</span>
                </li>`;
        } else if (window.ENABLE_VOIP_CALLING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                            <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-call-icon">
                                <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                            <svg width="17" height="17" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-calling-icon" style="display: none;">
                                <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Voice Call</span>
                </li>`;
        } else if (window.ALLOW_COBROWSING_MEETING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Video Call</span>
                </li>`;
        }
    }

    if (window.IS_ADMIN_AGENT != "True") {
        if (window.ENABLE_VOIP_CALLING == "True") {
            modal += `<li>
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="join-customer-voice-call-meeting-btn" onclick="hide_cobrowsing_modals(this);customer_init_open_call_joining_modal();">
                            <svg width="17" height="13" viewBox="0 0 17 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M11.9 10.1833C11.9 11.7389 10.6632 13 9.1375 13H2.7625C1.23681 13 0 11.7389 0 10.1833V2.81667C0 1.26106 1.23681 0 2.7625 0H9.1375C10.6632 0 11.9 1.26106 11.9 2.81667V10.1833ZM16.7977 1.20756C16.9283 1.36425 17 1.56319 17 1.76883V11.231C17 11.7096 16.6194 12.0976 16.15 12.0976C15.9483 12.0976 15.7532 12.0245 15.5995 11.8913L12.75 9.42148V3.57754L15.5995 1.10846C15.9572 0.798477 16.4937 0.842848 16.7977 1.20756Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Voice Call</span>
                </li>`;
        } else {
            modal += `<li style="display: none;">
                    <div class="menu-item">
                        <a href="#" data-toggle="modal" id="join-customer-cobrowsing-video-call-meeting-btn" onclick="hide_cobrowsing_modals(this);customer_init_open_call_joining_modal();">
                            <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </svg>
                        </a>
                    </div>
                    <span>Video Call</span>
                </li>`;
        }
    }

    if (
        window.ENABLE_LOW_BANDWIDTH_COBROWSING == "True" &&
        window.ENABLE_MANUAL_SWITCHING == "True"
    ) {
        modal += `<li id="lite_mode_switch_btn">
                <div class="menu-item">
                    <a href="javascript:void(0)" data-toggle="modal" data-target="#check_for_internet_modal" onclick="hide_cobrowsing_modals(this)" style="display: flex; flex-direction: column;">
                        <svg enable-background="new 0 0 512 512" height="18" viewBox="0 0 512 512" width="16" xmlns="http://www.w3.org/2000/svg">
                            <g>
                                <path d="m92.69 216c6.23 6.24 16.39 6.24 22.62 0l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69h284.69c26.47 0 48 21.53 48 48 0 13.23 10.77 24 24 24h16c13.23 0 24-10.77 24-24 0-61.76-50.24-112-112-112h-284.69l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69c-6.23-6.24-16.39-6.24-22.62 0l-90.35 90.34c-3.12 3.13-3.12 8.19 0 11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="m419.31 296c-6.23-6.24-16.38-6.24-22.62 0l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69h-284.69c-26.47 0-48-21.53-48-48 0-13.23-10.77-24-24-24h-16c-13.23 0-24 10.77-24 24 0 61.76 50.24 112 112 112h284.69l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69c6.241 6.241 16.38 6.24 22.62 0l90.35-90.34c3.12-3.13 3.12-8.19 0-11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </g>
                        </svg>
                        <span class="network-bandwidth-beta-text" style="color:${window.FLOATING_BUTTON_BG_COLOR}">Beta</span>
                    </a>
                </div>
                <span>Switch to Lite mode</span>
            </li>
            <li id="normal_mode_swtich_btn" style="display: none;">
                <div class="menu-item">
                    <a href="javascript:void(0)" data-toggle="modal" data-target="#normal_mode_cobrowsing_toggle_modal" onclick="hide_cobrowsing_modals(this)" style="display: flex; flex-direction: column;">
                        <svg enable-background="new 0 0 512 512" height="18" viewBox="0 0 512 512" width="16" xmlns="http://www.w3.org/2000/svg">
                            <g>
                                <path d="m92.69 216c6.23 6.24 16.39 6.24 22.62 0l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69h284.69c26.47 0 48 21.53 48 48 0 13.23 10.77 24 24 24h16c13.23 0 24-10.77 24-24 0-61.76-50.24-112-112-112h-284.69l20.69-20.69c6.24-6.23 6.24-16.39 0-22.62l-20.69-20.69c-6.23-6.24-16.39-6.24-22.62 0l-90.35 90.34c-3.12 3.13-3.12 8.19 0 11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                                <path d="m419.31 296c-6.23-6.24-16.38-6.24-22.62 0l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69h-284.69c-26.47 0-48-21.53-48-48 0-13.23-10.77-24-24-24h-16c-13.23 0-24 10.77-24 24 0 61.76 50.24 112 112 112h284.69l-20.69 20.69c-6.252 6.252-6.262 16.358 0 22.62l20.69 20.69c6.241 6.241 16.38 6.24 22.62 0l90.35-90.34c3.12-3.13 3.12-8.19 0-11.32z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </g>
                        </svg>
                        <span class="network-bandwidth-beta-text" style="color:${window.FLOATING_BUTTON_BG_COLOR}">Beta</span>
                    </a>
                </div>
                <span>Switch to Normal mode</span>
            </li>`;
    }

    if (window.ENABLE_COBROWSING_ANNOTATION == "True" && window.IS_ADMIN_AGENT == "True") {
        modal += `<li>
                <div class="menu-item">
                    <a href="javascript:void(0)" id="drawing-mode" onclick="easyassist_activate_canvas(this);hide_cobrowsing_modals(this)">
                        <svg width="20" height="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="${window.FLOATING_BUTTON_BG_COLOR}">
                            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                        </svg>
                    </a>
                </div>
                <span id="easyassist-toggle-canvas-label">Enter Drawing Mode</span>
            </li>`;
    }

    if(window.COBROWSING_TYPE == "outbound-proxy-cobrowsing" && window.IS_ADMIN_AGENT == "True") {
        modal += `
            <li>
                <div class="menu-item">
                    <a href="javascript:void(0)" onclick="hide_all_cobrowsing_modals(); toggle_copy_link_modal_visibility()" ">
                        <svg width="22" height="22" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" fill="{{ floating_button_bg_color }}" xml:space="preserve"><g><g>
                            <path id="easyassist-icon-path-4" d="M406,332c-29.641,0-55.761,14.581-72.167,36.755L191.99,296.124c2.355-8.027,4.01-16.346,4.01-25.124
                                c0-11.906-2.441-23.225-6.658-33.636l148.445-89.328C354.307,167.424,378.589,180,406,180c49.629,0,90-40.371,90-90
                                c0-49.629-40.371-90-90-90c-49.629,0-90,40.371-90,90c0,11.437,2.355,22.286,6.262,32.358l-148.887,89.59
                                C156.869,193.136,132.937,181,106,181c-49.629,0-90,40.371-90,90c0,49.629,40.371,90,90,90c30.13,0,56.691-15.009,73.035-37.806
                                l141.376,72.395C317.807,403.995,316,412.75,316,422c0,49.629,40.371,90,90,90c49.629,0,90-40.371,90-90
                                C496,372.371,455.629,332,406,332z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            </g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g><g></g></svg>
                    </a>
                </div>
            </li>`;
    }

    if (window.IS_ADMIN_AGENT == "True") {
        modal += `</ul>
                        <button class="menu-end-session-btn" type="button" style="background-color: #D70000 !important;" onclick="hide_cobrowsing_modals(this);remove_onbeforeunload();open_close_session_modal()">End Session</button>
                            </div>
                        </div>
                </div>`;
    } else {
        modal += `</ul>
                        <button class="menu-end-session-btn" type="button" style="background-color: #D70000 !important;" onclick="hide_cobrowsing_modals(this);remove_onbeforeunload();open_close_session_modal()">Leave Session</button>
                            </div>
                        </div>
                </div>`;
    }
    

    div.innerHTML = modal;

    document.getElementsByTagName("body")[0].appendChild(div);
}

