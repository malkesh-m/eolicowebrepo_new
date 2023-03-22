const urlParams = new URLSearchParams(location.search)
const artistId = urlParams.get('aid').replaceAll('"', '')
const artistNameID = document.querySelector('#artistNameId')
const nationalityBirthDeathId = document.querySelector('#nationalityBirthDeathId')
const artistImageId = document.querySelector('#artistImageId')
const aboutNameId = document.querySelector('#aboutNameId')
const artistBioId = document.querySelector('#artistBioId')
const lastYearSoldLotsId = document.querySelector('#lastYearSoldLotsId')
const lastYearSellRateId = document.querySelector('#lastYearSellRateId')
const lastYearAveSalePriceId = document.querySelector('#lastYearAveSalePriceId')
const lastYearSoldPriceEstimatesId = document.querySelector('#lastYearSoldPriceEstimatesId')
const auctionsDataDivID = document.querySelector('#pastauctions')
const upcomingauctions = document.querySelector('#upcomingauctions')
const artsitFollowUnfollowId = document.querySelector('#artsitFollowUnfollowId')
const advancedAnalytics = document.querySelector('#advancedAnalytics')
let pastUpcomingStrData = 'past'

function htmlDataBinder(auctionData) {
    let htmlData = `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-4 mb-4 artworkData">
                        <div class="latest-artists">
                            <a href="/auction/details/?lid=${auctionData.fal_lot_ID}" class="latest-card">
                                <div class="thumb">
                                    <img src="https://f000.backblazeb2.com/file/fineart-images/${auctionData.faa_artwork_image1}" class="card-img" alt="img">
                                </div>
                                <div class="artist-card">
                                    <h3>Title : <span>${auctionData.faa_artwork_title}</span></h3>
                                    <h3>Artist : <span>${auctionData.fa_artist_name}</span></h3>
                                    <h3 class="mb-3">Lot : ${auctionData.fal_lot_no}</h3>

                                    <h3>Medium : <span>${auctionData.faa_artwork_material}</span></h3>
                                    <h3 class="mb-3">Category : <span>${auctionData.faa_artwork_category}</span>
                                    </h3>

                                    <h3>${auctionData.faac_auction_title}</h3>
                                    <h3><span>${auctionData.cah_auction_house_name}</span></h3>
                                    <h3 class="mb-3"><span>${auctionData.faac_auction_start_date} | ${auctionData.cah_auction_house_location}</span>
                                    </h3>

                                    <h3>Estimate : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_low_estimate} - ${auctionData.fal_lot_high_estimate}</span></h3>`
    if (auctionData.cah_auction_house_currency_code === 'USD') {
        if (auctionData.fal_lot_sale_price == 0) {
            htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
        }
        else {
            htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>`
        }
    }
    else {
        htmlData += `<h3>Estimate USD : <span>${auctionData.fal_lot_low_estimate_USD} - ${auctionData.fal_lot_high_estimate_USD}</span></h3>`
        if (auctionData.fal_lot_sale_price == 0) {
            htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
        }
        else {
            htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>
                                                        <h3>Price Sold USD : <span>${auctionData.fal_lot_sale_price_USD}</span></h3>`
        }
    }
    htmlData += `
                                </div>
                            </a>
                        </div>
                    </div>`
    return htmlData
}

function upcomingAuctionDataSet(queryParams, limit) {
    fetch(`/artist/getArtistUpcomingAuctions/?aid=${artistId}&${queryParams}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionData => {
                htmlData += htmlDataBinder(auctionData)
            })
            auctionsDataDivID.innerHTML = htmlData
        })
}

function pastAuctionDataSet(queryParams, limit) {
    fetch(`/artist/getArtistPastAuctions/?aid=${artistId}&${queryParams}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionData => {
                htmlData += htmlDataBinder(auctionData)
            })
            auctionsDataDivID.innerHTML = htmlData
        })
}

