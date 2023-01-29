var count_of_chunk = 0
var total_length_of_chunk = 0
var suggestion_list = []
var suggestion_db;
var db_name = "suggestion_list"
var table_name = "suggestion_list_table"
var table_index = "suggestion_list_key"
var is_get_suggestion_going_on = false
////////////////////////////////// utility function starts  ////////////////////////////////////// 

function get_time_in_seconds_from_datetime(date_time){

    let date = new Date(date_time)
    let seconds = Math.floor(date.getTime() / 1000);

    return seconds
}

function are_suggestions_to_be_fetched_from_server(){

    let last_bot_time_from_server = get_time_in_seconds_from_datetime(BOT_LAST_UPDATED_TIME)
    
    if(last_bot_time_from_server != get_cookie('last_bot_updated_time')){
        count_of_chunk = 0
        return true
    }

    return false
}

function open_local_suggestion_db() {

    window.indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
    window.IDBTransaction = window.IDBTransaction || window.webkitIDBTransaction || window.msIDBTransaction || {READ_WRITE: "readwrite"};
    window.IDBKeyRange = window.IDBKeyRange || window.webkitIDBKeyRange || window.msIDBKeyRange;

    if (!window.indexedDB) {
        console.log("Your browser doesn't support a stable version of IndexedDB.");
        is_indexed_db_supported = false;
        return;
    }
    var openRequest = window.indexedDB.open(db_name, 1);

    openRequest.onerror = function () {
        is_indexed_db_supported = false        
        console.error("Error", openRequest.error);
    };

    openRequest.onsuccess = function (event) {
        suggestion_db = event.target.result; 
    };
    openRequest.onupgradeneeded = function (event) {
        suggestion_db = event.target.result;
        switch (event.oldVersion) {
            case 0:
                //when user has no database
                // for debugging
                console.log("new suggestion index db is cretaed now ")
                suggestion_list_store = suggestion_db.createObjectStore(table_name, { autoIncrement: true });
                suggestion_list_store.createIndex('table_index', 'table_index', { unique: false });
        }
    };

}

function load_storage(){
    try {
        if (window.localStorage['word_mapper_list'] != null) {
            window.localStorage.removeItem('word_mapper_list');
            window.localStorage.removeItem('autocorrect_bot_replace')
        }
    } catch (error) {
        console.log(error)
    }
    
    delete_suggestions_from_local_db(table_name)
    open_local_suggestion_db()
}

function custom_decrypt(msg_string) {

    var payload = msg_string.split(".");
    var key = payload[0];
    var decrypted_data = payload[1];
    var decrypted = EasyChatCryptoJS.AES.decrypt(decrypted_data, EasyChatCryptoJS.enc.Utf8.parse(key), { iv: EasyChatCryptoJS.enc.Base64.parse(payload[2]) });
    return decrypted.toString(EasyChatCryptoJS.enc.Utf8);
}



function get_suggestion_object_store(store_name, mode) {
    try{
        var tx = suggestion_db.transaction(store_name, mode);
        return tx.objectStore(store_name);
    }catch(err){
        console.log(err)
        return -1
    }
}

function add_suggestions_to_local_db(data, store_name) {
    var db_obj = get_suggestion_object_store(store_name, 'readwrite');
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

function delete_suggestions_from_local_db(store_name) {
    var suggestion_list_store = get_suggestion_object_store(store_name, 'readwrite');
    if(suggestion_list_store != -1){
        var index = suggestion_list_store.index('table_index');
        var key = IDBKeyRange.only(table_index);
        index.openCursor(key, "next").onsuccess = function (event) {
            var cursor = event.target.result;
            if (cursor) {
                request = cursor.delete();

                request.onsuccess = function() {
                    console.log('deleted message successfully!');
                }
                cursor.continue();
            }
        };
    }
}

function get_suggestions_from_server() {

    var json_string = JSON.stringify({
        bot_id: BOT_ID,
        count_of_chunk: count_of_chunk
    });
    json_string = encrypt_variable(json_string);
    json_string = encodeURIComponent(json_string);
    is_get_suggestion_going_on = true
    var xhttp = new XMLHttpRequest();
    var params = 'json_string=' + json_string
    xhttp.open("POST", "/chat/get-data-suggestions/", true);
    xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            response = JSON.parse(this.responseText);
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                suggestion_list_response = JSON.parse(response["sentence_list"]);
                word_mapper_list = JSON.parse(response["word_mapper_list"]);
                total_length_of_chunk = response["total_length_of_chunk"]
                suggestion_list = suggestion_list.concat(suggestion_list_response)
                delete_suggestions_from_local_db(table_name)
                suggestion_list_dict = {
                    'table_index': table_index,
                    'suggestion_list': suggestion_list,
                }
                add_suggestions_to_local_db(suggestion_list_dict,table_name)
                window.localStorage['word_mapper_list'] = JSON.stringify(word_mapper_list)
                count_of_chunk = count_of_chunk + 1
                if (total_length_of_chunk > 1 && count_of_chunk != total_length_of_chunk){
                    // adding some delay in the api calls to try to minimize the very frequent load on the server
                    setTimeout(function(){
                        get_suggestions_from_server()
                    }, 2000)
                }
                is_get_suggestion_going_on = false
            }else{
                console.log("Error in getting suggestions")
                is_get_suggestion_going_on = false
            }
        }
    }
    xhttp.send(params);
}

$( document ).ready(function() {    

    load_storage();
    if (are_suggestions_to_be_fetched_from_server()){
        get_suggestions_from_server();
    }
    set_cookie("last_bot_updated_time", get_time_in_seconds_from_datetime(BOT_LAST_UPDATED_TIME))

});

(function (exports) {

    function check_and_get_suggestions_in_index_db(){
        if(is_get_suggestion_going_on){
            return
        }
        count_of_chunk = 0
        get_suggestions_from_server()
            
    }
    
    exports.check_and_get_suggestions_in_index_db = check_and_get_suggestions_in_index_db;  
})(window)
//////////////////////////////// utility function ends //////////////////////////////////