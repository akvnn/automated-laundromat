const loadBookingInfo = async () => {
  const booking_id = window.location.pathname.split('/')[2]
  const response = await fetch('/getBooking/' + booking_id, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  const data = await response.json()
  console.log(data)
  const booking_confirmation = document.getElementById('booking_confirmation')
  if (
    response.status == 404 ||
    response.status == 401 ||
    response.status == 400 ||
    data.length === 0
  ) {
    booking_confirmation.innerHTML =
      '<h3 class="confimration_title">No booking Found</h3>'
    return
  }
  const {
    machineType,
    machineName,
    start,
    end,
    cycles,
    status,
    paymentMethod,
  } = data
  booking_confirmation.innerHTML = `
        <h3 class="confimration_title">Your Booking is Confirmed!</h3>
        <p class="confirmation_p">${machineType} ${machineName} - ${cycles} cycle(s)</p>
        <p class="confirmation_p">Start: ${start}</p>
        <p class="confirmation_p">End: ${end}</p>
        <p class="confirmation_p">Status: ${status}</p>
        <p class="confirmation_p">Payment Method: ${paymentMethod}</p>
        `
}
document.addEventListener('DOMContentLoaded', async () => {
  loadBookingInfo()
})
