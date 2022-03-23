$(document).ready(async function () {

    if($('#wr-weight').length || $('#wr-hogs-weight').length){
        ajaxCSRF();
        metadata = await $.ajax({
            type: 'POST',
            url: '/weight-range',
            success: function(response) {
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


        // DASHBOARD WEIGHT column chart 
        if ($('#wr-weight').length) {
            Highcharts.chart('wr-weight', {
                title: 
                {
                    text: 'No. of Fattener Pigs per Weight Range'
                },
                chart: 
                {
                    type: 'column'
                },

                plotOptions: {
                    series: {
                        stacking: 'normal'
                    }
                },

                // areas
                xAxis: {
                    categories: ['TISISI', 'West', 'East', 'North']
                },
                yAxis: {
                    text: 'Population',
                    stackLabels: {
                        enabled: true,
                    },
                    min: 40,
                    max: 120
                },

                series: [
                    {
                        name: "100-120 kg",
                        data: [{
                            y: 101.0,
                            drilldown: "test1"
                        }, 
                        {
                            y: 110.2,
                            drilldown: "test1"
                        },
                        {
                            y: 120.2,
                            drilldown: "test1"
                        },
                        {
                            y: 100.2,
                            drilldown: "test1"
                        }
                        ]
                    },
                    {
                        name: "80-99 kg",
                        data: [{
                            y: 88.0,
                            drilldown: "test1"
                        }, 
                        {
                            y: 82.4,
                            drilldown: "test1"
                        },
                        {
                            y: 80.2,
                            drilldown: "test1"
                        },
                        {
                            y: 94.2,
                            drilldown: "test1"
                        }
                        ]
                    },
                    {
                        name: "60-79 kg",
                        data: [{
                            y: 60.0,
                            drilldown: "test1"
                        }, 
                        {
                            y: 70.4,
                            drilldown: "test1"
                        },
                        ]
                    }
                    
                ]
                
            });
        }


        // SELECTED WEIGHT pie chart (hogs-health and health-symptoms)
        // if ($('#wr-hogs-weight').length) {
        //     Highcharts.chart('wr-hogs-weight', {
        //         chart: {
        //             type: 'column'
        //         },
        //         title: {
        //             text: 'No. of Fattener Pigs per Weight Range'
        //         },
        //         xAxis: {
        //             categories: [
        //                 '60-79 kg',
        //                 '80-99 kg',
        //                 '100-120 kg',
        //             ],
        //             crosshair: true
        //         },
        //         yAxis: {
        //             min: 0,
        //             title: {
        //                 text: 'Count'
        //             }
        //         },
        //         plotOptions: {
        //             column: {
        //                 pointPadding: 0.2,
        //                 borderWidth: 0
        //             }
        //         },
        //         series: [{
        //             showInLegend: false,             
        //             data: [49.9, 71.5, 106.4]
            
        //         }]
        //     });
        // }


        // SELECTED WEIGHT pie chart (hogs-health and health-symptoms)
        // if ($('#wr-hogs-weight').length) {
        //     Highcharts.chart('wr-hogs-weight', {
        //         chart: {
        //             type: 'pie'
        //         },
        //         title: {
        //             text: 'No. of Fattener Pigs per Weight Range'
        //         },
        //         tooltip: {
        //             pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        //         },
        //         accessibility: {
        //             point: {
        //                 valueSuffix: '%'
        //             }
        //         },
        //         plotOptions: {
        //             pie: {
        //                 allowPointSelect: true,
        //                 cursor: 'pointer',
        //                 dataLabels: {
        //                     enabled: false
        //                 },
        //                 showInLegend: true
        //             }
        //         },
        //         series: [{
        //             name: 'Weight Range',
        //             colorByPoint: true,
        //             data: [{
        //                 name: '60-79 kg',
        //                 y: 10.41
        //             },
        //             {
        //                 name: '80-99 kg',
        //                 y: 11.84
        //             },
        //             {
        //                 name: '100-120 kg',
        //                 y: 61.85,
        //                 sliced: true,
        //                 selected: true
        //             }]
        //         }]
        //     });
        // }

        
    }
    
})