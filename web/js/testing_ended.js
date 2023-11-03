document.addEventListener('DOMContentLoaded', async function () {
    const progressResults = await eel.get_progress_results()();
    const pointsCounter = document.getElementById('points-counter');
    const wrongPoints = progressResults['max_points'] - progressResults['got_points']
    pointsCounter.textContent = `${progressResults['got_points']}/${progressResults['max_points']}`;

    // spawn pie chart of wrong/right answers
    Highcharts.chart('chart-container', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: null,
        tooltip: {pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'},
        accessibility: {point: {valueSuffix: '%'}},
        plotOptions: {
            pie: {
                allowPointSelect: false,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        series: [{
            name: 'Brands',
            colorByPoint: true,
            data: [{
                name: 'Right',
                y: progressResults['got_points'],
                sliced: true,
                selected: true
            }, {
                name: 'Wrong',
                y: wrongPoints
            }]
        }]
    })
})
