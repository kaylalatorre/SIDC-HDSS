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
    Highcharts.chart('dm-active-incid', {
        title: {
            text: 'Active Incidents for the past 4 mos'
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
                text: 'No. of Affected Hogs'
            }
        },
        
        series: [
            {
                name: metadata[0][0],
                data: metadata[0][1],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },
            {
                name: metadata[0][2],
                data: metadata[0][3],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },            
            {
                name: metadata[0][4],
                data: metadata[0][5],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },            
            {
                name: metadata[0][6],
                data: metadata[0][7],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },
        ]
    
    });

    Highcharts.chart('dm-mortality', {
        title: {
            text: 'Mortality Reports for the past 4 mos'
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
                data: metadata[1][3],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },        {
                name: metadata[1][4],
                data: metadata[1][5],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },
            {
                name: metadata[1][6],
                data: metadata[1][7],
                pointStart: Date.UTC(2019, 0, 7),
                pointInterval: 24 * 3600 * 1000 * 7 // one week
            },
        ]

    });

    Highcharts.chart('dm-symptoms-rep', {
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Symptoms Reported'
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
                name: 'TSISI',
                data: [10, 11, 0, 2, 2, 0, 0, 12, 2, 1, 0, 0, 0, 0, 0, 1, 10, 10, 10, 5, 2]
            }, 
            {
                name: 'West',
                data: [0, 21, 1, 2, 2, 0, 0, 1, 12, 14, 1, 3, 5, 0, 0, 1, 11, 0, 0, 0, 2]
            }
        ]
    });
})