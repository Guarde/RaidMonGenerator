import random, copy
from math import ceil
from scripts import file_man

def import_files(home):
    file_man.load_files(home)
    file_man.load_settings(home)

def effectiveness(types):
    resist = {}
    for type in file_man.type_data["defending"].keys():
        resist[type] = 0
    for defending_type in types:
        for attacking_type in file_man.type_data["defending"][defending_type]["immune"]:
            resist[attacking_type] += +99
        for attacking_type in file_man.type_data["defending"][defending_type]["resists"]:
            resist[attacking_type] += +1
        for attacking_type in file_man.type_data["defending"][defending_type]["weak"]:
            resist[attacking_type] += -1 
    return resist

def weaknesses(pokemon):
    types = pokemon["type"]
    weak = [t[0] for t in effectiveness(types).items() if t[1] < 0]
    return weak

def coverage(weaknesses):
    cover = []
    for w in weaknesses:
        cover += [t[0] for t in effectiveness([w]).items() if t[1] < 0]
    sorted_cover = {}
    for c in cover:
        if not c in sorted_cover.keys():
            sorted_cover[c] = 0
        sorted_cover[c] += 1
    cover = list(dict.fromkeys(cover).keys())
    cover = sorted(cover, key=lambda d: sorted_cover[d], reverse=True)
    return cover

def get_pokemon():
    pokemon = {}
    for key, value in file_man.pokemon_data.items():
        if not file_man.s_pokemon["pokemon_whitelist"] == [] and not key in file_man.s_pokemon["pokemon_whitelist"] and not file_man.s_pokemon["is_blacklist"]:
            continue
        if not file_man.s_pokemon["pokemon_whitelist"] == [] and key in file_man.s_pokemon["pokemon_whitelist"] and file_man.s_pokemon["is_blacklist"]:
            continue
        if value["can_evolve"] and not file_man.s_pokemon["unevolved"]:
            continue
        if value["base_total"] < file_man.s_pokemon["base_stat_min"]:
            continue
        if value["base_total"] > file_man.s_pokemon["base_stat_max"]:
            continue
        for aspect, replace in file_man.s_aspects["aspects_lookup"].items():
            if str.endswith(key, "-" + aspect):
                key = key.replace("-" + aspect, "-" + replace)            
            if value["form"] == aspect:
                value["form"] = replace
        if value["legendary"] and file_man.s_pokemon["legendaries"]:
            pokemon[key] = value
            continue
        if value["mythical"] and file_man.s_pokemon["mythicals"]:
            pokemon[key] = value
            continue
        if value["ultrabeast"] and file_man.s_pokemon["ultrabeasts"]:
            pokemon[key] = value
            continue
        if file_man.s_pokemon["regular"]:
            pokemon[key] = value
    return pokemon

def get_moves(pokemon:dict, attack_type):
    moves = []
    for move in list(pokemon["moves"].values())[0]:
        move = file_man.move_list[move]
        
        if move["name"] in file_man.s_moves["move_blacklist"]:
            continue

        if not file_man.s_moves["allow_recoil_moves"] and move["name"] in file_man.s_moves["recoil_moves"]:
            continue

        type_match = True
        for key, values in file_man.s_moves["move_type_lock"].items():
            if not move["name"] == key:    
                continue

            if not [t for t in pokemon["type"] if t in values] == []:
                continue

            type_match = False
            break

        if not type_match:
            continue

        cat_match = True
        for key, values in file_man.s_moves["move_category_lock"].items():
            if not move["name"] in values:                
                continue
            if attack_type == key:
                continue
            cat_match = False
            break

        if not cat_match:
            continue
        if move["power"] == None:
            move["power"] = -1
        if move["accuracy"] == None:
            move["accuracy"] = 100
        moves.append(move)
    moves = sorted(moves, key=lambda d: d['power'], reverse=True)
    return moves

def move_filter_category(categories, moves, types, coverage_types):
    new_moves = []
    for category in categories:
        match category:
            case "primary":
                new_moves = [m for m in moves if m["type"] == types[0] and not m["damage_class"] == "status"]

            case "secondary":
                if len(types) < 2:
                    continue
                new_moves = [m for m in moves if m["type"] == types[1] and not m["damage_class"] == "status"]

            case "coverage":
                temp_moves = [m for m in moves if not m["damage_class"] == "status"]
                for t in coverage_types:
                    new_moves += [m for m in temp_moves if m["type"] == t]                    

            case "non-stab":
                new_moves = [m for m in moves if not m["type"] in types and not m["damage_class"] == "status"]

            case "status":
                prefer = [m for m in moves if m["name"] in file_man.s_moves["preferred_status_moves"]]
                if not prefer == []:
                    new_moves = prefer
                else:
                    new_moves = [m for m in moves if m["damage_class"] == "status"]

            case "any":
                new_moves = moves

            case _:
                pass

        if not new_moves == []:
            break
    return new_moves

