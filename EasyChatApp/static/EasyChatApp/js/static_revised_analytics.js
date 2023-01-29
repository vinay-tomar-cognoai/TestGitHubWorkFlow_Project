
// Drop Down Code

function create_custom_dropdowns() {

    $(".easychat-console-select-drop").each(function (i, select) {
        if (!$(this).next().hasClass('easychat-dropdown-select-custom')) {
            $(this).after('<div id="' + this.id + "-select" + '" class="easychat-dropdown-select-custom wide ' + ($(this).attr('class') || '') + '" tabindex="0" style = margin-top: -5px!important;><span class="current" id="' + this.id + "-current-wrapper" + '"></span><div class="list"><ul></ul></div></div>');
            var dropdown = $(this).next();
            var options = $(select).find('span');
            var selected = $(this).find('easychat-console-language-option:selected');

            dropdown.find('.current').html(selected.data('display-text') || selected.text());
            options.each(function (j, o) {

                var display = $(o).data('display-text') || '';
                dropdown.find('ul').append('<li class="easychat-console-language-option ' + ($(o).is(':selected') ? 'selected' : '') + '" data-value="' + $(o).data("value") + '" data-display-text="' + display + '">' + $(o).text() + '</li>');
            });

            if (this.id == "easychat-console-lang-dropdown") {

                var url_string = window.location.href
                var url = new URL(url_string);
                var selected_language = url.searchParams.get("selected_language");
                $("#easychat-console-lang-dropdown-select ul li[data-value='" + selected_language + "']").addClass('easychat-lang-selected');
                var default_select_lang_drop = $('#easychat-console-lang-dropdown-select ul li[data-value="' + selected_language + '"]').text();
                $('#easychat-console-lang-dropdown-select .current').html(default_select_lang_drop);

            } else {

                $("#" + this.id + "-select" + " ul li:first").addClass('easychat-lang-selected');
                var default_select_lang_drop = $('#' + this.id + "-select" + ' ul li:first').text();
                $('#' + this.id + "-select" + ' .current').html(default_select_lang_drop);

            }

        }

    });

    $('.easychat-dropdown-select-custom ul').before('<div class="dd-search"> <svg class="drop-language-search-icon" width="15" height="14" viewBox="0 0 15 14" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.1875 12.0689L9.88352 8.76489C10.6775 7.81172 11.0734 6.58914 10.9889 5.35148C10.9045 4.11382 10.3461 2.95638 9.42994 2.11993C8.51381 1.28349 7.31047 0.83244 6.07025 0.86062C4.83003 0.8888 3.64842 1.39404 2.77123 2.27123C1.89404 3.14842 1.3888 4.33003 1.36062 5.57025C1.33244 6.81047 1.78349 8.01381 2.61993 8.92994C3.45638 9.84607 4.61382 10.4045 5.85148 10.4889C7.08914 10.5734 8.31172 10.1775 9.26489 9.38352L12.5689 12.6875L13.1875 12.0689ZM2.25002 5.68752C2.25002 4.90876 2.48095 4.14748 2.91361 3.49996C3.34627 2.85244 3.96122 2.34776 4.6807 2.04974C5.40019 1.75172 6.19189 1.67375 6.95569 1.82568C7.71949 1.97761 8.42108 2.35262 8.97175 2.90329C9.52242 3.45396 9.89743 4.15555 10.0494 4.91935C10.2013 5.68315 10.1233 6.47485 9.8253 7.19433C9.52728 7.91382 9.0226 8.52877 8.37508 8.96143C7.72756 9.39409 6.96628 9.62502 6.18752 9.62502C5.14358 9.62386 4.14274 9.20865 3.40457 8.47047C2.66639 7.7323 2.25118 6.73145 2.25002 5.68752Z" fill="#909090"/></svg><input id="txtSearchValue" autocomplete="off" placeholder="Search Language" onkeyup="filter()" class="dd-searchbox" type="text"></div>');

    $('.easychat-dropdown-select-custom ul li:last').after('<div class="custom-drop-nodata-found-div">No result found</div> ');

}