function pastUpcomingAuction(e, pastUpcomingStr, queryParams) {
    advancedAnalytics.style.display = 'none'
    pastUpcomingStrData = pastUpcomingStr
    let limit = document.querySelector('#inputGroupSelect01').value
    if (pastUpcomingStrData === 'past') {
        pastAuctionDataSet(queryParams, limit)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionDataSet(queryParams, limit)
    }
    document.querySelector('#inputGroupSelect01').style.display = upcomingauctions.style.display = 'block'
}

function selectChange(e) {
    let limit = e.target.value
    if (pastUpcomingStrData === 'past') {
        pastAuctionDataSet('', limit)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionDataSet('', limit)
    }
}

function filterAuction(e) {
    const artworkTitleTextId = document.querySelector('#artworkTitleTextId')
    const lotLowToHighCheckId = document.querySelector('#lotLowToHighCheckId')
    const lotHighToLowCheckId = document.querySelector('#lotHighToLowCheckId')
    const priceLowToHighCheckId = document.querySelector('#priceLowToHighCheckId')
    const priceHighToLowCheckId = document.querySelector('#priceHighToLowCheckId')
    const paintingsCheckId = document.querySelector('#paintingsCheckId')
    const printsCheckId = document.querySelector('#printsCheckId')
    const photographsCheckId = document.querySelector('#photographsCheckId')
    const miniaturesCheckId = document.querySelector('#miniaturesCheckId')
    const othersCheckId = document.querySelector('#othersCheckId')
    const soldCheckId = document.querySelector('#soldCheckId')
    const yetToBeSoldCheckId = document.querySelector('#yetToBeSoldCheckId')
    const boughtInCehckId = document.querySelector('#boughtInCehckId')
    const withdrawnCheckId = document.querySelector('#withdrawnCheckId')
    const fromDateTextId = document.querySelector('#fromDateTextId')
    const toDateTextId = document.querySelector('#toDateTextId')

    let queryParams = ``

    if (artworkTitleTextId.value) {
        queryParams = queryParams + `artworkTitle=${artworkTitleTextId.value}&`
    }
    if (lotLowToHighCheckId.checked) {
        queryParams = queryParams + `lotLowToHigh=true&`
    }
    if (lotHighToLowCheckId.checked) {
        queryParams = queryParams + `lotHighToLow=true&`
    }
    if (priceLowToHighCheckId.checked) {
        queryParams = queryParams + `priceLowToHigh=true&`
    }
    if (priceHighToLowCheckId.checked) {
        queryParams = queryParams + `priceHighToLow=true&`
    }
    if (paintingsCheckId.checked) {
        queryParams = queryParams + `paintings=paintings&`
    }
    if (printsCheckId.checked) {
        queryParams = queryParams + `prints=prints&`
    }
    if (photographsCheckId.checked) {
        queryParams = queryParams + `photographs=photographs&`
    }
    if (miniaturesCheckId.checked) {
        queryParams = queryParams + `miniatures=miniatures&`
    }
    if (othersCheckId.checked) {
        queryParams = queryParams + 'others=all&'
    }
    if (soldCheckId.checked) {
        queryParams = queryParams + `sold=sold&`
    }
    if (yetToBeSoldCheckId.checked) {
        queryParams = queryParams + `yetToBeSold=yet to be sold&`
    }
    if (boughtInCehckId.checked) {
        queryParams = queryParams + `boughtIn=bought-in&`
    }
    if (withdrawnCheckId.checked) {
        queryParams = queryParams + `withdrawn=withdrawn&`
    }
    if (fromDateTextId.value) {
        queryParams = queryParams + `fromDate=${fromDateTextId.value}&`
    }
    if (toDateTextId.value) {
        queryParams = queryParams + `toDate=${toDateTextId.value}&`
    }

    pastUpcomingAuction(e, pastUpcomingStrData, queryParams)
}

function abbreviateNumber(value) {
    let newValue = value;
    if (value >= 1000) {
        let suffixes = ["", "K", "M", "B", "T"];
        let suffixNum = Math.floor(("" + value).length / 3);
        let shortValue = '';
        for (let precision = 2; precision >= 1; precision--) {
            shortValue = parseFloat((suffixNum != 0 ? (value / Math.pow(1000, suffixNum)) : value).toPrecision(precision));
            let dotLessShortValue = (shortValue + '').replace(/[^a-zA-Z 0-9]+/g, '');
            if (dotLessShortValue.length <= 2) { break; }
        }
        if (shortValue % 1 != 0) shortValue = shortValue.toFixed(2);
        newValue = shortValue + suffixes[suffixNum];
    }
    return newValue;
}

