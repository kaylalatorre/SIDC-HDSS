// DISEASE MONITORING
$(document).ready(async function () {
    if($('#dm-confirmed-per').length) {

        ajaxCSRF();
        console.log('here');
        metadata = await $.ajax({
            type: 'POST',
            url: '/disease-monitoring/ASF/', // add disease name
            success: function(response){
                return response;
            }
        });
        
        console.log(metadata);

        // CASES per disease line chart
        if($('#dm-confirmed-per').length) {
            Highcharts.chart('dm-confirmed-per', {
                chart: {
                    type: 'line'
                },
                title: {
                    text: 'Title'
                },
                xAxis: {
                    title: {
                        text: 'Dates'
                    },
                },
                yAxis: {
                    title: {
                        text: 'No. of Pigs'
                    },
                },
            
                series: [
                    {
                        name: 'Confirmed',
                        data: [29, 5, 64, 12, 10]
                    },
                    {
                        name: 'Recovered',
                        data: [9, 75, 14, 12, 14]
                    },
                    {
                        name: 'Died',
                        data: [29, 75, 64, 12, 100]
                    }
                ] 
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
        
    }
})
