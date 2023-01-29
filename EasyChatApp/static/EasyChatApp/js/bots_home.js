(function($) {
    var defaults = {
        columns: 1, // how many columns should be use to show options
        search: false, // include option search box

        // search filter options
        searchOptions: {
            delay: 250, // time (in ms) between keystrokes until search happens
            showOptGroups: false, // show option group titles if no options remaining
            searchText: true, // search within the text
            searchValue: false, // search within the value
            onSearch: function(element) {} // fires on keyup before search on options happens
        },

        // plugin texts
        texts: {
            placeholder: 'Select options', // text to use in dummy input
            search: 'Search', // search input placeholder text
            selectedOptions: ' selected', // selected suffix text
            selectAll: 'Select all', // select all text
            unselectAll: 'Unselect all', // unselect all text
            noneSelected: 'None Selected' // None selected text
        },

        // general options
        selectAll: false, // add select all option
        selectGroup: false, // select entire optgroup
        minHeight: 50, // minimum height of option overlay
        maxHeight: null, // maximum height of option overlay
        maxWidth: null, // maximum width of option overlay (or selector)
        maxPlaceholderWidth: null, // maximum width of placeholder button
        maxPlaceholderOpts: 2, // maximum number of placeholder options to show until "# selected" shown instead
        showCheckbox: true, // display the checkbox to the user
        checkboxAutoFit: false, // auto calc checkbox padding
        optionAttributes: [], // attributes to copy to the checkbox from the option element

        // Callbacks
        onLoad: function(element) {}, // fires at end of list initialization
        onOptionClick: function(element, option) {}, // fires when an option is clicked
        onControlClose: function(element) {}, // fires when the options list is closed
        onSelectAll: function(element, selected) {}, // fires when (un)select all is clicked
    };

    var msCounter = 1; // counter for each select list
    var msOptCounter = 1; // counter for each option on page

    // FOR LEGACY BROWSERS (talking to you IE8)
    if (typeof Array.prototype.map !== 'function') {
        Array.prototype.map = function(callback, thisArg) {
            if (typeof thisArg === 'undefined') {
                thisArg = this;
            }

            return $.isArray(thisArg) ? $.map(thisArg, callback) : [];
        };
    }
    if (typeof String.prototype.trim !== 'function') {
        String.prototype.trim = function() {
            return this.replace(/^\s+|\s+$/g, '');
        };
    }

    function MultiSelect(element, options) {
        this.element = element;
        this.options = $.extend(true, {}, defaults, options);
        this.updateSelectAll = true;
        this.updatePlaceholder = true;
        this.listNumber = msCounter;

        msCounter = msCounter + 1; // increment counter

        /* Make sure its a multiselect list */
        if (!$(this.element).attr('multiple')) {
            throw new Error('[jQuery-MultiSelect] Select list must be a multiselect list in order to use this plugin');
        }

        /* Options validation checks */
        if (this.options.search) {
            if (!this.options.searchOptions.searchText && !this.options.searchOptions.searchValue) {
                throw new Error('[jQuery-MultiSelect] Either searchText or searchValue should be true.');
            }
        }

        /** BACKWARDS COMPATIBILITY **/
        if ('placeholder' in this.options) {
            this.options.texts.placeholder = this.options.placeholder;
            delete this.options.placeholder;
        }
        if ('default' in this.options.searchOptions) {
            this.options.texts.search = this.options.searchOptions['default'];
            delete this.options.searchOptions['default'];
        }
        /** END BACKWARDS COMPATIBILITY **/

        // load this instance
        this.load();
    }

    MultiSelect.prototype = {
        /* LOAD CUSTOM MULTISELECT DOM/ACTIONS */
        load: function() {
            var instance = this;

            // make sure this is a select list and not loaded
            if ((instance.element.nodeName != 'SELECT') || $(instance.element).hasClass('jqmsLoaded')) {
                return true;
            }

            // sanity check so we don't double load on a select element
            $(instance.element).addClass('jqmsLoaded ms-list-' + instance.listNumber).data('plugin_multiselect-instance', instance);

            // add option container
            $(instance.element).after('<div id="ms-list-' + instance.listNumber + '" class="ms-options-wrap"><button type="button"><span>None Selected</span></button><div class="ms-options"><ul></ul></div></div>');

            var placeholder = $(instance.element).siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> button:first-child');
            var optionsWrap = $(instance.element).siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> .ms-options');
            var optionsList = optionsWrap.find('> ul');

            // don't show checkbox (add class for css to hide checkboxes)
            if (!instance.options.showCheckbox) {
                optionsWrap.addClass('hide-checkbox');
            } else if (instance.options.checkboxAutoFit) {
                optionsWrap.addClass('checkbox-autofit');
            }

            // check if list is disabled
            if ($(instance.element).prop('disabled')) {
                placeholder.prop('disabled', true);
            }

            // set placeholder maxWidth
            if (instance.options.maxPlaceholderWidth) {
                placeholder.css('maxWidth', instance.options.maxPlaceholderWidth);
            }

            // override with user defined maxHeight
            if (instance.options.maxHeight) {
                var maxHeight = instance.options.maxHeight;
            } else {
                // cacl default maxHeight
                var maxHeight = ($(window).height() - optionsWrap.offset().top + $(window).scrollTop() - 20);
            }

            // maxHeight cannot be less than options.minHeight
            maxHeight = maxHeight < instance.options.minHeight ? instance.options.minHeight : maxHeight;

            optionsWrap.css({
                maxWidth: instance.options.maxWidth,
                minHeight: instance.options.minHeight,
                maxHeight: maxHeight,
            });

            // isolate options scroll
            // @source: https://github.com/nobleclem/jQuery-IsolatedScroll
            optionsWrap.on('touchmove mousewheel DOMMouseScroll', function(e) {
                if (($(this).outerHeight() < $(this)[0].scrollHeight)) {
                    var e0 = e.originalEvent,
                        delta = e0.wheelDelta || -e0.detail;

                    if (($(this).outerHeight() + $(this)[0].scrollTop) > $(this)[0].scrollHeight) {
                        e.preventDefault();
                        this.scrollTop += (delta < 0 ? 1 : -1);
                    }
                }
            });

            // hide options menus if click happens off of the list placeholder button
            $(document).off('click.ms-hideopts').on('click.ms-hideopts', function(event) {
                if (!$(event.target).closest('.ms-options-wrap').length) {
                    $('.ms-options-wrap.ms-active > .ms-options').each(function() {
                        $(this).closest('.ms-options-wrap').removeClass('ms-active');

                        var listID = $(this).closest('.ms-options-wrap').attr('id');

                        var thisInst = $(this).parent().siblings('.' + listID + '.jqmsLoaded').data('plugin_multiselect-instance');

                        // USER CALLBACK
                        if (typeof thisInst.options.onControlClose == 'function') {
                            thisInst.options.onControlClose(thisInst.element);
                        }
                    });
                }
                // hide open option lists if escape key pressed
            }).on('keydown', function(event) {
                if ((event.keyCode || event.which) == 27) { // esc key
                    $(this).trigger('click.ms-hideopts');
                }
            });

            // handle pressing enter|space while tabbing through
            placeholder.on('keydown', function(event) {
                var code = (event.keyCode || event.which);
                if ((code == 13) || (code == 32)) { // enter OR space
                    placeholder.trigger('mousedown');
                }
            });

            // disable button action
            placeholder.on('mousedown', function(event) {
                // ignore if its not a left click
                if (event.which && (event.which != 1)) {
                    return true;
                }

                // hide other menus before showing this one
                $('.ms-options-wrap.ms-active').each(function() {
                    if ($(this).siblings('.' + $(this).attr('id') + '.jqmsLoaded')[0] != optionsWrap.parent().siblings('.ms-list-' + instance.listNumber + '.jqmsLoaded')[0]) {
                        $(this).removeClass('ms-active');

                        var thisInst = $(this).siblings('.' + $(this).attr('id') + '.jqmsLoaded').data('plugin_multiselect-instance');

                        // USER CALLBACK
                        if (typeof thisInst.options.onControlClose == 'function') {
                            thisInst.options.onControlClose(thisInst.element);
                        }
                    }
                });

                // show/hide options
                optionsWrap.closest('.ms-options-wrap').toggleClass('ms-active');

                // recalculate height
                if (optionsWrap.closest('.ms-options-wrap').hasClass('ms-active')) {
                    optionsWrap.css('maxHeight', '');

                    // override with user defined maxHeight
                    if (instance.options.maxHeight) {
                        var maxHeight = instance.options.maxHeight;
                    } else {
                        // cacl default maxHeight
                        var maxHeight = ($(window).height() - optionsWrap.offset().top + $(window).scrollTop() - 20);
                    }

                    if (maxHeight) {
                        // maxHeight cannot be less than options.minHeight
                        maxHeight = maxHeight < instance.options.minHeight ? instance.options.minHeight : maxHeight;

                        optionsWrap.css('maxHeight', maxHeight);
                    }
                } else if (typeof instance.options.onControlClose == 'function') {
                    instance.options.onControlClose(instance.element);
                }
            }).click(function(event) {
                event.preventDefault();
            });

            // add placeholder copy
            if (instance.options.texts.placeholder) {
                placeholder.find('span').text(instance.options.texts.placeholder);
            }

            // add search box
            if (instance.options.search) {
                optionsList.before('<div class="ms-search"><input type="text" value="" placeholder="' + instance.options.texts.search + '" /></div>');

                var search = optionsWrap.find('.ms-search input');
                search.on('keyup', function() {
                    // ignore keystrokes that don't make a difference
                    if ($(this).data('lastsearch') == $(this).val()) {
                        return true;
                    }

                    // pause timeout
                    if ($(this).data('searchTimeout')) {
                        clearTimeout($(this).data('searchTimeout'));
                    }

                    var thisSearchElem = $(this);

                    $(this).data('searchTimeout', setTimeout(function() {
                        thisSearchElem.data('lastsearch', thisSearchElem.val());

                        // USER CALLBACK
                        if (typeof instance.options.searchOptions.onSearch == 'function') {
                            instance.options.searchOptions.onSearch(instance.element);
                        }

                        // search non optgroup li's
                        var searchString = $.trim(search.val().toLowerCase());
                        if (searchString) {
                            optionsList.find('li[data-search-term*="' + searchString + '"]:not(.optgroup)').removeClass('ms-hidden');
                            optionsList.find('li:not([data-search-term*="' + searchString + '"], .optgroup)').addClass('ms-hidden');
                        } else {
                            optionsList.find('.ms-hidden').removeClass('ms-hidden');
                        }
                        if (optionsList.find('li:not(.ms-hidden)').length == 0) {
                            $(optionsList).append(`<li data-search-term="" style="text-align: center; color: #4d4d4d; font-size: 14px" class="no-data-found"><p>No result found</p></li>`)
                        } else {
                            var el = optionsList.find('li[class="no-data-found"]')
                            $(el).remove()
                        }

                        // show/hide optgroups based on if there are items visible within
                        if (!instance.options.searchOptions.showOptGroups) {
                            optionsList.find('.optgroup').each(function() {
                                if ($(this).find('li:not(.ms-hidden)').length) {
                                    $(this).show();
                                } else {
                                    $(this).hide();
                                }
                            });
                        }

                        instance._updateSelectAllText();
                    }, instance.options.searchOptions.delay));
                });
            }

            // add global select all options
            if (instance.options.selectAll) {
                optionsList.before('<div class="ms-selectall global" for="selectall-cb">' + instance.options.texts.selectAll + '</div>');
            }

            // handle select all option
            optionsWrap.on('click', '.ms-selectall', function(event) {
                event.preventDefault();

                instance.updateSelectAll = false;
                instance.updatePlaceholder = false;

                var select = optionsWrap.parent().siblings('.ms-list-' + instance.listNumber + '.jqmsLoaded');

                if ($(this).hasClass('global')) {
                    // check if any options are not selected if so then select them
                    if (optionsList.find('li:not(.optgroup, .selected, .ms-hidden)').length) {
                        // get unselected vals, mark as selected, return val list
                        optionsList.find('li:not(.optgroup, .selected, .ms-hidden)').addClass('selected');
                        optionsList.find('li.selected input[type="checkbox"]:not(:disabled)').prop('checked', true);
                    }
                    // deselect everything
                    else {
                        optionsList.find('li:not(.optgroup, .ms-hidden).selected').removeClass('selected');
                        optionsList.find('li:not(.optgroup, .ms-hidden, .selected) input[type="checkbox"]:not(:disabled)').prop('checked', false);
                    }
                } else if ($(this).closest('li').hasClass('optgroup')) {
                    var optgroup = $(this).closest('li.optgroup');

                    // check if any selected if so then select them
                    if (optgroup.find('li:not(.selected, .ms-hidden)').length) {
                        optgroup.find('li:not(.selected, .ms-hidden)').addClass('selected');
                        optgroup.find('li.selected input[type="checkbox"]:not(:disabled)').prop('checked', true);
                    }
                    // deselect everything
                    else {
                        optgroup.find('li:not(.ms-hidden).selected').removeClass('selected');
                        optgroup.find('li:not(.ms-hidden, .selected) input[type="checkbox"]:not(:disabled)').prop('checked', false);
                    }
                }

                var vals = [];
                optionsList.find('li.selected input[type="checkbox"]').each(function() {
                    vals.push($(this).val());
                });
                select.val(vals).trigger('change');

                instance.updateSelectAll = true;
                instance.updatePlaceholder = true;

                // USER CALLBACK
                if (typeof instance.options.onSelectAll == 'function') {
                    instance.options.onSelectAll(instance.element, vals.length);
                }

                instance._updateSelectAllText();
                instance._updatePlaceholderText();
            });

            // add options to wrapper
            var options = [];
            $(instance.element).children().each(function() {
                if (this.nodeName == 'OPTGROUP') {
                    var groupOptions = [];

                    $(this).children('option').each(function() {
                        var thisOptionAtts = {};
                        for (var i = 0; i < instance.options.optionAttributes.length; i++) {
                            var thisOptAttr = instance.options.optionAttributes[i];

                            if ($(this).attr(thisOptAttr) !== undefined) {
                                thisOptionAtts[thisOptAttr] = $(this).attr(thisOptAttr);
                            }
                        }

                        groupOptions.push({
                            name: $(this).text(),
                            value: $(this).val(),
                            checked: $(this).prop('selected'),
                            attributes: thisOptionAtts
                        });
                    });

                    options.push({
                        label: $(this).attr('label'),
                        options: groupOptions
                    });
                } else if (this.nodeName == 'OPTION') {
                    var thisOptionAtts = {};
                    for (var i = 0; i < instance.options.optionAttributes.length; i++) {
                        var thisOptAttr = instance.options.optionAttributes[i];

                        if ($(this).attr(thisOptAttr) !== undefined) {
                            thisOptionAtts[thisOptAttr] = $(this).attr(thisOptAttr);
                        }
                    }

                    options.push({
                        name: $(this).text(),
                        value: $(this).val(),
                        checked: $(this).prop('selected'),
                        attributes: thisOptionAtts
                    });
                } else {
                    // bad option
                    return true;
                }
            });
            instance.loadOptions(options, true, false);

            // BIND SELECT ACTION
            optionsWrap.on('click', 'input[type="checkbox"]', function() {
                $(this).closest('li').toggleClass('selected');

                var select = optionsWrap.parent().siblings('.ms-list-' + instance.listNumber + '.jqmsLoaded');

                // toggle clicked option
                select.find('option[value="' + instance._escapeSelector($(this).val()) + '"]').prop(
                    'selected', $(this).is(':checked')
                ).closest('select').trigger('change');

                // USER CALLBACK
                if (typeof instance.options.onOptionClick == 'function') {
                    instance.options.onOptionClick(instance.element, this);
                }

                instance._updateSelectAllText();
                instance._updatePlaceholderText();
            });

            // BIND FOCUS EVENT
            optionsWrap.on('focusin', 'input[type="checkbox"]', function() {
                $(this).closest('label').addClass('focused');
            }).on('focusout', 'input[type="checkbox"]', function() {
                $(this).closest('label').removeClass('focused');
            });

            // USER CALLBACK
            if (typeof instance.options.onLoad === 'function') {
                instance.options.onLoad(instance.element);
            }

            // hide native select list
            $(instance.element).hide();
        },

        /* LOAD SELECT OPTIONS */
        loadOptions: function(options, overwrite, updateSelect) {
            overwrite = (typeof overwrite == 'boolean') ? overwrite : true;
            updateSelect = (typeof updateSelect == 'boolean') ? updateSelect : true;

            var instance = this;
            var select = $(instance.element);
            var optionsList = select.siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> .ms-options > ul');
            var optionsWrap = select.siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> .ms-options');

            if (overwrite) {
                optionsList.find('> li').remove();

                if (updateSelect) {
                    select.find('> *').remove();
                }
            }

            var containers = [];
            for (var key in options) {
                // Prevent prototype methods injected into options from being iterated over.
                if (!options.hasOwnProperty(key)) {
                    continue;
                }

                var thisOption = options[key];
                var container = $('<li/>');
                var appendContainer = true;

                // OPTION
                if (thisOption.hasOwnProperty('value')) {
                    if (instance.options.showCheckbox && instance.options.checkboxAutoFit) {
                        container.addClass('ms-reflow');
                    }

                    // add option to ms dropdown
                    instance._addOption(container, thisOption);

                    if (updateSelect) {
                        var selOption = $('<option value="' + thisOption.value + '">' + thisOption.name + '</option>');

                        // add custom user attributes
                        if (thisOption.hasOwnProperty('attributes') && Object.keys(thisOption.attributes).length) {
                            selOption.attr(thisOption.attributes);
                        }

                        // mark option as selected
                        if (thisOption.checked) {
                            selOption.prop('selected', true);
                        }

                        select.append(selOption);
                    }
                }
                // OPTGROUP
                else if (thisOption.hasOwnProperty('options')) {
                    var optGroup = $('<optgroup label="' + thisOption.label + '"></optgroup>');

                    optionsList.find('> li.optgroup > span.label').each(function() {
                        if ($(this).text() == thisOption.label) {
                            container = $(this).closest('.optgroup');
                            appendContainer = false;
                        }
                    });

                    // prepare to append optgroup to select element
                    if (updateSelect) {
                        if (select.find('optgroup[label="' + thisOption.label + '"]').length) {
                            optGroup = select.find('optgroup[label="' + thisOption.label + '"]');
                        } else {
                            select.append(optGroup);
                        }
                    }

                    // setup container
                    if (appendContainer) {
                        container.addClass('optgroup');
                        container.append('<span class="label">' + thisOption.label + '</span>');
                        container.find('> .label').css({
                            clear: 'both'
                        });

                        // add select all link
                        if (instance.options.selectGroup) {
                            container.append('<a href="#" class="ms-selectall">' + instance.options.texts.selectAll + '</a>');
                        }

                        container.append('<ul/>');
                    }

                    for (var gKey in thisOption.options) {
                        // Prevent prototype methods injected into options from
                        // being iterated over.
                        if (!thisOption.options.hasOwnProperty(gKey)) {
                            continue;
                        }

                        var thisGOption = thisOption.options[gKey];
                        var gContainer = $('<li/>');
                        if (instance.options.showCheckbox && instance.options.checkboxAutoFit) {
                            gContainer.addClass('ms-reflow');
                        }

                        // no clue what this is we hit (skip)
                        if (!thisGOption.hasOwnProperty('value')) {
                            continue;
                        }

                        instance._addOption(gContainer, thisGOption);

                        container.find('> ul').append(gContainer);

                        // add option to optgroup in select element
                        if (updateSelect) {
                            var selOption = $('<option value="' + thisGOption.value + '">' + thisGOption.name + '</option>');

                            // add custom user attributes
                            if (thisGOption.hasOwnProperty('attributes') && Object.keys(thisGOption.attributes).length) {
                                selOption.attr(thisGOption.attributes);
                            }

                            // mark option as selected
                            if (thisGOption.checked) {
                                selOption.prop('selected', true);
                            }

                            optGroup.append(selOption);
                        }
                    }
                } else {
                    // no clue what this is we hit (skip)
                    continue;
                }

                if (appendContainer) {
                    containers.push(container);
                }
            }
            optionsList.append(containers);

            // pad out label for room for the checkbox
            if (instance.options.checkboxAutoFit && instance.options.showCheckbox && !optionsWrap.hasClass('hide-checkbox')) {
                var chkbx = optionsList.find('.ms-reflow:eq(0) input[type="checkbox"]');
                if (chkbx.length) {
                    var checkboxWidth = chkbx.outerWidth();
                    checkboxWidth = checkboxWidth ? checkboxWidth : 15;

                    optionsList.find('.ms-reflow label').css(
                        'padding-left',
                        (parseInt(chkbx.closest('label').css('padding-left')) * 2) + checkboxWidth
                    );

                    optionsList.find('.ms-reflow').removeClass('ms-reflow');
                }
            }

            // update placeholder text
            instance._updatePlaceholderText();

            // RESET COLUMN STYLES
            optionsWrap.find('ul').css({
                'column-count': '',
                'column-gap': '',
                '-webkit-column-count': '',
                '-webkit-column-gap': '',
                '-moz-column-count': '',
                '-moz-column-gap': ''
            });

            // COLUMNIZE
            if (select.find('optgroup').length) {
                // float non grouped options
                optionsList.find('> li:not(.optgroup)').css({
                    'float': 'left',
                    width: (100 / instance.options.columns) + '%'
                });

                // add CSS3 column styles
                optionsList.find('li.optgroup').css({
                    clear: 'both'
                }).find('> ul').css({
                    'column-count': instance.options.columns,
                    'column-gap': 0,
                    '-webkit-column-count': instance.options.columns,
                    '-webkit-column-gap': 0,
                    '-moz-column-count': instance.options.columns,
                    '-moz-column-gap': 0
                });

                // for crappy IE versions float grouped options
                if (this._ieVersion() && (this._ieVersion() < 10)) {
                    optionsList.find('li.optgroup > ul > li').css({
                        'float': 'left',
                        width: (100 / instance.options.columns) + '%'
                    });
                }
            } else {
                // add CSS3 column styles
                optionsList.css({
                    'column-count': instance.options.columns,
                    'column-gap': 0,
                    '-webkit-column-count': instance.options.columns,
                    '-webkit-column-gap': 0,
                    '-moz-column-count': instance.options.columns,
                    '-moz-column-gap': 0
                });

                // for crappy IE versions float grouped options
                if (this._ieVersion() && (this._ieVersion() < 10)) {
                    optionsList.find('> li').css({
                        'float': 'left',
                        width: (100 / instance.options.columns) + '%'
                    });
                }
            }

            // update un/select all logic
            instance._updateSelectAllText();
        },

        /* UPDATE MULTISELECT CONFIG OPTIONS */
        settings: function(options) {
            this.options = $.extend(true, {}, this.options, options);
            this.reload();
        },

        /* RESET THE DOM */
        unload: function() {
            $(this.element).siblings('#ms-list-' + this.listNumber + '.ms-options-wrap').remove();
            $(this.element).show(function() {
                $(this).css('display', '').removeClass('jqmsLoaded');
            });
        },

        /* RELOAD JQ MULTISELECT LIST */
        reload: function() {
            // remove existing options
            $(this.element).siblings('#ms-list-' + this.listNumber + '.ms-options-wrap').remove();
            $(this.element).removeClass('jqmsLoaded');

            // load element
            this.load();
        },

        // RESET BACK TO DEFAULT VALUES & RELOAD
        reset: function() {
            var defaultVals = [];
            $(this.element).find('option').each(function() {
                if ($(this).prop('defaultSelected')) {
                    defaultVals.push($(this).val());
                }
            });

            $(this.element).val(defaultVals);

            this.reload();
        },

        disable: function(status) {
            status = (typeof status === 'boolean') ? status : true;
            $(this.element).prop('disabled', status);
            $(this.element).siblings('#ms-list-' + this.listNumber + '.ms-options-wrap').find('button:first-child')
                .prop('disabled', status);
        },

        /** PRIVATE FUNCTIONS **/
        // update the un/select all texts based on selected options and visibility
        _updateSelectAllText: function() {
            if (!this.updateSelectAll) {
                return;
            }

            var instance = this;

            // select all not used at all so just do nothing
            if (!instance.options.selectAll && !instance.options.selectGroup) {
                return;
            }

            var optionsWrap = $(instance.element).siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> .ms-options');

            // update un/select all text
            optionsWrap.find('.ms-selectall').each(function() {
                var unselected = $(this).parent().find('li:not(.optgroup,.selected,.ms-hidden)');

                $(this).text(
                    unselected.length ? instance.options.texts.selectAll : instance.options.texts.unselectAll
                );
            });
        },

        // update selected placeholder text
        _updatePlaceholderText: function() {
            if (!this.updatePlaceholder) {
                return;
            }

            var instance = this;
            var select = $(instance.element);
            var selectVals = select.val() ? select.val() : [];
            var placeholder = select.siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> button:first-child');
            var placeholderTxt = placeholder.find('span');
            var optionsWrap = select.siblings('#ms-list-' + instance.listNumber + '.ms-options-wrap').find('> .ms-options');

            // if there are disabled options get those values as well
            if (select.find('option:selected:disabled').length) {
                selectVals = [];
                select.find('option:selected').each(function() {
                    selectVals.push($(this).val());
                });
            }

            // get selected options
            var selOpts = [];
            for (var key in selectVals) {
                // Prevent prototype methods injected into options from being iterated over.
                if (!selectVals.hasOwnProperty(key)) {
                    continue;
                }

                selOpts.push(
                    $.trim(select.find('option[value="' + instance._escapeSelector(selectVals[key]) + '"]').text())
                );

                if (selOpts.length >= instance.options.maxPlaceholderOpts) {
                    break;
                }
            }

            // UPDATE PLACEHOLDER TEXT WITH OPTIONS SELECTED
            placeholderTxt.text(selOpts.join(', '));

            if (selOpts.length) {
                optionsWrap.closest('.ms-options-wrap').addClass('ms-has-selections');
                optionsWrap[0].parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.getElementsByClassName("filter-modal-footer-btn")[0].removeAttribute("disabled");
            } else {
                optionsWrap.closest('.ms-options-wrap').removeClass('ms-has-selections');
                optionsWrap[0].parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.getElementsByClassName("filter-modal-footer-btn")[0].setAttribute("disabled", "");
            }

            // replace placeholder text
            if (!selOpts.length) {
                placeholderTxt.text(instance.options.texts.placeholder);
            }
            // if copy is larger than button width use "# selected"
            else if ((placeholderTxt.width() > placeholder.width()) || (selOpts.length != selectVals.length)) {
                placeholderTxt.text(selectVals.length + instance.options.texts.selectedOptions);
            }
        },

        // Add option to the custom dom list
        _addOption: function(container, option) {
            var instance = this;
            var thisOption = $('<label/>', {
                for: 'ms-opt-' + msOptCounter,
                text: option.name
            });

            var thisCheckbox = $('<input>', {
                type: 'checkbox',
                title: option.name,
                id: 'ms-opt-' + msOptCounter,
                value: option.value,
                class: 'managers'
            });

            // add user defined attributes
            if (option.hasOwnProperty('attributes') && Object.keys(option.attributes).length) {
                thisCheckbox.attr(option.attributes);
            }

            if (option.checked) {
                container.addClass('default selected');
                thisCheckbox.prop('checked', true);
            }

            thisOption.prepend(thisCheckbox);

            var searchTerm = '';
            if (instance.options.searchOptions.searchText) {
                searchTerm += ' ' + option.name.toLowerCase();
            }
            if (instance.options.searchOptions.searchValue) {
                searchTerm += ' ' + option.value.toLowerCase();
            }

            container.attr('data-search-term', $.trim(searchTerm)).prepend(thisOption);

            msOptCounter = msOptCounter + 1;
        },

        // check ie version
        _ieVersion: function() {
            var myNav = navigator.userAgent.toLowerCase();
            return (myNav.indexOf('msie') != -1) ? parseInt(myNav.split('msie')[1]) : false;
        },

        // escape selector
        _escapeSelector: function(string) {
            if (typeof $.escapeSelector == 'function') {
                return $.escapeSelector(string);
            } else {
                return string.replace(/[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~]/g, "\\$&");
            }
        }
    };

    // ENABLE JQUERY PLUGIN FUNCTION
    $.fn.multiselect = function(options) {
        if (!this.length) {
            return;
        }

        var args = arguments;
        var ret;

        // menuize each list
        if ((options === undefined) || (typeof options === 'object')) {
            return this.each(function() {
                if (!$.data(this, 'plugin_multiselect')) {
                    $.data(this, 'plugin_multiselect', new MultiSelect(this, options));
                }
            });
        } else if ((typeof options === 'string') && (options[0] !== '_') && (options !== 'init')) {
            this.each(function() {
                var instance = $.data(this, 'plugin_multiselect');

                if (instance instanceof MultiSelect && typeof instance[options] === 'function') {
                    ret = instance[options].apply(instance, Array.prototype.slice.call(args, 1));
                }

                // special destruct handler
                if (options === 'unload') {
                    $.data(this, 'plugin_multiselect', null);
                }
            });

            return ret;
        }
    };
}(jQuery));

