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
tms = {}
cached_moves = {
    'level':{},
    'tutor':{},
    'egg':{}
}
class FileManager:
    
    @staticmethod
    def open_file():
        global file_path
        file_path = filedialog.askopenfilename(title="Abrir tm.txt")
        if not file_path or not file_path.endswith("tm.txt"):
            messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo tm.txt')
            return
        file_path_label = file_path.split("/")
        file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
        app.file_label.configure(text="Archivo: " + file_path_label)

    @staticmethod
    def open_pokemon_file():
        global file_path_pokemon 
        file_path_pokemon = filedialog.askopenfilename(title="Abrir pokemon.txt")
        if (file_path_pokemon and not file_path_pokemon.endswith("pokemon.txt")):
            messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo pokemon.txt')
            return
        app.poke_name_label.grid_remove()
        app.entry_poke.grid_remove()
        file_path_label = file_path_pokemon.split("/")
        file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
        app.file_label_pokemon.configure(text="Archivo: " + file_path_label)

    @staticmethod
    def open_moves_file():
        global file_path_moves
        file_path_moves = filedialog.askopenfilename(title="Abrir moves.txt")
        if (file_path_moves and not file_path_moves.endswith("moves.txt")):
            messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo moves.txt')
            return
        file_path_label = file_path_moves.split("/")
        file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
        app.file_label_moves.configure(text="Archivo: " + file_path_label)
    
    @staticmethod
    def update_file(tms):
        global file_path
        file_modified = False
        app.start_loading("Actualizando archivo")
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
            app.stop_loading()
    
    @staticmethod
    def update_pokemon_file(self, moves, existing_moves=[]):
        global file_path_pokemon
        file_modified = False
        app.start_loading("Actualizando archivo")
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
                        if move[1] in current_moves_dict and app.update_learn_level.get():
                            current_moves_dict[move[1]] = move[0]
                            continue
                        elif move[1] in current_moves_dict and not app.update_learn_level.get():
                            continue
                        current_moves_dict[move[1]] = move[0]
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
            app.stop_loading()

    @staticmethod
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

    @staticmethod
    def read_moves_file(file_path_moves):
        moves = []
        with open (file_path_moves, "r", encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                move_name = line.split(',')[1].split(',')[0].strip()
                moves.append(move_name)
        return moves


class Scraper:
    @staticmethod
    def scrape(pokemons, search_everything=False):
        app.start_loading("Buscando MTs")
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
            response = requests.get(url)
            if response.status_code != 200:
                messagebox.showwarning('Pokémon no encontrado', 'No se encontro el pokémon ' +  pokemon[0] + ' en la bulbapedia revise que haya escrito bien el nombre, se siguira buscando el resto de los pokémon')
                continue
            html = response.content
            soup = BeautifulSoup(html, "html.parser")
            cached_moves = Scraper.scrape_moves(None, pokemon, soup, search_everything)
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
    
    @staticmethod
    def scrape_moves(pokemons=None, pokemon=None, soup=None, search_everything=False):
        if not soup: app.start_loading("Buscando Movimientos") 
        level_moves = {}
        tutor_moves = {}
        egg_moves = {}
        moves = {
            'level': {},
            'tutor': {},
            'egg': {}
        }
        if pokemon and soup:
            moves["level"] = Scraper.parse_level_moves(pokemon, soup)
            # moves["tutor"], moves["egg"] = Scraper.parse_tutor_and_breeding_moves(pokemon, soup) if app.search_tutor_moves.get() or app.search_egg_moves.get() else ({}, {})
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
                moves["level"] = Scraper.parse_level_moves(pokemon, soup, level_moves)
                moves["tutor"], moves["egg"] = Scraper.parse_tutor_and_breeding_moves(pokemon, soup, tutor_moves, egg_moves) if app.search_tutor_moves.get() or app.search_egg_moves.get() else ({}, {})
            return moves

    @staticmethod
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

    @staticmethod
    def parse_tutor_and_breeding_moves(pokemon, soup, tutor_moves={}, egg_moves={}):
        for hidden in soup.body.find_all(style=re.compile(r'display:\s*none')):
                hidden.decompose()
        span_by_leveling = soup.find('span', {"id": re.compile('By_leveling*')})
        if not span_by_leveling:
            return tutor_moves, egg_moves
        table = span_by_leveling.findNext("table")
        if not table:
            return tutor_moves, egg_moves
        span_evolution = soup.find('span', {"id": re.compile('Evolution')})
        is_baby_pokemon = False if 'evolves from' in span_evolution.findNext("p").text.strip() else True
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
            if span_by_breeding and app.search_egg_moves.get() and is_baby_pokemon:
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
            
            if span_by_tutor and app.search_tutor_moves.get():
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

def process(pokemons, search_everything=False):
    tms = Scraper.scrape(pokemons, search_everything)
    if not tms:
        messagebox.showerror('No hay MTs', 'No se encontraron MTs.')
        app.stop_loading()
    else:
        FileManager.update_file(tms)
        messagebox.showinfo('MTs actualizadas', f'Se actualizaron las MTs de {len(pokemons)} pokemon(s)')

def search_level_moves(pokemons, existing_moves):
    global cached_moves
    moves = Scraper.scrape_moves(pokemons) if not cached_moves['level'] else cached_moves
    if not moves["egg"] and app.search_egg_moves.get():
        moves = Scraper.scrape_moves(pokemons)
    if not moves["tutor"] and app.search_tutor_moves.get():
        moves = Scraper.scrape_moves(pokemons)
    if moves:
        FileManager.update_pokemon_file(moves, existing_moves)
        if not app.search_egg_moves.get() and not app.search_tutor_moves.get():
            messagebox.showinfo('Movimientos actualizados', f'Se actualizaron los movimientos por nivel de {len(pokemons)} pokemon(s)')
        else:
            messagebox.showinfo('Movimientos actualizados', f'Se actualizaron los movimientos de {len(pokemons)} pokemon(s)')
    else:
        messagebox.showerror('No hay movimientos', 'No se encontraron movimientos para los Pokémon del archivo.')
        app.stop_loading()



def execute(search_everything=False):
    global file_path, file_path_pokemon
    
    pokemon = app.tk_poke.get()
    if not pokemon and not file_path_pokemon:
        messagebox.showerror('Los datos del pokemon no pueden estar vacios', 'Ingrese el nombre del pokemon o seleccione el archivo pokemon.txt')
        return app.entry_poke.focus()
    
    if not file_path or not file_path.endswith("tm.txt"):
        messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo tm.txt')
        return
    if file_path_pokemon:
        pokemons = FileManager.read_pokemon_file(file_path_pokemon)
    else:
        pokemons = [[pokemon, pokemon.upper().replace(" ", "").replace("-", "")]]
    app.tm_thread = threading.Thread(target=process, daemon=True, args=(pokemons, search_everything, ))
    app.btn_excute['state'] = 'disabled'
    app.btn_moves['state'] = 'disabled'
    app.btn_search_everything['state'] = 'disabled'
    app.tm_thread.start()
    app.check_tm_thread()    


def update_level_moves():
    global file_path_pokemon
    if not file_path_pokemon or not file_path_moves:
        if not file_path_pokemon:
            messagebox.showerror('Los datos del pokemon no pueden estar vacios', 'Debe seleccionar el archivo pokemon.txt')
            return 
    
        if not file_path_moves:
            messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo moves.txt')
            return

    pokemons = FileManager.read_pokemon_file(file_path_pokemon)
    moves = FileManager.read_moves_file(file_path_moves)

    app.level_moves_thread = threading.Thread(target=search_level_moves, daemon=True, args=(pokemons, moves,))
    app.btn_moves['state'] = 'disabled'
    app.level_moves_thread.start()
    app.check_level_moves_thread()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PBS Updater")
        self.iconbitmap(resource("tmicon.ico"))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.tm_thread = None
        self.level_moves_thread = None
        self.moves_is_on = False
        self.update_learn_level = tk.BooleanVar()
        self.search_tutor_moves = tk.BooleanVar()
        self.search_egg_moves = tk.BooleanVar()
        self.btn_excute = None
        self.btn_moves = None
        self.btn_search_everything = None
        self.select_file_label = None
        self.file_button = None
        self.checkbox_update_learn_level = None
        self.checkbox_tutor_moves = None
        self.checkbox_egg_moves = None
        self.btn_moves = None
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="Seleccione el archivo pokemon.txt").grid(row=0, column=0, pady=5, padx=15, sticky='w')
        tk.Button(self, text="Seleccionar archivo", command=FileManager.open_pokemon_file).grid(row=0, column=1, pady=5, padx=15, ipadx=8)
        self.file_label_pokemon = tk.Label(self, text="Archivo Pokemons: ")
        self.file_label_pokemon.grid(row=1, column=0, pady=5, padx=15, columnspan=3, sticky='NW')
        tk.Button(self, text="Deseleccionar Archivo", command=self.remove_pokemon_file).grid(row=1, column=1, pady=5, padx=15, ipadx=1)
        self.poke_name_label = tk.Label(self, text="Ingrese el nombre del pokemon")
        self.poke_name_label.grid(row=2, column=0, pady=5, padx=15, sticky='w')
        self.tk_poke = tk.StringVar()
        self.entry_poke = tk.Entry(self, textvariable=self.tk_poke)
        self.entry_poke.focus()
        self.entry_poke.grid(row=2, column=1, pady=5, padx=15)
        tk.Label(self, text="Si selecciona el archivo pokemon.txt este campo será ingorado y se hara la búsqueda para todos los pokémon del archivo", fg='#f00').grid(row=3, column=0, columnspan=3, pady=5, padx=15, sticky='w')
        tk.Label(self, text="Seleccione el archivo tms.txt").grid(row=4, column=0, pady=5, padx=15, sticky='w')
        tk.Button(self, text="Seleccionar archivo", command=FileManager.open_file).grid(row=4, column=1, pady=5, padx=15)
        self.file_label = tk.Label(self, text="Archivo: ")
        self.file_label.grid(row=5, column=0, pady=5, padx=15, columnspan=3, sticky='NW')

        self.btn_excute = tk.Button(self, text="Buscar MTs", command=self.execute_button)
        self.btn_excute.grid(row=6, columnspan=3, pady=5, padx=15, sticky='we')

        self.toggle_button = tk.Button(self, text="Desplegar opciones para buscar movimientos por nivel, tutor y huevo", relief="raised", command=self.turn_on_level_moves)
        self.toggle_button.grid(row=7, columnspan=3, column=0, pady=5, padx=15, sticky='we')
        self.file_label_moves = tk.Label(self, text="Archivo: ")

        self.progressbar_label = tk.Label(self, text="")
        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=200, mode="indeterminate")

        self.btn_search_everything = tk.Button(self, text="Buscar movimientos y MTs", command=lambda: self.execute_button(True))

        self.select_file_label = tk.Label(self, text="Seleccione el archivo moves.txt")
        self.file_button = tk.Button(self, text="Seleccionar archivo", command=FileManager.open_moves_file)
        self.checkbox_update_learn_level = tk.Checkbutton(self, text="Actualizar nivel de aprendizaje", variable = self.update_learn_level)
        self.checkbox_tutor_moves = tk.Checkbutton(self, text="Buscar movimientos por tutor", variable = self.search_tutor_moves)
        self.checkbox_egg_moves = tk.Checkbutton(self, text="Buscar movimientos huevo", variable = self.search_egg_moves)
        self.btn_moves = tk.Button(self, text="Buscar y actualizar movimientos", command=update_level_moves)
    
    def remove_pokemon_file(self):
        self.file_path_pokemon = ""
        self.file_label_pokemon.configure(text="Archivo Pokemons: ")
        self.poke_name_label.grid(row=2, column=0, pady=5, padx=15, sticky='w')
        self.entry_poke.focus()
        self.entry_poke.grid(row=2, column=1, pady=5, padx=15)

    def turn_on_level_moves(self):
        self.moves_is_on = not self.moves_is_on
        if self.moves_is_on:
            self.checkbox_update_learn_level.grid(row=8, column=0, pady=5, padx=15, sticky='w')
            self.checkbox_tutor_moves.grid(row=9, column=0, pady=5, padx=15, sticky='w')
            self.checkbox_egg_moves.grid(row=9, column=1, pady=5)
            self.select_file_label.grid(row=10, column=0, pady=5, padx=15, sticky='w')
            self.file_button.grid(row=10, column=1, pady=5)
            self.file_label_moves.grid(row=11, column=0, pady=5, padx=15, columnspan=3, sticky='NW')
            self.btn_moves.grid(row=12, columnspan=3, pady=5, padx=15, sticky='we')
            self.toggle_button.config(relief="sunken")
            self.btn_search_everything.grid(row=13, columnspan=3, pady=5, padx=15, sticky='we')
        else:
            self.select_file_label.grid_remove()
            self.file_button.grid_remove()
            self.file_label_moves.grid_remove()
            self.btn_moves.grid_remove()
            self.checkbox_egg_moves.grid_remove()
            self.checkbox_tutor_moves.grid_remove()
            self.checkbox_update_learn_level.grid_remove()
            self.btn_search_everything.grid_remove()
            self.toggle_button.config(relief="raised")

    def start_loading(self, label):
        self.progressbar_label.configure(text=label)
        if not self.progressbar_label.grid_info():
            self.progressbar_label.grid(row=14, columnspan=3, pady=5, padx=15, sticky='we')
        self.progressbar.grid(row=15, columnspan=3, pady=5, padx=15, sticky='we')
        self.progressbar.start()
        self.update_idletasks()
    
    def stop_loading(self):
        self.progressbar.stop()
        self.progressbar.grid_remove()
        self.progressbar_label.grid_remove()

    def execute_button(self):
        search_everything = True if self.search_egg_moves.get() or self.search_tutor_moves.get() else False
        execute(search_everything)
    
    def check_tm_thread(self):
        if self.tm_thread.is_alive():
            self.after(100, self.check_tm_thread)
            return
        self.btn_excute['state'] = 'normal'
        self.btn_moves['state'] = 'normal'
        self.btn_search_everything['state'] = 'normal'

    def check_level_moves_thread(self):
        if self.level_moves_thread.is_alive():
            self.after(100, self.check_level_moves_thread)
            return
        self.btn_moves['state'] = 'normal'
        self.btn_excute['state'] = 'normal'
        self.btn_search_everything['state'] = 'normal'

    def on_closing(self):
        if (not self.tm_thread or not self.tm_thread.is_alive()) and (not self.level_moves_thread or not self.level_moves_thread.is_alive()):
            self.quit()
            return
        if messagebox.askokcancel("Salir", "¿Está seguro de que desea salir y cancelar todos los procesos pendientes? Esto puede generar que los archivos queden corruptos o que se pierda información existente."):
            self.quit()


if __name__ == "__main__":
    app = App()
    app.mainloop()

