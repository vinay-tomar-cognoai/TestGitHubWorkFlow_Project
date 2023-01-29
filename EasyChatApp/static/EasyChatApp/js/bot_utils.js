(function (exports) {

    function set_target_blank() {

        var a = document.getElementsByTagName('a'); // Grab every link in the bot
        for (var i = 0; i < a.length; i++) {

        	a_href = a[i].getAttribute("href");
        	if(a_href == "#" || a_href == "Javascript:void(0)" || a_href == null || a_href ==  undefined) {

        		continue;
        	}
            a[i].setAttribute('target', '_blank');
        }
    }
    
    exports.set_target_blank = set_target_blank;  

})(window)