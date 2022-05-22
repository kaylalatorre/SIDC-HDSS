/*
    Collect SEIRD input from slide rangers
*/
function getSEIRDInput(input) {
    // console.log(input.value);

    var values = [];
    var dname = $(input).attr("dname");
    $(input).parent().parent().children().each(function () {
        let curr = $(this).children("output[name='SEIRDOutput']");
        values.push(curr.val());
    });
    console.log(values);
    console.log(dname);

    load_SEIRD(values, dname);

}


$(document).ready(function () {
    // onclick disease -- render specific disease
    // async function diseaseChart(strdisease) {
    var incub_days = $('#outputIncubDays').val();
    var repro_no = $('#outputReproNo').val();
    var disease_spread = $('#outputDiseaseSpread').val();
    var fatality = $('#outputFatality').val();
    var death_days = $('#outputDeathDays').val();

    values = [incub_days, repro_no, disease_spread, fatality, death_days];

    console.log(values);
    load_SEIRD(values, "ASF");


});

async function load_SEIRD(values, strDisease) {


    console.log(strDisease);
    ajaxCSRF();
    
    let metadata = await $.ajax({
        type: 'POST',
        url: '/disease-seird/' + strDisease + '/',
        data: {
            'values': values
        },
        success: function (res) {
            console.log(res);
            return res;
        }
    });
    console.log(metadata);


    // SERID
    if ($(`#dm-seird-${strDisease}`).length) {
        console.log("loading sierd chart")

        Highcharts.chart(`dm-seird-${strDisease}`, {
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