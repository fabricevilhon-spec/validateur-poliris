import streamlit as st
import pandas as pd
import io
from datetime import datetime

# =============================================================================
# DÉFINITION DE LA VERSION ET CONFIGURATION
# =============================================================================
__version__ = "9.1.0 (Nettoyage final des données brutes)"

EXPECTED_COLUMNS = 334
HEADER_FILE = 'En-tête_Poliris.csv'
REF_ANNONCE_INDEX = 1

# =============================================================================
# DÉFINITION COMPLÈTE ET DÉTAILLÉE DU SCHÉMA (votre "base de règles")
# =============================================================================
SCHEMA = [
    # --- Bloc 1: Identification (1-10) ---
    {'rang': 1, 'nom': 'Identifiant agence', 'type': 'Texte', 'obligatoire': True},
    {'rang': 2, 'nom': 'Référence agence du bien', 'type': 'Texte', 'obligatoire': True},
    {'rang': 3, 'nom': 'Type d\'annonce', 'type': 'Texte', 'obligatoire': True},
    {'rang': 4, 'nom': 'Type de bien', 'type': 'Texte', 'obligatoire': True},
    {'rang': 5, 'nom': 'CP', 'type': 'Texte', 'obligatoire': True},
    {'rang': 6, 'nom': 'Ville', 'type': 'Texte', 'obligatoire': True},
    {'rang': 7, 'nom': 'Pays', 'type': 'Texte', 'obligatoire': True},
    {'rang': 8, 'nom': 'Adresse', 'type': 'Texte', 'obligatoire': False},
    {'rang': 9, 'nom': 'Quartier / Proximité', 'type': 'Texte', 'obligatoire': False},
    {'rang': 10, 'nom': 'Activités commerciales', 'type': 'Texte', 'obligatoire': False},

    # --- Bloc 2: Données financières (11-15) ---
    {'rang': 11, 'nom': 'Prix', 'type': 'Décimal', 'obligatoire': True},
    {'rang': 12, 'nom': 'Loyer / mois murs', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 13, 'nom': 'Loyer CC', 'type': 'Texte', 'obligatoire': False},
    {'rang': 14, 'nom': 'Loyer HT', 'type': 'Texte', 'obligatoire': False},
    {'rang': 15, 'nom': 'Honoraires', 'type': 'Décimal', 'obligatoire': False},

    # --- Bloc 3: Surfaces et Pièces (16-19) ---
    {'rang': 16, 'nom': 'Surface', 'type': 'Décimal', 'obligatoire': True},
    {'rang': 17, 'nom': 'Surface terrain', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 18, 'nom': 'NB de pièces', 'type': 'Entier', 'obligatoire': True},
    {'rang': 19, 'nom': 'NB de chambres', 'type': 'Entier', 'obligatoire': False},

    # --- Bloc 4: Textes descriptifs (20-21) ---
    {'rang': 20, 'nom': 'Libellé', 'type': 'Texte', 'obligatoire': True},
    {'rang': 21, 'nom': 'Descriptif', 'type': 'Texte', 'obligatoire': True},

    # --- Bloc 5: Dates (22-25) ---
    {'rang': 22, 'nom': 'Date de disponibilité', 'type': 'Date', 'obligatoire': False},
    {'rang': 23, 'nom': 'Date de libération', 'type': 'Date', 'obligatoire': False},
    {'rang': 24, 'nom': 'Année de construction', 'type': 'Entier', 'obligatoire': False},
    {'rang': 25, 'nom': 'Date de rénovation', 'type': 'Date', 'obligatoire': False},

    # --- Bloc 6: Structure du bien (26-30) ---
    {'rang': 26, 'nom': 'NB de salles de bain', 'type': 'Entier', 'obligatoire': False},
    {'rang': 27, 'nom': 'NB de salles d\'eau', 'type': 'Entier', 'obligatoire': False},
    {'rang': 28, 'nom': 'NB de WC', 'type': 'Entier', 'obligatoire': False},
    {'rang': 29, 'nom': 'Étage', 'type': 'Entier', 'obligatoire': False},
    {'rang': 30, 'nom': 'NB d\'étages', 'type': 'Entier', 'obligatoire': False},

    # --- Bloc 7: Prestations et équipements (31-40) ---
    {'rang': 31, 'nom': 'Ascenseur', 'type': 'Texte', 'obligatoire': False},
    {'rang': 32, 'nom': 'Type de chauffage', 'type': 'Texte', 'obligatoire': False},
    {'rang': 33, 'nom': 'Balcon', 'type': 'Texte', 'obligatoire': False},
    {'rang': 34, 'nom': 'Terrasse', 'type': 'Texte', 'obligatoire': False},
    {'rang': 35, 'nom': 'Piscine', 'type': 'Texte', 'obligatoire': False},
    {'rang': 36, 'nom': 'Cave', 'type': 'Texte', 'obligatoire': False},
    {'rang': 37, 'nom': 'Parking', 'type': 'Entier', 'obligatoire': False},
    {'rang': 38, 'nom': 'Garage / Box', 'type': 'Entier', 'obligatoire': False},
    {'rang': 39, 'nom': 'Meublé', 'type': 'Texte', 'obligatoire': False},
    {'rang': 40, 'nom': 'Gardien', 'type': 'Texte', 'obligatoire': False},

    # --- Bloc 8: Photos (URL) (41-100) ---
    {'rang': 41, 'nom': 'Photo 1', 'type': 'Texte', 'obligatoire': False},
    {'rang': 42, 'nom': 'Photo 2', 'type': 'Texte', 'obligatoire': False},
    {'rang': 43, 'nom': 'Photo 3', 'type': 'Texte', 'obligatoire': False},
    {'rang': 44, 'nom': 'Photo 4', 'type': 'Texte', 'obligatoire': False},
    {'rang': 45, 'nom': 'Photo 5', 'type': 'Texte', 'obligatoire': False},
    {'rang': 46, 'nom': 'Photo 6', 'type': 'Texte', 'obligatoire': False},
    {'rang': 47, 'nom': 'Photo 7', 'type': 'Texte', 'obligatoire': False},
    {'rang': 48, 'nom': 'Photo 8', 'type': 'Texte', 'obligatoire': False},
    {'rang': 49, 'nom': 'Photo 9', 'type': 'Texte', 'obligatoire': False},
    {'rang': 50, 'nom': 'Photo 10', 'type': 'Texte', 'obligatoire': False},
    {'rang': 51, 'nom': 'Photo 11', 'type': 'Texte', 'obligatoire': False},
    {'rang': 52, 'nom': 'Photo 12', 'type': 'Texte', 'obligatoire': False},
    {'rang': 53, 'nom': 'Photo 13', 'type': 'Texte', 'obligatoire': False},
    {'rang': 54, 'nom': 'Photo 14', 'type': 'Texte', 'obligatoire': False},
    {'rang': 55, 'nom': 'Photo 15', 'type': 'Texte', 'obligatoire': False},
    {'rang': 56, 'nom': 'Photo 16', 'type': 'Texte', 'obligatoire': False},
    {'rang': 57, 'nom': 'Photo 17', 'type': 'Texte', 'obligatoire': False},
    {'rang': 58, 'nom': 'Photo 18', 'type': 'Texte', 'obligatoire': False},
    {'rang': 59, 'nom': 'Photo 19', 'type': 'Texte', 'obligatoire': False},
    {'rang': 60, 'nom': 'Photo 20', 'type': 'Texte', 'obligatoire': False},
    {'rang': 61, 'nom': 'Photo 21', 'type': 'Texte', 'obligatoire': False},
    {'rang': 62, 'nom': 'Photo 22', 'type': 'Texte', 'obligatoire': False},
    {'rang': 63, 'nom': 'Photo 23', 'type': 'Texte', 'obligatoire': False},
    {'rang': 64, 'nom': 'Photo 24', 'type': 'Texte', 'obligatoire': False},
    {'rang': 65, 'nom': 'Photo 25', 'type': 'Texte', 'obligatoire': False},
    {'rang': 66, 'nom': 'Photo 26', 'type': 'Texte', 'obligatoire': False},
    {'rang': 67, 'nom': 'Photo 27', 'type': 'Texte', 'obligatoire': False},
    {'rang': 68, 'nom': 'Photo 28', 'type': 'Texte', 'obligatoire': False},
    {'rang': 69, 'nom': 'Photo 29', 'type': 'Texte', 'obligatoire': False},
    {'rang': 70, 'nom': 'Photo 30', 'type': 'Texte', 'obligatoire': False},
    {'rang': 71, 'nom': 'Photo 31', 'type': 'Texte', 'obligatoire': False},
    {'rang': 72, 'nom': 'Photo 32', 'type': 'Texte', 'obligatoire': False},
    {'rang': 73, 'nom': 'Photo 33', 'type': 'Texte', 'obligatoire': False},
    {'rang': 74, 'nom': 'Photo 34', 'type': 'Texte', 'obligatoire': False},
    {'rang': 75, 'nom': 'Photo 35', 'type': 'Texte', 'obligatoire': False},
    {'rang': 76, 'nom': 'Photo 36', 'type': 'Texte', 'obligatoire': False},
    {'rang': 77, 'nom': 'Photo 37', 'type': 'Texte', 'obligatoire': False},
    {'rang': 78, 'nom': 'Photo 38', 'type': 'Texte', 'obligatoire': False},
    {'rang': 79, 'nom': 'Photo 39', 'type': 'Texte', 'obligatoire': False},
    {'rang': 80, 'nom': 'Photo 40', 'type': 'Texte', 'obligatoire': False},
    {'rang': 81, 'nom': 'Photo 41', 'type': 'Texte', 'obligatoire': False},
    {'rang': 82, 'nom': 'Photo 42', 'type': 'Texte', 'obligatoire': False},
    {'rang': 83, 'nom': 'Photo 43', 'type': 'Texte', 'obligatoire': False},
    {'rang': 84, 'nom': 'Photo 44', 'type': 'Texte', 'obligatoire': False},
    {'rang': 85, 'nom': 'Photo 45', 'type': 'Texte', 'obligatoire': False},
    {'rang': 86, 'nom': 'Photo 46', 'type': 'Texte', 'obligatoire': False},
    {'rang': 87, 'nom': 'Photo 47', 'type': 'Texte', 'obligatoire': False},
    {'rang': 88, 'nom': 'Photo 48', 'type': 'Texte', 'obligatoire': False},
    {'rang': 89, 'nom': 'Photo 49', 'type': 'Texte', 'obligatoire': False},
    {'rang': 90, 'nom': 'Photo 50', 'type': 'Texte', 'obligatoire': False},
    {'rang': 91, 'nom': 'Photo 51', 'type': 'Texte', 'obligatoire': False},
    {'rang': 92, 'nom': 'Photo 52', 'type': 'Texte', 'obligatoire': False},
    {'rang': 93, 'nom': 'Photo 53', 'type': 'Texte', 'obligatoire': False},
    {'rang': 94, 'nom': 'Photo 54', 'type': 'Texte', 'obligatoire': False},
    {'rang': 95, 'nom': 'Photo 55', 'type': 'Texte', 'obligatoire': False},
    {'rang': 96, 'nom': 'Photo 56', 'type': 'Texte', 'obligatoire': False},
    {'rang': 97, 'nom': 'Photo 57', 'type': 'Texte', 'obligatoire': False},
    {'rang': 88, 'nom': 'Photo 58', 'type': 'Texte', 'obligatoire': False},
    {'rang': 99, 'nom': 'Photo 59', 'type': 'Texte', 'obligatoire': False},
    {'rang': 100, 'nom': 'Photo 60', 'type': 'Texte', 'obligatoire': False},
    
    # --- Bloc 9: Titres de Photos (101-160) ---
    {'rang': 101, 'nom': 'Titre Photo 1', 'type': 'Texte', 'obligatoire': False},
    {'rang': 102, 'nom': 'Titre Photo 2', 'type': 'Texte', 'obligatoire': False},
    {'rang': 103, 'nom': 'Titre Photo 3', 'type': 'Texte', 'obligatoire': False},
    {'rang': 104, 'nom': 'Titre Photo 4', 'type': 'Texte', 'obligatoire': False},
    {'rang': 105, 'nom': 'Titre Photo 5', 'type': 'Texte', 'obligatoire': False},
    {'rang': 106, 'nom': 'Titre Photo 6', 'type': 'Texte', 'obligatoire': False},
    {'rang': 107, 'nom': 'Titre Photo 7', 'type': 'Texte', 'obligatoire': False},
    {'rang': 108, 'nom': 'Titre Photo 8', 'type': 'Texte', 'obligatoire': False},
    {'rang': 109, 'nom': 'Titre Photo 9', 'type': 'Texte', 'obligatoire': False},
    {'rang': 110, 'nom': 'Titre Photo 10', 'type': 'Texte', 'obligatoire': False},
    {'rang': 111, 'nom': 'Titre Photo 11', 'type': 'Texte', 'obligatoire': False},
    {'rang': 112, 'nom': 'Titre Photo 12', 'type': 'Texte', 'obligatoire': False},
    {'rang': 113, 'nom': 'Titre Photo 13', 'type': 'Texte', 'obligatoire': False},
    {'rang': 114, 'nom': 'Titre Photo 14', 'type': 'Texte', 'obligatoire': False},
    {'rang': 115, 'nom': 'Titre Photo 15', 'type': 'Texte', 'obligatoire': False},
    {'rang': 116, 'nom': 'Titre Photo 16', 'type': 'Texte', 'obligatoire': False},
    {'rang': 117, 'nom': 'Titre Photo 17', 'type': 'Texte', 'obligatoire': False},
    {'rang': 118, 'nom': 'Titre Photo 18', 'type': 'Texte', 'obligatoire': False},
    {'rang': 119, 'nom': 'Titre Photo 19', 'type': 'Texte', 'obligatoire': False},
    {'rang': 120, 'nom': 'Titre Photo 20', 'type': 'Texte', 'obligatoire': False},
    {'rang': 121, 'nom': 'Titre Photo 21', 'type': 'Texte', 'obligatoire': False},
    {'rang': 122, 'nom': 'Titre Photo 22', 'type': 'Texte', 'obligatoire': False},
    {'rang': 123, 'nom': 'Titre Photo 23', 'type': 'Texte', 'obligatoire': False},
    {'rang': 124, 'nom': 'Titre Photo 24', 'type': 'Texte', 'obligatoire': False},
    {'rang': 125, 'nom': 'Titre Photo 25', 'type': 'Texte', 'obligatoire': False},
    {'rang': 126, 'nom': 'Titre Photo 26', 'type': 'Texte', 'obligatoire': False},
    {'rang': 127, 'nom': 'Titre Photo 27', 'type': 'Texte', 'obligatoire': False},
    {'rang': 128, 'nom': 'Titre Photo 28', 'type': 'Texte', 'obligatoire': False},
    {'rang': 129, 'nom': 'Titre Photo 29', 'type': 'Texte', 'obligatoire': False},
    {'rang': 130, 'nom': 'Titre Photo 30', 'type': 'Texte', 'obligatoire': False},
    {'rang': 131, 'nom': 'Titre Photo 31', 'type': 'Texte', 'obligatoire': False},
    {'rang': 132, 'nom': 'Titre Photo 32', 'type': 'Texte', 'obligatoire': False},
    {'rang': 133, 'nom': 'Titre Photo 33', 'type': 'Texte', 'obligatoire': False},
    {'rang': 134, 'nom': 'Titre Photo 34', 'type': 'Texte', 'obligatoire': False},
    {'rang': 135, 'nom': 'Titre Photo 35', 'type': 'Texte', 'obligatoire': False},
    {'rang': 136, 'nom': 'Titre Photo 36', 'type': 'Texte', 'obligatoire': False},
    {'rang': 137, 'nom': 'Titre Photo 37', 'type': 'Texte', 'obligatoire': False},
    {'rang': 138, 'nom': 'Titre Photo 38', 'type': 'Texte', 'obligatoire': False},
    {'rang': 139, 'nom': 'Titre Photo 39', 'type': 'Texte', 'obligatoire': False},
    {'rang': 140, 'nom': 'Titre Photo 40', 'type': 'Texte', 'obligatoire': False},
    {'rang': 141, 'nom': 'Titre Photo 41', 'type': 'Texte', 'obligatoire': False},
    {'rang': 142, 'nom': 'Titre Photo 42', 'type': 'Texte', 'obligatoire': False},
    {'rang': 143, 'nom': 'Titre Photo 43', 'type': 'Texte', 'obligatoire': False},
    {'rang': 144, 'nom': 'Titre Photo 44', 'type': 'Texte', 'obligatoire': False},
    {'rang': 145, 'nom': 'Titre Photo 45', 'type': 'Texte', 'obligatoire': False},
    {'rang': 146, 'nom': 'Titre Photo 46', 'type': 'Texte', 'obligatoire': False},
    {'rang': 147, 'nom': 'Titre Photo 47', 'type': 'Texte', 'obligatoire': False},
    {'rang': 148, 'nom': 'Titre Photo 48', 'type': 'Texte', 'obligatoire': False},
    {'rang': 149, 'nom': 'Titre Photo 49', 'type': 'Texte', 'obligatoire': False},
    {'rang': 150, 'nom': 'Titre Photo 50', 'type': 'Texte', 'obligatoire': False},
    {'rang': 151, 'nom': 'Titre Photo 51', 'type': 'Texte', 'obligatoire': False},
    {'rang': 152, 'nom': 'Titre Photo 52', 'type': 'Texte', 'obligatoire': False},
    {'rang': 153, 'nom': 'Titre Photo 53', 'type': 'Texte', 'obligatoire': False},
    {'rang': 154, 'nom': 'Titre Photo 54', 'type': 'Texte', 'obligatoire': False},
    {'rang': 155, 'nom': 'Titre Photo 55', 'type': 'Texte', 'obligatoire': False},
    {'rang': 156, 'nom': 'Titre Photo 56', 'type': 'Texte', 'obligatoire': False},
    {'rang': 157, 'nom': 'Titre Photo 57', 'type': 'Texte', 'obligatoire': False},
    {'rang': 158, 'nom': 'Titre Photo 58', 'type': 'Texte', 'obligatoire': False},
    {'rang': 159, 'nom': 'Titre Photo 59', 'type': 'Texte', 'obligatoire': False},
    {'rang': 160, 'nom': 'Titre Photo 60', 'type': 'Texte', 'obligatoire': False},

    # --- Bloc 10: Informations administratives et légales (161-170) ---
    {'rang': 161, 'nom': 'DPE Consommation', 'type': 'Entier', 'obligatoire': False},
    {'rang': 162, 'nom': 'DPE Lettre', 'type': 'Texte', 'obligatoire': False},
    {'rang': 163, 'nom': 'GES Emission', 'type': 'Entier', 'obligatoire': False},
    {'rang': 164, 'nom': 'GES Lettre', 'type': 'Texte', 'obligatoire': False},
    {'rang': 165, 'nom': 'Numéro Mandat', 'type': 'Texte', 'obligatoire': False},
    {'rang': 166, 'nom': 'Exclusivité', 'type': 'Texte', 'obligatoire': False},
    {'rang': 167, 'nom': 'Charges', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 168, 'nom': 'Taxe Foncière', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 169, 'nom': 'Dépôt Garantie', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 170, 'nom': 'Charges Acquéreur', 'type': 'Texte', 'obligatoire': False},

    # --- Bloc 11: Champs Divers (171-200) ---
    {'rang': 171, 'nom': 'Inter-cabinet', 'type': 'Texte', 'obligatoire': False},
    {'rang': 172, 'nom': 'Latitude', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 173, 'nom': 'Longitude', 'type': 'Décimal', 'obligatoire': False},
    {'rang': 174, 'nom': 'URL Visite Virtuelle', 'type': 'Texte', 'obligatoire': False},
    {'rang': 175, 'nom': 'URL Vidéo', 'type': 'Texte', 'obligatoire': False},
    {'rang': 176, 'nom': 'Programme neuf', 'type': 'Texte', 'obligatoire': False},
    {'rang': 177, 'nom': 'Nom du programme', 'type': 'Texte', 'obligatoire': False},
    {'rang': 178, 'nom': 'URL Programme', 'type': 'Texte', 'obligatoire': False},
    {'rang': 179, 'nom': 'Champ libre 1', 'type': 'Texte', 'obligatoire': False},
    {'rang': 180, 'nom': 'Champ libre 2', 'type': 'Texte', 'obligatoire': False},
    {'rang': 181, 'nom': 'Champ libre 3', 'type': 'Texte', 'obligatoire': False},
    {'rang': 182, 'nom': 'Champ libre 4', 'type': 'Texte', 'obligatoire': False},
    {'rang': 183, 'nom': 'Champ libre 5', 'type': 'Texte', 'obligatoire': False},
    {'rang': 184, 'nom': 'Champ libre 6', 'type': 'Texte', 'obligatoire': False},
    {'rang': 185, 'nom': 'Champ libre 7', 'type': 'Texte', 'obligatoire': False},
    {'rang': 186, 'nom': 'Champ libre 8', 'type': 'Texte', 'obligatoire': False},
    {'rang': 187, 'nom': 'Champ libre 9', 'type': 'Texte', 'obligatoire': False},
    {'rang': 188, 'nom': 'Champ libre 10', 'type': 'Texte', 'obligatoire': False},
    {'rang': 189, 'nom': 'Champ libre 11', 'type': 'Texte', 'obligatoire': False},
    {'rang': 190, 'nom': 'Champ libre 12', 'type': 'Texte', 'obligatoire': False},
    {'rang': 191, 'nom': 'Champ libre 13', 'type': 'Texte', 'obligatoire': False},
    {'rang': 192, 'nom': 'Champ libre 14', 'type': 'Texte', 'obligatoire': False},
    {'rang': 193, 'nom': 'Champ libre 15', 'type': 'Texte', 'obligatoire': False},
    {'rang': 194, 'nom': 'Champ libre 16', 'type': 'Texte', 'obligatoire': False},
    {'rang': 195, 'nom': 'Champ libre 17', 'type': 'Texte', 'obligatoire': False},
    {'rang': 196, 'nom': 'Champ libre 18', 'type': 'Texte', 'obligatoire': False},
    {'rang': 197, 'nom': 'Champ libre 19', 'type': 'Texte', 'obligatoire': False},
    {'rang': 198, 'nom': 'Champ libre 20', 'type': 'Texte', 'obligatoire': False},
    {'rang': 199, 'nom': 'Champ libre 21', 'type': 'Texte', 'obligatoire': False},
    {'rang': 200, 'nom': 'Champ libre 22', 'type': 'Texte', 'obligatoire': False},

    # --- Bloc 12: Contact Agence (201-210) ---
    {'rang': 201, 'nom': 'Contact Nom', 'type': 'Texte', 'obligatoire': False},
    {'rang': 202, 'nom': 'Contact Prénom', 'type': 'Texte', 'obligatoire': False},
    {'rang': 203, 'nom': 'Contact Téléphone', 'type': 'Texte', 'obligatoire': False},
    {'rang': 204, 'nom': 'Contact Email', 'type': 'Texte', 'obligatoire': False},
    {'rang': 205, 'nom': 'Contact Site Web', 'type': 'Texte', 'obligatoire': False},
    {'rang': 206, 'nom': 'Agence Nom', 'type': 'Texte', 'obligatoire': False},
    {'rang': 207, 'nom': 'Agence Adresse', 'type': 'Texte', 'obligatoire': False},
    {'rang': 208, 'nom': 'Agence CP', 'type': 'Texte', 'obligatoire': False},
    {'rang': 209, 'nom': 'Agence Ville', 'type': 'Texte', 'obligatoire': False},
    {'rang': 210, 'nom': 'Agence Téléphone', 'type': 'Texte', 'obligatoire': False},

    # --- Remplissage des champs restants (211-334) ---
    {'rang': 211, 'nom': 'Champ Poliris 211', 'type': 'Texte', 'obligatoire': False},
    {'rang': 212, 'nom': 'Champ Poliris 212', 'type': 'Texte', 'obligatoire': False},
    {'rang': 213, 'nom': 'Champ Poliris 213', 'type': 'Texte', 'obligatoire': False},
    {'rang': 214, 'nom': 'Champ Poliris 214', 'type': 'Texte', 'obligatoire': False},
    {'rang': 215, 'nom': 'Champ Poliris 215', 'type': 'Texte', 'obligatoire': False},
    {'rang': 216, 'nom': 'Champ Poliris 216', 'type': 'Texte', 'obligatoire': False},
    {'rang': 217, 'nom': 'Champ Poliris 217', 'type': 'Texte', 'obligatoire': False},
    {'rang': 218, 'nom': 'Champ Poliris 218', 'type': 'Texte', 'obligatoire': False},
    {'rang': 219, 'nom': 'Champ Poliris 219', 'type': 'Texte', 'obligatoire': False},
    {'rang': 220, 'nom': 'Champ Poliris 220', 'type': 'Texte', 'obligatoire': False},
    {'rang': 221, 'nom': 'Champ Poliris 221', 'type': 'Texte', 'obligatoire': False},
    {'rang': 222, 'nom': 'Champ Poliris 222', 'type': 'Texte', 'obligatoire': False},
    {'rang': 223, 'nom': 'Champ Poliris 223', 'type': 'Texte', 'obligatoire': False},
    {'rang': 224, 'nom': 'Champ Poliris 224', 'type': 'Texte', 'obligatoire': False},
    {'rang': 225, 'nom': 'Champ Poliris 225', 'type': 'Texte', 'obligatoire': False},
    {'rang': 226, 'nom': 'Champ Poliris 226', 'type': 'Texte', 'obligatoire': False},
    {'rang': 227, 'nom': 'Champ Poliris 227', 'type': 'Texte', 'obligatoire': False},
    {'rang': 228, 'nom': 'Champ Poliris 228', 'type': 'Texte', 'obligatoire': False},
    {'rang': 229, 'nom': 'Champ Poliris 229', 'type': 'Texte', 'obligatoire': False},
    {'rang': 230, 'nom': 'Champ Poliris 230', 'type': 'Texte', 'obligatoire': False},
    {'rang': 231, 'nom': 'Champ Poliris 231', 'type': 'Texte', 'obligatoire': False},
    {'rang': 232, 'nom': 'Champ Poliris 232', 'type': 'Texte', 'obligatoire': False},
    {'rang': 233, 'nom': 'Champ Poliris 233', 'type': 'Texte', 'obligatoire': False},
    {'rang': 234, 'nom': 'Champ Poliris 234', 'type': 'Texte', 'obligatoire': False},
    {'rang': 235, 'nom': 'Champ Poliris 235', 'type': 'Texte', 'obligatoire': False},
    {'rang': 236, 'nom': 'Champ Poliris 236', 'type': 'Texte', 'obligatoire': False},
    {'rang': 237, 'nom': 'Champ Poliris 237', 'type': 'Texte', 'obligatoire': False},
    {'rang': 238, 'nom': 'Champ Poliris 238', 'type': 'Texte', 'obligatoire': False},
    {'rang': 239, 'nom': 'Champ Poliris 239', 'type': 'Texte', 'obligatoire': False},
    {'rang': 240, 'nom': 'Champ Poliris 240', 'type': 'Texte', 'obligatoire': False},
    {'rang': 241, 'nom': 'Champ Poliris 241', 'type': 'Texte', 'obligatoire': False},
    {'rang': 242, 'nom': 'Champ Poliris 242', 'type': 'Texte', 'obligatoire': False},
    {'rang': 243, 'nom': 'Champ Poliris 243', 'type': 'Texte', 'obligatoire': False},
    {'rang': 244, 'nom': 'Champ Poliris 244', 'type': 'Texte', 'obligatoire': False},
    {'rang': 245, 'nom': 'Champ Poliris 245', 'type': 'Texte', 'obligatoire': False},
    {'rang': 246, 'nom': 'Champ Poliris 246', 'type': 'Texte', 'obligatoire': False},
    {'rang': 247, 'nom': 'Champ Poliris 247', 'type': 'Texte', 'obligatoire': False},
    {'rang': 248, 'nom': 'Champ Poliris 248', 'type': 'Texte', 'obligatoire': False},
    {'rang': 249, 'nom': 'Champ Poliris 249', 'type': 'Texte', 'obligatoire': False},
    {'rang': 250, 'nom': 'Champ Poliris 250', 'type': 'Texte', 'obligatoire': False},
    {'rang': 251, 'nom': 'Champ Poliris 251', 'type': 'Texte', 'obligatoire': False},
    {'rang': 252, 'nom': 'Champ Poliris 252', 'type': 'Texte', 'obligatoire': False},
    {'rang': 253, 'nom': 'Champ Poliris 253', 'type': 'Texte', 'obligatoire': False},
    {'rang': 254, 'nom': 'Champ Poliris 254', 'type': 'Texte', 'obligatoire': False},
    {'rang': 255, 'nom': 'Champ Poliris 255', 'type': 'Texte', 'obligatoire': False},
    {'rang': 256, 'nom': 'Champ Poliris 256', 'type': 'Texte', 'obligatoire': False},
    {'rang': 257, 'nom': 'Champ Poliris 257', 'type': 'Texte', 'obligatoire': False},
    {'rang': 258, 'nom': 'Champ Poliris 258', 'type': 'Texte', 'obligatoire': False},
    {'rang': 259, 'nom': 'Champ Poliris 259', 'type': 'Texte', 'obligatoire': False},
    {'rang': 260, 'nom': 'Champ Poliris 260', 'type': 'Texte', 'obligatoire': False},
    {'rang': 261, 'nom': 'Champ Poliris 261', 'type': 'Texte', 'obligatoire': False},
    {'rang': 262, 'nom': 'Champ Poliris 262', 'type': 'Texte', 'obligatoire': False},
    {'rang': 263, 'nom': 'Champ Poliris 263', 'type': 'Texte', 'obligatoire': False},
    {'rang': 264, 'nom': 'Champ Poliris 264', 'type': 'Texte', 'obligatoire': False},
    {'rang': 265, 'nom': 'Champ Poliris 265', 'type': 'Texte', 'obligatoire': False},
    {'rang': 266, 'nom': 'Champ Poliris 266', 'type': 'Texte', 'obligatoire': False},
    {'rang': 267, 'nom': 'Champ Poliris 267', 'type': 'Texte', 'obligatoire': False},
    {'rang': 268, 'nom': 'Champ Poliris 268', 'type': 'Texte', 'obligatoire': False},
    {'rang': 269, 'nom': 'Champ Poliris 269', 'type': 'Texte', 'obligatoire': False},
    {'rang': 270, 'nom': 'Champ Poliris 270', 'type': 'Texte', 'obligatoire': False},
    {'rang': 271, 'nom': 'Champ Poliris 271', 'type': 'Texte', 'obligatoire': False},
    {'rang': 272, 'nom': 'Champ Poliris 272', 'type': 'Texte', 'obligatoire': False},
    {'rang': 273, 'nom': 'Champ Poliris 273', 'type': 'Texte', 'obligatoire': False},
    {'rang': 274, 'nom': 'Champ Poliris 274', 'type': 'Texte', 'obligatoire': False},
    {'rang': 275, 'nom': 'Champ Poliris 275', 'type': 'Texte', 'obligatoire': False},
    {'rang': 276, 'nom': 'Champ Poliris 276', 'type': 'Texte', 'obligatoire': False},
    {'rang': 277, 'nom': 'Champ Poliris 277', 'type': 'Texte', 'obligatoire': False},
    {'rang': 278, 'nom': 'Champ Poliris 278', 'type': 'Texte', 'obligatoire': False},
    {'rang': 279, 'nom': 'Champ Poliris 279', 'type': 'Texte', 'obligatoire': False},
    {'rang': 280, 'nom': 'Champ Poliris 280', 'type': 'Texte', 'obligatoire': False},
    {'rang': 281, 'nom': 'Champ Poliris 281', 'type': 'Texte', 'obligatoire': False},
    {'rang': 282, 'nom': 'Champ Poliris 282', 'type': 'Texte', 'obligatoire': False},
    {'rang': 283, 'nom': 'Champ Poliris 283', 'type': 'Texte', 'obligatoire': False},
    {'rang': 284, 'nom': 'Champ Poliris 284', 'type': 'Texte', 'obligatoire': False},
    {'rang': 285, 'nom': 'Champ Poliris 285', 'type': 'Texte', 'obligatoire': False},
    {'rang': 286, 'nom': 'Champ Poliris 286', 'type': 'Texte', 'obligatoire': False},
    {'rang': 287, 'nom': 'Champ Poliris 287', 'type': 'Texte', 'obligatoire': False},
    {'rang': 288, 'nom': 'Champ Poliris 288', 'type': 'Texte', 'obligatoire': False},
    {'rang': 289, 'nom': 'Champ Poliris 289', 'type': 'Texte', 'obligatoire': False},
    {'rang': 290, 'nom': 'Champ Poliris 290', 'type': 'Texte', 'obligatoire': False},
    {'rang': 291, 'nom': 'Champ Poliris 291', 'type': 'Texte', 'obligatoire': False},
    {'rang': 292, 'nom': 'Champ Poliris 292', 'type': 'Texte', 'obligatoire': False},
    {'rang': 293, 'nom': 'Champ Poliris 293', 'type': 'Texte', 'obligatoire': False},
    {'rang': 294, 'nom': 'Champ Poliris 294', 'type': 'Texte', 'obligatoire': False},
    {'rang': 295, 'nom': 'Champ Poliris 295', 'type': 'Texte', 'obligatoire': False},
    {'rang': 296, 'nom': 'Champ Poliris 296', 'type': 'Texte', 'obligatoire': False},
    {'rang': 297, 'nom': 'Champ Poliris 297', 'type': 'Texte', 'obligatoire': False},
    {'rang': 298, 'nom': 'Champ Poliris 298', 'type': 'Texte', 'obligatoire': False},
    {'rang': 299, 'nom': 'Champ Poliris 299', 'type': 'Texte', 'obligatoire': False},
    {'rang': 300, 'nom': 'Champ Poliris 300', 'type': 'Texte', 'obligatoire': False},
    {'rang': 301, 'nom': 'Champ Poliris 301', 'type': 'Texte', 'obligatoire': False},
    {'rang': 302, 'nom': 'Champ Poliris 302', 'type': 'Texte', 'obligatoire': False},
    {'rang': 303, 'nom': 'Champ Poliris 303', 'type': 'Texte', 'obligatoire': False},
    {'rang': 304, 'nom': 'Champ Poliris 304', 'type': 'Texte', 'obligatoire': False},
    {'rang': 305, 'nom': 'Champ Poliris 305', 'type': 'Texte', 'obligatoire': False},
    {'rang': 306, 'nom': 'Champ Poliris 306', 'type': 'Texte', 'obligatoire': False},
    {'rang': 307, 'nom': 'Champ Poliris 307', 'type': 'Texte', 'obligatoire': False},
    {'rang': 308, 'nom': 'Champ Poliris 308', 'type': 'Texte', 'obligatoire': False},
    {'rang': 309, 'nom': 'Champ Poliris 309', 'type': 'Texte', 'obligatoire': False},
    {'rang': 310, 'nom': 'Champ Poliris 310', 'type': 'Texte', 'obligatoire': False},
    {'rang': 311, 'nom': 'Champ Poliris 311', 'type': 'Texte', 'obligatoire': False},
    {'rang': 312, 'nom': 'Champ Poliris 312', 'type': 'Texte', 'obligatoire': False},
    {'rang': 313, 'nom': 'Champ Poliris 313', 'type': 'Texte', 'obligatoire': False},
    {'rang': 314, 'nom': 'Champ Poliris 314', 'type': 'Texte', 'obligatoire': False},
    {'rang': 315, 'nom': 'Champ Poliris 315', 'type': 'Texte', 'obligatoire': False},
    {'rang': 316, 'nom': 'Champ Poliris 316', 'type': 'Texte', 'obligatoire': False},
    {'rang': 317, 'nom': 'Champ Poliris 317', 'type': 'Texte', 'obligatoire': False},
    {'rang': 318, 'nom': 'Champ Poliris 318', 'type': 'Texte', 'obligatoire': False},
    {'rang': 319, 'nom': 'Champ Poliris 319', 'type': 'Texte', 'obligatoire': False},
    {'rang': 320, 'nom': 'Champ Poliris 320', 'type': 'Texte', 'obligatoire': False},
    {'rang': 321, 'nom': 'Champ Poliris 321', 'type': 'Texte', 'obligatoire': False},
    {'rang': 322, 'nom': 'Champ Poliris 322', 'type': 'Texte', 'obligatoire': False},
    {'rang': 323, 'nom': 'Champ Poliris 323', 'type': 'Texte', 'obligatoire': False},
    {'rang': 324, 'nom': 'Champ Poliris 324', 'type': 'Texte', 'obligatoire': False},
    {'rang': 325, 'nom': 'Champ Poliris 325', 'type': 'Texte', 'obligatoire': False},
    {'rang': 326, 'nom': 'Champ Poliris 326', 'type': 'Texte', 'obligatoire': False},
    {'rang': 327, 'nom': 'Champ Poliris 327', 'type': 'Texte', 'obligatoire': False},
    {'rang': 328, 'nom': 'Champ Poliris 328', 'type': 'Texte', 'obligatoire': False},
    {'rang': 329, 'nom': 'Champ Poliris 329', 'type': 'Texte', 'obligatoire': False},
    {'rang': 330, 'nom': 'Champ Poliris 330', 'type': 'Texte', 'obligatoire': False},
    {'rang': 331, 'nom': 'Champ Poliris 331', 'type': 'Texte', 'obligatoire': False},
    {'rang': 332, 'nom': 'Champ Poliris 332', 'type': 'Texte', 'obligatoire': False},
    {'rang': 333, 'nom': 'Champ Poliris 333', 'type': 'Texte', 'obligatoire': False},
    {'rang': 334, 'nom': 'Champ Poliris 334', 'type': 'Texte', 'obligatoire': False},
]
nb_champs_definis = len(SCHEMA)
placeholders = [{'rang': i + 1, 'nom': f'Champ non-défini {i+1}', 'type': 'Texte', 'obligatoire': False} for i in range(nb_champs_definis, 334)]
SCHEMA.extend(placeholders)

