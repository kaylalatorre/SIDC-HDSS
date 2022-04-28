// DISEASE MONITORING
$(document).ready(async function () {
    // onclick disease -- render specific disease
    async function diseaseChart(strdisease) {

        ajaxCSRF();
        console.log('here');
        console.log('disease: ' + strdisease);
        metadata = await $.ajax({
            type: 'POST',
            url: '/disease-charts/' + strdisease + '/',
            success: function(response){
                return response;
            }
        });
        
        console.log(metadata);

        var today = new Date();
        // console.log(today);
        
        var dateBefore = Date.UTC(today.getFullYear(), today.getMonth()-1, today.getDate());
        // console.log(dateBefore);
    
        var dateToday = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
        // console.log(dateToday);

        // CASES per disease line chart
        if($('#dm-confirmed-per').length) {

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

            Highcharts.chart('dm-confirmed-per', {
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

        // SERID for ASF
        if($('#dm-seird-asf').length) {
            Highcharts.chart('dm-seird-asf', {
                chart: {
                    type: 'spline'
                },
                title: {
                    text: 'Title'
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
                        text: ''
                    },
                },
                tooltip: {
                    shared: true,
                    valueSuffix: ' units'
                },
                series: [{
                    name: 'Susceptible',
                    data: [3, 4, 3, 5, 4, 10, 12]
                }, {
                    name: 'Exposed',
                    data: [0, 0, 0, 0, 3, 5, 4]
                }, {
                    name: 'Infected',
                    data: [1, 2, 2, 1, 3, 5, 4]
                }, {
                    name: 'Recovered',
                    data: [5, 4, 10, 9, 2, 1, 1]
                }, {
                    name: 'Dead',
                    data: [2, 2, 3, 4, 4, 0, 4]
                }]
            })
        }
        
    };

    // const tab = $('#diseasemonitor');
    // console.log("tab");
    // console.log(tab.hasClass('show'));
    // console.log(tab.hasClass('active'));

    // if(tab.hasClass('show') && (tab.hasClass('active'))){
    //     console.log("!!!!!!!!!!!!!!!!!!!!!");
    //     diseaseChart('ASF');
    // }
})
