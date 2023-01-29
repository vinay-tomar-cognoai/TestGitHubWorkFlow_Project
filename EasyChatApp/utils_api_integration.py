from copy import copy
import json


def json_parser(ordered_json, start_string, selecthtml):
    request_packet_html_string = start_string
    if isinstance(ordered_json, str):
        ordered_json = json.loads(ordered_json)
    if isinstance(ordered_json, list) == False:
        for key, value in ordered_json.items():
            request_packet_html_string = request_packet_html_string + \
                '<li><span class="caret">' + str(key) + '</span>'
            if isinstance(value, dict) or isinstance(value, list):
                request_packet_html_string = request_packet_html_string + '<ul class="nested">'
                request_packet_html_string = json_parser(
                    value, request_packet_html_string, selecthtml)
            else:
                request_packet_html_string = request_packet_html_string + '<select name="' + str(key) + '" id= "' + str(key) + "jpd" + '" ><option value="' + "defaultallincallvalue" + str(
                    value) + '" class="tree">' + str(value) + '</option>' + selecthtml + '</select></li>'

        if isinstance(ordered_json, dict):
            request_packet_html_string = request_packet_html_string + "</ul>"

    elif isinstance(ordered_json, list) == True:
        for item in ordered_json:
            if isinstance(item, dict):
                for key, value in item.items():
                    request_packet_html_string = request_packet_html_string + \
                        '<li><span class="caret">' + str(key) + '</span>'
                    if isinstance(value, dict) or isinstance(value, list):
                        request_packet_html_string = request_packet_html_string + '<ul class="nested">'
                        request_packet_html_string = json_parser(
                            value, request_packet_html_string, selecthtml)
                    else:
                        request_packet_html_string = request_packet_html_string + '<select name="' + str(key) + '" id= "' + str(key) + "jpd" + '" ><option value="' + "defaultallincallvalue" + str(
                            value) + '" class="tree">' + str(value) + '</option>' + selecthtml + '</select></li>'

                if isinstance(ordered_json, dict):
                    request_packet_html_string = request_packet_html_string + "</ul>"
            else:
                request_packet_html_string = request_packet_html_string + '<select name="' + str(item) + '" id= "' + str(item) + "jpd" + '" ><option value="' + "defaultallincallvalue" + str(
                    item) + '" class="tree">' + str(item) + '</option>' + selecthtml + '</select></li>'

    return request_packet_html_string


def response_parser(ordered_json, start_string):
    response_packet_html_string = start_string
    if isinstance(ordered_json, str):
        ordered_json = json.loads(ordered_json)
    if isinstance(ordered_json, list) == False:
        for key, value in ordered_json.items():
            response_packet_html_string = response_packet_html_string + '<li><span class="caret">' + '<input type="text" name="' + \
                str(key) + '" id= "' + str(key) + \
                '" value="' + str(key) + '">' + '</span>'
            if isinstance(value, dict) or isinstance(value, list):
                response_packet_html_string = response_packet_html_string + '<ul class="nested">'
                response_packet_html_string = response_parser(
                    value, response_packet_html_string)
            else:
                response_packet_html_string = response_packet_html_string + \
                    str(value) + '</li>'

        if isinstance(ordered_json, dict):
            response_packet_html_string = response_packet_html_string + "</ul>"
    elif isinstance(ordered_json, list) == True:
        for item in ordered_json:
            if isinstance(item, dict):
                for key, value in item.items():
                    response_packet_html_string = response_packet_html_string + '<li><span class="caret">' + '<input type="text" name="' + \
                        str(key) + '" id= "' + str(key) + \
                        '" value="' + str(key) + '">' + '</span>'
                    if isinstance(value, dict) or isinstance(value, list):
                        response_packet_html_string = response_packet_html_string + "<ul class='nested'>"
                        response_packet_html_string = response_parser(
                            value, response_packet_html_string)
                    else:
                        response_packet_html_string = response_packet_html_string + \
                            str(value) + '</li>'

                if isinstance(ordered_json, dict):
                    response_packet_html_string = response_packet_html_string + "</ul>"

    return response_packet_html_string


