var selected_node = null;
var copied_node_id = null;
var last_selected_elm = null;
var child_inbetween_node = null;
var maxwidth = null;
var maxheight = null;
var node_intent_data = {}
var rhs_panel_timer = null
var click_ended = true
var context_click = false
var child_create_action = false
var selected_move_intent = null
var is_category_changed = false

var html = `
<div class="node-wrapper-div"><span></span>
<div>
<a oncontextmenu="show_node_action_options(this)" class="node-menu-option-icon" > <span class="tooltipped" data-position="top" data-tooltip="Right click to open the menu"><svg width="12" height="13" viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="5.99994" cy="6.72772" r="1" transform="rotate(89.9055 5.99994 6.72772)" fill="#2D2D2D"/>
<circle cx="5.99433" cy="3.22772" r="1" transform="rotate(89.9055 5.99433 3.22772)" fill="#2D2D2D"/>
<circle cx="6.0058" cy="10.2277" r="1" transform="rotate(89.9055 6.0058 10.2277)" fill="#2D2D2D"/>
</svg></span>
</a>
<ul class="node-menu-option-container">
<li onclick="create_child_intent(event)" class="child-create"> Create Child Intent </li>
<li onclick="delete_flow()" id="delete_whole_flow" style="display: block"> Delete Whole Flow</li>
<li onclick="single_delete()"> Delete Only Node </li>
<li onclick="copy_node(event)"> Copy Tree</li>
<li onclick="paste_node()" style="display: none" class="paste_tree_li"> Paste Tree </li>
<li onclick="move_node()"> Move Node </li>
<li onclick="insert_inbetween()" class="child-create" id="insert_in_between" style="display: block"> Insert In between </li>
</ul></div>
</div>
<svg class="node-create-child-icon" onclick="create_child_intent_from_plus(event)" width="37" height="37" viewBox="0 0 37 37" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.5 32.375C10.841 32.375 4.625 26.159 4.625 18.5C4.625 10.841 10.841 4.625 18.5 4.625C26.159 4.625 32.375 10.841 32.375 18.5C32.375 26.159 26.159 32.375 18.5 32.375ZM17.1125 24.05C17.1125 24.8131 17.7369 25.4375 18.5 25.4375C19.2631 25.4375 19.8875 24.8131 19.8875 24.05V19.8875H24.05C24.8131 19.8875 25.4375 19.2631 25.4375 18.5C25.4375 17.7369 24.8131 17.1125 24.05 17.1125H19.8875V12.95C19.8875 12.1869 19.2631 11.5625 18.5 11.5625C17.7369 11.5625 17.1125 12.1869 17.1125 12.95V17.1125H12.95C12.1869 17.1125 11.5625 17.7369 11.5625 18.5C11.5625 19.2631 12.1869 19.8875 12.95 19.8875H17.1125V24.05Z" fill="black"/>
</svg>
<svg class="node-remove-child-icon" onclick="remove_singe_node(selected_node)" width="37" height="37" viewBox="0 0 37 37" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5 19.125C5 26.784 11.216 33 18.875 33C26.534 33 32.75 26.784 32.75 19.125C32.75 11.466 26.534 5.25 18.875 5.25C11.216 5.25 5 11.466 5 19.125ZM11.8041 19.4594C11.8041 18.6862 12.4309 18.0594 13.2041 18.0594H24.4041C25.1773 18.0594 25.8041 18.6862 25.8041 19.4594C25.8041 20.2326 25.1773 20.8594 24.4041 20.8594H13.2041C12.4309 20.8594 11.8041 20.2326 11.8041 19.4594Z" fill="black"/>
</svg>
`;