function show_custom_access_options(model_index) {

    if (document.getElementById('easychat-custom-access-rb-' + model_index).checked) {
        document.getElementById("easychat-bot-custom-access-container-" + model_index).style.display = "block";
    } else {
        document.getElementById("easychat-bot-custom-access-container-" + model_index).style.display = "none";
    }

}

var share_bot_models = document.getElementsByClassName("easychat-modal-share-bot");
for (var i=0; i<share_bot_models.length; i++){
    var filter_chip_div = share_bot_models[i].getElementsByClassName("manager-chip-box");
    for (var j = 7; j < filter_chip_div.length; j++) {
        filter_chip_div[j].style.display = "none";
        share_bot_models[i].getElementsByClassName("show-filters")[0].classList.add('manager-chip-box');
        share_bot_models[i].getElementsByClassName("show-filters")[0].style.display = "inline-flex";
        share_bot_models[i].getElementsByClassName("count-filters")[0].innerText = `+ ${ filter_chip_div.length - 8} more`;
    }
}

function showCounts(bot_id) {

    var filter_chip_div_hide = document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("manager-chip-box");
    for (var i = 7; i < filter_chip_div_hide.length; i++) {
        filter_chip_div_hide[i].style.display = "inline-flex";
        document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("show-filters")[0].style.display = "none";
    }

}

