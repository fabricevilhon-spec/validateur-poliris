import streamlit as st
import pandas as pd
import io
from datetime import datetime

# =============================================================================
# DÉFINITION DE LA VERSION ET CONFIGURATION
# =============================================================================
__version__ = "12.2.0 (Validation des valeurs tolérante aux tirets)"

EXPECTED_COLUMNS = 334
HEADER_FILE = 'En-tête_Poliris.csv'
REF_ANNONCE_INDEX = 1

# =============================================================================
# CONFIGURATION CENTRALE DES RÈGLES (VOTRE "PANNEAU DE CONTRÔLE")
# =============================================================================
MANDATORY_RANKS = {1, 2, 3, 4, 5, 6, 11, 18, 20, 21, 175}

KNOWN_FIELDS = {
    1: {'nom': 'Identifiant agence', 'type': 'Entier'},
    2: {'nom': 'Référence agence du bien', 'type': 'Texte'},
    3: {'nom': 'Type d\'annonce', 'type': 'Texte', 'valeurs': ["cession de bail", "location", "location vacances", "produit d'investissement", "vente", "vente de prestige", "vente-fonds-de-commerce", "viager"]},
    4: {'nom': 'Type de bien', 'type': 'Texte'},
    5: {'nom': 'CP', 'type': 'Texte'},
    6: {'nom': 'Ville', 'type': 'Texte'},
    11: {'nom': 'Prix', 'type': 'Décimal'},
    18: {'nom': 'NB de pièces', 'type': 'Entier'},
    20: {'nom': 'Libellé', 'type': 'Texte'},
    21: {'nom': 'Descriptif', 'type': 'Texte'},
    22: {'nom': 'Date de disponibilité', 'type': 'Date'},
    175: {'nom': 'Identifiant technique', 'type': 'Texte'},
}

SCHEMA = []
for i in range(1, 335):
    is_obligatoire = i in MANDATORY_RANKS
    if i in KNOWN_FIELDS:
        field_def = KNOWN_FIELDS[i].copy()
        field_def['rang'] = i
        field_def['obligatoire'] = is_obligatoire
    else:
        field_def = {'rang': i, 'nom': f'Champ Poliris {i}', 'type': 'Texte', 'obligatoire': is_obligatoire}
    SCHEMA.append(field_def)

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

# --- LA CORRECTION EST ICI ---
def check_valeurs_permises(value, rule):
    """Vérifie si la valeur fait partie d'une liste, en ignorant casse et tirets."""
    allowed_values = rule.get('valeurs')
    if allowed_values:
        # Normalisation : on passe tout en minuscule et on remplace les tirets par des espaces pour la comparaison
        normalized_input = value.lower().replace('-', ' ')
        normalized_allowed = [str(v).lower().replace('-', ' ') for v in allowed_values]
        
        if normalized_input not in normalized_allowed:
            return f'Valeur non autorisée. Attendues: {rule["valeurs"]}'
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
            
            fields = line.split('!#')
            
            if len(fields) == 335 and fields[334] == '':
                fields.pop()
            
            cleaned_row = [field.strip('"').strip() for field in fields]
            
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
