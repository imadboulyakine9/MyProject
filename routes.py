# Routes pour l'authentification
from flask import Blueprint, request, render_template, redirect, url_for, flash, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Route d'inscription - permet de créer un nouveau compte utilisateur"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        
        if User.query.filter_by(username=username).first():
            flash('Nom d\'utilisateur déjà pris')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email déjà utilisé')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        if age:
            user.age = int(age)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Route de connexion - authentifie l'utilisateur et crée un token JWT"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            response = make_response(redirect(url_for('auth.profile')))
            set_access_cookies(response, access_token)
            return response
        
        flash('Identifiants invalides')
    return render_template('login.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@jwt_required()
def profile():
    """Route du profil - permet de voir et modifier les informations de l'utilisateur"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if request.method == 'POST':
        email = request.form.get('email')
        age = request.form.get('age')
        username = request.form.get('username')
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        existing_user_mail = User.query.filter_by(email=email).first()
        if existing_user_mail and existing_user_mail.username != current_user:
            flash('Cet email est déjà utilisé')
            return redirect(url_for('auth.profile'))
        
        # Vérifier si le nom d'utilisateur est déjà utilisé par un autre utilisateur
        existing_user_name = User.query.filter_by(username=username).first()
        if existing_user_name and existing_user_name.username != current_user:
            flash('Ce nom d\'utilisateur est déjà pris')
            return redirect(url_for('auth.profile'))
            
        user.email = email
        user.username = username
        if age:
            user.age = int(age)
        db.session.commit()
        flash('Profil mis à jour avec succès!')
        
    if user:
        return render_template('profile.html', user=user)
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    """Route de déconnexion - supprime le token JWT"""
    response = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(response)
    flash('Vous avez été déconnecté')
    return response
