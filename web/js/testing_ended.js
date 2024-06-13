document.addEventListener('DOMContentLoaded', async () => {
    const storage = await fetch('http://127.0.0.1:8000/db/get/storage').then(response => response.json());
    const pointsCounter = document.getElementById('points-counter');
    const wrongPoints = storage['max_points'] - storage['points']
    pointsCounter.textContent = `${storage['points']}/${storage['max_points']}`;

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
                y: storage['points'],
                sliced: true,
                selected: true
            }, {
                name: 'Wrong',
                y: wrongPoints
            }]
        }]
    })
})
