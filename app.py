import streamlit as st
import sqlite3
import anthropic
import json
from datetime import datetime

st.set_page_config(
    page_title="Bible Memory ✝️",
    page_icon="✝️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
# CSS MOBILE-FIRST
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --gold:#C9A84C; --dark:#0D0D1A; --mid:#14142A;
    --card:#1A1A35; --accent:#E94560; --text:#F0E6D3;
    --green:#27AE60; --purple:#8E44AD; --blue:#2980B9; --border:#2A2A4A;
}
.stApp{background:var(--dark);color:var(--text);font-family:'Segoe UI',sans-serif;}
.app-header{text-align:center;padding:1rem 0 0.4rem;margin-bottom:.8rem;}
.app-title{font-size:1.9rem;font-weight:900;color:var(--gold);
    text-shadow:0 0 25px rgba(201,168,76,.5);margin:0;}
.app-sub{color:#777;font-size:.78rem;margin:.2rem 0 0;}
.sec-title{font-size:1rem;font-weight:800;color:var(--gold);
    border-bottom:2px solid var(--gold);padding-bottom:.2rem;margin:1rem 0 .6rem;}
.card{background:var(--card);border-radius:14px;padding:.9rem;
    margin:.5rem 0;border:1px solid var(--border);}
.card-gold{border-left:4px solid var(--gold);}
.card-red{border-left:4px solid var(--accent);}
.card-green{border-left:4px solid var(--green);}
.card-purple{border-left:4px solid var(--purple);}
.card-blue{border-left:4px solid var(--blue);}
.verse-box{background:rgba(255,255,255,.04);border-radius:10px;
    padding:.75rem;font-size:.88rem;line-height:1.7;color:var(--text);
    border-left:3px solid var(--gold);}
.story-box{background:rgba(142,68,173,.1);border-radius:10px;
    padding:.75rem;font-style:italic;font-size:.84rem;
    line-height:1.6;color:#ddd;border:1px solid rgba(142,68,173,.3);}
.mnemo-box{background:rgba(39,174,96,.1);border-radius:10px;
    padding:.75rem;font-size:.86rem;color:#2ECC71;
    border:1px solid rgba(39,174,96,.3);line-height:1.5;}
.ref-pill{display:inline-block;background:rgba(41,128,185,.2);color:#5DADE2;
    border:1px solid rgba(41,128,185,.4);border-radius:20px;
    font-size:.7rem;font-weight:700;padding:2px 7px;margin:2px;}
.stat-card{background:var(--card);border-radius:12px;padding:.7rem;
    text-align:center;border:1px solid var(--border);}
.stat-num{font-size:1.7rem;font-weight:900;color:var(--gold);margin:0;}
.stat-lbl{font-size:.7rem;color:#888;margin:0;}
.seg-num{background:var(--gold);color:#0D0D1A;font-weight:900;
    border-radius:50%;width:30px;height:30px;display:inline-flex;
    align-items:center;justify-content:center;font-size:.85rem;
    flex-shrink:0;margin-right:.4rem;}
.stButton>button{background:linear-gradient(135deg,var(--gold),#a0760a);
    color:#0D0D1A;font-weight:800;border:none;border-radius:10px;
    padding:.5rem;cursor:pointer;transition:all .2s;width:100%;}
.stButton>button:hover{opacity:.88;transform:translateY(-1px);}
.stTextInput input,.stTextArea textarea{background:var(--mid)!important;
    color:var(--text)!important;border:1px solid var(--border)!important;border-radius:8px!important;}
div[data-testid="stExpander"]{background:var(--card);border:1px solid var(--border);border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# DONNÉES — 12 SEGMENTS DU COURS
# ─────────────────────────────────────────────────────────────────
COURS_DATA = [
    {
        "num":1,"titre":"La Voie de l'Abondance et de la Puissance",
        "theme":"Dieu désire que son peuple prospère physiquement, mentalement et spirituellement. Jésus Christ est la voie, la vérité et la vie. Notre libre arbitre nous permet de choisir d'obéir à Sa Parole et de jouir de l'abondance qu'Il a pour nous.",
        "refs_cles":["Jean 14:6","Jean 4:34","Jean 5:30","Jean 6:38","Jean 8:29","Jean 10:30","Jean 12:49-50"],
        "refs_sec":["Deutéronome 30:14-20","Aggée 1:5","Matthieu 22:29","Jean 8:31-32"],
        "passage_cle":"Jean 14:6","chap":14,"v_deb":6,"v_fin":6,"livre_cle":"Jean",
        "texte_cle":"Jésus lui dit : Je suis le chemin, la vérité, et la vie. Nul ne vient au Père que par moi.",
        "mnemo":"🛣️ JVC = JÉSUS-VOIE-CHEMIN\nJésus = le GPS parfait qui ne ment jamais et ne tombe jamais en panne !\n3 promesses : 📍Chemin (il guide) → 📖 Vérité (il enseigne) → 💚 Vie (il donne)",
        "histoire":"Un homme perdu dans un désert appelle un GPS. La voix répond : 'Je suis JÉSUS, le Chemin, la Vérité et la Vie.' L'homme dit : 'Recalcul en cours ?' Jésus répond : 'Non. Je ne recalcule jamais. Je suis déjà arrivé là où tu vas.' L'homme suit les instructions. Il arrive dans un jardin rempli d'abondance. Son GPS dit : 'Vous êtes arrivé. Et au fait, profitez — c'est tout pour vous.' Fin du trajet. Début de la vie."
    },
    {
        "num":2,"titre":"La Parole de Dieu est la Norme",
        "theme":"La vérité demeure qu'on la croie ou non. Les objectifs du voleur : dérober, égorger et détruire. Jésus est venu pour donner la vie en abondance. L'autorité et l'intégrité de la Parole révélée de Dieu est notre norme absolue.",
        "refs_cles":["Jean 10:10","1 Jean 3:7-8","Actes 10:38"],
        "refs_sec":["2 Pierre 1:20-21","Genèse 3:15","Ésaïe 9:6-8","Hébreux 6:18","Nombres 23:19","Malachie 3:6","Romains 16:25-26","Éphésiens 3:3-4","Galates 1:11-12","Deutéronome 29:29","Hébreux 4:12","Actes 8:29-31"],
        "passage_cle":"Jean 10:10","chap":10,"v_deb":10,"v_fin":10,"livre_cle":"Jean",
        "texte_cle":"Le voleur ne vient que pour dérober, égorger et détruire ; moi, je suis venu afin que les brebis aient la vie, et qu'elles soient dans l'abondance.",
        "mnemo":"⚖️ VOLEUR vs JÉSUS — Jean 10:10\n❌ Voleur = 3D : Dérober – Détruire – Décimer\n✅ Jésus = 3V : Vie – Victoire – Volume d'abondance\n📌 10/10 = la note parfaite de Dieu pour Sa Parole !",
        "histoire":"Un cambrioleur débarque avec un sac estampillé 'Misère & Destruction'. Il renverse tout, vole la joie, casse l'espoir et repart. Cinq minutes plus tard, Jésus sonne à la porte avec un camion-citerne rempli d'abondance. Il répare tout, remplit chaque pièce de vie débordante et pose une pancarte 'PLUS JAMAIS'. Le cambrioleur revient. La porte résiste. Pourquoi ? Parce que la Parole de Dieu est un verrou incassable."
    },
    {
        "num":3,"titre":"La Sûreté de Nos Jours",
        "theme":"Nous pouvons apprendre à retenir la Parole dans notre intelligence et agir selon elle. La sincérité n'est pas une garantie pour la vérité — seule la Parole de Dieu l'est. Sa Parole est une lampe à nos pieds et une lumière sur notre sentier.",
        "refs_cles":["2 Pierre 1:20-21","2 Timothée 3:16","Matthieu 4:4"],
        "refs_sec":["Éphésiens 3:3","Romains 16:25","Galates 1:11-12","Matthieu 5:18","Psaumes 12:7","Psaumes 119:105","Psaumes 119:160","Ésaïe 33:5-6","Exode 31:18"],
        "passage_cle":"Psaumes 119:105","chap":119,"v_deb":105,"v_fin":105,"livre_cle":"Psaumes",
        "texte_cle":"Ta parole est une lampe à mes pieds, et une lumière sur mon sentier.",
        "mnemo":"🔦 LAMPE + LUMIÈRE = PAROLE\nPieds = présent (lampe = éclaire le prochain pas)\nSentier = futur (lumière = éclaire la route entière)\n📌 La Parole = GPS + lampe torche + boussole en un !",
        "histoire":"Un explorateur part dans une grotte sombre avec deux gadgets : une lampe-frontale (Parole pour les pieds) et un phare géant (Parole pour le sentier). Les autres explorent sincèrement... mais dans le noir. Ils se cognent aux stalactites, tombent dans des trous. Notre explorateur avance sereinement. Il sort bronzé et plein de trésors. La sincérité n'éclaire pas. La Parole, si."
    },
    {
        "num":4,"titre":"Le Sujet de Toute la Parole de Dieu",
        "theme":"Jésus Christ est le passe-partout à l'interprétation de la Parole. Il a divisé la Parole en trois catégories : la Loi, les Prophètes et les Psaumes. Se présenter devant Dieu comme un homme éprouvé, un ouvrier approuvé. La Parole de Dieu est la volonté de Dieu.",
        "refs_cles":["Luc 24:44-45","2 Timothée 2:15","Psaumes 119:89"],
        "refs_sec":["Jean 1:45","1 Jean 5:20","Colossiens 1:18-19","Colossiens 2:9-10","1 Thessaloniciens 2:4","Psaumes 138:2","Ésaïe 55:8-11","Colossiens 3:16","Actes 17:11","Jean 5:39","Exode 24:7","Deutéronome 17:18-20","Néhémie 8:8","Psaumes 119:16,24,77,174","Éphésiens 3:3-4","Colossiens 4:16","1 Thessaloniciens 5:27"],
        "passage_cle":"2 Timothée 2:15","chap":2,"v_deb":15,"v_fin":15,"livre_cle":"2 Timothée",
        "texte_cle":"Efforce-toi de te présenter devant Dieu comme un homme éprouvé, un ouvrier qui n'a point à rougir, qui dispense droitement la parole de la vérité.",
        "mnemo":"🔑 JÉSUS = CLÉ PASSE-PARTOUT de toute la Bible\nLoi + Prophètes + Psaumes → JÉSUS est au centre de tout !\n📌 Ouvrier approuvé = Effort + Droiture + Parole bien divisée",
        "histoire":"Un serrurier reçoit 1500 clés pour ouvrir une porte mystérieuse. Il essaie clé par clé pendant des années. Puis quelqu'un lui tend une seule clé dorée : 'Jésus-Christ'. Elle ouvre toutes les portes d'un coup. Toute la Loi, tous les Prophètes, tous les Psaumes — une seule clé les déverrouille. Le serrurier jette les 1499 autres et devient le meilleur ouvrier de la Parole du quartier."
    },
    {
        "num":5,"titre":"Les Clés à l'Interprétation de la Parole",
        "theme":"Toute Écriture s'interprète elle-même : dans le verset, dans le contexte. Le verset difficile doit être compris à la lumière des versets clairs. L'interprétation et l'application tiennent toujours compte de à qui c'est adressé et de la période de temps.",
        "refs_cles":["2 Pierre 1:20","1 Timothée 3:16","1 Corinthiens 10:31-32"],
        "refs_sec":["Romains 15:4","Jacques 5:10"],
        "passage_cle":"2 Pierre 1:20","chap":1,"v_deb":20,"v_fin":20,"livre_cle":"2 Pierre",
        "texte_cle":"Sachez d'abord vous-mêmes qu'aucune prophétie de l'Écriture ne peut être un objet d'interprétation particulière.",
        "mnemo":"📖 3 RÈGLES D'OR de l'interprétation :\n1️⃣ CONTEXTE — La Bible s'explique par elle-même\n2️⃣ CLARTÉ — Le verset obscur cède au verset clair\n3️⃣ CIBLE — À qui est-ce adressé ? Dans quelle époque ?",
        "histoire":"Un détective biblique reçoit un message crypté. Son assistant : 'Cherchons des experts extérieurs !' Le détective : 'Non. La Bible se déchiffre elle-même.' Il sort sa loupe, compare verset à verset, époque à époque. Le message devient clair. Pas d'interprétation solitaire, pas de hors-contexte. La Bible est son propre dictionnaire, son propre traducteur, son propre guide touristique."
    },
    {
        "num":6,"titre":"Au Commencement",
        "theme":"Au commencement, Jésus Christ était dans la présence de Dieu. Dieu est l'Initiateur du salut et Jésus Christ en est l'Agent. La terre était devenue informe et vide à cause de l'adversaire. La Parole de Dieu est notre norme de croyance et d'action.",
        "refs_cles":["Genèse 1:1","Jean 1:1-4","Hébreux 11:3"],
        "refs_sec":["2 Pierre 1:3","Matthieu 1:18","Jean 1:5","Genèse 1:1-2","Ézéchiel 28:12-17","Jérémie 4:23"],
        "passage_cle":"Jean 1:1-2","chap":1,"v_deb":1,"v_fin":2,"livre_cle":"Jean",
        "texte_cle":"Au commencement était la Parole, et la Parole était avec Dieu, et la Parole était Dieu. Elle était au commencement avec Dieu.",
        "mnemo":"🌌 AU COMMENCEMENT = 3 ÉTAPES\n1. CHAOS → La terre était informe et vide (adversaire)\n2. CRÉATION → Dieu parle, tout existe (Parole créatrice)\n3. CHRIST → Déjà là avant le début (Jean 1:1)\n📌 Avant le Big Bang : le BIG WORD !",
        "histoire":"Avant même que l'Univers n'existe, Jésus et Dieu prenaient le café dans l'éternité. Dieu dit : 'Et si on créait quelque chose ?' BOUM — galaxies, étoiles, planètes. Mais l'adversaire sabote la Terre et la laisse informe et vide. Dieu ne panique pas. Il reprend son projet depuis le début et le reconstruit, encore meilleur. Morale : Dieu n'abandonne jamais ses projets."
    },
    {
        "num":7,"titre":"La Surface de l'Abîme",
        "theme":"Les trois cieux et les trois terres. Dieu prépare la terre. La seule masse terrestre de Genèse s'est divisée au temps de Péleg. La terre a changé après le déluge et la dispersion à Babel.",
        "refs_cles":["Genèse 1:2","1 Jean 1:5","2 Pierre 3:5-6"],
        "refs_sec":["Genèse 1:2-5","Genèse 1:14-19","Apocalypse 21:1","Genèse 6:1","Genèse 4:16-17"],
        "passage_cle":"Genèse 1:2","chap":1,"v_deb":2,"v_fin":2,"livre_cle":"Genèse",
        "texte_cle":"La terre était informe et vide : il y avait des ténèbres à la surface de l'abîme, et l'esprit de Dieu se mouvait au-dessus des eaux.",
        "mnemo":"🌊 3 CIELS + 3 TERRES :\n🌍 Terre 1 = Originelle (avant la chute de Satan)\n🌍 Terre 2 = Actuelle (depuis la re-création)\n🌍 Terre 3 = Nouvelle (Apocalypse 21)\n📌 Péleg = 'division' → les continents sont nés !",
        "histoire":"Imaginez un puzzle de 7 milliards de pièces, toutes collées (Pangée biblique). Satan passe par là et renverse tout. Dieu récupère les pièces, les recolle progressivement. Noé prend un bateau car tout était encore une masse. À Babel, les gens se dispersent. Au temps de Péleg, le puzzle géant se découpe en continents. L'Afrique, l'Europe, l'Amérique — tous issus du même puzzle de Genèse 1."
    },
    {
        "num":8,"titre":"L'Idiome de Permission",
        "theme":"Un idiome est un usage de mots particulier à une langue. L'idiome hébreu de permission permet de ne jamais attribuer le mal à Dieu. La raison d'être de l'Univers est la Terre, celle de la Terre est l'Homme, celle de l'Homme est d'aimer Dieu.",
        "refs_cles":["Exode 10:20","Genèse 6:8-13","Matthieu 22:36-37"],
        "refs_sec":["Genèse 1:9-13","Genèse 1:14","Genèse 1:24-25"],
        "passage_cle":"Matthieu 22:36-37","chap":22,"v_deb":36,"v_fin":37,"livre_cle":"Matthieu",
        "texte_cle":"Maître, quel est le grand commandement de la loi ? Jésus lui répondit : Tu aimeras le Seigneur, ton Dieu, de tout ton cœur, de toute ton âme, et de toute ta pensée.",
        "mnemo":"🎭 IDIOME HÉBREU DE PERMISSION\n❌ Dieu n'a PAS durci le cœur de Pharaon directement\n✅ Dieu a PERMIS que Pharaon fasse ses propres choix\nFormule : 'Dieu a fait X' = souvent 'Dieu a PERMIS X'\n📌 Ne jamais attribuer le mal à Dieu !",
        "histoire":"Un journaliste écrit : 'Dieu a durci le cœur de Pharaon.' Un expert hébreu corrige : 'En hébreu idiomatique, ça veut dire que Dieu a permis que Pharaon fasse ses propres choix.' Le journaliste relit ses articles — il avait accusé Dieu de 47 catastrophes ! L'expert explique : la raison d'être de l'Univers, c'est la Terre ; de la Terre, c'est l'Homme ; de l'Homme, c'est d'aimer Dieu. Pharaon avait choisi de court-circuiter tout ça."
    },
    {
        "num":9,"titre":"Les Fondements de Toute Vie",
        "theme":"Le but et la signification de la création : les fondements de toute vie. L'homme est constitué de Corps (formé), d'Âme (faite) et d'Esprit (créé). Dieu est Esprit, et l'homme a été créé pour communier avec Lui.",
        "refs_cles":["Genèse 1:26","Genèse 2:7","Jean 4:24"],
        "refs_sec":["Actes 27:37","Lévitique 17:11","Genèse 1:28"],
        "passage_cle":"Genèse 1:26","chap":1,"v_deb":26,"v_fin":26,"livre_cle":"Genèse",
        "texte_cle":"Dieu dit : Faisons l'homme à notre image, selon notre ressemblance, et qu'il domine sur les poissons de la mer, sur les oiseaux du ciel, sur le bétail, sur toute la terre.",
        "mnemo":"🧬 L'HOMME = 3 DIMENSIONS :\n🫀 CORPS = Formé (comme de l'argile — Genèse 2:7)\n💛 ÂME = Faite (siège des émotions — Lév. 17:11)\n✨ ESPRIT = Créé (pour communier avec Dieu — Jean 4:24)\n📌 Dieu est Esprit → Il communique avec notre esprit !",
        "histoire":"Dieu fabrique l'homme comme un chef cuisinier fait son plat signature. Il prend de la terre (corps), souffle dessus (esprit), et la créature devient une âme vivante. Le chef dit : 'Image de Moi !' L'homme se regarde dans le miroir et voit un être royal avec couronne et sceptre. La grenouille dans l'étang voisin est impressionnée. L'homme est littéralement la meilleure œuvre de Dieu."
    },
    {
        "num":10,"titre":"La Connaissance du Bien et du Mal",
        "theme":"La Parole de Dieu est une Parole de vie, pas un simple livre de morale. Dieu voulait que l'homme expérimente le bien et évite le mal. Les bénédictions nous appartiennent quand nous choisissons la vie. La femme est une compagne dans la relation du mariage.",
        "refs_cles":["Genèse 2:8-9","Genèse 2:16-17","Genèse 2:18"],
        "refs_sec":["Proverbes 1:17","Genèse 2:1","Genèse 2:4-7","Ésaïe 42:5","Luc 1:35","Genèse 2:10-17","Genèse 2:21-24"],
        "passage_cle":"Genèse 2:16-17","chap":2,"v_deb":16,"v_fin":17,"livre_cle":"Genèse",
        "texte_cle":"L'Éternel Dieu donna cet ordre à l'homme : Tu pourras manger de tous les arbres du jardin ; mais tu ne mangeras pas de l'arbre de la connaissance du bien et du mal, car le jour où tu en mangeras, tu mourras.",
        "mnemo":"🌳 JARDIN = LIBERTÉ avec UNE SEULE LIMITE :\n✅ TOUS les arbres = OUI (abondance totale)\n❌ UN seul arbre = NON (protection, pas punition)\n📌 Dieu donne 99% de OUI pour 1% de NON.\nL'homme s'est fixé sur le 1%. Erreur fatale !",
        "histoire":"Dieu ouvre un buffet à volonté avec 10 000 plats délicieux. Il dit : 'Mangez tout ! Sauf ce plat au bout de la table.' Adam et Ève ont 9 999 plats à disposition. Mais le 10 000ème les obsède. 'Pourquoi pas celui-là ?' Dieu répond : 'Parce que c'est du poison.' Ils le mangent quand même. Morale : Dieu donne l'abondance totale. Le problème, c'est notre fixation sur le seul interdit."
    },
    {
        "num":11,"titre":"Le Premier Péché de l'Humanité",
        "theme":"Satan met en question l'intégrité de la Parole, pousse à considérer, omet, ajoute et change la Parole. L'homme a perdu la domination. Jésus Christ est la semence promise qui écrase la tête de l'adversaire et redonne à l'homme l'accès libre à Dieu.",
        "refs_cles":["Genèse 3:1-6","Genèse 3:15","1 Jean 3:8"],
        "refs_sec":["Genèse 2:16-17","Genèse 3:7-14","Genèse 1:28","Jean 14:30","Genèse 3:16"],
        "passage_cle":"Genèse 3:15","chap":3,"v_deb":15,"v_fin":15,"livre_cle":"Genèse",
        "texte_cle":"Je mettrai inimitié entre toi et la femme, entre ta postérité et sa postérité : celle-ci t'écrasera la tête, et tu lui blesseras le talon.",
        "mnemo":"🐍 LES 5 TACTIQUES DE SATAN (Genèse 3) :\n1️⃣ QUESTIONNE l'intégrité ('A-t-il vraiment dit ?')\n2️⃣ POUSSE à considérer l'interdit\n3️⃣ OMET les conséquences\n4️⃣ AJOUTE ('ni y toucher' — Ève modifie la Parole !)\n5️⃣ CHANGE ('Vous ne mourrez PAS')\n📌 Genèse 3:15 = 1ère prophétie messianique !",
        "histoire":"Satan arrive en mode débat avec micro et tableau. Étape 1 : 'Dieu a vraiment dit ÇA ?' (doute). Étape 2 : 'Regarde comme c'est beau l'arbre interdit' (tentation). Étape 3 : Il oublie de mentionner la mort. Étape 4 : Ève ajoute 'ni toucher'. Étape 5 : Satan ment : 'Vous ne mourrez PAS !' Résultat : chute. Mais Dieu répond au verset 15 : 'La semence de la femme t'écrasera la tête.' Satan perd avant même de célébrer."
    },
    {
        "num":12,"titre":"Le Plus Grand Principe : La Croyance",
        "theme":"Pour recevoir quoi que ce soit de Dieu, on doit savoir ce qui est disponible, comment le recevoir et qu'en faire. La croyance provient du cœur. Confesser de la bouche, du cœur et avec nos actions. La vie synchronisée = Parole + Cœur + Actions alignés.",
        "refs_cles":["Jean 15:16","Romains 10:10","Éphésiens 1:19"],
        "refs_sec":["3 Jean 2","2 Corinthiens 9:8","Romains 8:37","Éphésiens 3:16-19","Jacques 1:21","1 Jean 5:14","Philippiens 4:19","Romains 4:20-21","Hébreux 11:11","Éphésiens 3:20","Marc 11:22-24","Proverbes 4:20-23","Proverbes 23:7"],
        "passage_cle":"Romains 10:10","chap":10,"v_deb":10,"v_fin":10,"livre_cle":"Romains",
        "texte_cle":"Car c'est en croyant du cœur qu'on parvient à la justice, et c'est en confessant de la bouche qu'on parvient au salut.",
        "mnemo":"🔑 3 ÉTAPES DE LA CROYANCE VICTORIEUSE :\n1️⃣ SAVOIR — Quelle est la promesse de Dieu pour mon besoin ?\n2️⃣ IMAGINER — Mettre l'image de la victoire dans mon esprit\n3️⃣ AGIR — Agir fidèlement selon la promesse\n📌 Bouche + Cœur + Actions = VIE SYNCHRONISÉE !",
        "histoire":"Un athlète veut gagner la course. Étape 1 : il lit le règlement (Parole disponible). Étape 2 : il s'imagine franchir la ligne d'arrivée chaque matin (image de croyance). Étape 3 : il s'entraîne selon la promesse de victoire (action fidèle). Le jour J, il ne court pas seul — la Parole de Dieu court avec lui. Il franchit la ligne avec une facilité déconcertante. Dans les gradins, trois anges prennent des notes : 'Voilà comment fonctionne la croyance.'"
    }
]

ALL_BOOKS_ORDERED = [
    "Genèse","Exode","Lévitique","Nombres","Deutéronome",
    "Josué","Juges","Ruth","1 Samuel","2 Samuel",
    "1 Rois","2 Rois","1 Chroniques","2 Chroniques",
    "Esdras","Néhémie","Esther","Job","Psaumes","Proverbes",
    "Ecclésiaste","Cantique des Cantiques","Ésaïe","Jérémie",
    "Lamentations","Ézéchiel","Daniel","Osée","Joël","Amos",
    "Abdias","Jonas","Michée","Nahum","Habacuc","Sophonie",
    "Aggée","Zacharie","Malachie","Matthieu","Marc","Luc","Jean",
    "Actes des Apôtres","Romains","1 Corinthiens","2 Corinthiens",
    "Galates","Éphésiens","Philippiens","Colossiens",
    "1 Thessaloniciens","2 Thessaloniciens","1 Timothée","2 Timothée",
    "Tite","Philémon","Hébreux","Jacques","1 Pierre","2 Pierre",
    "1 Jean","2 Jean","3 Jean","Jude","Apocalypse"
]

BIBLE_GROUPS = {
    "Pentateuque (5)":{"livres":["Genèse","Exode","Lévitique","Nombres","Deutéronome"],
        "acronyme":"GE-EX-LÉV-NOM-DEU",
        "mnemo":"📌 GEorges EXplose LEVitant sur NOMbreux DEUtons !\nImagine : GEorges (un boucher géant) EXplose en LÉVitant, compte un NOMbre de fois et le fait DEUx fois !",
        "histoire":"GEorges, gros boucher du marché, décide d'EXplorer la ville en LÉVitant. Il rencontre un clown jonglant avec un NOMbre de pommes. DEUx éléphants roses lui lisent le règlement en chœur. Voilà comment GEorges comprend la Loi."},
    "Livres Historiques (12)":{"livres":["Josué","Juges","Ruth","1 Samuel","2 Samuel","1 Rois","2 Rois","1 Chroniques","2 Chroniques","Esdras","Néhémie","Esther"],
        "acronyme":"JO-JU-RU-SA-SA-R-R-CH-CH-ESD-NÉH-EST",
        "mnemo":"📌 JOJo le JUgeur RUe vers deux SAmuels, deux Rois, deux CHroniques, ESDras, NÉHémie, ESTher !",
        "histoire":"JOJo le clown JUgeur atterrit sur une RUche avec deux SAuterelles en costume. Deux Rois (Lion & Requin) se battent avec des CHronometeurs. Dragon ESDras souffle du feu sur NÉHumiste qui fond sur une ESTrade."},
    "Livres Poétiques (5)":{"livres":["Job","Psaumes","Proverbes","Ecclésiaste","Cantique des Cantiques"],
        "acronyme":"JOB-PS-PRO-ECC-CAN",
        "mnemo":"📌 JOBert le chômeur PSyché chante des PROverbes ECCentriques sur son CANapé !",
        "histoire":"JOBert est au chômage depuis 3 siècles. Son PSychologue conseille chanter des PROverbes. JOBert, ECCentrique, le fait sur son CANapé en pyjama de licorne en mangeant de la fondue. Sa voisine filme pour TikTok."},
    "Grands Prophètes (5)":{"livres":["Ésaïe","Jérémie","Lamentations","Ézéchiel","Daniel"],
        "acronyme":"ÉS-JÉR-LAM-ÉZ-DAN",
        "mnemo":"📌 ÉSpadon rencontre JÉRôme qui se LAMente, ÉZéchias appelle DANiel le danseur !",
        "histoire":"Un ÉSpadon géant frappe chez JÉRôme, paysan qui se LAMente car sa moustache a disparu. ÉZéchias arrive en robe de soirée et appelle DANiel, danseur de lion professionnel, pour résoudre cette crise capillaire urgente."},
    "Petits Prophètes (12)":{"livres":["Osée","Joël","Amos","Abdias","Jonas","Michée","Nahum","Habacuc","Sophonie","Aggée","Zacharie","Malachie"],
        "acronyme":"OS-JO-AM-AB-JON-MI-NA-HA-SO-AG-ZA-MAL",
        "mnemo":"📌 OS du JOuet de l'AMbassadeur tombe sur ABricot, JONquille dans MIroir mange NAvet et HAricot en SOurdine, AG ZA MAL !",
        "histoire":"Diplomate perd l'OS de son jouet. Il atterrit sur un ABricot qui fait pousser une JONquille. La fleur se regarde dans un MIroir et mange NAvet puis HAricot discrètement (SOurdine). Elle note dans son AGenda : 'ZApper la MALette'. La police débarque."},
    "Les 4 Évangiles":{"livres":["Matthieu","Marc","Luc","Jean"],
        "acronyme":"MAT-MAR-LU-JE",
        "mnemo":"📌 MA-MAR-LU-JE → MATelas, MARmite, LUciole, JEton ! Méthode ultra-simple !",
        "histoire":"MAT le matelas bavard glisse et atterrit dans la MARmite de LUciole, cheffe cuisinière. Pour payer les dommages, il donne des JEtons de casino. Le commissaire arrivé est aussi un matelas. Fin."},
    "Actes des Apôtres (1)":{"livres":["Actes des Apôtres"],
        "acronyme":"ACTES",
        "mnemo":"📌 Après les 4 évangiles, les ACTES commencent le grand spectacle de l'Église !",
        "histoire":"Jour de Pentecôte : 120 ACrobates débarquent sur la scène du Temple. Sauts périlleux en 17 langues. Pierre prend le micro : 'Nous ne sommes pas ivres, il est 9h du matin !' Applaudissements. L'Église est née."},
    "Lettres de Paul (13)":{"livres":["Romains","1 Corinthiens","2 Corinthiens","Galates","Éphésiens","Philippiens","Colossiens","1 Thessaloniciens","2 Thessaloniciens","1 Timothée","2 Timothée","Tite","Philémon"],
        "acronyme":"RO-CO-CO-GA-ÉP-PH-CO-TH-TH-TI-TI-TIT-PHI",
        "mnemo":"📌 ROmains, deux COrinthiens, GAlates, ÉPhésiens, PHilippiens, COlossiens, deux THessaloniciens, deux TImothée, TIte, PHIlémon !",
        "histoire":"Paul-RObot avale deux COraux comme chips et un GAteau ÉPhémère. Suit un PHare jusqu'à une statue COLOSSale, boit deux THéières, affronte deux TIgres. Le vainqueur est TITon, philosophe chauve. Paul écrit tout ça."},
    "Lettres Générales (8)":{"livres":["Hébreux","Jacques","1 Pierre","2 Pierre","1 Jean","2 Jean","3 Jean","Jude"],
        "acronyme":"HÉB-JAC-PI-PI-J-J-J-JU",
        "mnemo":"📌 HÉBergeur + JACquot + 2 PIerres + 3 Jeans + JUde dans le même couloir d'hôtel !",
        "histoire":"HÉBergeur gère le chaos : JACquot le perroquet réserve 2 chambres pour les frères PIerre (qui se disputent lequel est le vrai). Trois cousins prénommés JEAN arrivent avec le même bagage. JUde arrive avec un tambourin. L'hôtel ferme."},
    "Apocalypse (1)":{"livres":["Apocalypse"],
        "acronyme":"APOCALYPSE",
        "mnemo":"📌 L'APOCALYPSE = Grand Finale de la Bible. Impossible à oublier — gardez-le pour la fin !",
        "histoire":"Jean exilé sur Patmos reçoit la vision ultime : un agneau ouvre 7 sceaux-enveloppes géantes. 7 anges soufflent dans des trompettes désaccordées. Un dragon rouge danse la samba. Une ville en or descend du ciel. Le stylo de Jean explose."}
}

# ─────────────────────────────────────────────────────────────────
# BASE DE DONNÉES
# ─────────────────────────────────────────────────────────────────
DB_PATH = "bible_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS passages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seg_num INTEGER DEFAULT 0, seg_titre TEXT DEFAULT '',
        livre TEXT NOT NULL, chapitre INTEGER NOT NULL,
        v_deb INTEGER NOT NULL, v_fin INTEGER,
        texte TEXT NOT NULL, mnemo TEXT DEFAULT '',
        histoire TEXT DEFAULT '', date_ajout TEXT NOT NULL,
        est_seed INTEGER DEFAULT 0
    )""")
    c.execute("SELECT COUNT(*) FROM passages WHERE est_seed=1")
    if c.fetchone()[0] == 0:
        _seed(c)
    conn.commit(); conn.close()

def _seed(c):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for s in COURS_DATA:
        c.execute("""INSERT INTO passages
            (seg_num,seg_titre,livre,chapitre,v_deb,v_fin,texte,mnemo,histoire,date_ajout,est_seed)
            VALUES (?,?,?,?,?,?,?,?,?,?,1)""",
            (s["num"],s["titre"],s["livre_cle"],s["chap"],s["v_deb"],s["v_fin"],
             s["texte_cle"],s["mnemo"],s["histoire"],now))

def get_passages(search="", seg_filter=0, perso_only=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    q = "SELECT * FROM passages WHERE 1=1"
    p = []
    if perso_only:
        q += " AND est_seed=0"
    if search:
        q += " AND (LOWER(livre) LIKE ? OR LOWER(texte) LIKE ? OR LOWER(seg_titre) LIKE ?)"
        s = f"%{search.lower()}%"; p += [s,s,s]
    if seg_filter > 0:
        q += " AND seg_num=?"; p.append(seg_filter)
    q += " ORDER BY seg_num ASC, id ASC"
    c.execute(q, p); rows = c.fetchall(); conn.close(); return rows

def add_passage(sn, st_, livre, chap, vd, vf, texte, mnemo, hist):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("""INSERT INTO passages
        (seg_num,seg_titre,livre,chapitre,v_deb,v_fin,texte,mnemo,histoire,date_ajout,est_seed)
        VALUES (?,?,?,?,?,?,?,?,?,?,0)""",
        (sn,st_,livre,chap,vd,vf,texte,mnemo,hist,
         datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

def delete_passage(pid):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM passages WHERE id=?", (pid,))
    conn.commit(); conn.close()

def update_mnemo(pid, mnemo, hist):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("UPDATE passages SET mnemo=?, histoire=? WHERE id=?", (mnemo,hist,pid))
    conn.commit(); conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(CASE WHEN est_seed=0 THEN 1 ELSE 0 END) FROM passages")
    r = c.fetchone(); conn.close(); return r

def generate_mnemo_ai(api_key, livre, ref, texte):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-opus-4-5", max_tokens=800,
            messages=[{"role":"user","content":
                f"""Expert en mémorisation biblique créative et humoristique en français.
Pour ce passage, crée :
1. Un MOYEN MNÉMOTECHNIQUE original (acronyme, images, rimes)
2. Une HISTOIRE LOUFOQUE mémorable (5-8 phrases absurdes)

Passage : {livre} {ref}
Texte : "{texte}"

Réponds UNIQUEMENT en JSON valide :
{{"moyen_mnemotechnique": "...", "histoire_loufoune": "..."}}"""
            }]
        )
        raw = resp.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        d = json.loads(raw.strip())
        return d.get("moyen_mnemotechnique",""), d.get("histoire_loufoune","")
    except Exception as e:
        return None, str(e)

# ─────────────────────────────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────────────────────────────
for k,v in [("page","accueil"),("api_key",""),("seg_idx",None)]:
    if k not in st.session_state: st.session_state[k] = v

init_db()

# ─────────────────────────────────────────────────────────────────
# EN-TÊTE
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-title">✝️ Bible Memory</div>
    <div class="app-sub">La Voie de l'Abondance et de la Puissance</div>
</div>""", unsafe_allow_html=True)

# NAV
n1,n2,n3,n4 = st.columns(4)
with n1:
    if st.button("🏠\nAccueil"): st.session_state.page="accueil"
with n2:
    if st.button("📚\nCours"): st.session_state.page="cours"; st.session_state.seg_idx=None
with n3:
    if st.button("📖\nPassages"): st.session_state.page="passages"
with n4:
    if st.button("🗂️\n66 Livres"): st.session_state.page="livres"

st.markdown("<hr style='border-color:#2A2A4A;margin:.4rem 0 .8rem;'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# ACCUEIL
# ═══════════════════════════════════════════════════════════════
if st.session_state.page == "accueil":
    total, perso = get_stats()
    perso = perso or 0
    s1,s2,s3 = st.columns(3)
    with s1: st.markdown(f'<div class="stat-card"><p class="stat-num">{total}</p><p class="stat-lbl">Passages</p></div>', unsafe_allow_html=True)
    with s2: st.markdown(f'<div class="stat-card"><p class="stat-num">12</p><p class="stat-lbl">Segments</p></div>', unsafe_allow_html=True)
    with s3: st.markdown(f'<div class="stat-card"><p class="stat-num">{perso}</p><p class="stat-lbl">Mes ajouts</p></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-gold" style="margin-top:.8rem;">
        <div style="color:var(--gold);font-weight:800;margin-bottom:.4rem;">🎯 La Voie de l'Abondance et de la Puissance</div>
        <p style="color:#ddd;font-size:.83rem;line-height:1.6;margin:0;">
        Une étude biblique en <strong style="color:var(--gold)">12 segments</strong> pour découvrir
        que Dieu veut que son peuple prospère <em>physiquement, mentalement et spirituellement.</em>
        Jésus Christ est la voie, la vérité et la vie. Sa Parole est notre norme absolue.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">🚀 Accès rapide</div>', unsafe_allow_html=True)
    for i in range(0,12,2):
        ca, cb = st.columns(2)
        for j, col in enumerate([ca, cb]):
            idx = i + j
            if idx < 12:
                seg = COURS_DATA[idx]
                with col:
                    st.markdown(f"""
                    <div class="card card-gold" style="padding:.65rem;">
                        <div style="color:var(--gold);font-size:.68rem;font-weight:800;">SEG {seg['num']}</div>
                        <div style="color:#fff;font-size:.78rem;font-weight:700;line-height:1.3;margin-top:2px;">
                            {seg['titre'][:42]}{'...' if len(seg['titre'])>42 else ''}
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("📖", key=f"home_seg_{idx}"):
                        st.session_state.page = "cours"
                        st.session_state.seg_idx = idx
                        st.rerun()

    st.markdown('<div class="sec-title">🔑 Clé API (optionnel)</div>', unsafe_allow_html=True)
    api_in = st.text_input("Clé Anthropic pour générer des mnémotechniques IA",
        value=st.session_state.api_key, type="password", placeholder="sk-ant-...",
        label_visibility="collapsed")
    if api_in: st.session_state.api_key = api_in; st.success("✅ Clé enregistrée !")
    st.markdown('<div style="color:#555;font-size:.75rem;text-align:center;">Sans clé, toutes les mnémotechniques pré-construites sont accessibles.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# COURS
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page == "cours":
    if st.session_state.seg_idx is not None:
        idx = st.session_state.seg_idx
        if st.button("← Tous les segments"):
            st.session_state.seg_idx = None; st.rerun()

        seg = COURS_DATA[idx]
        st.markdown(f"""
        <div class="card card-gold">
            <div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem;">
                <div class="seg-num">{seg['num']}</div>
                <div style="color:var(--gold);font-weight:800;font-size:.95rem;line-height:1.3;">{seg['titre']}</div>
            </div>
            <p style="color:#ddd;font-size:.82rem;line-height:1.6;margin:0;">{seg['theme']}</p>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title">📖 Passage Clé</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:var(--gold);font-weight:800;font-size:.95rem;margin-bottom:.4rem;">{seg["passage_cle"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="verse-box">{seg["texte_cle"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🧠 Mnémotechnique</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mnemo-box">{seg["mnemo"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🎭 Histoire Loufoque</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="story-box">{seg["histoire"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-title">📌 Références Clés</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">' + " ".join([f'<span class="ref-pill">{r}</span>' for r in seg["refs_cles"]]) + '</div>', unsafe_allow_html=True)

        if seg["refs_sec"]:
            st.markdown('<div class="sec-title">📎 Références Secondaires</div>', unsafe_allow_html=True)
            st.markdown('<div class="card">' + " ".join([f'<span class="ref-pill">{r}</span>' for r in seg["refs_sec"]]) + '</div>', unsafe_allow_html=True)

        st.markdown("---")
        pa, pb = st.columns(2)
        with pa:
            if idx > 0 and st.button(f"← Seg {idx}"):
                st.session_state.seg_idx = idx-1; st.rerun()
        with pb:
            if idx < 11 and st.button(f"Seg {idx+2} →"):
                st.session_state.seg_idx = idx+1; st.rerun()
    else:
        st.markdown('<div class="sec-title">📚 La Voie de l\'Abondance — 12 Segments</div>', unsafe_allow_html=True)
        st.markdown('<div class="card card-green" style="margin-bottom:.8rem;"><p style="color:var(--green);font-size:.8rem;margin:0;">💡 Appuie sur 📖 pour voir le passage clé, la mnémotechnique et l\'histoire loufoque de chaque segment.</p></div>', unsafe_allow_html=True)

        for seg in COURS_DATA:
            cc, cb_ = st.columns([5,1])
            with cc:
                refs_html = " ".join([f'<span class="ref-pill">{r}</span>' for r in seg["refs_cles"][:3]])
                st.markdown(f"""
                <div class="card card-gold">
                    <div style="display:flex;align-items:flex-start;gap:.5rem;">
                        <div class="seg-num">{seg['num']}</div>
                        <div>
                            <div style="color:#fff;font-weight:700;font-size:.85rem;line-height:1.3;">{seg['titre']}</div>
                            <div style="margin-top:3px;">{refs_html}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with cb_:
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                if st.button("📖", key=f"seg_btn_{seg['num']}"):
                    st.session_state.seg_idx = seg['num']-1; st.rerun()

# ═══════════════════════════════════════════════════════════════
# PASSAGES
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page == "passages":
    st.markdown('<div class="sec-title">📖 Passages Bibliques</div>', unsafe_allow_html=True)

    # Filtres
    seg_opts = ["Tous"] + [f"Seg {s['num']} — {s['titre'][:30]}..." for s in COURS_DATA] + ["Mes ajouts seulement"]
    fc, sc_ = st.columns([3,1])
    with fc: search = st.text_input("🔍", placeholder="Livre, texte...", label_visibility="collapsed")
    with sc_: seg_sel = st.selectbox("Segment", seg_opts, label_visibility="collapsed")

    if seg_sel == "Tous": seg_f, perso_f = 0, False
    elif seg_sel == "Mes ajouts seulement": seg_f, perso_f = 0, True
    else: seg_f = int(seg_sel.split(" ")[1]); perso_f = False

    passages = get_passages(search, seg_f, perso_f)
    st.caption(f"{len(passages)} passage(s)")

    if not passages:
        st.markdown('<div class="card" style="text-align:center;padding:1.5rem;"><div style="font-size:2.5rem">📭</div><p style="color:#888;">Aucun passage.</p></div>', unsafe_allow_html=True)

    for p in passages:
        pid,sn,st_,livre,chap,vd,vf,texte,mnemo,hist,date,seed = p
        ref = f"{chap}:{vd}" + (f"-{vf}" if vf and vf!=vd else "")
        badge = "📌 Cours" if seed else "✍️ Perso"
        bc = "var(--gold)" if seed else "var(--green)"

        with st.expander(f"{livre} {ref}  ·  {'Seg '+str(sn) if sn else '—'}  ·  {date[:10]}"):
            st.markdown(f'<div style="margin-bottom:.4rem;"><span style="color:{bc};font-size:.72rem;font-weight:700;">{badge}</span><span style="color:#666;font-size:.72rem;margin-left:.5rem;">{st_[:45] if st_ else ""}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:var(--gold);font-weight:800;margin-bottom:.4rem;">{livre} {ref}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="verse-box">{texte}</div>', unsafe_allow_html=True)
            if mnemo: st.markdown(f'<div class="mnemo-box" style="margin-top:.5rem;"><strong>🧠</strong> {mnemo}</div>', unsafe_allow_html=True)
            if hist: st.markdown(f'<div class="story-box" style="margin-top:.4rem;"><strong>🎭</strong> {hist}</div>', unsafe_allow_html=True)

            ga, gb = st.columns(2)
            with ga:
                if st.button("🤖 Générer IA", key=f"g_{pid}"):
                    if st.session_state.api_key:
                        with st.spinner("🧠..."):
                            m,h = generate_mnemo_ai(st.session_state.api_key, livre, ref, texte)
                        if m: update_mnemo(pid,m,h); st.success("✅ Mis à jour !"); st.rerun()
                        else: st.error(h)
                    else: st.warning("⚠️ Entre ta clé API dans Accueil !")
            with gb:
                if st.button("🗑️ Supprimer", key=f"d_{pid}"):
                    delete_passage(pid); st.rerun()

    # Ajouter un passage
    st.markdown('<div class="sec-title">➕ Ajouter un Passage</div>', unsafe_allow_html=True)
    with st.expander("📝 Nouveau passage"):
        seg_a_opts = [f"Seg {s['num']} — {s['titre'][:35]}" for s in COURS_DATA] + ["Hors cours"]
        seg_a = st.selectbox("Segment", seg_a_opts, key="seg_a")
        if seg_a == "Hors cours": sn_a, st_a = 0, ""
        else: sn_a = int(seg_a.split(" ")[1]); st_a = COURS_DATA[sn_a-1]["titre"]

        lv_a = st.selectbox("Livre", ALL_BOOKS_ORDERED, key="lv_a")
        ca_, cb__, cc_ = st.columns(3)
        with ca_: ch_a = st.number_input("Chap.", 1, 150, 1, key="ch_a")
        with cb__: vd_a = st.number_input("V. deb.", 1, 200, 1, key="vd_a")
        with cc_: vf_a = st.number_input("V. fin", 1, 200, 1, key="vf_a")

        tx_a = st.text_area("Texte", placeholder="Colle le texte ici...", height=90, key="tx_a")
        gen_a = st.checkbox("🤖 Générer avec l'IA", value=bool(st.session_state.api_key), key="gen_a")

        if st.button("💾 Enregistrer", key="save_a"):
            if not tx_a.strip(): st.error("❌ Texte obligatoire !")
            else:
                mn_n, hs_n = "", ""
                ref_a = f"{int(ch_a)}:{int(vd_a)}" + (f"-{int(vf_a)}" if vf_a>vd_a else "")
                if gen_a and st.session_state.api_key:
                    with st.spinner("🧠 Génération..."):
                        mn_n, hs_n = generate_mnemo_ai(st.session_state.api_key, lv_a, ref_a, tx_a)
                    if not mn_n: st.warning(f"IA indisponible: {hs_n}"); mn_n, hs_n = "", ""
                add_passage(sn_a, st_a, lv_a, int(ch_a), int(vd_a), int(vf_a), tx_a.strip(), mn_n, hs_n)
                st.success(f"✅ {lv_a} {ref_a} enregistré !"); st.rerun()

# ═══════════════════════════════════════════════════════════════
# 66 LIVRES
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page == "livres":
    st.markdown('<div class="sec-title">📚 Les 66 Livres de la Bible</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card card-green">
        <p style="color:var(--green);font-weight:700;margin:0 0 .3rem;">🎯 Méthode globale</p>
        <p style="color:#ddd;font-size:.8rem;margin:0;line-height:1.6;">
        <strong>AT (39)</strong> : 5 Penta + 12 Hist + 5 Poé + 5 GdPro + 12 PtPro<br>
        <strong>NT (27)</strong> : 4 Évan + 1 Actes + 13 Paul + 8 Gén + 1 Apoc<br>
        <span style="color:var(--gold);">📌 39 + 27 = 66 → 3×9 = 27 ✓</span>
        </p>
    </div>""", unsafe_allow_html=True)

    with st.expander("🔢 Voir les 66 livres dans l'ordre"):
        for i, bk in enumerate(ALL_BOOKS_ORDERED):
            col = "#E94560" if i>=39 else "var(--gold)"
            st.markdown(f'<div style="display:flex;padding:3px 0;border-bottom:1px solid #1a1a35;"><span style="color:{col};font-weight:800;width:28px;font-size:.78rem;">{i+1}</span><span style="color:#ddd;font-size:.83rem;">{bk}</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="background:linear-gradient(135deg,#1a1a2e,#0d0d1a);border-radius:12px;padding:.7rem;margin:1rem 0 .3rem;border:2px solid var(--gold);"><h3 style="color:var(--gold);margin:0;font-size:1.1rem;">✡️ Ancien Testament — 39 Livres</h3></div>', unsafe_allow_html=True)
    for gn in ["Pentateuque (5)","Livres Historiques (12)","Livres Poétiques (5)","Grands Prophètes (5)","Petits Prophètes (12)"]:
        g = BIBLE_GROUPS[gn]
        with st.expander(f"📂 {gn}"):
            st.markdown(f'<div class="card card-purple"><strong style="color:var(--purple)">🔤 Acronyme</strong><br><span style="color:var(--gold);font-size:.95rem;font-weight:800;letter-spacing:2px;">{g["acronyme"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="mnemo-box"><strong>💡</strong> {g["mnemo"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="story-box" style="margin-top:.4rem;"><strong>🎭</strong> {g["histoire"]}</div>', unsafe_allow_html=True)
            first = g["livres"][0]; start = ALL_BOOKS_ORDERED.index(first)+1 if first in ALL_BOOKS_ORDERED else 1
            for i, bk in enumerate(g["livres"]):
                st.markdown(f'<div style="display:flex;align-items:center;padding:3px 8px;margin:2px 0;background:#1a1a35;border-radius:8px;"><span style="color:var(--gold);font-weight:900;width:28px;font-size:.78rem;">#{start+i}</span><span style="color:#fff;font-size:.85rem;font-weight:600;">{bk}</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="background:linear-gradient(135deg,#1a0a1a,#0d0d1a);border-radius:12px;padding:.7rem;margin:1rem 0 .3rem;border:2px solid var(--accent);"><h3 style="color:var(--accent);margin:0;font-size:1.1rem;">✝️ Nouveau Testament — 27 Livres</h3></div>', unsafe_allow_html=True)
    for gn in ["Les 4 Évangiles","Actes des Apôtres (1)","Lettres de Paul (13)","Lettres Générales (8)","Apocalypse (1)"]:
        g = BIBLE_GROUPS[gn]
        with st.expander(f"📂 {gn}"):
            st.markdown(f'<div class="card card-red"><strong style="color:var(--accent)">🔤 Acronyme</strong><br><span style="color:var(--gold);font-size:.95rem;font-weight:800;letter-spacing:2px;">{g["acronyme"]}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="mnemo-box"><strong>💡</strong> {g["mnemo"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="story-box" style="margin-top:.4rem;"><strong>🎭</strong> {g["histoire"]}</div>', unsafe_allow_html=True)
            first = g["livres"][0]; start = ALL_BOOKS_ORDERED.index(first)+1 if first in ALL_BOOKS_ORDERED else 40
            for i, bk in enumerate(g["livres"]):
                st.markdown(f'<div style="display:flex;align-items:center;padding:3px 8px;margin:2px 0;background:#1a0a2a;border-radius:8px;"><span style="color:var(--accent);font-weight:900;width:28px;font-size:.78rem;">#{start+i}</span><span style="color:#fff;font-size:.85rem;font-weight:600;">{bk}</span></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-gold" style="margin-top:.8rem;text-align:center;padding:1rem;">
        <div style="font-size:1.6rem">🏆</div>
        <p style="color:var(--gold);font-weight:800;margin:.2rem 0;">Grand Défi</p>
        <p style="color:#ddd;font-size:.8rem;margin:0;line-height:1.7;">
        <strong style="color:var(--green)">Étape 1</strong> : 5 groupes d'AT<br>
        <strong style="color:var(--green)">Étape 2</strong> : 5 groupes du NT<br>
        <strong style="color:var(--green)">Étape 3</strong> : Chaque acronyme<br>
        <strong style="color:var(--gold)">🎯 66 livres en moins de 2 minutes !</strong>
        </p>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1a1a35;margin:.8rem 0 .3rem;'><div style='text-align:center;color:#333;font-size:.7rem;'>✝️ Bible Memory · La Voie de l'Abondance et de la Puissance</div>", unsafe_allow_html=True)
