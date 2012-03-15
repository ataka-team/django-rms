var new_rule_cursor = 0;
var new_rule_key_cursor = 0;
var new_category_cursor = 0;


function active_input(event) {
    $(event.target).addClass("active");   
}

function deactive_input(event) {
    $(event.target).removeClass("active");
}

function disable_enter_key(event) {      
    if ( event.which == 13 ) {
        event.preventDefault();
    }
}

function check_ruledata(event) {
    try
    {
        res = $(event.target).val();
        res = JSON.parse(res);
        $(event.target).val(JSON.stringify(res, null, "  "));
        
        if ($(event.target).hasClass('rule-ruledata-incorrect')){
            $(event.target).removeClass("rule-ruledata-incorrect");
        }
        $(event.target).addClass("rule-ruledata-correct");
    }
    catch(err)
    {
        if ($(event.target).hasClass('rule-ruledata-correct')){
            $(event.target).removeClass("rule-ruledata-correct");
        }
        $(event.target).addClass("rule-ruledata-incorrect");
    }

}

function update_locale() {
    var locale = $("#select-locales").val();
    $(".message").hide();
    $("." + locale).show();
}

function toggle_expandable (event) {
    tmp = $(event.target).attr("id").split("-");
    $('#expandable-' + tmp[1]+ '-' + tmp[2]).toggle();
}

function expand() {
    $('.expandable').show();
}

function collapse() {
    $('.expandable').hide();
}

function show_localefile_input() {
    $('#input-localefile').toggle();
}

function get_locales(app_id) {
    var locales_items = [];
    $.getJSON('/locales/' + app_id, function(data) {
        var selected = false;
        $.each(data, function(key, locale) {
            if ( locale == "default" ) {
                selected = true;
                locales_items.push('<option class="select-locales-option" selected="selected" value="' + 
                locale + '">' + 
                locale + '</option>');
            }
            else {
                if ( selected ) {
                  locales_items.push('<option class="select-locales-option" value="' + 
                    locale + '">' + 
                    locale + '</option>');
                }
                else {
                selected = true;
                locales_items.push('<option class="select-locales-option" selected="selected" value="' + 
                  locale + '">' + 
                  locale + '</option>');
                }
            }
        });
        $('').replaceAll('.select-locales-option');
        $(locales_items.join("")).appendTo('#select-locales');

        update_locale();

    });
}

function change_deleted_visibility() {
    var action = $("#select-show-deleted-rules").val();
    $.each($(".weight"), function(key, weight) {
        w = $(weight).val();

        if (w == 0) {
          
            id = $(weight).attr("id");
            tmp = id.split("-");

            if (action == "hide" ){
                $("#rule-" + tmp[1]).hide();
            }
            else {
                $("#rule-" + tmp[1]).show();              
            }
        }
    });          
}

function add_rule(event){

    var tmp = $(event.target).attr("id").split("-");
    var key_rk = tmp[2];
    var key_r = "new" + new_rule_cursor;
    var locale = $("#select-locales").val();

    new_item =  '<li class="row1 tr message new ' + locale +'" id="rule-' + key_r + '">' +
                ' <div class="td noexpand" id="expand-ruledata-' + key_r +'"> ' + 
                '   <div style="display:none"> ' + 
                '     <input type="hidden" value="' + key_rk + '" name="rule-' + key_r + '-rulekey"> ' +
                '   </div>' +
                '   <div style="display:none"> ' + 
                '     <input type="hidden" value="' + locale + '" name="rule-' + key_r + '-locale"> ' +
                '   </div>' +                    
                ' </div>' + 
                ' <div class="td">' +
                '   <input name="rule-' + key_r + '-message" value="' + '' + '" ' +
                '          class="vTextField" maxlength="100" id="rule-' + key_r + '-message" type="text">' +
                ' </div>' + 
                ' <div class="td">' +
                '   <input name="rule-' + key_r + '-slug" value="'+ 'auto-generated' + '" ' +
                '          class="vTextField slug" maxlength="50" id="rule-' + key_r + '-catid" type="text"' +
                '          readonly="readonly">' +
                ' </div>' + 
                ' <div class="td">' +
                '   <input name="rule-' + key_r + '-weight" value="' + '1' + '" ' +
                '          class="vTextField weight" maxlength="50" id="rule-' + key_r + '-weight" type="text">' +
                ' </div>' +                   
                ' <div class="td align-right">' + 
                '   <input name="rule-' + key_r + '-DELETE" id="rule-' + key_r + '-DELETE" type="checkbox">' + 
                ' </div>' + 
                ' <div class="ruledata noexpandable" id="expandable-ruledata-' + key_r + '" >' +
                ' <label class="required" for="id_description">Rule data:</label> ' + 
                '   <textarea class="vLargeTextField rule-ruledata"' +
                '             name="rule-' + key_r + '-rule" cols="180" rows="5"' + 
                '             id="rule-' + key_r + '-rule">' +
                '' +
                '   </textarea>' +
                '</li>'

    $(new_item).appendTo($('#ul-rules-' + key_rk)); 

    $(".vTextField").keypress(disable_enter_key); 

    $(".vTextField").focus(active_input);
    $(".vTextField").blur(deactive_input);
    $(".vLargeTextField").focus(active_input);
    $(".vLargeTextField").blur(deactive_input);

    $(".rule-ruledata").change(check_ruledata);
    
    $.each($(".rule-ruledata"), function(k, v) {
        val = $(v).val();
        try {
            val = JSON.stringify(JSON.parse(val), null, "  ");
        }
        catch (err){
            console.log(val);
        }
        $(v).val(val); 
    });


    new_rule_cursor = new_rule_cursor + 1;

}

