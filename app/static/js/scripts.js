function showLoginForm(userType) {
  const accessChoiceDiv = document.getElementById('botoes-acesso');
  const loginForm = document.getElementById('form-login');
  const formTitle = document.getElementById('form-titulo');
  const formLabel = document.getElementById('form-label-usuario');
  const userTypeInput = document.getElementById('tipo');

  accessChoiceDiv.style.display = 'none';
  loginForm.style.display = 'flex';
  userTypeInput.value = userType;
  
  if (userType === 'Cliente') {
    formTitle.textContent = 'Login Cliente';
    formLabel.textContent = 'CPF:';
  } else {
    formTitle.textContent = 'Login Funcionário';
    formLabel.textContent = 'Matrícula:';
  }
}

function showAccessChoice() {
  const accessChoiceDiv = document.getElementById('botoes-acesso');
  const loginForm = document.getElementById('form-login');

  loginForm.style.display = 'none';
  accessChoiceDiv.style.display = 'block';
}
