function DropDown(el) {
    this.dd = el;
    this.placeholder = this.dd.children('span');
    this.opts = this.dd.find('ul.drop li');
    this.val = '';
    this.index = -1;
    this.initEvents();
}

DropDown.prototype = {
    initEvents: function () {
        var obj = this;
        obj.dd.on('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).toggleClass('active');
        });
        obj.opts.on('click', function () {
            var opt = $(this);
            obj.val = opt.text();
            obj.index = opt.index();
            obj.placeholder.text(obj.val);
            opt.siblings().removeClass('selected');
            opt.filter(':contains("' + obj.val + '")').addClass('selected');
        }).change();
    },
    getValue: function () {
        return this.val;
    },
    getIndex: function () {
        return this.index;
    }
};

$(function () {
    // create new variable for each menu
    var dd1 = new DropDown($('#select-message-type-dropdown'));
    $(document).click(function () {
        // close menu on document click
        $('.wrap-drop').removeClass('active');
    });

});

$(document).ready(function () {
    $('.select-message-type-dropdown__list-item').click(function () {
        var itemValue = $(this).data('value');

        if (itemValue == 1) {
            $('.message-type-text-div').removeClass('d-none')
        } else {
            $('.message-type-text-div').addClass('d-none')
        }
        if (itemValue == 2) {
            $('.message-type-media-div').removeClass('d-none')
        } else {
            $('.message-type-media-div').addClass('d-none')
        }
        if (itemValue == 3) {
            $('.combined-message-type-container').removeClass('d-none')
            $('.message-type-rich-card').removeClass('d-none')
        } else {
            $('.combined-message-type-container').addClass('d-none')
            $('.message-type-rich-card').addClass('d-none')
        }
        if (itemValue == 4) {
            $('.combined-message-type-container').removeClass('d-none')
            $('.message-type-carousel').removeClass('d-none')
        } else {
            $('.message-type-carousel').addClass('d-none')
        }

    })

})

// creating dynamic accordion for suggested reply for all type of message reply
var $SimpleReplyAction = $('#simple-reply-action');
var $OpenURLAction = $('#open-url-option');
var $DailAction = $('#dail-action');
var $ShareLocationAction = $('#share-loaction-action');

$SimpleReplyAction.click(function () {
    if ($('#accordiondynamic .accordion__header').length >= 11) {
        show_campaign_toast("Cannot add another reply, maximum 11 replies are supported!");
        return;
    }
    $(get_simple_reply_html()).appendTo("#accordiondynamic");
    scroll_template_modal_to_bottom();
})

$OpenURLAction.click(function () {
    if ($('#accordiondynamic .accordion__header').length >= 11) {
        show_campaign_toast("Cannot add another reply, maximum 11 replies are supported!");
        return;
    }
    $(get_open_url_action_html()).appendTo("#accordiondynamic");
    scroll_template_modal_to_bottom();
})

$DailAction.click(function () {
    if ($('#accordiondynamic .accordion__header').length >= 11) {
        show_campaign_toast("Cannot add another reply, maximum 11 replies are supported!");
        return;
    }
    $(get_dial_action_html()).appendTo("#accordiondynamic");
    scroll_template_modal_to_bottom();
})

$ShareLocationAction.click(function () {
    if ($('#accordiondynamic .accordion__header').length >= 11) {
        show_campaign_toast("Cannot add another reply, maximum 11 replies are supported!");
        return;
    }
    $(get_share_location_html()).appendTo("#accordiondynamic");
    scroll_template_modal_to_bottom();
})

var $SimpleReplyRichcardCaraousel = $('#simple-reply-rich-card-caraousel');
var $OpenURLActionRichcardCaraousel = $('#open-url-rich-card-caraousel');
var $DailActionRichcardCaraousel = $('#dail-action-rich-card-caraousel');
var $ShareLocationActionRichcardCaraousel = $('#share-loaction-rich-card-caraousel');

$SimpleReplyRichcardCaraousel.click(function () {
    if ($('#AccordionRichCard .accordion__header').length >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_simple_reply_html()).appendTo("#AccordionRichCard");
})

$OpenURLActionRichcardCaraousel.click(function () {
    if ($('#AccordionRichCard .accordion__header').length >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_open_url_action_html()).appendTo("#AccordionRichCard");
})

$DailActionRichcardCaraousel.click(function () {
    if ($('#AccordionRichCard .accordion__header').length >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_dial_action_html()).appendTo("#AccordionRichCard");
})

$ShareLocationActionRichcardCaraousel.click(function () {
    if ($('#AccordionRichCard .accordion__header').length >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_share_location_html()).appendTo("#AccordionRichCard");
})

$(document).on('click', '.accordion__header', function (e) {
    e.preventDefault();
    var currentIsActive = $(this).hasClass('is-active');
    $(this).parent('.accordion').find('> *').removeClass('is-active');
    if (currentIsActive != 1) {
        $(this).addClass('is-active');
        $(this).next('.accordion__body').addClass('is-active');
    }
});

$(document).on('click', '.delete_current_div', function (e) {
    $(this).parent().next().remove();
    $(this).parent().remove();
})

//Adds carousel card in template
let $dynamicAddCardButton = $('#add-dynamic-card-button');
$dynamicAddCardButton.click(function () {
    if ($('.custom-nav-tab .nav-item').length > 9) {
        show_campaign_toast('Cannot add another card, maximum 10 cards supported')
        return;
    }
    let unique_element_id = generate_random_string(5)
    $(get_caraousel_pills_html(unique_element_id)).insertBefore('#add_card_div');

    $(get_caraousel_pills_body_html(unique_element_id)).prependTo('.tab-content')

    $('#caraousel_card_title_' + unique_element_id).keyup(function (e) {
        $('#card_title_count_' + unique_element_id).text(this.value.length)
    })
    $('#caraousel_card_description_' + unique_element_id).keyup(function (e) {
        $('#caraousel_description_count_' + unique_element_id).text(this.value.length)
    })
    $('#caraousel_media_url_' + unique_element_id).keyup(function (e) {
        let url = $(this).val()
        if ($(this).val() && isValidURL(url)) {
            $("#" + unique_element_id + " .preview-media-logo").show();
            $('#open_carousel_media_' + unique_element_id).attr('href', url)
        } else {
            $("#" + unique_element_id + " .preview-media-logo").hide();
            $('#open_carousel_media_' + unique_element_id).attr('href', null)
        }
    })

    tooltipToggle();

    if ($('.custom-nav-tab .nav-item').length == 1) {
        $('#pills-tabContent').children('.tab-pane').last().addClass('active')
        $('#pills-tab').children('.nav-item').last().find('.show-button').addClass('selected')
    }
    $('#caraousel_card_title_' + unique_element_id).focusout(function () {
        let card_title = $('#caraousel_card_title_' + unique_element_id).val()
        if (card_title.trim() == '') {
            $('#pills_card_title_' + unique_element_id).text('Card Title')
        } else {
            $('#pills_card_title_' + unique_element_id).text($('#caraousel_card_title_' + unique_element_id).val())
        }
    })
})

function tooltipToggle() {
    $('[data-toggle="tooltip"]').tooltip()
}

$('#new_rcs_template_btn').click(function () {
    reset_rcs_template_modal();
})

$(document).on('click', '.simple-reply-caraousel', function () {
    let container = $(this).closest(".add-card-reply ").next('.dynamic-append-div').children('.carouseldynamicaccordion');
    if (container.children().length / 2 >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_simple_reply_html()).appendTo(container);
})

