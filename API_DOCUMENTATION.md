# Plateforme Agentique de Négociation Autonome - Documentation API

## Table des matières
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Exemples d'utilisation](#exemples-dutilisation)
5. [Codes d'erreur](#codes-derreur)

## Introduction

Cette API REST permet de gérer le processus complet de négociation autonome d'offres automobiles. Les agents IA gèrent la négociation de manière autonome en analysant les données du marché, évaluant les reprises, et structurant des offres optimales.

### Base URL
```
http://localhost:8000/api/
```

### Content-Type
Tous les endpoints acceptent et retournent du JSON.
```
Content-Type: application/json
```

## Authentication

Actuellement, la plateforme utilise l'authentification par token (optionnel).

### Token Authentication
```bash
Authorization: Token YOUR_API_TOKEN
```

### Session Authentication
Les sessions Django sont également supportées pour les tests.

## Endpoints

### Véhicules

#### Lister les véhicules
```
GET /api/vehicles/
```

**Paramètres de query:**
- `make`: Marque (ex: Peugeot)
- `model`: Modèle (ex: 3008)
- `year`: Année
- `fuel_type`: Type de carburant (essence, diesel, hybride, electrique)
- `transmission`: Transmission (manuelle, automatique)
- `condition`: État (excellent, bon, moyen, acceptable)
- `in_stock`: Disponible (true/false)
- `search`: Recherche textuelle (VIN, immatriculation, marque, modèle)
- `ordering`: Tri (-created_at, year, mileage, current_market_value)

**Exemple:**
```bash
curl http://localhost:8000/api/vehicles/?fuel_type=diesel&in_stock=true
```

**Réponse:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "vin": "VF7JU5N0005000001",
      "registration_number": "AB-123-CD",
      "make": "Peugeot",
      "model": "3008",
      "year": 2022,
      "version": "Allure",
      "mileage": 15000,
      "fuel_type": "diesel",
      "transmission": "automatique",
      "power_hp": 160,
      "engine_cc": 1956,
      "original_purchase_price": "35000.00",
      "current_market_value": "32000.00",
      "estimated_trade_in_value": "30000.00",
      "condition": "excellent",
      "in_stock": true,
      "stock_location": "Lot A, Place 1",
      "created_at": "2024-11-23T10:00:00Z",
      "updated_at": "2024-11-23T10:00:00Z"
    }
  ]
}
```

#### Créer un véhicule
```
POST /api/vehicles/
```

**Body:**
```json
{
  "vin": "VF7JU5N0005000001",
  "registration_number": "AB-123-CD",
  "make": "Peugeot",
  "model": "3008",
  "year": 2022,
  "version": "Allure",
  "mileage": 15000,
  "fuel_type": "diesel",
  "transmission": "automatique",
  "power_hp": 160,
  "engine_cc": 1956,
  "original_purchase_price": "35000.00",
  "current_market_value": "32000.00",
  "estimated_trade_in_value": "30000.00",
  "condition": "excellent",
  "in_stock": true,
  "stock_location": "Lot A, Place 1"
}
```

#### Détails d'un véhicule
```
GET /api/vehicles/{id}/
```

#### Véhicules en stock
```
GET /api/vehicles/in_stock/
```

### Clients

#### Lister les clients
```
GET /api/clients/
```

**Paramètres de query:**
- `city`: Ville
- `subscription_preference`: Préférence (achat, lld, abonnement, flexible)
- `search`: Recherche textuelle

**Réponse:**
```json
{
  "results": [
    {
      "id": 1,
      "first_name": "Jean",
      "last_name": "Dupont",
      "email": "jean.dupont@example.com",
      "phone": "06 12 34 56 78",
      "address": "123 Rue de la Paix",
      "city": "Paris",
      "postal_code": "75001",
      "trade_in_vehicle": 1,
      "preferred_fuel": "diesel",
      "preferred_transmission": "automatique",
      "budget_min": "25000.00",
      "budget_max": "40000.00",
      "subscription_preference": "achat",
      "loyalty_score": "0.70",
      "risk_score": "0.30",
      "created_at": "2024-11-23T10:00:00Z",
      "updated_at": "2024-11-23T10:00:00Z"
    }
  ]
}
```

#### Créer un client
```
POST /api/clients/
```

**Body:**
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "phone": "06 12 34 56 78",
  "address": "123 Rue de la Paix",
  "city": "Paris",
  "postal_code": "75001",
  "preferred_fuel": "diesel",
  "preferred_transmission": "automatique",
  "budget_min": "25000.00",
  "budget_max": "40000.00",
  "subscription_preference": "achat"
}
```

