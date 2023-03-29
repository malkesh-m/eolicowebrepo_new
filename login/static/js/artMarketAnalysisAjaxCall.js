const topLotsOfTheMonthDiv = document.querySelector('#topLotsOfTheMonth')
const topArtistsOfTheMonthDiv = document.querySelector('#topArtistsOfTheMonth')
const topSalesOfTheMonthDiv = document.querySelector('#topSalesOfTheMonth')

function topPerfromanceOfTheYearChartMaker() {
    let year = 12
    fetch(`/login/topPerformanceOfYearCharts/?year=${year}`, {
        method: 'GET' ,
    })
        .then(response => response.json())
        .then(body => {
            console.log(body)
        })
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

function owlCarouselInit(elementId) {
    var owl = $(`#${elementId}`);
    owl.owlCarousel({
        items: 3,
        margin: 10,
        loop: true,
        nav: true
    });
}

function topArtistsOfTheMonth() {
    fetch('/login/topArtistsOfMonthForCharts/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = topArtistsOfTheMonthDiv.innerHTML = ''
            body.forEach(artistData => {
                htmlData += `
                <div class="item">
                <div class="latest-artists">
                    <a href="/artist/details/?aid=${artistData.artistID}" class="latest-card">
                        <div class="thumb">
                            <img src="https://f000.backblazeb2.com/file/fineart-images/${artistData.artistImage}"
                                class="card-img" alt="img">
                        </div>
                        <div class="artist-card">
                            <table class="table table-striped w-100">
                                <thead class="thead-dark">
                                    <tr>
                                        <th>
                                            <h3>Artist</h3>
                                        </th>
                                        <th class="text-right border-left">
                                            <span>${artistData.artistName}</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            <h3>Total Sale This Year</h3>
                                        </td>
                                        <td  class="text-right border-left">
                                            <span>$ ${artistData.totalSaleOfThisYear}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Average Sale Price (USD)</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>$ ${artistData.averageSalePriceUSD}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sell Through Rate</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${artistData.sellThroughRate}%</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sold Price Above Estimates</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${artistData.soldPriceOverEstimate}%</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </a>
                </div>
            </div>`
            })
            if (htmlData) {
                topArtistsOfTheMonthDiv.innerHTML = htmlData
                owlCarouselInit('topArtistsOfTheMonth')
            }
        })
}

function topSalesOfTheMonth() {
    fetch('/login/topSalesOfMonthForCharts/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = topSalesOfTheMonthDiv.innerHTML = ''
            body.forEach(saleData => {
                htmlData += `
                <div class="item">
                <div class="latest-artists">
                    <a href="/auction/showauction/?aucid=${saleData.auctionID}" class="latest-card">
                        <div class="thumb">
                            <img src="https://f000.backblazeb2.com/file/fineart-images/${saleData.autionImage}"
                                class="card-img" alt="img">
                        </div>
                        <div class="artist-card">
                            <table class="table table-striped w-100">
                                <thead class="thead-dark">
                                    <tr>
                                        <th>
                                            <h3>Sale Title</h3>
                                        </th>
                                        <th class="text-right border-left">
                                            <span>${saleData.auctionName}</span>
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            <h3>Auction House</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${saleData.auctionHouseName}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sale Date</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${saleData.auctionStartDate}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Auction Location</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${saleData.auctionHouseLocation}</span>
                                        </td>
                                    </tr>
                                    
                                    <tr>
                                        <td>
                                            <h3>Total Lots Offered</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${saleData.totalLotsOffered}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Total Lots Sold</h3>
                                        </td>
                                        <td  class="text-right border-left">
                                            <span>${saleData.totalLotsSold}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sell Through Rate</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${saleData.sellThroughRate}%</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Sold Price Over Estimates</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>${saleData.soldPriceOverEstimate}%</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <h3>Total Sale Value</h3>
                                        </td>
                                        <td class="text-right border-left">
                                            <span>$ ${saleData.totalSaleValue}</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </a>
                </div>
            </div>`
            })
            if (htmlData) {
                topSalesOfTheMonthDiv.innerHTML = htmlData
                owlCarouselInit('topSalesOfTheMonth')
            }
        })
}

function topLotsOfTheMonth() {
    fetch('/login/topLotsOfMonthForCharts/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = topLotsOfTheMonthDiv.innerHTML = ''
            let flag = false
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
            if (htmlData) {
                topLotsOfTheMonthDiv.innerHTML = htmlData
                owlCarouselInit('topLotsOfTheMonth')
            }
        })
}

