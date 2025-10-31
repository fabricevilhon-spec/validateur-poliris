import streamlit as st
import csv
import io
from datetime import datetime

# =============================================================================
# DÉFINITION DE LA VERSION
# =============================================================================
# Modifiez cette variable pour chaque nouvelle mise à jour.
# (Ex: 1.1.1 pour un correctif, 1.2.0 pour une nouvelle fonctionnalité)
__version__ = "1.1.0"

# =============================================================================
# DÉFINITION DU SCHÉMA (Basé sur Doc_technique_FCMS_Poliris v1.04.pdf)
# =============================================================================
# Ceci est un extrait représentatif du schéma complet des 334 champs.
SCHEMA = [
    # ... (Le reste du schéma reste inchangé)
    {'rang': 1, 'nom': 'Identifiant agence', 'type': 'Entier', 'obligatoire': True},
    {'rang': 2, 'nom': 'Référence agence du bien', 'type': 'Texte', 'obligatoire': True},
    {'rang': 3, 'nom': 'Type d\'annonce', 'type': 'Texte', 'obligatoire': True, 'valeurs': ["cession de bail", "location", "location vacances", "produit d'investissement", "vente", "vente de prestige", "vente fonds-de-commerce", "viager"]},
    {'rang': 4, 'nom': 'Type de bien', 'type': 'Texte', 'obligatoire': True, 'valeurs': ["appartement", "bâtiment", "boutique", "bureaux", "château", "inconnu", "hôtel particulier", "immeuble", "local", "loft/atelier/surface", "maison/villa", "parking/box", "terrain", "maison avec terrain"]},
    {'rang': 5, 'nom': 'CP', 'type': 'Texte(5)', 'obligatoire': True},
    {'rang': 6, 'nom': 'Ville', 'type': 'Texte', 'obligatoire': True},
    {'rang': 11, 'nom': 'Prix / Loyer / Prix de cession', 'type': 'Décimal', 'obligatoire': True},
    {'rang': 13, 'nom': 'Loyer CC', 'type': 'Texte(3)', 'obligatoire': False, 'valeurs': ['OUI', 'NON']},
    {'rang': 18, 'nom': 'NB de pièces', 'type': 'Entier', 'obligatoire': True},
    {'rang': 20, 'nom': 'Libellé', 'type': 'Texte', 'obligatoire': True},
    {'rang': 21, 'nom': 'Descriptif', 'type': 'Texte', 'obligatoire': True},
    {'rang': 22, 'nom': 'Date de disponibilité', 'type': 'Date', 'obligatoire': False},
]

nb_champs_definis = len(SCHEMA)
for i in range(nb_champs_definis, 334):
    SCHEMA.append({'rang': i + 1, 'nom': f'Champ non-défini {i+1}', 'type': 'Texte', 'obligatoire': False})

EXPECTED_COLUMNS = 334
UNIQUE_IDS = set()

# =============================================================================
# FONCTIONS DE VALIDATION (inchangées)
# =============================================================================

def validate_row(row_num, row_data):
    errors = []
    
    if len(row_data) != EXPECTED_COLUMNS:
        errors.append(f"Ligne {row_num}: Nombre de colonnes incorrect. Attendu: {EXPECTED_COLUMNS}, Trouvé: {len(row_data)}.")
        return errors

    for i, field_value in enumerate(row_data):
        rule = SCHEMA[i]
        field_name = rule['nom']
        field_num = rule['rang']

        if rule['obligatoire'] and not field_value:
            errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): Le champ obligatoire est vide.")
            continue

        if field_value:
            if rule['type'] == 'Entier' and not field_value.isdigit():
                errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): Doit être un entier. Valeur: '{field_value}'.")
            elif rule['type'] == 'Décimal':
                try:
                    float(field_value.replace(',', '.'))
                except ValueError:
                    errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): Doit être un nombre. Valeur: '{field_value}'.")
            elif rule['type'] == 'Date':
                try:
                    datetime.strptime(field_value, '%d/%m/%Y')
                except ValueError:
                     errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): Format de date invalide (attendu: JJ/MM/AAAA). Valeur: '{field_value}'.")
            elif rule['type'] == 'Texte(5)' and (not field_value.isdigit() or len(field_value) != 5):
                errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): Doit être un code postal de 5 chiffres. Valeur: '{field_value}'.")
            
            if rule.get('valeurs') and field_value not in rule['valeurs']:
                errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): Valeur non autorisée. Valeur: '{field_value}'. Valeurs attendues: {rule['valeurs']}.")
                
            if field_num == 2:
                if field_value in UNIQUE_IDS:
                    errors.append(f"Ligne {row_num}, Champ {field_num} ('{field_name}'): La référence '{field_value}' est déjà utilisée.")
                else:
                    UNIQUE_IDS.add(field_value)
    return errors

# =============================================================================
# INTERFACE UTILISATEUR (STREAMLIT)
# =============================================================================

def main():
    st.set_page_config(layout="wide")

    # --- AJOUT : AFFICHAGE DE LA VERSION ---
    st.sidebar.info(f"**Version : {__version__}**")

    st.title("✅ Validateur de Fichier pour Figaro Immo")
    st.markdown("Cette application vérifie la conformité de votre fichier d'annonces (`Annonces.csv`) avec la documentation technique `v1.04`.")

    uploaded_file = st.file_uploader("Chargez votre fichier d'annonces (.csv ou .txt)", type=['csv', 'txt'])

    if uploaded_file is not None:
        if st.button("🚀 Valider le fichier"):
            UNIQUE_IDS.clear()
            all_errors = []
            
            try:
                # ... (le reste de la fonction est inchangé)
                file_content = uploaded_file.getvalue().decode('utf-8')
                reader = csv.reader(io.StringIO(file_content), delimiter='!', quotechar='"', quoting=csv.QUOTE_ALL)
                
                with st.spinner('Analyse en cours...'):
                    for i, row in enumerate(reader):
                        if not any(row): continue
                        errors_in_row = validate_row(i + 1, row)
                        all_errors.extend(errors_in_row)

                st.header("Résultats de la validation")
                if not all_errors:
                    st.success("🎉 Félicitations ! Le fichier est conforme aux règles de validation implémentées.")
                else:
                    st.error(f"Le fichier contient {len(all_errors)} erreur(s).")
                    error_data = [{"Source": err.split(":", 1)[0].strip(), "Message": err.split(":", 1)[1].strip()} for err in all_errors]
                    st.dataframe(error_data, height=600, use_container_width=True)

            except Exception as e:
                st.error("Une erreur critique est survenue. Le fichier est peut-être malformé ou ne respecte pas le format de délimiteur `!#` et de guillemets `\"`.")
                st.code(f"Détail technique : {e}")

if __name__ == "__main__":
    main()
