$("input[type='checkbox']").each(function(){

    let mod = $(this).attr("module-namechan").split('.')[2];
    if(mod != undefined){
        if(post_form_validations[mod]['image_type'] != undefined && post_form_validations[mod]['image_type'].toLocaleLowerCase() =="url"){
             $(this).on("click",adapt_post_to_channel($(this).attr('data-namechan')+"_imagepost"));
        }
    }
});

$("#publish-button").click(function(event){
    var toReturn = true;
     $("input[type='checkbox']:checked").each(function(){
         let mod = $(this).attr("module-namechan").split('.')[2];
         let title_max_length=100000;
         let descr_max_length=100000;
         if(mod != undefined){
             console.log(post_form_validations[mod]);
             if(post_form_validations[mod]['title_max_length'] != undefined){
                 title_max_length = post_form_validations[mod]['title_max_length'] ;
             }
             if(post_form_validations[mod]['description_max_length'] != undefined){
                 descr_max_length = post_form_validations[mod]['description_max_length'] ;
             }
         }

        if((!prevalidate_post($(this).attr("data-namechan"),title_max_length,descr_max_length))){
            document.getElementById("li_"+$(this).attr("data-namechan")).children[0].style.color = "red";
            toReturn = false;
            return toReturn;
        }

      });
     return toReturn;
});

function prevalidate_post (chan_name,title_length,descr_length){
    return prevalidate_post_or_publishing (chan_name+"_titlepost",chan_name+"_descriptionpost",
    chan_name+"_linkurlpost",chan_name+"_imagepost",
    chan_name+"_datefrompost",chan_name+"_dateuntilpost",title_length,descr_length);
}

