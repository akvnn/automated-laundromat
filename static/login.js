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
  if (response.status === 200) {
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
  const response = await fetch('/signup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  })
  print(response.status)
  if (response.status === 200) {
    window.location.href = '/'
  } else {
    alert('Email already exists')
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
