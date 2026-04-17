import streamlit as st
import sqlite3
import json
import random
from datetime import datetime, timedelta

try:
    import anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cours Fondamental ✝️",
    page_icon="✝️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════
# CSS MOBILE-FIRST
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
:root{
    --gold:#C9A84C;--dark:#0A0A18;--mid:#12122A;
    --card:#181830;--accent:#E94560;--text:#F0E6D3;
    --green:#27AE60;--purple:#8E44AD;--blue:#2471A3;
    --border:#252545;--orange:#E67E22;--teal:#1ABC9C;
}
.stApp{background:var(--dark);color:var(--text);font-family:'Segoe UI',sans-serif;}
.app-header{text-align:center;padding:1.2rem 0 .5rem;
    background:linear-gradient(180deg,#181830 0%,transparent 100%);
    border-radius:0 0 20px 20px;margin-bottom:.6rem;}
.app-title{font-size:1.7rem;font-weight:900;color:var(--gold);
    text-shadow:0 0 30px rgba(201,168,76,.6);margin:0;}
.app-sub{color:#777;font-size:.73rem;margin:.3rem 0 0;letter-spacing:1px;}
.sec-title{font-size:1rem;font-weight:800;color:var(--gold);
    border-bottom:2px solid var(--gold);padding-bottom:.25rem;margin:1rem 0 .6rem;}
.sub-title{font-size:.88rem;font-weight:700;color:var(--orange);
    margin:.8rem 0 .3rem;text-transform:uppercase;letter-spacing:.5px;}
.card{background:var(--card);border-radius:14px;padding:.9rem;
    margin:.5rem 0;border:1px solid var(--border);}
.card-gold{border-left:4px solid var(--gold);}
.card-red{border-left:4px solid var(--accent);}
.card-green{border-left:4px solid var(--green);}
.card-purple{border-left:4px solid var(--purple);}
.card-blue{border-left:4px solid var(--blue);}
.card-orange{border-left:4px solid var(--orange);}
.card-teal{border-left:4px solid var(--teal);}
.verse-box{background:rgba(201,168,76,.06);border-radius:10px;
    padding:.8rem;font-size:.88rem;line-height:1.8;color:var(--text);
    border-left:3px solid var(--gold);margin:.4rem 0;}
.ref-tag{color:var(--gold);font-weight:800;font-size:.82rem;
    display:block;margin-bottom:.3rem;}
.story-box{background:rgba(142,68,173,.1);border-radius:10px;
    padding:.8rem;font-style:italic;font-size:.84rem;
    line-height:1.7;color:#ddd;border:1px solid rgba(142,68,173,.3);}
.mnemo-box{background:rgba(39,174,96,.1);border-radius:10px;
    padding:.8rem;font-size:.86rem;color:#2ECC71;
    border:1px solid rgba(39,174,96,.3);line-height:1.6;}
.ref-pill{display:inline-block;background:rgba(36,113,163,.2);color:#5DADE2;
    border:1px solid rgba(36,113,163,.4);border-radius:20px;
    font-size:.7rem;font-weight:700;padding:2px 8px;margin:2px;}
.seg-header{background:linear-gradient(135deg,#1a1a35,#0a0a18);
    border-radius:14px;padding:1rem;margin:.5rem 0;
    border:2px solid var(--gold);}
.seg-num-badge{background:var(--gold);color:#0A0A18;font-weight:900;
    border-radius:50%;width:36px;height:36px;display:inline-flex;
    align-items:center;justify-content:center;font-size:1rem;
    margin-right:.5rem;flex-shrink:0;}
.stat-card{background:var(--card);border-radius:12px;padding:.8rem;
    text-align:center;border:1px solid var(--border);}
.stat-num{font-size:1.8rem;font-weight:900;color:var(--gold);margin:0;}
.stat-lbl{font-size:.7rem;color:#888;margin:0;}
.stButton>button{background:linear-gradient(135deg,var(--gold),#8B6914);
    color:#0A0A18;font-weight:800;border:none;border-radius:10px;
    padding:.55rem;transition:all .2s;width:100%;}
.stButton>button:hover{opacity:.85;transform:translateY(-1px);}
.stTextInput input,.stTextArea textarea,.stSelectbox select{
    background:var(--mid)!important;color:var(--text)!important;
    border:1px solid var(--border)!important;border-radius:8px!important;}
div[data-testid="stExpander"]{
    background:var(--card);border:1px solid var(--border);border-radius:12px;}
.key-truth{background:rgba(201,168,76,.08);border-radius:10px;
    padding:.7rem;border:1px solid rgba(201,168,76,.3);
    font-size:.85rem;color:#F0E6D3;line-height:1.6;margin:.4rem 0;}
.quiz-card{background:linear-gradient(135deg,#181830,#0e0e25);
    border-radius:16px;padding:1.2rem;border:2px solid var(--gold);margin:.5rem 0;}
.quiz-question{font-size:.95rem;font-weight:700;color:#fff;line-height:1.6;margin-bottom:1rem;}
.quiz-correct{background:rgba(39,174,96,.2);border:2px solid var(--green);
    border-radius:10px;padding:.8rem;color:var(--green);font-weight:700;margin:.4rem 0;
    font-size:.88rem;line-height:1.5;}
.quiz-wrong{background:rgba(233,69,96,.15);border:2px solid var(--accent);
    border-radius:10px;padding:.8rem;color:var(--accent);font-weight:700;margin:.4rem 0;
    font-size:.88rem;line-height:1.5;}
.search-result{background:var(--card);border-radius:12px;padding:.8rem;
    margin:.4rem 0;border-left:4px solid var(--teal);}
.search-seg-tag{background:rgba(26,188,156,.15);color:var(--teal);
    border-radius:8px;padding:2px 8px;font-size:.7rem;font-weight:700;
    display:inline-block;margin-bottom:.3rem;}
.prog-bar-outer{background:#252545;border-radius:10px;height:8px;
    margin:.2rem 0;overflow:hidden;}
.prog-bar-inner{height:8px;border-radius:10px;transition:width .5s ease;}
.due-badge{background:var(--accent);color:#fff;border-radius:20px;
    padding:2px 8px;font-size:.7rem;font-weight:800;display:inline-block;}
.ok-badge{background:var(--green);color:#fff;border-radius:20px;
    padding:2px 8px;font-size:.7rem;font-weight:800;display:inline-block;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# DONNÉES — 14 SEGMENTS
# ══════════════════════════════════════════════════════════
SEGMENTS = [
    {
        "num": 1, "titre": "La Voie de l'Abondance et de la Puissance",
        "couleur": "#C9A84C",
        "intro": "La **voie** fait allusion à un chemin à suivre. La destination c'est **DIEU**. "
            "L'abondance, c'est ce que Dieu désire pour son peuple — prospérer physiquement, "
            "mentalement et spirituellement. La **puissance**, c'est la force et la capacité "
            "de réaliser les choses et de manifester la puissance de Dieu.",
        "sections": [
            {
                "titre": "Jésus Christ : La Voie, la Vérité et la Vie",
                "contenu": "Jésus n'est pas seulement un guide — Il est le chemin lui-même. "
                    "Il ne pointe pas vers la vérité, Il EST la vérité. Il ne donne pas la vie, Il EST la vie.",
                "versets": [
                    {"ref": "Jean 14:6", "texte": "Jésus lui dit : Je suis le chemin, la vérité, et la vie. Nul ne vient au Père que par moi."},
                    {"ref": "Jean 4:34", "texte": "Jésus leur dit : Ma nourriture est de faire la volonté de celui qui m'a envoyé, et d'accomplir son oeuvre."},
                    {"ref": "Jean 6:38", "texte": "Car je suis descendu du ciel pour faire, non ma volonté, mais la volonté de celui qui m'a envoyé."},
                    {"ref": "Jean 10:30", "texte": "Moi et le Père nous sommes un."},
                ],
            },
            {
                "titre": "Choisir une Norme de la Vérité",
                "contenu": "La vérité c'est la vérité, que l'on soit d'accord avec elle ou non — elle demeure. "
                    "Laisser la Parole s'interpréter elle-même pour voir le vrai dessein de Dieu.",
                "versets": [
                    {"ref": "Jean 17:17", "texte": "Sanctifie-les par ta vérité : ta parole est la vérité."},
                    {"ref": "Deutéronome 30:19-20", "texte": "J'en prends aujourd'hui à témoin contre vous le ciel et la terre : j'ai mis devant toi la vie et la mort, la bénédiction et la malédiction. Choisis la vie, afin que tu vives, toi et ta postérité."},
                    {"ref": "Jean 8:31-32", "texte": "Si vous demeurez dans ma parole, vous êtes vraiment mes disciples ; vous connaîtrez la vérité, et la vérité vous affranchira."},
                ],
            },
            {
                "titre": "Notre Choix selon le Libre Arbitre",
                "contenu": "Nous aimons Dieu parce que Dieu nous a aimés le premier. "
                    "C'est notre choix, selon le libre arbitre, d'obéir à Sa Parole et de jouir de l'abondance qu'Il a pour nous.",
                "versets": [
                    {"ref": "Aggée 1:5", "texte": "Maintenant, ainsi parle l'Éternel des armées : Portez votre attention sur vos voies !"},
                    {"ref": "Matthieu 22:29", "texte": "Jésus leur répondit : Vous êtes dans l'erreur, parce que vous ne comprenez ni les Écritures ni la puissance de Dieu."},
                ],
            },
        ],
        "mnemo": "🛣️ J-V-T-V = JÉSUS : Voie – Vérité – (et la) Vie\n"
            "Retiens : Jean 14:6 = Chapitre 14, verset 6\n"
            "→ 1+4 = 5 lettres dans 'JESUS' ✓\n"
            "📌 Jésus = GPS parfait : il ne recalcule jamais, il EST déjà arrivé !",
        "histoire": "Un automobiliste perdu dans le désert appelle un GPS. La voix répond : "
            "'Je suis JÉSUS — le Chemin, la Vérité et la Vie.' L'homme dit : 'Recalcul en cours ?' "
            "Jésus : 'Non. Je ne recalcule jamais. Je suis déjà arrivé là où tu vas.' "
            "L'homme suit. Il arrive dans un jardin d'abondance totale. Fin du trajet. Début de la vie.",
        "verite_cle": "Dieu veut que son peuple prospère physiquement, mentalement et spirituellement. Ce n'est pas une option — c'est Son désir dès la création !",
    },
    {
        "num": 2, "titre": "La Parole de Dieu est la Norme",
        "couleur": "#E94560",
        "intro": "La Parole de Dieu est notre norme absolue de croyance et d'action. "
            "Personne ne va au-delà de ce qu'on lui a enseigné. "
            "Il est donc essentiel de connaître et d'étudier la Parole.",
        "sections": [
            {
                "titre": "Les Objectifs du Voleur vs Jésus",
                "contenu": "Le voleur entre furtivement. Ses 3 objectifs : **dérober**, **égorger**, **détruire**. "
                    "Jésus au contraire est venu pour donner la vie — et la vie en abondance.",
                "versets": [
                    {"ref": "Jean 10:10", "texte": "Le voleur ne vient que pour dérober, égorger et détruire ; moi, je suis venu afin que les brebis aient la vie, et qu'elles soient dans l'abondance."},
                    {"ref": "1 Jean 3:8", "texte": "Celui qui pèche est du diable, car le diable pèche dès le commencement. Le Fils de Dieu a paru afin de détruire les oeuvres du diable."},
                    {"ref": "Actes 10:38", "texte": "Comment Dieu a oint de l'Esprit Saint et de force Jésus de Nazareth, qui allait de lieu en lieu faisant du bien et guérissant tous ceux qui étaient tyrannisés par le diable, car Dieu était avec lui."},
                ],
            },
            {
                "titre": "L'Autorité et l'Intégrité de la Parole Révélée",
                "contenu": "Dieu ne peut pas mentir. Sa Parole est immuable. Ce qu'Il a promis, Il l'accomplit.",
                "versets": [
                    {"ref": "2 Pierre 1:20", "texte": "Sachez d'abord vous-mêmes qu'aucune prophétie de l'Écriture ne peut être un objet d'interprétation particulière."},
                    {"ref": "Hébreux 6:18", "texte": "Afin que, par deux choses immuables, dans lesquelles il est impossible que Dieu mente, nous trouvions un puissant encouragement."},
                    {"ref": "Nombres 23:19", "texte": "Dieu n'est pas un homme pour mentir, ni un fils d'homme pour se repentir. Ce qu'il a dit, ne le fera-t-il pas ? Ce qu'il a déclaré, ne l'exécutera-t-il pas ?"},
                    {"ref": "Malachie 3:6", "texte": "Car je suis l'Éternel, je ne change pas."},
                ],
            },
            {
                "titre": "Nous Pouvons Avoir Confiance en Sa Parole",
                "contenu": "La Parole de Dieu est vivante et efficace. Elle pénètre jusqu'à la division de l'âme et de l'esprit.",
                "versets": [
                    {"ref": "Hébreux 4:12", "texte": "Car la parole de Dieu est vivante et efficace, plus tranchante qu'une épée quelconque à deux tranchants, pénétrante jusqu'à partager âme et esprit, jointures et moelles ; elle juge les sentiments et les pensées du coeur."},
                    {"ref": "Romains 16:25-26", "texte": "Or, à celui qui a le pouvoir de vous affermir selon mon évangile et la prédication de Jésus Christ — à lui soit la gloire aux siècles des siècles."},
                ],
            },
        ],
        "mnemo": "⚖️ VOLEUR 3D vs JÉSUS 3V\n"
            "❌ Voleur : Dérober – Détruire – Décimer\n"
            "✅ Jésus : Vie – Victoire – Volume d'abondance\n"
            "📌 Jean 10:10 → '10 sur 10' = Note parfaite de la Parole !",
        "histoire": "Un cambrioleur arrive avec un grand sac marqué 'DESTRUCTION'. "
            "Il vole la joie, casse l'espoir, détruit la paix. Cinq minutes plus tard, "
            "Jésus arrive avec un camion-citerne rempli d'abondance. Il pose sur la porte : "
            "'VERROU INCASSABLE — Parole de Dieu.' Le cambrioleur revient. La porte ne cède pas. Fin.",
        "verite_cle": "Personne ne va au-delà de ce qu'on lui a enseigné. "
            "La qualité de notre vie spirituelle dépend de la qualité de notre connaissance de la Parole.",
    },
    {
        "num": 3, "titre": "La Sûreté de Nos Jours",
        "couleur": "#27AE60",
        "intro": "Nous pouvons apprendre à retenir la Parole dans notre intelligence, "
            "à avoir confiance en elle, à croire cette Parole, à voir son intégrité et "
            "l'authenticité de la vérité. La sincérité n'est **pas** une garantie pour la vérité.",
        "sections": [
            {
                "titre": "La Sincérité ne Garantit pas la Vérité",
                "contenu": "On peut être sincèrement dans l'erreur. "
                    "La sincérité est une qualité de coeur, mais elle ne remplace pas la connaissance de la vérité.",
                "versets": [
                    {"ref": "2 Timothée 3:16", "texte": "Toute Écriture est inspirée de Dieu, et utile pour enseigner, pour convaincre, pour corriger, pour instruire dans la justice."},
                    {"ref": "Matthieu 4:4", "texte": "Jésus répondit : Il est écrit : L'homme ne vivra pas de pain seulement, mais de toute parole qui sort de la bouche de Dieu."},
                    {"ref": "Matthieu 5:18", "texte": "Car, je vous le dis en vérité, tant que le ciel et la terre subsisteront, il ne disparaîtra pas de la loi un seul iota ou un seul trait de lettre."},
                ],
            },
            {
                "titre": "Ce que Dieu dit à propos de Sa Parole",
                "contenu": "La Parole de Dieu est pure, préservée à jamais. "
                    "Elle est une lampe à nos pieds et une lumière sur notre sentier.",
                "versets": [
                    {"ref": "Psaumes 119:105", "texte": "Ta parole est une lampe à mes pieds, et une lumière sur mon sentier."},
                    {"ref": "Psaumes 119:160", "texte": "La somme de ta parole est la vérité, et toutes tes lois éternelles sont justes."},
                    {"ref": "Psaumes 12:7", "texte": "Toi, Éternel ! tu les garderas, tu nous préserveras de cette race, à jamais."},
                    {"ref": "Ésaïe 33:5-6", "texte": "L'Éternel est élevé, car il habite dans les hauteurs ; il remplit Sion de droiture et de justice. Il sera la sécurité de tes jours, une riche source de salut, de sagesse et de connaissance."},
                ],
            },
        ],
        "mnemo": "🔦 LAMPE pour les PIEDS = présent immédiat\n"
            "💡 LUMIÈRE sur le SENTIER = direction future\n"
            "Ps 119:105 → 119 = 1-1-9 → 'Une seule Parole, 9 fois confirmée !'\n"
            "📌 Parole = GPS + lampe torche + boussole + assurance vie !",
        "histoire": "Un explorateur part dans une grotte sombre avec deux gadgets : "
            "une lampe-frontale (Parole pour les pieds) et un phare géant (Parole pour le sentier). "
            "D'autres explorent sincèrement... mais dans le noir. "
            "Notre explorateur sort bronzé et chargé de trésors. "
            "Conclusion : la sincérité n'éclaire pas. La Parole, si.",
        "verite_cle": "La Parole de Dieu est la sûreté de nos jours. "
            "Elle ne change pas selon nos humeurs ou les circonstances — elle demeure éternellement.",
    },
    {
        "num": 4, "titre": "Le Sujet de Toute la Parole de Dieu",
        "couleur": "#8E44AD",
        "intro": "Jésus Christ est le passe-partout à l'interprétation de toute la Parole. "
            "Il a lui-même divisé la Parole en trois catégories : "
            "**la Loi**, **les Prophètes** et **les Psaumes**. Toute l'Écriture parle de Lui.",
        "sections": [
            {
                "titre": "Jésus Christ : Clé de Toute la Parole",
                "contenu": "De la Genèse à l'Apocalypse, tout parle de Jésus Christ. "
                    "C'est Lui le fil conducteur de toute l'Écriture. Sans Lui, la Bible reste un livre fermé.",
                "versets": [
                    {"ref": "Luc 24:44-45", "texte": "Puis il leur dit : C'est là ce que je vous disais lorsque j'étais encore avec vous, qu'il fallait que s'accomplît tout ce qui est écrit de moi dans la loi de Moïse, dans les prophètes, et dans les psaumes. Alors il leur ouvrit l'intelligence, pour qu'ils comprissent les Écritures."},
                    {"ref": "Jean 1:45", "texte": "Philippe rencontra Nathanaël, et lui dit : Nous avons trouvé celui dont Moïse a parlé dans la loi et dont les prophètes ont parlé, Jésus de Nazareth, fils de Joseph."},
                    {"ref": "Colossiens 1:18-19", "texte": "Il est la tête du corps de l'Église ; il est le commencement, le premier-né d'entre les morts, afin d'être en tout le premier. Car Dieu a voulu faire habiter toute la plénitude en lui."},
                ],
            },
            {
                "titre": "Se Présenter comme un Ouvrier Approuvé",
                "contenu": "La plus grande des oeuvres de Dieu est Sa Parole. "
                    "Dieu a magnifié Sa Parole au-dessus de Son nom. "
                    "C'est à nous de la lire, l'écouter, l'étudier et d'y mettre des efforts diligents.",
                "versets": [
                    {"ref": "2 Timothée 2:15", "texte": "Efforce-toi de te présenter devant Dieu comme un homme éprouvé, un ouvrier qui n'a point à rougir, qui dispense droitement la parole de la vérité."},
                    {"ref": "Psaumes 119:89", "texte": "Éternel ! ta parole subsiste à jamais dans les cieux."},
                    {"ref": "Psaumes 138:2", "texte": "Je me prosterne vers ton saint temple, et je célèbre ton nom pour ta bonté et ta fidélité, parce que tu as fait passer ta parole avant tout ce qui te fait glorifier."},
                    {"ref": "Actes 17:11", "texte": "Ces Juifs avaient des sentiments plus nobles que ceux de Thessalonique ; ils reçurent la parole avec beaucoup d'empressement, et ils examinaient chaque jour les Écritures, pour voir si ce qu'on leur disait était exact."},
                ],
            },
            {
                "titre": "La Parole de Dieu est la Volonté de Dieu",
                "contenu": "Lire la Parole est la plus grande clé pour être un ouvrier de Dieu.",
                "versets": [
                    {"ref": "Ésaïe 55:8-11", "texte": "Car mes pensées ne sont pas vos pensées, et vos voies ne sont pas mes voies, dit l'Éternel... ainsi en est-il de ma parole : elle ne retourne point à moi sans effet, sans avoir exécuté ma volonté."},
                    {"ref": "Néhémie 8:8", "texte": "Ils lurent dans le livre de la loi de Dieu d'une manière distincte, avec explication, et l'on faisait comprendre ce qu'on lisait."},
                ],
            },
        ],
        "mnemo": "🔑 JÉSUS = CLÉ PASSE-PARTOUT\n"
            "Loi + Prophètes + Psaumes → tout parle de LUI\n"
            "2Tim 2:15 = '2 choses × 15 méthodes = ouvrier parfait'\n"
            "📌 Ouvrier = Effort + Droiture + Parole bien divisée",
        "histoire": "Un serrurier reçoit 1500 clés pour ouvrir la Bible. "
            "Il essaie clé par clé pendant 20 ans. "
            "Puis quelqu'un lui tend une clé dorée : 'Jésus-Christ'. "
            "Elle ouvre TOUT en une seconde. La Loi, les Prophètes, les Psaumes — tout s'illumine. "
            "Le serrurier jette les 1499 autres et devient le meilleur ouvrier du quartier.",
        "verite_cle": "Dieu a magnifié Sa Parole au-dessus de Son propre Nom (Ps 138:2). "
            "Rien n'est plus important que de connaître et de diviser droitement Sa Parole.",
    },
    {
        "num": 5, "titre": "Les Clés à l'Interprétation de la Parole",
        "couleur": "#2471A3",
        "intro": "Toute Écriture s'interprète elle-même : dans le verset lui-même, "
            "ou dans le contexte utilisé auparavant. "
            "Il existe des vérités bibliques fondamentales auxquelles nous devons adhérer.",
        "sections": [
            {
                "titre": "3 Vérités Fondamentales d'Interprétation",
                "contenu": "**1.** Il faut savoir la **période de temps** à laquelle une section est adressée.\n"
                    "**2.** Le **verset difficile** doit être compris à la lumière des versets clairs.\n"
                    "**3.** L'interprétation tient toujours compte de **à qui** c'est adressé.",
                "versets": [
                    {"ref": "2 Pierre 1:20", "texte": "Sachez d'abord vous-mêmes qu'aucune prophétie de l'Écriture ne peut être un objet d'interprétation particulière."},
                    {"ref": "1 Timothée 3:16", "texte": "Toute Écriture est inspirée de Dieu, et utile pour enseigner, pour convaincre, pour corriger, pour instruire dans la justice."},
                    {"ref": "1 Corinthiens 10:31-32", "texte": "Soit donc que vous mangiez, soit que vous buviez, soit que vous fassiez quelque autre chose, faites tout pour la gloire de Dieu."},
                ],
            },
            {
                "titre": "Toute la Parole est Utile — mais pas tout nous est directement adressé",
                "contenu": "Toute la Parole est utile pour enseigner, convaincre, corriger et instruire. "
                    "Cependant, toute la Parole ne nous est pas directement adressée aujourd'hui "
                    "dans cette administration, en tant que croyants nés de nouveau.",
                "versets": [
                    {"ref": "Romains 15:4", "texte": "Car tout ce qui a été écrit d'avance a été écrit pour notre instruction, afin que, par la patience, et par la consolation que donnent les Écritures, nous possédions l'espérance."},
                    {"ref": "Jacques 5:10", "texte": "Frères, prenez pour modèles de souffrance et de patience les prophètes qui ont parlé au nom du Seigneur."},
                ],
            },
        ],
        "mnemo": "📖 3C d'interprétation :\n"
            "C1 = CONTEXTE (la Bible s'explique par elle-même)\n"
            "C2 = CLARTÉ (le flou cède au clair)\n"
            "C3 = CIBLE (à qui ? quelle époque ?)\n"
            "📌 Sans les 3C, tu risques d'interpréter à côté !",
        "histoire": "Un détective reçoit un message biblique crypté. "
            "Son assistant propose des experts extérieurs. Le détective refuse : 'La Bible se déchiffre elle-même.' "
            "Il compare verset à verset, période à période, destinataire à destinataire. "
            "Le message devient lumineux. La Bible est son propre dictionnaire.",
        "verite_cle": "2 Pierre 1:20 est la règle d'or : aucune prophétie de l'Écriture "
            "ne peut être une affaire d'interprétation privée. La Bible s'explique elle-même.",
    },
    {
        "num": 6, "titre": "Au Commencement",
        "couleur": "#E67E22",
        "intro": "La Parole de Dieu n'a jamais été écrite pour l'incrédule. "
            "Elle est écrite pour ceux qui veulent aimer Dieu, connaître la vérité, "
            "et qui sont prêts à être humbles et disciplinés selon la vérité. "
            "Au commencement, Jésus Christ était dans la présence de Dieu.",
        "sections": [
            {
                "titre": "Dieu : Initiateur du Salut — Christ : Agent du Salut",
                "contenu": "Dieu est l'Auteur et l'Initiateur du salut. "
                    "Jésus Christ en est le Moyen et l'Agent. "
                    "Au commencement, la Parole était déjà là — elle était Dieu.",
                "versets": [
                    {"ref": "Genèse 1:1", "texte": "Au commencement, Dieu créa les cieux et la terre."},
                    {"ref": "Jean 1:1-4", "texte": "Au commencement était la Parole, et la Parole était avec Dieu, et la Parole était Dieu. Elle était au commencement avec Dieu. Toutes choses ont été faites par elle, et rien de ce qui a été fait n'a été fait sans elle. En elle était la vie, et la vie était la lumière des hommes."},
                    {"ref": "Hébreux 11:3", "texte": "C'est par la foi que nous reconnaissons que le monde a été formé par la parole de Dieu, en sorte que ce qu'on voit n'a pas été fait de choses visibles."},
                ],
            },
            {
                "titre": "La Terre Devint Informe et Vide",
                "contenu": "La terre est devenue informe et vide à cause de l'adversaire. "
                    "Ce n'était pas son état original. Dieu l'a créée bonne — c'est Satan qui l'a rendue chaotique.",
                "versets": [
                    {"ref": "Genèse 1:2", "texte": "La terre était informe et vide : il y avait des ténèbres à la surface de l'abîme, et l'esprit de Dieu se mouvait au-dessus des eaux."},
                    {"ref": "Ézéchiel 28:12-15", "texte": "Tu étais le sceau de la perfection, plein de sagesse, parfait en beauté... Tu as été intègre dans tes voies, depuis le jour où tu fus créé jusqu'à celui où l'iniquité a été trouvée en toi."},
                    {"ref": "Jérémie 4:23", "texte": "Je regardai la terre, et voici, elle était informe et vide ; les cieux, et ils n'avaient point de lumière."},
                ],
            },
        ],
        "mnemo": "🌌 AU COMMENCEMENT = 3 réalités :\n"
            "1. PAROLE → était déjà là (Jean 1:1)\n"
            "2. CRÉATION → Dieu parle, tout existe\n"
            "3. CHAOS → l'adversaire sabote la terre\n"
            "📌 Avant le Big Bang : le BIG WORD !",
        "histoire": "Avant l'Univers, Jésus et Dieu prenaient le café dans l'éternité. "
            "Dieu dit : 'Et si on créait quelque chose ?' BOUM — galaxies, étoiles, planètes ! "
            "Mais Satan sabote la Terre et la laisse informe et vide. "
            "Dieu ne panique pas. Il reprend son projet et le reconstruit, encore meilleur. "
            "Morale : Dieu n'abandonne jamais ses projets.",
        "verite_cle": "Jean 1:1 révèle que Jésus-Christ (la Parole) existait avant toute création. "
            "Il n'est pas une créature — Il est le Créateur lui-même.",
    },
    {
        "num": 7, "titre": "La Surface de l'Abîme",
        "couleur": "#1ABC9C",
        "intro": "Qu'est-ce que la surface de l'abîme et l'étendue ? "
            "Il existe trois cieux et trois terres dans la Parole de Dieu. "
            "La terre a changé au fil du temps selon le plan de Dieu.",
        "sections": [
            {
                "titre": "Les Trois Cieux et les Trois Terres",
                "contenu": "**Terre 1** : Originelle (avant la chute de Satan — parfaite).\n"
                    "**Terre 2** : Actuelle (depuis la re-création de Genèse 1 — en cours).\n"
                    "**Terre 3** : Nouvelle (Apocalypse 21 — à venir — parfaite pour l'éternité).",
                "versets": [
                    {"ref": "Genèse 1:1", "texte": "Au commencement, Dieu créa les cieux et la terre."},
                    {"ref": "Apocalypse 21:1", "texte": "Puis je vis un nouveau ciel et une nouvelle terre ; car le premier ciel et la première terre avaient disparu, et la mer n'était plus."},
                    {"ref": "2 Pierre 3:5-6", "texte": "Ils oublient volontairement que des cieux existaient autrefois et qu'il y avait une terre sortie de l'eau et subsistant au milieu de l'eau, par la parole de Dieu, et que, par ces mêmes moyens, le monde d'alors périt submergé par l'eau."},
                    {"ref": "1 Jean 1:5", "texte": "La nouvelle que nous avons apprise de lui et que nous vous annonçons, c'est que Dieu est lumière, et qu'il n'y a point en lui de ténèbres."},
                ],
            },
            {
                "titre": "Dieu Prépare la Terre — La Terre a Changé",
                "contenu": "La seule masse de terre de Genèse 1:10 s'est divisée en plusieurs continents. "
                    "Au temps de **Péleg**, la terre s'est divisée en continents.",
                "versets": [
                    {"ref": "Genèse 1:9-10", "texte": "Dieu dit : Que les eaux qui sont au-dessous du ciel se rassemblent en un seul lieu, et que le sec paraisse. Et cela fut ainsi."},
                    {"ref": "Genèse 10:25", "texte": "À Héber naquirent deux fils ; l'un s'appelait Péleg, parce que de son temps la terre fut partagée."},
                ],
            },
        ],
        "mnemo": "🌍 3T = 3 TERRES :\n"
            "T1 = Terre parfaite originelle\n"
            "T2 = Terre actuelle (Genèse 1 re-création)\n"
            "T3 = Terre nouvelle (Apocalypse 21)\n"
            "📌 PÉLEG = 'Division' → les continents sont nés de son vivant !",
        "histoire": "Imaginez un puzzle de 7 milliards de pièces toutes collées (Pangée biblique). "
            "Satan renverse tout. Dieu récupère les pièces et les recolle. "
            "Noé prend un bateau car la masse est encore unique. "
            "À Babel, les gens se dispersent. Au temps de Péleg (son nom = division), les continents apparaissent. "
            "Afrique, Europe, Amérique — tous issus du même puzzle de Genèse 1.",
        "verite_cle": "Le nom de Péleg signifie 'division' (Genèse 10:25). "
            "La Parole confirme que les continents se sont séparés à une époque précise de l'histoire biblique.",
    },
    {
        "num": 8, "titre": "L'Idiome de Permission",
        "couleur": "#E74C3C",
        "intro": "Un idiome est un usage de mots particulier à une langue ou une culture. "
            "En tant qu'idiome, les mots ne doivent pas être pris dans leur sens littéral. "
            "Reconnaître l'idiome hébreu de permission nous permet de ne **jamais** attribuer le mal à Dieu.",
        "sections": [
            {
                "titre": "L'Idiome Hébreu de Permission",
                "contenu": "En hébreu, 'Dieu a fait X' peut souvent signifier 'Dieu a PERMIS que X arrive'. "
                    "Cette distinction est cruciale pour comprendre le caractère de Dieu "
                    "et ne pas Lui attribuer le mal.",
                "versets": [
                    {"ref": "Exode 10:20", "texte": "Mais l'Éternel endurcit le coeur de Pharaon, et Pharaon ne laissa point aller les enfants d'Israël."},
                    {"ref": "Genèse 6:8-13", "texte": "Mais Noé trouva grâce aux yeux de l'Éternel... La terre était corrompue devant Dieu, la terre était pleine de violence. Dieu regarda la terre, et voici, elle était corrompue ; car toute chair avait corrompu sa voie sur la terre."},
                ],
            },
            {
                "titre": "La Raison d'Être de l'Homme",
                "contenu": "La raison d'être de l'Univers est la Terre. "
                    "La raison d'être de la Terre est l'Homme. "
                    "La raison d'être de l'Homme est d'**aimer Dieu**, de l'adorer et de communier avec Lui.",
                "versets": [
                    {"ref": "Matthieu 22:36-37", "texte": "Maître, quel est le grand commandement de la loi ? Jésus lui répondit : Tu aimeras le Seigneur, ton Dieu, de tout ton coeur, de toute ton âme, et de toute ta pensée."},
                    {"ref": "Genèse 1:24-25", "texte": "Dieu dit : Que la terre produise des animaux vivants selon leur espèce... Et Dieu vit que cela était bon."},
                ],
            },
        ],
        "mnemo": "🎭 IDIOME HÉBREU = PERMISSION\n"
            "'Dieu a fait X' → souvent 'Dieu a PERMIS X'\n"
            "Pharaon = il a durci son propre coeur, Dieu l'a permis\n"
            "📌 RÈGLE D'OR : Ne jamais attribuer le mal à Dieu !",
        "histoire": "Un journaliste titre : 'Dieu a durci le coeur de Pharaon !' "
            "Un expert hébreu corrige : 'En hébreu idiomatique, Dieu a permis que Pharaon "
            "fasse ses propres choix stupides.' "
            "Le journaliste résume : Univers = pour la Terre. Terre = pour l'Homme. "
            "Homme = pour aimer Dieu. Pharaon avait court-circuité tout ça.",
        "verite_cle": "Dieu ne fait jamais le mal. Jacques 1:13 confirme : "
            "'Dieu ne tente personne.' L'idiome de permission explique "
            "les passages qui semblent attribuer le mal à Dieu.",
    },
    {
        "num": 9, "titre": "Les Fondements de Toute Vie",
        "couleur": "#27AE60",
        "intro": "Le but et la signification de la création sont établis en Genèse : "
            "les fondements de toute vie. "
            "L'homme est un être tripartite : Corps, Âme et Esprit. "
            "Comprendre cette trilogie est essentiel pour comprendre notre relation avec Dieu.",
        "sections": [
            {
                "titre": "L'Homme : Corps, Âme et Esprit",
                "contenu": "🫀 **Corps** : Formé de la poussière du sol (Genèse 2:7)\n"
                    "💛 **Âme** : Faite — siège des émotions, de la volonté, de la personnalité\n"
                    "✨ **Esprit** : Créé — pour communier directement avec Dieu",
                "versets": [
                    {"ref": "Genèse 2:7", "texte": "L'Éternel Dieu forma l'homme de la poussière du sol, il souffla dans ses narines un souffle de vie et l'homme devint un être vivant."},
                    {"ref": "Lévitique 17:11", "texte": "Car la vie de la chair est dans le sang. Je vous l'ai donné sur l'autel pour faire l'expiation pour vos âmes."},
                    {"ref": "Jean 4:24", "texte": "Dieu est Esprit, et il faut que ceux qui l'adorent l'adorent en esprit et en vérité."},
                ],
            },
            {
                "titre": "L'Homme Créé à l'Image de Dieu",
                "contenu": "L'homme a été créé à l'image et selon la ressemblance de Dieu. "
                    "Il était destiné à dominer sur toute la création. "
                    "C'est la plus haute dignité que Dieu puisse accorder.",
                "versets": [
                    {"ref": "Genèse 1:26", "texte": "Dieu dit : Faisons l'homme à notre image, selon notre ressemblance, et qu'il domine sur les poissons de la mer, sur les oiseaux du ciel, sur le bétail, sur toute la terre."},
                    {"ref": "Genèse 1:28", "texte": "Dieu les bénit, et Dieu leur dit : Soyez féconds, multipliez, remplissez la terre, et l'assujettissez ; et dominez sur les poissons de la mer, sur les oiseaux du ciel."},
                ],
            },
        ],
        "mnemo": "🧬 C-A-E = Corps – Âme – Esprit\n"
            "Corps = FORMÉ (argile)\nÂme = FAITE (vie émotionnelle)\nEsprit = CRÉÉ (communion avec Dieu)\n"
            "📌 Dieu est Esprit → Il nous parle esprit à esprit !",
        "histoire": "Dieu fabrique l'homme comme un chef fait son plat signature. "
            "Il prend de la terre (corps), souffle dessus (esprit), "
            "et la créature devient une âme vivante. "
            "Le chef dit : 'Image de Moi !' L'homme se regarde dans le miroir et voit un être royal avec couronne et sceptre. "
            "La grenouille du jardin voisin est très impressionnée.",
        "verite_cle": "L'homme est la seule créature créée à l'image de Dieu. "
            "Il est le sommet de toute la création — pas un accident cosmique, "
            "mais le chef-d'oeuvre intentionnel du Créateur.",
    },
    {
        "num": 10, "titre": "La Connaissance du Bien et du Mal",
        "couleur": "#F39C12",
        "intro": "La Parole de Dieu est une Parole de vie — pas simplement un livre de morale "
            "ou de philosophie. Dieu voulait que l'homme expérimente le bien et évite le mal. "
            "Les bénédictions de Dieu nous appartiennent quand nous choisissons la vie "
            "en obéissant à Sa Parole.",
        "sections": [
            {
                "titre": "Le Souffle de Vie et le Jardin d'Éden",
                "contenu": "Dieu a tout préparé avant de créer l'homme. "
                    "Le jardin d'Éden était un lieu d'abondance totale, de beauté parfaite.",
                "versets": [
                    {"ref": "Genèse 2:8-9", "texte": "L'Éternel Dieu planta un jardin en Éden, à l'orient, et il y mit l'homme qu'il avait formé. L'Éternel Dieu fit pousser du sol des arbres de toute espèce, agréables à voir et bons à manger, et l'arbre de la vie au milieu du jardin."},
                    {"ref": "Ésaïe 42:5", "texte": "Ainsi parle le Dieu, l'Éternel, qui a créé les cieux et les a déployés, qui a étendu la terre et ses productions, qui a donné la respiration à ceux qui la peuplent."},
                ],
            },
            {
                "titre": "La Volonté de Dieu : Bien Expérimenter, Mal Éviter",
                "contenu": "Dieu avait clairement enseigné la différence entre le bien et le mal. "
                    "L'arbre interdit n'était pas une punition — c'était une **protection**.",
                "versets": [
                    {"ref": "Genèse 2:16-17", "texte": "L'Éternel Dieu donna cet ordre à l'homme : Tu pourras manger de tous les arbres du jardin ; mais tu ne mangeras pas de l'arbre de la connaissance du bien et du mal, car le jour où tu en mangeras, tu mourras."},
                    {"ref": "Genèse 2:18", "texte": "L'Éternel Dieu dit : Il n'est pas bon que l'homme soit seul ; je lui ferai une aide semblable à lui."},
                    {"ref": "Genèse 2:24", "texte": "C'est pourquoi l'homme quittera son père et sa mère, et s'attachera à sa femme, et ils deviendront une seule chair."},
                ],
            },
        ],
        "mnemo": "🌳 JARDIN = LIBERTÉ TOTALE sauf 1 arbre\n"
            "✅ 9 999 arbres = OUI (abondance !)\n"
            "❌ 1 arbre = NON (protection !)\n"
            "Dieu = 99% OUI pour 1% NON\n"
            "📌 L'homme s'est fixé sur le 1%. Erreur fatale !",
        "histoire": "Dieu ouvre le plus grand buffet de l'histoire : 10 000 plats magnifiques. "
            "'Mangez tout !' dit-Il. 'Sauf ce plat au bout de la table — c'est du poison.' "
            "Adam et Ève ont 9 999 options délicieuses. "
            "Mais le 10 000ème les obsède. Ils le mangent quand même. "
            "Morale : Dieu donne l'abondance totale. Nous, on se fixe sur le seul interdit.",
        "verite_cle": "Le mariage est une institution divine créée avant la chute. "
            "Genèse 2:24 est la fondation biblique du mariage : un homme, une femme, une seule chair — pour la vie.",
    },
    {
        "num": 11, "titre": "Le Premier Péché de l'Humanité",
        "couleur": "#E94560",
        "intro": "Dieu a établi la vie aussi parfaitement que possible, "
            "donnant à l'homme et à la femme le choix selon le libre arbitre "
            "de la vivre abondamment. Mais Satan est venu pervertir cette Parole.",
        "sections": [
            {
                "titre": "Les 5 Tactiques de Satan pour Détruire la Parole",
                "contenu": "Satan utilise 5 tactiques précises :\n\n"
                    "**1.** Met en question l'intégrité de la Parole\n"
                    "**2.** Pousse à répondre en considérant\n"
                    "**3.** Omet librement les conséquences\n"
                    "**4.** Ajoute à la Parole ('vous n'y toucherez point' — Ève ajoute !)\n"
                    "**5.** Change la Parole ('vous ne mourrez PAS')",
                "versets": [
                    {"ref": "Genèse 3:1-4", "texte": "Le serpent était le plus rusé de tous les animaux des champs... Il dit à la femme : Dieu a-t-il réellement dit : Vous ne mangerez pas de tous les arbres du jardin ? ... Le serpent dit à la femme : Vous ne mourrez point."},
                ],
            },
            {
                "titre": "L'Homme a Perdu la Domination",
                "contenu": "Suite à la chute, l'homme a perdu la domination que Dieu lui avait donnée. "
                    "Satan est devenu 'le prince de ce monde'. Mais Dieu avait déjà prévu la solution.",
                "versets": [
                    {"ref": "Genèse 1:28", "texte": "Dieu les bénit, et Dieu leur dit : Soyez féconds, multipliez, remplissez la terre, et l'assujettissez."},
                    {"ref": "Jean 14:30", "texte": "Je ne parlerai plus guère avec vous ; car le prince du monde vient. Il n'a rien en moi."},
                ],
            },
            {
                "titre": "Jésus Christ : Notre Semence Promise",
                "contenu": "Genèse 3:15 est la première prophétie messianique de la Bible. "
                    "Dès la chute, Dieu annonce la victoire finale de Christ. "
                    "Jésus est la semence promise qui écrase la tête de l'adversaire.",
                "versets": [
                    {"ref": "Genèse 3:15", "texte": "Je mettrai inimitié entre toi et la femme, entre ta postérité et sa postérité : celle-ci t'écrasera la tête, et tu lui blesseras le talon."},
                    {"ref": "1 Jean 3:8", "texte": "Le Fils de Dieu a paru afin de détruire les oeuvres du diable."},
                ],
            },
        ],
        "mnemo": "🐍 SATAN = 5 tactiques (QOACE) :\n"
            "Q = Questionne ('A-t-il dit ?')\nO = Omet les conséquences\n"
            "A = Ajoute ('ni toucher' — Ève !)\nC = Change ('vous ne mourrez PAS')\n"
            "E = Engage à considérer l'interdit\n"
            "📌 Genèse 3:15 = 1ère prophétie de Christ !",
        "histoire": "Satan arrive avec micro, tableau et costume trois pièces. "
            "Étape 1 : 'Dieu a vraiment dit ÇA ?' (doute instillé). "
            "Étape 2 : 'Regarde comme c'est beau...' (tentation). "
            "Étape 3 : Il oublie de mentionner la mort (omission). "
            "Étape 4 : Ève ajoute 'ni toucher' (modification). "
            "Étape 5 : 'Vous ne mourrez PAS !' (mensonge pur). "
            "Résultat : chute. Mais Dieu répond au verset 15 : 'La semence écrasera ta tête.'",
        "verite_cle": "Genèse 3:15 est appelé le Protévangile — la première bonne nouvelle. "
            "Dès le début de la chute, Dieu annonce la victoire de Christ sur Satan.",
    },
    {
        "num": 12, "titre": "Le Plus Grand Principe : La Croyance",
        "couleur": "#8E44AD",
        "intro": "Le plus grand principe dans toute la vie, c'est la **croyance**. "
            "Pour recevoir quoi que ce soit de Dieu, on doit d'abord savoir "
            "ce qui est disponible, comment le recevoir, et qu'en faire. "
            "La croyance provient du coeur.",
        "sections": [
            {
                "titre": "Ce qui est Disponible en Dieu",
                "contenu": "Dieu veut bénir son peuple dans tous les domaines. "
                    "Avant de recevoir, il faut savoir ce qui est disponible. "
                    "L'ignorance empêche la réception.",
                "versets": [
                    {"ref": "3 Jean 2", "texte": "Bien-aimé, je souhaite que tu prospères à tous égards et sois en bonne santé, comme prospère l'état de ton âme."},
                    {"ref": "2 Corinthiens 9:8", "texte": "Et Dieu peut vous combler de toutes sortes de grâces, afin que, ayant toujours en toutes choses de quoi satisfaire à tous vos besoins, vous ayez encore en abondance pour toute bonne oeuvre."},
                    {"ref": "Romains 8:37", "texte": "Mais dans toutes ces choses nous sommes plus que vainqueurs par celui qui nous a aimés."},
                    {"ref": "Éphésiens 3:16-19", "texte": "Qu'il vous accorde, selon la richesse de sa gloire, d'être puissamment fortifiés par son Esprit dans l'homme intérieur... afin que vous soyez remplis jusqu'à toute la plénitude de Dieu."},
                ],
            },
            {
                "titre": "La Loi de la Croyance — 3 Images",
                "contenu": "**Image 1 :** Précis et préoccupé — on garde nos pensées sur la promesse de Dieu.\n\n"
                    "**Image 2 :** On se l'imagine — c'est l'image de croyance dans l'intelligence.\n\n"
                    "**Image 3 :** On agit selon la promesse de Dieu, fidèlement.",
                "versets": [
                    {"ref": "Romains 10:10", "texte": "Car c'est en croyant du coeur qu'on parvient à la justice, et c'est en confessant de la bouche qu'on parvient au salut."},
                    {"ref": "Proverbes 4:20-23", "texte": "Mon fils, sois attentif à mes paroles... Garde ton coeur plus que toute autre chose, car c'est de lui que viennent les sources de la vie."},
                    {"ref": "Romains 4:20-21", "texte": "Il ne chancela point par incrédulité au sujet de la promesse de Dieu ; mais il fut fortifié par la foi, donnant gloire à Dieu, et ayant la pleine certitude que ce que Dieu a promis, il est puissant pour l'accomplir."},
                    {"ref": "Philippiens 4:19", "texte": "Mon Dieu pourvoira à tous vos besoins selon sa richesse, avec gloire, en Jésus Christ."},
                ],
            },
            {
                "titre": "La Vie Synchronisée : Bouche + Coeur + Actions",
                "contenu": "Confesser signifie :\n"
                    "**1.** De notre BOUCHE\n**2.** Dans notre COEUR\n**3.** Avec nos ACTIONS\n\n"
                    "Lorsque nous croyons positivement, nous avons une vie dans l'abondance.",
                "versets": [
                    {"ref": "Jacques 1:21", "texte": "C'est pourquoi, rejetant toute souillure et tout débordement de malice, recevez avec douceur la parole qui a été plantée en vous, et qui peut sauver vos âmes."},
                    {"ref": "Hébreux 11:11", "texte": "C'est aussi par la foi que Sara elle-même, malgré son âge avancé, reçut la force d'être mère, parce qu'elle crut à la fidélité de celui qui avait fait la promesse."},
                    {"ref": "Éphésiens 1:19", "texte": "Et quelle est envers nous qui croyons l'infinie grandeur de sa puissance, se manifestant avec efficacité par la vertu de sa force."},
                ],
            },
        ],
        "mnemo": "🔑 3 ÉTAPES DE LA CROYANCE VICTORIEUSE :\n"
            "1️⃣ SAVOIR → Quelle promesse pour mon besoin ?\n"
            "2️⃣ IMAGINER → Mettre l'image de victoire dans mon esprit\n"
            "3️⃣ AGIR → Agir fidèlement selon la promesse\n"
            "📌 Bouche + Coeur + Actions = VIE SYNCHRONISÉE !",
        "histoire": "Un athlète veut gagner la course de sa vie. "
            "Étape 1 : il lit la promesse (Parole disponible). "
            "Étape 2 : il s'imagine franchir la ligne d'arrivée chaque matin (image de croyance). "
            "Étape 3 : il s'entraîne selon la promesse (action fidèle). "
            "Le jour J, la Parole de Dieu court avec lui. Il franchit la ligne avec une facilité déconcertante. "
            "Dans les gradins, trois anges prennent des notes : 'Voilà comment fonctionne la croyance.'",
        "verite_cle": "Romains 4:20-21 (Abraham) = le modèle parfait de la croyance : "
            "ne pas chanceler, être fortifié par la foi, "
            "avoir la pleine certitude que Dieu accomplit ce qu'Il a promis.",
    },
    {
        "num": 13, "titre": "L'Endurance de Job — Deux Types de Croyance",
        "couleur": "#F39C12",
        "intro": "Il y a deux types de croyance : **positive** et **négative**. "
            "La croyance est une loi. Au côté négatif, la crainte est une croyance à l'envers — "
            "elle produit des résultats négatifs aussi sûrement que la foi produit des résultats positifs. "
            "La seule chose qui fait échouer le croyant, c'est la crainte.",
        "sections": [
            {
                "titre": "Deux Types de Croyance",
                "contenu": "Au côté positif : confiance, assurance et fidélité aboutissent à la croyance.\n"
                    "Au côté négatif : doute, inquiétude et crainte aboutissent à l'incrédulité.\n\n"
                    "La crainte bâtit l'incrédulité — et c'est l'incrédulité qui fait échouer les promesses de Dieu.",
                "versets": [
                    {"ref": "Proverbes 29:25", "texte": "La crainte des hommes tend un piège ; mais celui qui se confie en l'Éternel est protégé."},
                    {"ref": "2 Timothée 1:7", "texte": "Car ce n'est pas un esprit de timidité que Dieu nous a donné, mais un esprit de force, d'amour et de sagesse."},
                    {"ref": "Deutéronome 31:8", "texte": "L'Éternel lui-même marchera devant toi, il sera lui-même avec toi, il ne te délaissera point et ne t'abandonnera point ; ne crains point et ne t'effraie point."},
                    {"ref": "Psaumes 34:5", "texte": "Ceux qui portent leurs regards vers lui seront rayonnants de joie, et leurs visages ne seront pas couverts de honte."},
                ],
            },
            {
                "titre": "L'Exemple de Job — La Crainte Négative",
                "contenu": "Job était béni comme Dieu voulait qu'il le soit. "
                    "Mais Job avait une crainte qui ouvrait une porte à l'adversaire. "
                    "Job 3:25 révèle que ce qu'il craignait lui est arrivé — "
                    "la crainte avait produit ses fruits négatifs.",
                "versets": [
                    {"ref": "Job 3:25", "texte": "Car ce que je craignais m'est arrivé, et ce dont j'avais peur m'est échu."},
                    {"ref": "Job 1:1", "texte": "Il y avait dans le pays d'Uts un homme qui s'appelait Job. Cet homme était intègre et droit ; il craignait Dieu et se détournait du mal."},
                    {"ref": "Job 1:5", "texte": "Quand les jours de festin étaient passés, Job les faisait venir et les sanctifiait... car Job se disait : Peut-être mes fils ont-ils péché et ont-ils maudit Dieu dans leur coeur."},
                    {"ref": "Jacques 1:13", "texte": "Que nul, lorsqu'il est tenté, ne dise : C'est Dieu qui me tente. Car Dieu ne peut être tenté par le mal, et il ne tente lui-même personne."},
                ],
            },
            {
                "titre": "La Parole de Dieu : Notre Sûreté dans l'Incertitude",
                "contenu": "La Parole de Dieu doit être pour nous un mouillage sûr "
                    "dans le vaste océan de doute, un rocher ferme dans la mer de spéculation — "
                    "afin que nous soyons certains au milieu de l'incertitude.",
                "versets": [
                    {"ref": "Ésaïe 33:6", "texte": "Il sera la sécurité de tes jours, une riche source de salut, de sagesse et de connaissance ; la crainte de l'Éternel est son trésor."},
                    {"ref": "Jacques 5:10-11", "texte": "Frères, prenez pour modèles de souffrance et de patience les prophètes qui ont parlé au nom du Seigneur. Voici, nous disons bienheureux ceux qui ont souffert patiemment. Vous avez entendu parler de la patience de Job, et vous avez vu la fin que le Seigneur lui a accordée."},
                ],
            },
        ],
        "mnemo": "🎭 2 TYPES de croyance :\n"
            "✅ FOI : Confiance → Assurance → Fidélité → CROYANCE\n"
            "❌ CRAINTE : Doute → Inquiétude → Peur → INCRÉDULITÉ\n"
            "📌 Job 3:25 = 'Ce que je craignais m'est arrivé' → La crainte ATTIRE le mal !",
        "histoire": "Job est le PDG le plus béni de sa région. "
            "Mais chaque soir avant de dormir, il signe une assurance pour ses enfants 'au cas où'. "
            "Satan voit l'assurance et dit : 'Ah, il n'est pas aussi confiant qu'il le paraît !' "
            "La porte de la crainte est ouverte. "
            "Leçon : les confessions de peur ouvrent des portes. Les confessions de foi les ferment.",
        "verite_cle": "La crainte est la croyance à l'envers. Elle produit des résultats négatifs "
            "aussi sûrement que la foi produit des résultats positifs. "
            "2 Timothée 1:7 : Dieu ne nous a PAS donné un esprit de crainte !",
    },
    {
        "num": 14, "titre": "L'Intégrité Spirituelle",
        "couleur": "#1ABC9C",
        "intro": "Malgré les attaques intenses du diable, Job n'a jamais accusé Dieu "
            "de lui avoir envoyé le mal. C'est le point majeur à retenir : "
            "il a tenu ferme dans son intégrité spirituelle. "
            "Sa délivrance finale démontre que Dieu récompense toujours celui qui persévère.",
        "sections": [
            {
                "titre": "Job Demeure Ferme dans Son Intégrité",
                "contenu": "Job 1:20-22 : Après avoir tout perdu en un jour, "
                    "Job se prosterne et adore Dieu. Il ne pèche pas et n'attribue "
                    "rien d'inconsidéré à Dieu. C'est le modèle de l'intégrité spirituelle sous pression extrême.",
                "versets": [
                    {"ref": "Job 1:20-22", "texte": "Alors Job se leva, déchira son manteau, et se rasa la tête ; puis se jetant par terre, il se prosterna... L'Éternel a donné, et l'Éternel a ôté ; que le nom de l'Éternel soit béni ! En tout cela, Job ne pécha point et n'attribua rien d'inconsidéré à Dieu."},
                    {"ref": "Job 2:9-10", "texte": "Sa femme lui dit : Tu persistes encore dans ton intégrité ! Maudis Dieu, et meurs. Job lui répondit : Tu parles comme une femme insensée. Quoi ! nous recevons de Dieu le bien, et nous ne recevrions pas aussi le mal ? En tout cela, Job ne pécha point par ses lèvres."},
                    {"ref": "Job 27:6", "texte": "Je m'attache à ma justice, je ne la lâcherai point ; mon coeur ne me reprochera aucun de mes jours."},
                    {"ref": "1 Jean 4:4", "texte": "Vous êtes de Dieu, petits enfants, et vous les avez vaincus, parce que celui qui est en vous est plus grand que celui qui est dans le monde."},
                ],
            },
            {
                "titre": "La Délivrance de Job — Le Double",
                "contenu": "Après avoir prié pour ses amis qui avaient mal parlé de Dieu, "
                    "Job reçoit sa délivrance. L'Éternel rétablit sa situation et lui donne "
                    "le **double** de ce qu'il avait. Job vivra encore 140 ans.",
                "versets": [
                    {"ref": "Job 42:10", "texte": "L'Éternel rétablit la situation de Job, lorsque Job eut prié pour ses amis. L'Éternel donna à Job le double de tout ce qu'il avait eu."},
                    {"ref": "Job 42:12-13", "texte": "L'Éternel bénit la fin de la vie de Job plus que le commencement... Il eut aussi sept fils et trois filles."},
                    {"ref": "Job 42:16-17", "texte": "Après cela, Job vécut encore cent quarante ans ; il vit ses fils et les fils de ses fils jusqu'à la quatrième génération. Puis Job mourut vieux et rassasié de jours."},
                    {"ref": "Éphésiens 6:12", "texte": "Car nous n'avons pas à lutter contre la chair et le sang, mais contre les dominations, contre les autorités, contre les princes des ténèbres de ce siècle, contre les esprits méchants dans les lieux célestes."},
                ],
            },
        ],
        "mnemo": "🏆 JOB = INTÉGRITÉ SOUS PRESSION :\n"
            "Perte totale → Adoration (pas accusation !)\n"
            "Amis erronés → Prière pour eux\n"
            "Fidélité → DOUBLE délivrance\n"
            "📌 Job 42:10 = Prier pour tes ennemis = clé de ta délivrance !",
        "histoire": "Job perd tout en 24 heures : enfants, richesses, santé. "
            "Sa femme lui dit : 'Maudis Dieu et meurs !' Job refuse. "
            "Ses amis passent 7 jours à lui expliquer que c'est sa faute. Job refuse de signer les accusations contre Dieu. "
            "À la fin, Dieu dit aux amis : 'Job a mieux parlé de moi que vous !' "
            "Et Job reçoit le DOUBLE. Morale : garder son intégrité quand tout s'effondre, c'est la clé du double.",
        "verite_cle": "Job 42:10 : L'Éternel rétablit la situation de Job LORSQUE Job eut prié pour ses amis. "
            "La clé de la délivrance était l'intercession pour ceux qui l'avaient accusé. "
            "L'intégrité spirituelle triomphe toujours.",
    },
]

# ══════════════════════════════════════════════════════════
# DONNÉES QUIZ — SM-2 Spaced Repetition
# ══════════════════════════════════════════════════════════
QUIZ_DATA = [
    # --- Segment 1 ---
    {"id":"s1q1","seg":1,"q":"Selon Jean 14:6, Jésus se définit comme...",
     "r":"Le chemin, la vérité et la vie",
     "c":["Un prophète parmi d'autres","Le chemin, la vérité et la vie","Un bon enseignant moral","La sagesse de Dieu"]},
    {"id":"s1q2","seg":1,"q":"L'abondance que Dieu désire pour son peuple selon le Segment 1 est...",
     "r":"Physique, mentale et spirituelle",
     "c":["Uniquement spirituelle","Physique, mentale et spirituelle","Uniquement financière","Seulement après la mort"]},
    {"id":"s1q3","seg":1,"q":"Quel verset dit : 'Sanctifie-les par ta vérité : ta parole est la vérité' ?",
     "r":"Jean 17:17",
     "c":["Jean 14:6","Jean 8:32","Jean 17:17","Deutéronome 30:19"]},
    # --- Segment 2 ---
    {"id":"s2q1","seg":2,"q":"Selon Jean 10:10, les 3 objectifs du voleur sont...",
     "r":"Dérober, égorger et détruire",
     "c":["Mentir, voler et tuer","Dérober, égorger et détruire","Tromper, blesser et ruiner","Séduire, corrompre et détruire"]},
    {"id":"s2q2","seg":2,"q":"Que dit Nombres 23:19 sur Dieu ?",
     "r":"Dieu n'est pas un homme pour mentir",
     "c":["Dieu est tout-puissant","Dieu n'est pas un homme pour mentir","Dieu aime son peuple","Dieu exauce la prière"]},
    {"id":"s2q3","seg":2,"q":"Selon Hébreux 4:12, la Parole de Dieu est...",
     "r":"Vivante et efficace",
     "c":["Ancienne et immuable","Vivante et efficace","Douce et apaisante","Forte et redoutable"]},
    # --- Segment 3 ---
    {"id":"s3q1","seg":3,"q":"Psaumes 119:105 dit que la Parole est...",
     "r":"Une lampe à mes pieds et une lumière sur mon sentier",
     "c":["Un bouclier contre l'ennemi","Une lampe à mes pieds et une lumière sur mon sentier","Un pain pour mon âme","Une force dans ma faiblesse"]},
    {"id":"s3q2","seg":3,"q":"La sincérité par rapport à la vérité...",
     "r":"N'est pas une garantie pour la vérité",
     "c":["Est toujours suffisante","N'est pas une garantie pour la vérité","Remplace la connaissance","Est la même chose que la vérité"]},
    {"id":"s3q3","seg":3,"q":"Selon Ésaïe 33:6, Dieu sera pour nous...",
     "r":"La sécurité de nos jours",
     "c":["Un refuge dans la tempête","La sécurité de nos jours","Un père bienveillant","Notre force quotidienne"]},
    # --- Segment 4 ---
    {"id":"s4q1","seg":4,"q":"Selon Luc 24:44, Jésus a divisé la Parole en...",
     "r":"3 catégories : Loi, Prophètes et Psaumes",
     "c":["2 parties : AT et NT","4 sections selon les thèmes","3 catégories : Loi, Prophètes et Psaumes","5 livres de base"]},
    {"id":"s4q2","seg":4,"q":"2 Timothée 2:15 appelle le croyant à se présenter comme...",
     "r":"Un ouvrier qui dispense droitement la parole",
     "c":["Un guerrier de la foi","Un ouvrier qui dispense droitement la parole","Un serviteur humble","Un prédicateur éloquent"]},
    {"id":"s4q3","seg":4,"q":"Psaumes 138:2 dit que Dieu a...",
     "r":"Fait passer sa parole avant tout ce qui le fait glorifier",
     "c":["Créé les cieux par sa parole","Fait passer sa parole avant tout ce qui le fait glorifier","Gardé sa parole pour ses fidèles","Révélé sa parole aux prophètes seulement"]},
    # --- Segment 5 ---
    {"id":"s5q1","seg":5,"q":"Selon 2 Pierre 1:20, aucune prophétie de l'Écriture...",
     "r":"Ne peut être un objet d'interprétation particulière",
     "c":["N'est facile à comprendre","Ne peut être un objet d'interprétation particulière","N'a été écrite par les hommes","N'est infaillible"]},
    {"id":"s5q2","seg":5,"q":"Les 3 clés d'interprétation (3C) sont...",
     "r":"Contexte, Clarté et Cible",
     "c":["Culture, Chronologie, Comparaison","Contexte, Clarté et Cible","Conviction, Compréhension, Cohérence","Citation, Commentaire, Conclusion"]},
    {"id":"s5q3","seg":5,"q":"Selon Romains 15:4, tout ce qui a été écrit d'avance l'a été pour...",
     "r":"Notre instruction et notre espérance",
     "c":["La gloire de Dieu seul","Notre instruction et notre espérance","Condamner les incroyants","Prouver l'existence de Dieu"]},
    # --- Segment 6 ---
    {"id":"s6q1","seg":6,"q":"Jean 1:1 nous dit que la Parole était...",
     "r":"Au commencement avec Dieu et était Dieu",
     "c":["Une révélation progressive","Au commencement avec Dieu et était Dieu","Créée avant les anges","Donnée à Moïse en premier"]},
    {"id":"s6q2","seg":6,"q":"Dans le segment 6, qui est l'Initiateur du salut ?",
     "r":"Dieu (Jésus Christ est l'Agent)",
     "c":["Jésus Christ","Dieu (Jésus Christ est l'Agent)","L'Esprit Saint","Les prophètes"]},
    {"id":"s6q3","seg":6,"q":"Selon Jérémie 4:23, après le passage de l'adversaire, la terre était...",
     "r":"Informe et vide, sans lumière",
     "c":["Couverte d'eau uniquement","Informe et vide, sans lumière","Peuplée de créatures mauvaises","En ordre parfait"]},
    # --- Segment 7 ---
    {"id":"s7q1","seg":7,"q":"Combien y a-t-il de terres selon la Parole ?",
     "r":"3 terres (originelle, actuelle, nouvelle)",
     "c":["1 seule terre","2 terres (actuelle et future)","3 terres (originelle, actuelle, nouvelle)","7 terres symboliques"]},
    {"id":"s7q2","seg":7,"q":"Au temps de qui la terre s'est-elle divisée en continents ?",
     "r":"Péleg",
     "c":["Noé","Abraham","Péleg","Babel"]},
    {"id":"s7q3","seg":7,"q":"Que décrit Apocalypse 21:1 ?",
     "r":"Un nouveau ciel et une nouvelle terre où la mer n'est plus",
     "c":["La fin du monde","Un nouveau ciel et une nouvelle terre où la mer n'est plus","Le retour de Christ","Le jugement dernier"]},
    # --- Segment 8 ---
    {"id":"s8q1","seg":8,"q":"L'idiome hébreu de permission signifie que 'Dieu a fait X' peut signifier...",
     "r":"Dieu a permis que X arrive",
     "c":["Dieu a directement causé X","Dieu a permis que X arrive","Dieu a prévu X de toute éternité","Dieu a récompensé X"]},
    {"id":"s8q2","seg":8,"q":"La raison d'être de l'homme selon le segment 8 est...",
     "r":"Aimer Dieu, l'adorer et communier avec Lui",
     "c":["Remplir la terre et la soumettre","Aimer Dieu, l'adorer et communier avec Lui","Étudier et enseigner la Parole","Obéir aux commandements"]},
    {"id":"s8q3","seg":8,"q":"Selon Jacques 1:13, Dieu...",
     "r":"Ne tente personne",
     "c":["Permet toutes les épreuves","Ne tente personne","Envoie des maladies pour nous purifier","Choisit qui il bénit"]},
    # --- Segment 9 ---
    {"id":"s9q1","seg":9,"q":"L'homme est composé de 3 éléments. Lesquels ?",
     "r":"Corps, Âme et Esprit",
     "c":["Corps, Cœur et Raison","Corps, Âme et Esprit","Chair, Sang et Esprit","Intellect, Volonté et Émotions"]},
    {"id":"s9q2","seg":9,"q":"Selon Genèse 2:7, le corps a été...",
     "r":"Formé de la poussière du sol",
     "c":["Créé de rien par la Parole","Formé de la poussière du sol","Fait à partir de l'eau","Modelé comme une statue d'argile"]},
    {"id":"s9q3","seg":9,"q":"Jean 4:24 dit que Dieu est Esprit et qu'il faut l'adorer...",
     "r":"En esprit et en vérité",
     "c":["Avec des sacrifices et des offrandes","En esprit et en vérité","Dans le temple et la prière","Avec humilité et jeûne"]},
    # --- Segment 10 ---
    {"id":"s10q1","seg":10,"q":"Selon Genèse 2:16-17, Dieu a dit à Adam qu'il pourrait manger...",
     "r":"De tous les arbres sauf l'arbre de la connaissance",
     "c":["De certains arbres seulement","De tous les arbres sauf l'arbre de la connaissance","Uniquement des fruits donnés par Dieu","De l'arbre de vie uniquement"]},
    {"id":"s10q2","seg":10,"q":"L'arbre interdit dans le jardin était en réalité...",
     "r":"Une protection, pas une punition",
     "c":["Une épreuve de fidélité arbitraire","Une protection, pas une punition","Un symbole du péché originel","Un test de force spirituelle"]},
    {"id":"s10q3","seg":10,"q":"Genèse 2:24 fonde le mariage comme...",
     "r":"L'homme et la femme qui deviennent une seule chair",
     "c":["Un contrat social entre familles","L'homme et la femme qui deviennent une seule chair","Une institution post-chute","Un arrangement pratique pour la société"]},
    # --- Segment 11 ---
    {"id":"s11q1","seg":11,"q":"Combien de tactiques Satan utilise-t-il contre la Parole selon le segment 11 ?",
     "r":"5 (questionner, considérer, omettre, ajouter, changer)",
     "c":["3 (mentir, séduire, détruire)","5 (questionner, considérer, omettre, ajouter, changer)","7 (les 7 péchés capitaux)","2 (doute et peur)"]},
    {"id":"s11q2","seg":11,"q":"Genèse 3:15 est appelé le Protévangile car...",
     "r":"C'est la première prophétie annonçant la victoire de Christ",
     "c":["C'est le premier verset de la Bible","C'est la première prophétie annonçant la victoire de Christ","C'est le premier commandement de Dieu","C'est la première mention du salut explicite"]},
    {"id":"s11q3","seg":11,"q":"Après la chute, l'homme a perdu...",
     "r":"La domination sur la création",
     "c":["Son intelligence et sa sagesse","La domination sur la création","Sa capacité à prier","Son âme immortelle"]},
    # --- Segment 12 ---
    {"id":"s12q1","seg":12,"q":"Selon 3 Jean 2, Dieu souhaite que tu prospères...",
     "r":"À tous égards et en bonne santé",
     "c":["Uniquement spirituellement","À tous égards et en bonne santé","Selon tes mérites spirituels","Dans la souffrance purificatrice"]},
    {"id":"s12q2","seg":12,"q":"Les 3 images de croyance pour la victoire sont...",
     "r":"Précision, Imagination, Action",
     "c":["Prière, Jeûne, Confession","Précision, Imagination, Action","Lecture, Méditation, Mémorisation","Foi, Espérance, Amour"]},
    {"id":"s12q3","seg":12,"q":"La vie synchronisée selon le segment 12 signifie confesser...",
     "r":"De la bouche, dans le cœur et avec les actions",
     "c":["En public, en privé et en prière","De la bouche, dans le cœur et avec les actions","Devant l'Église, devant Dieu et devant soi","En paroles, en actes et en jeûne"]},
    # --- Segment 13 ---
    {"id":"s13q1","seg":13,"q":"Les deux types de croyance selon le segment 13 sont...",
     "r":"Positive (foi) et négative (crainte)",
     "c":["Intellectuelle et émotionnelle","Positive (foi) et négative (crainte)","Biblique et traditionnelle","Personnelle et collective"]},
    {"id":"s13q2","seg":13,"q":"Selon 2 Timothée 1:7, Dieu ne nous a pas donné...",
     "r":"Un esprit de timidité (crainte)",
     "c":["Un esprit de sagesse","Un esprit de timidité (crainte)","Un esprit de force","Un esprit de jugement"]},
    {"id":"s13q3","seg":13,"q":"Job 3:25 révèle que...",
     "r":"Ce que Job craignait lui est arrivé",
     "c":["Job était innocent de tout péché","Ce que Job craignait lui est arrivé","Dieu avait abandonné Job","Satan avait raison sur Job"]},
    # --- Segment 14 ---
    {"id":"s14q1","seg":14,"q":"Malgré ses épreuves, Job n'a jamais...",
     "r":"Accusé Dieu de lui avoir envoyé le mal",
     "c":["Cessé de prier","Accusé Dieu de lui avoir envoyé le mal","Demandé de l'aide à ses amis","Reconnu ses péchés"]},
    {"id":"s14q2","seg":14,"q":"Que se passe-t-il pour Job après qu'il a prié pour ses amis (Job 42:10) ?",
     "r":"L'Éternel rétablit sa situation et doubla ses biens",
     "c":["Il reçut des excuses de ses amis","L'Éternel rétablit sa situation et doubla ses biens","Il fut guéri instantanément","Dieu lui révéla tous ses mystères"]},
    {"id":"s14q3","seg":14,"q":"Selon Éphésiens 6:12, notre combat est contre...",
     "r":"Les dominations, les autorités et les puissances des ténèbres",
     "c":["Les personnes qui nous font du mal","Les dominations, les autorités et les puissances des ténèbres","Notre propre nature pécheresse","Les épreuves matérielles de la vie"]},
]

# ══════════════════════════════════════════════════════════
# 66 LIVRES
# ══════════════════════════════════════════════════════════
ALL_BOOKS = [
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

GROUPES_BIBLE = [
    {"nom":"Pentateuque (5)","livres":["Genèse","Exode","Lévitique","Nombres","Deutéronome"],
     "acronyme":"GE-EX-LÉV-NOM-DEU",
     "mnemo":"GEorges EXplose LEVitant sur NOMbreux DEUtons !",
     "histoire":"GEorges, boucher géant, EXplore la ville en LÉVitant. Il compte un NOMbre de fois et le fait DEUx fois. Les voisins appellent la police."},
    {"nom":"Livres Historiques (12)","livres":["Josué","Juges","Ruth","1 Samuel","2 Samuel","1 Rois","2 Rois","1 Chroniques","2 Chroniques","Esdras","Néhémie","Esther"],
     "acronyme":"JO-JU-RU-SA-SA-R-R-CH-CH-ESD-NÉH-EST",
     "mnemo":"JOJo JUgeur sur RUche avec 2 SAmuels, 2 Rois, 2 CHroniques, ESDras, NÉHémie, ESTher !",
     "histoire":"JOJo le clown JUgeur atterrit sur une RUche. Deux SAuterelles en costume arrivent. Deux Rois se battent avec des CHronometeurs. ESDras souffle du feu sur NÉHumiste. ESTrade s'effondre."},
    {"nom":"Livres Poétiques (5)","livres":["Job","Psaumes","Proverbes","Ecclésiaste","Cantique des Cantiques"],
     "acronyme":"JOB-PS-PRO-ECC-CAN",
     "mnemo":"JOBert PSyché chante PROverbes ECCentriques sur son CANapé !",
     "histoire":"JOBert au chômage depuis 3 siècles. Son PSychologue dit : chante des PROverbes. Il le fait ECCentriquement sur son CANapé en pyjama de licorne. Sa voisine filme pour TikTok."},
    {"nom":"Grands Prophètes (5)","livres":["Ésaïe","Jérémie","Lamentations","Ézéchiel","Daniel"],
     "acronyme":"ÉS-JÉR-LAM-ÉZ-DAN",
     "mnemo":"ÉSpadon rencontre JÉRôme qui LAMente, ÉZéchias appelle DANiel !",
     "histoire":"Un ÉSpadon géant frappe chez JÉRôme qui se LAMente (moustache perdue). ÉZéchias arrive en robe de soirée et appelle DANiel, danseur de lion professionnel."},
    {"nom":"Petits Prophètes (12)","livres":["Osée","Joël","Amos","Abdias","Jonas","Michée","Nahum","Habacuc","Sophonie","Aggée","Zacharie","Malachie"],
     "acronyme":"OS-JO-AM-AB-JON-MI-NA-HA-SO-AG-ZA-MAL",
     "mnemo":"OS du JOuet de l'AMbassadeur sur ABricot, JONquille dans MIroir, NAvet-HAricot en SOurdine, note AG ZA MAL !",
     "histoire":"Diplomate perd l'OS de son jouet. Il atterrit sur un ABricot magique qui fait pousser une JONquille. La fleur mange NAvet et HAricot discrètement (SOurdine). Elle note dans AGenda : ZApper MALette."},
    {"nom":"Les 4 Évangiles","livres":["Matthieu","Marc","Luc","Jean"],
     "acronyme":"MAT-MAR-LU-JE",
     "mnemo":"MATelas dans MARmite de LUciole paie avec JEtons !",
     "histoire":"MAT le matelas bavard glisse dans la MARmite de LUciole chef cuisinière. Pour payer, il donne des JEtons de casino. Le commissaire arrive — c'est aussi un matelas."},
    {"nom":"Actes des Apôtres (1)","livres":["Actes des Apôtres"],
     "acronyme":"ACTES",
     "mnemo":"120 ACrobates à Pentecôte parlent en 17 langues !",
     "histoire":"120 ACrobates débarquent au Temple. Sauts périlleux en 17 langues simultanées. Pierre prend le micro : 'Il est 9h du matin, nous ne sommes pas ivres !' L'Église est née."},
    {"nom":"Lettres de Paul (13)","livres":["Romains","1 Corinthiens","2 Corinthiens","Galates","Éphésiens","Philippiens","Colossiens","1 Thessaloniciens","2 Thessaloniciens","1 Timothée","2 Timothée","Tite","Philémon"],
     "acronyme":"RO-CO-CO-GA-ÉP-PH-CO-TH-TH-TI-TI-TIT-PHI",
     "mnemo":"ROmains, 2 COrinthiens, GAlates, ÉPhésiens, PHilippiens, COlossiens, 2 THessaloniciens, 2 TImothée, TIte, PHIlémon !",
     "histoire":"Paul-RObot mange 2 COraux et GAteau ÉPhémère. Suit un PHare jusqu'au COlosse géant. Boit 2 THéières, combat 2 TIgres en cravate. Vainqueur : TITon philosophe chauve."},
    {"nom":"Lettres Générales (8)","livres":["Hébreux","Jacques","1 Pierre","2 Pierre","1 Jean","2 Jean","3 Jean","Jude"],
     "acronyme":"HÉB-JAC-PI-PI-J-J-J-JU",
     "mnemo":"HÉBergeur, JACquot, 2 PIerres, 3 Jeans, JUde dans même couloir d'hôtel !",
     "histoire":"HÉBergeur gère le chaos : JACquot perroquet réserve 2 chambres pour frères PIerre (qui se disputent). 3 cousins prénommés JEAN avec même bagage. JUde arrive avec tambourin. Hôtel ferme."},
    {"nom":"Apocalypse (1)","livres":["Apocalypse"],
     "acronyme":"APOCALYPSE",
     "mnemo":"Grand Finale impossible à oublier : 7 sceaux, dragon, ville en or !",
     "histoire":"Jean exilé sur Patmos. Agneau ouvre 7 sceaux-enveloppes. 7 anges soufflent trompettes désaccordées. Dragon rouge danse la samba. Ville toute en or descend du ciel. Stylo de Jean explose. Rideau."},
]

# ══════════════════════════════════════════════════════════
# BASE DE DONNÉES
# ══════════════════════════════════════════════════════════
DB = "cours_fondamental.db"

def init_db():
    c = sqlite3.connect(DB)
    # Notes
    c.execute("""CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seg_num INTEGER DEFAULT 0,
        titre TEXT, livre TEXT, ref TEXT,
        texte TEXT, note TEXT, date TEXT
    )""")
    # Quiz cards (SM-2)
    c.execute("""CREATE TABLE IF NOT EXISTS quiz_cards(
        id TEXT PRIMARY KEY,
        seg_num INTEGER,
        ease_factor REAL DEFAULT 2.5,
        interval_days INTEGER DEFAULT 1,
        repetitions INTEGER DEFAULT 0,
        next_review TEXT,
        last_score INTEGER DEFAULT -1
    )""")
    # Quiz history
    c.execute("""CREATE TABLE IF NOT EXISTS quiz_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT, score INTEGER, date TEXT
    )""")
    # Segments visited
    c.execute("""CREATE TABLE IF NOT EXISTS progress(
        seg_num INTEGER PRIMARY KEY,
        visited INTEGER DEFAULT 0,
        last_visit TEXT,
        time_spent INTEGER DEFAULT 0
    )""")
    c.commit()
    # Init quiz cards if empty
    if c.execute("SELECT COUNT(*) FROM quiz_cards").fetchone()[0] == 0:
        today = datetime.now().strftime("%Y-%m-%d")
        for q in QUIZ_DATA:
            c.execute("INSERT OR IGNORE INTO quiz_cards(id,seg_num,next_review) VALUES(?,?,?)",
                (q["id"], q["seg"], today))
        c.commit()
    c.close()

# Notes CRUD
def add_note(sn, titre, livre, ref, texte, note):
    c = sqlite3.connect(DB)
    c.execute("INSERT INTO notes(seg_num,titre,livre,ref,texte,note,date) VALUES(?,?,?,?,?,?,?)",
        (sn, titre, livre, ref, texte, note, datetime.now().strftime("%Y-%m-%d %H:%M")))
    c.commit(); c.close()

def get_notes(seg=0):
    c = sqlite3.connect(DB)
    q = "SELECT * FROM notes"
    if seg > 0: q += f" WHERE seg_num={seg}"
    q += " ORDER BY date DESC"
    r = c.execute(q).fetchall(); c.close(); return r

def del_note(nid):
    c = sqlite3.connect(DB)
    c.execute("DELETE FROM notes WHERE id=?", (nid,)); c.commit(); c.close()

def get_note_count():
    c = sqlite3.connect(DB)
    r = c.execute("SELECT COUNT(*) FROM notes").fetchone()[0]; c.close(); return r

# Progress CRUD
def mark_visited(seg_num):
    c = sqlite3.connect(DB)
    c.execute("""INSERT INTO progress(seg_num,visited,last_visit) VALUES(?,1,?)
        ON CONFLICT(seg_num) DO UPDATE SET visited=1, last_visit=?""",
        (seg_num, datetime.now().strftime("%Y-%m-%d %H:%M"),
         datetime.now().strftime("%Y-%m-%d %H:%M")))
    c.commit(); c.close()

def get_progress():
    c = sqlite3.connect(DB)
    r = c.execute("SELECT seg_num FROM progress WHERE visited=1").fetchall()
    c.close(); return [x[0] for x in r]

# Quiz SM-2
def get_due_cards():
    today = datetime.now().strftime("%Y-%m-%d")
    c = sqlite3.connect(DB)
    r = c.execute("SELECT id,seg_num,ease_factor,interval_days,repetitions FROM quiz_cards WHERE next_review<=? ORDER BY next_review ASC", (today,)).fetchall()
    c.close(); return r

def get_quiz_stats():
    c = sqlite3.connect(DB)
    total = c.execute("SELECT COUNT(*) FROM quiz_history").fetchone()[0]
    correct = c.execute("SELECT COUNT(*) FROM quiz_history WHERE score>=1").fetchone()[0]
    mastered = c.execute("SELECT COUNT(*) FROM quiz_cards WHERE repetitions>=3").fetchone()[0]
    due = len(get_due_cards())
    c.close()
    return {"total": total, "correct": correct, "mastered": mastered, "due": due}

def update_card_sm2(card_id, score):
    """score: 0=fail, 1=hard, 2=good, 3=easy"""
    c = sqlite3.connect(DB)
    row = c.execute("SELECT ease_factor,interval_days,repetitions FROM quiz_cards WHERE id=?", (card_id,)).fetchone()
    if not row:
        c.close(); return
    ef, interval, reps = row
    # SM-2 simplified
    if score == 0:
        interval = 1; reps = 0
    elif score == 1:
        interval = max(1, interval)
        ef = max(1.3, ef - 0.15)
    elif score == 2:
        if reps == 0: interval = 1
        elif reps == 1: interval = 3
        else: interval = round(interval * ef)
        reps += 1
    else:  # 3 = easy
        if reps == 0: interval = 2
        elif reps == 1: interval = 5
        else: interval = round(interval * ef * 1.3)
        ef = min(3.0, ef + 0.1)
        reps += 1
    next_rev = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
    c.execute("UPDATE quiz_cards SET ease_factor=?,interval_days=?,repetitions=?,next_review=?,last_score=? WHERE id=?",
        (ef, interval, reps, next_rev, score, card_id))
    c.execute("INSERT INTO quiz_history(card_id,score,date) VALUES(?,?,?)",
        (card_id, score, datetime.now().strftime("%Y-%m-%d %H:%M")))
    c.commit(); c.close()

def get_seg_quiz_stats(seg_num):
    c = sqlite3.connect(DB)
    cards = c.execute("SELECT id,repetitions,last_score FROM quiz_cards WHERE seg_num=?", (seg_num,)).fetchall()
    c.close()
    if not cards: return 0, 0
    mastered = sum(1 for _,r,_ in cards if r >= 3)
    return len(cards), mastered

# Search
def search_content(query):
    if not query or len(query.strip()) < 2:
        return []
    terms = query.lower().strip().split()
    results = []
    for seg in SEGMENTS:
        score = 0
        matches = []
        # Search in titre and intro
        text_pool = seg["titre"].lower() + " " + seg["intro"].lower()
        for term in terms:
            if term in text_pool: score += 2
        # Search in sections
        for section in seg["sections"]:
            sec_text = section["titre"].lower() + " " + section["contenu"].lower()
            for term in terms:
                if term in sec_text: score += 1
            # Search in versets
            for v in section["versets"]:
                v_text = v["texte"].lower() + " " + v["ref"].lower()
                for term in terms:
                    if term in v_text:
                        score += 3
                        matches.append({"ref": v["ref"], "texte": v["texte"][:120] + "..."})
        if score > 0:
            results.append({"seg": seg, "score": score, "matches": matches[:3]})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:8]

# ══════════════════════════════════════════════════════════
# IA (optionnel)
# ══════════════════════════════════════════════════════════
def gen_ia(api_key, ref, texte):
    if not ANTHROPIC_OK:
        return None, "Module anthropic non disponible."
    try:
        client = anthropic.Anthropic(api_key=api_key)
        r = client.messages.create(
            model="claude-opus-4-5", max_tokens=700,
            messages=[{"role":"user","content":
                f"Expert mnémotechnique biblique francophone. Pour '{ref}' : '{texte}'\n"
                f"Crée: 1) Mnémotechnique original 2) Histoire loufoque (5 phrases)\n"
                f"JSON uniquement: {{\"mnemo\":\"...\",\"histoire\":\"...\"}}"}])
        import json as _json
        raw = r.content[0].text.strip().replace("```json","").replace("```","")
        d = _json.loads(raw)
        return d.get("mnemo",""), d.get("histoire","")
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════════════════════════
# SESSION & INIT
# ══════════════════════════════════════════════════════════
for k, v in [("page","accueil"),("api_key",""),("seg_idx",None),
              ("quiz_card",None),("quiz_answered",False),("quiz_selected",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

init_db()

# ══════════════════════════════════════════════════════════
# EN-TÊTE
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="app-header">
    <div class="app-title">✝️ Cours Fondamental</div>
    <div class="app-sub">LA VOIE DE L'ABONDANCE ET DE LA PUISSANCE · 14 SEGMENTS</div>
</div>""", unsafe_allow_html=True)

# NAVIGATION (2 rangées × 3)
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1:
    if st.button("🏠\nAccueil"): st.session_state.page = "accueil"
with r1c2:
    if st.button("📚\nCours"): st.session_state.page = "cours"; st.session_state.seg_idx = None
with r1c3:
    if st.button("🔍\nRecherche"): st.session_state.page = "recherche"

r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    due = len(get_due_cards())
    label = f"🎯\nQuiz ({due})" if due > 0 else "🎯\nQuiz"
    if st.button(label): st.session_state.page = "quiz"; st.session_state.quiz_card = None; st.session_state.quiz_answered = False
with r2c2:
    if st.button("📊\nProgrès"): st.session_state.page = "progres"
with r2c3:
    if st.button("📝\nNotes"): st.session_state.page = "notes"

# Livres accessible via bouton discret
with st.expander("📖 66 Livres de la Bible"):
    if st.button("Ouvrir la section 66 Livres", key="go_livres"):
        st.session_state.page = "livres"; st.rerun()

st.markdown("<hr style='border-color:#252545;margin:.3rem 0 .6rem;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE ACCUEIL
# ══════════════════════════════════════════════════════════
if st.session_state.page == "accueil":
    visited = get_progress()
    stats = get_quiz_stats()
    nb_notes = get_note_count()

    # Stats row 1
    a, b, c_, d = st.columns(4)
    with a: st.markdown(f'<div class="stat-card"><p class="stat-num">14</p><p class="stat-lbl">Segments</p></div>', unsafe_allow_html=True)
    with b: st.markdown(f'<div class="stat-card"><p class="stat-num">{len(visited)}</p><p class="stat-lbl">Étudiés</p></div>', unsafe_allow_html=True)
    with c_: st.markdown(f'<div class="stat-card"><p class="stat-num">{stats["mastered"]}</p><p class="stat-lbl">Maîtrisés</p></div>', unsafe_allow_html=True)
    with d: st.markdown(f'<div class="stat-card"><p class="stat-num">{nb_notes}</p><p class="stat-lbl">Notes</p></div>', unsafe_allow_html=True)

    # Progress bar
    pct = int(len(visited) / 14 * 100)
    st.markdown(f"""
    <div style="margin:.8rem 0 .3rem;">
        <div style="display:flex;justify-content:space-between;font-size:.75rem;color:#888;margin-bottom:.3rem;">
            <span>Progression du cours</span><span style="color:var(--gold);">{pct}%</span>
        </div>
        <div class="prog-bar-outer">
            <div class="prog-bar-inner" style="width:{pct}%;background:linear-gradient(90deg,var(--gold),#E67E22);"></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Quiz reminder
    if stats["due"] > 0:
        st.markdown(f"""
        <div class="card card-red" style="margin:.6rem 0;">
            <span style="color:var(--accent);font-weight:800;">🎯 {stats['due']} carte(s) à réviser aujourd'hui !</span><br>
            <span style="color:#ddd;font-size:.82rem;">Continue ta progression avec le quiz adaptatif.</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-gold" style="margin-top:.6rem;">
        <div style="color:var(--gold);font-weight:800;font-size:1rem;margin-bottom:.5rem;">📖 À Propos de ce Cours</div>
        <p style="color:#ddd;font-size:.84rem;line-height:1.7;margin:0;">
        Ce cours biblique en <strong style="color:var(--gold)">14 segments</strong> explore la voie que Dieu a tracée :<br><br>
        ✅ <strong>L'Abondance</strong> — Dieu désire que tu prospères en tout.<br>
        ✅ <strong>La Puissance</strong> — La force de manifester la puissance de Dieu.<br>
        ✅ <strong>La Parole</strong> — Notre seule norme de croyance et d'action.<br>
        ✅ <strong>La Croyance</strong> — Le plus grand principe dans toute la vie.<br><br>
        <em style="color:var(--gold);">Jean 14:6 — "Je suis le chemin, la vérité et la vie."</em>
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">📚 Les 14 Segments</div>', unsafe_allow_html=True)

    for i in range(0, 14, 2):
        col_a, col_b = st.columns(2)
        for j, col in enumerate([col_a, col_b]):
            idx = i + j
            if idx < 14:
                seg = SEGMENTS[idx]
                is_visited = seg["num"] in visited
                badge = "✅" if is_visited else "📖"
                with col:
                    nb_cards, nb_mastered = get_seg_quiz_stats(seg["num"])
                    st.markdown(f"""
                    <div class="card card-gold" style="padding:.65rem;min-height:80px;">
                        <div style="color:var(--gold);font-size:.65rem;font-weight:800;margin-bottom:2px;">
                            {badge} SEG {seg['num']}</div>
                        <div style="color:#fff;font-size:.76rem;font-weight:700;line-height:1.3;">
                            {seg['titre']}</div>
                        <div style="color:#555;font-size:.65rem;margin-top:3px;">
                            Quiz: {nb_mastered}/{nb_cards}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"h_{idx}"):
                        st.session_state.page = "cours"
                        st.session_state.seg_idx = idx
                        st.rerun()

    st.markdown('<div class="sec-title">🔑 Clé API IA (optionnel)</div>', unsafe_allow_html=True)
    api = st.text_input("Clé Anthropic pour générer des mnémotechniques IA",
        value=st.session_state.api_key, type="password",
        placeholder="sk-ant-...", label_visibility="collapsed")
    if api:
        st.session_state.api_key = api
        st.success("✅ Clé enregistrée pour cette session !")
    st.caption("Sans clé, tous les contenus pré-construits restent disponibles.")

# ══════════════════════════════════════════════════════════
# PAGE COURS
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "cours":

    if st.session_state.seg_idx is not None:
        idx = st.session_state.seg_idx
        seg = SEGMENTS[idx]

        # Mark as visited
        mark_visited(seg["num"])

        if st.button("← Retour aux segments"):
            st.session_state.seg_idx = None; st.rerun()

        nb_cards, nb_mastered = get_seg_quiz_stats(seg["num"])
        st.markdown(f"""
        <div class="seg-header">
            <div style="display:flex;align-items:flex-start;gap:.5rem;">
                <div class="seg-num-badge">{seg['num']}</div>
                <div style="flex:1;">
                    <div style="color:var(--gold);font-weight:900;font-size:1rem;
                        line-height:1.3;margin-bottom:.4rem;">{seg['titre']}</div>
                    <p style="color:#ccc;font-size:.82rem;line-height:1.6;margin:0 0 .4rem;">
                        {seg['intro']}</p>
                    <span style="background:rgba(39,174,96,.2);color:var(--green);border-radius:8px;
                        padding:2px 8px;font-size:.68rem;font-weight:700;">
                        Quiz: {nb_mastered}/{nb_cards} maîtrisé(s)</span>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="key-truth">
            <span style="color:var(--gold);font-weight:800;">💡 Vérité Clé :</span><br>
            {seg['verite_cle']}
        </div>""", unsafe_allow_html=True)

        for section in seg["sections"]:
            st.markdown(f'<div class="sub-title">📌 {section["titre"]}</div>', unsafe_allow_html=True)
            if section["contenu"]:
                content_html = "<br>".join(section["contenu"].split('\n'))
                st.markdown(f'<div class="card card-orange" style="font-size:.84rem;color:#ddd;line-height:1.7;">{content_html}</div>',
                    unsafe_allow_html=True)
            for v in section["versets"]:
                st.markdown(f"""
                <div class="verse-box">
                    <span class="ref-tag">📖 {v['ref']} — Louis Segond</span>
                    {v['texte']}
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🧠 Mnémotechnique</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mnemo-box">{seg["mnemo"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🎭 Histoire Loufoque</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="story-box">{seg["histoire"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-title">📌 Toutes les Références</div>', unsafe_allow_html=True)
        all_refs = []
        for s in seg["sections"]:
            all_refs += [v["ref"] for v in s["versets"]]
        st.markdown('<div class="card">' +
            " ".join([f'<span class="ref-pill">{r}</span>' for r in all_refs]) +
            '</div>', unsafe_allow_html=True)

        # Quiz rapide pour ce segment
        seg_quiz = [q for q in QUIZ_DATA if q["seg"] == seg["num"]]
        if seg_quiz:
            st.markdown('<div class="sec-title">🎯 Questions Clés de ce Segment</div>', unsafe_allow_html=True)
            for q in seg_quiz:
                with st.expander(f"❓ {q['q']}"):
                    st.markdown(f'<div class="quiz-correct">✅ {q["r"]}</div>', unsafe_allow_html=True)

        st.markdown("---")
        nav_a, nav_b = st.columns(2)
        with nav_a:
            if idx > 0 and st.button(f"← Segment {idx}"):
                st.session_state.seg_idx = idx - 1; st.rerun()
        with nav_b:
            if idx < 13 and st.button(f"Segment {idx+2} →"):
                st.session_state.seg_idx = idx + 1; st.rerun()

    else:
        st.markdown('<div class="sec-title">📚 Les 14 Segments du Cours</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="card card-green" style="margin-bottom:.8rem;">
            <p style="color:var(--green);font-size:.82rem;margin:0;">
            💡 Appuie sur 📖 pour étudier chaque segment avec ses versets (Louis Segond),
            ses sections détaillées, sa mnémotechnique et son histoire loufoque.
            </p>
        </div>""", unsafe_allow_html=True)

        visited = get_progress()
        for seg in SEGMENTS:
            is_visited = seg["num"] in visited
            nb_cards, nb_mastered = get_seg_quiz_stats(seg["num"])
            nb_versets = sum(len(s["versets"]) for s in seg["sections"])
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                badge = "✅" if is_visited else "🔵"
                st.markdown(f"""
                <div class="card card-gold">
                    <div style="display:flex;align-items:flex-start;gap:.5rem;">
                        <div class="seg-num-badge">{seg['num']}</div>
                        <div>
                            <div style="color:#fff;font-weight:700;font-size:.86rem;line-height:1.3;">
                                {badge} {seg['titre']}</div>
                            <div style="color:#888;font-size:.7rem;margin-top:3px;">
                                {len(seg['sections'])} sections · {nb_versets} versets · Quiz {nb_mastered}/{nb_cards}
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                if st.button("📖", key=f"s_{seg['num']}"):
                    st.session_state.seg_idx = seg["num"] - 1; st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE RECHERCHE
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "recherche":
    st.markdown('<div class="sec-title">🔍 Recherche Intelligente</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card card-teal" style="margin-bottom:.6rem;">
        <p style="color:var(--teal);font-size:.82rem;margin:0;">
        Recherche dans les <strong>versets, titres et contenus</strong> des 14 segments.
        Essaie : "abondance", "croyance", "Job", "Satan", "crainte"...
        </p>
    </div>""", unsafe_allow_html=True)

    query = st.text_input("🔍 Rechercher dans le cours...",
        placeholder="Ex: vie abondante, Genèse, domination...",
        label_visibility="collapsed")

    if query:
        results = search_content(query)
        if results:
            st.caption(f"✅ {len(results)} résultat(s) pour « {query} »")
            for res in results:
                seg = res["seg"]
                st.markdown(f"""
                <div class="search-result">
                    <span class="search-seg-tag">Segment {seg['num']}</span>
                    <strong style="color:#fff;font-size:.88rem;">{seg['titre']}</strong>
                    <div style="color:#888;font-size:.72rem;margin-top:.3rem;">
                        Score de pertinence : {res['score']} point(s)
                    </div>
                </div>""", unsafe_allow_html=True)
                for match in res["matches"]:
                    st.markdown(f"""
                    <div class="verse-box" style="margin-left:.5rem;">
                        <span class="ref-tag">📖 {match['ref']}</span>
                        {match['texte']}
                    </div>""", unsafe_allow_html=True)
                if st.button(f"📖 Ouvrir le Segment {seg['num']}", key=f"sr_{seg['num']}"):
                    st.session_state.page = "cours"
                    st.session_state.seg_idx = seg["num"] - 1
                    st.rerun()
                st.markdown("---")
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:2rem">🔍</div>
                <p style="color:#888;margin:.5rem 0 0;">Aucun résultat trouvé. Essaie d'autres mots-clés.</p>
            </div>""", unsafe_allow_html=True)
    else:
        # Suggestions
        st.markdown('<div class="sec-title">💡 Suggestions de recherche</div>', unsafe_allow_html=True)
        suggestions = ["abondance","croyance","parole","crainte","Job","Satan","création","vérité","foi","domination"]
        cols = st.columns(5)
        for i, sug in enumerate(suggestions):
            with cols[i % 5]:
                if st.button(sug, key=f"sug_{sug}"):
                    st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE QUIZ (SM-2 Spaced Repetition)
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "quiz":
    st.markdown('<div class="sec-title">🎯 Quiz Adaptatif</div>', unsafe_allow_html=True)

    stats = get_quiz_stats()
    due_cards = get_due_cards()

    # Stats rapides
    q1, q2, q3, q4 = st.columns(4)
    with q1: st.markdown(f'<div class="stat-card"><p class="stat-num">{stats["due"]}</p><p class="stat-lbl">À réviser</p></div>', unsafe_allow_html=True)
    with q2: st.markdown(f'<div class="stat-card"><p class="stat-num">{stats["mastered"]}</p><p class="stat-lbl">Maîtrisées</p></div>', unsafe_allow_html=True)
    with q3: st.markdown(f'<div class="stat-card"><p class="stat-num">{stats["total"]}</p><p class="stat-lbl">Réponses</p></div>', unsafe_allow_html=True)
    acc = int(stats["correct"]/stats["total"]*100) if stats["total"]>0 else 0
    with q4: st.markdown(f'<div class="stat-card"><p class="stat-num">{acc}%</p><p class="stat-lbl">Précision</p></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-purple" style="margin:.6rem 0;font-size:.8rem;color:#ddd;line-height:1.6;">
        <strong style="color:var(--purple);">🧠 Algorithme SM-2 (Spaced Repetition)</strong><br>
        Chaque question est programmée pour réapparaître au moment optimal.<br>
        Plus tu réponds correctement, plus l'intervalle s'allonge.
    </div>""", unsafe_allow_html=True)

    if not due_cards:
        st.markdown("""
        <div class="card card-green" style="text-align:center;padding:1.5rem;">
            <div style="font-size:2.5rem">🎉</div>
            <p style="color:var(--green);font-weight:800;margin:.5rem 0;">Toutes les révisions sont à jour !</p>
            <p style="color:#888;font-size:.82rem;margin:0;">Reviens demain pour de nouvelles révisions.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # Pick current card
        if st.session_state.quiz_card is None:
            card_data = due_cards[0]
            card_id = card_data[0]
            # Find question
            qdata = next((q for q in QUIZ_DATA if q["id"] == card_id), None)
            if qdata:
                choices = qdata["c"][:]
                random.shuffle(choices)
                st.session_state.quiz_card = {
                    "id": card_id,
                    "seg": card_data[1],
                    "q": qdata["q"],
                    "r": qdata["r"],
                    "choices": choices
                }
                st.session_state.quiz_answered = False
                st.session_state.quiz_selected = None

        card = st.session_state.quiz_card
        if card:
            seg_name = next((s["titre"] for s in SEGMENTS if s["num"] == card["seg"]), "")
            remaining = len(due_cards)

            st.markdown(f"""
            <div class="quiz-card">
                <div style="display:flex;justify-content:space-between;margin-bottom:.6rem;">
                    <span style="color:var(--gold);font-size:.72rem;font-weight:700;">
                        📚 Segment {card['seg']} — {seg_name[:30]}...</span>
                    <span style="color:#888;font-size:.72rem;">{remaining} à réviser</span>
                </div>
                <div class="quiz-question">❓ {card['q']}</div>
            </div>""", unsafe_allow_html=True)

            if not st.session_state.quiz_answered:
                for i, choice in enumerate(card["choices"]):
                    if st.button(choice, key=f"choice_{i}"):
                        st.session_state.quiz_selected = choice
                        st.session_state.quiz_answered = True
                        st.rerun()
            else:
                selected = st.session_state.quiz_selected
                correct = card["r"]
                is_correct = (selected == correct)

                if is_correct:
                    st.markdown(f'<div class="quiz-correct">✅ Correct ! {correct}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="quiz-wrong">❌ Incorrect. Tu as répondu : {selected}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quiz-correct">✅ Bonne réponse : {correct}</div>', unsafe_allow_html=True)

                st.markdown("<br><strong style='color:var(--gold);'>Comment était cette question ?</strong>", unsafe_allow_html=True)
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    if st.button("😰\nTrès dur", key="score0"):
                        update_card_sm2(card["id"], 0)
                        st.session_state.quiz_card = None
                        st.session_state.quiz_answered = False
                        st.rerun()
                with sc2:
                    if st.button("😓\nDifficile", key="score1"):
                        update_card_sm2(card["id"], 1)
                        st.session_state.quiz_card = None
                        st.session_state.quiz_answered = False
                        st.rerun()
                with sc3:
                    if st.button("😊\nCorrect", key="score2"):
                        update_card_sm2(card["id"], 2)
                        st.session_state.quiz_card = None
                        st.session_state.quiz_answered = False
                        st.rerun()
                with sc4:
                    if st.button("😄\nFacile !", key="score3"):
                        update_card_sm2(card["id"], 3)
                        st.session_state.quiz_card = None
                        st.session_state.quiz_answered = False
                        st.rerun()

    # Mode entraînement libre
    st.markdown('<div class="sec-title">🏋️ Entraînement Libre</div>', unsafe_allow_html=True)
    seg_opts = ["Tous les segments"] + [f"Seg {s['num']} — {s['titre'][:30]}" for s in SEGMENTS]
    sel_seg = st.selectbox("Choisir un segment pour s'entraîner", seg_opts, label_visibility="collapsed")

    if st.button("🔀 Question aléatoire", key="random_q"):
        if sel_seg == "Tous les segments":
            pool = QUIZ_DATA
        else:
            seg_num = int(sel_seg.split(" ")[1])
            pool = [q for q in QUIZ_DATA if q["seg"] == seg_num]
        if pool:
            q = random.choice(pool)
            choices = q["c"][:]
            random.shuffle(choices)
            st.session_state["random_quiz"] = {"q": q["q"], "r": q["r"], "choices": choices, "answered": False, "selected": None}

    if "random_quiz" in st.session_state and st.session_state["random_quiz"]:
        rq = st.session_state["random_quiz"]
        st.markdown(f'<div class="quiz-card"><div class="quiz-question">❓ {rq["q"]}</div></div>', unsafe_allow_html=True)

        if not rq["answered"]:
            for i, ch in enumerate(rq["choices"]):
                if st.button(ch, key=f"rq_{i}"):
                    rq["selected"] = ch
                    rq["answered"] = True
                    st.rerun()
        else:
            if rq["selected"] == rq["r"]:
                st.markdown(f'<div class="quiz-correct">✅ Correct ! {rq["r"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="quiz-wrong">❌ Tu as répondu : {rq["selected"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="quiz-correct">✅ Bonne réponse : {rq["r"]}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE PROGRÈS
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "progres":
    st.markdown('<div class="sec-title">📊 Tableau de Bord de Progression</div>', unsafe_allow_html=True)

    visited = get_progress()
    stats = get_quiz_stats()
    nb_notes = get_note_count()
    total_quiz_cards = len(QUIZ_DATA)
    acc = int(stats["correct"]/stats["total"]*100) if stats["total"]>0 else 0

    # Global stats
    g1, g2, g3 = st.columns(3)
    with g1: st.markdown(f'<div class="stat-card"><p class="stat-num">{len(visited)}/14</p><p class="stat-lbl">Segments vus</p></div>', unsafe_allow_html=True)
    with g2: st.markdown(f'<div class="stat-card"><p class="stat-num">{stats["mastered"]}/{total_quiz_cards}</p><p class="stat-lbl">Cartes maîtrisées</p></div>', unsafe_allow_html=True)
    with g3: st.markdown(f'<div class="stat-card"><p class="stat-num">{acc}%</p><p class="stat-lbl">Précision quiz</p></div>', unsafe_allow_html=True)

    # Barres de progression globales
    pct_segments = int(len(visited)/14*100)
    pct_mastered = int(stats["mastered"]/total_quiz_cards*100) if total_quiz_cards>0 else 0

    st.markdown(f"""
    <div class="card" style="margin:.6rem 0;">
        <div style="margin-bottom:.6rem;">
            <div style="display:flex;justify-content:space-between;font-size:.78rem;color:#aaa;margin-bottom:.2rem;">
                <span>📚 Segments étudiés</span><span style="color:var(--gold);">{pct_segments}%</span>
            </div>
            <div class="prog-bar-outer">
                <div class="prog-bar-inner" style="width:{pct_segments}%;background:linear-gradient(90deg,var(--gold),#E67E22);"></div>
            </div>
        </div>
        <div style="margin-bottom:.6rem;">
            <div style="display:flex;justify-content:space-between;font-size:.78rem;color:#aaa;margin-bottom:.2rem;">
                <span>🧠 Cartes quiz maîtrisées</span><span style="color:var(--purple);">{pct_mastered}%</span>
            </div>
            <div class="prog-bar-outer">
                <div class="prog-bar-inner" style="width:{pct_mastered}%;background:linear-gradient(90deg,var(--purple),#8E44AD);"></div>
            </div>
        </div>
        <div>
            <div style="display:flex;justify-content:space-between;font-size:.78rem;color:#aaa;margin-bottom:.2rem;">
                <span>🎯 Précision quiz</span><span style="color:var(--green);">{acc}%</span>
            </div>
            <div class="prog-bar-outer">
                <div class="prog-bar-inner" style="width:{acc}%;background:linear-gradient(90deg,var(--green),#27AE60);"></div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Détail par segment
    st.markdown('<div class="sec-title">📋 Détail par Segment</div>', unsafe_allow_html=True)

    for seg in SEGMENTS:
        is_visited = seg["num"] in visited
        nb_cards, nb_mastered = get_seg_quiz_stats(seg["num"])
        pct = int(nb_mastered/nb_cards*100) if nb_cards>0 else 0
        bar_color = "var(--green)" if pct >= 100 else ("var(--gold)" if pct >= 50 else "var(--accent)")
        visited_badge = '<span class="ok-badge">✅ Vu</span>' if is_visited else '<span style="color:#555;font-size:.7rem;">Non vu</span>'

        st.markdown(f"""
        <div class="card" style="padding:.65rem;margin:.3rem 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem;">
                <div>
                    <span style="color:var(--gold);font-size:.7rem;font-weight:800;">SEG {seg['num']}</span>
                    <span style="color:#ddd;font-size:.78rem;font-weight:600;margin-left:.3rem;">{seg['titre'][:35]}...</span>
                </div>
                {visited_badge}
            </div>
            <div style="display:flex;justify-content:space-between;font-size:.7rem;color:#888;margin-bottom:.2rem;">
                <span>Quiz: {nb_mastered}/{nb_cards} maîtrisée(s)</span>
                <span style="color:{bar_color};">{pct}%</span>
            </div>
            <div class="prog-bar-outer">
                <div class="prog-bar-inner" style="width:{pct}%;background:{bar_color};"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Statistiques quiz détaillées
    st.markdown('<div class="sec-title">📈 Statistiques Quiz</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card card-blue">
        <p style="color:#ddd;font-size:.84rem;line-height:1.8;margin:0;">
        🎯 Total réponses : <strong style="color:var(--gold);">{stats['total']}</strong><br>
        ✅ Bonnes réponses : <strong style="color:var(--green);">{stats['correct']}</strong><br>
        ❌ Mauvaises réponses : <strong style="color:var(--accent);">{stats['total']-stats['correct']}</strong><br>
        🏆 Cartes maîtrisées : <strong style="color:var(--gold);">{stats['mastered']}/{total_quiz_cards}</strong><br>
        📅 À réviser aujourd'hui : <strong style="color:var(--orange);">{stats['due']}</strong><br>
        📝 Notes créées : <strong style="color:var(--blue);">{nb_notes}</strong>
        </p>
    </div>""", unsafe_allow_html=True)

    if len(visited) == 14 and stats["mastered"] == total_quiz_cards:
        st.markdown("""
        <div class="card card-gold" style="text-align:center;padding:1.2rem;margin-top:.8rem;">
            <div style="font-size:2.5rem">🏆</div>
            <p style="color:var(--gold);font-weight:900;margin:.3rem 0;">Cours Complété !</p>
            <p style="color:#ddd;font-size:.82rem;margin:0;">Tu as maîtrisé tous les 14 segments du Cours Fondamental !</p>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE NOTES
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "notes":
    st.markdown('<div class="sec-title">📝 Mes Notes Personnelles</div>', unsafe_allow_html=True)

    opts = ["Toutes"] + [f"Seg {s['num']} — {s['titre'][:30]}..." for s in SEGMENTS]
    sel = st.selectbox("Filtrer", opts, label_visibility="collapsed")
    seg_f = 0 if sel == "Toutes" else int(sel.split(" ")[1])
    notes = get_notes(seg_f)
    st.caption(f"{len(notes)} note(s)")

    if not notes:
        st.markdown("""
        <div class="card" style="text-align:center;padding:1.5rem;">
            <div style="font-size:2.5rem">📭</div>
            <p style="color:#888;margin:.5rem 0 0;">Aucune note. Ajoute-en une ci-dessous !</p>
        </div>""", unsafe_allow_html=True)

    for n in notes:
        nid, sn, titre, livre, ref, texte, note, date = n
        with st.expander(f"{'📌 Seg '+str(sn)+' — ' if sn else ''}{livre} {ref} · {date[:10]}"):
            if texte:
                st.markdown(f'<div class="verse-box"><span class="ref-tag">📖 {livre} {ref}</span>{texte}</div>',
                    unsafe_allow_html=True)
            if note:
                st.markdown(f'<div class="card card-blue" style="margin-top:.4rem;font-size:.84rem;color:#ddd;">'
                    f'<strong style="color:var(--blue)">📝 Ma Note</strong><br>{note}</div>',
                    unsafe_allow_html=True)
            if st.button("🗑️ Supprimer", key=f"dn_{nid}"):
                del_note(nid); st.rerun()

    st.markdown('<div class="sec-title">➕ Ajouter une Note</div>', unsafe_allow_html=True)
    with st.expander("📝 Nouvelle note"):
        seg_opts = [f"Seg {s['num']} — {s['titre'][:35]}" for s in SEGMENTS] + ["Hors cours"]
        seg_sel = st.selectbox("Segment", seg_opts, key="seg_note")
        sn_n = 0 if seg_sel == "Hors cours" else int(seg_sel.split(" ")[1])
        st_n = "" if sn_n == 0 else SEGMENTS[sn_n-1]["titre"]

        livre_n = st.selectbox("Livre", ALL_BOOKS, key="lv_note")
        ref_n = st.text_input("Référence", placeholder="ex: 14:6", key="ref_note")
        texte_n = st.text_area("Texte du verset", placeholder="Colle le texte ici...", height=80, key="tx_note")
        note_n = st.text_area("Ma note personnelle", placeholder="Ma réflexion, commentaire...", height=80, key="nt_note")

        gen_cb = st.checkbox("🤖 Générer mnémotechnique IA", key="gen_note",
            value=bool(st.session_state.api_key))

        if st.button("💾 Enregistrer", key="save_note"):
            if not ref_n.strip():
                st.error("❌ La référence est obligatoire !")
            else:
                note_finale = note_n.strip()
                if gen_cb and st.session_state.api_key and texte_n.strip():
                    with st.spinner("🧠 Génération IA..."):
                        m, h = gen_ia(st.session_state.api_key, f"{livre_n} {ref_n}", texte_n)
                    if m:
                        note_finale += f"\n\n🧠 Mnémotechnique IA:\n{m}\n\n🎭 Histoire:\n{h}"
                    else:
                        st.warning(f"IA indisponible: {h}")
                add_note(sn_n, st_n, livre_n, ref_n.strip(), texte_n.strip(), note_finale)
                st.success(f"✅ {livre_n} {ref_n} enregistré !"); st.rerun()

# ══════════════════════════════════════════════════════════
# PAGE 66 LIVRES
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "livres":
    st.markdown('<div class="sec-title">🗂️ Les 66 Livres de la Bible</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-green">
        <p style="color:var(--green);font-weight:700;margin:0 0 .3rem;">🎯 Méthode Globale</p>
        <p style="color:#ddd;font-size:.82rem;margin:0;line-height:1.7;">
        <strong>AT (39)</strong> = 5+12+5+5+12 livres<br>
        <strong>NT (27)</strong> = 4+1+13+8+1 livres<br>
        <strong style="color:var(--gold);">📌 39+27=66 · 3×9=27 ✓</strong>
        </p>
    </div>""", unsafe_allow_html=True)

    with st.expander("🔢 Les 66 livres dans l'ordre"):
        for i, bk in enumerate(ALL_BOOKS):
            col = "#E94560" if i >= 39 else "var(--gold)"
            st.markdown(f"""
            <div style="display:flex;padding:3px 0;border-bottom:1px solid #1a1a35;">
                <span style="color:{col};font-weight:800;width:28px;font-size:.78rem;">{i+1}</span>
                <span style="color:#ddd;font-size:.83rem;">{bk}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a1a2e,#0a0a18);border-radius:12px;
        padding:.7rem;margin:1rem 0 .3rem;border:2px solid var(--gold);">
        <h3 style="color:var(--gold);margin:0;font-size:1.1rem;">✡️ Ancien Testament — 39 Livres</h3>
    </div>""", unsafe_allow_html=True)

    for g in GROUPES_BIBLE[:5]:
        with st.expander(f"📂 {g['nom']}"):
            st.markdown(f"""
            <div class="card card-purple" style="margin-bottom:.4rem;">
                <strong style="color:var(--purple)">🔤 Acronyme</strong><br>
                <span style="color:var(--gold);font-size:.95rem;font-weight:800;
                    letter-spacing:2px;">{g['acronyme']}</span>
            </div>""", unsafe_allow_html=True)
            st.markdown(f'<div class="mnemo-box"><strong>💡</strong> {g["mnemo"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="story-box" style="margin-top:.4rem;"><strong>🎭</strong> {g["histoire"]}</div>', unsafe_allow_html=True)
            first = g["livres"][0]
            start = ALL_BOOKS.index(first) + 1 if first in ALL_BOOKS else 1
            for i, bk in enumerate(g["livres"]):
                st.markdown(f"""
                <div style="display:flex;align-items:center;padding:3px 8px;
                    margin:2px 0;background:#1a1a35;border-radius:8px;">
                    <span style="color:var(--gold);font-weight:900;width:28px;font-size:.78rem;">#{start+i}</span>
                    <span style="color:#fff;font-size:.85rem;font-weight:600;">{bk}</span>
                </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0a1a,#0a0a18);border-radius:12px;
        padding:.7rem;margin:1rem 0 .3rem;border:2px solid var(--accent);">
        <h3 style="color:var(--accent);margin:0;font-size:1.1rem;">✝️ Nouveau Testament — 27 Livres</h3>
    </div>""", unsafe_allow_html=True)

    for g in GROUPES_BIBLE[5:]:
        with st.expander(f"📂 {g['nom']}"):
            st.markdown(f"""
            <div class="card card-red" style="margin-bottom:.4rem;">
                <strong style="color:var(--accent)">🔤 Acronyme</strong><br>
                <span style="color:var(--gold);font-size:.95rem;font-weight:800;
                    letter-spacing:2px;">{g['acronyme']}</span>
            </div>""", unsafe_allow_html=True)
            st.markdown(f'<div class="mnemo-box"><strong>💡</strong> {g["mnemo"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="story-box" style="margin-top:.4rem;"><strong>🎭</strong> {g["histoire"]}</div>', unsafe_allow_html=True)
            first = g["livres"][0]
            start = ALL_BOOKS.index(first) + 1 if first in ALL_BOOKS else 40
            for i, bk in enumerate(g["livres"]):
                st.markdown(f"""
                <div style="display:flex;align-items:center;padding:3px 8px;
                    margin:2px 0;background:#1a0a2a;border-radius:8px;">
                    <span style="color:var(--accent);font-weight:900;width:28px;font-size:.78rem;">#{start+i}</span>
                    <span style="color:#fff;font-size:.85rem;font-weight:600;">{bk}</span>
                </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-gold" style="margin-top:.8rem;text-align:center;padding:1rem;">
        <div style="font-size:1.5rem">🏆</div>
        <p style="color:var(--gold);font-weight:800;margin:.2rem 0;">Grand Défi !</p>
        <p style="color:#ddd;font-size:.8rem;margin:0;line-height:1.8;">
        <strong style="color:var(--green)">1.</strong> 5 groupes AT<br>
        <strong style="color:var(--green)">2.</strong> 5 groupes NT<br>
        <strong style="color:var(--green)">3.</strong> Chaque acronyme<br>
        <strong style="color:var(--gold)">🎯 66 livres en 2 minutes !</strong>
        </p>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════
st.markdown("""
<hr style='border-color:#1a1a35;margin:.8rem 0 .3rem;'>
<div style='text-align:center;color:#333;font-size:.68rem;'>
    ✝️ Cours Fondamental · La Voie de l'Abondance et de la Puissance · 14 Segments · Louis Segond
</div>""", unsafe_allow_html=True)
