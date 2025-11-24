# Plateforme Agentique de Négociation Autonome - Guide Technique et Architecture

## Vue d'ensemble de l'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        REST API (DRF)                           │
├──────────────────────────────────────────────────────────────────┤
│  /api/vehicles  /api/clients  /api/negotiations  /api/offers    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌─────────────────────┐    ┌──────────────────────┐
│  Orchestration      │    │  Serializers (DRF)   │
│  + Business Logic   │    │  + Validation        │
└──────────┬──────────┘    └──────────────────────┘
           │
        ┌──┴─────────────────────────────────────────┐
        │                                            │
        ▼                                            ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   AI AGENTS              │    │  DATA SCRAPING           │
├──────────────────────────┤    ├──────────────────────────┤
│ • Market Analysis        │    │ • LeBonCoin             │
│ • Trade-in Evaluation    │    │ • Argus                  │
│ • Offer Structuring      │    │ • Webmoteurs             │
│ • Negotiation            │    │ • Caradisiac             │
└──────────────────────────┘    └──────────────────────────┘
        │                                │
        └────────────────┬───────────────┘
                         │
┌────────────────────────┴────────────────────────┐
│    ANTHROPIC CLAUDE API (Agentic AI)           │
├─────────────────────────────────────────────────┤
│  • Multi-round conversation                     │
│  • JSON reasoning                               │
│  • Complex analysis                             │
└─────────────────────────────────────────────────┘
        │
┌───────┴──────────────────────────────┐
│   DJANGO MODELS & DATABASE           │
├──────────────────────────────────────┤
│ • Vehicle                             │
│ • Client                              │
│ • Negotiation                         │
│ • Offer                               │
│ • NegotiationRound                    │
│ • MarketData                          │
└──────────────────────────────────────┘
```

## Flux de négociation autonome

```
1. INITIATION
   ├─ Créer session Negotiation
   ├─ Récupérer les données du client
   ├─ Récupérer les données des véhicules
   └─ Initialiser les agents IA
        │
        ▼
2. ANALYSE DE MARCHÉ
   ├─ Scraper les données de marché multi-sources
   ├─ Analyser les conditions de demande
   ├─ Évaluer le positionnement compétitif
   └─ MarketAnalysisAgent génère l'analyse
        │
        ▼
3. ÉVALUATION DE REPRISE
   ├─ TradeInEvaluationAgent analyse le véhicule
   ├─ Considère l'état, kilométrage, marché
   ├─ Ajuste selon la loyauté du client
   └─ Propose valeur équitable
        │
        ▼
4. STRUCTURATION D'OFFRES
   ├─ OfferStructuringAgent crée 1-3 offres
   ├─ Achat, LLD, ou Abonnement
   ├─ Optimize margins vs satisfaction
   └─ Générer justifications
        │
        ▼
5. NÉGOCIATION (LOOP MAX 10 ROUNDS)
   ├─ NegotiationAgent propose l'offre
   │  └─ Stock la proposition
   │
   ├─ Attendre retour du client
   │
   ├─ NegotiationAgent traite le feedback
   │  ├─ Analyse la contre-proposition
   │  ├─ Ajuste l'offre si nécessaire
   │  └─ Évalue proximité d'accord
   │
   ├─ Décision:
   │  ├─ SI accord → 6. CONCLUSION
   │  ├─ SI max rounds → 6. CONCLUSION (échec)
   │  └─ SINON → boucle au round suivant
        │
        ▼
6. CONCLUSION
   ├─ Finaliser l'offre acceptée
   ├─ Calculer les marges réalisées
   ├─ Générer le rapport final
   └─ Archiver la négociation
