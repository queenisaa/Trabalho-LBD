// static/js/abertura_conta.js

function toggleAccountFields() {
    const accountType = document.getElementById('tipo_conta').value;
    
    // Esconde todos os campos específicos
    document.getElementById('campos_cc').style.display = 'none';
    document.getElementById('campos_cp').style.display = 'none';
    document.getElementById('campos_ci').style.display = 'none';

    // Mostra os campos relevantes para o tipo de conta selecionado
    if (accountType === 'Corrente') {
        document.getElementById('campos_cc').style.display = 'block';
    } else if (accountType === 'Poupanca') {
        document.getElementById('campos_cp').style.display = 'block';
    } else if (accountType === 'Investimento') {
        document.getElementById('campos_ci').style.display = 'block';
    }
}

// Garante que a função rode quando a página carregar pela primeira vez
// para o caso de o navegador pré-preencher o formulário
document.addEventListener('DOMContentLoaded', toggleAccountFields);
