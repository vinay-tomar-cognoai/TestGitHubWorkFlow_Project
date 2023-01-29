(function ($) {
    $.fn.scrollTo = function (elem, speed) {
        $(this).animate({
            scrollTop: $(this).scrollTop() - $(this).offset().top + $(elem).offset().top
        }, speed == undefined ? 1000 : speed);
        return this;
    };
    $.fn.njTimepick = function () {
        init(this);
        function init(timeInputs) {
            let totalTimeInputs = timeInputs.length,
                timeInput = undefined,
                type = undefined,
                i = 0;
            for (i; i < totalTimeInputs; i++) {
                timeInput = $(timeInputs[i]);
                type = timeInput.attr('type');
                if (type === 'text') {
                    timeInput.addClass('nj-timepick-input');
                    settings(timeInput);
                }
                else console.log('Element is not of type time');
            }
            /******** Settings for each input******/
            function settings(timeInput) {
                createPopup(timeInput);
                popupSettings();
                timeInputClickEvent(timeInput);
                timeInputChangeEvent(timeInput);
                validateTimeOnChange(timeInput)
            }
            function createPopup() {
                let popupPresent = $('.nj-timepick').length > 0;
                if (popupPresent) return; // return immediately if popup is present
                let template = '\
                                    <div class="nj-timepick"> \
                                        <div class="nj-timepick__panel">\
                                        <div>\
                                            <div class="nj-timepick-heading">\
                                                '+"Choose a time"+'\
                                            </div>\
                                        </div>\
                                        <div class="nj-timepick__container">\
                                            <div class="nj-timepick__boxes-column nj-timepick__hours">\
                                            '+ createBoxes("hours", 1, 12, 1, "hour") + '\
                                            </div>\
                                            <div class="nj-timepick__boxes-column nj-timepick__minutes">\
                                                    '+ createBoxes("minutes", 0, 59, 0, "minute") + '\
                                            </div>\
                                            <div class="nj-timepick__boxes-column nj-timepick__meridians">\
                                            <div val="AM" class="nj-timepick__box nj-timepick__meridian  nj-timepick__box--active">AM</div>\
                                            <div val="PM" class="nj-timepick__box nj-timepick__meridian">PM</div>\
                                            </div>\
                                        </div>\
                                ';
                $('body').append(template);
                /* Create hours and minute boxes */
                function createBoxes(type, start, end, activateDigit, boxClass) {
                    let template = '<div class="nj-timepick__boxes nj-timepick__' + type + '-boxes">';
                    for (start; start <= end; start++) {
                        activeClass = start === activateDigit ? "nj-timepick__box--active " : "";
                        value = ('0' + start).slice(-2);
                        template += '\
                                      <div val="'+ value + '" class=" ' + activeClass + 'nj-timepick__box nj-timepick__' + boxClass + '">\
                                        '+ value + '\
                                      </div>\
                                   ';
                    }
                    template += '</div>';
                    return template;
                }
            }
            function popupSettings() {
                setTimeout(function () {
                    let njTimePick = $('.nj-timepick');
                    timeClick();
                    popupOutsideClick();
                    function timeClick() {
                        njTimePick.find('.nj-timepick__box').on('click', function () {
                            let box = $(this),
                                value = box.text().trim();
                            box.addClass('nj-timepick__box--active')
                                .siblings()
                                .removeClass('nj-timepick__box--active');
                            setTimeout(function () { setTime() }, 200);
                        });
                        function setTime() {
                            let hourActive = njTimePick.find('.nj-timepick__hours .nj-timepick__box--active'),
                                minuteActive = njTimePick.find('.nj-timepick__minutes .nj-timepick__box--active'),
                                meridianActive = njTimePick.find('.nj-timepick__meridians .nj-timepick__box--active'),
                                hourValue = hourActive.text().trim(),
                                minuteValue = minuteActive.text().trim(),
                                meridianValue = meridianActive.text().trim(),
                                timeIn24hr = to24hrFormat(hourValue, minuteValue, meridianValue);
                                const time = moment(timeIn24hr, "HH:mm");
                                const hrformattedTime = time.format("hh:mm A");
                                $(".nj-timepick__hours-boxes").scrollTo(hourActive, 100);
                                $(".nj-timepick__minutes-boxes").scrollTo(minuteActive, 100);
                                $('.nj-timepick-input--active').val(hrformattedTime);
                                $('.nj-timepick-input--active').addClass('active-picker-input')
                        }
                    }
                    function popupOutsideClick() {
                        $(document).mouseup(function (e) {
                            let container = njTimePick.find('.nj-timepick__panel');
                            // if the target of the click isn't the container nor a descendant of the container
                            if (!container.is(e.target) && container.has(e.target).length === 0) {
                                $('.nj-timepick-input--active').removeClass('nj-timepick-input--active');
                                njTimePick.removeClass('nj-timepick--active');
                            }
                        });
                    }

                    $(window).on('resize', function(){
                        njTimePick.removeClass('nj-timepick--active');
                    })

                }, 500);
            }
            function timeInputClickEvent(timeInput) {
                timeInput.on('click', function () {
                    let top_position = timeInput.offset().top
                    let left_position = timeInput.offset().left
                    let input_height = timeInput.height()
                    let popup = $('.nj-timepick'),
                        alreadyActive = timeInput.hasClass('nj-timepick-input--active');
                    $('.nj-timepick-input--active').removeClass('nj-timepick-input--active');
                    if (alreadyActive) return;
                    let clickedTime = timeInput.val();
                    if (clickedTime != '') changeTimeInPopup(clickedTime, 'scroll-enable');
                    popup.removeClass('nj-timepick--active');
                    popup.css({top : `${top_position + input_height + 5 }px`,left: `${left_position}px`}) 
                    timeInput.addClass('nj-timepick-input--active');
                    popup.addClass('nj-timepick--active');
                    let njTimePick = $('.nj-timepick');
                    let hourActive = njTimePick.find('.nj-timepick__hours .nj-timepick__box--active'),
                    minuteActive = njTimePick.find('.nj-timepick__minutes .nj-timepick__box--active')
                    $(".nj-timepick__hours-boxes").scrollTo(hourActive, 100);
                    $(".nj-timepick__minutes-boxes").scrollTo(minuteActive, 100);
                });

            }
            function timeInputChangeEvent(timeInput) {
                timeInput.on('change', function () {
                    let changedTime = timeInput.val();
                    if (changedTime != '') changeTimeInPopup(changedTime);
                    
                });
            }
            function changeTimeInPopup(clickedTime) {
                let timeObj = convert24hrToNormal(clickedTime),
                    hour = timeObj.hour,
                    minute = timeObj.minute,
                    meridian = timeObj.meridian,
                    boxesToActivate = $('.nj-timepick__hour[val="' + hour + '"] , \
                               .nj-timepick__minute[val="' + minute + '"] , \
                               .nj-timepick__meridian[val="' + meridian + '"]');
                boxesToActivate.addClass('nj-timepick__box--active')
                    .siblings()
                    .removeClass('nj-timepick__box--active');
            }

            function to24hrFormat(hour, minute, meridian) {
                if (hour === '12') hour = '00';
                if (meridian === 'PM') hour = parseInt(hour, 10) + 12;
                return hour + ':' + minute + " " + meridian;
            }
            function convert24hrToNormal(time) {
                let splitTime = time.split(':'),
                    hour = splitTime[0],
                    minute = splitTime[1].split(" ")[0],
                    meridian = splitTime[1].split(" ")[1];
                hour = hour % 12 || 12;
                hour = hour < 10 ? "0" + hour : hour;
                return {
                    hour: hour,
                    minute: minute,
                    meridian: meridian
                }
            }
            function validateTimeOnChange(timeInput) {
                timeInput.on('input', function () {
                    $(this).val($(this).val().toUpperCase());
                    let changedTime = timeInput.val();
                        isValidTime(changedTime)
                });
            }
            function isValidTime(time) {
                const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9] (AM|PM)$/;
                if(timeRegex.test(time) == true){
                    $('.nj-timepick-input--active').addClass('active-picker-input')
                }else{
                    $('.nj-timepick-input--active').removeClass('active-picker-input')
                }
            }
        }

    };

    $(window).on('load', function () {

            timePicker();
    })
}(jQuery));