def calc_attack_type(pokemon):
    if pokemon["base_att"] > pokemon["base_spatt"]:
        attack_type = "physical"
    if pokemon["base_att"] < pokemon["base_spatt"]:
        attack_type = "special"
    if pokemon["base_att"] == pokemon["base_spatt"]:
        attack_type = random.choice(["physical", "special"])
    return attack_type

def choose_moves(pokemon, moves, attack_type, coverage_types):
    choices = []

    for slot in file_man.s_moves["moveset"]:
        options = move_filter_category(slot["category"], moves, pokemon["type"], coverage_types)
        if slot["shuffle"]:
            random.shuffle(options)
        for option in options:
            if option["name"] in choices:
                continue
            if not option["damage_class"] in ["status", attack_type]:
                continue
            if slot["power_min"] > option["power"] and not option["damage_class"] == "status":
                continue
            if slot["acc_min"] > option["accuracy"]:
                continue
            choices.append(option["name"])
            break

    if len(choices) < len(file_man.s_moves["moveset"]):
        for move in moves:
            if move["name"] in choices:
                continue
            choices.append(move["name"])
    if len(choices) < len(file_man.s_moves["moveset"]):
        choices += ["struggle", "struggle", "struggle"]

    if len(choices) > len(file_man.s_moves["moveset"]):
        choices = choices[:len(file_man.s_moves["moveset"])]

    final = {}
    i = 0
    for choice in choices:
        i += 1
        final[f"move{i}"] = choice.replace("-", "")

    return final

def calc_ivs():
    stats = ["hp", "attack", "defence", "special_attack", "special_defence", "speed"]
    result = {}
    for stat in stats:
        result[stat] = min(random.randint(file_man.s_stats["iv_range"][0], file_man.s_stats["iv_range"][1]), 31)
    return result

def calc_evs(nature):
    result = []
    match nature:
        case "admant" | "jolly":
            result = [6, 252, 0, 0, 0, 252]
        case "impish":
            result = [6, 252, 0, 0, 252, 0]
        case "careful":
            result = [0, 252, 252, 0, 0, 0]
        case "modest" | "timid":
            result = [6, 0, 0, 252, 0, 252]
        case "bold":
            result = [6, 0, 0, 252, 252, 0]
        case "calm":
            result = [6, 0, 252, 252, 0, 0]
        case _:
            result = [252, 0, 130, 0, 128, 0]
    return {"hp": result[0], "attack": result[1], "defence": result[2], "special_attack": result[3], "special_defence": result[4], "speed": result[5]}

def calc_nature(pokemon, attack_type):
    if not file_man.s_stats["nature"] == "optimal":
        return random.choice(file_man.s_stats["nature_random_choices"])
    
    if attack_type == "physical":
        if pokemon["base_att"]*1.5 <= pokemon["base_spd"]:
            return "adamant"
        if pokemon["base_att"]/2 < pokemon["base_spd"]:
            return "jolly"
        if pokemon["base_def"] >= pokemon["base_spdef"]:
            return "impish"
        if pokemon["base_def"] < pokemon["base_spdef"]:
            return "careful"
        
    if attack_type == "special":
        if pokemon["base_spatt"]*1.5 <= pokemon["base_spd"]:
            return "modest"
        if pokemon["base_spatt"]/2 < pokemon["base_spd"]:
            return "timid"
        if pokemon["base_def"] >= pokemon["base_spdef"]:
            return "bold"
        if pokemon["base_def"] < pokemon["base_spdef"]:
            return "calm"

def calc_gender(pokemon):
    if pokemon["gender_rate"] == None:
        return "MALE"
    male_chance = pokemon["gender_rate"][0]
    if random.random() > male_chance:
        return "FEMALE"
    return "MALE"

def calc_rewards(distribute:dict, rewards:dict, id:int, multiplier, enable_scaling):
    for i in range(len(rewards["place"])):
        place = rewards["place"][i]
        amount = rewards["amount"][i]
        chance = rewards["chance"][i]
        if not place in distribute.keys():
            distribute[place] = []
        distribute[place].append({"id": id, "amount": ceil(amount * multiplier), "chance": chance})
    return distribute

def calc_multiplier(base_total:int):
    multiplier = 1
    for v in sorted(file_man.s_rewards["tiers"], key=lambda d: d['treshold']):
        if not base_total > v["treshold"]:
            break
        multiplier = v["multiplier"]
    return multiplier

