$(document).ready(async function () {

    if($('#dm-active-incid').length || $('#dm-mortality').length || $('#dm-symptoms-rep').length || $('#dm-activities').length){
        ajaxCSRF();
        metadata = await $.ajax({
            type: 'POST',
            url: '/disease-dashboard',
            success: function(response) {
                return response;
            }
        });

        console.log(metadata);

        
        var today = new Date();
        var dateBefore = Date.UTC(today.getFullYear(), today.getMonth()-1, today.getDate());
        var dateToday = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());

        
        // ACTIVE INCIDENTS line chart
        if ($('#dm-active-incid').length) {

            var incSeries = [];
            for(var i = 0; i < metadata[0].length; i++){
                // console.log(metadata[0][i][1])
                
                incSeries.push({
                    name: metadata[0][i][0],
                    data: metadata[0][i][1].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[0][1];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    })
                });
            }

            // console.log(incSeries);

            Highcharts.chart('dm-active-incid', {
                title: {
                    text: 'Active Incidents for the past month'
                },
            
                xAxis: {
                    type: 'datetime',
                    min: dateBefore,
                    max: dateToday,
                    dateTimeLabelFormats: {
                        week: '%e %b' },
                    units: [
                        [ 'week', [1] ],
                        [ 'month', [1] ]
                    ]
                },
            
                yAxis: {
                    title: {
                        text: 'No. of Affected Hogs'
                    }
                },
                
                plotOptions: {
                    series: {
                        connectNulls: true
                    }
                },

                series: incSeries,
            
            });
        }
    

        // MORTALITY line chart
        if ($('#dm-mortality').length) {

            var mortSeries = [];
            for(var i = 0; i < metadata[1].length; i++){

                mortSeries.push({
                    name: metadata[1][i][0],
                    data: metadata[1][i][1].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[1][1];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    })
                });
            }

            // console.log(mortSeries);

            Highcharts.chart('dm-mortality', {
                title: {
                    text: 'Mortality Reports for the past month'
                },
        
                xAxis: {
                    type: 'datetime',
                    min: dateBefore,
                    max: dateToday,
                    dateTimeLabelFormats: {
                        week: '%e %b' },
                    units: [
                        [ 'week', [1] ],
                        [ 'month', [1] ]
                    ]
                },
        
                yAxis: {
                    title: {
                        text: 'No. of Hogs Died'
                    }
                },
                            
                plotOptions: {
                    series: {
                        connectNulls: true
                    }
                },

                series: mortSeries,
        
            });
        }
        

        // SYMPTOMS RECORDED bar chart
        if ($('#dm-symptoms-rep').length) {

            var symSeries = [];
            for(var i = 0; i < metadata[2].length; i++){

                symSeries.push({
                    name: metadata[2][i][0],
                    data: metadata[2][i][1]
                });
            }

            // console.log(symSeries);
            
            Highcharts.chart('dm-symptoms-rep', {
                chart: {
                    type: 'bar'
                },
                title: {
                    text: 'Symptoms Reported for the past month'
                },
                xAxis: {
                    categories: [
                        'High Fever',
                        'Loss of Appetite',
                        'Depression',
                        'Lethargic',
                        'Constipation',
                        'Vomitting/diarrhea with bloody discharge',
                        'White-skinned or cyanotic',
                        'Red/blotchy skin lesions',
                        'Discrete hemorrhages',
                        'Abnormal breathing',
                        'Heavy discharge from eyes and/or nose',
                        'Death within 6-13 days',
                        'Death (in less than 1 week old)',
                        'Coughing',
                        'Sneezing',
                        'Runny nose',
                        'Wasting',
                        'Reduced libido (boars)',
                        'Miscarriage (farrows)',
                        'Weight loss',
                        'Trembling and incoordination',
                        'Conjunctivitis'
                    ],
                    title: {
                        text: 'Symptoms'
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Population',
                        align: 'high'
                    },
                    labels: {
                        overflow: 'justify'
                    }
                },
                plotOptions: {
                    bar: {
                        dataLabels: {
                            enabled: true
                        }
                    }
                },
                series: symSeries,
            });
        }
        

        // ACTIVITIES line chart
        if ($('#dm-activities').length) {

            var actSeries = [];
            for(var i = 0; i < metadata[3].length; i++){

                actSeries.push({
                    name: metadata[3][i][0],
                    data: metadata[3][i][1].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[3][1];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    })
                });
            }

            // console.log(actSeries);

            Highcharts.chart('dm-activities', {
                title: {
                    text: 'Activities Made for the past month'
                },
        
                xAxis: {
                    type: 'datetime',
                    min: dateBefore,
                    max: dateToday,
                    dateTimeLabelFormats: {
                    week: '%e %b'
                    },
                    units: [
                        [ 'week', [1] ],
                        [ 'month', [1] ]
                    ]
                },
        
                yAxis: {
                    title: {
                        text: 'Count'
                    }
                },
                
                plotOptions: {
                    series: {
                        connectNulls: true
                    }
                },

                series: actSeries,
            });
        }



    }
    
})