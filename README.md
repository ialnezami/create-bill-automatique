# Créateur de Factures Automatisées

[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Nuxt.js](https://img.shields.io/badge/Nuxt.js-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com/)
[![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com/)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.com/)

## 📋 Description

Application web complète pour la création, gestion et automatisation de factures avec intégration des systèmes de paiement Stripe et PayPal. Cette solution permet aux entreprises de gérer efficacement leur facturation avec des fonctionnalités avancées de suivi, de paiement et de reporting.

## ✨ Fonctionnalités

### 🧾 Gestion des Factures
- Création automatique de factures personnalisables
- Modèles de factures réutilisables
- Numérotation automatique et séquentielle
- Support multi-devises
- Calcul automatique des taxes (TVA, etc.)
- Gestion des remises et promotions

### 💳 Intégrations de Paiement
- **Stripe** : Paiements par carte, virements SEPA, wallets digitaux
- **PayPal** : Paiements PayPal, cartes de crédit via PayPal
- Webhooks pour synchronisation automatique des paiements
- Support des paiements récurrents/abonnements
- Gestion des remboursements

### 👥 Gestion Clients
- Carnet d'adresses clients complet
- Historique des transactions
- Profils de facturation personnalisés
- Notifications automatiques par email

### 📊 Reporting & Analytics
- Tableau de bord avec métriques en temps réel
- Rapports de ventes et revenus
- Statistiques de paiement
- Export des données (PDF, Excel, CSV)

### 🔐 Sécurité & Administration
- Authentification JWT
- Chiffrement des données sensibles
- Logs d'audit complets
- Gestion des rôles et permissions

## 🏗️ Architecture

### Frontend (Nuxt.js + Vue.js)
```
frontend/
├── components/          # Composants Vue réutilisables
│   ├── Invoice/        # Composants spécifiques aux factures
│   ├── Payment/        # Composants de paiement
│   ├── Dashboard/      # Composants du tableau de bord
│   └── Common/         # Composants communs (UI)
├── pages/              # Pages et routing
├── layouts/            # Layouts de l'application
├── plugins/            # Plugins Nuxt
├── middleware/         # Middleware d'authentification
├── store/              # Pinia/Vuex store
├── utils/              # Utilitaires et helpers
└── assets/             # Assets statiques
```

### Backend (Flask + Python)
```
backend/
├── app/
│   ├── models/         # Modèles MongoDB (MongoEngine)
│   ├── routes/         # Routes API REST
│   │   ├── auth.py     # Authentification
│   │   ├── invoices.py # Gestion des factures
│   │   ├── payments.py # Intégrations paiements
│   │   ├── clients.py  # Gestion clients
│   │   └── reports.py  # Rapports et analytics
│   ├── services/       # Logique métier
│   │   ├── stripe_service.py
│   │   ├── paypal_service.py
│   │   ├── invoice_service.py
│   │   └── email_service.py
│   ├── utils/          # Utilitaires
│   └── config/         # Configuration
├── migrations/         # Scripts de migration DB
└── tests/             # Tests unitaires et d'intégration
```

## 🛠️ Stack Technique

### Frontend
- **Framework** : Nuxt.js 3.x (Vue.js 3.x)
- **UI Framework** : Tailwind CSS + Headless UI
- **State Management** : Pinia
- **HTTP Client** : Axios/Fetch API
- **Validation** : VeeValidate + Yup
- **Charts** : Chart.js / ApexCharts
- **PDF Generation** : jsPDF
- **Date Handling** : Day.js

### Backend
- **Framework** : Flask 2.x
- **ORM** : MongoEngine
- **Authentication** : Flask-JWT-Extended
- **API Documentation** : Flask-RESTX (Swagger)
- **Task Queue** : Celery + Redis
- **Email** : Flask-Mail
- **PDF Generation** : ReportLab
- **Validation** : Marshmallow

### Base de Données
- **Database** : MongoDB 6.x
- **Cache** : Redis
- **Search** : MongoDB Atlas Search (optionnel)

### Intégrations & Services
- **Paiements** : Stripe API v2023, PayPal REST API
- **Email** : SendGrid / SMTP
- **Storage** : AWS S3 / Local Storage
- **Monitoring** : Sentry (optionnel)

## 🚀 Installation

### Prérequis
- Node.js 18+ et npm/yarn
- Python 3.9+
- MongoDB 6.0+
- Redis 6.0+
- Comptes Stripe et PayPal (clés API)

### 1. Cloner le Repository
```bash
git clone https://github.com/votre-username/invoice-generator.git
cd invoice-generator
```

### 2. Configuration Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration des variables d'environnement
cp .env.example .env
```

Éditer le fichier `.env` :
```env
# Database
MONGODB_URI=mongodb://localhost:27017/invoice_app
REDIS_URL=redis://localhost:6379

# JWT Secret
JWT_SECRET_KEY=votre-cle-secrete-jwt

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal
PAYPAL_CLIENT_ID=votre-client-id
PAYPAL_CLIENT_SECRET=votre-client-secret
PAYPAL_ENVIRONMENT=sandbox  # ou production

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre-email
MAIL_PASSWORD=votre-mot-de-passe

# AWS S3 (optionnel)
AWS_ACCESS_KEY_ID=votre-access-key
AWS_SECRET_ACCESS_KEY=votre-secret-key
AWS_S3_BUCKET=votre-bucket
```

### 3. Configuration Frontend

```bash
cd frontend

# Installer les dépendances
npm install
# ou
yarn install

# Configuration Nuxt
cp .env.example .env
```

Éditer le fichier `.env` :
```env
# API Base URL
NUXT_PUBLIC_API_BASE_URL=http://localhost:5000/api

# Stripe
NUXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_...

# PayPal
NUXT_PUBLIC_PAYPAL_CLIENT_ID=votre-client-id
```

### 4. Initialisation de la Base de Données

```bash
cd backend

# Lancer MongoDB (si local)
mongod

# Exécuter les migrations
python manage.py init_db
```

### 5. Lancement de l'Application

#### Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python app.py
# API disponible sur http://localhost:5000
```

#### Worker Celery (Terminal 2)
```bash
cd backend
source venv/bin/activate
celery -A app.celery worker --loglevel=info
```

#### Frontend (Terminal 3)
```bash
cd frontend
npm run dev
# Application disponible sur http://localhost:3000
```

## 📝 Utilisation

### 1. Création d'un Compte
- Accéder à `http://localhost:3000/register`
- Créer un compte administrateur
- Configurer les paramètres de l'entreprise

### 2. Configuration des Paiements
- Aller dans `Paramètres > Paiements`
- Configurer Stripe et/ou PayPal
- Tester les intégrations avec les clés de test

### 3. Création de Factures
- `Factures > Nouvelle Facture`
- Sélectionner/ajouter un client
- Ajouter les lignes de facture
- Prévisualiser et envoyer

### 4. Suivi des Paiements
- Les webhooks mettent à jour automatiquement le statut
- Tableau de bord pour vue d'ensemble
- Notifications en temps réel

## 🔧 API Documentation

L'API REST est documentée avec Swagger UI, accessible à `http://localhost:5000/docs`

### Endpoints Principaux

#### Authentification
```
POST /api/auth/register    # Inscription
POST /api/auth/login       # Connexion
POST /api/auth/refresh     # Refresh token
```

#### Factures
```
GET    /api/invoices       # Liste des factures
POST   /api/invoices       # Créer une facture
GET    /api/invoices/{id}  # Détails d'une facture
PUT    /api/invoices/{id}  # Modifier une facture
DELETE /api/invoices/{id}  # Supprimer une facture
POST   /api/invoices/{id}/send  # Envoyer par email
```

#### Paiements
```
POST /api/payments/stripe/create-intent    # Créer un PaymentIntent Stripe
POST /api/payments/paypal/create-order     # Créer une commande PayPal
POST /api/payments/stripe/webhook          # Webhook Stripe
POST /api/payments/paypal/webhook          # Webhook PayPal
```

## 🧪 Tests

### Backend
```bash
cd backend
python -m pytest tests/
```

### Frontend
```bash
cd frontend
npm run test
```

### Tests E2E
```bash
cd frontend
npm run test:e2e
```

## 📦 Déploiement

### Docker
```yaml
# docker-compose.yml fourni pour déploiement rapide
docker-compose up -d
```

### Production
1. Configurer les variables d'environnement de production
2. Utiliser un serveur WSGI (Gunicorn) pour Flask
3. Utiliser PM2 ou similaire pour Nuxt.js
4. Configurer un reverse proxy (Nginx)
5. Mettre en place le monitoring et les logs

## 🤝 Contribution

1. Fork du projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit des changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- **Documentation** : [Wiki du projet](https://github.com/votre-username/invoice-generator/wiki)
- **Issues** : [GitHub Issues](https://github.com/votre-username/invoice-generator/issues)
- **Email** : support@votre-domaine.com

## 🙏 Remerciements

- Vue.js et Nuxt.js pour le framework frontend
- Flask pour l'API backend robuste
- Stripe et PayPal pour les intégrations de paiement
- MongoDB pour la base de données flexible
- La communauté open source