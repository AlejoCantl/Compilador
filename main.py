import tkinter as tk
from parser import Compilador
from gui import CompiladorGUI
    
# Crear ventana principal
root = tk.Tk()
    
# Crear instancia del compilador
compilador = Compilador()
    
# Crear interfaz gráfica
app = CompiladorGUI(root, compilador)
    
# Iniciar aplicación
root.mainloop()