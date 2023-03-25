Highcharts.setOptions({
    title: { style: { fontSize: "24px" },},
    subtitle: { style: { fontSize: "12px" },},
    lang: {
        thousandsSep: ','
    },
    credits: { enabled: false },
    
    xAxis: {
        crosshair: true,
        style: {
            fontSize: "12px;"
        },
        labels: {
            // rotation: 270,
            useHTML: true
        },
    },
    yAxis: {        
        labels: {            
            style: { fontSize: "12px" },
        }
    },
    exporting: {
        enabled: true,
        tableCaption: false,
    }
});

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
let artistBioStrData = ''

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
            artistBioStrData = body.fa_artist_bio
            artistBioId.innerHTML = `<p class="mb-1" id="artistDescPId">${artistBioStrData.slice(0,480)}....</p><a href="javascript:readMore('more')" id="readMoreId">Read More</a>`
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

function readMore(readMoreLess) {
    if (readMoreLess === 'more') {
        artistBioId.innerHTML = `<p class="mb-1" id="artistDescPId">${artistBioStrData}</p><a href="javascript:readMore('less')" id="readMoreId">Read Less</a>`
    }
    else {
        artistBioId.innerHTML = `<p class="mb-1" id="artistDescPId">${artistBioStrData.slice(0,480)}....</p><a href="javascript:readMore('more')" id="readMoreId">Read More</a>`
    }
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
    fetch(`/artist/artistAnnualPerformanceChart/?artistId=${artistId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let lotsYearArray = body.reverse().map(obj => obj.lotsYear)
            let numberOfLotsOfferedArray = body.map(obj => Number(obj.numberOfLotsOffered))
            let numberOfLotsSoldArray = body.map(obj => Number(obj.numberOfLotsSold))
            let numberOfLotsUnsoldArray = body.map(obj => Number(obj.numberOfLotsUnsold))
            let saleThroughRateArray = body.map(obj => Number(obj.saleThroughRate))
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
                    categories: lotsYearArray,
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Total Lots Count'
                    }
                },
                tooltip: {
                    // headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    // pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    //     '<td style="padding:0"><b>{point.y}</b></td></tr>',
                    // footerFormat: '</table>',
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0"> <br>Number of Lots </td>' +
                        '<td style="padding:0"><b>{point.y}</b></td></tr>',
                    footerFormat: '</table>',
                    shared: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.1,
                        borderWidth: 0
                    }
                },
                series: [{
                    name: 'Number of Lots Offered',
                    data: numberOfLotsOfferedArray,
            
                }, {
                    name: 'Number of Lots Sold',
                    data: numberOfLotsSoldArray
            
                }, {
                    name: 'Number of Lots Unsold',
                    data: numberOfLotsUnsoldArray
                }]
            });
        })
}

function yoyTotalSaleInUSDChartMaker() {
    fetch(`/artist/yoyTotalSaleAverageChart/?artistId=${artistId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let totalSaleAndYearObjArray = body.reverse().map(obj => {
                let data = {name: obj.saleYear, y: Math.round((Math.abs(Number(obj.totalSale)) / 1.0e+6)), avg: Math.round((Math.abs(Number(obj.saleAverage)) / 1.0e+6))}
                return data
            })
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
                    headerFormat: '<span style="font-size:11px"></span><br>',
                    pointFormat: '<span style="color:{point.color}">Average of {point.name} (USD) </span>: <b>{point.avg:.1f}M</b><br/>'
                },
        
                series: [
                    {
                        name: 'Years',
                        colorByPoint: false,
                        data: totalSaleAndYearObjArray
                    }
                ]
            })
        })
}