var root_html = `
<div><a oncontextmenu="show_node_action_options(this)" title="Right Click to Open Node Menu" class="node-menu-option-icon"> <span class="tooltipped" data-position="top" data-tooltip="Right click to open the menu"><svg width="12" height="13"
                viewBox="0 0 12 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="5.99994" cy="6.72772" r="1" transform="rotate(89.9055 5.99994 6.72772)" fill="#2D2D2D" />
                <circle cx="5.99433" cy="3.22772" r="1" transform="rotate(89.9055 5.99433 3.22772)" fill="#2D2D2D" />
                <circle cx="6.0058" cy="10.2277" r="1" transform="rotate(89.9055 6.0058 10.2277)" fill="#2D2D2D" />
            </svg></span></a>
        <ul class="node-menu-option-container">
            <li onclick="create_child_intent(event)" class="child-create"> Create Child Intent </li>
            <li onclick="single_delete()" id="delete_root_node"> Delete Whole Flow</li>
            <li onclick="copy_node(event)"> Copy Tree</li>
            <li onclick="paste_node()" style="display: none" class="paste_tree_li"> Paste Tree </li>
            <li onclick="insert_inbetween()" class="child-create" id="insert_in_between" style="display: block"> Insert In between </li>
        </ul>
    </div>
</div> <svg class="node-create-child-icon" onclick="create_child_intent_from_plus(event)" width="37" height="37"
    viewBox="0 0 37 37" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path fill-rule="evenodd" clip-rule="evenodd"
        d="M18.5 32.375C10.841 32.375 4.625 26.159 4.625 18.5C4.625 10.841 10.841 4.625 18.5 4.625C26.159 4.625 32.375 10.841 32.375 18.5C32.375 26.159 26.159 32.375 18.5 32.375ZM17.1125 24.05C17.1125 24.8131 17.7369 25.4375 18.5 25.4375C19.2631 25.4375 19.8875 24.8131 19.8875 24.05V19.8875H24.05C24.8131 19.8875 25.4375 19.2631 25.4375 18.5C25.4375 17.7369 24.8131 17.1125 24.05 17.1125H19.8875V12.95C19.8875 12.1869 19.2631 11.5625 18.5 11.5625C17.7369 11.5625 17.1125 12.1869 17.1125 12.95V17.1125H12.95C12.1869 17.1125 11.5625 17.7369 11.5625 18.5C11.5625 19.2631 12.1869 19.8875 12.95 19.8875H17.1125V24.05Z"
        fill="black" />
</svg> <svg class="root-node-identifier-icon" width="14" height="14" viewBox="0 0 14 14" fill="none"
    xmlns="http://www.w3.org/2000/svg">
    <path
        d="M7 1.16602L8.8025 4.81768L12.8333 5.40685L9.91667 8.24768L10.605 12.261L7 10.3652L3.395 12.261L4.08333 8.24768L1.16667 5.40685L5.1975 4.81768L7 1.16602Z"
        fill="#F7D14C" />
</svg>
`

var unique_id = 1;
var copy_value = null;

function copy_intent() {
    copy_value = editor.getNodeFromId(selected_node)
}

function paste_intent() {
    // editor.addNode(copy_value)
    copy_value.id = copy_value.id + 1
        // editor.addNodeInput(copy_value.id)  
    editor.import(copy_value);
    // editor.addConnection(copy_value.id, 2, copy_value.class, "personalized")
}

function move_node(confirm) {
    context_click = true
    const node_id = selected_node

    if (!confirm) {
        $("#easychat_flow_node_move_modal .termination-confirmation-heading-text").text(
            `Are you sure you want to move the ${node_intent_data[node_id].name} node?`
        )
        $("#easychat_flow_node_move_modal").modal("open")
        $("#easychat_flow_node_move_modal .termination-yes-btn").attr("onclick", "move_node(true)")
        $("#easychat_flow_node_move_modal .termination-no-btn").attr("onclick", "hide_right_nav_menu()")

        return
    }

    $("#easychat_flow_node_move_modal").modal("close")

    selected_move_intent = selected_node
    document.getElementById(`node-${selected_node}`).style.outline = "solid #FF0000";
    const all_nodes = Object.values(editor.drawflow.drawflow.Home.data).map((elm) => elm.id).filter((elm) => elm !== node_id)

    var mode_node_data = editor.drawflow.drawflow.Home.data[selected_node]['outputs']['output_1']['connections']

    $(".main-path").hide()
    editor.removeNodeInput(node_id, "input_1")
    editor.addNodeInput(node_id, "input_1")

    $(".input_1").css("pointer-events", "auto")
    $(".output_1").css("pointer-events", "auto")

    for (const node of all_nodes) {
        if (node != selected_node){
            $(`#node-${node} .inputs .input`).css('pointer-events','none');
        }
        else if (node == selected_node){
            $(`#node-${node} .outputs .output`).css('pointer-events','none');
        }
    }

    // Disable all output connection of particular node 
    all_child_nodes(mode_node_data)
    
    // Disable right nav bar from opening
    hide_right_nav_menu()
    
}

function all_child_nodes(nodes) {
    for (const [key, value] of Object.entries(nodes)) {
        $(`#node-${value["node"]} .outputs .output`).css('pointer-events','none');
        all_child_nodes(editor.drawflow.drawflow.Home.data[value["node"]]['outputs']['output_1']['connections'])    
    }
}