```

## Détail des Agents IA

### 1. MarketAnalysisAgent

**Responsabilité**: Analyser les conditions du marché automobiles

**Entrées**:
```python
{
    'vehicle': {
        'make': 'Peugeot',
        'model': '3008',
        'year': 2022,
        'mileage': 15000,
        'fuel_type': 'diesel'
    },
    'market_data': {
        'average_price': 32000,
        'min_price': 28000,
        'max_price': 36000,
        'listings_count': 45
    }
}
```

**Sorties**:
```json
{
    "demand": "high",
    "pricing_position": "at_market",
    "competitive_factors": ["low_mileage", "excellent_condition"],
    "recommended_strategy": "premium_positioning",
    "risk_factors": ["fuel_type_trend"],
    "opportunity": "Strong market for this model"
}
```

### 2. TradeInEvaluationAgent

**Responsabilité**: Évaluer équitablement les véhicules en reprise

**Contexte de décision**:
- Données du marché actuelles
- État et condition du véhicule
- Score de loyauté du client
- Objectifs commerciaux

**Processus**:
1. Analyser les comparables de marché
2. Ajuster pour l'état spécifique
3. Appliquer les facteurs de loyauté
4. Proposer fourchette équitable
5. Justifier la valorisation

**Exemple de résultat**:
```json
{
    "base_trade_in_value": 10200,
    "condition_adjustments": -300,
    "loyalty_bonus": 200,
    "final_recommended_value": 10100,
    "confidence_score": 0.87,
    "reasoning": "Véhicule en bon état avec faible kilométrage..."
}
```

### 3. OfferStructuringAgent

**Responsabilité**: Créer des offres commerciales optimales

**Variables optimisées**:
- Valeur de reprise
- Prix d'achat
- Mensualités (LLD/Abonnement)
- Durée du contrat
- Services inclus
- Marges

**Contraintes**:
- Budget client
- Marges commerciales minimales
- Satisfaction client
- Stock disponible

**Trois types d'offres**:

1. **Achat direct**
   - Paiement comptant
   - Meilleure marge
   - Satisfaction client: Possession

2. **Location Longue Durée (LLD)**
   - Mensualités fixes
   - Incluant entretien/assurance
   - Flexibilité

3. **Abonnement**
   - Formule tout compris
   - Usage illimité
   - Changement facile

### 4. NegotiationAgent

**Responsabilité**: Négocier de manière autonome

**Stratégies**:
1. **Consultative**: Écouter, adapter
2. **Principled**: Basée sur les données
3. **Win-win**: Créer de la valeur

**Logique de décision**:
```
ROUND N:
├─ Proposer offre
├─ Attendre retour client
├─ Analyser feedback
├─ Calculer écart
├─ Décision:
│  ├─ SI écart < seuil → Accepter
│  ├─ SI écart grand → Ajuster & continuer
│  └─ SI client très strict → Dernier effort ou cloturer
└─ Mettre à jour historique
```

## Intégration Claude API

### Configuration

```python
from anthropic import Anthropic

client = Anthropic(api_key='your-key')

# Conversation multi-round persistante
messages = [
    {"role": "user", "content": "Première message"},
    {"role": "assistant", "content": "Réponse 1"},
    {"role": "user", "content": "Deuxième message"}
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    system="Vous êtes un expert en négociation commerciale...",
    messages=messages
)
```

### Prompts Système

**MarketAnalysisAgent**:
```
Vous êtes un expert en analyse du marché automobile. 
Analysez les données fournies et fournissez des insights 
stratégiques sur les conditions de marché. 
Répondez toujours en JSON valide.
```

**TradeInEvaluationAgent**:
```
Vous êtes un expert en évaluation automobile. 
Fournissez une évaluation équitable basée sur:
- Données de marché
- État du véhicule
- Loyauté du client
Répondez en JSON avec justification.
```

## Scraping de données de marché

### Architecture du Scraper

```python
class MarketDataScraper:
    def aggregate_market_data(make, model, year, fuel):
        """Agrège les données de 4 sources"""
        sources = [
            scrape_leboncoin(),
            scrape_webmoteurs(),
            scrape_caradisiac(),
            scrape_argus()
        ]
        
        # Normaliser et agréger
        aggregate_stats = {
            'average_price': mean(prices),
            'min_price': min(prices),
            'max_price': max(prices),
            'listings_count': count(listings),
            'confidence': calculate_confidence()
        }
        
        # Cacher dans MarketData
        return cache_result()
