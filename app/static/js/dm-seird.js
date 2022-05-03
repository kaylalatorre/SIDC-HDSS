$(document).ready(async function () {
    // onclick disease -- render specific disease
    // async function diseaseChart(strdisease) {

        
        // console.log(metadata);
        console.log("loading sierd chart")

        var today = new Date();
        // console.log(today);
        
        var dateBefore = Date.UTC(today.getFullYear(), today.getMonth()-1, today.getDate());
        // console.log(dateBefore);
    
        var dateToday = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
        // console.log(dateToday);

        // SERID
        if($('#dm-seird').length) {
            Highcharts.chart('dm-seird', {
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
        
    // };

    // const tab = $('#diseasemonitor-tab');
    // console.log(tab);
    // console.log(tab.hasClass('active'));

    // if((tab.hasClass('active'))){
    //     console.log("!!!!!!!!!!!!!!!!!!!!!");
        
    // }
});