import { get_session_id, get_agent_username, check_is_email_session } from "./console";
import {
    set_chat_data,
    get_customer_details,
    get_chat_info,
    get_chat_history,
    set_chat_history,
    get_suggestion_list,
    set_end_chat_closing_category,
    append_message_history,
    return_time,
    get_chat_data,
} from "./chatbox";
import { create_websocket } from "./livechat_chat_socket";

const state = {
    index_db: {
        version: 4,
        supported: true,
        instance: null,
        name: "livechat_message_history_database",
        store: {
            message_history: {
                name: "message_history_store",
                data_present: false,
            },
            chat_info: {
                name: "chat_info_store",
            },
            customer_details: {
                name: "customer_details_store",
            },
            translated_messages: {
                name: "translated_messages_store",
            },
        },
    },
};

function open_local_db() {
    const index_db = state.index_db;

    let indexedDB =
        window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
    let IDBTransaction = window.IDBTransaction ||
        window.webkitIDBTransaction ||
        window.msIDBTransaction || { READ_WRITE: "readwrite" };
    let IDBKeyRange = window.IDBKeyRange || window.webkitIDBKeyRange || window.msIDBKeyRange;

    Object.defineProperty(window, "indexedDB", {
        value: indexedDB,
    });

    Object.defineProperty(window, "IDBTransaction", {
        value: IDBTransaction,
    });

    Object.defineProperty(window, "IDBKeyRange", {
        value: IDBKeyRange,
    });

    const session_id = get_session_id();
    if (!window.indexedDB) {
        console.log("Your browser doesn't support a stable version of IndexedDB.");
        index_db.supported = false;

        document.getElementById(`style-2_${session_id}`).innerHTML =
            '<p id="livechat-chat-loader" style="margin: 30% auto; text-align: center; width: 50%;">Loading chat...</p>';
        return;
    }

    var openRequest = window.indexedDB.open(index_db.name, index_db.version);

    openRequest.onerror = function () {
        state.index_db.supported = false;
        console.error("Error", openRequest.error);
    };

    openRequest.onsuccess = function (event) {
        state.index_db.instance = event.target.result;
    };

    openRequest.onupgradeneeded = function (event) {
        state.index_db.instance = event.target.result;

        switch (event.oldVersion) {
            case 0:
                //when user has no database
                let message_history = index_db.instance.createObjectStore(
                    index_db.store.message_history.name,
                    { autoIncrement: true }
                );
                message_history.createIndex("session_id", "session_id", { unique: false });

            case 1:
                let chat_info = state.index_db.instance.createObjectStore(index_db.store.chat_info.name, {
                    autoIncrement: true,
                });
                chat_info.createIndex("session_id", "session_id", { unique: false });

                let customer_details = state.index_db.instance.createObjectStore(
                    index_db.store.customer_details.name,
                    { autoIncrement: true }
                );
                customer_details.createIndex("session_id", "session_id", { unique: false });

            case 2:
                let translated_messages = index_db.instance.createObjectStore(
                    index_db.store.translated_messages.name,
                    { autoIncrement: true }
                );
                translated_messages.createIndex("message_id", ["message_id", "language"], { unique: true });

            case 3:
                const txn = event.target.transaction;
                let message_history_store = txn.objectStore(index_db.store.message_history.name);

                const delete_req = message_history_store.clear();

                delete_req.onsuccess = () => {
                    message_history_store.createIndex("message_id", "message_id", { unique: true });
                }
        }
    };
}

function get_object_store(store_name, mode) {
    var tx = state.index_db.instance.transaction(store_name, mode);
    return tx.objectStore(store_name);
}