function insert_inbetween(confirm) {
    context_click = true
    const node_id = selected_node

    if (!confirm) {
        $("#easychat_flow_node_insert_modal .termination-confirmation-heading-text").text(
            `Are you sure you want to insert a node in between ${node_intent_data[node_id].name} and its child?`
        )
        $("#easychat_flow_node_insert_modal").modal("open")
        $("#easychat_flow_node_insert_modal .termination-yes-btn").attr("onclick", "insert_inbetween(true)")
        $("#easychat_flow_node_insert_modal .termination-no-btn").attr("onclick", "hide_right_nav_menu()")

        return
    }

    $("#easychat_flow_node_insert_modal").modal("close")

    const node = editor.getNodeFromId(node_id)
    const output_conn = node.outputs.output_1.connections
    const data = {
        "name": ''
    };

    editor.removeNodeOutput(node_id, "output_1")
    editor.addNodeOutput(node_id, "output_1")

    let offsety = node.pos_y + 100
    let offsetx = node.pos_x
    
    const new_node = editor.addNode("name", 1, 1, offsetx, offsety, "new-intent-node-identifier-div facebook", data, html.replace("<span></span>", `<span>Click here to edit</span>`));
    
    editor.addConnection(node_id, new_node, "output_1", "input_1")

    node_intent_data[new_node] = JSON.parse(JSON.stringify(NEW_NODE_DUMMY_DATA))
    if ($("#channel-GoogleBusinessMessages")[0].checked) {
        node_intent_data[new_node].short_name_enabled = true
    }
    node_intent_data[new_node].other_settings.is_last_tree = true
    node_intent_data[new_node].is_new_tree = true
    node_intent_data[new_node].is_in_between_tree = true

    $("#node-"+ new_node + " a").hide()
    $("#node-"+ new_node + " .node-create-child-icon").css("visibility", "hidden")
    $("#node-"+ new_node + " .node-remove-child-icon").css("visibility", "visible")

    for (const output of output_conn) {
        editor.addConnection(new_node, output.node, "output_1", "input_1")
    }

    update_flow(1, window.outerWidth / 6)
    update_node_vertical_positions(1)

    editor.node_selected = document.getElementById("node-" + new_node)
    editor.events.nodeSelected.listeners[0](new_node)
    $("#node-"+ new_node).addClass("selected")
    if ($(`#node-${node_id}`).hasClass("selected")) {
        $(`#node-${node_id}`).removeClass("selected")
    }
}

function create_intent() {
    let data = {
        "name": ''
    };

    editor.addNode("name", 1, 1, 100, 100, "facebook", data, html);
    show_details_wrapper()

}

function save_node_name() {
    let input_val = document.querySelector("#intent_name_input_div").value
    let training_questions = node_intent_data[selected_node].training_data
    $("#bot_response .tabs").tabs('select', 'intent-bot-response-tab')

    if (!input_val.trim()) {
        M.toast({
            "html": "Node name cannot be empty."
        }, 2000);
        open_intent_menu_data({currentTarget: $("#create_intent_menu_icon")[0]}, 'create_intent')
        return;
    }

    if (input_val.trim().length > INTENT_TREE_NAME_CHARACTER_LIMIT) {
        M.toast({
            "html": "Intent Name Cannot Contain More Than 500 Characters"
        }, 2000);
        open_intent_menu_data({currentTarget: $("#create_intent_menu_icon")[0]}, 'create_intent')
        return;
    }

    if (node_intent_data[selected_node].isRoot && training_questions.length == 0) {
        M.toast({
            "html": "At least one training sentence is required."
        }, 2000);
        open_intent_menu_data({currentTarget: $("#create_intent_menu_icon")[0]}, 'create_intent')
        return;
    }

    last_selected_elm.querySelector(".node-wrapper-div span").innerText = document.querySelector("#intent_name_input_div").value
    editor.updateNodeDataFromId(selected_node, {
        name: input_val
    })
    $(".intent_name_input_div").val(input_val)
    if ($(".intent_name_tooltip").length) {
        $(".intent_name_tooltip").attr("data-tooltip", input_val)
    } else {
        $(".intent_name_input_div:not(#intent_name_input_div)").wrap(`
        <span class="tooltipped intent_name_tooltip" style="flex-grow: 2;" data-position="bottom" data-tooltip="${input_val}"></span>
        `)
        $(".tooltipped").tooltip()
    }
    $(".tabcontent").hide()
    $("#bot_response").show()
    $("#edit_bot_response_icon").addClass("active")
    $("#create_intent_menu_icon").removeClass("active")

    if (selected_node != 1) {
        if (!node_intent_data[selected_node].whatsapp_short_name) {
            if (input_val.length > 24) {
                let new_input_val = input_val.substring(0, 21) + "..."
                $("#tree-whatsapp-short-name-input").val(new_input_val)
                $("#tree_whatsapp_short_name_field-char-count").text(new_input_val.length)
                node_intent_data[selected_node].whatsapp_short_name = new_input_val
            } else {
                $("#tree-whatsapp-short-name-input").val(input_val)
                $("#tree_whatsapp_short_name_field-char-count").text(input_val.length)
                node_intent_data[selected_node].whatsapp_short_name = input_val
            }
        }
        if (!node_intent_data[selected_node].whatsapp_description) {
            if (input_val.length > 72) {
                let new_input_val = input_val.substring(0, 69) + "..."
                $("#tree-whatsapp-description-input").val(new_input_val)
                $("#tree_whatsapp_description_field-char-count").text(new_input_val.length)
                node_intent_data[selected_node].whatsapp_description = new_input_val
            } else {
                $("#tree-whatsapp-description-input").val(input_val)
                $("#tree_whatsapp_description_field-char-count").text(input_val.length)
                node_intent_data[selected_node].whatsapp_description = input_val
            }
        }
    }

    if ($("#node-"+selected_node).outerHeight() > 50) {
        update_flow(1, window.outerWidth / 6)
        update_node_vertical_positions(1)
    }
}

