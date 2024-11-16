import random
import yogi
import json
import pathlib
import uuid
from dataclasses import dataclass
from typing import Dict, List, Literal

def obtener_datos_persona():
    """Recolecta los datos de una persona"""
    nombre = input("Ingresa el nombre de la persona: ")
    interes = input("Ingresa el interés de la persona: ")
    nom = yogi.read(str)
    email = yogi.read(str)
    age = yogi.read(int)
    year_of_study = yogi.read(Literal)
    university = yogi.read(str)
    experience_level = yogi.read(Literal)
    hackathons_done = yogi.read(int)
    objective = yogi.read(str)
    return {"nombre": nombre, "age": age, "year_of_study": year_of_study, "university": university, "experience_level": experience_level, "hackathons_done": hackathons_done,}

def agrupar_por_interes(personas):
    """Agrupa a las personas según su interés."""
    grupos = {}
    
    # Agrupar personas por su interés
    for persona in personas:
        interes = persona['interes']
        if interes not in grupos:
            grupos[interes] = []
        grupos[interes].append(persona)
    
    # Ahora que tenemos grupos por interés, formamos los subgrupos
    subgrupos = []
    for interes, grupo in grupos.items():
        # Si el grupo tiene más de 4 personas, las dividimos en subgrupos de 4
        while len(grupo) > 4:
            subgrupos.append(grupo[:4])
            grupo = grupo[4:]
        # Si queda menos de 4 personas, las dejamos como están
        if grupo:
            subgrupos.append(grupo)
    
    return subgrupos

def mostrar_grupos(subgrupos):
    """Muestra los subgrupos generados."""
    for i, subgrupo in enumerate(subgrupos, 1):
        nombres = [persona['nombre'] for persona in subgrupo]
        print(f"Grupo {i}: {', '.join(nombres)}")

def main():
    personas = []
    num_personas = int(input("¿Cuántas personas quieres agrupar? "))
    
    # Recolectar datos de las personas
    for _ in range(num_personas):
        persona = obtener_datos_persona()
        personas.append(persona)
    
    # Agrupar a las personas
    subgrupos = agrupar_por_interes(personas)
    
    # Mostrar los subgrupos resultantes
    mostrar_grupos(subgrupos)

if __name__ == "__main__":
    main()
