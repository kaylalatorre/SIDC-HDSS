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
 * Function for preparing reports in pdf. 
 * @param htmlID the string ID name of an HTML tag 
 */
function printReport(htmlID){
    // get only Report portion of HTML page
    var printCont = document.getElementById(htmlID).innerHTML;
    var orig = document.body.innerHTML; // revert to whole HTML page

    document.body.innerHTML = printCont;
    window.print();
    document.body.innerHTML = orig;
}

/** 
 * on-change AJAX for Biochecklist search dropdown
 */
$('.checklist-date').change(function() {

// function searchBiocheck(){
    disableCheck();

    // Get biosec ID of selected option tag
    var biosecID = $(this).val();

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/biosecurity/getchecklist/' + biosecID,
        success: function (response){

            // alert("in AJAX success");
            var biofields = JSON.parse(response["instance"]);

            // check if Checklist can still be editable
            if (biofields["isEditable"] === false){
                $('#edit-grp-desktop').hide();
                $('#edit-grp-mobile').hide();
            }
            else {
                $('#edit-grp-desktop').show();
                $('#edit-grp-mobile').show();                
            }

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
// }
});

/** 
 * on-change AJAX for Farm search dropdown
 */
$('#farm-code').change(function() { 

    farmID = $("#farm-code option:selected").val();
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
 * Helper function for setting dropdown acc. to selected option
 */
 function setSelectedValue(selectObj, valueToSet) {
    for (var i = 0; i < selectObj.options.length; i++) {
        if (selectObj.options[i].text == valueToSet) {
            selectObj.options[i].selected = true;
            console.log("option [" + selectObj.options[i].text + "] is selected.");
            return;
        }
    }
}

/**
 * function filtering Farm Assessment report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
function filterFarmRep(){

    var sDate = $("#farm-start-date").val();
    var eDate = $("#farm-end-date").val();
    var arName = $("#farm-area option:selected").val();

    // alert("in filterFarmRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);


    try{

        url = "/farms-assessment/" + sDate + "/" + eDate + "/" + arName;
        console.log(url);

        // for loading report table data
        $('#rep-farmAssess').load(url + ' #rep-farmAssess', function (response) {
            $(this).children().unwrap();

            // includes the alert div tag            
            var alertHTML = $(response).find('.alert.farmass-report');
            // console.log(alertHTML);
            $('#farmrep-container').prepend(alertHTML);
            
        });

        // for loading report subheader
        $('.farmrep-subheading').load(url + ' .farmrep-subheading', function () {
            $(this).children().unwrap();
            
        });
        

    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}


/**
 * function for filtering Internal Biosec report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
 function filterIntBioRep(){

    var sDate = $("#intbio-start-date").val();
    var eDate = $("#intbio-end-date").val();
    var arName = $("#intbio-area option:selected").val();

    // alert("in filterIntBioRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);

    try{
        url = "/int-biosecurity/" + sDate + "/" + eDate + "/" + arName;
        console.log(url);

        // for loading report table data
        $('#rep-intbiosec').load(url + ' #rep-intbiosec', function (response) {
            $(this).children().unwrap();

            // includes the alert div tag            
            var alertHTML = $(response).find('.alert.intbio-report');
            // console.log(alertHTML);
            $('#intbioRep-container').prepend(alertHTML);
            
        });

        // for loading report subheader
        $('.intbioRep-subheading').load(url + ' .intbioRep-subheading', function () {
            $(this).children().unwrap();
            
        });
        
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}


/**
 * function for filtering External Biosec report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
 function filterExtBioRep(){

    var sDate = $("#extbio-start-date").val();
    var eDate = $("#extbio-end-date").val();
    var arName = $("#extbio-area option:selected").val();

    // alert("in filterExtBioRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);

    try{
        url = "/ext-biosecurity/" + sDate + "/" + eDate + "/" + arName;
        console.log(url);

        // for loading report table data
        $('#rep-extbiosec').load(url + ' #rep-extbiosec', function (response) {
            $(this).children().unwrap();

            // includes the alert div tag            
            var alertHTML = $(response).find('.alert.extbio-report');
            // console.log(alertHTML);
            $('#extbioRep-container').prepend(alertHTML);
            
        });

        // for loading report subheader
        $('.extbioRep-subheading').load(url + ' .extbioRep-subheading', function () {
            $(this).children().unwrap();
            
        });
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}


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
function saveBiocheck(elem){

    // Get biosec ID of selected option tag
    var biosecID = $(elem).parent().siblings(".input-group").children(".checklist-date").val();
    // alert("in saveBiocheck() biosecID: " + biosecID);

    // Put biosec fields in an array
    var checkArr = [];

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
        url: '/biosecurity/edit-checklist/' + biosecID,
        data: {"checkArr": checkArr}, 
        success: function (response) {
            
            if (response.status_code == '200'){
                alert("Biosec checklist successfully updated!");
            }

            if (response.status == 400){
                alert("ERROR [" + res.status + "]: " +  res.responseJSON.error);
            }

            var biofields = JSON.parse(response["instance"]);

            // Always updates btn groups depending on AJAX response (1) update fields or (2) not-updated fields from db
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
            
            // Get farmID for biosec URL redirect
            var farmID = $("#farm-code option:selected").val();
            // alert("in saveBiocheck() -- farmID: " +  farmID);

            // reload Biosec page to update dropdown of Biosec last_updated
            // window.location.reload(true);
            // window.location.replace("/biosecurity");
            // window.location.replace("/biosecurity/" + farmID);

            try{
                url = "/biosecurity/" + farmID;
                console.log(url);
                location.href = url;
            } catch (error){
                console.log("Fetching biosec details failed.");
                location.reload(true);
            }


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

function deleteBiocheck(elem){

    // Get biosec ID of selected option tag
    var biosecID = $(elem).parent().siblings(".input-group").children(".checklist-date").val();
    // alert("in deleteBiocheck() -- biosecID: " + biosecID);

    var farmID = $("#farm-code option:selected").val();
    // alert("in deleteBiocheck() -- farmID: " + farmID);

    if (confirm("Delete this checklist?")) {
        ajaxCSRF();

        $.ajax({
            type: 'POST',
            url: '/biosecurity/delete-checklist/' + biosecID + '/' + farmID,
            // data: {"checkArr": checkArr}, 
            success: function (response){

                // console.log(response);
                // if (response.status == 200){
                //     alert("Biochecklist record deleted.");
                // }
                // // reload Biosec page to update dropdown of Biosec last_updated
                // // window.location.reload(true);
                window.location.replace("/biosecurity/" + farmID);
                alert(response.success);
                
            },
            error: function (res){
                alert("ERROR [" + res.status + "]: " +  res.responseJSON.error);
            }
        });
    }

}

/**
*   - Redirects current user (technician) to the selected farm. 
*   - Appends selected farm ID to url that will display farm details.
*   
*   techFarm = row of selected farm
*/
function viewTechFarm(techFarm) {

    try{
        url = "/tech-selected-farm/" + techFarm.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
        console.log(url);
        location.href = url;
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}

/**
*   - Redirects current technician from selected farm page to designated biosecurity page.
*   - Appends selected farm ID to url that will display biosecurity measure, checklists, and activities.
*   
*   farmID = button value (carries ID of selected farm)
*/
function viewBiosec(farmID) {

    var techFarm = $(farmID).val(); 
    console.log(techFarm)

    try{
        url = "/biosecurity/" + techFarm;
        console.log(url);
        location.href = url;
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}

/**
*   - Redirects current technician from biosecurity page to add-checklist page for selected farm.
*   - Appends selected farm ID to url that will display an empty biosecurity checklist.
*   
*   farmID = button value (carries ID of selected farm)
*/
function addBiosecPage(farmID) {

    var techFarm = $(farmID).val(); 
    console.log(techFarm)

    try{
        url = "/add-checklist/" + techFarm;
        console.log(url);
        location.href = url;
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}

/**
*   - Redirects current technician from biosecurity page to add-activity page for selected farm.
*   - Appends selected farm ID to url that will display an empty activity record.
*   
*   farmID = button value (carries ID of selected farm)
*/
function addActivityPage(farmID) {

    var techFarm = $(farmID).val(); 
    console.log(techFarm)

    try{
        url = "/add-activity/" + techFarm;
        console.log(url);
        location.href = url;
    } catch (error){
        console.log("Fetching farm details failed.");
        location.reload(true);
    }
}

/** 
* Used to assign technicians to area.
*/
$('.assignSave').on('click', function () {
    var area = $(this).parent().parent().siblings(":eq(0)").text();
    var technician = $(this).parent().parent().siblings(":eq(2)").children().children().val();
    ajaxCSRF();
    if(technician){
        $.ajax({
            type:'POST',
            url:'technician-assignment/assign',
            data:{
                "area":area,
                "technician":technician
            },
            success: function(response){
                console.log(response);
                location.reload(true);
            },
            error: function(response){
                console.log(response);
                location.reload(true);
            }
        });
    }
});