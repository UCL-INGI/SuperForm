$("#inlineFormCustomSelectModule").on("change",function(){
    var e = document.getElementById("inlineFormCustomSelectModule");
    var module = e.options[e.selectedIndex].value;

    if(module != undefined){
        add_auth_inputs_for_channel(module);
    }
});

function add_auth_inputs_for_channel(module){
    var input_username = document.getElementById("inlineFormInputTextUserName");
    var input_password = document.getElementById("inlineFormInputTextPassword");

    if(auth_fields[module] != undefined){
        if(auth_fields[module] == true) {

            input_username.hidden = false;
            input_password.hidden = false;
        }else{
            input_username.value='';
            input_username.hidden = true;
            input_password.value='';
            input_password.hidden = true;
        }
    }else{
        input_username.value='';
        input_username.hidden = true;
        input_password.value='';
        input_password.hidden = true;
    }
}