function save_message_to_local(msg_obj) {

    var session_id = msg_obj.hasOwnProperty("session_id")
        ? msg_obj.session_id
        : get_session_id();

    // no need to store email chat data in indexdb
    if(check_is_email_session(session_id)) return;

    var attached_file_src = msg_obj.hasOwnProperty("attached_file_src")
        ? msg_obj.attached_file_src
        : "";

    var message = msg_obj.hasOwnProperty("message") ? msg_obj.message : "";

    var sender = msg_obj.hasOwnProperty("sender") ? msg_obj.sender : "";

    var sender_name = msg_obj.hasOwnProperty("sender_name") ? msg_obj.sender_name : "";

    var file = msg_obj.hasOwnProperty("file") ? msg_obj.file : "";

    var time = return_time();
    var time_in_millisecond = Date.parse(new Date());

    var is_guest_agent_message = msg_obj.hasOwnProperty("is_guest_agent_message") ? msg_obj.is_guest_agent_message : false;

    var sender_username = msg_obj.hasOwnProperty("sender_username") ? msg_obj.sender_username : "";

    var message_id = msg_obj.hasOwnProperty("message_id") ? msg_obj.message_id : "";

    var reply_message_id = msg_obj.hasOwnProperty("reply_message_id") ? msg_obj.reply_message_id : "";

    var language = msg_obj.hasOwnProperty("language") ? msg_obj.language : "en";

    var is_voice_call_message = msg_obj.hasOwnProperty("is_voice_call_message") ? msg_obj.is_voice_call_message : false;

    var is_video_call_message = msg_obj.hasOwnProperty("is_video_call_message") ? msg_obj.is_video_call_message : false;

    var message_for = msg_obj.hasOwnProperty("message_for") ? msg_obj.message_for : "";

    var is_cobrowsing_message = msg_obj.hasOwnProperty("is_cobrowsing_message") ? msg_obj.is_cobrowsing_message : false;

    var is_customer_warning_message = msg_obj.hasOwnProperty("is_customer_warning_message") ? msg_obj.is_customer_warning_message : false;

    var is_customer_report_message_notification = msg_obj.hasOwnProperty("is_customer_report_message_notification") ? msg_obj.is_customer_report_message_notification : false;

    let message_obj = {
        attached_file_src: attached_file_src,
        message: message,
        sender: sender,
        sender_name: sender_name,
        session_id: session_id,
        time: time,
        time_in_minisec: time_in_millisecond,
        file: file,
        is_guest_agent_message: is_guest_agent_message,
        sender_username: sender_username,
        message_id: message_id,
        reply_message_id: reply_message_id,
        is_voice_call_message: is_voice_call_message,
        is_video_call_message: is_video_call_message,
        is_cobrowsing_message: is_cobrowsing_message,
        message_for: message_for,
        language: language,
        is_customer_warning_message: is_customer_warning_message,
        is_customer_report_message_notification: is_customer_report_message_notification,
    };

    let chat_history = get_chat_history();
    if (chat_history[session_id] != undefined) {
        chat_history[session_id].push(message_obj);
        set_chat_history(chat_history);
    }

    if (state.index_db.supported) {
        add_message_to_local_db(message_obj, state.index_db.store.message_history.name);
    }

    // This will save the message with original language coming from the customer side

    if(localStorage.getItem('is_virtual_interpretation_enabled') == "true") {

        if(localStorage.getItem(`is_translated-${session_id}`) == "true") {

            let translated_message_obj = {
                message_id: message_id,
                language: language,
                message: message,
                session_id: session_id,
                sender_username: sender_username,
            };
            if (state.index_db.supported) {
                add_translated_message_to_local_db(translated_message_obj, state.index_db.store.translated_messages.name);
            }
        }

        if(sender_username != "" && sender == "Agent") {
            localStorage.setItem(`guest_agent_language-${sender_username}-${session_id}`, language);
        }
    }
}

function add_translated_message_to_local_db(data, db_name) {
    var db_obj = get_object_store(db_name, "readwrite");

    if(!data.message_id || !data.language)
        return;

    var req = db_obj.get([data.message_id, data.language]);

    req.onsuccess = function () {
        db_obj.put(data, [data.message_id, data.language]);
    };
    req.onerror = function () {
        db_obj.add(data, data);
    };   
}

function add_message_to_local_db(data, db_name) {
    var db_obj = get_object_store(db_name, "readwrite");
    var req;

    try {
        req = db_obj.add(data);
    } catch (error) {
        console.log(error);
    }

    req.onsuccess = function (evt) {
        console.log("saved data to local db!");
    };
    req.onerror = function () {
        console.error("error in saving data to local db: ", this.error);
    };
}