$(function() {
    $('.bot_search_select_manager_multi_dropdown').multiselect({
        columns: 1,
        placeholder: 'Search',
        search: true,
        searchOptions: {
            'default': 'Search Here'
        }

    });

});

$(".easychat-manager-edit-access-btn").click(function() {

    $(this).closest('.manager-chip-box').toggleClass("edit-manages-access-active");
    // $('.manager-chip-box').toggleClass("edit-manages-access-active");


});

$("#home-button").click(function() {
    if ($("#panel").is(":visible") == true) {
        $("#panel").hide(100);
    } else {
        $("#panel").show(100);
    }
});

$(document).on('contextmenu', '.collapsible_custom', function(e) {
    e.preventDefault();
    var d = document.getElementById('menu-div');
    d.style.position = "absolute";
    d.style.left = e.pageX - 200 + 'px';
    d.style.top = e.pageY + 'px';
    pk_list = this.id.split("_");
    global_select_tree_name = $(this).text().trim()
    global_select_intent_id = pk_list[0];
    global_select_parent_id = pk_list[1];
    global_select_tree_id = pk_list[2];
    var tree_name = document.getElementById(this.id + "_tree_name_container").getAttribute("value");
    document.getElementById("modal_tree_name").value = tree_name;
    $("#menu-div").show();
    return false;
});

