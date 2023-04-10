const contactUsFormId = document.querySelector('#contactUsFormId')

contactUsFormId.addEventListener('submit', function (event) {
    event.preventDefault()
    const contactUsNameId = event.target.elements['contactUsNameId']
    const contactUsEmailId = event.target.elements['contactUsEmailId']
    const contactUsSubjectId = event.target.elements['contactUsSubjectId']
    const contactUsMessageId = event.target.elements['contactUsMessageId']
    const csrfmiddlewaretoken = event.target.elements['csrfmiddlewaretoken']

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
        .then(body => body)

})

document.addEventListener('DOMContentLoaded', function () {

})
