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
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'No. of Fattener Pigs per Weight Range'
                },
                xAxis: {
                    type: 'category'
                },
                yAxis: {
                    title: {
                        text: 'Count'
                    }
                },

                plotOptions: {
                    series: {
                        stacking: 'normal',
                        borderWidth: 0,
                        dataLabels: {
                            enabled: true
                        }
                    }
                },
        
                /* Each series includes the count of fattener hogs in ONE WEIGHT RANGE in ALL AREAS. */
                series: [{
                    name: '60-79 kg',
                    data: [{
                        name: 'TISISI',
                        y: 5,
                        drilldown: 'tisisi-low'
                    }, {
                        name: 'West',
                        y: 2,
                        drilldown: 'west-low'
                    }, {
                        name: 'East',
                        y: 4,
                        drilldown: 'east-low'
                    },
                    {
                        name: 'North',
                        y: 4,
                        drilldown: 'north-low'
                    }]
                },
                
                { 
                    name: '80-99 kg',
                    data: [{
                        name: 'TISISI',
                        y: 4,
                        drilldown: 'tisisi-med'
                    }, {
                        name: 'West',
                        y: 4,
                        drilldown: 'west-med'
                    }, {
                        name: 'East',
                        y: 4,
                        drilldown: 'east-med'
                    }, {
                        name: 'North',
                        y: 4,
                        drilldown: 'north-med'
                    }]
                },
                
                {
                    name: '100-120 kg',
                    data: [{
                        name: 'TISISI',
                        y: 5,
                        drilldown: 'tisisi-high'
                    }, {
                        name: 'West',
                        y: 2,
                        drilldown: 'west-high'
                    }, {
                        name: 'East',
                        y: 4,
                        drilldown: 'east-high'
                    },
                    {
                        name: 'North',
                        y: 4,
                        drilldown: 'north-high'
                    }]
                }],

                /* Each drilldown series includes the count of fattener hogs in ONE WEIGHT RANGE in ALL FARMS under ONE AREA. */
                drilldown: {
                    series: [
                    {
                        // showInLegend: false,
                        id: 'tisisi-low',
                        data: [
                            ['Farm 001', 4],
                            ['Farm 002', 2],
                            ['Farm 003', 1],
                            ['Farm 004', 4]
                        ]
                    }, {
                        // showInLegend: false,
                        id: 'west-low',
                        data: [
                            ['Farm 008', 6],
                            ['Farm 009', 2],
                            ['Farm 010', 2],
                            ['Farm 011', 4],
                            ['Farm 012', 4],
                        ]
                    }, {
                        id: 'east-low',
                        data: [
                            ['Farm 013', 2],
                            ['Farm 014', 7],
                            ['Farm 015', 3],
                            ['Farm 016', 2]
                        ]
                    }, {
                        id: 'north-low',
                        data: [
                            ['Farm 017', 2],
                            ['Farm 018', 7],
                            ['Farm 019', 3],
                            ['Farm 020', 2]
                        ]
                    },
                    
                    {
                        id: 'tisisi-med',
                        data: [
                            ['Farm 001', 2],
                            ['Farm 002', 4],
                            ['Farm 003', 1],
                            ['Farm 004', 7]
                        ]
                    }, {
                        id: 'west-med',
                        data: [
                            ['Farm 008', 4],
                            ['Farm 009', 2],
                            ['Farm 010', 5],
                            ['Farm 011', 3],
                            ['Farm 012', 4],
                        ]
                    }, {
                        id: 'east-med',
                        data: [
                            ['Farm 013', 7],
                            ['Farm 014', 8],
                            ['Farm 015', 2],
                            ['Farm 016', 2]
                        ]
                    }, {
                        id: 'north-med',
                        data: [
                            ['Farm 017', 7],
                            ['Farm 018', 8],
                            ['Farm 019', 2],
                            ['Farm 020', 2]
                        ]
                    },
                    
                    {
                        id: 'tisisi-high',
                        data: [
                            ['Farm 001', 4],
                            ['Farm 002', 2],
                            ['Farm 003', 1],
                            ['Farm 004', 4]
                        ]
                    }, {
                        id: 'west-high',
                        data: [
                            ['Farm 008', 6],
                            ['Farm 009', 2],
                            ['Farm 010', 2],
                            ['Farm 011', 4],
                            ['Farm 012', 4],
                        ]
                    }, {
                        id: 'east-high',
                        data: [
                            ['Farm 013', 2],
                            ['Farm 014', 7],
                            ['Farm 015', 3],
                            ['Farm 016', 2]
                        ]
                    },{
                        id: 'north-high',
                        data: [
                            ['Farm 017', 2],
                            ['Farm 018', 7],
                            ['Farm 019', 3],
                            ['Farm 020', 2]
                        ]
                    }]
                }
                
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