var get_all_bots_data
$( document ).ready(function() {
    get_all_bots_list()
});

$(document).ready(function() {
    $('.modal').modal();
    $('.modal').on('shown.bs.modal', function(e) {
        $('#modal-general-feedback').find('input:text, input:file, input:password, select, textarea').val('');
        $(this).removeData();
    });
});

function get_all_bots_list(){
    get_all_bots_data = null
    $.ajax({
        url: "/chat/bots-details/",
        type: "POST",
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if(response.status === 200){
                get_all_bots_data = response.data
                document.getElementById("bot_loader").style.display = "none"

                if( get_all_bots_data.no_of_bots === 0 ){
                    document.getElementById("bot-list").style.display = "none"
                    if(get_all_bots_data.is_chatbot_creation_allowed == 1){
                        document.getElementById("bot_count_result").style.display = "none"
                        document.getElementById("background-color-theme").style.display = "block"
                        document.getElementById("instruction_div").style.display = "flex"
                    }
                    document.getElementById("no_bot_found").style.display = "none"
                    document.getElementById("create_new_bot").style.display = "block";
                }else{
                    if(get_all_bots_data.is_chatbot_creation_allowed == 1){
                        render_bots(document.getElementById("easychat-search-bar").value);
                    }else{
                        render_bots();
                    }
                }
            }else{
                M.toast({
                    "html": response.message
                }, 2000);
            }

        },
        error: function(error) {
            console.log("Report this error: ", error);
        }
    });
}

