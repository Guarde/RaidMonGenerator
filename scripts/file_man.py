import os, shutil
from datetime import datetime
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

def cleanup_output_folder(home):
    output_path = os.path.join(home, "output")
    temp_path = os.path.join(output_path, "_temp")
    shutil.rmtree(temp_path, ignore_errors=True)
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    os.mkdir(temp_path)

def make_zip_file(home):
    output_path = os.path.join(home, "output")
    temp_path = os.path.join(output_path, "_temp")
    filename = datetime.now().strftime("RaidMons_%b-%d-%Y-%H-%M-%S")
    shutil.make_archive(filename, "zip", root_dir=temp_path)


def do_dump(output, home, folder, filename):
    filename = f"{filename}.json"
    folder_path = os.path.join(home, "output", "_temp", folder)
    if not os.path.exists(os.path.join(home, "output")):
        os.mkdir(os.path.join(home, "output"))
    if not os.path.exists(os.path.join(home, "output", "_temp")):
        os.mkdir(os.path.join(home, "output", "_temp",))
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    with open(os.path.join(folder_path, filename), mode="w+") as f:
        json.dump(output, f, indent=3)