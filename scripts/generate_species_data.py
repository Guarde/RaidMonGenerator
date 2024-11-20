import os, json

home = os.path.dirname(__file__)
all_species = {}

def load_files():
    for root, folder, files in os.walk(os.path.join(home, "resolvers"), topdown=True):
        for file in files:
            if not ".json" in file:
                continue
            with open(os.path.join(root, file), mode="r") as f:
                content = json.load(f)
            if not "species" in content.keys():
                continue
            species = content["species"].replace("cobblemon:", "")
            if not species in all_species.keys():
                all_species[species] = []
            for variation in content["variations"]:
                if not "aspects" in variation.keys() or variation["aspects"] == []:
                    if not "" in all_species[species]:
                        all_species[species].append([])
                    continue
                all_species[species].append(variation["aspects"])

load_files()
with open(os.path.join(home, "data_resourcepack.json"), mode="w+") as f:
    json.dump(all_species, f, indent=3)