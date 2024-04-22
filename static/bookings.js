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
  console.log(data.booking_id)
}
const displaySchedule = async () => {
  let calendarEl = document.getElementById('calendar')
  //   let draggableEl = document.getElementById('external-events')
  const machine_type = window.location.pathname.split('/')[2]
  const machine_id = window.location.pathname.split('/')[3]
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
        processBooking(
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
  displaySchedule()
})
