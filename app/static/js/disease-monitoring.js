// onclick disease -- render specific disease
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
            })
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
            })
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
            })
        });

        // console.log(disSeries);

        Highcharts.chart(`dm-confirmed-per-${strdisease}`, {
            chart: {
                type: 'line'
            },
            title: {
                text: 'No. of Cases'
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