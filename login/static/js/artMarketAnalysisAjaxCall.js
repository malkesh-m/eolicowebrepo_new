const topLotsOfTheMonthDiv = document.querySelector('#topLotsOfTheMonth')

function topPerfromanceOfTheYearChartMaker() {
    Highcharts.chart('topPerformancesOfTheYearChartId', {
        title: {
            text: 'Top Performance Of The Year',
            align: 'center'
        },
        yAxis: {
            title: {
                text: null
            }
        },
        xAxis: {
            categories: [
                'Jan',
                'Feb',
                'Mar',
                'Apr',
                'May',
                'Jun',
                'Jul',
                'Aug',
                'Sep',
                'Oct',
                'Nov',
                'Dec'
            ]
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },
        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                }
            }
        },
        series: [{
            name: 'Pablo Picasso',
            data: [43934, 48656, 65165, 81827, 112143, 142383,
                171533, 165174, 155157, 161454, 154610, 154610]
        }, {
            name: 'Marc Chagall',
            data: [24916, 37941, 29742, 29851, 32490, 30282,
                38121, 36885, 33726, 34243, 31050, 154610]
        }, {
            name: 'Jean-Michel BASQUIAT',
            data: [11744, 30000, 16005, 19771, 20185, 24377,
                32147, 30912, 29243, 29213, 25663, 154610]
        }, {
            name: 'BANKSY',
            data: [null, null, null, null, null, null, null,
                null, 11164, 11218, 10077, 154610]
        }, {
            name: 'Yoshitomo NARA',
            data: [21908, 5548, 8105, 11248, 8989, 11816, 18274,
                17300, 13053, 11906, 10073, 154610]
        }],
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }
    })
}

function topArtistsOfTheMonth() {
    fetch('/login/topArtistsOfMonthForCharts/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            console.log(body)
        })
}

function topSalesOfTheMonth() {
    fetch('/login/topSalesOfMonthForCharts/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            console.log(body)
        })
}

function topLotsOfTheMonth() {
    fetch('/login/topLotsOfMonthForCharts/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = topLotsOfTheMonthDiv.innerHTML = ''
            body.forEach(lotsData => {
                htmlData += `
                <div class="item">
                <div class="latest-artists">
                    <a href="/auction/details/?lid=${lotsData.lotID}" class="latest-card">
                        <div class="thumb">
                            <img src="https://f000.backblazeb2.com/file/fineart-images/${lotsData.artworkImage}"
                                class="card-img" alt="img">
                        </div>
                        <div class="artist-card">
                            <table class="table table-striped w-100">
                                <thead class="thead-dark">
                                    <tr>
                                        <th>
                                            <h3>Lot Title</h3>
                                        </th>
                                        <th class="text-right border-left">
                                            <span>${lotsData.artworkTitle}</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            <h3>Artist</h3>
                                        </td>
                                        <td  class="text-right border-left">
                                            <span>${lotsData.artistName}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Price Sold</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${lotsData.currencyCode} ${lotsData.lotSalePrice}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Price Sold</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>USD ${lotsData.lotSalePriceUSD}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Lot</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${lotsData.lotNum}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sale Title</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${lotsData.auctionTitle}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Auction House</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${lotsData.auctionHouseName}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sale Date</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${lotsData.auctionStartDate}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Auction Location</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${lotsData.auctionHouseLocation}</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </a>
                </div>
            </div>`
            })
            topLotsOfTheMonthDiv.innerHTML = htmlData
            owlSlider('#topLotsOfTheMonth')
        })
}

function topGeographicalLocationsChartMaker() {
    Highcharts.chart('topGeographicalLocationChartId', {
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Top Geographical Locations',
            align: 'center'
        },
        xAxis: {
            categories: ['China', 'United States', 'United Kingdom', 'Germany', 'Australia', 'France', 'Austria', 'Italy', 'Russia', 'Others'],
            title: {
                text: null
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: null
            },
            labels: {
                overflow: 'justify'
            }
        },
        // tooltip: {
        //     valueSuffix: ' millions'
        // },
        plotOptions: {
            bar: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -40,
            y: 80,
            floating: true,
            borderWidth: 1,
            backgroundColor:
                Highcharts.defaultOptions.legend.backgroundColor || '#FFFFFF',
            shadow: true
        },
        credits: {
            enabled: false
        },
        series: [{
            name: '2022',
            data: [631, 727, 202, 721, 26, 631, 727, 202, 721, 26]
        }, {
            name: '2021',
            data: [814, 841, 374, 726, 31, 814, 841, 714, 726, 31]
        }, {
            name: '2020',
            data: [144, 44, 470, 735, 40, 144, 944, 170, 735, 40]
        }, {
            name: '2019',
            data: [276, 107, 561, 746, 42, 1276, 170, 461, 746, 42]
        }]
    });
    
}

document.addEventListener('DOMContentLoaded', function () {
    topPerfromanceOfTheYearChartMaker()
    topArtistsOfTheMonth()
    topSalesOfTheMonth()
    // topLotsOfTheMonth()
    topGeographicalLocationsChartMaker()
})