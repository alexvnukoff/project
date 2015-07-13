// Switch TEXT

                       $(document).ready(function() {
						   var path = (window.location.host).split('.');
						   console.log(path)
                          path = path[0];
						  $("#lang_select").find('option').each(function( i, opt ) {
							  console.log(opt.value)
							  if( opt.value === path )
							  $(opt).attr('selected', 'selected');
						  });
						  $("#lang_select" ).change(function(e) {
							  if(!$(this).val())
							  return;
							 // path = (src).split('.');
							  var languages = ["am","ar","en","he","ru","zh"];
							  if ($.inArray(path[0], languages) > -1) {
								  path[0] = $(this).val();
							  }
							  
						  });	
					  });
					  
					  $( "#lang_select" ).change(function(e) {
						  console.log("change");
						  console.log(this.value);
						  
						  if (this.value == "ar" || this.value == "he") {
								   console.log("ok")
								   $('head').append('<link id="txtalign" href="css/text-align.css" type="text/css" rel="stylesheet" />');
							   }
							   else {
								   $('#txtalign').remove();
							   }
						  
						  
						  if (!$( this ).val())
						  return;
						  path = (window.location.host).split('.');
						  if (path[0] == 'www'){
							  delete path[0]
						  }
						  var languages = ["am", "ar", "en", "he", "ru", "zh"];	
						  if($.inArray(path[0], languages)>-1){
							  path[0] = $(this).val();
						  }
						 
						  window.location.href = window.location.protocol + "//" + path.join('.');
					 });