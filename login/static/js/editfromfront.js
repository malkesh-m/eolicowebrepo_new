// Javascript functions to allow admin user to edit entities from frontend edit links.
// Author: Supriyo

function t_editcarousel(entity, entity_id){
    //alert(entity_id);
    //alert(document.getElementById('frmedit').csrfmiddlewaretoken.value);
    csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    carform = document.getElementById('frmedit');
	    carform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    //console.log(JSON.stringify(context));
	    cardict = context['carouseldict'];
            cardatatype = cardict['carouseldatatype'];
            cardataentry = cardict['carouseldataentry'];
            cardatadict = context['carouseldatadict'];
	    carpriority = cardict['selpriority'];
	    pagetitlediv = document.getElementById("pagetitle");
            pagetitlediv.innerHTML = "<h3>Edit Carousel Entry</h3>";
	    gform += "<div class='card-title'><h4>Entry Title</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Entry Title' name='carouselitemname' value='" + cardict['carouselitemname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Entry Text</h4></div><div class='form-group'><textarea class='form-control input-default' name='carouselitemtext'>" + cardict['carouselitemtext'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Image</h4></div><div class='form-group'><input type='file' name='carouselimage' id='carouselimage' class='form-control input-default'><a href='" + cardict['carouselimage'] + "'><img src='" + cardict['carouselimage'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Data Type</h4></div><div class='form-group'><select class='form-control input-default' name='seldatatype' id='seldatatype' onchange='javascript:populateentrydata();'>";
	    if(cardatatype == "gallery"){
		gform += "<option value=''>Select Type</option><option value='gallery' 'selected'>Gallery</option><option value='gevent'>Gallery Event</option><option value='museum'>Museum</option><option value='mevent'>Museum Event</option><option value='auction'>Auction</option> <option value='artist'>Artist</option><option value='auctionhouse'>Auction House</option>";
	    }
	    else if(cardatatype == "gevent"){
		gform += "<option value=''>Select Type</option><option value='gallery'>Gallery</option><option value='gevent' 'selected'>Gallery Event</option><option value='museum'>Museum</option><option value='mevent'>Museum Event</option><option value='auction'>Auction</option> <option value='artist'>Artist</option><option value='auctionhouse'>Auction House</option>";
	    }
	    else if(cardatatype == "museum"){
		gform += "<option value=''>Select Type</option><option value='gallery'>Gallery</option><option value='gevent'>Gallery Event</option><option value='museum' 'selected'>Museum</option><option value='mevent'>Museum Event</option><option value='auction'>Auction</option> <option value='artist'>Artist</option><option value='auctionhouse'>Auction House</option>";
	    }
	    else if(cardatatype == "mevent"){
		gform += "<option value=''>Select Type</option><option value='gallery'>Gallery</option><option value='gevent'>Gallery Event</option><option value='museum'>Museum</option><option value='mevent' 'selected'>Museum Event</option><option value='auction'>Auction</option> <option value='artist'>Artist</option><option value='auctionhouse'>Auction House</option>";
	    }
	    else if(cardatatype == "artist"){
		gform += "<option value=''>Select Type</option><option value='gallery'>Gallery</option><option value='gevent'>Gallery Event</option><option value='museum'>Museum</option><option value='mevent'>Museum Event</option><option value='auction'>Auction</option> <option value='artist' 'selected'>Artist</option><option value='auctionhouse'>Auction House</option>";
	    }
	    else if(cardatatype == "auction"){
		gform += "<option value=''>Select Type</option><option value='gallery'>Gallery</option><option value='gevent'>Gallery Event</option><option value='museum'>Museum</option><option value='mevent'>Museum Event</option><option value='auction' 'selected'>Auction</option> <option value='artist'>Artist</option><option value='auctionhouse'>Auction House</option>";
	    }
	    else if(cardatatype == "auctionhouse"){
		gform += "<option value=''>Select Type</option><option value='gallery'>Gallery</option><option value='gevent'>Gallery Event</option><option value='museum'>Museum</option><option value='mevent'>Museum Event</option><option value='auction'>Auction</option> <option value='artist'>Artist</option><option value='auctionhouse' 'selected'>Auction House</option>";
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Select Entry</h4></div><div class='form-group'><select class='form-control input-default' name='seldataentry' id='seldataentry'>";
	    for (const [entname, entid] of Object.entries(cardatadict)){
		if(cardataentry == entid){
		    gform += "<option value='" + entid + "' 'selected'>" + entname + "</option>";
		}
		else{
		    gform += "<option value='" + entid + "'>" + entname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Select Priority</h4></div><div class='form-group'><select class='form-control input-default' name='selpriority' id='selpriority'>";
	    if(carpriority == "1"){
		gform += "<option value=''>Select Priority</option><option value='1' selected>1 </option><option value='2'>2 </option><option value='3'>3 </option><option value='4'>4 </option><option value='5'>5 </option>";
	    }
	    else if(carpriority == "2"){
		gform += "<option value=''>Select Priority</option><option value='1'>1 </option><option value='2' selected>2 </option><option value='3'>3 </option><option value='4'>4 </option><option value='5'>5 </option>";
	    }
	    else if(carpriority == "3"){
		gform += "<option value=''>Select Priority</option><option value='1'>1 </option><option value='2'>2 </option><option value='3' selected>3 </option><option value='4'>4 </option><option value='5'>5 </option>";
	    }
	    else if(carpriority == "4"){
		gform += "<option value=''>Select Priority</option><option value='1'>1 </option><option value='2'>2 </option><option value='3'>3 </option><option value='4' selected>4 </option><option value='5'>5 </option>";
	    }
	    else if(carpriority == "5"){
		gform += "<option value=''>Select Priority</option><option value='1'>1 </option><option value='2'>2 </option><option value='3'>3 </option><option value='4'>4 </option><option value='5' selected>5 </option>";
	    }
    	    gform += "</select></div>";
	    gform += "<div class='card-title'><input type='button' name='addnewcarousel' class='form-control input-default' value='Save Carousel' onclick='javascript:t_savecarousel();'></div>";
	    gform += "<div class='card-title' id='crstatus'></div>";
	    gform += "<input type='hidden' name='carid' value='" + entity_id + "'>";
	    carform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editcarousel/?carid=" + entity_id);
	  xmlhttp.send();
}

function t_savecarousel(entity, entity_id){
    //alert(entity_id);
    //alert(document.getElementById('frmedit').csrfmiddlewaretoken.value);
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  carouselnm = document.frmedit.carouselitemname.value;
	  carouselval = document.frmedit.carouselitemtext.value;
	  carouseldt = document.frmedit.seldatatype.options[document.frmedit.seldatatype.options.selectedIndex].value;
	  carouselde = document.frmedit.seldataentry.options[document.frmedit.seldataentry.options.selectedIndex].value;
	  carouselpr = document.frmedit.selpriority.options[document.frmedit.selpriority.options.selectedIndex].value;
	  entity_id = document.frmedit.carid.value;
	  let formData = new FormData();
	  let carouselimg = document.getElementById("carouselimage").files[0];
	  formData.append("carouselimage", carouselimg);
	  //alert(formData);
	  formData.append("carouselitemname", carouselnm); 
	  formData.append("carouselitemtext", carouselval); 
 	  formData.append("seldatatype", carouseldt); 
	  formData.append("seldataentry", carouselde); 
	  formData.append("selpriority", carouselpr);
	  formData.append("carid", entity_id);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('crstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savecarousel/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editgallery(gid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	//alert(csrf);
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
	    galform = document.getElementById('frmedit');
	    galform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    gallerydict = context['gallery'];
	    gallerytypes = context['gallerytypes'];
	    gform += "<div class='card-title'><h4>Gallery Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Gallery Name' name='galleryname' value='" + gallerydict['galleryname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Gallery Location</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Gallery Location' name='gallerylocation' value='" + gallerydict['location'] + "'></div>";
	    gform += "<div class='card-title'><h4>Gallery Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='gallerydescription'>" + gallerydict['description'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Gallery Website</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Gallery Website' name='gallerywebsite' value='" + gallerydict['website'] + "'></div>";
	    gform += "<div class='card-title'><h4>Gallery Type</h4></div><div class='form-group'>";
	    gform += "<select name='selgallerytype' id ='selgallerytype' class='form-control input-default'><option value=''>Select type </option>";
	    for(var i=0; i < gallerytypes.length; i++){
		if(gallerytypes[i] == gallerydict['gallerytype']){
		gform += "<option value='" + gallerytypes[i] + "' selected>" + gallerytypes[i] + "</option>";
		}
		else{
		gform += "<option value='" + gallerytypes[i] + "'>" + gallerytypes[i] + "</option>";
		}
	    }
	    gform += "<option value='none'>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Enter Gallery Type' name='gallerytype'></div>";
	    gform += "<div class='card-title'><h4>Gallery Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selgallerypriority' id='selgallerypriority' class='form-control input-default'><option value=''>Select type </option>";
	    for(i=1; i <= 5; i++){
		if(gallerydict['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Gallery Cover Image</h4></div><div class='form-group'><input type='file' name='gallerycoverimage' id='gallerycoverimage' class='form-control input-default'><a href='" + gallerydict['coverimage'] + "'><img src='" + gallerydict['coverimage'] + "'></a></div>";
	    gform += "<div class='card-title'><input type='button' name='addnewgallery' class='form-control input-default' value='Save Gallery' onclick='javascript:savegallery();'></div>";
	    gform += "<div class='card-title' id='galstatus'></div>";
	    gform += "<input type='hidden' name='gid' value='" + gallerydict['id'] + "'>";
	    galform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editgallery/?gid=" + gid);
	  xmlhttp.send();

}

function t_savegallery(gid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  gallerynm = document.frmedit.galleryname.value;
	  galleryloc = document.frmedit.gallerylocation.value;
	  gallerydesc = document.frmedit.gallerydescription.value;
	  galleryweburl = document.frmedit.gallerywebsite.value;
	  //galleryseltype = document.frmedit.selgallerytype.options[document.frmedit.selgallerytype.options.selectedIndex].value;
	  galleryseltype = document.getElementById('selgallerytype').value;
	  //gallerypr = document.frmedit.selgallerypriority.options[document.frmedit.selgallerypriority.options.selectedIndex].value;
  	  gallerypr = document.getElementById('selgallerypriority').value;
	  gallerycover = document.frmedit.gallerycoverimage.value;
	  galid = document.frmedit.gid.value;
  	  postdata = "galleryname=" + gallerynm + "&gallerylocation=" + galleryloc + "&gallerydescription=" + gallerydesc + "&gallerywebsite=" + galleryweburl + "&selgallerytype=" + galleryseltype + "&selgallerypriority=" + gallerypr + "&gallerycoverimage=" + gallerycover;
	  let formData = new FormData();
	  //alert(formData);
	  let coverimage = document.getElementById("gallerycoverimage").files[0];
	  formData.append("gallerycoverimage", coverimage); 
	  formData.append("galleryname", gallerynm); 
	  formData.append("gallerylocation", galleryloc); 
	  formData.append("gallerydescription", gallerydesc); 
 	  formData.append("gallerywebsite", galleryweburl); 
	  formData.append("selgallerypriority", gallerypr); 
	  if (galleryseltype == ""){
	    galleryseltype = document.frmedit.gallerytype.value;
	  }
	  formData.append("selgallerytype", galleryseltype);
	  formData.append("gid", galid);
	  var xmlhttp;
	  if (window.XMLHttpRequest){
	    xmlhttp=new XMLHttpRequest();
	  }
	  else{
	    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	  }
	  // Register the handler
          postdata += "&csrfmiddlewaretoken=" + csrf;
	  xmlhttp.onreadystatechange = function(){
	  if(xmlhttp.readyState == 4 && xmlhttp.status==200){
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('galstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savegallery/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editgevent(gevid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    gevform = document.getElementById('frmedit');
	    gevform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    geventsdict = context['gevent'];
	    geventtypes = context['geventtypes'];
	    galleries = context['galleriesdict'];
	    gform += "<div class='card-title'><h4>Event Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Event Name' name='geventname' value='" + geventsdict['eventname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Gallery Name</h4></div><div class='form-group'>";
	    gform += "<select name='selgalleryname' id ='selgalleryname' class='form-control input-default'><option value=''>Select Gallery </option>";
	    for (const [galname, galid] of Object.entries(galleries)){
		if(geventsdict['galleryname'] == galname){
		gform += "<option value='" + galid + "' selected>" + galname + "</option>";
		}
		else{
		gform += "<option value='" + galid + "'>" + galname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Location</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Event Location' name='geventlocation' value='" + geventsdict['location'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event Info</h4></div><div class='form-group'><textarea class='form-control input-default ' name='geventinfo'>" + geventsdict['eventinfo'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Event Type</h4></div><div class='form-group'>";
	    gform += "<select name='selgeventtype' id ='selgeventtype' class='form-control input-default'><option value=''>Select type </option>";
	    for(var i=0; i < geventtypes.length; i++){
		if(geventtypes[i] == geventsdict['eventtype']){
		gform += "<option value='" + geventtypes[i] + "' selected>" + geventtypes[i] + "</option>";
		}
		else{
		gform += "<option value='" + geventtypes[i] + "'>" + geventtypes[i] + "</option>";
		}
	    }
	    gform += "<option value='none'>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Enter Event Type' name='geventtype'></div>";
	    gform += "<div class='card-title'><h4>Event Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selgeventpriority' id='selgeventpriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(geventsdict['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Status</h4></div><div class='form-group'><select name='selgeventstatus' class='form-control input-default'><option value=''>Select Status </option>";
	    if(geventsdict['eventstatus'] == "upcoming"){
	        gform += "<option value='upcoming' selected>Upcoming </option>";
	    }
	    else{
		gform += "<option value='upcoming'>Upcoming </option>";
	    }
	    if(geventsdict['eventstatus'] == "ongoing"){
	        gform += "<option value='ongoing' selected>Ongoing </option>";
	    }
	    else{
		gform += "<option value='ongoing'>Ongoing </option>";
	    }
	    if(geventsdict['eventstatus'] == "past"){
	        gform += "<option value='past' selected>Past </option>";
	    }
	    else{
		gform += "<option value='past'>Past </option>";
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Start Date</h4></div><div class='form-group'><input type='date' class='form-control input-default ' placeholder='' name='geventstartdate' value='" + geventsdict['eventstartdate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event End Date</h4></div><div class='form-group'><input type='date' class='form-control input-default ' placeholder='' name='geventenddate' value='" + geventsdict['eventenddate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event Cover Image</h4></div><div class='form-group'><input type='file' name='geventcoverimage' id='geventcoverimage' class='form-control input-default'><a href='" + geventsdict['coverimage'] + "'><img src='" + geventsdict['coverimage'] + "'></a></div>";
	    gform += "<div class='card-title'><input type='button' name='editgevent' class='form-control input-default' value='Save Event' onclick='javascript:savegevent();'></div>";
	    gform += "<div class='card-title' id='gevstatus'></div>";
	    gform += "<input type='hidden' name='gevid' value='" + geventsdict['id'] + "'>";
	    gevform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editgevent/?evid=" + gevid);
	  xmlhttp.send();
}

function t_savegevent(gevid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  eventnm = document.frmedit.geventname.value;
	  eventloc = document.frmedit.geventlocation.value;
	  galleryid = document.frmedit.selgalleryname.options[document.frmedit.selgalleryname.options.selectedIndex].value;
	  eventinfo = document.frmedit.geventinfo.innerHTML;
	  eventtype = document.frmedit.selgeventtype.options[document.frmedit.selgeventtype.options.selectedIndex].value;
	  eventseltype = document.frmedit.selgeventtype.options[document.frmedit.selgeventtype.options.selectedIndex].value;
	  eventpr = document.frmedit.selgeventpriority.options[document.frmedit.selgeventpriority.options.selectedIndex].value;
	  eventstatus = document.frmedit.selgeventstatus.options[document.frmedit.selgeventstatus.options.selectedIndex].value;
	  geventcover = document.frmedit.geventcoverimage.value;
	  eventstartdate = document.frmedit.geventstartdate.value;
	  eventenddate = document.frmedit.geventenddate.value;
	  gevid = document.frmedit.gevid.value;
	  let formData = new FormData();
	  let coverimage = document.getElementById("geventcoverimage").files[0];
	  formData.append("geventcoverimage", coverimage); 
	  if (eventseltype == ""){
	    eventseltype = document.frmedit.geventtype.value;
	  }
	  formData.append("geventname", eventnm); 
	  formData.append("geventlocation", eventloc); 
	  formData.append("geventinfo", eventinfo); 
 	  formData.append("geventstartdate", eventstartdate); 
	  formData.append("geventenddate", eventenddate); 
	  formData.append("selgalleryname", galleryid); 
	  formData.append("selgeventtype", eventseltype);
	  formData.append("selgeventstatus", eventstatus); 
	  formData.append("selgeventpriority", eventpr); 
	  formData.append("gevid", gevid); 
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('gevstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savegevent/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editartist(artistid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    artform = document.getElementById('frmedit');
	    artform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    eventsdict = context['eventsdict'];
	    artistsdict = context['artistsdict'];
	    gform += "<div class='card-title'><h4>Artist Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Name' name='artistname' value='" + artistsdict['artistname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event Name</h4></div><div class='form-group'>";
	    gform += "<select name='seleventname' id ='seleventname' class='form-control input-default'><option value=''>Select Event </option>";
	    for (const [evname, evid] of Object.entries(eventsdict)){
		if(evid == artistsdict['eventid']){
		gform += "<option value='" + evid + "' selected>" + evname + "</option>";
		}
		else{
		gform += "<option value='" + evid + "'>" + evname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>About Artist</h4></div><div class='form-group'><textarea class='form-control input-default' placeholder='' name='aboutartist'>" + artistsdict['about'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Artist Nationality</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Nationality' name='artistnationality' value='" + artistsdict['nationality'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Birth Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Birth Year' name='artistbirth' value='" + artistsdict['artistbirth'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Death Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Death Year' name='artistdeath' value='" + artistsdict['artistdeath'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Gender</h4></div><div class='form-group'>";
	    gform += "<select name='selgender' id ='selgender' class='form-control input-default'><option value=''>Select Gender </option>";
		if(artistsdict['gender'] == "male"){
		gform += "<option value='male' selected>Male</option>";
		}
		else{
		gform += "<option value='male'>Male</option>";
		}
		if(artistsdict['gender'] == "female"){
		gform += "<option value='female' selected>Female</option>";
		}
		else{
		gform += "<option value='female'>Female</option>";
		}
		if(artistsdict['gender'] == "none"){
		gform += "<option value='none' selected>Can't Decide</option>";
		}
		else{
		gform += "<option value='none'>Can't Decide</option>";
		}
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Artist Cover Image</h4></div><div class='form-group'><input type='file' name='artistcoverimage' id='artistcoverimage' class='form-control input-default'><a href='" + artistsdict['squareimage'] + "'><img src='" + artistsdict['squareimage'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artist Large Image</h4></div><div class='form-group'><input type='file' name='artistlargeimage' id='artistlargeimage' class='form-control input-default'><a href='" + artistsdict['largeimage'] + "'><img src='" + artistsdict['largeimage'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artist URL</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist URL' name='artistprofileurl' value='" + artistsdict['artistprofileurl'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selartistpriority' id='selartistpriority' class='form-control input-default'><option value=''>Select type </option>";
	    for(i=1; i <= 5; i++){
		if(artistsdict['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><input type='button' name='addnewartist' class='form-control input-default' value='Save Artist' onclick='javascript:saveartist();'></div>";
	    gform += "<div class='card-title' id='artiststatus'></div>";
	    gform += "<input type='hidden' name='aid' value='" + artistsdict['id'] + "'>";
	    artform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editartist/?aid=" + artistid);
	  xmlhttp.send();
}

function t_saveartist(aid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  artistnm = document.frmedit.artistname.value;
	  aboutartist = document.frmedit.aboutartist.value;
	  artistnationality = document.frmedit.artistnationality.value;
	  artistbirth = document.frmedit.artistbirth.value;
	  artistdeath = document.frmedit.artistdeath.value;
	  seleventname = document.getElementById('seleventname').value;
  	  artistpr = document.getElementById('selartistpriority').value;
	  artistgender = document.getElementById('selgender').value;
	  artistpriority = document.getElementById('selartistpriority').value;
	  artistprofileurl = document.frmedit.artistprofileurl.value;
	  aid = document.frmedit.aid.value;
	  let formData = new FormData();
	  //alert(formData);
	  let coverimage = document.getElementById("artistcoverimage").files[0];
	  let largeimage = document.getElementById("artistlargeimage").files[0];
	  formData.append("artistcoverimage", coverimage); 
	  formData.append("artistlargeimage", largeimage);
	  formData.append("artistname", artistnm); 
	  formData.append("aboutartist", aboutartist); 
	  formData.append("artistnationality", artistnationality); 
 	  formData.append("artistbirth", artistbirth); 
	  formData.append("artistdeath", artistdeath); 
	  formData.append("seleventname", seleventname); 
	  formData.append("selgender", artistgender); 
	  formData.append("selartistpriority", artistpriority); 
	  formData.append("artistprofileurl", artistprofileurl); 
	  formData.append("aid", aid);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('artiststatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/saveartist/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editartwork(awid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    awform = document.getElementById('frmedit');
	    awform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    geventsdict = context['gevents'];
	    artwork = context['artwork'];
	    galleries = context['galleriesdict'];
	    gform += "<div class='card-title'><h4>Artwork Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artwork Name' name='artworkname' value='" + artwork['artworkname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Gallery Name</h4></div><div class='form-group'>";
	    gform += "<select name='selgalleryname' id ='selgalleryname' class='form-control input-default' onchange='javascript:populategevents();'><option value=''>Select Gallery </option>";
	    for (const [galname, galid] of Object.entries(galleries)){
		if(artwork['gallery'] == galid){
		gform += "<option value='" + galid + "' selected>" + galname + "</option>";
		}
		else{
		gform += "<option value='" + galid + "'>" + galname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Name</h4></div><div class='form-group'>";
	    gform += "<select name='selgeventname' id ='selgeventname' class='form-control input-default'><option value=''>Select Event </option>";
	    for (const [gevname, gevid] of Object.entries(geventsdict)){
		if(artwork['event'] == gevid){
		gform += "<option value='" + gevid + "' selected>" + gevname + "</option>";
		}
		else{
		gform += "<option value='" + gevid + "'>" + gevname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Artist Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Name' name='artistname' value='" + artwork['artistname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Birth Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Birth Year' name='artistbirth' value='" + artwork['artistbirthyear'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Death Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Death Year' name='artistdeath' value='" + artwork['artistdeathyear'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Nationality</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Nationality' name='artistnationality' value='" + artwork['artistnationality'] + "'></div>";
	    gform += "<div class='card-title'><h4>Medium</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Medium' name='medium' value='" + artwork['medium'] + "'></div>";
	    gform += "<div class='card-title'><h4>Size</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Size' name='size' value='" + artwork['size'] + "'></div>";
	    gform += "<div class='card-title'><h4>Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='artworkdescription'>" + artwork['description'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Signature</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Signature' name='signature' value='" + artwork['signature'] + "'></div>";
	    gform += "<div class='card-title'><h4>Letter of Authenticity</h4></div><div class='form-group'><textarea class='form-control input-default ' name='authenticity'>" + artwork['letterofauthenticity'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Estimate</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Estimate' name='estimate' value='" + artwork['estimate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Sold Price</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Sold Price' name='soldprice' value='" + artwork['soldprice'] + "'></div>";
	    gform += "<div class='card-title'><h4>Provenance</h4></div><div class='form-group'><textarea class='form-control input-default ' name='provenance'>" + artwork['provenance'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Literature</h4></div><div class='form-group'><textarea class='form-control input-default ' name='literature'>" + artwork['literature'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Exhibitions</h4></div><div class='form-group'><textarea class='form-control input-default ' name='exhibitions'>" + artwork['exhibitions'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Artwork URL</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artwork URL' name='artworkurl' value='" + artwork['workurl'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 1</h4></div><div class='form-group'><input type='file' name='image1' id='image1' class='form-control input-default'><a href='" + artwork['image1'] + "'><img src='" + artwork['image1'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 2</h4></div><div class='form-group'><input type='file' name='image2' id='image2' class='form-control input-default'><a href='" + artwork['image2'] + "'><img src='" + artwork['image2'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 3</h4></div><div class='form-group'><input type='file' name='image3' id='image3' class='form-control input-default'><a href='" + artwork['image3'] + "'><img src='" + artwork['image3'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 4</h4></div><div class='form-group'><input type='file' name='image4' id='image4' class='form-control input-default'><a href='" + artwork['image4'] + "'><img src='" + artwork['image4'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Event Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selartworkpriority' id='selartworkpriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(artwork['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";

	    gform += "<div class='card-title'><input type='button' name='editartwork' class='form-control input-default' value='Save Artwork' onclick='javascript:saveartwork();'></div>";
	    gform += "<div class='card-title' id='artworkstatus'></div>";
	    gform += "<input type='hidden' name='awid' value='" + artwork['id'] + "'>";
	    awform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editartwork/?awid=" + awid);
	  xmlhttp.send();
}

function t_saveartwork(awid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  artworknm = document.frmedit.artworkname.value;
	  selgalleryname = document.getElementById('selgalleryname').value;
	  selgeventname = document.getElementById('selgeventname').value;
	  artistname = document.frmedit.artistname.value;
	  artistbirth = document.frmedit.artistbirth.value;
	  artistdeath = document.frmedit.artistdeath.value;
	  artistnationality = document.frmedit.artistnationality.value;
	  medium = document.frmedit.medium.value;
	  size = document.frmedit.size.value;
	  artworkdesc = document.frmedit.artworkdescription.value;
	  //alert(artworkdesc);
	  signature = document.frmedit.signature.value;
	  authenticity = document.frmedit.authenticity.value;
	  estimate = document.frmedit.estimate.value;
	  soldprice = document.frmedit.soldprice.value;
	  provenance = document.frmedit.provenance.value;
	  literature = document.frmedit.literature.value;
	  exhibitions = document.frmedit.exhibitions.value;
	  artworkurl = document.frmedit.artworkurl.value;
	  priority = document.getElementById('selartworkpriority').value;
	  awid = document.frmedit.awid.value;
	  let formData = new FormData();
	  //alert(formData);
	  let image1 = document.getElementById("image1").files[0];
	  let image2 = document.getElementById("image2").files[0];
	  let image3 = document.getElementById("image3").files[0];
	  let image4 = document.getElementById("image4").files[0];
	  formData.append("image1", image1); 
	  formData.append("image2", image2);
	  formData.append("image3", image3);
	  formData.append("image4", image4);
	  formData.append("artworkname", artworknm); 
	  formData.append("galleryid", selgalleryname); 
	  formData.append("eventid", selgeventname); 
 	  formData.append("artistname", artistname); 
	  formData.append("artistbirth", artistbirth); 
	  formData.append("artistdeath", artistdeath); 
	  formData.append("artistnationality", artistnationality); 
	  formData.append("medium", medium); 
	  formData.append("size", size); 
	  formData.append("artworkdescription", artworkdesc); 
	  formData.append("signature", signature); 
	  formData.append("authenticity", authenticity); 
	  formData.append("estimate", estimate); 
	  formData.append("soldprice", soldprice); 
	  formData.append("provenance", provenance); 
	  formData.append("literature", literature); 
	  formData.append("exhibitions", exhibitions); 
	  formData.append("artworkurl", artworkurl); 
	  formData.append("priority", priority); 
	  formData.append("awid", awid);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('artworkstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/saveartwork/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editmuseum(mid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    musform = document.getElementById('frmedit');
	    musform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    museumdict = context['museum'];
	    museumtypes = context['museumtypes'];
	    gform += "<div class='card-title'><h4>Museum Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Museum Name' name='museumname' value='" + museumdict['museumname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Museum Location</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Museum Location' name='museumlocation' value='" + museumdict['location'] + "'></div>";
	    gform += "<div class='card-title'><h4>Museum Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='museumdescription'>" + museumdict['description'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Museum Website</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Museum Website' name='museumwebsite' value='" + museumdict['website'] + "'></div>";
	    gform += "<div class='card-title'><h4>Museum Type</h4></div><div class='form-group'>";
	    gform += "<select name='selmuseumtype' id ='selmuseumtype' class='form-control input-default'><option value=''>Select type </option>";
	    for(var i=0; i < museumtypes.length; i++){
		if(museumtypes[i] == museumdict['museumtype']){
		gform += "<option value='" + museumtypes[i] + "' selected>" + museumtypes[i] + "</option>";
		}
		else{
		gform += "<option value='" + museumtypes[i] + "'>" + museumtypes[i] + "</option>";
		}
	    }
	    gform += "<option value='none'>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Enter Museum Type' name='museumtype'></div>";
	    gform += "<div class='card-title'><h4>Museum Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selmuseumpriority' id='selmuseumpriority' class='form-control input-default'><option value=''>Select priority </option>";
	    for(i=1; i <= 5; i++){
		if(museumdict['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Museum Cover Image</h4></div><div class='form-group'><input type='file' name='museumcoverimage' id='museumcoverimage' class='form-control input-default'><a href='" + museumdict['coverimage'] + "'><img src='" + museumdict['coverimage'] + "'></a></div>";
	    gform += "<div class='card-title'><input type='button' name='addnewmuseum' class='form-control input-default' value='Save Museum' onclick='javascript:savemuseum();'></div>";
	    gform += "<div class='card-title' id='musstatus'></div>";
	    gform += "<input type='hidden' name='mid' value='" + museumdict['id'] + "'>";
	    musform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editmuseum/?mid=" + mid);
	  xmlhttp.send();
}

function t_savemuseum(mid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  museumnm = document.frmedit.museumname.value;
	  museumloc = document.frmedit.museumlocation.value;
	  museumdesc = document.frmedit.museumdescription.value;
	  museumweburl = document.frmedit.museumwebsite.value;
	  //museumseltype = document.frmedit.selmuseumtype.options[document.frmedit.selmuseumtype.options.selectedIndex].value;
	  museumseltype = document.getElementById('selmuseumtype').value;
	  //museumpr = document.frmedit.selmuseumpriority.options[document.frmedit.selmuseumpriority.options.selectedIndex].value;
  	  museumpr = document.getElementById('selmuseumpriority').value;
	  museumcover = document.frmedit.museumcoverimage.value;
	  musid = document.frmedit.mid.value;
	  let formData = new FormData();
	  //alert(formData);
	  let coverimage = document.getElementById("museumcoverimage").files[0];
	  formData.append("museumcoverimage", coverimage); 
	  formData.append("museumname", museumnm); 
	  formData.append("museumlocation", museumloc); 
	  formData.append("museumdescription", museumdesc); 
 	  formData.append("museumwebsite", museumweburl); 
	  formData.append("selmuseumpriority", museumpr); 
	  if (museumseltype == ""){
	    museumseltype = document.frmedit.museumtype.value;
	  }
	  formData.append("selmuseumtype", museumseltype);
	  formData.append("mid", musid);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('musstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savemuseum/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editmevent(mevid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    mevform = document.getElementById('frmedit');
	    mevform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    meventsdict = context['mevent'];
	    meventtypes = context['meventtypes'];
	    museums = context['museumsdict'];
	    gform += "<div class='card-title'><h4>Event Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Event Name' name='meventname' value='" + meventsdict['eventname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Museum Name</h4></div><div class='form-group'>";
	    gform += "<select name='selmuseumname' id ='selmuseumname' class='form-control input-default'><option value=''>Select museum </option>";
	    for (const [musname, musid] of Object.entries(museums)){
		if(meventsdict['museumname'] == musname){
		gform += "<option value='" + musid + "' selected>" + musname + "</option>";
		}
		else{
		gform += "<option value='" + musid + "'>" + musname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Location</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Event Location' name='meventlocation' value='" + meventsdict['location'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event Info</h4></div><div class='form-group'><textarea class='form-control input-default ' name='meventinfo'>" + meventsdict['eventinfo'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Event Type</h4></div><div class='form-group'>";
	    gform += "<select name='selmeventtype' id ='selmeventtype' class='form-control input-default'><option value=''>Select type </option>";
	    for(var i=0; i < meventtypes.length; i++){
		if(meventtypes[i] == meventsdict['eventtype']){
		gform += "<option value='" + meventtypes[i] + "' selected>" + meventtypes[i] + "</option>";
		}
		else{
		gform += "<option value='" + meventtypes[i] + "'>" + meventtypes[i] + "</option>";
		}
	    }
	    gform += "<option value='none'>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Enter Event Type' name='meventtype'></div>";
	    gform += "<div class='card-title'><h4>Event Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selmeventpriority' id='selmeventpriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(meventsdict['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Status</h4></div><div class='form-group'><select name='selmeventstatus' id='selmeventstatus' class='form-control input-default'><option value=''>Select Status </option>";
	    if(meventsdict['eventstatus'] == "upcoming"){
	        gform += "<option value='upcoming' selected>Upcoming </option>";
	    }
	    else{
		gform += "<option value='upcoming'>Upcoming </option>";
	    }
	    if(meventsdict['eventstatus'] == "ongoing"){
	        gform += "<option value='ongoing' selected>Ongoing </option>";
	    }
	    else{
		gform += "<option value='ongoing'>Ongoing </option>";
	    }
	    if(meventsdict['eventstatus'] == "past"){
	        gform += "<option value='past' selected>Past </option>";
	    }
	    else{
		gform += "<option value='past'>Past </option>";
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Start Date</h4></div><div class='form-group'><input type='date' class='form-control input-default ' placeholder='' name='meventstartdate' value='" + meventsdict['eventstartdate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event End Date</h4></div><div class='form-group'><input type='date' class='form-control input-default ' placeholder='' name='meventenddate' value='" + meventsdict['eventenddate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Event Cover Image</h4></div><div class='form-group'><input type='file' name='meventcoverimage' id='meventcoverimage' class='form-control input-default'><a href='" + meventsdict['coverimage'] + "'><img src='" + meventsdict['coverimage'] + "'></a></div>";
	    gform += "<div class='card-title'><input type='button' name='editmevent' class='form-control input-default' value='Save Event' onclick='javascript:savemevent();'></div>";
	    gform += "<div class='card-title' id='mevstatus'></div>";
	    gform += "<input type='hidden' name='mevid' value='" + meventsdict['id'] + "'>";
	    mevform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editmevent/?evid=" + mevid);
	  xmlhttp.send();
}

function t_savemevent(mevid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  eventnm = document.frmedit.meventname.value;
	  eventloc = document.frmedit.meventlocation.value;
	  museumid = document.frmedit.selmuseumname.options[document.frmedit.selmuseumname.options.selectedIndex].value;
	  eventinfo = document.frmedit.meventinfo.innerHTML;
	  eventtype = document.frmedit.selmeventtype.options[document.frmedit.selmeventtype.options.selectedIndex].value;
	  eventseltype = document.frmedit.selmeventtype.options[document.frmedit.selmeventtype.options.selectedIndex].value;
	  eventpr = document.frmedit.selmeventpriority.options[document.frmedit.selmeventpriority.options.selectedIndex].value;
	  eventstatus = document.frmedit.selmeventstatus.options[document.frmedit.selmeventstatus.options.selectedIndex].value;
	  meventcover = document.frmedit.meventcoverimage.value;
	  eventstartdate = document.frmedit.meventstartdate.value;
	  eventenddate = document.frmedit.meventenddate.value;
	  mevid = document.frmedit.mevid.value;
	  let formData = new FormData();
	  let coverimage = document.getElementById("meventcoverimage").files[0];
	  formData.append("meventcoverimage", coverimage); 
	  if (eventseltype == ""){
	    eventseltype = document.frmedit.meventtype.value;
	  }
	  formData.append("meventname", eventnm); 
	  formData.append("meventlocation", eventloc); 
	  formData.append("meventinfo", eventinfo); 
 	  formData.append("meventstartdate", eventstartdate); 
	  formData.append("meventenddate", eventenddate); 
	  formData.append("selmuseumname", museumid); 
	  formData.append("selmeventtype", eventseltype);
	  formData.append("selmeventstatus", eventstatus); 
	  formData.append("selmeventpriority", eventpr); 
	  formData.append("mevid", mevid); 
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('mevstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savemevent/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editmarticle(articleid){
}

function t_savemarticle(articleid){
}


function t_editmpiece(awid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    awform = document.getElementById('frmedit');
	    awform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    meventsdict = context['mevents'];
	    artwork = context['artwork'];
	    museums = context['museumsdict'];
	    //alert(museums);
	    gform += "<div class='card-title'><h4>Artwork Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artwork Name' name='artworkname' value='" + artwork['piecename'] + "'></div>";
	    gform += "<div class='card-title'><h4>Museum Name</h4></div><div class='form-group'>";
	    gform += "<select name='selmuseumname' id ='selmuseumname' class='form-control input-default' onchange='javascript:populatemevents();'><option value=''>Select Museum </option>";
	    for (const [musname, musid] of Object.entries(museums)){
		if(artwork['museum'] == musid){
		gform += "<option value='" + musid + "' selected>" + musname + "</option>";
		}
		else{
		gform += "<option value='" + musid + "'>" + musname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Event Name</h4></div><div class='form-group'>";
	    gform += "<select name='selmeventname' id ='selmeventname' class='form-control input-default'><option value=''>Select Event </option>";
	    for (const [mevname, mevid] of Object.entries(meventsdict)){
		if(artwork['event'] == mevid){
		gform += "<option value='" + mevid + "' selected>" + mevname + "</option>";
		}
		else{
		gform += "<option value='" + mevid + "'>" + mevname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Artist Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Name' name='artistname' value='" + artwork['artistname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Birth Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Birth Year' name='artistbirth' value='" + artwork['artistbirthyear'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Death Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Death Year' name='artistdeath' value='" + artwork['artistdeathyear'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Nationality</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Nationality' name='artistnationality' value='" + artwork['artistnationality'] + "'></div>";
	    gform += "<div class='card-title'><h4>Medium</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Medium' name='medium' value='" + artwork['medium'] + "'></div>";
	    gform += "<div class='card-title'><h4>Size</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Size' name='size' value='" + artwork['size'] + "'></div>";
	    gform += "<div class='card-title'><h4>Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='artworkdescription'>" + artwork['description'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Signature</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Signature' name='signature' value='" + artwork['signature'] + "'></div>";
	    //gform += "<div class='card-title'><h4>Letter of Authenticity</h4></div><div class='form-group'><textarea class='form-control input-default ' name='authenticity'>" + artwork['letterofauthenticity'] + "</textarea></div>";
	    //gform += "<div class='card-title'><h4>Estimate</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Estimate' name='estimate' value='" + artwork['estimate'] + "'></div>";
	    //gform += "<div class='card-title'><h4>Sold Price</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Sold Price' name='soldprice' value='" + artwork['soldprice'] + "'></div>";
	    gform += "<div class='card-title'><h4>Provenance</h4></div><div class='form-group'><textarea class='form-control input-default ' name='provenance'>" + artwork['provenance'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Literature</h4></div><div class='form-group'><textarea class='form-control input-default ' name='literature'>" + artwork['literature'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Exhibitions</h4></div><div class='form-group'><textarea class='form-control input-default ' name='exhibitions'>" + artwork['exhibitions'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Artwork URL</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artwork URL' name='artworkurl' value='" + artwork['workurl'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 1</h4></div><div class='form-group'><input type='file' name='image1' id='image1' class='form-control input-default'><a href='" + artwork['image1'] + "'><img src='" + artwork['image1'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 2</h4></div><div class='form-group'><input type='file' name='image2' id='image2' class='form-control input-default'><a href='" + artwork['image2'] + "'><img src='" + artwork['image2'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 3</h4></div><div class='form-group'><input type='file' name='image3' id='image3' class='form-control input-default'><a href='" + artwork['image3'] + "'><img src='" + artwork['image3'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Artwork Image 4</h4></div><div class='form-group'><input type='file' name='image4' id='image4' class='form-control input-default'><a href='" + artwork['image4'] + "'><img src='" + artwork['image4'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Event Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selartworkpriority' id='selartworkpriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(artwork['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";

	    gform += "<div class='card-title'><input type='button' name='editartwork' class='form-control input-default' value='Save Artwork' onclick='javascript:saveartwork();'></div>";
	    gform += "<div class='card-title' id='artworkstatus'></div>";
	    gform += "<input type='hidden' name='awid' value='" + artwork['id'] + "'>";
	    awform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editmpieces/?awid=" + awid);
	  xmlhttp.send();
}

function t_savempiece(awid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  artworknm = document.frmedit.artworkname.value;
	  selmuseumname = document.getElementById('selmuseumname').value;
	  selmeventname = document.getElementById('selmeventname').value;
	  artistname = document.frmedit.artistname.value;
	  artistbirth = document.frmedit.artistbirth.value;
	  artistdeath = document.frmedit.artistdeath.value;
	  artistnationality = document.frmedit.artistnationality.value;
	  medium = document.frmedit.medium.value;
	  size = document.frmedit.size.value;
	  artworkdesc = document.frmedit.artworkdescription.value;
	  //alert(artworkdesc);
	  signature = document.frmedit.signature.value;
	  //authenticity = document.frmedit.authenticity.value;
	  //estimate = document.frmedit.estimate.value;
	  //soldprice = document.frmedit.soldprice.value;
	  provenance = document.frmedit.provenance.value;
	  literature = document.frmedit.literature.value;
	  exhibitions = document.frmedit.exhibitions.value;
	  artworkurl = document.frmedit.artworkurl.value;
	  priority = document.getElementById('selartworkpriority').value;
	  awid = document.frmedit.awid.value;
	  let formData = new FormData();
	  //alert(formData);
	  let image1 = document.getElementById("image1").files[0];
	  let image2 = document.getElementById("image2").files[0];
	  let image3 = document.getElementById("image3").files[0];
	  let image4 = document.getElementById("image4").files[0];
	  formData.append("image1", image1); 
	  formData.append("image2", image2);
	  formData.append("image3", image3);
	  formData.append("image4", image4);
	  formData.append("artworkname", artworknm); 
	  formData.append("museumid", selmuseumname); 
	  formData.append("eventid", selmeventname); 
 	  formData.append("artistname", artistname); 
	  formData.append("artistbirth", artistbirth); 
	  formData.append("artistdeath", artistdeath); 
	  formData.append("artistnationality", artistnationality); 
	  formData.append("medium", medium); 
	  formData.append("size", size); 
	  formData.append("artworkdescription", artworkdesc); 
	  formData.append("signature", signature); 
	  //formData.append("authenticity", authenticity); 
	  //formData.append("estimate", estimate); 
	  //formData.append("soldprice", soldprice); 
	  formData.append("provenance", provenance); 
	  formData.append("literature", literature); 
	  formData.append("exhibitions", exhibitions); 
	  formData.append("artworkurl", artworkurl); 
	  formData.append("priority", priority); 
	  formData.append("awid", awid);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('artworkstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savempieces/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editauctionhouse(auchouseid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    auchouseform = document.getElementById('frmedit');
	    auchouseform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    auctionhousedict = context['auctionhousedict'];
	    allauctionhousetypes = context['allauctionhousetypes'];
	    gform += "<div class='card-title'><h4>Auction House Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Auction House Name' name='auctionhousename' value='" + auctionhousedict['auctionhousename'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction House Location</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Auction House Location' name='auctionhouselocation' value='" + auctionhousedict['auctionhouselocation'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction House Brief</h4></div><div class='form-group'><textarea class='form-control input-default ' name='auctionhousebrief'>" + auctionhousedict['auctionhousebrief'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Auction House URL</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Auction House URL' name='auctionhouse_url' value='" + auctionhousedict['auctionhouseurl'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction House Type</h4></div><div class='form-group'>";
	    gform += "<select name='selauctionhousetype' id ='selauctionhousetype' class='form-control input-default'><option value=''>Select Type </option>";
	    for(var i=0; i < allauctionhousetypes.length; i++){
		if(allauctionhousetypes[i] == auctionhousedict['auctionhousetype']){
		gform += "<option value='" + allauctionhousetypes[i] + "' selected>" + allauctionhousetypes[i] + "</option>";
		}
		else{
		gform += "<option value='" + allauctionhousetypes[i] + "'>" + allauctionhousetypes[i] + "</option>";
		}
	    }
	    gform += "<option value='none'>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Enter Auction House Type' name='auctionhousetype'></div>";
	    gform += "<div class='card-title'><h4>Auction House Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selauctionhousepriority' id='selauctionhousepriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(auctionhousedict['auctionhousepriority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Auction House Cover Image</h4></div><div class='form-group'><input type='file' name='auctionhousecoverimage' id='auctionhousecoverimage' class='form-control input-default'><a href='" + auctionhousedict['auctionhousecoverimage'] + "'><img src='" + auctionhousedict['auctionhousecoverimage'] + "'></a></div>";
	    gform += "<div class='card-title'><input type='button' name='editauctionhouse' class='form-control input-default' value='Save Auction House' onclick='javascript:saveauctionhouse();'></div>";
	    gform += "<div class='card-title' id='aucstatus'></div>";
	    gform += "<input type='hidden' name='ahid' value='" + auctionhousedict['id'] + "'>";
	    auchouseform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editauctionhouses/?ahid=" + auchouseid);
	  xmlhttp.send();
}

function t_saveauctionhouse(ahid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  auctionhousenm = document.frmedit.auctionhousename.value;
	  auctionhouseloc = document.frmedit.auctionhouselocation.value;
	  auctionhousedesc = document.frmedit.auctionhousebrief.value;
	  auctionhouseurl = document.frmedit.auctionhouse_url.value;
	  auctionhouseseltype = document.frmedit.selauctionhousetype.options[document.frmedit.selauctionhousetype.options.selectedIndex].value;
	  auctionhousetp = document.frmedit.auctionhousetype.value;
	  auctionhousepr = document.frmedit.selauctionhousepriority.options[document.frmedit.selauctionhousepriority.options.selectedIndex].value;
	  ahid = document.frmedit.ahid.value;
	  let formData = new FormData();
	  let coverimage = document.getElementById("auctionhousecoverimage").files[0];
	  formData.append("auctionhousecoverimage", coverimage); 
          if (auctionhouseseltype == ""){
	    auctionhouseseltype = auctionhousetp;
	  }
	  formData.append("auctionhousename", auctionhousenm); 
	  formData.append("auctionhouselocation", auctionhouseloc); 
	  formData.append("auctionhousebrief", auctionhousedesc); 
 	  formData.append("auctionhouse_url", auctionhouseurl); 
	  formData.append("selauctionhousetype", auctionhouseseltype); 
	  formData.append("selauctionhousepriority", auctionhousepr);
	  formData.append("ahid", ahid);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('aucstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/saveauctionhouses/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editauction(aucid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    aucform = document.getElementById('frmedit');
	    aucform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    auctiondict = context['auctiondict'];
	    allauctiontypes = context['allauctiontypes'];
	    auctionhousesdict = context['auctionhousesdict'];
	    gform += "<div class='card-title'><h4>Auction Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Auction Name' name='auctionname' value='" + auctiondict['auctionname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction House</h4></div><div class='form-group'>";
	    gform += "<select name='selauctionhousename' id='selauctionhousename' class='form-control input-default'><option value=''>Select Auction House </option>";
	    for (const [auchousename, auchouseid] of Object.entries(auctionhousesdict)){
		if(auctiondict['auctionhouse'] == auchousename){
		gform += "<option value='" + auchouseid + "' selected>" + auchousename + "</option>";
		}
		else{
		gform += "<option value='" + auchouseid + "'>" + auchousename + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Auction Location</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Auction Location' name='auctionlocation' value='" + auctiondict['auctionlocation'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='auctioninfo'>" + auctiondict['description'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Auction URL</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Auction URL' name='auction_url' value='" + auctiondict['auctionurl'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction Type</h4></div><div class='form-group'>";
	    gform += "<select name='selauctiontype' id ='selauctiontype' class='form-control input-default'><option value=''>Select type </option>";
	    for(var i=0; i < allauctiontypes.length; i++){
		if(allauctiontypes[i] == auctiondict['auctiontype']){
		gform += "<option value='" + allauctiontypes[i] + "' selected>" + allauctiontypes[i] + "</option>";
		}
		else{
		gform += "<option value='" + allauctiontypes[i] + "'>" + allauctiontypes[i] + "</option>";
		}
	    }
	    gform += "<option value='none'>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Enter Auction Type' name='auctiontype'></div>";
	    gform += "<div class='card-title'><h4>Auction Priority</h4></div><div class='form-group'>";
	    gform += "<select name='selauctionpriority' id='selauctionpriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(auctiondict['selpriority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Auction Date</h4></div><div class='form-group'><input type='date' name='auctiondate' class='form-control input-default' value='" + auctiondict['auctiondate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction Cover Image</h4></div><div class='form-group'><input type='file' name='auctioncoverimage' id='auctioncoverimage' class='form-control input-default'><a href='" + auctiondict['coverimage'] + "'><img src='" + auctiondict['coverimage'] + "'></a></div>";
	    gform += "<div class='card-title'><input type='button' name='editauction' class='form-control input-default' value='Save Auction' onclick='javascript:saveauction();'></div>";
	    gform += "<div class='card-title' id='aucstatus'></div>";
	    gform += "<input type='hidden' name='aucid' value='" + auctiondict['id'] + "'>";
	    aucform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editauctions/?aucid=" + aucid);
	  xmlhttp.send();
}

function t_saveauction(aucid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  auctionnm = document.frmedit.auctionname.value;
	  auctionloc = document.frmedit.auctionlocation.value;
	  auchouseid = document.frmedit.selauctionhousename.options[document.frmedit.selauctionhousename.options.selectedIndex].value;
	  auctiondesc = document.frmedit.auctioninfo.value;
	  auctionseltype = document.frmedit.selauctiontype.options[document.frmedit.selauctiontype.options.selectedIndex].value;
	  auctionpr = document.frmedit.selauctionpriority.options[document.frmedit.selauctionpriority.options.selectedIndex].value;
	  auctionurl = document.frmedit.auction_url.value;
	  aucdate = document.frmedit.auctiondate.value;
	  auctionid = document.frmedit.aucid.value;
	  let formData = new FormData();
	  let coverimage = document.getElementById("auctioncoverimage").files[0];
	  formData.append("auctioncoverimage", coverimage); 
	  if (auctionseltype == ""){
	    auctionseltype = document.frmedit.auctiontype.value;
	  }
	  if (auchouseid == ""){
	    alert("Please select Auction House to proceed");
	    exit();
	  }
	  formData.append("auctionname", auctionnm); 
	  formData.append("auctionlocation", auctionloc); 
	  formData.append("auctioninfo", auctiondesc); 
	  formData.append("selauctionhousename", auchouseid); 
 	  formData.append("selauctiontype", auctionseltype); 
	  formData.append("auctiondate", aucdate); 
	  formData.append("selauctionpriority", auctionpr); 
	  formData.append("auction_url", auctionurl);
	  formData.append("aucid", auctionid); 
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('aucstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/saveauctions/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editlot(lid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    lotform = document.getElementById('frmedit');
	    lotform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    auctionsdict = context['auctionsdict'];
	    lot = context['lot'];
	    auctionhouses = context['auctionhousesdict'];
    	    alllotcategories = context['alllotcategories'];
	    allcurrencies = context['allcurrencies'];
	    gform += "<div class='card-title'><h4>Lot Title</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Lot Title' name='lottitle' value='" + lot['lottitle'] + "'></div>";
	    gform += "<div class='card-title'><h4>Auction House Name</h4></div><div class='form-group'>";
	    gform += "<select name='selauctionhousename' id ='selauctionhousename' class='form-control input-default' onchange='javascript:populateauctions();'><option value=''>Select Auction House </option>";
	    for (const [ahname, ahid] of Object.entries(auctionhouses)){
		if(lot['auctionhouse'] == ahid){
		gform += "<option value='" + ahid + "' selected>" + ahname + "</option>";
		}
		else{
		gform += "<option value='" + ahid + "'>" + ahname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Auction</h4></div><div class='form-group'>";
	    gform += "<select name='selauctionname' id ='selauctionname' class='form-control input-default'><option value=''>Select Auction </option>";
	    for (const [aucname, aucid] of Object.entries(auctionsdict)){
		if(lot['auction'] == aucid){
		gform += "<option value='" + aucid + "' selected>" + aucname + "</option>";
		}
		else{
		gform += "<option value='" + aucid + "'>" + aucname + "</option>";
		}
	    }
	    gform += "</select></div>";
	    gform += "<div class='card-title'><h4>Artist Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Name' name='artistname' value='" + lot['artistname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Birth Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Birth Year' name='artistbirth' value='" + lot['artistbirth'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Death Year</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Death Year' name='artistdeath' value='" + lot['artistdeath'] + "'></div>";
	    gform += "<div class='card-title'><h4>Artist Nationality</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Artist Nationality' name='artistnationality' value='" + lot['artistnationality'] + "'></div>";
	    gform += "<div class='card-title'><h4>Medium</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Medium' name='medium' value='" + lot['medium'] + "'></div>";
	    gform += "<div class='card-title'><h4>Size</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Size' name='size' value='" + lot['size'] + "'></div>";
	    gform += "<div class='card-title'><h4>Lot Category </h4></div><div class='form-group'><select name='sellotcategory' id='sellotcategory' class='form-control input-default'><option value=''>Select Category </option>";
	    for(var i=0; i < alllotcategories.length; i++){
		if(lot['lotcategory'] == alllotcategories[i]){
		    gform += "<option value='" + alllotcategories[i] + "' selected>" + alllotcategories[i] + "</option>";
		}
		else{
		    gform += "<option value='" + alllotcategories[i] + "'>" + alllotcategories[i] + "</option>";
		}
	    }
	    gform += "<option value=''>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Lot Category' name='lotcategory'></div>";
	    gform += "<div class='card-title'><h4>Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='lotdescription'>" + lot['description'] + "</textarea></div>";
	    //gform += "<div class='card-title'><h4>Signature</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Signature' name='signature' value='" + lot['signature'] + "'></div>";
	    //gform += "<div class='card-title'><h4>Letter of Authenticity</h4></div><div class='form-group'><textarea class='form-control input-default ' name='authenticity'>" + lot['letterofauthenticity'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Currency </h4></div><div class='form-group'><select name='sellotcurrency' id='sellotcurrency' class='form-control input-default'><option value=''>Select Currency </option>";
	    for(var i=0; i < allcurrencies.length; i++){
		if(lot['currency'] == allcurrencies[i]){
		    gform += "<option value='" + allcurrencies[i] + "' selected>" + allcurrencies[i] + "</option>";
		}
		else{
		    gform += "<option value='" + allcurrencies[i] + "'>" + allcurrencies[i] + "</option>";
		}
	    }
	    gform += "<option value=''>None of the above</option></select><input type='text' class='form-control input-default' placeholder='Lot Currency' name='lotcurrency'></div>";
	    gform += "<div class='card-title'><h4>Estimate</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Estimate' name='estimate' value='" + lot['estimate'] + "'></div>";
	    gform += "<div class='card-title'><h4>Sold Price</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Sold Price' name='soldprice' value='" + lot['soldprice'] + "'></div>";
	    gform += "<div class='card-title'><h4>Provenance</h4></div><div class='form-group'><textarea class='form-control input-default ' name='provenance'>" + lot['provenance'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Literature</h4></div><div class='form-group'><textarea class='form-control input-default ' name='literature'>" + lot['literature'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Exhibitions</h4></div><div class='form-group'><textarea class='form-control input-default ' name='exhibitions'>" + lot['exhibited'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Lot URL</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Lot URL' name='loturl' value='" + lot['loturl'] + "'></div>";
	    gform += "<div class='card-title'><h4>Lot Image 1</h4></div><div class='form-group'><input type='file' name='lotimage1' id='lotimage1' class='form-control input-default'><a href='" + lot['lotimage1'] + "'><img src='" + lot['lotimage1'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Lot Image 2</h4></div><div class='form-group'><input type='file' name='lotimage2' id='lotimage2' class='form-control input-default'><a href='" + lot['lotimage2'] + "'><img src='" + lot['lotimage2'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Lot Image 3</h4></div><div class='form-group'><input type='file' name='lotimage3' id='lotimage3' class='form-control input-default'><a href='" + lot['lotimage3'] + "'><img src='" + lot['lotimage3'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Lot Image 4</h4></div><div class='form-group'><input type='file' name='lotimage4' id='lotimage4' class='form-control input-default'><a href='" + lot['lotimage4'] + "'><img src='" + lot['lotimage4'] + "'></a></div>";
	    gform += "<div class='card-title'><h4>Lot Priority</h4></div><div class='form-group'>";
	    gform += "<select name='sellotpriority' id='sellotpriority' class='form-control input-default'><option value=''>Select Priority </option>";
	    for(i=1; i <= 5; i++){
		if(lot['priority'] == i){
		gform += "<option value='" + i + "' selected>" + i + " </option>";
		}
		else{
		gform += "<option value='" + i + "'>" + i + " </option>";
		}
	    }
	    gform += "</select></div>";

	    gform += "<div class='card-title'><input type='button' name='editlot' class='form-control input-default' value='Save Lot' onclick='javascript:savelot();'></div>";
	    gform += "<div class='card-title' id='lotstatus'></div>";
	    gform += "<input type='hidden' name='lid' value='" + lot['id'] + "'>";
	    lotform.innerHTML = gform;
            adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editlots/?lid=" + lid);
	  xmlhttp.send();
}

function t_savelot(lid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  lotnm = document.frmedit.lottitle.value;
	  artistnm = document.frmedit.artistname.value;
	  auchouseid = document.frmedit.selauctionhousename.options[document.frmedit.selauctionhousename.options.selectedIndex].value;
	  auctionid = document.frmedit.selauctionname.options[document.frmedit.selauctionname.options.selectedIndex].value;
	  abirth = document.frmedit.artistbirth.value;
	  adeath = document.frmedit.artistdeath.value;
	  anationality = document.frmedit.artistnationality.value;
	  medium = document.frmedit.medium.value;
	  sz = document.frmedit.size.value;
	  lotdesc = document.frmedit.lotdescription.value;
	  //lotsig = document.frmedit.signature.value;
	  //lotauth = document.frmedit.authenticity.value;
	  lotestimate = document.frmedit.estimate.value;
	  lotsoldprice = document.frmedit.soldprice.value;
	  lotprovenance = document.frmedit.provenance.value;
	  lotliterature = document.frmedit.literature.value;
	  lotexhibitions = document.frmedit.exhibitions.value;
          lotcat = document.frmedit.sellotcategory.options[document.frmedit.sellotcategory.options.selectedIndex].value;
          if(lotcat == ""){
            lotcat = document.frmedit.lotcategory.value;
          }
          currency = document.frmedit.sellotcurrency.options[document.frmedit.sellotcurrency.options.selectedIndex].value;
          if(currency == ""){
            currency = document.frmedit.lotcurrency.value;
          }
	  loturl = document.frmedit.loturl.value;
          lotid = document.frmedit.lid.value
	  lotpriority = document.frmedit.sellotpriority.options[document.frmedit.sellotpriority.options.selectedIndex].value;
	  let formData = new FormData();
	  if(document.getElementById("lotimage1").files.length > 0){
	  let lotimage1 = document.getElementById("lotimage1").files[0];
	  formData.append("lotimage1", lotimage1);
	  }
	  if(document.getElementById("lotimage2").files.length > 0){
	  let lotimage2 = document.getElementById("lotimage2").files[0];
	  formData.append("lotimage2", lotimage2); 
	  }
	  if(document.getElementById("lotimage3").files.length > 0){
	  let lotimage3 = document.getElementById("lotimage3").files[0];
	  formData.append("lotimage3", lotimage3); 
	  }
	  if(document.getElementById("lotimage4").files.length > 0){
	  let lotimage4 = document.getElementById("lotimage4").files[0];
	  formData.append("lotimage4", lotimage4); 
	  }
	  formData.append("lottitle", lotnm); 
	  formData.append("artistname", artistnm); 
	  formData.append("selauctionhousename", auchouseid); 
 	  formData.append("selauctionname", auctionid); 
	  formData.append("artistbirth", abirth); 
	  formData.append("artistdeath", adeath); 
	  formData.append("artistnationality", anationality);
	  formData.append("medium", medium); 
	  formData.append("size", sz); 
	  formData.append("lotdescription", lotdesc); 
	  //formData.append("signature", lotsig); 
	  //formData.append("authenticity", lotauth); 
	  formData.append("estimate", lotestimate); 
	  formData.append("soldprice", lotsoldprice); 
	  formData.append("provenance", lotprovenance); 
	  formData.append("literature", lotliterature); 
	  formData.append("exhibitions", lotexhibitions); 
	  formData.append("loturl", loturl); 
	  formData.append("sellotcategory", lotcat); 
	  formData.append("sellotcurrency", currency); 
	  formData.append("sellotpriority", lotpriority); 
	  formData.append("lid", lotid); 
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('lotstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savelots/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


function t_editwebconfig(wcid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
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
	    wcform = document.getElementById('frmedit');
	    wcform.innerHTML = "";
	    gform = "<input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>";
	    context = JSON.parse(xmlhttp.responseText);
	    console.log(JSON.stringify(context));
	    wcdict = context['webconfig'];
	    gform += "<div class='card-title'><h4>Config Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Config Name' name='webconfigname' value='" + wcdict['webconfigname'] + "'></div>";
	    gform += "<div class='card-title'><h4>Config Value</h4></div><div class='form-group'><textarea class='form-control input-default ' name='webconfigvalue'>" + wcdict['webconfigvalue'] + "</textarea></div>";
	    gform += "<div class='card-title'><h4>Page Path (Web)</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Page Path' name='webconfigpath' value='" + wcdict['webconfigpath'] + "'></div>";
	    gform += "<div class='card-title'><h4>Page Name</h4></div><div class='form-group'><input type='text' class='form-control input-default ' placeholder='Page Name' name='webconfigpagename' value='" + wcdict['webconfigpagename'] + "'></div>";
	    gform += "<div class='card-title'><h4>Config Description</h4></div><div class='form-group'><textarea class='form-control input-default ' name='webconfigdescription'>" + wcdict['webconfigdescription'] + "</textarea></div>";
	    
	    gform += "<div class='card-title'><input type='button' name='addnewwebconfig' class='form-control input-default' value='Save Config Param' onclick='javascript:savewebconfig();'></div>";
	    gform += "<div class='card-title' id='wcstatus'></div>";
	    gform += "<input type='hidden' name='wcid' value='" + wcdict['id'] + "'>";
	    wcform.innerHTML = gform;
	    adminscr = document.getElementById('adminScreen');
	    adminscr.class = "basic-form";
	    adminscr.innerHTML = "<a href='#' class='cancel'>×</a><form name='frmedit' id='frmedit'><input type='hidden' name='csrfmiddlewaretoken' value='" + csrf + "'>" + gform + "</form>";
	  }
	  };
	  xmlhttp.open("GET", "/admin/editwebconfig/?wcid=" + wcid);
	  xmlhttp.send();
}

function t_savewebconfig(wcid){
	csrf = document.frmedit.csrfmiddlewaretoken.value;
	  webconfignm = document.frmedit.webconfigname.value;
	  webconfigval = document.frmedit.webconfigvalue.value;
	  webconfigpth = document.frmedit.webconfigpath.value;
	  webconfigpgname = document.frmedit.webconfigpagename.value;
	  webconfigdesc = document.frmedit.webconfigdescription.value;
	  webconfigid = document.frmedit.wcid.value;
	  let formData = new FormData();
	  //alert(formData);
	  formData.append("webconfigname", webconfignm); 
	  formData.append("webconfigvalue", webconfigval); 
	  formData.append("webconfigpath", webconfigpth); 
 	  formData.append("webconfigpagename", webconfigpgname); 
	  formData.append("webconfigdescription", webconfigdesc); 
	  formData.append("wcid", webconfigid);
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
	    //alert(xmlhttp.responseText);
	    statusdiv = document.getElementById('wcstatus');
	    statusdiv.innerHTML = "<p style='color:0000AA'>" + xmlhttp.responseText + "</p>";
	    setTimeout(function() {
    		document.location.href = document.location.href;
	    }, 5000);
	  }
	  };
	  xmlhttp.open("POST", '/admin/savewebconfig/');
	  xmlhttp.setRequestHeader("X-CSRFToken", csrf);
	  xmlhttp.send(formData);
}


