const accountSettingFormId = document.querySelector('#accountSettingFormId')
const firstNameInputEleId = document.querySelector('#firstNameInputEleId')
const lastNameInputEleId = document.querySelector('#lastNameInputEleId')
const emailInputEleId = document.querySelector('#emailInputEleId')
const addressInputEleId = document.querySelector('#addressInputEleId')
const countryInputEleId = document.querySelector('#countryInputEleId')
const stateInputId = document.querySelector('#stateInputId')
const zipCodeInputEleId = document.querySelector('#zipCodeInputEleId')
const phoneNoInputEleId = document.querySelector('#mobile_code')
const changePasswordFormId = document.querySelector('#changePasswordFormId')
const loginFaildAlert = document.querySelector('#loginFaildAlert')
let countriesStatesArray = []

function alertMsg (alertDivTag, alertDivInnerHtml, innerDivTagId) {
    alertDivTag.innerHTML = alertDivInnerHtml
    $(`#${innerDivTagId}`).delay(2000).slideUp(300, function() {
        $(this).alert('close');
        alertDivTag.innerHTML = ``
    })
}

function setState(statesArray) {
    stateInputId.disabled = false
    let htmlData = '<option></option>'
    statesArray.forEach(state => {
        htmlData += `<option value="${state.state_code}">${state.name}</option>`
    })
    stateInputId.innerHTML = htmlData
}

function getAllCountriesAndStates() {
    fetch('https://countriesnow.space/api/v0.1/countries/states', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            countriesStatesArray = body.data
            let htmlData = '<option></option>'
            body.data.forEach(country => {
                htmlData += `<option value="${country.iso3}">${country.name}</option>`
            })
            countryInputEleId.innerHTML = htmlData
        })
}

$(countryInputEleId).on('select2:select', function (e) {
    let statesArray = countriesStatesArray.find(obj => obj.iso3 === e.params.data.id).states
    setState(statesArray)
})

function getUserData() {
    fetch('/login/getUserData/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            firstNameInputEleId.value = body.firstName
            lastNameInputEleId.value = body.lastName
            emailInputEleId.value = body.login_email
            addressInputEleId.value = body.address
            if (body.country) {
                $(`#countryInputEleId`).val(body.country).trigger('change')
                let statesArray = countriesStatesArray.find(obj => obj.iso3 === body.country).states
                setState(statesArray)
            }
            if (body.state) {
                $('#stateInputId').val(body.state).trigger('change')
            }
            zipCodeInputEleId.value = body.zipCode
            phoneNoInputEleId.value = body.phoneNo
            document.querySelector('#accountSettingFormBtnId').disabled = false
        })
}

async function setData() {
    await getAllCountriesAndStates()
    getUserData()
}

document.addEventListener('DOMContentLoaded', function () {
    $(countryInputEleId).select2()
    $(stateInputId).select2()
    setData()
})

accountSettingFormId.addEventListener('submit', function(event) {
    event.preventDefault()
    const formData = new FormData()
    formData.append('csrfmiddlewaretoken', event.target.elements['csrfmiddlewaretoken'].value)
    console.log(countryInputEleId.value)
    if (firstNameInputEleId.value) {
        formData.append('firstName', firstNameInputEleId.value)
    }
    if (lastNameInputEleId.value) {
        formData.append('lastName', lastNameInputEleId.value)
    }
    if (emailInputEleId.value) {
        formData.append('loginEmail', emailInputEleId.value)
    }
    if (addressInputEleId.value) {
        formData.append('address', addressInputEleId.value)
    }
    if (countryInputEleId.value) {
        formData.append('country', countryInputEleId.value)
    }
    if (stateInputId.value) {
        formData.append('state', stateInputId.value)
    }
    if (zipCodeInputEleId.value) {
        formData.append('zipCode', zipCodeInputEleId.value)
    }
    if (phoneNoInputEleId.value) {
        formData.append('phoneNo', phoneNoInputEleId.value)
    }

    fetch('/login/getUserData/', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(body => {
            let successOrFail = ''
            if (body.success) {
                successOrFail = 'success'
            }
            else {
                successOrFail = 'danger'
            }
            loginFaildAlertInnerHtml = `<div class="alert alert-${successOrFail} alert-dismissible fade show" role="alert" id="loginFaildAlertMsg"><strong>Account Settings</strong> ${body.msg}.<button type="button" class="btn-close p-0 bg-transparent text-${successOrFail}" data-bs-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>`
            alertMsg(loginFaildAlert, loginFaildAlertInnerHtml, 'loginFaildAlertMsg')
            accountSettingFormId.reset()
            setData()
        })
})

changePasswordFormId.addEventListener('submit', function(event) {
    event.preventDefault()
    const currentPaswordInputId = document.querySelector('#currentPaswordInputId')
    const newPaswordInputId = document.querySelector('#newPaswordInputId')
    const newConfirmPaswordInputId = document.querySelector('#newConfirmPaswordInputId')
    if (newConfirmPaswordInputId.value !== newPaswordInputId.value) {
        alert('new password & confirm password must be same')
        changePasswordFormId.reset()
    }
    else if (newPaswordInputId.value === currentPaswordInputId.value) {
        alert('current password & new password can not be same')
        changePasswordFormId.reset()
    }
    else {
        const formData = new FormData()
        formData.append('csrfmiddlewaretoken', event.target.elements['csrfmiddlewaretoken'].value)
        formData.append('currentPassword', currentPaswordInputId.value)
        formData.append('newPassword', newPaswordInputId.value)
        formData.append('confirmPassword', newConfirmPaswordInputId.value)
        fetch('/login/changePassword/', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(body => {
                let successOrFail = ''
                if (body.success) {
                    successOrFail = 'success'
                }
                else {
                    successOrFail = 'danger'
                }
                loginFaildAlertInnerHtml = `<div class="alert alert-${successOrFail} alert-dismissible fade show" role="alert" id="loginFaildAlertMsg"><strong>Change Password</strong> ${body.msg}.<button type="button" class="btn-close bg-transparent text-${successOrFail}" data-bs-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>`
                alertMsg(loginFaildAlert, loginFaildAlertInnerHtml, 'loginFaildAlertMsg')
                changePasswordFormId.reset()
            })
    }
})
