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
    {'rang': 1, 'nom': 'Identifiant agence', 'obligatoire': True, 'type': 'Entier'},
    {'rang': 2, 'nom': 'Référence agence du bien', 'obligatoire': True, 'type': 'Texte'},
    {'rang': 3, 'nom': 'Type d\'annonce', 'obligatoire': True, 'type': 'Texte', 'valeurs': ['cession de bail', 'location', 'location vacances', 'produit d\'investissement', 'vente', 'vente de prestige', 'vente fonds-de-commerce', 'viager']},
    {'rang': 4, 'nom': 'Mandat', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['exclusif', 'simple']},
    {'rang': 5, 'nom': 'Code postal', 'obligatoire': True, 'type': 'Texte'},
    {'rang': 6, 'nom': 'Ville', 'obligatoire': True, 'type': 'Texte'},
    {'rang': 7, 'nom': 'Pays', 'obligatoire': True, 'type': 'Texte', 'valeurs': ['France']},
    {'rang': 8, 'nom': 'Quartier', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 9, 'nom': 'Adresse', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 10, 'nom': 'Complément d\'adresse', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 11, 'nom': 'Prix / Loyer / Prix de cession', 'obligatoire': True, 'type': 'Décimal'},
    {'rang': 12, 'nom': 'Unité de prix', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['mois', 'semaine', 'nuit']},
    {'rang': 13, 'nom': 'Mention du prix', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['prix', 'à partir de', 'nous consulter']},
    {'rang': 14, 'nom': 'Complément de prix', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 15, 'nom': 'Prix hors taxe', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 16, 'nom': 'TVA', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 17, 'nom': 'Prix du terrain', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 18, 'nom': 'Prix de construction', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 19, 'nom': 'Prix honoraires inclus', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 20, 'nom': 'Prix honoraires', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 21, 'nom': 'Charges', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 22, 'nom': 'Date de disponibilité', 'obligatoire': False, 'type': 'Date'},
    {'rang': 23, 'nom': 'Charges comprises', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 24, 'nom': 'Type de charges', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 25, 'nom': 'Dépôt de garantie', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 26, 'nom': 'Honoraires locataire', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 27, 'nom': 'Honoraires état des lieux', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 28, 'nom': 'Modalités', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 29, 'nom': 'Complément loyer', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 30, 'nom': 'Devise', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['EUR', 'USD', 'GBP', 'CHF']},
    {'rang': 31, 'nom': 'Type de bien', 'obligatoire': True, 'type': 'Texte'},
    {'rang': 32, 'nom': 'Sous-type de bien', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 33, 'nom': 'Nombre de pièces', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 34, 'nom': 'Nombre de chambres', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 35, 'nom': 'Nombre de salles de bain', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 36, 'nom': 'Nombre de salles d\'eau', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 37, 'nom': 'Nombre de WC', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 38, 'nom': 'Nombre de WC séparés', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 39, 'nom': 'Surface habitable', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 40, 'nom': 'Surface terrain', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 41, 'nom': 'Surface séjour', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 42, 'nom': 'Surface totale', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 43, 'nom': 'Surface loi Carrez', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 44, 'nom': 'Surface cave', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 45, 'nom': 'Surface balcon', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 46, 'nom': 'Surface terrasse', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 47, 'nom': 'Surface jardin', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 48, 'nom': 'Étage', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 49, 'nom': 'Nombre d\'étages', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 50, 'nom': 'Ascenseur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 51, 'nom': 'Cave', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 52, 'nom': 'Parking', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 53, 'nom': 'Nombre de parkings', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 54, 'nom': 'Box', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 55, 'nom': 'Nombre de box', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 56, 'nom': 'Chauffage', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 57, 'nom': 'Type de chauffage', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 58, 'nom': 'Accès handicapé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 59, 'nom': 'Année de construction', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 60, 'nom': 'État du bien', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 61, 'nom': 'Orientation', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 62, 'nom': 'Vue', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 63, 'nom': 'Vue mer', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 64, 'nom': 'Vue montagne', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 65, 'nom': 'Piscine', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 66, 'nom': 'Alarme', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 67, 'nom': 'Câble TV', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 68, 'nom': 'Calme', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 69, 'nom': 'Climatisation', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 70, 'nom': 'Proche métro', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 71, 'nom': 'Titre', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 72, 'nom': 'Texte annonce', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 73, 'nom': 'Proximités', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 74, 'nom': 'Nom contact', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 75, 'nom': 'Téléphone', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 76, 'nom': 'Email', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 77, 'nom': 'Langue 1', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 78, 'nom': 'Langue 2', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 79, 'nom': 'Langue 3', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 80, 'nom': 'Photo 1', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 81, 'nom': 'Titre photo 1', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 82, 'nom': 'Photo 2', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 83, 'nom': 'Titre photo 2', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 84, 'nom': 'Photo 3', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 85, 'nom': 'Titre photo 3', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 86, 'nom': 'Photo 4', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 87, 'nom': 'Titre photo 4', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 88, 'nom': 'Photo 5', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 89, 'nom': 'Titre photo 5', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 90, 'nom': 'Photo 6', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 91, 'nom': 'Titre photo 6', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 92, 'nom': 'Photo 7', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 93, 'nom': 'Titre photo 7', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 94, 'nom': 'Photo 8', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 95, 'nom': 'Titre photo 8', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 96, 'nom': 'Photo 9', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 97, 'nom': 'Titre photo 9', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 98, 'nom': 'Photo 10', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 99, 'nom': 'Titre photo 10', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 100, 'nom': 'Photo 11', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 101, 'nom': 'Titre photo 11', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 102, 'nom': 'Photo 12', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 103, 'nom': 'Titre photo 12', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 104, 'nom': 'Photo 13', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 105, 'nom': 'Titre photo 13', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 106, 'nom': 'Photo 14', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 107, 'nom': 'Titre photo 14', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 108, 'nom': 'Photo 15', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 109, 'nom': 'Titre photo 15', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 110, 'nom': 'Photo 16', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 111, 'nom': 'Titre photo 16', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 112, 'nom': 'Photo 17', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 113, 'nom': 'Titre photo 17', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 114, 'nom': 'Photo 18', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 115, 'nom': 'Titre photo 18', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 116, 'nom': 'Photo 19', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 117, 'nom': 'Titre photo 19', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 118, 'nom': 'Photo 20', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 119, 'nom': 'Titre photo 20', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 120, 'nom': 'Photo 21', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 121, 'nom': 'Titre photo 21', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 122, 'nom': 'Photo 22', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 123, 'nom': 'Titre photo 22', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 124, 'nom': 'Photo 23', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 125, 'nom': 'Titre photo 23', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 126, 'nom': 'Photo 24', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 127, 'nom': 'Titre photo 24', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 128, 'nom': 'Photo 25', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 129, 'nom': 'Titre photo 25', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 130, 'nom': 'Photo 26', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 131, 'nom': 'Titre photo 26', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 132, 'nom': 'Photo 27', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 133, 'nom': 'Titre photo 27', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 134, 'nom': 'Photo 28', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 135, 'nom': 'Titre photo 28', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 136, 'nom': 'Photo 29', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 137, 'nom': 'Titre photo 29', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 138, 'nom': 'Photo 30', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 139, 'nom': 'Titre photo 30', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 140, 'nom': 'Latitude', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 141, 'nom': 'Longitude', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 142, 'nom': 'Date de création', 'obligatoire': False, 'type': 'Date'},
    {'rang': 143, 'nom': 'Date de modification', 'obligatoire': False, 'type': 'Date'},
    {'rang': 144, 'nom': 'Actif', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 145, 'nom': 'Publié sur internet', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 146, 'nom': 'Coup de coeur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 147, 'nom': 'Exclusivité', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 148, 'nom': 'Nouveauté', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 149, 'nom': 'Visite virtuelle', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 150, 'nom': 'Vidéo', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 151, 'nom': 'Référence propriétaire', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 152, 'nom': 'Nom propriétaire', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 153, 'nom': 'Téléphone propriétaire', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 154, 'nom': 'Email propriétaire', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 155, 'nom': 'Commentaire interne', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 156, 'nom': 'Syndic', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 157, 'nom': 'Procédure en cours', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 158, 'nom': 'Détail procédure', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 159, 'nom': 'Nombre de lots', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 160, 'nom': 'Charges annuelles', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 161, 'nom': 'Appel de fonds', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 162, 'nom': 'Taxe foncière', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 163, 'nom': 'Taxe habitation', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 164, 'nom': 'Consommation énergétique', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 165, 'nom': 'Émission de gaz', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 166, 'nom': 'Performance énergétique', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 167, 'nom': 'Performance climatique', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 168, 'nom': 'Logement économe', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 169, 'nom': 'Logement énergivore', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 170, 'nom': 'Diagnostic réalisé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 171, 'nom': 'Date diagnostic', 'obligatoire': False, 'type': 'Date'},
    {'rang': 172, 'nom': 'Prix au m² habitable', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 173, 'nom': 'Prix au m² utile', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 174, 'nom': 'Prix au m² terrain', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 175, 'nom': 'Loyer au m² habitable', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 176, 'nom': 'Rentabilité brute', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 177, 'nom': 'Rentabilité nette', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 178, 'nom': 'Meublé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 179, 'nom': 'Animaux acceptés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 180, 'nom': 'Fumeurs acceptés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 181, 'nom': 'Colocation', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 182, 'nom': 'Étudiants acceptés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 183, 'nom': 'Retraités acceptés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 184, 'nom': 'Saisonniers acceptés', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 185, 'nom': 'Bail commercial', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 186, 'nom': 'Droit au bail', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 187, 'nom': 'Pas de porte', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 188, 'nom': 'Chiffre d\'affaires', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 189, 'nom': 'Résultat net', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 190, 'nom': 'Prix du fonds', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 191, 'nom': 'Prix des murs', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 192, 'nom': 'Activité commerciale', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 193, 'nom': 'Longueur façade', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 194, 'nom': 'Nombre de vitrines', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 195, 'nom': 'Nombre d\'employés', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 196, 'nom': 'Équipements inclus', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 197, 'nom': 'Détail équipements', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 198, 'nom': 'Cuisine équipée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 199, 'nom': 'Cuisine aménagée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 200, 'nom': 'Kitchenette', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 201, 'nom': 'Coin cuisine', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 202, 'nom': 'Cuisine américaine', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 203, 'nom': 'Cuisine séparée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 204, 'nom': 'Séjour double', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 205, 'nom': 'Salle à manger', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 206, 'nom': 'Bureau', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 207, 'nom': 'Cellier', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 208, 'nom': 'Débarras', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 209, 'nom': 'Dressing', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 210, 'nom': 'Buanderie', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 211, 'nom': 'Véranda', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 212, 'nom': 'Loggia', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 213, 'nom': 'Balcon', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 214, 'nom': 'Terrasse', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 215, 'nom': 'Jardin', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 216, 'nom': 'Cour', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 217, 'nom': 'Garage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 218, 'nom': 'Nombre de garages', 'obligatoire': False, 'type': 'Entier'},
    {'rang': 219, 'nom': 'Grenier', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 220, 'nom': 'Sous-sol', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 221, 'nom': 'Piscine couverte', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 222, 'nom': 'Piscine privée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 223, 'nom': 'Tennis', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 224, 'nom': 'Sauna', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 225, 'nom': 'Hammam', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 226, 'nom': 'Jacuzzi', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 227, 'nom': 'Salle de sport', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 228, 'nom': 'Salle de jeux', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 229, 'nom': 'Salle de cinéma', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 230, 'nom': 'Cheminée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 231, 'nom': 'Climatisation réversible', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 232, 'nom': 'VMC', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 233, 'nom': 'Double vitrage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 234, 'nom': 'Triple vitrage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 235, 'nom': 'Volets électriques', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 236, 'nom': 'Porte blindée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 237, 'nom': 'Digicode', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 238, 'nom': 'Interphone', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 239, 'nom': 'Gardien', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 240, 'nom': 'Concierge', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 241, 'nom': 'Fibre optique', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 242, 'nom': 'ADSL', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 243, 'nom': 'Antenne TV', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 244, 'nom': 'Antenne satellite', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 245, 'nom': 'Lave-vaisselle', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 246, 'nom': 'Lave-linge', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 247, 'nom': 'Sèche-linge', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 248, 'nom': 'Réfrigérateur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 249, 'nom': 'Congélateur', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 250, 'nom': 'Four', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 251, 'nom': 'Micro-ondes', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 252, 'nom': 'Plaques de cuisson', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 253, 'nom': 'Hotte', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 254, 'nom': 'Plan de travail', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 255, 'nom': 'Placards cuisine', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 256, 'nom': 'Placards entrée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 257, 'nom': 'Placards chambres', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 258, 'nom': 'Parquet', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 259, 'nom': 'Carrelage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 260, 'nom': 'Moquette', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 261, 'nom': 'Lino', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 262, 'nom': 'Béton ciré', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 263, 'nom': 'Pierre apparente', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 264, 'nom': 'Poutres apparentes', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 265, 'nom': 'Moulures', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 266, 'nom': 'Rosaces', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 267, 'nom': 'Hauteur sous plafond', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 268, 'nom': 'Lumineux', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 269, 'nom': 'Traversant', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 270, 'nom': 'Sur cour', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 271, 'nom': 'Sur rue', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 272, 'nom': 'Sur jardin', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 273, 'nom': 'Vue dégagée', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 274, 'nom': 'Vue panoramique', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 275, 'nom': 'Proche commerces', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 276, 'nom': 'Proche écoles', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 277, 'nom': 'Proche transports', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 278, 'nom': 'Proche autoroute', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 279, 'nom': 'Proche aéroport', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 280, 'nom': 'Proche gare', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 281, 'nom': 'Proche centre ville', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 282, 'nom': 'Proche plage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 283, 'nom': 'Proche montagne', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 284, 'nom': 'Proche forêt', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 285, 'nom': 'Proche lac', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 286, 'nom': 'Proche rivière', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 287, 'nom': 'Proche parc', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 288, 'nom': 'Proche hôpital', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 289, 'nom': 'Proche pharmacie', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 290, 'nom': 'Proche médecin', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 291, 'nom': 'Proche banque', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 292, 'nom': 'Proche poste', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 293, 'nom': 'Proche mairie', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 294, 'nom': 'Proche restaurant', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 295, 'nom': 'Proche cinéma', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 296, 'nom': 'Proche théâtre', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 297, 'nom': 'Proche salle de sport', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 298, 'nom': 'Proche stade', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 299, 'nom': 'Proche golf', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 300, 'nom': 'Proche piscine', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 301, 'nom': 'Zone touristique', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 302, 'nom': 'Zone résidentielle', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 303, 'nom': 'Zone commerciale', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 304, 'nom': 'Zone industrielle', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 305, 'nom': 'Zone agricole', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 306, 'nom': 'Constructible', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 307, 'nom': 'Viabilisé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 308, 'nom': 'Raccordé eau', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 309, 'nom': 'Raccordé électricité', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 310, 'nom': 'Raccordé gaz', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 311, 'nom': 'Raccordé téléphone', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 312, 'nom': 'Tout à l\'égout', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 313, 'nom': 'Fosse septique', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 314, 'nom': 'Puits', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 315, 'nom': 'Forage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 316, 'nom': 'Arrosage automatique', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 317, 'nom': 'Portail électrique', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 318, 'nom': 'Clôturé', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 319, 'nom': 'Arboré', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 320, 'nom': 'Plat', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 321, 'nom': 'En pente', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 322, 'nom': 'Exposition terrain', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 323, 'nom': 'Nature du sol', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 324, 'nom': 'Coefficient d\'occupation', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 325, 'nom': 'Surface constructible', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 326, 'nom': 'Hauteur maximale', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 327, 'nom': 'Recul obligatoire', 'obligatoire': False, 'type': 'Décimal'},
    {'rang': 328, 'nom': 'Servitudes', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 329, 'nom': 'Détail servitudes', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 330, 'nom': 'Mitoyenneté', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 331, 'nom': 'Droit de passage', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 332, 'nom': 'Nuisances', 'obligatoire': False, 'type': 'Texte', 'valeurs': ['oui', 'non']},
    {'rang': 333, 'nom': 'Détail nuisances', 'obligatoire': False, 'type': 'Texte'},
    {'rang': 334, 'nom': 'Commentaires libres', 'obligatoire': False, 'type': 'Texte'}
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