def find_folder(pokemon, build):
    folder = "regular"
    if pokemon["legendary"]:
        folder = "legendary"
    if pokemon["mythical"]:
        folder = "mythical"
    if pokemon["ultrabeast"]:
        folder = "ultrabeast"

    for a in file_man.s_aspects["non_regular_aspects"]:
        if not a in build["form"]:
            continue
        folder = a
        break

    for key, values in file_man.s_aspects["aspect_groups"].items():
        if not folder in values:
            continue
        folder = key
        break
    return folder

def reward_form(form):
    form = form.split(" ")
    form = [f for f in form if not f in file_man.s_aspects["reward_form_blacklist"]]
    return " ".join(form)

def boss_form_prefix(form):
    form = form.split(" ")
    pre_prefix = "Boss"
    prefix = []
    for a, v in file_man.s_aspects["aspect_boss_names"].items():
        for f in form:
            if not f == a:
                continue
            if f in file_man.s_aspects["aspect_prefixes"].keys():
                continue
            prefix.append(v)
            form.remove(f)
            break
    if not form == []:
        for f in form:                
            for key, values in file_man.s_aspects["aspect_groups"].items():
                if key[0] == "_":
                    continue
                if [t for t in values if t in f] == []:
                    continue
                if f in file_man.s_aspects["aspect_prefixes"].keys():
                    continue
                form.remove(f)
                prefix.append(key.title())
                break
    if not form == []:
        for f in form:                
            for v in file_man.s_aspects["non_regular_aspects"]:
                if not v in f:
                    continue
                if f in file_man.s_aspects["aspect_prefixes"].keys():
                    continue
                form.remove(f)
                p = f.replace(v, f" {v} ")
                prefix.append(p.strip().title())
                break
    for f in form:
        if not f in file_man.s_aspects["aspect_prefixes"].keys():
            continue
        pre_prefix = file_man.s_aspects["aspect_prefixes"][f]
    return " ".join([pre_prefix] + prefix)

def get_reward_ability(build):
    form = build["form"].split()
    blacklisted = [f for f in form if f in file_man.s_aspects["reward_form_blacklist"]]
    if blacklisted == []:
        return build["ability"]
    nonvis = [f for f in form if f in file_man.s_aspects["non_visual_aspects"]]
    if nonvis == []:
        return build["ability"]
    if [f for f in blacklisted if f in nonvis] == []:
        return build["ability"]
    abilities = [a.replace("-", "") for a in file_man.pokemon_data[build["species"]]["abilities"]]
    if build["ability"] in abilities:
        return build["ability"]
    return random.choice(abilities)

def get_boss_scale(species):
    if not species in file_man.s_stats["scale_override"].keys():
        return file_man.s_stats["boss_scale"]
    return file_man.s_stats["scale_override"][species]

def get_arena_for_mon(pokemon, folder):
    options = get_arena_for_aspect(folder)
    if options == []:
        options = get_arena_for_type(pokemon["type"][0])
    if options == [] and len(pokemon["type"]) > 1:
        options = get_arena_for_type(pokemon["type"][1])
    if options == []:
        result = file_man.s_generic["arenas_default"]
    else:
        result = random.choice(options)
    return result

def get_arena_for_type(type:str):
    options = []
    for a, v in file_man.s_generic["arenas_by_type"].items():
        if not type in v:
            continue
        options.append(a)
    return options

def get_arena_for_aspect(aspect:str):
    options = []
    for a, v in file_man.s_generic["arenas_by_aspect"].items():
        if not aspect in v:
            continue
        options.append(a)
    return options



