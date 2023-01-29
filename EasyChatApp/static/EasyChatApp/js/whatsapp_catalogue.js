const BOT_ID = get_url_vars()["id"];
const EMPTY_TABLE_SVG = `<svg width="170" height="130" viewBox="0 0 170 130" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M77.9062 0.866749C70.6925 2.80635 64.5414 7.89718 61.3403 14.5762C60.2727 16.8039 59.2342 19.727 59.0325 21.072L58.6659 23.5171H52.5994H46.5329L46.2314 25.8989C46.0661 27.2091 45.4127 38.8725 44.7794 51.8182C44.1461 64.7638 43.496 76.4143 43.3352 77.7077C42.9894 80.4779 45.1537 80.0166 24.0473 81.8184C16.1875 82.4892 7.61311 83.327 4.99317 83.6801C0.396067 84.2999 0.223458 84.3761 0.0525308 85.8635C-0.113913 87.3071 0.00993913 87.404 2.01399 87.3996C3.1903 87.3968 7.30488 87.0263 11.1577 86.5763C19.5337 85.5978 37.7932 84.0421 40.8963 84.0421H43.1065L42.7383 90.4869L42.3702 96.9317H84.5488H126.727L126.331 90.3384L125.935 83.7451L128.651 83.9104C135.621 84.3341 152.862 85.8371 159.829 86.629C165.908 87.32 167.731 87.362 168.375 86.8268C171.473 84.2556 165.588 83.1337 137.575 80.9553C131.397 80.4745 126.188 79.9006 125.999 79.6798C125.812 79.459 125.103 68.1823 124.425 54.6202C123.748 41.0582 123.045 28.5115 122.864 26.7395L122.536 23.5171H116.533H110.53L109.844 20.4511C106.625 6.0663 91.9754 -2.91718 77.9062 0.866749ZM88.6079 5.08445C92.6009 5.91947 97.616 8.64085 99.9743 11.2513C102.273 13.795 104.524 18.0671 105.235 21.2317L105.749 23.5171H84.5023H63.2552L63.6312 21.976C65.3965 14.746 69 10.0481 75.1842 6.91477C79.7186 4.6165 83.7474 4.06729 88.6079 5.08445ZM58.7932 31.957V35.3537L60.8947 35.1794L62.9963 35.0057L63.1644 31.7833L63.3325 28.5609H84.5723H105.812L105.98 31.7833L106.148 35.0057H108.11H110.071L110.239 31.7833L110.408 28.5609H114.262H118.117L118.427 31.503C118.762 34.689 121.572 87.6344 121.564 90.627L121.56 92.4484H84.5723H47.5848L47.5686 90.3468C47.5428 86.9479 50.443 31.2027 50.7176 29.8218C50.949 28.6584 51.2718 28.5609 54.8809 28.5609H58.7932V31.957ZM67.8719 62.8584C67.502 63.2282 67.1994 64.0605 67.1994 64.7077C67.1994 65.355 67.502 66.1872 67.8719 66.5571C68.2418 66.927 69.074 67.2296 69.7213 67.2296C70.3686 67.2296 71.2008 66.927 71.5707 66.5571C71.9405 66.1872 72.2432 65.355 72.2432 64.7077C72.2432 64.0605 71.9405 63.2282 71.5707 62.8584C71.2008 62.4885 70.3686 62.1859 69.7213 62.1859C69.074 62.1859 68.2418 62.4885 67.8719 62.8584ZM96.9671 63.4261C96.2873 65.2631 96.8533 66.6356 98.4561 67.038C100.22 67.4807 101.607 66.6636 101.848 65.0401C102.102 63.3258 100.987 62.1859 99.0563 62.1859C97.8856 62.1859 97.2966 62.5356 96.9671 63.4261ZM85.9734 72.5043C82.5184 74.0398 80.5071 77.8775 83.1573 77.8775C85.3031 77.8775 95.5374 76.1033 95.9875 75.6532C96.8488 74.7919 95.8799 73.3785 93.845 72.5283C91.4402 71.5235 88.2022 71.5134 85.9734 72.5043Z" fill="#CBCACA"/>
                            <path d="M36.6194 125.932V116.129H38.2327L42.8811 123.382H42.9631V116.129H44.4329V125.932H42.8059L38.1917 118.679H38.1028V125.932H36.6194ZM46.3264 122.274C46.3264 121.55 46.4905 120.894 46.8186 120.306C47.1513 119.718 47.6139 119.258 48.2063 118.925C48.7987 118.592 49.4641 118.426 50.2024 118.426C50.9407 118.426 51.6038 118.594 52.1917 118.932C52.7841 119.269 53.2421 119.731 53.5657 120.319C53.8938 120.903 54.0579 121.554 54.0579 122.274C54.0579 122.995 53.8915 123.648 53.5588 124.236C53.2307 124.82 52.7704 125.28 52.178 125.617C51.5855 125.95 50.9224 126.116 50.1887 126.116C49.0676 126.116 48.1425 125.754 47.4133 125.029C46.6887 124.3 46.3264 123.382 46.3264 122.274ZM47.8235 122.274C47.8235 123.004 48.0445 123.605 48.4866 124.079C48.9332 124.549 49.5006 124.783 50.1887 124.783C50.8814 124.783 51.4488 124.546 51.8909 124.072C52.3375 123.598 52.5608 122.999 52.5608 122.274C52.5608 121.545 52.3375 120.946 51.8909 120.477C51.4488 120.007 50.8814 119.773 50.1887 119.773C49.496 119.773 48.9286 120.009 48.4866 120.483C48.0445 120.953 47.8235 121.55 47.8235 122.274ZM59.4172 116.525C59.4172 116.257 59.5084 116.036 59.6907 115.862C59.873 115.689 60.1031 115.603 60.3811 115.603C60.6682 115.603 60.9029 115.689 61.0852 115.862C61.2721 116.036 61.3655 116.257 61.3655 116.525C61.3655 116.803 61.2721 117.029 61.0852 117.202C60.9029 117.375 60.6682 117.462 60.3811 117.462C60.0986 117.462 59.8661 117.375 59.6838 117.202C59.5061 117.029 59.4172 116.803 59.4172 116.525ZM59.6428 125.932V118.61H61.1125V125.932H59.6428ZM62.6233 119.814V118.624H63.5872C63.7148 118.624 63.8196 118.581 63.9016 118.494C63.9836 118.408 64.0247 118.291 64.0247 118.146V116.539H65.4055V118.61H67.5383V119.814H65.4055V123.566C65.4055 124.314 65.761 124.688 66.4719 124.688H67.4631V125.932H66.2463C65.5172 125.932 64.9498 125.733 64.5442 125.337C64.1386 124.936 63.9358 124.359 63.9358 123.607V119.814H62.6233ZM68.762 122.295C68.762 121.534 68.9215 120.859 69.2405 120.272C69.5595 119.679 69.9947 119.223 70.5461 118.904C71.1021 118.585 71.7265 118.426 72.4192 118.426C72.9752 118.426 73.481 118.524 73.9368 118.72C74.3925 118.916 74.7685 119.185 75.0647 119.526C75.3655 119.868 75.5956 120.267 75.7551 120.723C75.9192 121.178 76.0012 121.668 76.0012 122.192V122.739H70.2317C70.259 123.382 70.4755 123.899 70.8811 124.291C71.2867 124.683 71.8222 124.879 72.4875 124.879C72.9524 124.879 73.3671 124.774 73.7317 124.565C74.1008 124.355 74.3583 124.072 74.5042 123.717H75.9329C75.7415 124.437 75.3336 125.018 74.7092 125.46C74.0894 125.898 73.3352 126.116 72.4465 126.116C71.3573 126.116 70.4709 125.759 69.7874 125.043C69.1038 124.323 68.762 123.407 68.762 122.295ZM70.259 121.605H74.5452C74.4996 121.003 74.2786 120.529 73.8821 120.183C73.4856 119.832 72.998 119.656 72.4192 119.656C71.8541 119.656 71.3665 119.839 70.9563 120.203C70.5461 120.568 70.3137 121.035 70.259 121.605ZM77.7854 125.932V118.61H79.2141V119.574H79.3098C79.483 119.237 79.745 118.961 80.0959 118.747C80.4469 118.533 80.8707 118.426 81.3674 118.426C81.8824 118.426 82.3313 118.535 82.7141 118.754C83.0969 118.973 83.3954 119.273 83.6096 119.656H83.7053C84.1702 118.836 84.9221 118.426 85.9612 118.426C86.7633 118.426 87.4081 118.679 87.8958 119.185C88.3879 119.686 88.634 120.335 88.634 121.133V125.932H87.1643V121.632C87.1643 121.044 87.0299 120.593 86.761 120.278C86.4921 119.959 86.1139 119.8 85.6262 119.8C85.1477 119.8 84.7489 119.968 84.4299 120.306C84.1155 120.638 83.9583 121.09 83.9583 121.659V125.932H82.4885V121.468C82.4885 120.962 82.3427 120.559 82.051 120.258C81.7594 119.953 81.3788 119.8 80.9094 119.8C80.44 119.8 80.0458 119.971 79.7268 120.313C79.4124 120.65 79.2551 121.085 79.2551 121.618V125.932H77.7854ZM93.8157 119.814V118.61H95.1487V117.879C95.1487 117.127 95.3879 116.532 95.8665 116.095C96.345 115.653 96.9739 115.432 97.7532 115.432H98.5803V116.676H97.8352C97.4159 116.676 97.1038 116.792 96.8987 117.024C96.6936 117.252 96.5911 117.553 96.5911 117.927V118.61H98.635V119.814H96.6047V125.932H95.135V119.814H93.8157ZM99.469 122.274C99.469 121.55 99.6331 120.894 99.9612 120.306C100.294 119.718 100.756 119.258 101.349 118.925C101.941 118.592 102.607 118.426 103.345 118.426C104.083 118.426 104.746 118.594 105.334 118.932C105.927 119.269 106.385 119.731 106.708 120.319C107.036 120.903 107.2 121.554 107.2 122.274C107.2 122.995 107.034 123.648 106.701 124.236C106.373 124.82 105.913 125.28 105.321 125.617C104.728 125.95 104.065 126.116 103.331 126.116C102.21 126.116 101.285 125.754 100.556 125.029C99.8313 124.3 99.469 123.382 99.469 122.274ZM100.966 122.274C100.966 123.004 101.187 123.605 101.629 124.079C102.076 124.549 102.643 124.783 103.331 124.783C104.024 124.783 104.591 124.546 105.033 124.072C105.48 123.598 105.703 122.999 105.703 122.274C105.703 121.545 105.48 120.946 105.033 120.477C104.591 120.007 104.024 119.773 103.331 119.773C102.639 119.773 102.071 120.009 101.629 120.483C101.187 120.953 100.966 121.55 100.966 122.274ZM108.862 123.314V118.61H110.331V123.047C110.331 123.557 110.486 123.97 110.796 124.284C111.106 124.599 111.496 124.756 111.965 124.756C112.48 124.756 112.904 124.583 113.237 124.236C113.574 123.885 113.742 123.443 113.742 122.91V118.61H115.212V125.932H113.783V124.954H113.688C113.528 125.282 113.259 125.558 112.881 125.781C112.507 126.005 112.063 126.116 111.548 126.116C110.732 126.116 110.081 125.852 109.593 125.323C109.105 124.795 108.862 124.125 108.862 123.314ZM117.365 125.932V118.61H118.794V119.588H118.89C119.049 119.26 119.318 118.984 119.697 118.761C120.075 118.537 120.521 118.426 121.036 118.426C121.852 118.426 122.504 118.69 122.991 119.219C123.479 119.747 123.723 120.417 123.723 121.229V125.932H122.253V121.509C122.253 121.003 122.096 120.593 121.781 120.278C121.472 119.959 121.082 119.8 120.613 119.8C120.102 119.8 119.678 119.978 119.341 120.333C119.004 120.684 118.835 121.126 118.835 121.659V125.932H117.365ZM126.307 125.057C125.651 124.35 125.323 123.43 125.323 122.295C125.323 121.16 125.648 120.233 126.3 119.513C126.952 118.788 127.788 118.426 128.809 118.426C129.137 118.426 129.445 118.471 129.732 118.563C130.019 118.654 130.258 118.772 130.449 118.918C130.645 119.064 130.8 119.198 130.914 119.321C131.028 119.44 131.124 119.558 131.201 119.677H131.304V115.432H132.774V125.932H131.331V124.893H131.242C130.664 125.708 129.875 126.116 128.877 126.116C127.824 126.116 126.968 125.763 126.307 125.057ZM126.82 122.274C126.82 123.031 127.027 123.639 127.442 124.1C127.861 124.555 128.41 124.783 129.089 124.783C129.773 124.783 130.32 124.544 130.73 124.065C131.14 123.587 131.345 122.99 131.345 122.274C131.345 121.504 131.131 120.896 130.702 120.449C130.279 119.998 129.736 119.773 129.075 119.773C128.41 119.773 127.868 120.007 127.448 120.477C127.029 120.941 126.82 121.541 126.82 122.274Z" fill="#7B7A7B"/>
                        </svg>`
const country_options = ["AD","AE","AF","AG","AI","AL","AM","AN","AO","AQ","AR","AS","AT","AU","AW","AX","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BL","BM","BN","BO","BQ","BR","BS","BT","BV","BW","BY","BZ","CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CU","CV","CW","CX","CY","CZ","DE","DJ","DK","DM","DO","DZ","EC","EE","EG",
"EH","ER","ES","ET","FI","FJ","FK","FM","FO","FR","GA","GB","GD","GE","GF","GG","GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GW","GY","HK","HM","HN","HR","HT","HU","ID","IE","IL","IM","IN","IO","IQ","IR","IS","IT","JE","JM","JO","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ","LA","LB","LC","LI","LK","LR",
"LS","LT","LU","LV","LY","MA","MC","MD","ME","MF","MG","MH","MK","ML","MM","MN","MO","MP","MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ","OM","PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY","QA","RE","RO","RS","RU","RW","SA","SB","SC","SD","SE",
"SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","SS","ST","SV","SX","SY","SZ","TC","TD","TF","TG","TH","TJ","TK","TL","TM","TN","TO","TR","TT","TV","TW","TZ","UA","UG","UM","US","UY","UZ","VA","VC","VE","VG","VI","VN","VU","WF","WS","XK","YE","YT","ZA","ZM","ZW"]

