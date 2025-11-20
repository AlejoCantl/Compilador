import tkinter as tk
from tkinter import scrolledtext
import re

class CompiladorGUI:
    def __init__(self, root, compilador):
        self.root = root
        self.compilador = compilador
        self.root.title("🌴 Compilador Costeñol")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f4f8')
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        main_frame = tk.Frame(self.root, bg='#f0f4f8')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.crear_header(main_frame)
        
        panel_container = tk.Frame(main_frame, bg='#f0f4f8')
        panel_container.pack(fill=tk.BOTH, expand=True)
        
        self.crear_panel_editor(panel_container)
        self.crear_panel_consola(panel_container)
    
    def crear_header(self, parent):
        """Crea el encabezado con título y estadísticas"""
        header_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="🌴 Compilador Costeñol", 
                               font=('Arial', 24, 'bold'), bg='white', fg='#2c3e50')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        subtitle_label = tk.Label(header_frame, text="¡Dale pues, escribe tu código y dale al botón!", 
                                 font=('Arial', 11), bg='white', fg='#7f8c8d')
        subtitle_label.pack(side=tk.LEFT, padx=10)
        
        # Estadísticas
        self.stats_frame = tk.Frame(header_frame, bg='white')
        self.stats_frame.pack(side=tk.RIGHT, padx=20)
        
        self.aciertos_label = tk.Label(self.stats_frame, text="0\nAciertos", 
                                       font=('Arial', 14, 'bold'), bg='#d4edda', fg='#155724',
                                       width=10, relief=tk.RAISED, bd=2, padx=10, pady=5)
        self.aciertos_label.pack(side=tk.LEFT, padx=5)
        
        self.errores_label = tk.Label(self.stats_frame, text="0\nErrores", 
                                      font=('Arial', 14, 'bold'), bg='#f8d7da', fg='#721c24',
                                      width=10, relief=tk.RAISED, bd=2, padx=10, pady=5)
        self.errores_label.pack(side=tk.LEFT, padx=5)
    
    def crear_panel_editor(self, parent):
        """Crea el panel del editor de código"""
        left_panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        editor_header = tk.Frame(left_panel, bg='#3498db')
        editor_header.pack(fill=tk.X)
        
        tk.Label(editor_header, text="📝 Editor de Código", font=('Arial', 14, 'bold'),
                bg='#3498db', fg='white').pack(side=tk.LEFT, padx=15, pady=10)
        
        self.analizar_btn = tk.Button(editor_header, text="▶ Analizar", 
                                      font=('Arial', 12, 'bold'),
                                      bg='#2ecc71', fg='white', 
                                      activebackground='#27ae60',
                                      relief=tk.RAISED, bd=3,
                                      cursor='hand2',
                                      command=self.analizar_codigo)
        self.analizar_btn.pack(side=tk.RIGHT, padx=15, pady=5)
        
        # Área de ejemplos ARRIBA - MÁS VISIBLE
        self.crear_ejemplos(left_panel)
        
        # Área de código
        self.codigo_text = scrolledtext.ScrolledText(left_panel, 
                                                     font=('Consolas', 11),
                                                     bg='#2c3e50', fg='#ecf0f1',
                                                     insertbackground='white',
                                                     relief=tk.FLAT,
                                                     padx=10, pady=10,
                                                     wrap=tk.WORD)
        self.codigo_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def crear_ejemplos(self, parent):
        """Crea el área de ejemplos con mejor visibilidad"""
        ejemplos_frame = tk.Frame(parent, bg='#fff9e6', relief=tk.GROOVE, bd=3)
        ejemplos_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Header de ejemplos
        header_ejemplos = tk.Frame(ejemplos_frame, bg='#ffd700')
        header_ejemplos.pack(fill=tk.X)
        
        tk.Label(header_ejemplos, text="💡 Ejemplos de Sintaxis Válida", 
                font=('Arial', 10, 'bold'), bg='#ffd700', fg='#000000').pack(pady=5)
        
        # Frame para el texto con scrollbar horizontal
        texto_frame = tk.Frame(ejemplos_frame, bg='#fffef0')
        texto_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar horizontal
        scrollbar_x = tk.Scrollbar(texto_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Texto de ejemplos
        ejemplo_text = tk.Text(texto_frame, height=5, font=('Consolas', 9),
                              bg='#fffef0', fg='#333333', relief=tk.FLAT,
                              wrap=tk.NONE, borderwidth=0,
                              xscrollcommand=scrollbar_x.set)
        ejemplo_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        scrollbar_x.config(command=ejemplo_text.xview)
        
        # ⭐ ACTUALIZADO: Ejemplos con punto Y coma
        ejemplos = """// Declaración y asignación
nombre Texto;
nombre = "Carlos";
edad Entero;
edad = 25;
altura Real;
altura = 1,75;  // ó 1.75 (ambos funcionan)"""
        
        ejemplo_text.insert('1.0', ejemplos)
        ejemplo_text.config(state=tk.DISABLED)
    
    def crear_panel_consola(self, parent):
        """Crea el panel de la consola de resultados"""
        right_panel = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        console_header = tk.Frame(right_panel, bg='#e74c3c')
        console_header.pack(fill=tk.X)
        
        tk.Label(console_header, text="🖥️ Consola de Resultados", 
                font=('Arial', 14, 'bold'),
                bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=15, pady=10)
        
        # Área de consola
        console_frame = tk.Frame(right_panel, bg='#1e1e1e')
        console_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.consola_text = scrolledtext.ScrolledText(console_frame, 
                                                      font=('Consolas', 10),
                                                      bg='#1e1e1e', fg='#d4d4d4',
                                                      relief=tk.FLAT,
                                                      padx=10, pady=10,
                                                      state=tk.DISABLED,
                                                      wrap=tk.WORD)
        self.consola_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags de colores
        self.consola_text.tag_config('exito', foreground='#4ade80', font=('Consolas', 10, 'bold'))
        self.consola_text.tag_config('error', foreground='#f87171', font=('Consolas', 10, 'bold'))
        self.consola_text.tag_config('advertencia', foreground='#fbbf24', font=('Consolas', 10, 'bold'))
        self.consola_text.tag_config('linea', foreground='#60a5fa', font=('Consolas', 9))
        self.consola_text.tag_config('resumen', foreground='#c084fc', font=('Consolas', 11, 'bold'))
    
    def analizar_codigo(self):
        """Ejecuta el análisis del código"""
        codigo = self.codigo_text.get('1.0', tk.END)
        
        # Limpiar consola
        self.consola_text.config(state=tk.NORMAL)
        self.consola_text.delete('1.0', tk.END)
        
        # ⭐ VALIDACIÓN PREVIA: Verificar si hay código (sin contar comentarios)
        codigo_sin_comentarios = re.sub(r'//.*', '', codigo)
        codigo_sin_comentarios = re.sub(r'/\*[\s\S]*?\*/', '', codigo_sin_comentarios)
        codigo_limpio = codigo_sin_comentarios.strip()
        
        if not codigo_limpio:
            self.consola_text.insert(tk.END, "❌ ", 'error')
            self.consola_text.insert(tk.END, "¡Ombe! No hay nada que analizar, escribe algo pues.\n", 'error')
            self.actualizar_estadisticas(0, 0)
            self.consola_text.config(state=tk.DISABLED)
            return
        
        # Analizar con el compilador
        resultado = self.compilador.analizar(codigo)
        
        # Mostrar mensajes
        self.mostrar_mensajes(resultado['mensajes'])
        
        # Actualizar estadísticas SOLO en el header
        stats = resultado['estadisticas']
        self.actualizar_estadisticas(stats['aciertos'], stats['errores'])
        
        self.consola_text.config(state=tk.DISABLED)
    
    def mostrar_mensajes(self, mensajes):
        """Muestra los mensajes en la consola"""
        for msg in mensajes:
            linea_text = f"[Línea {msg['linea']}] "
            self.consola_text.insert(tk.END, linea_text, 'linea')
            
            if msg['tipo'] == 'exito':
                self.consola_text.insert(tk.END, f"✅ {msg['mensaje']}\n", 'exito')
            elif msg['tipo'] == 'error':
                self.consola_text.insert(tk.END, f"❌ {msg['mensaje']}\n", 'error')
            else:
                self.consola_text.insert(tk.END, f"⚠️  {msg['mensaje']}\n", 'advertencia')
        
        # Resumen final
        if mensajes:
            self.mostrar_resumen(mensajes)
    
    def mostrar_resumen(self, mensajes):
        """Muestra el resumen de compilación"""
        aciertos = sum(1 for m in mensajes if m['tipo'] == 'exito')
        errores = sum(1 for m in mensajes if m['tipo'] == 'error')
        
        self.consola_text.insert(tk.END, f"\n{'='*50}\n", 'resumen')
        self.consola_text.insert(tk.END, f"📊 RESUMEN FINAL\n", 'resumen')
        self.consola_text.insert(tk.END, f"{'='*50}\n", 'resumen')
        
        if errores == 0 and aciertos > 0:
            self.consola_text.insert(tk.END, "¡Quedó chevere! Todo bien 🎉\n", 'exito')
        elif errores > 0:
            self.consola_text.insert(tk.END, f"¡Ombe! Hay {errores} error(es) que arreglar\n", 'error')
    
    def actualizar_estadisticas(self, aciertos, errores):
        """Actualiza las estadísticas SOLO en el header"""
        self.aciertos_label.config(text=f"{aciertos}\nAciertos")
        self.errores_label.config(text=f"{errores}\nErrores")