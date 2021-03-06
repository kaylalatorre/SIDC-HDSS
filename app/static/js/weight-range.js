$(document).ready(async function () {

    if($('#wr-weight').length){
        ajaxCSRF();
        metadata = await $.ajax({
            type: 'POST',
            url: '/weight-range',
            success: function(response) {
                return response;
            }
        });

        // console.log(metadata);

        // DASHBOARD WEIGHT column chart 
        if ($('#wr-weight').length) {

            // ADDING DATA TO THE MAIN SERIES
            var weightSeries = [], range0 = [],
                range1 = [], range2 = [],
                range3 = [], range4 = [];

            // looping through all areas
            for(var i = 0; i < metadata.length; i++){

                // feeding data of current area to each weight range
                range0.push({
                    name: metadata[i][0],
                    y: metadata[i][1][0],
                    drilldown: metadata[i][0].concat("-range0")
                });

                range1.push({
                    name: metadata[i][0],
                    y: metadata[i][2][0],
                    drilldown: metadata[i][0].concat("-range1")
                });

                range2.push({
                    name: metadata[i][0],
                    y: metadata[i][3][0],
                    drilldown: metadata[i][0].concat("-range2")
                });

                range3.push({
                    name: metadata[i][0],
                    y: metadata[i][4][0],
                    drilldown: metadata[i][0].concat("-range3")
                });

                range4.push({
                    name: metadata[i][0],
                    y: metadata[i][5][0],
                    drilldown: metadata[i][0].concat("-range4")
                });
            };

            // feeding all weight range data to the corresponding categories (main series)
            weightSeries.push({
                name: '59 kg and below',
                data: range0,
                color: '#ff401f'
            }, {
                name: '60-79 kg',
                data: range1,
                color: '#ff931f'
            }, {
                name: '80-99 kg',
                data: range2,
                color: '#ffda1f'
            }, {
                name: '100-119 kg',
                data: range3,
                color: '#1fff5e'
            }, {
                name: '120 kg and above',
                data: range4,
                color: '#1cbfff'
            });


            // ADDING DATA TO THE DRILLDOWN SERIES
            var drilldownSeries = [];

            for(var i = 0; i < metadata.length; i++){

                drilldownSeries.push({
                    name: '59 kg and below',
                    id: metadata[i][0].concat("-range0"),
                    data: metadata[i][1][1]
                })

                drilldownSeries.push({
                    name: '60-79 kg',
                    id: metadata[i][0].concat("-range1"),
                    data: metadata[i][2][1]
                })
                
                drilldownSeries.push({
                    name: '80-99 kg',
                    id: metadata[i][0].concat("-range2"),
                    data: metadata[i][3][1]
                })
                
                drilldownSeries.push({
                    name: '100-119 kg',
                    id: metadata[i][0].concat("-range3"),
                    data: metadata[i][4][1]
                })
                
                drilldownSeries.push({
                    name: '120 kg and above',
                    id: metadata[i][0].concat("-range4"),
                    data: metadata[i][5][1]
                })
            };

            // console.log(weightSeries);
            // console.log(drilldownSeries);


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
                        text: 'Hog Count'
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
                series: weightSeries,

                /* Each drilldown series includes the count of fattener hogs in ONE WEIGHT RANGE in ALL FARMS under ONE AREA. */
                drilldown: {series: drilldownSeries},

            });
        }
    }
})