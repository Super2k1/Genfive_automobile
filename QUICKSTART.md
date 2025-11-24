# Quick Start Guide - Plateforme Agentique de Négociation Autonome

## Installation rapide (5 minutes)

### 1. Cloner et naviguer
```bash
cd c:\Users\lilia\OneDrive\Desktop\automobile
```

### 2. Créer l'environnement virtuel
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
# Créer le fichier .env
copy .env.example .env

# Éditer le fichier .env avec vos clés API
# ANTHROPIC_API_KEY=sk-proj-xxx...
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

## Accès aux interfaces

### Admin Django
- URL: http://localhost:8000/admin
- Login: Compte créé à l'étape 5

### API REST
- Base: http://localhost:8000/api/
- Documentation: Voir API_DOCUMENTATION.md

### Endpoints rapides
- GET `/api/vehicles/` - Liste des véhicules
- GET `/api/clients/` - Liste des clients
- POST `/api/negotiations/initiate/` - Lancer une négociation

## Cas d'usage de base

### 1. Lancer une négociation via cURL

```bash
# 1. Créer un client
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marc",
    "last_name": "Laurent",
    "email": "marc@example.com",
    "phone": "0612345678",
    "address": "456 Rue Test",
    "city": "Lyon",
    "postal_code": "69000",
    "budget_min": 25000,
    "budget_max": 40000,
    "subscription_preference": "achat"
  }'

# Récupérer l'ID du client (ex: 4)

# 2. Créer un véhicule pour la reprise
curl -X POST http://localhost:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "VF7JU5N9999999999",
    "registration_number": "XY-999-ZW",
    "make": "Toyota",
    "model": "Yaris",
    "year": 2018,
    "version": "Active",
    "mileage": 95000,
    "fuel_type": "essence",
    "transmission": "manuelle",
    "power_hp": 110,
    "engine_cc": 1497,
    "current_market_value": 9500,
    "condition": "moyen",
    "in_stock": false
  }'

# Récupérer l'ID du véhicule (ex: 6)

# 3. Initier la négociation
curl -X POST http://localhost:8000/api/negotiations/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 4,
    "trade_in_vehicle_id": 6,
    "target_vehicle_id": 1,
    "business_margin_target": 0.15
  }'

# Récupérer l'ID de la négociation (ex: 2)

# 4. Voir les détails
curl http://localhost:8000/api/negotiations/2/details/

# 5. Exécuter un round
curl -X POST http://localhost:8000/api/negotiations/2/execute_round/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_feedback": "L'"'"'offre me semble correcte, pouvez-vous inclure la révision?"
  }'

# 6. Analyser les résultats
curl http://localhost:8000/api/negotiations/2/analysis/
```

### 2. Via le panel Admin Django

1. Aller à http://localhost:8000/admin
2. Dans "Negotiation" → "Ajouter une négociation"
3. Sélectionner client, véhicules
4. Sauvegarder
5. Les agents IA lancent automatiquement le processus

### 3. Via Python (Script)

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from negotiation.orchestration import NegotiationOrchestrator
from negotiation.models import Client, Vehicle

# Récupérer les données
client = Client.objects.first()
trade_in_vehicle = Vehicle.objects.filter(in_stock=False).first()
target_vehicle = Vehicle.objects.filter(in_stock=True).first()

# Lancer la négociation
orchestrator = NegotiationOrchestrator()
negotiation = orchestrator.initiate_negotiation(
    client_id=client.id,
    trade_in_vehicle_id=trade_in_vehicle.id,
    target_vehicle_id=target_vehicle.id,
    business_margin_target=0.15
)

print(f"Négociation {negotiation.id} initiée")
print(f"Statut: {negotiation.status}")
print(f"Raisonnement IA: {negotiation.agent_reasoning}")
```

## Données d'exemple disponibles

### Clients
1. Jean Dupont - Budget 25k-40k - Diesel
2. Marie Martin - Budget 15k-25k - Essence
3. Pierre Bernard - Budget 40k-50k - Électrique

### Véhicules à la vente
1. Peugeot 3008 (2022) - 32,000€
2. Renault Clio (2021) - 17,500€
3. Toyota Corolla (2023) - 27,000€
4. Tesla Model 3 (2022) - 42,000€
5. VW Golf GTI (2020) - 24,000€

## Commandes utiles

```bash
# Voir tous les véhicules
python manage.py shell
>>> from negotiation.models import Vehicle
>>> for v in Vehicle.objects.all():
...     print(f"{v.year} {v.make} {v.model} - {v.current_market_value}€")

# Voir toutes les négociations
>>> from negotiation.models import Negotiation
>>> for n in Negotiation.objects.all():
...     print(f"Negotiation {n.id} - {n.client} - {n.status}")

# Voir les offres d'une négociation
>>> n = Negotiation.objects.get(id=1)
>>> for o in n.offers.all():
...     print(f"Offre {o.id}: {o.offer_type} - {o.total_cost}€")
```

## Configuration des clés API

### Anthropic Claude API
1. Créer un compte sur https://console.anthropic.com
2. Aller à "API Keys"
3. Créer une nouvelle clé
4. Ajouter dans `.env`:
   ```
   ANTHROPIC_API_KEY=sk-proj-xxx...
   ```

## Dépannage

### Erreur: "ANTHROPIC_API_KEY not set"
- ✓ Vérifier le fichier `.env`
- ✓ Exécuter: `source venv/Scripts/activate`
- ✓ Redémarrer le serveur

### Erreur: "Port 8000 déjà utilisé"
```bash
python manage.py runserver 8001
# ou
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Erreur: Base de données
```bash
python manage.py migrate
python manage.py init_sample_data
```

## Prochaines étapes

1. **Ajouter votre API Anthropic**
   - Obtenir la clé depuis console.anthropic.com
   - Mettre à jour .env

2. **Tester avec des données réelles**
   - Créer des véhicules avec vos données
   - Importer des clients depuis CRM

3. **Configurer le scraping**
   - Implémenter les parseurs pour vos sources
   - Tester la collecte de données

4. **Adapter les stratégies commerciales**
   - Configurer les marges cibles
   - Ajuster les seuils de satisfaction

5. **Déployer en production**
   - Configurer la base de données PostgreSQL
   - Mettre en place Celery/Redis
   - Configurer le monitoring

## Support

- Documentation détaillée: Voir `README.md`
- API: Voir `API_DOCUMENTATION.md`
- Architecture: Voir `ARCHITECTURE.md`

## Structure de dossiers

```
automobile/
├── config/                      # Configuration Django
├── negotiation/                 # App principale
│   ├── models.py               # Modèles
│   ├── views.py                # API Views
│   ├── serializers.py          # Sérialiseurs
│   ├── agents.py               # Agents IA
│   ├── orchestration.py        # Orchestration
│   ├── scrapers.py             # Scraping
│   ├── admin.py                # Admin
│   ├── tests.py                # Tests
│   └── management/
│       └── commands/
│           └── init_sample_data.py  # Initialisation
├── manage.py                   # CLI
├── requirements.txt            # Dépendances
├── .env.example               # Variables d'environnement
├── README.md                  # Documentation
├── API_DOCUMENTATION.md       # API
└── ARCHITECTURE.md            # Architecture
```

Prêt à commencer! 🚀
