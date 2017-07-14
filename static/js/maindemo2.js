
var speech_text = '';
var recognizing = false;
var submit_text = true;
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
    if (final_span.innerHTML == "") {
    texttospeech(event);
    }
  };
  recognition.onresult = function(event) {
    var temp_transcript = '';
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        speech_text = event.results[i][0].transcript;
      }
    }
    final_span.innerHTML = linebreak(speech_text);
    if (final_span.innerHTML != "") {
    texttospeech(event);
    }
  };
}
var two_line = /\n\n/g;
var one_line = /\n/g;
function linebreak(s) {
  return s.replace(two_line, '<p></p>').replace(one_line, '<br>');
}
function startButton(event) {
  $(".change-text").html("<h2>Listening...</h2>");
  if ($.trim($(".feedback-text").html()) != "") {
    console.log(final_span.innerHTML);
    $("#final_span_output").html(final_span.innerHTML)
  }
  else {
    $(".output-text").html("");
    $(".output-value").html("");
    $(".feedback-text").html("");
    $("#final_span_output").html("");
  }
  $(".button-transperent").addClass("filter-img");
  speech_text = '';
  recognition.start();
  setTimeout(function() {
    if (final_span.innerHTML == '' && $(".change-text").html()!='<h2>Error...</h2>' && !(recognizing)) {
      texttospeech(event);
    }
  }, 10000);
  ignore_onend = false;
  final_span.innerHTML = '';
  temp_span.innerHTML = '';
  start_timestamp = event.timeStamp;
}
function texttospeech(event) {
    recognition.stop();
    $(".button-transperent").removeClass("filter-img");
    $('#loading').show();
    $(".change-text").html("<h2>Processing...</h2>");
    if (submit_text) {
      submit_text = false;
      var ajax_post = function() {
        if ($.trim($("#final_span").html()) != "") {
          var speech_text = $("#final_span").html();
          console.log(speech_text);
          var feedback_text = "";
          if ($.trim($(".feedback-text").html()) != "") {
            console.log("feedback");
            console.log($(".feedback-text").html());
            speech_text = $("#final_span_output").html();
            feedback_text = $("#final_span").html();
          }
          var temp_feedback_list = JSON.parse(sessionStorage.getItem("feedback_list"));
          var temp_feedback_text = sessionStorage.getItem("feedback_text");
          console.log(temp_feedback_list);
          for (var i = 0; i < temp_feedback_list.length; i++) {
            var check_feedback = speech_text.replace(/\?/g, '').toLowerCase().indexOf(temp_feedback_list[i].toLowerCase())
            if (check_feedback != -1) {
              feedback_text = 'yes';
              break;
            }
          }
          $.ajax({
            url : "demo2/",
            type : "POST",
            data : { 'csrfmiddlewaretoken':csrftoken,'speech_text' : speech_text,'feedback_text':feedback_text, 'submit' : 'Process Text' },
            success : function(json) {
              $(".change-text").html("");
              var output = ""
              $('#input_query').val('')
              $('select').val(0);
              if (json.ret_text.length != 0) {
                if ($(".output-value").html()!="<h2>"+json["output_value"]+"</h2>") {
                $(".output-text").html("<h3>JSON Data: <br>"+json["ret_text"]+"</h3>");
                var msg = new SpeechSynthesisUtterance(json["output_value"]);
                window.speechSynthesis.speak(msg);
                $(".output-value").html("<h2>"+json["output_value"]+"</h2>");
                console.log("success");
                $('#loading').hide();
                $(".feedback-text").html("");
                if($("#final_span").html() == 'yes'){
                  var temp_feedback_list = JSON.parse(sessionStorage.getItem("feedback_list"));
                  temp_feedback_list.push(sessionStorage.getItem("feedback_text"));
                  sessionStorage.setItem('feedback_list',JSON.stringify(temp_feedback_list));
                  var temp_feedback_text = '';
                  sessionStorage.setItem('feedback_text',temp_feedback_text);
                }
                }
                submit_text = true;
              }
              else if (json.output_feedback.length != 0) {
                $("#final_span_output").html("");
                var feedback_text = ""
                for (var i = 0; i < json["feedback_text"].length; i++) {
                  feedback_text += json["feedback_text"][i]
                }
                var temp_feedback_text = feedback_text;
                sessionStorage.setItem('feedback_text',temp_feedback_text);
                feedback_output = "Do you mean "+feedback_text+" in "+json["output_feedback"]+"?"
                var msg = new SpeechSynthesisUtterance(feedback_output);
                window.speechSynthesis.speak(msg);
                $(".feedback-text").html("<h2>"+feedback_output+"</h2>");
                $('#loading').hide();
                submit_text = true;
                setTimeout(function() { startButton(event); }, 3000);
              }
              else {
                output +="<h3>No results found.</h3>"
                if ($(".output-value").html()!=output) {
                var msg = new SpeechSynthesisUtterance('No results found');
                window.speechSynthesis.speak(msg);
                $(".output-value").html(output);
                $(".output-text").html("");
                $(".feedback-text").html("");
                $("#final_span_output").html("");
                }
                $('#loading').hide();
                submit_text = true;
              }
            },
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ": " + xhr.responseText);
                output +="<h3>Try Again...</h3>"
                if ($(".output-value").html()!=output) {
                var msg = new SpeechSynthesisUtterance('Try Again');
                window.speechSynthesis.speak(msg);
                $(".output-value").html(output);
                $(".output-text").html("");
                $(".change-text").html("<h2>Error...</h2>");
                }
                $('#loading').hide();
                submit_text = true;
            }
          });
        }
        else {
          if ($(".output-text").html()!= "<h2>Sorry, I didn't get that. Please try again</h2>") {
            var msg = new SpeechSynthesisUtterance("Sorry, I didn't get that. Please try again");
            window.speechSynthesis.speak(msg);
            $(".output-text").html("<h2>Sorry, I didn't get that. Please try again</h2>");
            $(".change-text").html("<h2>Error...</h2>");
          }
          $('#loading').hide();
          submit_text = true;
        }
      };
      setTimeout(ajax_post, 2000);
    }
    return;
}