function close_delete_notification(){
    document.getElementById("deleted_bot_toast_container").style.display = "none"
}

function show_create_new_bot_page(){
    document.getElementById("bot-list").style.display = "none"
    document.getElementById("no_bot_found").style.display = "none"
    
    document.getElementById("create_new_bot").style.display = "block";
    if(get_all_bots_data.is_chatbot_creation_allowed == 1){
        document.getElementById("bot_count_result").style.display = "none"
        document.getElementById("background-color-theme").style.display = "block"
        document.getElementById("instruction_div").style.display = "flex"
    }
}

function toggleText(){
    if(get_all_bots_data.is_chatbot_creation_allowed == 1){
        document.getElementById("background-color-theme").style.display = "none"
        document.getElementById("instruction_div").style.display = "none"
    }
}

function clear_search_input(){
    if(get_all_bots_data.is_chatbot_creation_allowed == 1){
        document.getElementById("easychat-search-bar").value = ""
    }
    render_bots()
}

function render_bots(bot_name_to_search = ""){
    let all_bots_lists = document.getElementById("all-bots-lists");
    let all_bots_html = "";
    let counter = 0;

    if(get_all_bots_data.is_chatbot_creation_allowed == 1){
        if(bot_name_to_search === ""){
            document.getElementById("cross_icon").style.display = "none"
        }else{
            document.getElementById("cross_icon").style.display = "block"
        }
    }
    
    get_all_bots_data.bot_obj_list.forEach(bot_obj => {
        if(bot_obj.name.toLowerCase().includes(bot_name_to_search.toLowerCase())){
            counter++;

            let access_found = false;
    
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Full Access") ){
                access_found = true;
                all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/intent/?bot_pk=${bot_obj.id}&selected_language=en" class="black-text center-align">`
            }
            else if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Self Learning Related")){
                access_found = true;
                all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot-learning/?bot_pk=${bot_obj.id}" class="black-text center-align">`
            }
            else if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Lead Gen Related")){
                if (bot_obj.is_lead_generation_enabled) {
                    access_found = true;
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/lead-generation/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            else if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Form Assist Related")){
                if (bot_obj.is_form_assist_enabled) {
                    access_found = true;
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/form-assist/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") && !access_found ){
                access_found = true;
                all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("EasyDrive Related") && !access_found ){
                access_found = true;
                all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("EasyDataCollection Related") && !access_found ){
                access_found = true;
                all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Intent Related") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") ){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else{
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/intent/?bot_pk=${bot_obj.id}&selected_language=en" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Create Bot With Excel Related") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") ){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/create-quick-bot/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Word Mapper Related") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") ){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/word-mappers/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Categories") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related")){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/categories/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("PDF Searcher") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related")){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/pdf-searcher/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }

            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Automated Testing") && !access_found){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") ){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/test-chatbot/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Message History Related") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related")){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/user-filtered/?bot_id=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Analytics Related") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") ){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/revised-analytics/?bot_id=${bot_obj.id}" class="black-text center-align">`
                }
            }
            if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("API Analytics Related") && !access_found ){
                access_found = true;
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") ){
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/bot/edit/${bot_obj.id}/?selected_language=en" class="black-text center-align">`
                }
                else {
                    all_bots_html += `<div class="col s3"><div class="card medium"><a href="/chat/easychat-api-analytics/?bot_pk=${bot_obj.id}" class="black-text center-align">`
                }
            }
            
            if(access_found){
                all_bots_html += `<div class="card-image">
                        <div id="card_img_div" style="min-height:1.5em;">
                            <div class="bot-img">`
                if(bot_obj.bot_image){
                    all_bots_html += `<img class="responsive-img" alt="bot image" src="${bot_obj.bot_image}">`
                }
                else {
                    all_bots_html += `<img class="responsive-img" alt="bot image" src="/static/EasyChatApp/img/popup-4.gif">`
                }
                all_bots_html += `
                            </div>
                            <div id="indicators" style="min-height:1.5em;">`
                if (bot_obj.is_easy_search_allowed ){
                    all_bots_html += `<span data-position="right" data-tooltip="EasySearch" class="tooltipped font-indicator-easy-search">E</span>`
                }
                if (bot_obj.is_form_assist_enabled ){
                    all_bots_html += `<span data-position="right" data-tooltip="Form Assist" class="tooltipped font-indicator-form-assist">F</span>`
                }
                all_bots_html += `
                        </div>
                        </div>
                        <link id="font-link" rel="stylesheet" href="https://fonts.googleapis.com/css?family=${bot_obj.font}">
                        <H6  class="bot-name" style="font-family: '${bot_obj.font}'">${bot_obj.name}</H6>
                        </div></a>
                        <div class="card-action center">`
                if ( get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Bot Setting Related") || get_all_bots_data.get_bot_related_access_perm[bot_obj.id].includes("Full Access") ){
                    if (get_all_bots_data.is_bot_shareable ){
                        if (!get_all_bots_data.is_sandbox_user && get_all_bots_data.is_user_guest == false){
                        all_bots_html += `
                            <a class="card-action-share modal-trigger tooltipped"data-position="bottom" href="#modal-share-bot-${bot_obj.id}" data-tooltip="Share">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M14.7629 2.88281C16.2357 2.88281 17.4297 3.97691 17.4297 5.32656C17.4297 6.6762 16.2357 7.7703 14.7629 7.7703C14.0137 7.7703 13.3368 7.48725 12.8523 7.03149L7.99819 9.5743C8.05898 9.77914 8.09143 9.99469 8.09143 10.2172C8.09143 10.4397 8.05898 10.6552 7.99819 10.8601L12.853 13.4023C13.3374 12.9469 14.0141 12.6641 14.7629 12.6641C16.2357 12.6641 17.4297 13.7582 17.4297 15.1078C17.4297 16.4574 16.2357 17.5515 14.7629 17.5515C13.29 17.5515 12.0961 16.4574 12.0961 15.1078C12.0961 14.8853 12.1285 14.6698 12.1893 14.4649L7.33517 11.9221C6.85074 12.3779 6.17375 12.6609 5.42462 12.6609C3.95178 12.6609 2.75781 11.5668 2.75781 10.2172C2.75781 8.86754 3.95178 7.77344 5.42462 7.77344C6.17342 7.77344 6.85013 8.05623 7.33452 8.51163L12.1893 5.96944C12.1285 5.76459 12.0961 5.54905 12.0961 5.32656C12.0961 3.97691 13.29 2.88281 14.7629 2.88281Z" fill="#0254D7"/>
                            </svg>    
                            </a>`
                        }
                    }
                    all_bots_html += `
                        <a class="card-action-edit tooltipped" data-position="bottom" href="/chat/bot/edit/${bot_obj.id}?selected_language=en" data-tooltip="Edit">
                        <svg width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12.2339 5.27184L15.853 8.89089L8.74633 15.9975C8.54834 16.1955 8.30211 16.3384 8.03198 16.412L4.37382 17.4097C3.97346 17.5189 3.6061 17.1515 3.71529 16.7512L4.71297 13.093C4.78664 12.8229 4.92954 12.5767 5.12753 12.3787L12.2339 5.27184ZM17.3047 3.82028C18.304 4.81959 18.304 6.43978 17.3047 7.43909L16.611 8.13218L12.9919 4.51384L13.6859 3.82028C14.6852 2.82097 16.3054 2.82097 17.3047 3.82028Z" fill="#047857"/>
                        </svg>
                        </a>
                        <a class="card-action-delete modal-trigger tooltipped"data-position="bottom" href="#modal-delete-bot-${bot_obj.id}" data-tooltip="Delete">
                        <svg width="21" height="22" viewBox="0 0 21 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M9.52082 2.55579C8.1594 2.55579 7.05575 3.65944 7.05575 5.02086V5.11829H4.39582H3.54165C3.12372 5.11829 2.78491 5.45709 2.78491 5.87502C2.78491 6.29296 3.12372 6.63176 3.54165 6.63176H4.39582H4.66884L5.37465 17.1251L5.37475 17.1267C5.45258 18.3586 6.47446 19.3181 7.70904 19.3181H13.0409C14.2755 19.3181 15.2974 18.3586 15.3752 17.1267L15.3753 17.1251L16.0811 6.63176H16.3542H17.2083C17.6263 6.63176 17.9651 6.29296 17.9651 5.87502C17.9651 5.45709 17.6263 5.11829 17.2083 5.11829H16.3542H13.6942V5.02086C13.6942 3.65944 12.5906 2.55579 11.2292 2.55579H9.52082ZM12.1807 5.11829H8.56922V5.02086C8.56922 4.49531 8.99527 4.06926 9.52082 4.06926H11.2292C11.7547 4.06926 12.1807 4.49531 12.1807 5.02086V5.11829ZM13.0957 9.32407C13.1136 8.90652 12.7896 8.55352 12.372 8.53562C11.9545 8.51773 11.6015 8.84171 11.5836 9.25927L11.3273 15.2384C11.3094 15.656 11.6334 16.009 12.051 16.0269C12.4685 16.0448 12.8215 15.7208 12.8394 15.3032L13.0957 9.32407ZM9.16649 9.25927C9.14859 8.84171 8.79559 8.51773 8.37804 8.53562C7.96049 8.55352 7.6365 8.90652 7.6544 9.32407L7.91065 15.3032C7.92854 15.7208 8.28154 16.0448 8.6991 16.0269C9.11665 16.009 9.44063 15.656 9.42274 15.2384L9.16649 9.25927Z" fill="#FF4C40"/>
                        </svg>    
                        </a>
                        <a target="_blank" class="card-action-open-chat-window modal-trigger tooltipped"data-position="bottom" href="/chat/bot/?id=${bot_obj.id}" style="font-weight: bold;" data-tooltip="Open Chat Window">
                        <svg width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6.18742 3.78255H9.08838C9.43176 3.78255 9.71013 4.06092 9.71013 4.4043C9.71013 4.71906 9.47623 4.9792 9.17275 5.02037L9.08838 5.02604H6.18712C5.20978 5.02558 4.4079 5.77744 4.32862 6.73455L4.32234 6.86629L4.32469 13.9381C4.32495 14.9253 5.09211 15.7332 6.06271 15.7986L6.19041 15.8029L13.2353 15.7932C14.2215 15.7918 15.0281 15.0252 15.0936 14.0555L15.0979 13.928V11.0213C15.0979 10.6779 15.3763 10.3995 15.7197 10.3995C16.0344 10.3995 16.2946 10.6334 16.3357 10.9369L16.3414 11.0213V13.928C16.3414 15.5879 15.0404 16.9442 13.4019 17.0322L13.237 17.0367L6.19419 17.0464L6.02564 17.0421C4.44014 16.9595 3.16893 15.689 3.08555 14.1036L3.0812 13.9385L3.07935 6.89338L3.083 6.7255C3.16598 5.13988 4.43706 3.86903 6.02234 3.78678L6.18742 3.78255ZM11.7861 2.53906L16.802 2.54027L16.8845 2.54861L16.9522 2.56191L17.0414 2.58873L17.1397 2.63188L17.1835 2.65696C17.3987 2.78543 17.5504 3.00862 17.5814 3.26885L17.5873 3.36806V8.34783C17.5873 8.80567 17.2161 9.17683 16.7583 9.17683C16.3331 9.17683 15.9827 8.8568 15.9349 8.44451L15.9293 8.34783L15.9287 5.36842L10.7113 10.5862C10.4124 10.885 9.94218 10.908 9.61698 10.6551L9.53888 10.5862C9.24004 10.2873 9.21705 9.81712 9.46992 9.49191L9.53888 9.41381L14.7549 4.19705H11.7861C11.3609 4.19705 11.0105 3.87702 10.9626 3.46473L10.9571 3.36806C10.9571 2.91022 11.3282 2.53906 11.7861 2.53906Z" fill="black"/>
                        </svg>
                        </a>`
                }
                else{
                    all_bots_html += `
                            <a target="_blank" class="card-action-open-chat-window modal-trigger tooltipped"data-position="bottom" href="/chat/bot/?id=${bot_obj.id}" style="font-weight: bold;" data-tooltip="Open Chat Window">
                            <svg width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M6.18742 3.78255H9.08838C9.43176 3.78255 9.71013 4.06092 9.71013 4.4043C9.71013 4.71906 9.47623 4.9792 9.17275 5.02037L9.08838 5.02604H6.18712C5.20978 5.02558 4.4079 5.77744 4.32862 6.73455L4.32234 6.86629L4.32469 13.9381C4.32495 14.9253 5.09211 15.7332 6.06271 15.7986L6.19041 15.8029L13.2353 15.7932C14.2215 15.7918 15.0281 15.0252 15.0936 14.0555L15.0979 13.928V11.0213C15.0979 10.6779 15.3763 10.3995 15.7197 10.3995C16.0344 10.3995 16.2946 10.6334 16.3357 10.9369L16.3414 11.0213V13.928C16.3414 15.5879 15.0404 16.9442 13.4019 17.0322L13.237 17.0367L6.19419 17.0464L6.02564 17.0421C4.44014 16.9595 3.16893 15.689 3.08555 14.1036L3.0812 13.9385L3.07935 6.89338L3.083 6.7255C3.16598 5.13988 4.43706 3.86903 6.02234 3.78678L6.18742 3.78255ZM11.7861 2.53906L16.802 2.54027L16.8845 2.54861L16.9522 2.56191L17.0414 2.58873L17.1397 2.63188L17.1835 2.65696C17.3987 2.78543 17.5504 3.00862 17.5814 3.26885L17.5873 3.36806V8.34783C17.5873 8.80567 17.2161 9.17683 16.7583 9.17683C16.3331 9.17683 15.9827 8.8568 15.9349 8.44451L15.9293 8.34783L15.9287 5.36842L10.7113 10.5862C10.4124 10.885 9.94218 10.908 9.61698 10.6551L9.53888 10.5862C9.24004 10.2873 9.21705 9.81712 9.46992 9.49191L9.53888 9.41381L14.7549 4.19705H11.7861C11.3609 4.19705 11.0105 3.87702 10.9626 3.46473L10.9571 3.36806C10.9571 2.91022 11.3282 2.53906 11.7861 2.53906Z" fill="black"/>
                            </svg>
                            </a>
                    `
                }
                all_bots_html += `
                            </div>
                        </div>
                    </div>
                    <!--Mudit--> 
                `
            }
        }

    })
    if(all_bots_html === ""){
        if(get_all_bots_data.no_of_bots === 0 && bot_name_to_search === ""){
            document.getElementById("bot-list").style.display = "none"
            document.getElementById("no_bot_found").style.display = "none"
            document.getElementById("create_new_bot").style.display = "block";
            if(get_all_bots_data.is_chatbot_creation_allowed == 1){
                document.getElementById("bot_count_result").style.display = "none"
            }
        }else{
            document.getElementById("bot-list").style.display = "none"
            document.getElementById("create_new_bot").style.display = "none";
            document.getElementById("no_bot_found").style.display = "block"
            if(get_all_bots_data.is_chatbot_creation_allowed == 1){
                document.getElementById("bot_count_result").style.display = "none"
            }
        }
    }
    else{
        document.getElementById("create_new_bot").style.display = "none";
        document.getElementById("no_bot_found").style.display = "none"
        document.getElementById("bot-list").style.display = "block"
        if(get_all_bots_data.is_chatbot_creation_allowed == 1){
            document.getElementById("bot_count_result").style.display = "block"
            document.getElementById("total_number_of_bots").innerText = get_all_bots_data.no_of_bots
            document.getElementById("total_number_of_bots").style.display = "inline-block"
            document.getElementById("searched_results").innerText = counter + "/"
            if(counter !== get_all_bots_data.no_of_bots){
                document.getElementById("searched_results").style.display = "inline-block"
            }else{
                document.getElementById("searched_results").style.display = "none"
            }
        }
        all_bots_lists.innerHTML = all_bots_html
    }
    $(".tooltipped").tooltip()

}

