import ply.yacc as yacc
from lexer import tokens
from pprint import pprint

# ------------------ Tabla de Símbolos --------------------
tabla_simbolos = {}

# ------------------ Validación de Tipos --------------------
def obtener_tipo_expresion(expresion):
    """Determina el tipo de una expresión"""
    if expresion[0] == 'numero':
        valor = expresion[1]
        if isinstance(valor, int):
            return 'Entero'
        elif isinstance(valor, float):
            return 'Real'
    elif expresion[0] == 'cadena':
        return 'Texto'
    elif expresion[0] == 'variable':
        variable = expresion[1]
        if variable in tabla_simbolos:
            return tabla_simbolos[variable]['tipo']
        else:
            return 'Desconocido'
    elif expresion[0] == 'capturar':
        tipo_captura = expresion[1]
        parametro = expresion[2]
        tipo_parametro = obtener_tipo_expresion(parametro)
        
        if tipo_captura == 'Entero' and tipo_parametro != 'Entero':
            return f'Error: Captura.Entero espera Entero, no {tipo_parametro}'
        elif tipo_captura == 'Real' and tipo_parametro not in ['Entero', 'Real']:
            return f'Error: Captura.Real espera número, no {tipo_parametro}'
        elif tipo_captura == 'Texto' and tipo_parametro != 'Texto':
            return f'Error: Captura.Texto espera texto, no {tipo_parametro}'
        
        return tipo_captura
    elif expresion[0] == 'operacion_binaria':
        return 'Real'
    
    return 'Desconocido'

def tipos_compatibles(tipo_declarado, tipo_expresion):
    """Verifica si los tipos son compatibles"""
    if 'Error:' in str(tipo_expresion):
        return False
        
    compatibilidad = {
        'Entero': ['Entero'],
        'Real': ['Entero', 'Real'],  
        'Texto': ['Texto']
    }
    return tipo_expresion in compatibilidad.get(tipo_declarado, [])

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
    # Filtrar sentencias None (errores)
    if len(t) == 3:
        if t[2] is not None:
            t[0] = t[1] + [t[2]]
        else:
            t[0] = t[1]
    else:
        t[0] = [t[1]] if t[1] is not None else []

def p_tipo(t):
    '''tipo : ENTERO
            | REAL
            | TEXTO'''
    t[0] = t[1]

def p_sentencia_declaracion(t):
    'sentencia : IDENTIFICADOR tipo PUNTO_Y_COMA'
    var = t[1]
    tipo_var = t[2]
    linea = t.lineno(1)

    if var in tabla_simbolos:
        print(f"⚠️  [Línea {linea}] ¡Epa! La variable '{var}' ya la declaraste mano, no la repitas.")
        t[0] = None
    else:
        tabla_simbolos[var] = {'tipo': tipo_var, 'valor': None, 'linea': linea}
        t[0] = ('declarar', var, tipo_var)
        print(f"✅ [Línea {linea}] ¡Bien ahí! Variable '{var}' quedó como {tipo_var}")

def p_sentencia_asignacion(t):
    'sentencia : IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA'
    var = t[1]
    expr = t[3]
    linea = t.lineno(1)

    if var not in tabla_simbolos:
        print(f"⚠️  [Línea {linea}] ¡Ombe! La variable '{var}' no existe, declárala primero pues.")
        t[0] = None
    else:
        tipo_declarado = tabla_simbolos[var]['tipo']
        tipo_expresion = obtener_tipo_expresion(expr)
        
        if 'Error:' in str(tipo_expresion):
            print(f"❌ [Línea {linea}] {tipo_expresion}")
            t[0] = None
        elif not tipos_compatibles(tipo_declarado, tipo_expresion):
            print(f"❌ [Línea {linea}] ¡Eso no cuadra parce! No puedes meter {tipo_expresion} en '{var}' que es {tipo_declarado}")
            t[0] = None
        else:
            tabla_simbolos[var]['valor'] = expr
            t[0] = ('asignar', var, expr)
            print(f"✅ [Línea {linea}] ¡Tá bueno! {tipo_expresion} → {var}({tipo_declarado})")

def p_sentencia_mensaje(t):
    '''sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ CADENA_TEXTO PARENTESIS_DER PUNTO_Y_COMA
                 | MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_Y_COMA'''
    linea = t.lineno(1)
    t[0] = ('mensaje_texto', t[5])
    print(f"✅ [Línea {linea}] Mensaje listo pa' mostrar")

