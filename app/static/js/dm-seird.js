/*
    something
*/
function getSEIRDInput(input){
    // console.log(input.value);

    var values = [];
    $(input).parent().parent().children().each(function(){
        let curr = $(this).children("output[name='SEIRDOutput']");
        values.push(curr.val());
    });
    console.log(values);

    load_SEIRD(values);

}


$(document).ready(function () {
    // onclick disease -- render specific disease
    // async function diseaseChart(strdisease) {
    // load_SEIRD()

        
});

async function load_SEIRD(values){
    

    ajaxCSRF();

    let metadata = await $.ajax({
        type: 'POST',
        url: '/disease-seird/ASF/',
        data: {'values': values},
        success: function(res){
            console.log(res);
            return res;
        }
    });
    console.log(metadata);


    // SERID
    if($('#dm-seird').length) {
        console.log("loading sierd chart")

        Highcharts.chart('dm-seird', {
            chart: {
                type: 'spline'
            },
            title: {
                text: 'SEIRD Data Chart'
            },
            legend: {
                layout: 'horizontal',
                align: 'center',
                verticalAlign: 'bottom',
                floating: false,
            },
            xAxis: {
                title: {
                    text: ''
                },
            },
            yAxis: {
                title: {
                    text: 'Pig Count'
                },
            },
            tooltip: {
                shared: true,
                valueSuffix: ' units'
            },
            series: [{
                name: 'Total',
                data: metadata[0],
                dashStyle: 'Dash',
                zIndex: 0
            }, {
                name: 'Susceptible',
                data: metadata[1]
            }, {
                name: 'Exposed',
                data: metadata[2]
            }, {
                name: 'Infected',
                data: metadata[3]
            }, {
                name: 'Recovered',
                data: metadata[4]
            }, {
                name: 'Dead',
                data: metadata[5]
            }]
        })
    }
}