function getArtistDetails() {
    fetch(`/artist/getArtistDetails/?aid=${artistId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            artistNameID.innerHTML = body.fa_artist_name
            nationalityBirthDeathId.innerHTML = `${body.fa_artist_nationality}, ${body.fa_artist_birth_year} - ${body.fa_artist_death_year}`
            artistImageId.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fa_artist_image}`
            aboutNameId.innerHTML = aboutNameId.innerHTML + ' ' + body.fa_artist_name
            artistBioId.innerHTML = body.fa_artist_bio
            let htmlData = ''
            if (body.fa_artist_nationality !== 'na') {
                htmlData = htmlData + body.fa_artist_nationality
            }
            if (body.fa_artist_birth_year != 0) {
                htmlData = htmlData + ' , ' + body.fa_artist_birth_year
                if (body.fa_artist_death_year != 0) {
                    htmlData = htmlData + ` - ${body.fa_artist_death_year}`
                }
            }
            nationalityBirthDeathId.innerHTML = htmlData
            lastYearSoldLotsId.innerHTML = body.years_lot_sale
            lastYearSellRateId.innerHTML = Math.round(body.sell_through_rate) + '%'
            lastYearAveSalePriceId.innerHTML = abbreviateNumber(Math.round(body.avg_sale_price_usd))
            lastYearSoldPriceEstimatesId.innerHTML = Math.round(body.mean_price_usd) + '%'
        })
}

