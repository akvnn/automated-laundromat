const processBooking = async (
  machine_id,
  machine_type,
  start,
  end,
  title,
  userId
) => {
  const response = await fetch('/bookMachine', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      machineId: machine_id,
      start: start,
      end: end,
      title: title,
      userId: userId,
    }),
  })
  const data = await response.json()
  return data.booking_id
}
let booking_data = {}
const proceedToPayment = async (
  machine_name,
  machine_id,
  machine_type,
  start,
  end,
  title,
  userId
) => {
  booking_data = {
    machine_name,
    machine_id,
    machine_type,
    start,
    end,
    title,
    userId,
  }
  localStorage.setItem('booking_data', JSON.stringify(booking_data))
  window.location.href = `/payment`
}

const payment_method_btn = document.getElementById('payment_method_btn')
const phantom_label = document.getElementById('phantom_label')
if (payment_method_btn !== null) {
  window.addEventListener('DOMContentLoaded', () => {
    // display booking info
    const booking_info = document.getElementById('booking_info')
    const {
      machine_name,
      machine_id,
      machine_type,
      start,
      end,
      title,
      userId,
    } = JSON.parse(localStorage.getItem('booking_data'))
    booking_info.innerHTML = `
    <p class="payment_p">${machine_type} ${machine_name}</p>
    <p class="payment_p">${
      start.split('T')[0] + ' ' + start.split('T')[1].split('+')[0]
    } - ${end.split('T')[0] + ' ' + end.split('T')[1].split('+')[0]}</p>`
    // check if phantom wallet is installed
    if (window.phantom?.solana?.isPhantom) {
      phantom_label.innerText = 'Phantom - Detected'
    }
  })

  payment_method_btn.addEventListener('click', async (e) => {
    e.preventDefault()
    const selected_payment_method = document.querySelector(
      'input[name="payment_method"]:checked'
    ).value
    if (selected_payment_method === 'phantom') {
      if (!window.phantom?.solana?.isPhantom) {
        alert('Please install Phantom Wallet')
        return
      }
      const provider = window.phantom?.solana // see "Detecting the Provider"
      try {
        const resp = await provider.connect()
        console.log(resp.publicKey.toString())
        // 26qv4GCcx98RihuK3c4T6ozB3J7L6VwCuFVc7Ta2A3Uo
        // make a transaction using phantom
        const connection = new solanaWeb3.Connection(
          solanaWeb3.clusterApiUrl('devnet')
        )
        //does not work
        const transaction = new solanaWeb3.Transaction().add(
          solanaWeb3.SystemProgram.transfer({
            fromPubkey: resp.publicKey,
            toPubkey: new solanaWeb3.PublicKey(
              'JAiGi1CXYZRXZsbTdCEpTaXuAX7Apc95HLQYeaKdwB7Z'
            ),
            lamports: 10000,
          })
        )
        // Set recent blockhash
        transaction.recentBlockhash = (
          await connection.getRecentBlockhash()
        ).blockhash

        // Set fee payer
        transaction.feePayer = provider.publicKey
        // Request user to sign and send the transaction via Phantom
        let signedTransaction = await provider.signTransaction(transaction)
        let signature = await connection.sendRawTransaction(
          signedTransaction.serialize()
        )

        // Optionally, await confirmation
        await connection.confirmTransaction(signature)
      } catch (err) {
        console.log(err)

        // { code: 4001, message: 'User rejected the request.' }
      }
    } else if (selected_payment_method === 'card') {
      response = await fetch('/payment', {
        method: 'POST',
        body: JSON.stringify({})
      })

      if (!response.ok) {
        throw new Error('failed to create stripe session')
      }

      const { redirectUrl } = await response.json()
      location.assign(redirectUrl)
    } else if (selected_payment_method === 'coin') {
      location.assign('/coin');
    }
  })
}
const displaySchedule = async () => {
  let calendarEl = document.getElementById('calendar')
  //   let draggableEl = document.getElementById('external-events')
  const machine_type = window.location.pathname.split('/')[2]
  const machine_id = window.location.pathname.split('/')[3]
  const machine_name = window.location.pathname.split('/')[4]
  let calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    droppable: true,
    editable: true,
    selectable: true,
    allDaySlot: false,
    slotDuration: '00:30:00', // 1 slot = 1 cycle
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'timeGridWeek,timeGridDay',
    },
    events: [
      // {
      // title: 'All Day Event',
      //start: '2024-04-21',
      //},
    ],
    eventOverlap: false,
    select: function (info) {
      // is called when a user selects a time slot
      let duration = moment.duration(
        moment(info.endStr).diff(moment(info.startStr))
      )
      if (duration.asHours() > 1) {
        console.log(duration.asHours())
        alert('Events cannot be longer than 1 hour')
        calendar.unselect()
        return
      }
      let title = prompt('Please enter a title for your event')
      // generate ObjectID
      const userId = '60b9b3b3b3b3b3b3b3b3b3b3'
      if (title) {
        calendar.addEvent({
          title: title,
          start: info.startStr,
          end: info.endStr,
          createdByUser: userId,
        })
        // make api call to save event
        proceedToPayment(
          machine_name,
          machine_id,
          machine_type,
          info.startStr,
          info.endStr,
          title,
          userId
        )
      }
      calendar.unselect()
    },
    eventAllow: function (dropInfo, draggedEvent) {
      // only allow dragging and resizing if the event was created by the user
      return draggedEvent.extendedProps.createdByUser
    },
  })

  calendar.render()
  const response = await fetch('/machineBookings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ machineId: machine_id }),
  })
  const data = await response.json()
  data.forEach((booking) => {
    let event = {
      title: booking.title,
      start: booking.start,
      end: booking.end,
      createdByUser: booking.userId,
    }
    calendar.addEvent(event)
  })
}
document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.split('/')[1] === 'bookings') {
    displaySchedule()
  }
})
