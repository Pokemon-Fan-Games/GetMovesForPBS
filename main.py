import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import re
import threading
import sys, os
def resource(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



file_path = ""
file_path_moves = ""
file_path_pokemon = ""
current_tms = {}
entry_poke = None
file_label = None
file_label_pokemon = None
file_label_moves = None
poke_name_label = None
tk_poke = None
execute_button = None
progressbar = None
progressbar_label = None
tms = {}
cached_moves = {
    'level':{},
    'tutor':{},
    'egg':{}
}
toggle_button = None
root = tk.Tk()
is_on = False
update_learn_level = tk.BooleanVar()
search_tutor_moves = tk.BooleanVar()
search_egg_moves = tk.BooleanVar()
tm_thread = None
level_moves_thread = None

def on_closing():
    global tm_thread, level_moves_thread
    if (not tm_thread or not tm_thread.is_alive()) and (not level_moves_thread or not level_moves_thread.is_alive()):
        root.quit()
        return
    if messagebox.askokcancel("Salir", "¿Está seguro de que desea salir y cancelar todos los procesos pendientes? Esto puede generar que los archivos queden corruptos."):
        root.quit()

def create_screen():
    global entry_poke
    global file_label
    global file_label_pokemon
    global file_label_moves
    global poke_name_label
    global tk_poke
    global progressbar
    global progressbar_label
    global toggle_button
    global root
    
    tk.Label(root, text="Seleccione el archivo pokemon.txt").grid(row=0, column=0, pady=5, padx=15, sticky='w')
    tk.Button(root, text="Seleccione el archivo", command=open_pokemon_file).grid(row=0, column=1, pady=5, padx=15)
    file_label_pokemon = tk.Label(root, text="Archivo Pokemons: ")
    file_label_pokemon.grid(row=1, column=0, pady=5, padx=15, columnspan=3, sticky='NW')
    tk.Button(root, text="Deseleccionar Archivo: ", command=remove_pokemon_file).grid(row=1, column=1, pady=5, padx=15)
    poke_name_label = tk.Label(root, text="Ingrese el nombre del pokemon")
    poke_name_label.grid(row=2, column=0, pady=5, padx=15, sticky='w')
    tk_poke = tk.StringVar()
    entry_poke = tk.Entry(root, textvariable=tk_poke)
    entry_poke.focus()
    entry_poke.grid(row=2, column=1, pady=5, padx=15)
    tk.Label(root, text="Si selecciona el archivo pokemon.txt este campo será ingorado y se hara la búsqueda para todos los pokémon del archivo", fg='#f00').grid(row=3, column=0, columnspan=3, pady=5, padx=15, sticky='w')
    tk.Label(root, text="Seleccione el archivo tms.txt").grid(row=4, column=0, pady=5, padx=15, sticky='w')
    tk.Button(root, text="Seleccionar archivo", command=open_file).grid(row=4, column=1, pady=5, padx=15)
    file_label = tk.Label(root, text="Archivo: ")
    file_label.grid(row=5, column=0, pady=5, padx=15, columnspan=3, sticky='NW')

    tk.Button(root, text="Buscar MTs", command=execute).grid(row=6, columnspan=3, pady=5, padx=15, sticky='we')

    toggle_button = tk.Button(root, text="Desplegar opciones para buscar movimientos por nivel, tutor y huevo", relief="raised", command=turn_on_level_moves)
    toggle_button.grid(row=7, columnspan=3, column=0, pady=5, padx=15, sticky='we')
    file_label_moves = tk.Label(root, text="Archivo: ")

    progressbar_label = tk.Label(root, text="")
    progressbar = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")

    root.title("Buscador de MTs")
    root.iconbitmap(resource("tmicon.ico"))
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

def turn_on_level_moves():
    global is_on, file_label_moves, toggle_button, update_learn_level
    is_on = not is_on
    select_file_label = tk.Label(root, text="Seleccione el archivo moves.txt")
    file_button = tk.Button(root, text="Seleccionar archivo", command=open_moves_file)
    button = tk.Button(root, text="Actualizar aprendizaje por nivel", command=update_level_moves)
    checkbox_update_learn_level = tk.Checkbutton(root, text="Actualizar nivel de aprendizaje", variable = update_learn_level)
    checkbox_tutor_moves = tk.Checkbutton(root, text="Buscar movimientos por tutor", variable = search_tutor_moves)
    checkbox_egg_moves = tk.Checkbutton(root, text="Buscar movimientos huevo", variable = search_egg_moves)
    if is_on:
        checkbox_update_learn_level.grid(row=8, column=0, pady=5, padx=15)
        checkbox_tutor_moves.grid(row=8, column=1, pady=5, padx=15)
        checkbox_egg_moves.grid(row=8, column=2, pady=5, padx=15)
        select_file_label.grid(row=9, column=0, pady=5, padx=15, sticky='w')
        file_button.grid(row=9, column=1, pady=5, padx=15)
        file_label_moves.grid(row=10, column=0, pady=5, padx=15, columnspan=3, sticky='NW')
        button.grid(row=11, columnspan=3, pady=5, padx=15, sticky='we')
        toggle_button.config(relief="sunken")
    else:
        select_file_label.grid_remove()
        file_button.grid_remove()
        file_label_moves.grid_remove()
        button.grid_remove()
        toggle_button.config(relief="raised")

def open_file():
    global file_path 
    global file_label
    file_path = filedialog.askopenfilename(title="Abrir tm.txt")
    if not file_path or not file_path.endswith("tm.txt"):
        messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo tm.txt')
        return
    file_path_label = file_path.split("/")
    file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
    file_label.configure(text="Archivo: " + file_path_label)

def open_pokemon_file():
    global file_path_pokemon 
    global file_label_pokemon
    global entry_poke
    global poke_name_label
    file_path_pokemon = filedialog.askopenfilename(title="Abrir pokemon.txt")
    if (file_path_pokemon and not file_path_pokemon.endswith("pokemon.txt")):
        messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo pokemon.txt')
        return
    poke_name_label.grid_remove()
    entry_poke.grid_remove()
    file_path_label = file_path_pokemon.split("/")
    file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
    file_label_pokemon.configure(text="Archivo: " + file_path_label)

def open_moves_file():
    global file_path_moves
    global file_label_moves
    file_path_moves = filedialog.askopenfilename(title="Abrir moves.txt")
    if (file_path_moves and not file_path_moves.endswith("moves.txt")):
        messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo moves.txt')
        return
    file_path_label = file_path_moves.split("/")
    file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
    file_label_moves.configure(text="Archivo: " + file_path_label)

def remove_pokemon_file():
    global file_path_pokemon 
    global file_label_pokemon
    global entry_poke
    global poke_name_label
    file_path_pokemon = ""
    file_label_pokemon.configure(text="Archivo Pokemons: ")
    poke_name_label.grid(row=2, column=0, pady=5, padx=15, sticky='w')
    entry_poke.focus()
    entry_poke.grid(row=2, column=1, pady=5, padx=15)

def start_loading(label):
    global progressbar
    global progressbar_label
    global root
    progressbar_label.configure(text=label)
    if not progressbar_label.grid_info():
        progressbar_label.grid(row=12, columnspan=3, pady=5, padx=15, sticky='we')
    #progressbar_label.grid(row=12, columnspan=3, pady=5, padx=15, sticky='we')
    progressbar.grid(row=13, columnspan=3, pady=5, padx=15, sticky='we')
    progressbar.start()
    root.update_idletasks()

def stop_loading():
    global progressbar
    global progressbar_label
    progressbar.stop()
    progressbar.grid_remove()
    progressbar_label.grid_remove()

def parse_level_moves(pokemon, soup, level_moves={}):
    for hidden in soup.body.find_all(style=re.compile(r'display:\s*none')):
            hidden.decompose()
    span_by_leveling = soup.find('span', {"id": re.compile('By_leveling*')})
    if not span_by_leveling:
        return
    table = span_by_leveling.findNext("table")
    if not table:
        return level_moves

    all_rows = table.findAll("tbody")[0].findAll("tr") 
    rows = all_rows[6:-1] # first 5 rows are headers
    for row in rows:
        table_columns = row.findAll("td")
        if len(table_columns) == 0:
            continue
        move_name = ""
        for i in range(0,3):
            column = table_columns[i]
            if i == 0:
                level = column.text.split("\n")[0]
                if not level.isdigit():
                    level = 1
                else:
                    level = int(level)
            if i == 1:
                move_name =  column.text.strip().replace(" ", "").upper()
        if level > 0 and len(move_name) > 0:
            if pokemon[1] in level_moves:
                level_moves[pokemon[1]].append((level, move_name)) 
            else:
                level_moves[pokemon[1]] = [(level, move_name)]
    level_moves[pokemon[1]].sort(key=lambda a: a[0])
    return level_moves

def parse_tutor_and_breeding_moves(pokemon, soup, tutor_moves={}, egg_moves={}):
    for hidden in soup.body.find_all(style=re.compile(r'display:\s*none')):
            hidden.decompose()
    span_by_leveling = soup.find('span', {"id": re.compile('By_leveling*')})
    if not span_by_leveling:
        return tutor_moves, egg_moves
    table = span_by_leveling.findNext("table")
    if not table:
        return tutor_moves, egg_moves

    all_rows = table.findAll("tbody")[0].findAll("tr") 
    other_gens = all_rows[3].findAll("th")[0].findAll("a")
    for gen in other_gens:
        url = 'https://bulbapedia.bulbagarden.net' + gen['href']
        response = requests.get(url)
        if response.status_code != 200:
            continue
        soup_gen = BeautifulSoup(response.content, "html.parser")
        span_by_breeding = soup_gen.find('span', {"id": re.compile('By_breeding*')})
        span_by_tutor = soup_gen.find('span', {"id": re.compile('By_tutoring*')})
        if not span_by_breeding and not span_by_tutor:
            continue
        if span_by_breeding:
            table = span_by_breeding.findNext("table")
            all_rows = table.findAll("tbody")[0].findAll("tr") 
            rows = all_rows[5:-1] # first 5 rows are headers
            for row in rows:
                table_columns = row.findAll("td")
                if len(table_columns) == 0:
                    continue
                move_name = ""
                for i in range(1,2):
                    column = table_columns[i].next
                    if i == 1:
                        move_name =  column.text.strip().replace(" ", "").upper()
                if len(move_name) > 0:
                    if pokemon[1] in egg_moves:
                        if move_name not in egg_moves[pokemon[1]]:
                            egg_moves[pokemon[1]].append(move_name) 
                    else:
                        egg_moves[pokemon[1]] = [move_name]
        
        if span_by_tutor:
            table = span_by_tutor.findNext("table")
            all_rows = table.findAll("tbody")[0].findAll("tr") 
            rows = all_rows[5:-1] # first 5 rows are headers
            for row in rows:
                table_columns = row.findAll("td")
                if len(table_columns) == 0:
                    continue
                move_name = ""
                column = table_columns[0]
                move_name =  column.text.strip().replace(" ", "").upper()
                if len(move_name) > 0:
                    if pokemon[1] in tutor_moves:
                        if move_name not in tutor_moves[pokemon[1]]:
                            tutor_moves[pokemon[1]].append(move_name) 
                    else:
                        tutor_moves[pokemon[1]] = [move_name]
    return tutor_moves, egg_moves


def scrape_moves(pokemons=None, pokemon=None, soup=None):
    if not soup: start_loading("Buscando Aprendizaje por nivel") 
    level_moves = {}
    tutor_moves = {}
    egg_moves = {}
    moves = {
        'level': {},
        'tutor': {},
        'egg': {}
    }
    if pokemon and soup:
        moves["level"] = parse_level_moves(pokemon, soup)
        moves["tutor"], moves["egg"] = parse_tutor_and_breeding_moves(pokemon, soup)
        return moves
    else:
        for pokemon in pokemons:
            if 'fE' in pokemon[1]:
                pokemon_url = pokemon[0]+'♀'
                pokemon_url.title()
            elif 'mA' in pokemon[1]:
                pokemon_url = pokemon_url = pokemon[0]+'♂'
                pokemon_url.title()
            elif "'" in pokemon[0]:
                pokemon_url = pokemon[0].capitalize()
            else:
                pokemon_url = pokemon[0].title()
            pokemon_url = pokemon[0].replace(" ", "_")
            url = "https://bulbapedia.bulbagarden.net/wiki/" + pokemon_url + '_(Pokémon)'
            response = requests.get(url)
            if response.status_code != 200:
                messagebox.showwarning('Pokémon no encontrado', 'No se encontro el pokémon ' +  pokemon[0] + ' en la bulbapedia revise que haya escrito bien el nombre, se siguira buscando el resto de los pokémon')
                continue
            html = response.content
            soup = BeautifulSoup(html, "html.parser")
            moves["level"] = parse_level_moves(pokemon, soup, level_moves)
            moves["tutor"], moves["egg"] = parse_tutor_and_breeding_moves(pokemon, soup, tutor_moves, egg_moves) if search_tutor_moves.get() or search_egg_moves.get() else ({}, {})
        return moves

def scrape(pokemons):
    start_loading("Buscando MTs")
    tms = {}
    global cached_moves
    for pokemon in pokemons:
        if 'fE' in pokemon[1]:
            pokemon_url = pokemon[0]+'♀'
            pokemon_url.title()
        elif 'mA' in pokemon[1]:
            pokemon_url = pokemon_url = pokemon[0]+'♂'
            pokemon_url.title()
        elif "'" in pokemon[0]:
            pokemon_url = pokemon[0].capitalize()
        else:
            pokemon_url = pokemon[0].title()
        pokemon_url = pokemon[0].replace(" ", "_")
        url = "https://bulbapedia.bulbagarden.net/wiki/" + pokemon_url + '_(Pokémon)'
        print(url)
        response = requests.get(url)
        if response.status_code != 200:
            messagebox.showwarning('Pokémon no encontrado', 'No se encontro el pokémon ' +  pokemon[0] + ' en la bulbapedia revise que haya escrito bien el nombre, se siguira buscando el resto de los pokémon')
            continue
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        cached_moves = scrape_moves(None, pokemon, soup)
        span_by_tm = soup.find('span', {"id": re.compile('By_TM*')})        


        if not span_by_tm:
            continue
        table = span_by_tm.findNext("table")
        if not table:
            messagebox.showwarning('No hay MTs', 'No se encontraron MTs para el pokemón en la bulbapedia')
            return {}
        # get all rows from the table
        rows = table.findAll("tbody")[0].findAll("tr")[6:-1] # first 5 rows are headers       
        for row in rows:
            table_columns = row.findAll("td")
            if len(table_columns) == 0:
                continue
            number = ""
            move_name = ""
            for i in range(1,3):
                column = table_columns[i]
                if i == 1:
                    number = column.text.upper().split("\n")[0]
                elif i == 2:
                    move_name = column.text.strip().replace(" ", "").upper()
            if len(number) > 0 and len(move_name) > 0:
                if move_name in tms:
                    tms[move_name].append(pokemon[1].upper()) 
                else:
                    tms[move_name] = [pokemon[1].upper()]
    return tms

def update_file(tms):
    global file_path
    file_modified = False
    start_loading("Actualizando archivo")
    with open(file_path, "r+", encoding='utf-8') as file:
        file_content = file.readlines()
        for i, line in enumerate(file_content):
            if line.startswith("["):
                line_part1 = line.split("[")[1].strip()
                tm_name = line_part1.split("]")[0].strip()
                if i+1 >= len(file_content):
                    break
                if tm_name not in tms:
                    continue
                pokemons = file_content[i+1].strip().split(",")
                for pokemon in tms[tm_name]:
                    if pokemon in pokemons:
                        continue
                    pokemons.append(pokemon)
                    file_content[i+1] = ",".join(pokemons) + "\n"
                    file_modified = True
        if file_modified:
            file.seek(0)
            file.writelines(file_content)
            file.close()
        stop_loading()

def process(pokemons):
    tms = scrape(pokemons)
    if not tms:
        messagebox.showerror('No hay MTs', 'No se encontraron MTs.')
        stop_loading()
    else:
        update_file(tms)
        messagebox.showinfo('MTs actualizadas', f'Se actualizaron las MTs de {len(pokemons)} pokemon(s)')

def search_level_moves(pokemons, existing_moves):
    global cached_moves
    moves = scrape_moves(pokemons) if not cached_moves['level'] else cached_moves
    if moves:
        update_pokemon_file(moves, existing_moves)
        messagebox.showinfo('Movimientos actualizados', f'Se actualizaron los movimientos por nivel de {len(pokemons)} pokemon(s)')
    else:
        messagebox.showerror('No hay movimientos', 'No se encontraron movimientos por nivel.')
        stop_loading()

def update_pokemon_file(moves, existing_moves=[]):
    global file_path_pokemon
    file_modified = False
    start_loading("Actualizando archivo")
    with open(file_path_pokemon, "r+", encoding='utf-8') as file:
        file_content = file.readlines()
        for i, line in enumerate(file_content):
            if line.startswith("InternalName"):
                pokemon_name = line.split("=")[1].strip()
            elif line.startswith("Moves"):
                if not moves['level'] or not moves['level'][pokemon_name]: continue
                current_moves_str = line.split("=")[1].strip()
                current_moves = current_moves_str.split(",")
                current_moves_dict = {}
                for j in range(0,len(current_moves)):
                    if j % 2 != 0:
                        current_moves_dict[current_moves[j]] = current_moves[j-1]
                #current_moves_names = current_moves[1::2]
                if i+1 >= len(file_content):
                    break
                if pokemon_name not in moves['level']:
                    continue
                for move in moves['level'][pokemon_name]:
                    if move[1] not in existing_moves:
                        continue
                    if move[1] in current_moves_dict and update_learn_level.get():
                        current_moves_dict[move[1]] = move[0]
                        continue
                    elif move[1] in current_moves_dict and not update_learn_level.get():
                        continue
                    current_moves_dict[move[1]] = move[0]
                    # for j in range(previous_j, len(current_moves)):
                    #     if j % 2 == 0:
                    #         level = current_moves[j]
                    #     else:
                    #         continue
                    #     if int(move[0]) <= int(level):
                    #         if j+2 < len(current_moves):
                    #             current_moves.insert(j+2, move[1])
                    #             current_moves.insert(j+2, str(move[0]))
                    #         else:
                    #             current_moves.append(str(move[0]))
                    #             current_moves.append(move[1])
                    #         previous_j = j
                    #         break
                current_moves_updated = []
                current_moves_dict = dict(sorted(current_moves_dict.items(), key=lambda item: int(item[1])))
                for key, value in current_moves_dict.items():
                    current_moves_updated.append(str(value))
                    current_moves_updated.append(str(key))
                file_content[i] = "Moves=" + ",".join(current_moves_updated) + "\n"
                file_modified = True
            elif line.startswith("TutorMoves"):
                if not moves['tutor'] or not moves['tutor'][pokemon_name]: continue
                current_tutor_moves = line.split("=")[1].strip().split(",")
                for move in moves['tutor'][pokemon_name]:
                    if move not in existing_moves:
                        continue
                    if move in current_tutor_moves:
                        continue
                    current_tutor_moves.append(move)
                file_content[i] = "TutorMoves=" + ",".join(current_tutor_moves) + "\n"
                file_modified = True
            elif line.startswith("EggMoves"):
                if not moves['egg'] or not moves['egg'][pokemon_name]: continue
                current_egg_moves = line.split("=")[1].strip().split(",")
                for move in moves['egg'][pokemon_name]:
                    if move not in existing_moves:
                        continue
                    if move in current_egg_moves:
                        continue
                    current_egg_moves.append(move)
                file_content[i] = "EggMoves=" + ",".join(current_egg_moves) + "\n"
                file_modified = True
        if file_modified:
            file.seek(0)
            file.writelines(file_content)
            file.close()
        stop_loading()

def read_pokemon_file(file_path_pokemon):
    pokemons = []
    with open (file_path_pokemon, "r", encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("Name"):
                pokemon_name = line.split("=")[1].strip()
            if line.startswith("InternalName"):
                intenal_name = line.split("=")[1].strip()
                pokemons.append([pokemon_name, intenal_name])
    return pokemons

def read_moves_file(file_path_moves):
    moves = []
    with open (file_path_moves, "r", encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            move_name = line.split(',')[1].split(',')[0].strip()
            moves.append(move_name)
    return moves

def execute():
    global tk_poke, entry_poke, file_path, file_path_pokemon, tm_thread
    
    pokemon = tk_poke.get()
    if not pokemon and not file_path_pokemon:
        messagebox.showerror('Los datos del pokemon no pueden estar vacios', 'Ingrese el nombre del pokemon o seleccione el archivo pokemon.txt')
        return entry_poke.focus()
    
    if not file_path or not file_path.endswith("tm.txt"):
        messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo tm.txt')
        return
    if file_path_pokemon:
        pokemons = read_pokemon_file(file_path_pokemon)
    else:
        pokemons = [[pokemon, pokemon.upper().replace(" ", "").replace("-", "")]]
    tm_thread = threading.Thread(target=process, daemon=True, args=(pokemons, ))
    tm_thread.start()    


def update_level_moves():
    global file_path_pokemon, level_moves_thread
    if not file_path_pokemon or not file_path_moves:
        if not file_path_pokemon:
            messagebox.showerror('Los datos del pokemon no pueden estar vacios', 'Debe seleccionar el archivo pokemon.txt')
            return 
    
        if not file_path_moves:
            messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo moves.txt')
            return
        

    pokemons = read_pokemon_file(file_path_pokemon)
    moves = read_moves_file(file_path_moves)

    level_moves_thread = threading.Thread(target=search_level_moves, daemon=True, args=(pokemons, moves,))
    level_moves_thread.start()



if __name__ == "__main__":
    create_screen()

