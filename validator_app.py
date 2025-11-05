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
   {'rang': 1, 'nom': 'Identifiant agence', 'obligatoire': True, 'type': 'Entier', 'maxLength': 20},
    {'rang': 2, 'nom': 'Référence agence du bien', 'obligatoire': True, 'type': 'Texte', 'maxLength': 20},
    {'rang': 3, 'nom': 'Type d\'annonce', 'obligatoire': True, 'type': 'Texte', 'valeurs': ['cession de bail', 'location', 'location vacances', 'produit d\'investissement', 'vente', 'vente de prestige', 'vente fonds-de-commerce', 'viager']},
    {'rang': 4, 'nom': 'Type de bien', 'obligatoire': True, 'type': 'Texte' },
    {'rang': 5, 'nom': 'Code postal', 'obligatoire': True, 'type': 'Texte', 'maxLength': 5},
    {'rang': 6, 'nom': 'Ville', 'obligatoire': True, 'type': 'Texte', 'maxLength': 50},
    {'rang': 7, 'nom': 'Pays', 'obligatoire': True, 'type': 'Texte', 'valeurs': ['France']},
    {'rang': 8, 'nom': 'Adresse', 'obligatoire': False, 'type': 'Texte', 'maxLength': 128},
    {'rang': 9, 'nom': 'Quartier', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 10, 'nom': 'Activités commerciales', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 11, 'nom': 'Prix / Loyer / Prix de cession', 'obligatoire': True, 'type': 'Décimal'},
    {'rang': 12, 'nom': 'Loyer / mois murs', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 13, 'nom': 'Loyer CC', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 14, 'nom': 'Loyer HT', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 15, 'nom': 'Honoraires', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 16, 'nom': 'Surface (m²)', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 17, 'nom': 'SF terrain (m²)', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 18, 'nom': 'NB de pièces', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 19, 'nom': 'NB de chambres', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 20, 'nom': 'Libellé', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 21, 'nom': 'Descriptif', 'obligatoire': True, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 22, 'nom': 'Date de disponibilité', 'obligatoire': False, 'type': 'Date'},
    {'rang': 23, 'nom': 'Charges', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 24, 'nom': 'Etage', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 25, 'nom': 'NB d\’étages', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 26, 'nom': 'Meublé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 27, 'nom': 'Année de construction', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 28, 'nom': 'Refait à neuf', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 29, 'nom': 'NB de salles de bain', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 30, 'nom': 'Nombre de salles d\'eau', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 31, 'nom': 'Nombre de WC', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 32, 'nom': 'WC séparés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 33, 'nom': 'Type de chauffage', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 34, 'nom': 'Type de cuisine', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 35, 'nom': 'Orientation sud', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 36, 'nom': 'Orientation est', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 37, 'nom': 'Orientation ouest', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 38, 'nom': 'Orientation nord', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 39, 'nom': 'NB balcons', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 40, 'nom': 'SF balcon', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 41, 'nom': 'Ascenseur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 42, 'nom': 'Cave', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 43, 'nom': 'NB de parkings', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 44, 'nom': 'NB de box', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 45, 'nom': 'Digicode', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 46, 'nom': 'Interphone', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 47, 'nom': 'Gardien', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 48, 'nom': 'Terrasse', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 49, 'nom': 'Prix semaine Basse Saison', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 50, 'nom': 'Prix quinzaine Basse Saison', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 51, 'nom': 'Prix mois / Basse Saison', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 52, 'nom': 'Prix semaine Haute Saison', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 53, 'nom': 'Prix quinzaine Haute Saison', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 54, 'nom': 'Prix mois / Haute Saison', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 55, 'nom': 'NB de personnes', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 56, 'nom': 'Type de résidence', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 57, 'nom': 'Situation', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['montagne', 'mer', 'campagne', 'ville']},
    {'rang': 58, 'nom': 'NB de couverts', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 59, 'nom': 'NB de lits doubles', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 60, 'nom': 'NB de lits simples', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 61, 'nom': 'Alarme', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 62, 'nom': 'Câble TV', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 63, 'nom': 'Calme', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 64, 'nom': 'Climatisation', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 65, 'nom': 'Piscine', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 66, 'nom': 'Aménagement pour handicapés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 67, 'nom': 'Animaux acceptés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 68, 'nom':'Cheminée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 69, 'nom':'Congélateur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 70, 'nom':'Four', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 71, 'nom':'Lave-vaisselle', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 72, 'nom':'Micro-ondes', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 73, 'nom':'Placards', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 74, 'nom':'Téléphone', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 75, 'nom':'Proche lac', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 76, 'nom':'Proche tennis', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 77, 'nom':'Proche pistes de ski', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 78, 'nom':'Vue dégagée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 79, 'nom': 'Chiffre d\’affaire', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 80, 'nom': 'Longueur façade (m)', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 81, 'nom': 'Duplex', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 82, 'nom': 'Publications', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['SL', 'BD', 'WA']},
    {'rang': 83, 'nom': 'Mandat en exclusivité', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 84, 'nom': 'Coup de coeur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 85, 'nom': 'Photo 1', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 86, 'nom': 'Photo 2', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 87, 'nom': 'Photo 3', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 88, 'nom': 'Photo 4', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 89, 'nom': 'Photo 5', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 90, 'nom': 'Photo 6', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 91, 'nom': 'Photo 7', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 92, 'nom': 'Photo 8', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 93, 'nom': 'Photo 9', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 94, 'nom': 'Titre photo 1', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 95, 'nom': 'Titre photo 2', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 96, 'nom': 'Titre photo 3', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 97, 'nom': 'Titre photo 4', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 98, 'nom': 'Titre photo 5', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 99, 'nom': 'Titre photo 6', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 100, 'nom': 'Titre photo 7', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 101, 'nom': 'Titre photo 8', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 102, 'nom': 'Titre photo 9', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 103, 'nom': 'Photo panoramique', 'obligatoire': False, 'type': 'Texte', 'maxLength': 128},
    {'rang': 104, 'nom': 'URL visite virtuelle', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 105, 'nom': 'Téléphone à afficher', 'obligatoire': False, 'type': 'Texte', 'maxLength': 10},
    {'rang': 106, 'nom': 'Contact à afficher', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 107, 'nom': 'Email de contact', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 108, 'nom': 'CP Réel du bien', 'obligatoire': False, 'type': 'Texte', 'maxLength': 5},
    {'rang': 109, 'nom': 'Ville réelle du bien', 'obligatoire': False, 'type': 'Texte', 'maxLength': 50},
    {'rang': 110, 'nom': 'Inter-cabinet', 'obligatoire': False, 'type': 'Texte', 'maxLength': 3},
    {'rang': 111, 'nom': 'Inter-cabinet prive', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 112, 'nom': 'N° de mandat', 'obligatoire': False, 'type': 'Texte', 'maxLength': 15},
    {'rang': 113, 'nom': 'Date mandat', 'obligatoire': False, 'type': 'Date', 'format': 'DD-MM-YYYY'},
    {'rang': 114, 'nom': 'Nom mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 115, 'nom': 'Prénom mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 116, 'nom': 'Raison sociale mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 117, 'nom': 'Adresse mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 128},
    {'rang': 118, 'nom': 'CP mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 5},
    {'rang': 119, 'nom': 'Ville mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 50},
    {'rang': 120, 'nom': 'Téléphone mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 10},
    {'rang': 121, 'nom': 'Commentaires mandataire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 122, 'nom': 'Commentaires privés', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 123, 'nom': 'Code négociateur', 'obligatoire': False, 'type': 'Texte', 'maxLength': 50},
    {'rang': 124, 'nom': 'Code Langue 1', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['EN', 'ES', 'DE', 'IT', 'NL', 'PT'], 'maxLength': 3},
    {'rang': 125, 'nom': 'Proximité Langue 1', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 126, 'nom': 'Libellé Langue 1', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 127, 'nom': 'Descriptif Langue 1', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 128, 'nom': 'Code Langue 2', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['EN', 'ES', 'DE', 'IT', 'NL', 'PT'], 'maxLength': 3},
    {'rang': 129, 'nom': 'Proximité Langue 2', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 130, 'nom': 'Libellé Langue 2', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 131, 'nom': 'Descriptif Langue 2', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 132, 'nom': 'Code Langue 3', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['EN', 'ES', 'DE', 'IT', 'NL', 'PT'], 'maxLength': 3},
    {'rang': 133, 'nom': 'Proximité Langue 3', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 134, 'nom': 'Libellé Langue 3', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 135, 'nom': 'Descriptif Langue 3', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 136, 'nom': 'Champ personnalisé 1', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 137, 'nom': 'Champ personnalisé 2', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 138, 'nom': 'Champ personnalisé 3', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 139, 'nom': 'Champ personnalisé 4', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 140, 'nom': 'Champ personnalisé 5', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 141, 'nom': 'Champ personnalisé 6', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 142, 'nom': 'Champ personnalisé 7', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 143, 'nom': 'Champ personnalisé 8', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 144, 'nom': 'Champ personnalisé 9', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 145, 'nom': 'Champ personnalisé 10', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 146, 'nom': 'Champ personnalisé 11', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 147, 'nom': 'Champ personnalisé 12', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 148, 'nom': 'Champ personnalisé 13', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 149, 'nom': 'Champ personnalisé 14', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 150, 'nom': 'Champ personnalisé 15', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 151, 'nom': 'Champ personnalisé 16', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 152, 'nom': 'Champ personnalisé 17', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 153, 'nom': 'Champ personnalisé 18', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 154, 'nom': 'Champ personnalisé 19', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 155, 'nom': 'Champ personnalisé 20', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 156, 'nom': 'Champ personnalisé 21', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 157, 'nom': 'Champ personnalisé 22', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 158, 'nom': 'Champ personnalisé 23', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 159, 'nom': 'Champ personnalisé 24', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 160, 'nom': 'Champ personnalisé 25', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 161, 'nom': 'Dépôt de garantie', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 162, 'nom': 'Récent', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 163, 'nom': 'Travaux à prévoir', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 164, 'nom': 'Photo 10', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 165, 'nom': 'Photo 11', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 166, 'nom': 'Photo 12', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 167, 'nom': 'Photo 13', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 168, 'nom': 'Photo 14', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 169, 'nom': 'Photo 15', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 170, 'nom': 'Photo 16', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 171, 'nom': 'Photo 17', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 172, 'nom': 'Photo 18', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 173, 'nom': 'Photo 19', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 174, 'nom': 'Photo 20', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 175, 'nom': 'Identifiant technique', 'obligatoire': True, 'type': 'Texte', 'maxLength': 30},
    {'rang': 176, 'nom': 'Consommation énergie', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 177, 'nom': 'Bilan consommation énergie', 'obligatoire': False, 'type': 'Texte', 'maxLength': 2},
    {'rang': 178, 'nom': 'Emissions GES', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 179, 'nom': 'Bilan émission GES', 'obligatoire': False, 'type': 'Texte', 'maxLength': 2},
    {'rang': 180, 'nom': 'Identifiant quartier', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 181, 'nom': 'Sous type de bien', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 182, 'nom': 'Périodes de disponibilité', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 183, 'nom': 'Périodes basse saison', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 184, 'nom': 'Périodes haute saison', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 185, 'nom': 'Prix du bouquet', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 186, 'nom': 'Droit au bail', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 187, 'nom': 'Age de l\’homme', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 188, 'nom': 'Age de la femme', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 189, 'nom': 'Entrée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 190, 'nom': 'Résidence', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 191, 'nom': 'Parquet', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 192, 'nom': 'Vis-à-vis', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 193, 'nom': 'Transport : Ligne', 'obligatoire': False, 'type': 'Texte', 'maxLength': 5},
    {'rang': 194, 'nom': 'Transport : Station', 'obligatoire': False, 'type': 'Texte', 'maxLength': 32},
    {'rang': 195, 'nom': 'Durée bail', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 196, 'nom': 'Places en salle', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 197, 'nom': 'Monte-charge', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 198, 'nom': 'Quai', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 199, 'nom': 'Nombre de bureaux', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 200, 'nom': 'Prix du droit d’entrée', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 201, 'nom': 'Prix masqué', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 202, 'nom': 'Loyer annuel global', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 203, 'nom': 'Charges annuelles globales', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 204, 'nom': 'Loyer annuel au m2', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 205, 'nom': 'Charges annuelles au m2', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 206, 'nom': 'Charges mensuelles HT', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 207, 'nom': 'Loyer annuel CC', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 208, 'nom': 'Loyer annuel HT', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 209, 'nom': 'Charges annuelles HT', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 210, 'nom': 'Loyer annuel au m2 CC', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 211, 'nom': 'Loyer annuel au m2 HT', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 212, 'nom': 'Charges annuelles au m2 HT', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 213, 'nom': 'Divisible', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 214, 'nom': 'Surface divisible minimale', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 215, 'nom': 'Surface divisible maximale', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 216, 'nom': 'Surface séjour', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 217, 'nom': 'Nombre de véhicules', 'obligatoire': False, 'type': 'Entier', 'maxLength': 2},
    {'rang': 218, 'nom': 'Prix du droit au bail', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 219, 'nom': 'Valeur à l’achat', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 220, 'nom': 'Répartition du chiffre d’affaire', 'obligatoire': False, 'type': 'Texte', 'maxLength': 100},
    {'rang': 221, 'nom': 'Terrain agricole', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 222, 'nom': 'Equipement bébé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 223, 'nom': 'Terrain constructible', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 224, 'nom': 'Résultat Année N-2', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 225, 'nom': 'Résultat Année N-1', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 226, 'nom': 'Résultat Actuel', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 227, 'nom': 'Immeuble de parkings', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 228, 'nom': 'Parking isolé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 229, 'nom': 'Si Viager Vendu Libre', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 230, 'nom': 'Logement à disposition', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 231, 'nom': 'Terrain en pente', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 232, 'nom': 'Plan d’eau', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 233, 'nom': 'Lave-linge', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 234, 'nom': 'Sèche-linge', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 235, 'nom': 'Connexion internet', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 236, 'nom': 'Chiffre affaire Année N-2', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 237, 'nom': 'Chiffre affaire Année N-1', 'obligatoire': False,  'type': 'Entier'},
    {'rang': 238, 'nom': 'Conditions financières', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 239, 'nom': 'Prestations diverses', 'obligatoire': False, 'type': 'Texte', 'maxLength': 4000},
    {'rang': 240, 'nom': 'Longueur façade', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 241, 'nom': 'Montant du rapport', 'obligatoire': False, 'type': 'Texte', 'maxLength': 20},
    {'rang': 242, 'nom': 'Nature du bail', 'obligatoire': False, 'type': 'Texte', 'maxLength': 50},
    {'rang': 243, 'nom': 'Nature bail commercial', 'obligatoire': False, 'type': 'Texte', 'maxLength': 50},
    {'rang': 244, 'nom': 'Nombre terrasses', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 245, 'nom': 'Prix hors taxes', 'obligatoire': False, 'type': 'Texte','valeurs': ['oui', 'non']},
    {'rang': 246, 'nom': 'Si Salle à manger', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 247, 'nom': 'Si Séjour', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 248, 'nom': 'Terrain donne sur la rue', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 249, 'nom': 'Immeuble de type bureaux', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 250, 'nom': 'Terrain viabilisé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 251, 'nom': 'Equipement Vidéo', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 252, 'nom': 'Surface de la cave', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 253, 'nom': 'Surface de la salle à manger', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 254, 'nom': 'Situation commerciale', 'obligatoire': False, 'type': 'Texte', 'maxLength': 64},
    {'rang': 255, 'nom': 'Surface maximale d’un bureau', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 256, 'nom': 'Honoraires charge acquéreur (obsolète)', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 257, 'nom': 'Pourcentage honoraires TTC', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 258, 'nom': 'En copropriété', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 259, 'nom': 'Nombre de lots', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 260, 'nom': 'Charges annuelles', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 261, 'nom': 'Syndicat des copropriétaires en procédure', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 262, 'nom': 'Détail procédure du syndicat des copropriétaires', 'obligatoire': False, 'type': 'Texte', 'maxLength': 128},
    {'rang': 263, 'nom': 'Champ personnalisé 26', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 264, 'nom': 'Photo 21', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 265, 'nom': 'Photo 22', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 266, 'nom': 'Photo 23', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 267, 'nom': 'Photo 24', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 268, 'nom': 'Photo 25', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 269, 'nom': 'Photo 26', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 270, 'nom': 'Photo 27', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 271, 'nom': 'Photo 28', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 272, 'nom': 'Photo 29', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 273, 'nom': 'Photo 30', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 274, 'nom': 'Titre photo 10', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 275, 'nom': 'Titre photo 11', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 276, 'nom': 'Titre photo 12', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 277, 'nom': 'Titre photo 13', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 278, 'nom': 'Titre photo 14', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 279, 'nom': 'Titre photo 15', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 280, 'nom': 'Titre photo 16', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 281, 'nom': 'Titre photo 17', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 282, 'nom': 'Titre photo 18', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 283, 'nom': 'Titre photo 19', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 284, 'nom': 'Titre photo 20', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 285, 'nom': 'Titre photo 21', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 286, 'nom': 'Titre photo 22', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 287, 'nom': 'Titre photo 23', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 288, 'nom': 'Titre photo 24', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 289, 'nom': 'Titre photo 25', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 290, 'nom': 'Titre photo 26', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 291, 'nom': 'Titre photo 27', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 292, 'nom': 'Titre photo 28', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 293, 'nom': 'Titre photo 29', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 294, 'nom': 'Titre photo 30', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 295, 'nom': 'Prix du terrain', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 296, 'nom': 'Proche théâtre', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 297, 'nom': 'Nom de l\'agence gérant le terrain', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 298, 'nom': 'Latitude', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 299, 'nom': 'Longitude', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 300, 'nom': 'Précision GPS', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 301, 'nom': 'Version Format', 'obligatoire': False, 'type': 'Texte', 'maxLength': 10},
    {'rang': 302, 'nom': 'Honoraires à la charge de', 'obligatoire': False, 'type': 'Entier', 'valeurs': ['1', '2', '3']},
    {'rang': 303, 'nom': 'Prix hors honoraires acquéreur', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 304, 'nom': 'Modalités charges locataire', 'obligatoire': False, 'type': 'Entier', 'valeurs': ['1', '2', '3']},
    {'rang': 305, 'nom': 'Complément loyer', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 306, 'nom': 'Part honoraires état des lieux', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 307, 'nom': 'URL du Barème des honoraires de l’Agence', 'obligatoire': False, 'type': 'Texte', 'maxLength': 256},
    {'rang': 308, 'nom': 'Prix minimum', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 309, 'nom': 'Prix maximum', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 310, 'nom': 'Surface minimale', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 311, 'nom': 'Surface maximale', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 312, 'nom': 'Nombre de pièces minimum', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 313, 'nom': 'Nombre de pièces maximum', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 314, 'nom': 'Nombre de chambres minimum', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 315, 'nom': 'Nombre de chambres maximum', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 316, 'nom': 'ID type étage', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 317, 'nom': 'Si combles aménageables', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 318, 'nom': 'Si garage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 319, 'nom': 'ID type garage', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 320, 'nom': 'Si possibilité mitoyenneté', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 321, 'nom': 'Surface terrain nécessaire', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 322, 'nom': 'Localisation', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 323, 'nom': 'Nom du modèle', 'obligatoire': False, 'type': 'Texte', 'maxLength': 50},
    {'rang': 324, 'nom': 'Date réalisation DPE', 'obligatoire': False, 'type': 'Date', 'format': 'DD-MM-YYYY'},
    {'rang': 325, 'nom': 'Version DPE', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['DPE_v01-2011', 'DPE_v07-2021'], 'maxLength': 12},
    {'rang': 326, 'nom': 'DPE coût min conso', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 327, 'nom': 'DPE coût max conso', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 328, 'nom': 'DPE date référence conso', 'obligatoire': False, 'type': 'Date', 'format': 'DD-MM-YYYY'},
    {'rang': 329, 'nom': 'Surface terrasse', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 330, 'nom': 'DPE coût conso annuelle', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 331, 'nom': 'Loyer de base', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 332, 'nom': 'Loyer de référence majoré', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 333, 'nom': 'Encadrement des loyers', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non'], 'maxLength': 3},
    {'rang': 334, 'nom': 'Conso énergie finale', 'obligatoire': False, 'type': 'Entier'}
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