$(document).ready(function () {
    $("nav[role='navigation']").prepend(`<div id="sync_preview_toast_container" style="">
                            <svg style="margin-top:-2px;" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 3C16.9707 3 21 7.0302 21 12C21 16.9698 16.9707 21 12 21C7.0293 21 3 16.9698 3 12C3 7.0302 7.0293 3 12 3ZM12.0016 14.7034C11.5052 14.7034 11.1028 15.1058 11.1028 15.6021C11.1028 16.0985 11.5052 16.5009 12.0016 16.5009C12.498 16.5009 12.9004 16.0985 12.9004 15.6021C12.9004 15.1058 12.498 14.7034 12.0016 14.7034ZM11.9997 7.5C11.5381 7.50017 11.1578 7.84774 11.106 8.29536L11.1 8.40032L11.1016 12.9011L11.1077 13.0061C11.1599 13.4537 11.5404 13.801 12.0019 13.8008C12.4635 13.8006 12.8438 13.4531 12.8956 13.0054L12.9016 12.9005L12.9 8.39968L12.8939 8.29472C12.8418 7.84713 12.4612 7.49983 11.9997 7.5Z" fill="#F5C828"></path>
                                </svg>
                            <span id="easychat-navbar-toast-message">
                                Please ensure to click on the "Sync Preview" button if any changes in product/items are made from the Facebook Commerce Manager side.
                            </span>
                        </div>`)
    $(`<div class="col s12 easychat-product-review-toast-div" id="easychat-product-review-toast-div">
                            <div class="product-review-message">
                                All products will go through a standard review procedure. It may take up to a day to complete the review and get approved. If there is an issue it won't be approved because it goes against Facebook's Commerce Policies. You can view the product’s status in Facebook Commerce Manager. 
                            </div>
                            <a href="javascript:void(0)" onclick="hide_review_product_toast()">
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path fill-rule="evenodd" clip-rule="evenodd" d="M2.70356 2.5304C2.96828 2.27583 3.38924 2.28406 3.64381 2.54878L11.3176 10.5286C11.5722 10.7933 11.5639 11.2142 11.2992 11.4688C11.0345 11.7234 10.6135 11.7152 10.359 11.4504L2.68518 3.47064C2.43061 3.20593 2.43884 2.78496 2.70356 2.5304Z" fill="#FAFAFA"/>
                                    <path fill-rule="evenodd" clip-rule="evenodd" d="M11.2984 2.53085C11.5633 2.78562 11.5719 3.20658 11.3175 3.47108L3.64376 11.4509C3.3894 11.7154 2.96843 11.7233 2.7035 11.4685C2.43857 11.2137 2.43001 10.7928 2.68437 10.5283L10.3582 2.54848C10.6125 2.28397 11.0335 2.27608 11.2984 2.53085Z" fill="#FAFAFA"/>
                                </svg>            
                            </a>
                        </div>`).insertBefore('.navbar-fixed')
    $('#sync_preview_toast_container').delay(10000).fadeOut(3000);
    const CURRENCY_NAME_MAP = { "DZD": "Algerian Dinar", "ARS": "Argentine Peso", "AUD": "Australian Dollar", "BDT": "Bangladeshi Taka", "BOB": "Bolivian Boliviano", "BRL": "Brazilian Real", "GBP": "British Pound", "CAD": "Canadian Dollar", "CLP": "Chilean Peso", "CNY": "Chinese Yuan", "COP": "Colombian Peso", "CRC": "Costa Rican Colon", "CZK": "Czech Koruna", "DKK": "Danish Krone", "EGP": "Egyptian Pounds", "EUR": "Euro", "GTQ": "Guatemalan Quetza", "HNL": "Honduran Lempira", "HKD": "Hong Kong Dollar", "HUF": "Hungarian Forint", "ISK": "Iceland Krona", "INR": "Indian Rupee", "IDR": "Indonesian Rupiah", "ILS": "Israeli New Shekel", "JPY": "Japanese Yen", "KES": "Kenyan Shilling", "KRW": "Korean Won", "MOP": "Macau Patacas", "MYR": "Malaysian Ringgit", "MXN": "Mexican Peso", "NZD": "New Zealand Dollar", "NIO": "Nicaraguan Cordoba", "NGN": "Nigerian Naira", "NOK": "Norwegian Krone", "PKR": "Pakistani Rupee", "PYG": "Paraguayan Guarani", "PEN": "Peruvian Nuevo Sol", "PHP": "Philippine Peso", "PLN": "Polish Zloty", "QAR": "Qatari Rials", "RON": "Romanian Leu", "RUB": "Russian Ruble", "SAR": "Saudi Arabian Riyal", "SGD": "Singapore Dollar", "ZAR": "South African Rand", "SEK": "Swedish Krona", "CHF": "Swiss Franc", "TWD": "Taiwan Dollar", "THB": "Thai Baht", "TRY": "Turkish Lira", "AED": "Uae Dirham", "USD": "United States Dollar", "UYU": "Uruguay Peso", "VEF": "Venezuelan Bolivar", "VND": "Vietnamese Dong" }
    const accepted_csv_types = ["text/csv", "text/x-csv", "application/x-csv", "application/csv", "text/x-comma-separated-values", "text/comma-separated-values", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"];
    track_sync_products_progress();
    var sync_products_timer = setInterval(track_sync_products_progress, 5000);
    track_upload_items_progress();
    var upload_items_timer = setInterval(track_upload_items_progress, 3000);
    var upload_items_in_progress = false;
    let is_first_time_upload = true;
    function initialize_catalogue_items_table() {
        let catalogue_items_table_container = document.querySelector("#message-history-info-table_wrapper");
        let catalogue_item_searchbar = document.querySelector("#item-search-bar");
        let pagination_container = document.getElementById("message_history_table_pagination_div");

        window.ACTIVE_CATALOGUE_TABLE = new CatalogueItemsTable(
            catalogue_items_table_container, catalogue_item_searchbar, pagination_container);
    }
    initialize_catalogue_items_table();
    add_event_listeners_for_catalogue_items("static");
    add_event_listeners_for_catalogue_items("edit_item");
    $("#edit_item_origin_country_ul").append(get_origin_country_dropdown_options())
    $("#currency_dropdown_ul_edit_item").append(get_currency_dropdown_options());
    $("#sync_products_btn").click(() => {
        sync_products_from_facebook();
    })
    function sync_products_from_facebook() {
        $("#sync_products_svg").css("animation", "rotate 2s infinite");
        $("#sync_products_btn").css("pointer-events", "none");
        let xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/chat/channels/whatsapp/catalogue-products/?bot_id=" + BOT_ID, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    sync_products_timer = setInterval(track_sync_products_progress, 5000);
                } else {
                    if ("message" in response) {
                        M.toast({
                            "html": response["message"]
                        }, 5000);
                    }
                }
            } else if (this.readyState == 4 && this.status != 200) {
                $("#sync_products_svg").css("animation", "none");
                $("#sync_products_btn").css("pointer-events", "auto");
                M.toast({
                    "html": "Error in Syncing products with Commerce Manager, please try again later."
                }, 2000);
            }
        }
        xhttp.send(params);
    }
    $("#save_catalogue_items").click(() => {
        if ($("#add_item_modal #accordion-div .accrodion-wrapper").length > 6) {
            showToast("Maximum 5 items can be created at once!", 3000)
            return;
        }
        let [catalogue_items_data, error_message] = get_catalogue_items_data("add_item_modal");
        if (error_message && error_message != "") {
            // showToast(error_message, 2000);
            return;
        }
        $("#save_catalogue_items").css({
            "opacity": "0.5",
            "pointer-events": "none"
        })
        $(".save-note").css("display", "flex")
        $("#save_catalogue_items").html(`Saving <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="animation: rotate 2s infinite">
        <path d="M20.946 12.9846C21.4949 13.0451 21.896 13.5408 21.7811 14.081C21.3316 16.1942 20.2069 18.1149 18.5634 19.5446C16.6673 21.1941 14.2196 22.0692 11.7075 21.9957C9.19542 21.9222 6.80309 20.9055 5.00668 19.148C3.21026 17.3904 2.14149 15.0209 2.01306 12.511C1.88464 10.0011 2.70599 7.53486 4.31364 5.60314C5.92129 3.67141 8.19735 2.41585 10.6888 2.08633C13.1803 1.75681 15.7045 2.3775 17.7591 3.82487C19.5399 5.07942 20.8548 6.87531 21.5176 8.93157C21.6871 9.45722 21.3387 9.99129 20.7988 10.1074V10.1074C20.2588 10.2236 19.7329 9.87693 19.5504 9.35569C19.002 7.78996 17.977 6.42479 16.6073 5.4599C14.9636 4.302 12.9443 3.80545 10.9511 4.06906C8.95788 4.33268 7.13703 5.33713 5.85091 6.88251C4.56479 8.42789 3.90771 10.4009 4.01045 12.4088C4.11319 14.4167 4.96821 16.3123 6.40534 17.7184C7.84247 19.1244 9.75633 19.9378 11.766 19.9966C13.7757 20.0554 15.7339 19.3553 17.2507 18.0357C18.5148 16.9361 19.3952 15.4734 19.7808 13.8599C19.9092 13.3227 20.397 12.9242 20.946 12.9846V12.9846Z" fill="white"/>
        </svg>`)
        $("#fb_error_message_toast").hide();
        let json_string = JSON.stringify({
            bot_id: BOT_ID,
            catalogue_items_data: catalogue_items_data
        })
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        let params = 'json_string=' + json_string
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/chat/channels/whatsapp/catalogue-products/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                $("#sync_products_svg").css("animation", "none")
                $(".save-note").hide();
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    sync_products_from_facebook();
                    M.toast({
                        "html": "Items created successfully!"
                    }, 2000);
                    $("#add_item_modal").modal("close");
                    show_review_product_toast();
                    reset_add_item_modal();
                    $("#save_catalogue_items").css({
                        "opacity": "1",
                        "pointer-events": "auto"
                    })
                    $("#save_catalogue_items").html(`Save`)
                } else {
                    if ("message" in response) {
                        M.toast({
                            "html": response["message"]
                        }, 5000);
                    }
                    if ("successfully_added_items" in response) {
                        let successfully_added_items = response.successfully_added_items
                        for (let index = 0; index < successfully_added_items.length; index++) {
                            $("#accordion-header-wrapper-" + successfully_added_items[index]).remove();
                        }
                    }
                    $("#save_catalogue_items").css({
                        "opacity": "1",
                        "pointer-events": "auto"
                    })
                    $("#save_catalogue_items").html(`Save`)
                    update_item_titles();

                    if ("api_error_messages" in response) {
                        $("#fb_error_toast_wrapper").html('');
                        let error_html = `<ul>`
                        api_error_messages = JSON.parse(response.api_error_messages)
                        for (section_id in api_error_messages) {
                            let item_title = $("#item_heading_" + section_id).text().trim();
                            $("#accordion-header-wrapper-" + section_id + " .error-in-item-div").show();
                            error_html += `<li><span>${item_title}: </span>${api_error_messages[section_id]}</li>`
                        }
                        error_html += `</ul>`
                        $("#fb_error_toast_wrapper").append(error_html)
                        $("#fb_error_message_toast").css("display", "flex");
                    }
                }
            } else if (this.readyState == 4 && this.status != 200) {
                $("#sync_products_svg").css("animation", "none")
                $("#save_catalogue_items").css({
                    "opacity": "1",
                    "pointer-events": "auto"
                })
                $("#save_catalogue_items").html(`Save`)
                M.toast({
                    "html": "Error in creating product item(s), please try again later."
                }, 2000);
                $(".save-note").hide();
            }
        }
        xhttp.send(params);
    })

    function reset_add_item_modal() {
        $("#add_item_modal .accrodion-wrapper").remove();
        $("#create-item-button").click();
    }

    $(document).on("click", "#create-item-button", function (e) {
        if ($("#add_item_modal #accordion-div .accrodion-wrapper").length >= 5) {
            showToast("Maximum 5 items can be created at once!", 3000)
            return;
        }
        let item_wrapper = $("#add_item_modal #accordion-div");
        let unique_element_id = generate_random_string(4);
        $(create_accordion_header_html(unique_element_id)).appendTo(item_wrapper);
        add_event_listeners_for_catalogue_items(unique_element_id);
    })

    function create_accordion_header_html(unique_element_id) {
        let items_count = $(".accrodion-wrapper .accordion__header .item-name.non-variant").length + 1;
        let accordion_header = `
        <div class="accrodion-wrapper" id="accordion-header-wrapper-${unique_element_id}">
        <div class="accordion__header">
        <div class="accordion-header-body">
            <div class="accordion-header-body-left">
                <div class="checkbox">
                    <label>
                        <input class="new-item-selection-cb" type="checkbox" section-id="${unique_element_id}" id="sales_price">
                        <span></span>
                    </label>
                </div>
                <div class="item-name non-variant" id="item_heading_${unique_element_id}">
                    Item ${items_count}
                </div>
            </div>
            <div class="accordion-header-body-right">
             <div class="error-in-item-div" style="display: none;margin-right: 11px;">
                <svg style="position: relative;top: 3px;" width="25" height="25" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11.2005 4.74392C12.1355 4.24607 13.3028 4.53535 13.8764 5.38383L13.9508 5.50297L20.9283 17.6125C21.0945 17.901 21.1816 18.2253 21.1816 18.555C21.1816 19.5844 20.3497 20.4271 19.2968 20.4955L19.1583 20.5H5.20538C4.86247 20.5 4.5252 20.4162 4.22521 20.2565C3.29011 19.7588 2.92587 18.6542 3.36971 17.7366L3.43527 17.6127L10.4107 5.50317C10.5947 5.18387 10.8683 4.92076 11.2005 4.74392ZM19.7483 18.2408L12.7709 6.13125C12.5904 5.81802 12.1799 5.70474 11.8541 5.87823C11.771 5.92244 11.699 5.98283 11.6422 6.05516L11.5908 6.13132L4.61534 18.2409C4.4349 18.5541 4.55279 18.9487 4.87866 19.1222C4.95365 19.1621 5.03564 19.1878 5.12017 19.1981L5.20538 19.2033H19.1583C19.5308 19.2033 19.8327 18.913 19.8327 18.555C19.8327 18.4725 19.8164 18.3911 19.7848 18.315L19.7483 18.2408L12.7709 6.13125L19.7483 18.2408ZM12.1816 16.1717C12.6776 16.1717 13.0797 16.5583 13.0797 17.0351C13.0797 17.5118 12.6776 17.8984 12.1816 17.8984C11.6857 17.8984 11.2836 17.5118 11.2836 17.0351C11.2836 16.5583 11.6857 16.1717 12.1816 16.1717ZM12.1779 9.68637C12.5193 9.68611 12.8017 9.9298 12.8466 10.2462L12.8529 10.3342L12.8561 14.2256C12.8564 14.5837 12.5547 14.8742 12.1822 14.8745C11.8407 14.8748 11.5583 14.6311 11.5134 14.3146L11.5072 14.2267L11.5039 10.3352C11.5037 9.97716 11.8054 9.68665 12.1779 9.68637Z" fill="#E53935"/>
                    </svg>
               </div>
          
                <div class="toggle-accordion-div">
                    <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6.70711 7.1679C6.31658 7.55842 5.68342 7.55842 5.29289 7.1679L0.7 2.57501C0.313401 2.18841 0.313401 1.56161 0.7 1.17501V1.17501C1.0866 0.788407 1.7134 0.788407 2.1 1.17501L5.29289 4.3679C5.68342 4.75842 6.31658 4.75842 6.70711 4.3679L9.9 1.17501C10.2866 0.788407 10.9134 0.788407 11.3 1.17501V1.17501C11.6866 1.56161 11.6866 2.18841 11.3 2.57501L6.70711 7.1679Z" fill="#1C1B1F"/>
                    </svg>
                
                </div>
            </div>
            
        </div>
      </div>
      ${create_accordion_body_html(unique_element_id)}
      </div>`

        return accordion_header
    }

    function create_variant_header_html() {
        let unique_element_id = generate_random_string(4)
        let variant_header = `
        <div class="accordion__header variant-header" id="accordion-header-${unique_element_id}">
        <div class="accordion-header-body">
            <div class="accordion-header-body-left">
                <div class="checkbox">
                    <label>
                        <input type="checkbox" id="sales_price">
                        <span></span>
                    </label>
                </div>
                <div class="item-name">
                    Variant 1
                </div>
            </div>
            <div class="accordion-header-body-right">
                <div class="toggle-accordion-div">
                    <svg width="12" height="8" viewBox="0 0 12 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6.70711 7.1679C6.31658 7.55842 5.68342 7.55842 5.29289 7.1679L0.7 2.57501C0.313401 2.18841 0.313401 1.56161 0.7 1.17501V1.17501C1.0866 0.788407 1.7134 0.788407 2.1 1.17501L5.29289 4.3679C5.68342 4.75842 6.31658 4.75842 6.70711 4.3679L9.9 1.17501C10.2866 0.788407 10.9134 0.788407 11.3 1.17501V1.17501C11.6866 1.56161 11.6866 2.18841 11.3 2.57501L6.70711 7.1679Z" fill="#1C1B1F"/>
                    </svg>
                </div>
            </div>
            
        </div>
      </div>
      ${create_accordion_body_html(unique_element_id)}`
        return variant_header;
    }

    function create_accordion_body_html(unique_element_id) {
        let accordion_body = `<div class="accordion__body">
      <div class="modal-overflow-content-div" style="padding: 6px 0px 6px 0px !important; width: 100%"
          id="variant_container_data_wrapper_id">
          <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%">
              <h3 class="variant-heading-text">Title <span style="color:#E10E00">*</span></h3>
              <input class="variant-input" id="item_title_${unique_element_id}" type="text" id="" placeholder="Enter a short and clear title" maxlength="150"/>
              <span class="variant-input-counter"><span id="title_count_${unique_element_id}">0</span>/150</span>
          </div>
          <div class="col s12  variant-wrapper-div grow-wrap" style="padding: 0px; width: 100%">
              <h3 class="variant-heading-text">Description <span style="color:#E10E00">*</span> </h3>
    
              <textarea class="description-textarea form-control" type="text" name="text" rows="2"
              id="item_description_${unique_element_id}"
                  placeholder="Describe the features and benefits" maxlength="9999"></textarea>
    
              <span class="variant-input-counter"><span id="description_count_${unique_element_id}">0</span>/9999</span>
          </div>
          <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%">
              <h3 class="variant-heading-text">Website Link <span style="color:#E10E00">*</span></h3>
              <input class="variant-input url-input-box" type="text" id="item_website_${unique_element_id}" placeholder="https://www.example.com/item"
                  style="color: #0254d7" />
          </div>
          <!-- sprint 6.4.2 -->
          <div class="col s12  variant-wrapper-div upload-image-wrapper"
              style="padding: 0px; width: 100%;">
              <h3 class="variant-heading-text">Images</h3>
              <button class="upload-img-btn upload-image-on-server modal-trigger" id="upload_image_${unique_element_id}" href="#modal-upload-product-image">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path fill-rule="evenodd" clip-rule="evenodd"
                          d="M1 4C0.45 4 0 4.45 0 5V18C0 19.1 0.9 20 2 20H15C15.55 20 16 19.55 16 19C16 18.45 15.55 18 15 18H3C2.45 18 2 17.55 2 17V5C2 4.45 1.55 4 1 4ZM18 0H6C4.9 0 4 0.9 4 2V14C4 15.1 4.9 16 6 16H18C19.1 16 20 15.1 20 14V2C20 0.9 19.1 0 18 0ZM16 9H13V12C13 12.55 12.55 13 12 13C11.45 13 11 12.55 11 12V9H8C7.45 9 7 8.55 7 8C7 7.45 7.45 7 8 7H11V4C11 3.45 11.45 3 12 3C12.55 3 13 3.45 13 4V7H16C16.55 7 17 7.45 17 8C17 8.55 16.55 9 16 9Z"
                          fill="#0254D7"></path>
                  </svg>
                  Upload Images
              </button>
          </div>
          <!-- end sprint 6.4.2 -->
          <div class="col s12  variant-wrapper-div multiple-img-link-div" style="padding: 0px; width: 100%">
              <div class="add-more-img-heading-div">
                  <h3 class="variant-heading-text">Image Link <span style="color:#E10E00">*</span></h3>
                  <h3 class="variant-heading-text add-more-image-link" id="add_more_image_btn_${unique_element_id}" onclick="add_more_image_link(this, '${unique_element_id}')">
                      + Add more
                  </h3>
              </div>
              <div class="multiple-img-link-wrapper-div">
              <div class="img-variant-input additional-image-url additional-close-img-wrapper" type="text" placeholder="https://www.example.com/item"
              style="color: #0254d7" />
              <div class="drag-drop-img-link-wrapper">
              <div class="drag-drop-img-link">
              <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12.7708 14.4583C13.4266 14.4583 13.9583 14.99 13.9583 15.6458C13.9583 16.3017 13.4266 16.8333 12.7708 16.8333C12.115 16.8333 11.5833 16.3017 11.5833 15.6458C11.5833 14.99 12.115 14.4583 12.7708 14.4583ZM7.22913 14.4583C7.88496 14.4583 8.41663 14.99 8.41663 15.6458C8.41663 16.3017 7.88496 16.8333 7.22913 16.8333C6.57329 16.8333 6.04163 16.3017 6.04163 15.6458C6.04163 14.99 6.57329 14.4583 7.22913 14.4583ZM12.7708 8.91667C13.4266 8.91667 13.9583 9.44833 13.9583 10.1042C13.9583 10.76 13.4266 11.2917 12.7708 11.2917C12.115 11.2917 11.5833 10.76 11.5833 10.1042C11.5833 9.44833 12.115 8.91667 12.7708 8.91667ZM7.22913 8.91667C7.88496 8.91667 8.41663 9.44833 8.41663 10.1042C8.41663 10.76 7.88496 11.2917 7.22913 11.2917C6.57329 11.2917 6.04163 10.76 6.04163 10.1042C6.04163 9.44833 6.57329 8.91667 7.22913 8.91667ZM12.7708 3.375C13.4266 3.375 13.9583 3.90666 13.9583 4.5625C13.9583 5.21834 13.4266 5.75 12.7708 5.75C12.115 5.75 11.5833 5.21834 11.5833 4.5625C11.5833 3.90666 12.115 3.375 12.7708 3.375ZM7.22913 3.375C7.88496 3.375 8.41663 3.90666 8.41663 4.5625C8.41663 5.21834 7.88496 5.75 7.22913 5.75C6.57329 5.75 6.04163 5.21834 6.04163 4.5625C6.04163 3.90666 6.57329 3.375 7.22913 3.375Z" fill="#212121"/>
                </svg>
          
              </div>
              <input type="text" class="additional-image-url-input image-upload-url url-input-box" id="item_image_link_${unique_element_id}" placeholder="https://www.example.com/item" style="color: #0254d7">
              <a href="javascript:void(0)" onclick=open_preview_url(this) class="drag-drop-link-div">
              <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <mask id="path-1-inside-1_620_11914-${unique_element_id}" fill="white">
              <path d="M6.23973 4.56251H9.01008C9.338 4.56251 9.60383 4.82834 9.60383 5.15626C9.60383 5.45685 9.38046 5.70527 9.09065 5.74459L9.01008 5.75001H6.23945C5.30612 5.74957 4.54034 6.46757 4.46463 7.3816L4.45863 7.5074L4.46088 14.2608C4.46112 15.2036 5.19375 15.9751 6.12064 16.0375L6.24259 16.0416L12.9702 16.0324C13.9121 16.0311 14.6824 15.299 14.7449 14.373L14.749 14.2511V11.4753C14.749 11.1474 15.0149 10.8815 15.3428 10.8815C15.6434 10.8815 15.8918 11.1049 15.9311 11.3947L15.9365 11.4753V14.2511C15.9365 15.8363 14.6941 17.1316 13.1294 17.2155L12.9719 17.2199L6.2462 17.2291L6.08524 17.225C4.57113 17.1462 3.35716 15.9329 3.27753 14.4188L3.27338 14.2611L3.27161 7.53327L3.2751 7.37295C3.35434 5.85872 4.56819 4.6451 6.08209 4.56655L6.23973 4.56251H9.01008H6.23973ZM11.384 3.37604L16.5723 3.37644L16.6512 3.38734L16.731 3.40966L16.776 3.42874C16.8181 3.44709 16.8586 3.47117 16.8963 3.50063L16.9512 3.55028L17.0175 3.62832L17.0604 3.69966L17.091 3.77116L17.1063 3.82198L17.117 3.87254L17.1244 3.94711L17.1248 9.1187C17.1248 9.44662 16.859 9.71245 16.531 9.71245C16.2305 9.71245 15.982 9.48908 15.9427 9.19927L15.9373 9.1187L15.9367 5.4027L10.2215 11.1211C10.0107 11.3319 9.68086 11.3512 9.44838 11.1788L9.38178 11.1213C9.17093 10.9105 9.1517 10.5807 9.32411 10.3482L9.38159 10.2816L15.0959 4.56354H11.384C11.0834 4.56354 10.835 4.34017 10.7957 4.05036L10.7903 3.96979C10.7903 3.6692 11.0136 3.42077 11.3034 3.38146L11.384 3.37604Z"/>
              </mask>
              <path d="M6.23973 4.56251V3.37501H6.22451L6.20929 3.3754L6.23973 4.56251ZM9.09065 5.74459L9.17036 6.92941L9.21046 6.92671L9.25028 6.92131L9.09065 5.74459ZM9.01008 5.75001V6.93751H9.04998L9.08979 6.93483L9.01008 5.75001ZM6.23945 5.75001L6.23888 6.93751H6.23945V5.75001ZM4.46463 7.3816L3.28118 7.28357L3.27947 7.30428L3.27848 7.32504L4.46463 7.3816ZM4.45863 7.5074L3.27248 7.45085L3.27112 7.47931L3.27113 7.5078L4.45863 7.5074ZM4.46088 14.2608L5.64838 14.2605V14.2604L4.46088 14.2608ZM6.12064 16.0375L6.04084 17.2223L6.06088 17.2237L6.08096 17.2244L6.12064 16.0375ZM6.24259 16.0416L6.20292 17.2284L6.22357 17.2291L6.24423 17.2291L6.24259 16.0416ZM12.9702 16.0324L12.9719 17.2199L12.9702 16.0324ZM14.7449 14.373L15.9297 14.453L15.9311 14.433L15.9318 14.4129L14.7449 14.373ZM14.749 14.2511L15.9359 14.2911L15.9365 14.2711V14.2511H14.749ZM15.9311 11.3947L17.1159 11.315L17.1132 11.2749L17.1078 11.2351L15.9311 11.3947ZM15.9365 11.4753H17.124V11.4354L17.1214 11.3956L15.9365 11.4753ZM13.1294 17.2155L13.162 18.4026L13.1775 18.4022L13.193 18.4013L13.1294 17.2155ZM12.9719 17.2199L12.9735 18.4074L12.989 18.4073L13.0044 18.4069L12.9719 17.2199ZM6.2462 17.2291L6.21618 18.4162L6.232 18.4166L6.24783 18.4166L6.2462 17.2291ZM6.08524 17.225L6.0235 18.4109L6.03935 18.4117L6.05521 18.4121L6.08524 17.225ZM3.27753 14.4188L2.09044 14.4501L2.09085 14.4656L2.09167 14.4812L3.27753 14.4188ZM3.27338 14.2611L2.08588 14.2614L2.08588 14.2769L2.08629 14.2924L3.27338 14.2611ZM3.27161 7.53327L2.08439 7.50742L2.0841 7.5205L2.08411 7.53358L3.27161 7.53327ZM3.2751 7.37295L2.08922 7.3109L2.08827 7.32899L2.08788 7.3471L3.2751 7.37295ZM6.08209 4.56655L6.05165 3.37944L6.03609 3.37984L6.02056 3.38065L6.08209 4.56655ZM11.384 3.37604L11.3841 2.18854L11.3442 2.18853L11.3043 2.19122L11.384 3.37604ZM16.5723 3.37644L16.735 2.20014L16.6541 2.18895L16.5724 2.18894L16.5723 3.37644ZM16.6512 3.38734L16.9709 2.2437L16.8935 2.22206L16.8139 2.21104L16.6512 3.38734ZM16.731 3.40966L17.1947 2.31645L17.1243 2.2866L17.0507 2.26601L16.731 3.40966ZM16.776 3.42874L17.25 2.33992L17.2397 2.33553L16.776 3.42874ZM16.8963 3.50063L17.6929 2.61989L17.6609 2.59097L17.6269 2.56444L16.8963 3.50063ZM16.9512 3.55028L17.8563 2.78147L17.8057 2.72193L17.7477 2.66953L16.9512 3.55028ZM17.0175 3.62832L18.0353 3.01646L17.9853 2.93339L17.9226 2.85951L17.0175 3.62832ZM17.0604 3.69966L18.152 3.23201L18.12 3.15738L18.0781 3.0878L17.0604 3.69966ZM17.091 3.77116L18.2287 3.43074L18.2093 3.36581L18.1826 3.30351L17.091 3.77116ZM17.1063 3.82198L18.2678 3.57521L18.2578 3.5279L18.2439 3.48156L17.1063 3.82198ZM17.117 3.87254L18.2987 3.75511L18.2922 3.68988L18.2786 3.62576L17.117 3.87254ZM17.1244 3.94711L18.3119 3.94702L18.3119 3.88821L18.3061 3.82968L17.1244 3.94711ZM17.1248 9.1187H18.3123V9.11861L17.1248 9.1187ZM15.9427 9.19927L14.7579 9.27899L14.7606 9.31908L14.766 9.35891L15.9427 9.19927ZM15.9373 9.1187L14.7498 9.1189L14.7498 9.1587L14.7525 9.19842L15.9373 9.1187ZM15.9367 5.4027L17.1242 5.40251L17.1237 2.53517L15.0968 4.56325L15.9367 5.4027ZM10.2215 11.1211L11.0613 11.9606L11.0614 11.9605L10.2215 11.1211ZM9.44838 11.1788L8.67259 12.0778L8.70579 12.1065L8.741 12.1326L9.44838 11.1788ZM9.38178 11.1213L8.54228 11.9612L8.57305 11.9919L8.60599 12.0203L9.38178 11.1213ZM9.32411 10.3482L8.42505 9.57241L8.39641 9.6056L8.37029 9.64082L9.32411 10.3482ZM9.38159 10.2816L8.54162 9.44217L8.51091 9.4729L8.48253 9.5058L9.38159 10.2816ZM15.0959 4.56354L15.9359 5.40296L17.9615 3.37604H15.0959V4.56354ZM10.7957 4.05036L9.61085 4.13006L9.61355 4.17016L9.61895 4.20999L10.7957 4.05036ZM10.7903 3.96979H9.60275V4.00969L9.60543 4.04949L10.7903 3.96979ZM11.3034 3.38146L11.2237 2.19664L11.1836 2.19933L11.1438 2.20474L11.3034 3.38146ZM6.23973 5.75001H9.01008V3.37501H6.23973V5.75001ZM9.01008 5.75001C8.68216 5.75001 8.41633 5.48418 8.41633 5.15626H10.7913C10.7913 4.17251 9.99384 3.37501 9.01008 3.37501V5.75001ZM8.41633 5.15626C8.41633 4.8547 8.64004 4.60734 8.93101 4.56787L9.25028 6.92131C10.1209 6.80321 10.7913 6.05901 10.7913 5.15626H8.41633ZM9.01094 4.55977L8.93037 4.56519L9.08979 6.93483L9.17036 6.92941L9.01094 4.55977ZM9.01008 4.56251H6.23945V6.93751H9.01008V4.56251ZM6.24001 4.56251C4.68321 4.56177 3.40746 5.75902 3.28118 7.28357L5.64807 7.47962C5.67321 7.17613 5.92902 6.93736 6.23888 6.93751L6.24001 4.56251ZM3.27848 7.32504L3.27248 7.45085L5.64478 7.56395L5.65078 7.43815L3.27848 7.32504ZM3.27113 7.5078L3.27338 14.2612L5.64838 14.2604L5.64613 7.50701L3.27113 7.5078ZM3.27338 14.2611C3.27379 15.8329 4.49487 17.1182 6.04084 17.2223L6.20044 14.8527C5.89263 14.832 5.64846 14.5743 5.64838 14.2605L3.27338 14.2611ZM6.08096 17.2244L6.20292 17.2284L6.28227 14.8548L6.16031 14.8507L6.08096 17.2244ZM6.24423 17.2291L12.9719 17.2199L12.9686 14.8449L6.24096 14.8541L6.24423 17.2291ZM12.9719 17.2199C14.5421 17.2177 15.8254 15.9975 15.9297 14.453L13.5601 14.2929C13.5394 14.6004 13.2821 14.8444 12.9686 14.8449L12.9719 17.2199ZM15.9318 14.4129L15.9359 14.2911L13.5622 14.2112L13.5581 14.333L15.9318 14.4129ZM15.9365 14.2511V11.4753H13.5615V14.2511H15.9365ZM15.9365 11.4753C15.9365 11.8032 15.6707 12.069 15.3428 12.069V9.69405C14.359 9.69405 13.5615 10.4915 13.5615 11.4753H15.9365ZM15.3428 12.069C15.0412 12.069 14.7939 11.8453 14.7544 11.5544L17.1078 11.2351C16.9897 10.3645 16.2455 9.69405 15.3428 9.69405V12.069ZM14.7463 11.4745L14.7517 11.555L17.1214 11.3956L17.1159 11.315L14.7463 11.4745ZM14.749 11.4753V14.2511H17.124V11.4753H14.749ZM14.749 14.2511C14.749 15.2018 14.0036 15.9794 13.0657 16.0297L13.193 18.4013C15.3846 18.2837 17.124 16.4707 17.124 14.2511H14.749ZM13.0968 16.0285L12.9393 16.0328L13.0044 18.4069L13.162 18.4026L13.0968 16.0285ZM12.9702 16.0324L6.24457 16.0416L6.24783 18.4166L12.9735 18.4074L12.9702 16.0324ZM6.27623 16.042L6.11526 16.0379L6.05521 18.4121L6.21618 18.4162L6.27623 16.042ZM6.14698 16.0391C5.23991 15.9919 4.5111 15.2635 4.46339 14.3564L2.09167 14.4812C2.20322 16.6023 3.90235 18.3005 6.0235 18.4109L6.14698 16.0391ZM4.46462 14.3875L4.46046 14.2298L2.08629 14.2924L2.09044 14.4501L4.46462 14.3875ZM4.46088 14.2608L4.45911 7.53295L2.08411 7.53358L2.08588 14.2614L4.46088 14.2608ZM4.45882 7.55912L4.46232 7.39881L2.08788 7.3471L2.08439 7.50742L4.45882 7.55912ZM4.46097 7.43501C4.50845 6.52774 5.23722 5.79948 6.14361 5.75246L6.02056 3.38065C3.89916 3.49071 2.20022 5.1897 2.08922 7.3109L4.46097 7.43501ZM6.11252 5.75366L6.27017 5.74962L6.20929 3.3754L6.05165 3.37944L6.11252 5.75366ZM6.23973 5.75001H9.01008V3.37501H6.23973V5.75001ZM9.01008 3.37501H6.23973V5.75001H9.01008V3.37501ZM11.3839 4.56354L16.5722 4.56394L16.5724 2.18894L11.3841 2.18854L11.3839 4.56354ZM16.4096 4.55274L16.4885 4.56365L16.8139 2.21104L16.735 2.20014L16.4096 4.55274ZM16.3314 4.53098L16.4112 4.5533L17.0507 2.26601L16.9709 2.2437L16.3314 4.53098ZM16.2672 4.50286L16.3122 4.52194L17.2397 2.33553L17.1947 2.31645L16.2672 4.50286ZM16.3019 4.51751C16.2506 4.49517 16.2051 4.46752 16.1658 4.43682L17.6269 2.56444C17.512 2.47482 17.3856 2.39902 17.25 2.33997L16.3019 4.51751ZM16.0998 4.38138L16.1547 4.43102L17.7477 2.66953L17.6929 2.61989L16.0998 4.38138ZM16.0462 4.31909L16.1125 4.39714L17.9226 2.85951L17.8563 2.78147L16.0462 4.31909ZM15.9998 4.24018L16.0427 4.31152L18.0781 3.0878L18.0353 3.01646L15.9998 4.24018ZM15.9689 4.16732L15.9995 4.23881L18.1826 3.30351L18.152 3.23201L15.9689 4.16732ZM15.9534 4.11158L15.9686 4.1624L18.2439 3.48156L18.2287 3.43074L15.9534 4.11158ZM15.9447 4.06876L15.9554 4.11931L18.2786 3.62576L18.2678 3.57521L15.9447 4.06876ZM15.9353 3.98997L15.9427 4.06454L18.3061 3.82968L18.2987 3.75511L15.9353 3.98997ZM15.9369 3.9472L15.9373 9.11879L18.3123 9.11861L18.3119 3.94702L15.9369 3.9472ZM15.9373 9.1187C15.9373 8.79078 16.2031 8.52495 16.531 8.52495V10.9C17.5148 10.9 18.3123 10.1025 18.3123 9.1187H15.9373ZM16.531 8.52495C16.8326 8.52495 17.08 8.74867 17.1194 9.03963L14.766 9.35891C14.8841 10.2295 15.6283 10.9 16.531 10.9V8.52495ZM17.1275 9.11955L17.1221 9.03898L14.7525 9.19842L14.7579 9.27899L17.1275 9.11955ZM17.1248 9.11851L17.1242 5.40251L14.7492 5.4029L14.7498 9.1189L17.1248 9.11851ZM15.0968 4.56325L9.38154 10.2816L11.0614 11.9605L16.7766 6.24216L15.0968 4.56325ZM9.38159 10.2816C9.59308 10.07 9.92241 10.0519 10.1558 10.2249L8.741 12.1326C9.43932 12.6505 10.4284 12.5939 11.0613 11.9606L9.38159 10.2816ZM10.2242 10.2797L10.1576 10.2222L8.60599 12.0203L8.67259 12.0778L10.2242 10.2797ZM10.2213 10.2814C10.4329 10.4929 10.451 10.8222 10.2779 11.0556L8.37029 9.64082C7.8524 10.3391 7.909 11.3282 8.54228 11.9612L10.2213 10.2814ZM10.2232 11.124L10.2806 11.0574L8.48253 9.5058L8.42505 9.57241L10.2232 11.124ZM10.2215 11.121L15.9359 5.40296L14.256 3.72412L8.54162 9.44217L10.2215 11.121ZM15.0959 3.37604H11.384V5.75104H15.0959V3.37604ZM11.384 3.37604C11.6856 3.37604 11.9329 3.59975 11.9724 3.89072L9.61895 4.20999C9.73706 5.08058 10.4813 5.75104 11.384 5.75104V3.37604ZM11.9805 3.97065L11.9751 3.89008L9.60543 4.04949L9.61085 4.13006L11.9805 3.97065ZM11.9778 3.96979C11.9778 4.27135 11.754 4.51871 11.4631 4.55818L11.1438 2.20474C10.2732 2.32284 9.60275 3.06704 9.60275 3.96979H11.9778ZM11.3831 4.56628L11.4637 4.56086L11.3043 2.19122L11.2237 2.19664L11.3831 4.56628Z" fill="#404040" mask="url(#path-1-inside-1_620_11914-${unique_element_id})"/>
              </svg>
              </a>
              </div>
              <span class="remove-img c-pointer">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3.11499 3L8.8849 9" stroke="#4D4D4D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8.88501 3L3.1151 9" stroke="#4D4D4D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </span>
            </div>
                </div>
          </div>
    
          <div class="col s12  variant-wrapper-div"
              style="padding: 0px; width: 100%; display: none">
              <h3 class="variant-heading-text">Images</h3>
              <button class="upload-img-btn">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path fill-rule="evenodd" clip-rule="evenodd"
                          d="M1 4C0.45 4 0 4.45 0 5V18C0 19.1 0.9 20 2 20H15C15.55 20 16 19.55 16 19C16 18.45 15.55 18 15 18H3C2.45 18 2 17.55 2 17V5C2 4.45 1.55 4 1 4ZM18 0H6C4.9 0 4 0.9 4 2V14C4 15.1 4.9 16 6 16H18C19.1 16 20 15.1 20 14V2C20 0.9 19.1 0 18 0ZM16 9H13V12C13 12.55 12.55 13 12 13C11.45 13 11 12.55 11 12V9H8C7.45 9 7 8.55 7 8C7 7.45 7.45 7 8 7H11V4C11 3.45 11.45 3 12 3C12.55 3 13 3.45 13 4V7H16C16.55 7 17 7.45 17 8C17 8.55 16.55 9 16 9Z"
                          fill="#0254D7"></path>
                  </svg>
                  Upload Images
              </button>
          </div>
          <!-- upload images-> data added start  -->
          <div class="col s12  images-uploaded d-none"
              style="padding: 0px; width: 100%">
              <h3 class="variant-heading-text">Images</h3>
              <button class="upload-img-btn">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path fill-rule="evenodd" clip-rule="evenodd"
                          d="M1 4C0.45 4 0 4.45 0 5V18C0 19.1 0.9 20 2 20H15C15.55 20 16 19.55 16 19C16 18.45 15.55 18 15 18H3C2.45 18 2 17.55 2 17V5C2 4.45 1.55 4 1 4ZM18 0H6C4.9 0 4 0.9 4 2V14C4 15.1 4.9 16 6 16H18C19.1 16 20 15.1 20 14V2C20 0.9 19.1 0 18 0ZM16 9H13V12C13 12.55 12.55 13 12 13C11.45 13 11 12.55 11 12V9H8C7.45 9 7 8.55 7 8C7 7.45 7.45 7 8 7H11V4C11 3.45 11.45 3 12 3C12.55 3 13 3.45 13 4V7H16C16.55 7 17 7.45 17 8C17 8.55 16.55 9 16 9Z"
                          fill="#0254D7"></path>
                  </svg>
                  Upload Images
              </button>
              <div class="priview-uploaded-img-div">
                  <div class="img-div-wrapper">
                      <span class="remove-img">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                              xmlns="http://www.w3.org/2000/svg">
                              <circle cx="6" cy="6" r="6" fill="#F6F6F6"></circle>
                              <path d="M3.5957 3.5L8.40396 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                              <path d="M8.4043 3.5L3.59604 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                          </svg>
                      </span>
                  </div>
                  <div class="img-div-wrapper">
                      <span class="remove-img">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                              xmlns="http://www.w3.org/2000/svg">
                              <circle cx="6" cy="6" r="6" fill="#F6F6F6"></circle>
                              <path d="M3.5957 3.5L8.40396 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                              <path d="M8.4043 3.5L3.59604 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                          </svg>
                      </span>
                  </div>
                  <div class="img-div-wrapper">
                      <span class="remove-img">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                              xmlns="http://www.w3.org/2000/svg">
                              <circle cx="6" cy="6" r="6" fill="#F6F6F6"></circle>
                              <path d="M3.5957 3.5L8.40396 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                              <path d="M8.4043 3.5L3.59604 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                          </svg>
                      </span>
                  </div>
                  <div class="img-div-wrapper">
                      <span class="remove-img">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                              xmlns="http://www.w3.org/2000/svg">
                              <circle cx="6" cy="6" r="6" fill="#F6F6F6"></circle>
                              <path d="M3.5957 3.5L8.40396 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                              <path d="M8.4043 3.5L3.59604 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                          </svg>
                      </span>
                  </div>
                  <div class="img-div-wrapper">
                      <span class="remove-img">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                              xmlns="http://www.w3.org/2000/svg">
                              <circle cx="6" cy="6" r="6" fill="#F6F6F6"></circle>
                              <path d="M3.5957 3.5L8.40396 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                              <path d="M8.4043 3.5L3.59604 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                          </svg>
                      </span>
                  </div>
                  <div class="img-div-wrapper">
                      <span class="remove-img">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none"
                              xmlns="http://www.w3.org/2000/svg">
                              <circle cx="6" cy="6" r="6" fill="#F6F6F6"></circle>
                              <path d="M3.5957 3.5L8.40396 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                              <path d="M8.4043 3.5L3.59604 8.5" stroke="#2D2D2D" stroke-width="0.868072"
                                  stroke-linecap="round" stroke-linejoin="round"></path>
                          </svg>
                      </span>
                  </div>
              </div>
          </div>
          <!-- upload images-> data added end -->
          <div class="col s12  status-wrapper"
              style="padding: 0px; width: 100%; margin-top: 12px">
              <div class="status-wrapper-div d-none">
                  <h3 class="variant-heading-text" style="margin-right: 11px">
                      Status
                  </h3>
                  <div class="easychat-custom-switch-toggle-wrapper" id="whatsapp_catalog_toggle">
                      <label class="easychat-custom-toggle-switch">
                          <input type="checkbox" id="item_status_${unique_element_id}" />
    
                          <span class="easychat-custom-toggle-slider easychat-custom-toggle-round"></span>
                      </label>
                  </div>
                  <svg width="10" height="17" viewBox="0 0 3 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path opacity="0.07" d="M0.757812 16.2969V0.46875H2.375V16.2969H0.757812Z" fill="#262B33">
                      </path>
                  </svg>
                  <h3 class="variant-heading-text" style="margin-right: 11px; opacity: 1">
                      Active
                  </h3>
              </div>
              <div class="variant-price-wrapper-div" style="width: 100%">
              <h3 class="variant-heading-text">Availability</h3>
                <div class="custom_dropdown"> 
                    <button class="dropdown__button" type="button"><span style="text-transform: capitalize" id="item_availability_${unique_element_id}">In Stock</span></button>
                    <ul class="dropdown__list">
                        <li class="dropdown__list-item" data-value="In Stock"><span>In Stock</span></li>
                        <li class="dropdown__list-item" data-value="Available for order"><span>Available for order</span></li>
                        <li class="dropdown__list-item" data-value="Preorder"><span>Preorder</span></li>
                        <li class="dropdown__list-item" data-value="Out of stock"><span>Out of stock</span></li>
                        <li class="dropdown__list-item" data-value="Discontinued"><span>Discontinued</span></li>
                    </ul>
                    <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
                </div>
              </div>
              <div class="input-wrapper-div">
              <div class="sales-price-date" style="width: 100%">
                  <h3 class="variant-heading-text">Origin Country <span style="color:#E10E00">*</span></h3>
                  <div class="custom_dropdown"> 
                  <button class="dropdown__button" type="button"><span id="item_origin_${unique_element_id}">IN</span></button>
                  <ul class="dropdown__list">
                  <li class="dropdown__list-item dropdown-filter"><input type="text" onkeyup="custom_dropdown_search(this)" class="search-country-input" placeholder="Search Country"/></li>
                    ${get_origin_country_dropdown_options()}
                  <div class="no-data-div">No country found</div>
                  </ul>
                  <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
              </div>
              </div>
          </div>
          </div>
          <div class="col s12  variant-wrapper-div images-uploaded"
              style="padding: 0px; width: 100%">
              <div class="variant-price-wrapper">
                  <div class="variant-price-wrapper-div">
                      <h3 class="variant-heading-text">Price <span style="color:#E10E00">*</span></h3>
                      <div class="price-input-box custom-dropdown-input">
                      <div class="custom_dropdown"> 
                            <button class="dropdown__button" type="button"><span id="item_currency_${unique_element_id}">INR</span></button>
                            <ul class="dropdown__list">
                            <li class="dropdown__list-item dropdown-filter"><input type="text" onkeyup="custom_dropdown_search(this)" class="search-currency-input" placeholder="Search Currency"/></li>
                            ${get_currency_dropdown_options()}
                            <div class="no-data-div">No currency found</div>
                            </ul>
                            <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
                        </div> 
                      <div class="inr-count">
                                  <input id="item_price_${unique_element_id}" placeholder="0.00" />
                              </div>
                      </div>      
                  </div>
                  <div class="variant-price-wrapper-div">
                      <h3 class="variant-heading-text">Sale price</h3>
                      <div class="price-input-box">
                          <div class="inr-count">
                              <input style=" border-radius: 4px!important;" id="item_sale_price_${unique_element_id}" placeholder="0.00" />
                          </div>
                      </div>
                  </div>
              </div>
          </div>
          <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%">
            <div class="input-wrapper-div">
                <div class="sales-price-date">
                    <h3 class="variant-heading-text">Brand <span style="color:#E10E00">*</span></h3>
                    <input class="variant-input" type="text" id="item_brand_${unique_element_id}" placeholder="Example: Nike" maxlength="100" />
                    <span class="variant-input-counter"><span id="brand_count_${unique_element_id}">0</span>/100</span>
                </div>
                <div class="sales-price-date">
                    <h3 class="variant-heading-text">Content ID <span style="color:#E10E00">*</span></h3>
                    <input class="variant-input" type="text" id="item_content_id_${unique_element_id}" placeholder="Example: nike_shoes_1" maxlength="100" />
                    <span class="variant-input-counter"><span id="content_id_count_${unique_element_id}">0</span>/100</span>
                </div>
            </div>
            </div>
            <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%">
                <div class="input-wrapper-div">
                    <div class="sales-price-date">
                        <h3 class="variant-heading-text">Category <span style="color:#E10E00">*</span></h3>
                        <input class="variant-input" type="text" id="item_product_category_${unique_element_id}" placeholder="Example: footwear" maxlength="100" />
                        <span class="variant-input-counter"><span id="product_category_count_${unique_element_id}">0</span>/100</span>
                    </div>
                    <div class="sales-price-date">
                        <h3 class="variant-heading-text">Fb Product Category</h3>
                        <input class="variant-input" type="text" id="item_facebook_product_category_${unique_element_id}" maxlength="100" />
                        <span class="variant-input-counter"><span id="fb_category_count_${unique_element_id}">0</span>/100</span>
                    </div>
                </div>
            </div>
          <div class="col s12  variant-wrapper-div"
              style="padding: 0px; width: 100%; margin-top: 12px">
              <div class="input-wrapper-div" >
                  <div class="sales-price-date">
                      <h3 class="variant-heading-text">Sale price starting date</h3>
                      <input class="variant-input" id="item_sale_start_date_${unique_element_id}" type="datetime-local" placeholder="YYYY-MM-DDT23:59+00:00" >
                  </div>
                  <div class="sales-price-date">
                      <h3 class="variant-heading-text">Sale price ending date</h3>
                      <input class="variant-input" type="datetime-local" id="item_sale_end_date_${unique_element_id}" placeholder="YYYY-MM-DDT23:59+00:00" />
                  </div>
              </div>
          </div>
          <div class="col s12  input-wrapper-div"style="margin-bottom: 8px;">
          <div class="variant-price-wrapper-div" style="width: 100%">
          <h3 class="variant-heading-text">Condition</h3>
            <div class="custom_dropdown"> 
                <button class="dropdown__button" type="button"><span id="item_condition_${unique_element_id}">New</span></button>
                <ul class="dropdown__list">
                    <li class="dropdown__list-item" data-value="New"><span>New</span></li>
                    <li class="dropdown__list-item" data-value="Refurbished"><span>Refurbished</span></li>
                    <li class="dropdown__list-item" data-value="Used (like new)"><span>Used (like new)</span></li>
                    <li class="dropdown__list-item" data-value="Used (good)"><span>Used (good)</span></li>
                    <li class="dropdown__list-item" data-value="Used (fair)"><span>Used (fair)</span></li>
                </ul>
                <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
            </div>
         
        
            
          </div>
          <div class="select-gender">
          <h3 class="variant-heading-text">Select Gender</h3>
          <div class="custom_dropdown"> 
          <button class="dropdown__button" type="button"><span id="item_gender_${unique_element_id}">Male</span></button>
          <ul class="dropdown__list">
          <li class="dropdown__list-item" data-value="Male"><span>Male</span></li>
          <li class="dropdown__list-item" data-value="Female"><span>Female</span></li>
          <li class="dropdown__list-item" data-value="Unisex"><span>Unisex</span></li>
          </ul>
              <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
          </div>
          </div>
      </div>
          <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%;margin-bottom: 0px;">
              <div class="input-wrapper-div">
                  <div class="sales-price-date">
                  <div style="display: flex;gap:1px;">
                  <h3 class="variant-heading-text">Item Group ID      
                  </h3>
                  <div class="tooltip-group-id"><svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                     <path d="M7 1.75C9.89958 1.75 12.25 4.10095 12.25 7C12.25 9.89905 9.89958 12.25 7 12.25C4.10043 12.25 1.75 9.89905 1.75 7C1.75 4.10095 4.10043 1.75 7 1.75ZM7 8.8375C6.71005 8.8375 6.475 9.07255 6.475 9.3625C6.475 9.65245 6.71005 9.8875 7 9.8875C7.28995 9.8875 7.525 9.65245 7.525 9.3625C7.525 9.07255 7.28995 8.8375 7 8.8375ZM7 4.24375C6.20264 4.24375 5.55625 4.89014 5.55625 5.6875C5.55625 5.90496 5.73254 6.08125 5.95 6.08125C6.14934 6.08125 6.31408 5.93312 6.34016 5.74093L6.34375 5.6875C6.34375 5.32506 6.63756 5.03125 7 5.03125C7.36244 5.03125 7.65625 5.32506 7.65625 5.6875C7.65625 5.97038 7.58538 6.11026 7.31768 6.3869L7.24658 6.45908C6.78557 6.92008 6.60625 7.21895 6.60625 7.7875C6.60625 8.00496 6.78254 8.18125 7 8.18125C7.21746 8.18125 7.39375 8.00496 7.39375 7.7875C7.39375 7.50462 7.46462 7.36474 7.73232 7.0881L7.80342 7.01592C8.26443 6.55492 8.44375 6.25605 8.44375 5.6875C8.44375 4.89014 7.79736 4.24375 7 4.24375Z" fill="#4D4D4D"/>
                     </svg>
                     <span class="tooltiptext-group-id">To create a variant of any item, keep the group item id the same as the created item.</span>
                   </div>
                 </div>
                      <input class="variant-input" type="text" id="item_group_id_${unique_element_id}" maxlength="100" />
                      <span class="variant-input-counter"><span id="group_id_count_${unique_element_id}">0</span>/100</span>
                  </div>
                  <div class="sales-price-date">
                      <h3 class="variant-heading-text">Color</h3>
                      <input class="variant-input" type="text" id="item_color_${unique_element_id}" maxlength="100" />
                      <span class="variant-input-counter"><span id="color_count_${unique_element_id}">0</span>/100</span>
                  </div>
              </div>
          </div>
          <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%">
              <div class="input-wrapper-div">
       
            <div class="select-size-group d-none">
            <h3 class="variant-heading-text">Size Group</h3>
            <div class="custom_dropdown"> 
                <button class="dropdown__button" type="button"><span>Delhi</span></button>
                <ul class="dropdown__list">
                <li class="dropdown__list-item" data-value="Delhi"><span>Delhi</span></li>
                <li class="dropdown__list-item" data-value="Mumbai"><span>Mumbai</span></li>
                </ul>
                <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
            </div>
            </div>
            <div class="select-shipping-weight d-none">
            <h3 class="variant-heading-text">Shipping Weight</h3>
            <div class="custom_dropdown"> 
            <button class="dropdown__button" type="button"><span>Kg</span></button>
            <ul class="dropdown__list">
            <li class="dropdown__list-item" data-value="Kg"><span>Kg</span></li>
            <li class="dropdown__list-item" data-value="Gm"><span>Gm</span></li>
            <li class="dropdown__list-item" data-value="Pound"><span>Pound</span></li>
            </ul>
                <input class="dropdown__input_hidden" type="text" name="select-category" value="" />
            </div>
            </div>
              </div>
          </div>
    
          <div class="col s12  variant-wrapper-div" style="padding: 0px; width: 100%">
              <div class="input-wrapper-div">
                  <div class="sales-price-date">
                      <h3 class="variant-heading-text">Material</h3>
                      <input class="variant-input" type="text" id="item_material_${unique_element_id}" maxlength="100" />
                      <span class="variant-input-counter"><span id="material_count_${unique_element_id}">0</span>/100</span>
                  </div>
                  <div class="sales-price-date">
                      <h3 class="variant-heading-text">Pattern</h3>
                      <input class="variant-input" type="text" id="item_pattern_${unique_element_id}" maxlength="100" />
                      <span class="variant-input-counter"><span id="pattern_count_${unique_element_id}">0</span>/100</span>
                  </div>
              </div>
          </div>
      </div>
    </div>
        `;
        return accordion_body;
    }

    function get_catalogue_items_data(modal_id) {
        // let catalogue_items = [];
        let catalogue_items = {};
        let error_message = null;
        $("#" + modal_id + " #accordion-div .accrodion-wrapper").each(function () {
            let element_id = this.id.split('-');
            element_id = element_id[element_id.length - 1];
            let item_title = $("#accordion-header-wrapper-" + element_id + " .item-name.non-variant").text().trim() + ": ";
            if (modal_id == "edit_item_modal") {
                element_id = "edit_item";
                item_title = "";
            }
            reset_item_errors(element_id);

            item = {};
            item.name = $("#item_title_" + element_id).val().trim();
            if (item.name == "") {
                error_message = item_title + "Title cannot be empty!";
                $("#item_title_" + element_id).attr("style", "border: 1px solid #ff2818 !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }
            item.description = $("#item_description_" + element_id).val().trim();
            if (item.description == "") {
                error_message = item_title + "Description cannot be empty!";
                $("#item_description_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }
            item.url = $("#item_website_" + element_id).val().trim();
            if (item.url == "") {
                error_message = item_title + ": Website URL cannot be empty!";
                $("#item_website_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            if (!isValidURL(item.url)) {
                error_message = item_title + "Please enter a valid website URL!";
                $("#item_website_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            item.image_url = $("#accordion-header-wrapper-" + element_id + " .additional-image-url-input").eq(0).val().trim();
            if (item.image_url == "") {
                error_message = item_title + "Image URL cannot be empty!";
                $("#accordion-header-wrapper-" + element_id + " .additional-image-url-input").eq(0).closest(".drag-drop-img-link-wrapper").attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            if (!isValidURL(item.image_url)) {
                error_message = item_title + "Please enter a valid Image URL!";
                $("#accordion-header-wrapper-" + element_id + " .additional-image-url-input").eq(0).closest(".drag-drop-img-link-wrapper").attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            item.currency = $("#item_currency_" + element_id).text().trim();
            if (item.currency == "") {
                error_message = item_title + "Currency cannot be empty!";
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }
            item.price = $("#item_price_" + element_id).val().trim();
            if (item.price == "") {
                error_message = item_title + "Price cannot be empty!";
                $("#item_price_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            if ((/^\s*$/.test(item.price)) && isNaN(item.price)) {
                error_message = item_title + "Please enter a valid price!";
                $("#item_price_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }
            item.price = parseFloat(item.price);

            item.brand = $("#item_brand_" + element_id).val().trim();
            if (item.brand == "") {
                error_message = item_title + "Brand cannot be empty!";
                $("#item_brand_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            item.retailer_id = $("#item_content_id_" + element_id).val().trim();
            if (item.retailer_id == "") {
                error_message = item_title + "Content ID cannot be empty!";
                $("#item_content_id_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            item.category = $("#item_product_category_" + element_id).val().trim();
            if (item.category == "") {
                error_message = item_title + "Category cannot be empty!";
                $("#item_product_category_" + element_id).attr("style", "border: 1px solid red !important")
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            item.origin_country = $("#item_origin_" + element_id).text().trim();
            if (item.origin_country == "") {
                error_message = item_title + "Origin Country cannot be empty!";
                $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                // return false;
            }

            item.availability = $("#item_availability_" + element_id).text().toLowerCase().trim();

            let additional_image_urls = [];
            $("#accordion-header-wrapper-" + element_id + " .additional-image-url").each((index, element) => {
                if (index == 0) return true;
                let additional_url = $(element).find('input').val().trim()
                if (!isValidURL(additional_url) || additional_url == "") {
                    error_message = item_title + "Please enter valid additional URL!";
                    $(element).find('input').closest(".drag-drop-img-link-wrapper").attr("style", "border: 1px solid red !important")
                    $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                    // return false;
                }
                additional_image_urls.push(additional_url)
            })

            if (additional_image_urls.length) {
                item.additional_image_urls = additional_image_urls;
            }

            if ($("#item_facebook_product_category_" + element_id).val().trim() != "") {
                item.fb_product_category = $("#item_facebook_product_category_" + element_id).val().trim()
            }

            if ($("#item_group_id_" + element_id).val().trim() != "" && modal_id != "edit_item_modal") {
                item.retailer_product_group_id = $("#item_group_id_" + element_id).val().trim()
            }

            if ($("#item_color_" + element_id).val().trim() != "") {
                item.color = $("#item_color_" + element_id).val().trim()
            }

            item.gender = $("#item_gender_" + element_id).text().trim().toLowerCase();

            if ($("#item_material_" + element_id).val().trim() != "") {
                item.material = $("#item_material_" + element_id).val().trim()
            }

            if ($("#item_pattern_" + element_id).val().trim() != "") {
                item.pattern = $("#item_pattern_" + element_id).val().trim()
            }

            if ($("#item_sale_price_" + element_id).val().trim() != "") {
                item.sale_price = $("#item_sale_price_" + element_id).val();
                if ((/^\s*$/.test(item.sale_price)) && isNaN(item.sale_price)) {
                    let item_title = $("#accordion-header-wrapper-" + element_id + " .item-name.non-variant").text().trim()
                    error_message = item_title + "Please enter a valid sale price!";
                    showToast(error_message, 2000);
                    $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").show();
                    // return false;
                } else {
                    item.sale_price = parseFloat(item.sale_price);
                }
            }

            item.sale_price_start_date = "";
            if ($("#item_sale_start_date_" + element_id).val().trim() != "") {
                item.sale_price_start_date = $("#item_sale_start_date_" + element_id).val().trim() + "+0530"
            }

            item.sale_price_end_date = "";
            if ($("#item_sale_end_date_" + element_id).val().trim() != "") {
                item.sale_price_end_date = $("#item_sale_end_date_" + element_id).val().trim() + "+0530"
            }

            let item_condition = $("#item_condition_" + element_id).text().trim().toLowerCase()

            item = get_item_condition(item, item_condition)

            // catalogue_items.push(item);
            catalogue_items[element_id] = item;
        })
        return [catalogue_items, error_message];
    }

    function get_item_condition(item, item_condition) {
        if (item_condition == "new") {
            item.condition = "new";
        } else if (item_condition == "refurbished") {
            item.condition = "refurbished";
        } else if (item_condition == "used (like new)") {
            item.condition = "used_like_new";
        } else if (item_condition == "used (good)") {
            item.condition = "used_good";
        } else if (item_condition == "used (fair)") {
            item.condition = "used_fair";
        }
        return item;
    }

    function add_char_count_event_listeners(element_id) {
        $("#item_title_" + element_id).keyup((el) => $("#title_count_" + element_id).text(el.target.value.length))
        $("#item_description_" + element_id).keyup((el) => $("#description_count_" + element_id).text(el.target.value.length))
        $("#item_brand_" + element_id).keyup((el) => $("#brand_count_" + element_id).text(el.target.value.length))
        $("#item_content_id_" + element_id).keyup((el) => $("#content_id_count_" + element_id).text(el.target.value.length))
        $("#item_group_id_" + element_id).keyup((el) => $("#group_id_count_" + element_id).text(el.target.value.length))
        $("#item_color_" + element_id).keyup((el) => $("#color_count_" + element_id).text(el.target.value.length))
        $("#item_product_category_" + element_id).keyup((el) => $("#product_category_count_" + element_id).text(el.target.value.length))
        $("#item_facebook_product_category_" + element_id).keyup((el) => $("#fb_category_count_" + element_id).text(el.target.value.length))
        $("#item_material_" + element_id).keyup((el) => $("#material_count_" + element_id).text(el.target.value.length))
        $("#item_pattern_" + element_id).keyup((el) => $("#pattern_count_" + element_id).text(el.target.value.length))
        $("#item_manufacturing_country_" + element_id).keyup((el) => $("#manufacturing_count_" + element_id).text(el.target.value.length))
    }

    function add_number_validator_event_listeners(element_id) {
        $('#item_price_' + element_id + ', #item_sale_price_' + element_id).on('input', function () {
            this.value = this.value.replace(/[^0-9.]/g, '').replace(/(\..*?)\..*/g, '$1');
        });
    }

    function add_new_variant_event_listener(element_id) {
        $(document).on("click", "#accordion-header-wrapper-" + element_id + " .variant_dropdown ul li.add-variant", function (e) {
            let accordion_wrapper = $(this).closest('.accrodion-wrapper')
            accordion_wrapper.addClass('dynamic-wrapper')
            $(create_variant_header_html()).appendTo(accordion_wrapper);
        })
    }

    function add_delete_new_item_event_listeners(element_id) {
        $("#accordion-header-wrapper-" + element_id + " .new-item-selection-cb").change(() => {
            let checked_items_length = $(".new-item-selection-cb:checked").length
            $(".delete-new-item").css({
                "opacity": checked_items_length ? "1" : "0.5",
                "pointer-events": checked_items_length ? "auto" : "none"
            })
        })
        if ($(".new-item-selection-cb").length) {
            $("#save_catalogue_items").css({
                "opacity": "1",
                "pointer-events": "auto"
            })
        }
        $(".new-item-selection-cb").change();
    }

    function add_event_listeners_for_catalogue_items(element_id) {
        add_new_variant_event_listener(element_id);
        add_char_count_event_listeners(element_id);
        add_number_validator_event_listeners(element_id);
        add_delete_new_item_event_listeners(element_id);
        check_img_cross_icon_condition(element_id);
        $("#upload_image_" + element_id).click(() => {
            $("#upload_images_on_server").attr("active_section", element_id)
            $("#item-images-wrapper").empty()
            count_images();
            check_upload_image_button_condition();
        })
    }

    $("#delete_catalogue_products_btn").click(() => {
        let product_ids = [];
        $(".catalogue-select-row-cb:checked").each((index, item) => {
            let product_id = item.id.split('_');
            product_id = product_id[product_id.length - 1];
            product_ids.push(product_id)
        })
        if (!product_ids.length) {
            showToast("Please select atleast one item to be deleted!", 2000);
            return;
        }
        delete_product_items(product_ids)
    });

    $("#delete_single_item_btn").click(() => {
        let product_id = $("#item_being_edited").val();
        delete_product_items([product_id], true);
    })
    
    function delete_product_items(product_ids, single_item=false) {
        let delete_btn_id = "delete_catalogue_products_btn";
        if (single_item) {
            delete_btn_id = "delete_single_item_btn"
        }
        $("#" + delete_btn_id).css({
            "opacity": "0.5",
            "pointer-events": "none"
        })
        $("#" + delete_btn_id).text("Deleting...")
        let json_string = JSON.stringify({
            bot_id: BOT_ID,
            product_ids: product_ids,
        })
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        let params = 'json_string=' + json_string
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/chat/channels/whatsapp/delete-catalogue-products/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    sync_products_from_facebook();
                    M.toast({
                        "html": "Item(s) deleted successfully!"
                    }, 2000);
                    $("#" + delete_btn_id).css({
                        "opacity": "1",
                        "pointer-events": "auto"
                    })
                    $("#" + delete_btn_id).text("Delete")
                    $("#modal-delete-item, #modal-delete-single-item, #edit_item_modal").modal("close");
                } else {
                    if ("message" in response) {
                        M.toast({
                            "html": response["message"]
                        }, 5000);
                    } else {
                        M.toast({
                            "html": "Error in deleting item(s), please try again later."
                        }, 2000);
                    }
                    $("#" + delete_btn_id).css({
                        "opacity": "1",
                        "pointer-events": "auto"
                    })
                    $("#" + delete_btn_id).text("Delete")
                }
            } else if (this.readyState == 4 && this.status != 200) {
                M.toast({
                    "html": "Error in deleting item(s), please try again later."
                }, 2000);
                $("#" + delete_btn_id).css({
                    "opacity": "1",
                    "pointer-events": "auto"
                })
                $("#" + delete_btn_id).text("Delete")
            }
        }
        xhttp.send(params);
    }

    $("#initialize_single_delete").click(() => {
        $("#modal-delete-single-item").modal("open")
    })

    function reset_item_errors(element_id) {
        $("#accordion-header-wrapper-" + element_id + " .error-in-item-div").hide();
        $("#item_title_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_description_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_website_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_image_link_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_price_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_brand_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_content_id_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#item_product_category_" + element_id).attr("style", "border: 1px solid #CBCACA !important");
        $("#accordion-header-wrapper-" + element_id + " .drag-drop-img-link-wrapper").attr("style", "border: 1px solid #CBCACA !important");
    }

    function update_item_titles() {
        $("#add_item_modal #accordion-div .accrodion-wrapper").each(function (index, element) {
            $("#add_item_modal #" + element.id + " .item-name.non-variant").text("Item " + (index + 1).toString());
        })
    }

    $("#delete_new_item_btn").click(() => {
        $("#add_item_modal .new-item-selection-cb:checked").each((index, item) => {
            let section_id = $(item).attr("section-id");
            $("#accordion-header-wrapper-" + section_id).remove();
        })
        $("#modal-delete-new-item").modal("close")
        $("#add_item_modal .new-item-selection-cb").change();
        if (!$("#add_item_modal .new-item-selection-cb").length) {
            $(".delete-new-item, #save_catalogue_items").css({
                "opacity": "0.5",
                "pointer-events": "none"
            })
        }
        update_item_titles();
    });

    $("#detail_item_modal #edit_catalogue_item_btn").click(() => {
        let item_id = $("#detail_item_modal #edit_catalogue_item_btn").prop("active-item-id");
        $("#edit_item_modal").modal("open");
        populate_edit_item_modal(item_id);
    })

    function populate_edit_item_modal(item_id) {
        $("#edit_item_modal .modal-overflow-content-div").scrollTop(0);
        let items_map = window.ACTIVE_CATALOGUE_TABLE.catalogue_items_map;
        let item_details = items_map[item_id];
        let item_details_dump = JSON.parse(item_details.details_dump)
        empty_existing_edit_item_fields();
        $("#accordion-header-wrapper-edit_item .additional-image-url").remove();
        $("#item_being_edited").val(item_id)
        $("#item_title_edit_item").val(item_details.name).keyup();
        $("#item_description_edit_item").val(item_details_dump.description).keyup();
        $("#item_website_edit_item").val(item_details_dump.url).keyup();
        $("#accordion-header-wrapper-edit_item .add-more-image-link").click();
        $("#accordion-header-wrapper-edit_item .additional-image-url-input").eq(0).val(item_details.image_url).keyup();
        $("#item_currency_edit_item").text(item_details.currency)
        $("#item_price_edit_item").val(item_details.price).keyup().trigger("input");
        $("#item_brand_edit_item").val(item_details.brand).keyup();
        $("#item_content_id_edit_item").val(item_details.retailer_id).keyup();
        $("#item_group_id_edit_item").val(item_details_dump.retailer_product_group_id).keyup();
        $("#item_product_category_edit_item").val(item_details_dump.category).keyup();
        $("#item_availability_edit_item").text(item_details.availability)
        $("#item_facebook_product_category_edit_item").val(item_details_dump.fb_product_category).keyup();
        $("#item_color_edit_item").val(item_details_dump.color).keyup();
        $("#item_material_edit_item").val(item_details_dump.material).keyup();
        $("#item_pattern_edit_item").val(item_details_dump.pattern).keyup();
        $("#item_sale_price_edit_item").val(item_details_dump.sale_price).keyup().trigger("input");
        if ("additional_image_urls" in item_details_dump && item_details_dump.additional_image_urls.length) {
            for (let index = 0; index < item_details_dump.additional_image_urls.length; index++) {
                $("#accordion-header-wrapper-edit_item .add-more-image-link").click();
                $("#accordion-header-wrapper-edit_item .additional-image-url-input").eq(index+1).val(item_details_dump.additional_image_urls[index]);
            }
        }
        if ("sale_price_start_date" in item_details_dump && item_details_dump.sale_price_start_date != "") {
            let start_date = new Date(item_details_dump.sale_price_start_date)
            start_date = new Date(start_date.getTime() - start_date.getTimezoneOffset() * 60000).toISOString();
            $("#item_sale_start_date_edit_item").val(start_date.slice(0, 16));
        }
        if ("sale_price_end_date" in item_details_dump && item_details_dump.sale_price_end_date != "") {
            let end_date = new Date(item_details_dump.sale_price_end_date)
            end_date = new Date(end_date.getTime() - end_date.getTimezoneOffset() * 60000).toISOString();
            $("#item_sale_end_date_edit_item").val(end_date.slice(0, 16));
        }

        if ("origin_country" in item_details_dump && item_details_dump.origin_country != "") {
            $("#item_origin_edit_item").text(item_details_dump.origin_country)
        }

        populate_item_condition(item_details)
    }

    function populate_item_condition(item_details) {
        let item_condition = item_details.condition;

        if (item_condition == "new") {
            $("#item_condition_edit_item").text("New");
        } else if (item_condition == "refurbished") {
            $("#item_condition_edit_item").text("Refurbished");
        } else if (item_condition == "used_like_new") {
            $("#item_condition_edit_item").text("Used (like new)");
        } else if (item_condition == "used_good") {
            $("#item_condition_edit_item").text("Used (good)");
        } else if (item_condition == "used_fair") {
            $("#item_condition_edit_item").text("Used (fair)");
        } else {
            $("#item_condition_edit_item").text("New");
        }
    }

    function empty_existing_edit_item_fields() {
        $("#item_title_edit_item").val("").keyup();
        $("#item_description_edit_item").val("").keyup();
        $("#item_website_edit_item").val("").keyup();
        $("#accordion-header-wrapper-edit_item .multiple-img-link-wrapper-div").empty();
        $("#item_price_edit_item").val("").keyup().trigger("input");
        $("#item_brand_edit_item").val("").keyup();
        $("#item_content_id_edit_item").val("").keyup();
        $("#item_group_id_edit_item").val("").keyup();
        $("#item_product_category_edit_item").val("").keyup();
        $("#item_facebook_product_category_edit_item").val("").keyup();
        $("#item_color_edit_item").val("").keyup();
        $("#item_material_edit_item").val("").keyup();
        $("#item_pattern_edit_item").val("").keyup();
        $("#item_sale_price_edit_item").val("").keyup().trigger("input");
        $("#item_sale_start_date_edit_item").val("");
        $("#item_sale_end_date_edit_item").val("");
    }

    $("#edit-item-save-btn").click(() => {
        let [updated_item_data, error_message] = get_catalogue_items_data("edit_item_modal");
        if (error_message && error_message != "") {
            showToast(error_message, 2000);
            return;
        }
        $("#edit-item-save-btn").css({
            "opacity": "0.5",
            "pointer-events": "none"
        })
        $(".save-note").css("display", "flex")
        $("#edit-item-save-btn").html(`Saving <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="animation: rotate 2s infinite">
        <path d="M20.946 12.9846C21.4949 13.0451 21.896 13.5408 21.7811 14.081C21.3316 16.1942 20.2069 18.1149 18.5634 19.5446C16.6673 21.1941 14.2196 22.0692 11.7075 21.9957C9.19542 21.9222 6.80309 20.9055 5.00668 19.148C3.21026 17.3904 2.14149 15.0209 2.01306 12.511C1.88464 10.0011 2.70599 7.53486 4.31364 5.60314C5.92129 3.67141 8.19735 2.41585 10.6888 2.08633C13.1803 1.75681 15.7045 2.3775 17.7591 3.82487C19.5399 5.07942 20.8548 6.87531 21.5176 8.93157C21.6871 9.45722 21.3387 9.99129 20.7988 10.1074V10.1074C20.2588 10.2236 19.7329 9.87693 19.5504 9.35569C19.002 7.78996 17.977 6.42479 16.6073 5.4599C14.9636 4.302 12.9443 3.80545 10.9511 4.06906C8.95788 4.33268 7.13703 5.33713 5.85091 6.88251C4.56479 8.42789 3.90771 10.4009 4.01045 12.4088C4.11319 14.4167 4.96821 16.3123 6.40534 17.7184C7.84247 19.1244 9.75633 19.9378 11.766 19.9966C13.7757 20.0554 15.7339 19.3553 17.2507 18.0357C18.5148 16.9361 19.3952 15.4734 19.7808 13.8599C19.9092 13.3227 20.397 12.9242 20.946 12.9846V12.9846Z" fill="white"/>
        </svg>`)
        let product_id = $("#item_being_edited").val().trim();
        if (product_id == "") {
            showToast("Please select a valid item to edit!", 2000);
            return;
        }
        let json_string = JSON.stringify({
            product_id: product_id,
            bot_id: BOT_ID,
            updated_item_data: updated_item_data
        })
        json_string = EncryptVariable(json_string);
        json_string = encodeURIComponent(json_string);
        let params = 'json_string=' + json_string
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/chat/channels/whatsapp/update-catalogue-product/", true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                $(".save-note").hide();
                if (response["status"] == 200) {
                    sync_products_from_facebook();
                    M.toast({
                        "html": "Item edited successfully!"
                    }, 2000);
                    $("#edit_item_modal").modal("close");
                    show_review_product_toast();
                    reset_add_item_modal();
                    $("#edit-item-save-btn").css({
                        "opacity": "1",
                        "pointer-events": "auto"
                    })
                    $("#edit-item-save-btn").html(`Save`)
                } else {
                    if ("message" in response) {
                        M.toast({
                            "html": response["message"]
                        }, 5000);
                    } else {
                        M.toast({
                            "html": "Error in editing item, please try again later."
                        }, 5000);
                    }
                    $("#edit-item-save-btn").css({
                        "opacity": "1",
                        "pointer-events": "auto"
                    })
                    $("#edit-item-save-btn").html(`Save`)
                    update_item_titles();
                }
            } else if (this.readyState == 4 && this.status != 200) {
                $(".save-note").hide();
                $("#sync_products_svg").css("animation", "none")
                $("#edit-item-save-btn").css({
                    "opacity": "1",
                    "pointer-events": "auto"
                })
                $("#edit-item-save-btn").html(`Save`)
                M.toast({
                    "html": "Error in editing item, please try again later."
                }, 2000);
            }
        }
        xhttp.send(params);
    })

    $("#fb_error_message_toast .error-toast-msg-close").click(() => {
        $("#fb_error_message_toast").hide();
    })

    $("#apply_catalogue_filter").click(() => {
        let currency = $('#price-list-dropdown').val();
        let availability = $('input[name="select_item_availability"]:checked').val();
        let gender = $('input[name="select_suitable_gender"]:checked').val();
        let condition = $('input[name="select_item_condition"]:checked').val();
        let price_from = $("#easychat-bot-range-min-selected-value").text();
        let price_to = $("#easychat-bot-range-max-selected-value").text();
        if(isNaN(price_from) || price_from.trim() == "") {
            showToast("Please enter a valid minimum price for price filter!")
            return;
        }
        if(isNaN(price_to || price_to.trim() == "")) {
            showToast("Please enter a valid maximum price for price filter!")
            return;
        }
        price_from = parseInt(price_from)
        price_to = parseInt(price_to)
        if (price_from > price_to) {
            showToast("Minimum price value cannot be greater than maximum price value!")
            return;
        }
        if (price_to > 10000000) {
            showToast("Maximum price value cannot be greater than 1,00,00,000!")
            return;   
        }
        if (price_from < 0) {
            showToast("Minimum price value cannot be smaller than 0!")
            return;   
        }
        let url_vars = get_url_multiple_vars();
        if (currency) {
            url_vars.currency = [currency];
        } 
        if (availability) {
            url_vars.availability = [availability];
        }
        if (gender) {
            url_vars.gender = [gender];
        }
        if (condition) {
            url_vars.condition = [condition];
        }
        if (price_from) {
            url_vars.price_from = [price_from];
        }
        if (price_to) {
            url_vars.price_to = [price_to];
        }
        window.ACTIVE_CATALOGUE_TABLE.update_url_with_filters(url_vars);
        window.ACTIVE_CATALOGUE_TABLE.fetch_catalogue_items();
        $("#filter_meta_data_modal").modal("close");
    })

    $("#clear_catalogue_filter").click(() => {
        let url_vars = get_url_multiple_vars();
        if ("availability" in url_vars) {
            delete url_vars.availability;
        }
        if ("gender" in url_vars) {
            delete url_vars.gender;
        }
        if ("condition" in url_vars) {
            delete url_vars.condition;
        }
        if ("currency" in url_vars) {
            delete url_vars.currency;
        }
        if ("price_from" in url_vars) {
            delete url_vars.price_from;
        }
        if ("price_to" in url_vars) {
            delete url_vars.price_to;
        }
        window.ACTIVE_CATALOGUE_TABLE.update_url_with_filters(url_vars);
        window.ACTIVE_CATALOGUE_TABLE.fetch_catalogue_items();
        $("#filter_meta_data_modal").modal("close");
        $('input[name="select_item_availability"], input[name="select_suitable_gender"], input[name="select_item_condition"]').prop("checked", false)
        $("#price-list-dropdown").val("all").change();
        $(".js-range-slider").data("ionRangeSlider").update({ from: 0 });
        $("#easychat-bot-range-min-selected-value").text($(".js-range-slider").data("ionRangeSlider").result.from)
        $(".js-range-slider").data("ionRangeSlider").update({ to: 10000000 });
        $("#easychat-bot-range-max-selected-value").text($(".js-range-slider").data("ionRangeSlider").result.to)
    })

    function populate_filter_selected_values() {
        let url_vars = get_url_vars();
        if ("availability" in url_vars) {
            $('input[name="select_item_availability"][value="' + url_vars.availability + '"]').prop("checked", true)
        }
        if ("gender" in url_vars) {
            $('input[name="select_suitable_gender"][value="' + url_vars.gender + '"]').prop("checked", true)
        }
        if ("condition" in url_vars) {
            $('input[name="select_item_condition"][value="' + url_vars.condition + '"]').prop("checked", true)
        }
        if ("currency" in url_vars) {
            $('input[name="select_currency_cb"][value="' + url_vars.currency + '"]').prop("checked", true)
        }
        if ("price_from" in url_vars) {
            $(".js-range-slider").data("ionRangeSlider").update({ from: url_vars.price_from });
            $("#easychat-bot-range-min-selected-value").text($(".js-range-slider").data("ionRangeSlider").result.from)
        }
        if ("price_to" in url_vars) {
            $(".js-range-slider").data("ionRangeSlider").update({ to: url_vars.price_to });
            $("#easychat-bot-range-max-selected-value").text($(".js-range-slider").data("ionRangeSlider").result.to)
        }

        if ("items_per_page" in url_vars && ["10", "25", "50", "75", "100"].includes(url_vars.items_per_page)) {
            $("#easychat_catalogue_table_row_dropdown option[value='" + url_vars.items_per_page + "']").prop("selected", true)
            $("#select2-easychat_catalogue_table_row_dropdown-container").text(url_vars.items_per_page)
        } else {
            $("#easychat_catalogue_table_row_dropdown option[value='25']").prop("selected", true)
            $("#select2-easychat_catalogue_table_row_dropdown-container").text("25")
        }
    }

    setTimeout(populate_filter_selected_values, 500);
    reset_add_item_modal();

    function track_sync_products_progress() {

        let json_string = JSON.stringify({
            bot_id: BOT_ID,
            event_type: 'sync_products',
        })
        $("#sync_products_svg").css("animation", "rotate 2s infinite");
        $("#sync_products_btn").css("pointer-events", "none");
        json_string = EncryptVariable(json_string)
        $.ajax({
            url: "/chat/bot/track-event-progress/",
            type: "POST",
            headers: {
                'X-CSRFToken': get_csrf_token()
            },
            data: {
                data: json_string,
            },
            success: function(response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);

                if (response.status == 200) {
                    let is_completed = response.is_completed;
                    let is_toast_displayed = response.is_toast_displayed;
                    let is_failed = response.is_failed;
                    let event_info = response.event_info;

                    if (is_failed && !is_toast_displayed) {
                        if ("message" in event_info) {
                            M.toast({
                                "html": event_info["message"]
                            }, 5000);
                        } else {
                            M.toast({
                                "html": "Error in Syncing products with Commerce Manager, please try again later."
                            }, 2000);
                        }
                        $("#sync_products_svg").css("animation", "none");
                        $("#sync_products_btn").css("pointer-events", "auto");
                        if (sync_products_timer) {
                            clearInterval(sync_products_timer);
                        }
                    } else if (is_completed && !is_toast_displayed) {
                        if ("status" in event_info && event_info.status != 200 && "message" in event_info) {
                            M.toast({
                                "html": event_info["message"]
                            }, 5000);
                        } else {
                            window.ACTIVE_CATALOGUE_TABLE.fetch_catalogue_items();
                            M.toast({
                                "html": "Products Synced Successfully"
                            }, 2000);
                        }
                        $("#sync_products_svg").css("animation", "none");
                        $("#sync_products_btn").css("pointer-events", "auto");
                        if (sync_products_timer) {
                            clearInterval(sync_products_timer);
                        }
                    } else if (is_completed && is_toast_displayed){
                        if (sync_products_timer) {
                            clearInterval(sync_products_timer);
                        }
                        $("#sync_products_svg").css("animation", "none");
                        $("#sync_products_btn").css("pointer-events", "auto");
                    }
                } else {
                    if (sync_products_timer) {
                        clearInterval(sync_products_timer);
                    }
                    $("#sync_products_svg").css("animation", "none");
                    $("#sync_products_btn").css("pointer-events", "auto");
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                $("#sync_products_svg").css("animation", "none");
                $("#sync_products_btn").css("pointer-events", "auto");
            }
        });
    }

    function track_upload_items_progress() {

        let json_string = JSON.stringify({
            bot_id: BOT_ID,
            event_type: 'upload_catalogue_products',
        })
        upload_items_in_progress = true;
        $("#download_template_btn").css("visibility", "hidden");
        $("#csv_uploading_container").css("display", "flex");
        $("#catalogue_items_uploading").get(0).play();
        $("#csv_drag_drop_container, #csv_items_failed_container, #view_report_btn, #no_products_error").hide();
        $("#upload_catalogue_csv").show();
        $("#upload_catalogue_csv").css({
            "pointer-events": "none",
            "opacity": "0.5"
        })
        json_string = EncryptVariable(json_string)
        $.ajax({
            url: "/chat/bot/track-event-progress/",
            type: "POST",
            headers: {
                'X-CSRFToken': get_csrf_token()
            },
            data: {
                data: json_string,
            },
            success: function(response) {
                response = custom_decrypt(response)
                response = JSON.parse(response);

                if (response.status == 200) {
                    let is_completed = response.is_completed;
                    let is_toast_displayed = response.is_toast_displayed;
                    let is_failed = response.is_failed;
                    let event_info = response.event_info;
                    let event_progress = response.event_progress;
                    $("#upload_catalogue_csv").text("Uploading " + event_progress.toFixed(2).toString() + "%");
                    if ("original_file_name" in event_info) {
                        $("#uploaded_file_name").text(event_info.original_file_name)
                    }
                    if ("products_limit_exceed" in event_info && event_info.products_limit_exceed) {
                        $("#products_limit_exceed").show();
                    }
                    if (is_failed && !is_toast_displayed) {
                        if ("message" in event_info) {
                            M.toast({
                                "html": event_info["message"]
                            }, 5000);
                        } else {
                            M.toast({
                                "html": "Error in uploading products via CSV, please try again later."
                            }, 2000);
                        }
                        $("#csv_items_failed_container, #csv_uploading_container, #view_report_btn, #products_limit_exceed, #no_products_error").hide();
                        $("#upload_catalogue_csv, #csv_drag_drop_container").show();
                        $("#download_template_btn").css("visibility", "visible");
                        $("#upload_catalogue_csv").text("Next");
                        check_upload_csv_button_condition();
                        if (upload_items_timer) {
                            clearInterval(upload_items_timer);
                            upload_items_in_progress = false;
                        }
                    } else if (is_completed && !is_toast_displayed) {
                        if ("status" in event_info && event_info.status == 201) {
                            $("#csv_items_failed_container").css("display", "flex");
                            $("#csv_drag_drop_container, #csv_uploading_container, #upload_catalogue_csv, .file-upload-success-container, .success-note-wrapper, #products_limit_exceed, #no_products_error").hide();
                            $("#download_template_btn").css("visibility", "hidden");
                            populate_items_report_modal(event_info);
                            $("#view_report_btn").show();
                            if(!("header_missing" in event_info.errors_map)) {
                                sync_products_from_facebook();
                            }
                        } else if ("status" in event_info && event_info.status == 200) {
                            sync_products_from_facebook();
                            $("#csv_uploaded_video").get(0).play();
                            $(".file-upload-success-container").css("display", "flex");
                            show_review_product_toast();
                            $(".success-note-wrapper").show();
                            $("#csv_drag_drop_container, #csv_uploading_container, #csv_items_failed_container, #view_report_btn, #upload_catalogue_csv, #products_limit_exceed, #no_products_error").hide();
                            $("#download_template_btn").css("visibility", "hidden");
                            $("#upload_catalogue_csv").text("Next");
                            check_upload_csv_button_condition();
                        } else if ("status" in event_info && event_info.status == 202) {
                            $("#csv_items_failed_container").css("display", "flex");
                            $("#csv_drag_drop_container, #csv_uploading_container, #upload_catalogue_csv, .file-upload-success-container, .success-note-wrapper, #products_limit_exceed").hide();
                            $("#download_template_btn").css("visibility", "hidden");
                            $("#no_products_error").show();
                            $("#failed_items_text").text("")
                        }
                        if (upload_items_timer) {
                            clearInterval(upload_items_timer);
                            upload_items_in_progress = false;
                        }

                    } else if (is_completed && is_toast_displayed){
                        $("#csv_uploading_container, #csv_items_failed_container, #view_report_btn, #products_limit_exceed, #no_products_error").hide();
                        $("#upload_catalogue_csv, #csv_drag_drop_container").show();
                        $("#download_template_btn").css("visibility", "visible");
                        $("#upload_catalogue_csv").text("Next");
                        check_upload_csv_button_condition();
                        if (upload_items_timer) {
                            clearInterval(upload_items_timer);
                            upload_items_in_progress = false;
                        }
                    }
                } else {
                    if (upload_items_timer) {
                        clearInterval(upload_items_timer);
                        upload_items_in_progress = false;
                    }
                    if (is_first_time_upload) {
                        $("#csv_drag_drop_container, #upload_catalogue_csv").show();
                        $("#download_template_btn").css("visibility", "visible");
                        $("#csv_uploading_container, #csv_items_failed_container, #view_report_btn, #products_limit_exceed").hide();
                        $("#upload_catalogue_csv").text("Next");
                        check_upload_csv_button_condition();
                        is_first_time_upload = false;
                    }
                }
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: " + errorthrown + xhr.status + xhr.responseText);
                $("#csv_uploading_container, #csv_items_failed_container, #view_report_btn, #products_limit_exceed").hide();
                $("#upload_catalogue_csv, #csv_drag_drop_container").show();
                $("#download_template_btn").css("visibility", "visible");
                $("#upload_catalogue_csv").text("Next");
                check_upload_csv_button_condition();
                if (upload_items_timer) {
                    clearInterval(upload_items_timer);
                    upload_items_in_progress = false;
                }
            }
        });
    }

    function check_upload_csv_button_condition() {
        let file_container_value = $("#upload-file-items").val();
        $("#upload_catalogue_csv").css({
            "pointer-events": file_container_value ? "auto" : "none",
            "opacity": file_container_value ? "1" : "0.5"
        })
    }

    function populate_items_report_modal(response) {
        let error_present_headers = response.error_present_headers
        let errors_map = response.errors_map
        let headers_index_map = response.headers_index_map
        $("#reports_modal_thead, #reports_modal_tbody").html("")
        let header_html = `<tr role="row"><th scope="col" style="background-color: white !important;width: 200px;" class="sorting_disabled" rowspan="1" colspan="1"><p>
        Row Number </p></th>`
        for (let header of error_present_headers) {
            header_html += `<th scope="col" style="background-color: white !important;width: 200px;" class="sorting_disabled" rowspan="1" colspan="1"><p>
            ${header} </p></th>`
        }
        header_html += `</tr>`;
        $("#reports_modal_thead").html(header_html);
        let validation_error_present = false;
        let fb_error_present = false;
        let facebook_error_tbody_html = "";
        let body_html = "";
        for (let error_item in errors_map) {
            if (error_item == "header_missing"){
                validation_error_present = true;
                continue;
            }
            if ("error_from_facebook" in errors_map[error_item]) {
                facebook_error_tbody_html += `<tr role="row" class="odd">
                                                <td data-content=" " data-toggle="tooltip" class="text-center" title="${error_item}">${error_item}</td>
                                                <td data-content=" " data-toggle="tooltip" title="${errors_map[error_item].error_from_facebook}">${errors_map[error_item].error_from_facebook}</td>
                                            </tr>`;
                fb_error_present = true;
                continue;
            }
            validation_error_present = true;
            body_html += `<tr role="row" class="odd"><td data-content=" " class="text-center" sdata-toggle="tooltip" title="${error_item}">${error_item}</td>`
            let item_details = errors_map[error_item].item_details
            for (let header of error_present_headers) {
                if (header == "header_missing") continue
                if(!(header in headers_index_map)) {
                    body_html += `<td data-content=" " class="error_msg_background-red" data-toggle="tooltip" title="Required header '${header}' is missing"></td>`
                }
                else {
                    let header_index = headers_index_map[header]
                    let td_class = "";
                    if ("error_mapping" in errors_map[error_item] && header_index in errors_map[error_item].error_mapping) {
                        if (item_details[header_index].trim() == "") {
                            td_class = "class='error_msg_background-red'";
                        } else {
                            td_class = "class='error_msg_background-yellow'";
                        }
                    }
                    let item_title = errors_map[error_item].error_mapping[header_index]
                    if (!item_title) {
                        item_title = item_details[header_index];
                    }
                    body_html += `<td data-content=" " ${td_class} data-toggle="tooltip" title="${item_title}">${item_details[header_index]}</td>`
                }
            }
            body_html += `</tr>`;
        }
        $("#reports_modal_tbody").html(body_html);
        $("#errors_from_facebook_tbody").html(facebook_error_tbody_html);
        $("#invalid_information_text").text("These fields have missing or invalid information: " + error_present_headers.join(", "))

        let total_items = response.total_items;
        let failed_items = Object.keys(errors_map).length
        if ("header_missing" in errors_map) {
            failed_items = total_items;
        }
        if(failed_items != total_items){
            show_review_product_toast()
        }else{
            hide_review_product_toast()
        }
        $("#failed_items_text").text(`${failed_items} item(s) not uploaded or added out of ${total_items} item(s) due to error.`)
        if (!validation_error_present) {
            $("#validation_error, #validation_error_div").hide();
            $(".missing-information-div").css("display", "flex");
        } else {
            $("#validation_error").click();
            $("#validation_error, #validation_error_div").show();
        }
        if (!fb_error_present) {
            $("#facebook_error, #facebook_error_div").hide();
        } else {
            $("#facebook_error").show();
        }
        if (fb_error_present && !validation_error_present) {
            $("#facebook_error").click();
            $(".missing-information-div").hide();
        }
    }

    let items_file_drag_drop_wrapper = $('#items-file-drag-drop');
    $(document).on("change", "#upload-file-items", function (e) {
        let file_name = e.target.files[0].name;
        let file_extension = file_name.split('.')
        file_extension = file_extension[file_extension.length - 1].toLowerCase();
        if (!(accepted_csv_types.includes(e.target.files[0].type) && file_extension == "csv")) {
            M.toast({
                "html": "Only CSV files are allowed"
            }, 2000);
            // if the file is not allowed then clear the value of the upload element
            e.target.value = "";
            return;
        }
        if (e.target.files[0].size > 5*1024*1024) {
            M.toast({
                "html": "File greater than 5 MB is not allowed!"
            }, 2000);
            e.target.value = "";
            return;
        }
        check_upload_csv_button_condition();
        let uploaded_item_file_name = $('#uploaded-item-file-name')
        let uploaded_file_data_container = $('.uploaded-file-data-container')
        items_file_drag_drop_wrapper.css('display', 'none');
        uploaded_file_data_container.css('display', 'flex');
        uploaded_item_file_name.text(file_name);
    })

    $(document).on("click", ".delete-items-file", function (e) {
        let uploaded_item_file_name = $('#uploaded-item-file-name')
        let uploaded_file_data_container = $('.uploaded-file-data-container')
        let items_file_input = $('#upload-file-items')
        items_file_drag_drop_wrapper.css('display', 'flex');
        uploaded_file_data_container.css('display', 'none');
        items_file_input.val('')
        $("#upload_catalogue_csv").css({
            "opacity": "0.5",
            "pointer-events": "none"
        })
        uploaded_item_file_name.html();
        document.getElementById("upload-image-for-item").value = "";
    })

    $("#upload_catalogue_csv").click(() => {
        let catalogue_csv_file = ($("#upload-file-items"))[0].files[0];
        if (!catalogue_csv_file) {
            M.toast({
                "html": "Please choose a file to upload"
            }, 2000);
            return;
        }
        let reader = new FileReader();
        reader.readAsDataURL(catalogue_csv_file);
        reader.onload = function () {

            let base64_str = reader.result.split(",")[1];

            let json_string = {
                "filename": catalogue_csv_file.name,
                "base64_file": base64_str,
                "bot_id": BOT_ID
            };
            json_string = JSON.stringify(json_string);
            json_string = EncryptVariable(json_string);
            json_string = encodeURIComponent(json_string);
            let params = 'json_string=' + json_string
            let xhttp = new XMLHttpRequest();
            xhttp.open("POST", "/chat/channels/whatsapp/upload-products-csv/", true);
            xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());

            xhttp.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {
                    let response = JSON.parse(this.responseText);
                    response = custom_decrypt(response);
                    response = JSON.parse(response);
                    if (response["status"] == 200) {
                        $("#csv_drag_drop_container").hide();
                        $("#csv_uploading_container").css("display", "flex");
                        $("#catalogue_items_uploading").get(0).play();
                        $("#csv_items_failed_container").hide();
                        $("#view_report_btn").hide();
                        $("#download_template_btn").css("visibility", "hidden");
                        $("#upload_catalogue_csv").show();
                        $("#upload_catalogue_csv").text("Uploading");
                        $("#upload_catalogue_csv").css({
                            "pointer-events": "none",
                            "opacity": "0.5"
                        })
                        $(".delete-items-file").click();
                        upload_items_in_progress = true;
                        upload_items_timer = setInterval(track_upload_items_progress, 3000);
                        setTimeout(track_upload_items_progress, 500)
                    } else {
                        if ("message" in response) {
                            M.toast({
                                "html": response["message"]
                            }, 5000);
                        }
                    }
                } else if (this.readyState == 4 && this.status != 200) {
                    M.toast({
                        "html": "Internal server error while uploading the file, please try again later"
                    }, 2000);
                }
            }
            xhttp.send(params);
        };

        reader.onerror = function (error) {
            M.toast({
                "html": "Error occured while reading the file, please make sure a valid CSV file is uploaded."
            }, 2000);
        };
    })

    $("#view_report_btn").click(() => {
        $("#report_details_page_modal").modal("open");
    })

    $("#upload_item_csv_modal_back, #upload_item_csv_modal_close, .upload-more-products").click(() => {
        if(upload_items_in_progress) {
            $("#csv_uploading_container").css("display", "flex");
            $("#catalogue_items_uploading").get(0).play();
            $("#csv_drag_drop_container, #csv_items_failed_container, #view_report_btn, .file-upload-success-container, .success-note-wrapper, #products_limit_exceed, #no_products_error").hide();
            $("#download_template_btn").css("visibility", "hidden");
            $("#upload_catalogue_csv").show();
            $("#upload_catalogue_csv").text("Uploading");
            $("#upload_catalogue_csv").css({
                "pointer-events": "none",
                "opacity": "0.5"
            })
            return;
        }
        $("#csv_items_failed_container, #csv_uploading_container, #view_report_btn, .file-upload-success-container, .success-note-wrapper, #no_products_error").hide();
        $("#csv_drag_drop_container, #upload_catalogue_csv").show();
        $("#download_template_btn").css("visibility", "visible");
        $("#upload_catalogue_csv").text("Next");
        check_upload_csv_button_condition();
    })
    let currency_options_html = ''
    for (currency in CURRENCY_NAME_MAP) {
        let currency_name = currency + " - " + CURRENCY_NAME_MAP[currency]
        currency_options_html += `<option value="${currency}">${currency_name}</option>`
    }
    $("#price-list-dropdown").append(currency_options_html)

    $("#validation_error").click(() => {
        $("#validation_error_div").show();
        $("#facebook_error_div").hide();
        $("#validation_error").addClass("active-btn")
        $("#facebook_error").removeClass("active-btn")
    })
    $("#facebook_error").click(() => {
        $("#validation_error_div").hide();
        $("#facebook_error_div").show();
        $("#validation_error").removeClass("active-btn")
        $("#facebook_error").addClass("active-btn")
    })

    function get_currency_dropdown_options() {
        let dropdown_html = "";
        for (const currency in CURRENCY_NAME_MAP) {
            dropdown_html += `<li class="dropdown__list-item" data-value="${currency}"><span>${currency}</span></li>`
        }
        return dropdown_html;
    }

    $("#download_template_btn").click(() => {
        let xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/chat/channels/whatsapp/download-catalogue-csv-template", true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    if (response.export_path_exist) {
                        window.open(response.export_path, "_self");
                    } else {
                        showToast("Unable to download Catalogue CSV Template, please try again later.", 3000)
                    }
                } else {
                    showToast("Unable to download Catalogue CSV Template, please try again later.", 3000)
                }
            } else if (this.readyState == 4 && this.status != 200) {
                showToast("Unable to download Catalogue CSV Template, please try again later.", 3000)
            }
        }
        xhttp.send();
    })
    $("#close_product_note").click(() => {
        $("#sync_product_note").hide();
    })
});

const debounce = (func, delay = 500) => {
    let clearTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(clearTimer);
        clearTimer = setTimeout(() => func.apply(context, args), delay);
    }
}

const search_catalogue_items = debounce(function() {
    window.ACTIVE_CATALOGUE_TABLE.fetch_catalogue_items();
})

function append_multi_bot_range_slider(range_slider_list) {
    if (range_slider_list.length > 0) {
        easychat_range_slider_container = document.getElementById("easychat-bot-multi-range-slider");
        if (easychat_range_slider_container != undefined && easychat_range_slider_container != null) {
            easychat_range_slider_container.remove();
        }
        let range_slider = range_slider_list[0];
        let range_slider_html = '<div class="easychat-range-slider-wrapper" id="easychat-bot-multi-range-slider"><div class="easychat-bot-range-slider-div">\
                \
                <div class="easychat-bot-range-slider-area" style="margin-bottom: 28px; margin-top:0px;">\
                    <input type="text" class="js-range-slider" name="my_range" value="" data-skin="round" data-type="double" data-min="' + range_slider["min"] + '" data-max="' + range_slider["max"] + '" data-grid="false" />\
                    <div id="multi-range-slider-min-max-static-value"><div style="padding-left: 3px;">' + range_slider["min"] + '</div><div style="padding-right: 3px;">1,00,00,000</div></div>\
                    <input type="text" maxlength="1" value="' + range_slider["min"] + '" class="from dual-range-min-value" id="multi-range-slider-min-val" readonly oninput="change_multi_range_min_value()" style="display: none" />\
                    <input type="text" maxlength="1" value="' + range_slider["max"] + '" class="to dual-range-max-value" id="multi-range-slider-max-val" readonly oninput="change_multi_range_max_value()" style="display: none" />\
                </div>\
                <div class="easychat-bot-range-min-max-value-wrapper">\
                    <div class="easychat-bot-range-min-value-div">\
                        <div contenteditable="true" class="easychat-bot-range-min-inner-value" id="easychat-bot-range-min-selected-value" >\
                            12000\
                        </div>\
                        <p>Minimum value</p>\
                    </div>\
                    <svg width="9" height="2" viewBox="0 0 9 2" fill="none" xmlns="http://www.w3.org/2000/svg">\
                        <path d="M0 0.905273H9" stroke="#8F8F8F"/>\
                        </svg>\
                    <div class="easychat-bot-range-max-value-div">\
                        <div contenteditable="true" class="easychat-bot-range-max-inner-value" id="easychat-bot-range-max-selected-value" >\
                            1023400\
                        </div>\
                        <p>Maximum value</p>\
                    </div>\
                </div></div>'

        document.getElementById("easychat-chat-container").innerHTML += range_slider_html;
        element_response = document.querySelectorAll(".easychat-bot-range-slider-div")
        // element_response_previous_height += element_response[element_response.length - 1].clientHeight

        let multi_range_min_slider = document.getElementById("multi-range-slider-min-val");
        let multi_range_max_slider = document.getElementById("multi-range-slider-max-val");
        document.getElementById("easychat-bot-range-min-selected-value").innerHTML = multi_range_min_slider.value;
        document.getElementById("easychat-bot-range-max-selected-value").innerHTML = multi_range_max_slider.value;

        setTimeout(function () {
            $(".js-range-slider").ionRangeSlider({
                onChange: function (data) {
                    slider_from = data.from;
                    slider_to = data.to;
                    update_slider_values();
                }
            });
        }, 100);

        // disable_user_input();
    }
    $("#easychat-bot-range-min-selected-value, #easychat-bot-range-max-selected-value").keypress(function(e) {
        let x = event.charCode || event.keyCode;
        if (isNaN(String.fromCharCode(e.which)) && x!=46 || x===32 || x===13 || (x===46)) e.preventDefault();
    });

    $("#easychat-bot-range-min-selected-value").on('input', function(e) {
        $(".js-range-slider").data("ionRangeSlider").update({ from: $("#easychat-bot-range-min-selected-value").text() });
    });

    $("#easychat-bot-range-max-selected-value").on('input', function(e) {
        $(".js-range-slider").data("ionRangeSlider").update({ to: $("#easychat-bot-range-max-selected-value").text() });
    });
}

var update_slider_values = function () {
    $(".from").prop("value", slider_from);
    $(".to").prop("value", slider_to);

    if (document.getElementsByTagName("body")[0].classList.contains("language-right-to-left-wrapper")) {
        let min_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value").children[0].innerText);
        let max_value = parseInt(document.getElementById("multi-range-slider-min-max-static-value").children[1].innerText);
        let span_length = max_value - min_value;

        // Calculate distance of max value from right end
        document.getElementById("easychat-bot-range-max-selected-value").innerHTML = Math.round((1 - ((slider_from - min_value) / span_length)) * span_length + min_value);

        // Calculate distance of min value from left end
        document.getElementById("easychat-bot-range-min-selected-value").innerHTML = Math.round((1 - ((slider_to - min_value) / span_length)) * span_length + min_value);
    } else {
        document.getElementById("easychat-bot-range-min-selected-value").innerHTML = document.getElementById("multi-range-slider-min-val").value;
        document.getElementById("easychat-bot-range-max-selected-value").innerHTML = document.getElementById("multi-range-slider-max-val").value;
    }
};

$(document).on("click", ".accordion__header", function (e) {
    let current_is_active = $(this).hasClass("is-active");
    $(this).parentsUntil(".accordion-wrapper").find("> *").removeClass("is-active");
    if (current_is_active != 1) {
        $(this).addClass("is-active");
        $(this).next(".accordion__body").addClass("is-active");
    }
});

$(document).on("click", ".custom_dropdown", function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (!$(this).hasClass("dropdown__list_visible")) {
        $(".custom_dropdown.dropdown__list_visible").removeClass("dropdown__list_visible");
    }
    $(this).toggleClass("dropdown__list_visible");
})

$(document).on("click", ".dropdown__list > li", function (e) {
    e.preventDefault();
    e.stopPropagation();
    if($(this).hasClass('dropdown-filter')){
        return;
    }
    let element_text = $(this).text();
    let dropdown_list = $(this).closest('.custom_dropdown');
    let dropdown_button = $(this).closest('.custom_dropdown').children('.dropdown__button').children('span');
    dropdown_button.html(element_text);
    dropdown_list.removeClass('dropdown__list_visible');
})

$(document).on('click', function (e) {
    if (!$(e.target).hasClass('dropdown__list_visible')) {
        $('.custom_dropdown').removeClass('dropdown__list_visible')
    }
})

function check_img_cross_icon_condition(element_id) {
    let image_urls_input_length = $("#accordion-header-wrapper-" + element_id + " .additional-image-url-input").length
    if (image_urls_input_length < 2) {
        $("#accordion-header-wrapper-" + element_id + " .remove-img").hide();
    }
    if (image_urls_input_length > 1) {
        $("#accordion-header-wrapper-" + element_id + " .remove-img").show();
    }
}

function add_more_image_link(element, unique_element_id) {
    let image_link_parent_div = $(element).parent().next('.multiple-img-link-wrapper-div');
    $(create_image_link_input(unique_element_id)).appendTo(image_link_parent_div);
    $('.remove-img').click((event) => {
        $(event.target).closest('.img-variant-input').remove();
        check_img_cross_icon_condition(unique_element_id);
        if ($("#accordion-header-wrapper-" + unique_element_id + " .additional-image-url-input").length < 2) {
            $("#accordion-header-wrapper-" + unique_element_id + " .remove-img").hide();
        }
    })
    check_img_cross_icon_condition(unique_element_id);
    if ($("#accordion-header-wrapper-" + unique_element_id + " .additional-image-url-input").length > 1) {
        $("#accordion-header-wrapper-" + unique_element_id + " .remove-img").show();
    }
    $(image_link_parent_div).sortable({
        connectWith: ".multiple-img-link-div-wrapper",
        containment: "window",
        handle: '.drag-drop-img-link'
    });
}

function open_preview_url(url_element) {
    let preview_url = $(url_element).prev('.additional-image-url-input').val().trim();
    if(isValidURL(preview_url)) {
        let other_window_opener = window.open();
        other_window_opener.opener = null;
        other_window_opener.location = preview_url;
    } else {
        showToast("Not a valid URL to open!", 3000)
    }
}

function create_image_link_input(unique_element_id) {

    let image_link_input =`<div class="img-variant-input additional-image-url additional-close-img-wrapper" type="text" placeholder="https://www.example.com/item"
    style="color: #0254d7" />
    <div class="drag-drop-img-link-wrapper">
    <div class="drag-drop-img-link">
    <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12.7708 14.4583C13.4266 14.4583 13.9583 14.99 13.9583 15.6458C13.9583 16.3017 13.4266 16.8333 12.7708 16.8333C12.115 16.8333 11.5833 16.3017 11.5833 15.6458C11.5833 14.99 12.115 14.4583 12.7708 14.4583ZM7.22913 14.4583C7.88496 14.4583 8.41663 14.99 8.41663 15.6458C8.41663 16.3017 7.88496 16.8333 7.22913 16.8333C6.57329 16.8333 6.04163 16.3017 6.04163 15.6458C6.04163 14.99 6.57329 14.4583 7.22913 14.4583ZM12.7708 8.91667C13.4266 8.91667 13.9583 9.44833 13.9583 10.1042C13.9583 10.76 13.4266 11.2917 12.7708 11.2917C12.115 11.2917 11.5833 10.76 11.5833 10.1042C11.5833 9.44833 12.115 8.91667 12.7708 8.91667ZM7.22913 8.91667C7.88496 8.91667 8.41663 9.44833 8.41663 10.1042C8.41663 10.76 7.88496 11.2917 7.22913 11.2917C6.57329 11.2917 6.04163 10.76 6.04163 10.1042C6.04163 9.44833 6.57329 8.91667 7.22913 8.91667ZM12.7708 3.375C13.4266 3.375 13.9583 3.90666 13.9583 4.5625C13.9583 5.21834 13.4266 5.75 12.7708 5.75C12.115 5.75 11.5833 5.21834 11.5833 4.5625C11.5833 3.90666 12.115 3.375 12.7708 3.375ZM7.22913 3.375C7.88496 3.375 8.41663 3.90666 8.41663 4.5625C8.41663 5.21834 7.88496 5.75 7.22913 5.75C6.57329 5.75 6.04163 5.21834 6.04163 4.5625C6.04163 3.90666 6.57329 3.375 7.22913 3.375Z" fill="#212121"/>
      </svg>
    </div>
    <input class="additional-image-url-input image-upload-url url-input-box" type="text" placeholder="https://www.example.com/item" style="color: #0254d7">
    <a href="javascript:void(0)" onclick=open_preview_url(this) class="drag-drop-link-div">
    <svg width="19" height="20" viewBox="0 0 19 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <mask id="path-1-inside-1_620_11914-${unique_element_id}" fill="white">
    <path d="M6.23973 4.56251H9.01008C9.338 4.56251 9.60383 4.82834 9.60383 5.15626C9.60383 5.45685 9.38046 5.70527 9.09065 5.74459L9.01008 5.75001H6.23945C5.30612 5.74957 4.54034 6.46757 4.46463 7.3816L4.45863 7.5074L4.46088 14.2608C4.46112 15.2036 5.19375 15.9751 6.12064 16.0375L6.24259 16.0416L12.9702 16.0324C13.9121 16.0311 14.6824 15.299 14.7449 14.373L14.749 14.2511V11.4753C14.749 11.1474 15.0149 10.8815 15.3428 10.8815C15.6434 10.8815 15.8918 11.1049 15.9311 11.3947L15.9365 11.4753V14.2511C15.9365 15.8363 14.6941 17.1316 13.1294 17.2155L12.9719 17.2199L6.2462 17.2291L6.08524 17.225C4.57113 17.1462 3.35716 15.9329 3.27753 14.4188L3.27338 14.2611L3.27161 7.53327L3.2751 7.37295C3.35434 5.85872 4.56819 4.6451 6.08209 4.56655L6.23973 4.56251H9.01008H6.23973ZM11.384 3.37604L16.5723 3.37644L16.6512 3.38734L16.731 3.40966L16.776 3.42874C16.8181 3.44709 16.8586 3.47117 16.8963 3.50063L16.9512 3.55028L17.0175 3.62832L17.0604 3.69966L17.091 3.77116L17.1063 3.82198L17.117 3.87254L17.1244 3.94711L17.1248 9.1187C17.1248 9.44662 16.859 9.71245 16.531 9.71245C16.2305 9.71245 15.982 9.48908 15.9427 9.19927L15.9373 9.1187L15.9367 5.4027L10.2215 11.1211C10.0107 11.3319 9.68086 11.3512 9.44838 11.1788L9.38178 11.1213C9.17093 10.9105 9.1517 10.5807 9.32411 10.3482L9.38159 10.2816L15.0959 4.56354H11.384C11.0834 4.56354 10.835 4.34017 10.7957 4.05036L10.7903 3.96979C10.7903 3.6692 11.0136 3.42077 11.3034 3.38146L11.384 3.37604Z"/>
    </mask>
    <path d="M6.23973 4.56251V3.37501H6.22451L6.20929 3.3754L6.23973 4.56251ZM9.09065 5.74459L9.17036 6.92941L9.21046 6.92671L9.25028 6.92131L9.09065 5.74459ZM9.01008 5.75001V6.93751H9.04998L9.08979 6.93483L9.01008 5.75001ZM6.23945 5.75001L6.23888 6.93751H6.23945V5.75001ZM4.46463 7.3816L3.28118 7.28357L3.27947 7.30428L3.27848 7.32504L4.46463 7.3816ZM4.45863 7.5074L3.27248 7.45085L3.27112 7.47931L3.27113 7.5078L4.45863 7.5074ZM4.46088 14.2608L5.64838 14.2605V14.2604L4.46088 14.2608ZM6.12064 16.0375L6.04084 17.2223L6.06088 17.2237L6.08096 17.2244L6.12064 16.0375ZM6.24259 16.0416L6.20292 17.2284L6.22357 17.2291L6.24423 17.2291L6.24259 16.0416ZM12.9702 16.0324L12.9719 17.2199L12.9702 16.0324ZM14.7449 14.373L15.9297 14.453L15.9311 14.433L15.9318 14.4129L14.7449 14.373ZM14.749 14.2511L15.9359 14.2911L15.9365 14.2711V14.2511H14.749ZM15.9311 11.3947L17.1159 11.315L17.1132 11.2749L17.1078 11.2351L15.9311 11.3947ZM15.9365 11.4753H17.124V11.4354L17.1214 11.3956L15.9365 11.4753ZM13.1294 17.2155L13.162 18.4026L13.1775 18.4022L13.193 18.4013L13.1294 17.2155ZM12.9719 17.2199L12.9735 18.4074L12.989 18.4073L13.0044 18.4069L12.9719 17.2199ZM6.2462 17.2291L6.21618 18.4162L6.232 18.4166L6.24783 18.4166L6.2462 17.2291ZM6.08524 17.225L6.0235 18.4109L6.03935 18.4117L6.05521 18.4121L6.08524 17.225ZM3.27753 14.4188L2.09044 14.4501L2.09085 14.4656L2.09167 14.4812L3.27753 14.4188ZM3.27338 14.2611L2.08588 14.2614L2.08588 14.2769L2.08629 14.2924L3.27338 14.2611ZM3.27161 7.53327L2.08439 7.50742L2.0841 7.5205L2.08411 7.53358L3.27161 7.53327ZM3.2751 7.37295L2.08922 7.3109L2.08827 7.32899L2.08788 7.3471L3.2751 7.37295ZM6.08209 4.56655L6.05165 3.37944L6.03609 3.37984L6.02056 3.38065L6.08209 4.56655ZM11.384 3.37604L11.3841 2.18854L11.3442 2.18853L11.3043 2.19122L11.384 3.37604ZM16.5723 3.37644L16.735 2.20014L16.6541 2.18895L16.5724 2.18894L16.5723 3.37644ZM16.6512 3.38734L16.9709 2.2437L16.8935 2.22206L16.8139 2.21104L16.6512 3.38734ZM16.731 3.40966L17.1947 2.31645L17.1243 2.2866L17.0507 2.26601L16.731 3.40966ZM16.776 3.42874L17.25 2.33992L17.2397 2.33553L16.776 3.42874ZM16.8963 3.50063L17.6929 2.61989L17.6609 2.59097L17.6269 2.56444L16.8963 3.50063ZM16.9512 3.55028L17.8563 2.78147L17.8057 2.72193L17.7477 2.66953L16.9512 3.55028ZM17.0175 3.62832L18.0353 3.01646L17.9853 2.93339L17.9226 2.85951L17.0175 3.62832ZM17.0604 3.69966L18.152 3.23201L18.12 3.15738L18.0781 3.0878L17.0604 3.69966ZM17.091 3.77116L18.2287 3.43074L18.2093 3.36581L18.1826 3.30351L17.091 3.77116ZM17.1063 3.82198L18.2678 3.57521L18.2578 3.5279L18.2439 3.48156L17.1063 3.82198ZM17.117 3.87254L18.2987 3.75511L18.2922 3.68988L18.2786 3.62576L17.117 3.87254ZM17.1244 3.94711L18.3119 3.94702L18.3119 3.88821L18.3061 3.82968L17.1244 3.94711ZM17.1248 9.1187H18.3123V9.11861L17.1248 9.1187ZM15.9427 9.19927L14.7579 9.27899L14.7606 9.31908L14.766 9.35891L15.9427 9.19927ZM15.9373 9.1187L14.7498 9.1189L14.7498 9.1587L14.7525 9.19842L15.9373 9.1187ZM15.9367 5.4027L17.1242 5.40251L17.1237 2.53517L15.0968 4.56325L15.9367 5.4027ZM10.2215 11.1211L11.0613 11.9606L11.0614 11.9605L10.2215 11.1211ZM9.44838 11.1788L8.67259 12.0778L8.70579 12.1065L8.741 12.1326L9.44838 11.1788ZM9.38178 11.1213L8.54228 11.9612L8.57305 11.9919L8.60599 12.0203L9.38178 11.1213ZM9.32411 10.3482L8.42505 9.57241L8.39641 9.6056L8.37029 9.64082L9.32411 10.3482ZM9.38159 10.2816L8.54162 9.44217L8.51091 9.4729L8.48253 9.5058L9.38159 10.2816ZM15.0959 4.56354L15.9359 5.40296L17.9615 3.37604H15.0959V4.56354ZM10.7957 4.05036L9.61085 4.13006L9.61355 4.17016L9.61895 4.20999L10.7957 4.05036ZM10.7903 3.96979H9.60275V4.00969L9.60543 4.04949L10.7903 3.96979ZM11.3034 3.38146L11.2237 2.19664L11.1836 2.19933L11.1438 2.20474L11.3034 3.38146ZM6.23973 5.75001H9.01008V3.37501H6.23973V5.75001ZM9.01008 5.75001C8.68216 5.75001 8.41633 5.48418 8.41633 5.15626H10.7913C10.7913 4.17251 9.99384 3.37501 9.01008 3.37501V5.75001ZM8.41633 5.15626C8.41633 4.8547 8.64004 4.60734 8.93101 4.56787L9.25028 6.92131C10.1209 6.80321 10.7913 6.05901 10.7913 5.15626H8.41633ZM9.01094 4.55977L8.93037 4.56519L9.08979 6.93483L9.17036 6.92941L9.01094 4.55977ZM9.01008 4.56251H6.23945V6.93751H9.01008V4.56251ZM6.24001 4.56251C4.68321 4.56177 3.40746 5.75902 3.28118 7.28357L5.64807 7.47962C5.67321 7.17613 5.92902 6.93736 6.23888 6.93751L6.24001 4.56251ZM3.27848 7.32504L3.27248 7.45085L5.64478 7.56395L5.65078 7.43815L3.27848 7.32504ZM3.27113 7.5078L3.27338 14.2612L5.64838 14.2604L5.64613 7.50701L3.27113 7.5078ZM3.27338 14.2611C3.27379 15.8329 4.49487 17.1182 6.04084 17.2223L6.20044 14.8527C5.89263 14.832 5.64846 14.5743 5.64838 14.2605L3.27338 14.2611ZM6.08096 17.2244L6.20292 17.2284L6.28227 14.8548L6.16031 14.8507L6.08096 17.2244ZM6.24423 17.2291L12.9719 17.2199L12.9686 14.8449L6.24096 14.8541L6.24423 17.2291ZM12.9719 17.2199C14.5421 17.2177 15.8254 15.9975 15.9297 14.453L13.5601 14.2929C13.5394 14.6004 13.2821 14.8444 12.9686 14.8449L12.9719 17.2199ZM15.9318 14.4129L15.9359 14.2911L13.5622 14.2112L13.5581 14.333L15.9318 14.4129ZM15.9365 14.2511V11.4753H13.5615V14.2511H15.9365ZM15.9365 11.4753C15.9365 11.8032 15.6707 12.069 15.3428 12.069V9.69405C14.359 9.69405 13.5615 10.4915 13.5615 11.4753H15.9365ZM15.3428 12.069C15.0412 12.069 14.7939 11.8453 14.7544 11.5544L17.1078 11.2351C16.9897 10.3645 16.2455 9.69405 15.3428 9.69405V12.069ZM14.7463 11.4745L14.7517 11.555L17.1214 11.3956L17.1159 11.315L14.7463 11.4745ZM14.749 11.4753V14.2511H17.124V11.4753H14.749ZM14.749 14.2511C14.749 15.2018 14.0036 15.9794 13.0657 16.0297L13.193 18.4013C15.3846 18.2837 17.124 16.4707 17.124 14.2511H14.749ZM13.0968 16.0285L12.9393 16.0328L13.0044 18.4069L13.162 18.4026L13.0968 16.0285ZM12.9702 16.0324L6.24457 16.0416L6.24783 18.4166L12.9735 18.4074L12.9702 16.0324ZM6.27623 16.042L6.11526 16.0379L6.05521 18.4121L6.21618 18.4162L6.27623 16.042ZM6.14698 16.0391C5.23991 15.9919 4.5111 15.2635 4.46339 14.3564L2.09167 14.4812C2.20322 16.6023 3.90235 18.3005 6.0235 18.4109L6.14698 16.0391ZM4.46462 14.3875L4.46046 14.2298L2.08629 14.2924L2.09044 14.4501L4.46462 14.3875ZM4.46088 14.2608L4.45911 7.53295L2.08411 7.53358L2.08588 14.2614L4.46088 14.2608ZM4.45882 7.55912L4.46232 7.39881L2.08788 7.3471L2.08439 7.50742L4.45882 7.55912ZM4.46097 7.43501C4.50845 6.52774 5.23722 5.79948 6.14361 5.75246L6.02056 3.38065C3.89916 3.49071 2.20022 5.1897 2.08922 7.3109L4.46097 7.43501ZM6.11252 5.75366L6.27017 5.74962L6.20929 3.3754L6.05165 3.37944L6.11252 5.75366ZM6.23973 5.75001H9.01008V3.37501H6.23973V5.75001ZM9.01008 3.37501H6.23973V5.75001H9.01008V3.37501ZM11.3839 4.56354L16.5722 4.56394L16.5724 2.18894L11.3841 2.18854L11.3839 4.56354ZM16.4096 4.55274L16.4885 4.56365L16.8139 2.21104L16.735 2.20014L16.4096 4.55274ZM16.3314 4.53098L16.4112 4.5533L17.0507 2.26601L16.9709 2.2437L16.3314 4.53098ZM16.2672 4.50286L16.3122 4.52194L17.2397 2.33553L17.1947 2.31645L16.2672 4.50286ZM16.3019 4.51751C16.2506 4.49517 16.2051 4.46752 16.1658 4.43682L17.6269 2.56444C17.512 2.47482 17.3856 2.39902 17.25 2.33997L16.3019 4.51751ZM16.0998 4.38138L16.1547 4.43102L17.7477 2.66953L17.6929 2.61989L16.0998 4.38138ZM16.0462 4.31909L16.1125 4.39714L17.9226 2.85951L17.8563 2.78147L16.0462 4.31909ZM15.9998 4.24018L16.0427 4.31152L18.0781 3.0878L18.0353 3.01646L15.9998 4.24018ZM15.9689 4.16732L15.9995 4.23881L18.1826 3.30351L18.152 3.23201L15.9689 4.16732ZM15.9534 4.11158L15.9686 4.1624L18.2439 3.48156L18.2287 3.43074L15.9534 4.11158ZM15.9447 4.06876L15.9554 4.11931L18.2786 3.62576L18.2678 3.57521L15.9447 4.06876ZM15.9353 3.98997L15.9427 4.06454L18.3061 3.82968L18.2987 3.75511L15.9353 3.98997ZM15.9369 3.9472L15.9373 9.11879L18.3123 9.11861L18.3119 3.94702L15.9369 3.9472ZM15.9373 9.1187C15.9373 8.79078 16.2031 8.52495 16.531 8.52495V10.9C17.5148 10.9 18.3123 10.1025 18.3123 9.1187H15.9373ZM16.531 8.52495C16.8326 8.52495 17.08 8.74867 17.1194 9.03963L14.766 9.35891C14.8841 10.2295 15.6283 10.9 16.531 10.9V8.52495ZM17.1275 9.11955L17.1221 9.03898L14.7525 9.19842L14.7579 9.27899L17.1275 9.11955ZM17.1248 9.11851L17.1242 5.40251L14.7492 5.4029L14.7498 9.1189L17.1248 9.11851ZM15.0968 4.56325L9.38154 10.2816L11.0614 11.9605L16.7766 6.24216L15.0968 4.56325ZM9.38159 10.2816C9.59308 10.07 9.92241 10.0519 10.1558 10.2249L8.741 12.1326C9.43932 12.6505 10.4284 12.5939 11.0613 11.9606L9.38159 10.2816ZM10.2242 10.2797L10.1576 10.2222L8.60599 12.0203L8.67259 12.0778L10.2242 10.2797ZM10.2213 10.2814C10.4329 10.4929 10.451 10.8222 10.2779 11.0556L8.37029 9.64082C7.8524 10.3391 7.909 11.3282 8.54228 11.9612L10.2213 10.2814ZM10.2232 11.124L10.2806 11.0574L8.48253 9.5058L8.42505 9.57241L10.2232 11.124ZM10.2215 11.121L15.9359 5.40296L14.256 3.72412L8.54162 9.44217L10.2215 11.121ZM15.0959 3.37604H11.384V5.75104H15.0959V3.37604ZM11.384 3.37604C11.6856 3.37604 11.9329 3.59975 11.9724 3.89072L9.61895 4.20999C9.73706 5.08058 10.4813 5.75104 11.384 5.75104V3.37604ZM11.9805 3.97065L11.9751 3.89008L9.60543 4.04949L9.61085 4.13006L11.9805 3.97065ZM11.9778 3.96979C11.9778 4.27135 11.754 4.51871 11.4631 4.55818L11.1438 2.20474C10.2732 2.32284 9.60275 3.06704 9.60275 3.96979H11.9778ZM11.3831 4.56628L11.4637 4.56086L11.3043 2.19122L11.2237 2.19664L11.3831 4.56628Z" fill="#404040" mask="url(#path-1-inside-1_620_11914-${unique_element_id})"/>
    </svg>
    </a>
    </div>
    <span class="remove-img c-pointer">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3.11499 3L8.8849 9" stroke="#4D4D4D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8.88501 3L3.1151 9" stroke="#4D4D4D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
  </div>`
    return image_link_input;
}

class CatalogueBase {
    update_table_attribute(table_elements) {
        for (var idx = 0; idx < table_elements.length; idx++) {
            var table_el = table_elements[idx];
            var thead_el = table_elements[idx].getElementsByTagName('thead');
            if (thead_el.length == 0) {
                continue;
            }
            thead_el = thead_el[0];
            var tbody_el = table_elements[idx].getElementsByTagName('tbody');
            if (tbody_el.length == 0) {
                continue;
            }

            tbody_el = tbody_el[0];
            for (var row_index = 0; row_index < tbody_el.rows.length; row_index++) {
                if (tbody_el.rows[row_index].children.length != thead_el.rows[0].children.length) {
                    continue;
                }
                for (var col_index = 0; col_index < tbody_el.rows[row_index].children.length; col_index++) {
                    var column_element = tbody_el.rows[row_index].children[col_index];
                    var th_text = thead_el.rows[0].children[col_index].innerText;
                    column_element.setAttribute("data-content", th_text);
                }
            }
        }
    }

    apply_pagination(pagination_container, pagination_metadata, onclick_handler, target_obj) {
        let metadata = pagination_metadata;
        let html = "";

        let filter_default_text = "Showing " + metadata.start_point + " to " + metadata.end_point + " of " + metadata.total_count + " entries";

        if (metadata.has_previous) {
            html += [
                '<li class="page-item">',
                '<a class="page-link previous_button" data-page="' + metadata.previous_page_number + '" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Previous</span>',
                '<span class="sr-only">Previous</span>',
                '</a>',
                '</li>'
            ].join('');
        } else {
            html += [
                '<li class="page-item disabled">',
                '<a class="page-link previous_button" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Previous</span>',
                '<span class="sr-only">Previous</span>',
                '</a>',
                '</li>'
            ].join('');
        }

        if ((metadata.number - 4) > 1) {
            html += '<li class="page-item"><a class="page-link" data-page="' + (metadata.number - 5) + '" href="javascript:void(0)">&hellip;</a></li>';
        }

        for (var index = metadata.page_range[0]; index < metadata.page_range[1]; index++) {
            if (metadata.number == index) {
                html += [
                    '<li class="page-item">',
                    '<a data-page="' + index + '" href="javascript:void(0)" class="active page-link">' + index + '</a>',
                    '</li>',
                ].join('');
            } else if (index > (metadata.number - 5) && index < (metadata.number + 5)) {
                html += [
                    '<li class="page-item">',
                    '<a href="javascript:void(0)" data-page="' + index + '" class="page-link">' + index + '</a>',
                    '</li>',
                ].join('');
            }
        }

        if (metadata.num_pages > (metadata.number + 4)) {
            html += [
                '<li class="page-item">',
                '<a href="javascript:void(0)" data-page="' + (metadata.number + 5) + '" class="page-link">&hellip;</a>',
                '</li>',
            ].join('');
        }

        if (metadata.has_next) {
            html += [
                '<li class="page-item">',
                '<a class="page-link next_button" data-page="' + metadata.next_page_number + '" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Next</span>',
                '<span class="sr-only">Next</span>',
                '</a>',
                '</li>'
            ].join('');
        } else {
            html += [
                '<li class="page-item disabled">',
                '<a class="page-link next_button" href="javascript:void(0)" aria-label="Previous">',
                '<span aria-hidden="true">Next</span>',
                '<span class="sr-only">Next</span>',
                '</a>',
                '</li>'
            ].join('');
        }

        html = [
            '<div class="col-md-6 col-sm-12 show-pagination-entry-container dataTables_info" filter_default_text=\'' + filter_default_text + '\'>',
            filter_default_text,
            '</div>',
            '<div class="col-md-6 col-sm-12">',
            '<div class="d-flex justify-content-end">',
            '<nav aria-label="Page navigation example">',
            '<ul class="pagination">',
            html,
            '</ul>',
            '</nav>',
            '</div>',
            '</div>',
        ].join('');

        pagination_container.innerHTML = html;

        let pagination_links = pagination_container.querySelectorAll('a.page-link');

        pagination_links.forEach((pagination_link_element) => {
            let page_number = pagination_link_element.getAttribute('data-page');
            if (page_number != null && page_number != undefined) {
                pagination_link_element.addEventListener('click', function (event) {
                    onclick_handler('page', page_number, target_obj);
                })
            }
        });
    }
};

class CatalogueItemsTable extends CatalogueBase {
    constructor(table_container, searchbar_element, pagination_container) {
        super();
        this.table_container = table_container;
        this.table = null;
        this.options = {
            enable_select_rows: true,
        }

        this.active_user_metadata = {};
        this.pagination_container = pagination_container;
        this.searchbar_element = searchbar_element;

        this.data_checklist = {
            'catalogue_items_data': false,
        };

        this.data_table_obj = null;

        this.init();
    }

    init() {
        var _this = this;
        _this.initialize_table_header_metadata();
        _this.initialize_lead_data_metadata_update_modal();
        _this.fetch_catalogue_items();
    }

    initialize_table_header_metadata() {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = _this.get_table_meta_data();
    }

    initialize_table() {
        var _this = this;

        _this.table_container.innerHTML = '<table class="table table-bordered" id="message-history-info-table" width="100%" cellspacing="0"></table>';
        _this.table = _this.table_container.querySelector("table");

        if (!_this.table) return;
        if (_this.active_user_metadata.lead_data_cols.length == 0) return;
        if (_this.catalogue_items_data.length == 0) {
            _this.options.enable_select_rows = false;
        } else {
            _this.options.enable_select_rows = true;
        }

        _this.initialize_head();
        _this.initialize_body();
        _this.add_event_listeners();
        _this.update_table_attribute([_this.table]);

        // document.getElementById("assign-campaign-btn").style.display = "none";
        /*
            ------- saved for future reference -------
            $(_this.table).DataTable().clear().draw();
            $(_this.table).DataTable().destroy(true);
        */
    }

    initialize_head() {
        var _this = this;
        const { enable_select_rows } = _this.options;

        let th_html = "";
        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            if (column_info_obj.selected == false) return;
            let name = column_info_obj.name;
            let display_name = column_info_obj.display_name;
            th_html += '<th name="' + name + '">' + display_name + '</th>'
        });
        let select_rows_html = "";
        if (enable_select_rows) {
            select_rows_html = [
                '<th>',
                '<div class="easychat-custom-checkbox-wrapper">',
                '<label>',
                '<input class="filled-in catalogue-items-select-all-cb" type="checkbox">',
                '<span></span>',
                '</label>',
                '</div>',
                '</th>',
            ].join('');
        }

        let thead_html = [
            '<thead>',
            '<tr>',
            select_rows_html,
            th_html,
            '</tr>',
            '</thead>',
        ].join('');

        _this.table.innerHTML = thead_html;
    }

    initialize_body() {
        var _this = this;

        let [catalogue_items_data_list, catalogue_items_map] = this.get_rows_and_create_items_map();
        _this.catalogue_items_map = catalogue_items_map;

        _this.data_table_obj = $(_this.table).DataTable({
            "language": {
                "emptyTable": EMPTY_TABLE_SVG
            },
            "data": catalogue_items_data_list,
            "ordering": false,
            "bPaginate": false,
            "bInfo": false,
            "bLengthChange": false,
            "searching": true,
            'columnDefs': [{
                "targets": 0,
                "className": "text-left text-md-center",
                "width": "4%"
            },
            ],

            initComplete: function (settings) {
                $(_this.table).colResizable({
                    disable: true
                });
                $(_this.table).colResizable({
                    liveDrag: true,
                    minWidth: 100,
                    postbackSafe: true,
                });
                _this.apply_table_pagination();
                // _this.show_filter_div();
                // _this.add_filter_event_listener();
            },
            createdRow: function (row, data, dataIndex) {
                row.setAttribute("item_id", _this.catalogue_items_data[dataIndex].item_id);
            },
        });
    }

    update_url_with_filters(filters) {
        let key_value = "";
        for (var filter_key in filters) {
            let filter_data = filters[filter_key];
            for (var index = 0; index < filter_data.length; index++) {
                key_value += filter_key + "=" + filter_data[index] + "&";
            }
        }

        let new_url = window.location.protocol + "//" + window.location.host + window.location.pathname + '?' + key_value;
        window.history.pushState({ path: new_url }, '', new_url);
    }

    add_filter_and_fetch_data(key, value, target_obj = null) {
        let _this = this;
        if (target_obj) {
            _this = target_obj;
        }

        let filters = get_url_multiple_vars();
        if (key == "page") {
            filters.page = [value];
        }

        _this.update_url_with_filters(filters);
        _this.fetch_catalogue_items();
    }

    apply_table_pagination() {
        let _this = this;
        if (_this.catalogue_items_data.length == 0) {
            _this.pagination_container.innerHTML = "";
            return;
        }

        let container = _this.pagination_container;
        let metadata = _this.pagination_metadata;
        let onclick_handler = _this.add_filter_and_fetch_data;
        _this.apply_pagination(container, metadata, onclick_handler, _this);
    }

    fetch_catalogue_items() {
        let _this = this;

        let url_params = get_url_vars();
        let page = url_params["page"] ? url_params["page"] : 1;
        let items_per_page = url_params["items_per_page"] ? url_params["items_per_page"] : 25;
        let params_string = url_params["availability"] ? "&availability=" + url_params["availability"] : "";
        params_string += url_params["gender"] ? "&gender=" + url_params["gender"] : "";
        params_string += url_params["condition"] ? "&condition=" + url_params["condition"] : "";
        params_string += url_params["currency"] ? "&currency=" + url_params["currency"] : "";
        params_string += url_params["price_from"] ? "&price_from=" + url_params["price_from"] : "";
        params_string += url_params["price_to"] ? "&price_to=" + url_params["price_to"] : "";
        let search_term = $("#item-search-bar").val().trim();
        let xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/chat/channels/whatsapp/get-catalogue-products/?bot_id=" + BOT_ID + "&page=" + page + "&items_per_page=" + items_per_page + params_string + "&search_term=" + search_term, true);
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                let response = JSON.parse(this.responseText);
                response = custom_decrypt(response);
                response = JSON.parse(response);
                if (response["status"] == 200) {
                    _this.pagination_metadata = response.pagination_metadata;
                    _this.set_catalogue_data(response.catalogue_items);
                    $("#total_catalogue_items").text(response.pagination_metadata.total_count)
                } else {
                    _this.set_catalogue_data([]);
 
                    if ("message" in response) {
                        showToast(response.message, 3000)
                    } else {
                        showToast("Unable to fetch Catalogue Items, please try again later.", 3000)
                    }
                }
            } else if (this.readyState == 4 && this.status != 200) {
                showToast("Unable to fetch Catalogue Items, please try again later.", 3000)
            }
        }
        xhttp.send(params);
    }

    set_catalogue_data(catalogue_items_data) {
        let _this = this;
        if (catalogue_items_data) {
            _this.catalogue_items_data = catalogue_items_data;
            _this.data_checklist.catalogue_items_data = true;
        }
        if (!catalogue_items_data || !catalogue_items_data.length) {
            $("#delete_catalogue_btn").css({
                "opacity": "0.5",
                "pointer-events": "none"
            })
        }
        _this.check_and_initialize_table();
    }

    check_and_initialize_table() {
        let _this = this;

        if (_this.data_checklist.catalogue_items_data == false) return false;

        _this.initialize_table();
    }

    get_row_html(name, catalogue_items_data_obj) {
        let data = catalogue_items_data_obj[name];
        if (data == null || data == undefined) {
            data = "-";
        }
        let html = "";
        let item_other_details = JSON.parse(catalogue_items_data_obj.details_dump);
        switch (name) {
            case "name":
                let main_image_url = "/static/EasyChatApp/img/no-image.svg"
                let preview_image_urls = []
                if ("preview_image_urls" in catalogue_items_data_obj) {
                    preview_image_urls = JSON.parse(catalogue_items_data_obj.preview_image_urls);
                    if (preview_image_urls.length && preview_image_urls[0].trim() != "-" && preview_image_urls[0].trim()) {
                        main_image_url = preview_image_urls[0].trim()
                    }
                }
                html = `<a class="c-pointer item-name-wrapper" item-id="${catalogue_items_data_obj["item_id"]}">
                            <div class="item-img-wrapper">
                                <img src="${main_image_url}" alt="No preview available!" onerror="this.onerror=null;this.src='/static/EasyChatApp/img/no-image.svg';"/>
                            </div>
                            <div class="item-text-wrapper">
                                <h2>${data}
                                </h2>
                                <span>Content ID: ${catalogue_items_data_obj["retailer_id"]}</span>
                            </div>
                        </a>`
                break;

            case "currency":
                html = data;
                break;

            case "gender":
                html = `<p style='text-transform: capitalize;'>${data}</p>`;
                break;

            case "brand":
                html = data;
                break;

            case "availability":
                html = `<p style='text-transform: capitalize;'>${data}</p>`;
                break;

            case "price":
                html = item_other_details.price ? item_other_details.price : "-";
                break;

            default:
                html = "-";
                console.log("Error: unknown column")
                break;
        }
        return html;
    }

    get_select_row_html(catalogue_items_data_obj) {
        let _this = this;
        const { enable_select_rows } = _this.options;

        if (!enable_select_rows) {
            return "";
        }

        let select_row_html = `<div class="easychat-custom-checkbox-wrapper">
                                    <label>
                                        <input class="filled-in catalogue-select-row-cb" id="select_cb_${catalogue_items_data_obj.item_id}" type="checkbox" name="input-checkbox-selected-misdashboard-">
                                        <span></span>
                                    </label>
                                </div>`
        return select_row_html;
    }

    get_row(catalogue_items_data_obj) {
        let _this = this;
        const { enable_select_rows } = _this.options;

        var catalogue_items_data_list = [];

        let select_row_html = _this.get_select_row_html(catalogue_items_data_obj);
        if (enable_select_rows) {
            catalogue_items_data_list.push(select_row_html);
        }

        _this.active_user_metadata.lead_data_cols.forEach((column_info_obj) => {
            try {
                if (column_info_obj.selected == false) return;
                var name = column_info_obj.name;
                catalogue_items_data_list.push(_this.get_row_html(name, catalogue_items_data_obj));
            } catch (err) {
                console.log("ERROR get_row on adding row data of column : ", column_info_obj);
            }
        });

        return catalogue_items_data_list;
    }

    get_rows_and_create_items_map() {
        let _this = this;
        let catalogue_items_data_list = [];
        let catalogue_items_map = {};
        _this.catalogue_items_data.forEach((catalogue_items_data_obj) => {
            catalogue_items_data_list.push(_this.get_row(catalogue_items_data_obj));
            catalogue_items_map[catalogue_items_data_obj["item_id"]] = catalogue_items_data_obj
        })
        return [catalogue_items_data_list, catalogue_items_map];
    }

    show_filtered_results(event) {
        let _this = this;
        let value = event.target.value;

        if (!_this.data_table_obj) {
            return;
        }

        _this.data_table_obj.search(value).draw();

        let pagination_entry_container = _this.pagination_container.querySelector(".show-pagination-entry-container");

        if (pagination_entry_container) {
            let showing_entry_count = _this.table.querySelectorAll("tbody tr[role='row']").length;
            let total_entry = _this.pagination_metadata.end_point - _this.pagination_metadata.start_point + 1;

            if (value.length != 0) {
                let text = "Showing " + showing_entry_count + " entries (filtered from " + total_entry + " total entries)";
                pagination_entry_container.innerHTML = text;
                if (showing_entry_count == 0) {
                    $("#message-history-info-table tbody").html(`<tr class="odd"><td valign="top" colspan="8" class="dataTables_empty">
                        ${EMPTY_TABLE_SVG}
                    </td></tr>
                    `)
                }
            } else {
                pagination_entry_container.innerHTML = pagination_entry_container.getAttribute("filter_default_text");
            }
        }
    }

    add_event_listeners() {
        let _this = this;
        $(".catalogue-items-select-all-cb").change(() => {
            if ($(".catalogue-items-select-all-cb").prop("checked")) {
                $(".catalogue-select-row-cb").prop("checked", true).change();
            } else {
                $(".catalogue-select-row-cb").prop("checked", false).change();
            }
        });

        $(".catalogue-select-row-cb").change(() => {
            if ($(".catalogue-select-row-cb").length == $(".catalogue-select-row-cb:checked").length) {
                $(".catalogue-items-select-all-cb").prop("checked", true);
            } else {
                $(".catalogue-items-select-all-cb").prop("checked", false);
            }

            if ($(".catalogue-select-row-cb:checked").length >= 1) {
                $("#delete_catalogue_btn").css({
                    "pointer-events": "auto",
                    "opacity": "1"
                })
            } else {
                $("#delete_catalogue_btn").css({
                    "pointer-events": "none",
                    "opacity": "0.5"
                })
            }
        })
        $(".catalogue-select-row-cb").change();

        $(".item-name-wrapper").click((el) => {
            let item_id = $(el.target).closest(".item-name-wrapper").attr("item-id").split('-');
            item_id = item_id[item_id.length - 1];
            _this.initialize_edit_item_modal(item_id);
        })
    }

    initialize_edit_item_modal(item_id) {
        let _this = this;
        $("#item_details_preview_wrapper").show();
        $("#media_items_wrapper").hide();
        $("#detail-btn").addClass("active");
        $("#media-btn").removeClass("active");
        let active_item_obj = _this.catalogue_items_map[item_id]
        let active_item_other_details = JSON.parse(active_item_obj.details_dump);
        let main_image_url = "/static/EasyChatApp/img/no-image.svg"
        let preview_image_urls = []
        if ("preview_image_urls" in active_item_obj) {
            preview_image_urls = JSON.parse(active_item_obj.preview_image_urls);
            if (preview_image_urls && preview_image_urls[0].trim() != "" && preview_image_urls[0].trim() != "-") {
                main_image_url = preview_image_urls[0].trim()
            }
        }
        $("#detail_item_modal").modal("open")
        $(".edit-item-modal.item-name").text(active_item_obj.name)
        $(".edit-item-modal.item-content-id").text(active_item_obj.retailer_id)
        $(".edit-item-modal.item-price").text(active_item_other_details.price)
        $(".edit-item-modal.item-description").text(active_item_other_details.description)
        $(".edit-item-modal.item-website-url").attr("href", active_item_other_details.url)
        $(".edit-item-modal.item-website-url").text(active_item_other_details.url)
        $(".edit-item-modal.item-image-url").attr("href", active_item_obj.image_url)
        $(".edit-item-modal.item-image-url").text(active_item_obj.image_url)
        $(".edit-item-modal.item-preview-image").attr("src", main_image_url)
        $(".edit-item-modal.item-availibility").text(active_item_obj.availability)
        $(".edit-item-modal.item-group-id").text(active_item_other_details.retailer_product_group_id)
        $("#detail_item_modal #edit_catalogue_item_btn").prop("active-item-id", item_id)
        $("#media_items_wrapper").empty();
        let media_wrapper_html = `<div class="media-container-div">
                                    <img src="${main_image_url}" alt="No preview available!" onerror="this.onerror=null;this.src='/static/EasyChatApp/img/no-image.svg';">`
        if (preview_image_urls.length > 1) {
            for (let index = 1; index < preview_image_urls.length; index++) {
                if (index % 2 == 0) {
                    media_wrapper_html += `</div><div class="media-container-div">`
                }
                let image_url = "/static/EasyChatApp/img/no-image.svg"
                if (preview_image_urls[index] && preview_image_urls[index].trim() != "-") {
                    image_url = preview_image_urls[index]
                }
                media_wrapper_html += `<img src="${preview_image_urls[index]}" alt="No preview available!" onerror="this.onerror=null;this.src='/static/EasyChatApp/img/no-image.svg';">`
            }
        }
        media_wrapper_html += `</div>`
        $("#media_items_wrapper").html(media_wrapper_html);
        $("#edit_item_country_search").val("").keyup();
    }

    initialize_lead_data_metadata_update_modal() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols;
        var container = document.querySelector("#whatsapp_dala_table_meta_div");
        var selected_values = [];
        var unselected_values = [];
        lead_data_cols.forEach((obj) => {
            if (obj.selected == true) {
                selected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            } else {
                unselected_values.push({
                    'key': obj.name,
                    'value': obj.display_name
                });
            }
        });

        initialize_custom_tag_input(selected_values, unselected_values, container)
    }

    update_table_meta_deta(lead_data_cols) {
        var _this = this;
        _this.active_user_metadata.lead_data_cols = lead_data_cols;

        _this.save_table_meta_data();
        _this.initialize_table();
    }

    save_table_meta_data() {
        var _this = this;
        var lead_data_cols = _this.active_user_metadata.lead_data_cols
        window.localStorage.setItem("catalogue_manager_table_metadata", JSON.stringify(lead_data_cols));
    }

    get_table_meta_data() {
        var _this = this;
        var lead_data_cols = window.localStorage.getItem("catalogue_manager_table_metadata");

        if (lead_data_cols == null) {
            lead_data_cols = _this.get_default_meta_data();
        } else {
            lead_data_cols = JSON.parse(lead_data_cols);
        }
        return lead_data_cols;
    }

    get_default_meta_data() {
        var lead_data_cols = [
            ['name', 'Name', true],
            ['availability', 'Availability', true],
            ['price', 'Price', true],
            ['brand', 'Brand', true],
            ['gender', 'Gender', false],
            ['currency', 'Currency', false]
        ]

        var default_lead_data_cols = [];
        lead_data_cols.forEach((lead_data_col, index) => {
            default_lead_data_cols.push({
                name: lead_data_col[0],
                display_name: lead_data_col[1],
                index: index,
                selected: lead_data_col[2],
            });
        });
        return default_lead_data_cols;
    }
}