$(document).on('click', '.open-url-caraousel', function () {
    let container = $(this).closest(".add-card-reply ").next('.dynamic-append-div').children('.carouseldynamicaccordion');
    if (container.children().length / 2 >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_open_url_action_html()).appendTo(container);
})

$(document).on('click', '.dail-action-caraousel', function () {
    let container = $(this).closest(".add-card-reply ").next('.dynamic-append-div').children('.carouseldynamicaccordion');
    if (container.children().length / 2 >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_dial_action_html()).appendTo(container);
})

$(document).on('click', '.share-loaction-caraousel', function () {
    let container = $(this).closest(".add-card-reply ").next('.dynamic-append-div').children('.carouseldynamicaccordion');
    if (container.children().length / 2 >= 4) {
        show_campaign_toast("Cannot add another card reply, maximum 4 replies are supported!");
        return;
    }
    $(get_share_location_html()).appendTo(container);
})

//Removes carousel card and its contents
$(document).on('click', '.closeCard', function () {
    $(this).closest('.nav-item').remove();

    let id = this.id.split('_')[1]

    $('#' + id).remove();

    $('#pills-tabContent').children('.tab-pane').first().addClass('active')

    $('#pills-tab').children('.nav-item').last().find('.show-button').addClass('selected')

});

function get_simple_reply_html() {
    let unique_element_id = generate_random_string(5);
    return `<div class="accordion__header" id="simple-reply_${unique_element_id}">
                <div class="d-flex align-items-center">
                    <p class="mb-0">Simple Reply</p>
                    <span class="accordion__toggle">
                        <svg width="12" height="7" viewBox="0 0 12 7" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11.793 6.26729C12.0787 5.96737 12.0672 5.49263 11.7672 5.20694L6.51678 0.205606C6.22711 -0.0703173 5.77187 -0.0703173 5.4822 0.205606L0.231735 5.20694C-0.0681872 5.49263 -0.0797238 5.96737 0.205968 6.26729C0.491659 6.56721 0.966392 6.57875 1.26631 6.29306L5.99949 1.78447L10.7327 6.29306C11.0326 6.57875 11.5073 6.56721 11.793 6.26729Z" fill="#212121"/>
                        </svg> </span>
                </div>
                <div class="delete_current_div">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 10L13.7 17M10.3 17L10 10M6 6L6.87554 19.133C6.94558 20.1836 7.81818 21 8.87111 21H15.1289C16.1818 21 17.0544 20.1836 17.1245 19.133L18 6M6 6H9M6 6H4M18 6H20M18 6H15M15 6V5C15 3.89543 14.1046 3 13 3H11C9.89543 3 9 3.89543 9 5V6M15 6H9" stroke="#FF0000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>                                            
                </div>
            </div>
            <div class="accordion__body">
                <div class="col-sm-12 d-flex">
                    <div class="col-sm-6">
                        <span >Suggested Text <span class="text-danger">*</span></span>
                        <input type="text" class="template_input w-100 mt-3" placeholder="Suggested Text" id="card_suggested_text_${unique_element_id}">
                    </div>
                    <div class="col-sm-6">
                        <span>Suggested Postback <span class="text-danger">*</span></span>
                        <input type="text" class="template_input w-100 mt-3" placeholder="Suggested Postback" id="card_suggested_postback_${unique_element_id}">
                    </div>
                </div>
            </div>`
}

function get_open_url_action_html() {
    let unique_element_id = generate_random_string(5);
    return `<div class="accordion__header" id="open-url_${unique_element_id}">
                    <div class="d-flex align-items-center">
                        <p class="mb-0">Open URL Action</p>
                        <span class="accordion__toggle">
                            <svg width="12" height="7" viewBox="0 0 12 7" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M11.793 6.26729C12.0787 5.96737 12.0672 5.49263 11.7672 5.20694L6.51678 0.205606C6.22711 -0.0703173 5.77187 -0.0703173 5.4822 0.205606L0.231735 5.20694C-0.0681872 5.49263 -0.0797238 5.96737 0.205968 6.26729C0.491659 6.56721 0.966392 6.57875 1.26631 6.29306L5.99949 1.78447L10.7327 6.29306C11.0326 6.57875 11.5073 6.56721 11.793 6.26729Z" fill="#212121"/>
                            </svg> </span>
                    </div>
                    <div class="delete_current_div">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M14 10L13.7 17M10.3 17L10 10M6 6L6.87554 19.133C6.94558 20.1836 7.81818 21 8.87111 21H15.1289C16.1818 21 17.0544 20.1836 17.1245 19.133L18 6M6 6H9M6 6H4M18 6H20M18 6H15M15 6V5C15 3.89543 14.1046 3 13 3H11C9.89543 3 9 3.89543 9 5V6M15 6H9" stroke="#FF0000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>                                            
                    </div>
                </div>
                <div class="accordion__body">
                    <div class="col-sm-12 d-flex">
                        <div class="col-sm-6 px-0 pr-2">
                            <span>Suggested Text <span class="text-danger">*</span></span>
                            <input type="text" class="template_input w-100 mt-3" placeholder="Suggested Text" id="card_suggested_text_${unique_element_id}">
                        </div>
                        <div class="col-sm-6 px-0">
                            <span>Suggested Postback <span class="text-danger">*</span></span>
                            <input type="text" class="template_input w-100 mt-3" placeholder="Suggested Postback" id="card_suggested_postback_${unique_element_id}">
                        </div>
                    </div>
                    <div class="col-sm-12 mt-3">
                        <span>URL To Open <span class="text-danger">*</span></span>
                        <input type="text" class="template_input w-100 mt-3" placeholder="URL To Open" id="url_to_open_${unique_element_id}">
                    </div>
                </div>`
}

function get_dial_action_html() {
    let unique_element_id = generate_random_string(5);
    return `<div class="accordion__header" id="dial-action_${unique_element_id}">
                    <div class="d-flex align-items-center">
                        <p class="mb-0">Dial Action</p>
                        <span class="accordion__toggle">
                            <svg width="12" height="7" viewBox="0 0 12 7" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M11.793 6.26729C12.0787 5.96737 12.0672 5.49263 11.7672 5.20694L6.51678 0.205606C6.22711 -0.0703173 5.77187 -0.0703173 5.4822 0.205606L0.231735 5.20694C-0.0681872 5.49263 -0.0797238 5.96737 0.205968 6.26729C0.491659 6.56721 0.966392 6.57875 1.26631 6.29306L5.99949 1.78447L10.7327 6.29306C11.0326 6.57875 11.5073 6.56721 11.793 6.26729Z" fill="#212121"/>
                            </svg> </span>
                    </div>
                    <div class="delete_current_div">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M14 10L13.7 17M10.3 17L10 10M6 6L6.87554 19.133C6.94558 20.1836 7.81818 21 8.87111 21H15.1289C16.1818 21 17.0544 20.1836 17.1245 19.133L18 6M6 6H9M6 6H4M18 6H20M18 6H15M15 6V5C15 3.89543 14.1046 3 13 3H11C9.89543 3 9 3.89543 9 5V6M15 6H9" stroke="#FF0000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>                                            
                    </div>
                </div>
                <div class="accordion__body">
                    <div class="col-sm-12 d-flex">
                        <div class="col-sm-6 px-0 pr-2">
                            <span>Suggested Text <span class="text-danger">*</span></span>
                            <input type="text" class="template_input w-100 mt-3" placeholder="Suggested Text" id="card_suggested_text_${unique_element_id}">
                        </div>
                        <div class="col-sm-6 px-0">
                            <span>Suggested Postback <span class="text-danger">*</span></span>
                            <input type="text" class="template_input w-100 mt-3" placeholder="Suggested Postback" id="card_suggested_postback_${unique_element_id}">
                        </div>
                    </div>
                    <div class="col-sm-12 mt-3">
                        <span>Phone Number(with Country Code)<span class="text-danger">*</span></span>
                        <input type="text" class="template_input w-100 mt-3" placeholder="Phone Number(with Country Code)" id="dial_action_number_${unique_element_id}">
                    </div>
                </div>`
}

