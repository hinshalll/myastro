"""features.chart.nakshatras — warm, plain-English personality for the 27 birth-stars.

The birth Moon's nakshatra is, in classical Jyotish, the most personal signature of
temperament. Each entry's `body` is a warm, jargon-free read of that temperament,
written in plain second person — faithful to the STANDARD classical nature of the
star (its deity, symbol and ruling planet, cross-checked across reputable nakshatra
sources; the deity/symbol/ruler facts match the engine's own
`get_nakshatra_attributes`). The Sanskrit name, deity and symbol stay in the
`sanskrit`/`why` the service builds — never in `body`. Gentle guidance, never fate.

Keys EXACTLY match shared.astro.constants.NAKSHATRAS (so the Moon's `nakshatra`
field looks up directly).
"""
from __future__ import annotations

NAKSHATRA: dict[str, dict] = {
    "Ashwini": {
        "body": "You move fast and start things others only think about — quick, brave, and a little impatient. There's a natural healer in you: when something's wrong, your instinct is to rush in and fix it.",
        "ruler": "Ketu", "deity": "the Ashwini Kumaras, the twin healers", "symbol": "a horse's head", "dev": "अश्विनी",
    },
    "Bharani": {
        "body": "You feel everything intensely and can carry far more than most — you take things all the way, whether that's love, work, or change. There's real creative force in you, and a strength that shows up when life gets heavy.",
        "ruler": "Venus", "deity": "Yama, who holds life and death", "symbol": "the womb — a vessel of creation", "dev": "भरणी",
    },
    "Krittika": {
        "body": "You're sharp, bright, and honest to a fault — you cut straight through nonsense and don't suffer pretence. There's a protective fire in you that gets things (and people) into shape, and a real glow when you're on a mission.",
        "ruler": "Sun", "deity": "Agni, the god of fire", "symbol": "a flame or a razor", "dev": "कृत्तिका",
    },
    "Rohini": {
        "body": "You're magnetic and grounded — people are drawn to your warmth, and you have a real gift for making things grow and flourish, from gardens to relationships. You love beauty, comfort, and the good things of life.",
        "ruler": "Moon", "deity": "Brahma, the creator", "symbol": "an ox-cart and a spreading banyan tree", "dev": "रोहिणी",
    },
    "Mrigashira": {
        "body": "You're a gentle seeker, always a little curious, always reaching for the next thing — a new idea, a new place, a new feeling. You notice subtle things others miss, and you're happiest when you're exploring.",
        "ruler": "Mars", "deity": "Soma, the Moon's nectar", "symbol": "a deer's head", "dev": "मृगशिरा",
    },
    "Ardra": {
        "body": "You feel deeply and think sharply, and you're not afraid of the hard, stormy stuff that others avoid — you break things down so something truer can grow. After the storm, you're the one who's clearer and stronger.",
        "ruler": "Rahu", "deity": "Rudra, the storm", "symbol": "a teardrop", "dev": "आर्द्रा",
    },
    "Punarvasu": {
        "body": "You have a deep resilience — no matter how dark it gets, you find your way back to the light, and you help others do the same. You're hopeful, generous, and easy to be around, with a love of simple, honest things.",
        "ruler": "Jupiter", "deity": "Aditi, the mother of the gods", "symbol": "a quiver of arrows", "dev": "पुनर्वसु",
    },
    "Pushya": {
        "body": "You're one of life's natural nurturers — steady, caring, and dependable, the person others lean on. You give generously and want to protect the people you love, and there's a quiet, devoted strength in you.",
        "ruler": "Saturn", "deity": "Brihaspati, teacher of the gods", "symbol": "a cow's udder and a lotus", "dev": "पुष्य",
    },
    "Ashlesha": {
        "body": "You're perceptive in a way that can be almost unsettling — you read people instantly and feel what's really going on beneath the surface. There's a hypnotic, deep quality to you, and real healing power when you use it kindly.",
        "ruler": "Mercury", "deity": "the Nagas, the serpent spirits", "symbol": "a coiled serpent", "dev": "आश्लेषा",
    },
    "Magha": {
        "body": "You carry a natural dignity — you honour where you come from, respect tradition, and want to leave something lasting behind. People sense the authority in you, and you're at your best when you lead with heart.",
        "ruler": "Ketu", "deity": "the Pitris, the ancestors", "symbol": "a royal throne", "dev": "मघा",
    },
    "Purva Phalguni": {
        "body": "You know how to enjoy life — you're warm, playful, and creative, and you bring ease and pleasure wherever you go. You value rest and good company, and you're generous with both.",
        "ruler": "Venus", "deity": "Bhaga, god of delight and good fortune", "symbol": "the front of a hammock", "dev": "पूर्वफाल्गुनी",
    },
    "Uttara Phalguni": {
        "body": "You're the loyal, dependable one — generous, kind, and steady in your friendships and commitments. You like to help in real, practical ways, and people trust you because you mean what you say.",
        "ruler": "Sun", "deity": "Aryaman, god of friendship and contracts", "symbol": "the back of a bed — a place of rest", "dev": "उत्तरफाल्गुनी",
    },
    "Hasta": {
        "body": "You're skilful and resourceful — clever with your hands and your wits, able to make almost anything happen through sheer craft. You've got quick humour and a knack for turning ideas into something real.",
        "ruler": "Moon", "deity": "Savitar, the inspiring Sun", "symbol": "an open hand", "dev": "हस्त",
    },
    "Chitra": {
        "body": "You have an eye for beauty and a flair for making things — and yourself — shine. You're charismatic and creative, a natural designer or builder, and you like your work to be admired (rightly so).",
        "ruler": "Mars", "deity": "Vishvakarma, the cosmic architect", "symbol": "a bright jewel", "dev": "चित्रा",
    },
    "Swati": {
        "body": "You need your independence the way you need air — you're adaptable, self-made, and you bend with the wind rather than break. You're diplomatic and fair, and you do your best growing on your own terms.",
        "ruler": "Rahu", "deity": "Vayu, the wind", "symbol": "a young shoot swaying in the breeze", "dev": "स्वाति",
    },
    "Vishakha": {
        "body": "You're driven and goal-focused — once you fix on something, you don't stop until it's yours. There's a bright, ambitious fire in you, and a patience underneath it that waits for exactly the right moment to strike.",
        "ruler": "Jupiter", "deity": "Indra and Agni, power and fire", "symbol": "a triumphal archway", "dev": "विशाखा",
    },
    "Anuradha": {
        "body": "You build deep, lasting bonds — you're devoted, friendly, and able to bring people together and keep them together. You succeed through relationship and loyalty, and you're warmer than you sometimes let on.",
        "ruler": "Saturn", "deity": "Mitra, god of friendship", "symbol": "a lotus", "dev": "अनुराधा",
    },
    "Jyeshtha": {
        "body": "You're the capable, senior one — protective, brave, and able to carry responsibility others can't. You've often had to be strong early, and there's real depth and skill in you, even if it sometimes feels like a weight.",
        "ruler": "Mercury", "deity": "Indra, king of the gods", "symbol": "a protective amulet", "dev": "ज्येष्ठा",
    },
    "Mula": {
        "body": "You go straight to the root of things — you're not satisfied with surface answers, and you'll dig until you find what's true, even if it shakes things up. There's a fearless, investigative, transformative streak in you.",
        "ruler": "Ketu", "deity": "Nirriti, goddess of dissolution", "symbol": "a bundle of tied roots", "dev": "मूल",
    },
    "Purva Ashadha": {
        "body": "You have an almost unshakeable optimism — you believe things will work out, and that conviction carries you (and others) through. You're persuasive and proud in the best way, hard to defeat once your heart is set.",
        "ruler": "Venus", "deity": "the cosmic waters", "symbol": "a fan and a winnowing basket", "dev": "पूर्वाषाढा",
    },
    "Uttara Ashadha": {
        "body": "You go for the lasting win, not the quick one — you're principled, patient, and honest, and the things you build tend to endure. People follow you because you lead with integrity rather than noise.",
        "ruler": "Sun", "deity": "the Vishvedevas, the universal gods", "symbol": "an elephant's tusk", "dev": "उत्तराषाढा",
    },
    "Shravana": {
        "body": "You're a listener and a learner — you take the world in carefully, understand people deeply, and hold a real love of knowledge and tradition. You connect others through what you hear and remember.",
        "ruler": "Moon", "deity": "Vishnu, the preserver", "symbol": "an ear, and three footprints", "dev": "श्रवण",
    },
    "Dhanishta": {
        "body": "You've got rhythm and drive — energetic, generous, and good at getting things done, often with a musical or creative beat running under it. You like to achieve and to share the rewards around.",
        "ruler": "Mars", "deity": "the Vasus, the gods of the elements", "symbol": "a drum", "dev": "धनिष्ठा",
    },
    "Shatabhisha": {
        "body": "You're an independent, slightly mysterious healer-type — drawn to what's hidden, unconventional in your thinking, and most yourself when you have space and privacy. You see and mend things others can't reach.",
        "ruler": "Rahu", "deity": "Varuna, lord of cosmic waters and law", "symbol": "an empty circle of a hundred healers", "dev": "शतभिषा",
    },
    "Purva Bhadrapada": {
        "body": "You're an intense idealist — passionate about what you believe, drawn to the deep and the otherworldly, and capable of seeing far beyond the ordinary. There's a fire in you that wants to transform things.",
        "ruler": "Jupiter", "deity": "Aja Ekapada, the one-footed fiery one", "symbol": "the front of a funeral cot — a threshold", "dev": "पूर्वभाद्रपदा",
    },
    "Uttara Bhadrapada": {
        "body": "You're the calm, deep one — still waters that run far deeper than they look. You're patient, wise, and compassionate, with a controlled strength that keeps you steady when everything around you isn't.",
        "ruler": "Saturn", "deity": "Ahir Budhnya, the serpent of the deep", "symbol": "the back of a funeral cot — rest and release", "dev": "उत्तरभाद्रपदा",
    },
    "Revati": {
        "body": "You're gentle and nourishing — kind to almost everyone, protective of the vulnerable, and gifted at guiding people safely through. You have a soft, imaginative heart and a quiet wish to see others home.",
        "ruler": "Mercury", "deity": "Pushan, the nourisher and guide of travellers", "symbol": "a pair of fish", "dev": "रेवती",
    },
}
