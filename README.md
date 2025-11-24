# Plateforme Agentique de Négociation Autonome - Automobile

## Vue d'ensemble

Plateforme d'agents IA capable de négocier de manière autonome une offre de reprise pour un véhicule existant et de structurer une nouvelle offre (achat, LLD, abonnement) pour le client.

### Proposition de valeur

- **Automatisation**: Réduction de la charge des équipes commerciales
- **Optimisation**: Maximisation des marges et amélioration de la satisfaction client
- **Transparence**: Négociation équitable et basée sur les données de marché

## Architecture

### Composants Principaux

#### 1. **Models Django**
- `Vehicle`: Véhicules en inventaire et en reprise
- `Client`: Profils clients avec préférences et budget
- `Negotiation`: Session de négociation
- `Offer`: Offres structurées (achat, LLD, abonnement)
- `MarketData`: Données de marché mises en cache
- `NegotiationRound`: Historique des rounds de négociation

#### 2. **AI Agents**
- `MarketAnalysisAgent`: Analyse des conditions de marché
- `TradeInEvaluationAgent`: Évaluation équitable des reprises
- `OfferStructuringAgent`: Structuration des offres commerciales
- `NegotiationAgent`: Orchestration de la négociation autonome

#### 3. **Data Scraping**
- `MarketDataScraper`: Collecte de données multi-sources
  - LeBonCoin
  - Argus
  - Webmoteurs
  - Caradisiac

#### 4. **REST API**
- CRUD complets pour les véhicules, clients, offres
- Endpoints de négociation
- Endpoints d'analyse et d'historique

## Installation

### 1. Cloner le projet
```bash
cd c:\Users\lilia\OneDrive\Desktop\automobile
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env et ajouter vos clés API
```

### 5. Initialiser la base de données
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py init_sample_data
```

### 6. Démarrer le serveur
```bash
python manage.py runserver
```

L'API sera disponible à `http://localhost:8000/api/`

## Utilisation

### 1. Créer un client et un véhicule
```python
# Créer un client
POST /api/clients/
{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "phone": "06 12 34 56 78",
    "address": "123 Rue de la Paix",
    "city": "Paris",
    "postal_code": "75001",
    "budget_min": 25000,
    "budget_max": 40000,
    "subscription_preference": "achat"
}

# Créer un véhicule pour la reprise
POST /api/vehicles/
{
    "vin": "VF7JU5N0005000001",
    "registration_number": "AB-123-CD",
    "make": "Renault",
    "model": "Clio",
    "year": 2019,
    "mileage": 80000,
    "fuel_type": "essence",
    "transmission": "manuelle",
    "power_hp": 110,
    "engine_cc": 1197,
    "current_market_value": 12000,
    "condition": "bon"
}
```

### 2. Initier une négociation
```bash
POST /api/negotiations/initiate/
{
    "client_id": 1,
    "trade_in_vehicle_id": 1,
    "target_vehicle_id": 2,
    "business_margin_target": 0.15
}
```

### 3. Exécuter des rounds de négociation
```bash
POST /api/negotiations/{id}/execute_round/
{
    "client_feedback": "L'offre est intéressante, mais je voudrais une valeur de reprise plus élevée"
}
```

### 4. Consulter les résultats
```bash
GET /api/negotiations/{id}/analysis/
```

## Fonctionnalités Clés

### Agents IA Autonomes

1. **Market Analysis Agent**
   - Évalue la demande du marché
   - Positionne le véhicule dans la gamme de prix
   - Identifie les avantages compétitifs

2. **Trade-in Evaluation Agent**
   - Évalue les véhicules de reprise de manière équitable
   - Considère l'état, le kilométrage, l'historique
   - Ajuste pour la loyauté du client

3. **Offer Structuring Agent**
   - Structure des offres gagnant-gagnant
   - Propose achat, LLD ou abonnement
   - Optimise les marges tout en satisfaisant le client

