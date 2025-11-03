import streamlit as st
import pandas as pd
import csv
import io
from datetime import datetime

# =============================================================================
# DÉFINITION DE LA VERSION ET CONFIGURATION
# =============================================================================
__version__ = "3.1.0" # Mise à jour suite à la correction du crash

EXPECTED_COLUMNS = 334
HEADER_FILE = 'En-tête_Poliris.csv'

# =============================================================================
# DÉFINITION DU SCHÉMA (Extrait pour la démonstration)
# =============================================================================
SCHEMA = [
    {'rang': 1, 'nom': 'Identifiant agence', 'type': 'Entier', 'obligatoire': True},
    {'rang': 2, 'nom': 'Référence agence du bien', 'type': 'Texte', 'obligatoire': True},
    {'rang': 3, 'nom': 'Type d\'annonce', 'type': 'Texte', 'obligatoire': True, 'valeurs': ["cession de bail", "location", "location vacances", "produit d'investissement", "vente", "vente de prestige", "vente fonds-de-commerce", "viager"]},
    {'rang': 5, 'nom': 'CP', 'type': 'Texte(5)', 'obligatoire': True},
    {'rang': 6, 'nom': 'Ville', 'type': 'Texte', 'obligatoire': True},
    {'rang': 11, 'nom': 'Prix / Loyer / Prix de cession', 'type': 'Décimal', 'obligatoire': True},
    {'rang': 22, 'nom': 'Date de disponibilité', 'type': 'Date', 'obligatoire': False},
]
# Remplissage du reste du schéma
nb_champs_definis = len(SCHEMA)
placeholders = [{'rang': i + 1, 'nom': f'Champ non-défini {i+1}', 'type': 'Texte', 'obligatoire': False} for i in range(nb_champs_definis, 334)]
SCHEMA.extend(placeholders)

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
def try_decode(data_bytes):
    """Tente de décoder les données avec une liste d'encodages courants."""
    for encoding in ['utf-8', 'ISO-8859-1', 'windows-1252']:
        try:
            return data_bytes.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return None, None

def validate_row(row_num, row_data):
    """Valide une ligne et retourne une liste de dictionnaires d'erreurs."""
    errors = []
    # Note : la validation du nombre de colonnes est maintenant faite en amont.
    for i, field_value in enumerate(row_data):
        rule = SCHEMA[i]
        field_name = rule['nom']
        
        if rule['obligatoire'] and not field_value:
            errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Le champ obligatoire est vide.', 'Valeur': f'"{field_value}"'})
        elif field_value:
            if rule['type'] == 'Entier' and not field_value.isdigit():
                errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Doit être un entier.', 'Valeur': f'"{field_value}"'})
            elif rule['type'] == 'Décimal' and not pd.to_numeric(field_value.replace(',', '.'), errors='coerce'):
                errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Doit être un nombre.', 'Valeur': f'"{field_value}"'})
            elif rule['type'] == 'Date':
                try:
                    datetime.strptime(field_value, '%d/%m/%Y')
                except ValueError:
                    errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': 'Format de date invalide (JJ/MM/AAAA).', 'Valeur': f'"{field_value}"'})
            elif rule.get('valeurs') and field_value not in rule['valeurs']:
                errors.append({'Ligne': row_num, 'Champ': field_name, 'Message': f'Valeur non autorisée. Attendues: {rule["valeurs"]}', 'Valeur': f'"{field_value}"'})
    return errors

def style_error_rows(row, error_row_indices):
    """Applique un style à toute la ligne si son index est dans la liste des erreurs."""
    return ['background-color: rgba(255, 204, 204, 0.6)'] * len(row) if row.name in error_row_indices else [''] * len(row)

# =============================================================================
# INTERFACE PRINCIPALE (STREAMLIT)
# =============================================================================
def main():
    st.set_page_config(layout="wide", page_title="Validateur Figaro Immo")
    st.title("✅ Validateur de Fichier Poliris")

    try:
        headers_df = pd.read_csv(HEADER_FILE, header=None, encoding='ISO-8859-1', sep=';')
        column_headers = headers_df.iloc[0].tolist()
        if len(column_headers) != EXPECTED_COLUMNS:
            st.error(f"Erreur de configuration : le fichier d'en-têtes `{HEADER_FILE}` est incorrect.")
            return
    except FileNotFoundError:
        st.error(f"Fichier de configuration manquant : `{HEADER_FILE}` introuvable.")
        return

    uploaded_file = st.file_uploader("1. Chargez votre fichier d'annonces", type=['csv', 'txt'])

    if uploaded_file:
        file_bytes = uploaded_file.getvalue()
        file_content, detected_encoding = try_decode(file_bytes)

        if file_content is None:
            st.error("Impossible de lire le fichier. Aucun encodage compatible trouvé (UTF-8, ISO-8859-1, etc.).")
            return
        
        st.info(f"Fichier lu avec l'encodage : **{detected_encoding}**")
        
        all_errors = []
        data_rows = []
        reader = csv.reader(io.StringIO(file_content), delimiter='!', quotechar='"', quoting=csv.QUOTE_ALL)
        
        for i, row in enumerate(reader):
            if not any(row): continue

            if len(row) != EXPECTED_COLUMNS:
                all_errors.append({
                    'Ligne': i + 1,
                    'Champ': 'Général',
                    'Message': f"Erreur de structure : La ligne ne contient pas le bon nombre de colonnes (attendu: {EXPECTED_COLUMNS}, trouvé: {len(row)}).",
                    'Valeur': 'Cette ligne n\'est pas affichée dans le tableau.'
                })
                continue
            
            data_rows.append(row)
            all_errors.extend(validate_row(i + 1, row))

        st.header("2. Résultats de l'Analyse")

        if not all_errors:
            st.success("🎉 Félicitations ! Aucune erreur détectée dans le fichier.")
        else:
            st.error(f"Le fichier contient {len(all_errors)} erreur(s).")
            errors_df = pd.DataFrame(all_errors)
            st.write("Rapport détaillé des erreurs :")
            st.dataframe(errors_df, use_container_width=True)
        
        if data_rows:
            st.header("3. Visualisation des Données")
            df = pd.DataFrame(data_rows, columns=column_headers)
            
            error_row_indices = {error['Ligne'] - 1 for error in all_errors if error['Champ'] != 'Général'}

            st.dataframe(
                df.style.apply(style_error_rows, error_row_indices=error_row_indices, axis=1),
                use_container_width=True,
                height=600
            )
        elif all_errors:
             st.warning("Aucune donnée à afficher car toutes les lignes du fichier présentent une erreur de structure (nombre de colonnes incorrect).")

    st.markdown(f'<div style="text-align: center; color: grey; font-size: 0.8em; padding-top: 2em;">Version {__version__}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
