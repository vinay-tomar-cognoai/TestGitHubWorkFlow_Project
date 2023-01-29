window.onload = function() {

    $('a[target="_blank"]').each(function(){
       $(this).removeAttr('target');
    });
}
