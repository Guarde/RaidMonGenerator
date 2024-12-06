import os, shutil
from datetime import datetime
import jstyleson as json

pokemon_data = {}
pokemon_vouchers = {"customVouchers": {}, "customVouchersTextures": {}}
pokemon_list = {}
type_data = {}
move_list = {}
s_generic = {}
s_moves = {}
s_stats = {}
s_aspects = {}
s_rewards = {}
s_pokemon = {}
template = {}
cobbledata = {}

def load_files(home):
    global pokemon_data, move_list, type_data, template, cobbledata
    with open(os.path.join(home, "data", "data_pokemon.json"), mode = "r") as f:
        d = json.load(f)
        pokemon_data = d["pokemon"]
        move_list = d["moves"]

    with open(os.path.join(home, "data", "data_types.json"), mode="r") as f:
        type_data = json.load(f)

    print("Data loaded...")

    with open(os.path.join(home, "data", "template.json"), mode = "r") as f:
        template = json.load(f)
    print("Template loaded...")

    with open(os.path.join(home, "data", "data_resourcepack.json"), mode = "r") as f:
        cobbledata = json.load(f)
    print("Resource pack data loaded...")

def load_settings(home):
    global s_aspects, s_generic, s_moves, s_pokemon, s_rewards, s_stats
    with open(os.path.join(home, "config", "config_generic.jsonc"), mode = "r") as f:
        s_generic = json.load(f)
    with open(os.path.join(home, "config", "config_moves.jsonc"), mode = "r") as f:
        s_moves = json.load(f)
    with open(os.path.join(home, "config", "config_stats.jsonc"), mode = "r") as f:
        s_stats = json.load(f)
    with open(os.path.join(home, "config", "config_aspects.jsonc"), mode = "r") as f:
        s_aspects = json.load(f)
    with open(os.path.join(home, "config", "config_rewards.jsonc"), mode = "r") as f:
        s_rewards = json.load(f)
    with open(os.path.join(home, "config", "config_pokemon.jsonc"), mode = "r") as f:
        s_pokemon = json.load(f)
    print("Config loaded...")


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
    os.chdir(output_path)
    shutil.make_archive(filename, "zip", root_dir=temp_path)

def save_voucher_config(home):
    output_path = os.path.join(home, "output")
    filename = datetime.now().strftime("Raid_Vouchers_%b-%d-%Y-%H-%M-%S")
    filename = f"{filename}.json"
    os.chdir(output_path)
    with open(os.path.join(output_path, filename), mode="w+") as f:
        json.dump(pokemon_vouchers, f, indent=2)

def do_dump(output:dict, home:str, folder:str, filename:str):
    for k, v in s_aspects["aspects_lookup"].items():
        if not v in filename:
            continue
        filename = filename.replace(v, k)
    if s_generic["prefix_folder_to_filename"] and not folder[0] == "_":
        filename = folder + "-" + filename.replace(f"-{folder}", "-")
    filename = filename.replace(f"--", "-")
    filename = filename.rstrip("-")
    if folder in s_generic["raid_vouchers"].keys():
        voucher = s_generic["raid_vouchers"][folder]
        if not voucher["name"] in pokemon_vouchers["customVouchers"].keys():
            pokemon_vouchers["customVouchers"][voucher["name"]] = []
            pokemon_vouchers["customVouchersTextures"][voucher["name"]] = voucher["id"]
        pokemon_vouchers["customVouchers"][voucher["name"]].append(filename)
    filename = f"{filename}.json"
    if s_generic["disable_subfolders"]:
        folder_path = os.path.join(home, "output", "_temp")
    else:
        folder_path = os.path.join(home, "output", "_temp", folder)
    if not os.path.exists(os.path.join(home, "output")):
        os.mkdir(os.path.join(home, "output"))
    if not os.path.exists(os.path.join(home, "output", "_temp")):
        os.mkdir(os.path.join(home, "output", "_temp",))
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    with open(os.path.join(folder_path, filename), mode="w+") as f:
        json.dump(output, f, indent=3)