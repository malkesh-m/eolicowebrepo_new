// Eolico authentication functions only. 
// Please DO NOT add functions related to some other site functionality.
// Supriyo.

function dologin(){
  usrname = document.frmlogin.username.value.replace(/^\s+|\s+$/gm,'');
  passwrd = document.frmlogin.passwd.value.replace(/^\s+|\s+$/gm,'');
  csrf = document.frmlogin.csrfmiddlewaretoken.value;
  if(usrname == "" || passwrd == ""){
    alert("Username or password cannot be empty");
    return(false);
  }
  var xmlhttp;
  let formData = new FormData();
  formData.append("username", usrname); 
  formData.append("passwd", passwrd); 
  if (window.XMLHttpRequest){
    xmlhttp=new XMLHttpRequest();
  }
  else{
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  // Register the handler
  xmlhttp.onreadystatechange = function(){
  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
    try{
        $('#exampleModal-login').modal('hide'); // Try hiding the modal window, if one is open.
    }
    catch(err){ // If we can't find the modal window, it is ok. User is probably logging in through the login page.
    }
    // Should open profile page if user logs in using login page.
    loginpagepattern = new RegExp(/login\/show\//);
    if(window.location.href.match(loginpagepattern)){
	// Redirect to the profile page
	window.location.href = "/login/profile/";
    }
    else{ // Else, simply refresh the current page
    	window.location.href = window.location.href; // Simply refresh the page so that user can see the logged-in view.
    }
  }
  };
  xmlhttp.open("POST", "/login/dologin/");
  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
  xmlhttp.send(formData);
}

function doregister(){
  if(document.frmsignup.agree.checked == false){
    alert("Please agree to Terms of Use, Privacy Policy, and Conditions of sale");
    return(false);
  }
  csrf = document.frmsignup.csrfmiddlewaretoken.value;
  usrname = document.frmsignup.username.value.replace(/^\s+|\s+$/gm,'');
  email = document.frmsignup.emailid.value.replace(/^\s+|\s+$/gm,'');
  passwrd1 = document.frmsignup.password1.value.replace(/^\s+|\s+$/gm,'');
  passwrd2 = document.frmsignup.password2.value.replace(/^\s+|\s+$/gm,'');
  if(passwrd1 != passwrd2){
    alert("The two passwords entered do not match");
    return(false);
  }
  if(usrname == ""){
    alert("Username cannot be empty");
    return(false);
  }
  if(email == ""){
    alert("Email address cannot be empty");
    return(false);
  }
  emailPattern = new RegExp(/^\w+\.?\w*@\w+\.\w{3,4}$/g);
  if(!email.match(emailPattern)){
    alert("Email address entered is not valid");
    return(false);
  }
  csrf = document.frmlogin.csrfmiddlewaretoken.value;
  var xmlhttp;
  let formData = new FormData();
  formData.append("username", usrname); 
  formData.append("emailid", email); 
  formData.append("password1", passwrd1); 
  formData.append("password2", passwrd2);
  if (window.XMLHttpRequest){
    xmlhttp=new XMLHttpRequest();
  }
  else{
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  // Register the handler
  xmlhttp.onreadystatechange = function(){
  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
    content = JSON.parse(xmlhttp.responseText);
    if(content['error'].length > 0){
      errcontainer = document.getElementById("errormsg");
      errcontainer.innerHTML = content['error'];
    }
    else{
      $('#exampleModal-signup').modal('hide');
      window.location.href = "/login/index/"
    }
  }
  };
  xmlhttp.open("POST", "/login/registration/");
  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
  xmlhttp.send(formData);
}

function checklogin(){
  var xmlhttp;
  if (window.XMLHttpRequest){
    xmlhttp=new XMLHttpRequest();
  }
  else{
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  // Register the handler
  xmlhttp.onreadystatechange = function(){
  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
    return(xmlhttp.responseText); // This will return a true or false value.
  }
  };
  xmlhttp.open("GET", "/login/checklogin/");
  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
  xmlhttp.send();
}


function follow(artistid, divid){
  var xmlhttp;
  divelement = document.getElementById(divid);
  csrf = document.frmedit.csrfmiddlewaretoken.value;
  if (window.XMLHttpRequest){
    xmlhttp=new XMLHttpRequest();
  }
  else{
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  // Register the handler
  xmlhttp.onreadystatechange = function(){
  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
    resp = JSON.parse(xmlhttp.responseText)
    msg = resp['msg'];
    divid = resp['div_id'];
    aid = resp['aid'];
    if(msg == 1){
      divelement = document.getElementById(divid);
      divelement.innerHTML = "<h6>Following (<a href='#/' style='color:#000000;bgcolor:#ffffff;' onclick='javascript:unfollow(" + aid + ", \"" + divid + "\");'>Leave</a>)</h6>";
    }
    else{
      // Show an alert stating that the operation was not successful
      alert("Could not perform the operation successfully. Please try again.");
      return(false);
    }
  }
  };
  divelement.innerHTML = "<img src='/static/images/loading.gif'>";
  postdata="aid=" + artistid + "&csrfmiddlewaretoken=" + csrf + "&div_id=" + divid;
  //alert(postdata);
  xmlhttp.open("POST", "/login/follow/");
  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
  xmlhttp.send(postdata);
}


function unfollow(artistid, divid){
  var xmlhttp;
  divelement = document.getElementById(divid);
  csrf = document.frmedit.csrfmiddlewaretoken.value;
  if (window.XMLHttpRequest){
    xmlhttp=new XMLHttpRequest();
  }
  else{
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  // Register the handler
  xmlhttp.onreadystatechange = function(){
  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
    resp = JSON.parse(xmlhttp.responseText)
    msg = resp['msg'];
    divid = resp['div_id'];
    aid = resp['aid'];
    if(msg == 1){
      divelement = document.getElementById(divid);
      divelement.innerHTML = "<h6><a href='#/' style='color:#000000;bgcolor:#ffffff;' onclick='javascript:follow(" + aid + ", \"" + divid + "\");'>Follow</a></h6>";
    }
    else{
      // Show an alert stating that the operation was not successful
      alert("Could not perform the operation successfully. Please try again.");
      return(false);
    }
  }
  };
  divelement.innerHTML = "<img src='/static/images/loading.gif'>";
  postdata="aid=" + artistid + "&csrfmiddlewaretoken=" + csrf + "&div_id=" + divid;
  //alert(postdata);
  xmlhttp.open("POST", "/login/unfollow/");
  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
  xmlhttp.send(postdata);
}


function addtofavourites(entitytype, entityid, divid){
  var xmlhttp;
  divelement = document.getElementById(divid);
  csrf = document.frmedit.csrfmiddlewaretoken.value;
  if (window.XMLHttpRequest){
    xmlhttp=new XMLHttpRequest();
  }
  else{
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  // Register the handler
  xmlhttp.onreadystatechange = function(){
  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
    resp = JSON.parse(xmlhttp.responseText)
    msg = resp['msg'];
    divid = resp['div_id'];
    aid = resp['aid'];
    awid = resp['awid'];
    aucid = resp['aucid']; // Only one of the above 3 Ids will be returned by the python API.
    if(msg == 1){
      divelement = document.getElementById(divid);
      divelement.innerHTML = "<h6>My Favourite</h6>";
    }
    else{
      // Show an alert stating that the operation was not successful
      alert("Could not perform the operation successfully. Please try again.");
      return(false);
    }
  }
  };
  divelement.innerHTML = "<img src='/static/images/loading.gif'>";
  postdata="entitytype=" + entitytype + "&entityid=" + entityid + "&csrfmiddlewaretoken=" + csrf + "&div_id=" + divid;
  //alert(postdata);
  if(entitytype == 'artist'){
    xmlhttp.open("POST", "/artist/favourite/");
  }
  else if(entitytype == 'artwork'){
    xmlhttp.open("POST", "/artist/favouritework/");
  }
  else if(entitytype == 'auction'){
    xmlhttp.open("POST", "/auction/favourite/");
  }
  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
  xmlhttp.send(postdata);
}


