import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Bible Power App", page_icon="⚡", layout="centered")

# CSS Personnalisé pour look "App Mobile"
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .segment-card { background: white; padding: 20px; border-radius: 15px; border-top: 5px solid #2E7D32; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .bible-ref { color: #1565C0; font-weight: bold; }
    .mnemo-story { background: #FFF3E0; padding: 10px; border-radius: 10px; border-left: 4px solid #FF9800; font-style: italic; }
    .stButton>button { border-radius: 25px; background-color: #2E7D32; color: white; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('bible_database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mes_versets 
                 (id INTEGER PRIMARY KEY, livre TEXT, passage TEXT, texte TEXT, histoire TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- DONNÉES DES SEGMENTS (TES NOTES) ---
segments_data = {
    "S1: La Voie de l'Abondance": {
        "acronyme": "A.P.V (Abondance, Puissance, Voie)",
        "histoire": "Imagine un chemin (Voie) en or où les arbres poussent des billets (Abondance) et quand tu touches une feuille, tu reçois une décharge électrique de super-héros (Puissance).",
        "versets": "Jean 14:6, Jean 10:30"
    },
    "S2: La Norme (Pentateuque)": {
        "acronyme": "G.E.L.N.D (Gèle-Ne-Dégèle)",
        "histoire": "GEorges (Genèse) l'EX-catcheur (Exode) LÉvite (Lévitique) sur un nuage de NOMBRES (Nombres) pour DEscendre (Deutéronome) au marché.",
        "versets": "Jean 10:10, Actes 10:38"
    },
    "S5: Clés d'Interprétation": {
        "acronyme": "C.O.A (Contexte, Objet, Adresse)",
        "histoire": "Un détective avec une loupe géante regarde une lettre. Il vérifie le CONTEXTE (la météo), l'OBJET (un diamant volé) et l'ADRESSE (à qui c'est écrit).",
        "versets": "2 Pierre 1:20, 1 Cor 10:32"
    },
    "S11: La Chute & La Semence": {
        "acronyme": "M.R.O.A.C (Le piège de la Chute)",
        "histoire": "Satan est un cuisinier qui : Met en question, Répond, Omet le sel, Ajoute du piment et Change la recette !",
        "versets": "Genèse 3:15, 1 Jean 3:8"
    }
}

# --- MENU NAVIGATION ---
menu = ["🏠 Accueil", "📖 Mes Passages", "🎓 Parcours 12 Segments", "📚 Les 66 Livres"]
choix = st.sidebar.radio("Navigation", menu)

if choix == "🏠 Accueil":
    st.title("⚡ Bible Abondance & Puissance")
    st.image("https://images.unsplash.com/photo-1504052434139-441c27e43d93?q=80&w=500") # Image inspirante
    st.write("Bienvenue Rosly ! Utilise cette app pour transformer la Parole en puissance mémorisée.")

elif choix == "🎓 Parcours 12 Segments":
    st.header("Entraînement par Segment")
    for titre, info in segments_data.items():
        with st.expander(titre):
            st.markdown(f"**Acronyme :** `{info['acronyme']}`")
            st.markdown(f"<div class='mnemo-story'>🎬 {info['histoire']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Versets clés :** <span class='bible-ref'>{info['versets']}</span>", unsafe_allow_html=True)

elif choix == "📖 Mes Passages":
    st.header("Enregistre ton Verset")
    
    with st.form("ajout_verset"):
        l = st.text_input("Livre")
        p = st.text_input("Chapitre:Verset")
        t = st.text_area("Texte du verset")
        h = st.text_area("Ton histoire loufoque pour mémoriser")
        
        if st.form_submit_button("Graver dans le marbre"):
            c = conn.cursor()
            c.execute("INSERT INTO mes_versets (livre, passage, texte, histoire) VALUES (?,?,?,?)", (l, p, t, h))
            conn.commit()
            st.success("C'est enregistré !")

    st.divider()
    st.subheader("Ma Bibliothèque")
    df = pd.read_sql_query("SELECT * FROM mes_versets", conn)
    for i, row in df.iterrows():
        st.markdown(f"""
        <div class='segment-card'>
            <h4>{row['livre']} {row['passage']}</h4>
            <p>"{row['texte']}"</p>
            <div class='mnemo-story'>🧠 {row['histoire']}</div>
        </div>
        """, unsafe_allow_html=True)

elif choix == "📚 Les 66 Livres":
    st.header("L'ordre des 66 Livres")
    st.info("Méthode mnémotechnique complète")
    st.write("**Pentateuque :** GEorges l'EX-catcheur LÉvite sur des NOMBRES pour DEscendre.")
    st.write("**Historiques :** JOSUÉ et les JUGES mangent une RUTHabaga...")
    # Tu peux continuer ici selon tes notes pour les 66 livres.
