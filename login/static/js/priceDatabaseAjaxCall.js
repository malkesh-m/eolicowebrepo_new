const frmpricefilter = document.querySelector('#frmpricefilter')

frmpricefilter.addEventListener('submit', function (event) {
    event.preventDefault()
    const txtartistname = event.target.elements['txtartistname']
    const txttitle = event.target.elements['txttitle']
    const medium1 = event.target.elements['medium1']
    const medium2 = event.target.elements['medium2']
    const medium3 = event.target.elements['medium3']
    const medium4 = event.target.elements['medium4']
    const medium5 = event.target.elements['medium5']
    const medium6 = event.target.elements['medium6']
    const sel_artwork_start = event.target.elements['sel_artwork_start']
    const sel_artwork_end = event.target.elements['sel_artwork_end']
    const dtauctionstartdate = event.target.elements['dtauctionstartdate']
    const sel_auctionhouses = event.target.elements['sel_auctionhouses']
    const txtauctionlocation = event.target.elements['txtauctionlocation']
    const soldCheckId = event.target.elements['soldCheckId']
    const yetToBeSoldCheckId = event.target.elements['yetToBeSoldCheckId']
    const boughtInCehckId = event.target.elements['boughtInCehckId']
    const withdrawnCheckId = event.target.elements['withdrawnCheckId']
    const txtsaletitle = event.target.elements['txtsaletitle']
    const txtsalecode = event.target.elements['txtsalecode']
    const dtauctionenddate = event.target.elements['dtauctionenddate']

    const formData = new FormData()
    formData.append('txtartistname', txtartistname.value)
    formData.append('txttitle', txttitle.value)
    formData.append('medium1', medium1.value)
    formData.append('medium2', medium2.value)
    formData.append('medium3', medium3.value)
    formData.append('medium4', medium4.value)
    formData.append('medium5', medium5.value)
    formData.append('medium6', medium6.value)
    formData.append('sel_artwork_start', sel_artwork_start.value)
    formData.append('sel_artwork_end', sel_artwork_end.value)
    formData.append('dtauctionstartdate', dtauctionstartdate.value)
    formData.append('sel_auctionhouses', sel_auctionhouses.value)
    formData.append('txtauctionlocation', txtauctionlocation.value)
    formData.append('soldCheckId', soldCheckId.value)
    formData.append('yetToBeSoldCheckId', yetToBeSoldCheckId.value)
    formData.append('boughtInCehckId', boughtInCehckId.value)
    formData.append('withdrawnCheckId', withdrawnCheckId.value)
    formData.append('txtsaletitle', txtsaletitle.value)
    formData.append('txtsalecode', txtsalecode.value)
    formData.append('dtauctionenddate', dtauctionenddate.value)

    console.log(formData)
})

document.addEventListener('DOMContentLoaded', function () {
    $('#sel_auctionhouses').select2({
        placeholder: 'Select Auction House', 
        ajax: {
            url: '/price/searchAuctionHouses/',
            type: "GET",
            dataType: 'json',
            data: function (data) {
                return {search: data.term}
            },
            processResults: function (response) {
                let data = $.map(response, function (dataObj) {
                    return {id: dataObj.cah_auction_house_name, text: dataObj.cah_auction_house_name}
                });
                return {results: data}
            },
        }
    });
})
