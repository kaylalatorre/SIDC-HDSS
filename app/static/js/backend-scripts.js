/**
 * Helper function to format date objects 
 * for frontend display.
 * @param {date} date 
 * @returns a formatted date YYYY-MM-DD
 */
function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

/**
 * Helper function to prepare AJAX functions with CSRF middleware tokens.
 * This avoids getting 403 (Forbidden) errors.
 */
function ajaxCSRF() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
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
function printReport(htmlID) {
    // get only Report portion of HTML page
    var printCont = document.getElementById(htmlID).innerHTML;
    var orig = document.body.innerHTML; // revert to whole HTML page

    document.body.innerHTML = printCont;
    window.print();
    document.body.innerHTML = orig;
}

//---- MODULE 1 functions ----//

/** 
 * on-change AJAX for Biochecklist search dropdown
 */
$('.checklist-date').change(function () {

    // function searchBiocheck(){
    disableCheck();

    // Get biosec ID of selected option tag
    var biosecID = $(this).val();

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/biosecurity/getchecklist/' + biosecID,
        success: function (response) {

            // alert("in AJAX success");
            var biofields = JSON.parse(response["instance"]);

            // check if Checklist can still be editable
            if (biofields["isEditable"] === false) {
                $('#edit-grp-desktop').hide();
                $('#edit-grp-mobile').hide();
            } else {
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
        error: function (res) {
            console.log(res.responseJSON.error);
            // alert("ERROR [" + res.status + "]: " + res.responseJSON.error);
        }
    });
});

/** 
 * on-change AJAX for Farm search dropdown
 */
$('#farm-code').change(function () {
    console.log("Farm Code: " + this.value);
    if (this.value > 0) {
        $('#biosec-details').show();
        $('#biosec-checklists').show();
        $('farm-activities').show();

        farmID = $("#farm-code option:selected").val();
        try {
            url = "/biosecurity/" + farmID;
            // console.log(url);
            location.href = url;
        } catch (error) {
            console.log(error);
        }
    }
});


/**
 * function filtering Farm Assessment report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
function filterFarmRep() {

    var sDate = $("#farm-start-date").val();
    var eDate = $("#farm-end-date").val();
    var arName = $("#farm-area option:selected").val();

    // alert("in filterFarmRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);


    try {

        url = "/farms-assessment/" + sDate + "/" + eDate + "/" + arName;
        // console.log(url);

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


    } catch (error) {
        console.log(error);
    }
}


/**
 * function for filtering Internal Biosec report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
function filterIntBioRep() {

    var sDate = $("#intbio-start-date").val();
    var eDate = $("#intbio-end-date").val();
    var arName = $("#intbio-area option:selected").val();

    // alert("in filterIntBioRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);

    try {
        url = "/int-biosecurity/" + sDate + "/" + eDate + "/" + arName;
        // console.log(url);

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

    } catch (error) {
        console.log(error);
    }
}


/**
 * function for filtering External Biosec report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
function filterExtBioRep() {

    var sDate = $("#extbio-start-date").val();
    var eDate = $("#extbio-end-date").val();
    var arName = $("#extbio-area option:selected").val();

    // alert("in filterExtBioRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);

    try {
        url = "/ext-biosecurity/" + sDate + "/" + eDate + "/" + arName;
        // console.log(url);

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
    } catch (error) {
        console.log(error);
    }
}


/**
 * functions for enabling/disabling Biochecklist btns; 
 */
function enableBiocheck() {
    // remove disabled attribute from biosec grp btns 
    var bioBtns = document.getElementsByClassName('btn-check');
    for (var i = 0; i < bioBtns.length; i++) {
        bioBtns[i].disabled = false;
    }
}

function disableCheck() {
    // disable biosec grp btns 
    var bioBtns = document.getElementsByClassName('btn-check');
    for (var i = 0; i < bioBtns.length; i++) {
        bioBtns[i].disabled = true;
    }
}

/**
 * on-click AJAX for save Biochecklist btn
 */
