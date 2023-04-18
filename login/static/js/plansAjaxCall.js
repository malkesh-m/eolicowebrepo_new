const basicDaily = document.querySelector('#basicDaily')
const basicMonthly = document.querySelector('#basicMonthly')
const basicYearly = document.querySelector('#basicYearly')
const premiumDaily = document.querySelector('#premiumDaily')
const premiumMonthly = document.querySelector('#premiumMonthly')
const premiumYearly = document.querySelector('#premiumYearly')

const basicSubcribeBtn = document.querySelector('#basicSubcribeBtn')
const premiumSubcribeBtn = document.querySelector('#premiumSubcribeBtn')

function subcribe() {
    let queryParam = ''
    if (basicDaily.checked) {
        queryParam = 'basicDaily'
    }
    else if (basicMonthly.checked) {
        queryParam = 'basicMonthly'
    }
    else if (basicYearly.checked) {
        queryParam = 'basicYearly'
    }
    else if (premiumDaily.checked) {
        queryParam = 'premiumDaily'
    }
    else if (premiumMonthly.checked) {
        queryParam = 'premiumMonthly'
    }
    else if (premiumYearly.checked) {
        queryParam = 'premiumYearly'
    }

    fetch(`/price/checkoutSession/?plans=${queryParam}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            const stripe = Stripe(body.publicKey)
            return stripe.redirectToCheckout({sessionId: body.sessionId})
        })
}

function checkedEvent(basicOrPremiunStr) {
    if (basicOrPremiunStr === 'basic') {
        basicSubcribeBtn.disabled = false
        premiumSubcribeBtn.disabled = true
    }
    else if (basicOrPremiunStr === 'premium') {
        premiumSubcribeBtn.disabled = false
        basicSubcribeBtn.disabled = true
    }
}

document.addEventListener('DOMContentLoaded', function () {
    basicSubcribeBtn.disabled = true
    premiumSubcribeBtn.disabled = true
})
