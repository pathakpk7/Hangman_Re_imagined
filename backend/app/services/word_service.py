import sqlite3
import os
import random
import hashlib
import json
import re
from typing import Dict, Any, Optional, List
from backend.app.config import settings

PRESET_CATEGORIES = [
    "Technology", "Science", "Nature", "Animals", "Space", "Geography",
    "Food & Cooking", "Sports", "History", "Medicine", "Arts & Culture", "Business"
]

FALLBACK_WORDS = [
    # Technology (10)
    {
        "word": "code", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "Program instructions written by a programmer.",
        "example_sentence": "Engineers write clean ___ to build modern web applications.",
        "synonyms": ["script", "program", "instructions"], "category": "Technology"
    },
    {
        "word": "data", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": True, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "Facts and statistics collected together for reference or analysis.",
        "example_sentence": "The server processed gigabytes of user ___ securely.",
        "synonyms": ["information", "records", "facts"], "category": "Technology"
    },
    {
        "word": "algorithm", "length": 9, "vowel_count": 3, "consonant_count": 6, "has_repeated_letters": False, "frequency": 4.5, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A process or set of rules to be followed in calculations.",
        "example_sentence": "The computer executed an efficient ___ to sort millions of data points.",
        "synonyms": ["procedure", "formula", "routine"], "category": "Technology"
    },
    {
        "word": "hardware", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.3, "difficulty": 2, "part_of_speech": "noun",
        "definition": "The physical components of a computer system.",
        "example_sentence": "Upgrading the graphics ___ improved system performance dramatically.",
        "synonyms": ["equipment", "machinery", "components"], "category": "Technology"
    },
    {
        "word": "encryption", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.8, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The process of encoding data to prevent unauthorized access.",
        "example_sentence": "End-to-end ___ secures message transmission between users.",
        "synonyms": ["encoding", "ciphering", "protection"], "category": "Technology"
    },
    {
        "word": "microprocessor", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "An integrated circuit that contains all the functions of a CPU.",
        "example_sentence": "The multi-core ___ executes billions of cycles per second.",
        "synonyms": ["chip", "cpu", "processor"], "category": "Technology"
    },
    {
        "word": "cybernetics", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.0, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The science of communications and automatic control systems.",
        "example_sentence": "Advanced ___ bridges human biology with mechanical prosthetics.",
        "synonyms": ["automation", "robotics", "bionics"], "category": "Technology"
    },
    {
        "word": "cryptography", "length": 12, "vowel_count": 3, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The practice of securing communication in the presence of adversaries.",
        "example_sentence": "Quantum-resistant ___ protects sensitive financial ledgers.",
        "synonyms": ["ciphers", "steganography", "secret writing"], "category": "Technology"
    },
    {
        "word": "supercomputer", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.5, "difficulty": 5, "part_of_speech": "noun",
        "definition": "A high-performance computer capable of processing complex calculations.",
        "example_sentence": "Scientists used a weather-modeling ___ to predict hurricane trajectories.",
        "synonyms": ["mainframe", "supernode"], "category": "Technology"
    },
    {
        "word": "bandwidth", "length": 9, "vowel_count": 2, "consonant_count": 7, "has_repeated_letters": True, "frequency": 4.1, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The maximum data transfer rate of a network connection.",
        "example_sentence": "High fiber-optic ___ enables smooth ultra-high-definition streaming.",
        "synonyms": ["capacity", "throughput"], "category": "Technology"
    },

    # Science (10)
    {
        "word": "atom", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.7, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The basic unit of a chemical element.",
        "example_sentence": "Protons and neutrons form the central nucleus of an ___.",
        "synonyms": ["particle", "unit", "element"], "category": "Science"
    },
    {
        "word": "cell", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": True, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The smallest structural and functional unit of an organism.",
        "example_sentence": "The microscopic biological ___ is the basic building block of life.",
        "synonyms": ["unit", "corpuscle"], "category": "Science"
    },
    {
        "word": "electron", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.2, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A stable subatomic particle with a charge of negative electricity.",
        "example_sentence": "An ___ orbits the positive atomic nucleus in distinct shells.",
        "synonyms": ["lepton", "particle"], "category": "Science"
    },
    {
        "word": "molecule", "length": 8, "vowel_count": 4, "consonant_count": 4, "has_repeated_letters": True, "frequency": 4.1, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A group of atoms bonded together representing the smallest unit of a compound.",
        "example_sentence": "A water ___ consists of two hydrogen atoms bonded to oxygen.",
        "synonyms": ["compound", "particle"], "category": "Science"
    },
    {
        "word": "photosynthesis", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The biological process by which green plants convert light into chemical energy.",
        "example_sentence": "Plants use sunlight to perform ___ and produce oxygen.",
        "synonyms": ["energy synthesis", "chlorophyll process"], "category": "Science"
    },
    {
        "word": "thermodynamics", "length": 14, "vowel_count": 4, "consonant_count": 10, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The branch of physical science dealing with heat and temperature relations.",
        "example_sentence": "The second law of ___ states that entropy in an isolated system increases.",
        "synonyms": ["heat physics", "energy dynamics"], "category": "Science"
    },
    {
        "word": "quantum", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": True, "frequency": 3.9, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A discrete quantity of energy proportional in magnitude to the frequency of radiation.",
        "example_sentence": "Physicists explored subatomic particle interactions using ___ mechanics.",
        "synonyms": ["unit", "quanta"], "category": "Science"
    },
    {
        "word": "biotechnology", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The exploitation of biological processes for industrial and scientific purposes.",
        "example_sentence": "Modern agricultural ___ engineered drought-resistant crops.",
        "synonyms": ["bioengineering", "genetic technology"], "category": "Science"
    },
    {
        "word": "crystallography", "length": 15, "vowel_count": 4, "consonant_count": 11, "has_repeated_letters": True, "frequency": 2.8, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The branch of science concerned with the structure and properties of crystals.",
        "example_sentence": "X-ray ___ revealed the double-helix geometry of DNA.",
        "synonyms": ["crystal analysis", "x-ray diffraction"], "category": "Science"
    },
    {
        "word": "electromagnetism", "length": 16, "vowel_count": 5, "consonant_count": 11, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The interaction of electric currents or fields and magnetic fields.",
        "example_sentence": "Maxwell unified electricity and magnetism into classic ___ theory.",
        "synonyms": ["magnetic field theory", "electrodynamics"], "category": "Science"
    },

    # Nature (10)
    {
        "word": "leaf", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A flattened structure of a higher plant, typically green and blade-like.",
        "example_sentence": "A green ___ absorbs sunlight to synthesize plant nutrients.",
        "synonyms": ["frond", "blade", "foliage"], "category": "Nature"
    },
    {
        "word": "tree", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": True, "frequency": 5.0, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A woody perennial plant, typically having a single stem or trunk.",
        "example_sentence": "The ancient oak ___ provided shade over the grassy meadow.",
        "synonyms": ["sapling", "timber"], "category": "Nature"
    },
    {
        "word": "forest", "length": 6, "vowel_count": 2, "consonant_count": 4, "has_repeated_letters": False, "frequency": 4.6, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A large area covered chiefly with trees and undergrowth.",
        "example_sentence": "Dense pine trees stretched across the mountain ___.",
        "synonyms": ["woods", "jungle", "woodland"], "category": "Nature"
    },
    {
        "word": "glacier", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": False, "frequency": 3.8, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A slowly moving mass or river of ice formed by the accumulation of snow.",
        "example_sentence": "The massive alpine ___ carved a deep valley over millennia.",
        "synonyms": ["ice sheet", "icefield"], "category": "Nature"
    },
    {
        "word": "biodiversity", "length": 12, "vowel_count": 6, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.5, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The variety of plant and animal life in a particular habitat.",
        "example_sentence": "The tropical rainforest possesses incredible biological ___.",
        "synonyms": ["ecosystem variety", "nature richness"], "category": "Nature"
    },
    {
        "word": "avalanche", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A mass of snow, ice, and rocks falling rapidly down a mountainside.",
        "example_sentence": "Warnings were issued after a sudden snow ___ blocked the pass.",
        "synonyms": ["snowslide", "landslide"], "category": "Nature"
    },
    {
        "word": "precipitation", "length": 13, "vowel_count": 6, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "Rain, snow, sleet, or hail that falls to the ground.",
        "example_sentence": "Heavy seasonal ___ restored water levels in coastal reservoirs.",
        "synonyms": ["rainfall", "downpour", "sleet"], "category": "Nature"
    },
    {
        "word": "deforestation", "length": 13, "vowel_count": 6, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The action of clearing a wide area of trees.",
        "example_sentence": "Environmental policies aim to combat illegal forest ___.",
        "synonyms": ["logging", "clearance"], "category": "Nature"
    },
    {
        "word": "photosynthetic", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 5, "part_of_speech": "adjective",
        "definition": "Relating to or involved in the synthesis of compounds with light.",
        "example_sentence": "Microscopic algae perform vital ___ activity in oceans.",
        "synonyms": ["light-synthesizing"], "category": "Nature"
    },
    {
        "word": "desertification", "length": 15, "vowel_count": 7, "consonant_count": 8, "has_repeated_letters": True, "frequency": 2.7, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The process by which fertile land becomes desert.",
        "example_sentence": "Severe drought and overgrazing accelerated arid land ___.",
        "synonyms": ["soil degradation", "aridification"], "category": "Nature"
    },

    # Animals (10)
    {
        "word": "lion", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A large wild cat of the genus Panthera native to Africa and India.",
        "example_sentence": "The male ___ let out a loud roar across the savanna.",
        "synonyms": ["feline", "predator"], "category": "Animals"
    },
    {
        "word": "bear", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A large heavy mammal with thick fur and a short tail.",
        "example_sentence": "A grizzly ___ fished for salmon in the clear river stream.",
        "synonyms": ["grizzly", "beast"], "category": "Animals"
    },
    {
        "word": "chameleon", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.7, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A reptile known for changing color to blend into its environment.",
        "example_sentence": "The small ___ blended seamlessly into the tree branch.",
        "synonyms": ["lizard", "adapter"], "category": "Animals"
    },
    {
        "word": "flamingo", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": False, "frequency": 3.8, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A tall wading bird with bright pink feathers and long legs.",
        "example_sentence": "A flock of pink ___ stood gracefully in shallow lake waters.",
        "synonyms": ["wader", "pink bird"], "category": "Animals"
    },
    {
        "word": "salamander", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 3, "part_of_speech": "noun",
        "definition": "An amphibian resembling a lizard with damp scaleless skin.",
        "example_sentence": "The spotted ___ hid under moist decay in the forest soil.",
        "synonyms": ["amphibian", "newt"], "category": "Animals"
    },
    {
        "word": "hippopotamus", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "A large thick-skinned African mammal living chiefly in rivers.",
        "example_sentence": "The massive ___ submerged its body to keep cool in midday heat.",
        "synonyms": ["hippo", "river horse"], "category": "Animals"
    },
    {
        "word": "invertebrate", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "An animal lacking a backbone, such as an arthropod or mollusk.",
        "example_sentence": "Jellyfish and octopuses belong to marine ___ classifications.",
        "synonyms": ["boneless creature", "mollusk"], "category": "Animals"
    },
    {
        "word": "ornithology", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.0, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The scientific study of birds.",
        "example_sentence": "Field experts in ___ documented rare migratory songbird routes.",
        "synonyms": ["bird study", "avian science"], "category": "Animals"
    },
    {
        "word": "entomology", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The branch of zoology concerned with the study of insects.",
        "example_sentence": "A researcher in ___ cataloged rare rainforest beetle species.",
        "synonyms": ["insect science", "bug study"], "category": "Animals"
    },
    {
        "word": "cheetah", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A large spotted cat of Africa and southwestern Asia, the fastest land animal.",
        "example_sentence": "The agile ___ sprinted across the plain to catch its prey.",
        "synonyms": ["sprinter cat", "feline"], "category": "Animals"
    },

    # Space (10)
    {
        "word": "star", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 5.1, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A luminous point in the night sky that is a large, remote incandescent body.",
        "example_sentence": "A bright evening ___ shone clearly above the horizon.",
        "synonyms": ["sun", "sunlet", "luminary"], "category": "Space"
    },
    {
        "word": "moon", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": True, "frequency": 5.0, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The natural satellite of the earth, visible by reflected light from the sun.",
        "example_sentence": "The full ___ illuminated the quiet countryside at midnight.",
        "synonyms": ["satellite", "lunar body"], "category": "Space"
    },
    {
        "word": "astronomy", "length": 9, "vowel_count": 3, "consonant_count": 6, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 2, "part_of_speech": "noun",
        "definition": "The scientific study of stars, planets, galaxies, and celestial bodies.",
        "example_sentence": "She studied ___ through a powerful mountain telescope.",
        "synonyms": ["stargazing", "astrophysics"], "category": "Space"
    },
    {
        "word": "asteroid", "length": 8, "vowel_count": 4, "consonant_count": 4, "has_repeated_letters": False, "frequency": 3.9, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A small rocky body orbiting the sun.",
        "example_sentence": "The metallic ___ orbited in the belt between Mars and Jupiter.",
        "synonyms": ["minor planet", "planetesimal"], "category": "Space"
    },
    {
        "word": "constellation", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A group of stars forming a recognizable pattern.",
        "example_sentence": "Stargazers identified the Orion ___ in the clear winter night sky.",
        "synonyms": ["star pattern", "asterism"], "category": "Space"
    },
    {
        "word": "supernova", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.5, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A star that suddenly increases greatly in brightness because of a catastrophic explosion.",
        "example_sentence": "A distant ___ released a burst of cosmic radiation across space.",
        "synonyms": ["exploding star", "stellar blast"], "category": "Space"
    },
    {
        "word": "gravitational", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 4, "part_of_speech": "adjective",
        "definition": "Relating to movement caused by gravity.",
        "example_sentence": "The black hole exerted immense ___ pull on nearby stars.",
        "synonyms": ["attracting", "gravitative"], "category": "Space"
    },
    {
        "word": "exoplanet", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": False, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "A planet that orbits a star outside the solar system.",
        "example_sentence": "Astronomers detected an Earth-sized ___ in the habitable star zone.",
        "synonyms": ["extrasolar planet"], "category": "Space"
    },
    {
        "word": "astrophysics", "length": 12, "vowel_count": 3, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The branch of astronomy concerned with the physical nature of stars.",
        "example_sentence": "Research in ___ explores black hole thermodynamics and dark energy.",
        "synonyms": ["stellar physics", "cosmology"], "category": "Space"
    },
    {
        "word": "interstellar", "length": 12, "vowel_count": 4, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 5, "part_of_speech": "adjective",
        "definition": "Occurring or situated between stars.",
        "example_sentence": "A probe journeyed through deep ___ space beyond our solar boundary.",
        "synonyms": ["deep space", "cosmic"], "category": "Space"
    },

    # Geography (10)
    {
        "word": "peak", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.6, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The pointed top of a mountain.",
        "example_sentence": "Climbers reached the snow-capped mountain ___ at dawn.",
        "synonyms": ["summit", "top", "pinnacle"], "category": "Geography"
    },
    {
        "word": "hill", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": True, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A naturally raised area of land, not as high as a mountain.",
        "example_sentence": "Wildflowers bloomed across the rolling green ___.",
        "synonyms": ["mound", "slope", "knoll"], "category": "Geography"
    },
    {
        "word": "canyon", "length": 6, "vowel_count": 2, "consonant_count": 4, "has_repeated_letters": False, "frequency": 4.1, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A deep gorge, typically one with a river flowing through it.",
        "example_sentence": "The rushing river carved a steep rock ___ over millions of years.",
        "synonyms": ["gorge", "ravine", "chasm"], "category": "Geography"
    },
    {
        "word": "plateau", "length": 7, "vowel_count": 4, "consonant_count": 3, "has_repeated_letters": True, "frequency": 3.7, "difficulty": 2, "part_of_speech": "noun",
        "definition": "An area of relatively level high ground.",
        "example_sentence": "The high desert ___ offered vast panoramic sunset views.",
        "synonyms": ["tableland", "high plain"], "category": "Geography"
    },
    {
        "word": "archipelago", "length": 11, "vowel_count": 5, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 3, "part_of_speech": "noun",
        "definition": "An extensive group or chain of islands.",
        "example_sentence": "The tropical ___ consists of over a hundred small islands.",
        "synonyms": ["island chain", "atolls"], "category": "Geography"
    },
    {
        "word": "peninsula", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.8, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A piece of land almost surrounded by water or projecting into a body of water.",
        "example_sentence": "Coastal lighthouses guided ships along the rocky maritime ___.",
        "synonyms": ["headland", "cape"], "category": "Geography"
    },
    {
        "word": "topography", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The arrangement of the natural and artificial physical features of an area.",
        "example_sentence": "Topographical maps depict rugged mountainous terrain ___ accurately.",
        "synonyms": ["landscape", "terrain", "geomorphology"], "category": "Geography"
    },
    {
        "word": "cartography", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The science or practice of drawing maps.",
        "example_sentence": "Early explorers relied on hand-drawn navigational ___ charts.",
        "synonyms": ["mapmaking", "charting"], "category": "Geography"
    },
    {
        "word": "geomorphology", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 2.7, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The study of physical features of the surface of the earth and their relation to geological structures.",
        "example_sentence": "Studies in ___ examine river delta erosion and mountain uplift.",
        "synonyms": ["landform science", "terrain study"], "category": "Geography"
    },
    {
        "word": "meridian", "length": 8, "vowel_count": 4, "consonant_count": 4, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 5, "part_of_speech": "noun",
        "definition": "A circle of constant longitude passing through a given place on the earth's surface.",
        "example_sentence": "The Prime ___ passes directly through Greenwich Observatory.",
        "synonyms": ["longitude line", "circle"], "category": "Geography"
    },

    # Food & Cooking (10)
    {
        "word": "soup", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A liquid dish made by boiling meat, fish, or vegetables in stock or water.",
        "example_sentence": "A bowl of hot vegetable ___ warmed the winter evening.",
        "synonyms": ["broth", "chowder", "stew"], "category": "Food & Cooking"
    },
    {
        "word": "chef", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A professional cook, especially the head cook in a restaurant.",
        "example_sentence": "The executive ___ crafted an exquisite seasonal menu.",
        "synonyms": ["cook", "culinarian"], "category": "Food & Cooking"
    },
    {
        "word": "gourmet", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": False, "frequency": 3.9, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A connoisseur of fine food and drink.",
        "example_sentence": "The chef prepared a seven-course ___ dinner for the guests.",
        "synonyms": ["epicure", "gastronome"], "category": "Food & Cooking"
    },
    {
        "word": "recipe", "length": 6, "vowel_count": 3, "consonant_count": 3, "has_repeated_letters": True, "frequency": 4.5, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A set of instructions for preparing a particular dish.",
        "example_sentence": "She followed her grandmother's traditional sourdough bread ___.",
        "synonyms": ["formula", "instructions"], "category": "Food & Cooking"
    },
    {
        "word": "gastronomy", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The practice or art of choosing, cooking, and eating good food.",
        "example_sentence": "Paris is internationally celebrated for its rich haute ___.",
        "synonyms": ["culinary art", "fine dining"], "category": "Food & Cooking"
    },
    {
        "word": "fermentation", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The chemical breakdown of a substance by bacteria, yeasts, or other microorganisms.",
        "example_sentence": "Yeast enables dough rise through natural sugar ___.",
        "synonyms": ["brewing", "leavening"], "category": "Food & Cooking"
    },
    {
        "word": "confectionery", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "Sweets and chocolates considered collectively.",
        "example_sentence": "Artisanal artisans created colorful fruit-flavored sugar ___.",
        "synonyms": ["sweets", "candies", "pastries"], "category": "Food & Cooking"
    },
    {
        "word": "sommelier", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.0, "difficulty": 4, "part_of_speech": "noun",
        "definition": "A wine steward in a restaurant.",
        "example_sentence": "The certified ___ recommended a vintage red to complement steak.",
        "synonyms": ["wine steward", "cellarmaster"], "category": "Food & Cooking"
    },
    {
        "word": "charcuterie", "length": 11, "vowel_count": 5, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 5, "part_of_speech": "noun",
        "definition": "Cold cooked meats collectively served on a decorative wooden board.",
        "example_sentence": "Guests sampled cured meats and aged cheeses on a ___ board.",
        "synonyms": ["cured meats", "cold cuts"], "category": "Food & Cooking"
    },
    {
        "word": "pasteurization", "length": 14, "vowel_count": 6, "consonant_count": 8, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The partial sterilization of a product to make it safe for consumption.",
        "example_sentence": "Thermal ___ eliminates harmful bacteria from fresh dairy milk.",
        "synonyms": ["sterilization", "sanitization"], "category": "Food & Cooking"
    },

    # Sports (10)
    {
        "word": "ball", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": True, "frequency": 5.1, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A solid or hollow spherical object used in games and sports.",
        "example_sentence": "The striker kicked the leather ___ into the upper net goal.",
        "synonyms": ["sphere", "orb"], "category": "Sports"
    },
    {
        "word": "race", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A competition between runners, horses, vehicles, etc., to see which is fastest.",
        "example_sentence": "Runners sprinted across the finish line of the 100m ___.",
        "synonyms": ["contest", "sprint", "dash"], "category": "Sports"
    },
    {
        "word": "marathon", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.1, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A long-distance running race with an official distance of 42.195 kilometers.",
        "example_sentence": "Thousands of runners trained for months to finish the city ___.",
        "synonyms": ["long race", "endurance run"], "category": "Sports"
    },
    {
        "word": "stadium", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": False, "frequency": 4.3, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A sports arena with tiered seating for spectators.",
        "example_sentence": "Cheering fans filled every seat in the championship ___.",
        "synonyms": ["arena", "colosseum", "field"], "category": "Sports"
    },
    {
        "word": "championship", "length": 12, "vowel_count": 3, "consonant_count": 9, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A contest for the position of champion in a sport or game.",
        "example_sentence": "The team celebrated after winning the national trophy ___.",
        "synonyms": ["tournament", "title match"], "category": "Sports"
    },
    {
        "word": "decathlon", "length": 9, "vowel_count": 3, "consonant_count": 6, "has_repeated_letters": False, "frequency": 3.1, "difficulty": 3, "part_of_speech": "noun",
        "definition": "An athletic event taking place over two days, consisting of ten track and field events.",
        "example_sentence": "The Olympic athlete scored high points across every event in the ___.",
        "synonyms": ["ten-event competition"], "category": "Sports"
    },
    {
        "word": "gymnastics", "length": 10, "vowel_count": 3, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.7, "difficulty": 4, "part_of_speech": "noun",
        "definition": "Exercises developing or displaying physical agility and coordination.",
        "example_sentence": "The balance beam routine showcased precision in competitive ___.",
        "synonyms": ["acrobatic skills", "tumbling"], "category": "Sports"
    },
    {
        "word": "mountaineering", "length": 14, "vowel_count": 6, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The sport or activity of climbing mountains.",
        "example_sentence": "Extreme alpine ___ demands endurance, ice axes, and oxygen tanks.",
        "synonyms": ["mountain climbing", "alpinism"], "category": "Sports"
    },
    {
        "word": "equestrianism", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 2.8, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The skill or sport of horse riding.",
        "example_sentence": "Riders demonstrated jump timing during international ___ trials.",
        "synonyms": ["horseback riding", "horsemanship"], "category": "Sports"
    },
    {
        "word": "biathlon", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": False, "frequency": 3.0, "difficulty": 5, "part_of_speech": "noun",
        "definition": "A winter sport combining cross-country skiing and rifle shooting.",
        "example_sentence": "Competitors skied fast before steadying their breath in the target ___.",
        "synonyms": ["ski-shoot event"], "category": "Sports"
    },

    # History (10)
    {
        "word": "king", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 5.0, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The male ruler of an independent state, especially one who inherits position by right of birth.",
        "example_sentence": "The medieval ___ wore a golden crown in the throne room.",
        "synonyms": ["monarch", "sovereign", "ruler"], "category": "History"
    },
    {
        "word": "fort", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 4.6, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A fortified building or strategic military position.",
        "example_sentence": "Stone walls defended the hilltop military ___ against attackers.",
        "synonyms": ["fortress", "stronghold", "castle"], "category": "History"
    },
    {
        "word": "dynasty", "length": 7, "vowel_count": 2, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A line of hereditary rulers of a country.",
        "example_sentence": "The imperial Ming ___ ruled China for nearly three centuries.",
        "synonyms": ["lineage", "bloodline", "empire"], "category": "History"
    },
    {
        "word": "empire", "length": 6, "vowel_count": 3, "consonant_count": 3, "has_repeated_letters": True, "frequency": 4.4, "difficulty": 2, "part_of_speech": "noun",
        "definition": "An extensive group of states or countries under a single supreme authority.",
        "example_sentence": "The ancient Roman ___ expanded across continental Europe.",
        "synonyms": ["realm", "domain", "kingdom"], "category": "History"
    },
    {
        "word": "civilization", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 3, "part_of_speech": "noun",
        "definition": "An advanced stage of human social and cultural development.",
        "example_sentence": "Historians study the rise and fall of ancient Mesopotamian ___.",
        "synonyms": ["culture", "society"], "category": "History"
    },
    {
        "word": "archaeology", "length": 11, "vowel_count": 5, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The study of human history and prehistory through site excavation.",
        "example_sentence": "Excavations in ___ uncovered buried stone tools and pottery.",
        "synonyms": ["antiquarianism", "historical study"], "category": "History"
    },
    {
        "word": "hieroglyphic", "length": 12, "vowel_count": 4, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "Enigmatic or incomprehensible symbols or writing.",
        "example_sentence": "Scholars decoded Egyptian ___ symbols using the Rosetta Stone.",
        "synonyms": ["pictograph", "symbolic script"], "category": "History"
    },
    {
        "word": "historiography", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The study of historical writing and methodology.",
        "example_sentence": "Modern ___ re-evaluates primary historical source document biases.",
        "synonyms": ["historical methodology"], "category": "History"
    },
    {
        "word": "paleography", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 2.6, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The study of ancient writing systems and the deciphering of manuscripts.",
        "example_sentence": "Professors of ___ deciphered medieval Latin manuscript handwriting.",
        "synonyms": ["script analysis", "codicology"], "category": "History"
    },
    {
        "word": "feudalism", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The dominant social system in medieval Europe.",
        "example_sentence": "Under medieval ___, serfs held land in exchange for labor.",
        "synonyms": ["feudal system", "manorialism"], "category": "History"
    },

    # Medicine (10)
    {
        "word": "lung", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 4.7, "difficulty": 1, "part_of_speech": "noun",
        "definition": "Each of the pair of organs within the rib cage consisting of aerated wall sacs.",
        "example_sentence": "Oxygen enters the bloodstream through healthy ___ tissue.",
        "synonyms": ["respiratory organ"], "category": "Medicine"
    },
    {
        "word": "heart", "length": 5, "vowel_count": 2, "consonant_count": 3, "has_repeated_letters": False, "frequency": 5.0, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A hollow muscular organ that pumps the blood through the circulatory system.",
        "example_sentence": "The human ___ pumps blood continuously through blood vessels.",
        "synonyms": ["cardiac organ", "ticker"], "category": "Medicine"
    },
    {
        "word": "vaccine", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": True, "frequency": 4.2, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A substance used to stimulate the production of antibodies and provide immunity.",
        "example_sentence": "The newly developed ___ protected patients against viral infection.",
        "synonyms": ["immunization", "inoculation"], "category": "Medicine"
    },
    {
        "word": "stethoscope", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A medical instrument used for listening to someone's heart or lungs.",
        "example_sentence": "The doctor placed the cold ___ against the patient's chest.",
        "synonyms": ["heart monitor", "medical acoustic tool"], "category": "Medicine"
    },
    {
        "word": "anesthesia", "length": 10, "vowel_count": 5, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.5, "difficulty": 3, "part_of_speech": "noun",
        "definition": "Insensibility to pain, especially as artificially induced by administration of gases.",
        "example_sentence": "Surgeons administered general ___ before starting the procedure.",
        "synonyms": ["analgesia", "numbness"], "category": "Medicine"
    },
    {
        "word": "epidemiology", "length": 12, "vowel_count": 6, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The branch of medicine which deals with the incidence, distribution, and control of diseases.",
        "example_sentence": "Specialists in ___ tracked disease outbreak spread across nations.",
        "synonyms": ["outbreak science", "disease tracking"], "category": "Medicine"
    },
    {
        "word": "pharmacology", "length": 12, "vowel_count": 4, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The branch of medicine concerned with the uses, effects, and modes of action of drugs.",
        "example_sentence": "Clinical ___ studies drug interactions and therapeutic dosages.",
        "synonyms": ["drug science", "pharmaceutics"], "category": "Medicine"
    },
    {
        "word": "gastroenterology", "length": 16, "vowel_count": 7, "consonant_count": 9, "has_repeated_letters": True, "frequency": 2.7, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The branch of medicine which deals with disorders of the stomach and intestines.",
        "example_sentence": "A specialist in ___ diagnosed the complex digestive disorder.",
        "synonyms": ["digestive medicine"], "category": "Medicine"
    },
    {
        "word": "ophthalmology", "length": 13, "vowel_count": 4, "consonant_count": 9, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The branch of medicine concerned with the study and treatment of eye disorders.",
        "example_sentence": "Surgeons in ___ performed laser vision correction treatments.",
        "synonyms": ["eye care science", "optometry"], "category": "Medicine"
    },
    {
        "word": "antibodies", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.9, "difficulty": 2, "part_of_speech": "noun",
        "definition": "Blood proteins produced in response to and counteracting a specific antigen.",
        "example_sentence": "Immune white cells produce protective ___ against viruses.",
        "synonyms": ["immunoglobulins", "defenses"], "category": "Medicine"
    },

    # Arts & Culture (10)
    {
        "word": "art", "length": 3, "vowel_count": 1, "consonant_count": 2, "has_repeated_letters": False, "frequency": 5.2, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The expression or application of human creative skill and imagination.",
        "example_sentence": "Visitors admired oil canvas ___ in the modern gallery hall.",
        "synonyms": ["artwork", "craft", "creation"], "category": "Arts & Culture"
    },
    {
        "word": "song", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 5.1, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A short poem or other set of words set to music or meant to be sung.",
        "example_sentence": "The soloist sang a graceful acoustic ___ accompanied by piano.",
        "synonyms": ["tune", "melody", "track"], "category": "Arts & Culture"
    },
    {
        "word": "portrait", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.1, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A painting, drawing, photograph, or engraving of a person.",
        "example_sentence": "The artist painted a realistic oil ___ of the royal monarch.",
        "synonyms": ["painting", "likeness", "depiction"], "category": "Arts & Culture"
    },
    {
        "word": "symphony", "length": 8, "vowel_count": 2, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.9, "difficulty": 2, "part_of_speech": "noun",
        "definition": "An elaborate musical composition for full orchestra.",
        "example_sentence": "The grand orchestral ___ featured brass, strings, and percussion.",
        "synonyms": ["concerto", "orchestral piece"], "category": "Arts & Culture"
    },
    {
        "word": "renaissance", "length": 11, "vowel_count": 5, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.8, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A cultural rebirth and revival of European art and literature.",
        "example_sentence": "Florence was the epicenter of the Italian ___ in the 15th century.",
        "synonyms": ["rebirth", "revival"], "category": "Arts & Culture"
    },
    {
        "word": "sculpture", "length": 9, "vowel_count": 3, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.9, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The art of making two- or three-dimensional representative or abstract forms.",
        "example_sentence": "The museum displayed a carved marble ___ from ancient Greece.",
        "synonyms": ["statue", "carving", "bust"], "category": "Arts & Culture"
    },
    {
        "word": "choreography", "length": 12, "vowel_count": 4, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The sequence of steps and movements in dance or figure skating.",
        "example_sentence": "Dancers practiced synchronized stage ___ for the ballet debut.",
        "synonyms": ["dance composition", "staging"], "category": "Arts & Culture"
    },
    {
        "word": "amphitheater", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "An open-air venue used for entertainment, performances, and sports.",
        "example_sentence": "A dramatic theatrical play unfolded under stars in the stone ___.",
        "synonyms": ["arena", "colosseum", "auditorium"], "category": "Arts & Culture"
    },
    {
        "word": "impressionism", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.0, "difficulty": 5, "part_of_speech": "noun",
        "definition": "A style or movement in painting originating in France in the 1860s.",
        "example_sentence": "Monet achieved soft light effects using French ___ painting techniques.",
        "synonyms": ["art style", "light painting movement"], "category": "Arts & Culture"
    },
    {
        "word": "expressionism", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 5, "part_of_speech": "noun",
        "definition": "A style of painting in which the artist seeks to express emotional experience.",
        "example_sentence": "Vivid distorted colors characterized modern German ___ art pieces.",
        "synonyms": ["emotional art movement"], "category": "Arts & Culture"
    },

    # Business (10)
    {
        "word": "bank", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 5.1, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A financial establishment that uses money deposited by customers for investment.",
        "example_sentence": "Depositors secured commercial savings in a licensed central ___.",
        "synonyms": ["repository", "depository", "vault"], "category": "Business"
    },
    {
        "word": "cash", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "Money in coins or notes, as distinct from checks, credit, or debit cards.",
        "example_sentence": "The register clerk provided immediate physical ___ change to buyers.",
        "synonyms": ["currency", "money", "capital"], "category": "Business"
    },
    {
        "word": "investment", "length": 10, "vowel_count": 3, "consonant_count": 7, "has_repeated_letters": True, "frequency": 4.4, "difficulty": 2, "part_of_speech": "noun",
        "definition": "The action of investing money for future financial gain.",
        "example_sentence": "Diversifying your portfolio reduces the risk of any single ___.",
        "synonyms": ["capital", "venture"], "category": "Business"
    },
    {
        "word": "dividend", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A sum of money paid regularly by a company to its shareholders.",
        "example_sentence": "Stockholders earned a quarterly cash ___ payout per share.",
        "synonyms": ["payout", "yield", "return"], "category": "Business"
    },
    {
        "word": "entrepreneur", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.8, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A person who sets up a business, taking on financial risks in the hope of profit.",
        "example_sentence": "The tech ___ launched an innovative startup platform.",
        "synonyms": ["founder", "business builder"], "category": "Business"
    },
    {
        "word": "conglomerate", "length": 12, "vowel_count": 5, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A number of different things or parts that are put together to form a whole.",
        "example_sentence": "The multinational corporate ___ acquired several tech subsidiaries.",
        "synonyms": ["corporation", "syndicate"], "category": "Business"
    },
    {
        "word": "hyperinflation", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.0, "difficulty": 4, "part_of_speech": "noun",
        "definition": "Monetary inflation occurring at a very high rate.",
        "example_sentence": "Uncontrolled printing of currency caused severe national ___.",
        "synonyms": ["price surge", "runaway inflation"], "category": "Business"
    },
    {
        "word": "amortization", "length": 12, "vowel_count": 6, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The action or process of gradually writing off the initial cost of an asset.",
        "example_sentence": "The accountant calculated annual asset loan ___ payment schedules.",
        "synonyms": ["depreciation", "loan payoff"], "category": "Business"
    },
    {
        "word": "privatization", "length": 13, "vowel_count": 6, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The transfer of a business or industry from public to private ownership.",
        "example_sentence": "Legislators debated economic benefits of public utility ___.",
        "synonyms": ["denationalization", "sale"], "category": "Business"
    },
    {
        "word": "recapitalization", "length": 16, "vowel_count": 7, "consonant_count": 9, "has_repeated_letters": True, "frequency": 2.7, "difficulty": 5, "part_of_speech": "noun",
        "definition": "Restructuring a company's debt and equity ratio.",
        "example_sentence": "Corporate financial restructuring involved debt-for-equity ___.",
        "synonyms": ["refinancing", "financial restructuring"], "category": "Business"
    }
]