function get_share_location_html() {
    let unique_element_id = generate_random_string(5);
    return `
    <div class="accordion__header" id="share-location_${unique_element_id}">
        <div class="d-flex align-items-center">
            <p class="mb-0">Share Location Action</p>
            <span class="accordion__toggle">
                <svg width="12" height="7" viewBox="0 0 12 7" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11.793 6.26729C12.0787 5.96737 12.0672 5.49263 11.7672 5.20694L6.51678 0.205606C6.22711 -0.0703173 5.77187 -0.0703173 5.4822 0.205606L0.231735 5.20694C-0.0681872 5.49263 -0.0797238 5.96737 0.205968 6.26729C0.491659 6.56721 0.966392 6.57875 1.26631 6.29306L5.99949 1.78447L10.7327 6.29306C11.0326 6.57875 11.5073 6.56721 11.793 6.26729Z" fill="#212121"/>
                </svg> </span>
        </div>
        <div class="delete_current_div">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 10L13.7 17M10.3 17L10 10M6 6L6.87554 19.133C6.94558 20.1836 7.81818 21 8.87111 21H15.1289C16.1818 21 17.0544 20.1836 17.1245 19.133L18 6M6 6H9M6 6H4M18 6H20M18 6H15M15 6V5C15 3.89543 14.1046 3 13 3H11C9.89543 3 9 3.89543 9 5V6M15 6H9" stroke="#FF0000" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>                                            
        </div>
    </div>
    <div class="accordion__body">
        <div class="col-sm-12 d-flex">
            <div class="col-sm-6 px-0 pr-2">
                <span>Suggested Text <span class="text-danger">*</span></span>
                <input type="text" class="template_input w-100 mt-1" placeholder="Suggested Text" id="card_suggested_text_${unique_element_id}">
            </div>
            <div class="col-sm-6 px-0">
                <span>Suggested Postback <span class="text-danger">*</span></span>
                <input type="text" class="template_input w-100 mt-1" placeholder="Suggested Postback" id="card_suggested_postback_${unique_element_id}">
            </div>
        </div>
        <div class="col-sm-12 mt-3">
            <span>Latitude <span class="text-danger">*</span></span>
            <input type="text" class="template_input w-100 mt-1" placeholder="Latitude" id="location_latitude_${unique_element_id}">
        </div>
        <div class="col-sm-12 mt-3">
            <span>Longitude <span class="text-danger">*</span></span>
            <input type="text" class="template_input w-100 mt-1" placeholder="Longitude" id="location_longitude_${unique_element_id}">
        </div>
        <div class="col-sm-12 mt-3">
            <span>Label <span class="text-danger">*</span></span>
            <input type="text" class="template_input w-100 mt-1" placeholder="Label" id="location_label_${unique_element_id}">
        </div>
    </div>`
}

function get_caraousel_pills_html(unique_element_id) {
    return `<li class="nav-item" id="card_${unique_element_id}">
                <a href="#${unique_element_id}" class="custom-link"
                data-toggle="pill" role="tab" aria-controls="${unique_element_id}" aria-selected="false">
                    <button class="show-button"><span class="btn_title text-truncate" id="pills_card_title_${unique_element_id}">Card Title</span>
                        <span class="show-button1">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 10L13.7 17M10.3 17L10 10M6 6L6.87554 19.133C6.94558 20.1836 7.81818 21 8.87111 21H15.1289C16.1818 21 17.0544 20.1836 17.1245 19.133L18 6M6 6H9M6 6H4M18 6H20M18 6H15M15 6V5C15 3.89543 14.1046 3 13 3H11C9.89543 3 9 3.89543 9 5V6M15 6H9" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        </span>
                    </button>
                    <button class="hide-button">
                        <span class="btn_title">Delete</span>
                        <span class="btn_title1 hide-button1">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4.2097 4.3871L4.29289 4.29289C4.65338 3.93241 5.22061 3.90468 5.6129 4.2097L5.70711 4.29289L12 10.585L18.2929 4.29289C18.6834 3.90237 19.3166 3.90237 19.7071 4.29289C20.0976 4.68342 20.0976 5.31658 19.7071 5.70711L13.415 12L19.7071 18.2929C20.0676 18.6534 20.0953 19.2206 19.7903 19.6129L19.7071 19.7071C19.3466 20.0676 18.7794 20.0953 18.3871 19.7903L18.2929 19.7071L12 13.415L5.70711 19.7071C5.31658 20.0976 4.68342 20.0976 4.29289 19.7071C3.90237 19.3166 3.90237 18.6834 4.29289 18.2929L10.585 12L4.29289 5.70711C3.93241 5.34662 3.90468 4.77939 4.2097 4.3871L4.29289 4.29289L4.2097 4.3871Z" fill="white"/>
                        </svg>
                        </span>
                        <span class="btn_title1 closeCard" id="delete_${unique_element_id}">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8.5 16.5858L4.70711 12.7929C4.31658 12.4024 3.68342 12.4024 3.29289 12.7929C2.90237 13.1834 2.90237 13.8166 3.29289 14.2071L7.79289 18.7071C8.18342 19.0976 8.81658 19.0976 9.20711 18.7071L20.2071 7.70711C20.5976 7.31658 20.5976 6.68342 20.2071 6.29289C19.8166 5.90237 19.1834 5.90237 18.7929 6.29289L8.5 16.5858Z" fill="white"/>
                        </svg>
                        </span>
                    </button> 
                </a>                                           
            </li>`
}