#### Négociations d'un client
```
GET /api/clients/{id}/negotiations/
```

### Négociations

#### Initier une négociation
```
POST /api/negotiations/initiate/
```

**Description:** Démarre un nouveau processus de négociation autonome. L'API lancera automatiquement les agents IA pour:
1. Analyser les données de marché
2. Évaluer la reprise
3. Structurer les offres
4. Débuter la négociation

**Body:**
```json
{
  "client_id": 1,
  "trade_in_vehicle_id": 1,
  "target_vehicle_id": 2,
  "business_margin_target": 0.15
}
```

**Paramètres:**
- `client_id` (requis): ID du client
- `trade_in_vehicle_id` (optionnel): Véhicule à reprendre
- `target_vehicle_id` (optionnel): Véhicule cible
- `business_margin_target` (optionnel): Marge commerciale cible (0-1)

**Réponse (201 Created):**
```json
{
  "id": 1,
  "client": 1,
  "client_details": {...},
  "trade_in_vehicle": 1,
  "trade_in_details": {...},
  "target_vehicle": 2,
  "target_details": {...},
  "status": "in_progress",
  "negotiation_rounds": 0,
  "max_rounds": 10,
  "trade_in_offered_value": null,
  "final_price": null,
  "margin_achieved": null,
  "chosen_offer_type": null,
  "agent_reasoning": {...},
  "market_analysis": {...},
  "negotiation_history": [],
  "offers_list": [],
  "rounds": [],
  "started_at": "2024-11-23T10:00:00Z",
  "ended_at": null,
  "updated_at": "2024-11-23T10:00:00Z"
}
```

#### Détails d'une négociation
```
GET /api/negotiations/{id}/details/
```

**Réponse complète avec toutes les informations:**
```json
{
  "id": 1,
  "client": 1,
  "status": "in_progress",
  "negotiation_rounds": 2,
  "max_rounds": 10,
  "trade_in_offered_value": "10500.00",
  "final_price": null,
  "margin_achieved": null,
  "chosen_offer_type": null,
  "agent_reasoning": {
    "strategy": "Maximiser la satisfaction du client...",
    "initial_trade_in_range": [9500, 11500],
    "approach": "consultative"
  },
  "market_analysis": {
    "demand": "high",
    "pricing_position": "at_market",
    "competitive_factors": [...]
  },
  "negotiation_history": [...],
  "offers": [...],
  "negotiation_rounds": [...],
  "started_at": "2024-11-23T10:00:00Z",
  "ended_at": null,
  "updated_at": "2024-11-23T10:05:00Z"
}
```

#### Exécuter un round de négociation
```
POST /api/negotiations/{id}/execute_round/
```

**Description:** Lance le prochain round de la négociation autonome. L'agent IA analysera le retour du client et proposera une nouvelle offre.

**Body:**
```json
{
  "client_feedback": "L'offre de reprise est trop basse, je m'attendais à 12000€",
  "proposed_counter_offer": null
}
```

**Réponse:**
```json
{
  "round_number": 3,
  "proposed_offer": {
    "offer_type": "achat",
    "trade_in_value": "11200.00",
    "purchase_price": "31500.00",
    "monthly_payment": null,
    "duration_months": null,
    "total_cost": "31500.00",
    "warranty_months": 12,
    "maintenance_included": false,
    "insurance_included": false,
    "confidence_score": 82.5
  },
  "status": "in_progress",
  "should_continue": true,
  "confidence": 82.5
}
```

#### Historique des rounds
```
GET /api/negotiations/{id}/history/
```

**Réponse:**
```json
{
  "results": [
    {
      "id": 1,
      "round_number": 1,
      "agent_proposal": {...},
      "agent_reasoning": "Première offre basée sur l'analyse de marché...",
      "client_feedback": null,
      "client_counter_proposal": null,
      "round_status": "ongoing",
      "created_at": "2024-11-23T10:00:00Z"
    },
    {
      "id": 2,
      "round_number": 2,
      "agent_proposal": {...},
      "agent_reasoning": "Ajustement suite au retour...",
      "client_feedback": "C'est mieux mais pas encore convaincant",
      "client_counter_proposal": {...},
      "round_status": "ongoing",
      "created_at": "2024-11-23T10:02:00Z"
    }
  ]
}
```