function saveBiocheck(elem) {

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

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/biosecurity/edit-checklist/' + biosecID,
        data: {
            "checkArr": checkArr
        },
        success: function (response) {

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

            try {
                url = "/biosecurity/" + farmID;
                location.href = url;
            } catch (error) {
                console.log(error);
            }


        },
        error: function (res) {
            console.log(res.responseJSON.error);
        }
    });

    disableCheck();
}

function deleteBiocheck(elem) {

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
            success: function (response) {

                // console.log(response);
                window.location.replace("/biosecurity/" + farmID);
            },
            error: function (res) {
                console.log(res.responseJSON.error);
            }
        });
    }

}

/** 
 * Used to assign technicians to area.
 */
$('.assignSave').on('click', function () {
    var area = $(this).parent().parent().siblings(":eq(0)").text();
    var technician = $(this).parent().parent().siblings(":eq(2)").children().children().val();
    ajaxCSRF();
    if (technician) {
        $.ajax({
            type: 'POST',
            url: 'technician-assignment/assign',
            data: {
                "area": area,
                "technician": technician
            },
            success: function (response) {
                console.log(response);
            },
            error: function (response) {
                console.log(response);
            },
            complete: function () {
                location.reload(true);
            }
        });
    }
});

/** 
 * Create new area
 */
$('#save-area').on('click', function () {
    area = $(this).siblings('.form-control').val();
    ajaxCSRF();
    if (area) {
        if (area.length <= 15) {
            $.ajax({
                type: 'POST',
                url: 'technician-assignment/savearea',
                data: {
                    "area": area
                },
                success: function (response) {
                    console.log(response);
                },
                error: function (response) {
                    console.log(response);

                },
                complete: function () {
                    location.reload(true);
                }
            });
            return;
        }
        alert("Area name must have 15 or less characters");
        return;
    }
    alert("No area name provided");
});

function for_approval(button, decision) {
    var forApproval_IDs = [];
    button.closest('div.flex').siblings('div.box-style').children('table.table').children('tbody').find(':checkbox:checked').each(function () {
        forApproval_IDs.push(parseInt(this.id));
    });
    if (forApproval_IDs.length === 0) {
        console.log('skip');
        return;
    }

    console.log(forApproval_IDs);
    console.log($('#rejectMessage').val())
    console.log('member-announcements/' + decision);
    ajaxCSRF()
    $.ajax({
        type: 'POST',
        url: '/member-announcements/' + decision,
        dataType: "json",
        data: {
            "idList": JSON.stringify(forApproval_IDs),
            "mssg": $('#rejectMessage').val()
        },
        success: function (response) {
            if (response.status == 200) {
                console.log(response.responseJSON.success);
            }

            window.location.replace("/member-announcements");
        },
        error: function (res) {
            console.log(res.responseJSON.error);
            // alert("Error in submitting the approval.")
        }
    });
}

/** 
 * Create array of announcement to be approved then send to backend through ajax.
 */
$('#approveChecked.primary-btn').on('click', function () {
    for_approval($(this), 'approve');
});
$('#rejectAncmts.primary-btn-red').on('click', function () {
    if ($('#rejectMessage').val()){
        for_approval($('#rejectChecked.primary-btn-red'), 'reject');
        return;
    }
    alert("No reason provided");    
});

/**
 *   - Deletes selected activity row from database
 *   
 *   actID = button value (carries ID of selected activity)
 */
function deleteActivity(actID) {

    var activityID = $(actID).val();
    console.log("Activity ID: " + activityID);

    if (confirm("Delete selected activity?")) {
        ajaxCSRF();

        $.ajax({
            type: 'POST',
            url: '/delete-activity/' + activityID,

            success: function (response) {
                if (response.status == 200) {
                    console.log(response.responseJSON.success)
                }

                location.reload(true);
            },
            error: function (res) {
                console.log(res.responseJSON.error);
            }
        })
    }

}

/**
 *   - Updates selected activity row
 *   - Disable all other edit buttons and delete buttons
 *   - Display data inputs and send to saveActivity() function
 *
 *   actID = button value (carries ID of selected activity)
 */
