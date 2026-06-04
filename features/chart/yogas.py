"""features.chart.yogas — warm, plain-English copy for the notable chart patterns.

Two kinds of highlight on the chart's front room:
  • GIFTS — auspicious yogas, framed as genuine strengths.
  • GROWTH — the classically "difficult" combinations, framed GENTLY as areas that
    ask for care — never as curses or verdicts (anti-fatalism, blueprint §2).

Keys are matched by substring against the engine's yoga/dosha names (which carry
suffixes like " Yoga", " (Negative)", " (Kuja Dosha)"), so a key like "Gajakesari"
catches "Gajakesari Yoga". Each meaning is the standard classical signification,
re-voiced warm and jargon-free. The scarier-named combinations (Daridra/Shrapit)
are deliberately NOT surfaced in the front room — they belong in the deeper premium
reading, not the welcoming first look. Sanskrit stays out of `body`.
"""
from __future__ import annotations

# ── GIFTS — auspicious yogas (only the well-known, clearly positive ones). ────
YOGA_WARM: dict[str, dict] = {
    "Gajakesari": {"body": "You have a natural blessing of good judgement and goodwill — people tend to trust and respect you, and wisdom seems to find you. It's one of the loveliest combinations to have.",
                   "sanskrit": "गजकेसरी योग (चन्द्र-गुरु)"},
    "Budha-Aditya": {"body": "You've got a bright, quick intelligence — you learn fast, explain things well, and your mind is one of your real strengths.",
                     "sanskrit": "बुध-आदित्य योग"},
    "Ruchaka": {"body": "You carry a strong, commanding presence — courage, leadership, and the kind of energy that makes people follow you. One of the 'great person' combinations.",
                "sanskrit": "रुचक महापुरुष योग (मंगल)"},
    "Bhadra": {"body": "You have a sharp, articulate, capable mind — a real gift for thinking, learning, and putting things clearly. One of the 'great person' combinations.",
               "sanskrit": "भद्र महापुरुष योग (बुध)"},
    "Hamsa": {"body": "You have a naturally good, principled, respected nature — people sense your decency and wisdom. One of the 'great person' combinations.",
              "sanskrit": "हंस महापुरुष योग (गुरु)"},
    "Malavya": {"body": "You're blessed with charm, an eye for beauty, and a pull toward comfort and grace — life tends to bring you the finer things. One of the 'great person' combinations.",
                "sanskrit": "मालव्य महापुरुष योग (शुक्र)"},
    "Shasha": {"body": "You have real staying power and quiet authority — the discipline to build lasting things and to rise through patience. One of the 'great person' combinations.",
               "sanskrit": "शश महापुरुष योग (शनि)"},
    "Raja": {"body": "There's a rising quality in your chart — recognition, responsibility, and success tend to find you as life unfolds, often more than your start would suggest.",
             "sanskrit": "राज योग"},
    "Dhana": {"body": "You have a money-builder's chart — wealth tends to come through your own efforts, and you've a knack for turning work into resources.",
              "sanskrit": "धन योग"},
    "Lakshmi": {"body": "There's a grace and prosperity in your chart — comfort and good fortune have a way of coming to you.",
                "sanskrit": "लक्ष्मी योग"},
    "Saraswati": {"body": "You have a real gift for learning, art, and expression — a naturally creative and knowledgeable mind.",
                  "sanskrit": "सरस्वती योग"},
    "Amala": {"body": "You carry a spotless reputation — your good name and integrity open doors and stay with you.",
              "sanskrit": "अमल योग"},
    "Viparita": {"body": "You have a rare 'rise after the fall' gift — you tend to come through hard times not just intact but stronger, often better off than before.",
                 "sanskrit": "विपरीत राज योग"},
    "Neecha Bhanga": {"body": "Something that looks like a weakness in your chart quietly flips into a strength — an early disadvantage that ends up making you.",
                      "sanskrit": "नीच भंग राज योग"},
    "Chandra-Mangala": {"body": "You pair drive with feeling — a real ability to turn energy and emotion into getting things done and earning.",
                        "sanskrit": "चन्द्र-मंगल योग"},
    "Adhi": {"body": "You tend to be well-supported by good people — quiet backing and good fortune through the right company.",
             "sanskrit": "अधि योग"},
    "Sankha": {"body": "There's a marker of a full, comfortable life in your chart — good values, ease, and longevity.",
               "sanskrit": "शंख योग"},
    "Parivartana": {"body": "Two areas of your life trade strengths and lift each other — what helps one quietly helps the other.",
                    "sanskrit": "परिवर्तन योग"},
    "Sunapha": {"body": "Your Moon is well-supported, giving you steadiness and your own quiet resources to draw on.",
                "sanskrit": "सुनफा योग"},
    "Anapha": {"body": "Your Moon is well-supported — a calm, self-possessed quality and a good presence.",
               "sanskrit": "अनफा योग"},
    "Durudhura": {"body": "Your Moon is supported on both sides — a marker of comfort, resources, and a generous life.",
                  "sanskrit": "दुरुधरा योग"},
    "Ubhayachari": {"body": "Your Sun is well-supported — confidence, a strong sense of self, and an easy way with people.",
                    "sanskrit": "उभयचरी योग"},
    "Veshi": {"body": "Your Sun is supported — a steady confidence and a principled way of moving through the world.",
              "sanskrit": "वेशि योग"},
    "Voshi": {"body": "Your Sun is supported — capability, intelligence, and a good name.",
              "sanskrit": "वोशि योग"},
}

# ── GROWTH — the classically 'difficult' combinations, framed GENTLY. Only the
#    commonly-discussed ones that can be reassured; never the scary-named ones. ──
DOSHA_WARM: dict[str, dict] = {
    "Kemadruma": {"body": "Your Moon stands a little on its own in the chart — emotionally, you've often had to be your own anchor. It can bring lonely patches, but it also builds a deep, real self-reliance, and it's easily softened by the good things elsewhere in your chart.",
                  "sanskrit": "केमद्रुम योग"},
    "Mangal": {"body": "Mars sits somewhere that adds heat to close relationships — lots of passion and drive that simply wants a healthy outlet. It's extremely common (a big share of people have it) and very workable — not a verdict on your love life.",
               "sanskrit": "मंगल दोष (कुज दोष)"},
    "Kaal Sarp": {"body": "All your planets sit to one side of the lunar nodes, so life can come in intense, all-or-nothing waves — with a strong sense of destiny running through it. Plenty of very successful people share this; it's a particular rhythm, not a doom.",
                  "sanskrit": "काल सर्प योग"},
    "Sade Sati": {"body": "You're in (or close to) Saturn's slow seven-and-a-half-year passage over your Moon — a heavier, more serious season that tends to leave you wiser, steadier, and more solid by the time it lifts.",
                  "sanskrit": "साढ़े साती"},
    "Pitra": {"body": "There's a thread of ancestral 'unfinished business' in your chart — traditionally honoured by remembering and caring for your elders and those who came before. Gentle to work with, and nothing to fear.",
              "sanskrit": "पितृ दोष"},
    "Grahan": {"body": "One of your lights — the Sun or Moon — sits close to a node, which can dim confidence or stir moods now and then. A little awareness and a few steadying habits settle it.",
               "sanskrit": "ग्रहण दोष"},
}
