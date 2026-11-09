from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime


app = Flask(__name__)

# Configurações
app.config["SECRET_KEY"] = "voz-cidada-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voz_cidada.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# MODELOS DO BANCO DE DADOS

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

    tipo = db.Column(
        db.String(20),
        nullable=False,
        default="morador"
    )

    data_cadastro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    manifestacoes = db.relationship(
        "Manifestacao",
        backref="usuario",
        lazy=True
    )


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    manifestacoes = db.relationship(
        "Manifestacao",
        backref="categoria",
        lazy=True
    )


class Manifestacao(db.Model):
    __tablename__ = "manifestacoes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=False
    )

    localizacao = db.Column(
        db.String(150),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Pendente"
    )

    data_registro = db.Column(
        db.DateTime,
        default=datetime.now
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False
    )


# FUNÇÕES AUXILIARES

def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar_login(*args, **kwargs):

        if "usuario_id" not in session:
            flash("Você precisa fazer login para acessar esta página.", "erro")
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return verificar_login


def admin_obrigatorio(funcao):
    @wraps(funcao)
    def verificar_admin(*args, **kwargs):

        if "usuario_id" not in session:
            flash("Você precisa fazer login.", "erro")
            return redirect(url_for("login"))

        if session.get("usuario_tipo") != "admin":
            flash("Você não tem permissão para acessar esta página.", "erro")
            return redirect(url_for("inicio"))

        return funcao(*args, **kwargs)

    return verificar_admin


# ROTAS PRINCIPAIS

@app.route("/")
def inicio():

    total_manifestacoes = Manifestacao.query.count()

    total_resolvidas = Manifestacao.query.filter_by(
        status="Resolvido"
    ).count()

    total_pendentes = Manifestacao.query.filter_by(
        status="Pendente"
    ).count()

    return render_template(
        "index.html",
        total_manifestacoes=total_manifestacoes,
        total_resolvidas=total_resolvidas,
        total_pendentes=total_pendentes
    )


# CADASTRO

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario_existente = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario_existente:
            flash("Este e-mail já está cadastrado.", "erro")
            return redirect(url_for("cadastro"))

        senha_criptografada = generate_password_hash(senha)

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha_criptografada,
            tipo="morador"
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "sucesso")

        return redirect(url_for("login"))

    return render_template("cadastro.html")


# LOGIN

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario and check_password_hash(
            usuario.senha,
            senha
        ):

            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            session["usuario_tipo"] = usuario.tipo

            flash(
                f"Bem-vindo, {usuario.nome}!",
                "sucesso"
            )

            return redirect(url_for("inicio"))

        flash("E-mail ou senha incorretos.", "erro")

    return render_template("login.html")


# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    flash("Você saiu da sua conta.", "sucesso")

    return redirect(url_for("inicio"))


# LISTAR MANIFESTAÇÕES

@app.route("/manifestacoes")
def listar_manifestacoes():

    categoria_id = request.args.get("categoria")
    status = request.args.get("status")
    localizacao = request.args.get("localizacao")

    consulta = Manifestacao.query

    if categoria_id:
        consulta = consulta.filter_by(
            categoria_id=categoria_id
        )

    if status:
        consulta = consulta.filter_by(
            status=status
        )

    if localizacao:
        consulta = consulta.filter(
            Manifestacao.localizacao.contains(localizacao)
        )

    manifestacoes = consulta.order_by(
        Manifestacao.data_registro.desc()
    ).all()

    categorias = Categoria.query.order_by(
        Categoria.nome
    ).all()

    return render_template(
        "manifestacoes.html",
        manifestacoes=manifestacoes,
        categorias=categorias
    )


# CADASTRAR MANIFESTAÇÃO

@app.route("/manifestacao/nova", methods=["GET", "POST"])
@login_obrigatorio
def nova_manifestacao():

    categorias = Categoria.query.order_by(
        Categoria.nome
    ).all()

    if request.method == "POST":

        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        localizacao = request.form.get("localizacao")
        categoria_id = request.form.get("categoria_id")

        nova_manifestacao = Manifestacao(
            titulo=titulo,
            descricao=descricao,
            localizacao=localizacao,
            categoria_id=categoria_id,
            usuario_id=session["usuario_id"],
            status="Pendente"
        )

        db.session.add(nova_manifestacao)
        db.session.commit()

        flash(
            "Manifestação registrada com sucesso!",
            "sucesso"
        )

        return redirect(url_for("listar_manifestacoes"))

    return render_template(
        "nova_manifestacao.html",
        categorias=categorias
    )


# DETALHES DA MANIFESTAÇÃO

@app.route("/manifestacao/<int:id>")
def detalhes_manifestacao(id):

    manifestacao = Manifestacao.query.get_or_404(id)

    return render_template(
        "detalhes_manifestacao.html",
        manifestacao=manifestacao
    )


# EDITAR MANIFESTAÇÃO