function editActivity(actID) {

    var row = actID.parentNode.parentNode.parentNode; //get row of clicked button
    var rowIndex = row.rowIndex;
    console.log("Row ID: " + rowIndex);

    var activityID = $(actID).val();
    console.log("Activity ID: " + activityID);

    var toShow = row.getElementsByClassName("activity-input");
    // console.log(toShow.length);

    var toHide = row.getElementsByClassName("activity-data");
    // console.log(toHide.length);
    for (var i = 0; i < toHide.length; i++) {
        // show displayed data of current row
        toHide[i].style.display = "none";

        // hide data inputs
        toShow[i].style.display = "block";
    }

    // enable other edit buttons and delete buttons
    var disableEdit = document.getElementsByName("editActBtn");
    var disableDelete = document.getElementsByName("deleteActBtn");
    for (var i = 0; i < disableEdit.length; i++) {
        disableEdit[i].disabled = true;
        disableDelete[i].disabled = true;
    }

}

/**
 *   - Cancels edit of selected activity
 *
 *   actID = button value (carries ID of selected activity)
 */
function cancelActivity(actID) {

    var row = actID.parentNode.parentNode.parentNode; //get row of clicked button
    var rowIndex = row.rowIndex;
    console.log("Row ID: " + rowIndex);

    var toShow = row.getElementsByClassName("activity-input");
    var toHide = row.getElementsByClassName("activity-data");

    for (var i = 0; i < toHide.length; i++) {
        // hide displayed data of current row
        toHide[i].style.display = "block";

        // display data inputs
        toShow[i].style.display = "none";
    }

    // disable other edit buttons and delete buttons
    var disableEdit = document.getElementsByName("editActBtn");
    var disableDelete = document.getElementsByName("deleteActBtn");
    for (var i = 0; i < disableEdit.length; i++) {
        disableEdit[i].disabled = false;
        disableDelete[i].disabled = false;
    }

}

/**
 *   - Send data to backend function save to database
 *   - Check if date input is not later than today
 *   - Check if arrival time is after departure time
 *
 *   actID = button value (carries ID of selected activity)
 *   farmID = id value of farm activities are connected to   
 */
function saveActivity(actID, farmID) {

    var row = actID.parentNode.parentNode.parentNode; //get row of clicked button
    var rowIndex = row.rowIndex;
    console.log("Row ID: " + rowIndex);

    var activityID = $(actID).val();
    console.log("Activity ID: " + activityID);

    console.log("Farm ID: " + farmID)

    var checkTrue = 2;
    var today = new Date(); // date today
    var date = row.getElementsByClassName("activity-input")[0].value;
    var tripVar = row.getElementsByClassName("activity-input")[1];
    var trip_type = tripVar.options[tripVar.selectedIndex].text;
    var arrival = row.getElementsByClassName("activity-input")[2].value;
    var departure = row.getElementsByClassName("activity-input")[3].value;
    var description = row.getElementsByClassName("activity-input")[4].value;
    var remarks = row.getElementsByClassName("activity-input")[5].value;

    // check if date is not later than today
    if (new Date(date) > today) {
        checkTrue -= 1;
        console.log("Date should not be later than today.");
    }

    // check if arrival is after departure
    if (arrival > departure) {
        checkTrue -= 1;
        console.log("Departure time should be after arrival time.");
    }

    if (checkTrue == 2) {
        ajaxCSRF();

        $.ajax({
            type: 'POST',
            url: '/save-activity/' + farmID + '/' + activityID,
            data: {
                "date": date,
                "trip_type": trip_type,
                "time_arrival": arrival,
                "time_departure": departure,
                "description": description,
                "remarks": remarks
            },

            success: function (response) {
                if (response.status == 200) {
                    console.log(response.responseJSON.success)
                }

                location.reload(true);
            },
            error: function (res) {
                console.log(res.responseJSON.error);
            }
        })
    }
}