def error_response_parser(ordered_json, start_string):
    response_packet_html_string = start_string
    if isinstance(ordered_json, str):
        ordered_json = json.loads(ordered_json)
    if isinstance(ordered_json, list) == False:
        for key, value in ordered_json.items():
            response_packet_html_string = response_packet_html_string + '<li><span class="caret">' + '<input type="text" name="' + \
                str(key) + "error_response_key" + '" id= "' + str(key) + "error_response_key" + \
                '" value="' + str(key) + '">' + '</span>'
            if isinstance(value, dict) or isinstance(value, list):
                response_packet_html_string = response_packet_html_string + '<ul class="nested">'
                response_packet_html_string = response_parser(
                    value, response_packet_html_string)
            else:
                response_packet_html_string = response_packet_html_string + \
                    str(value) + '</li>'

        if isinstance(ordered_json, dict):
            response_packet_html_string = response_packet_html_string + "</ul>"
    elif isinstance(ordered_json, list) == True:
        for item in ordered_json:
            if isinstance(item, dict):
                for key, value in item.items():
                    response_packet_html_string = response_packet_html_string + '<li><span class="caret">' + '<input type="text" name="' + \
                        str(key) + "error_response_key" + '" id= "' + str(key) + "error_response_key" + \
                        '" value="' + str(key) + '">' + '</span>'
                    if isinstance(value, dict) or isinstance(value, list):
                        response_packet_html_string = response_packet_html_string + "<ul class='nested'>"
                        response_packet_html_string = response_parser(
                            value, response_packet_html_string)
                    else:
                        response_packet_html_string = response_packet_html_string + \
                            str(value) + '</li>'

                if isinstance(ordered_json, dict):
                    response_packet_html_string = response_packet_html_string + "</ul>"

    return response_packet_html_string


def json_key(jsonstring, packet):
    if isinstance(jsonstring, list) == False:
        for key in jsonstring:
            if(isinstance(jsonstring[key], dict)) == False and isinstance(jsonstring[key], list) == False:
                if "defaultallincallvalue" in packet[key]:
                    packet[key] = packet[key].replace(
                        "defaultallincallvalue", "")

                else:
                    packet[key] = "{/" + packet[key] + "/}"
                jsonstring[key] = packet[key].strip()

            else:
                packets = packet
                json_key(jsonstring[key], packets)
    else:
        for item in jsonstring:
            for key in item:
                if(isinstance(item[key], dict)) == False and (isinstance(item[key], list)) == False:
                    if "defaultallincallvalue" in packet[key]:
                        packet[key] = packet[key].replace(
                            "defaultallincallvalue", "")
                    else:
                        packet[key] = "{/" + packet[key] + "/}"
                    item[key] = packet[key].strip()
                else:
                    packets = packet
                    json_key(item[key], packets)


def find_path(dict_obj, input_key, path, result, extra_data=None):
    for key, value in dict_obj.items():
        # add key to path
        path.append(key)
        if isinstance(value, dict):
            # continue searching
            find_path(value, input_key, path, result, extra_data)
        if isinstance(value, list):
            # search through list of dictionaries
            for iterator, item in enumerate(value):
                # add the index of list that item dict is part of, to path
                path.append(iterator)
                if isinstance(item, dict):
                    # continue searching in item dict
                    find_path(item, input_key, path, result, iterator)
                # if reached here, the last added index was incorrect, so
                # removed
                path.pop()
        if key == input_key:
            # add path to our result
            result.append(copy(path))
        # remove the key added in the first line
        if path != []:
            path.pop()


def json_key_response(jsonstring, packet, blank_dictionary):
    for key in packet:
        result = []
        path = []
        find_path(jsonstring, key, path, result)
        if len(result) > 0:
            value = ""
            for iterator in range(0, len(result[0])):
                if isinstance(result[0][iterator], str):
                    value = value + "['" + str(result[0][iterator]) + "']"
                else:
                    value = value + "[" + str(result[0][iterator]) + "]"

            blank_dictionary[packet[key]] = value
