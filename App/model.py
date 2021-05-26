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


from os import name
from sys import int_info
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
                    'landing_points_names':None,
                    'connections': None,
                    'countries': None,
                    'paths': None
                    }

        analyzer['landing_points'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['landing_points_names'] = m.newMap(numelements=14000,
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
        # if lenght != 'n.a.':
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
    lp_name = lp['name'].split(',')[0]
    entry_id = m.get(analyzer['landing_points'], lp_id)
    entry_name = m.get(analyzer['landing_points_names'], lp_name)

    if entry_id is None:
        new_entry_id = {'landing_point_id': int(lp['landing_point_id']),
                        'ic': lp['id'],
                        'name': lp['name'],
                        'latitude': lp['latitude'],
                        'longitude': lp['longitude']}
        m.put(analyzer['landing_points'], lp_id, new_entry_id)
    if entry_name is None:
        new_entry_name = {'name':lp['name'],
                          'landing_point_id': int(lp['landing_point_id'])}
        m.put(analyzer['landing_points_names'], lp_name, new_entry_name)
    return analyzer

# Funciones de consulta


def VertexInComponents(analyzer, vertex1, vertex2):
    '''
    Calcula si dos vertices pertenecen al mismo cluster
    '''
    n_components = NumberConnectedComponents(analyzer)
    components = analyzer['components']
    vert1_comp, vert2_comp = None, None
    for elem_ in components['idscc']['table']['elements']:
        if elem_['key'] == vertex1:
            vert1_comp = elem_['value']
        if elem_['key'] == vertex2:
            vert2_comp = elem_['value']
    
    same_comp = False
    if vert1_comp == vert2_comp:
        same_comp = True

    return n_components, same_comp


def NumberConnectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    return scc.connectedComponents(analyzer['components'])


def mostConnectedLandingPoint(analyzer):
    '''
    Calcula los landing points mas conectados
    '''
    landing_points = gr.vertices(analyzer['connections'])
    lp_degs = {}    # organize in dict
    for lp in lt.iterator(landing_points):
        deg_ = gr.degree(analyzer['connections'],lp)
        try:
            lp_degs[deg_].append(lp)
        except Exception as exp:
            lp_degs[deg_] = list()
            lp_degs[deg_].append(lp)
    degs_list = (lp_degs.keys())
    max_deg = max(degs_list)    # get max degree
    max_lps = lp_degs[max_deg]

    info_out = {}   # save info of each max landing point
    for lp in max_lps:
        lp_info = m.get(analyzer['landing_points'],lp)['value']
        info_out[lp] = {'name':lp_info['name'],
                        'deg':max_deg}

    return max_deg, max_lps, info_out
    

def minDistanceBetweenCapitals(analyzer, countryA, countryB):
    '''
    Calcula la distancia minima entre las capitales de dos paises dados
    '''
    capitalA = getCapital(analyzer, countryA)
    capitalB = getCapital(analyzer, countryB)
    nameA = '{}, {}'.format(capitalA, countryA)
    nameB = '{}, {}'.format(capitalB, countryB)
    lpA = formatVertex(analyzer, capitalA)
    lpB = formatVertex(analyzer, capitalB)
    analyzer['min_dists_paths'] = djk.Dijkstra(analyzer['connections'], lpA)
    min_path = djk.pathTo(analyzer['min_dists_paths'], lpB)
    
    info_out = {}   # save info of each max landing point
    total_dist = 0
    for lp in lt.iterator(min_path):
        total_dist += lp['weight']
        for vertex in ['vertexA','vertexB']:
            lp_info = m.get(analyzer['landing_points'],lp[vertex])['value']
            info_out[lp[vertex]] = {'name':lp_info['name']}

    return min_path, total_dist, info_out


def LandingPointNN(analyzer, lp_name):
    '''
    Calcula los landing points vecinos
    '''
    lp = formatVertex(analyzer, lp_name)
    adj_edges = gr.adjacentEdges(analyzer['connections'], lp)

    info_out = {}   # save info of each max landing point
    vert_dist = {}
    for edge_ in lt.iterator(adj_edges):
        lp_info = m.get(analyzer['landing_points'],edge_['vertexB'])['value']
        info_out[edge_['vertexB']] = {'name':lp_info['name'],'dist':edge_['weight']}
        vert_dist[edge_['vertexB']] = edge_['weight']
    sort_dist = sorted(vert_dist.items(), key=lambda x:x[1], reverse=True)
    return adj_edges, sort_dist, info_out


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

def totalCountries(analyzer):
    '''
    Retorna el total de países cargados
    '''
    return m.size(analyzer['countries'])

def getLastCountryInfo(analyzer):
    '''
    Retorna la informacion del ultimo pais cargado
    '''
    loaded_countries = m.keySet(analyzer['countries'])
    last_country = lt.lastElement(loaded_countries)
    info_country = m.get(analyzer['countries'],last_country)['value']
    res = {'country': info_country['country_name'],
           'population': info_country['population'],
           'internet_users': info_country['internet_users']}
    return res

def getFirstLandingPointInfo(analyzer):
    '''
    Retorna la informacion del primer landing point cargado
    '''
    loaded_lp = gr.vertices(analyzer['connections'])
    first_lp = lt.firstElement(loaded_lp)
    lp_info = m.get(analyzer['landing_points'],first_lp)['value']
    res = {'id': lp_info['landing_point_id'],
           'name': lp_info['name'],
           'lat': lp_info['latitude'],
           'long': lp_info['longitude']}
    return res


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


def formatVertex(analyzer, vertex_name):
    '''
    Formatea el nombre del vertice a su id
    '''
    vertex = m.get(analyzer['landing_points_names'],vertex_name)['value']
    if vertex:
        return vertex['landing_point_id']
    else:
        print('Landing point ', vertex_name, ' not found...')


def getCapital(analyzer, country_name):
    '''
    Retorna capital de un capital de un pais dado
    '''
    country_info = m.get(analyzer['countries'],country_name)
    if country_info:
        return country_info['value']['capital_name']
    else:
        print('Country ', country_name, ' not found...')


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