@app.route(
    "/manifestacao/<int:id>/editar",
    methods=["GET", "POST"]
)
@login_obrigatorio
def editar_manifestacao(id):

    manifestacao = Manifestacao.query.get_or_404(id)

    # Moradores só podem editar as próprias manifestações
    if (
        manifestacao.usuario_id != session["usuario_id"]
        and session.get("usuario_tipo") != "admin"
    ):

        flash(
            "Você não tem permissão para editar esta manifestação.",
            "erro"
        )

        return redirect(
            url_for("listar_manifestacoes")
        )

    categorias = Categoria.query.order_by(
        Categoria.nome
    ).all()

    if request.method == "POST":

        manifestacao.titulo = request.form.get("titulo")
        manifestacao.descricao = request.form.get("descricao")
        manifestacao.localizacao = request.form.get("localizacao")
        manifestacao.categoria_id = request.form.get("categoria_id")

        db.session.commit()

        flash(
            "Manifestação atualizada com sucesso!",
            "sucesso"
        )

        return redirect(
            url_for(
                "detalhes_manifestacao",
                id=manifestacao.id
            )
        )

    return render_template(
        "editar_manifestacao.html",
        manifestacao=manifestacao,
        categorias=categorias
    )


# EXCLUIR MANIFESTAÇÃO

@app.route(
    "/manifestacao/<int:id>/excluir",
    methods=["POST"]
)
@login_obrigatorio
def excluir_manifestacao(id):

    manifestacao = Manifestacao.query.get_or_404(id)

    if (
        manifestacao.usuario_id != session["usuario_id"]
        and session.get("usuario_tipo") != "admin"
    ):

        flash(
            "Você não tem permissão para excluir esta manifestação.",
            "erro"
        )

        return redirect(
            url_for("listar_manifestacoes")
        )

    db.session.delete(manifestacao)
    db.session.commit()

    flash(
        "Manifestação excluída com sucesso!",
        "sucesso"
    )

    return redirect(
        url_for("listar_manifestacoes")
    )


# PAINEL ADMINISTRATIVO

@app.route("/admin")
@admin_obrigatorio
def admin():

    manifestacoes = Manifestacao.query.order_by(
        Manifestacao.data_registro.desc()
    ).all()

    total_manifestacoes = Manifestacao.query.count()

    total_pendentes = Manifestacao.query.filter_by(
        status="Pendente"
    ).count()

    total_andamento = Manifestacao.query.filter_by(
        status="Em andamento"
    ).count()

    total_resolvidas = Manifestacao.query.filter_by(
        status="Resolvido"
    ).count()

    return render_template(
        "admin.html",
        manifestacoes=manifestacoes,
        total_manifestacoes=total_manifestacoes,
        total_pendentes=total_pendentes,
        total_andamento=total_andamento,
        total_resolvidas=total_resolvidas
    )


# ALTERAR STATUS

@app.route(
    "/admin/manifestacao/<int:id>/status",
    methods=["POST"]
)
@admin_obrigatorio
def alterar_status(id):

    manifestacao = Manifestacao.query.get_or_404(id)

    novo_status = request.form.get("status")

    status_validos = [
        "Pendente",
        "Em análise",
        "Em andamento",
        "Resolvido"
    ]

    if novo_status in status_validos:

        manifestacao.status = novo_status
        db.session.commit()

        flash(
            "Status atualizado com sucesso!",
            "sucesso"
        )

    return redirect(url_for("admin"))


# API JSON

@app.route("/api/manifestacoes")
def api_manifestacoes():

    manifestacoes = Manifestacao.query.all()

    dados = []

    for manifestacao in manifestacoes:

        dados.append({
            "id": manifestacao.id,
            "titulo": manifestacao.titulo,
            "descricao": manifestacao.descricao,
            "localizacao": manifestacao.localizacao,
            "categoria": manifestacao.categoria.nome,
            "status": manifestacao.status,
            "data_registro": manifestacao.data_registro.strftime(
                "%d/%m/%Y %H:%M"
            )
        })

    return jsonify(dados)


# CRIAÇÃO DO BANCO E DADOS INICIAIS

def criar_dados_iniciais():

    categorias_iniciais = [
        "Buracos e calçadas",
        "Iluminação pública",
        "Lixo e descarte irregular",
        "Vazamentos e saneamento",
        "Praças e espaços públicos",
        "Serviços públicos",
        "Sugestões de melhorias",
        "Outros"
    ]

    for nome in categorias_iniciais:

        categoria = Categoria.query.filter_by(
            nome=nome
        ).first()

        if not categoria:

            nova_categoria = Categoria(
                nome=nome
            )

            db.session.add(nova_categoria)

    admin = Usuario.query.filter_by(
        email="admin@vozcidada.com"
    ).first()

    if not admin:

        senha_admin = generate_password_hash(
            "admin123"
        )

        admin = Usuario(
            nome="Administrador",
            email="admin@vozcidada.com",
            senha=senha_admin,
            tipo="admin"
        )

        db.session.add(admin)

    db.session.commit()


# INICIALIZAÇÃO

with app.app_context():

    db.create_all()

    criar_dados_iniciais()


if __name__ == "__main__":
    app.run(debug=True)