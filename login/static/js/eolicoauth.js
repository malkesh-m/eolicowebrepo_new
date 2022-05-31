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
    $('#exampleModal-login').modal('hide');
    // Do something... find out what can be done. Should open profile page if user logs in using login page.
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


