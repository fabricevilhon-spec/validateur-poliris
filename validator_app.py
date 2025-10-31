import streamlit as st
import pandas as pd
import csv
import io
from datetime import datetime

# =============================================================================
# DÉFINITION DE LA VERSION ET CONFIGURATION
# =============================================================================
__version__ = "2.0.0"

EXPECTED_COLUMNS = 334
HEADER_FILE = 'En-tête_Poliris.csv' # Le fichier d'en-têtes que vous avez fourni

# =============================================================================
# DÉFINITION DU SCHÉMA (Basé sur la doc technique)
# =============================================================================
# Le schéma reste le même, il sert de base pour la validation.
SCHEMA = [
    # ... (Le schéma complet est ici, je montre un extrait)
    {'rang': 1, 'nom': 'Identifiant agence', 'type': 'Entier', 'obligatoire': True},
    {'rang': 2, 'nom': 'Référence agence du bien', 'type': 'Texte', 'obligatoire': True},
    {'rang': 3, 'nom': 'Type d\'annonce', 'type': 'Texte', 'obligatoire': True, 'valeurs': ["cession de bail", "location", "location vacances", "produit d'investissement", "vente", "vente de prestige", "vente fonds-de-commerce", "viager"]},
    {'rang': 5, 'nom': 'CP', 'type': 'Texte(5)', 'obligatoire': True},
    {'rang': 6, 'nom': 'Ville', 'type': 'Texte', 'obligatoire': True},
    {'rang': 11, 'nom': 'Prix / Loyer / Prix de cession', 'type': 'Décimal', 'obligatoire': True},
    {'rang': 22, 'nom': 'Date de disponibilité', 'type': 'Date', 'obligatoire': False},
]

# Remplir le reste du schéma avec des placeholders pour atteindre 334 champs.
nb_champs_definis = len(SCHEMA)
placeholders = []
for i in range(nb_champs_definis, 334):
    placeholders.append({'rang': i + 1, 'nom': f'Champ non-défini {i+1}', 'type': 'Texte', 'obligatoire': False})
SCHEMA.extend(placeholders)

# =============================================================================
# FONCTIONS DE VALIDATION
# =============================================================================
def validate_row(row_num, row_data):
    """
    Valide une ligne et retourne une liste de dictionnaires d'erreurs structurés.
    Chaque erreur contient : ligne, index de colonne, nom du champ et message.
    """
    errors = []
    
    # Valider le nombre de colonnes
    if len(row_data) != EXPECTED_COLUMNS:
        errors.append({
            'Ligne': row_num,
            'Champ': 'Général',
            'Message': f"Nombre de colonnes incorrect. Attendu: {EXPECTED_COLUMNS}, Trouvé: {len(row_data)}.",
            'Valeur': ''
        })
        return errors

    # Valider chaque champ
    for i, field_value in enumerate(row_data):
        rule = SCHEMA[i]
        field_name = rule['nom']
        
        # Logique de validation (similaire à avant, mais retourne une erreur structurée)
        if rule['obligatoire'] and not field_value:
            errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Le champ obligatoire est vide.', 'Valeur': f'"{field_value}"'})
            continue

        if field_value:
            if rule['type'] == 'Entier' and not field_value.isdigit():
                errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Doit être un entier.', 'Valeur': f'"{field_value}"'})
            elif rule['type'] == 'Décimal' and not pd.to_numeric(field_value.replace(',', '.'), errors='coerce'):
                 errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Doit être un nombre.', 'Valeur': f'"{field_value}"'})
            elif rule['type'] == 'Date':
                try:
                    datetime.strptime(field_value, '%d/%m/%Y')
                except ValueError:
                    errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Format de date invalide (attendu: JJ/MM/AAAA).', 'Valeur': f'"{field_value}"'})
            elif rule.get('valeurs') and field_value not in rule['valeurs']:
                errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': f'Valeur non autorisée. Attendues: {rule["valeurs"]}', 'Valeur': f'"{field_value}"'})

    return errors

def highlight_errors(styler, error_locations):
    """Applique un style de fond rouge aux cellules avec des erreurs."""
    styler.set_properties(**{'background-color': 'rgba(255, 204, 204, 0.6)'}, subset=error_locations)
    return styler

# =============================================================================
# INTERFACE UTILISATEUR (STREAMLIT)
# =============================================================================
def main():
    st.set_page_config(layout="wide", page_title="Validateur Figaro Immo")

    st.title("✅ Validateur de Fichier pour Figaro Immo")
    st.markdown("Chargez un fichier `Annonces.csv` pour l'analyser, visualiser les données et identifier les erreurs.")

    # Charger les en-têtes depuis le fichier fourni
    try:
        headers_df = pd.read_csv(HEADER_FILE, header=None)
        column_headers = headers_df[0].tolist()
        if len(column_headers) != EXPECTED_COLUMNS:
            st.warning(f"Attention, le fichier d'en-têtes `{HEADER_FILE}` ne contient pas les {EXPECTED_COLUMNS} colonnes attendues.")
    except FileNotFoundError:
        st.error(f"Fichier d'en-têtes `{HEADER_FILE}` introuvable. Assurez-vous qu'il est dans le même dossier que le script.")
        return

    uploaded_file = st.file_uploader("Chargez votre fichier d'annonces (.csv ou .txt)", type=['csv', 'txt'])

    if uploaded_file:
        all_errors = []
        data_rows = []
        
        # Lecture et validation du fichier
        file_content = uploaded_file.getvalue().decode('utf-8')
        reader = csv.reader(io.StringIO(file_content), delimiter='!', quotechar='"', quoting=csv.QUOTE_ALL)
        
        for i, row in enumerate(reader):
            if not any(row): continue
            data_rows.append(row)
            errors_in_row = validate_row(i + 1, row)
            all_errors.extend(errors_in_row)

        st.header("Résultats de l'Analyse")

        # Afficher le résumé des erreurs en premier
        if not all_errors:
            st.success("🎉 Félicitations ! Aucune erreur détectée dans le fichier.")
        else:
            st.error(f"Le fichier contient {len(all_errors)} erreur(s).")
            errors_df = pd.DataFrame(all_errors)
            st.dataframe(errors_df, use_container_width=True)
        
        # Créer le DataFrame avec les données et les bons en-têtes
        if data_rows:
            st.subheader("Visualisation des Données")
            df = pd.DataFrame(data_rows, columns=column_headers)
            
            # Surligner les erreurs dans le DataFrame
            if all_errors:
                # Créer une liste de tuples (index_ligne, nom_colonne) pour le surlignage
                error_locations = []
                # Créer un mapping nom_champ -> nom_colonne_officiel pour le surlignage
                schema_map = {rule['nom']: column_headers[i] for i, rule in enumerate(SCHEMA)}
                
                for error in all_errors:
                    if error['Champ'] != 'Général':
                        # Trouver l'index de la ligne (base 0)
                        row_idx = error['Ligne'] - 1
                        # Trouver le nom de la colonne
                        col_name = schema_map.get(error['Champ'])
                        if col_name:
                             error_locations.append((row_idx, col_name))
                
                # Appliquer le style
                st.dataframe(df.style.apply(highlight_errors, error_locations=pd.IndexSlice[error_locations], axis=None), use_container_width=True, height=600)
            else:
                st.dataframe(df, use_container_width=True, height=600)

    # Affichage de la version en bas de page
    st.markdown(
        f"""
        <div style="position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); font-size: 0.8em; color: grey;">
            Version {__version__}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
