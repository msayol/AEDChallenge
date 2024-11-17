import pandas as pd
import networkx as nx
import streamlit as st

# Carregar dades
dades_0 = pd.read_json("data/datathon_participants.json")
dades = dades_0.drop(
    ['email', 'shirt_size', 'dietary_restrictions', 'interests', 'introduction', 
     'future_excitement', 'age', 'fun_fact', 'interest_in_challenges', 'programming_skills', 
     'experience_level', 'hackathons_done', 'objective', 'technical_project', 'preferred_role', 'availability'], 
    axis=1)


sols = dades[dades['preferred_team_size'] == 1]  # Participants que volen anar sols
tancat = {}  # Diccionari per emmagatzemar grups tancats

# Crear subtaules per a participants que volen anar sols
for i, row in sols.iterrows():
    subtaula = pd.DataFrame([row])
    tancat[f"subtaula_{len(tancat) + 1}"] = subtaula

# Amics
df = pd.DataFrame(dades)

# Construir el graf
G2 = nx.Graph()
for _, row in df.iterrows():
    persona = row['id']
    amics = row['friend_registration']
    for amic in amics:
        G2.add_edge(persona, amic)

# Trobar components connectats
components = list(nx.connected_components(G2))
pendents_amics = {}

# Crear subtaules per a components
for i, component in enumerate(components, 1):
    subtaula = df[df['id'].isin(component)].reset_index(drop=True)
    if subtaula.shape[0] > 1 and subtaula.iloc[1]['preferred_team_size'] == subtaula.shape[0]:
        tancat[f"subtaula_{len(tancat) + 1}"] = subtaula
    else:
        pendents_amics[f"subtaula_{len(pendents_amics) + 1}"] = subtaula

# Gents que queda sola sense amics i que em de classificar
pendents_NOamics = {}
sense_amics = df[df['friend_registration'].apply(lambda x: len(x) == 0)]

# Separar per nivell d'estudi
levels = ["1st year", "2nd year", "3rd year", "4th year", "Masters", "PhD"]
for level in levels:
    level_data = sense_amics[sense_amics['year_of_study'] == level]
    pendents_NOamics[level] = level_data

# Separar per mida de grup (2, 3, 4)
pendents_NOamics_group_size = {}
for level, level_data in pendents_NOamics.items():
    for group_size in [2, 3, 4]:
        group_data = level_data[level_data['preferred_team_size'] == group_size]
        if not group_data.empty:
            group_key = f"{level}_group_size_{group_size}"
            pendents_NOamics_group_size[group_key] = group_data

# Separar per idioma dins de cada mida de grup
pendents_NOamics_group_size_long = {}
language_priority = ['English', 'Catalan', 'Spanish']
for group_key, group_data in pendents_NOamics_group_size.items():
    for lang in language_priority:
        subtaula = group_data[group_data['preferred_languages'].apply(lambda x: lang in x)]
        if not subtaula.empty:
            lang_key = f"{group_key}_{lang}"
            pendents_NOamics_group_size_long[lang_key] = subtaula

    # Subtaula per "altres idiomes"
    subtaula_altres = group_data[~group_data['preferred_languages'].apply(lambda x: any(l in x for l in language_priority))]
    if not subtaula_altres.empty:
        lang_key_altres = f"{group_key}_altres"
        pendents_NOamics_group_size_long[lang_key_altres] = subtaula_altres

# Separar per universitat dins de cada idioma
pendents_NOamics_group_size_lang_unis = {}
universidades = [
    "Universitat Polit\u00e8cnica de Catalunya (UPC)",
    "Universitat Aut\u00f2noma de Barcelona (UAB)",
    "Universitat de Barcelona (UB)",
    "Universitat Internacional de Catalunya (UIC)"
]
for lang_key, lang_data in pendents_NOamics_group_size_long.items():
    for uni in universidades:
        subtaula = lang_data[lang_data['university'] == uni]
        if not subtaula.empty:
            uni_key = f"{lang_key}_{uni.replace(' ', '_')}"
            pendents_NOamics_group_size_lang_unis[uni_key] = subtaula

    # Subtaula per "altres universitats"
    subtaula_altres = lang_data[~lang_data['university'].isin(universidades)]
    if not subtaula_altres.empty:
        uni_key_altres = f"{lang_key}_altres"
        pendents_NOamics_group_size_lang_unis[uni_key_altres] = subtaula_altres

# Funció per agrupar els participants
def agrupar_participants(dades):
    grups_creats = []
    claus_a_eliminar = []
    for key, subtaula in dades.items():
        subtaula = subtaula.sort_values(by=["preferred_team_size", "year_of_study"], ascending=[True, True])
        participants = subtaula.to_dict('records')
        grup_actual = []
        tamany_maxim = 4

        for participant in participants:
            preferred_size = participant["preferred_team_size"]
            tamany_límit = min(tamany_maxim, preferred_size)

            if len(grup_actual) < tamany_límit:
                grup_actual.append(participant)
            else:
                grups_creats.append(grup_actual)
                grup_actual = [participant]

        if grup_actual:
            grups_creats.append(grup_actual)

        if len(participants) == sum(len(grup) for grup in grups_creats):
            claus_a_eliminar.append(key)

    for key in claus_a_eliminar:
        del dades[key]

    return grups_creats

# Funció per mostrar grups amb Streamlit
def mostrar_grups(grups):
    for i, grup in enumerate(grups, 1):
        st.subheader(f"Grup {i}")
        grup_df = pd.DataFrame(grup)
        st.write(grup_df)

# Agrupar els participants restants entre ells
def agrupar_restants(pendents):
    restants_agrupats = []
    participants = []
    
    for key, subtaula in pendents.items():
        participants.extend(subtaula.to_dict('records'))
    
    participants = sorted(participants, key=lambda x: (x['year_of_study'], x['preferred_team_size'], x['preferred_languages']))
    
    grup_actual = []
    for participant in participants:
        if len(grup_actual) < 4:
            grup_actual.append(participant)
        else:
            restants_agrupats.append(grup_actual)
            grup_actual = [participant]
    
    if grup_actual:
        restants_agrupats.append(grup_actual)

    return restants_agrupats

# Agrupar els participants pendents restants
restants_agrupats = agrupar_restants(pendents_NOamics_group_size_lang_unis)

# Traslladar els grups restants a "tancat"
for i, grup in enumerate(restants_agrupats, 1):
    tancat[f"grup_restants_{i}"] = pd.DataFrame(grup)

# Mostrar els grups finals a Streamlit
if not tancat:
    st.write("Encara queden participants pendents.")
else:
    st.write("Tots els participants han estat agrupats.")
    mostrar_grups(tancat.values())