/**
 *   - Send data to backend function save to database
 *   - Check if date input is not later than today
 *   - Check if arrival time is after departure time
 *
 *   actFormID = id value of selected activity form
 *   actDate = date_added value of selected activity form   
 */
function resubmitActivity(actDate, actFormID, farmID) {
    // get all data from each column
    var date = document.getElementsByClassName("act-date-input");
    var trip = document.getElementsByClassName("act-trip-type-input");
    var arrival = document.getElementsByClassName("act-arrival-input");
    var departure = document.getElementsByClassName("act-departure-input");
    var description = document.getElementsByClassName("act-description-input");
    var remarks = document.getElementsByClassName("act-remarks-input");

    const convertTime = timeStr => {
        const [time, modifier] = timeStr.split(' ');
        let [hours, minutes] = time.split(':');
        // console.log(hours, minutes, time, modifier)

        if (hours === '12') {
            hours = '00';
        };
        if (modifier === 'p.m.') {
            hours = parseInt(hours, 10) + 12;
        };
        if (minutes === undefined) {
            minutes = '00';
        };
        return `${hours}:${minutes}`;
    };

    var x = 0;
    // pass each row into one object    
    var activityList = [];
    for (var i = 0; i < date.length; i++){
        if (date[i].value !== '') {
            var activity = {
                date: formatDate(date[i].value),
                trip_type: trip[i].value,
                time_arrival: convertTime(arrival[i].value),
                time_departure: convertTime(departure[i].value),
                description: description[i].value,
                remarks: remarks[i].value
            };

            activityList[x] = activity;
            x++;
        };

    }

    console.log(activityList);
    // // check if date is not later than today
    // if (new Date(date) > today){
    //     checkTrue -= 1;
    //     console.log("Date should not be later than today.");
    // }

    // // check if arrival is after departure
    // if (arrival > departure){
    //     checkTrue -= 1;
    //     console.log("Departure time should be after arrival time.");
    // }

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/resubmit-activity-form/' + actFormID + '/' + farmID + '/' + actDate,
        data: {
            "activityList": activityList
        },

        success: function (response) {
            if (response.status == 200) {
                console.log(response.responseJSON.success)
            }

            window.location.replace("/forms-approval");
        },
        error: function (res) {
            console.log(res.responseJSON.error);
        }
    })
}

/**
 *   - Approves all activities under selected activity form
 *   
 *   actFormID = id value of selected activity form
 */
function approveActivity(actFormID) {

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/approve-activity-form/' + actFormID,
        data: {
            "id": actFormID,
            "is_checked": true,
        },

        success: function (response) {
            if (response.status == 200) {
                console.log(response.responseJSON.success)
            }

            window.location.replace("/forms-approval");
        },
        error: function (res) {
            console.log(res.responseJSON.error);
        }
    })
}

/**
 *   - Rejects all activities under selected activity form
 *   
 *   actFormID = id value of selected activity form
 */
function rejectActivity(actFormID) {

    var rejectReason = document.getElementById("reject-reason").value;
    // console.log(rejectReason);

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/reject-activity-form/' + actFormID,
        data: {
            "id": actFormID,
            "is_checked": false,
            "reason": rejectReason },

        success: function (response) {
            if (response.status == 200) {
                console.log(response.responseJSON.success)
            }

            window.location.replace("/forms-approval");
        },
        error: function (res) {
            console.log(res.responseJSON.error);
        }
    })
}

$('.edit_ancmtRow').on("click", function(){
    $(this).prop('hidden', true);
    $('.edit_ancmtRow').prop('disabled', true);
    $(this).parent().parent().siblings("td.ancmt_editSubj").children("p.ancmt_display").prop('hidden', true);
    $(this).parent().parent().siblings("td.ancmt_editSubj").children(".ancmt_edit").prop('hidden', false);
    $(this).siblings("button.ancmt_edit.save_ancmtRow").prop('hidden', false).prop('disabled', false);
    $(this).siblings("button.ancmt_edit.cancel_ancmtRow").prop('hidden', false).prop('disabled', false);
});

