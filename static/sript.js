// VOZ CIDADÃ - JAVASCRIPT
// Sistema de participação comunitária 

// 1. INICIALIZAÇÃO

document.addEventListener("DOMContentLoaded", function () {

    console.log("Voz Cidadã iniciado com sucesso!");

    iniciarMensagens();
    iniciarFormularios();
    iniciarFiltros();
    iniciarConfirmacaoExclusao();
    iniciarAnimacoes();
    iniciarNavegacao();

});


// 2. MENSAGENS DO SISTEMA

// Faz as mensagens de sucesso e erro desaparecerem
// automaticamente depois de 5 segundos.

function iniciarMensagens() {

    const mensagens = document.querySelectorAll(".mensagem");

    mensagens.forEach(function (mensagem) {

        setTimeout(function () {

            mensagem.style.transition = "opacity 0.4s ease";
            mensagem.style.opacity = "0";

            setTimeout(function () {
                mensagem.remove();
            }, 400);

        }, 5000);

    });

}


// 3. VALIDAÇÃO DOS FORMULÁRIOS

function iniciarFormularios() {

    const formularios = document.querySelectorAll(".formulario");

    formularios.forEach(function (formulario) {

        formulario.addEventListener("submit", function (evento) {

            const campos = formulario.querySelectorAll(
                "input[required], textarea[required], select[required]"
            );

            let formularioValido = true;

            campos.forEach(function (campo) {

                if (campo.value.trim() === "") {

                    formularioValido = false;

                    campo.style.borderColor = "#d83a3a";

                } else {

                    campo.style.borderColor = "";

                }

            });

            if (!formularioValido) {

                evento.preventDefault();

                alert("Por favor, preencha todos os campos obrigatórios.");

                return;

            }

            // Verifica o tamanho mínimo da senha no cadastro

            const campoSenha = formulario.querySelector("#senha");
            const campoNome = formulario.querySelector("#nome");

            if (campoSenha && campoNome) {

                if (campoSenha.value.length < 6) {

                    evento.preventDefault();

                    alert("A senha deve conter pelo menos 6 caracteres.");

                    campoSenha.focus();

                    return;

                }

            }

        });

    });

}


// 4. FILTROS DAS MANIFESTAÇÕES

// Mantém os filtros selecionados depois de uma pesquisa.

function iniciarFiltros() {

    const formularioFiltros = document.querySelector(".filtros");

    if (!formularioFiltros) {
        return;
    }

    const parametros = new URLSearchParams(window.location.search);

    const categoria = formularioFiltros.querySelector("#categoria");
    const status = formularioFiltros.querySelector("#status");
    const localizacao = formularioFiltros.querySelector("#localizacao");

    if (categoria && parametros.has("categoria")) {

        categoria.value = parametros.get("categoria");

    }

    if (status && parametros.has("status")) {

        status.value = parametros.get("status");

    }

    if (localizacao && parametros.has("localizacao")) {

        localizacao.value = parametros.get("localizacao");

    }

}


// 5. CONFIRMAÇÃO DE EXCLUSÃO

// Impede exclusões acidentais.
// Funciona com formulários de exclusão que ainda não possuem
// confirmação diretamente no HTML.

function iniciarConfirmacaoExclusao() {

    const formularios = document.querySelectorAll(
        'form[action*="/excluir"]'
    );

    formularios.forEach(function (formulario) {

        formulario.addEventListener("submit", function (evento) {

            const botao = formulario.querySelector(
                'button[type="submit"]'
            );

            // Se o botão já possui confirmação no HTML,
            // não adicionamos outra confirmação.

            if (botao && botao.hasAttribute("onclick")) {
                return;
            }

            const confirmado = confirm(
                "Tem certeza que deseja excluir esta manifestação? Esta ação não poderá ser desfeita."
            );

            if (!confirmado) {

                evento.preventDefault();

            }

        });

    });

}


// 6. ANIMAÇÃO DOS CARDS

// Aplica uma animação suave aos cards quando aparecem na tela.

function iniciarAnimacoes() {

    const elementos = document.querySelectorAll(
        ".passo, .categoria-card, .manifestacao-card, .admin-card"
    );

    if (!("IntersectionObserver" in window)) {
        return;
    }

    const observador = new IntersectionObserver(function (entradas) {

        entradas.forEach(function (entrada) {

            if (entrada.isIntersecting) {

                entrada.target.style.opacity = "1";
                entrada.target.style.transform = "translateY(0)";

                observador.unobserve(entrada.target);

            }

        });

    }, {
        threshold: 0.1
    });

    elementos.forEach(function (elemento) {

        elemento.style.opacity = "0";
        elemento.style.transform = "translateY(15px)";

        elemento.style.transition =
            "opacity 0.5s ease, transform 0.5s ease";

        observador.observe(elemento);

    });

}


// 7. NAVEGAÇÃO

// Destaca o link da página atual no menu.

function iniciarNavegacao() {

    const links = document.querySelectorAll(".menu a");

    const paginaAtual = window.location.pathname;

    links.forEach(function (link) {

        const endereco = new URL(link.href).pathname;

        if (endereco === paginaAtual) {

            link.classList.add("menu-ativo");

        }

    });

}


// 8. CONTADOR DE CARACTERES

// Exibe a quantidade de caracteres digitados na descrição
// das manifestações.

const campoDescricao = document.querySelector("#descricao");

if (campoDescricao) {

    const contador = document.createElement("small");

    contador.className = "contador-caracteres";

    contador.style.color = "#66736c";
    contador.style.fontSize = "12px";
    contador.style.marginTop = "5px";

    campoDescricao.insertAdjacentElement("afterend", contador);

    function atualizarContador() {

        const quantidade = campoDescricao.value.length;

        contador.textContent = quantidade + " caracteres digitados";

    }

    campoDescricao.addEventListener("input", atualizarContador);

    atualizarContador();

}


// 9. CONFIRMAÇÃO DE ATUALIZAÇÃO DE STATUS

// Exibe uma confirmação antes de alterar o status
// de uma manifestação no painel administrativo.

const formulariosStatus = document.querySelectorAll(".form-status");

formulariosStatus.forEach(function (formulario) {

    formulario.addEventListener("submit", function (evento) {

        const confirmado = confirm(
            "Deseja realmente atualizar o status desta manifestação?"
        );

        if (!confirmado) {

            evento.preventDefault();

        }

    });

});


// 10. EFEITO NO CABEÇALHO

// Adiciona uma sombra mais forte quando a página é rolada.

const cabecalho = document.querySelector(".cabecalho");

if (cabecalho) {

    window.addEventListener("scroll", function () {

        if (window.scrollY > 20) {

            cabecalho.style.boxShadow =
                "0 6px 25px rgba(0, 0, 0, 0.08)";

        } else {

            cabecalho.style.boxShadow =
                "0 4px 20px rgba(0, 0, 0, 0.03)";

        }

    });

}