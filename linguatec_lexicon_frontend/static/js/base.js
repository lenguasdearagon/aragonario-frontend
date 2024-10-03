//////////// SANDBOX WITH THREE STATE BUTTON ////////////////////////////

document.addEventListener('DOMContentLoaded', function () {
    const stateButton = document.getElementById('state-button');
    const stateHidden = document.getElementById('state-hidden');
    const activeLexicon = document.getElementById('selected_lex');
    const states = [
        { text: 'es-ar', value: 'es-ar', desc: 'castellano-aragonés' },
        { text: 'ar-es', value: 'ar-es', desc: 'aragonés-castellano' },
        { text: 'an-an', value: 'an-an', desc: 'Definiciones en Aragonés' }
    ];
    let currentState = 0;

    stateButton.addEventListener('click', function () {
        currentState = (currentState + 1) % states.length;
        stateButton.textContent = states[currentState].text;
        stateHidden.value = states[currentState].value;
        activeLexicon.value = states[currentState].value;
    });



    const urlParams = new URLSearchParams(window.location.search);
    const lexiconParam = urlParams.get('l');

    if (lexiconParam) {
        const stateIndex = states.findIndex(state => state.value === lexiconParam);
        if (stateIndex !== -1) {
            currentState = stateIndex;
            stateButton.textContent = states[currentState].text;
            stateHidden.value = states[currentState].value;
            activeLexicon.value = states[currentState].value;
        }
    } else {

        const pathParts = window.location.pathname.split('/');
        const pathLexiconParam = pathParts.length > 2 ? pathParts[2] : null;

        if (pathLexiconParam) {
            const stateIndex = states.findIndex(state => state.value === pathLexiconParam);
            if (stateIndex !== -1) {
                currentState = stateIndex;
                stateButton.textContent = states[currentState].text;
                stateHidden.value = states[currentState].value;
                activeLexicon.value = states[currentState].value;
            }

        } else {
            // Default initialization to the first value of states
            currentState = 0;
            stateButton.textContent = states[currentState].text;
            stateHidden.value = states[currentState].value;
            activeLexicon.value = states[currentState].value;
        }
    }
});


//////////////////////////////////////// SANDBOX END //////////////////////////////////////


