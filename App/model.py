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

import pandas as pd
import random
from haversine import haversine
from os import name
from sys import int_info
from typing import Coroutine
import config as cf
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as m
from DISClib.Algorithms.Graphs import scc, prim
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.Algorithms.Sorting import mergesort as merg
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

        analyzer['landing_points_capitals'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareLandingPointIds)

        analyzer['landing_points_names_capitals'] = m.newMap(numelements=14000,
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

def addConnections(analyzer, connections):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        vertex_listA = []
        vertex_listB = []
        dupsA = []
        dupsB = []
        lp_cables_min_cap = {}
        for i, connection in connections.iterrows():
            # Get origin
            origin = int(connection['origin']); origin_cable = connection['cable_id']
            origin_lp = str(origin) + '*' + origin_cable
            # Get destination
            destination = int(connection['destination']); destination_cable = connection['cable_id']
            destination_lp = str(destination) + '*' + destination_cable
            # Get distance given coordinates
            distance = getDistance(analyzer, origin, destination)
            # Add nodes to graph
            addNode(analyzer, origin_lp)
            addNode(analyzer, destination_lp)
            # Add bidirectional
            addEdge(analyzer, origin_lp, destination_lp, distance)
            addEdge(analyzer, destination_lp, origin_lp, distance)
            # Add path pointer lpA -> lpB and lpB -> lpA
            addPath(analyzer, origin_lp, destination_lp, connection)
            addPath(analyzer, destination_lp, origin_lp, connection)
            # Add to vertex list
            vertex_listA.append(origin)
            vertex_listB.append(destination)
            # Check if duplicated
            if origin in vertex_listA:
                dupsA.append(origin)
            if destination in vertex_listB:
                dupsB.append(destination)
            # Check if cable already saved
            if origin not in list(lp_cables_min_cap.keys()):
                # Add lp cable with min capacity
                sort_TBPS = connections[connections['origin']==origin].sort_values(by=['capacityTBPS']).iloc[0]
                lp_cables_min_cap[origin] = {'cable_id':sort_TBPS['cable_id']}

        # Connect repeated
        for dup_vert in dupsA: # Origins
            get_info = connections[connections['origin']==dup_vert]
            origin_list = get_info['origin'].tolist()
            cable_id_list = get_info['cable_id'].tolist()
            origins_list_lp = []
            for i in range(len(origin_list)):
                conn = str(origin_list[i]) + '*' + cable_id_list[i]
                if conn not in origins_list_lp: 
                    origins_list_lp.append(conn)
            # Create circular list
            origins_circular = []
            for i in range(len(origins_list_lp)-1):
                origins_circular.append([origins_list_lp[i],origins_list_lp[i+1]])
            # Close circular list
            origins_circular.append([origins_list_lp[0],origins_list_lp[-1]])

        for dup_vert in dupsB: # Destinations
            get_info = connections[connections['destination']==dup_vert]
            destination_list = get_info['destination'].tolist()
            cable_id_list = get_info['cable_id'].tolist()
            destinations_list_lp = []
            for i in range(len(destination_list)):
                conn = str(destination_list[i]) + '*' + cable_id_list[i]
                if conn not in destinations_list_lp: 
                    destinations_list_lp.append(conn)
            # Create circular list
            destinations_circular = []
            for i in range(len(destinations_list_lp)-1):
                destinations_circular.append([destinations_list_lp[i],destinations_list_lp[i+1]])
            # Close circular list
            destinations_circular.append([destinations_list_lp[0],destinations_list_lp[-1]])
            
        for dups_origin in origins_circular:
            # Add bidirectional
            addEdge(analyzer, dups_origin[0], dups_origin[1], 0.1)
            addEdge(analyzer, dups_origin[1], dups_origin[0], 0.1)
        for dups_dests in destinations_circular:
            # Add bidirectional
            addEdge(analyzer, dups_dests[0], dups_dests[1], 0.1)
            addEdge(analyzer, dups_dests[1], dups_dests[0], 0.1)

        return analyzer, lp_cables_min_cap
    except Exception as exp:
        error.reraise(exp, 'model:addNodeConnection')


def addCountries(analyzer, country, country_lps, minC_cables):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        connectCapital(analyzer, country, country_lps, minC_cables)
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
        #addCountryLandingPoint(analyzer, lp)

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

def addEdge(analyzer, origin, destination, weight):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(analyzer['connections'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connections'], origin, destination, weight)
    return analyzer
    
def connectCapital(analyzer, country, country_lps, minC_cables):
    '''
    Conectar la capital los landing points del pais
    '''
    country_name = country['CountryName']
    capital_name = country['CapitalName']
    # Generate ld id
    capital_id = random.randint(0,3000)
    # Get coords capital
    cap_lat = float(country['CapitalLatitude'])
    cap_lon = float(country['CapitalLongitude'])
    capital_coors = (cap_lat, cap_lon)
    # Get landing points to connect
    # country_lps = m.get(analyzer['landing_points_countries'], country_name)['value']['landing_points']
    for lp in country_lps:
        lp = int(lp)
        min_cable_lp = minC_cables[lp]['cable_id']
        capital_lp = str(capital_id) + '*' + min_cable_lp
        destination_lp = str(lp) + '*' + min_cable_lp
        # Add capital node
        addNode(analyzer,capital_lp)
        addNode(analyzer,destination_lp)
        # Get coords lp
        destination_coords = getCoordsLPs(analyzer, lp)
        # Get distance
        distance = int(haversine(capital_coors, destination_coords))
        # Add bidirectional
        addEdge(analyzer, capital_lp, destination_lp, distance)
        addEdge(analyzer, destination_lp, capital_lp, distance)
        # Save capital as lp
        addCapitalLandingPoint(analyzer, capital_name, country_name, capital_id, capital_coors, capital_lp)
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
    path = str(origin) + '>' + str(destination)
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
                        'id': lp['id'],
                        'name': lp['name'],
                        'latitude': float(lp['latitude']),
                        'longitude': float(lp['longitude'])}
        m.put(analyzer['landing_points'], lp_id, new_entry_id)
    if entry_name is None:
        new_entry_name = {'name': lp['name'],
                          'landing_point_id': int(lp['landing_point_id']),
                          'latitude': float(lp['latitude']),
                          'longitude': float(lp['longitude'])}
        m.put(analyzer['landing_points_names'], lp_name, new_entry_name)
    return analyzer

def addCapitalLandingPoint(analyzer, lp_name, lp_coutry_name, lp_id, coords, lp_save):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    # lp_name is capital name
    # lp_id is generated random number id

    # entry_id = m.get(analyzer['landing_points_capitals'], lp_id)
    # if entry_id is None:
    new_entry_id = {'name': lp_name,
                        'landing_point_id': lp_id,
                        'landing_point_vertex': lp_save,
                        'latitude': coords[0],
                        'longitude': coords[1]}
    m.put(analyzer['landing_points_capitals'], lp_id, new_entry_id)

    # entry_name = m.get(analyzer['landing_points_names_capitals'], lp_name)
    # if entry_name is None:
    new_entry_name = {'name': lp_name,
                        'landing_point_id': lp_id,
                        'landing_point_vertex': lp_save,
                        'latitude': coords[0],
                        'longitude': coords[1]}
    m.put(analyzer['landing_points_names_capitals'], lp_name, new_entry_name)

    entry_id = m.get(analyzer['landing_points'], lp_id)
    if entry_id is None:
        new_entry_id = {'name': lp_name + ', ' + lp_coutry_name,
                        'landing_point_id': lp_id,
                        'latitude': coords[0],
                        'longitude': coords[1]}
        m.put(analyzer['landing_points'], lp_id, new_entry_id)
    return analyzer



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
        lp_id = int(lp.split('*')[0])
        lp_info = m.get(analyzer['landing_points'],lp_id)['value']
        info_out[lp] = {'name':lp_info['name'],
                        'deg':max_deg}

    return max_deg, max_lps, info_out
    

def minDistanceBetweenCapitals(analyzer, countryA, countryB):
    '''
    Calcula la distancia minima entre las capitales de dos paises dados
    '''
    capitalA = getCapital(analyzer, countryA)
    capitalB = getCapital(analyzer, countryB)
    lpA = formatVertexCapitals(analyzer, capitalA)
    lpB = formatVertexCapitals(analyzer, capitalB)
    analyzer['min_dists_paths'] = djk.Dijkstra(analyzer['connections'], lpA)
    min_path = djk.pathTo(analyzer['min_dists_paths'], lpB)
    cost = djk.distTo(analyzer['min_dists_paths'], lpB)

    if min_path is not None:
        info_out = {}   # save info of each landing point
        total_dist = 0
        for lp in lt.iterator(min_path):
            total_dist += lp['weight']
            for vertex in ['vertexA','vertexB']:
                vertex = InterruptedError(vertex.split('*')[0])
                lp_info = m.get(analyzer['landing_points'],lp[vertex])['value']
                info_out[lp[vertex]] = {'name':lp_info['name']}
        return [min_path, total_dist, info_out]
    else:
        return [min_path]


def minDistanceBetweenCities(analyzer, cityA, cityB):
    '''
    Calcula la distancia minima entre las capitales de dos paises dados
    '''
    lpA = formatVertex(analyzer, cityA)
    lpB = formatVertex(analyzer, cityB)
    analyzer['min_dists_paths'] = djk.Dijkstra(analyzer['connections'], lpA)
    min_path = djk.pathTo(analyzer['min_dists_paths'], lpB)

    if min_path is not None:
        info_out = {}   # save info of each landing point
        total_dist = 0
        total_jumps = 0
        for lp in lt.iterator(min_path):
            total_dist += lp['weight']
            total_jumps += 1
            for vertex in ['vertexA','vertexB']:
                lp_info = m.get(analyzer['landing_points'],lp[vertex])['value']
                info_out[lp[vertex]] = {'name':lp_info['name']}
        return min_path, total_dist, total_jumps, info_out
    else:
        return min_path

def simulateFailure(analyzer, lp_name):
    '''
    Calcula la lista de paises afectados
    '''
    lp_fail = formatVertex(analyzer, lp_name)
    landing_points = gr.vertices(analyzer['connections'])
    adj_edges_list = []
    vert_dist_list = []
    info_out_list  = []
    for lp in lt.iterator(landing_points):
        lp_id = int(lp.split('*')[0])
        if lp_fail == lp_id:
            adj_edges, vert_dist, info_out = LandingPointNN(analyzer, lp)
            adj_edges_list.append(adj_edges)
            vert_dist_list.append(vert_dist)
            info_out_list.append(info_out)
    vert_dist_map = {}
    info_out_map  = {}
    countries = []
    for i in range(len(vert_dist_list)):
        dists = vert_dist_list[i]
        verts = info_out_list[i]
        for k, v in dists.items():
            vert_dist_map[k] = v
        for k, v in verts.items():
            info_out_map[k] = v
            countries.append(v['name'].split(', ')[-1])
    sort_vals = sorted(vert_dist_map.items(), key=lambda x:x[1], reverse=True)
    affected_countries = list(dict.fromkeys(countries))
    n_affected = len(affected_countries)
    return sort_vals,vert_dist_map,info_out_map,n_affected


def LandingPointNN(analyzer, lp_vertex):
    '''
    Calcula los landing points vecinos
    '''
    adj_edges = gr.adjacentEdges(analyzer['connections'], lp_vertex)

    info_out = {}   # save info of each landing point
    vert_dist = {}
    for edge_ in lt.iterator(adj_edges):
        nb = edge_['vertexB']
        nb_id = int(nb.split('*')[0])
        lp_info = m.get(analyzer['landing_points'],nb_id)['value']
        info_out[edge_['vertexB']] = {'name':lp_info['name'],'dist':edge_['weight']}
        vert_dist[edge_['vertexB']] = edge_['weight']
    # sort_dist = sorted(vert_dist.items(), key=lambda x:x[1], reverse=True)
    return adj_edges, vert_dist, info_out

def primSearch(analyzer):
     analyzer["prim"] = prim.PrimMST(analyzer)
     return analyzer["prim"]

def totalNodes(mst):
    return m.size(mst)

def minRoute(mst):
    mst=mst["distTo"]
    keys=m.keySet(mst)
    suma=0.0
    for elementos in lt.iterator(keys):
        info = m.get(mst,elementos)
        if info["value"] >100000000: 
            suma+=0
        else:
            suma+=info["value"]
    return suma

def largeConnection(analyzer,mst):
    componentes=normalList(mst["distTo"])
    analyzer["mst_organized"]=merge_sort(componentes,lt.size(componentes),cmpfunction_merge)
    return lt.firstElement(analyzer["mst_organized"])

def shortConnection(analyzer):
    return lt.getElement(analyzer["mst_organized"],lt.size(analyzer["mst_organized"]))

def normalList(mst):
    normal_list=lt.newList(datastructure="ARRAY_LIST")
    keys=m.keySet(mst)
    for element in lt.iterator(keys):
        lt.addLast(normal_list,m.get(mst,element))
    return normal_list

def cmpfunction_merge(vertex1, vertex2):
    return (float(vertex1["value"]) > float(vertex2["value"]))


def totalLPs(analyzer):
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
    loaded_lp = m.keySet(analyzer['landing_points'])
    first_lp = lt.firstElement(loaded_lp)
    lp_info = m.get(analyzer['landing_points'],first_lp)['value']
    res = {'id': lp_info['landing_point_id'],
           'name': lp_info['name'],
           'lat': lp_info['latitude'],
           'long': lp_info['longitude']}
    return res


# Funciones utilizadas para comparar elementos dentro de una lista

def cmpfunction_merge(vertex1, vertex2):

    return (float(vertex1["value"]) > float(vertex2["value"]))

def merge_sort(lista,size,cmpfunction_merge):
    sub_list = lt.subList(lista,0, size)
    sub_list = lista.copy()
    sorted_list=merg.sort(sub_list, cmpfunction_merge)
    return  sorted_list


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

def vertexInfo(analyzer, vertex_id):
    '''
    Formatea el nombre del vertice a su id
    '''
    vertex = m.get(analyzer['landing_points'],vertex_id)['value']
    if vertex:
        return vertex['landing_point_id']
    else:
        print('Landing point ', vertex_id, ' not found...')


def formatVertexCapitals(analyzer, vertex_name):
    '''
    Formatea el nombre del vertice a su id
    '''
    vertex = m.get(analyzer['landing_points_names_capitals'],vertex_name)['value']
    if vertex:
        return vertex['landing_point_vertex']
    else:
        print('Landing point ', vertex_name, ' not found...')


def getDistance(analyzer, origin, destination):
    '''
    Retorna la ditancia Hervesiana entre dos landing points
    '''
    coords_origin = getCoordsLPs(analyzer, origin)
    coords_destination = getCoordsLPs(analyzer, destination)
    distance = int(haversine(coords_origin, coords_destination))
    return distance


def getCoordsLPs(analyzer, lp_id):
    '''
    Retorna las coordenadas dado un landing point
    '''
    lp = m.get(analyzer['landing_points'], lp_id)['value']
    if lp:
        coords = (lp['latitude'], lp['longitude'])
        return coords
    else:
        print('Landing point not found...')


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