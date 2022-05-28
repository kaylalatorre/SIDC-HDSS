/**
 * Declare globale variables for the charts
 */
var disChart, seirdChart;

/**
 * A global getSVG method that takes an array of charts as an
 * argument
 */
Highcharts.getSVG = function(charts) {
    var svgArr = [],
        top = 0,
        width = 0,
        endWidth = 0;
  
    Highcharts.each(charts, function(chart) {
        var svg = chart.getSVG(),
            // Get width/height of SVG for export
            svgWidth = +svg.match(
            /^<svg[^>]*width\s*=\s*\"?(\d+)\"?[^>]*>/
            )[1],
            svgHeight = +svg.match(
            /^<svg[^>]*height\s*=\s*\"?(\d+)\"?[^>]*>/
            )[1];
    
        svg = svg.replace(
            '<svg',
            '<g transform="translate(' + width + ', ' + top + ')" '
        );
  
        svg = svg.replace('</svg>', '</g>');
  
        width += svgWidth;
        endWidth = Math.max(endWidth, width)
    
        if (width === 2 * svgWidth) {
            width = 0;
            top += svgHeight;
        }
    
        svgArr.push(svg);
    });

    top += 200;
    return '<svg height="' + top + '" width="' + endWidth +
      '" version="1.1" xmlns="http://www.w3.org/2000/svg">' +
      svgArr.join('') + '</svg>';
};


/**
 * A global exportCharts method that takes an array of charts as an
 * argument, and exporting options as the second argument
 */
Highcharts.exportCharts = function(charts, options) {
    // Merge the options
    options = Highcharts.merge(Highcharts.getOptions().exporting, options);

    // Post to export server
    Highcharts.post(options.url, {
        filename: options.filename || 'disease-monitoring-charts',
        type: options.type,
        width: options.width,
        svg: Highcharts.getSVG(charts)
    });
}

/**
 * -----------------------------------
 * Disease Count Chart 
 * Async Function
 * OnClick - Render specific disease
 * -----------------------------------
 */
async function diseaseChart(strdisease) {

    ajaxCSRF();
    // console.log('here');
    // console.log('disease: ' + strdisease);
    metadata = await $.ajax({
        type: 'POST',
        url: '/disease-chart/' + strdisease + '/',
        success: function(response){
            return response;
        }
    });
    
    console.log(metadata);

    var today = new Date();
    var dateBefore = Date.UTC(today.getFullYear(), today.getMonth()-1, today.getDate());
    var dateToday = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());

    // CASES per disease line chart
    if($(`#dm-confirmed-per-${strdisease}`).length) {

        var disSeries = [];

        disSeries.push({
            name: 'Confirmed',
            data: metadata[0]['confirmed'].map(function(elem){
                try {
                    var dStr = elem[0].split('-');
                } catch{
                    return metadata[0]['confirmed'];
                }

                return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
            }),
            color: '#ed501c'
        });

        disSeries.push({
            name: 'Recovered',
            data: metadata[0]['recovered'].map(function(elem){
                try {
                    var dStr = elem[0].split('-');
                } catch{
                    return metadata[0]['recovered'];
                }

                return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
            }),
            color: '#08cc39'
        });

        disSeries.push({
            name: 'Died',
            data: metadata[0]['died'].map(function(elem){
                try {
                    var dStr = elem[0].split('-');
                } catch{
                    return metadata[0]['died'];
                }

                return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
            }),
            color: '#17a4fc'
        });

        // Create Disease Count Chart
        disChart = Highcharts.chart(`dm-confirmed-per-${strdisease}`, {
            chart: {
                type: 'line',
                events: {
                    load: function() {
                        this.update({
                        credits: {
                            text: 'Generated on: ' + Highcharts.dateFormat('%m/%d/%Y %H:%M:%S', Date.now())
                        }
                        });
                    }
                }
            },
            title: {
                text: strdisease + ' No. of Cases'
            },
            xAxis: {
                type: 'datetime',
                startOnTick: true,
                endOnTick: true,
                min: dateBefore,
                max: dateToday,
                dateTimeLabelFormats: {
                    week: '%e of %b' },
                units: [
                    [ 'week', [1] ],
                    [ 'month', [1] ]
                ]
            },
            yAxis: {
                title: {
                    text: 'No. of Pigs'
                },
            },
            
        
            series: disSeries,
        })
    }
    
};


/**
 * -----------------------------------
 * SEIRD Chart Functions
 * getSEIRDInput, load_SEIRD
 * -----------------------------------
 */

// Collect SEIRD input from slide rangers
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
        // Create SEIRD chart
        seirdChart = Highcharts.chart(`dm-seird-${strDisease}`, {
            chart: {
                type: 'spline',
                events: {
                    load: function() {
                        this.update({
                        credits: {
                            text: 'Generated on: ' + Highcharts.dateFormat('%m/%d/%Y %H:%M:%S', Date.now())
                        }
                        });
                    }
                }
            },
            title: {
                text: strDisease + ' SEIRD Data Chart'
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

/**
 * Print Function
 * - calls exportCharts to merge the charts into one file
 */
$('#print-dm').click(function() {
    Highcharts.exportCharts([disChart, seirdChart], {
      type: 'application/pdf'
    });
});