$(function () {

    /* home external links sidebar menu */
    $('.dismiss').on('click', function () {
        $('.sidebar').removeClass('active');
        $('.open-menu').removeClass('d-none');
    });

    $('.open-menu').on('click', function (e) {
        e.preventDefault();
        $('.sidebar').addClass('active');
        $('.open-menu').addClass('d-none');
        // close opened sub-menus
        $('.collapse.show').toggleClass('show');
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });
    /** end home external links sidebar menu */

    init_lexicon_button();
    init_topic_button($(".topic-item.active"));

    function init_lexicon_button() {
        var selected_lexicon = $("#selected_lex").val();
        var lexicon_button = $(".button-lexicon-change");

        if (selected_lexicon == 'es-ar') {
            lexicon_button.removeClass('ar-es');
            lexicon_button.addClass('es-ar');
            lexicon_button.data("way", 'es-ar')
            $('#input-search').attr('placeholder', 'castellano-aragonés');
        } else if (selected_lexicon == 'ar-es') {
            lexicon_button.removeClass('es-ar');
            lexicon_button.addClass('ar-es');
            lexicon_button.data("way", 'ar-es')
            $('#input-search').attr('placeholder', 'aragonés-castellano');
        } else {
            // do nothing on other lexicons
        }

        // topic-general has two ways: ar-es & es-ar update active way
        keep_topic_general_button_way();
    }

    function keep_topic_general_button_way() {
        var topic_general = $("#topic-general")
        var lexicon_button = $(".button-lexicon-change");

        switch (lexicon_button.data("way")) {
            case 'es-ar':
                topic_general.data("lexicode", 'es-ar');
                topic_general.data("lexidesc", "castellano-aragonés")
                break;
            case 'ar-es':
                topic_general.data("lexicode", 'ar-es');
                topic_general.data("lexidesc", "aragonés-castellano");
                break;
        }
    }

    $(".button-lexicon-change").click(function () {
        var current_lexicon = $("#selected_lex").val();

        switch (current_lexicon) {
            case 'es-ar':
                new_lex = 'ar-es';
                break;

            case 'ar-es':
                new_lex = 'es-ar';
                break;

            default:
                // don't toggle lexicon direction
                new_lex = current_lexicon;
        }

        $("#selected_lex").val(new_lex);
        init_lexicon_button();
    });

    function responsive_search_placeholder(topic) {
        let viewport_width = $(window).width();

        if (viewport_width < 576) {
            suffix = " (c ➜ a)";
        } else {
            suffix = " (castellano-aragonés)";
        }

        return topic + suffix;
    }

    function init_topic_button($topic) {

        let button_lexicon_toggle = $(".button-lexicon-change");
        let button_topic = $(".button-topic");

        // TODO handle for monolingual lexicon (it doesn't have topic-general value)
        if ($topic.length === 0) {
            search_placeholder = "Definiciones en aragonés"
            return;
        }

        switch ($topic.attr("id")) {
            case "topic-toggler":
                button_lexicon_toggle.addClass('d-none');
                button_topic.removeClass("d-none");
                $('#input-search').attr('placeholder', 'Selecciona área temática')
                $(".topic-toggler").removeClass("some-topic-active");
                $(".logo-caption").html("Diccionario<br>\npor áreas temáticas");

                return; // is the menu toggler: nothing else to do
            case "topic-general":
                button_lexicon_toggle.removeClass('d-none');
                button_topic.addClass('d-none');
                $(".topic-toggler").removeClass("some-topic-active");
                $(".logo-caption").html("Diccionario<br>\ncastellano/aragonés<br>\naragonés/castellano");

                search_placeholder = $topic.data("lexidesc");
                break;

            default:
                button_lexicon_toggle.addClass('d-none');
                button_topic.removeClass("d-none");
                $(".topic-toggler").addClass("some-topic-active");
                $(".logo-caption").html("Diccionario<br>\npor áreas temáticas<br>\n" + $topic.data("lexidesc"));
                $("#topic-general").removeClass("active");

                search_placeholder = responsive_search_placeholder($topic.data("lexidesc"));
        }

        $("#topic-menu .topic-item").removeClass("active");
        $topic.addClass("active");

        $("#selected_lex").val($topic.data("lexicode"));

        $('#input-search').attr('placeholder', search_placeholder);

        // remove other fa-icon
        let all_classes = [];
        $(".topic-item").each(function () {
            if ($(this).data("fa-icon")) {
                all_classes.push($(this).data("fa-icon"));
            }
        });
        let current_topic_icon = $topic.data("fa-icon") || "fa-ellipsis-v";
        button_topic.find('[data-fa-i2svg]')
            .removeClass(all_classes)
            .addClass(current_topic_icon);

    }

    $("#topic-general").click(function () {
        init_topic_button($(this));
        $("#input-search").val("");
    });

    $("#topic-menu .topic-item").click(function () {
        init_topic_button($(this));
        $("#input-search").val("");
    });

    $("#topic-toggler").click(function () {
        $("#topic-menu").toggleClass("unfolded");
        if ($("#topic-menu").hasClass("unfolded")) {
            init_topic_button($(this));
        } else {
            init_topic_button($("#topic-general"));
        }
    });

    $("#topic-toggler-base").click(function () {
        $(".topic-menu-wrapper").toggleClass("collapsed");
    });

    // if the user goes to input search without choosing a topic
    // perform search to general dictionary.
    $(".home #input-search").focus(function () {
        if (!$("#topic-toggler").hasClass("some-topic-active")) {
            init_topic_button($("#topic-general"));
            $("#topic-menu").removeClass("unfolded");
        }
    });

    // scroll to active topic
    if ($(".topic-menu-wrapper .topic-item.active").length) {
        let wrapper_offset = $(".topic-menu-wrapper .topic-item.active").parent().parent().offset()
        let active_topic_offset = $(".topic-menu-wrapper .topic-item.active").parent().offset();
        let diff = active_topic_offset.left - wrapper_offset.left;

        $(".topic-menu-wrapper").animate({
            scrollLeft: diff
        }, 2000);
    }

    $("#input-search").autocomplete({
        source: function (request, response) {
            $.getJSON({
                url: autocomplete_api_url,
                data: {
                    q: request.term,
                    l: $("#selected_lex").val(),
                    limit: 5
                },
                success: function (json) {
                    const data = $.map(
                        json["results"],
                        word => word["term"]
                    );
                    response(data);
                }
            });
        },
        minLength: 1,
        // on select update input value and submit form
        select: function (event, ui) {
            $(this).val(ui.item.value);
            $(this).closest('form').trigger('submit');
        }
    });
});


function specialReadText(url, player_id) {
    // clear selected text to avoid be read by speaker
    var sel = window.getSelection ? window.getSelection() : document.selection;
    if (sel) {
        if (sel.removeAllRanges) {
            sel.removeAllRanges();
        } else if (sel.empty) {
            sel.empty();
        }
    }
    // ugly hack because timing affects player behaviour
    setTimeout(() => { readpage(url, player_id); }, 200);
}
