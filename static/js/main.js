
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
    $("img").removeClass("filter-img");
    $(".change-text").html("<h2>Processing...</h2>");
    var ajax_post = function() {
     $.ajax({
         url : "/",
         type : "POST",
         data : { 'csrfmiddlewaretoken':csrftoken,'speech_text' : $("#final_span").html(), 'submit' : 'Process Text' },
         success : function(json) {
            $(".change-text").html("");
            var output = "<h2>Query Output</h2><h3><ul>";
            for (var i = 0; i < json["ret_text"].length; i++) {
              output += "<li>" + json["ret_text"][i] + "</li>";
            }
            output += "</ul><h3>";
            $(".output-text").html(output);
             console.log("success");
         },
         error : function(xhr,errmsg,err) {
             console.log(xhr.status + ": " + xhr.responseText);
         }
     });
   };
   setTimeout(ajax_post, 2000);
    return;
  }
  $(".change-text").html("<h2>Listening...</h2>");
  $("img").addClass("filter-img");
  speech_text = '';
  recognition.start();
  ignore_onend = false;
  final_span.innerHTML = '';
  temp_span.innerHTML = '';
  start_timestamp = event.timeStamp;
}
