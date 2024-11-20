import os
from math import ceil
from scripts.generators import import_files, filter_aspects, get_pokemon, filter_pokemon_with_aspects, run_process

if __name__ == "__main__":
    home = os.path.dirname(__file__)
    import_files(home)
    aspects = filter_aspects()
    pokemon_list = get_pokemon()
    pokemon_list = filter_pokemon_with_aspects(aspects, pokemon_list)
    run_process(pokemon_list, home)