import json

def analyze():
    with open('outputs/music_final_50_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tr_chars = set('çğışıöüİ')
    tr_count = 0
    en_count = 0
    
    for q in data:
        name = q['reasoning_path'][0]
        if any(c in name.lower() for c in tr_chars):
            tr_count += 1
        else:
            en_count += 1
            
    print(f"TR name count: {tr_count}")
    print(f"EN name count: {en_count}")
    
    # Sub-domain analysis (genre-based)
    genres = {}
    for q in data:
        # Infer genre from reasoning path if available
        # Path: Zulfu Livaneli, place of birth, ilgın, country, turkiye
        # Path: Arif Sag, genre, Türkü, instance of, styles of music
        genre = "Unknown"
        if "genre" in q['reasoning_path']:
            idx = q['reasoning_path'].index("genre")
            if idx + 1 < len(q['reasoning_path']):
                genre = q['reasoning_path'][idx+1]
        
        genres[genre] = genres.get(genre, 0) + 1
    
    print(f"Sub-genres found: {genres}")

if __name__ == "__main__":
    analyze()
