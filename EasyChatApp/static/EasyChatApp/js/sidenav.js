function remove_all_other_active_collapsed_sidebar_menu() {
    $('.collabsible-sidebar-menu').each(function() {
        if ($(this).hasClass('collabsible-sidebar-menu-active')) {
            $(this).next().slideUp(700);
            $(this).removeClass('collabsible-sidebar-menu-active');
        }
    })
}

$('.collabsible-sidebar-menu').click(function(e) {

    var sidebar_section = $('#easychat-sidenav-wrapper');
    var sidebar_width = sidebar_section.width();

    if (sidebar_width > 90) {
        if ($(this).hasClass('collabsible-sidebar-menu-active') === false) {
            remove_all_other_active_collapsed_sidebar_menu();
        }
        $(this).next().slideToggle(700);
        $(this).toggleClass('collabsible-sidebar-menu-active');
        // console.log($(this).next(".collapsed-section-content"));

    }


});


// $('.collapsed-section-item').click(function(e) {
//     e.stopPropagation();
//     $('.collapsed-section-item').each(function() {
//         $(this).removeClass('collapsed-item-active')
//     })

//     $(this).addClass('collapsed-item-active');

//     var sidebar_section = $('#easychat-sidenav-wrapper');
//     var sidebar_width = sidebar_section.width();

//     if (sidebar_width < 90) {
//         $('.collapsed-section-item').each(function() {
//             $(this).parent().parent().siblings(".sidebar-menu-item").removeClass('uncollapsed-item-active');
//         })
//         $(this).parent().parent().siblings(".sidebar-menu-item").addClass("uncollapsed-item-active");
//     }


// })


$('.collapse-expand-sidebar-div').click(function() {
    $(this).toggleClass('collapsed')

    $(".collapsed-section-content").css("display", "none");

    // setTimeout(function() {
    //     var sidebar_section = $('#easychat-sidenav-wrapper');
    //     var sidebar_width = sidebar_section.width();
    //     if (sidebar_width < 90) {

    //         if ($(".collabsible-sidebar-menu").hasClass('collabsible-sidebar-menu-active') === true) {
    //             remove_all_other_active_collapsed_sidebar_menu();
    //         }
    //         $('.collapsed-section-item').each(function() {
    //             $(".collapsed-section-item").parent().parent().siblings(".sidebar-menu-item").removeClass('uncollapsed-item-active');
    //         })
    //         $(".collapsed-item-active").parent().parent().siblings(".sidebar-menu-item").addClass("uncollapsed-item-active");
    //     }
    // }, 100);

    elements = document.getElementsByClassName("collapsed-section-href");
  for(var index=0; index<elements.length; index++){
     if(elements[index].href!=undefined){
        elements[index].classList.remove("collapsed-item-active");
        $(elements[index]).parent().prev().removeClass("uncollapsed-item-active");
     }
  }

  for(var index=0; index<elements.length; index++){
     if(elements[index].href!=undefined && window.location.href.indexOf(elements[index].href)!=-1){
        elements[index].classList.add("collapsed-item-active");
        $(elements[index]).parent().prev().addClass("uncollapsed-item-active");
        break;
     }
  }


    $('#easychat-sidenav-wrapper').toggleClass('collapsed', 1000)

    $('.expanded-logo').toggle();
    $('.collapsed-logo').toggle();
    $('.easychat-botname-wrapper').toggleClass('tooltipped')
    if ($('.easychat-botname-wrapper').hasClass('tooltipped'))
        $('.tooltipped').tooltip();
    else
        $('.easychat-botname-wrapper').tooltip('destroy');

})