function delete_messages_from_local(db_name) {
    var message_history = get_object_store(db_name, "readwrite");

    var index = message_history.index("session_id");
    var key = IDBKeyRange.only(get_session_id());
    index.openCursor(key, "next").onsuccess = function (event) {
        var cursor = event.target.result;
        if (cursor) {
            let request = cursor.delete();

            request.onsuccess = function () {
                console.log("deleted message successfully!");
            };

            cursor.continue();
        }
    };
    delete_translated_messages_from_local(); 
}

function delete_translated_messages_from_local() {
    var message_history = get_object_store(state.index_db.store.translated_messages.name, "readwrite");    

    const session_id = get_session_id();
    var cursorRequest = message_history.openCursor();
    cursorRequest.onsuccess = function (event){
        var cursor = event.target.result;
        if (cursor){
            if(event.target.result.value["session_id"] == session_id){ //compare values
                let request = cursor.delete();
                request.onsuccess = function () {
                    console.log("deleted message successfully!");
                };
            }
            cursor.continue();
        }
    };
}

function get_messages_from_local() {
    const index_db = state.index_db;
    const session_id = get_session_id();
    let chat_history = get_chat_history();
    if (chat_history[session_id] != undefined) {
        index_db.store.message_history.data_present = true;
        return;
    }

    let index_db_supported = !localStorage.getItem(`index_db_supported-${session_id}`) ? "false" : index_db_supported;
    if (index_db_supported == "false") {
        index_db.store.message_history.data_present = false;
        index_db.supported = false;
        return;
    }

    try {
        var message_history = get_object_store(index_db.store.message_history.name, "readwrite");

        var index = message_history.index("session_id");
        var key = IDBKeyRange.only(session_id);
        var data = [];
        index.openCursor(key, "next").onsuccess = function (event) {
            var cursor = event.target.result;
            if (cursor) {
                index_db.store.message_history.data_present = true;
                data.push(cursor.value);
                cursor.continue();
            } else {
                if (data.length > 0) {
                    chat_history[session_id] = data;
                    set_chat_history(chat_history);
                    append_message_history(data);
                } else {
                    index_db.store.message_history.data_present = false;
                    document.getElementById(`style-2_${session_id}`).innerHTML =
                        '<p id="livechat-chat-loader" style="margin: 30% auto; text-align: center; width: 50%;">Loading chat...</p>';
                }
            }
        };
    } catch (err) {
        console.log(err);
        index_db.store.message_history.data_present = false;
        index_db.supported = false;
        localStorage.setItem(`index_db_supported-${session_id}`, false);
        document.getElementById(`style-2_${session_id}`).innerHTML =
            '<p id="livechat-chat-loader" style="margin: 30% auto; text-align: center; width: 50%;">Loading chat...</p>';
    }
}

function get_chat_info_from_local() {
    let session_id = get_session_id();
    const index_db = state.index_db;

    // Bypassing the local db support
    /*
    let index_db_supported = localStorage.getItem(`index_db_supported-${session_id}`);
    if (index_db_supported == "false" || true) {
        index_db.store.message_history.data_present = false;
        index_db.supported = false;
        get_chat_info(session_id);
        return;
    }
    */

    index_db.store.message_history.data_present = false;
    index_db.supported = false;
    get_chat_info(session_id);
    return;

    try {
        var chat_info = get_object_store(state.index_db.store.chat_info.name, "readwrite");

        var index = chat_info.index("session_id");
        var key = IDBKeyRange.only(session_id);
        var data = [];
        index.openCursor(key, "next").onsuccess = function (event) {
            var cursor = event.target.result;
            if (cursor) {
                index_db.store.message_history.data_present = true;
                data.push(cursor.value);
                cursor.continue();
            } else {
                if (data.length > 0) {
                    data = data[0];

                    const {
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
                        raise_ticket_form
                    } = data;

                    set_chat_data(
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
                        raise_ticket_form
                    );

                    if (category_enabled == false) {
                        document.getElementById("closing-category-div").style.display = "none";
                    }

                    document.getElementById("livechat-customer-name").innerHTML = customer_name;

                    create_websocket();
                    get_suggestion_list();
                    set_end_chat_closing_category();
                } else {
                    index_db.store.message_history.data_present = false;
                    get_chat_info(session_id);
                }
            }
        };
    } catch (err) {
        console.log(err);
        index_db.store.message_history.data_present = false;
        index_db.supported = false;
        localStorage.setItem(`index_db_supported-${session_id}`, false);
        get_chat_info(session_id);
    }
}

