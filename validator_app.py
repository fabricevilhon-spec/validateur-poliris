import streamlit as st
import pandas as pd
import io
from datetime import datetime

# =============================================================================
# DÉFINITION DE LA VERSION ET CONFIGURATION
# =============================================================================
__version__ = "4.4.0" # Ajout du redimensionnement des colonnes dans le rapport d'erreurs

EXPECTED_COLUMNS = 334
HEADER_FILE = 'En-tête_Poliris.csv'
REF_ANNONCE_INDEX = 1

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
        except ValueError: return 'Format de date invalide (attendu: JJ/MM/AAAA).'
    return None

def check_valeurs_permises(value, rule):
    if rule.get('valeurs') and value not in rule.get('valeurs', []): return f'Valeur non autorisée. Attendues: {rule["valeurs"]}'
    return None

VALIDATION_PIPELINE = [check_obligatoire, check_type_entier, check_type_decimal, check_type_date, check_valeurs_permises]

def validate_row(row_num, row_data):
    errors = []
    annonce_ref = row_data[REF_ANNONCE_INDEX].strip('"') if len(row_data) > REF_ANNONCE_INDEX else 'N/A'
    for i, field_value in enumerate(row_data):
        rule = SCHEMA[i]
        clean_value = field_value.strip('"')
        error_template = {'Ligne': row_num, 'Référence Annonce': annonce_ref, 'Rang': rule['rang'], 'Champ': rule['nom'], 'Valeur': f'"{clean_value}"'}
        if not clean_value:
            error_message = check_obligatoire(clean_value, rule)
            if error_message:
                error_template['Message'] = error_message
                errors.append(error_template)
            continue
        for validation_function in VALIDATION_PIPELINE:
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
        with open(HEADER_FILE, 'rb') as f:
            header_bytes = f.read()
        decoded_content, _ = try_decode(header_bytes)
        if decoded_content is None:
            st.error(f"Erreur de configuration : Impossible de lire `{HEADER_FILE}`. Encodage non supporté.")
            return
        headers_df = pd.read_csv(io.StringIO(decoded_content), header=None, sep=';')
        column_headers = headers_df.iloc[1].tolist()
        if len(column_headers) != EXPECTED_COLUMNS:
            st.error(f"Erreur de configuration : Le fichier d'en-têtes `{HEADER_FILE}` est incorrect.")
            return
    except FileNotFoundError:
        st.error(f"Fichier de configuration manquant : `{HEADER_FILE}` introuvable.")
        return
    except IndexError:
        st.error(f"Erreur de configuration : Impossible de lire la deuxième ligne de `{HEADER_FILE}`.")
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
        lines = file_content.strip().splitlines()
        for i, line in enumerate(lines):
            if not line: continue
            fields = line.split('!#')
            if len(fields) != EXPECTED_COLUMNS:
                all_errors.append({'Ligne': i + 1, 'Référence Annonce': 'N/A', 'Rang': 'N/A', 'Champ': 'Général', 'Message': f"Erreur de structure (attendu: {EXPECTED_COLUMNS}, trouvé: {len(fields)}).", 'Valeur': 'Ligne non affichée.'})
                continue
            data_rows.append([field.strip('"') for field in fields])
            all_errors.extend(validate_row(i + 1, fields))

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
            
            # --- MODIFICATION ICI : On définit une configuration pour les colonnes du rapport d'erreurs ---
            column_config = {
                "Ligne": st.column_config.NumberColumn("Ligne", width="small"),
                "Rang": st.column_config.NumberColumn("Rang", width="small"),
                "Champ": st.column_config.TextColumn("Champ", width="medium"),
                "Message": st.column_config.TextColumn("Message", width="large"),
            }
            
            errors_df = pd.DataFrame(all_errors)[['Ligne', 'Référence Annonce', 'Rang', 'Champ', 'Message', 'Valeur']]
            st.dataframe(
                errors_df,
                column_config=column_config,  # On applique la configuration ici
                use_container_width=True
            )

    st.markdown(f'<div style="text-align: center; color: grey; font-size: 0.8em; padding-top: 2em;">Version {__version__}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Une erreur fatale et non prévue a provoqué le crash de l'application.")
        st.exception(e)
