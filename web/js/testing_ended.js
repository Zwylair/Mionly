function toMainMenu() {
    window.location.href = 'http://127.0.0.1:8000/index.html';
}

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

    const highchartsCredits = document.getElementsByClassName('highcharts-credits');
    for (let element of highchartsCredits) {
        element.remove();
    }

    const highchartsBackground = document.getElementsByClassName('highcharts-background');
    for (let element of highchartsBackground) {
        element.setAttribute('fill', '#ffffff00');
    }

    const highchartsTextOutline = document.getElementsByClassName('highcharts-text-outline');
        for (let element of highchartsTextOutline) {
            element.setAttribute('stroke', '#ffffff00');
    }

    if (localStorage.getItem('theme') === 'dark') {
        const highchartsText = document.querySelectorAll('text');
        for (let element of highchartsText) {
            element.style = 'color: rgb(255, 255, 255); font-size: 0.7em; font-weight: bold; fill: rgb(255, 255, 255);';
        }
    }
});
