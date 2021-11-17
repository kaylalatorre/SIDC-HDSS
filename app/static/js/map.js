$(document).ready(function() {
    console.log( "ready!" );
    $("#map-container").highcharts({
        chart: {
            map: 'countries/ph/ph-all'
        },
        title: {
            text: "test"
        },
    }) 
});