function get_caraousel_pills_body_html(unique_element_id) {
    return `<div class="tab-pane" id="${unique_element_id}" role="tabpanel">
        <div class="col-sm-12 mt-4">
            <div class="d-flex justify-content-between">
                <p class="mb-0 heading-text">Card Title <span
                        class="text-danger">*</span></p>
                <p class="mb-0 text-right input-length"><span
                        class="font-weight-bold card-title-count" id="card_title_count_${unique_element_id}">0</span>
                    <span class="text-secondary">/ 50</span></p>
            </div>

            <input type="text"
                class="template_input w-100 mt-1 card-title-text"
                placeholder="Card Title" id="caraousel_card_title_${unique_element_id}" maxlength="50">
        </div>
        <div class="col-sm-12 mt-4">
            <p class="mb-0 heading-text">Image/Video URL <span
                    class="text-danger">*</span> 
                    <sup class="ml-2">
                    <svg data-toggle="tooltip" data-placement="top"
                        title="URL types like Text and HTTP are not supported. Please use a valid URL type like JPEG, JPG, GIF, and PNG for images or H263, M4V, MP4, MPEG, MPEG4, and WebM for videos."
                        width="16" height="16" viewBox="0 0 16 16" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M14.4001 7.99998C14.4001 9.69736 13.7258 11.3252 12.5256 12.5255C11.3253 13.7257 9.69748 14.4 8.0001 14.4C6.30271 14.4 4.67485 13.7257 3.47461 12.5255C2.27438 11.3252 1.6001 9.69736 1.6001 7.99998C1.6001 6.30259 2.27438 4.67472 3.47461 3.47449C4.67485 2.27426 6.30271 1.59998 8.0001 1.59998C9.69748 1.59998 11.3253 2.27426 12.5256 3.47449C13.7258 4.67472 14.4001 6.30259 14.4001 7.99998ZM8.0001 5.59998C7.85954 5.59984 7.72142 5.63674 7.59966 5.70696C7.47789 5.77718 7.37678 5.87825 7.3065 5.99998C7.25575 6.09428 7.18659 6.17743 7.10311 6.2445C7.01963 6.31158 6.92353 6.36121 6.82051 6.39046C6.71749 6.4197 6.60965 6.42797 6.50338 6.41476C6.39711 6.40156 6.29457 6.36715 6.20184 6.31358C6.10912 6.26002 6.02809 6.18837 5.96356 6.10291C5.89904 6.01744 5.85233 5.91989 5.8262 5.81604C5.80007 5.71219 5.79506 5.60415 5.81147 5.49832C5.82787 5.3925 5.86536 5.29104 5.9217 5.19998C6.18587 4.74247 6.59362 4.3849 7.08172 4.18275C7.56981 3.98059 8.11097 3.94512 8.62127 4.08186C9.13157 4.2186 9.5825 4.51989 9.90412 4.93901C10.2257 5.35814 10.4001 5.87167 10.4001 6.39998C10.4002 6.89647 10.2465 7.3808 9.95991 7.78626C9.67336 8.19172 9.26816 8.49837 8.8001 8.66398V8.79998C8.8001 9.01215 8.71581 9.21563 8.56578 9.36566C8.41575 9.51569 8.21227 9.59998 8.0001 9.59998C7.78792 9.59998 7.58444 9.51569 7.43441 9.36566C7.28438 9.21563 7.2001 9.01215 7.2001 8.79998V7.99998C7.2001 7.7878 7.28438 7.58432 7.43441 7.43429C7.58444 7.28426 7.78792 7.19998 8.0001 7.19998C8.21227 7.19998 8.41575 7.11569 8.56578 6.96566C8.71581 6.81563 8.8001 6.61215 8.8001 6.39998C8.8001 6.1878 8.71581 5.98432 8.56578 5.83429C8.41575 5.68426 8.21227 5.59998 8.0001 5.59998ZM8.0001 12C8.21227 12 8.41575 11.9157 8.56578 11.7657C8.71581 11.6156 8.8001 11.4121 8.8001 11.2C8.8001 10.9878 8.71581 10.7843 8.56578 10.6343C8.41575 10.4843 8.21227 10.4 8.0001 10.4C7.78792 10.4 7.58444 10.4843 7.43441 10.6343C7.28438 10.7843 7.2001 10.9878 7.2001 11.2C7.2001 11.4121 7.28438 11.6156 7.43441 11.7657C7.58444 11.9157 7.78792 12 8.0001 12Z"
                            fill="#2D2D2D" />
                    </svg>
                </sup><span
                    class=" sub-info-text">(Min. Resolution 770*335, Max
                    Resolution 1440*720)</span></p>
            <input type="text"
                class="template_input w-100 mt-3 media-url-input"
                placeholder="Enter a valid public URL" id="caraousel_media_url_${unique_element_id}">

            <span class="preview-media-logo" style="display: none;">
                <a href="/" target="_blank" id="open_carousel_media_${unique_element_id}">
                    <svg width="20" height="20" viewBox="0 0 24 24"
                        fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                            d="M7.25019 4.5H10.7496C11.1638 4.5 11.4996 4.83579 11.4996 5.25C11.4996 5.6297 11.2174 5.94349 10.8513 5.99315L10.7496 6H7.24983C6.07088 5.99944 5.10359 6.90639 5.00795 8.06095L5.00037 8.21986L5.00321 16.7505C5.00352 17.9414 5.92894 18.9159 7.09975 18.9948L7.2538 18.9999L15.7519 18.9882C16.9416 18.9866 17.9146 18.0618 17.9936 16.8921L17.9988 16.7382V13.2319C17.9988 12.8177 18.3346 12.4819 18.7488 12.4819C19.1285 12.4819 19.4423 12.7641 19.4919 13.1302L19.4988 13.2319V16.7382C19.4988 18.7405 17.9294 20.3767 15.9529 20.4828L15.7539 20.4882L7.25836 20.4999L7.05504 20.4948C5.14248 20.3952 3.60904 18.8626 3.50846 16.95L3.50321 16.7509L3.50098 8.25253L3.50539 8.05003C3.60548 6.13732 5.13876 4.60432 7.05105 4.50511L7.25019 4.5H10.7496H7.25019ZM14.0037 3L20.0543 3.00146L20.1539 3.01152L20.2356 3.02756L20.3432 3.05991L20.4617 3.11196L20.5146 3.14222C20.7742 3.29719 20.9571 3.56642 20.9945 3.88033L21.0016 4V10.007C21.0016 10.5593 20.5539 11.007 20.0016 11.007C19.4888 11.007 19.0661 10.621 19.0084 10.1236L19.0016 10.007L19.001 6.413L12.7072 12.7071C12.3467 13.0676 11.7795 13.0953 11.3872 12.7903L11.293 12.7071C10.9325 12.3466 10.9048 11.7794 11.2098 11.3871L11.293 11.2929L17.585 5H14.0037C13.4909 5 13.0682 4.61396 13.0105 4.11662L13.0037 4C13.0037 3.44772 13.4514 3 14.0037 3Z"
                            fill="#7B7A7B" />
                    </svg>
                </a>
            </span>
        </div>
        <div class="col-sm-12 mt-4">
            <p class="mb-0 heading-text">Card Description <span
                    class="text-danger">*</span></p>

            <textarea class="w-100 message-text-input"
                maxlength="1000"
                placeholder="Enter card description" id="caraousel_card_description_${unique_element_id}"></textarea>
            <p class="mb-0 text-right input-length"><span
                    class="font-weight-bold"
                    id="caraousel_description_count_${unique_element_id}">0</span> <span
                    class="text-secondary">/ 1000</span></p>

        </div>
        <div class="add-card-reply  mt-4 mb-3 px-3 d-flex align-items-center justify-content-between">
            <p class="mb-0 heading-text" style="padding-right: 10px;">Add Card Reply
                <sup class="ml-2 hand-cursor">
                    <svg data-toggle="tooltip" data-placement="top"
                        title="To add suggested replies in rich cards/ carousels."
                        width="16" height="16" viewBox="0 0 16 16" fill="none"
                        xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd"
                            d="M14.4001 7.99998C14.4001 9.69736 13.7258 11.3252 12.5256 12.5255C11.3253 13.7257 9.69748 14.4 8.0001 14.4C6.30271 14.4 4.67485 13.7257 3.47461 12.5255C2.27438 11.3252 1.6001 9.69736 1.6001 7.99998C1.6001 6.30259 2.27438 4.67472 3.47461 3.47449C4.67485 2.27426 6.30271 1.59998 8.0001 1.59998C9.69748 1.59998 11.3253 2.27426 12.5256 3.47449C13.7258 4.67472 14.4001 6.30259 14.4001 7.99998ZM8.0001 5.59998C7.85954 5.59984 7.72142 5.63674 7.59966 5.70696C7.47789 5.77718 7.37678 5.87825 7.3065 5.99998C7.25575 6.09428 7.18659 6.17743 7.10311 6.2445C7.01963 6.31158 6.92353 6.36121 6.82051 6.39046C6.71749 6.4197 6.60965 6.42797 6.50338 6.41476C6.39711 6.40156 6.29457 6.36715 6.20184 6.31358C6.10912 6.26002 6.02809 6.18837 5.96356 6.10291C5.89904 6.01744 5.85233 5.91989 5.8262 5.81604C5.80007 5.71219 5.79506 5.60415 5.81147 5.49832C5.82787 5.3925 5.86536 5.29104 5.9217 5.19998C6.18587 4.74247 6.59362 4.3849 7.08172 4.18275C7.56981 3.98059 8.11097 3.94512 8.62127 4.08186C9.13157 4.2186 9.5825 4.51989 9.90412 4.93901C10.2257 5.35814 10.4001 5.87167 10.4001 6.39998C10.4002 6.89647 10.2465 7.3808 9.95991 7.78626C9.67336 8.19172 9.26816 8.49837 8.8001 8.66398V8.79998C8.8001 9.01215 8.71581 9.21563 8.56578 9.36566C8.41575 9.51569 8.21227 9.59998 8.0001 9.59998C7.78792 9.59998 7.58444 9.51569 7.43441 9.36566C7.28438 9.21563 7.2001 9.01215 7.2001 8.79998V7.99998C7.2001 7.7878 7.28438 7.58432 7.43441 7.43429C7.58444 7.28426 7.78792 7.19998 8.0001 7.19998C8.21227 7.19998 8.41575 7.11569 8.56578 6.96566C8.71581 6.81563 8.8001 6.61215 8.8001 6.39998C8.8001 6.1878 8.71581 5.98432 8.56578 5.83429C8.41575 5.68426 8.21227 5.59998 8.0001 5.59998ZM8.0001 12C8.21227 12 8.41575 11.9157 8.56578 11.7657C8.71581 11.6156 8.8001 11.4121 8.8001 11.2C8.8001 10.9878 8.71581 10.7843 8.56578 10.6343C8.41575 10.4843 8.21227 10.4 8.0001 10.4C7.78792 10.4 7.58444 10.4843 7.43441 10.6343C7.28438 10.7843 7.2001 10.9878 7.2001 11.2C7.2001 11.4121 7.28438 11.6156 7.43441 11.7657C7.58444 11.9157 7.78792 12 8.0001 12Z"
                            fill="#2D2D2D" />
                    </svg>
                </sup> 
                <br>
                <span style="color:#5e5b5b; font-size: 12px">Note - A flow will be triggered based on the Postback text added, so make sure you add a valid text that initiates a correct intent.</span>
            </p>
            <!-- sprint 5.7 -->
            <div class="btn-group custom-dropdown-add-reply">
                <button type="button"
                    class="btn btn-primary dropdown-toggle rect-border"
                    data-toggle="dropdown" aria-expanded="false">
                    Add Reply
                </button>
                <div class="dropdown-menu">
                    <a class="dropdown-item simple-reply-caraousel">Simple
                        Reply</a>
                    <a class="dropdown-item open-url-caraousel">Open URL
                        Action</a>
                    <a class="dropdown-item dail-action-caraousel">Dial
                        Action</a>
                    <a class="dropdown-item share-loaction-caraousel">Share
                        Location Action</a>
                </div>
            </div>

        </div>
        <div class="col-sm-12 dynamic-append-div">
            <div class="accordion mb-3 carouseldynamicaccordion">
            </div>
        </div>
    </div>`
}

