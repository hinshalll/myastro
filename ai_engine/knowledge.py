import os
import requests

def get_knowledge_files(file_names):
    """Loads MD reference files locally first, then falls back to GitHub."""
    loaded_texts = []
    
    for name in file_names:
        try:
            # Strictly clean the URL to prevent 'No connection adapter' errors
            clean_name = name.strip(" '\n\r")
            local_candidates = [
                os.path.join(os.path.expanduser("~"), "Desktop", "aiguide", clean_name),
                os.path.join(os.path.expanduser("~"), "Desktop", "aiguide", "Being Used", clean_name),
            ]
            for local_path in local_candidates:
                if os.path.exists(local_path):
                    with open(local_path, "r", encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                    loaded_texts.append(f"\n--- START OF REFERENCE BOOK: {clean_name} ---\n{text}\n--- END OF REFERENCE BOOK: {clean_name} ---\n")
                    break
            if len(loaded_texts) and loaded_texts[-1].startswith(f"\n--- START OF REFERENCE BOOK: {clean_name} ---"):
                continue
            github_url = f"https://raw.githubusercontent.com/hinshalll/text2kprompt/main/aiguide/{clean_name}"
            
            # Fetch the raw markdown text directly from GitHub
            response = requests.get(github_url, timeout=15)
            response.raise_for_status() 
            
            # Wrap the text so the AI knows exactly which book it is reading
            file_content = f"\n--- START OF REFERENCE BOOK: {clean_name} ---\n{response.text}\n--- END OF REFERENCE BOOK: {clean_name} ---\n"
            loaded_texts.append(file_content)
            
        except Exception as e:
            # Raise the exception so Streamlit aborts the cache and tries cleanly next time
            raise Exception(f"Network error loading {name}. Please check your connection and try again. Details: {e}")
            
    return loaded_texts


def get_comparison_reference_digest():
    """
    Token-light reference pack for Compare Profiles.
    Uses a compact digest from BPHS1 + KP3 instead of attaching multi-MB books.
    """
    return ["""
--- START OF REFERENCE DIGEST: BPHS1.md + KP3.md for Compare Profiles ---
Use this digest as the book authority for comparison output.

PARASHARI / BPHS1 PRINCIPLES
- Judge a topic from the relevant house, its lord, occupants, aspects/associations, natural karaka, dignity, yogas, and appropriate varga.
- House meanings used here: H1 body/vitality/self; H2 wealth/family/speech; H3 courage/effort; H4 peace of mind/home/happiness/property; H5 intelligence/children/fame/purva punya; H6 disease/debts/enemies/competition; H7 spouse/marriage/partnership; H8 longevity/sudden reversals/hidden matters; H9 fortune/dharma/guru; H10 profession/status/honour; H11 gains/fulfilment; H12 losses/expenditure/moksha.
- Divisional chart use: Hora for wealth; Navamsa for spouse and durable inner strength; Dashamsa for power, position and career; Dvadashamsa can support constitution/family inheritance; Vimsamsa is for worship/spiritual progress when available; Trimsamsa is for evils and hidden adversity.
- Dignity matters: exaltation/own sign/vargottama strengthen; debility/enemy sign/combustion/planetary war/bad avastha weaken or spoil results unless cancelled by Neecha Bhanga or other protection.
- Yogas matter only when the causing planets are strong enough. Kendra-trikona links, yogakarakas and Raja/Dhana/Lakshmi-type yogas support high promise; Kemadruma and severe malefic hemming raise burden.
- Longevity and health use Lagna, Lagna lord, H3/H8, maraka pressure from H2/H7, Saturn, Sun, Moon, and afflictions. Do not turn this into medical diagnosis.
- Spirituality uses H9/H12/H8/H5, Ketu, Jupiter, Saturn, Atmakaraka/Karakamsa ideas, and moksha-oriented varga support.

KP3 PRINCIPLES
- KP refines whether an event manifests. The star lord shows the main house results; the sub-lord selects/denies the specific outcome.
- A cusp sub-lord that signifies the event houses promises the event; if it signifies opposing houses, it delays, obstructs or denies.
- Marriage/engagement: houses 2, 7 and 11 are primary; 3 and 9 can support agreement/consent.
- Finance: H2 is bank position/self-acquisition; H11 is profit/net gain; H12 is loss/expense. For service-linked money include H10.
- Profession/status: H10 is position, fame, reputation and profession; H11 is fulfilment/realisation; H6 supports service, competition and victory over opponents.
- Partnership/business: H7 with H2/H10/H11 supports success; H8/H12 links weaken.
- Disease judgment uses the 6th cusp sub-lord and its star/sub links; chronicity and danger require H8/H12 context.

COMPARISON OUTPUT RULE
- Python scores are final. Explain rankings with chart evidence and this digest. Do not recalculate, invent positions, or use current transits/Sade Sati/current dasha to alter lifetime baseline scores.
--- END OF REFERENCE DIGEST ---
"""]