function share_bot(bot_id){
    var access_type = null;
    if (document.getElementById("easychat-bot-full-access-btn-" + bot_id).checked){
        access_type = "full_access";
    }
    if (document.getElementById("easychat-custom-access-rb-" + bot_id).checked){
        access_type = "custom_access";
    }
    if (access_type == undefined || access_type == null) {
        alert("Please select valid access type");
        return
    }

    custom_access_array = []
    if (access_type == "custom_access") {
        var custom_access_checkboxes = document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("custom-access-modules");
        for (var i = 0; i < custom_access_checkboxes.length; i++) {
            if (custom_access_checkboxes[i].checked){
                custom_access_array.push(custom_access_checkboxes[i].value);
            }
        }

        if (custom_access_array.length == 0) {
            alert("Please select atleast one custom access type.")
            return
        }
    }

    var user_list = [];

    if (document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("ms-options-wrap")[0].children[0].disabled){
        user_list = [document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("edit-manages-access-active")[0].getAttribute("value")];
    } else {
        var managers = document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("managers");
        for (var i=0; i<managers.length; i++){
            if (managers[i].checked){
                user_list.push(managers[i].value);
            }
        }
    }

    if (user_list.length == 0) {
        alert("Please select atleast one recipient")
        return
    }

    is_livechat_supervisor_access_guaranted = "false";
    if (document.getElementById("livechat-supervisor-access-" + bot_id) && document.getElementById("livechat-supervisor-access-" + bot_id).checked){
        is_livechat_supervisor_access_guaranted = "true";
    }

    is_tms_supervisor_access_guaranted = "false";
    if (document.getElementById("tms-supervisor-access-" + bot_id) && document.getElementById("tms-supervisor-access-" + bot_id).checked){
        is_tms_supervisor_access_guaranted = "true";
    }

    json_string = JSON.stringify({
        "bot_id": bot_id,
        "user_id_list": user_list,
        "access_type": access_type,
        "custom_access_array": custom_access_array,
        "is_livechat_supervisor_access_guaranted": is_livechat_supervisor_access_guaranted,
        "is_tms_supervisor_access_guaranted": is_tms_supervisor_access_guaranted
    });
    json_string = EncryptVariable(json_string)

    $.ajax({
        url: "/chat/bot/share/",
        type: "POST",
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            data: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                var bot_id = response["bot_id"];
                if (document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("ms-options-wrap")[0].children[0].disabled) {
                    M.toast({
                        "html": "Accesses edited successfully."
                    }, 2000);
                } else {
                    M.toast({
                        "html": "Bot shared successfully."
                    }, 2000);
                }
                setTimeout(function(e) {
                    window.location.reload();
                }, 2000);
            } else {
                M.toast({
                    "html": "Unable to share bot. Please try again later."
                }, 2000);
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        }
    });
};

