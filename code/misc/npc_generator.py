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

ATTITUDES = ["hostile", "friendly", "indifferent"]

LIFESTYLES = [
  "wretched",
  "poor",
  "comfortable",
  "wealthy",
  "aristocratic",
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
  "gender": {
    "m": {"do": [], "avoid": []},
    "f": {"do": [], "avoid": []},
  },
  "ancestry": {
    "human": {
      "do": ["adapt quickly", "blend with others"],
      "avoid": ["cling to tradition", "act rigid"],
    },
    "dwarf": {
      "do": ["value craft", "endure hardship"],
      "avoid": ["cut corners", "show weakness"],
    },
    "elf": {
      "do": ["observe first", "think long-term"],
      "avoid": ["rush", "act impulsively"],
    },
    "halfling": {
      "do": ["seek comfort", "stay approachable"],
      "avoid": ["take big risks", "intimidate others"],
    },
  },
  "wealth": {
    "wretched": {
      "do": ["scavenge", "survive day-to-day"],
      "avoid": ["waste anything", "plan luxuriously"],
    },
    "poor": {
      "do": ["save resources", "reuse items"],
      "avoid": ["waste", "expect comfort"],
    },
    "comfortable": {
      "do": ["maintain stability", "spend moderately"],
      "avoid": ["risk ruin", "live excessively"],
    },
    "wealthy": {
      "do": ["spend freely", "expect quality"],
      "avoid": ["settle for less", "worry over small cost"],
    },
    "aristocratic": {
      "do": ["command respect", "display refinement"],
      "avoid": ["act common", "lower status"],
    },
  },
  "age": {
    "young": {
      "do": ["act boldly", "seek excitement"],
      "avoid": ["hesitate", "play safe"],
    },
    "adult": {
      "do": ["act decisively", "take responsibility"],
      "avoid": ["act unsure", "avoid duty"],
    },
    "mature": {
      "do": ["weigh options", "trust experience"],
      "avoid": ["rush decisions", "take needless risks"],
    },
    "elder": {
      "do": ["speak with weight", "recall the past"],
      "avoid": ["act rashly", "chase novelty"],
    },
  },
  "role": {
    "acolyte": {
      "do": ["refer to faith", "respect doctrine"],
      "avoid": ["act irreverent", "dismiss belief"],
    },
    "charlatan": {
      "do": ["deceive smoothly", "maintain persona"],
      "avoid": ["tell full truth", "break character"],
    },
    "criminal": {
      "do": ["seek advantage", "avoid law"],
      "avoid": ["trust authority", "act openly"],
    },
    "entertainer": {
      "do": ["engage others", "seek attention"],
      "avoid": ["be dull", "fade into background"],
    },
    "artisan": {
      "do": ["value craft", "work diligently"],
      "avoid": ["rush work", "ignore flaws"],
    },
    "hermit": {
      "do": ["keep distance", "follow routines"],
      "avoid": ["seek crowds", "invite company"],
    },
    "noble": {
      "do": ["assert status", "expect respect"],
      "avoid": ["submit easily", "act beneath station"],
    },
    "outlander": {
      "do": ["trust instincts", "live off the land"],
      "avoid": ["rely on society", "follow custom blindly"],
    },
    "sage": {
      "do": ["analyze", "share knowledge"],
      "avoid": ["act without thought", "ignore facts"],
    },
    "sailor": {
      "do": ["speak plainly", "value crew"],
      "avoid": ["overthink", "stand idle"],
    },
    "soldier": {
      "do": ["follow structure", "act decisively"],
      "avoid": ["hesitate", "reject discipline"],
    },
    "urchin": {
      "do": ["stay alert", "take opportunities"],
      "avoid": ["trust easily", "waste chances"],
    },
  },
  "role_detail": {
    "chance game cheat": {
      "do": ["watch reactions", "manipulate odds"],
      "avoid": ["play fair", "show your method"],
    },
    "selling junk": {
      "do": ["oversell value", "dress trash as treasure"],
      "avoid": ["describe goods honestly", "undercut your pitch"],
    },
    "burglar": {
      "do": ["move quietly", "look for entry and exit"],
      "avoid": ["make noise", "linger after the job"],
    },
    "assassin": {
      "do": ["wait for the right moment", "strike decisively"],
      "avoid": ["draw attention", "fight fairly"],
    },
    "smuggler": {
      "do": ["hide goods", "circumvent inspection"],
      "avoid": ["invite scrutiny", "trust officials"],
    },
    "actor": {
      "do": ["inhabit roles", "heighten expression"],
      "avoid": ["drop character carelessly", "stay emotionally flat"],
    },
    "juggler": {
      "do": ["show dexterity", "keep things moving"],
      "avoid": ["stand still", "appear clumsy"],
    },
    "musician": {
      "do": ["shape mood through sound", "listen for rhythm"],
      "avoid": ["ignore atmosphere", "treat silence carelessly"],
    },
    "alchemist": {
      "do": ["measure carefully", "think in mixtures"],
      "avoid": ["experiment carelessly", "ignore reactions"],
    },
    "cook": {
      "do": ["value nourishment", "think practically"],
      "avoid": ["waste ingredients", "ignore appetite"],
    },
    "painter": {
      "do": ["notice color and form", "frame things aesthetically"],
      "avoid": ["ignore appearance", "treat beauty as trivial"],
    },
    "smith": {
      "do": ["respect durability", "judge workmanship"],
      "avoid": ["accept weakness in craft", "praise shoddy work"],
    },
    "weaver": {
      "do": ["notice patterns", "work patiently"],
      "avoid": ["rush detail", "ignore flaws in structure"],
    },
    "innocently exiled": {
      "do": ["keep to yourself", "carry old grievance quietly"],
      "avoid": ["trust institutions", "rejoin society easily"],
    },
    "isolated workspace": {
      "do": ["protect your solitude", "value uninterrupted thought"],
      "avoid": ["welcome interruption", "work in crowds"],
    },
    "guarded ruin or relict": {
      "do": ["watch over the site", "protect old things"],
      "avoid": ["allow trespass lightly", "share secrets freely"],
    },
    "guide": {
      "do": ["read the way ahead", "lead by practical knowledge"],
      "avoid": ["wander blindly", "depend on city knowledge"],
    },
    "bounty_hunter": {
      "do": ["track relentlessly", "size others up"],
      "avoid": ["forget a target", "trust quarry easily"],
    },
    "hunter_gatherer": {
      "do": ["notice resources", "live by terrain"],
      "avoid": ["overconsume", "ignore scarcity"],
    },
    "astronomer": {
      "do": ["look upward", "think in cycles and patterns"],
      "avoid": ["ignore signs in the heavens", "focus only on the immediate"],
    },
    "professor": {
      "do": ["explain concepts", "organize knowledge"],
      "avoid": ["leave ideas vague", "skip analysis"],
    },
    "scribe": {
      "do": ["record precisely", "care about wording"],
      "avoid": ["speak carelessly", "treat records loosely"],
    },
    "captain": {
      "do": ["take command", "think of the whole ship"],
      "avoid": ["defer too easily", "lose authority"],
    },
    "first_mate": {
      "do": ["enforce discipline", "support command structure"],
      "avoid": ["undermine leadership", "let slackness spread"],
    },
    "quartermaster": {
      "do": ["track shares and supplies", "think in fairness and logistics"],
      "avoid": ["lose count", "ignore distribution"],
    },
    "officer": {
      "do": ["issue orders", "maintain hierarchy"],
      "avoid": ["blur rank", "show indecision"],
    },
    "infantry": {
      "do": ["endure pressure", "hold the line"],
      "avoid": ["break formation", "seek glory over duty"],
    },
    "cavalry": {
      "do": ["value mobility", "strike with momentum"],
      "avoid": ["get bogged down", "fight too statically"],
    },
  },
  "ideal": {
    "Tradition. The ancient traditions of worship and sacrifice must be preserved and upheld.": {
      "do": ["preserve rites", "defer to tradition"],
      "avoid": ["discard custom", "welcome change lightly"],
    },
    "Charity. I always try to help those in need, no matter what the personal cost.": {
      "do": ["aid the needy", "accept personal cost"],
      "avoid": ["ignore suffering", "withhold help"],
    },
    "Change. We must help bring about the changes the gods are constantly working in the world.": {
      "do": ["embrace change", "push renewal"],
      "avoid": ["cling to stasis", "preserve things blindly"],
    },
    "Power. I hope to one day rise to the top of my faith's religious hierarchy.": {
      "do": ["seek advancement", "respect rank"],
      "avoid": ["ignore status", "surrender ambition"],
    },
    "Faith. I trust that my deity will guide my actions. I have faith that if I work hard, things will go well.": {
      "do": ["trust divine guidance", "work diligently"],
      "avoid": ["despair quickly", "act without faith"],
    },
    "Aspiration. I seek to prove myself worthy of my god's favor by matching my actions against teachings.": {
      "do": ["measure self against teachings", "strive to improve"],
      "avoid": ["act carelessly", "settle for less"],
    },
    "Independence. I am a free spirit—no one tells me what to do.": {
      "do": ["resist control", "act freely"],
      "avoid": ["submit easily", "accept restraint"],
    },
    "Fairness. I never target people who can't afford to lose a few coins.": {
      "do": ["choose marks selectively", "observe limits"],
      "avoid": ["prey on the desperate", "take everything"],
    },
    "Charity. I distribute the money I acquire to the people who really need it.": {
      "do": ["share gains", "help the needy"],
      "avoid": ["hoard wealth", "ignore hardship"],
    },
    "Creativity. I never run the same con twice.": {
      "do": ["invent new angles", "adapt schemes"],
      "avoid": ["repeat stale tricks", "be predictable"],
    },
    "Friendship. Material goods come and go. Bonds of friendship last forever.": {
      "do": ["protect friends", "value loyalty"],
      "avoid": ["trade friends for profit", "treat bonds lightly"],
    },
    "Aspiration. I'm determined to make something of myself.": {
      "do": ["push upward", "seek a better station"],
      "avoid": ["accept mediocrity", "give up"],
    },
    "Honor. I don't steal from others in the trade.": {
      "do": ["respect professional bounds", "keep underworld codes"],
      "avoid": ["betray fellow criminals", "steal from your own circle"],
    },
    "Freedom. Chains are meant to be broken, as are those who would forge them.": {
      "do": ["break constraints", "oppose captors"],
      "avoid": ["accept domination", "submit quietly"],
    },
    "Charity. I steal from the wealthy so that I can help people in need.": {
      "do": ["target the rich", "aid the poor"],
      "avoid": ["prey on the needy", "keep all spoils"],
    },
    "Greed. I will do whatever it takes to become wealthy.": {
      "do": ["chase profit", "take lucrative risks"],
      "avoid": ["pass up gain", "act generously without reason"],
    },
    "People. I'm loyal to my friends, not to ideals.": {
      "do": ["stand by allies", "choose people over principle"],
      "avoid": ["sacrifice friends for doctrine", "moralize abstractly"],
    },
    "Redemption. There's a spark of good in everyone.": {
      "do": ["look for better in others", "allow second chances"],
      "avoid": ["write people off entirely", "choose cruelty first"],
    },
    "Beauty. When I perform, I make the world better than it was.": {
      "do": ["elevate the moment", "pursue beauty"],
      "avoid": ["be crude without purpose", "treat art as empty"],
    },
    "Tradition. The stories, legends, and songs of the past must never be forgotten.": {
      "do": ["preserve old tales", "honor inherited art"],
      "avoid": ["discard the past", "mock tradition lightly"],
    },
    "Creativity. The world is in need of new ideas and bold action.": {
      "do": ["invent boldly", "push novelty"],
      "avoid": ["repeat convention", "play safe"],
    },
    "Greed. I'm only in it for the money and fame.": {
      "do": ["seek applause", "chase profit"],
      "avoid": ["perform for free", "ignore renown"],
    },
    "People. I like seeing the smiles on people's faces when I perform.": {
      "do": ["delight audiences", "read the room"],
      "avoid": ["ignore crowd feeling", "alienate without cause"],
    },
    "Honesty. Art should reflect the soul; it should come from within.": {
      "do": ["speak sincerely through art", "value authenticity"],
      "avoid": ["fake feeling", "perform hollowly"],
    },
    "Community. It is the duty of all civilized people to strengthen the bonds of community.": {
      "do": ["support the community", "strengthen social bonds"],
      "avoid": ["sow division", "abandon civic duty"],
    },
    "Generosity. My talents were given to me so that I could use them to benefit the world.": {
      "do": ["use craft to help", "share skill"],
      "avoid": ["hoard talent", "withhold aid selfishly"],
    },
    "Freedom. Everyone should be free to pursue their own livelihood.": {
      "do": ["respect independence", "defend self-direction"],
      "avoid": ["control livelihoods", "accept coercion lightly"],
    },
    "Greed. I'm only in it for the money.": {
      "do": ["prioritize profit", "price for advantage"],
      "avoid": ["work charitably", "ignore payment"],
    },
    "People. I'm committed to the people I care about, not to ideals.": {
      "do": ["support your circle", "choose loved ones first"],
      "avoid": ["sacrifice people for principles", "moralize abstractly"],
    },
    "Aspiration. I work hard to be the best there is at my craft.": {
      "do": ["pursue mastery", "refine skill constantly"],
      "avoid": ["accept shoddy work", "settle for average"],
    },
    "Greater Good. My gifts are meant to be shared with all, not used for my own benefit.": {
      "do": ["share gifts", "serve others"],
      "avoid": ["hoard benefits", "act selfishly"],
    },
    "Logic. Emotions must not cloud our sense of what is right and true.": {
      "do": ["reason carefully", "value truth over feeling"],
      "avoid": ["act emotionally", "ignore evidence"],
    },
    "Free Thinking. Inquiry and curiosity are the pillars of progress.": {
      "do": ["question freely", "pursue inquiry"],
      "avoid": ["accept dogma blindly", "fear difficult questions"],
    },
    "Power. Solitude and contemplation are paths toward mystical or magical power.": {
      "do": ["seek inner power", "guard your focus"],
      "avoid": ["waste solitude", "share power freely"],
    },
    "Live and Let Live. Meddling in the affairs of others only causes trouble.": {
      "do": ["interfere little", "let others choose"],
      "avoid": ["intrude", "force outcomes"],
    },
    "Self-Knowledge. If you know yourself, there's nothing left to know.": {
      "do": ["reflect inwardly", "seek self-understanding"],
      "avoid": ["ignore inner motives", "live thoughtlessly"],
    },
    "Respect. Respect is due to me because of my position, but all people deserve dignity.": {
      "do": ["carry yourself with dignity", "treat others as worthy of respect"],
      "avoid": ["grovel", "degrade others casually"],
    },
    "Responsibility. It is my duty to respect the authority of those above me.": {
      "do": ["honor duty", "defer to rightful authority"],
      "avoid": ["defy hierarchy lightly", "neglect obligation"],
    },
    "Independence. I must prove that I can handle myself without coddling from my family.": {
      "do": ["prove self-reliance", "reject coddling"],
      "avoid": ["lean on family protection", "appear helpless"],
    },
    "Power. If I can attain more power, no one will tell me what to do.": {
      "do": ["seek influence", "expand control"],
      "avoid": ["accept limits", "remain subordinate willingly"],
    },
    "Family. Blood runs thicker than water.": {
      "do": ["protect kin", "put family first"],
      "avoid": ["betray family", "treat blood ties lightly"],
    },
    "Noble Obligation. It is my duty to protect and care for the people beneath me.": {
      "do": ["protect dependents", "act as steward"],
      "avoid": ["abuse station", "ignore those in your care"],
    },
    "Change. Life is like the seasons, in constant change, and we must change with it.": {
      "do": ["adapt with circumstances", "accept change"],
      "avoid": ["cling stubbornly", "fight every shift"],
    },
    "Greater Good. It is each person's responsibility to make the most happiness for the whole tribe.": {
      "do": ["serve the group", "think of the whole"],
      "avoid": ["act selfishly", "ignore group welfare"],
    },
    "Honor. If I dishonor myself, I dishonor my whole clan.": {
      "do": ["guard your honor", "act for clan reputation"],
      "avoid": ["shame yourself", "betray clan standards"],
    },
    "Might. The strongest are meant to rule.": {
      "do": ["respect strength", "assert dominance"],
      "avoid": ["submit to weakness", "pity the unfit too quickly"],
    },
    "Nature. The natural world is more important than all constructs of civilization.": {
      "do": ["favor the natural world", "distrust overcivilization"],
      "avoid": ["revere cities over nature", "treat nature as trivial"],
    },
    "Glory. I must earn glory in battle, for myself and my clan.": {
      "do": ["seek renown", "face worthy trials"],
      "avoid": ["shrink from honor", "choose obscurity"],
    },
    "Knowledge. The path to power and self-improvement is through knowledge.": {
      "do": ["pursue learning", "value understanding"],
      "avoid": ["dismiss knowledge", "remain ignorant by choice"],
    },
    "Beauty. What is beautiful points us beyond itself toward what is true.": {
      "do": ["seek truth through beauty", "notice elegance"],
      "avoid": ["dismiss beauty as useless", "embrace ugliness carelessly"],
    },
    "Logic. Emotions must not cloud our logical thinking.": {
      "do": ["reason clearly", "separate feeling from judgment"],
      "avoid": ["argue emotionally", "ignore logic"],
    },
    "No Limits. Nothing should fetter the infinite possibility inherent in all existence.": {
      "do": ["push boundaries", "reject imposed limits"],
      "avoid": ["accept restriction", "close off possibility"],
    },
    "Power. Knowledge is the path to power and domination.": {
      "do": ["seek useful knowledge", "use learning to gain leverage"],
      "avoid": ["share power freely", "study aimlessly"],
    },
    "Self-Improvement. The goal of a life of study is the betterment of oneself.": {
      "do": ["study to improve", "discipline the mind"],
      "avoid": ["stagnate", "waste learning"],
    },
    "Respect. The thing that keeps a ship together is mutual respect between captain and crew.": {
      "do": ["respect shipmates", "value mutual trust"],
      "avoid": ["undermine the crew", "treat others with contempt"],
    },
    "Fairness. We all do the work, so we all share in the rewards.": {
      "do": ["divide rewards fairly", "value shared labor"],
      "avoid": ["take more than your share", "exploit crewmates"],
    },
    "Freedom. The sea is freedom—the freedom to go anywhere and do anything.": {
      "do": ["seek open horizons", "value freedom of movement"],
      "avoid": ["submit to confinement", "accept narrow limits"],
    },
    "Mastery. I'm a predator, and the other ships on the sea are my prey.": {
      "do": ["dominate rivals", "hunt advantage"],
      "avoid": ["show weakness", "let prey escape lightly"],
    },
    "People. I'm committed to my crewmates, not to ideals.": {
      "do": ["back your crew", "choose shipmates over abstractions"],
      "avoid": [
        "sacrifice crewmates for principle",
        "preach ideals over loyalty",
      ],
    },
    "Aspiration. Someday, I'll own my own ship and chart my own destiny.": {
      "do": ["seek command", "work toward independence"],
      "avoid": ["accept permanent subordination", "drift without aim"],
    },
    "Greater Good. Our lot is to lay down our lives in defense of others.": {
      "do": ["protect others", "accept sacrifice"],
      "avoid": ["abandon the vulnerable", "prioritize self-preservation always"],
    },
    "Responsibility. I do what I must and obey just authority.": {
      "do": ["fulfill duty", "obey just command"],
      "avoid": ["shirk duty", "defy rightful authority lightly"],
    },
    "Independence. When people follow orders blindly, they embrace a kind of tyranny.": {
      "do": ["question blindly given orders", "preserve autonomy"],
      "avoid": ["submit without thought", "praise tyranny"],
    },
    "Might. In life as in war, the stronger force wins.": {
      "do": ["respect strength", "press advantage"],
      "avoid": ["mistake mercy for strategy", "ignore power"],
    },
    "Live and Let Live. Ideals aren't worth killing over.": {
      "do": ["avoid pointless conflict", "treat doctrine cautiously"],
      "avoid": ["kill for abstractions", "escalate ideology readily"],
    },
    "Nation. My city, nation, or people are all that matter.": {
      "do": ["serve your people", "put nation first"],
      "avoid": ["betray homeland", "treat loyalty lightly"],
    },
    "Respect. All people, rich or poor, deserve respect.": {
      "do": ["treat others as people", "defend dignity"],
      "avoid": ["worship status", "despise the lowly"],
    },
    "Community. We have to take care of each other, because no one else is going to do it.": {
      "do": ["protect your own", "share burdens"],
      "avoid": ["abandon neighbors", "wait for outside rescue"],
    },
    "Change. The low are lifted up, and the high and mighty are brought down.": {
      "do": ["favor upheaval", "challenge the powerful"],
      "avoid": ["preserve unfair order", "accept hierarchy meekly"],
    },
    "Retribution. The rich need to be shown what life and death are like in the gutters.": {
      "do": ["punish the privileged", "nurture vengeance"],
      "avoid": ["forgive the rich easily", "respect comfort"],
    },
    "People. I help the people who help me—that's what keeps us alive.": {
      "do": ["repay aid", "keep mutual loyalties"],
      "avoid": ["help ingrates freely", "forget who stood by you"],
    },
    "Aspiration. I'm going to prove that I'm worthy of a better life.": {
      "do": ["strive upward", "prove your worth"],
      "avoid": ["accept your lot", "settle into despair"],
    },
  },
  "alignment": {
    "LG": {
      "do": ["uphold justice", "act with honor"],
      "avoid": ["break rightful order", "act selfishly"],
    },
    "NG": {
      "do": ["help others", "reduce harm"],
      "avoid": ["cause suffering", "ignore need"],
    },
    "CG": {
      "do": ["act freely", "oppose oppression"],
      "avoid": ["submit to unjust control", "obey blindly"],
    },
    "LN": {
      "do": ["follow structure", "enforce order"],
      "avoid": ["act randomly", "undermine systems"],
    },
    "N": {
      "do": ["avoid extremes", "stay pragmatic"],
      "avoid": ["commit fanatically", "take absolute sides"],
    },
    "CN": {
      "do": ["act on impulse", "value freedom"],
      "avoid": ["commit to structure", "accept restraint"],
    },
    "LE": {
      "do": ["use rules for gain", "control others"],
      "avoid": ["act randomly", "lose authority"],
    },
    "NE": {
      "do": ["pursue self-interest", "manipulate"],
      "avoid": ["help freely", "sacrifice for others"],
    },
    "CE": {
      "do": ["follow destructive impulse", "threaten chaos"],
      "avoid": ["respect order", "show restraint"],
    },
  },
  "flaw": {
    "I judge others harshly, and myself even more severely.": {
      "do": ["criticize faults", "hold yourself to strict standards"],
      "avoid": ["forgive easily", "accept imperfection lightly"],
      "when": ["witnessing failure", "judging conduct", "being judged"],
    },
    "I put too much trust in those who wield power within my temple's hierarchy.": {
      "do": ["defer to religious authority", "trust rank too readily"],
      "avoid": ["question temple leaders", "suspect clerical power"],
      "when": [
        "speaking with superiors",
        "receiving orders from clergy",
        "temple hierarchy is involved",
      ],
    },
    "My piety sometimes leads me to blindly trust those that profess faith in my god.": {
      "do": ["trust shared believers", "lower your guard before the pious"],
      "avoid": ["test professed faith carefully", "doubt fellow worshippers"],
      "when": [
        "someone invokes your god",
        "meeting a fellow believer",
        "religious loyalty is claimed",
      ],
    },
    "I am inflexible in my thinking.": {
      "do": ["cling to your view", "reject compromise"],
      "avoid": ["adapt easily", "entertain alternatives"],
      "when": [
        "challenged in belief",
        "forced to compromise",
        "facing moral disagreement",
      ],
    },
    "I am suspicious of strangers and expect the worst of them.": {
      "do": ["assume bad intent", "keep strangers at distance"],
      "avoid": ["trust newcomers", "offer easy warmth"],
      "when": [
        "meeting strangers",
        "hearing unfamiliar claims",
        "being approached unexpectedly",
      ],
    },
    "Once I pick a goal, I become obsessed with it to the detriment of everything else in my life.": {
      "do": ["fixate on the goal", "neglect other concerns"],
      "avoid": ["rebalance priorities", "let distractions in"],
      "when": [
        "pursuing a chosen objective",
        "progress is within reach",
        "the goal is obstructed",
      ],
    },
    "I can't resist a pretty face.": {
      "do": ["soften toward beauty", "show off and indulge"],
      "avoid": ["stay guarded", "refuse charm"],
      "when": [
        "meeting an attractive person",
        "being flirted with",
        "beauty is used persuasively",
      ],
    },
    "I'm always in debt. I spend my ill-gotten gains on decadent luxuries faster than I bring them in.": {
      "do": ["chase quick money", "justify excess"],
      "avoid": ["save prudently", "live modestly"],
      "when": ["money is short", "luxury is offered", "debts are mentioned"],
    },
    "I'm convinced that no one could ever fool me the way I fool others.": {
      "do": ["act overconfident", "dismiss the chance of being deceived"],
      "avoid": ["check for traps", "admit vulnerability"],
      "when": [
        "a deal is proposed",
        "someone flatters you",
        "a con may be in play",
      ],
    },
    "I'm too greedy for my own good. I can't resist taking a risk if there's money involved.": {
      "do": ["take profit-driven risks", "fixate on payout"],
      "avoid": ["walk away from gain", "choose safety first"],
      "when": [
        "money is at stake",
        "a risky scheme appears profitable",
        "treasure is offered",
      ],
    },
    "I can't resist swindling people who are more powerful than me.": {
      "do": ["target the mighty", "prove your daring"],
      "avoid": ["leave the powerful alone", "show restraint"],
      "when": [
        "facing a wealthy or powerful person",
        "seeing a chance to con authority",
        "being slighted by status",
      ],
    },
    "I hate to admit it, but I'll run and preserve my own hide if the going gets tough.": {
      "do": ["look for escape", "save yourself first"],
      "avoid": ["stand firm under pressure", "risk yourself for others"],
      "when": [
        "danger escalates",
        "violence seems imminent",
        "the plan goes bad",
      ],
    },
    "When I see something valuable, I can't think about anything but how to steal it.": {
      "do": ["fixate on valuables", "plot theft immediately"],
      "avoid": ["ignore treasure", "focus on other priorities"],
      "when": ["spotting wealth", "handling valuables", "seeing something rare"],
    },
    "When faced with a choice between money and my friends, I usually choose the money.": {
      "do": ["favor profit over loyalty", "rationalize betrayal"],
      "avoid": ["sacrifice money for friends", "choose loyalty easily"],
      "when": [
        "forced to choose between coin and companions",
        "a payoff tempts betrayal",
        "friends cost you profit",
      ],
    },
    "If there's a plan, I'll forget it. If I don't forget it, I'll ignore it.": {
      "do": ["improvise recklessly", "deviate from plans"],
      "avoid": ["follow the agreed strategy", "respect preparation"],
      "when": [
        "a plan is explained",
        "timing matters",
        "others expect coordination",
      ],
    },
    "I have a tell that reveals when I'm lying.": {
      "do": ["grow visibly strained", "overcompensate while deceiving"],
      "avoid": ["lie smoothly", "hide the strain completely"],
      "when": ["you lie", "you conceal guilt", "you bluff under pressure"],
    },
    "I turn tail and run when things look bad.": {
      "do": ["look for exits", "flee early"],
      "avoid": ["stand and fight", "hold the line"],
      "when": ["odds worsen", "violence erupts", "capture seems possible"],
    },
    "An innocent person is in prison for a crime that I committed. I'm okay with that.": {
      "do": ["bury guilt", "deflect blame"],
      "avoid": ["confess freely", "take responsibility willingly"],
      "when": [
        "the crime is mentioned",
        "justice is discussed",
        "the innocent suffers",
      ],
    },
    "I'll do anything to win fame and renown.": {
      "do": ["seek the spotlight", "court attention at all costs"],
      "avoid": ["share credit gladly", "remain unnoticed"],
      "when": [
        "an audience is present",
        "renown is possible",
        "a dramatic opportunity appears",
      ],
    },
    "I'm a sucker for a pretty face.": {
      "do": ["grow indulgent", "try to impress beauty"],
      "avoid": ["keep distance", "stay professionally detached"],
      "when": [
        "meeting an attractive person",
        "being admired",
        "romantic attention appears",
      ],
    },
    "A scandal prevents me from ever going home again.": {
      "do": ["avoid the past", "grow guarded about home"],
      "avoid": ["speak openly of your origins", "return lightly"],
      "when": [
        "home is mentioned",
        "your past is questioned",
        "someone recognizes you",
      ],
    },
    "I once satirized a noble who still wants my head.": {
      "do": ["watch nobles warily", "treat power with nervous wit"],
      "avoid": ["mock aristocrats openly", "forget the danger"],
      "when": [
        "nobility is present",
        "your past performances come up",
        "you are recognized",
      ],
    },
    "I have trouble keeping my true feelings hidden. My sharp tongue lands me in trouble.": {
      "do": ["speak too sharply", "show emotion plainly"],
      "avoid": ["mask feelings well", "hold your tongue"],
      "when": ["angered", "insulted", "emotionally stirred"],
    },
    "Despite my best efforts, I am unreliable to my friends.": {
      "do": ["overpromise", "fail to follow through"],
      "avoid": ["be consistently dependable", "show up reliably"],
      "when": [
        "friends ask for help",
        "commitments pile up",
        "duty conflicts with convenience",
      ],
    },
    "I'll do anything to get my hands on something rare or priceless.": {
      "do": ["covet rarities", "push boundaries to acquire them"],
      "avoid": ["walk away from masterpieces", "settle for the ordinary"],
      "when": [
        "a rare item appears",
        "priceless craft is discussed",
        "acquisition becomes possible",
      ],
    },
    "I'm quick to assume that someone is trying to cheat me.": {
      "do": ["scrutinize terms", "suspect bad faith"],
      "avoid": ["trust bargains easily", "take offers at face value"],
      "when": ["haggling", "making deals", "discussing payment"],
    },
    "No one must ever learn that I once stole money from guild coffers.": {
      "do": ["guard the secret", "steer talk away from the guild"],
      "avoid": ["confess", "invite investigation"],
      "when": [
        "the guild is mentioned",
        "accounts are examined",
        "your past comes under scrutiny",
      ],
    },
    "I'm never satisfied with what I have—I always want more.": {
      "do": ["push for better and more", "remain restless"],
      "avoid": ["be content", "stop at enough"],
      "when": [
        "profit is in reach",
        "comparing yourself to others",
        "new opportunity appears",
      ],
    },
    "I would kill to acquire a noble title.": {
      "do": ["pursue status obsessively", "resent low birth"],
      "avoid": ["accept your station", "treat titles lightly"],
      "when": [
        "nobility is discussed",
        "social rank bars your way",
        "advancement becomes possible",
      ],
    },
    "I'm horribly jealous of anyone who can outshine my handiwork.": {
      "do": ["resent rivals", "undercut superior artisans"],
      "avoid": ["praise competitors freely", "accept being surpassed gracefully"],
      "when": [
        "someone's craft exceeds yours",
        "rivals are praised",
        "comparisons are drawn",
      ],
    },
    "Now that I've returned to the world, I enjoy its delights a little too much.": {
      "do": ["indulge temptation", "linger over pleasures"],
      "avoid": ["show restraint", "return to austerity quickly"],
      "when": [
        "luxury is offered",
        "company is pleasant",
        "worldly delights appear",
      ],
    },
    "I harbor dark, bloodthirsty thoughts that my isolation and meditation failed to quell.": {
      "do": ["turn grim", "entertain violent impulses"],
      "avoid": ["respond gently", "dismiss violent solutions"],
      "when": ["angered", "provoked", "violence becomes possible"],
    },
    "I am dogmatic in my thoughts and philosophy.": {
      "do": ["state certainties strongly", "dismiss opposing views"],
      "avoid": ["bend easily", "treat all views as equal"],
      "when": [
        "your philosophy is challenged",
        "debate arises",
        "someone questions your worldview",
      ],
    },
    "I let my need to win arguments overshadow friendships and harmony.": {
      "do": ["press the point", "argue to win"],
      "avoid": ["let a dispute go", "prioritize peace over being right"],
      "when": ["debating", "being contradicted", "your reasoning is challenged"],
    },
    "I'd risk too much to uncover a lost bit of knowledge.": {
      "do": ["pursue forbidden knowledge", "accept dangerous curiosity"],
      "avoid": ["walk away from mystery", "choose safety over discovery"],
      "when": [
        "ancient secrets appear",
        "hidden lore is hinted at",
        "danger guards knowledge",
      ],
    },
    "I like keeping secrets and won't share them with anyone.": {
      "do": ["withhold truth", "deflect questions"],
      "avoid": ["open up", "reveal what you know freely"],
      "when": [
        "asked about the past",
        "asked about hidden things",
        "pressed for confidences",
      ],
    },
    "I secretly believe that everyone is beneath me.": {
      "do": ["look down on others", "assume superiority"],
      "avoid": ["treat equals as equals", "show humility"],
      "when": [
        "giving orders",
        "being inconvenienced by commoners",
        "status is contested",
      ],
    },
    "I hide a truly scandalous secret that could ruin my family forever.": {
      "do": ["guard the family image", "smother dangerous questions"],
      "avoid": ["speak candidly", "risk exposure lightly"],
      "when": [
        "family reputation is threatened",
        "the past is discussed",
        "someone gets too close to the secret",
      ],
    },
    "I too often hear veiled insults and threats in every word addressed to me.": {
      "do": ["take offense quickly", "read hostility into remarks"],
      "avoid": ["assume good intent", "take words simply"],
      "when": [
        "receiving criticism",
        "hearing ambiguity",
        "someone addresses you formally",
      ],
    },
    "I have an insatiable desire for carnal pleasures.": {
      "do": ["pursue indulgence", "treat temptation weakly"],
      "avoid": ["show discipline", "walk away from pleasure"],
      "when": ["temptation is near", "luxury is available", "desire is stirred"],
    },
    "In fact, the world does revolve around me.": {
      "do": ["center yourself", "expect priority"],
      "avoid": ["share attention", "consider others first"],
      "when": [
        "competing for attention",
        "plans ignore your wishes",
        "you are inconvenienced",
      ],
    },
    "By my words and actions, I often bring shame to my family.": {
      "do": ["act impulsively in public", "speak without restraint"],
      "avoid": ["protect decorum", "guard the family name carefully"],
      "when": [
        "emotion runs high",
        "public attention is present",
        "family expectations are invoked",
      ],
    },
    "I am too enamored of ale, wine, and other intoxicants.": {
      "do": ["seek drink", "linger where intoxication is available"],
      "avoid": ["stay sober readily", "refuse temptation"],
      "when": ["drink is offered", "celebration begins", "stress rises"],
    },
    "There's no room for caution in a life lived to the fullest.": {
      "do": ["rush into risk", "mock hesitation"],
      "avoid": ["plan carefully", "hold back"],
      "when": [
        "danger promises excitement",
        "someone counsels caution",
        "a bold path appears",
      ],
    },
    "I remember every insult I've received and nurse a silent resentment.": {
      "do": ["hold grudges", "store slights quietly"],
      "avoid": ["forgive easily", "forget insult"],
      "when": [
        "old wrongs are recalled",
        "you are slighted",
        "a past offender appears",
      ],
    },
    "I am slow to trust members of other races, tribes, and societies.": {
      "do": ["keep outsiders at arm's length", "trust your own first"],
      "avoid": ["extend quick trust", "open up readily to strangers"],
      "when": [
        "meeting outsiders",
        "entering civilization",
        "others ask for trust",
      ],
    },
    "Violence is my answer to almost any challenge.": {
      "do": ["escalate to force", "treat threat with aggression"],
      "avoid": ["negotiate patiently", "seek subtle solutions"],
      "when": ["challenged", "insulted", "obstacles block your way"],
    },
    "Don't expect me to save those who can't save themselves.": {
      "do": ["withhold rescue", "value self-reliance harshly"],
      "avoid": ["help the helpless freely", "show much pity"],
      "when": [
        "someone begs for rescue",
        "the weak depend on you",
        "effort is required to save others",
      ],
    },
    "I am easily distracted by the promise of information.": {
      "do": ["chase new facts", "lose focus for learning"],
      "avoid": ["stay on task", "ignore intriguing knowledge"],
      "when": [
        "new lore appears",
        "a mystery is hinted at",
        "someone offers information",
      ],
    },
    "Most people scream and run when they see a demon. I stop and take notes on its anatomy.": {
      "do": ["observe the monstrous closely", "treat danger as study material"],
      "avoid": ["flee at once", "react normally to horror"],
      "when": [
        "facing strange creatures",
        "encountering the forbidden",
        "the unknown becomes observable",
      ],
    },
    "Unlocking an ancient mystery is worth the price of a civilization.": {
      "do": [
        "prioritize discovery over safety",
        "justify catastrophic curiosity",
      ],
      "avoid": ["leave mysteries sealed", "weigh human cost first"],
      "when": [
        "ancient secrets are near",
        "warnings forbid inquiry",
        "knowledge requires sacrifice",
      ],
    },
    "I overlook obvious solutions in favor of complicated ones.": {
      "do": ["complicate the problem", "prefer elaborate answers"],
      "avoid": ["take the simple route", "accept the obvious"],
      "when": [
        "solving a problem",
        "offered an easy answer",
        "analysis is needed",
      ],
    },
    "I speak without really thinking through my words, invariably insulting others.": {
      "do": ["blurt observations", "speak too bluntly"],
      "avoid": ["filter your words", "protect feelings carefully"],
      "when": [
        "explaining something",
        "correcting others",
        "speaking under excitement",
      ],
    },
    "I can't keep a secret to save my life, or anyone else's.": {
      "do": ["spill what you know", "speak too freely"],
      "avoid": ["hold confidences", "guard dangerous information"],
      "when": [
        "carrying a secret",
        "being questioned",
        "interesting knowledge comes up",
      ],
    },
    "I follow orders, even if I think they're wrong.": {
      "do": ["obey command", "suppress your doubts"],
      "avoid": ["refuse orders", "assert your judgment over rank"],
      "when": [
        "given a clear order",
        "leadership is present",
        "discipline is tested",
      ],
    },
    "I'll say anything to avoid having to do extra work.": {
      "do": ["make excuses", "talk your way out of labor"],
      "avoid": ["volunteer for burden", "admit laziness plainly"],
      "when": [
        "extra work appears",
        "you are assigned chores",
        "someone asks for help",
      ],
    },
    "Once someone questions my courage, I never back down.": {
      "do": ["prove your bravery", "double down under challenge"],
      "avoid": ["retreat gracefully", "ignore taunts"],
      "when": [
        "your courage is mocked",
        "you are called a coward",
        "reputation is challenged",
      ],
    },
    "Once I start drinking, it's hard for me to stop.": {
      "do": ["keep drinking", "grow loose and careless"],
      "avoid": ["show restraint after starting", "stop early"],
      "when": [
        "you begin drinking",
        "celebration turns rowdy",
        "alcohol flows freely",
      ],
    },
    "I can't help but pocket loose coins and other trinkets I come across.": {
      "do": ["snatch small valuables", "justify petty theft"],
      "avoid": ["leave loose wealth alone", "resist easy taking"],
      "when": [
        "finding unattended trinkets",
        "seeing loose coin",
        "handling another's belongings",
      ],
    },
    "My pride will probably lead to my destruction.": {
      "do": ["refuse slight", "choose pride over caution"],
      "avoid": ["back down quietly", "admit weakness"],
      "when": [
        "your status is challenged",
        "someone insults you",
        "prudence would mean yielding",
      ],
    },
    "The monstrous enemy we faced in battle still leaves me quivering with fear.": {
      "do": ["show shaken fear", "react strongly to reminders"],
      "avoid": ["stay calm before similar threats", "speak of it casually"],
      "when": [
        "facing monstrous foes",
        "hearing battle memories",
        "encountering reminders of the enemy",
      ],
    },
    "I have little respect for anyone who is not a proven warrior.": {
      "do": ["value martial merit", "dismiss the untested"],
      "avoid": ["honor the weak readily", "take noncombatants seriously"],
      "when": [
        "judging others",
        "hearing civilian opinions",
        "leadership is contested",
      ],
    },
    "I made a terrible mistake in battle that cost many lives.": {
      "do": ["carry guilt", "grow grim around command decisions"],
      "avoid": ["speak lightly of war", "trust your judgment easily"],
      "when": [
        "battle is discussed",
        "lives depend on your choices",
        "past campaigns are recalled",
      ],
    },
    "My hatred of my enemies is blinding and unreasoning.": {
      "do": ["demonize foes", "push vengeance over judgment"],
      "avoid": ["show mercy", "hear enemies fairly"],
      "when": [
        "an enemy appears",
        "old foes are mentioned",
        "revenge becomes possible",
      ],
    },
    "I obey the law, even if the law causes misery.": {
      "do": ["submit to law strictly", "enforce order despite suffering"],
      "avoid": ["bend rules for compassion", "break law for mercy"],
      "when": [
        "law conflicts with kindness",
        "authority gives legal order",
        "mercy would require disobedience",
      ],
    },
    "I'd rather eat my armor than admit when I'm wrong.": {
      "do": ["dig in stubbornly", "deny error"],
      "avoid": ["apologize", "change position easily"],
      "when": ["corrected", "proven mistaken", "your judgment is challenged"],
    },
    "If I'm outnumbered, I will run away from a fight.": {
      "do": ["flee bad odds", "look for escape paths"],
      "avoid": ["stand and fight outnumbered", "play the hero"],
      "when": [
        "facing superior numbers",
        "a brawl turns against you",
        "escape is possible",
      ],
    },
    "Gold seems like a lot of money to me, and I'll do just about anything for more of it.": {
      "do": ["fixate on coin", "justify ugly choices for money"],
      "avoid": ["turn down cash", "treat gold casually"],
      "when": [
        "gold is offered",
        "payment is discussed",
        "wealth appears within reach",
      ],
    },
    "I will never fully trust anyone other than myself.": {
      "do": ["keep backup plans", "hold back trust"],
      "avoid": ["rely completely on others", "share full confidence"],
      "when": [
        "someone asks for trust",
        "you depend on others",
        "alliances deepen",
      ],
    },
    "I'd rather kill someone in their sleep than fight fair.": {
      "do": ["favor dirty advantage", "prefer the safe kill"],
      "avoid": ["fight honorably", "risk fairness"],
      "when": [
        "violence is likely",
        "a target is vulnerable",
        "you can strike unfairly",
      ],
    },
    "It's not stealing if I need it more than someone else.": {
      "do": ["justify theft by need", "take what seems necessary"],
      "avoid": ["respect property strictly", "leave needed goods untouched"],
      "when": [
        "you lack essentials",
        "someone has more than enough",
        "survival or comfort is at stake",
      ],
    },
    "People who can't take care of themselves get what they deserve.": {
      "do": ["dismiss weakness", "withhold sympathy"],
      "avoid": ["show pity", "take responsibility for others"],
      "when": [
        "someone helpless asks for aid",
        "the weak fail",
        "rescue would burden you",
      ],
    },
  },
  "attitude": {
    "friendly": {
      "do": ["speak warmly", "invite trust"],
      "avoid": ["snap quickly", "assume hostility"],
    },
    "indifferent": {
      "do": ["stay neutral", "answer plainly"],
      "avoid": ["show strong emotion", "engage deeply"],
    },
    "hostile": {
      "do": ["challenge others", "assume threat"],
      "avoid": ["trust easily", "yield ground"],
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
  block = {"do": [], "avoid": []}
  if is_flaw:
    block["when"] = []
  return block


def _get_rule_block(category: str, trait_value: str) -> Dict[str, List[str]]:
  category_rules = RULES.get(category, {})
  rule_block = category_rules.get(trait_value)

  if rule_block is None:
    return _empty_rule_block(is_flaw=(category == "flaw"))

  safe_block = {
    "do": _ensure_list(rule_block.get("do")),
    "avoid": _ensure_list(rule_block.get("avoid")),
  }

  if category == "flaw":
    safe_block["when"] = _ensure_list(rule_block.get("when"))

  return safe_block


def collect_selected_when(
  character: Dict[str, Any], rules: Dict[str, Any]
) -> List[Dict[str, Any]]:
  """
  Collect all selected rule blocks that contain `when`.
  Returns a flat list so later systems can:
  - inspect all triggers
  - choose one at random
  - know which trait it came from
  """
  selected_traits = [
    ("ancestry", character.get("ancestry")),
    ("age", character.get("age")),
    ("gender", character.get("gender")),
    ("alignment", character.get("alignment")),
    ("wealth", character.get("wealth")),
    ("role", character.get("role")),
    ("role_detail", character.get("role_detail")),
    ("ideal", character.get("ideal")),
    ("flaw", character.get("flaw")),
    ("attitude", character.get("attitude")),
  ]

  results: List[Dict[str, Any]] = []

  for category, key in selected_traits:
    if not key:
      continue

    block = get_rule_block(rules, category, key)
    when_list = block.get("when", [])
    if not when_list:
      continue

    results.append(
      {
        "category": category,
        "trait": key,
        "when": list(when_list),
      }
    )

  return results


def validate_character(character: Dict[str, Any]) -> None:
  required = [
    "name",
    "gender",
    "alignment",
    "ancestry",
    "age",
    "attitude",
    "role",
    "wealth",
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
    "wealth",
    "age",
    "role",
    "role_detail",
    "ideal",
    "alignment",
    "flaw",
    "attitude",
  ]:
    if category not in RULES:
      raise ValueError(f"RULES missing category '{category}'")
    if not isinstance(RULES[category], dict):
      raise ValueError(f"RULES['{category}'] must be a dict")

  for trait_value, block in RULES["flaw"].items():
    if "when" not in block:
      raise ValueError(f"Flaw '{trait_value}' must include a 'when' list.")


# ============================================================================
# CORE BUILDERS
# ============================================================================


def build_character(
  name: str,
  gender: str,
  ancestry: str,
  wealth: str,
  age: str,
  role: str,
  attitude: str,
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
    "attitude": attitude,
    "role": role,
    "wealth": wealth,
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
      "wealth": character["wealth"],
      "age": character["age"],
      "role": character["role"],
      "role_detail": character["role_detail"],
      "ideal": character["ideal"],
      "ideal_axis": character.get("ideal_axis", ""),
      "alignment": character["alignment"],
      "flaw": character["flaw"],
      "attitude": character["attitude"],
    },
    "meta": {
      "role_detail_label": character.get(
        "role_detail_label", get_background_detail_label(character["role"])
      ),
      "array": character.get("array", []),
      "selected_when": character.get("selected_when", []),
    },
    "rules": {
      "gender": _get_rule_block("gender", character["gender"]),
      "ancestry": _get_rule_block("ancestry", character["ancestry"]),
      "wealth": _get_rule_block("wealth", character["wealth"]),
      "age": _get_rule_block("age", character["age"]),
      "role": _get_rule_block("role", character["role"]),
      "role_detail": _get_rule_block("role_detail", character["role_detail"]),
      "ideal": _get_rule_block("ideal", character["ideal"]),
      "alignment": _get_rule_block("alignment", character["alignment"]),
      "flaw": _get_rule_block("flaw", character["flaw"]),
      "attitude": _get_rule_block("attitude", character["attitude"]),
    },
  }


def generate_character() -> Dict[str, Any]:
  gender_idx, gender = choose(GENDERS)
  alignment_idx, alignment = choose(ALIGNMENTS)
  ancestry_idx, ancestry = choose(ANCESTRIES)
  attitude_idx, attitude = choose(ATTITUDES)
  role_idx, role = choose(ROLES)
  wealth_idx, wealth = choose(LIFESTYLES)
  age_idx, age = choose(AGES)

  bg = generate_background_package(role, alignment)

  numeric_array = [
    gender_idx,  # 1
    alignment_idx,  # 2
    ancestry_idx,  # 3
    age_idx,  # 4
    attitude_idx,  # 5
    role_idx,  # 6
    wealth_idx,  # 7
    bg["detail_idx"],  # 8
    bg["ideal_idx"],  # 9
    bg["flaw_idx"],  # 10
  ]

  character = {
    "array": numeric_array,
    "name": random_full_name(ancestry, gender),
    "gender": gender,
    "alignment": alignment,
    "ancestry": ancestry,
    "age": age,
    "attitude": attitude,
    "role": role,
    "wealth": wealth,
    "role_detail_label": bg["role_label"],
    "role_detail": bg["role_detail_text"],
    "ideal": bg["ideal_text"],
    "ideal_axis": bg["ideal_axis"],
    "flaw": bg["flaw_text"],
  }

  character["selected_when"] = collect_selected_when(character, RULES)

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