function initialize_custom_tag_input(selected_values, unselected_values, container) {
    window.LEAD_DATA_METADATA_INPUT = new CognoAICustomTagInput(container, selected_values, unselected_values);
}

class CognoAICustomTagInput {
    constructor(container, selected_values, unselected_values) {
        this.container = container;
        this.selected_values = selected_values;
        this.unselected_values = unselected_values;
        this.button_display_div = null;
        this.drag_obj = null;
        this.init();
    }

    init() {
        var _this = this;
        _this.initialize();
    }

    add_event_listeners() {
        var _this = this;
        var delete_buttons = _this.button_display_div.querySelectorAll(".tag_delete_button");
        delete_buttons.forEach((delete_button) => {
            delete_button.addEventListener('click', function (event) {
                _this.tag_delete_button_click_listner(event)
            });
        });

        var select_element = _this.select_element;
        select_element.addEventListener("change", function (event) {
            _this.tag_select_listnet(event);
        })
    }

    tag_delete_button_click_listner(event) {
        var _this = this;
        var target = event.target;
        var key = target.previousElementSibling.getAttribute("key");
        var index = _this.find_index_of_element(key, _this.selected_values);
        if (index != -1) {
            var target_obj = _this.selected_values[index];
            _this.selected_values.splice(index, 1);
            _this.unselected_values.push(target_obj);
            _this.initialize();
        }
    }