function unshare(manager_id, bot_id){

    json_string = JSON.stringify({
      "bot_id":bot_id,
      "user_id":manager_id
    });
    json_string = EncryptVariable(json_string)
    $.ajax({
        url:"/chat/bot/unshare/",
        type:"POST",
        headers:{
        "X-CSRFToken":get_csrf_token()
        },
        data:{
         data:json_string
        },
        success: function(response){

            if(response["status"]==200){

                M.toast({"html":"Bot unshared successfully."}, 2000);
                window.location.reload();
            }else if(response["status"]==401) {
                M.toast({"html": response["message"]}, 2000);
            }else{

                M.toast({"html":"Unable to undo bot share. Please try again later."}, 2000);
            }
        },
        error: function(error){
         console.log("Report this error: ", error);
        }
    });
}


function update_manager_bot_access_details(response) {
    var bot_id = response["bot_id"];

    if (response["access_type"] == "full_access"){
        document.getElementById("easychat-bot-full-access-btn-" + bot_id).checked = true;
        document.getElementById("easychat-bot-custom-access-container-" + bot_id).style.display = "none";
    } else {
        document.getElementById("easychat-custom-access-rb-" + bot_id).checked = true;
        var custom_access_container = document.getElementById("easychat-bot-custom-access-container-" + bot_id);

        for (var i=0; i<response["custom_access_type"].length; i++){
            custom_access_container.querySelector('[value="' + response["custom_access_type"][i] + '"]').checked = true;
        }
        custom_access_container.style.display = "block";
    }

    if (response["is_livechat_supervisor_access"] == "true"){
        document.getElementById("livechat-supervisor-access-" + bot_id).checked = true;
    } else {
        if (document.getElementById("livechat-supervisor-access-" + bot_id)){
            document.getElementById("livechat-supervisor-access-" + bot_id).checked = false;
        }
    }

    if (response["is_tms_supervisor_access"] == "true"){
        document.getElementById("tms-supervisor-access-" + bot_id).checked = true;
    } else {
        if (document.getElementById("tms-supervisor-access-" + bot_id)){
            document.getElementById("tms-supervisor-access-" + bot_id).checked = false;
        }
    }
}


