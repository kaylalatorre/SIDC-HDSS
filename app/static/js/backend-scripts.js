
// TODO: add onchange() for select tag
// https://stackoverflow.com/questions/11179406/jquery-get-value-of-select-onchange --> get latest AJAX-jquery script
// https://www.pluralsight.com/guides/work-with-ajax-django --> refer to POST request

$('#checklist-date').change(function() {
    
    // Get biosec ID of selected option tag
    var biosecID = $("#checklist-date option:selected").val()
    alert("biosecID: " + biosecID);

    

    $.ajax({
        type: 'POST',
        // url: "{% url 'search_biochecklist' %}", 
        url: '/biosecurity/getchecklist',
        data: {"biosecID": biosecID}, // pass biosec id here
        success: function (response){

            alert("in AJAX success");
            var bioInstance = JSON.parse(response["instance"]);
            var biofields = bioInstance[0]["fields"];

            alert("biofields[prvdd_alco_soap]: " + biofields["prvdd_alco_soap"]);

            // select btn in btn group based on db value
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

        },
        error: function (response){
            alert("in AJAX error. ");
            // alert(response);
        }
    })

});

// function searchChecklist(){
    
//     // Get biosec ID of selected option tag
//     var biosecID = $("#checklist-date").filter(":selected").val();
//     alert("biosecID: " + biosecID);

//     $.ajax({
//         type: 'POST',
//         url: "{% url 'search_biochecklist' %}", 
//         data: biosecID, // pass biosec id here
//         success: function (response){

//             var biocheck = JSON.parse(response["instance"]);

//             // select btn in btn group based on db value
//             if (biocheck.prvdd_foot_dip == 0)
//                 $('#prvdd_foot_dip_radio1').prop("checked", true);

//         },
//         error: function (response){
//             alert("ERROR: Biochecklist not found.");
//         }
//     })


//     $.ajax({
//         type: 'POST',
//         url: "{% url 'post_friend' %}",
//         data: serializedData,
//         success: function (response) {
//             // on successfull creating object
//             // 1. clear the form.
//             $("#friend-form").trigger('reset');
//             // 2. focus to nickname input 
//             $("#id_nick_name").focus();

//             // display the newly friend to table.
//             var instance = JSON.parse(response["instance"]);
//             var fields = instance[0]["fields"];
//             $("#my_friends tbody").prepend(
//                 `<tr>
//                 <td>${fields["nick_name"]||""}</td>
//                 <td>${fields["first_name"]||""}</td>
//                 <td>${fields["last_name"]||""}</td>
//                 <td>${fields["likes"]||""}</td>
//                 <td>${fields["dob"]||""}</td>
//                 <td>${fields["lives_in"]||""}</td>
//                 </tr>`
//             )
//         },
//         error: function (response) {
//             // alert the error if any error occured
//             alert(response["responseJSON"]["error"]);
//         }
//     })

// }