function create_child_intent(e) {
    context_click = true
    const parent = Number(getNodeId(e.target))
    let data = {
        "name": ''
    };

    let offsety = editor.getNodeFromId(parent).pos_y + 100
    let offsetx = editor.getNodeFromId(parent).pos_x
    if (editor.getNodeFromId(parent).outputs.output_1.connections.at(-1)) {
        let sibling_node = editor.getNodeFromId(parent).outputs.output_1.connections.at(-1).node
        offsetx = editor.getNodeFromId(sibling_node).pos_x + 250
    }

    const node_id = editor.addNode("name", 1, 1, offsetx, offsety, "new-intent-node-identifier-div facebook", data, html.replace("<span></span>", `<span>Click here to edit</span>`));
    show_details_wrapper()

    editor.addConnection(parent, node_id, "output_1", "input_1")

    node_intent_data[node_id] = JSON.parse(JSON.stringify(NEW_NODE_DUMMY_DATA))
    if ($("#channel-GoogleBusinessMessages")[0].checked) {
        node_intent_data[node_id].short_name_enabled = true
    }
    node_intent_data[node_id].other_settings.is_last_tree = true
    node_intent_data[node_id].is_new_tree = true

    $("#node-"+ node_id + " a").hide()
    $("#node-"+ node_id + " .node-create-child-icon").css("visibility", "hidden")
    $("#node-"+ node_id + " .node-remove-child-icon").css("visibility", "visible")

    update_flow(1, window.outerWidth / 6)
    update_node_vertical_positions(1)

    context_click = false
    editor.node_selected = document.getElementById("node-" + node_id)
    editor.events.nodeSelected.listeners[0](node_id)
    $("#node-"+ node_id).addClass("selected")

    if ($(`#node-${parent}`).hasClass("selected")) {
        $(`#node-${parent}`).removeClass("selected")
    }
}

function create_child_intent_from_plus(e) {
    child_create_action = true
    context_click = true
    const parent = Number(e.currentTarget.parentElement.parentElement.id.split("-")[1])
    let data = {
        "name": ''
    };

    let offsety = editor.getNodeFromId(parent).pos_y + 100
    let offsetx = editor.getNodeFromId(parent).pos_x
    if (editor.getNodeFromId(parent).outputs.output_1.connections.at(-1)) {
        let sibling_node = editor.getNodeFromId(parent).outputs.output_1.connections.at(-1).node
        offsetx = editor.getNodeFromId(sibling_node).pos_x + 250
    }

    const node_id = editor.addNode("name", 1, 1, offsetx, offsety, "new-intent-node-identifier-div facebook", data, html.replace("<span></span>", `<span>Click here to edit</span>`));
    show_details_wrapper()
    editor.addConnection(parent, node_id, "output_1", "input_1")

    node_intent_data[node_id] = JSON.parse(JSON.stringify(NEW_NODE_DUMMY_DATA))
    if ($("#channel-GoogleBusinessMessages")[0].checked) {
        node_intent_data[node_id].short_name_enabled = true
    }
    node_intent_data[node_id].other_settings.is_last_tree = true
    node_intent_data[node_id].is_new_tree = true

    $("#node-"+ node_id + " a").hide()
    $("#node-"+ node_id + " .node-create-child-icon").css("visibility", "hidden")
    $("#node-"+ node_id + " .node-remove-child-icon").css("visibility", "visible")

    update_flow(1, window.outerWidth / 6)
    update_node_vertical_positions(1)

    context_click = false
    editor.node_selected = document.getElementById("node-" + node_id)
    editor.events.nodeSelected.listeners[0](node_id)
    $("#node-"+ node_id).addClass("selected")
    if ($(`#node-${parent}`).hasClass("selected")) {
        $(`#node-${parent}`).removeClass("selected")
    }
}

function recurse_color_change(node_id) {
    const node = editor.getNodeFromId(node_id)
    for (const child of node.outputs.output_1.connections) {
        $(`.node_in_node-${child.node} path`).css("stroke", "red")
        $(`.node_in_node-${child.node} path`).css("stroke-dasharray", 4)
        recurse_color_change(child.node)
    } 
}

function copy_node(e) {
    context_click = true
    copied_node_id = getNodeId(e.target)
    $(".paste_tree_li").show()
    $(`.connection path`).css("stroke", "#4ea9ff")
    $(`.connection path`).css("stroke-dasharray", "none")
    recurse_color_change(copied_node_id)
    hide_right_nav_menu()

}

