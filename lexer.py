import ply.lex as lex

# Variable global para almacenar errores léxicos
errores_lexicos = []

def agregar_error_lexico(linea, mensaje):
    """Agrega un error léxico a la lista global"""
    errores_lexicos.append({
        'tipo': 'error',
        'linea': linea,
        'mensaje': mensaje
    })

def limpiar_errores_lexicos():
    """Limpia la lista de errores léxicos"""
    errores_lexicos.clear()

# ----------------------- TOKENS -----------------------------
tokens = (
    'IGUAL', 'MAS', 'MENOS', 'POR', 'DIVIDIDO',
    'NUMERO_ENTERO', 'NUMERO_REAL', 'IDENTIFICADOR',
    'PARENTESIS_IZQ', 'PARENTESIS_DER',
    'PUNTO_Y_COMA', 'COMA', 'CADENA_TEXTO', 'PUNTO'
)

# Palabras reservadas
reservadas = {
    'Texto': 'TEXTO',
    'Entero': 'ENTERO',
    'Real': 'REAL',
    'Captura': 'CAPTURA',
    'Mensaje': 'MENSAJE'
}

tokens = tokens + tuple(reservadas.values())

# -------------EXPRESIONES REGULARES--------------------
t_IGUAL = r'='
t_MAS = r'\+'
t_MENOS = r'-'
t_POR = r'\*'
t_DIVIDIDO = r'/'
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'
t_PUNTO_Y_COMA = r';'
t_COMA = r','
t_PUNTO = r'\.'

t_ignore = ' \t'

# -------------------REGLAS DE TOKENS-------------------------

# ⭐ ORDEN IMPORTANTE: Esta regla debe estar ANTES de t_IDENTIFICADOR
def t_NUMERO_PEGADO_A_LETRA(t):
    r'\d+[a-zA-Z_][a-zA-Z0-9_]*'
    agregar_error_lexico(t.lexer.lineno, f"¡Eche tú que ve! Las variables no pueden empezar con números: '{t.value}'")
    t.type = 'IDENTIFICADOR'
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    return t

# ⭐ NUEVO: Acepta tanto coma como punto para números reales
def t_NUMERO_REAL(t):
    r'\d+[,\.]\d+'
    # Normalizar: convertir coma a punto para Python
    t.value = float(t.value.replace(',', '.'))
    return t

def t_NUMERO_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_CADENA_TEXTO(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_COMENTARIO_SIMPLE(t):
    r'//.*'
    pass

def t_COMENTARIO_MULTILINEA(t):
    r'/\*[\s\S]*?\*/'
    pass

def t_nueva_linea(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    agregar_error_lexico(t.lexer.lineno, f"Carácter ilegal: '{t.value[0]}'")
    t.lexer.skip(1)

# Construcción del analizador léxico
analizador_lexico = lex.lex()
