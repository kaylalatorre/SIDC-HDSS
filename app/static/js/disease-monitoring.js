// DISEASE MONITORING
$(document).ready(async function () {
    if($('#dm-confirmed-per').length || $('#dm-mortality-per').length) {
        
        // CONFIRMED CASES per disease column chart
        if($('#dm-confirmed-per').length) {
            Highcharts.chart('dm-confirmed-per', {
                chart: {
                    type: 'column'
                },
            })
        }
    
        // MORTALITIES per disease column chart
        if($('#dm-mortality-per').length) {
            Highcharts.chart('dm-mortality-per', {
                chart: {
                    type: 'column'
                },
            })
        }

        // SERID for ASF
        if($('#dm-seird-asf').length) {
            Highcharts.chart('dm-seird-asf', {
                chart: {
                    type: 'spline'
                },
            })
        }
        
    }
})
