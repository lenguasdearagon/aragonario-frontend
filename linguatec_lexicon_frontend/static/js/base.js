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

        if (['es-ar', 'ar-es', 'an-an'].includes(selected_lexicon)) {
            let current = lexicon_button.data("way");
            lexicon_button.removeClass(current);
            lexicon_button.addClass(selected_lexicon);
            lexicon_button.data("way", selected_lexicon)
        }
        else {
            // do nothing on other lexicons
        }

        // topic-general has two ways: ar-es & es-ar update active way
        keep_topic_general_button_way();
    }

    function keep_topic_general_button_way() {
        var topic_general = $("#topic-general")
        var lexicon_button = $(".button-lexicon-change");

        switch (lexicon_button.data("way")) {
            case 'ar-es':
                topic_general.data("lexicode", 'ar-es');
                topic_general.data("lexidesc", "aragonés-castellano");
                break;

            case 'es-ar':
            default:
                topic_general.data("lexicode", 'es-ar');
                topic_general.data("lexidesc", "castellano-aragonés")
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

        let search_placeholder = $("#topic-general").data("lexidesc");
        $("#input-search").attr('placeholder', search_placeholder);
        $("#input-search").val("");

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

        switch ($topic.attr("id")) {
            case "topic-toggler":
                button_lexicon_toggle.addClass('d-none');
                button_topic.removeClass("d-none");
                $('#input-search').attr('placeholder', 'Selecciona área temática')
                $(".topic-toggler").removeClass("some-topic-active");
                $(".logo-caption").html("Diccionario<br>\npor áreas temáticas");

                return; // is the menu toggler: nothing else to do

            case "topic-definition":
                button_lexicon_toggle.addClass('d-none');
                button_topic.addClass("d-none");
                $(".topic-toggler").removeClass("some-topic-active");
                $(".logo-caption").html($topic.data("logo-caption"));
                search_placeholder = $topic.data("lexidesc");
                break;

            case "topic-general":
                button_lexicon_toggle.removeClass('d-none');
                button_topic.addClass('d-none');
                $(".topic-toggler").removeClass("some-topic-active");
                $(".logo-caption").html($topic.data("logo-caption"));
                search_placeholder = $topic.data("lexidesc");
                break;

            default:
                button_lexicon_toggle.addClass('d-none');
                button_topic.removeClass("d-none");
                $(".topic-toggler").addClass("some-topic-active");
                $(".logo-caption").html("Diccionario<br>\npor áreas temáticas<br>\n" + $topic.data("lexidesc"));
                $("#topic-general").removeClass("active");

                search_placeholder = responsive_search_placeholder($topic.data("lexidesc"));

                if ($topic.data("lexicode") === "an-an") {
                    $(".logo-caption").html("Diccionario<br>\n" + $topic.data("lexidesc"));
                    search_placeholder = "Definizión en aragonés";
                    // TODO replace elipsis with an-an icon
                }
        }

        $(".topic-item").removeClass("active");
        $topic.addClass("active");

        $("#selected_lex").val($topic.data("lexicode"));
        init_lexicon_button();
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

    // initialize onclick event for topic buttons
    $("#topic-general").click(function () {
        init_topic_button($(this));
        $("#input-search").val("");
    });

    $("#topic-menu .topic-item").click(function () {
        init_topic_button($(this));
        $("#input-search").val("");
    });

    $("#topic-definition").click(function () {
        init_topic_button($(this));
        $("#input-search").val("");
    });

    $("#topic-toggler").click(function () {
        $("#topic-menu").toggleClass("unfolded");
        if ($("#topic-menu").hasClass("unfolded")) {
            init_topic_button($(this));
        }
    });

    $("#topic-toggler-base").click(function () {
        $(".topic-menu-wrapper").toggleClass("collapsed");
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