function getNodeId(elm) {
    return elm.parentElement.parentElement.parentElement.parentElement.parentElement.id.split("-")[1]
}

function paste_node(confirm) {
    context_click = true
    const paste_id = selected_node

    if (!confirm) {
        $("#easychat_flow_node_copy_modal .termination-confirmation-heading-text").text(
            `Are you sure you want to paste the ${node_intent_data[copied_node_id].name} at ${node_intent_data[paste_id].name} node?`
        )
        $("#easychat_flow_node_copy_modal").modal("open")
        $("#easychat_flow_node_copy_modal .termination-yes-btn").attr("onclick", "paste_node(true)")
        $("#easychat_flow_node_copy_modal .termination-no-btn").attr("onclick", "hide_right_nav_menu()")
        return
    } 

    $("#easychat_flow_node_copy_modal").modal("close")

    response = pasteTreeNode(
        node_intent_data[paste_id].tree_pk, 
        get_url_vars()["intent_pk"], 
        node_intent_data[paste_id].tree_pk, 
        node_intent_data[copied_node_id].tree_pk
        );
    if (response['status'] == 200) {
        // recurse_create(paste_id, copied_node_id)
        M.toast({
            'html': 'Tree pasted',
            'displayLength': 500
        }, 2000);
        $(".paste_tree_li").hide()
        $(`.connection path`).css("stroke", "#4ea9ff")
        $(`.connection path`).css("stroke-dasharray", "none")

        const intent_pk = get_url_vars()["intent_pk"];
        const tree_structure = fetchIntentTreeStructureByIntentID(intent_pk, SELECTED_LANGUAGE)
        if (tree_structure["need_to_show_auto_fix_popup"]) {
            $("#autofix_div").show()
        } else {
            $("#autofix_div").hide()
        }
        editor.clear()
        editor.nodeId = 1
        node_intent_data = {}
        build_initial_flow(tree_structure[1], true, null, window.outerWidth / 6)
        update_flow()
        update_node_vertical_positions(1)
        editor.events.nodeSelected.listeners[0](paste_id)
        hide_right_nav_menu()
    } else {
        M.toast({
            'html': 'Unable to connect to server. Please try again later.'
        }, 2000);
    }
}

function recurse_create(parent, child) {
    const node = editor.getNodeFromId(child)
    let data = node.data;
    let new_html = html.replace("<span></span>", `<span>${data.name}</span>`)
    let offsety = editor.getNodeFromId(parent).pos_y + 100
    let offsetx = editor.getNodeFromId(parent).pos_x
    if (editor.getNodeFromId(parent).outputs.output_1.connections.at(-1)) {
        let sibling_node = editor.getNodeFromId(parent).outputs.output_1.connections.at(-1).node
        offsetx = editor.getNodeFromId(sibling_node).pos_x + 250
    }
    const new_child = editor.addNode("name", 1, 1, offsetx, offsety, "facebook", data, new_html);
    node_intent_data[new_child] = JSON.parse(JSON.stringify(node_intent_data[child]))
    editor.addConnection(parent, new_child, "output_1", "input_1")

    if (selected_node == child) {
        return
    }

    for (const child of node.outputs.output_1.connections) {
        recurse_create(new_child, child.node)
    }
}

function remove_singe_node(node_id) {
    const node = editor.getNodeFromId(node_id)
    const input_conn = node.inputs.input_1.connections[0]
    const output_conn = node.outputs.output_1.connections

    editor.removeNodeId(`node-${node_id}`)

    for (const output of output_conn) {
        editor.addConnection(input_conn.node, output.node, "output_1", "input_1")
    }
    delete node_intent_data[node_id]
    $(".easychat-edit-intent-rightnav-menu-wrapper").hide()
    $(".easychat-edit-intent-preview-wrapper").hide()
    hide_details_wrapper()
    update_flow(1, window.outerWidth / 6)
    update_node_vertical_positions(1)
}

