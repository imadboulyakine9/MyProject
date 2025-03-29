# Rapport de Projet: Système d'Authentification avec Flask
### Faculté des Sciences et Techniques - FST
#### Réalisé par: [Votre Nom]
#### Encadré par: [Nom du Professeur]

## Table des Matières
1. [Introduction](#introduction)
2. [Technologies Utilisées](#technologies-utilisées)
3. [Structure du Projet](#structure-du-projet)
4. [Diagramme de Séquence](#diagramme-de-séquence)
5. [Code Important](#code-important)
6. [Explication du Code](#explication-du-code)
7. [Conclusion](#conclusion)

## Introduction
الحمد لله
Dans le cadre de notre formation à la FSTT, j'ai développé une application web utilisant le framework Flask de Python. Ce projet met en œuvre un système d'authentification complet avec des fonctionnalités de base comme l'inscription, la connexion, et la gestion de profil utilisateur.

## Technologies Utilisées
Pour ce projet, j'ai utilisé plusieurs technologies modernes:

- **Flask**: Framework web en Python
  - Documentation: https://flask.palletsprojects.com/
- **SQLAlchemy**: ORM pour la base de données
  - Documentation: https://docs.sqlalchemy.org/
- **Flask-JWT-Extended**: Pour la gestion des tokens d'authentification
  - Documentation: https://flask-jwt-extended.readthedocs.io/
- **Python-dotenv**: Pour la gestion des variables d'environnement
  - Documentation: https://pypi.org/project/python-dotenv/

## Structure du Projet
```
MyProject/
├── app.py              # Point d'entrée de l'application
├── models.py           # Modèles de données
├── routes.py           # Routes et logique de l'application
├── requirements.txt    # Dépendances du projet
├── .env               # Configuration et variables d'environnement
└── templates/         # Templates HTML
    ├── base.html      # Template de base
    ├── login.html     # Page de connexion
    ├── register.html  # Page d'inscription
    └── profile.html   # Page de profil
```

## Diagramme de Séquence
Voici le diagramme de séquence pour le processus d'authentification:

```
┌──────┐          ┌──────┐          ┌──────┐         ┌──────┐
│Client│          │Route │          │Model │         │  DB  │
└──┬───┘          └──┬───┘          └──┬───┘         └──┬───┘
   │   Login Request │                 │                │
   │────────────────>│                 │                │
   │                 │ Check User      │                │
   │                 │────────────────>│                │
   │                 │                 │  Query User    │
   │                 │                 │───────────────>│
   │                 │                 │   Return User  │
   │                 │                 │<───────────────│
   │                 │   Return User   │                │
   │                 │<────────────────│                │
   │  JWT Tokn       │                 │                │
   │<────────────────│                 │                │
   │                 │                 │                │
```

## Code Important
Voici les  snippets de code les plus importants de notre application avec leurs explications détaillées:

### 1. Configuration de l'Application et Gestion JWT
```python
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
```
**Explication**: 
- Ce code est crucial car il initialise notre application Flask avec les configurations essentielles
- Il configure la sécurité avec des clés secrètes stockées dans le fichier .env
- Il configure JWT pour utiliser les cookies comme méthode de stockage des tokens
- Il désactive la protection CSRF pour simplifier l'exemple (à activer en production)

### 2. Modèle Utilisateur avec Hachage de Mot de Passe
```python
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```
**Explication**:
- Définit la structure de notre table utilisateur dans la base de données
- Implémente des méthodes sécurisées pour le hachage et la vérification des mots de passe
- Utilise Werkzeug pour le hachage cryptographique des mots de passe
- Garantit l'unicité des noms d'utilisateur et des emails

### 3. Authentification et Gestion des Sessions
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            response = make_response(redirect(url_for('auth.profile')))
            set_access_cookies(response, access_token)
            return response
```
**Explication**:
- Gère le processus de connexion des utilisateurs
- Vérifie les identifiants de manière sécurisée
- Crée un token JWT pour la session authentifiée
- Configure les cookies sécurisés pour maintenir la session

### 4. Protection des Routes et Vérification d'Authentification
```python
@app.context_processor
def utility_processor():
    def is_authenticated():
        try:
            verify_jwt_in_request()
            return True
        except:
            return False
    return dict(is_authenticated=is_authenticated)
```
**Explication**:
- Fournit une fonction globale pour vérifier l'état d'authentification
- Permet aux templates de conditionner l'affichage selon l'état de connexion
- Vérifie la validité du token JWT de manière sécurisée
- Simplifie la gestion de l'interface utilisateur

### 5. Gestion du Profil Utilisateur
```python
@auth_bp.route('/profile', methods=['GET', 'POST'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if request.method == 'POST':
        email = request.form.get('email')
        age = request.form.get('age')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.username != current_user:
            flash('Cet email est déjà utilisé')
            return redirect(url_for('auth.profile'))
            
        user.email = email
        if age:
            user.age = int(age)
        db.session.commit()
```
**Explication**:
- Protège la route du profil avec le décorateur @jwt_required()
- Permet la mise à jour des informations utilisateur
- Vérifie l'unicité de l'email lors des modifications
- Gère la validation et la persistance des données

## Explication du Code

### 1. Configuration de l'Application (`app.py`)
Le fichier `app.py` est le point d'entrée de notre application. Il configure:
- L'initialisation de Flask
- La configuration de la base de données
- La gestion des JWT pour l'authentification
- Les routes principales

```python
# Exemple de configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') 
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # Pour conection a database
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') # used for auth
```

### 2. Modèle de Données (`models.py`)
Le modèle User définit la structure de nos données utilisateur:
- Username (nom d'utilisateur)
- Email (adresse électronique)
- Age (âge de l'utilisateur)
- Password hash (mot de passe crypté) one way encryption

### 3. Routes et Logique (`routes.py`)
Les principales fonctionnalités implémentées:

#### Inscription (`/register`)
- Validation des données
- Création du compte utilisateur
- Hashage du mot de passe

#### Connexion (`/login`)
- Vérification des identifiants
- Création du token JWT
- Redirection vers le profil

#### Profil (`/profile`)
- Affichage des informations
- Modification des données personnelles

### 4. Interface Utilisateur (Templates)
L'interface utilise:
- Bootstrap pour le style (classes CSS)
- Jinja2 pour le templating
- Formulaires HTML sécurisés

### 5. Sécurité
Mesures de sécurité implémentées:
- Hashage des mots de passe avec Werkzeug
- Protection contre les injections SQL avec SQLAlchemy
- Tokens JWT pour la session
- Protection CSRF

## Conclusion
بِسْمِ اللَّـهِ الرَّحْمَـٰنِ الرَّحِيمِ

Ce projet m'a permis de mettre en pratique mes connaissances en:
- Développement web avec Flask
- Gestion de base de données
- Sécurité web
- Architecture MVC

### Perspectives d'Amélioration
- Ajouter la récupération de mot de passe
- Implémenter l'authentification à deux facteurs
- Améliorer l'interface utilisateur
- Ajouter plus de fonctionnalités au profil utilisateur

### Remerciements
Je tiens à remercier mes professeurs de la FST pour leur encadrement et leurs conseils précieux tout au long de ce projet.

---
© 2024 FST - Tous droits réservés