self.importScripts(self.location.protocol + '//' + self.location.host + "/static/EasyChatApp/js/FuzzySearch.js" );

var fuzzyhound = ""
var is_indexed_db_supported = true;
var db;
var db_name = "suggestion_list"
var table_name = "suggestion_list_table"
var table_index = "suggestion_list_key"
var is_db_reinitalized = false

self.onmessage = function (event) {
    var data = JSON.parse(event.data)
    
    if (data.id == 'initialize') {
        open_local_db();
    } else if (data.id == 'search') {

        var result = search_for_suggestion(data.value);
        postMessage(JSON.stringify({
            id: 'search_res',
            value: result,
        }));
    }
}

function initialize_fuzzy_search(suggestion_list) {
    fuzzyhound = new FuzzySearch({output_limit: 20, output_map:"alias"});
    fuzzyhound.setOptions({
        source: suggestion_list,
        keys: ["key"],
        score_test_fused: true,
        score_per_token: true,
        score_acronym:true,
    })
}

function search_for_suggestion(val) {
    if(!fuzzyhound.source){
        get_messages_from_local() 
    }
    fuzzyhound.search(val)
    results_fuzzy = fuzzyhound.results
    results_fuzzy.sort(function (first, second) {
        return second["_item"]["count"] - first["_item"]["count"];
    });

    return results_fuzzy;
}

/* Index DB */

function open_local_db() {
    self.indexedDB = self.indexedDB || self.mozIndexedDB || self.webkitIndexedDB || self.msIndexedDB;
    self.IDBTransaction = self.IDBTransaction || self.webkitIDBTransaction || self.msIDBTransaction || { READ_WRITE: "readwrite" };
    self.IDBKeyRange = self.IDBKeyRange || self.webkitIDBKeyRange || self.msIDBKeyRange;

    if (!self.indexedDB) {
        console.log("Your browser doesn't support a stable version of IndexedDB.");
        is_indexed_db_supported = false;
        return;
    }

    var openRequest = self.indexedDB.open(db_name, 1);

    openRequest.onerror = function () {
        is_indexed_db_supported = false
        console.error("Error", openRequest.error);
    };

    openRequest.onsuccess = function (event) {
        db = event.target.result;
        get_messages_from_local()
    };
}

function get_object_store(store_name, mode) {
    try {
        var tx = db.transaction(store_name, mode);
        return tx.objectStore(store_name);
    } catch (err) {
        console.log(err);
        return -1
    }
}

function update_suggestion_list(){
    if(is_db_reinitalized){
        return
    }
    postMessage(JSON.stringify({
        id: 'check_and_update_suggestion_list',
        value: "suggestion_list_empty_need_to_update_index_db",
    }));
    is_db_reinitalized = true
}

function get_messages_from_local() {
    try {
        var suggestion_list_store = get_object_store(table_name, 'readwrite');
        var index = suggestion_list_store.index('table_index');
        var key = IDBKeyRange.only(table_index);
        var data = []
        index.openCursor(key, "next").onsuccess = function (event) {
            var cursor = event.target.result;
            if (cursor) {
                is_data_present = true;
                data.push(cursor.value)
                cursor.continue();
                suggestion_list = data[0]['suggestion_list']
                initialize_fuzzy_search(suggestion_list);
            }else if(cursor==null){
                update_suggestion_list()
            }
        };
    } catch (err) {
        console.log(err);
    }
}