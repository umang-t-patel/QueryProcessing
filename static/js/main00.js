
var speech_text = '';
var recognizing = false;
var ignore_onend;
var start_timestamp;
if (!('webkitSpeechRecognition' in window)) {
  upgrade();
} else {
  var recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.tempResults = true;
  recognition.onstart = function() {
    recognizing = true;
  };
  recognition.onerror = function(event) {
    if (event.error == 'no-speech') {
      ignore_onend = true;
    }
    if (event.error == 'audio-capture') {
      ignore_onend = true;
    }
    if (event.error == 'not-allowed') {
      ignore_onend = true;
    }
  };
  recognition.onend = function() {
    recognizing = false;
    if (ignore_onend) {
      return;
    }
    if (window.getSelection) {
      window.getSelection().removeAllRanges();
      var range = document.createRange();
      range.selectNode(document.getElementById('final_span'));
      window.getSelection().addRange(range);
    }
  };
  recognition.onresult = function(event) {
    var temp_transcript = '';
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        speech_text += event.results[i][0].transcript;
      } else {
        temp_transcript += event.results[i][0].transcript;
      }
    }
    final_span.innerHTML = linebreak(speech_text);
    temp_span.innerHTML = linebreak(temp_transcript);
  };
}
var two_line = /\n\n/g;
var one_line = /\n/g;
function linebreak(s) {
  return s.replace(two_line, '<p></p>').replace(one_line, '<br>');
}
function startButton(event) {
  if (recognizing) {
    recognition.stop();
    $(".button-transperent").removeClass("filter-img");
    $(".change-text").html("<h2>Processing...</h2>");
    var ajax_post = function() {
      if ($("#final_span").html() != "") {
        $.ajax({
          url : "google/",
          type : "POST",
          data : { 'csrfmiddlewaretoken':csrftoken,'speech_text' : $("#final_span").html(), 'submit' : 'Process Text' },
          success : function(json) {
            $(".change-text").html("");
            var msg = new SpeechSynthesisUtterance('Please see the Query Output from Google Natural Language Processing as below');
            window.speechSynthesis.speak(msg);
            var output = "<h2>Query Output</h2>"
            if (json.ret_text.length != 0) {
              output += "<h4><ul>";
              for (var i = 0; i < json["ret_text"].length; i++) {
                output += "<li><ul><h3>" + json["ret_text"][i]["text"]+"</h3>";
                output += "<li>Text: " + json["ret_text"][i]["text"] + "</li>";
                output += "<li>Part of Speech: " + JSON.stringify(json["ret_text"][i]["partOfSpeech"]) + "</li>";
                output += "<li>Dependency Edge: " + JSON.stringify(json["ret_text"][i]["dependencyEdge"]) + "</li>";
                output += "<li>Lemma: " + json["ret_text"][i]["lemma"] + "</li>";
                output += "</ul></li>";
              }
              output += "</ul><h4>";
            }
            else {
              var msg = new SpeechSynthesisUtterance('No results found');
              window.speechSynthesis.speak(msg);
              output +="<h3>No results found.</h3>"
            }
            $(".output-text").html(output);
            $(".output-value").html("<h3>Final Output: "+json["output_value"]+"</h3>");
            console.log("success");
          },
          error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
          }
        });
      }
      else {
        var msg = new SpeechSynthesisUtterance("Sorry, I didn't get that. Please try again");
        window.speechSynthesis.speak(msg);
        $(".output-text").html("<h2>Sorry, I didn't get that. Please try again</h2>");
        $(".change-text").html("<h2>Error...</h2>");
      }
    };
    setTimeout(ajax_post, 2000);
    return;
  }
  $(".change-text").html("<h2>Listening...</h2>");
  $(".output-text").html("");
  $(".button-transperent").addClass("filter-img");
  speech_text = '';
  recognition.start();
  ignore_onend = false;
  final_span.innerHTML = '';
  temp_span.innerHTML = '';
  start_timestamp = event.timeStamp;
}