    tag_select_listnet(event) {
        var _this = this;
        var target = event.target;
        var key = target.value;
        var index = _this.find_index_of_element(key, _this.unselected_values);
        if (index != -1) {
            var target_obj = _this.unselected_values[index];
            _this.selected_values.push(target_obj);
            _this.unselected_values.splice(index, 1);
            _this.initialize();
        }
    }

    find_index_of_element(key, list) {
        for (var index = 0; index < list.length; index++) {
            if (list[index].key == key) return index;
        }
        return -1;
    }

    find_unselected_element_by_key(key) {
        var _this = this;
        var target_obj = null;
        _this.unselected_values.forEach((obj) => {
            if (obj.key == key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    find_selected_element_by_key(key) {
        var _this = this;
        var target_obj = null;
        _this.selected_values.forEach((obj) => {
            if (obj.key == key && target_obj == null) {
                target_obj = obj;
            }
        });
        return target_obj;
    }

    onmouseover_tag = function (element) {
        var handler = element.querySelector("svg");
        handler.style.display = "";
    }

    onmouseout_tag = function (element) {
        var handler = element.querySelector("svg");
        handler.style.display = "none";
    }

    get_tag_input_html() {
        var _this = this;
        var tag_input_html = '<ul class="cognoai-custom-tag-input mt-3">';

        _this.selected_values.forEach((obj, index) => {
            tag_input_html += [
                '<li class="bg-primary" onmouseover="window.LEAD_DATA_METADATA_INPUT.onmouseover_tag(this)" onmouseout="window.LEAD_DATA_METADATA_INPUT.onmouseout_tag(this)">',
                '<svg class="drag-handle" width="14" height="16" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 2px; display: none;">',
                '<path fill-rule="evenodd" clip-rule="evenodd" d="M9.91658 3.5C9.91658 4.14167 9.39158 4.66667 8.74992 4.66667C8.10825 4.66667 7.58325 4.14167 7.58325 3.5C7.58325 2.85834 8.10825 2.33334 8.74992 2.33334C9.39158 2.33334 9.91658 2.85834 9.91658 3.5ZM5.24996 2.33334C4.60829 2.33334 4.08329 2.85834 4.08329 3.50001C4.08329 4.14167 4.60829 4.66667 5.24996 4.66667C5.89163 4.66667 6.41663 4.14167 6.41663 3.50001C6.41663 2.85834 5.89163 2.33334 5.24996 2.33334ZM4.08325 7C4.08325 6.35834 4.60825 5.83334 5.24992 5.83334C5.89159 5.83334 6.41659 6.35834 6.41659 7C6.41659 7.64167 5.89159 8.16667 5.24992 8.16667C4.60825 8.16667 4.08325 7.64167 4.08325 7ZM5.24992 11.6667C5.89159 11.6667 6.41659 11.1417 6.41659 10.5C6.41659 9.85834 5.89159 9.33334 5.24992 9.33334C4.60825 9.33334 4.08325 9.85834 4.08325 10.5C4.08325 11.1417 4.60825 11.6667 5.24992 11.6667ZM8.74992 5.83334C8.10825 5.83334 7.58325 6.35834 7.58325 7C7.58325 7.64167 8.10825 8.16667 8.74992 8.16667C9.39158 8.16667 9.91658 7.64167 9.91658 7C9.91658 6.35834 9.39158 5.83334 8.74992 5.83334ZM7.58325 10.5C7.58325 9.85834 8.10825 9.33334 8.74992 9.33334C9.39158 9.33334 9.91658 9.85834 9.91658 10.5C9.91658 11.1417 9.39158 11.6667 8.74992 11.6667C8.10825 11.6667 7.58325 11.1417 7.58325 10.5Z" fill="white"/>',
                '</svg>',
                '<span key=' + obj.key + ' class="value_display_span">',
                obj.value,
                '</span>',
                '<span class="tag_delete_button" index=' + index + '>',
                'x',
                '</span>',
                '</li>',
            ].join('');
        });

        tag_input_html += '</ul>';
        return tag_input_html;
    }

    get_tag_select_html() {
        var _this = this;
        var tag_select_html = '<select class="form-control">';
        tag_select_html += '<option disabled selected> Choose column name </option>';

        _this.unselected_values.forEach((obj, index) => {
            tag_select_html += '<option value="' + obj.key + '"> ' + obj.value + '</option>';
        });

        tag_select_html += '</select>';
        return tag_select_html;
    }

    initialize() {
        var _this = this;
        var html = "";
        html += _this.get_tag_input_html();
        html += _this.get_tag_select_html();
        _this.container.innerHTML = html;

        _this.button_display_div = _this.container.querySelector("ul");
        _this.select_element = _this.container.querySelector("select");
        _this.add_event_listeners();
        _this.select_element_obj = new EasyChatCustomSelect(_this.select_element, null, window.CONSOLE_THEME_COLOR);
        _this.drag_obj = new CognoAiDragableTagInput(_this.button_display_div, function (event) {
            _this.drag_finish_callback(event)
        });
    }

    drag_finish_callback = function (event) {
        var _this = this;

        var elements = _this.button_display_div.children;
        var new_list = [];
        for (var idx = 0; idx < elements.length; idx++) {
            var element = elements[idx];
            var value_display_span = element.querySelector(".value_display_span");
            var key = value_display_span.getAttribute("key");
            var index = _this.find_index_of_element(key, _this.selected_values);
            new_list.push(_this.selected_values[index]);
        }

        _this.selected_values = new_list;
    }
}

class CognoAiDragableTagInput {
    constructor(container, drag_finish_callback) {
        this.container = container
        this.element = null;
        this.currX = 0;
        this.currY = 0;
        this.clientX = 0;
        this.clientY = 0;
        this.pageX = 0;
        this.offset = 12;
        this.is_dragging = false;
        this.drag_container = null;
        this.prevX = 0;
        this.prevY = 0;
        this.drag_finish_callback = drag_finish_callback;

        var _this = this;

        document.addEventListener("mouseleave", function (e) {
            _this.drag_element('out', e);
            e.preventDefault();
        });

        _this.drag_container = document;

        _this.drag_container.addEventListener("mousemove", function (e) {
            _this.drag_element('move', e);
        });

        _this.drag_container.addEventListener("mouseup", function (e) {
            _this.drag_element('up', e);
        });

        _this.initialize();
    }

    initialize() {
        var _this = this;
        var elements = _this.container.querySelectorAll(".drag-handle");
        if (elements.length == 0) {
            elements = _this.container.children;
        }
        for (var index = 0; index < elements.length; index++) {
            var element = elements[index];
            var target_element = _this.get_target_element(element);

            element.addEventListener("mousedown", function (e) {
                _this.drag_element('down', e);
            });

            element.addEventListener("mouseup", function (e) {
                _this.drag_element('up', e);
            });

            target_element.addEventListener("touchstart", function (e) {
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('down', e);
            });

            target_element.addEventListener("touchmove", function (e) {
                var data = {
                    movementX: e.touches[0].clientX - _this.prevX,
                    movementY: e.touches[0].clientY - _this.prevY,
                    clientX: e.touches[0].clientX,
                    clientY: e.touches[0].clientY,
                }
                _this.prevX = e.touches[0].clientX;
                _this.prevY = e.touches[0].clientY;
                _this.drag_element('move', data);
            });

            target_element.addEventListener("touchend", function (e) {
                _this.prevX = 0;
                _this.prevY = 0;
                _this.drag_element('out', e);
            });

            element.style.cursor = "move";
        }
    }

    get_target_element(element) {
        var _this = this;
        var handle = element;
        while (handle.parentElement != _this.container)
            handle = handle.parentElement;
        return handle;
    }

    drag_element(direction, e) {
        var _this = this;
        if (direction == 'down') {
            _this.is_dragging = true;
            _this.element = _this.get_target_element(e.target);
            if (!_this.dummy_element) {
                _this.dummy_element = document.createElement("span");
                _this.dummy_element.className = "cognoai-drag-dummy-element";
            }
        }

        if (direction == 'up' || direction == "out") {
            if (_this.is_dragging == false) {
                return;
            }

            _this.dummy_element.insertAdjacentElement("beforebegin", _this.element);
            _this.element.classList.remove("cognoai-drag-helper");
            _this.element.style.top = "";
            _this.element.style.left = "";
            _this.currX = 0;
            _this.currY = 0;
            _this.offset = 12;
            _this.is_dragging = false;
            _this.drag_container = null;
            _this.prevX = 0;
            _this.prevY = 0;
            _this.is_dragging = false;

            _this.element = null;
            if (_this.dummy_element.parentElement) {
                _this.dummy_element.parentElement.removeChild(_this.dummy_element);
            }
            _this.dummy_element = null;

            if (_this.drag_finish_callback) {
                try {
                    _this.drag_finish_callback()
                } catch (err) { }
            }
        }

        if (direction == 'move') {
            if (_this.is_dragging) {

                var left = _this.element.offsetLeft;
                var top = _this.element.offsetTop;

                _this.element.classList.add("cognoai-drag-helper");
                _this.currX = e.movementX + left;
                _this.currY = e.movementY + top;

                _this.clientX = e.clientX;
                _this.clientY = e.clientY;

                _this.pageX = e.pageX;

                _this.drag();
                _this.compute();
            }
        }
    }

    drag() {
        var _this = this;
        // _this.currX = Math.max(_this.currX, 0);

        _this.element.style.left = _this.currX + "px";
        _this.element.style.top = _this.currY + "px";
    }

    compute() {
        var _this = this;

        _this.element.hidden = true;
        let elemBelow = document.elementFromPoint(_this.clientX, _this.clientY);
        _this.element.hidden = false;

        try {
            var target_element = _this.get_target_element(elemBelow);
            if (target_element) {

                var pWidth = $(target_element).innerWidth(); //use .outerWidth() if you want borders
                var pOffset = $(target_element).offset();
                var x = _this.pageX - pOffset.left;
                if (pWidth / 2 > x) {
                    target_element.insertAdjacentElement("beforebegin", _this.dummy_element);
                } else {
                    target_element.insertAdjacentElement("afterend", _this.dummy_element);
                }
            }
        } catch (err) { }
    }
}

function save_catalogue_data_table_metadata() {

    let lead_data_cols = window.ACTIVE_CATALOGUE_TABLE.active_user_metadata.lead_data_cols;

    let selected_values = [];
    let unselected_values = [];
    window.LEAD_DATA_METADATA_INPUT.selected_values.filter((obj) => {
        selected_values.push(obj.key);
    });
    window.LEAD_DATA_METADATA_INPUT.unselected_values.filter((obj) => {
        unselected_values.push(obj.key);
    });


    if (selected_values.length < 2) {
        M.toast({
            "html": "Atleast two columns needs to be selected."
        }, 2000);
        return;
    }

    lead_data_cols.forEach((item, index) => {
        if (selected_values.indexOf(item.name) >= 0) {
            item.selected = true;
            item.index = selected_values.indexOf(item.name);
        } else {
            item.selected = false;
            item.index = window.LEAD_DATA_METADATA_INPUT.selected_values.length;
        }
    })

    lead_data_cols.sort((obj1, obj2) => {
        return obj1.index - obj2.index;
    });

    window.ACTIVE_CATALOGUE_TABLE.update_table_meta_deta(lead_data_cols)
    $("#whatsapp_meta_data_table").modal("close");
}

function get_url_multiple_vars() {
    let url_vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        if (!(key in url_vars)) {
            url_vars[key] = [];
        }
        url_vars[key].push(value);
    });
    return url_vars;
}

$("#easychat_catalogue_table_row_dropdown").change(() => {
    let url_vars = get_url_multiple_vars();
    url_vars.items_per_page = [$("#easychat_catalogue_table_row_dropdown").val()];
    window.ACTIVE_CATALOGUE_TABLE.update_url_with_filters(url_vars);
    window.ACTIVE_CATALOGUE_TABLE.fetch_catalogue_items();
})

function get_origin_country_dropdown_options() {
    let dropdown_html = "";
    for (let index = 0; index < country_options.length; index++) {
        dropdown_html += `<li class="dropdown__list-item" data-value="${country_options[index]}"><span>${country_options[index]}</span></li>`
    }
    return dropdown_html
}

function custom_dropdown_search(elem) {
    let search_element = $(elem).val();

    $(elem).closest('.dropdown__list').children('ul > li:not(:first-child)').each(function () {
        let no_value = $(this).parent().children('.no-data-div');
        let element_text = $(this).text();
        (element_text.toLowerCase().indexOf(search_element.toLowerCase()) > -1) ? $(this).show() : $(this).hide();
        if ($(this).parent().children(':visible').not(no_value).length === 1) {
            $(no_value).show();
        } else {
            $(no_value).hide();
        }
    });
};

// sprint 6.4.2

let item_image_upload = $('#upload-image-for-item');
let item_images_wrapper = $('#item-images-wrapper');
$(document).on("change", "#upload-image-for-item", function (e) {
    item_images_wrapper.css('display', 'block');
    let input = this;
    let file_name = e.target.files[0].name;
    let file_extension = file_name.split('.')
    file_extension = file_extension[file_extension.length - 1];

    if (e.target.files[0].size > 8*1024*1024) {
        M.toast({
            "html": "File greater than 8MB is not allowed!"
        }, 2000);
        document.getElementById("upload-image-for-item").value = ""; 
        return;
    }
    if (!["JPEG", "PNG"].includes(file_extension.toUpperCase())) {
        M.toast({
            "html": "Only JPEG and PNG files are allowed!"
        }, 2000);
        document.getElementById("upload-image-for-item").value = ""; 
        return;
    }
    $(create_image_containe_html(file_name, input)).appendTo(item_images_wrapper);
    count_images();
    check_upload_image_button_condition();
})

function create_image_containe_html(file_name, input) {
    let image_id = generate_random_string(4);
    let image_container = `<div class="uploaded-image-container" id="uploaded_image_${image_id}">
        <div class="drag-handler">
            <svg width="10" height="18" viewBox="0 0 10 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8.5 14.1309C9.32843 14.1309 10 14.8024 10 15.6309C10 16.4593 9.32843 17.1309 8.5 17.1309C7.67157 17.1309 7 16.4593 7 15.6309C7 14.8024 7.67157 14.1309 8.5 14.1309ZM1.5 14.1309C2.32843 14.1309 3 14.8024 3 15.6309C3 16.4593 2.32843 17.1309 1.5 17.1309C0.671573 17.1309 0 16.4593 0 15.6309C0 14.8024 0.671573 14.1309 1.5 14.1309ZM8.5 7.13086C9.32843 7.13086 10 7.80243 10 8.63086C10 9.45929 9.32843 10.1309 8.5 10.1309C7.67157 10.1309 7 9.45929 7 8.63086C7 7.80243 7.67157 7.13086 8.5 7.13086ZM1.5 7.13086C2.32843 7.13086 3 7.80243 3 8.63086C3 9.45929 2.32843 10.1309 1.5 10.1309C0.671573 10.1309 0 9.45929 0 8.63086C0 7.80243 0.671573 7.13086 1.5 7.13086ZM8.5 0.130859C9.32843 0.130859 10 0.802432 10 1.63086C10 2.45929 9.32843 3.13086 8.5 3.13086C7.67157 3.13086 7 2.45929 7 1.63086C7 0.802432 7.67157 0.130859 8.5 0.130859ZM1.5 0.130859C2.32843 0.130859 3 0.802432 3 1.63086C3 2.45929 2.32843 3.13086 1.5 3.13086C0.671573 3.13086 0 2.45929 0 1.63086C0 0.802432 0.671573 0.130859 1.5 0.130859Z" fill="#212121"/>
            </svg> 
        </div>
        <div class="image-body">
            <img id="${image_id}-item-image" file-name="${file_name}" class="item-image-upload-preview" alt="">
            <div class="image-data">
                <p>${sanitize_html(file_name)}</p>
            </div>
        </div>
        <div class="remove-image">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1.19165 1.13086L10.8082 11.1309" stroke="#2D2D2D" stroke-width="1.73614" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10.8083 1.13086L1.19183 11.1309" stroke="#2D2D2D" stroke-width="1.73614" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </div>`
    var reader = new FileReader();

    reader.onload = function (e) {
        let image = new Image();
        image.src = e.target.result;
        image.onload = function () {
            let height = this.height;
            let width = this.width;
            if (height < 500 || width < 500) {
                M.toast({
                    "html": "Image is smaller than 500 x 500 px"
                }, 2000);
                $(`#uploaded_image_${image_id}`).remove();
                count_images();
                return false;
            }
            $(`#${image_id}-item-image`).attr('src', e.target.result);
            return true;
        };
        image.onerror = function () {
            M.toast({
                "html": "Uploaded file is not a valid image file!"
            }, 2000);
            $(`#uploaded_image_${image_id}`).remove();
            count_images();
            return false;
        };
        document.getElementById("upload-image-for-item").value = "";
        check_upload_image_button_condition();
    };
    reader.readAsDataURL(input.files[0]);
    return image_container;
}

$(document).on("click", ".remove-image", function (e) {
    $(e.target).closest('.uploaded-image-container').remove();
    count_images();
    check_upload_image_button_condition();
})

function count_images() {
    let child_count = item_images_wrapper.children().length
    if (child_count == 0) {
        $('#modal-upload-product-image .drag-drop-container').css({ 'top': '50px', 'height': '427px' })
    } else {
        $('#modal-upload-product-image .drag-drop-container').css({ 'top': '0px', 'height': '258px' })
    }
}

$("#item-images-wrapper").sortable({
    containment: "parent",
    handle: '.drag-handler'
});


$("#upload_images_on_server").click(() => {
    let images_base64 = []
    $(".item-image-upload-preview").each((indx, ele) => {
        let file_id = ele.id.split('-')[0]
        images_base64.push({
            "filename": $(ele).attr("file-name"),
            "base64_file": ele.src,
            "file_id": file_id
        })
    })
    if (!images_base64.length) {
        M.toast({
            "html": "Please select atleast one image to upload!"
        }, 2000);
        return;
    }
    $("#upload_images_on_server").css({
        "opacity": "0.5",
        "pointer-events": "none"
    })
    $("#upload_images_on_server").html(`Uploading <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="animation: rotate 2s infinite">
    <path d="M20.946 12.9846C21.4949 13.0451 21.896 13.5408 21.7811 14.081C21.3316 16.1942 20.2069 18.1149 18.5634 19.5446C16.6673 21.1941 14.2196 22.0692 11.7075 21.9957C9.19542 21.9222 6.80309 20.9055 5.00668 19.148C3.21026 17.3904 2.14149 15.0209 2.01306 12.511C1.88464 10.0011 2.70599 7.53486 4.31364 5.60314C5.92129 3.67141 8.19735 2.41585 10.6888 2.08633C13.1803 1.75681 15.7045 2.3775 17.7591 3.82487C19.5399 5.07942 20.8548 6.87531 21.5176 8.93157C21.6871 9.45722 21.3387 9.99129 20.7988 10.1074V10.1074C20.2588 10.2236 19.7329 9.87693 19.5504 9.35569C19.002 7.78996 17.977 6.42479 16.6073 5.4599C14.9636 4.302 12.9443 3.80545 10.9511 4.06906C8.95788 4.33268 7.13703 5.33713 5.85091 6.88251C4.56479 8.42789 3.90771 10.4009 4.01045 12.4088C4.11319 14.4167 4.96821 16.3123 6.40534 17.7184C7.84247 19.1244 9.75633 19.9378 11.766 19.9966C13.7757 20.0554 15.7339 19.3553 17.2507 18.0357C18.5148 16.9361 19.3952 15.4734 19.7808 13.8599C19.9092 13.3227 20.397 12.9242 20.946 12.9846V12.9846Z" fill="white"/>
    </svg>`)
    var json_string = JSON.stringify(images_base64)
    json_string = EncryptVariable(json_string)

    encrypted_data = {
        "Request": json_string
    }

    var params = JSON.stringify(encrypted_data);
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/chat/upload-images-on-server/", true);
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.setRequestHeader('X-CSRFToken', get_csrf_token());
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            $("#upload_images_on_server").html("Next")
            let response = JSON.parse(this.responseText);
            response = custom_decrypt(response);
            response = JSON.parse(response);
            if (response["status"] == 200) {
                let files_data = JSON.parse(response.files_data)
                let active_section = $("#upload_images_on_server").attr("active_section")
                let error_present = false;
                for (const image_id in files_data) {
                    if (files_data[image_id].status == 200) {
                        let image_populated = false;
                        $("#accordion-header-wrapper-" + active_section + " .additional-image-url-input").each((indx, element) => {
                            if (element.value.trim() == "") {
                                element.value = files_data[image_id].compressed_path
                                image_populated = true
                                return false;
                            }
                        })
                        if (!image_populated) {
                            $("#add_more_image_btn_" + active_section).click();
                            $("#accordion-header-wrapper-" + active_section + " .additional-image-url-input:last").val(files_data[image_id].compressed_path)
                        }
                        $("#uploaded_image_" + image_id).remove();
                    } else {
                        error_present = true;
                    }
                }
                if(!error_present) {
                    $("#modal-upload-product-image").modal("close");
                } else {
                    $("#image-upload-error-wrapper").show();
                }
            } else {
                M.toast({
                    "html": "Failed to upload image(s) on server, please try again later."
                }, 2000);
            }
            check_upload_image_button_condition();
        } else if (this.readyState == 4 && this.status != 200) {
            M.toast({
                "html": "Internal server error occured while uploading images, please try again later."
            }, 2000);
            check_upload_image_button_condition();
        }
    }
    xhttp.send(params);
})

function check_upload_image_button_condition() {
    let images_length = $(".item-image-upload-preview").length;
    $("#upload_images_on_server").css({
        "pointer-events": images_length ? "auto" : "none",
        "opacity": images_length ? "1" : "0.5"
    })
}

function show_review_product_toast(){
    $('#easychat-product-review-toast-div').css("display","flex")
        if($('#easychat-product-review-toast-div').css('display') == 'flex'){
            $('.fixed-height-table').attr( "style","height : calc(100vh - 353px) !important;");
            $('#message-history-info-table_wrapper').addClass("set-dyamic-table-height");
        }
}

function hide_review_product_toast(){
    $('#easychat-product-review-toast-div').css("display","none");
        if($('#easychat-product-review-toast-div').css('display') == 'none'){
            $('.fixed-height-table').attr( "style","height : calc(100vh - 313px) !important;");
            $('#message-history-info-table_wrapper').removeClass("set-dyamic-table-height");
        }
} 