"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as m
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Utils import error as error
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'landing_points': None,
                    'connections': None,
                    'contries': None,
                    'paths': None
                    }

        analyzer['landing_points'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['countries'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['paths'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareLandingPointIds)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')


# Funciones para agregar informacion al catalogo

def addConnections(analyzer, connection):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        origin = int(connection['\ufefforigin'])
        destination = int(connection['destination'])
        lenght = connection['cable_length']
        lenght = formatLength(lenght)
        

        addNode(analyzer, origin)
        addNode(analyzer, destination)
        addEdge(analyzer, origin, destination, lenght)
        addPath(analyzer, origin, destination, connection)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addNodeConnection')


def addCountries(analyzer, country):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        addCountry(analyzer, country)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addCountry')


def addLandingPoints(analyzer, lp):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        addLandingPoint(analyzer, lp)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingPoint')

# Funciones para creacion de datos

def addNode(analyzer, lpoint_id):
    """
    Adiciona  vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], lpoint_id):
            gr.insertVertex(analyzer['connections'], lpoint_id)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addconnection')

def addEdge(analyzer, origin, destination, lenght):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, lenght)
    return analyzer

def addCountry(analyzer, country):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    country_name = country['CountryName']
    entry = m.get(analyzer['countries'], country_name)
    if entry is None:
        new_entry = {'country_name': country['CountryName'],
                     'capital_name': country['CapitalName'],
                     'country_code': country['CountryCode'],
                     'capital_lat': country['CapitalLatitude'],
                     'capital_long': country['CapitalLongitude'],
                     'continent_name': country['ContinentName'],
                     'population': int(country['Population'].replace('.','')),
                     'internet_users': int(country['Internet users'].replace('.',''))}
        m.put(analyzer['countries'], country_name, new_entry)
    return analyzer


def addPath(analyzer, origin, destination, connection):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    path = str(origin) + '-' + str(destination)
    entry = m.get(analyzer['paths'], path)
    if entry is None:
        new_entry = {'origin': origin,
                     'destination': destination,
                     'cable_name': connection['cable_name'],
                     'cable_id': connection['cable_id'],
                     'cable_length': connection['cable_length'],
                     'owners': connection['owners'],
                     'capacityTBPS': float(connection['capacityTBPS'])}
        m.put(analyzer['paths'], path, new_entry)
    return analyzer

def addLandingPoint(analyzer, lp):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    lp_id = int(lp['landing_point_id'])
    entry = m.get(analyzer['landing_points'], lp_id)
    if entry is None:
        new_entry = {'landing_point_id': int(lp['landing_point_id']),
                     'ic': lp['id'],
                     'name': lp['name'],
                     'latitude': lp['latitude'],
                     'longitude': lp['longitude']}
        m.put(analyzer['landing_points'], lp_id, new_entry)
    return analyzer

# Funciones de consulta

def totalEdges(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])

# Funciones utilizadas para comparar elementos dentro de una lista

# Funciones de ordenamiento

def compareLandingPointIds(stop, keyvalue):
    """
    Compara dos estaciones
    """
    code = keyvalue['key']
    if (stop == code):
        return 0
    elif (stop > code):
        return 1
    else:
        return -1

# Utils

def formatLength(length):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    if length == 'n.a.':
        lenght = 0.1
    else:
        lenght = length.split(' ')
        lenght = float(lenght[0].replace(',',''))
    return lenght

def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1