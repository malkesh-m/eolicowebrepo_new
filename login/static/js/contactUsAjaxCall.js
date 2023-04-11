const contactUsFormId = document.querySelector('#contactUsFormId')
const contacUsAlert = document.querySelector('#contactUsAlert')
const contactUsSendMessageBtnId = document.querySelector('#contactUsSendMessageBtnId')
let passwordShowHideFlag = false

function alertMsg (alertDivTag, alertDivInnerHtml, innerDivTagId) {
    alertDivTag.innerHTML = alertDivInnerHtml
    $(`#${innerDivTagId}`).delay(2000).slideUp(300, function() {
        $(this).alert('close');
        alertDivTag.innerHTML = ``
    })
}

contactUsFormId.addEventListener('submit', function (event) {
    event.preventDefault()
    const contactUsNameId = event.target.elements['contactUsNameId']
    const contactUsEmailId = event.target.elements['contactUsEmailId']
    const contactUsSubjectId = event.target.elements['contactUsSubjectId']
    const contactUsMessageId = event.target.elements['contactUsMessageId']
    const csrfmiddlewaretoken = event.target.elements['csrfmiddlewaretoken']
    contactUsSendMessageBtnId.value = 'Please wait'
    const formData = new FormData()
    formData.append('csrfmiddlewaretoken', csrfmiddlewaretoken.value)
    formData.append('contactUsName', contactUsNameId.value)
    formData.append('contactUsEmail', contactUsEmailId.value)
    formData.append('contactUsSubject', contactUsSubjectId.value)
    formData.append('contactUsMessage', contactUsMessageId.value)

    fetch(`/login/contactUs/`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ``
            if (body.success === true) {
                contactUsFormId.reset()
                htmlData = `<div class="alert alert-success alert-dismissible fade show" role="alert" id="contactUsAlertMsg"><strong>Email Sent Successfully</strong></div>`
            }
            else {
                htmlData = `<div class="alert alert-danger alert-dismissible fade show" role="alert" id="contactUsAlertMsg"><strong>Email Sending Failed</strong> please try again</div>`
            }
            alertMsg(contacUsAlert, htmlData, 'contactUsAlertMsg')
            contactUsSendMessageBtnId.value = 'Send Message'
        })

})

function passwordShowHide(elementId) {
    const passwordEle = document.querySelector(elementId)
    if (passwordShowHideFlag) {
        passwordEle.type = 'text'
        passwordShowHideFlag = false
    }
    else {
        passwordEle.type = 'password'
        passwordShowHideFlag = true
    }
}

document.addEventListener('DOMContentLoaded', function () {

})