function followUnfollowArtist(followUnfollowStr) {
    artsitFollowUnfollowId.innerHTML = '<button class="btn btn-login btn-round ms-0" type="button">Please Wait!</button>'
    fetch(`/artist/followUnfollowArtist/?artistId=${artistId}&followUnfollowStr=${followUnfollowStr}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = `<button class="btn btn-login btn-round ms-0" type="button" onclick="followUnfollowArtist('${body.msg}')">${body.msg}</button>`
            artsitFollowUnfollowId.innerHTML = htmlData
        })
}

function advacedAnalytics(e) {
    document.querySelector('#inputGroupSelect01').style.display = upcomingauctions.style.display = 'none'
    advancedAnalytics.style.display = 'block'
}

function artistAnnualPerformanceChartMaker() {
    Highcharts.chart('artistAnnualPerformanceChartId', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Artist Annual Performance'
        },
        subtitle: {
            text: 'Number of Lots offered & Lots Sold (Sale Through Rate) - Year v/s Number'
        },
        xAxis: {
            categories: [
                '2013',
                '2014',
                '2015',
                '2016',
                '2017',
                '2018',
                '2019',
                '2020',
                '2021',
                '2022',
                '2023'
            ],
            crosshair: true
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Rainfall (mm)'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: 'Number of Lots Offered',
            data: [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4,194.1, 95.6]
    
        }, {
            name: 'Number of Lots Sold',
            data: [83.6, 78.8, 98.5, 93.4, 106.0, 84.5, 105.0, 104.3, 91.2, 83.5,106.6]
    
        }, {
            name: 'Number of Lots Unsold',
            data: [48.9, 38.8, 39.3, 41.4, 47.0, 48.3, 59.0, 59.6, 52.4, 65.2, 59.3]
        }]
    });
}

function yoyTotalSaleInUSDChartMaker() {
    Highcharts.chart('yoyTotalSaleChartId', {
        chart: {
            type: 'column'
        },
        title: {
            align: 'center',
            text: 'YOY Total Sale'
        },
        accessibility: {
            announceNewData: {
                enabled: true
            }
        },
        xAxis: {
            type: 'category'
        },
        yAxis: {
            title: {
                text: 'Total Sales In Million (USD)'
            }

        },
        legend: {
            enabled: false
        },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    format: '{point.y}M'
                }
            }
        },

        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}M</b> of total<br/>'
        },

        series: [
            {
                name: 'Years',
                colorByPoint: false,
                data: [
                    {
                        name: '2013',
                        y: 63
                    },
                    {
                        name: '2014',
                        y: 19
                    },
                    {
                        name: '2015',
                        y: 10
                    },
                    {
                        name: '2016',
                        y: 15
                    },
                    {
                        name: '2017',
                        y: 20
                    },
                    {
                        name: '2018',
                        y: 23
                    },
                    {
                        name: '2019',
                        y: 15
                    },
                    {
                        name: '2020',
                        y: 15
                    },
                    {
                        name: '2021',
                        y: 20
                    },
                    {
                        name: '2022',
                        y: 23
                    },
                    {
                        name: '2023',
                        y: 15
                    }
                ]
            }
        ]
    })
}

function YoySellingCatAverageSellingPricePerCatChartMaker() {
    Highcharts.chart('YoySellingCatAverageSellingPricePerCatChartId', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'YOY Selling Categories & Average Selling Price Per Category'
        },
        xAxis: {
            categories: [
                '2013',
                '2014',
                '2015',
                '2016',
                '2017',
                '2018',
                '2019',
                '2020',
                '2021',
                '2022',
                '2023'
            ],
            crosshair: true
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Rainfall (mm)'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: 'Paintings',
            data: [10, 20, 30, 40, 50, 60, 70, 80, 90, 85, 75]

        }, {
            name: 'Work on Paper',
            data: [55, 90, 80, 70, 60, 50, 40, 30, 20, 10, 25]

        }, {
            name: 'Sculptures',
            data: [5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 50]

        }, {
            name: 'Prints',
            data: [60, 95, 85, 75, 65, 55, 45, 35, 25, 15, 5]

        }]
    });
}

// function artistPerformancesByRegionChartMaker() {
//     Highcharts.chart('artistPerformannceByRegionChartId', {
//         chart: {
//             type: 'bar'
//         },
//         title: {
//             align: 'center',
//             text: 'Browser market shares. January, 2022'
//         },
//         accessibility: {
//             announceNewData: {
//                 enabled: true
//             }
//         },
//         xAxis: {
//             type: 'category'
//         },
//         yAxis: {
//             title: {
//                 text: 'Total percent market share'
//             }

//         },
//         plotOptions: {
//             series: {
//                 borderWidth: 0,
//                 dataLabels: {
//                     enabled: true,
//                     format: '{point.y:.1f}%'
//                 }
//             }
//         },

//         tooltip: {
//             headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
//             pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of total<br/>'
//         },

//         series: [
//             {
//                 name: 'Browsers',
//                 colorByPoint: true,
//                 data: [
//                     {
//                         name: 'Chrome',
//                         y: 63.06,
//                         drilldown: 'Chrome'
//                     },
//                     {
//                         name: 'Safari',
//                         y: 19.84,
//                         drilldown: 'Safari'
//                     },
//                     {
//                         name: 'Firefox',
//                         y: 4.18,
//                         drilldown: 'Firefox'
//                     },
//                     {
//                         name: 'Edge',
//                         y: 4.12,
//                         drilldown: 'Edge'
//                     },
//                     {
//                         name: 'Opera',
//                         y: 2.33,
//                         drilldown: 'Opera'
//                     },
//                     {
//                         name: 'Internet Explorer',
//                         y: 0.45,
//                         drilldown: 'Internet Explorer'
//                     },
//                     {
//                         name: 'Other',
//                         y: 1.582,
//                         drilldown: null
//                     }
//                 ]
//             }
//         ]
//     });

// }

document.addEventListener('DOMContentLoaded', function () {
    advancedAnalytics.style.display = 'none'
    getArtistDetails()
    pastAuctionDataSet('', 50)
    artistAnnualPerformanceChartMaker()
    yoyTotalSaleInUSDChartMaker()
    YoySellingCatAverageSellingPricePerCatChartMaker()
    // artistPerformancesByRegionChartMaker()

})