class WordService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH

    def _get_connection(self):
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        return None

    def _map_category(self, category: str) -> List[str]:
        if not category or category == "General":
            return []
        cat_map = {
            "Food & Cooking": ["Food & Cooking", "Food", "Cooking"],
            "Arts & Culture": ["Arts & Culture", "Arts", "Culture", "Art"],
            "Technology": ["Technology", "Tech"],
            "Science": ["Science"],
            "Nature": ["Nature"],
            "Animals": ["Animals", "Animal"],
            "Space": ["Space", "Astronomy"],
            "Geography": ["Geography"],
            "Sports": ["Sports", "Sport"],
            "History": ["History"],
            "Medicine": ["Medicine", "Medical"],
            "Business": ["Business", "Finance", "Commerce"]
        }
        return cat_map.get(category, [category])

    def get_word_by_id(self, word_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        if not conn:
            return next((w for w in FALLBACK_WORDS if w.get('id') == word_id), FALLBACK_WORDS[0])
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM words WHERE id = ?", (word_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            d = dict(row)
            d['synonyms'] = json.loads(d['synonyms']) if isinstance(d['synonyms'], str) else d['synonyms']
            d['has_repeated_letters'] = bool(d['has_repeated_letters'])
            return d
        return None

    def select_word(self, difficulty: int = 2, category: str = "General", exclude_words: Optional[List[str]] = None) -> Dict[str, Any]:
        exclude_words = [w.lower() for w in (exclude_words or [])]
        conn = self._get_connection()
        categories = self._map_category(category)

        def format_word(w: Dict[str, Any]) -> Dict[str, Any]:
            w = dict(w)
            w['synonyms'] = json.loads(w['synonyms']) if isinstance(w.get('synonyms'), str) else (w.get('synonyms') or [])
            w['has_repeated_letters'] = bool(w.get('has_repeated_letters', False))
            
            word_str = w['word'].lower()
            ex_sent = w.get('example_sentence')
            if not ex_sent:
                def_str = w.get('definition', 'A term in vocabulary.')
                cat_name = w.get('category', 'vocabulary')
                ex_sent = f"In {cat_name}, the concept of ___ is defined as: {def_str}"
            
            pattern = re.compile(re.escape(word_str), re.IGNORECASE)
            w['example_sentence'] = pattern.sub("___", ex_sent)
            return w

        if not conn:
            candidates = [w for w in FALLBACK_WORDS if w['word'].lower() not in exclude_words]
            if not candidates:
                candidates = FALLBACK_WORDS

            if categories:
                cat_candidates = [w for w in candidates if w.get('category') in categories]
                if cat_candidates:
                    candidates = cat_candidates

            if difficulty:
                diff_candidates = [w for w in candidates if w.get('difficulty') == difficulty]
                if diff_candidates:
                    candidates = diff_candidates
            
            selected = random.choice(candidates)
            return format_word(selected)

        cur = conn.cursor()
        queries_to_try = []

        # Tier 1: Exact difficulty & category, excluding played words
        if difficulty and categories:
            cat_placeholders = ",".join("?" for _ in categories)
            queries_to_try.append((
                f"WHERE difficulty = ? AND category IN ({cat_placeholders})",
                [difficulty] + categories
            ))

        # Tier 2: Exact category, any difficulty, excluding played words
        if categories:
            cat_placeholders = ",".join("?" for _ in categories)
            queries_to_try.append((
                f"WHERE category IN ({cat_placeholders})",
                categories
            ))

        # Tier 3: Exact difficulty, any category, excluding played words
        if difficulty:
            queries_to_try.append((
                "WHERE difficulty = ?",
                [difficulty]
            ))

        # Tier 4: Any word in database, excluding played words
        queries_to_try.append(("", []))

        for where_clause, params in queries_to_try:
            sql = f"SELECT * FROM words {where_clause}"
            query_params = list(params)

            if exclude_words:
                ex_placeholders = ",".join("?" for _ in exclude_words)
                prefix = " AND " if where_clause else "WHERE "
                sql += f"{prefix}LOWER(word) NOT IN ({ex_placeholders})"
                query_params.extend(exclude_words)

            sql += " ORDER BY RANDOM() LIMIT 1"
            
            try:
                cur.execute(sql, query_params)
                row = cur.fetchone()
                if row:
                    conn.close()
                    return format_word(dict(row))
            except Exception:
                continue

        # Absolute Fallback if all 38k+ words in DB have been played
        cur.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if row:
            return format_word(dict(row))

        return format_word(random.choice(FALLBACK_WORDS))

    def get_daily_word(self, date_str: str) -> Dict[str, Any]:
        conn = self._get_connection()
        if not conn:
            idx = int(hashlib.md5(date_str.encode()).hexdigest(), 16) % len(FALLBACK_WORDS)
            return FALLBACK_WORDS[idx]

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM words")
        total = cur.fetchone()[0]
        
        if total == 0:
            return random.choice(FALLBACK_WORDS)

        hash_val = int(hashlib.sha256(date_str.encode('utf-8')).hexdigest(), 16)
        target_offset = hash_val % total

        cur.execute("SELECT * FROM words LIMIT 1 OFFSET ?", (target_offset,))
        row = cur.fetchone()
        conn.close()

        if row:
            d = dict(row)
            d['synonyms'] = json.loads(d['synonyms']) if isinstance(d['synonyms'], str) else d['synonyms']
            d['has_repeated_letters'] = bool(d['has_repeated_letters'])
            
            word_str = d['word'].lower()
            ex_sent = d.get('example_sentence')
            if not ex_sent:
                def_str = d.get('definition', 'A term in vocabulary.')
                ex_sent = f"In context, the term ___ is defined as: {def_str}"
            pattern = re.compile(re.escape(word_str), re.IGNORECASE)
            d['example_sentence'] = pattern.sub("___", ex_sent)
            return d

        return FALLBACK_WORDS[0]

    def get_categories(self) -> List[str]:
        return PRESET_CATEGORIES

word_service = WordService()
