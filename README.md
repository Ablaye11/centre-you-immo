# Centre Commercial YOU IMMO

Une application Django pour la gestion d'un centre commercial.
Fonctionnalités principales :
- Gestion des locataires et des boutiques
- Gestion financière (facturation, loyers, dépenses)
- Gestion de la maintenance et du stationnement
- Tableau de bord avec statistiques

## Prérequis
- Python 3.x
- PostgreSQL

## Installation

1. Cloner le dépôt
2. Installer les dépendances : `pip install -r requirements.txt` (ou équivalent)
3. Configurer les variables d'environnement dans un fichier `.env` (voir `.env.example`)
4. Appliquer les migrations : `python manage.py migrate`
5. Lancer le serveur de développement : `python manage.py runserver`
