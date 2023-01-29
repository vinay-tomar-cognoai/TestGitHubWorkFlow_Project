function resize_iframe(){
    var frame_div = document.getElementById("cognoai-iframe-div");
    frame_div.style.width = window.innerWidth + "px";
    frame_div.style.height = window.innerHeight + "px";

    var frame_div = document.getElementById("cognoai-iframe");
    frame_div.style.width = window.innerWidth + "px";
    frame_div.style.height = window.innerHeight + "px";
}

window.onresize = resize_iframe;
resize_iframe();

var cognoai_iframe = null;

// function cognoai_iframe_onload(){
//     console.log("cognoai_iframe_onload");
//     cognoai_iframe = document.getElementById("cognoai-iframe");
//     cognoai_iframe_contentdocument = cognoai_iframe.contentDocument;
//     // var head_element = cognoai_iframe_contentdocument.querySelector('head');
//     // var base_element = cognoai_iframe_contentdocument.createElement('BASE');
//     // base_element.href = "http://127.0.0.1:8000/easy-assist/cognoai-cobrowse/page-render/"
//     // head_element.appendChild(base_element);

//     cognoai_iframe_content_window = cognoai_iframe.contentWindow;
//     var proxied = cognoai_iframe_content_window.XMLHttpRequest.prototype.open;
//     cognoai_iframe_content_window.XMLHttpRequest.prototype.open = function(method, url, ...rest) {
//         console.log(url, method);

//         if(url.length && url[0] == '/') {
//             url = url.substr(1)
//         }
//         url = "http://127.0.0.1:8000/easy-assist/cognoai-cobrowse/page-render/" + url

//         console.log("new url = ", url)
//         return proxied.call(this,method, url, ...rest);
//     };
//     console.log("abcdefaldsjf")
// }

// cognoai_iframe_onload();