$('.cancel_ancmtRow').on("click", function(){
    $(this).prop('hidden', true).prop('disabled', true);
    $(this).siblings("button.ancmt_edit.save_ancmtRow").prop('hidden', true).prop('disabled', true);

    $(this).parent().parent().siblings("td.ancmt_editSubj").children(".ancmt_edit").val($(this).parent().parent().siblings("td.ancmt_editSubj").children("p.ancmt_display").text())
    $(this).parent().parent().siblings("td.ancmt_editSubj").children("p.ancmt_display").prop('hidden', false);
    $(this).parent().parent().siblings("td.ancmt_editSubj").children(".ancmt_edit").prop('hidden', true);
    $(this).siblings("button.ancmt_display.edit_ancmtRow").prop('hidden', false);
    $('.edit_ancmtRow').prop('disabled', false);
});

$('.save_ancmtRow').on("click", function(){
    $(this).prop('hidden', true).prop('disabled', true);
    $(this).siblings("button.ancmt_edit.cancel_ancmtRow").prop('hidden', true).prop('disabled', true);

    $(this).parent().parent().siblings("td.ancmt_editSubj").children("p.ancmt_display").text($(this).parent().parent().siblings("td.ancmt_editSubj").children(".ancmt_edit").val())
    
    $(this).parent().parent().siblings("td.ancmt_editSubj").children("p.ancmt_display").prop('hidden', false);
    $(this).parent().parent().siblings("td.ancmt_editSubj").children(".ancmt_edit").prop('hidden', true);
    $(this).siblings("button.ancmt_display.edit_ancmtRow").prop('hidden', false);
    $('.edit_ancmtRow').prop('disabled', false);
});


//---- MODULE 2 functions ----//

/**
 * Links to detailed view of selected Hogs Health record (for Asst. Manager view)
 * @param farmHTML the HTML tag of farm code column in table data
 */
function viewHogsHealth(farmHTML) {

    var farmID = farmHTML.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
    console.log("farmID -- " + farmID);

    try {
        url = "/selected-hogs-health/" + farmID;
        // console.log(url);
        location.href = url;
    } catch (error) {
        console.log(error);
    }
}

/**
 * Links to detailed view of selected Hogs Health record (for Technician view)
 * @param farmHTML the HTML tag of farm code column in table data
 */
function viewHealthSymptoms(farmHTML) {

    var farmID = farmHTML.parentNode.parentNode.getElementsByTagName("td")[0].innerHTML;
    console.log("farmID -- " + farmID);

    try {
        url = "/selected-health-symptoms/" + farmID;
        location.href = url;
    } catch (error) {
        console.log(error);
    }
}

/**
 * Helper function for setting dropdown acc. to selected option
 * Code modified from: https://usefulangle.com/post/254/javascript-loop-through-select-options
 * @param selectID HTML ID name of the dropdown
 * @param valueToSet string value of option tag to be selected
 */
function setSelectedValue(selectID, valueToSet) {
    Array.from(document.getElementById(selectID).options).forEach(function (option_element) {
        let option_text = option_element.text;
        let option_value = option_element.value;
        let is_option_selected = option_element.selected;

        if (option_value == valueToSet) {
            option_element.selected = true;
            console.log("option selected is -- [" + option_value + "]");
        }
    });
}

/** 
 * on-click POST AJAX for edit status btn for Incident Report
 * @param incidID string ID of Incident record to be edited
 */
