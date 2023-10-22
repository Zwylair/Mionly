
document.addEventListener('DOMContentLoaded', async function () {
    let progressResults = await eel.get_progress_results()();

    let pointsCounter = document.getElementById("points-counter");
    let possiblePoints = progressResults['wrong'] + progressResults['right'];
    pointsCounter.textContent = `${progressResults['right']}/${possiblePoints}`;

    Highcharts.chart('chart-container', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {text: 'Answers statistic', align: 'left'},
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
                y: progressResults['right'],
                sliced: true,
                selected: true
            }, {
                name: 'Wrong',
                y: progressResults['wrong']
            }]
        }]
    })
})