```

### Stratégie de Caching

```python
# Vérifier cache existant
market_data = MarketData.objects.filter(
    make=vehicle.make,
    model=vehicle.model,
    year=vehicle.year,
    fuel_type=vehicle.fuel_type
)

# Si < 24 heures, utiliser le cache
if market_data and (now - market_data.last_updated).days < 1:
    return market_data

# Sinon, scraper et mettre à jour
else:
    new_data = scraper.aggregate_market_data(...)
    MarketData.objects.update_or_create(..., defaults=new_data)
    return new_data
```

## Modèles de données

### Vehicle
- Information d'identification: VIN, immatriculation
- Données techniques: Marque, modèle, année, carburant, puissance
- Valorisation: Prix marché, valeur d'occasion
- État et inventaire: Condition, localisation

### Client
- Profil personnel et contact
- Préférences: Carburant, transmission, budget
- Scoring: Loyauté (0-1), Risque (0-1)
- Historique: Reprise associée, préférence d'offre

### Negotiation
- État: initiated, in_progress, pending_approval, concluded, failed
- Participants: Client, véhicule reprise, véhicule cible
- Métriques: Rounds exécutés, marges, prix final
- Données IA: Raisonnement, analyse de marché, historique

### Offer
- Type: achat, LLD, abonnement
- Conditions: Valeur reprise, prix, mensualités, durée
- Bénéfices: Garantie, maintenance, assurance
- Statut: proposed, accepted, rejected, negotiating

### NegotiationRound
- Numéro du round
- Proposition de l'agent (JSON)
- Raisonnement (texte)
- Retour du client
- Contre-proposition (JSON)
- Statut du round

## Optimisation et Performance

### Requêtes BD

```python
# Optimiser les joins
Negotiation.objects.select_related(
    'client', 'trade_in_vehicle', 'target_vehicle'
).prefetch_related(
    'offers', 'rounds'
)

# Paginer les résultats
paginator.paginate_queryset(queryset)

# Index sur les colonnes fréquemment filtrées
class Meta:
    indexes = [
        models.Index(fields=['status', '-started_at']),
        models.Index(fields=['client', 'status']),
    ]
```

### Caching

```python
# Cache des données de marché (24h)
MARKET_DATA_CACHE = 'market_{make}_{model}_{year}_{fuel}'

# Cache des analyses (1h)
ANALYSIS_CACHE = 'analysis_{vehicle_id}'

# Utiliser Redis pour la distribution
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Scalabilité

```python
# Async tasks avec Celery
@app.task
def scrape_market_data_async(vehicle_id):
    """Scraper en arrière-plan"""
    pass

@app.task
def execute_negotiation_round_async(negotiation_id):
    """Exécuter les rounds en parallèle"""
    pass
```

## Déploiement en Production

### Configuration Django

```python
# settings.py pour production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Logging complet
LOGGING = {...}
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD gunicorn config.wsgi --bind 0.0.0.0:8000
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: automobile-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: automobile:latest
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: config.settings
        ports:
        - containerPort: 8000
```

## Monitoring et Logs

### Structured Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

logger.info('Negotiation started', extra={
    'negotiation_id': negotiation.id,
    'client_id': client.id,
    'timestamp': datetime.now().isoformat()
})
```

### Métriques

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

negotiation_duration = Histogram(
    'negotiation_duration_seconds',
    'Durée des négociations'
)

negotiations_total = Counter(
    'negotiations_total',
    'Nombre total de négociations',
    ['status']
)
```

## Sécurité

1. **Authentication**: Token + Session
2. **Authorization**: Permissions DRF
3. **Data**: Chiffrement en transit (HTTPS)
4. **Secrets**: Variables d'environnement
5. **Validation**: Sérialiseurs DRF
6. **Rate Limiting**: À implémenter
7. **CORS**: Configuration stricte

## Maintenance

- Backup quotidien de la BD
- Monitoring des scrapes
- Logs des négociations
- Audit trail complet
- Versioning des APIs
