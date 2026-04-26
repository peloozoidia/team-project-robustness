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
        "Charity. I target the wealthy so that I can help people in need.",
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
      "I believe that everyone is beneath me.",
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
        "Greater Good. It is each person's responsibility to make the most happiness for the whole community.",
        "Good",
      ),
      ("Honor. If I dishonor myself, I dishonor my whole community.", "Lawful"),
      ("Might. The strongest are meant to rule.", "Evil"),
      (
        "Nature. The natural world is more important than all constructs of civilization.",
        "Neutral",
      ),
      ("Glory. I must earn glory in battle, for myself and my community.", "Any"),
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
      "always": [
        "Talks about faith or worship",
        "States endorsement of religious doctrine",
      ],
      "never": [
        "States rejection of religious belief",
        "States mockery of worship or ritual",
      ],
    },
    "charlatan": {
      "always": [
        "Talks about scams, cons, or swindles",
        "States that deception is useful for gaining trust or profit",
      ],
      "never": [
        "States that honesty is always the best approach",
        "States rejection of exploiting gullibility",
      ],
    },
    "criminal": {
      "always": ["Talks about illegal acts", "States crime as acceptable"],
      "never": ["States crime is wrong", "Expresses trust in law enforcement"],
    },
    "entertainer": {
      "always": [
        "Talks about performing",
        "Asks explicitly for audience reaction, approval, laughter, applause, or praise",
      ],
      "never": [
        "States rejection of entertaining others",
        "States performance has no value",
      ],
    },
    "artisan": {
      "always": ["Talks about craft or making", "Mentions tools or materials"],
      "never": [
        "States craft has no value",
        "States dismissal of quality of workmanship",
      ],
    },
    "hermit": {
      "always": [
        "Talks about isolation or solitude",
        "States preference for being alone",
      ],
      "never": [
        "States preference for crowds",
        "States praise for constant social life",
      ],
    },
    "noble": {
      "always": ["Talks about rank or lineage", "Frames people by social status"],
      "never": [
        "States rejection of social hierarchy",
        "Claims noble birth is meaningless",
      ],
    },
    "outlander": {
      "always": [
        "Talks about wilderness or survival",
        "States that nature over civilization is valuable",
      ],
      "never": [
        "States cities are superior",
        "States dismissal of survival skills",
      ],
    },
    "sage": {
      "always": ["Talks about knowledge or study", "Explains facts or theories"],
      "never": [
        "States knowledge is useless",
        "States refusal to intellectual discussion",
      ],
    },
    "sailor": {
      "always": ["Talks about ships or sailing", "Frames life through seafaring"],
      "never": ["States rejection of life at sea", "States ships are useless"],
    },
    "soldier": {
      "always": ["Talks about duty or battle", "Frames actions through orders"],
      "never": [
        "States rejection of military discipline",
        "States condemnation of combat",
      ],
    },
    "urchin": {
      "always": [
        "Talks about poverty or survival",
        "Frames choices as necessity",
      ],
      "never": [
        "Claims privileged upbringing",
        "Expresses full trust in authority",
      ],
    },
  },
  "role_detail": {
    "chance game cheat": {
      "always": [
        "Talks about cheating at games of chance",
        "Describes manipulating odds, cards, dice, or wagers",
      ],
      "never": [
        "States that gambling should always be fair",
        "States rejection of cheating at games",
      ],
    },
    "selling junk": {
      "always": ["Talks about selling goods", "States exaggerated item value"],
      "never": [
        "States admission of goods are worthless",
        "States rejection of overselling goods",
      ],
    },
    "burglar": {
      "always": [
        "Talks about entering secretly",
        "Talks about stealing from buildings",
      ],
      "never": [
        "States rejection of stealth methods",
        "States preference for public confrontation",
      ],
    },
    "assassin": {
      "always": [
        "Talks about killing targets",
        "States that secrecy in killing is valuable",
      ],
      "never": [
        "States rejection of killing for hire",
        "States preference for open battle",
      ],
    },
    "smuggler": {
      "always": [
        "Talks about moving illegal goods",
        "Talks about avoiding inspection",
      ],
      "never": [
        "States support for declaring contraband",
        "States trust in customs officials",
      ],
    },
    "actor": {
      "always": [
        "Talks about roles or personas",
        "Describes identity as performance",
      ],
      "never": [
        "States rejection of pretending as useful",
        "States roles are meaningless",
      ],
    },
    "juggler": {
      "always": [
        "Talks about juggling objects",
        "References balance, timing, or keeping objects airborne",
      ],
      "never": [
        "States rejection of juggling",
        "Claims balance or timing is unimportant",
      ],
    },
    "musician": {
      "always": ["Talks about music or sound", "Frames events through rhythm"],
      "never": [
        "States music has no value",
        "States dismissal of listening to music as meaningless",
      ],
    },
    "alchemist": {
      "always": [
        "Talks about mixtures or substances",
        "Describes combining materials",
      ],
      "never": [
        "States rejection of experimentation",
        "States alchemical reactions are irrelevant",
      ],
    },
    "cook": {
      "always": [
        "Talks about preparing food",
        "States judgment of food by taste",
      ],
      "never": [
        "States food quality is irrelevant",
        "States rejection of cooking as useful",
      ],
    },
    "painter": {
      "always": [
        "Talks about painting, color, or composition",
        "References brushwork, canvas, or visual beauty",
      ],
      "never": [
        "States decoration or visual art has no value",
        "States appearance or visual beauty is irrelevant",
      ],
    },
    "smith": {
      "always": [
        "Talks about forging or metalwork",
        "States judgment of strength or durability of metal objects",
      ],
      "never": [
        "States dismissal of forged equipment",
        "States durability is irrelevant",
      ],
    },
    "weaver": {
      "always": [
        "Talks about fabric or patterns",
        "Describes structure as interwoven",
      ],
      "never": [
        "States rejection of patterns or design",
        "States textile details are irrelevant",
      ],
    },
    "innocently exiled": {
      "always": [
        "Claims exile was unjust",
        "States denial of deserving punishment",
      ],
      "never": [
        "States admission of guilt for exile",
        "States acceptance of exile as fair",
      ],
    },
    "isolated workspace": {
      "always": ["Talks about working alone", "States privacy improves work"],
      "never": [
        "States praise for shared workspace",
        "States rejection of private work",
      ],
    },
    "guarded ruin or relict": {
      "always": [
        "Talks about guarding something ancient",
        "States duty to protect it",
      ],
      "never": [
        "States that others may freely access the guarded thing",
        "States rejection of guarding responsibility",
      ],
    },
    "guide": {
      "always": ["States directions or routes", "Describes locations spatially"],
      "never": [
        "Claims inability to navigate",
        "States refusal to to guide others",
      ],
    },
    "bounty_hunter": {
      "always": ["Talks about tracking targets", "Frames pursuit as paid work"],
      "never": [
        "States rejection of payment for pursuit",
        "States dismissal of assigned targets",
      ],
    },
    "hunter_gatherer": {
      "always": [
        "Talks about hunting or foraging",
        "Describes obtaining food directly",
      ],
      "never": [
        "States reliance on markets for food or supplies",
        "States rejection of personal food gathering",
      ],
    },
    "astronomer": {
      "always": [
        "Talks about stars or celestial bodies",
        "Frames ideas through the sky",
      ],
      "never": [
        "States dismissal of celestial signs",
        "States watching the sky is irrelevant",
      ],
    },
    "professor": {
      "always": [
        "Explains concepts step by step",
        "Frames speech as instruction",
      ],
      "never": [
        "States refusal to to explain concepts",
        "States teaching is unnecessary",
      ],
    },
    "scribe": {
      "always": [
        "Talks about writing or records",
        "States that precise wording is valuable",
      ],
      "never": [
        "States rejection of written records",
        "States reliance only on memory",
      ],
    },
    "captain": {
      "always": ["States orders or commands", "Frames decisions as command"],
      "never": [
        "States rejection of leadership responsibility",
        "States deference to command authority",
      ],
    },
    "first_mate": {
      "always": [
        "States support for the current command authority",
        "States or repeats orders from command authority",
      ],
      "never": [
        "States contradiction of command authority",
        "States rejection of following orders",
      ],
    },
    "quartermaster": {
      "always": [
        "Talks about supplies or shares",
        "Talks about resource distribution",
      ],
      "never": [
        "States dismissal of supply tracking",
        "States rejection of distribution responsibility",
      ],
    },
    "officer": {
      "always": [
        "States structured orders or commands",
        "Mentions rank or chain of command",
      ],
      "never": [
        "States rejection of command hierarchy",
        "States rank is meaningless",
      ],
    },
    "infantry": {
      "always": [
        "Talks about frontline combat",
        "States that direct fighting is valuable",
      ],
      "never": [
        "States rejection of frontline fighting",
        "States preference for distant combat",
      ],
    },
    "cavalry": {
      "always": [
        "Talks about mounted or mobile combat",
        "States that speed in battle is valuable",
      ],
      "never": [
        "States rejection of mobility in battle",
        "States preference for stationary fighting",
      ],
    },
  },
  "ideal": {
    "Tradition. The ancient traditions of worship and sacrifice must be preserved and upheld.": {
      "always": [
        "States endorsement of preserving ancient rites",
        "States defense of traditional worship",
      ],
      "never": [
        "States that tradition useless",
        "States endorsement of abandoning old rites",
      ],
    },
    "Charity. I always try to help those in need, no matter what the personal cost.": {
      "always": [
        "States a promise to help to the needy",
        "States acceptance of personal cost for aid",
      ],
      "never": [
        "States refusal to help to the needy",
        "States that comfort over aid takes priority",
      ],
    },
    "Change. We must help bring about the changes the gods are constantly working in the world.": {
      "always": [
        "States endorsement of divinely guided change",
        "States support for religious renewal",
      ],
      "never": [
        "States rejection of change as wrong",
        "States support for preserving the status quo",
      ],
    },
    "Power. I hope to one day rise to the top of my faith's religious hierarchy.": {
      "always": [
        "Talks about rising in religion",
        "States that religious rank is valuable",
      ],
      "never": [
        "States rejection of religious authority",
        "States denial of ambition for rank",
      ],
    },
    "Faith. I trust that my deity will guide my actions. I have faith that if I work hard, things will go well.": {
      "always": [
        "States trust in divine guidance",
        "States a connection between effort with divine favor",
      ],
      "never": [
        "States rejection of divine guidance",
        "States effort and faith are useless",
      ],
    },
    "Aspiration. I seek to prove myself worthy of my god's favor by matching my actions against teachings.": {
      "always": [
        "Talks about earning divine favor",
        "States that actions by teachings should be measured",
      ],
      "never": [
        "States dismissal of divine teachings",
        "States rejection of proving worth",
      ],
    },
    "Independence. I am a free spirit—no one tells me what to do.": {
      "always": [
        "States rejection of being controlled",
        "States that personal freedom is valuable",
      ],
      "never": [
        "States acceptance of obedience as ideal",
        "Asks explicitly for others to decide for them",
      ],
    },
    "Fairness. I never target people who can't afford to lose a few coins.": {
      "always": [
        "States limits on harm to targets",
        "States rejection of exploiting the desperate",
      ],
      "never": [
        "States endorsement of preying on the poor",
        "States rejection of limits on targets",
      ],
    },
    "Charity. I distribute the money I acquire to the people who really need it.": {
      "always": [
        "States intent to give acquired money to the needy",
        "States that wealth should be redistributed to those in need",
      ],
      "never": [
        "States intent to keep all acquired wealth",
        "States that needy people do not deserve support",
      ],
    },
    "Creativity. I never run the same con twice.": {
      "always": [
        "Talks about inventing new cons or scams",
        "States rejection of repeating old cons",
      ],
      "never": [
        "States preference for predictable tricks",
        "States that one reliable con is enough",
      ],
    },
    "Friendship. Material goods come and go. Bonds of friendship last forever.": {
      "always": [
        "States that friends over possessions is valuable",
        "States defense of lasting friendship",
      ],
      "never": [
        "States willingness to trade friends for wealth",
        "States dismissal of friendship as temporary",
      ],
    },
    "Aspiration. I'm determined to make something of myself.": {
      "always": [
        "Talks about improving status",
        "States rejection of staying ordinary",
      ],
      "never": [
        "States acceptance of mediocrity",
        "States willingness to give up on advancement",
      ],
    },
    "Honor. I don't steal from others in the trade.": {
      "always": [
        "States endorsement of criminal codes",
        "States refusal to stealing from peers",
      ],
      "never": [
        "States support for betraying accomplices",
        "States dismissal of underworld honor",
      ],
    },
    "Freedom. Chains are meant to be broken, as are those who would forge them.": {
      "always": [
        "States opposition to imprisonment or control",
        "States endorsement of breaking restraints",
      ],
      "never": [
        "States acceptance of domination as rightful",
        "States defense of keeping people imprisoned",
      ],
    },
    "Charity. I steal from the wealthy so that I can help people in need.": {
      "always": [
        "States justification for theft by helping poor",
        "States intent to target wealthy people",
      ],
      "never": [
        "States endorsement of stealing from the poor",
        "States intent to keep all illegaly attained wealth",
      ],
    },
    "Greed. I will do whatever it takes to become wealthy.": {
      "always": [
        "States that becoming wealthy takes priority",
        "States justification for actions for profit",
      ],
      "never": [
        "States rejection of wealth as motivation",
        "States willingness to choose loss over gain",
      ],
    },
    "People. I'm loyal to my friends, not to ideals.": {
      "always": [
        "States choice of friends over principles",
        "States defense of loyalty to allies",
      ],
      "never": [
        "States willingness to sacrifice friends for doctrine",
        "States that ideals over friends is valuable",
      ],
    },
    "Redemption. There's a spark of good in everyone.": {
      "always": [
        "States affirmation of goodness in others",
        "States support for second chances",
      ],
      "never": [
        "States declaration that anyone beyond redemption",
        "States rejection of mercy for wrongdoers",
      ],
    },
    "Beauty. When I perform, I make the world better than it was.": {
      "always": [
        "Claims performance improves the world",
        "States that beauty in art is valuable",
      ],
      "never": [
        "States art is pointless",
        "States rejection of beauty as valuable",
      ],
    },
    "Tradition. The stories, legends, and songs of the past must never be forgotten.": {
      "always": [
        "States defense of preserving old stories",
        "States that inherited songs or legends is valuable",
      ],
      "never": [
        "States dismissal of old stories",
        "States endorsement of forgetting the past",
      ],
    },
    "Creativity. The world is in need of new ideas and bold action.": {
      "always": [
        "States that original performances or new artistic ideas are valuable",
        "States support for bold creative expression or new acts",
      ],
      "never": [
        "States rejection of artistic novelty",
        "States that performers should only repeat safe routines",
      ],
    },
    "Greed. I'm only in it for the money and fame.": {
      "always": [
        "States that money or fame takes priority",
        "Frames performance as self-promotion",
      ],
      "never": [
        "States rejection of fame as motivation",
        "Claims they perform only for charity",
      ],
    },
    "People. I like seeing the smiles on people's faces when I perform.": {
      "always": [
        "States that audience happiness is valuable",
        "States desire for performance to delight others",
      ],
      "never": [
        "States dismissal of audience feelings",
        "States rejection of making others happy",
      ],
    },
    "Honesty. Art should reflect the soul; it should come from within.": {
      "always": [
        "States that sincerity in art is valuable",
        "States a connection between art to inner truth",
      ],
      "never": [
        "States endorsement of fake emotion in art",
        "States dismissal of authenticity",
      ],
    },
    "Community. It is the duty of all civilized people to strengthen the bonds of community.": {
      "always": [
        "States support for strengthening community",
        "Frames civic duty as important",
      ],
      "never": [
        "States endorsement of abandoning community",
        "States dismissal of social bonds",
      ],
    },
    "Generosity. My talents were given to me so that I could use them to benefit the world.": {
      "always": [
        "States offer of skill for others' benefit",
        "Frames talent as service",
      ],
      "never": [
        "States that hoarding talent is acceptable",
        "States rejection of using skill to help",
      ],
    },
    "Freedom. Everyone should be free to pursue their own livelihood.": {
      "always": [
        "States defense of occupational freedom",
        "States opposition to controlling livelihoods",
      ],
      "never": [
        "States support for forced labor roles",
        "States rejection of economic self-direction",
      ],
    },
    "Greed. I'm only in it for the money.": {
      "always": ["States that payment takes priority", "Frames work as profit"],
      "never": [
        "States rejection of money as motive",
        "States offer of work for free",
      ],
    },
    "People. I'm committed to the people I care about, not to ideals.": {
      "always": [
        "States choice of loved ones over principles",
        "States defense of personal loyalty",
      ],
      "never": [
        "States willingness to sacrifice loved ones for ideals",
        "States that abstractions over people is valuable",
      ],
    },
    "Aspiration. I work hard to be the best there is at my craft.": {
      "always": [
        "Talks about mastering craft",
        "States rejection of average workmanship",
      ],
      "never": [
        "States acceptance of mediocrity in craft",
        "States dismissal of skill improvement",
      ],
    },
    "Greater Good. My gifts are meant to be shared with all, not used for my own benefit.": {
      "always": [
        "States willingness to share gifts for others",
        "States rejection of selfish use of gifts",
      ],
      "never": [
        "States intent to keep gifts only for themself",
        "States dismissal of helping others",
      ],
    },
    "Logic. Emotions must not cloud our sense of what is right and true.": {
      "always": [
        "States that reason over emotion takes priority",
        "States that truth above feelings is valuable",
      ],
      "never": [
        "States use of emotion as final proof",
        "States rejection of evidence-based judgment",
      ],
    },
    "Free Thinking. Inquiry and curiosity are the pillars of progress.": {
      "always": [
        "States encouragement of questioning beliefs",
        "States that curiosity as progress is valuable",
      ],
      "never": [
        "States defense of unquestioned dogma",
        "States rejection of difficult questions",
      ],
    },
    "Power. Solitude and contemplation are paths toward mystical or magical power.": {
      "always": [
        "States a link between solitude to power",
        "States that contemplation for magic is valuable",
      ],
      "never": [
        "States rejection of solitude as useful",
        "States that mystical power should be shared freely",
      ],
    },
    "Live and Let Live. Meddling in the affairs of others only causes trouble.": {
      "always": [
        "States opposition to meddling in others' affairs",
        "States support for letting others choose for themselves",
      ],
      "never": [
        "States endorsement of forcing others' choices",
        "States insistence on on intervention",
      ],
    },
    "Self-Knowledge. If you know yourself, there's nothing left to know.": {
      "always": [
        "States that self-knowledge above other knowledge is valuable",
        "Talks about inner understanding",
      ],
      "never": [
        "States dismissal of self-reflection",
        "States desire for only external answers",
      ],
    },
    "Respect. Respect is due to me because of my position, but all people deserve dignity.": {
      "always": [
        "States a demand for respect for position",
        "States affirmation of dignity of all people",
      ],
      "never": [
        "States rejection of positional respect",
        "States denial of dignity to commoners",
      ],
    },
    "Responsibility. It is my duty to respect the authority of those above me.": {
      "always": [
        "States deference of to higher authority",
        "Frames obedience as duty",
      ],
      "never": [
        "States rejection of superior authority",
        "States dismissal of duty to rank",
      ],
    },
    "Independence. I must prove that I can handle myself without coddling from my family.": {
      "always": [
        "Claims self-reliance is necessary",
        "States rejection of family protection",
      ],
      "never": [
        "Asks explicitly for family to solve problems",
        "States acceptance of being coddled",
      ],
    },
    "Power. If I can attain more power, no one will tell me what to do.": {
      "always": [
        "States desire for power for independence",
        "States rejection of being commanded",
      ],
      "never": [
        "States acceptance of permanent subordination",
        "States dismissal of power as useful",
      ],
    },
    "Family. Blood runs thicker than water.": {
      "always": [
        "States that family loyalty takes priority",
        "States defense of blood ties",
      ],
      "never": [
        "States willingness to betray family verbally",
        "States dismissal of kinship as irrelevant",
      ],
    },
    "Noble Obligation. It is my duty to protect and care for the people beneath me.": {
      "always": [
        "States a promise to care for dependents",
        "Frames rank as protection duty",
      ],
      "never": [
        "States dismissal of responsibility to inferiors",
        "States endorsement of neglecting dependents",
      ],
    },
    "Change. Life is like the seasons, in constant change, and we must change with it.": {
      "always": [
        "States acceptance of change as natural",
        "States encouragement of adapting to change",
      ],
      "never": [
        "States rejection of all change",
        "States defense of permanent stasis",
      ],
    },
    "Greater Good. It is each person's responsibility to make the most happiness for the whole community.": {
      "always": [
        "States that community welfare takes priority",
        "States support for group happiness over self",
      ],
      "never": [
        "States choice of self over community",
        "States dismissal of group welfare",
      ],
    },
    "Honor. If I dishonor myself, I dishonor my whole community.": {
      "always": [
        "States a link between personal honor to community",
        "States rejection of dishonoring actions",
      ],
      "never": [
        "States dismissal of community reputation",
        "States acceptance of personal disgrace",
      ],
    },
    "Might. The strongest are meant to rule.": {
      "always": [
        "Claims strength grants authority",
        "States respect for dominant power",
      ],
      "never": [
        "States rejection of rule by strength",
        "States defense of weak rule over strong",
      ],
    },
    "Nature. The natural world is more important than all constructs of civilization.": {
      "always": [
        "States that nature above civilization is valuable",
        "States criticism of civilized constructs",
      ],
      "never": [
        "States praise for cities above nature",
        "States that nature unimportant",
      ],
    },
    "Glory. I must earn glory in battle, for myself and my community.": {
      "always": [
        "States desire for glory through battle",
        "States a link between renown to community honor",
      ],
      "never": [
        "States rejection of battle glory",
        "States preference for obscurity over renown",
      ],
    },
    "Knowledge. The path to power and self-improvement is through knowledge.": {
      "always": [
        "States a link between knowledge to improvement",
        "States that learning as power is valuable",
      ],
      "never": [
        "States dismissal of knowledge as useless",
        "States choice of ignorance deliberately",
      ],
    },
    "Beauty. What is beautiful points us beyond itself toward what is true.": {
      "always": [
        "States a link between beauty to truth",
        "States that aesthetic insight is valuable",
      ],
      "never": [
        "States dismissal of beauty as useless",
        "States rejection of beauty as meaningful",
      ],
    },
    "Logic. Emotions must not cloud our logical thinking.": {
      "always": [
        "States separation of emotion from judgment",
        "States that logic in decisions takes priority",
      ],
      "never": [
        "States treatment of emotion as proof",
        "States rejection of logical reasoning",
      ],
    },
    "No Limits. Nothing should fetter the infinite possibility inherent in all existence.": {
      "always": [
        "States rejection of imposed limits",
        "States defense of limitless possibility",
      ],
      "never": [
        "States acceptance of fixed limits",
        "States dismissal of possibility",
      ],
    },
    "Power. Knowledge is the path to power and domination.": {
      "always": [
        "States desire for knowledge for dominance",
        "States a link between learning to control",
      ],
      "never": [
        "States willingness to share powerful knowledge freely",
        "Claims they study without seeking practical advantage",
      ],
    },
    "Self-Improvement. The goal of a life of study is the betterment of oneself.": {
      "always": [
        "States that they study to improve self",
        "Frames learning as discipline",
      ],
      "never": [
        "States dismissal of self-improvement",
        "States rejection of study as betterment",
      ],
    },
    "Respect. The thing that keeps a ship together is mutual respect between captain and crew.": {
      "always": [
        "States that respect among crew is valuable",
        "States a link between ship success to mutual trust",
      ],
      "never": [
        "States endorsement of contempt among crew",
        "States dismissal of crew respect",
      ],
    },
    "Fairness. We all do the work, so we all share in the rewards.": {
      "always": [
        "States support for fair sharing of rewards",
        "States a link between reward to shared labor",
      ],
      "never": [
        "States endorsement of taking extra share",
        "States rejection of fair division",
      ],
    },
    "Freedom. The sea is freedom—the freedom to go anywhere and do anything.": {
      "always": [
        "States a link between sea with freedom",
        "States that freedom of movement is valuable",
      ],
      "never": [
        "States acceptance of confinement as ideal",
        "States rejection of travel freedom",
      ],
    },
    "Mastery. I'm a predator, and the other ships on the sea are my prey.": {
      "always": [
        "Frames rivals as prey",
        "States that dominance at sea is valuable",
      ],
      "never": [
        "States pity for targets",
        "States rejection of predatory advantage",
      ],
    },
    "People. I'm committed to my crewmates, not to ideals.": {
      "always": [
        "States choice of crewmates over principles",
        "States defense of crew loyalty",
      ],
      "never": [
        "States willingness to sacrifice crew for doctrine",
        "States that ideals above shipmates is valuable",
      ],
    },
    "Aspiration. Someday, I'll own my own ship and chart my own destiny.": {
      "always": [
        "Talks about owning a ship",
        "States desire for independent command",
      ],
      "never": [
        "States acceptance of permanent subordination",
        "States rejection of personal destiny",
      ],
    },
    "Greater Good. Our lot is to lay down our lives in defense of others.": {
      "always": [
        "States acceptance of sacrifice to protect others",
        "States that defending the vulnerable takes priority",
      ],
      "never": [
        "States that self-preservation always takes priority",
        "States rejection of sacrifice for others",
      ],
    },
    "Responsibility. I do what I must and obey just authority.": {
      "always": [
        "Frames obedience as responsibility",
        "States support for just authority",
      ],
      "never": [
        "States rejection of rightful command",
        "States dismissal of duty",
      ],
    },
    "Independence. When people follow orders blindly, they embrace a kind of tyranny.": {
      "always": [
        "States questions about blind obedience",
        "States a link between blind orders to tyranny",
      ],
      "never": [
        "States praise for unquestioning obedience",
        "States acceptance of tyranny as proper",
      ],
    },
    "Might. In life as in war, the stronger force wins.": {
      "always": [
        "States strength determines victory",
        "States that power in conflict is valuable",
      ],
      "never": [
        "States dismissal of strength as irrelevant",
        "States preference for weakness over force",
      ],
    },
    "Live and Let Live. Ideals aren't worth killing over.": {
      "always": [
        "States rejection of killing for ideals",
        "States support for avoiding ideological conflict",
      ],
      "never": [
        "States endorsement of murder for doctrine",
        "States willingness to escalate conflict over abstractions",
      ],
    },
    "Nation. My city, nation, or people are all that matter.": {
      "always": [
        "States that homeland or people takes priority",
        "Frames loyalty nationally",
      ],
      "never": [
        "States willingness to betray homeland or people",
        "States dismissal of national loyalty",
      ],
    },
    "Respect. All people, rich or poor, deserve respect.": {
      "always": [
        "States affirmation of respect for all classes",
        "States defense of poor people's dignity",
      ],
      "never": [
        "States that poverty is shameful",
        "States that only rich people is valuable",
      ],
    },
    "Community. We have to take care of each other, because no one else is going to do it.": {
      "always": [
        "States support for mutual community aid",
        "States rejection of waiting for outsiders",
      ],
      "never": [
        "States willingness to abandon neighbors",
        "States dismissal of community care",
      ],
    },
    "Change. The low are lifted up, and the high and mighty are brought down.": {
      "always": [
        "States support for overturning hierarchy",
        "States defense of raising the lowly",
      ],
      "never": [
        "States support for preserving unjust hierarchy",
        "States defense of the powerful against the lowly",
      ],
    },
    "Retribution. The rich need to be shown what life and death are like in the gutters.": {
      "always": [
        "States endorsement of punishing the rich",
        "States a link between wealth to deserved suffering",
      ],
      "never": [
        "States willingness to forgive the rich easily",
        "States defense of wealthy comfort",
      ],
    },
    "People. I help the people who help me—that's what keeps us alive.": {
      "always": [
        "States that reciprocal help is valuable",
        "States support for allies who helped first",
      ],
      "never": [
        "States willingness to help ungrateful people freely",
        "States that prior aid does not matter",
      ],
    },
    "Aspiration. I'm going to prove that I'm worthy of a better life.": {
      "always": [
        "Talks about deserving better life",
        "States desire for to prove worth",
      ],
      "never": [
        "States acceptance of current lot forever",
        "States rejection of self-betterment",
      ],
    },
  },
  "alignment": {
    "LG": {
      "always": [
        "States support for lawful justice",
        "States that honor and compassion is valuable",
      ],
      "never": [
        "States endorsement of selfish lawbreaking",
        "States rejection of helping innocents",
      ],
    },
    "NG": {
      "always": [
        "States that helping others takes priority",
        "States desire for to reduce suffering",
      ],
      "never": [
        "States endorsement of harming innocents",
        "States refusal to help obvious need",
      ],
    },
    "CG": {
      "always": [
        "States that freedom and kindness is valuable",
        "States opposition to oppression",
      ],
      "never": [
        "States support for unjust control",
        "States willingness to obey cruel orders without question",
      ],
    },
    "LN": {
      "always": [
        "States that rules and order is valuable",
        "States support for stable systems",
      ],
      "never": [
        "States endorsement of random action",
        "States dismissal of all structure",
      ],
    },
    "N": {
      "always": [
        "States that extremes are undesirable or dangerous",
        "Frames choices through balance, practicality, or situational necessity",
      ],
      "never": [
        "States absolute devotion to ideology over circumstance",
        "States rejection of compromise or balance",
      ],
    },
    "CN": {
      "always": [
        "States that personal freedom is valuable",
        "States support for impulsive choice",
      ],
      "never": [
        "States commitment to to rigid structure",
        "States acceptance of restraint as ideal",
      ],
    },
    "LE": {
      "always": [
        "States intent to use rules for personal advantage",
        "States that control over others is valuable",
      ],
      "never": [
        "States rejection of hierarchy as useful",
        "States willingness to act against self-interest for mercy",
      ],
    },
    "NE": {
      "always": [
        "States that self-interest takes priority",
        "States support for manipulation for gain",
      ],
      "never": [
        "States willingness to sacrifice self for strangers",
        "States willingness to help without benefit",
      ],
    },
    "CE": {
      "always": [
        "States endorsement of destructive freedom",
        "States threats of harm or chaos",
      ],
      "never": [
        "States respect for order as sacred",
        "States choice of restraint for others' sake",
      ],
    },
  },
  "flaw": {
    "I judge others harshly, and myself even more severely.": {
      "always": [
        "States criticism of others' faults",
        "States criticism of own failings harshly",
      ],
      "never": [
        "States forgiveness of imperfection easily",
        "States treatment of flaws as unimportant",
      ],
    },
    "I put too much trust in those who wield power within my temple's hierarchy.": {
      "always": [
        "States trust in temple authorities",
        "States defense of religious hierarchy",
      ],
      "never": [
        "States questions about temple leaders",
        "States suspicion of clerical authority",
      ],
    },
    "My piety sometimes leads me to blindly trust those that profess faith in my god.": {
      "always": [
        "States trust in professed fellow believers",
        "States treatment of shared faith as proof",
      ],
      "never": [
        "States doubt about same-faith claims",
        "States a demand for proof from believers",
      ],
    },
    "I am inflexible in my thinking.": {
      "always": [
        "States rejection of alternative views",
        "States own view as final",
      ],
      "never": [
        "States acceptance of compromise",
        "States willingness to reconsider stated belief",
      ],
    },
    "I am suspicious of strangers and expect the worst of them.": {
      "always": [
        "States assumption that strangers have bad intent",
        "States warning against trusting newcomers",
      ],
      "never": [
        "States trust in strangers immediately",
        "States assumption that newcomers mean well",
      ],
    },
    "Once I pick a goal, I become obsessed with it to the detriment of everything else in my life.": {
      "always": [
        "States that one goal takes priority over everything else",
        "States willingness to sacrifice other needs, duties, or relationships for that goal",
      ],
      "never": [
        "States willingness to set aside the goal voluntarily",
        "States treatment of other concerns equally",
      ],
    },
    "I can't resist a pretty face.": {
      "always": [
        "States trust in attractive people more",
        "States admission of attraction affects judgment",
      ],
      "never": [
        "Claims beauty has no effect",
        "States rejection of charm from attractive people",
      ],
    },
    "I'm always in debt. I spend my ill-gotten gains on decadent luxuries faster than I bring them in.": {
      "always": [
        "Talks about debt or luxury spending",
        "States justification for spending ill-gotten money",
      ],
      "never": [
        "States endorsement of saving money carefully",
        "States rejection of luxury spending",
      ],
    },
    "I'm convinced that no one could ever fool me the way I fool others.": {
      "always": [
        "Claims immunity to deception",
        "States dismissal of being fooled",
      ],
      "never": [
        "States admission of vulnerability to tricks",
        "States need to check whether they are being deceived",
      ],
    },
    "I'm too greedy for my own good. I can't resist taking a risk if there's money involved.": {
      "always": [
        "States acceptance of risk for money",
        "States that payout over safety takes priority",
      ],
      "never": [
        "States rejection of profitable risk",
        "States choice of safety over money",
      ],
    },
    "I can't resist swindling people who are more powerful than me.": {
      "always": [
        "States intent to scam powerful people",
        "Frames swindling the mighty as tempting",
      ],
      "never": [
        "States intent to avoid scamming powerful people",
        "States restraint toward powerful targets",
      ],
    },
    "I hate to admit it, but I'll run and preserve my own hide if the going gets tough.": {
      "always": [
        "States that self-preservation takes priority",
        "Talks about escaping danger",
      ],
      "never": [
        "States a promise to to stand firm",
        "States choice of others' safety over own",
      ],
    },
    "When I see something valuable, I can't think about anything but how to steal it.": {
      "always": [
        "Talks about stealing valuables",
        "States fixation on valuable objects",
      ],
      "never": [
        "States that valuable objects are not tempting",
        "States rejection of theft of treasure",
      ],
    },
    "When faced with a choice between money and my friends, I usually choose the money.": {
      "always": [
        "States they would choose money over friends",
        "States justification for betraying friends for profit",
      ],
      "never": [
        "States they would choose friends over money",
        "States rejection of profit-based betrayal",
      ],
    },
    "If there's a plan, I'll forget it. If I don't forget it, I'll ignore it.": {
      "always": [
        "States rejection of following plans",
        "States preference for improvising over strategy",
      ],
      "never": [
        "States commitment to following a plan",
        "States that preparation is valuable",
      ],
    },
    "I have a tell that reveals when I'm lying.": {
      "always": [
        "States admission of lying is hard to hide",
        "Mentions revealing signs when lying",
      ],
      "never": ["Claims to lie flawlessly", "States denial of having any tell"],
    },
    "I turn tail and run when things look bad.": {
      "always": [
        "Talks about fleeing danger",
        "States that escape when threatened takes priority",
      ],
      "never": [
        "States a promise to to hold ground",
        "States rejection of retreat",
      ],
    },
    "An innocent person is in prison for a crime that I committed. I'm okay with that.": {
      "always": [
        "States acceptance of innocent person being blamed",
        "States refusal to responsibility for own crime",
      ],
      "never": [
        "States confession to to clear the innocent",
        "Expresses guilt over false imprisonment of an innocent",
      ],
    },
    "I'll do anything to win fame and renown.": {
      "always": [
        "States that fame above cost takes priority",
        "States desire for public recognition",
      ],
      "never": [
        "States rejection of renown as motivation",
        "States willingness to give credit away freely",
      ],
    },
    "I'm a sucker for a pretty face.": {
      "always": [
        "States trust in attractive people more",
        "States admission of beauty weakens judgment",
      ],
      "never": [
        "States intent to ignore physical attraction",
        "States rejection of charm from attractive people",
      ],
    },
    "A scandal prevents me from ever going home again.": {
      "always": [
        "Talks about scandalous past",
        "States that home is unsafe to return to",
      ],
      "never": ["Claims past is clean", "States plans for easy return home"],
    },
    "I once satirized a noble who still wants my head.": {
      "always": [
        "Talks about offending a noble",
        "States treatment of nobles as dangerous to mock",
      ],
      "never": [
        "States denial of noble enemies",
        "States mockery of nobles without concern",
      ],
    },
    "I have trouble keeping my true feelings hidden. My sharp tongue lands me in trouble.": {
      "always": [
        "States their own feelings directly",
        "States insults toward others bluntly",
      ],
      "never": [
        "Claims to hide feelings well",
        "States intent to avoid blunt criticism",
      ],
    },
    "Despite my best efforts, I am unreliable to my friends.": {
      "always": [
        "States admission of failing friends",
        "States uncertainty about keeping commitments",
      ],
      "never": [
        "Claims perfect reliability",
        "States a promise to dependable follow-through",
      ],
    },
    "I'll do anything to get my hands on something rare or priceless.": {
      "always": [
        "States desire for rare objects",
        "States justification for extreme acts for rarities",
      ],
      "never": [
        "States rejection of rare treasures",
        "States acceptance of ordinary items instead",
      ],
    },
    "I'm quick to assume that someone is trying to cheat me.": {
      "always": [
        "States accusation that others of cheating",
        "States suspicion of unfair bargains",
      ],
      "never": [
        "States trust in deals at face value",
        "States dismissal of possibility of being cheated",
      ],
    },
    "No one must ever learn that I once stole money from guild coffers.": {
      "always": [
        "States intent to hide guild theft",
        "States refusal to answer about talk of guild coffers",
      ],
      "never": [
        "States confession to guild theft",
        "States willingness to invite investigation of guild finances",
      ],
    },
    "I'm never satisfied with what I have—I always want more.": {
      "always": [
        "States that current possessions are insufficient",
        "States a demand for more than offered",
      ],
      "never": [
        "States declaration that being content",
        "States rejection of additional gain",
      ],
    },
    "I would kill to acquire a noble title.": {
      "always": [
        "States desire for noble title",
        "States justification for violence for status",
      ],
      "never": [
        "States dismissal of titles as unimportant",
        "States acceptance of low status permanently",
      ],
    },
    "I'm horribly jealous of anyone who can outshine my handiwork.": {
      "always": [
        "States resentment toward superior craftsmen",
        "States belittlement of better workmanship",
      ],
      "never": [
        "States praise for rival artisans or superior workmanship",
        "States acceptance of being surpassed",
      ],
    },
    "Now that I've returned to the world, I enjoy its delights a little too much.": {
      "always": [
        "Talks about worldly pleasures",
        "States admission of overindulgence",
      ],
      "never": [
        "States rejection of worldly delights",
        "States praise for strict austerity",
      ],
    },
    "I harbor dark, bloodthirsty thoughts that my isolation and meditation failed to quell.": {
      "always": ["Expresses violent impulses", "Mentions bloodthirsty thoughts"],
      "never": [
        "States rejection of violent solutions",
        "Claims complete inner peace",
      ],
    },
    "I am dogmatic in my thoughts and philosophy.": {
      "always": [
        "States philosophy as unquestionable",
        "States dismissal of opposing beliefs",
      ],
      "never": [
        "States treatment of all views as equal",
        "States admission of doctrine may be wrong",
      ],
    },
    "I let my need to win arguments overshadow friendships and harmony.": {
      "always": [
        "States that winning arguments takes priority",
        "States refusal to to drop disputes",
      ],
      "never": [
        "States willingness to let disagreement go",
        "States choice of harmony over being right",
      ],
    },
    "I'd risk too much to uncover a lost bit of knowledge.": {
      "always": [
        "States acceptance of danger for hidden knowledge",
        "States that discovery over safety takes priority",
      ],
      "never": [
        "States willingness to walk away from mystery",
        "States choice of safety over knowledge",
      ],
    },
    "I like keeping secrets and won't share them with anyone.": {
      "always": [
        "States refusal to to reveal secrets",
        "States refusal to answer about direct questions",
      ],
      "never": [
        "States willingness to share hidden information freely",
        "Claims openness about secrets",
      ],
    },
    "I believe that everyone is beneath me.": {
      "always": [
        "Claims superiority over others",
        "States dismissal of others as lesser",
      ],
      "never": [
        "States others are equals",
        "States humility or equality with others",
      ],
    },
    "I hide a truly scandalous secret that could ruin my family forever.": {
      "always": [
        "States intent to protect family reputation",
        "States refusal to answer about questions about scandal",
      ],
      "never": [
        "States revelation of family scandal",
        "States dismissal of family disgrace",
      ],
    },
    "I too often hear veiled insults and threats in every word addressed to me.": {
      "always": [
        "States interpretation of remarks as insults",
        "States accusation that others of hidden threats",
      ],
      "never": [
        "States assumption that innocent wording",
        "States acceptance of criticism without resentment",
      ],
    },
    "I have an insatiable desire for carnal pleasures.": {
      "always": [
        "Talks about sensual indulgence",
        "States admission of desire for pleasure",
      ],
      "never": [
        "States rejection of sensual pleasure",
        "States praise for chastity or restraint",
      ],
    },
    "In fact, the world does revolve around me.": {
      "always": [
        "Frames every issue as centered on themself",
        "Claims own importance above others",
      ],
      "never": [
        "States that others should come before themself",
        "States rejection of special treatment",
      ],
    },
    "By my words and actions, I often bring shame to my family.": {
      "always": [
        "States admission of embarrassing family",
        "States disregard for reputation or family shame",
      ],
      "never": [
        "States intent to protect family honor carefully",
        "States that decorum takes priority",
      ],
    },
    "I am too enamored of ale, wine, and other intoxicants.": {
      "always": [
        "Talks about drinking or intoxicants",
        "States admission of craving intoxication",
      ],
      "never": ["States rejection of intoxicants", "States praise for sobriety"],
    },
    "There's no room for caution in a life lived to the fullest.": {
      "always": [
        "States dismissal of caution",
        "States endorsement of risky living",
      ],
      "never": [
        "States that careful planning is valuable",
        "States rejection of unnecessary risk",
      ],
    },
    "I remember every insult I've received and nurse a silent resentment.": {
      "always": [
        "States memory of past insults",
        "Expresses lingering resentment",
      ],
      "never": [
        "States forgiveness of insults easily",
        "Claims slights are forgotten",
      ],
    },
    "I am slow to trust members of other races, tribes, and societies.": {
      "always": [
        "States distrust of outsiders openly",
        "States that own group takes priority",
      ],
      "never": [
        "States trust in outsiders quickly",
        "States dismissal of group differences",
      ],
    },
    "Violence is my answer to almost any challenge.": {
      "always": [
        "States proposal of violence as solution",
        "States threat of force for problems",
      ],
      "never": [
        "States choice of patient negotiation",
        "States rejection of force as answer",
      ],
    },
    "Don't expect me to save those who can't save themselves.": {
      "always": [
        "States refusal to helping the helpless",
        "States that self-reliance harshly is valuable",
      ],
      "never": [
        "States a promise to to rescue the helpless",
        "Expresses pity for weakness",
      ],
    },
    "I am easily distracted by the promise of information.": {
      "always": [
        "States that new information takes priority",
        "States desire to change the topic toward knowledge",
      ],
      "never": [
        "States intent to ignore intriguing facts",
        "States rejection of learning opportunities",
      ],
    },
    "Most people scream and run when they see a demon. I stop and take notes on its anatomy.": {
      "always": [
        "States treatment of monsters as study subjects",
        "States that observation over fear takes priority",
      ],
      "never": [
        "States rejection of studying dangerous creatures",
        "States choice of flight over knowledge",
      ],
    },
    "Unlocking an ancient mystery is worth the price of a civilization.": {
      "always": [
        "States justification for catastrophe for discovery",
        "States that ancient mysteries take priority over lives",
      ],
      "never": [
        "States intent to protect civilization over knowledge",
        "States rejection of dangerous mysteries",
      ],
    },
    "I overlook obvious solutions in favor of complicated ones.": {
      "always": [
        "States preference for elaborate explanations",
        "States rejection of simple solutions",
      ],
      "never": [
        "States acceptance of obvious answer first",
        "States that simplicity is valuable",
      ],
    },
    "I speak without really thinking through my words, invariably insulting others.": {
      "always": [
        "States or makes blunt insulting remarks",
        "States admission of speaking without thinking",
      ],
      "never": [
        "States intent to filter words carefully",
        "States that politeness takes priority",
      ],
    },
    "I can't keep a secret to save my life, or anyone else's.": {
      "always": [
        "States revelation of confidential information",
        "States admission of inability to keep secrets",
      ],
      "never": [
        "States intent to keep secrets reliably",
        "States refusal to to share confidential facts",
      ],
    },
    "I follow orders, even if I think they're wrong.": {
      "always": [
        "States obedience to orders despite doubt",
        "States that command ranks command above judgment",
      ],
      "never": [
        "States refusal to questionable orders",
        "States that conscience over command takes priority",
      ],
    },
    "I'll say anything to avoid having to do extra work.": {
      "always": [
        "States or makes excuses to avoid work",
        "States argument against extra labor",
      ],
      "never": [
        "States willingness to volunteer for extra work",
        "States admission of laziness directly",
      ],
    },
    "Once someone questions my courage, I never back down.": {
      "always": [
        "States a response to courage challenges",
        "States refusal to retreat after being called cowardly",
      ],
      "never": [
        "States intent to ignore insults to courage",
        "States willingness to back down after challenge",
      ],
    },
    "Once I start drinking, it's hard for me to stop.": {
      "always": [
        "States admission of difficulty stopping drink",
        "States desire for more after drinking begins",
      ],
      "never": [
        "Claims ability to stop drinking easily",
        "States rejection of another drink after starting",
      ],
    },
    "I can't help but pocket loose coins and other trinkets I come across.": {
      "always": [
        "Talks about taking small valuables",
        "States justification for petty theft",
      ],
      "never": [
        "States intent to leave loose valuables alone",
        "States rejection of taking unattended coins",
      ],
    },
    "My pride will probably lead to my destruction.": {
      "always": [
        "States that pride over safety takes priority",
        "States refusal to to admit weakness",
      ],
      "never": [
        "States acceptance of humiliation calmly",
        "States choice of caution over pride",
      ],
    },
    "The monstrous enemy we faced in battle still leaves me quivering with fear.": {
      "always": [
        "Talks fearfully about past enemy",
        "States admission of battle trauma",
      ],
      "never": [
        "Talks about the enemy casually",
        "Claims no fear of similar monsters",
      ],
    },
    "I have little respect for anyone who is not a proven warrior.": {
      "always": [
        "States dismissal of non-warriors",
        "States that proven combat ability is valuable",
      ],
      "never": [
        "States respect for untested people equally",
        "States that noncombatants above warriors is valuable",
      ],
    },
    "I made a terrible mistake in battle that cost many lives.": {
      "always": [
        "States admission of guilt over battle mistake",
        "States a link between own error to deaths",
      ],
      "never": [
        "States they would speak lightly of command mistakes",
        "States denial of responsibility for battle deaths",
      ],
    },
    "My hatred of my enemies is blinding and unreasoning.": {
      "always": [
        "States that enemies are evil or contemptible",
        "States rejection of mercy toward enemies",
      ],
      "never": [
        "States willingness to consider enemies fairly",
        "States willingness to offer mercy to hated enemies",
      ],
    },
    "I obey the law, even if the law causes misery.": {
      "always": [
        "States that law over mercy takes priority",
        "States defense of harmful laws",
      ],
      "never": [
        "States willingness to break law for compassion",
        "States rejection of cruel law as invalid",
      ],
    },
    "I'd rather eat my armor than admit when I'm wrong.": {
      "always": [
        "States denial of being wrong",
        "States refusal to to apologize",
      ],
      "never": [
        "States admission of error plainly",
        "States willingness to change position after correction",
      ],
    },
    "If I'm outnumbered, I will run away from a fight.": {
      "always": [
        "States that outnumbered fights require escape",
        "States that retreat against bad odds takes priority",
      ],
      "never": [
        "States a promise to to fight while outnumbered",
        "States rejection of fleeing bad odds",
      ],
    },
    "Gold seems like a lot of money to me, and I'll do just about anything for more of it.": {
      "always": [
        "States fixation on small amounts of gold",
        "States justification for wrongdoing for money",
      ],
      "never": [
        "States that gold is not very tempting or important",
        "States rejection of cash incentives",
      ],
    },
    "I will never fully trust anyone other than myself.": {
      "always": [
        "States only self can be trusted",
        "States withholding of full trust from others",
      ],
      "never": [
        "States trust in another completely",
        "States full reliance on someone else",
      ],
    },
    "I'd rather kill someone in their sleep than fight fair.": {
      "always": [
        "States preference for unfair advantage",
        "States rejection of honorable fighting",
      ],
      "never": [
        "States insistence on fair fights",
        "States condemnation of killing vulnerable targets",
      ],
    },
    "It's not stealing if I need it more than someone else.": {
      "always": [
        "States justification for theft by need",
        "States that need over property takes priority",
      ],
      "never": [
        "States that property rights matter despite personal need",
        "States that need-based theft is wrong",
      ],
    },
    "People who can't take care of themselves get what they deserve.": {
      "always": [
        "States blame of helpless people",
        "States rejection of pity for weakness",
      ],
      "never": [
        "States sympathy for helpless people",
        "States support for protecting the weak",
      ],
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
    first = random.choice(DWARF_NAMES_MALE if gender_key == "m" else DWARF_NAMES_FEMALE)
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
    valid = [(i + 1, text, tag) for i, (text, tag) in enumerate(ideals) if tag == "Any"]

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