$(document).on('click', '.show-button', function () {
    $('.show-button').removeClass('selected');
    $('.show-button1').addClass('selected');
    $(this).addClass('selected');
    $(this).children().addClass('del-enabled');
});

$(document).on('click', '.show-button1', function () {
    $(this).parent().next().css('display', 'flex')
    $(this).parent().hide()
});

$(document).on('click', '.hide-button1', function () {
    $(this).parent().prev().show()
    $(this).parent().hide()
});

$(document).ready(function () {
    $('#campaign_batch_table').DataTable({});
    $('.dataTables_length').addClass('bs-select');
});

$("#rcs_rich_card_media_url").keyup(function () {
    let url = $(this).val()
    if ($(this).val() && isValidURL(url)) {
        $(".message-type-rich-card .preview-media-logo").show();
        $('#rich_card_url').attr('href', url)
    } else {
        $(".message-type-rich-card .preview-media-logo").hide();
        $('#rich_card_url').attr('href', null)
    }
});

$("#rcs_media_url").keyup(function () {
    let url = $(this).val()
    if ($(this).val() && isValidURL(url)) {
        $(".message-type-media-div .preview-media-logo").show();
        $('.redirect-url').attr('href', url)
    } else {
        $(".message-type-media-div .preview-media-logo").hide();
        $('.rich_card_url').attr('href', null)
    }
});


function save_rcs_campaign_template(el, update_template) {
    let template_name = $('#rcs_template_name').val();

    template_name = stripHTML(template_name);
    template_name = remove_special_char_from_str(template_name);

    if (template_name.trim() == '') {
        show_campaign_toast("Template name cannot be empty!");
        return;
    }

    if (check_all_speical_chars(template_name)) {
        show_campaign_toast("Template name with only special characters is not allowed!");
        return;
    }

    let message_type = $('#select-message-type-dropdown .selected').data('value');
    if (message_type == null || message_type == '') {
        show_campaign_toast("Please select a valid template type!");
        return;
    }

    let json_string = {
        'bot_pk': get_url_multiple_vars()['bot_pk'][0],
        'template_name': template_name,
        'message_type': message_type,
        'update_template': update_template, // True if user is editing an existing template, else False if user is saving a new template.
    };
    json_string = get_template_data(json_string, message_type);

    if ("error_message" in json_string) {
        show_campaign_toast(json_string.error_message);
        return;
    }

    json_string = JSON.stringify(json_string);

    var encrypted_data = campaign_custom_encrypt(json_string);

    encrypted_data = {
        "Request": encrypted_data
    };

    var params = JSON.stringify(encrypted_data);

    el.innerText = "Saving...";

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", '/campaign/save-template-rcs/', true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrfmiddlewaretoken());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            response = campaign_custom_decrypt(response.Response);
            response = JSON.parse(response);

            if (response["status"] == 200) {
                initialize_campaign_template_table();
                $('#upload_template_modal').modal('hide');
                if (update_template) {
                    show_campaign_toast('Template Edited successfully.');
                } else {
                    show_campaign_toast('Template uploaded successfully.');
                }
            } else {
                show_campaign_toast(response["message"]);
            }
            el.innerText = "Save Template";
        } else {
            show_campaign_toast('Unable to connect to server. Please try again later.');
        }
    }
    xhttp.send(params);
}