$('.symptomsSave').on('click', function () {
    // TODO: get incident ID based on DOM access
    var incidID = $(this).parent().parent().siblings(":eq(0)").text();

    console.log(".symptomsSave [incidID] -- " + incidID);

    // Get selected report_status in dropdown
    var selectedStat = $("#dropdown-repstatus-" + incidID + " option:selected").val();
    var currStat = $("#hidden-status-" + incidID).val();

    if (selectedStat !== currStat) {
        ajaxCSRF();

        $.ajax({
            type: 'POST',
            url: '/update-incident-status/' + incidID,
            data: {
                "selectStat": selectedStat
            },
            success: function (response) {

                if (response.status_code === "200") {
                    // update selected rep_status in dropdown acc. to returned db value
                    var updatedStat = response.updated_status;
                    // alert("updatedStat -- " + updatedStat);

                    setSelectedValue("dropdown-repstatus-" + incidID, updatedStat);

                    // update value of hidden input tag
                    $("#hidden-status-" + incidID).val(updatedStat);

                    console.log("Status for incident ID [" + incidID + "] has been updated.");
                } else {
                    console.log("ERROR [" + response.status_code + "]: " + response.error);
                    location.reload(true);
                }

            },
            error: function (res) {
                console.log("ERROR [" + res.status + "]: " + res.responseJSON.error);
            }
        });
    }
});

/** 
 * on-click POST AJAX function for adding an Incident Case.
 * @param farmID string ID of selected Farm record
*/
function addCase(farmID) {

    // get no. of pigs affected
    var num_pigs = $(".input-numAffected").val();

    // get symptoms list based on HTML class of input checkbox tag; put in Array
    var symptomsArr = [];
    $(".check-symp").each(function() {
        symptomsArr.push($(this).prop('checked'));
    });

    ajaxCSRF();

    $.ajax({
        type: 'POST',
        url: '/post-addCase/' + farmID, 
        data: {"num_pigsAffected": num_pigs, "symptomsArr": symptomsArr}, 
        success: function (response) {
            
            if (response.status_code === "200"){

                // redirect back to selected view page   
                try {
                    url = "/selected-health-symptoms/" + farmID;
                    // console.log(url);
                    location.href = url;
                    
                } catch (error){
                    console.log(error);
                }              
            } 
            else {
                console.log("ERROR [" + response.status_code + "]: " + response.error);
            }

        },
        error: function (res){
            console.log("ERROR [" + res.status_code + "]: " +  res.error);
        }
    });
}


/**
 * function filtering Mortality report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
 function filterMortRep() {

    var sDate = $("#mort-start-date").val();
    var eDate = $("#mort-end-date").val();
    var arName = $("#mort-area option:selected").val();

    // alert("in filterMortRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);


    try {

        url = "/hogs-mortality/" + sDate + "/" + eDate + "/" + arName;
        // console.log(url);

        // for loading report table data
        $('#rep-mort').load(url + ' #rep-mort', function (response) {
            $(this).children().unwrap();

            // includes the alert div tag            
            var alertHTML = $(response).find('.alert.mort-report');
            // console.log(alertHTML);
            $('#mortrep-container').prepend(alertHTML);

        });

        // for loading report subheader
        $('.mortrep-subheading').load(url + ' .mortrep-subheading', function () {
            $(this).children().unwrap();

        });


    } catch (error) {
        console.log(error);
    }
 }

/* function filtering Mortality report based on (1) date range and (2) areaName
 * 
 * Note: also contains an AJAX .load() for updating table contents upon filter.
 */
 function filterDiseaseRep() {

    var sDate = $("#disease-start-date").val();
    var eDate = $("#disease-end-date").val();
    var arName = $("#disease-area option:selected").val();

    // alert("in filterDiseaseRep()");
    console.log("sDate -- " + sDate);
    console.log("eDate -- " + eDate);
    console.log("arName -- " + arName);


    try {

        url = "/disease-monitoring/" + sDate + "/" + eDate + "/" + arName;
        // console.log(url);

        // for loading report table data
        $('#rep-diseaseMonitor').load(url + ' #rep-diseaseMonitor', function (response) {
            $(this).children().unwrap();

            // includes the alert div tag            
            var alertHTML = $(response).find('.alert.disease-report');
            // console.log(alertHTML);
            $('#disMonitor-container').prepend(alertHTML);

        });

        // for loading report subheader
        $('.diseaserep-subheading').load(url + ' .diseaserep-subheading', function () {
            $(this).children().unwrap();

        });

    } catch (error) {
        console.log(error);
    }
 }