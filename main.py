from ply import lex, yacc
from pprint import pprint

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

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    return t

def t_NUMERO_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
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
    print(f"⚠️  Carácter ilegal: '{t.value[0]}'")
    t.lexer.skip(1)

# Construcción del analizador léxico
analizador_lexico = lex.lex()

# ------------------ GRAMÁTICA -----------------------

precedence = (
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR', 'DIVIDIDO'),
)

def p_programa(t):
    'programa : lista_sentencias'
    t[0] = t[1]

def p_lista_sentencias(t):
    '''lista_sentencias : lista_sentencias sentencia
                        | sentencia'''
    t[0] = t[1] + [t[2]] if len(t) == 3 else [t[1]]

def p_tipo(t):
    '''tipo : ENTERO
            | REAL
            | TEXTO'''
    t[0] = t[1]

def p_sentencia_declaracion(t):
    'sentencia : IDENTIFICADOR tipo PUNTO_Y_COMA'
    t[0] = ('declarar', t[1], t[2])

def p_sentencia_asignacion(t):
    'sentencia : IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA'
    t[0] = ('asignar', t[1], t[3])

def p_sentencia_mensaje(t):
    '''sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_Y_COMA'''
    t[0] = ('mensaje_texto', t[5])

def p_expresion_binaria(t):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion POR expresion
                 | expresion DIVIDIDO expresion'''
    t[0] = (t[2], t[1], t[3])

def p_expresion_grupo(t):
    'expresion : PARENTESIS_IZQ expresion PARENTESIS_DER'
    t[0] = t[2]

def p_expresion_valor(t):
    '''expresion : NUMERO_ENTERO
                 | NUMERO_REAL'''
    t[0] = ('numero', t[1])

def p_expresion_identificador(t):
    'expresion : IDENTIFICADOR'
    t[0] = ('identificador', t[1])

def p_expresion_cadena(t):
    'expresion : CADENA_TEXTO'
    t[0] = ('cadena', t[1])

def p_expresion_captura(t):
    'expresion : CAPTURA PUNTO tipo PARENTESIS_IZQ expresion PARENTESIS_DER'
    t[0] = ('capturar', t[3], t[5])

def p_error(t):
    print(f"Error de sintaxis en '{t.value}'" if t else "Error de sintaxis al final del archivo")

# Construcción del parser
analizador_sintactico = yacc.yacc()

# ------------------------------------------
# 🧪 PRUEBA
# ------------------------------------------
if __name__ == "__main__":
    codigo = '''
    saludo Texto;
    saludo = Captura.Texto("Hola, Mundo!");
    edad Entero;
    edad = Captura.Entero(25);
    altura Real;
    altura = Captura.Real(1.75);
    Mensaje.Texto("Tu edad es: " + edad);
    '''
    resultado = analizador_sintactico.parse(codigo)
    pprint(resultado)
