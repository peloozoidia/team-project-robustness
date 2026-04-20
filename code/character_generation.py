import json
from datetime import datetime
from pathlib import Path

import config
from misc.npc_generator import generate_character


def main() -> None:

  for i in range(0, config.GENERATED_CHARACTERS_COUNT):
    npc = generate_character()
    out_dir = Path(config.OUTPUT_PATH).joinpath("./characters")
    out_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    out_path = out_dir / f"character_{ts}.json"

    out_path.write_text(json.dumps(npc, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print(f"Saved character to: {out_path}")


main()
