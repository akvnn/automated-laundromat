const loginbtn = document.getElementById('loginbtn')
const signupbtn = document.getElementById('signupbtn')

const handleLogin = async () => {
  const email = document.getElementById('email_login').value
  const password = document.getElementById('password_login').value
  if (email.trim() === '' || password.trim() === '') {
    alert('Please fill in all fields')
    return
  }
  if (!email.includes('@')) {
    alert('Invalid email')
    return
  }
  const response = await fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })
  const data = await response.json()
  if (response.status === 200) {
    localStorage.setItem('user_id', data.user_id)
    localStorage.setItem('user_email', data.user_email)
    localStorage.setItem('user_name', data.user_name)
    window.location.href = '/'
  } else {
    alert('Invalid email or password')
  }
}
const handleSignup = async () => {
  const email = document.getElementById('email_signup').value
  const password = document.getElementById('password_signup').value
  const name = document.getElementById('name_signup').value
  if (email.trim() === '' || password.trim() === '' || name.trim() === '') {
    alert('Please fill in all fields')
    return
  }
  if (!email.includes('@')) {
    alert('Invalid email')
    return
  }
  // check password > 8 characters and one number and one symbol
  if (password.length < 8) {
    alert('Password must be at least 8 characters')
    return
  }
  const hasNumber = /\d/
  if (!hasNumber.test(password)) {
    alert('Password must contain at least one number')
    return
  }
  const hasSymbol = /[^A-Za-z0-9]/
  if (!hasSymbol.test(password)) {
    alert('Password must contain at least one symbol')
    return
  }
  const response = await fetch('/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  })
  if (response.status === 200) {
    window.location.href = '/'
  } else {
    const data = await response.json()
    alert(data.message)
  }
}
loginbtn.addEventListener('click', (event) => {
  event.preventDefault()
  handleLogin()
})
signupbtn.addEventListener('click', (event) => {
  event.preventDefault()
  handleSignup()
})