#### Analyse et résultats
```
GET /api/negotiations/{id}/analysis/
```

**Réponse:**
```json
{
  "negotiation_id": 1,
  "status": "concluded",
  "rounds_executed": 5,
  "max_rounds": 10,
  "trade_in_offered_value": "11500.00",
  "final_price": "31800.00",
  "margin_achieved": 0.12,
  "market_analysis": {
    "demand": "high",
    "pricing_position": "at_market",
    "competitive_factors": ["low_mileage", "excellent_condition"]
  },
  "agent_reasoning": {
    "strategy": "Win-win approach",
    "key_decisions": [...]
  },
  "duration_minutes": 12.5
}
```

### Offres

#### Lister les offres
```
GET /api/offers/
```

**Paramètres de query:**
- `offer_type`: Type d'offre (achat, lld, abonnement)
- `offer_status`: Statut (proposed, accepted, rejected, negotiating)
- `negotiation`: ID de la négociation

#### Accepter une offre
```
POST /api/offers/{id}/accept_offer/
```

**Réponse:**
```json
{
  "status": "offer_accepted",
  "offer_id": 1,
  "negotiation_id": 1
}
```

#### Rejeter une offre
```
POST /api/offers/{id}/reject_offer/
```

**Réponse:**
```json
{
  "status": "offer_rejected",
  "offer_id": 1
}
```

## Exemples d'utilisation

### Cas d'usage complet: Négociation autonome

#### 1. Créer un client
```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean@example.com",
    "phone": "0612345678",
    "address": "123 Rue de la Paix",
    "city": "Paris",
    "postal_code": "75001",
    "budget_min": "25000",
    "budget_max": "40000",
    "subscription_preference": "achat"
  }'
```

#### 2. Créer un véhicule de reprise
```bash
curl -X POST http://localhost:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "VF7JU5N0005000099",
    "registration_number": "CD-456-EF",
    "make": "Renault",
    "model": "Clio",
    "year": 2019,
    "version": "Zen",
    "mileage": 80000,
    "fuel_type": "essence",
    "transmission": "manuelle",
    "power_hp": 110,
    "engine_cc": 1197,
    "current_market_value": "12000",
    "condition": "bon",
    "in_stock": false
  }'
```

#### 3. Initier la négociation
```bash
curl -X POST http://localhost:8000/api/negotiations/initiate/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "trade_in_vehicle_id": 1,
    "target_vehicle_id": 2,
    "business_margin_target": 0.15
  }'
```

#### 4. Obtenir les détails de la négociation
```bash
curl http://localhost:8000/api/negotiations/1/details/
```

#### 5. Exécuter des rounds de négociation
```bash
# Round 1 - Retour du client
curl -X POST http://localhost:8000/api/negotiations/1/execute_round/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_feedback": "L'"'"'offre de reprise est trop basse, je m'"'"'attendais à 12000€"
  }'

# Round 2 - Retour suivant
curl -X POST http://localhost:8000/api/negotiations/1/execute_round/ \
  -H "Content-Type: application/json" \
  -d '{
    "client_feedback": "Mieux! Mais le prix d'"'"'achat reste élevé de 800€"
  }'
```

#### 6. Consulter l'analyse finale
```bash
curl http://localhost:8000/api/negotiations/1/analysis/
```

## Codes d'erreur

| Code | Signification | Description |
|------|---|---|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée |
| 400 | Bad Request | Requête invalide |
| 404 | Not Found | Ressource non trouvée |
| 500 | Server Error | Erreur serveur |

### Exemples d'erreurs

```json
{
  "error": "Client ID 999 not found"
}
```

```json
{
  "detail": "Not found."
}
```

```json
{
  "non_field_errors": [
    "Invalid credentials"
  ]
}
```

## Limitations

- Maximum 10 rounds de négociation par défaut
- Timeout de 300 secondes par négociation
- Cache des données de marché: 24 heures
- Taille maximale des requêtes: 1MB

## Notes importantes

1. **Authentification**: À configurer en production
2. **Rate Limiting**: À implémenter pour la production
3. **CORS**: À configurer selon vos domaines
4. **Logging**: Les négociations sont complètement loggées
5. **Données sensibles**: À protéger en production