function get_customer_details_from_local() {
    const index_db = state.index_db;
    const session_id = get_session_id();
    let index_db_supported = !localStorage.getItem(`index_db_supported-${session_id}`) ? "false" : index_db_supported;
    if (index_db_supported == "false") {
        index_db.store.message_history.data_present = false;
        index_db.supported = false;
        return;
    }

    try {
        let customer_details = get_object_store(state.index_db.store.customer_details.name, "readwrite");

        let index = customer_details.index("session_id");
        let key = IDBKeyRange.only(session_id);
        let data = [];
        index.openCursor(key, "next").onsuccess = function (event) {
            let cursor = event.target.result;
            if (cursor) {
                index_db.store.message_history.data_present = true;
                data.push(cursor.value);
                cursor.continue();
            } else {
                if (data.length > 0) {
                    data = data[0];
                    get_customer_details(data);
                } else {
                    index_db.store.message_history.data_present = false;
                }
            }
        };
    } catch (err) {
        console.log(err);
        index_db.store.message_history.data_present = false;
        index_db.store.supported = false;
        localStorage.setItem(`index_db_supported-${session_id}`, false);
    }
}

export function update_customer_details_in_local(data) {
    const db_names = ["chat_info_store", "customer_details_store"];
    const session_id = get_session_id();
    try {
        db_names.forEach(db_name => {
            var db_obj = get_object_store(db_name, "readwrite");
            var cursorRequest = db_obj.openCursor();
            cursorRequest.onsuccess = function (event){
                var cursor = event.target.result;
                if (cursor){
                    if(event.target.result.value["session_id"] == session_id){ //compare values
                        if(db_name == 'chat_info_store'){
                            let updateData = cursor.value;
                            updateData.customer_name = data.name;
                            let request = cursor.update(updateData);
                            request.onsuccess = function () {
                                console.log("chat_info_store updated");
                            };
                        } else if(db_name == 'customer_details_store'){
                            let updateData = cursor.value;
                            updateData.name = data.name;
                            updateData.email = data.email;
                            updateData.phone = data.phone;
                            updateData.phone_country_code = data.phone_country_code;
                            let request = cursor.update(updateData);
                            request.onsuccess = function () {
                                console.log("customer_details_store updated");
                            };
                        }
                    }
                cursor.continue();
                }
            };
        });
    } catch (error) {
        console.log(error);
    }
}

export function empty_local_db () {
    const db_names = ["chat_info_store", "customer_details_store", "message_history_store"];

    db_names.forEach(db => {
        const object = get_object_store(db, "readwrite");

        const req = object.clear();
    
        req.onsuccess = function(event) {
            console.log('all data deleted successfully');
        };
    })
}

function set_data_present(val) {
    state.index_db.store.message_history.data_present = val;
}

function get_data_present() {
    return state.index_db.store.message_history.data_present;
}

function get_message_history_store() {
    return state.index_db.store.message_history;
}

function get_customer_details_store() {
    return state.index_db.store.customer_details;
}

function get_chat_info_store() {
    return state.index_db.store.chat_info;
}

function get_translated_messages_store() {
    return state.index_db.store.translated_messages;
}

function is_indexed_db_supported() {
    return false;
    // return state.index_db.supported == true;
}

export {
    open_local_db,
    get_chat_info_from_local,
    get_messages_from_local,
    get_customer_details_from_local,
    set_data_present,
    get_data_present,
    get_message_history_store,
    get_customer_details_store,
    get_chat_info_store,
    add_message_to_local_db,
    is_indexed_db_supported,
    save_message_to_local,
    delete_messages_from_local,
    add_translated_message_to_local_db,
    get_translated_messages_store,
    get_object_store,
};