4. **Negotiation Agent**
   - Négocie de manière autonome
   - S'adapte aux retours du client
   - Atteint la conclusion dans 10 rounds maximum

### Data Scraping Multi-Source

Collecte des données de marché en temps quasi-réel depuis:
- Portails de petites annonces
- Services d'évaluation automobiles
- Agrégateurs de prix

### Optimisation Commerciale

- Maximisation des marges (cible configurable)
- Analyse de la satisfaction client
- Génération automatique d'offres alternatives
- Historique complet pour optimisation continue

## Architecture Technique

### Stack

- **Backend**: Django 4.2 + Django REST Framework
- **BD**: PostgreSQL (configurable)
- **AI**: Anthropic Claude API
- **Scraping**: BeautifulSoup4 + Requests
- **Async**: Celery + Redis (optionnel)
- **API Documentation**: DRF

### Structure du Projet

```
automobile/
├── config/                      # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── negotiation/                 # App principale
│   ├── models.py                # Modèles Django
│   ├── views.py                 # ViewSets et endpoints
│   ├── serializers.py           # Sérialiseurs DRF
│   ├── agents.py                # Agents IA
│   ├── orchestration.py         # Orchestration
│   ├── scrapers.py              # Web scraping
│   ├── admin.py                 # Admin Django
│   └── tests.py                 # Tests unitaires
├── manage.py                    # CLI Django
├── requirements.txt             # Dépendances Python
└── README.md                    # Ce fichier
```

## API Endpoints

### Véhicules
- `GET /api/vehicles/` - Liste des véhicules
- `POST /api/vehicles/` - Créer un véhicule
- `GET /api/vehicles/{id}/` - Détails d'un véhicule
- `GET /api/vehicles/in_stock/` - Véhicules en stock

### Clients
- `GET /api/clients/` - Liste des clients
- `POST /api/clients/` - Créer un client
- `GET /api/clients/{id}/` - Détails d'un client
- `GET /api/clients/{id}/negotiations/` - Négociations du client

### Offres
- `GET /api/offers/` - Liste des offres
- `POST /api/offers/{id}/accept_offer/` - Accepter une offre
- `POST /api/offers/{id}/reject_offer/` - Rejeter une offre

### Négociations
- `POST /api/negotiations/initiate/` - Initier une négociation
- `GET /api/negotiations/{id}/details/` - Détails complets
- `POST /api/negotiations/{id}/execute_round/` - Exécuter un round
- `GET /api/negotiations/{id}/history/` - Historique des rounds
- `GET /api/negotiations/{id}/analysis/` - Analyse et résultats

## Configuration

### Variables d'environnement (.env)

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DB_ENGINE=django.db.backends.postgresql
DB_NAME=automobile_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# APIs
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here

# Scraping
SCRAPING_ENABLED=True
SCRAPING_TIMEOUT=30

# Négociation
NEGOTIATION_TIMEOUT=300
MAX_NEGOTIATION_ROUNDS=10
MARKET_DATA_REFRESH_HOURS=24
```

## Tests

```bash
# Exécuter tous les tests
python manage.py test

# Tests spécifiques
python manage.py test negotiation.tests.VehicleModelTest

# Avec couverture
coverage run --source='.' manage.py test
coverage report
```

## Évolutions Futures

1. **Machine Learning**
   - Prédiction des prix de reprise
   - Scoring de risque client amélioré
   - Optimisation dynamique des marges

2. **Intégrations**
   - Système CRM
   - Gestion des financement bancaires
   - Notification client (Email, SMS)

3. **Analytics**
   - Dashboard d'analyse des négociations
   - KPIs commerciaux en temps réel
   - A/B testing des stratégies

4. **Scalabilité**
   - Déploiement Kubernetes
   - Cache distribué (Redis)
   - Queue asynchrone (Celery)

5. **Multi-canal**
   - ChatBot intégré
   - Mobile app
   - API publique pour partenaires

## Licence

Propriétaire - Tous droits réservés

## Support

Pour toute question ou assistance, contactez l'équipe de développement.
