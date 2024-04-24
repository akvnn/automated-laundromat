const goToBooking = (id, type, name) => {
  window.location.href = `/bookings/${type}/${id}/${name}`
}
const loadMachines = async () => {
  const response = await fetch('/getMachines')
  const machines = await response.json()
  const washers = machines.washers
  const dryers = machines.dryers
  const washers_container = document.getElementById('washers')
  const dryers_container = document.getElementById('dryers')
  washers_container.innerHTML = ''
  dryers_container.innerHTML = ''

  washers.forEach((washer) => {
    const item = document.createElement('div')
    item.setAttribute('id', washer.id)
    item.classList.add('item')
    const desc = document.createElement('p')
    desc.classList.add('item-desc')
    // const len = washer.id.length
    // desc.innerText =
    //   'Washer ' + washer.id[len - 1] + washer.id[len - 2] + washer.id[len - 3]
    desc.innerText = `Washer ${washer.name}`
    const status = document.createElement('p')
    status.classList.add('item-status')
    status.innerText = `Current Status: ${washer.status}`
    const btn = document.createElement('button')
    btn.classList.add('btn')
    btn.classList.add('item-btn')
    btn.innerText = 'Book'
    btn.addEventListener('click', async () => {
      goToBooking(washer.id, 'washer', washer.name)
    })
    item.appendChild(desc)
    item.appendChild(status)
    item.appendChild(btn)
    washers_container.appendChild(item)
  })
  dryers.forEach((dryer) => {
    const item = document.createElement('div')
    item.setAttribute('id', dryer.id)
    item.classList.add('item')
    const desc = document.createElement('p')
    desc.classList.add('item-desc')
    // const len = dryer.id.length
    // desc.innerText =
    // 'Dryer ' + dryer.id[len - 1] + dryer.id[len - 2] + dryer.id[len - 3]
    desc.innerText = `Dryer ${dryer.name}`
    const status = document.createElement('p')
    status.classList.add('item-status')
    status.innerText = `Current Status: ${dryer.status}`
    const btn = document.createElement('button')
    btn.classList.add('btn')
    btn.classList.add('item-btn')
    btn.innerText = 'Book'
    btn.addEventListener('click', async () => {
      goToBooking(dryer.id, 'dryer', dryer.name)
    })
    item.appendChild(desc)
    item.appendChild(status)
    item.appendChild(btn)
    dryers_container.appendChild(item)
  })
}
document.addEventListener('DOMContentLoaded', () => {
  loadMachines()
})
