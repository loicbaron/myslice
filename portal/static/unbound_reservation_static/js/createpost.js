$(function() {


    // Submit post on submit
   // $('#b1').bind('click', function(event){
    //    event.preventDefault();
   //     console.log("form submitted!")  // sanity check
   //     create_post();
  //  });
 //var jsondata=document.getElementById("jsondata").value;
$('#b1').bind('click', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
		jsondata=document.getElementById("jsondata").value;
		user_data=document.getElementById("user_slices").value;
		//user_data="chrisap_slice";
		console.log(user_data);
        create_post(jsondata, user_data,1);
    });
	$('#b2').bind('click', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
		//jsondata=document.getElementById("jsondata").value;
		//user_data=document.getElementById("user_slices").value;
        create_post(jsondata, user_data,2);
    });
    // AJAX for posting
function addtitle(text,id) {
  var title = document.createElementNS("http://www.w3.org/2000/svg","title");
  title.textContent = text;
  document.getElementById(id).appendChild(title);
}

    function create_post(jsondata, user_data,b) {
	
	$("button").hide(300);
	  $("#but").show(6000);
	$('#but').html('<img src="http://preloaders.net/preloaders/287/Filling%20broken%20ring.gif"> ');
        console.log("create post is working!")
console.log(JSON.stringify(jsondata));	
var obj = jQuery.parseJSON(jsondata);
console.log(JSON.stringify(obj));
	// sanity check
		var myEvent = {"resources":[{"type": "Node"},{"type": "Node"}]};
		console.log(JSON.stringify(myEvent));
		//jsondata=JSON.parse(JSON.parse(json).jsondata);
		jsondata=jsondata.replace("\\", "");
		console.log(obj);
        $.ajax({
            url : "create_post/", // the endpoint
            type : "POST", // http method
            data : {"name" : user_data, "mitsos" : JSON.stringify(obj), "b": b}, // data sent with the post request
            // handle a successful response
			complete:function(){
			//alert("Request completed");
            $("#but").hide();
			$("button").show();
			$("#b2").show();
        },
            success : function(data,status) {
                
                console.log(data,status); // log the returned json to the console
               
			   var obj = JSON.parse(data);
var objson = JSON.parse(jsondata);
			  // alert(data);
			for (var i = 0; i < obj.resource_response.resources.length; i++) {
			var k=i+1;
			var m='#'+k;
			var ob='#72';
			   input_2 = "<span> Node-"+k+"</span>"+
					//"<div class='msglabel'>"<div class='msglabel'>+obj.resource_response.resources[0].domain+"<br>"+obj.resource_response.resources[0].name+"</div>"+
					"<div class='connect'><div class='msglabel'>domain:"+obj.resource_response.resources[i].domain+"<br>name:"+obj.resource_response.resources[i].name+"<br>"+obj.resource_response.resources[i].urn+"</div></div>";
			   $(m).html(input_2);
			   //$(ob).html(input_2);
			//   alert($('#72 text').html());
//alert(objson.resources[i].name);
addtitle(obj.resource_response.resources[i].urn,objson.resources[i].name);
elemid='#'+objson.resources[i].name+ ' text';
			  $(elemid).html(obj.resource_response.resources[i].name);
			   }
			   
                console.log("success"); // another sanity check
            },
            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log("papapa" + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