function single_delete(confirm) {
    context_click = true
    const node_id = selected_node

    if (!confirm) {
        $("#easychat_flow_node_delete_modal .termination-confirmation-heading-text").text(
            `Are you sure you want to delete the ${node_intent_data[node_id].name} node?`
        )

        if (!node_intent_data[selected_node].isRoot) {
            $(".note-text-wrapper-div").hide();
        }
        else {
            $(".note-text-wrapper-div").show();
        }

        $("#easychat_flow_node_delete_modal").modal("open")
        $("#easychat_flow_node_delete_modal .termination-yes-btn").attr("onclick", "single_delete(true)")
        $("#easychat_flow_node_delete_modal .termination-no-btn").attr("onclick", "hide_right_nav_menu()")

        return
    } 

    $("#easychat_flow_node_delete_modal").modal("close")

    if (node_id == 1) {
        delete_intent()
        return
    }

    const parent = editor.getNodeFromId(node_id).inputs.input_1.connections[0].node
    
    response = deleteTreeNode(
        node_intent_data[node_id].tree_pk, 
        get_url_vars()["intent_pk"], 
        node_intent_data[parent].tree_pk, 
    );

    if (response['status'] == 200) {
        if (response["is_root_childs_present"] == true) {
            M.toast({
                'html': 'You cannot perform this action!'
            }, 2000);
        } else {
            M.toast({
                'html': 'Tree Node deleted successfully!'
            }, 2000);

            node_intent_data[parent].lazyLoaded = false
            remove_singe_node(node_id)
            update_flow(1, window.outerWidth / 6)
            update_node_vertical_positions(1)
            if (Object.keys(node_intent_data).length === 1) {
                $("#save_intent_flow").hide()
                if (is_category_changed) {
                    $("#save_intent_category").show()
                }
            }
        }
    } else {
        M.toast({
            'html': 'Unable to connect to server. Please try again later.'
        }, 2000);
    }
}

function delete_flow(confirm) {
    context_click = true
    const delete_id = selected_node

    if (!confirm) {
        $("#easychat_flow_node_delete_modal .termination-confirmation-heading-text").text(
            `Are you sure you want to delete the ${node_intent_data[delete_id].name} node whole flow?`
        )
        $(".note-text-wrapper-div").show()
        $("#easychat_flow_node_delete_modal").modal("open")
        $("#easychat_flow_node_delete_modal .termination-yes-btn").attr("onclick", "delete_flow(true)")
        $("#easychat_flow_node_delete_modal .termination-no-btn").attr("onclick", "hide_right_nav_menu()")

        return
    } 

    $("#easychat_flow_node_delete_modal").modal("close")

    const parent = editor.getNodeFromId(delete_id).inputs.input_1.connections[0].node

    response = deleteTree(
        node_intent_data[delete_id].tree_pk, 
        get_url_vars()["intent_pk"], 
        node_intent_data[parent].tree_pk, 
    );

    if (response['status'] == 200) {
        if (response["is_root"] == true) {
            M.toast({
                'html': 'You cannot perform this action'
            }, 2000);
        } else {
            M.toast({
                'html': 'Tree deleted successfully!'
            }, 2000);
            node_intent_data[parent].lazyLoaded = false
            recurse_delete(delete_id)
            if (Object.keys(node_intent_data).length === 1) {
                $("#save_intent_flow").hide()
                if (is_category_changed) {
                    $("#save_intent_category").show()
                }
            }
            $(".easychat-edit-intent-rightnav-menu-wrapper").hide()
            $(".easychat-edit-intent-preview-wrapper").hide()
            hide_details_wrapper()
            update_flow(1, window.outerWidth / 6)
            update_node_vertical_positions(1)
        }
    } else {
        M.toast({
            'html': 'Unable to connect to server. Please try again later.'
        }, 2000);
    }
}

function recurse_delete(id) {
    const node = editor.getNodeFromId(id)
    const childs = node.outputs.output_1.connections
    for (const child of childs) {
        recurse_delete(child.node)
    }
    editor.removeNodeId(`node-${id}`)
    delete node_intent_data[id]
}

var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.reroute = false;
editor.reroute_fix_curvature = false;
editor.reroute_curvature_start_end = 0;
editor.curvature = 0;

editor.start();
// editor.import(dataToImport);
build_initial_flow(tree_structure, true, null, window.outerWidth / 6)
update_flow()
update_node_vertical_positions(1)
$(window).on("load", function(){
    let id = 1;

    if (get_url_vars()["tree_pk"]) {
        for (const index of Object.keys(node_intent_data)) {
            if (node_intent_data[index].tree_pk == get_url_vars()["tree_pk"]) {
                id = index
            }
        }
    }

    $(`#node-${id}`).addClass("selected")
    editor.events.nodeSelected.listeners[0](id)
    editor.node_selected = $(`#node-${id}`)[0]
});

// Events!
editor.on('nodeUnselected', function() {
    $(".easychat-edit-intent-rightnav-menu-wrapper").hide()
    $(".easychat-edit-intent-preview-wrapper").hide()
    hide_details_wrapper()
    $(".trumbowyg-modal-reset").click()
    
    if ($("#node-1").hasClass("selected")) {
        $("#node-1").removeClass("selected")
    }
})


editor.on('mouseUp', function() {
    click_ended = true
})

editor.on('click', function(e) {
    click_ended = false
})

editor.on("contextmenu", function() {
    hide_right_nav_menu()
    context_click = true
})

editor.on('connectionCancel', function(connection) {
    if(connection) {
        M.toast({
            "html": "Please connect to Red Node only"
        }, 2000);
    }
})

