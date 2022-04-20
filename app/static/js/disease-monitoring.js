// DISEASE MONITORING
$(document).ready(async function () {
    if($('#dm-confirmed-per').length || $('#dm-mortality-per').length) {
        
        // CONFIRMED CASES per disease column chart
        if($('#dm-confirmed-per').length) {
            Highcharts.chart('dm-confirmed-per', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                xAxis: {
                    title: {
                        text: 'Year'
                    },
                    categories: ['2018', '2019', '2020', '2021', '2022']
                },
                yAxis: {
                    title: {
                        text: 'Population Died'
                    }
                },
            
                series: [
                    {
                        name: 'ASF',
                        data: [29, 5, 64, 12, 10]
                    },
                    {
                        name: 'CSF',
                        data: [9, 75, 14, 12, 14]
                    },
                    {
                        name: 'IAV',
                        data: [29, 75, 64, 12, 100]
                    },
                    {
                        name: 'ADV',
                        data: [9, 71, 106, 129, 144]
                    },
                    {
                        name: 'PRRS',
                        data: [2, 7, 10, 12, 14]
                    },
                    {
                        name: 'PED',
                        data: [14, 17, 13, 18, 20]
                    }
                ] 
            })
        }
    
        // MORTALITIES per disease column chart
        if($('#dm-mortality-per').length) {
            Highcharts.chart('dm-mortality-per', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: ''
                },
                xAxis: {
                    title: {
                        text: 'Year'
                    },
                    categories: ['2018', '2019', '2020', '2021', '2022']
                },
                yAxis: {
                    title: {
                        text: 'Population Died'
                    }
                },
            
                series: [
                    {
                        name: 'ASF',
                        data: [29, 5, 64, 12, 10]
                    },
                    {
                        name: 'CSF',
                        data: [9, 75, 14, 12, 14]
                    },
                    {
                        name: 'IAV',
                        data: [29, 75, 64, 12, 100]
                    },
                    {
                        name: 'ADV',
                        data: [9, 71, 106, 129, 144]
                    },
                    {
                        name: 'PRRS',
                        data: [2, 7, 10, 12, 14]
                    },
                    {
                        name: 'PED',
                        data: [14, 17, 13, 18, 20]
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
                    text: ''
                },
                legend: {
                    layout: 'horizontal',
                    align: 'center',
                    verticalAlign: 'bottom',
                    floating: false,
                },
                xAxis: {
                },
                yAxis: {
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
