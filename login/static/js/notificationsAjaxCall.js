const myNotificationsLogsDivId = document.querySelector('#myNotificationsLogsDivId')

function getMyNotificationLogs(start) {
    fetch(`/login/getMyNotificationLogs/?start=${start}&limit=10`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(notificationData => {
                htmlData += `<div class="notifications-box mb-4 notificationLogsCls">
                                <div class="row">
                                    <div class="col-12">
                                        <div class="row align-items-center">
                                            <div class="col-auto">
                                                <div class="notifications-img">
                                                    <img src="https://f000.backblazeb2.com/file/fineart-images/${notificationData.fa_artist_image}" />
                                                </div>
                                            </div>
                                            <div class="col-md-6 col-xl-8 my-4 my-md-0">
                                                <div class="notifications-content">
                                                    <div>
                                                        <h3 class="mb-1">${notificationData.fa_artist_name}</h3>
                                                    </div>
                                                    <p>${notificationData.lotsCounts} Upcoming Lots</p>
                                                </div>
                                            </div>
                                            <div class="col text-md-end">
                                                <a class="btn btn-login btn-round ml-0 px-4" style="text-decoration: none;" href="/auction/showauction/?aucid=${notificationData.auctionId}">View Details</a>
                                                <span class="d-block mt-4">${notificationData.createdDate}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>`
            })
            if (body.length === 10) {
                let start = document.querySelectorAll('.notificationLogsCls').length + body.length
                htmlData += `<div class="col-12 text-center mt-4" id="relatedArtworkViewMoreId">
                                <button type="button" class="btn btn-login btn-round py-2" onclick="getMyNotificationLogs(${start})">View More</button>
                            </div>`
            }
            myNotificationsLogsDivId.innerHTML = htmlData
            
        })
}

document.addEventListener('DOMContentLoaded', function () {
    getMyNotificationLogs(0)
})