function handle_zoom(zoom_type) {
    click_ended = false

    if (zoom_type == "out") {
        if (editor.zoom <= editor.zoom_min) {
            $(".fa-search-minus").css({
                "pointer-events": "none",
                "opacity": 0.5
            })
        } else {
            editor.zoom_out()
        }
            
    } else if (zoom_type == "in") {
        editor.zoom_in()
    } else {
        editor.zoom_reset()
        update_flow()
        update_node_vertical_positions(1)
    }
}

function node_select_action(id) {
    if (!click_ended) {
        rhs_panel_timer && clearTimeout(rhs_panel_timer)
        context_click = false
        return
    }

    if (child_create_action && !node_intent_data[id].is_new_tree) {
        return
    }

    let editor_id = editor.node_selected
    editor_id = editor_id ? editor_id.id.split("-")[1] : ""

    if (editor_id != id && !child_create_action) {
        if ($("#node-" + id).hasClass("selected")) {
            $("#node-" + id).removeClass("selected")
        }
        id  = selected_node = editor_id
    }

    child_create_action = false

    if (id == 1) {
        $(".intent_name_input_div").prop("placeholder", "Enter Intent Name")
    } else {
        $(".intent_name_input_div").prop("placeholder", "Enter Child Intent Name")
    }

    if (!node_intent_data[id]) {
        $(".easychat-edit-intent-rightnav-menu-wrapper").hide()
        $(".easychat-edit-intent-preview-wrapper").hide()
        hide_details_wrapper()
        return
    }
    show_details_wrapper()
    
    if (node_intent_data[selected_node].keep_resp_page) {
        open_intent_menu_data({currentTarget: $("#edit_bot_response_icon")[0]}, 'bot_response')
        node_intent_data[selected_node].keep_resp_page = false
    }

    let intent_info;
    if (is_new_intent === "True") {
        $(".custom-tooltip-intent:not(#create_intent_menu_icon,#edit_bot_response_icon)").addClass("disable-video-recoder-save-value")
        $(".edit-intent-details-cancel-btn").addClass("disable-video-recoder-save-value")
        $("#save_intent_flow").hide()
        $("#flow_excel_trigger").hide()
        $(".bot_response_delete_button").hide()
        $("#save_intent_category").hide()

        if (get_url_vars()["val"]) {
            let training_questions = decodeURIComponent(get_url_vars()["val"].trim()).split(",")
            let intent_name = training_questions[0];
            $("#intent_name_input_div").val(intent_name)
            let input_val = document.querySelector("#intent_name_input_div").value
            if ($(".intent_name_tooltip").length) {
                $(".intent_name_tooltip").prop("data-tooltip", input_val)
            } else {
                $(".intent_name_input_div:not(#intent_name_input_div)").wrap(`
                <span class="tooltipped" class="intent_name_tooltip" style="flex-grow: 2;" data-position="bottom" data-tooltip="${input_val}"></span>
                `)
                $(".tooltipped").tooltip()
            }
            $(".intent_name_input_div:not(#intent_name_input_div)").val(intent_name)
            last_selected_elm.querySelector(".node-wrapper-div span").innerText = document.querySelector("#intent_name_input_div").value
            editor.updateNodeDataFromId(selected_node, {
                name: intent_name
            })
            node_intent_data[selected_node].name = intent_name
            node_intent_data[selected_node].training_data = training_questions
            fill_training_data_rhs(training_questions, true)
        }
        return
    }

    if (!node_intent_data[id].lazyLoaded) {
        if (id == 1) {
            let url_parameters = get_url_vars()
            intent_pk = url_parameters["intent_pk"];
            try {
                intent_info = getIntentInformationByID(intent_pk)
                node_intent_data[id].isRoot = true
                node_intent_data[id].lazyLoaded = true
            } catch (err) {
                console.error(err.message)
            }
        } else {
            try {
                intent_info = fetchTreeInformationByID(node_intent_data[id].tree_pk)
                node_intent_data[id].isRoot = false
                node_intent_data[id].lazyLoaded = true
            } catch (err) {
                console.error(err.message)
            }
        }

        node_intent_data[id] = {...node_intent_data[id], ...intent_info}
        fill_rhs_with_data_for_root(node_intent_data[id])
        
    } else {
        fill_rhs_with_data_for_root(node_intent_data[id])
    }
    rhs_panel_timer && clearTimeout(rhs_panel_timer)
}

editor.on('nodeSelected', function(id) {
    
    selected_node = id;
    last_selected_elm = document.querySelector(`#node-${id}`)

    if(editor.drawflow.drawflow.Home.data[id]['outputs']['output_1']['connections'].length == 0){
        $(".node-menu-option-container #insert_in_between").hide();
        $(".node-menu-option-container #delete_whole_flow").hide();

        if (id == 1) {
            $(".node-menu-option-container #delete_root_node").text("Delete Node");
        }
    }
    else {
        $(".node-menu-option-container #insert_in_between").show();
        $(".node-menu-option-container #delete_whole_flow").show();

        if (id == 1) {
            $(".node-menu-option-container #delete_root_node").text("Delete Whole Flow");
        }
    }

    rhs_panel_timer = setTimeout(function() {
        node_select_action(id)
    }, 200)

})

