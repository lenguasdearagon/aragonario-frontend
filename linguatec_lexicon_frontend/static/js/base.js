$(function () {

    init_lexicon_button();

    function init_lexicon_button(){
        var selected_lexicon = $("#selected_lex").val();
        var lexicon_button = $(".button-lexicon-change")
        if (selected_lexicon == 'es-ar'){
            lexicon_button.removeClass('ar-es');
            lexicon_button.addClass('es-ar');
            $('#input-search').attr('placeholder', 'castellano-aragonés');
        } else {
            lexicon_button.removeClass('es-ar');
            lexicon_button.addClass('ar-es');
            $('#input-search').attr('placeholder', 'aragonés-castellano');
        }
    }

    $(".button-lexicon-change").click(function() {
        var current_lexicon = $("#selected_lex").val();
        $("#selected_lex").val(current_lexicon == 'es-ar' ? 'ar-es' : 'es-ar');
        init_lexicon_button();
    });

    $("#topic-menu .topic-item").click(function() {
        let $topic = $(this);

        if( $topic.attr("id") == "topic-toggler") {
            return; // is the menu toggler: nothing to do
        }

        $("#topic-menu .topic-item").removeClass("active");
        $topic.addClass("active");

        $("#selected_lex").val($topic.data("lexicode"));

        // TODO(@slamora): update search input placeholder
        // TODO(@slamora): update icon of button-lexicon-change
    });

    $("#topic-toggler").click(function() {
        $("#topic-menu").toggleClass("unfolded");
    });

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
