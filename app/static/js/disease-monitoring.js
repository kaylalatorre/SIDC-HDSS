$(document).ready(async function () {

    ajaxCSRF();
        metadata = await $.ajax({
            type: 'POST',
            url: '/disease-dashboard',
            success: function(response) {
                return response;
            }
        });

        console.log(metadata);

    // initialize active incidents and load corresponding data
    if ($('#dm-active-incid').length) {

        var today = new Date();
        console.log("TODAY");
        console.log(today);
        // var dateMonthsAgo = today-2592000000;
        var dateMonthsAgo = Date.UTC(2021, 11, 7);
        // console.log(dateMonthsAgo);

        var oneMonth = 2592000000;

        var dateSplit = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
        console.log(dateSplit);

        Highcharts.chart('dm-active-incid', {
            title: {
                text: 'Active Incidents for the past 4 months'
            },
        
            xAxis: {
                type: 'datetime',
                startOnTick: true,
                endOnTick: true,
                min: dateMonthsAgo,
                max: dateSplit,
                labels: {
                    formatter: function() {
                    //   return Highcharts.dateFormat('%Y-%b%e', this.value);
                      return Highcharts.dateFormat('%b %e, %Y', this.value);
                    }},
                units: [
                  [
                    'week', [1]
                  ],
                  [
                    'month', [1]
                  ]
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

            series: [
                {
                    name: metadata[0][0],
                    // data: metadata[0][1],

                    data: metadata[0][1].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[0][1];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    }),

                    // pointStart: dateMonthsAgo,
                    // pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
                {
                    name: metadata[0][2],
                    data: metadata[0][3].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[0][3];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    }),
                    // pointStart: dateMonthsAgo,
                    // pointInterval: 24 * 3600 * 1000 * 7 // one week
                },            
                {
                    name: metadata[0][4],
                    data: metadata[0][5].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[0][5];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    }),
                    // pointStart: dateMonthsAgo,
                    // pointInterval: 24 * 3600 * 1000 * 7 // one week
                },            
                {
                    name: metadata[0][6],
                    data: metadata[0][7].map(function(elem){
                        try {
                            var dStr = elem[0].split('-');
                        } catch{
                            return metadata[0][7];
                        }

                        return [Date.UTC(parseInt(dStr[0]), parseInt(dStr[1])-1, parseInt(dStr[2])), elem[1]];
                    }),
                    // pointStart: dateMonthsAgo,
                    // pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
            ]
        
        });
    }
   
    if ($('#dm-mortality').length) {
        Highcharts.chart('dm-mortality', {
            title: {
                text: 'Mortality Reports for the past 4 months'
            },
    
            xAxis: {
                type: 'datetime',
                startOnTick: true,
                endOnTick: true,
                min: 1546819200000,
                dateTimeLabelFormats: {
                week: '%e of %b'
                },
                units: [
                [
                    'week', [1]
                ],
                [
                    'month', [1]
                ]
                ]
            },
    
            yAxis: {
                title: {
                    text: 'No. of Hogs Died'
                }
            },
            
            series: [
                {
                    name: metadata[1][0],
                    data: metadata[1][1],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
                {
                    name: metadata[1][2],
                    data: metadata[1][1],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },        {
                    name: metadata[1][3],
                    data: metadata[1][4],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
                {
                    name: metadata[1][5],
                    data: metadata[1][6],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
            ]
    
        });
    }
    
    if ($('#dm-symptoms-rep').length) {
        Highcharts.chart('dm-symptoms-rep', {
            chart: {
                type: 'bar'
            },
            title: {
                text: 'Symptoms Reported for the past 4 months'
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
            series: [
                {
                    name: metadata[2][0][0],
                    data: metadata[2][0][1]
                }, 
                {
                    name: metadata[2][1][0],
                    data: metadata[2][1][1]
                },
                {
                    name: metadata[2][2][0],
                    data: metadata[2][2][1]
                },
                {
                    name: metadata[2][3][0],
                    data: metadata[2][3][1]
                },
            ]
        });
    }
    
    if ($('#dm-activities').length) {
        Highcharts.chart('dm-activities', {
            title: {
                text: 'Activities Made'
            },
    
            xAxis: {
                type: 'datetime',
                startOnTick: true,
                endOnTick: true,
                min: 1546819200000,
                dateTimeLabelFormats: {
                week: '%e of %b'
                },
                units: [
                [
                    'week', [1]
                ],
                [
                    'month', [1]
                ]
                ]
            },
    
            yAxis: {
                title: {
                    text: 'No. of Hogs Died'
                }
            },
            
            series: [
                {
                    name: "Delivery of Feeds",
                    data: metadata[1][1],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
                {
                    name: "Delivery of Medicine",
                    data: metadata[1][1],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },        {
                    name: "Inspection",
                    data: metadata[1][4],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
                {
                    name: "Trucking",
                    data: metadata[1][6],
                    pointStart: Date.UTC(2019, 0, 7),
                    pointInterval: 24 * 3600 * 1000 * 7 // one week
                },
            ]
        });
    }
    




})