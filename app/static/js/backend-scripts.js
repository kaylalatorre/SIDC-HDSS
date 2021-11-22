
// TODO: add onchange() for select tag
// https://stackoverflow.com/questions/11179406/jquery-get-value-of-select-onchange --> get latest AJAX-jquery script
// https://www.pluralsight.com/guides/work-with-ajax-django --> refer to POST request

$('#checklist-date').change(function() {
    
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
            var bioInstance = JSON.parse(response["instance"]);
            var biofields = bioInstance[0]["fields"];

            // alert("biofields[prvdd_alco_soap]: " + biofields["prvdd_alco_soap"]);

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
    })

});

$('.assignSave').on('click', function () {
    var area = $(this).parent().parent().siblings(":eq(0)").text();
    var technician = $(this).parent().parent().siblings(":eq(2)").children().children().val();
    // location.reload(true);
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