function add_rule_key(event){
    
    var tmp = $(event.target).attr("id").split("-");
    var key_cat = tmp[2];
    var key_rk = "new" + new_rule_key_cursor;
    new_item = '<li class="row2 tr new" id="rulekey-' + key_rk + '">' +
      ' <div class="td align-left">' + 
      '   <div style="display:none"> ' + 
      '     <input type="hidden" value="' + key_cat + '" name="rulekey-' + key_rk + '-category"> ' +
      '   </div>' +
      ' </div>' + 
      ' <div class="td">' +
      '   <input name="rulekey-' + key_rk + '-keyname" value="' + '' + '" ' +
      '          class="vTextField" maxlength="100" id="rulekey-' + key_rk + '-keyname" type="text">' +
      ' </div>' + 
      ' <div class="td align-right action-checkbox">' + 
      '   <input type="checkbox" name="selected" value="rulekey-' + key_rk + '" class="action-select">' +
      ' </div>' +                                                  
      '</li>'; 

    $(new_item).appendTo($('#ul-rulekeys-' + key_cat)); 
    
    $(".vTextField").keypress(disable_enter_key); 

    $(".vTextField").focus(active_input);
    $(".vTextField").focusout(deactive_input);
    
    new_rule_key_cursor = new_rule_key_cursor + 1;

}

function add_category(event){
    
    var tmp = $(event.target).attr("id").split("-");
    var key_app = tmp[2];
    var key_cat = "new" + new_category_cursor;
    
    new_item = '<li class="row1 tr new" id="category-' + key_cat + '">' +
      ' <div class="td expand align-left" id="expand-rulekeys-' + key_cat +'">' +
      '   <div style="display:none"> ' + 
      '     <input type="hidden" value="' + key_app + '" name="category-' + key_cat + '-application"> ' +
      '   </div>' +      
      ' </div>' + 
      ' <div class="td">' +
      '   <input name="category-' + key_cat + '-catname" value="' + '' + '" ' +
      '          class="vTextField" maxlength="100" id="id_category-' + key_cat + '-catname" type="text">' +
      ' </div>' + 
      ' <div class="td">' +
      '   <input name="category-' + key_cat + '-catid" value="' + '' + '" ' +
      '          class="vTextField" maxlength="50" id="category-' + key_cat + '-catid" type="text">' +
      ' </div>' + 
      ' <div class="td align-right action-checkbox">' + 
      '   <input type="checkbox" name="selected" value="category-' + key_cat + '" class="action-select">' +
      ' </div>' +                        
      ' <div class="rulekeys expandable" id="expandable-rulekeys-' + key_cat + '" >' +
      '   <div class="th align-left"> </div> ' + 
      '   <div class="th"> Key name</div> ' +
      '   <div class="th align-right"> Select </div> <ul class="tr" id="ul-rulekeys-' + key_cat + '">' +
      '  </ul>' + 
      '  <div class="">' +
      '     <a class="add-rulekeys" id="add-rulekeys-' + key_cat + '" href="#" >' + "Add new rule key"  + '</a>' +
      '  </div>' +                                         
      ' </div>' +
      '</li>';
    
    $(new_item).appendTo($('#ul-categories-' + key_app)); 
    
    $('#expand-rulekeys-' + key_cat).click(toggle_expandable);
    $('#add-rulekeys-' + key_cat).click(add_rule_key);
    
    $(".vTextField").keypress(disable_enter_key); 

    $(".vTextField").focus(active_input);
    $(".vTextField").focusout(deactive_input);
    
    new_category_cursor = new_category_cursor + 1;

}


