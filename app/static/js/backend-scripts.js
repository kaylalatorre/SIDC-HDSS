
// TODO: add onchange() for select tag
// https://stackoverflow.com/questions/11179406/jquery-get-value-of-select-onchange --> get latest AJAX-jquery script
// https://www.pluralsight.com/guides/work-with-ajax-django --> refer to POST request

$('#checklist-date').on('change', function() {
    
    $.ajax({
        type: 'POST',
        url: "{% url 'search_biochecklist' %}", // pass biosec id here?= (?)
        data: resBiocheck, // change to name of data returned from view function
        success: function (response){

            // select btn in btn group based on db value
            if (resBiocheck.prvdd_foot_dip == 0)
                $('#prvdd_foot_dip_radio1').prop("checked", true)

        },
        error: function (response){
            alert("ERROR: Biochecklist not found.");
        }
    })


    $.ajax({
        type: 'POST',
        url: "{% url 'post_friend' %}",
        data: serializedData,
        success: function (response) {
            // on successfull creating object
            // 1. clear the form.
            $("#friend-form").trigger('reset');
            // 2. focus to nickname input 
            $("#id_nick_name").focus();

            // display the newly friend to table.
            var instance = JSON.parse(response["instance"]);
            var fields = instance[0]["fields"];
            $("#my_friends tbody").prepend(
                `<tr>
                <td>${fields["nick_name"]||""}</td>
                <td>${fields["first_name"]||""}</td>
                <td>${fields["last_name"]||""}</td>
                <td>${fields["likes"]||""}</td>
                <td>${fields["dob"]||""}</td>
                <td>${fields["lives_in"]||""}</td>
                </tr>`
            )
        },
        error: function (response) {
            // alert the error if any error occured
            alert(response["responseJSON"]["error"]);
        }
    })



});