function YoySellingCatAverageSellingPricePerCatChartMaker() {
    fetch(`/artist/yoySellingCategoryChart/?artistId=${artistId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let lotsYearArray = body.reverse().map(obj => obj.lotsYear).filter((value, index, array) => array.indexOf(value) === index)
            let paintingsArray = []
            let workOnPaperArray = []
            let sculptuesArray = []
            let printsArray = []
            lotsYearArray.forEach(lotYear => {
                let data = body.find(obj => obj.lotsYear == lotYear && obj.lotsCategory === 'paintings')
                paintingsArray.push({y: data == undefined ? 0 : Math.round(Math.abs(Number(data.totalSalePrice) / 1.0e+6)), avg: data == undefined ? 0 : Math.round(Math.abs(Number(data.averageSalePrice) / 1.0e+6))})

                data = body.find(obj => obj.lotsYear == lotYear && obj.lotsCategory === 'works on paper')
                workOnPaperArray.push({y: data == undefined ? 0 : Math.round(Math.abs(Number(data.totalSalePrice) / 1.0e+6)), avg: data == undefined ? 0 : Math.round(Math.abs(Number(data.averageSalePrice) / 1.0e+6))})

                data = body.find(obj => obj.lotsYear == lotYear && obj.lotsCategory === 'sculptures')
                sculptuesArray.push({y: data == undefined ? 0 : Math.round(Math.abs(Number(data.totalSalePrice) / 1.0e+6)), avg: data == undefined ? 0 : Math.round(Math.abs(Number(data.averageSalePrice) / 1.0e+6))})

                data = body.find(obj => obj.lotsYear == lotYear && obj.lotsCategory === 'prints')
                printsArray.push({y: data == undefined ? 0 : Math.round(Math.abs(Number(data.totalSalePrice) / 1.0e+6)), avg: data == undefined ? 0 : Math.round(Math.abs(Number(data.averageSalePrice) / 1.0e+6))})
            })
            Highcharts.chart('YoySellingCatAverageSellingPricePerCatChartId', {
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'YOY Selling Categories & Average Selling Price Per Category'
                },
                xAxis: {
                    categories: lotsYearArray,
                    crosshair: true
                },
                yAxis: {
                    min: 0
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">Average of {series.name} (USD): </td>' +
                        '<td style="padding:0"><b>{point.avg:.1f} m</b></td></tr>',
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
                    data: paintingsArray
        
                }, {
                    name: 'Work on Paper',
                    data: workOnPaperArray
        
                }, {
                    name: 'Sculptures',
                    data: sculptuesArray
        
                }, {
                    name: 'Prints',
                    data: printsArray
        
                }]
            });
        })
}

async function getCountryCode(countryName) {
    let countryCode = await fetch(`https://restcountries.com/v3.1/name/${countryName}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => body[0].cca2)
    return countryCode
}

async function artistPerformancesByRegionChartMaker() {
    fetch(`/artist/artistPerformanceByCountryChart/?artistId=${artistId}&lotYear=2012`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let myDataArray = []
            body.forEach(obj => {
                let countryCode = getCountryCode(obj.lotsCountry).then(countryCode => countryCode)
                myDataArray.push({name: obj.lotsCountry, code: countryCode})
            })
            console.log(myDataArray)
        })
    // (async () => {

        const topology = await fetch(
            'https://code.highcharts.com/mapdata/custom/world.topo.json'
        ).then(response => response.json());
    
        function drawChart(data) {
            return Highcharts.mapChart('artistPerformanceByCountry', {
                chart: {
                    map: topology,
                    borderWidth: 1
                },
    
                colors: ['rgba(19,64,117,0.05)', 'rgba(19,64,117,0.2)', 'rgba(19,64,117,0.4)',
                    'rgba(19,64,117,0.5)', 'rgba(19,64,117,0.6)', 'rgba(19,64,117,0.8)', 'rgba(19,64,117,1)'],
    
                title: {
                    text: 'Population density by country (/km²)',
                    align: 'left'
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
                        text: 'Individuals per km²',
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
                        to: 3
                    }, {
                        from: 3,
                        to: 10
                    }, {
                        from: 10,
                        to: 30
                    }, {
                        from: 30,
                        to: 100
                    }, {
                        from: 100,
                        to: 300
                    }, {
                        from: 300,
                        to: 1000
                    }, {
                        from: 1000
                    }]
                },
    
                series: [{
                    data: data,
                    joinBy: ['iso-a2', 'code'],
                    animation: true,
                    name: 'Population density',
                    states: {
                        hover: {
                            color: '#a4edba'
                        }
                    },
                    tooltip: {
                        valueSuffix: '/km²'
                    },
                    shadow: false
                }]
            });
        }
    
        var d = [ {
            code: "US",
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
    advancedAnalytics.style.display = 'none'
    getArtistDetails()
    pastAuctionDataSet('', 50)
    artistAnnualPerformanceChartMaker()
    yoyTotalSaleInUSDChartMaker()
    YoySellingCatAverageSellingPricePerCatChartMaker()
    artistPerformancesByRegionChartMaker()

})
