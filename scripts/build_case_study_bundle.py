from pathlib import Path
import json

dataset_file = Path("outputs/music_final_50_dataset.json")
activation_file = Path("outputs/spreading_activation_demo.json")
qe_file = Path("outputs/kg_qe_and_answer_demo.json")

output_json = Path("outputs/case_study_bundle.json")
output_txt = Path("outputs/case_study_bundle.txt")

with open(dataset_file, "r", encoding="utf-8") as f:
    dataset = json.load(f)

with open(activation_file, "r", encoding="utf-8") as f:
    activation = json.load(f)

with open(qe_file, "r", encoding="utf-8") as f:
    qe = json.load(f)

# İlk demo sorusunu dataset içinden bul
demo_question = None
for item in dataset:
    if "Zulfu Livaneli" in item["question_text"]:
        demo_question = item
        break

bundle = {
    "demo_question": demo_question,
    "activation": activation,
    "kg_qe_answer": qe,
}

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(bundle, f, ensure_ascii=False, indent=2)

lines = []
lines.append("CASE STUDY BUNDLE")
lines.append("=" * 60)

if demo_question:
    lines.append("\n[Dataset Question]")
    lines.append(f"ID: {demo_question['question_id']}")
    lines.append(f"Question: {demo_question['question_text']}")
    lines.append(f"Gold Answer: {demo_question['gold_answer']}")
    lines.append(f"Reasoning Path: {' | '.join(demo_question['reasoning_path'])}")

lines.append("\n[Activation Demo]")
lines.append(f"Query: {activation['query']}")
lines.append(f"Seed: {activation['seed']['name']} ({activation['seed']['id']})")
for t in activation["triples"]:
    lines.append(
        f"Round {t['round']}: {t['source_name']} --[{t['relation_name']}]--> {t['target_name']}"
    )

lines.append("\n[KG-QE-Answer Demo]")
lines.append(f"KG Summary: {qe['kg_summary']}")
lines.append(f"Expanded Query: {qe['expanded_query']}")
lines.append(f"Final Answer: {qe['final_answer']}")

with open(output_txt, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Saved:")
print(output_json)
print(output_txt)