editor.on('connectionCreated', function(connection) {
    $(".main-path").show()
    $(".input_1").css("pointer-events", "none")
    $(".output_1").css("pointer-events", "none")
    const all_nodes = Object.values(editor.drawflow.drawflow.Home.data).map((elm) => elm.id)

    for (const node of all_nodes) {
        $(`#node-${node}`).css("outline", "none")
    }
})

editor.on('zoom', function(zoom,e) {
    if (zoom >= editor.zoom_max) {
        $(".fa-search-plus").css({
            "pointer-events": "none",
            "opacity": 0.5
        })
    } else {
        $(".fa-search-plus").css({
            "pointer-events": "auto",
            "opacity": 1
        })
    }

    if (zoom <= editor.zoom_min) {
        $(".fa-search-minus").css({
            "pointer-events": "none",
            "opacity": 0.5
        })
    } else {
        $(".fa-search-minus").css({
            "pointer-events": "auto",
            "opacity": 1
        })
    }
})

editor.node_style = 'Vertical';

editor.curvature = 0;
editor.reroute_curvature_start_end = 0;
editor.reroute_curvature = 0;

editor.curvature = 0;
editor.reroute_curvature_start_end = 0;
editor.reroute_curvature = 0;

var elements = document.getElementsByClassName('drag-drawflow');
for (let i = 0; i < elements.length; i++) {
    elements[i].addEventListener('touchend', drop, false);
    elements[i].addEventListener('touchmove', positionMobile, false);
    elements[i].addEventListener('touchstart', drag, false);
}

var mobile_item_selec = '';
var mobile_last_move = null;

function positionMobile(ev) {
    mobile_last_move = ev;
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    if (ev.type === "touchstart") {
        mobile_item_selec = ev.target.closest(".drag-drawflow").getAttribute('data-node');
    } else {
        ev.dataTransfer.setData("node", ev.target.getAttribute('data-node'));
    }
}

function drop(ev) {
    if (ev.type === "touchend") {
        let parentdrawflow = document.elementFromPoint(mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY).closest("#drawflow");
        if (parentdrawflow != null) {
            addNodeToDrawFlow(mobile_item_selec, mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY);
        }
        mobile_item_selec = '';
    } else {
        ev.preventDefault();
        let data = ev.dataTransfer.getData("node");
        addNodeToDrawFlow(data, ev.clientX, ev.clientY);
    }

}

var transform = '';

function showpopup(e) {
    e.target.closest(".drawflow-node").style.zIndex = "9999";
    e.target.children[0].style.display = "block";
    //document.getElementById("modalfix").style.display = "block";

    //e.target.children[0].style.transform = 'translate('+translate.x+'px, '+translate.y+'px)';
    transform = editor.precanvas.style.transform;
    editor.precanvas.style.transform = '';
    editor.precanvas.style.left = editor.canvas_x + 'px';
    editor.precanvas.style.top = editor.canvas_y + 'px';

    //e.target.children[0].style.top  =  -editor.canvas_y - editor.container.offsetTop +'px';
    //e.target.children[0].style.left  =  -editor.canvas_x  - editor.container.offsetLeft +'px';
    editor.editor_mode = "fixed";

}

function closemodal(e) {
    e.target.closest(".drawflow-node").style.zIndex = "2";
    e.target.parentElement.parentElement.style.display = "none";
    //document.getElementById("modalfix").style.display = "none";
    editor.precanvas.style.transform = transform;
    editor.precanvas.style.left = '0px';
    editor.precanvas.style.top = '0px';
    editor.editor_mode = "edit";
}

function changeModule(event) {
    let all = document.querySelectorAll(".menu ul li");
    for (let i = 0; i < all.length; i++) {
        all[i].classList.remove('selected');
    }
    event.target.classList.add('selected');
}

function changeMode(option) {

    if (option == 'lock') {
        lock.style.display = 'none';
        unlock.style.display = 'block';
    } else {
        lock.style.display = 'block';
        unlock.style.display = 'none';
    }

}

function show_node_action_options(ele) {

    ele.nextElementSibling.style.display = "block";

}

function hide_right_nav_menu() {
    $(".easychat-edit-intent-rightnav-menu-wrapper").hide()
    $(".easychat-edit-intent-preview-wrapper").hide()
    hide_details_wrapper()
    $(".trumbowyg-modal-reset").click()
}

$('#select-intent-category').change(function() {
   is_category_changed = true;
})