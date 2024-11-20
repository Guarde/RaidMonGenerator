import os
import jstyleson as json

pokemon_data = {}
pokemon_list = {}
type_data = {}
move_list = {}
settings = {}
template = {}
cobbledata = {}

def load_files(home):
    global pokemon_data, move_list, type_data, settings, template, cobbledata
    with open(os.path.join(home, "data", "data_pokemon.json"), mode = "r") as f:
        d = json.load(f)
        pokemon_data = d["pokemon"]
        move_list = d["moves"]

    with open(os.path.join(home, "data", "data_types.json"), mode="r") as f:
        type_data = json.load(f)

    print("Data loaded...")

    with open(os.path.join(home, "generator_config.jsonc"), mode = "r") as f:
        settings = json.load(f)
    print("Config loaded...")

    with open(os.path.join(home, "data", "template.json"), mode = "r") as f:
        template = json.load(f)
    print("Template loaded...")

    with open(os.path.join(home, "data", "data_resourcepack.json"), mode = "r") as f:
        cobbledata = json.load(f)
    print("Resource pack data loaded...")

def do_dump(output, home):
    with open(os.path.join(home, "output", "output.json"), mode="w+") as f:
        json.dump(output, f, indent=3)