//Gathers and returns all the data of RCS Template filled by user.
function get_template_data(json_string, message_type) {
    if (message_type == 1) {
        let text_message = $('#message-text-user-input').val();
        text_message = stripHTML(text_message);
        text_message = strip_unwanted_security_characters(text_message);
        if (text_message.trim() == '') {
            json_string.error_message = "Message text cannot be empty!";
            return json_string;
        }
        if (text_message.length > 2000) {
            json_string.error_message = "Message cannot exceed 2000 characters!";
            return json_string;
        }
        json_string.text_message = text_message;
    } else if (message_type == 2) {
        let media_url = $('#rcs_media_url').val();
        if (!isValidURL(media_url)) {
            json_string.error_message = "Please enter a valid media URL!";
            return json_string;
        }
        json_string.media_url = media_url;
    } else if (message_type == 3) {
        let card_title = $('#rcs_rich_card_title').val();
        card_title = stripHTML(card_title);
        card_title = strip_unwanted_security_characters(card_title);
        if (card_title.trim() == '') {
            json_string.error_message = "Rich Card title cannot be empty!";
            return json_string;
        }
        if (card_title.length > 50) {
            json_string.error_message = "Rich Card title cannot ";
            return json_string;
        }

        let card_media_url = $('#rcs_rich_card_media_url').val();
        if (!isValidURL(card_media_url)) {
            json_string.error_message = "Please enter a valid media URL!";
            return json_string;
        }

        let card_description = $('#card-description-text').val();
        card_description = stripHTML(card_description);
        card_description = strip_unwanted_security_characters(card_description);
        if (card_description.trim() == '') {
            json_string.error_message = "Rich Card description cannot be empty!";
            return json_string;
        }
        if (card_description.length > 1000) {
            json_string.error_message = "Rich Card description cannot exceed 1000 characters!";
            return json_string;
        }

        json_string.card_title = card_title;
        json_string.card_media_url = card_media_url;
        json_string.card_description = card_description;

        json_string.card_reply = [];
        if ($('#AccordionRichCard .accordion__header').length > 0) {
            $('#AccordionRichCard .accordion__header').each(function () {
                let reply_type = this.id.split('_')[0];
                let element_id = this.id.split('_')[1];
                let reply_data = {};
                if (reply_type == 'simple-reply') {
                    reply_data.type = 'simple_reply';
                    json_string = get_simple_reply_data(json_string, reply_data, element_id, true);
                    if ('error_message' in json_string) return false;
                } else if (reply_type == 'open-url') {
                    reply_data.type = 'open_url';
                    json_string = get_open_url_action_data(json_string, reply_data, element_id, true);
                    if ('error_message' in json_string) return false;
                } else if (reply_type == 'dial-action') {
                    reply_data.type = 'dial_action';
                    json_string = get_dial_action_data(json_string, reply_data, element_id, true);
                    if ('error_message' in json_string) return false;
                } else if (reply_type == 'share-location') {
                    reply_data.type = 'share_location';
                    json_string = get_share_location_data(json_string, reply_data, element_id, true);
                    if ('error_message' in json_string) return false;
                }
            })
            if ('error_message' in json_string) return json_string;
        }
    } else if (message_type == 4) {
        let carousel_cards = $('.custom-nav-tab .nav-item')
        if (carousel_cards.length < 2) {
            json_string.error_message = "Minimum 2 cards are required in Carousel else use the Rich Card for adding a single card."
        }
        json_string.carousel_cards = []
        $(carousel_cards).each(function () {
            let element_id = this.id.split('_')[1];
            let card_data = {};
            let card_title = $('#caraousel_card_title_' + element_id).val();
            card_title = stripHTML(card_title);
            card_title = strip_unwanted_security_characters(card_title);
            if (card_title.trim() == '') {
                json_string.error_message = "Carousel Card title cannot be empty!";
                return false;
            }
            if (card_title.length > 50) {
                json_string.error_message = "Carousel Card title cannot exceed 50 characters!";
                return false;
            }

            let card_media_url = $('#caraousel_media_url_' + element_id).val();
            if (!isValidURL(card_media_url)) {
                json_string.error_message = "Please enter a valid media URL!";
                return false;
            }

            let card_description = $('#caraousel_card_description_' + element_id).val();
            card_description = stripHTML(card_description);
            card_description = strip_unwanted_security_characters(card_description);
            if (card_description.trim() == '') {
                json_string.error_message = "Carousel Card description cannot be empty!";
                return false;
            }
            if (card_description.length > 1000) {
                json_string.error_message = "Carousel Card Description cannot exceed 1000 characters!";
                return false;
            }

            card_data.card_title = card_title;
            card_data.card_media_url = card_media_url;
            card_data.card_description = card_description;

            card_data.card_reply = [];
            if ($('#' + element_id + ' .accordion__header').length > 0) {
                $('#' + element_id + ' .accordion__header').each(function () {
                    let reply_type = this.id.split('_')[0];
                    let element_id = this.id.split('_')[1];
                    let reply_data = {};
                    if (reply_type == 'simple-reply') {
                        reply_data.type = 'simple_reply';
                        card_data = get_simple_reply_data(card_data, reply_data, element_id, true);
                        if ('error_message' in card_data) {
                            json_string.error_message = card_data.error_message
                            return false;
                        }
                    } else if (reply_type == 'open-url') {
                        reply_data.type = 'open_url';
                        card_data = get_open_url_action_data(card_data, reply_data, element_id, true);
                        if ('error_message' in card_data) {
                            json_string.error_message = card_data.error_message
                            return false;
                        }
                    } else if (reply_type == 'dial-action') {
                        reply_data.type = 'dial_action';
                        card_data = get_dial_action_data(card_data, reply_data, element_id, true);
                        if ('error_message' in card_data) {
                            json_string.error_message = card_data.error_message
                            return false;
                        }
                    } else if (reply_type == 'share-location') {
                        reply_data.type = 'share_location';
                        card_data = get_share_location_data(card_data, reply_data, element_id, true);
                        if ('error_message' in card_data) {
                            json_string.error_message = card_data.error_message
                            return false;
                        }
                    }
                })
            }
            if ('error_message' in json_string) return false;
            json_string.carousel_cards.push(card_data)
        })
        if ('error_message' in json_string) return json_string;
    }

    json_string.suggested_reply = [];
    if ($('#accordiondynamic .accordion__header').length > 0) {
        $('#accordiondynamic .accordion__header').each(function () {
            let reply_type = this.id.split('_')[0];
            let element_id = this.id.split('_')[1];
            let reply_data = {};
            if (reply_type == 'simple-reply') {
                reply_data.type = 'simple_reply';
                json_string = get_simple_reply_data(json_string, reply_data, element_id, false);
                if ('error_message' in json_string) return false;
            } else if (reply_type == 'open-url') {
                reply_data.type = 'open_url';
                json_string = get_open_url_action_data(json_string, reply_data, element_id, false);
                if ('error_message' in json_string) return false;
            } else if (reply_type == 'dial-action') {
                reply_data.type = 'dial_action';
                json_string = get_dial_action_data(json_string, reply_data, element_id, false);
                if ('error_message' in json_string) return false;
            } else if (reply_type == 'share-location') {
                reply_data.type = 'share_location';
                json_string = get_share_location_data(json_string, reply_data, element_id, false);
                if ('error_message' in json_string) return false;
            }
        })
        if ('error_message' in json_string) return json_string;
    }

    return json_string;
}