async function topGeographicalLocationsChartMaker() {
    let year = 2012
    let body = await fetch(`/login/topGeographicalLocationsForCharts/?year=${year}`, {
        method: 'GET',
    })
        .then(response => response.json())
    console.log(body)
    // Highcharts.chart('topGeographicalLocationChartId', {
    //     chart: {
    //         type: 'bar'
    //     },
    //     title: {
    //         text: 'Top Geographical Locations',
    //         align: 'center'
    //     },
    //     xAxis: {
    //         categories: ['China', 'United States', 'United Kingdom', 'Germany', 'Australia', 'France', 'Austria', 'Italy', 'Russia', 'Others'],
    //         title: {
    //             text: null
    //         }
    //     },
    //     yAxis: {
    //         min: 0,
    //         title: {
    //             text: null
    //         },
    //         labels: {
    //             overflow: 'justify'
    //         }
    //     },
    //     // tooltip: {
    //     //     valueSuffix: ' millions'
    //     // },
    //     plotOptions: {
    //         bar: {
    //             dataLabels: {
    //                 enabled: true
    //             }
    //         }
    //     },
    //     legend: {
    //         layout: 'vertical',
    //         align: 'right',
    //         verticalAlign: 'top',
    //         x: -40,
    //         y: 80,
    //         floating: true,
    //         borderWidth: 1,
    //         backgroundColor:
    //             Highcharts.defaultOptions.legend.backgroundColor || '#FFFFFF',
    //         shadow: true
    //     },
    //     credits: {
    //         enabled: false
    //     },
    //     series: [{
    //         name: '2022',
    //         data: [631, 727, 202, 721, 26, 631, 727, 202, 721, 26]
    //     }, {
    //         name: '2021',
    //         data: [814, 841, 374, 726, 31, 814, 841, 714, 726, 31]
    //     }, {
    //         name: '2020',
    //         data: [144, 44, 470, 735, 40, 144, 944, 170, 735, 40]
    //     }, {
    //         name: '2019',
    //         data: [276, 107, 561, 746, 42, 1276, 170, 461, 746, 42]
    //     }]
    // });
    const topology = await fetch(
        'https://code.highcharts.com/mapdata/custom/world.topo.json'
    ).then(response => response.json());

    function drawChart(data) {
        return Highcharts.mapChart('topGeographicalLocationChartId', {
            chart: {
                map: topology,
                borderWidth: 1
            },

            colors: ['rgba(19,64,117,0.05)', 'rgba(19,64,117,0.2)', 'rgba(19,64,117,0.4)',
                'rgba(19,64,117,0.5)', 'rgba(19,64,117,0.6)', 'rgba(19,64,117,0.8)', 'rgba(19,64,117,1)'],

            title: {
                text: `Artist Performance By Region Year:- 2012`,
                align: 'center'
            },

            mapNavigation: {
                enabled: true,
                buttonOptions: {
                    align: 'right'
                }
            },

            mapView: {
                fitToGeometry: {
                    type: 'MultiPoint',
                    coordinates: [
                        // Alaska west
                        [-164, 54],
                        // Greenland north
                        [-35, 84],
                        // New Zealand east
                        [179, -38],
                        // Chile south
                        [-68, -55]
                    ]
                }
            },

            legend: {
                title: {
                    text: 'Sale Price (USD)',
                    style: {
                        color: ( // theme
                            Highcharts.defaultOptions &&
                            Highcharts.defaultOptions.legend &&
                            Highcharts.defaultOptions.legend.title &&
                            Highcharts.defaultOptions.legend.title.style &&
                            Highcharts.defaultOptions.legend.title.style.color
                        ) || 'black'
                    }
                },
                align: 'left',
                verticalAlign: 'bottom',
                floating: true,
                layout: 'vertical',
                valueDecimals: 0,
                backgroundColor: ( // theme
                    Highcharts.defaultOptions &&
                    Highcharts.defaultOptions.legend &&
                    Highcharts.defaultOptions.legend.backgroundColor
                ) || 'rgba(255, 255, 255, 0.85)',
                symbolRadius: 0,
                symbolHeight: 14
            },

            colorAxis: {
                dataClasses: [{
                    to: 100
                }, {
                    from: 100,
                    to: 200
                }, {
                    from: 200,
                    to: 400
                }, {
                    from: 400,
                    to: 800
                }, {
                    from: 800,
                    to: 1600
                }, {
                    from: 1600,
                    to: 3200
                }, {
                    from: 3200
                }]
            },

            series: [{
                data: data,
                joinBy: ['iso-a2', 'code'],
                animation: true,
                name: 'Total Sale Price (USD)',
                states: {
                    hover: {
                        color: '#a4edba'
                    }
                },
                // tooltip: {
                //     valueSuffix: ''
                // },
                shadow: false
            }]
        });
    };
    var d = [ {
        code: "YE",
        //name: "Yemen, Rep.",
        value: 46
      }, {
        code: "ZM",
        //name: "Zambia",
        value: 17
      }, {
        code: "ZW",
        //name: "Zimbabwe",
        value: 32
      }];
    drawChart(d)

}

document.addEventListener('DOMContentLoaded', function () {
    topPerfromanceOfTheYearChartMaker()
    topArtistsOfTheMonth()
    topSalesOfTheMonth()
    topLotsOfTheMonth()
    topGeographicalLocationsChartMaker()
})