# =============================================================================
# BLOC DE VALIDATION MODULAIRE
# =============================================================================
def check_obligatoire(value, rule):
    if rule.get('obligatoire') and not value: return 'Le champ obligatoire est vide.'
    return None

def check_type_entier(value, rule):
    if rule.get('type') == 'Entier' and not value.isdigit(): return 'Doit être un entier.'
    return None

def check_type_decimal(value, rule):
    if rule.get('type') == 'Décimal' and not pd.to_numeric(value.replace(',', '.'), errors='coerce'): return 'Doit être un nombre.'
    return None
    
def check_type_date(value, rule):
    if rule.get('type') == 'Date':
        try: datetime.strptime(value, '%d/%m/%Y')
        except ValueError: return f"Format de date invalide. La valeur est {repr(value)}."
    return None

def check_valeurs_permises(value, rule):
    if rule.get('valeurs') and value not in rule.get('valeurs', []): return f'Valeur non autorisée. Attendues: {rule["valeurs"]}'
    return None

TYPE_VALIDATION_PIPELINE = [check_type_entier, check_type_decimal, check_type_date, check_valeurs_permises]

def validate_row(row_num, row_data):
    errors = []
    annonce_ref = row_data[REF_ANNONCE_INDEX] if len(row_data) > REF_ANNONCE_INDEX else 'N/A'
    for i, clean_value in enumerate(row_data):
        rule = SCHEMA[i]
        error_template = {'Ligne': row_num, 'Référence Annonce': annonce_ref, 'Rang': rule['rang'], 'Champ': rule['nom'], 'Valeur': f'"{clean_value}"'}
        if not clean_value:
            error_message = check_obligatoire(clean_value, rule)
            if error_message:
                error_template['Message'] = error_message
                errors.append(error_template)
            continue
        for validation_function in TYPE_VALIDATION_PIPELINE:
            error_message = validation_function(clean_value, rule)
            if error_message:
                error_template['Message'] = error_message
                errors.append(error_template)
                break
    return errors

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
def try_decode(data_bytes):
    for encoding in ['utf-8', 'ISO-8859-1', 'windows-1252']:
        try: return data_bytes.decode(encoding), encoding
        except UnicodeDecodeError: continue
    return None, None

