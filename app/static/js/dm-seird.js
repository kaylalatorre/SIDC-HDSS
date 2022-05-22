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
                    text: 'Days'
                },
            },
            yAxis: {
                title: {
                    text: 'Pig Count'
                },
            },
            tooltip: {
                shared: true,
                valueSuffix: ' pigs',
            },
            series: [{
                name: 'Total',
                data: metadata[0],
                dashStyle: 'Dash',
                zIndex: 0,
                color: '#404242'
            }, {
                name: 'Susceptible',
                data: metadata[1],
                color: '#b4e024'
            }, {
                name: 'Exposed',
                data: metadata[2],
                color: '#f0ab16'
            }, {
                name: 'Infected',
                data: metadata[3],
                color: '#ed501c'
            }, {
                name: 'Recovered',
                data: metadata[4],
                color: '#08cc39'
            }, {
                name: 'Dead',
                data: metadata[5],
                color: '#17a4fc'
            }]
        })
    }
}