function get_manager_bot_access_details(bot_id, manager_id, el) {

    if ($(el).closest('.manager-chip-box').hasClass("edit-manages-access-active")) {
        document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("ms-options-wrap")[0].children[0].disabled = false;
        document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("filter-modal-footer-btn")[0].innerText = "Share";
        if (document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("ms-has-selections")[0]) {
            document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("filter-modal-footer-btn")[0].removeAttribute("disabled");
        } else {
            document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("filter-modal-footer-btn")[0].setAttribute("disabled", "");
        }
        return;
    }

    document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("ms-options-wrap")[0].children[0].disabled = true;
    document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("filter-modal-footer-btn")[0].innerText = "Save";
    document.getElementById("modal-share-bot-" + bot_id).getElementsByClassName("filter-modal-footer-btn")[0].removeAttribute("disabled");

    var edit_chip_tags = el.parentElement.parentElement.getElementsByClassName("edit-manages-access-active");
    for (var i=0; i<edit_chip_tags.length; i++){
        edit_chip_tags[i].classList.remove("edit-manages-access-active");
    }

    json_string = JSON.stringify({
        "bot_id": bot_id,
        "manager_id": manager_id
    });
    json_string = EncryptVariable(json_string)

    $.ajax({
        url: "/chat/get-manager-access-details/",
        type: "POST",
        headers: {
            "X-CSRFToken": get_csrf_token()
        },
        data: {
            json_string: json_string
        },
        success: function(response) {
            response = custom_decrypt(response)
            response = JSON.parse(response);
            if (response["status"] == 200) {
                update_manager_bot_access_details(response);
            }else if(response["status"]==401) {
                M.toast({"html": response["message"]}, 2000);
            } else {
                M.toast({
                    "html": "Unable to load the manager access details. Please try again later."
                }, 2000);
            }
        },
        error: function(error) {
            console.log("Report this error: ", error);
        }
    });
};

function close_termination_modal(bot_id, user_id) {
    $("#termination-confirmation-modal-" + bot_id + "-" + user_id).modal("close");
}
