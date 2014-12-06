var gameController = {}

gameController.loadNextWord = function(opt_oldWords, opt_newWord) {
  var data = {};

  if (opt_oldWords) {
    data['old_words'] = JSON.stringify(opt_oldWords);
  }

  if (opt_newWord) {
    data['new_word'] = opt_newWord;
  }

  $.getJSON( "/nextword", data)
  .done(function(response) {
    gameController.updateGameText_(
      response.words,
      response.pretty_words,
      response.last_input_pretty_word_index,
      response.goodness,
      response.finished,
      response.failed)
  });
};

gameController.createPrettyWordElement_ = function(
    prettyWord, lastWordEntered, goodness, failed) {
  var span = $('<span>', { "class": "prettyword", "text": prettyWord});
  var className;

  if (failed && lastWordEntered) {
    span.addClass("failedawnswer");
  } else if (lastWordEntered) {
    if (goodness > 0.75) {
      className = "greatawnswer";
    } else if (goodness > 0.5) {
      className = "goodanswer";
    } else if (goodness > 0.25) {
      className = "fairawnswer";
    } else {
      className = "badawnswer";
    }
    span.addClass(className)
      .delay(0)
      .queue(function() {
          $(this).removeClass(className);
          $(this).dequeue();
      });
  }
  return span;
};

gameController.updateGameText_ = function(words,
                                          prettyWords,
                                          lastInputPrettyWordIndex,
                                          goodness,
                                          finished,
                                          failed) {
  var gameDiv = $("#gametext");
  gameDiv.empty()

  $.each(prettyWords, function(index, prettyWord) {
    var lastWord = index == lastInputPrettyWordIndex;
    var element = gameController.createPrettyWordElement_(
      prettyWord, lastWord, goodness, failed);
    gameDiv.append(element);
    if (index < prettyWords.length - 1) {
      gameDiv.append(" ");
    }
  });

  if (!finished) {
    if (prettyWords.length) {
      gameDiv.append(" ");
    }
    var input = $('<input>').attr({"size": "1", "type": "text", "value": ""});
    input.on(
      'keydown',
      function(e) {
        if(e.which == 13 || e.which == 9) {
          e.preventDefault();
          gameController.loadNextWord(words, e.target.value);
        }
      });
    input.keyup(function(){
      $(this).attr({size: $(this).val().length + 1});
    });
    gameDiv.append(input);
    input.focus()
  }
};
