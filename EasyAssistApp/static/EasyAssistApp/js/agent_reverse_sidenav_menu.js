function easyassist_create_custom_navbar() {
    if (window.IS_MOBILE == 'False') {
        return;
    }

    if (window.FLOATING_BUTTON_POSITION == "left" || window.FLOATING_BUTTON_POSITION == "right") {
        easyassist_reverse_sidenav_menu_button();

        if (window.FLOATING_BUTTON_POSITION == "right") {
            document.getElementById("sidebar-mobile-modal-btn").style.borderRadius = "5px 0px 0px 5px"
        }

        let button_svg = `
        <svg width="14" height="8" viewBox="0 0 14 8" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1.93418 -5.07244e-07L6.76934 5L11.6045 -8.45407e-08L13.5386 1L6.76934 8L0.000113444 0.999999L1.93418 -5.07244e-07Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
        </svg>`

        document.getElementById("sidebar-mobile-modal-btn").innerHTML = button_svg;
        
        easyassist_reverse_mobile_modal();
    } else {
        easyassist_create_top_bottom_navbar_menu();

        let window_innerwidth = window.innerWidth;
        let options_width = window_innerwidth - 80;
        let icon_width = options_width / 3;
        let display_flex_counter = 0;

        let cobrowse_icons = document.getElementsByClassName('cobrowse-icons');
        document.getElementById('ul_items').style.width = options_width;

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

        easyassist_navbar_observer.observe(document.getElementById("ul_items"), { attributes: true, subtree: true })

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
            <a id="previous_button" href="javascript:void(0)" class="closebtn1" style="margin: 0px">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.3936 7.41289L8.44584 11.0199C7.85139 11.563 7.85139 12.4404 8.44584 12.9835L12.3936 16.5905C13.3538 17.4679 15 16.8412 15 15.6017V8.38776C15 7.14829 13.3538 6.53552 12.3936 7.41289Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                </svg>
            </a>
        </div>
    </li>`
    
    
    sidenav_menu_html += `
    <li class="cobrowse-icons">
        <div class="menu-item">
            <a href="#" onclick="hide_cobrowsing_modals(this);open_livechat_agent_window()">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 24px !important; height: 24px !important;">
                    <path d="M12 4C16.4182 4 20 7.58119 20 11.9988C20 16.4164 16.4182 19.9976 12 19.9976C10.6877 19.9976 9.42015 19.6808 8.28464 19.0844L4.85231 19.9778C4.48889 20.0726 4.11752 19.8547 4.02287 19.4913C3.99359 19.379 3.99359 19.261 4.02284 19.1486L4.91592 15.7184C4.31776 14.582 4 13.3128 4 11.9988C4 7.58119 7.58173 4 12 4ZM13.0014 12.7987H9.40001L9.3186 12.8041C9.02573 12.8439 8.80001 13.0949 8.80001 13.3986C8.80001 13.7023 9.02573 13.9533 9.3186 13.9931L9.40001 13.9985H13.0014L13.0828 13.9931C13.3757 13.9533 13.6014 13.7023 13.6014 13.3986C13.6014 13.0949 13.3757 12.8439 13.0828 12.8041L13.0014 12.7987ZM14.6 9.99911H9.40001L9.3186 10.0046C9.02573 10.0443 8.80001 10.2953 8.80001 10.599C8.80001 10.9027 9.02573 11.1538 9.3186 11.1935L9.40001 11.199H14.6L14.6815 11.1935C14.9743 11.1538 15.2 10.9027 15.2 10.599C15.2 10.2953 14.9743 10.0443 14.6815 10.0046L14.6 9.99911Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                </svg>
            </a>
        </div>
    </li>`

    if (window.ENABLE_EDIT_ACCESS == "True" && window.IS_AGENT == "False") {
        sidenav_menu_html += `
        <li class="cobrowse-icons">
            <div class="menu-item">
                <a href="#" id="easyassist-edit-access-icon" data-toggle="modal" data-target="#request_for_edit_access_modal" onclick="hide_cobrowsing_modals(this);">
                    <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.67131 0C0.752089 0 0 0.771429 0 1.71429V15.4286C0 16.3714 0.752089 17.1429 1.67131 17.1429H5.01393V15.5143L13.3705 6.94286V5.14286L8.35655 0H1.67131ZM7.52089 1.28571L12.117 6H7.52089V1.28571ZM13.454 9.42857C13.3705 9.42857 13.2033 9.51429 13.1198 9.6L12.2841 10.4571L14.039 12.2571L14.8747 11.4C15.0418 11.2286 15.0418 10.8857 14.8747 10.7143L13.7883 9.6C13.7047 9.51429 13.6212 9.42857 13.454 9.42857ZM11.7827 10.9714L6.68524 16.2V18H8.44011L13.5376 12.7714L11.7827 10.9714Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                    </svg>
                </a>
            </div>
        </li>`
    }

    if (window.IS_AGENT == "True") {
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
            </li>`
        } else if (window.ENABLE_VOIP_CALLING == "True") {

            sidenav_menu_html += `
            <li class="cobrowse-icons">
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-call-icon">
                            <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill=${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                        <svg width="17" height="17" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-calling-icon" style="display: none;">
                            <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR }"/>
                            <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
            </li>`
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
            </li>`
        }
    }

    sidenav_menu_html += `
    <li class="cobrowse-icons">
        <div>
            <a>
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
            <a id="next_button" href="javascript:void(0)" class="nexttabbtn" style="margin: 0px">
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

function easyassist_reverse_sidenav_menu_button() {
    let button = document.createElement("div");
    button.id = "sidebar-mobile-modal-btn"
    button.className = "open-menu-btn";
    button.setAttribute("onclick", "hide_mobile_modal_btn(this);");
    button.setAttribute("data-toggle", "modal");
    button.setAttribute("data-target", "#cobrowse-mobile-modal");

    document.getElementsByClassName(`easyassist-custom-${window.FLOATING_BUTTON_POSITION}-nav-bar_wrapper`)[0].appendChild(button);
}

function easyassist_reverse_mobile_modal() {
    let div_modal = document.createElement("div")
    div_modal.id = "cobrowse-mobile-modal"
    div_modal.className = "modal fade left"

    sidenav_menu = `
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" onclick="show_mobile_modal_btn();" id="mobile-modal-hide-btn">
                    <svg width="16" height="2" viewBox="0 0 16 2" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15 2H1C0.734784 2 0.48043 1.89464 0.292893 1.70711C0.105357 1.51957 0 1.26522 0 1C0 0.734784 0.105357 0.48043 0.292893 0.292893C0.48043 0.105357 0.734784 0 1 0H15C15.2652 0 15.5196 0.105357 15.7071 0.292893C15.8946 0.48043 16 0.734784 16 1C16 1.26522 15.8946 1.51957 15.7071 1.70711C15.5196 1.89464 15.2652 2 15 2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                <ul class="menu-items">
                    <li>
                        <div class="menu-item">
                            <a href="#" onclick="hide_cobrowsing_modals(this);open_livechat_agent_window()">
                                <svg width="24" height="24" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M8.5 0C13.1944 0 17 3.80501 17 8.49873C17 13.1925 13.1944 16.9975 8.5 16.9975C7.10562 16.9975 5.75889 16.6609 4.55241 16.0271L0.905575 16.9765C0.519433 17.0771 0.124868 16.8456 0.0242893 16.4595C-0.00681194 16.3401 -0.00681557 16.2148 0.0242652 16.0954L0.973164 12.4509C0.337619 11.2433 0 9.89489 0 8.49873C0 3.80501 3.80558 0 8.5 0ZM9.56395 9.3486H5.7375L5.651 9.35442C5.33983 9.39663 5.1 9.66331 5.1 9.98601C5.1 10.3087 5.33983 10.5754 5.651 10.6176L5.7375 10.6234H9.56395L9.65045 10.6176C9.96162 10.5754 10.2014 10.3087 10.2014 9.98601C10.2014 9.66331 9.96162 9.39663 9.65045 9.35442L9.56395 9.3486ZM11.2625 6.37405H5.7375L5.651 6.37987C5.33983 6.42207 5.1 6.68876 5.1 7.01145C5.1 7.33415 5.33983 7.60083 5.651 7.64304L5.7375 7.64886H11.2625L11.349 7.64304C11.6602 7.60083 11.9 7.33415 11.9 7.01145C11.9 6.68876 11.6602 6.42207 11.349 6.37987L11.2625 6.37405Z" fill="${window.FLOATING_BUTTON_BG_COLOR}" />
                                </svg>
                            </a>
                        </div>`

    if (window.IS_AGENT == "True") {
        sidenav_menu += `<span>Chat with the Customer</span>`
    } else {
        sidenav_menu += `<span>Chat with the Agent</span>`
    }

    sidenav_menu += `</li>`;

    if (window.ENABLE_EDIT_ACCESS == "True" && window.IS_AGENT == "False") {
        sidenav_menu += `
        <li>
            <div class="menu-item">
                <a href="#" id="easyassist-edit-access-icon" data-toggle="modal" data-target="#request_for_edit_access_modal" onclick="hide_cobrowsing_modals(this);">
                    <svg width="15" height="18" viewBox="0 0 15 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1.67131 0C0.752089 0 0 0.771429 0 1.71429V15.4286C0 16.3714 0.752089 17.1429 1.67131 17.1429H5.01393V15.5143L13.3705 6.94286V5.14286L8.35655 0H1.67131ZM7.52089 1.28571L12.117 6H7.52089V1.28571ZM13.454 9.42857C13.3705 9.42857 13.2033 9.51429 13.1198 9.6L12.2841 10.4571L14.039 12.2571L14.8747 11.4C15.0418 11.2286 15.0418 10.8857 14.8747 10.7143L13.7883 9.6C13.7047 9.51429 13.6212 9.42857 13.454 9.42857ZM11.7827 10.9714L6.68524 16.2V18H8.44011L13.5376 12.7714L11.7827 10.9714Z" fill="${window.FLOATING_BUTTON_BG_COLOR}" />
                    </svg>
                </a>
            </div>
            <span>Request for edit access</span>
        </li>`
    }

    if (window.IS_AGENT == "True") {
        if (window.ENABLE_VOIP_WITH_VIDEO_CALLING == "True") {
            sidenav_menu += `
            <li>
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
                <span>Video Call</span>
            </li>`
        } else if (window.ENABLE_VOIP_CALLING == "True") {
            sidenav_menu += `
            <li>
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-call-icon">
                            <path d="M16.065 11.6922C14.9033 11.6922 13.7794 11.5033 12.7311 11.1633C12.5669 11.1077 12.3903 11.0994 12.2216 11.1395C12.0529 11.1796 11.8989 11.2664 11.7772 11.39L10.2944 13.2506C7.62167 11.9756 5.11889 9.56722 3.78722 6.8L5.62889 5.23222C5.88389 4.96778 5.95944 4.59944 5.85556 4.26889C5.50611 3.22056 5.32667 2.09667 5.32667 0.935C5.32667 0.425 4.90167 0 4.39167 0H1.12389C0.613889 0 0 0.226667 0 0.935C0 9.70889 7.30056 17 16.065 17C16.7356 17 17 16.405 17 15.8856V12.6272C17 12.1172 16.575 11.6922 16.065 11.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}" />
                        </svg>
                        <svg width="17" height="17" viewBox="0 0 22 21" fill="none" xmlns="http://www.w3.org/2000/svg" id="voip-calling-icon" style="display: none;">
                            <path d="M16.065 15.6922C14.9033 15.6922 13.7794 15.5033 12.7311 15.1633C12.5669 15.1077 12.3903 15.0994 12.2216 15.1395C12.0529 15.1796 11.8989 15.2664 11.7772 15.39L10.2944 17.2506C7.62167 15.9756 5.11889 13.5672 3.78722 10.8L5.62889 9.23222C5.88389 8.96778 5.95944 8.59944 5.85556 8.26889C5.50611 7.22056 5.32667 6.09667 5.32667 4.935C5.32667 4.425 4.90167 4 4.39167 4H1.12389C0.613889 4 0 4.22667 0 4.935C0 13.7089 7.30056 21 16.065 21C16.7356 21 17 20.405 17 19.8856V16.6272C17 16.1172 16.575 15.6922 16.065 15.6922Z" fill="${window.FLOATING_BUTTON_BG_COLOR}" />
                            <path d="M19.2891 11.0679C18.6949 5.772 14.0939 1.87804 8.77448 2.16523C8.57445 2.17603 8.42184 2.35187 8.43718 2.55176L8.51883 3.61444C8.53335 3.80515 8.69642 3.94702 8.88731 3.93754C13.2516 3.72289 17.0146 6.90819 17.5226 11.249C17.5447 11.4389 17.7117 11.5761 17.902 11.5592L18.9636 11.4645C19.1631 11.4465 19.3114 11.267 19.2891 11.0679ZM11.1886 9.97458C10.5984 9.47489 9.70688 9.55798 9.197 10.1602C8.68712 10.7624 8.75218 11.6554 9.34233 12.1551C9.93248 12.6548 10.824 12.5717 11.3339 11.9695C11.8438 11.3673 11.7787 10.4743 11.1886 9.97458ZM15.7777 11.4154C15.3237 8.04975 12.4014 5.57866 9.01076 5.6858C8.80758 5.69218 8.65116 5.86947 8.66733 6.07211L8.75203 7.13796C8.76681 7.32362 8.92231 7.46698 9.10861 7.46327C11.5569 7.41367 13.6546 9.19448 14.0083 11.6118C14.0354 11.7962 14.2023 11.9261 14.388 11.9099L15.4532 11.8177C15.6559 11.8004 15.8049 11.6165 15.7777 11.4154Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
                <span>Voice Call</span>
            </li>`
        } else if (window.ALLOW_COBROWSING_MEETING == "True") {
            sidenav_menu += `
            <li>
                <div class="menu-item">
                    <a href="#" data-toggle="modal" id="request-cobrowsing-meeting-btn-invited-agent" onclick="hide_cobrowsing_modals(this);open_call_joining_modal();">
                        <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 18.8333C18 21.1346 16.1685 23 13.9091 23H4.09091C1.83156 23 0 21.1346 0 18.8333V7.16668C0 4.86548 1.83156 3 4.09091 3H13.9091C16.1685 3 18 4.86548 18 7.16668V18.8333Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                            <path d="M20 16.2V9.86326L24.1463 6.27492C24.8769 5.64261 26 6.1711 26 7.14721V18.8528C26 19.8243 24.8863 20.3543 24.1537 19.7315L20 16.2Z" fill="${window.FLOATING_BUTTON_BG_COLOR}"/>
                        </svg>
                    </a>
                </div>
                <span>Video Call</span>
            </li>`
        }
    }

    let ending_message = "";

    if (window.IS_AGENT == "True") {
        ending_message = "Leave Session"
    } else {
        ending_message = "End Session"
    }

    sidenav_menu += `</ul>
    <button class="menu-end-session-btn" type="button" style="background-color: #D70000 !important;" onclick="hide_cobrowsing_modals(this);open_close_session_modal()">
    ${ending_message}
    </button>
    </div>
    </div>
    </div>
    </div>`

    div_modal.innerHTML = sidenav_menu;

    document.getElementsByTagName("body")[0].appendChild(div_modal);
}