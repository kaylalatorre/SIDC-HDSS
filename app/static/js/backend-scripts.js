/* BACKEND-specific Functions */

/**
 * Helper function to prepare AJAX functions with CSRF middleware tokens.
 * This avoids getting 403 (Forbidden) errors.
 */
function ajaxCSRF(){
    $.ajaxSetup({ 
        beforeSend: function(xhr, settings) {
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
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        } 
   });
}

/** 
 * on-change AJAX for Biochecklist search
 */
$('#checklist-date').change(function() {
    
    disableCheck();

    // Get biosec ID of selected option tag
    var biosecID = $("#checklist-date option:selected").val()
    // alert("in search_checklist() -- biosecID: " + biosecID);

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        // url: '/biosecurity/getchecklist',
        url: '/biosecurity/getchecklist/' + biosecID,
        // data: {"biosecID": biosecID}, // pass biosec id here
        success: function (response){

            // alert("in AJAX success");
            var biofields = JSON.parse(response["instance"]);

            // select btn in btn group based on db value
            // EXTERNAL biosec fields
            if (biofields["prvdd_foot_dip"] == 0)
                $('#prvdd_foot_dip_radio1').prop("checked", true);
            else if (biofields["prvdd_foot_dip"] == 1)
                $('#prvdd_foot_dip_radio2').prop("checked", true);
            else
                $('#prvdd_foot_dip_radio3').prop("checked", true);

            if (biofields["prvdd_alco_soap"] == 0)
                $('#prvdd_alco_soap_radio1').prop("checked", true);
            else if (biofields["prvdd_alco_soap"] == 1)
                $('#prvdd_alco_soap_radio2').prop("checked", true);
            else
                $('#prvdd_alco_soap_radio3').prop("checked", true);

            if (biofields["obs_no_visitors"] == 0)
                $('#obs_no_visitors_radio1').prop("checked", true);
            else if (biofields["obs_no_visitors"] == 1)
                $('#obs_no_visitors_radio2').prop("checked", true);
            else
                $('#obs_no_visitors_radio3').prop("checked", true);
            
            if (biofields["prsnl_dip_footwear"] == 0)
                $('#prsnl_dip_footwear_radio1').prop("checked", true);
            else if (biofields["prsnl_dip_footwear"] == 1)
                $('#prsnl_dip_footwear_radio2').prop("checked", true);
            else
                $('#prsnl_dip_footwear_radio3').prop("checked", true);

            if (biofields["prsnl_sanit_hands"] == 0)
                $('#prsnl_sanit_hands_radio1').prop("checked", true);
            else if (biofields["prsnl_sanit_hands"] == 1)
                $('#prsnl_sanit_hands_radio2').prop("checked", true);
            else
                $('#prsnl_sanit_hands_radio3').prop("checked", true);

            if (biofields["chg_disinfect_daily"] == 0)
                $('#cng_disinfect_daily_radio1').prop("checked", true);
            else if (biofields["chg_disinfect_daily"] == 1)
                $('#cng_disinfect_daily_radio2').prop("checked", true);
            else
                $('#cng_disinfect_daily_radio3').prop("checked", true);

            // INTERNAL biosec fields
            if (biofields["disinfect_prem"] == 0)
                $('#disinfect_prem_radio1').prop("checked", true);
            else if (biofields["disinfect_prem"] == 1)
                $('#disinfect_prem_radio2').prop("checked", true);
            else
                $('#disinfect_prem_radio3').prop("checked", true);

            if (biofields["disinfect_vet_supp"] == 0)
                $('#disinfect_vet_supp_radio1').prop("checked", true);
            else if (biofields["disinfect_vet_supp"] == 1)
                $('#disinfect_vet_supp_radio2').prop("checked", true);
            else
                $('#disinfect_vet_supp_radio3').prop("checked", true);

        },
        error: function (res){
            alert("ERROR [" + res.status + "]: " +  res.responseJSON.error);
        }
    });

});

$('#farm-code').change(function() { 

    farmID = $("#farm-code option:selected").val()
    try{
        url = "/biosecurity/" + farmID;
        console.log(url);
        location.href = url;
    } catch (error){
        console.log("Fetching biosec details failed.");
        location.reload(true);
    }

});

/**
 * functions for enabling/disabling Biochecklist btns; 
 */
function enableBiocheck(){
    // remove disabled attribute from biosec grp btns 
    var bioBtns = document.getElementsByClassName('btn-check');
    for(var i = 0; i < bioBtns.length; i++) {
        bioBtns[i].disabled = false;
    }    
}

function disableCheck(){
    // disable biosec grp btns 
    var bioBtns = document.getElementsByClassName('btn-check');
    for(var i = 0; i < bioBtns.length; i++) {
        bioBtns[i].disabled = true;
    }    
}

/**
 * on-click AJAX for save Biochecklist btn
 */
