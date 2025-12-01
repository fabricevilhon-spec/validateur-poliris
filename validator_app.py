import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from collections import Counter

# =============================================================================
# CORRECTIF MÉMOIRE ET VERSION
# =============================================================================
pd.set_option("styler.render.max_elements", 2_000_000)

__version__ = "14.6.0 (Détection Décalage)"
EXPECTED_COLUMNS = 334
HEADER_FILE = 'En-tête_Poliris.csv'
REF_ANNONCE_INDEX = 1

# =============================================================================
# CONFIGURATION CENTRALE DES RÈGLES
# =============================================================================
MANDATORY_RANKS = {1, 2, 3, 4, 5, 6, 11, 18, 20, 21, 175}

KNOWN_FIELDS = {
    1: {'nom': 'Identifiant agence', 'type': 'Entier'},
    2: {'nom': 'Référence agence du bien', 'type': 'Texte'},
    3: {'nom': 'Type d\'annonce', 'type': 'Texte', 'valeurs': ["cession de bail", "location", "location vacances", "produit d'investissement", "vente", "vente-de-prestige", "vente-fonds-de-commerce", "viager"]},
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

def check_suspicion_decalage(value, rule):
    """
    Vérifie si la donnée est radicalement incohérente avec le type attendu,
    ce qui suggère un décalage de colonne (ex: Texte dans un champ Prix).
    """
    if not value:
        return None

    rtype = rule.get('type')

    # CAS 1 : Champ Numérique (Entier ou Décimal) qui contient des lettres
    # Ex: Le champ "Prix" contient "Paris" ou "Cuisine"
    if rtype in ['Entier', 'Décimal']:
        # On cherche s'il y a au moins une lettre (a-z)
        if re.search(r'[a-zA-Z]', value):
            return "🚨 DÉCALAGE PROBABLE : Texte détecté dans un champ numérique."

    # CAS 2 : Champ Date qui ne ressemble pas du tout à une date
    # Ex: Le champ "Date dispo" contient "Cuisine équipée" (texte long sans chiffre)
    if rtype == 'Date':
        # Si ne contient aucun chiffre OU est trop long (> 12 chars pour une date jj/mm/aaaa + marge)
        if not re.search(r'\d', value) or len(value) > 12:
             return "🚨 DÉCALAGE PROBABLE : Valeur incohérente pour une date (Texte ?)."

    # CAS 3 : Liste de valeurs (Enum) totalement hors sujet
    # Ex: Type d'annonce attend "Vente" mais reçoit un Code Postal "75001"
    if rule.get('valeurs'):
        valeurs_clean = [str(v).lower() for v in rule['valeurs']]
        # Si la valeur est numérique alors qu'on attend du texte (ex: "75000" au lieu de "Vente")
        # On vérifie d'abord que les valeurs attendues ne sont pas elles-mêmes des chiffres
        expected_are_numbers = any(v.isdigit() for v in valeurs_clean)
        
        if value.isdigit() and not expected_are_numbers:
            return "🚨 DÉCALAGE PROBABLE : Nombre trouvé dans un champ de type Liste (Texte attendu)."

    return None

def check_type_entier(value, rule):
    if rule.get('type') == 'Entier' and value and not value.isdigit(): return 'Doit être un entier.'
    return None

def check_type_decimal(value, rule):
    if rule.get('type') == 'Décimal' and value:
        try:
            pd.to_numeric(value.replace(',', '.'))
        except (ValueError, TypeError):
            return 'Doit être un nombre.'
    return None
    
def check_type_date(value, rule):
    if rule.get('type') == 'Date' and value:
        try:
            datetime.strptime(value, '%d/%m/%Y')
        except ValueError:
            return f"Format de date invalide. Attendu JJ/MM/AAAA, mais la valeur est {repr(value)}."
    return None

def check_valeurs_permises(value, rule):
    allowed_values = rule.get('valeurs')
    if allowed_values and value:
        normalized_input = value.lower().replace('-', ' ')
        normalized_allowed = [str(v).lower().replace('-', ' ') for v in allowed_values]
        if normalized_input not in normalized_allowed:
            return f'Valeur non autorisée. Attendues: {rule["valeurs"]}'
    return None

# Pipeline mis à jour : check_suspicion_decalage est prioritaire
TYPE_VALIDATION_PIPELINE = [check_suspicion_decalage, check_type_entier, check_type_decimal, check_type_date, check_valeurs_permises]

def validate_row(row_num, row_data):
    errors = []
    annonce_ref = row_data[REF_ANNONCE_INDEX] if len(row_data) > REF_ANNONCE_INDEX else 'N/A'
    for i, clean_value in enumerate(row_data):
        rule = SCHEMA[i]
        error_template = {'Ligne': row_num, 'Référence Annonce': annonce_ref, 'Rang': rule['rang'], 'Champ': rule['nom'], 'Valeur': f'"{clean_value}"'}
        
        error_message = check_obligatoire(clean_value, rule)
        if error_message:
            error_template['Message'] = error_message
            errors.append(error_template)
            continue

        if not clean_value:
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
        try:
            return data_bytes.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return None, None

def style_error_rows(row, error_row_indices):
    return ['background-color: rgba(255, 204, 204, 0.6)'] * len(row) if row.name in error_row_indices else [''] * len(row)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Données Validées')
    processed_data = output.getvalue()
    return processed_data

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
            st.error(f"Erreur config : Impossible de lire `{HEADER_FILE}`. Encodage non supporté.")
            return

        headers_df = pd.read_csv(io.StringIO(decoded_content), header=None, sep=';')
        ranks = headers_df.iloc[0].astype(str).tolist()
        names = headers_df.iloc[1].astype(str).tolist()

        if len(ranks) != EXPECTED_COLUMNS or len(names) != EXPECTED_COLUMNS:
            st.error(f"Erreur de configuration : le fichier d'en-têtes `{HEADER_FILE}` est incorrect.")
            return
            
        column_headers = [f"{rank} - {name}" for rank, name in zip(ranks, names)]
            
    except FileNotFoundError:
        st.error(f"Fichier de configuration manquant : `{HEADER_FILE}` introuvable.")
        return
    except IndexError:
        st.error(f"Erreur de configuration : Impossible de lire les deux premières lignes de `{HEADER_FILE}`.")
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
        
        # =================================================================
        # ÉTAPE 1 : Pré-analyse (Doublons + Structure Globale)
        # =================================================================
        ref_locations = {}
        line_lengths = []
        
        for i, line in enumerate(lines):
            if not line: continue
            temp_fields = line.split('!#')
            
            # Ajustement lecture fin de ligne
            if len(temp_fields) == 335 and temp_fields[334] == '':
                temp_fields.pop()
            
            # Stockage longueur pour analyse globale
            line_lengths.append(len(temp_fields))
            
            # Stockage Ref pour doublons
            if len(temp_fields) > REF_ANNONCE_INDEX:
                r = temp_fields[REF_ANNONCE_INDEX].strip('"').strip()
                if r:
                    if r not in ref_locations:
                        ref_locations[r] = []
                    ref_locations[r].append(i + 1)
        
        # --- Analyse de la structure globale ---
        unique_lengths = set(line_lengths)
        is_global_structure_error = False
        global_structure_msg = ""
        
        # S'il n'y a qu'une seule taille de ligne dans tout le fichier, et qu'elle est fausse
        if len(unique_lengths) == 1:
            common_len = list(unique_lengths)[0]
            if common_len != EXPECTED_COLUMNS:
                is_global_structure_error = True
                global_structure_msg = f"Structure fichier incorrecte : TOUTES les lignes contiennent {common_len} champs au lieu de {EXPECTED_COLUMNS}. Les colonnes ont été ajustées automatiquement pour la validation."
                
                # On ajoute UNE SEULE erreur générique
                all_errors.append({
                    'Ligne': 0, # Ligne 0 pour symboliser "Global"
                    'Référence Annonce': 'FICHIER ENTIER',
                    'Rang': '-',
                    'Champ': 'Structure Générale',
                    'Message': global_structure_msg,
                    'Valeur': f'{common_len} colonnes'
                })
        # =================================================================

        # ÉTAPE 2 : Traitement ligne par ligne
        for i, line in enumerate(lines):
            if not line: continue
            
            fields = line.split('!#')
            
            if len(fields) == 335 and fields[334] == '':
                fields.pop()
            
            current_len = len(fields)

            # =================================================================
            # Gestion Structure (Sporadique vs Global)
            # =================================================================
            if current_len != EXPECTED_COLUMNS:
                # On signale l'erreur ICI seulement si ce n'est PAS un problème global
                if not is_global_structure_error:
                    msg = f"Avertissement structure : {current_len} champs trouvés (attendu {EXPECTED_COLUMNS})."
                    if current_len < EXPECTED_COLUMNS:
                        msg += " Colonnes manquantes ajoutées."
                    else:
                        msg += " Colonnes excédentaires ignorées."

                    all_errors.append({
                        'Ligne': i + 1,
                        'Référence Annonce': 'Inconnue/Partielle',
                        'Rang': 'Général',
                        'Champ': 'Structure',
                        'Message': msg,
                        'Valeur': f'{current_len} cols'
                    })

            # Règle des guillemets
            raw_ref = fields[REF_ANNONCE_INDEX].strip('"') if len(fields) > REF_ANNONCE_INDEX else 'N/A'
            for idx, raw_val in enumerate(fields):
                is_valid_quote = len(raw_val) >= 2 and raw_val.startswith('"') and raw_val.endswith('"')
                if not is_valid_quote:
                    field_name = SCHEMA[idx]['nom'] if idx < len(SCHEMA) else f'Champ {idx+1}'
                    valeur_affichee = "[VIDE]" if raw_val == '' else raw_val
                    all_errors.append({
                        'Ligne': i + 1,
                        'Référence Annonce': raw_ref,
                        'Rang': idx + 1,
                        'Champ': field_name,
                        'Message': 'Format CSV invalide : Tout champ doit être entre guillemets (""), même vide.',
                        'Valeur': valeur_affichee
                    })

            # Règle Doublons
            clean_ref_for_check = fields[REF_ANNONCE_INDEX].strip('"').strip() if len(fields) > REF_ANNONCE_INDEX else ""
            if clean_ref_for_check and len(ref_locations.get(clean_ref_for_check, [])) > 1:
                locations = ref_locations[clean_ref_for_check]
                count = len(locations)
                locs_str = ", ".join(map(str, locations))
                all_errors.append({
                    'Ligne': i + 1,
                    'Référence Annonce': clean_ref_for_check,
                    'Rang': 2,
                    'Champ': "Référence agence du bien",
                    'Message': f"Référence multiple détectée : Présente {count} fois (lignes : {locs_str}).",
                    'Valeur': clean_ref_for_check
                })

            # =================================================================
            # NORMALISATION (Padding/Cutting)
            # =================================================================
            cleaned_row = [field.strip('"').strip() for field in fields]
            
            # On ajuste la taille QUELLE QUE SOIT la situation (Global ou Sporadique)
            # pour que la suite du code ne plante pas
            if len(cleaned_row) < EXPECTED_COLUMNS:
                cleaned_row += [''] * (EXPECTED_COLUMNS - len(cleaned_row))
            elif len(cleaned_row) > EXPECTED_COLUMNS:
                cleaned_row = cleaned_row[:EXPECTED_COLUMNS]
            
            data_rows.append(cleaned_row)
            all_errors.extend(validate_row(i + 1, cleaned_row))

        st.header("2. Visualisation des Données")
        if data_rows:
            df = pd.DataFrame(data_rows, columns=column_headers)
            df.index = df.index + 1
            
            # Calcul des lignes à surligner :
            # Si erreur globale, la ligne 0 est dans all_errors mais n'existe pas dans le DF (index commence à 1)
            # Donc elle ne sera pas surlignée. C'est le comportement voulu.
            error_row_indices = {error['Ligne'] for error in all_errors if error['Ligne'] > 0}
            
            st.dataframe(df.style.apply(style_error_rows, error_row_indices=error_row_indices, axis=1), use_container_width=True, height=600)
        
            st.header("3. Télécharger les données")
            excel_data = to_excel(df)
            st.download_button(
                label="📥 Télécharger en format Excel",
                data=excel_data,
                file_name=f'donnees_validees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        elif all_errors:
             st.warning("Aucune donnée à afficher car toutes les lignes présentent une erreur de structure majeure.")
        else:
             st.info("Le fichier est vide ou ne contient aucune donnée à afficher.")

        st.header("4. Rapport d'Erreurs")
        if not all_errors:
            st.success("🎉 Félicitations ! Aucune erreur détectée.")
        else:
            # Message spécial si erreur globale
            if is_global_structure_error:
                st.warning(f"⚠️ **ATTENTION :** {global_structure_msg}")
            
            st.error(f"Le fichier contient {len(all_errors)} erreur(s).")
            column_config = {"Ligne": st.column_config.NumberColumn(width="small"), "Rang": st.column_config.TextColumn(width="small"), "Champ": st.column_config.TextColumn(width="medium"), "Message": st.column_config.TextColumn(width="large")}
            errors_df = pd.DataFrame(all_errors)[['Ligne', 'Référence Annonce', 'Rang', 'Champ', 'Message', 'Valeur']]
            st.dataframe(errors_df, column_config=column_config, use_container_width=True)

    st.markdown(f'<div style="text-align: center; color: grey; font-size: 0.8em; padding-top: 2em;">Version {__version__}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("Une erreur fatale et non prévue a provoqué le crash de l'application.")
        st.exception(e)