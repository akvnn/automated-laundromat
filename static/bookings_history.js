const loadBookingHistory = async () => {
  const response = await fetch('/getBookings', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  const data = await response.json()
  if (response.status == 401) {
    window.location.href = '/login'
  }
  const bookingHistory = document.getElementById('bookings_history')
  if (data.length === 0) {
    bookingHistory.innerHTML = '<h3>No booking history Found</h3>'
  } else {
    bookingHistory.innerHTML = ''
    data.forEach((booking) => {
      const bookingCard = document.createElement('div')
      bookingCard.className = 'item'
      bookingCard.innerHTML = `
            <h5 class="item-desc
            ">${booking.machineType} ${booking.machineName}</h5>
            <p class="item-status">Start: ${booking.start}</p>
            <p class="item-status">End: ${booking.end}</p>
            <p class="item-status">Cycles: ${booking.cycles}</p>
            <p class="item-status">Status: ${booking.status}</p>
            <p class="item-status">Payment Method: ${booking.paymentMethod}</p>
        `
      bookingHistory.appendChild(bookingCard)
    })
  }
}
document.addEventListener('DOMContentLoaded', async () => {
  loadBookingHistory()
})