def style_error_rows(row, error_row_indices):
    return ['background-color: rgba(255, 204, 204, 0.6)'] * len(row) if row.name in error_row_indices else [''] * len(row)

# =============================================================================
# INTERFACE PRINCIPALE (STREAMLIT)
# =============================================================================
def main():
    st.set_page_config(layout="wide", page_title="Validateur Figaro Immo")
    st.title("✅ Validateur de Fichier Poliris")

    try:
        with open(HEADER_FILE, 'rb') as f: header_bytes = f.read()
        decoded_content, _ = try_decode(header_bytes)
        if decoded_content is None:
            st.error(f"Erreur config : Impossible de lire `{HEADER_FILE}`. Encodage non supporté.")
            return
        headers_df = pd.read_csv(io.StringIO(decoded_content), header=None, sep=';')
        column_headers = headers_df.iloc[1].tolist()
        if len(column_headers) != EXPECTED_COLUMNS:
            st.error(f"Erreur config : Le fichier d'en-têtes `{HEADER_FILE}` est incorrect.")
            return
    except FileNotFoundError:
        st.error(f"Fichier config manquant : `{HEADER_FILE}` introuvable.")
        return
    except IndexError:
        st.error(f"Erreur config : Impossible de lire la 2ème ligne de `{HEADER_FILE}`.")
        return

    uploaded_file = st.file_uploader("1. Chargez votre fichier d'annonces", type=['csv', 'txt'])

    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_content, detected_encoding = try_decode(file_bytes)
        if file_content is None:
            st.error("Impossible de lire le fichier. Aucun encodage compatible trouvé.")
            return
        st.info(f"Fichier lu avec l'encodage : **{detected_encoding}**")
        
        all_errors, data_rows = [], []
        
        normalized_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
        lines = normalized_content.strip().split('\n')

        for i, line in enumerate(lines):
            if not line: continue
            
            fields = line.split('#')
            
            # --- LA CORRECTION EST ICI ---
            # On applique une séquence de nettoyage robuste à chaque champ
            cleaned_row = [field.rstrip('!').strip('"').strip() for field in fields]
            
            if len(cleaned_row) != EXPECTED_COLUMNS:
                all_errors.append({'Ligne': i + 1, 'Référence Annonce': 'N/A', 'Rang': 'N/A', 'Champ': 'Général', 'Message': f"Erreur de structure (attendu: {EXPECTED_COLUMNS} champs, trouvé: {len(cleaned_row)}).", 'Valeur': 'Ligne non affichée.'})
                continue
                
            data_rows.append(cleaned_row)
            all_errors.extend(validate_row(i + 1, cleaned_row))

        st.header("2. Visualisation des Données")
        if data_rows:
            df = pd.DataFrame(data_rows, columns=column_headers)
            error_row_indices = {error['Ligne'] - 1 for error in all_errors}
            st.dataframe(df.style.apply(style_error_rows, error_row_indices=error_row_indices, axis=1), use_container_width=True, height=600)
        elif all_errors:
             st.warning("Aucune donnée à afficher car toutes les lignes présentent une erreur de structure majeure.")
        else:
             st.info("Le fichier est vide ou ne contient aucune donnée à afficher.")

        st.header("3. Rapport d'Erreurs")
        if not all_errors:
            st.success("🎉 Félicitations ! Aucune erreur détectée.")
        else:
            st.error(f"Le fichier contient {len(all_errors)} erreur(s).")
            column_config = {"Ligne": st.column_config.NumberColumn(width="small"), "Rang": st.column_config.NumberColumn(width="small"), "Champ": st.column_config.TextColumn(width="medium"), "Message": st.column_config.TextColumn(width="large")}
            errors_df = pd.DataFrame(all_errors)[['Ligne', 'Référence Annonce', 'Rang', 'Champ', 'Message', 'Valeur']]
            st.dataframe(errors_df, column_config=column_config, use_container_width=True)

    st.markdown(f'<div style="text-align: center; color: grey; font-size: 0.8em; padding-top: 2em;">Version {__version__}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Une erreur fatale et non prévue a provoqué le crash de l'application.")
        st.exception(e)
