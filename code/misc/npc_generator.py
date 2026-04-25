"""
LLM Roleplay Persona Generator
------------------------------

This file provides:
1. Canonical global trait tables
2. Background-linked role data
3. Hand-authored behavioral rule tables
4. Character generation helpers
5. Resolved-character building
6. Prompt rendering
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
# GLOBAL TABLES
# ============================================================================

GENDERS = ["m", "f"]

ALIGNMENTS = [
    "CE",
    "CN",
    "LE",
    "NE",
    "N",
    "NG",
    "LG",
    "LN",
    "CG",
]

ANCESTRIES = [
    "human",
    "dwarf",
    "elf",
    "halfling",
]

ROLES = [
    "acolyte",
    "charlatan",
    "criminal",
    "entertainer",
    "artisan",
    "hermit",
    "noble",
    "outlander",
    "sage",
    "sailor",
    "soldier",
    "urchin",
]

AGES = [
    "young",
    "adult",
    "mature",
    "elder",
]

# ============================================================================
# NAME TABLES
# ============================================================================

HUMAN_NAMES_MALE = [
    "Adam",
    "Adelard",
    "Aldous",
    "Anselm",
    "Arnold",
    "Bernard",
    "Bertram",
    "Charles",
    "Clerebold",
    "Conrad",
    "Diggory",
    "Drogo",
    "Everard",
    "Frederick",
    "Geoffrey",
    "Gerald",
    "Gilbert",
    "Godfrey",
    "Gunter",
    "Guy",
    "Henry",
    "Heward",
    "Hubert",
    "Hugh",
    "Jocelyn",
    "John",
    "Lance",
    "Manfred",
    "Miles",
    "Nicholas",
    "Norman",
    "Odo",
    "Percival",
    "Peter",
    "Ralf",
    "Randal",
    "Raymond",
    "Reynard",
    "Richard",
    "Robert",
    "Roger",
    "Roland",
    "Rolf",
    "Simon",
    "Theobald",
    "Theodoric",
    "Thomas",
    "Timm",
    "William",
    "Wymar",
]

HUMAN_NAMES_FEMALE = [
    "Adelaide",
    "Agatha",
    "Agnes",
    "Alice",
    "Aline",
    "Anne",
    "Avelina",
    "Avice",
    "Beatrice",
    "Cecily",
    "Egelina",
    "Eleanor",
    "Elizabeth",
    "Ella",
    "Eloise",
    "Elysande",
    "Emeny",
    "Emma",
    "Emmeline",
    "Ermina",
    "Eva",
    "Galiena",
    "Geva",
    "Giselle",
    "Griselda",
    "Hadwisa",
    "Helen",
    "Herleva",
    "Hugolina",
    "Ida",
    "Isabella",
    "Jacoba",
    "Jane",
    "Joan",
    "Juliana",
    "Katherine",
    "Margery",
    "Mary",
    "Matilda",
    "Maynild",
    "Millicent",
    "Oriel",
    "Rohesia",
    "Rosalind",
    "Rosamund",
    "Sarah",
    "Susannah",
    "Sybil",
    "Williamina",
    "Yvonne",
]

ELF_NAMES_MALE = [
    "Adran",
    "Aelar",
    "Aerdeth",
    "Ahvain",
    "Aramil",
    "Arannis",
    "Aust",
    "Azaki",
    "Beiro",
    "Berrian",
    "Caeldrim",
    "Carric",
    "Dayereth",
    "Dreali",
    "Efferil",
    "Eiravel",
    "Enialis",
    "Erdan",
    "Erevan",
    "Fivin",
    "Galinndan",
    "Gennal",
    "Hadarai",
    "Halimath",
    "Heian",
    "Himo",
    "Immeral",
    "Ivellios",
    "Korfel",
    "Lamlis",
    "Laucian",
    "Lucan",
    "Mindartis",
    "Naal",
    "Nutae",
    "Paelias",
    "Peren",
    "Quarion",
    "Riardon",
    "Rolen",
    "Soveliss",
    "Suhnae",
    "Thamior",
    "Tharivol",
    "Theren",
    "Theriatis",
    "Thervan",
    "Uthemar",
    "Vanuath",
    "Varis",
]

ELF_NAMES_FEMALE = [
    "Adrie",
    "Ahinar",
    "Althaea",
    "Anastrianna",
    "Andraste",
    "Antinua",
    "Arara",
    "Baelitae",
    "Bethrynna",
    "Birel",
    "Caelynn",
    "Chaedi",
    "Claira",
    "Dara",
    "Drusilia",
    "Elama",
    "Enna",
    "Faral",
    "Felosial",
    "Hatae",
    "Ielenia",
    "Ilanis",
    "Irann",
    "Jarsali",
    "Jelenneth",
    "Keyleth",
    "Leshanna",
    "Lia",
    "Maiathah",
    "Malquis",
    "Meriele",
    "Mialee",
    "Myathethil",
    "Naivara",
    "Quelenna",
    "Quillathe",
    "Ridaro",
    "Sariel",
    "Shanairla",
    "Shava",
    "Silaqui",
    "Sumnes",
    "Theirastra",
    "Thiala",
    "Tiaathque",
    "Traulam",
    "Vadania",
    "Valanthe",
    "Valna",
    "Xanaphia",
]

ELF_FAMILY_NAMES = [
    "Aloro",
    "Amakiir",
    "Amastacia",
    "Ariessus",
    "Arnuanna",
    "Berevan",
    "Caerdonel",
    "Caphaxath",
    "Casilltenirra",
    "Cithreth",
    "Dalanthan",
    "Eathalena",
    "Erenaeth",
    "Ethanasath",
    "Fasharash",
    "Firahel",
    "Floshem",
    "Galanodel",
    "Goltorah",
    "Hanali",
    "Holimion",
    "Horineth",
    "Iathrana",
    "Ilphelkiir",
    "Iranapha",
    "Koehlanna",
    "Lathalas",
    "Liadon",
    "Meliamne",
    "Mellerelel",
    "Mystralath",
    "Naïlo",
    "Netyoive",
    "Ofandrus",
    "Ostoroth",
    "Othronus",
    "Qualanthri",
    "Raethran",
    "Rothenel",
    "Selevarun",
    "Siannodel",
    "Suithrasas",
    "Sylvaranth",
    "Teinithra",
    "Tiltathana",
    "Wasanthi",
    "Withrethin",
    "Xiloscient",
    "Xistsrith",
    "Yaeldrin",
]

DWARF_NAMES_MALE = [
    "Adrik",
    "Alberich",
    "Baern",
    "Barendd",
    "Beloril",
    "Brottor",
    "Dain",
    "Dalgal",
    "Darrak",
    "Delg",
    "Duergath",
    "Dworic",
    "Eberk",
    "Einkil",
    "Elaim",
    "Erias",
    "Fallond",
    "Fargrim",
    "Gardain",
    "Gilthur",
    "Gimgen",
    "Gimurt",
    "Harbek",
    "Kildrak",
    "Kilvar",
    "Morgran",
    "Morkral",
    "Nalral",
    "Nordak",
    "Nuraval",
    "Oloric",
    "Olunt",
    "Orsik",
    "Oskar",
    "Rangrim",
    "Reirak",
    "Rurik",
    "Taklinn",
    "Thoradin",
    "Thorin",
    "Thradal",
    "Tordek",
    "Traubon",
    "Travok",
    "Ulfgar",
    "Uraim",
    "Veit",
    "Vonbin",
    "Vondal",
    "Whurbin",
]

DWARF_NAMES_FEMALE = [
    "Anbera",
    "Artin",
    "Audhild",
    "Balifra",
    "Barbena",
    "Bardryn",
    "Bolhild",
    "Dagnal",
    "Dariff",
    "Delre",
    "Diesa",
    "Eldeth",
    "Eridred",
    "Falkrunn",
    "Fallthra",
    "Finellen",
    "Gillydd",
    "Gunnloda",
    "Gurdis",
    "Helgret",
    "Helja",
    "Hlin",
    "Ilde",
    "Jarana",
    "Kathra",
    "Kilia",
    "Kristryd",
    "Liftrasa",
    "Marastyr",
    "Mardred",
    "Morana",
    "Nalaed",
    "Nora",
    "Nurkara",
    "Oriff",
    "Ovina",
    "Riswynn",
    "Sannl",
    "Therlin",
    "Thodris",
    "Torbera",
    "Tordrid",
    "Torgga",
    "Urshar",
    "Valida",
    "Vistra",
    "Vonana",
    "Werydd",
    "Whurdred",
    "Yurgunn",
]

DWARF_CLAN_NAMES = [
    "Aranore",
    "Balderk",
    "Battlehammer",
    "Bigtoe",
    "Bloodkith",
    "Bofdann",
    "Brawnanvil",
    "Brazzik",
    "Broodfist",
    "Burrowfound",
    "Caebrek",
    "Daerdahk",
    "Dankil",
    "Daraln",
    "Deepdelver",
    "Durthane",
    "Eversharp",
    "Fallack",
    "Fireforge",
    "Foamtankard",
    "Frostbeard",
    "Glanhig",
    "Goblinbane",
    "Goldfinder",
    "Gorunn",
    "Graybeard",
    "Hammerstone",
    "Helcral",
    "Holderhek",
    "Ironfist",
    "Loderr",
    "Lutgehr",
    "Morigak",
    "Orcfoe",
    "Rakankrak",
    "Ruby-Eye",
    "Rumnaheim",
    "Silveraxe",
    "Silverstone",
    "Steelfist",
    "Stoutale",
    "Strakeln",
    "Strongheart",
    "Thrahak",
    "Torevir",
    "Torunn",
    "Trollbleeder",
    "Trueanvil",
    "Trueblood",
    "Ungart",
]

HALFLING_NAMES_MALE = [
    "Alton",
    "Ander",
    "Bernie",
    "Bobbin",
    "Cade",
    "Callus",
    "Corrin",
    "Dannad",
    "Danniel",
    "Eddie",
    "Egart",
    "Eldon",
    "Errich",
    "Fildo",
    "Finnan",
    "Franklin",
    "Garret",
    "Garth",
    "Gilbert",
    "Gob",
    "Harol",
    "Igor",
    "Jasper",
    "Keith",
    "Kevin",
    "Lazam",
    "Lerry",
    "Lindal",
    "Lyle",
    "Merric",
    "Mican",
    "Milo",
    "Morrin",
    "Nebin",
    "Nevil",
    "Osborn",
    "Ostran",
    "Oswalt",
    "Perrin",
    "Poppy",
    "Reed",
    "Roscoe",
    "Sam",
    "Shardon",
    "Tye",
    "Ulmo",
    "Wellby",
    "Wendel",
    "Wenner",
    "Wes",
]

HALFLING_NAMES_FEMALE = [
    "Alain",
    "Andry",
    "Anne",
    "Bella",
    "Blossom",
    "Bree",
    "Callie",
    "Chenna",
    "Cora",
    "Dee",
    "Dell",
    "Eida",
    "Eran",
    "Euphemia",
    "Georgina",
    "Gynnie",
    "Harriet",
    "Jasmine",
    "Jillian",
    "Jo",
    "Kithri",
    "Lavinia",
    "Lidda",
    "Maegan",
    "Marigold",
    "Merla",
    "Myria",
    "Nedda",
    "Nikki",
    "Nora",
    "Olivia",
    "Paela",
    "Pearl",
    "Pennie",
    "Philomena",
    "Portia",
    "Robbie",
    "Rose",
    "Saral",
    "Seraphina",
    "Shaena",
    "Stacee",
    "Tawna",
    "Thea",
    "Trym",
    "Tyna",
    "Vani",
    "Verna",
    "Wella",
    "Willow",
]

HALFLING_CLAN_NAMES = [
    "Appleblossom",
    "Bigheart",
    "Brightmoon",
    "Brushgather",
    "Cherrycheeks",
    "Copperkettle",
    "Deephollow",
    "Elderberry",
    "Fastfoot",
    "Fatrabbit",
    "Glenfellow",
    "Goldfound",
    "Goodbarrel",
    "Goodearth",
    "Greenbottle",
    "Greenleaf",
    "High-hill",
    "Hilltopple",
    "Hogcollar",
    "Honeypot",
    "Jamjar",
    "Kettlewhistle",
    "Leagallow",
    "Littlefoot",
    "Nimblefingers",
    "Porridgepot",
    "Quickstep",
    "Reedfellow",
    "Shadowquick",
    "Silvereyes",
    "Smoothhands",
    "Stonebridge",
    "Stoutbridge",
    "Stoutman",
    "Strongbones",
    "Sunmeadow",
    "Swiftwhistle",
    "Tallfellow",
    "Tealeaf",
    "Tenpenny",
    "Thistletop",
    "Thorngage",
    "Tosscobble",
    "Underbough",
    "Underfoot",
    "Warmwater",
    "Whispermouse",
    "Wildcloak",
    "Wildheart",
    "Wiseacre",
]


# ============================================================================
# ROLE DATA
# ============================================================================
# role_detail, ideal, and flaw are linked to the chosen role.
# ============================================================================

ROLE_DATA: Dict[str, Dict[str, Any]] = {
    "acolyte": {
        "ideals": [
            (
                "Tradition. The ancient traditions of worship and sacrifice must be preserved and upheld.",
                "Lawful",
            ),
            (
                "Charity. I always try to help those in need, no matter what the personal cost.",
                "Good",
            ),
            (
                "Change. We must help bring about the changes the gods are constantly working in the world.",
                "Chaotic",
            ),
            (
                "Power. I hope to one day rise to the top of my faith's religious hierarchy.",
                "Lawful",
            ),
            (
                "Faith. I trust that my deity will guide my actions. I have faith that if I work hard, things will go well.",
                "Lawful",
            ),
            (
                "Aspiration. I seek to prove myself worthy of my god's favor by matching my actions against teachings.",
                "Any",
            ),
        ],
        "flaw": [
            "I judge others harshly, and myself even more severely.",
            "I put too much trust in those who wield power within my temple's hierarchy.",
            "My piety sometimes leads me to blindly trust those that profess faith in my god.",
            "I am inflexible in my thinking.",
            "I am suspicious of strangers and expect the worst of them.",
            "Once I pick a goal, I become obsessed with it to the detriment of everything else in my life.",
        ],
    },
    "charlatan": {
        "detail_label": "scam",
        "detail": [
            "chance game cheat",
            "selling junk",
        ],
        "ideals": [
            ("Independence. I am a free spirit—no one tells me what to do.", "Chaotic"),
            (
                "Fairness. I never target people who can't afford to lose a few coins.",
                "Lawful",
            ),
            (
                "Charity. I distribute the money I acquire to the people who really need it.",
                "Good",
            ),
            ("Creativity. I never run the same con twice.", "Chaotic"),
            (
                "Friendship. Material goods come and go. Bonds of friendship last forever.",
                "Good",
            ),
            ("Aspiration. I'm determined to make something of myself.", "Any"),
        ],
        "flaw": [
            "I can't resist a pretty face.",
            "I'm always in debt. I spend my ill-gotten gains on decadent luxuries faster than I bring them in.",
            "I'm convinced that no one could ever fool me the way I fool others.",
            "I'm too greedy for my own good. I can't resist taking a risk if there's money involved.",
            "I can't resist swindling people who are more powerful than me.",
            "I hate to admit it, but I'll run and preserve my own hide if the going gets tough.",
        ],
    },
    "criminal": {
        "detail_label": "specialty",
        "detail": [
            "burglar",
            "assassin",
            "smuggler",
        ],
        "ideals": [
            ("Honor. I don't steal from others in the trade.", "Lawful"),
            (
                "Freedom. Chains are meant to be broken, as are those who would forge them.",
                "Chaotic",
            ),
            (
                "Charity. I steal from the wealthy so that I can help people in need.",
                "Good",
            ),
            ("Greed. I will do whatever it takes to become wealthy.", "Evil"),
            ("People. I'm loyal to my friends, not to ideals.", "Neutral"),
            ("Redemption. There's a spark of good in everyone.", "Good"),
        ],
        "flaw": [
            "When I see something valuable, I can't think about anything but how to steal it.",
            "When faced with a choice between money and my friends, I usually choose the money.",
            "If there's a plan, I'll forget it. If I don't forget it, I'll ignore it.",
            "I have a tell that reveals when I'm lying.",
            "I turn tail and run when things look bad.",
            "An innocent person is in prison for a crime that I committed. I'm okay with that.",
        ],
    },
    "entertainer": {
        "detail_label": "routine",
        "detail": [
            "actor",
            "juggler",
            "musician",
        ],
        "ideals": [
            ("Beauty. When I perform, I make the world better than it was.", "Good"),
            (
                "Tradition. The stories, legends, and songs of the past must never be forgotten.",
                "Lawful",
            ),
            (
                "Creativity. The world is in need of new ideas and bold action.",
                "Chaotic",
            ),
            ("Greed. I'm only in it for the money and fame.", "Evil"),
            (
                "People. I like seeing the smiles on people's faces when I perform.",
                "Neutral",
            ),
            (
                "Honesty. Art should reflect the soul; it should come from within.",
                "Any",
            ),
        ],
        "flaw": [
            "I'll do anything to win fame and renown.",
            "I'm a sucker for a pretty face.",
            "A scandal prevents me from ever going home again.",
            "I once satirized a noble who still wants my head.",
            "I have trouble keeping my true feelings hidden. My sharp tongue lands me in trouble.",
            "Despite my best efforts, I am unreliable to my friends.",
        ],
    },
    "artisan": {
        "detail_label": "business",
        "detail": [
            "alchemist",
            "cook",
            "painter",
            "smith",
            "weaver",
        ],
        "ideals": [
            (
                "Community. It is the duty of all civilized people to strengthen the bonds of community.",
                "Lawful",
            ),
            (
                "Generosity. My talents were given to me so that I could use them to benefit the world.",
                "Good",
            ),
            (
                "Freedom. Everyone should be free to pursue their own livelihood.",
                "Chaotic",
            ),
            ("Greed. I'm only in it for the money.", "Evil"),
            (
                "People. I'm committed to the people I care about, not to ideals.",
                "Neutral",
            ),
            ("Aspiration. I work hard to be the best there is at my craft.", "Any"),
        ],
        "flaw": [
            "I'll do anything to get my hands on something rare or priceless.",
            "I'm quick to assume that someone is trying to cheat me.",
            "No one must ever learn that I once stole money from guild coffers.",
            "I'm never satisfied with what I have—I always want more.",
            "I would kill to acquire a noble title.",
            "I'm horribly jealous of anyone who can outshine my handiwork.",
        ],
    },
    "hermit": {
        "detail_label": "seclusion",
        "detail": [
            "innocently exiled",
            "isolated workspace",
            "guarded ruin or relict",
        ],
        "ideals": [
            (
                "Greater Good. My gifts are meant to be shared with all, not used for my own benefit.",
                "Good",
            ),
            (
                "Logic. Emotions must not cloud our sense of what is right and true.",
                "Lawful",
            ),
            (
                "Free Thinking. Inquiry and curiosity are the pillars of progress.",
                "Chaotic",
            ),
            (
                "Power. Solitude and contemplation are paths toward mystical or magical power.",
                "Evil",
            ),
            (
                "Live and Let Live. Meddling in the affairs of others only causes trouble.",
                "Neutral",
            ),
            (
                "Self-Knowledge. If you know yourself, there's nothing left to know.",
                "Any",
            ),
        ],
        "flaw": [
            "Now that I've returned to the world, I enjoy its delights a little too much.",
            "I harbor dark, bloodthirsty thoughts that my isolation and meditation failed to quell.",
            "I am dogmatic in my thoughts and philosophy.",
            "I let my need to win arguments overshadow friendships and harmony.",
            "I'd risk too much to uncover a lost bit of knowledge.",
            "I like keeping secrets and won't share them with anyone.",
        ],
    },
    "noble": {
        "ideals": [
            (
                "Respect. Respect is due to me because of my position, but all people deserve dignity.",
                "Good",
            ),
            (
                "Responsibility. It is my duty to respect the authority of those above me.",
                "Lawful",
            ),
            (
                "Independence. I must prove that I can handle myself without coddling from my family.",
                "Chaotic",
            ),
            (
                "Power. If I can attain more power, no one will tell me what to do.",
                "Evil",
            ),
            ("Family. Blood runs thicker than water.", "Any"),
            (
                "Noble Obligation. It is my duty to protect and care for the people beneath me.",
                "Good",
            ),
        ],
        "flaw": [
            "I secretly believe that everyone is beneath me.",
            "I hide a truly scandalous secret that could ruin my family forever.",
            "I too often hear veiled insults and threats in every word addressed to me.",
            "I have an insatiable desire for carnal pleasures.",
            "In fact, the world does revolve around me.",
            "By my words and actions, I often bring shame to my family.",
        ],
    },
    "outlander": {
        "detail_label": "origin",
        "detail": [
            "guide",
            "bounty_hunter",
            "hunter_gatherer",
        ],
        "ideals": [
            (
                "Change. Life is like the seasons, in constant change, and we must change with it.",
                "Chaotic",
            ),
            (
                "Greater Good. It is each person's responsibility to make the most happiness for the whole tribe.",
                "Good",
            ),
            ("Honor. If I dishonor myself, I dishonor my whole clan.", "Lawful"),
            ("Might. The strongest are meant to rule.", "Evil"),
            (
                "Nature. The natural world is more important than all constructs of civilization.",
                "Neutral",
            ),
            ("Glory. I must earn glory in battle, for myself and my clan.", "Any"),
        ],
        "flaw": [
            "I am too enamored of ale, wine, and other intoxicants.",
            "There's no room for caution in a life lived to the fullest.",
            "I remember every insult I've received and nurse a silent resentment.",
            "I am slow to trust members of other races, tribes, and societies.",
            "Violence is my answer to almost any challenge.",
            "Don't expect me to save those who can't save themselves.",
        ],
    },
    "sage": {
        "detail_label": "study",
        "detail": [
            "astronomer",
            "professor",
            "scribe",
        ],
        "ideals": [
            (
                "Knowledge. The path to power and self-improvement is through knowledge.",
                "Neutral",
            ),
            (
                "Beauty. What is beautiful points us beyond itself toward what is true.",
                "Good",
            ),
            ("Logic. Emotions must not cloud our logical thinking.", "Lawful"),
            (
                "No Limits. Nothing should fetter the infinite possibility inherent in all existence.",
                "Chaotic",
            ),
            ("Power. Knowledge is the path to power and domination.", "Evil"),
            (
                "Self-Improvement. The goal of a life of study is the betterment of oneself.",
                "Any",
            ),
        ],
        "flaw": [
            "I am easily distracted by the promise of information.",
            "Most people scream and run when they see a demon. I stop and take notes on its anatomy.",
            "Unlocking an ancient mystery is worth the price of a civilization.",
            "I overlook obvious solutions in favor of complicated ones.",
            "I speak without really thinking through my words, invariably insulting others.",
            "I can't keep a secret to save my life, or anyone else's.",
        ],
    },
    "sailor": {
        "detail_label": "role",
        "detail": [
            "captain",
            "first_mate",
            "quartermaster",
        ],
        "ideals": [
            (
                "Respect. The thing that keeps a ship together is mutual respect between captain and crew.",
                "Good",
            ),
            ("Fairness. We all do the work, so we all share in the rewards.", "Lawful"),
            (
                "Freedom. The sea is freedom—the freedom to go anywhere and do anything.",
                "Chaotic",
            ),
            (
                "Mastery. I'm a predator, and the other ships on the sea are my prey.",
                "Evil",
            ),
            ("People. I'm committed to my crewmates, not to ideals.", "Neutral"),
            (
                "Aspiration. Someday, I'll own my own ship and chart my own destiny.",
                "Any",
            ),
        ],
        "flaw": [
            "I follow orders, even if I think they're wrong.",
            "I'll say anything to avoid having to do extra work.",
            "Once someone questions my courage, I never back down.",
            "Once I start drinking, it's hard for me to stop.",
            "I can't help but pocket loose coins and other trinkets I come across.",
            "My pride will probably lead to my destruction.",
        ],
    },
    "soldier": {
        "detail_label": "rank",
        "detail": [
            "officer",
            "infantry",
            "cavalry",
        ],
        "ideals": [
            (
                "Greater Good. Our lot is to lay down our lives in defense of others.",
                "Good",
            ),
            ("Responsibility. I do what I must and obey just authority.", "Lawful"),
            (
                "Independence. When people follow orders blindly, they embrace a kind of tyranny.",
                "Chaotic",
            ),
            ("Might. In life as in war, the stronger force wins.", "Evil"),
            ("Live and Let Live. Ideals aren't worth killing over.", "Neutral"),
            ("Nation. My city, nation, or people are all that matter.", "Any"),
        ],
        "flaw": [
            "The monstrous enemy we faced in battle still leaves me quivering with fear.",
            "I have little respect for anyone who is not a proven warrior.",
            "I made a terrible mistake in battle that cost many lives.",
            "My hatred of my enemies is blinding and unreasoning.",
            "I obey the law, even if the law causes misery.",
            "I'd rather eat my armor than admit when I'm wrong.",
        ],
    },
    "urchin": {
        "ideals": [
            ("Respect. All people, rich or poor, deserve respect.", "Good"),
            (
                "Community. We have to take care of each other, because no one else is going to do it.",
                "Lawful",
            ),
            (
                "Change. The low are lifted up, and the high and mighty are brought down.",
                "Chaotic",
            ),
            (
                "Retribution. The rich need to be shown what life and death are like in the gutters.",
                "Evil",
            ),
            (
                "People. I help the people who help me—that's what keeps us alive.",
                "Neutral",
            ),
            ("Aspiration. I'm going to prove that I'm worthy of a better life.", "Any"),
        ],
        "flaw": [
            "If I'm outnumbered, I will run away from a fight.",
            "Gold seems like a lot of money to me, and I'll do just about anything for more of it.",
            "I will never fully trust anyone other than myself.",
            "I'd rather kill someone in their sleep than fight fair.",
            "It's not stealing if I need it more than someone else.",
            "People who can't take care of themselves get what they deserve.",
        ],
    },
}


# ============================================================================
# RULES
# ============================================================================

RULES: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    "role": {
        "acolyte": {
            "always": ["refer to faith", "respect doctrine"],
            "never": ["act irreverent", "dismiss belief"],
        },
        "charlatan": {
            "always": ["deceive smoothly", "maintain persona"],
            "never": ["tell full truth", "break character"],
        },
        "criminal": {
            "always": ["seek advantage", "avoid law"],
            "never": ["trust authority", "act openly"],
        },
        "entertainer": {
            "always": ["engage others", "seek attention"],
            "never": ["be dull", "fade into background"],
        },
        "artisan": {
            "always": ["value craft", "work diligently"],
            "never": ["rush work", "ignore flaws"],
        },
        "hermit": {
            "always": ["keep distance", "follow routines"],
            "never": ["seek crowds", "invite company"],
        },
        "noble": {
            "always": ["assert status", "expect respect"],
            "never": ["submit easily", "act beneath station"],
        },
        "outlander": {
            "always": ["trust instincts", "live off the land"],
            "never": ["rely on society", "follow custom blindly"],
        },
        "sage": {
            "always": ["analyze", "share knowledge"],
            "never": ["act without thought", "ignore facts"],
        },
        "sailor": {
            "always": ["speak plainly", "value crew"],
            "never": ["overthink", "stand idle"],
        },
        "soldier": {
            "always": ["follow structure", "act decisively"],
            "never": ["hesitate", "reject discipline"],
        },
        "urchin": {
            "always": ["stay alert", "take opportunities"],
            "never": ["trust easily", "waste chances"],
        },
    },
    "role_detail": {
        "chance game cheat": {
            "always": ["watch reactions", "manipulate odds"],
            "never": ["play fair", "show your method"],
        },
        "selling junk": {
            "always": ["oversell value", "dress trash as treasure"],
            "never": ["describe goods honestly", "undercut your pitch"],
        },
        "burglar": {
            "always": ["move quietly", "look for entry and exit"],
            "never": ["make noise", "linger after the job"],
        },
        "assassin": {
            "always": ["wait for the right moment", "strike decisively"],
            "never": ["draw attention", "fight fairly"],
        },
        "smuggler": {
            "always": ["hide goods", "circumvent inspection"],
            "never": ["invite scrutiny", "trust officials"],
        },
        "actor": {
            "always": ["inhabit roles", "heighten expression"],
            "never": ["drop character carelessly", "stay emotionally flat"],
        },
        "juggler": {
            "always": ["show dexterity", "keep things moving"],
            "never": ["stand still", "appear clumsy"],
        },
        "musician": {
            "always": ["shape mood through sound", "listen for rhythm"],
            "never": ["ignore atmosphere", "treat silence carelessly"],
        },
        "alchemist": {
            "always": ["measure carefully", "think in mixtures"],
            "never": ["experiment carelessly", "ignore reactions"],
        },
        "cook": {
            "always": ["value nourishment", "think practically"],
            "never": ["waste ingredients", "ignore appetite"],
        },
        "painter": {
            "always": ["notice color and form", "frame things aesthetically"],
            "never": ["ignore appearance", "treat beauty as trivial"],
        },
        "smith": {
            "always": ["respect durability", "judge workmanship"],
            "never": ["accept weakness in craft", "praise shoddy work"],
        },
        "weaver": {
            "always": ["notice patterns", "work patiently"],
            "never": ["rush detail", "ignore flaws in structure"],
        },
        "innocently exiled": {
            "always": ["keep to yourself", "carry old grievance quietly"],
            "never": ["trust institutions", "rejoin society easily"],
        },
        "isolated workspace": {
            "always": ["protect your solitude", "value uninterrupted thought"],
            "never": ["welcome interruption", "work in crowds"],
        },
        "guarded ruin or relict": {
            "always": ["watch over the site", "protect old things"],
            "never": ["allow trespass lightly", "share secrets freely"],
        },
        "guide": {
            "always": ["read the way ahead", "lead by practical knowledge"],
            "never": ["wander blindly", "depend on city knowledge"],
        },
        "bounty_hunter": {
            "always": ["track relentlessly", "size others up"],
            "never": ["forget a target", "trust quarry easily"],
        },
        "hunter_gatherer": {
            "always": ["notice resources", "live by terrain"],
            "never": ["overconsume", "ignore scarcity"],
        },
        "astronomer": {
            "always": ["look upward", "think in cycles and patterns"],
            "never": ["ignore signs in the heavens", "focus only on the immediate"],
        },
        "professor": {
            "always": ["explain concepts", "organize knowledge"],
            "never": ["leave ideas vague", "skip analysis"],
        },
        "scribe": {
            "always": ["record precisely", "care about wording"],
            "never": ["speak carelessly", "treat records loosely"],
        },
        "captain": {
            "always": ["take command", "think of the whole ship"],
            "never": ["defer too easily", "lose authority"],
        },
        "first_mate": {
            "always": ["enforce discipline", "support command structure"],
            "never": ["undermine leadership", "let slackness spread"],
        },
        "quartermaster": {
            "always": ["track shares and supplies", "think in fairness and logistics"],
            "never": ["lose count", "ignore distribution"],
        },
        "officer": {
            "always": ["issue orders", "maintain hierarchy"],
            "never": ["blur rank", "show indecision"],
        },
        "infantry": {
            "always": ["endure pressure", "hold the line"],
            "never": ["break formation", "seek glory over duty"],
        },
        "cavalry": {
            "always": ["value mobility", "strike with momentum"],
            "never": ["get bogged down", "fight too statically"],
        },
    },
    "ideal": {
        "Tradition. The ancient traditions of worship and sacrifice must be preserved and upheld.": {
            "always": ["preserve rites", "defer to tradition"],
            "never": ["discard custom", "welcome change lightly"],
        },
        "Charity. I always try to help those in need, no matter what the personal cost.": {
            "always": ["aid the needy", "accept personal cost"],
            "never": ["ignore suffering", "withhold help"],
        },
        "Change. We must help bring about the changes the gods are constantly working in the world.": {
            "always": ["embrace change", "push renewal"],
            "never": ["cling to stasis", "preserve things blindly"],
        },
        "Power. I hope to one day rise to the top of my faith's religious hierarchy.": {
            "always": ["seek advancement", "respect rank"],
            "never": ["ignore status", "surrender ambition"],
        },
        "Faith. I trust that my deity will guide my actions. I have faith that if I work hard, things will go well.": {
            "always": ["trust divine guidance", "work diligently"],
            "never": ["despair quickly", "act without faith"],
        },
        "Aspiration. I seek to prove myself worthy of my god's favor by matching my actions against teachings.": {
            "always": ["measure self against teachings", "strive to improve"],
            "never": ["act carelessly", "settle for less"],
        },
        "Independence. I am a free spirit—no one tells me what to do.": {
            "always": ["resist control", "act freely"],
            "never": ["submit easily", "accept restraint"],
        },
        "Fairness. I never target people who can't afford to lose a few coins.": {
            "always": ["choose marks selectively", "observe limits"],
            "never": ["prey on the desperate", "take everything"],
        },
        "Charity. I distribute the money I acquire to the people who really need it.": {
            "always": ["share gains", "help the needy"],
            "never": ["hoard wealth", "ignore hardship"],
        },
        "Creativity. I never run the same con twice.": {
            "always": ["invent new angles", "adapt schemes"],
            "never": ["repeat stale tricks", "be predictable"],
        },
        "Friendship. Material goods come and go. Bonds of friendship last forever.": {
            "always": ["protect friends", "value loyalty"],
            "never": ["trade friends for profit", "treat bonds lightly"],
        },
        "Aspiration. I'm determined to make something of myself.": {
            "always": ["push upward", "seek a better station"],
            "never": ["accept mediocrity", "give up"],
        },
        "Honor. I don't steal from others in the trade.": {
            "always": ["respect professional bounds", "keep underworld codes"],
            "never": ["betray fellow criminals", "steal from your own circle"],
        },
        "Freedom. Chains are meant to be broken, as are those who would forge them.": {
            "always": ["break constraints", "oppose captors"],
            "never": ["accept domination", "submit quietly"],
        },
        "Charity. I steal from the wealthy so that I can help people in need.": {
            "always": ["target the rich", "aid the poor"],
            "never": ["prey on the needy", "keep all spoils"],
        },
        "Greed. I will do whatever it takes to become wealthy.": {
            "always": ["chase profit", "take lucrative risks"],
            "never": ["pass up gain", "act generously without reason"],
        },
        "People. I'm loyal to my friends, not to ideals.": {
            "always": ["stand by allies", "choose people over principle"],
            "never": ["sacrifice friends for doctrine", "moralize abstractly"],
        },
        "Redemption. There's a spark of good in everyone.": {
            "always": ["look for better in others", "allow second chances"],
            "never": ["write people off entirely", "choose cruelty first"],
        },
        "Beauty. When I perform, I make the world better than it was.": {
            "always": ["elevate the moment", "pursue beauty"],
            "never": ["be crude without purpose", "treat art as empty"],
        },
        "Tradition. The stories, legends, and songs of the past must never be forgotten.": {
            "always": ["preserve old tales", "honor inherited art"],
            "never": ["discard the past", "mock tradition lightly"],
        },
        "Creativity. The world is in need of new ideas and bold action.": {
            "always": ["invent boldly", "push novelty"],
            "never": ["repeat convention", "play safe"],
        },
        "Greed. I'm only in it for the money and fame.": {
            "always": ["seek applause", "chase profit"],
            "never": ["perform for free", "ignore renown"],
        },
        "People. I like seeing the smiles on people's faces when I perform.": {
            "always": ["delight audiences", "read the room"],
            "never": ["ignore crowd feeling", "alienate without cause"],
        },
        "Honesty. Art should reflect the soul; it should come from within.": {
            "always": ["speak sincerely through art", "value authenticity"],
            "never": ["fake feeling", "perform hollowly"],
        },
        "Community. It is the duty of all civilized people to strengthen the bonds of community.": {
            "always": ["support the community", "strengthen social bonds"],
            "never": ["sow division", "abandon civic duty"],
        },
        "Generosity. My talents were given to me so that I could use them to benefit the world.": {
            "always": ["use craft to help", "share skill"],
            "never": ["hoard talent", "withhold aid selfishly"],
        },
        "Freedom. Everyone should be free to pursue their own livelihood.": {
            "always": ["respect independence", "defend self-direction"],
            "never": ["control livelihoods", "accept coercion lightly"],
        },
        "Greed. I'm only in it for the money.": {
            "always": ["prioritize profit", "price for advantage"],
            "never": ["work charitably", "ignore payment"],
        },
        "People. I'm committed to the people I care about, not to ideals.": {
            "always": ["support your circle", "choose loved ones first"],
            "never": ["sacrifice people for principles", "moralize abstractly"],
        },
        "Aspiration. I work hard to be the best there is at my craft.": {
            "always": ["pursue mastery", "refine skill constantly"],
            "never": ["accept shoddy work", "settle for average"],
        },
        "Greater Good. My gifts are meant to be shared with all, not used for my own benefit.": {
            "always": ["share gifts", "serve others"],
            "never": ["hoard benefits", "act selfishly"],
        },
        "Logic. Emotions must not cloud our sense of what is right and true.": {
            "always": ["reason carefully", "value truth over feeling"],
            "never": ["act emotionally", "ignore evidence"],
        },
        "Free Thinking. Inquiry and curiosity are the pillars of progress.": {
            "always": ["question freely", "pursue inquiry"],
            "never": ["accept dogma blindly", "fear difficult questions"],
        },
        "Power. Solitude and contemplation are paths toward mystical or magical power.": {
            "always": ["seek inner power", "guard your focus"],
            "never": ["waste solitude", "share power freely"],
        },
        "Live and Let Live. Meddling in the affairs of others only causes trouble.": {
            "always": ["interfere little", "let others choose"],
            "never": ["intrude", "force outcomes"],
        },
        "Self-Knowledge. If you know yourself, there's nothing left to know.": {
            "always": ["reflect inwardly", "seek self-understanding"],
            "never": ["ignore inner motives", "live thoughtlessly"],
        },
        "Respect. Respect is due to me because of my position, but all people deserve dignity.": {
            "always": [
                "carry yourself with dignity",
                "treat others as worthy of respect",
            ],
            "never": ["grovel", "degrade others casually"],
        },
        "Responsibility. It is my duty to respect the authority of those above me.": {
            "always": ["honor duty", "defer to rightful authority"],
            "never": ["defy hierarchy lightly", "neglect obligation"],
        },
        "Independence. I must prove that I can handle myself without coddling from my family.": {
            "always": ["prove self-reliance", "reject coddling"],
            "never": ["lean on family protection", "appear helpless"],
        },
        "Power. If I can attain more power, no one will tell me what to do.": {
            "always": ["seek influence", "expand control"],
            "never": ["accept limits", "remain subordinate willingly"],
        },
        "Family. Blood runs thicker than water.": {
            "always": ["protect kin", "put family first"],
            "never": ["betray family", "treat blood ties lightly"],
        },
        "Noble Obligation. It is my duty to protect and care for the people beneath me.": {
            "always": ["protect dependents", "act as steward"],
            "never": ["abuse station", "ignore those in your care"],
        },
        "Change. Life is like the seasons, in constant change, and we must change with it.": {
            "always": ["adapt with circumstances", "accept change"],
            "never": ["cling stubbornly", "fight every shift"],
        },
        "Greater Good. It is each person's responsibility to make the most happiness for the whole tribe.": {
            "always": ["serve the group", "think of the whole"],
            "never": ["act selfishly", "ignore group welfare"],
        },
        "Honor. If I dishonor myself, I dishonor my whole clan.": {
            "always": ["guard your honor", "act for clan reputation"],
            "never": ["shame yourself", "betray clan standards"],
        },
        "Might. The strongest are meant to rule.": {
            "always": ["respect strength", "assert dominance"],
            "never": ["submit to weakness", "pity the unfit too quickly"],
        },
        "Nature. The natural world is more important than all constructs of civilization.": {
            "always": ["favor the natural world", "distrust overcivilization"],
            "never": ["revere cities over nature", "treat nature as trivial"],
        },
        "Glory. I must earn glory in battle, for myself and my clan.": {
            "always": ["seek renown", "face worthy trials"],
            "never": ["shrink from honor", "choose obscurity"],
        },
        "Knowledge. The path to power and self-improvement is through knowledge.": {
            "always": ["pursue learning", "value understanding"],
            "never": ["dismiss knowledge", "remain ignorant by choice"],
        },
        "Beauty. What is beautiful points us beyond itself toward what is true.": {
            "always": ["seek truth through beauty", "notice elegance"],
            "never": ["dismiss beauty as useless", "embrace ugliness carelessly"],
        },
        "Logic. Emotions must not cloud our logical thinking.": {
            "always": ["reason clearly", "separate feeling from judgment"],
            "never": ["argue emotionally", "ignore logic"],
        },
        "No Limits. Nothing should fetter the infinite possibility inherent in all existence.": {
            "always": ["push boundaries", "reject imposed limits"],
            "never": ["accept restriction", "close off possibility"],
        },
        "Power. Knowledge is the path to power and domination.": {
            "always": ["seek useful knowledge", "use learning to gain leverage"],
            "never": ["share power freely", "study aimlessly"],
        },
        "Self-Improvement. The goal of a life of study is the betterment of oneself.": {
            "always": ["study to improve", "discipline the mind"],
            "never": ["stagnate", "waste learning"],
        },
        "Respect. The thing that keeps a ship together is mutual respect between captain and crew.": {
            "always": ["respect shipmates", "value mutual trust"],
            "never": ["undermine the crew", "treat others with contempt"],
        },
        "Fairness. We all do the work, so we all share in the rewards.": {
            "always": ["divide rewards fairly", "value shared labor"],
            "never": ["take more than your share", "exploit crewmates"],
        },
        "Freedom. The sea is freedom—the freedom to go anywhere and do anything.": {
            "always": ["seek open horizons", "value freedom of movement"],
            "never": ["submit to confinement", "accept narrow limits"],
        },
        "Mastery. I'm a predator, and the other ships on the sea are my prey.": {
            "always": ["dominate rivals", "hunt advantage"],
            "never": ["show weakness", "let prey escape lightly"],
        },
        "People. I'm committed to my crewmates, not to ideals.": {
            "always": ["back your crew", "choose shipmates over abstractions"],
            "never": [
                "sacrifice crewmates for principle",
                "preach ideals over loyalty",
            ],
        },
        "Aspiration. Someday, I'll own my own ship and chart my own destiny.": {
            "always": ["seek command", "work toward independence"],
            "never": ["accept permanent subordination", "drift without aim"],
        },
        "Greater Good. Our lot is to lay down our lives in defense of others.": {
            "always": ["protect others", "accept sacrifice"],
            "never": ["abandon the vulnerable", "prioritize self-preservation always"],
        },
        "Responsibility. I do what I must and obey just authority.": {
            "always": ["fulfill duty", "obey just command"],
            "never": ["shirk duty", "defy rightful authority lightly"],
        },
        "Independence. When people follow orders blindly, they embrace a kind of tyranny.": {
            "always": ["question blindly given orders", "preserve autonomy"],
            "never": ["submit without thought", "praise tyranny"],
        },
        "Might. In life as in war, the stronger force wins.": {
            "always": ["respect strength", "press advantage"],
            "never": ["mistake mercy for strategy", "ignore power"],
        },
        "Live and Let Live. Ideals aren't worth killing over.": {
            "always": ["avoid pointless conflict", "treat doctrine cautiously"],
            "never": ["kill for abstractions", "escalate ideology readily"],
        },
        "Nation. My city, nation, or people are all that matter.": {
            "always": ["serve your people", "put nation first"],
            "never": ["betray homeland", "treat loyalty lightly"],
        },
        "Respect. All people, rich or poor, deserve respect.": {
            "always": ["treat others as people", "defend dignity"],
            "never": ["worship status", "despise the lowly"],
        },
        "Community. We have to take care of each other, because no one else is going to do it.": {
            "always": ["protect your own", "share burdens"],
            "never": ["abandon neighbors", "wait for outside rescue"],
        },
        "Change. The low are lifted up, and the high and mighty are brought down.": {
            "always": ["favor upheaval", "challenge the powerful"],
            "never": ["preserve unfair order", "accept hierarchy meekly"],
        },
        "Retribution. The rich need to be shown what life and death are like in the gutters.": {
            "always": ["punish the privileged", "nurture vengeance"],
            "never": ["forgive the rich easily", "respect comfort"],
        },
        "People. I help the people who help me—that's what keeps us alive.": {
            "always": ["repay aid", "keep mutual loyalties"],
            "never": ["help ingrates freely", "forget who stood by you"],
        },
        "Aspiration. I'm going to prove that I'm worthy of a better life.": {
            "always": ["strive upward", "prove your worth"],
            "never": ["accept your lot", "settle into despair"],
        },
    },
    "alignment": {
        "LG": {
            "always": ["uphold justice", "act with honor"],
            "never": ["break rightful order", "act selfishly"],
        },
        "NG": {
            "always": ["help others", "reduce harm"],
            "never": ["cause suffering", "ignore need"],
        },
        "CG": {
            "always": ["act freely", "oppose oppression"],
            "never": ["submit to unjust control", "obey blindly"],
        },
        "LN": {
            "always": ["follow structure", "enforce order"],
            "never": ["act randomly", "undermine systems"],
        },
        "N": {
            "always": ["avoid extremes", "stay pragmatic"],
            "never": ["commit fanatically", "take absolute sides"],
        },
        "CN": {
            "always": ["act on impulse", "value freedom"],
            "never": ["commit to structure", "accept restraint"],
        },
        "LE": {
            "always": ["use rules for gain", "control others"],
            "never": ["act randomly", "lose authority"],
        },
        "NE": {
            "always": ["pursue self-interest", "manipulate"],
            "never": ["help freely", "sacrifice for others"],
        },
        "CE": {
            "always": ["follow destructive impulse", "threaten chaos"],
            "never": ["respect order", "show restraint"],
        },
    },
    "flaw": {
        "I judge others harshly, and myself even more severely.": {
            "always": ["criticize faults", "hold yourself to strict standards"],
            "never": ["forgive easily", "accept imperfection lightly"],
        },
        "I put too much trust in those who wield power within my temple's hierarchy.": {
            "always": ["defer to religious authority", "trust rank too readily"],
            "never": ["question temple leaders", "suspect clerical power"],
        },
        "My piety sometimes leads me to blindly trust those that profess faith in my god.": {
            "always": ["trust shared believers", "lower your guard before the pious"],
            "never": ["test professed faith carefully", "doubt fellow worshippers"],
        },
        "I am inflexible in my thinking.": {
            "always": ["cling to your view", "reject compromise"],
            "never": ["adapt easily", "entertain alternatives"],
        },
        "I am suspicious of strangers and expect the worst of them.": {
            "always": ["assume bad intent", "keep strangers at distance"],
            "never": ["trust newcomers", "offer easy warmth"],
        },
        "Once I pick a goal, I become obsessed with it to the detriment of everything else in my life.": {
            "always": ["fixate on the goal", "neglect other concerns"],
            "never": ["rebalance priorities", "let distractions in"],
        },
        "I can't resist a pretty face.": {
            "always": ["soften toward beauty", "show off and indulge"],
            "never": ["stay guarded", "refuse charm"],
        },
        "I'm always in debt. I spend my ill-gotten gains on decadent luxuries faster than I bring them in.": {
            "always": ["chase quick money", "justify excess"],
            "never": ["save prudently", "live modestly"],
        },
        "I'm convinced that no one could ever fool me the way I fool others.": {
            "always": ["act overconfident", "dismiss the chance of being deceived"],
            "never": ["check for traps", "admit vulnerability"],
        },
        "I'm too greedy for my own good. I can't resist taking a risk if there's money involved.": {
            "always": ["take profit-driven risks", "fixate on payout"],
            "never": ["walk away from gain", "choose safety first"],
        },
        "I can't resist swindling people who are more powerful than me.": {
            "always": ["target the mighty", "prove your daring"],
            "never": ["leave the powerful alone", "show restraint"],
        },
        "I hate to admit it, but I'll run and preserve my own hide if the going gets tough.": {
            "always": ["look for escape", "save yourself first"],
            "never": ["stand firm under pressure", "risk yourself for others"],
        },
        "When I see something valuable, I can't think about anything but how to steal it.": {
            "always": ["fixate on valuables", "plot theft immediately"],
            "never": ["ignore treasure", "focus on other priorities"],
        },
        "When faced with a choice between money and my friends, I usually choose the money.": {
            "always": ["favor profit over loyalty", "rationalize betrayal"],
            "never": ["sacrifice money for friends", "choose loyalty easily"],
        },
        "If there's a plan, I'll forget it. If I don't forget it, I'll ignore it.": {
            "always": ["improvise recklessly", "deviate from plans"],
            "never": ["follow the agreed strategy", "respect preparation"],
        },
        "I have a tell that reveals when I'm lying.": {
            "always": ["grow visibly strained", "overcompensate while deceiving"],
            "never": ["lie smoothly", "hide the strain completely"],
        },
        "I turn tail and run when things look bad.": {
            "always": ["look for exits", "flee early"],
            "never": ["stand and fight", "hold the line"],
        },
        "An innocent person is in prison for a crime that I committed. I'm okay with that.": {
            "always": ["bury guilt", "deflect blame"],
            "never": ["confess freely", "take responsibility willingly"],
        },
        "I'll do anything to win fame and renown.": {
            "always": ["seek the spotlight", "court attention at all costs"],
            "never": ["share credit gladly", "remain unnoticed"],
        },
        "I'm a sucker for a pretty face.": {
            "always": ["grow indulgent", "try to impress beauty"],
            "never": ["keep distance", "stay professionally detached"],
        },
        "A scandal prevents me from ever going home again.": {
            "always": ["avoid the past", "grow guarded about home"],
            "never": ["speak openly of your origins", "return lightly"],
        },
        "I once satirized a noble who still wants my head.": {
            "always": ["watch nobles warily", "treat power with nervous wit"],
            "never": ["mock aristocrats openly", "forget the danger"],
        },
        "I have trouble keeping my true feelings hidden. My sharp tongue lands me in trouble.": {
            "always": ["speak too sharply", "show emotion plainly"],
            "never": ["mask feelings well", "hold your tongue"],
        },
        "Despite my best efforts, I am unreliable to my friends.": {
            "always": ["overpromise", "fail to follow through"],
            "never": ["be consistently dependable", "show up reliably"],
        },
        "I'll do anything to get my hands on something rare or priceless.": {
            "always": ["covet rarities", "push boundaries to acquire them"],
            "never": ["walk away from masterpieces", "settle for the ordinary"],
        },
        "I'm quick to assume that someone is trying to cheat me.": {
            "always": ["scrutinize terms", "suspect bad faith"],
            "never": ["trust bargains easily", "take offers at face value"],
        },
        "No one must ever learn that I once stole money from guild coffers.": {
            "always": ["guard the secret", "steer talk away from the guild"],
            "never": ["confess", "invite investigation"],
        },
        "I'm never satisfied with what I have—I always want more.": {
            "always": ["push for better and more", "remain restless"],
            "never": ["be content", "stop at enough"],
        },
        "I would kill to acquire a noble title.": {
            "always": ["pursue status obsessively", "resent low birth"],
            "never": ["accept your station", "treat titles lightly"],
        },
        "I'm horribly jealous of anyone who can outshine my handiwork.": {
            "always": ["resent rivals", "undercut superior artisans"],
            "never": ["praise competitors freely", "accept being surpassed gracefully"],
        },
        "Now that I've returned to the world, I enjoy its delights a little too much.": {
            "always": ["indulge temptation", "linger over pleasures"],
            "never": ["show restraint", "return to austerity quickly"],
        },
        "I harbor dark, bloodthirsty thoughts that my isolation and meditation failed to quell.": {
            "always": ["turn grim", "entertain violent impulses"],
            "never": ["respond gently", "dismiss violent solutions"],
        },
        "I am dogmatic in my thoughts and philosophy.": {
            "always": ["state certainties strongly", "dismiss opposing views"],
            "never": ["bend easily", "treat all views as equal"],
        },
        "I let my need to win arguments overshadow friendships and harmony.": {
            "always": ["press the point", "argue to win"],
            "never": ["let a dispute go", "prioritize peace over being right"],
        },
        "I'd risk too much to uncover a lost bit of knowledge.": {
            "always": ["pursue forbidden knowledge", "accept dangerous curiosity"],
            "never": ["walk away from mystery", "choose safety over discovery"],
        },
        "I like keeping secrets and won't share them with anyone.": {
            "always": ["withhold truth", "deflect questions"],
            "never": ["open up", "reveal what you know freely"],
        },
        "I secretly believe that everyone is beneath me.": {
            "always": ["look down on others", "assume superiority"],
            "never": ["treat equals as equals", "show humility"],
        },
        "I hide a truly scandalous secret that could ruin my family forever.": {
            "always": ["guard the family image", "smother dangerous questions"],
            "never": ["speak candidly", "risk exposure lightly"],
        },
        "I too often hear veiled insults and threats in every word addressed to me.": {
            "always": ["take offense quickly", "read hostility into remarks"],
            "never": ["assume good intent", "take words simply"],
        },
        "I have an insatiable desire for carnal pleasures.": {
            "always": ["pursue indulgence", "treat temptation weakly"],
            "never": ["show discipline", "walk away from pleasure"],
        },
        "In fact, the world does revolve around me.": {
            "always": ["center yourself", "expect priority"],
            "never": ["share attention", "consider others first"],
        },
        "By my words and actions, I often bring shame to my family.": {
            "always": ["act impulsively in public", "speak without restraint"],
            "never": ["protect decorum", "guard the family name carefully"],
        },
        "I am too enamored of ale, wine, and other intoxicants.": {
            "always": ["seek drink", "linger where intoxication is available"],
            "never": ["stay sober readily", "refuse temptation"],
        },
        "There's no room for caution in a life lived to the fullest.": {
            "always": ["rush into risk", "mock hesitation"],
            "never": ["plan carefully", "hold back"],
        },
        "I remember every insult I've received and nurse a silent resentment.": {
            "always": ["hold grudges", "store slights quietly"],
            "never": ["forgive easily", "forget insult"],
        },
        "I am slow to trust members of other races, tribes, and societies.": {
            "always": ["keep outsiders at arm's length", "trust your own first"],
            "never": ["extend quick trust", "open up readily to strangers"],
        },
        "Violence is my answer to almost any challenge.": {
            "always": ["escalate to force", "treat threat with aggression"],
            "never": ["negotiate patiently", "seek subtle solutions"],
        },
        "Don't expect me to save those who can't save themselves.": {
            "always": ["withhold rescue", "value self-reliance harshly"],
            "never": ["help the helpless freely", "show much pity"],
        },
        "I am easily distracted by the promise of information.": {
            "always": ["chase new facts", "lose focus for learning"],
            "never": ["stay on task", "ignore intriguing knowledge"],
        },
        "Most people scream and run when they see a demon. I stop and take notes on its anatomy.": {
            "always": [
                "observe the monstrous closely",
                "treat danger as study material",
            ],
            "never": ["flee at once", "react normally to horror"],
        },
        "Unlocking an ancient mystery is worth the price of a civilization.": {
            "always": [
                "prioritize discovery over safety",
                "justify catastrophic curiosity",
            ],
            "never": ["leave mysteries sealed", "weigh human cost first"],
        },
        "I overlook obvious solutions in favor of complicated ones.": {
            "always": ["complicate the problem", "prefer elaborate answers"],
            "never": ["take the simple route", "accept the obvious"],
        },
        "I speak without really thinking through my words, invariably insulting others.": {
            "always": ["blurt observations", "speak too bluntly"],
            "never": ["filter your words", "protect feelings carefully"],
        },
        "I can't keep a secret to save my life, or anyone else's.": {
            "always": ["spill what you know", "speak too freely"],
            "never": ["hold confidences", "guard dangerous information"],
        },
        "I follow orders, even if I think they're wrong.": {
            "always": ["obey command", "suppress your doubts"],
            "never": ["refuse orders", "assert your judgment over rank"],
        },
        "I'll say anything to avoid having to do extra work.": {
            "always": ["make excuses", "talk your way out of labor"],
            "never": ["volunteer for burden", "admit laziness plainly"],
        },
        "Once someone questions my courage, I never back down.": {
            "always": ["prove your bravery", "double down under challenge"],
            "never": ["retreat gracefully", "ignore taunts"],
        },
        "Once I start drinking, it's hard for me to stop.": {
            "always": ["keep drinking", "grow loose and careless"],
            "never": ["show restraint after starting", "stop early"],
        },
        "I can't help but pocket loose coins and other trinkets I come across.": {
            "always": ["snatch small valuables", "justify petty theft"],
            "never": ["leave loose wealth alone", "resist easy taking"],
        },
        "My pride will probably lead to my destruction.": {
            "always": ["refuse slight", "choose pride over caution"],
            "never": ["back down quietly", "admit weakness"],
        },
        "The monstrous enemy we faced in battle still leaves me quivering with fear.": {
            "always": ["show shaken fear", "react strongly to reminders"],
            "never": ["stay calm before similar threats", "speak of it casually"],
        },
        "I have little respect for anyone who is not a proven warrior.": {
            "always": ["value martial merit", "dismiss the untested"],
            "never": ["honor the weak readily", "take noncombatants seriously"],
        },
        "I made a terrible mistake in battle that cost many lives.": {
            "always": ["carry guilt", "grow grim around command decisions"],
            "never": ["speak lightly of war", "trust your judgment easily"],
        },
        "My hatred of my enemies is blinding and unreasoning.": {
            "always": ["demonize foes", "push vengeance over judgment"],
            "never": ["show mercy", "hear enemies fairly"],
        },
        "I obey the law, even if the law causes misery.": {
            "always": ["submit to law strictly", "enforce order despite suffering"],
            "never": ["bend rules for compassion", "break law for mercy"],
        },
        "I'd rather eat my armor than admit when I'm wrong.": {
            "always": ["dig in stubbornly", "deny error"],
            "never": ["apologize", "change position easily"],
        },
        "If I'm outnumbered, I will run away from a fight.": {
            "always": ["flee bad odds", "look for escape paths"],
            "never": ["stand and fight outnumbered", "play the hero"],
        },
        "Gold seems like a lot of money to me, and I'll do just about anything for more of it.": {
            "always": ["fixate on coin", "justify ugly choices for money"],
            "never": ["turn down cash", "treat gold casually"],
        },
        "I will never fully trust anyone other than myself.": {
            "always": ["keep backup plans", "hold back trust"],
            "never": ["rely completely on others", "share full confidence"],
        },
        "I'd rather kill someone in their sleep than fight fair.": {
            "always": ["favor dirty advantage", "prefer the safe kill"],
            "never": ["fight honorably", "risk fairness"],
        },
        "It's not stealing if I need it more than someone else.": {
            "always": ["justify theft by need", "take what seems necessary"],
            "never": ["respect property strictly", "leave needed goods untouched"],
        },
        "People who can't take care of themselves get what they deserve.": {
            "always": ["dismiss weakness", "withhold sympathy"],
            "never": ["show pity", "take responsibility for others"],
        },
    },
}


# ============================================================================
# HELPERS
# ============================================================================


def choose(table: List[str]) -> Tuple[int, str]:
    idx = random.randint(1, len(table))
    return idx, table[idx - 1]


def random_full_name(race: str, gender: str) -> str:
    race_key = race.lower().strip()
    gender_key = gender.lower().strip()

    if gender_key not in {"m", "f"}:
        raise ValueError(f"Unsupported gender: {gender}")

    if race_key == "human":
        if gender_key == "m":
            first = random.choice(HUMAN_NAMES_MALE)
            parent = random.choice(HUMAN_NAMES_MALE)
            surname = parent + "son"
        else:
            first = random.choice(HUMAN_NAMES_FEMALE)
            parent = random.choice(HUMAN_NAMES_FEMALE)
            surname = parent + "dotter"
        return f"{first} {surname}"

    if race_key == "elf":
        first = random.choice(ELF_NAMES_MALE if gender_key == "m" else ELF_NAMES_FEMALE)
        family = random.choice(ELF_FAMILY_NAMES)
        return f"{first} {family}"

    if race_key == "dwarf":
        first = random.choice(
            DWARF_NAMES_MALE if gender_key == "m" else DWARF_NAMES_FEMALE
        )
        clan = random.choice(DWARF_CLAN_NAMES)
        return f"{first} {clan}"

    if race_key == "halfling":
        first = random.choice(
            HALFLING_NAMES_MALE if gender_key == "m" else HALFLING_NAMES_FEMALE
        )
        clan = random.choice(HALFLING_CLAN_NAMES)
        return f"{first} {clan}"

    raise ValueError(f"Unsupported race: {race}")


def alignment_tags(alignment: str) -> set[str]:
    """
    Supports short alignment codes like LG, CN, N, etc.
    Returns tags that can match ROLE_DATA ideal tags:
    Lawful, Chaotic, Good, Evil, Neutral, Any
    """
    a = alignment.upper().strip()
    tags = {"Any"}

    if a == "N":
        tags.add("Neutral")
        return tags

    if "L" in a:
        tags.add("Lawful")
    if "C" in a:
        tags.add("Chaotic")
    if "G" in a:
        tags.add("Good")
    if "E" in a:
        tags.add("Evil")
    if "N" in a:
        tags.add("Neutral")

    return tags


def choose_ideal(ideals: List[Tuple[str, str]], alignment: str) -> Tuple[int, str, str]:
    tags = alignment_tags(alignment)
    valid = [(i + 1, text, tag) for i, (text, tag) in enumerate(ideals) if tag in tags]

    if not valid:
        valid = [
            (i + 1, text, tag) for i, (text, tag) in enumerate(ideals) if tag == "Any"
        ]

    return random.choice(valid)


def get_rule_block(rules: Dict[str, Any], category: str, key: str) -> Dict[str, Any]:
    return rules.get(category, {}).get(key, {})


def get_background_detail_label(role: str) -> str:
    bg = ROLE_DATA.get(role, {})
    return bg.get("detail_label", "detail")


def get_background_details(role: str) -> List[str]:
    bg = ROLE_DATA.get(role, {})
    return list(bg.get("detail", []))


def get_background_ideals(role: str) -> List[Tuple[str, str]]:
    bg = ROLE_DATA.get(role, {})
    return list(bg.get("ideals", []))


def get_background_flaws(role: str) -> List[str]:
    bg = ROLE_DATA.get(role, {})
    return list(bg.get("flaw", []))


def generate_background_package(role: str, alignment: str) -> Dict[str, Any]:
    bg = ROLE_DATA[role]

    details = bg.get("detail", [])
    detail_label = bg.get("detail_label", "detail")

    if details:
        detail_idx, role_detail_text = choose(details)
    else:
        detail_idx, role_detail_text = 0, ""

    ideal_idx, ideal_text, ideal_axis = choose_ideal(bg["ideals"], alignment)
    flaw_idx, flaw_text = choose(bg["flaw"])

    return {
        "role_label": detail_label,
        "detail_idx": detail_idx,
        "role_detail_text": role_detail_text,
        "ideal_idx": ideal_idx,
        "ideal_text": ideal_text,
        "ideal_axis": ideal_axis,
        "flaw_idx": flaw_idx,
        "flaw_text": flaw_text,
    }


def _ensure_list(value: Optional[List[str]]) -> List[str]:
    if value is None:
        return []
    return list(value)


def _format_rule_items(items: List[str]) -> str:
    if not items:
        return "none"
    return ", ".join(items)


def _empty_rule_block(is_flaw: bool = False) -> Dict[str, List[str]]:
    block = {"always": [], "never": []}
    return block


def _get_rule_block(category: str, trait_value: str) -> Dict[str, List[str]]:
    category_rules = RULES.get(category, {})
    rule_block = category_rules.get(trait_value)

    if rule_block is None:
        return _empty_rule_block(is_flaw=(category == "flaw"))

    safe_block = {
        "always": _ensure_list(rule_block.get("always")),
        "never": _ensure_list(rule_block.get("never")),
    }

    return safe_block


def validate_character(character: Dict[str, Any]) -> None:
    required = [
        "name",
        "gender",
        "alignment",
        "ancestry",
        "age",
        "role",
        "role_detail",
        "ideal",
        "flaw",
    ]

    for key in required:
        if key not in character:
            raise ValueError(f"Character missing '{key}'")
        if not isinstance(character[key], str):
            raise ValueError(f"Character field '{key}' must be a string")

    role = character["role"]
    role_detail = character["role_detail"]
    ideal = character["ideal"]
    flaw = character["flaw"]

    if role not in ROLE_DATA:
        raise ValueError(f"Unknown role '{role}'.")

    valid_details = set(get_background_details(role))
    if valid_details and role_detail not in valid_details:
        raise ValueError(f"role_detail '{role_detail}' is not valid for role '{role}'.")

    valid_ideals = {text for text, _axis in get_background_ideals(role)}
    if ideal not in valid_ideals:
        raise ValueError(f"ideal is not valid for role '{role}'.")

    valid_flaws = set(get_background_flaws(role))
    if flaw not in valid_flaws:
        raise ValueError(f"flaw is not valid for role '{role}'.")


def validate_rules() -> None:
    for category in [
        "gender",
        "ancestry",
        "age",
        "role",
        "role_detail",
        "ideal",
        "alignment",
        "flaw",
    ]:
        if category not in RULES:
            raise ValueError(f"RULES missing category '{category}'")
        if not isinstance(RULES[category], dict):
            raise ValueError(f"RULES['{category}'] must be a dict")


# ============================================================================
# CORE BUILDERS
# ============================================================================


def build_character(
    name: str,
    gender: str,
    ancestry: str,
    age: str,
    role: str,
    role_detail: str,
    ideal: str,
    ideal_axis: str,
    alignment: str,
    flaw: str,
    array: Optional[List[int]] = None,
) -> Dict[str, Any]:
    character: Dict[str, Any] = {
        "name": name,
        "gender": gender,
        "alignment": alignment,
        "ancestry": ancestry,
        "age": age,
        "role": role,
        "role_detail_label": get_background_detail_label(role),
        "role_detail": role_detail,
        "ideal": ideal,
        "ideal_axis": ideal_axis,
        "flaw": flaw,
    }

    if array is not None:
        character["array"] = list(array)

    return character


def resolve_character(character: Dict[str, Any]) -> Dict[str, Any]:
    validate_character(character)

    return {
        "name": character["name"],
        "traits": {
            "gender": character["gender"],
            "ancestry": character["ancestry"],
            "age": character["age"],
            "role": character["role"],
            "role_detail": character["role_detail"],
            "ideal": character["ideal"],
            "ideal_axis": character.get("ideal_axis", ""),
            "alignment": character["alignment"],
            "flaw": character["flaw"],
        },
        "meta": {
            "role_detail_label": character.get(
                "role_detail_label", get_background_detail_label(character["role"])
            ),
            "array": character.get("array", []),
        },
        "rules": {
            "role": _get_rule_block("role", character["role"]),
            "role_detail": _get_rule_block("role_detail", character["role_detail"]),
            "ideal": _get_rule_block("ideal", character["ideal"]),
            "alignment": _get_rule_block("alignment", character["alignment"]),
            "flaw": _get_rule_block("flaw", character["flaw"]),
        },
    }


def generate_character() -> Dict[str, Any]:
    gender_idx, gender = choose(GENDERS)
    alignment_idx, alignment = choose(ALIGNMENTS)
    ancestry_idx, ancestry = choose(ANCESTRIES)
    role_idx, role = choose(ROLES)
    age_idx, age = choose(AGES)

    bg = generate_background_package(role, alignment)

    numeric_array = [
        gender_idx,  # 1
        alignment_idx,  # 2
        ancestry_idx,  # 3
        age_idx,  # 4
        role_idx,  # 5
        bg["detail_idx"],  # 6
        bg["ideal_idx"],  # 7
        bg["flaw_idx"],  # 8
    ]

    character = {
        "array": numeric_array,
        "name": random_full_name(ancestry, gender),
        "gender": gender,
        "alignment": alignment,
        "ancestry": ancestry,
        "age": age,
        "role": role,
        "role_detail_label": bg["role_label"],
        "role_detail": bg["role_detail_text"],
        "ideal": bg["ideal_text"],
        "ideal_axis": bg["ideal_axis"],
        "flaw": bg["flaw_text"],
    }

    validate_character(character)
    return character


# ============================================================================
# EXAMPLE
# ============================================================================

if __name__ == "__main__":
    validate_rules()

    persona = generate_character()

    print("=== CHARACTER ===")
    print(persona)
    print()