function saveBiocheck(){
    // Get biosec ID of selected option tag
    var biosecID = $("#checklist-date option:selected").val()
    // alert("biosecID: " + biosecID);

    // Put biosec fields in an array
    var checkArr = []

    // EXTERNAL biosec fields
    if ($('#prvdd_foot_dip_radio1').prop('checked') == true)
        checkArr[0] = 0;
    else if ($('#prvdd_foot_dip_radio2').prop('checked') == true) 
        checkArr[0] = 1;
    else
        checkArr[0] = 2;  
        
    if ($('#prvdd_alco_soap_radio1').prop('checked') == true)
        checkArr[1] = 0;
    else if ($('#prvdd_alco_soap_radio2').prop('checked') == true) 
        checkArr[1] = 1;
    else
        checkArr[1] = 2;        

    if ($('#obs_no_visitors_radio1').prop('checked') == true)
        checkArr[2] = 0;
    else if ($('#obs_no_visitors_radio2').prop('checked') == true) 
        checkArr[2] = 1;
    else
        checkArr[2] = 2;  
        
    if ($('#prsnl_dip_footwear_radio1').prop('checked') == true)
        checkArr[3] = 0;
    else if ($('#prsnl_dip_footwear_radio2').prop('checked') == true) 
        checkArr[3] = 1;
    else
        checkArr[3] = 2;  

    if ($('#prsnl_sanit_hands_radio1').prop('checked') == true)
        checkArr[4] = 0;
    else if ($('#prsnl_sanit_hands_radio2').prop('checked') == true) 
        checkArr[4] = 1;
    else
        checkArr[4] = 2;  

    if ($('#cng_disinfect_daily_radio1').prop('checked') == true)
        checkArr[5] = 0;
    else if ($('#cng_disinfect_daily_radio2').prop('checked') == true) 
        checkArr[5] = 1;
    else
        checkArr[5] = 2;  

    // INTERNAL biosec fields
    if ($('#disinfect_prem_radio1').prop('checked') == true)
        checkArr[6] = 0;
    else if ($('#disinfect_prem_radio2').prop('checked') == true) 
        checkArr[6] = 1;
    else
        checkArr[6] = 2;  

    if ($('#disinfect_vet_supp_radio1').prop('checked') == true)
        checkArr[7] = 0;
    else if ($('#disinfect_vet_supp_radio2').prop('checked') == true) 
        checkArr[7] = 1;
    else
        checkArr[7] = 2;
        
    // alert("checkArr length: " + checkArr.length);

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        // url: '/biosecurity/edit-checklist', // TODO: convert to '/biosecurity/edit-checklist/' + biosecID
        // data: {"biosecID": biosecID, "checkArr": checkArr}, 
        url: '/biosecurity/edit-checklist/' + biosecID,
        data: {"checkArr": checkArr}, 
        success: function (response){

            if (response.status == 200){
                // alert("in AJAX edit success");
                var biofields = JSON.parse(response["instance"]);

                // select btn in btn group based on db value
                // EXTERNAL biosec fields
                if (biofields["prvdd_foot_dip"] == 0)
                    $('#prvdd_foot_dip_radio1').prop("checked", true);
                else if (biofields["prvdd_foot_dip"] == 1)
                    $('#prvdd_foot_dip_radio2').prop("checked", true);
                else
                    $('#prvdd_foot_dip_radio3').prop("checked", true);

                if (biofields["prvdd_alco_soap"] == 0)
                    $('#prvdd_alco_soap_radio1').prop("checked", true);
                else if (biofields["prvdd_alco_soap"] == 1)
                    $('#prvdd_alco_soap_radio2').prop("checked", true);
                else
                    $('#prvdd_alco_soap_radio3').prop("checked", true);

                if (biofields["obs_no_visitors"] == 0)
                    $('#obs_no_visitors_radio1').prop("checked", true);
                else if (biofields["obs_no_visitors"] == 1)
                    $('#obs_no_visitors_radio2').prop("checked", true);
                else
                    $('#obs_no_visitors_radio3').prop("checked", true);
                
                if (biofields["prsnl_dip_footwear"] == 0)
                    $('#prsnl_dip_footwear_radio1').prop("checked", true);
                else if (biofields["prsnl_dip_footwear"] == 1)
                    $('#prsnl_dip_footwear_radio2').prop("checked", true);
                else
                    $('#prsnl_dip_footwear_radio3').prop("checked", true);

                if (biofields["prsnl_sanit_hands"] == 0)
                    $('#prsnl_sanit_hands_radio1').prop("checked", true);
                else if (biofields["prsnl_sanit_hands"] == 1)
                    $('#prsnl_sanit_hands_radio2').prop("checked", true);
                else
                    $('#prsnl_sanit_hands_radio3').prop("checked", true);

                if (biofields["chg_disinfect_daily"] == 0)
                    $('#cng_disinfect_daily_radio1').prop("checked", true);
                else if (biofields["chg_disinfect_daily"] == 1)
                    $('#cng_disinfect_daily_radio2').prop("checked", true);
                else
                    $('#cng_disinfect_daily_radio3').prop("checked", true);

                // INTERNAL biosec fields
                if (biofields["disinfect_prem"] == 0)
                    $('#disinfect_prem_radio1').prop("checked", true);
                else if (biofields["chg_disinfect_daily"] == 1)
                    $('#disinfect_prem_radio2').prop("checked", true);
                else
                    $('#disinfect_prem_radio3').prop("checked", true);

                if (biofields["disinfect_vet_supp"] == 0)
                    $('#disinfect_vet_supp_radio1').prop("checked", true);
                else if (biofields["chg_disinfect_daily"] == 1)
                    $('#disinfect_vet_supp_radio2').prop("checked", true);
                else
                    $('#disinfect_vet_supp_radio3').prop("checked", true);
            }
            // reload Biosec page to update dropdown of Biosec last_updated
            // window.location.reload(true);
            window.location.replace("/biosecurity");

        },
        error: function (res){
            // alert("in AJAX error. ");
            // alert(res.status); // the status code
            // alert(res.responseJSON.error); // the message

            alert("ERROR [" + res.status + "]: " +  res.responseJSON.error);
        }
    });
    
    disableCheck();
}

// VIEW SELECTED TECH FARM
function viewTechFarm(techFarm) {
    // var techFarm = document.getElementById("viewTechFarm");

    try{
        url = "/tech-selected-farm/" + techFarm.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
        console.log(url);
        location.href = url;
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}