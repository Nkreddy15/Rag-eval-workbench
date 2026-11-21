"""Create a deterministic benchmark for a fictional campus makerspace."""
import json
from pathlib import Path

records = [
    ("laser cutter", "certification", "Laser Safety Level 2", "evening supervisor"),
    ("resin printer", "cleanup fluid", "isopropyl alcohol", "resin technician"),
    ("wood lathe", "minimum stock length", "120 millimeters", "woodshop lead"),
    ("vinyl cutter", "maximum sheet width", "52 centimeters", "print coordinator"),
    ("embroidery machine", "approved needle", "Size 75 embroidery needle", "textile mentor"),
    ("electronics bench", "solder temperature", "340 degrees Celsius", "lab monitor"),
    ("ceramic kiln", "cooldown duration", "18 hours", "kiln operator"),
    ("waterjet station", "booking limit", "90 minutes", "fabrication manager"),
    ("metal brake", "maximum sheet thickness", "2 millimeters", "metals instructor"),
    ("photo scanner", "image format", "TIFF", "media desk"),
]
passages = []
cases = []
for i, (station, field, value, contact) in enumerate(records, start=1):
    passage_id = f"P{i}"
    passages.append({
        "id": passage_id,
        "text": f"The {station} {field} is {value}. Contact the {contact} for help.",
    })
    for question, phrase in [
        (f"What is the {field} for the {station}?", value),
        (f"Who can assist with the {station}?", contact),
        (f"Does the {station} have a documented {field}? Give its value.", value),
        (f"How much does it cost to reserve the {station}?", ""),
    ]:
        cases.append({
            "question": question,
            "expected_ids": [passage_id] if phrase else [],
            "expected_phrase": phrase,
        })

Path(__file__).with_name("demo.json").write_text(
    json.dumps({"passages": passages, "cases": cases}, indent=2) + "\n",
    encoding="utf-8",
)
