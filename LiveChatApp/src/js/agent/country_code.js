import { validate_phone_number, validate_number_input, validate_number_input_value, is_mobile } from "../utils";

const state = {
    country_code_component: null,
};

export function initialize_country_code_selector(phone_country_code, id){

    if(!phone_country_code) {
        phone_country_code = "in";
    }
    
    var telInput = $(`#${id}`);

    telInput.intlTelInput({
        initialCountry: phone_country_code,
        allowExtensions: true,
        formatOnDisplay: false,
        autoFormat: true,
        autoHideDialCode: true,
        autoPlaceholder: false,
        ipinfoToken: "yolo",
        nationalMode: false,
        numberType: "MOBILE",
        preferredCountries: [phone_country_code],
        preventInvalidNumbers: true,
        separateDialCode: true,
        utilsScript: "../../static/LiveChatApp/js/country_code_utils.js",
    });

    if (!is_mobile()) {
        if ($("#search_input_country").length == 0){ 
            $(".country-list").prepend("<input autocomplete='off' id='search_input_country' placeholder='Search..' class='search_phone_number_widget_class'  type='text' onkeydown='filter_function(event)' data-search autofocus/>");
            $(".country-list").append("<div class='country-no-result-found' id='country_no_result_found_livechat_modal'>No Result Found</div>");
            
            $("#search_input_country").focus();
            $("#search_input_country").click(function(event) {
                event.stopPropagation();
                $(".country-list").addClass("show");
            });
        }
    }

    $(".selected-flag").on("click", function() {
        if (is_mobile()) {
            $(".search_phone_number_widget_class").remove()
            $(".country-no-result-found").remove()
            $(".country").css("display", "");
            
            $(".country-list").prepend("<input autocomplete='off' id='search_input_country' placeholder='Search..' class='search_phone_number_widget_class'  type='text' onkeydown='filter_function(event)' data-search autofocus/>");
            $(".country-list").append("<div class='country-no-result-found' id='country_no_result_found_livechat_modal'>No Result Found</div>");
            
            $("#search_input_country").focus();
            $("#search_input_country").click(function(event) {
                event.stopPropagation();
                $(".country-list").addClass("show");
            });
        }
    })

    $(`#${id}`).on("countrychange", function() {
        $(`#${id}`).css({"border" : "1px solid #EBEBEB"});
        validate_customer_phone_number();
      });

    $(`#${id}`).keyup(function(event) {
        let character =  event.target.value.charAt(event.target.selectionStart - 1).charCodeAt();
        let value = String.fromCharCode(character);
        if (validate_number_input_value(value, event)) {
            $(`#${id}`).css({"border" : "1px solid #EBEBEB"});
        }  
        validate_customer_phone_number(id);
    })

    $(`#${id}`).keydown(function(event) {        
        validate_number_input(event);
    })

}

function validate_customer_phone_number(id) {
    let is_valid = $(`#${id}`).intlTelInput("isValidNumber");
    let validation_err = $(`#${id}`).intlTelInput("getValidationError");
    
    if (!is_valid) {
        $(`#${id}`).css({"border" : "1px solid #FF7C7C"});

    } else {
        if ($(`#${id}`).intlTelInput("getSelectedCountryData").dialCode == "91") {
            if (!validate_phone_number(id)) {
                $(`#${id}`).css({"border" : "1px solid #FF7C7C"});

            } else {
                $(`#${id}`).css({"border" : "1px solid #00C900"});
            }
        } else {
            $(`#${id}`).css({"border" : "1px solid #00C900"});
        }

    }
}

export function filter_function(event) {

    let input, filter, ul, a, i;
    input = document.getElementById("search_input_country");

    a = document.querySelectorAll(".country");
    event.stopPropagation();
    setTimeout(function() {
        filter = input.value.toUpperCase();
        var no_results_found = true
        for (i = 0; i < a.length; i++) {
            var txtValue = a[i].textContent || a[i].innerText;
            if (txtValue.toUpperCase().startsWith(filter)) {
                a[i].style.display = "";
                no_results_found = false
            } else {
                a[i].style.display = "none";
            }
        }
        if (no_results_found) {
            document.querySelector(".country-no-result-found").style.display = "block";
        } else {
            document.querySelector(".country-no-result-found").style.display = "none";
        }
    }, 100)
}

export function destroy_country_code_component(){
    $("#customer-phone-input").intlTelInput("destroy");
}