def build_set(pokemon):
    attack_type = calc_attack_type(pokemon)
    weak = weaknesses(pokemon)
    build = copy.deepcopy(file_man.template)
    build["distributeRewards"] = []
    build["species"] = pokemon["name"]
    build["form"] = pokemon["form"]
    build["level"] = file_man.s_stats["level"]
    build["gender"] = calc_gender(pokemon)
    build["nature"] = calc_nature(pokemon, attack_type)
    build["ivs"] = calc_ivs()
    build["evs"] = calc_evs(build["nature"])
    build["moveSet"] = choose_moves(pokemon, get_moves(pokemon, attack_type), attack_type, coverage(weak))
    build["scaleModifier"] = get_boss_scale(build["species"])
    build["encounterRewardForm"] = reward_form(pokemon["form"])
    build["bossEncounter_randomMoveset"] = file_man.s_moves["randomize_encounter_moveset"]
    build["formTextPlaceholder"] = boss_form_prefix(build["form"])
    build["folder"] = find_folder(pokemon, build)
    build["arena"] = get_arena_for_mon(pokemon, build["folder"])
    i = 0
    distribute = {}
    bonus_rewards = []
    
    key_rewards = file_man.s_rewards["key_rewards"]
    if build["folder"] in key_rewards["keys"].keys():
        key_name = key_rewards["keys"][build["folder"]]
        command = key_rewards["command"].replace("%key%", key_name)
        message = key_rewards["message"].replace("%key%", key_name)
        bonus_rewards.append({"type": "command", "command": command, "message": message, "distribution": key_rewards["distribution"]})

    mega_rewards = file_man.s_rewards["megastone"]
    mega_aspects = [a for a in build["form"].split(" ") if a in mega_rewards["aspects"]]
    if not mega_aspects == []:
        if build["species"] in mega_rewards["items"].keys():
            item = mega_rewards["items"][build["species"]]
            if mega_rewards["aspectx"] in mega_aspects:
                item = item + "x"
            elif mega_rewards["aspecty"] in mega_aspects:
                item = item + "y"
            command = mega_rewards["command"].replace("%item%", item)
            message = mega_rewards["message"].replace("%item%", item.title())
            bonus_rewards.append({"type": "command", "command": command, "message": message, "distribution": mega_rewards["distribution"]})



    for reward in file_man.s_rewards["base"] + bonus_rewards:
        i += 1
        reward["id"] = i
        r = {}
        for key, value in reward.items():
            if key == "distribution":
                continue
            r[key] = value
        reward_dist = reward["distribution"]
        multiplier = calc_multiplier(pokemon["base_total"]) if reward_dist["reward_scaling"] else 1
        for c in range(len(reward_dist["place"])):
            place = reward_dist["place"][c]
            amount = reward_dist["amount"][c]
            chance = reward_dist["chance"][c]
            if chance == 0:
                continue
            if not place in distribute.keys():
                distribute[place] = []
            distribute[place].append({"id": i, "amount": ceil(amount * multiplier), "chance": chance})
        build["rewards"].append(r)
    for k, d in distribute.items():
        d = {"place": k, "rewards": d}
        build["distributeRewards"].append(d)

    abilities = [a for a in pokemon["abilities"] if not a in file_man.s_stats["ability_blacklist"]]
    if not abilities == []:
        build["ability"] = random.choice(abilities).replace("-", "")
        build["bossEncounter_ability"] = get_reward_ability(build)
    return build

def filter_aspects():
    filtered_aspects = {}
    def add_aspect(pokemon, a):
        if not pokemon in filtered_aspects.keys():
            filtered_aspects[pokemon] = []
        filtered_aspects[pokemon].append(a)
    for pokemon, aspects in file_man.cobbledata.items():
        for aspect in aspects:
            passed = True
            for blacklist in file_man.s_aspects["aspects_blacklist"]:
                if [a for a in aspect if blacklist in a] == []:
                    continue
                passed = False
                break
            if not passed:
                continue
            if aspect == [] and "" in file_man.s_aspects["aspects_whitelist"]:
                add_aspect(pokemon, aspect)
                continue
            if file_man.s_aspects["aspects_whitelist"] == []:
                add_aspect(pokemon, aspect)
                continue
            if [a for a in aspect if a in file_man.s_aspects["aspects_whitelist"]] == []:
                continue
            add_aspect(pokemon, aspect)
    return filtered_aspects

def filter_pokemon_with_aspects(aspect_list, pokemon):
    new_pokemon_list = {}
    for key, value in pokemon.items():
        species = value["name"].replace("-", "")
        form = value["form"]
        if not species in aspect_list.keys():
            continue
        for aspects in aspect_list[species]:
            new_mon = copy.deepcopy(value)
            if not form == "" and not form in aspects:
                continue
            if form == "" and not [a for a in aspects if a in file_man.s_aspects["non_visual_aspects"]] == []:
                continue
            if aspects == []:
                new_pokemon_list[key] = new_mon
                continue
            new_key = f'{species}-{"-".join(aspects)}'
            new_mon["form"] = " ".join(aspects)
            new_pokemon_list[new_key] = new_mon
    return new_pokemon_list

def run_process(pokemon_list, home):
    file_man.cleanup_output_folder(home)
    for n, p in pokemon_list.items():
        o = build_set(p)
        o["species"] = o["species"].replace("-", "") 
        folder = o.pop("folder")
        if not folder in file_man.s_aspects["aspect_group_folders"]:
            print(f"No subfolder for group {folder} enabled. Skipping {n}")
            continue
        if o["ability"] == "":
            print(n + " has no ability.")
            continue

        file_man.do_dump(o, home, folder, n)
    if file_man.s_generic["create_zip"]:
        file_man.make_zip_file(home)
    if file_man.s_generic["create_vouchers_config"]:
        file_man.save_voucher_config(home)
    if file_man.s_generic["cleanup_temp"]:
        file_man.cleanup_output_folder(home)