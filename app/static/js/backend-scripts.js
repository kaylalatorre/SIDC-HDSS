/* BACKEND-specific Functions */

/** 
 * on-change AJAX for Biochecklist search
 */
$('#checklist-date').change(function() {
    
    disableCheck();

    // Get biosec ID of selected option tag
    var biosecID = $("#checklist-date option:selected").val()
    // alert("biosecID: " + biosecID);

    $.ajax({
        type: 'POST',
        // url: "{% url 'search_biochecklist' %}", 
        url: '/biosecurity/getchecklist',
        data: {"biosecID": biosecID}, // pass biosec id here
        success: function (response){

            // alert("in AJAX success");
            var biofields = JSON.parse(response["instance"]);

            console.log(response["instance"]);

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

            // alert("biofields[disinfect_prem] -- " + biofields["disinfect_prem"]);
            // alert("biofields[disinfect_vet_supp] -- " + biofields["disinfect_vet_supp"]);

            if (biofields["disinfect_vet_supp"] == 0)
                $('#disinfect_vet_supp_radio1').prop("checked", true);
            else if (biofields["disinfect_vet_supp"] == 1)
                $('#disinfect_vet_supp_radio2').prop("checked", true);
            else
                $('#disinfect_vet_supp_radio3').prop("checked", true);

        },
        error: function (response){
            alert("in AJAX error. ");
            // alert(response);
        }
    });

});


/**
 * on-click for edit Biochecklist btn; 
 * Gets relevant values for biosec tables (i.e., biosecID, biosec fields) then passes to saveBiocheck()
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
    alert("biosecID: " + biosecID);

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
        
    alert("checkArr length: " + checkArr.length);
    // for (i = 0; i < checkArr.length; i++)
    //     alert("checkArr ["+ i + "]:" + checkArr[i]);

// $('#saveCheck-btn').on("click", function(){
    $.ajax({
        type: 'POST',
        url: '/biosecurity/edit-checklist',
        data: {"biosecID": bioID, "checkArr": chArr}, // pass biosec id here
        success: function (response){

            alert("in AJAX edit success");
            var bioInstance = JSON.parse(response["instance"]);
            var biofields = bioInstance[0]["fields"];

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
        },
        error: function (response){
            alert("in AJAX error. ");
            // alert(response);
        }
    });
    
    disableCheck();

    // });
}