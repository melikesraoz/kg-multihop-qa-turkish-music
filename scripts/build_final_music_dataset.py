from pathlib import Path
import json
import csv

twohop_file = Path("outputs/music_2hop_questions_draft.json")
threehop_file = Path("outputs/music_3hop_questions_draft.json")
comp_file = Path("outputs/music_comparison_questions_draft.json")

output_json = Path("outputs/music_final_50_dataset.json")
output_tsv = Path("outputs/music_final_50_dataset.tsv")

with open(twohop_file, "r", encoding="utf-8") as f:
    twohop = json.load(f)

with open(threehop_file, "r", encoding="utf-8") as f:
    threehop = json.load(f)

with open(comp_file, "r", encoding="utf-8") as f:
    comp = json.load(f)

# 2-hop: ilk 30
final_2hop = twohop[:30]

# 3-hop: en gürültülü 2 taneyi at, kalan 15'i al
drop_3hop_ids = {"MUSIC_3HOP_009", "MUSIC_3HOP_010"}
filtered_3hop = [x for x in threehop if x["question_id"] not in drop_3hop_ids]
final_3hop = filtered_3hop[:15]

# comparison: ilk 5 temiz olanı al
keep_comp_ids = {
    "MUSIC_COMP_001",
    "MUSIC_COMP_002",
    "MUSIC_COMP_003",
    "MUSIC_COMP_004",
    "MUSIC_COMP_005",
}
final_comp = [x for x in comp if x["question_id"] in keep_comp_ids]

final_dataset = final_2hop + final_3hop + final_comp

# yeniden sırala ve id ver
renumbered = []
c2 = c3 = cc = 0

for item in final_dataset:
    new_item = dict(item)
    diff = new_item["difficulty"]

    if diff == "2-hop":
        c2 += 1
        new_item["question_id"] = f"MUSIC_2HOP_{c2:03d}"
    elif diff == "3-hop":
        c3 += 1
        new_item["question_id"] = f"MUSIC_3HOP_{c3:03d}"
    elif diff == "comparison":
        cc += 1
        new_item["question_id"] = f"MUSIC_COMP_{cc:03d}"

    renumbered.append(new_item)

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(renumbered, f, ensure_ascii=False, indent=2)

with open(output_tsv, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([
        "question_id",
        "question_text",
        "gold_answer",
        "reasoning_path",
        "seed_entity",
        "difficulty",
        "domain"
    ])
    for r in renumbered:
        writer.writerow([
            r["question_id"],
            r["question_text"],
            r["gold_answer"],
            " | ".join(r["reasoning_path"]),
            r["seed_entity"],
            r["difficulty"],
            r["domain"]
        ])

print("Final dataset size:", len(renumbered))
print("2-hop:", sum(1 for x in renumbered if x["difficulty"] == "2-hop"))
print("3-hop:", sum(1 for x in renumbered if x["difficulty"] == "3-hop"))
print("comparison:", sum(1 for x in renumbered if x["difficulty"] == "comparison"))
print("JSON:", output_json)
print("TSV:", output_tsv)

print("\nFirst 10 questions:")
for x in renumbered[:10]:
    print(f"{x['question_id']} | {x['question_text']} -> {x['gold_answer']}")