def p_expresion_binaria(t):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion POR expresion
                 | expresion DIVIDIDO expresion'''
    t[0] = ('operacion_binaria', t[2], t[1], t[3])

def p_expresion_grupo(t):
    'expresion : PARENTESIS_IZQ expresion PARENTESIS_DER'
    t[0] = t[2]

def p_expresion_valor(t):
    '''expresion : NUMERO_ENTERO
                 | NUMERO_REAL'''
    t[0] = ('numero', t[1])

def p_expresion_identificador(t):
    'expresion : IDENTIFICADOR'
    var = t[1]
    linea = t.lineno(1)
    if var not in tabla_simbolos:
        print(f"⚠️  [Línea {linea}] ¡Ajá! La variable '{var}' no existe todavía.")
        t[0] = ('error', var)
    else:
        t[0] = ('variable', var)

def p_expresion_cadena(t):
    'expresion : CADENA_TEXTO'
    t[0] = ('cadena', t[1])

def p_expresion_captura(t):
    'expresion : CAPTURA PUNTO tipo PARENTESIS_IZQ expresion PARENTESIS_DER'
    t[0] = ('capturar', t[3], t[5])

# Variable global para rastrear errores
ultimo_error_tipo = None

def p_error(t):
    global ultimo_error_tipo
    
    if t:
        linea = t.lineno
        # Detectar específicamente falta de punto y coma
        if t.type in ['IDENTIFICADOR', 'MENSAJE', 'CAPTURA']:
            print(f"❌ [Línea {linea}] ¡Ey parce! Te faltó el punto y coma (;) en la línea anterior, no te descuides.")
            ultimo_error_tipo = 'missing_semicolon'
        else:
            print(f"❌ [Línea {linea}] ¡Qué vaina! Hay un error con '{t.value}' aquí mano (tipo: {t.type})")
            ultimo_error_tipo = 'syntax_error'
        
        # Recuperación: buscar siguiente punto y coma
        while True:
            tok = analizador_sintactico.token()
            if not tok or tok.type == 'PUNTO_Y_COMA':
                break
        analizador_sintactico.errok()
        return tok
    else:
        print("❌ ¡Ombe! El archivo se acabó pero falta algo, revísalo completo.")
        ultimo_error_tipo = 'eof_error'

# Construcción del parser
analizador_sintactico = yacc.yacc()

# ------------------------------------------
# 🧪 PRUEBA FINAL
# ------------------------------------------
if __name__ == "__main__":
    tabla_simbolos.clear()
    
    # CASO 1: Con punto y coma faltante
    print("=" * 70)
    print("🌴 CASO 1: Falta punto y coma después de saludo2 (estilo costeño)")
    print("=" * 70)
    codigo1 = '''
    saludo Texto;
    saludo = Captura.Texto("Hola, Mundo!");
    saludo2 Texto;
    saludo2 = "Hola"
    edad Entero;
    edad = Captura.Entero("25");
    edad2 Entero;
    edad2 = Captura.Entero(30);
    '''
    tabla_simbolos.clear()
    resultado1 = analizador_sintactico.parse(codigo1)
    print("\n📋 Resultado:")
    pprint(resultado1)
    
    # CASO 2: Variable no declarada
    print("\n" + "=" * 70)
    print("🌴 CASO 2: Usando variable sin declarar")
    print("=" * 70)
    codigo2 = '''
    saludo Texto;
    saludo = "Hola";
    despedida = "Chao";
    '''
    tabla_simbolos.clear()
    resultado2 = analizador_sintactico.parse(codigo2)
    print("\n📋 Resultado:")
    pprint(resultado2)
    
    # CASO 3: Todo correcto
    print("\n" + "=" * 70)
    print("🌴 CASO 3: Todo bien pelao, sin errores")
    print("=" * 70)
    codigo3 = '''
    nombre Texto;
    nombre = "Carlos";
    edad Entero;
    edad = 25;
    altura Real;
    altura = 1,75;
    '''
    tabla_simbolos.clear()
    resultado3 = analizador_sintactico.parse(codigo3)
    print("\n📋 Resultado:")
    pprint(resultado3)