// Event listeners

// Open/close
$(document).on('click', '.easychat-dropdown-select-custom', function (event) {

    if ($(event.target).hasClass('dd-searchbox')) {
        return;
    }
    $('.easychat-dropdown-select-custom').not($(this)).removeClass('open');
    $(this).toggleClass('open');
    $('#txtSearchValue').val("");
    $(".easychat-dropdown-select-custom ul li").show();
    $('.custom-drop-nodata-found-div').hide();
    if ($(this).hasClass('open')) {
        $(this).find('.easychat-console-language-option').attr('tabindex', 0);
        $(this).find('.easychat-lang-selected').focus();
    } else {
        $(this).find('.easychat-console-language-option').removeAttr('tabindex');
        $(this).focus();
    }
});

// Close when clicking outside
$(document).on('click', function (event) {

    if ($(event.target).closest('.easychat-dropdown-select-custom').length === 0) {
        $('.easychat-dropdown-select-custom').removeClass('open');
        $('.easychat-dropdown-select-custom .option').removeAttr('tabindex');
    }
    event.stopPropagation();
});

function filter() {

    var valThis = $('#txtSearchValue').val();
    $('.easychat-dropdown-select-custom ul > li').each(function () {
        var text = $(this).text();
        (text.toLowerCase().indexOf(valThis.toLowerCase()) > -1) ? $(this).show() : $(this).hide();

        if ($('.easychat-dropdown-select-custom ul').children(':visible').not('.custom-drop-nodata-found-div').length === 0) {
            $('.custom-drop-nodata-found-div').show();
        } else {
            $('.custom-drop-nodata-found-div').hide();
        }

    });
};
// Search

// Option click
$(document).on('click', '.easychat-dropdown-select-custom .easychat-console-language-option', function (event) {

    $(this).closest('.list').find('.easychat-lang-selected').removeClass('easychat-lang-selected');
    $(this).addClass('easychat-lang-selected');

    var text = $(this).data('display-text') || $(this).text();
    console.log($(this).data('value'))
    $(this).closest('.easychat-dropdown-select-custom').find('.current').text(text);
    $(this).closest('.easychat-dropdown-select-custom').prev('select').val($(this).data('value')).trigger('change');

    if (event.target.parentElement.parentElement.parentElement.id == "easychat-console-lang-dropdown-select") {
        var url_string = window.location.href
        var url = new URL(url_string);
        bot_id = url.searchParams.get("bot_id");
        changed_language = $(this).attr('data-value');
        $('#modal-language-change-loader').modal("open");
        setTimeout(function () {
            window.location = "/chat/revised-analytics/?bot_id=" + bot_id + "&selected_language=" + changed_language;
        },2000)
    }

});

// Keyboard events
$(document).on('keydown', '.easychat-dropdown-select-custom', function (event) {
    var focused_option = $($(this).find('.list .easychat-console-language-option:focus')[0] || $(this).find('.list .easychat-console-language-option.easychat-lang-selected')[0]);
    // Space or Enter
    //if (event.keyCode == 32 || event.keyCode == 13) {
    if (event.keyCode == 13) {
        if ($(this).hasClass('open')) {
            focused_option.trigger('click');
        } else {
            $(this).trigger('click');
        }
        return false;
        // Down
    } else if (event.keyCode == 40) {
        if (!$(this).hasClass('open')) {
            $(this).trigger('click');
        } else {
            focused_option.next().focus();
        }
        return false;
        // Up
    } else if (event.keyCode == 38) {
        if (!$(this).hasClass('open')) {
            $(this).trigger('click');
        } else {
            var focused_option = $($(this).find('.list .easychat-console-language-option:focus')[0] || $(this).find('.list .easychat-console-language-option.easychat-lang-selected')[0]);
            focused_option.prev().focus();
        }
        return false;
        // Esc
    } else if (event.keyCode == 27) {
        if ($(this).hasClass('open')) {
            $(this).trigger('click');
        }
        return false;
    }
});

$(document).ready(function () {
    create_custom_dropdowns();
});
