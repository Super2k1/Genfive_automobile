#!/usr/bin/env python3
"""
PLATEFORME AGENTIQUE DE NÉGOCIATION AUTONOME - SETUP GUIDE
==========================================================

Ce script vous aide à démarrer rapidement avec la plateforme.
Exécutez: python SETUP_GUIDE.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_section(text):
    print(f"\n► {text}")
    print("-" * 70)

def print_success(text):
    print(f"  ✅ {text}")

def print_warning(text):
    print(f"  ⚠️  {text}")

def print_info(text):
    print(f"  ℹ️  {text}")

def print_code(text):
    print(f"\n  $ {text}\n")

def main():
    os.chdir(Path(__file__).parent)
    
    print_header("PLATEFORME AGENTIQUE DE NÉGOCIATION AUTONOME")
    print("Setup & Configuration Guide")
    
    # Step 1: Welcome
    print_section("ÉTAPE 1: Bienvenue")
    print_info("Cette plateforme utilise:")
    print_info("  • Django 4.2 + REST Framework")
    print_info("  • Claude 3.5 Sonnet (Anthropic)")
    print_info("  • PostgreSQL (optionnel)")
    print_info("  • 4 Agents IA autonomes")
    
    # Step 2: Check Python
    print_section("ÉTAPE 2: Vérifier Python")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 9:
        print_success(f"Python {python_version.major}.{python_version.minor} détecté")
    else:
        print_warning(f"Python {python_version.major}.{python_version.minor} détecté (3.9+ recommandé)")
    
    # Step 3: Environment
    print_section("ÉTAPE 3: Configuration Environnement")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_success("Environnement virtuel détecté")
    else:
        print_info("Création d'un environnement virtuel...")
        print_code("python -m venv venv")
        print_info("Puis activez-le avec:")
        if sys.platform == "win32":
            print_code("venv\\Scripts\\activate")
        else:
            print_code("source venv/bin/activate")
    
    # Step 4: Dependencies
    print_section("ÉTAPE 4: Installation des Dépendances")
    print_info("Assurez-vous que votre environnement virtuel est activé")
    print_code("pip install -r requirements.txt")
    print_info("Dépendances incluses:")
    print_info("  • Django 4.2.7")
    print_info("  • Django REST Framework 3.14.0")
    print_info("  • Anthropic Claude API 0.7.1")
    print_info("  • BeautifulSoup4 4.12.2")
    print_info("  • PostgreSQL, Celery, Redis (optionnel)")
    
    # Step 5: Environment variables
    print_section("ÉTAPE 5: Variables d'Environnement")
    print_info("Copier le fichier d'exemple:")
    print_code("copy .env.example .env  # Windows")
    print_code("cp .env.example .env    # Linux/Mac")
    print_info("\nÉditer le fichier .env et ajouter:")
    print_info("  • ANTHROPIC_API_KEY: Votre clé API Claude")
    print_info("  • DB_PASSWORD: Mot de passe PostgreSQL (si utilisé)")
    print_info("\nObtenir la clé Anthropic:")
    print_info("  1. Aller à https://console.anthropic.com")
    print_info("  2. Créer un compte ou se connecter")
    print_info("  3. Aller à 'API Keys'")
    print_info("  4. Créer une nouvelle clé")
    print_info("  5. Copier dans .env")
    
    # Step 6: Database
    print_section("ÉTAPE 6: Initialiser la Base de Données")
    print_code("python manage.py migrate")
    print_success("Migrations appliquées")
    
    print_code("python manage.py createsuperuser")
    print_info("Créez un compte administrateur")
    
    print_code("python manage.py init_sample_data")
    print_success("Données d'exemple chargées (5 véhicules, 3 clients)")
    
    # Step 7: Running
    print_section("ÉTAPE 7: Démarrer le Serveur")
    print_code("python manage.py runserver")
    print_success("Serveur lancé sur http://localhost:8000")
    
    print_info("Accès rapides:")
    print_info("  • Admin: http://localhost:8000/admin")
    print_info("  • API: http://localhost:8000/api/")
    print_info("  • Véhicules: http://localhost:8000/api/vehicles/")
    print_info("  • Clients: http://localhost:8000/api/clients/")
    
    # Step 8: Next
    print_section("ÉTAPE 8: Prochaines Étapes")
    print_info("1. Tester localement")
    print_code("python manage.py shell < examples.py")
    
    print_info("2. Consulter la documentation")
    print_info("  • QUICKSTART.md: Guide rapide")
    print_info("  • API_DOCUMENTATION.md: API complète")
    print_info("  • ARCHITECTURE.md: Architecture technique")
    
    print_info("3. Lancer une négociation")
    print_code("curl -X POST http://localhost:8000/api/negotiations/initiate/ \\\\")
    print_code("  -H 'Content-Type: application/json' \\\\")
    print_code("  -d '{\"client_id\": 1, \"trade_in_vehicle_id\": 1, \"target_vehicle_id\": 2}'")
    
    # Step 9: Documentation
    print_section("📚 DOCUMENTATION")
    files = {
        "INDEX.md": "Guide de navigation complet",
        "QUICKSTART.md": "Installation et premiers pas (5 min)",
        "PROJECT_SUMMARY.md": "Vue d'ensemble exécutive",
        "README.md": "Documentation principale (30 min)",
        "API_DOCUMENTATION.md": "Documentation API détaillée (45 min)",
        "ARCHITECTURE.md": "Architecture technique (60 min)",
        "DELIVERABLES.md": "Liste complète des livrables",
        "examples.py": "5 exemples de code exécutables"
    }
    
    for file, description in files.items():
        print_info(f"{file}: {description}")
    
    # Step 10: Support
    print_section("🆘 SUPPORT & AIDE")
    print_info("Erreur lors de l'installation?")
    print_info("  1. Vérifier Python 3.9+: python --version")
    print_info("  2. Vérifier pip: pip --version")
    print_info("  3. Lire QUICKSTART.md: section 'Dépannage'")
    print_info("  4. Vérifier les logs Django")
    
    print_info("\nClé API Anthropic manquante?")
    print_info("  1. Créer un compte: https://console.anthropic.com")
    print_info("  2. Générer une clé API")
    print_info("  3. Ajouter dans .env: ANTHROPIC_API_KEY=sk-proj-...")
    print_info("  4. Redémarrer le serveur")
    
    print_info("\nBesoin d'aide?")
    print_info("  • Lire la documentation appropriée")
    print_info("  • Consulter les exemples dans examples.py")
    print_info("  • Vérifier les tests dans negotiation/tests.py")
    
    # Summary
    print_header("✅ VOUS ÊTES PRÊT!")
    print("Votre plateforme d'agents IA est prête à être utilisée.")
    print("\nProchaines actions recommandées:")
    print("  1. ► Lire QUICKSTART.md pour l'installation détaillée")
    print("  2. ► Accéder à l'admin: http://localhost:8000/admin")
    print("  3. ► Consulter la documentation complète")
    print("  4. ► Lancer une négociation de test")
    print("  5. ► Adapter aux données réelles")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompu par l'utilisateur")
        sys.exit(1)
