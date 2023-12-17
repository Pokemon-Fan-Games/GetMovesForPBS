# Create web scraper for https://www.wikidex.net/wiki that scrapes all learnable tms for a pokemon input by the user

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import sys, os
def resource(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



file_path = ""
file_path_pokemon = ""
current_tms = {}
entry_poke = None
file_label = None
file_label_pokemon = None
poke_name_label = None
tk_poke = None
execute_button = None
progressbar = None
progressbar_label = None
tms = {}
root = tk.Tk()
def create_screen():
    global entry_poke
    global file_label
    global file_label_pokemon
    global poke_name_label
    global tk_poke
    global progressbar
    global progressbar_label
# Get user input
    global root
    #root.geometry("350x150")
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
    tk.Button(root, text="Seleccione el archivo", command=open_file).grid(row=4, column=1, pady=5, padx=15)
    file_label = tk.Label(root, text="Archivo: ")
    file_label.grid(row=5, column=0, pady=5, padx=15, columnspan=3, sticky='NW')
    tk.Button(root, text="Buscar MTs", command=execute).grid(row=6, columnspan=3, pady=5, padx=15, sticky='we')

    progressbar_label = tk.Label(root, text="")
    progressbar = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")

    root.title("Buscador de MTs")
    root.iconbitmap(resource("tmicon.ico"))
    root.mainloop()

def open_file():
    global file_path 
    global file_label
    file_path = filedialog.askopenfilename(title="Abrir tm.txt")
    if not file_path or not file_path.endswith("tm.txt"):
        tk.messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo tm.txt')
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
        tk.messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo pokemon.txt')
        return
    poke_name_label.grid_remove()
    entry_poke.grid_remove()
    file_path_label = file_path_pokemon.split("/")
    file_path_label = '/'.join(file_path_label[len(file_path_label)-3:])
    file_label_pokemon.configure(text="Archivo: " + file_path_label)

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
        progressbar_label.grid(row=7, columnspan=3, pady=5, padx=15, sticky='we')
    progressbar_label.grid(row=7, columnspan=3, pady=5, padx=15, sticky='we')
    progressbar.grid(row=8, columnspan=3, pady=5, padx=15, sticky='we')
    progressbar.start(10)
    root.update_idletasks()

def stop_loading():
    global progressbar
    global progressbar_label
    progressbar.stop()
    progressbar.grid_remove()
    progressbar_label.grid_remove()

def scrape(pokemons):
    # Get the html from the website
    start_loading("Buscando MTs")
    tms = {}
    for pokemon in pokemons:
        url = "https://bulbapedia.bulbagarden.net/wiki/" + pokemon.capitalize() + '_(Pokémon)'
        response = requests.get(url)
        if response.status_code != 200:
            tk.messagebox.showerror('Pokémon no encontrado', 'No se encontro el pokémon en la wikidex revise que haya escrito bien el nombre')
            entry_poke.focus()
            return {}
        html = response.content
        # get table with id tm-globalid-2
        soup = BeautifulSoup(html, "html.parser")
        span_by_tm = soup.find('span', {"id":"By_TM"})
        if not span_by_tm:
            continue
        table = span_by_tm.findNext("table")
        if not table:
            tk.messagebox.showwarning('No hay MTs', 'No se encontraron MTs para el pokemón en la wikidex')
            return {}
        # get all rows from the table
        rows = table.findAll("tbody")[0].findAll("tr")[6:-1] # first 5 rows are headers
        # get all the tms from the rows
        
        moves = []
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
                moves.append(move_name)
        tms[pokemon.upper()] = moves
    return tms

def update_file(tms, pokemon):
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
                if tm_name not in tms[pokemon]:
                    continue
                pokemons = file_content[i+1].strip().split(",")
                if pokemon not in pokemons:
                    pokemons.append(pokemon)
                    file_content[i+1] = ",".join(pokemons) + "\n"
                    file_modified = True
        if file_modified:
            file.seek(0)
            file.writelines(file_content)
            file.close()
        stop_loading()

def process(pokemon):
    tms = scrape(pokemon)
    pokemon = pokemon.upper()
    update_file(tms, pokemon)
    tk.messagebox.showinfo('MTs actualizadas', 'Se actualizaron las MTs: ' + ','.join(tms[pokemon]) + ' para el pokémon ' + pokemon)

def read_pokemon_file(file_path_pokemon):
    pokemons = []
    with open (file_path_pokemon, "r", encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("InternalName"):
                pokemon_name = line.split("=")[1].strip()
                pokemons.append(pokemon_name)
    return pokemons

def execute():
    global tk_poke
    global entry_poke
    global file_path
    global file_path_pokemon
    pokemon = tk_poke.get()
    if not pokemon and not file_path_pokemon:
        tk.messagebox.showerror('Los datos del pokemon no pueden estar vacios', 'Ingrese el nombre del pokemon o seleccione el archivo pokemon.txt')
        return entry_poke.focus()
    
    if not file_path or not file_path.endswith("tm.txt"):
        tk.messagebox.showerror('Seleccione el archivo', 'Debe seleccionar el archivo tm.txt')
        return
    if file_path_pokemon:
        pokemons = read_pokemon_file(file_path_pokemon)
    else:
        pokemons = [pokemon]
    process_thread = threading.Thread(target=process, args=(pokemons, ))
    process_thread.start()    



if __name__ == "__main__":
    create_screen()