function get_simple_reply_data(json_string, reply_data, element_id, is_card_reply) {

    let card_suggested_text = $('#card_suggested_text_' + element_id).val();
    card_suggested_text = stripHTML(card_suggested_text);
    card_suggested_text = strip_unwanted_security_characters(card_suggested_text);

    if (card_suggested_text.trim() == '') {
        json_string.error_message = "Simple Reply suggested text cannot be empty!";
        return json_string;
    }
    if (card_suggested_text.length > 25) {
        json_string.error_message = "The size of the reply text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let card_suggested_postback = $('#card_suggested_postback_' + element_id).val();
    card_suggested_postback = stripHTML(card_suggested_postback);
    card_suggested_postback = strip_unwanted_security_characters(card_suggested_postback);

    if (card_suggested_postback.trim() == '') {
        json_string.error_message = "Simple Reply suggested postback cannot be empty!";
        return json_string;
    }
    if (card_suggested_postback.length > 25) {
        json_string.error_message = "The size of the reply postback text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    reply_data.card_suggested_text = card_suggested_text;
    reply_data.card_suggested_postback = card_suggested_postback;
    if (is_card_reply) {
        json_string.card_reply.push(reply_data);
    } else {
        json_string.suggested_reply.push(reply_data)
    }

    return json_string;
}

function get_open_url_action_data(json_string, reply_data, element_id, is_card_reply) {
    let card_suggested_text = $('#card_suggested_text_' + element_id).val();
    card_suggested_text = stripHTML(card_suggested_text);
    card_suggested_text = strip_unwanted_security_characters(card_suggested_text);

    if (card_suggested_text.trim() == '') {
        json_string.error_message = "Open URL Action suggested text cannot be empty!";
        return json_string;
    }
    if (card_suggested_text.length > 25) {
        json_string.error_message = "The size of the reply text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let card_suggested_postback = $('#card_suggested_postback_' + element_id).val();
    card_suggested_postback = stripHTML(card_suggested_postback);
    card_suggested_postback = strip_unwanted_security_characters(card_suggested_postback);

    if (card_suggested_postback.trim() == '') {
        json_string.error_message = "Open URL Action suggested postback cannot be empty!";
        return json_string;
    }
    if (card_suggested_postback.length > 25) {
        json_string.error_message = "The size of the reply postback text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let url_to_open = $('#url_to_open_' + element_id).val();
    if (!isValidURL(url_to_open)) {
        json_string.error_message = "Please enter a valid URL to open!";
        return json_string;
    }

    reply_data.card_suggested_text = card_suggested_text;
    reply_data.card_suggested_postback = card_suggested_postback;
    reply_data.url_to_open = url_to_open;
    if (is_card_reply) {
        json_string.card_reply.push(reply_data);
    } else {
        json_string.suggested_reply.push(reply_data)
    }

    return json_string;
}

function get_dial_action_data(json_string, reply_data, element_id, is_card_reply) {
    let card_suggested_text = $('#card_suggested_text_' + element_id).val();
    card_suggested_text = stripHTML(card_suggested_text);
    card_suggested_text = strip_unwanted_security_characters(card_suggested_text);

    if (card_suggested_text.trim() == '') {
        json_string.error_message = "Dial Action suggested text cannot be empty!";
        return json_string;
    }
    if (card_suggested_text.length > 25) {
        json_string.error_message = "The size of the reply text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let card_suggested_postback = $('#card_suggested_postback_' + element_id).val();
    card_suggested_postback = stripHTML(card_suggested_postback);
    card_suggested_postback = strip_unwanted_security_characters(card_suggested_postback);

    if (card_suggested_postback.trim() == '') {
        json_string.error_message = "Dial Action suggested postback cannot be empty!";
        return json_string;
    }
    if (card_suggested_postback.length > 25) {
        json_string.error_message = "The size of the reply postback text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let dial_action_number = $('#dial_action_number_' + element_id).val();
    if (!is_valid_phone_number(dial_action_number)) {
        json_string.error_message = "Please enter a valid Dial Action number!";
        return json_string;
    }

    reply_data.card_suggested_text = card_suggested_text;
    reply_data.card_suggested_postback = card_suggested_postback;
    reply_data.dial_action_number = dial_action_number;
    if (is_card_reply) {
        json_string.card_reply.push(reply_data);
    } else {
        json_string.suggested_reply.push(reply_data)
    }

    return json_string;
}

function get_share_location_data(json_string, reply_data, element_id, is_card_reply) {
    let card_suggested_text = $('#card_suggested_text_' + element_id).val();
    card_suggested_text = stripHTML(card_suggested_text);
    card_suggested_text = strip_unwanted_security_characters(card_suggested_text);

    if (card_suggested_text.trim() == '') {
        json_string.error_message = "Share Location Action suggested text cannot be empty!";
        return json_string;
    }
    if (card_suggested_text.length > 25) {
        json_string.error_message = "The size of the reply text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let card_suggested_postback = $('#card_suggested_postback_' + element_id).val();
    card_suggested_postback = stripHTML(card_suggested_postback);
    card_suggested_postback = strip_unwanted_security_characters(card_suggested_postback);

    if (card_suggested_postback.trim() == '') {
        json_string.error_message = "Share Location Action suggested postback cannot be empty!";
        return json_string;
    }
    if (card_suggested_postback.length > 25) {
        json_string.error_message = "The size of the reply postback text exceeds the maximum limit of 25 characters!";
        return json_string;
    }

    let location_latitude = $('#location_latitude_' + element_id).val();
    if (!is_valid_latitude(location_latitude)) {
        json_string.error_message = "Please enter a valid latitude!";
        return json_string;
    }
    let location_longitude = $('#location_longitude_' + element_id).val();
    if (!is_valid_longitude(location_longitude)) {
        json_string.error_message = "Please enter a valid longitude!";
        return json_string;
    }

    let location_label = $('#location_label_' + element_id).val();
    location_label = stripHTML(location_label);
    location_label = strip_unwanted_security_characters(location_label);

    if (location_label.trim() == '') {
        json_string.error_message = "Please enter a valid location label!";
        return json_string;
    }

    reply_data.card_suggested_text = card_suggested_text;
    reply_data.card_suggested_postback = card_suggested_postback;
    reply_data.location_latitude = location_latitude;
    reply_data.location_longitude = location_longitude;
    reply_data.location_label = location_label;
    if (is_card_reply) {
        json_string.card_reply.push(reply_data);
    } else {
        json_string.suggested_reply.push(reply_data)
    }

    return json_string;
}

//Modifies Upload RCS Template Modal for Editing RCS Template
function set_edit_rcs_campaign_template_modal(template_metadata) {
    template_metadata = JSON.parse(template_metadata);
    reset_rcs_template_modal();
    $('#upload_template_modal').modal();
    $('#save_template_btn').attr('onclick', 'save_rcs_campaign_template(this, true)');

    let template_name = template_metadata.template_name;
    let message_type = template_metadata.message_type;
    let message_type_name = message_type_name_mapping(message_type);

    $('#modal_title_heading').text('Edit Template');
    $('#rcs_template_name').val(template_name);
    $('#rcs_template_name').attr('disabled', 'disabled');
    $('#select-message-type-dropdown [data-value="' + message_type + '"]').addClass('selected');
    $('#select-message-type-dropdown .selected').click();
    $('#select-message-type-dropdown').removeClass('active');
    $('#select-text-value').text(message_type_name);
    $('#select-message-type-dropdown').css('pointer-events', 'none')
    $('#select-message-type-dropdown').css('opacity', '0.5')
    $('#save_template_btn').attr('onclick', 'save_rcs_campaign_template(this, true)');

    populate_message_details(template_metadata, message_type);
}

//Populates RCS Template data in Edit Template modal for updating the template.
function populate_message_details(template_metadata, message_type) {
    $('#accordiondynamic, #Carouselaccordion, #AccordionRichCard').html('');
    if (message_type == '1') {
        $('#message-text-user-input').val(template_metadata.text_message);
    } else if (message_type == '2') {
        $('#rcs_media_url').val(template_metadata.media_url).keyup();
    } else if (message_type == '3') {
        $('#rcs_rich_card_title').val(template_metadata.card_title).keyup();
        $('#rcs_rich_card_media_url').val(template_metadata.card_media_url).keyup();
        $('#card-description-text').val(template_metadata.card_description).keyup();
        $(template_metadata.card_reply).each(function () {
            add_suggested_reply(this, message_type)
        })
    } else if (message_type == '4') {
        let is_first_card = true
        $(template_metadata.carousel_cards).each(function () {
            let element_id;
            if (is_first_card && $('.custom-nav-tab .nav-item').length == 1) {
                is_first_card = false;
                element_id = $('.custom-nav-tab .nav-item').attr('id').split('_')[1];
            } else {
                $('#add-dynamic-card-button').click();
                element_id = $('.custom-nav-tab .nav-item:last').attr("id").split('_')[1];
            }
            $('#caraousel_card_title_' + element_id).val(this.card_title).focusout().keyup();
            $('#caraousel_media_url_' + element_id).val(this.card_media_url).keyup();
            $('#caraousel_card_description_' + element_id).val(this.card_description).keyup();

            $(this.card_reply).each(function () {
                add_suggested_reply(this, message_type, element_id)
            })
        })
    }
    $(template_metadata.suggested_reply).each(function () {
        add_suggested_reply(this, 'suggested_reply')
    })
}

//Adds and populates suggested replies for message/Rich Card/Carousel Cards
function add_suggested_reply(card_data, message_type, carousel_id = null) {
    let element_id;
    if (card_data.type == 'simple_reply') {
        if (message_type == '3') {
            $SimpleReplyRichcardCaraousel.click()
            element_id = $('#AccordionRichCard .accordion__header:last').attr("id");
        } else if (message_type == '4') {
            $('#' + carousel_id + ' .simple-reply-caraousel').click()
            element_id = $('#' + carousel_id + ' .accordion__header:last').attr("id");
        } else if (message_type == 'suggested_reply') {
            $SimpleReplyAction.click()
            element_id = $('#accordiondynamic .accordion__header:last').attr("id");
        }
        element_id = element_id.split('_')[1]
    } else if (card_data.type == 'open_url') {
        if (message_type == '3') {
            $OpenURLActionRichcardCaraousel.click()
            element_id = $('#AccordionRichCard .accordion__header:last').attr("id");
        } else if (message_type == '4') {
            $('#' + carousel_id + ' .open-url-caraousel').click()
            element_id = $('#' + carousel_id + ' .accordion__header:last').attr("id");
        } else if (message_type == 'suggested_reply') {
            $OpenURLAction.click()
            element_id = $('#accordiondynamic .accordion__header:last').attr("id");
        }
        element_id = element_id.split('_')[1]
        $('#url_to_open_' + element_id).val(card_data.url_to_open)
    } else if (card_data.type == 'dial_action') {
        if (message_type == '3') {
            $DailActionRichcardCaraousel.click()
            element_id = $('#AccordionRichCard .accordion__header:last').attr("id");
        } else if (message_type == '4') {
            $('#' + carousel_id + ' .dail-action-caraousel').click()
            element_id = $('#' + carousel_id + ' .accordion__header:last').attr("id");
        } else if (message_type == 'suggested_reply') {
            $DailAction.click()
            element_id = $('#accordiondynamic .accordion__header:last').attr("id");
        }
        element_id = element_id.split('_')[1]
        $('#dial_action_number_' + element_id).val(card_data.dial_action_number)
    } else if (card_data.type == 'share_location') {
        if (message_type == '3') {
            $ShareLocationActionRichcardCaraousel.click()
            element_id = $('#AccordionRichCard .accordion__header:last').attr("id");
        } else if (message_type == '4') {
            $('#' + carousel_id + ' .share-loaction-caraousel').click()
            element_id = $('#' + carousel_id + ' .accordion__header:last').attr("id");
        } else if (message_type == 'suggested_reply') {
            $ShareLocationAction.click()
            element_id = $('#accordiondynamic .accordion__header:last').attr("id");
        }
        element_id = element_id.split('_')[1]
        $('#location_latitude_' + element_id).val(card_data.location_latitude)
        $('#location_longitude_' + element_id).val(card_data.location_longitude)
        $('#location_label_' + element_id).val(card_data.location_label)
    }
    $('#card_suggested_text_' + element_id).val(card_data.card_suggested_text)
    $('#card_suggested_postback_' + element_id).val(card_data.card_suggested_postback)
}

//Modifies Edit Template modal back to New Template modal for uploading new RCS Template
function reset_rcs_template_modal() {
    $('#modal_title_heading').text('New Template')
    $('#rcs_template_name').val('')
    $('#select-message-type-dropdown .select-message-type-dropdown__list-item').removeClass('selected')
    $('#select-message-type-dropdown [data-value="1"]').addClass('selected')
    $('#select-message-type-dropdown .selected').click()
    $('#select-message-type-dropdown').removeClass('active')
    $('#select-text-value').text('Text')
    $('#accordiondynamic, #Carouselaccordion, #AccordionRichCard, .carouseldynamicaccordion').html('');
    $('#rcs_template_name').removeAttr('disabled');
    $('#select-message-type-dropdown').css('pointer-events', 'auto')
    $('#select-message-type-dropdown').css('opacity', '1')
    $('#save_template_btn').attr('onclick', 'save_rcs_campaign_template(this, false)');

    //Resets Text Message and Media URL
    $('#message-text-user-input').val('')
    $('#rcs_media_url').val('')

    //Resets Rich Card
    $('#rcs_rich_card_title').val('')
    $('#rcs_rich_card_media_url').val('')
    $('#card-description-text').val('')

    //Resets Carousel Cards
    $('.custom-nav-tab .nav-item').each(function () {
        this.remove()
    })
    $('#pills-tabContent').empty()
    $('#add-dynamic-card-button').click();
}

function message_type_name_mapping(message_type) {
    if (message_type == '1') {
        return 'Text';
    } else if (message_type == '2') {
        return 'Media';
    } else if (message_type == '3') {
        return 'Rich Card';
    } else if (message_type == '4') {
        return 'Carousel';
    }
}

function is_valid_phone_number(phone) {
    phone = phone.trim();
    let regex = /\+[0-9]{1,3}[0-9]{4,14}/;
    if (phone != "" && regex.test(phone)) {
        return true;
    }
    return false;
}

function is_valid_latitude(coordinates) {
    let regex = /^(\+|-)?(?:90(?:(?:\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,6})?))$/
    if (coordinates != "" && regex.test(coordinates)) {
        return true;
    }
    return false;
}

function is_valid_longitude(coordinates) {
    let regex = /^(\+|-)?(?:180(?:(?:\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,6})?))$/
    if (coordinates != "" && regex.test(coordinates)) {
        return true;
    }
    return false;
}

function scroll_template_modal_to_bottom() {
    let ele = document.querySelector('#upload_template_modal .modal-body');
    ele.scrollTop = ele.scrollHeight;
}
