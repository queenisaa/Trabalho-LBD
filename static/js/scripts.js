// static/js/scripts.js

/**
 * Exibe o formulário de login para Cliente ou Funcionário.
 * 
 * @param {string} tipo - "Cliente" ou "Funcionario"
 */
function showLoginForm(tipo) {
  const body = document.body;
  const leftSide = document.querySelector(".left-side");
  const form = document.getElementById("form-login");
  const botaoCliente = document.getElementById("botaoCliente");
  const botaoFuncionario = document.getElementById("botaoFuncionario");

  // Adiciona classes para alterar o layout
  body.classList.add("login-layout");
  leftSide.classList.add("small-left");

  // Atualiza conteúdo do lado esquerdo (título + mensagem)
  const tituloEsquerda = tipo === "Cliente" 
    ? "Cliente" 
    : "Funcionário";
  const mensagemEsquerda = tipo === "Cliente"
    ? "Entre com seus dados e acesse sua conta como cliente."
    : "Faça login para acessar o sistema como funcionário.";

  leftSide.innerHTML = `
    <div class="welcome-box">
      <h1>${tituloEsquerda}</h1>
      <p>${mensagemEsquerda}</p>
    </div>
  `;

  // Atualiza cabeçalho e hidden input do formulário
  document.getElementById("form-titulo").textContent = `Login ${tituloEsquerda}`;
  document.getElementById("tipo").value = tituloEsquerda;

  // Esconde botões de seleção e exibe o formulário
  botaoCliente.style.display = "none";
  botaoFuncionario.style.display = "none";
  form.style.display = "flex";
}

/**
 * Volta ao estado inicial (tela com botões de acesso), quando clica na logo.
 */
document.addEventListener("DOMContentLoaded", () => {
  const logoLink = document.querySelector(".logo-link");
  logoLink.addEventListener("click", (e) => {
    e.preventDefault(); // impede comportamento padrão do <a>

    const body = document.body;
    const leftSide = document.querySelector(".left-side");
    const form = document.getElementById("form-login");
    const botaoCliente = document.getElementById("botaoCliente");
    const botaoFuncionario = document.getElementById("botaoFuncionario");

    // Remove classes de layout de login
    body.classList.remove("login-layout");
    leftSide.classList.remove("small-left");

    // Restaura conteúdo original do lado esquerdo
    leftSide.innerHTML = `
      <div class="welcome-box">
        <h1>Bem-vindo!</h1>
        <p>Acesse o sistema de forma segura com autenticação criptografada.</p>
      </div>
    `;

    // Exibe novamente os botões de acesso e esconde o formulário
    botaoCliente.style.display = "inline-block";
    botaoFuncionario.style.display = "inline-block";
    form.style.display = "none";
  });
});
