"use strict";

function reservip_submit_token(form_element) {
    var xhr = new XMLHttpRequest();
    var inputs = form_element.getElementsByTagName('input');
    var token;
    for (var elem of inputs) {
	elem.disabled = true;
	if (elem.type == "password") {
	    token = elem.value;
	} else if (elem.type == "submit") {
	    elem.name = "Loading...";
	}
    }

    function fail() {
	for (var elem of inputs) {
	    elem.disabled = false;
	    if (elem.type == "submit") {
		elem.name = "RSVP";
	    }
	}
    }

    xhr.open("GET", "http://localhost:8080/form/" + encodeURIComponent(token),
	     "false");
    xhr.onload = function() {
	if (xhr.status == 403) {
	    console.log("wrong password");
	    fail();
	    return;
	}

	alert(xhr.responseText);
    }
    xhr.onerror = function() {
	console.log(xhr.response);
	fail();
    }
    xhr.send();
}
