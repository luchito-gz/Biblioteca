import json
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path

ARCHIVO = Path("juegos.json")


def cargar():
    if ARCHIVO.exists():
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    return[]

def guardar(juegos):
    ARCHIVO.write_text(
        json.dumps(juegos, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    
    
    
class Biblioteca:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Mi biblioteca de juegos")
        self.ventana.geometry("900x600")
        self.juegos = cargar()
        
    #Barra de busqueda
        marco_busqueda = ttk.Frame(ventana, padding = 10)
        marco_busqueda.pack(fill = "x")
        ttk.Label(marco_busqueda, text="Buscar:").pack(side="left")
        self.texto_busqueda = tk.StringVar()
        self.texto_busqueda.trace_add("write", lambda *args: self.actualizar_lista())
        ttk.Entry(marco_busqueda, textvariable=self.texto_busqueda).pack(
            side="left", fill="x", expand=True, padx=5
        )
        
        #Tabla con la lista de juegos
        marco_tabla = ttk.Frame(ventana, padding=(10, 0))
        marco_tabla.pack(fill="both", expand=True)
        self.tabla = ttk.Treeview(
            marco_tabla, columns=("nombre","genero"), show="headings", selectmode="browse"
        )
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("genero", text="Genero")
        self.tabla.column("nombre", width=420)
        self.tabla.column("genero", width=200)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        barra.pack(side="right", fill="y")
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.bind("<Double-1>", lambda evento: self.jugar())
        
        #botones
        marco_botones = ttk.Frame(ventana, padding=10)
        marco_botones.pack(fill="x")
        ttk.Button(marco_botones, text="▶ jugar", command=self.jugar).pack(side="left")
        ttk.Button(marco_botones, text="agregar juego", command=self.agregar).pack(
            side="left", padx=5
        )
        ttk.Button(marco_botones, text="Eliminar", command=self.eliminar).pack(side="left")
        
        self.actualizar_lista()
        
    def actualizar_lista(self):
        filtro = self.texto_busqueda.get().lower()
        self.tabla.delete(*self.tabla.get_children())
        for i, juego in enumerate(self.juegos):
            if filtro in juego["nombre"].lower():
                self.tabla.insert(
                    "", "end", iid=str(i), values=(juego["nombre"], juego["genero"])
                )
                
    def indice_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Primero elegi un juego de la lista")
            return None
        return int(seleccion[0])
    
    def agregar(self):
        ruta = filedialog.askopenfilename(
            title= "Elegi el ejecutable del juego",
            filetypes=[("Ejecutables", "*.exe *.bat"), ("Todos los archivos", "*.*")],
        )
        if not ruta:
            return
        nombre = simpledialog.askstring(
            "Nombre", "Nombre del juego", initialvalue=Path(ruta).stem, parent=self.ventana
        )
        if not nombre:
            return
        genero = simpledialog.askstring("Genero", "Genero:", parent=self.ventana)
        self.juegos.append(
            {"nombre": nombre, "ruta": ruta, "genero": genero or "sin genero" }
        )
        guardar(self.juegos)
        self.actualizar_lista()
        
    def jugar(self):
        indice = self.indice_seleccionado()
        if indice is None:
            return
        ruta = Path(self.juegos[indice]["ruta"])
        if not ruta.exists():
            messagebox.showerror("Error", f"No se encontro el archivo:\n{ruta}")
            return
        
        try:
            subprocess.Popen([str(ruta)], cwd=ruta.parent)
        except OSError as error:
            messagebox.showerror("No se pudo abrir el juego", str(error))
            
    def eliminar(self):
        indice = self.indice_seleccionado()
        if indice is None:
            return
        nombre = self.juegos[indice]["nombre"]
        if messagebox.askyesno("eliminar", f"¿Quitar '{nombre}' de la biblioteca"):
            self.juegos.pop(indice)
            guardar(self.juegos)
            self.actualizar_lista()
            
if __name__ == "__main__":
    ventana = tk.Tk()
    Biblioteca(ventana)
    ventana.mainloop()
            
    