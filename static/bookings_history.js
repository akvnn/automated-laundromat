const loadBookingHistory = async () => {
  const response = await fetch('/getBookings', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  const data = await response.json()

  const machineResponse = await fetch('/getMachines', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  const machines = await machineResponse.json()
  const machineMap = {}
  machines['washers'].forEach((machine) => {
    machineMap[machine.id] = machine
  })
  machines['dryers'].forEach((machine) => {
    machineMap[machine.id] = machine
  })

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
            <p class="item-status">Machine Status: ${machineMap[booking.machineId].status}</p>
            <p class="item-status">Payment Status: ${booking.status}</p>
            <p class="item-status">Payment Method: ${booking.paymentMethod}</p>
        `
        const currentTime = new Date().getTime()
        
        // Add unlock button if the time >= start time and <= (end time - start time) / 2
        if (currentTime >= new Date(booking.start).getTime()
            && currentTime <= new Date(booking.end).getTime()
          ){
          const unlockButton = document.createElement('button')
          unlockButton.className = 'btn btn-primary'
          unlockButton.innerText = machineMap[booking.machineId].status === 'locked' ? 'Unlock' : 'Lock'
          unlockButton.addEventListener('click', () => {
            lockUnlockMachine(machineMap[booking.machineId], booking, bookingCard)
          })
          bookingCard.appendChild(unlockButton)
          const video = document.createElement('video')
          video.setAttribute('width', '320')
          video.setAttribute('height', '240')
          video.setAttribute('muted', '')
          video.setAttribute('autoplay', '')
          video.setAttribute('loop', '')
          video.setAttribute('playsinline', '')
          video.src = `/static/videos/machine.mov`
          bookingCard.appendChild(video)
          setTimeout(() => {
            video.play()
          }, 2500)
        }
        bookingCard.setAttribute('booking-id', booking.booking_id)

      bookingHistory.appendChild(bookingCard)
    })
  }
}

const lockUnlockMachine = async (machine, booking, bookingCard) => {
  await fetch('/setMachineStatus', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      machineId: machine.id,
      status: machine.status === 'locked' ? 'unlocked' : 'locked',
    }),
  })
  await loadBookingHistory()
  booking.previouslyLocked = true
  alert(`Machine ${machine.name} is now ${machine.status === 'locked' ? 'unlocked' : 'locked'}`)
}

document.addEventListener('DOMContentLoaded', async () => {
  loadBookingHistory()
})
