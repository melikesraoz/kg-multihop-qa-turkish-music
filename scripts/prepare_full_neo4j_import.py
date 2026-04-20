"""
prepare_full_neo4j_import.py - Wikidata5M Full Dataset -> Neo4j Import CSV

Tum Wikidata5M verisini (5M entity + ~20M triple) filtresiz olarak
Neo4j'nin 'neo4j-admin database import' formatina uygun CSV dosyalarina donusturur.

Kullanim:
  python scripts/prepare_full_neo4j_import.py

Cikti:
  outputs/nodes.csv          (~5M satir)
  outputs/relationships.csv  (~20M satir)
"""
import csv
import os
from pathlib import Path

# Dosya yollari
BASE = Path(__file__).resolve().parent.parent / "data" / "wikidata5m_raw_data"
ENTITY_FILE = BASE / "wikidata5m_alias" / "wikidata5m_entity.txt"
RELATION_FILE = BASE / "wikidata5m_alias" / "wikidata5m_relation.txt"
TRIPLET_FILE = BASE / "wikidata5m_all_triplet.txt"

OUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
NODES_CSV = OUT_DIR / "nodes.csv"
RELS_CSV = OUT_DIR / "relationships.csv"

def sanitize_rel_type(name: str) -> str:
    """Neo4j relationship type icin gecersiz karakterleri temizle."""
    # Virgul, bosluk, tire gibi sorunlu karakterleri alt cizgiyle degistir
    cleaned = name.upper().replace(" ", "_").replace(",", "").replace("-", "_")
    # Bas ve son alt cizgileri temizle, tekrarlayan alt cizgileri birlesir
    import re
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned if cleaned else "RELATED_TO"

def prepare():
    # 1. Relation isimlerini yukle (P-id -> okunabilir isim)
    print("1/3) Relation isimleri yukleniyor...")
    relations = {}
    with open(RELATION_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                relations[parts[0]] = sanitize_rel_type(parts[1])
    print(f"     {len(relations)} relation tipi yuklendi.")

    # 2. nodes.csv Olustur (TUM entity'ler)
    print("2/3) nodes.csv olusturuluyor (tum 5M+ entity)...")
    node_count = 0
    with open(NODES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        f.write("entityId:ID,name,description,:LABEL\n")

        with open(ENTITY_FILE, "r", encoding="utf-8") as ent:
            for line in ent:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    e_id = parts[0]
                    name = parts[1]
                    writer.writerow([e_id, name, name, "Entity"])
                    node_count += 1
                    if node_count % 500000 == 0:
                        print(f"     ... {node_count:,} node yazildi")

    print(f"     TOPLAM: {node_count:,} node yazildi -> {NODES_CSV}")

    # 3. relationships.csv Olustur (TUM triple'lar)
    print("3/3) relationships.csv olusturuluyor (tum ~20M triple)...")
    rel_count = 0
    skipped = 0
    with open(RELS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        f.write(":START_ID,:END_ID,:TYPE,relationId\n")

        with open(TRIPLET_FILE, "r", encoding="utf-8") as tri:
            for line in tri:
                parts = line.strip().split("\t")
                if len(parts) == 3:
                    subj, rel_id, obj = parts
                    rel_type = relations.get(rel_id, sanitize_rel_type(rel_id))
                    writer.writerow([subj, obj, rel_type, rel_id])
                    rel_count += 1
                    if rel_count % 2000000 == 0:
                        print(f"     ... {rel_count:,} relationship yazildi")
                else:
                    skipped += 1

    print(f"     TOPLAM: {rel_count:,} relationship yazildi -> {RELS_CSV}")
    if skipped:
        print(f"     UYARI: {skipped:,} satir atlandı (bozuk format)")

    print("\n" + "=" * 60)
    print("TAMAMLANDI!")
    print(f"  nodes.csv:         {NODES_CSV}")
    print(f"  relationships.csv: {RELS_CSV}")
    print("=" * 60)
    print("\nSimdi Neo4j'i durdur ve asagidaki komutu calistir:")
    print()
    print('  neo4j-admin database import full')
    print('    --nodes=Entity=outputs/nodes.csv')
    print('    --relationships=outputs/relationships.csv')
    print('    --overwrite-destination')
    print('    neo4j')
    print()

if __name__ == "__main__":
    prepare()
