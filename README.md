# Get Moves & TMs For PBS

Esta es una pequeña aplicacion que usa beautifulsoup para scrapear bulbapedia, obtiene todos los MTs y movimientos por nivel que puede aprender el pokemon ingresado y los agrega al archivo tm.txt y pokemon.txt de la carpeta PBS respectivamente.

## Como usar la aplicacion

1. Descarga el zip get_moves.zip de la pestaña de releases.
2. Descromprime el zip
3. Ejecuta el archivo get_moves.exe que está dentro de la carpeta get_moves del zip.
4. Ingresa el nombre del pokemon del que quieres obtener los MTs.
   1. Puedes tambien seleccionar el archivo pokemon.txt de la carpeta PBS de tu proyecto y buscara las MTs para todos los pokemon que esten en el archivo.
      Tengan en cuenta que esta funcionalidad tarda bastante ya que hace una request a bulbapedia por cada pokemon. Si tienen todos los pokemon serian mas de 1000 requests
5. Seleciona el archivo tm.txt de la carpeta PBS de tu proyecto.
6. Haz click en el boton "Buscar MTs".
7. Si todo salio bien, el programa te mostrara un mensaje de que se han agregado los MTs al archivo tm.txt
8. Si deseas que se agreguen los movimientos por nivel al archivo pokemon.txt, selecciona el archivo pokemon.txt de la carpeta PBS de tu proyecto.
   1. Haz click en el boton "Buscar Movimientos por nivel".
   2. Eso te desplegara nuevas opciones, selecciona el archivo moves.txt donde lo solicita.
   3. Haz click en el botón "Actualizar aprendizaje por nivel."
   4. Si todo salio bien, el programa te mostrara un mensaje de que se han agregado los movimientos al archivo pokemon.txt

## Recomendaciones  

### Recomiendo fuerte hacer una copia de seguridad del archivo tm.txt y pokemon.txt antes de usar la aplicación

### No actualizar ninguno de los archivos mientras el programa esta en ejecución.

### Si el programa esta en el status "Actualizando archivo", no cerrarlo hasta que termine ya que podría ocasionar que los archivos queden corruptos o que pierdan información:

### Tengo un problema, "El progrma no termina"
Puede ser que el programa siga procesando, hay una barra abajo que indica que el programa esta trabajando, al finalizar les mostrará un mensaje, ir a buscar infomación a otras paginas de internet a través de web scraping es un proceso lento, y si lo hacen para un archivo de pokemon.txt muy grande tardará bastante, dejenlo corriendo de fondo mientras hacen otras cosas. 


