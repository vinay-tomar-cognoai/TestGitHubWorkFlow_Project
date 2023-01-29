SINGLE_PRODUCT_CHOICE = "single_product"

MULTIPLE_PRODUCT_CHOICE = "multiple_product"

COMMERCE_MANAGER_CATALOGUE_CHOICE = "commerce_manager_catalogue"

API_CATALOGUE_CHOICE = "api_catalogue"

WHATSAPP_CATALOGUE_TYPES = (
    (COMMERCE_MANAGER_CATALOGUE_CHOICE, "Commerce Manager Catalogue"),
    (API_CATALOGUE_CHOICE, "Catalogue via API")
)

REQUIRED_CATALOGUE_HEADERS = ["name", "description", "url", "image_url", "currency",
                              "price", "brand", "retailer_id", "category", "origin_country", "availability"]

CATALOGUE_SUPPORTED_CURRENCIES = ['DZD', 'ARS', 'AUD', 'BDT', 'BOB', 'BRL', 'GBP', 'CAD', 'CLP', 'CNY', 'COP', 'CRC', 'CZK', 'DKK', 'EGP', 'EUR', 'GTQ', 'HNL', 'HKD', 'HUF', 'ISK', 'INR', 'IDR', 'ILS', 'JPY',
                                  'KES', 'KRW', 'MOP', 'MYR', 'MXN', 'NZD', 'NIO', 'NGN', 'NOK', 'PKR', 'PYG', 'PEN', 'PHP', 'PLN', 'QAR', 'RON', 'RUB', 'SAR', 'SGD', 'ZAR', 'SEK', 'CHF', 'TWD', 'THB', 'TRY', 'AED', 'USD', 'UYU', 'VEF', 'VND']

# These currencies are not multiplied by 100 when creating Catalogue Items
OFFSET_1_CURRENCIES = ['CLP', 'COP', 'CRC', 'HUF',
                       'ISK', 'IDR', 'JPY', 'KRW', 'PYG', 'TWD', 'VND']

CATALOGUE_COUNTRY_OPTIONS = ["AD", "AE", "AF", "AG", "AI", "AL", "AM", "AN", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG",
                             "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR",
                             "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", "SC", "SD", "SE",
                             "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "XK", "YE", "YT", "ZA", "ZM", "ZW"]

CURRENCY_NAME_MAP = {'DZD': 'Algerian Dinar', 'ARS': 'Argentine Peso', 'AUD': 'Australian Dollar', 'BDT': 'Bangladeshi Taka', 'BOB': 'Bolivian Boliviano', 'BRL': 'Brazilian Real', 'GBP': 'British Pound', 'CAD': 'Canadian Dollar', 'CLP': 'Chilean Peso', 'CNY': 'Chinese Yuan', 'COP': 'Colombian Peso', 'CRC': 'Costa Rican Colon', 'CZK': 'Czech Koruna', 'DKK': 'Danish Krone', 'EGP': 'Egyptian Pounds', 'EUR': 'Euro', 'GTQ': 'Guatemalan Quetza', 'HNL': 'Honduran Lempira', 'HKD': 'Hong Kong Dollar', 'HUF': 'Hungarian Forint', 'ISK': 'Iceland Krona', 'INR': 'Indian Rupee', 'IDR': 'Indonesian Rupiah', 'ILS': 'Israeli New Shekel', 'JPY': 'Japanese Yen', 'KES': 'Kenyan Shilling', 'KRW': 'Korean Won',
                     'MOP': 'Macau Patacas', 'MYR': 'Malaysian Ringgit', 'MXN': 'Mexican Peso', 'NZD': 'New Zealand Dollar', 'NIO': 'Nicaraguan Cordoba', 'NGN': 'Nigerian Naira', 'NOK': 'Norwegian Krone', 'PKR': 'Pakistani Rupee', 'PYG': 'Paraguayan Guarani', 'PEN': 'Peruvian Nuevo Sol', 'PHP': 'Philippine Peso', 'PLN': 'Polish Zloty', 'QAR': 'Qatari Rials', 'RON': 'Romanian Leu', 'RUB': 'Russian Ruble', 'SAR': 'Saudi Arabian Riyal', 'SGD': 'Singapore Dollar', 'ZAR': 'South African Rand', 'SEK': 'Swedish Krona', 'CHF': 'Swiss Franc', 'TWD': 'Taiwan Dollar', 'THB': 'Thai Baht', 'TRY': 'Turkish Lira', 'AED': 'Uae Dirham', 'USD': 'United States Dollar', 'UYU': 'Uruguay Peso', 'VEF': 'Venezuelan Bolivar', 'VND': 'Vietnamese Dong'}

FB_SUPPORTED_CATALOGUE_FIELDS = ['additional_image_urls', 'additional_uploaded_image_ids', 'additional_variant_attributes', 'android_app_name', 'android_class', 'android_package', 'android_url', 'availability', 'brand', 'category', 'category_specific_fields', 'item_sub_type', 'checkout_url', 'color', 'commerce_tax_category', 'condition', 'currency', 'custom_data', 'custom_label_0', 'custom_label_1', 'custom_label_2', 'custom_label_3', 'custom_label_4', 'custom_number_0', 'custom_number_1', 'custom_number_2', 'custom_number_3', 'custom_number_4', 'description', 'expiration_date', 'fb_product_category', 'gender', 'gtin', 'image_url', 'importer_address', 'street1', 'street2', 'city', 'region', 'postal_code', 'country',
                                 'importer_name', 'inventory', 'ios_app_name', 'ios_app_store_id', 'ios_url', 'ipad_app_name', 'ipad_app_store_id', 'ipad_url', 'iphone_app_name', 'iphone_app_store_id', 'iphone_url', 'manufacturer_info', 'manufacturer_part_number', 'marked_for_product_launch', 'material', 'mobile_link', 'name', 'offer_price_amount', 'offer_price_end_date', 'offer_price_start_date', 'ordering_index', 'origin_country', 'pattern', 'price', 'product_type', 'retailer_id', 'retailer_product_group_id', 'return_policy_days', 'sale_price', 'sale_price_end_date', 'sale_price_start_date', 'short_description', 'size', 'start_date', 'url', 'visibility', 'wa_compliance_category', 'windows_phone_app_id', 'windows_phone_app_name', 'windows_phone_url']
