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
 """

import config as cf
import pandas as pd
import model
import csv
import os

import plotly.graph_objects as go
import pandas as pd

"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo 

def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer

# Funciones para la carga de datos

def loadData(analyzer):
    country_lps = loadLandingPoints(analyzer)
    minC_cables = loadConnections(analyzer)
    loadCountries(analyzer, country_lps, minC_cables)

def loadLandingPoints(analyzer):
    landing_points_file = os.path.join('Data','landing_points.csv')
    input_file = csv.DictReader(open(landing_points_file, encoding="utf-8"),
                                delimiter=",")
    country_lps = {}
    for lp in input_file:
        model.addLandingPoints(analyzer, lp)
        lp_country = lp['name'].split(', ')[-1]
        try:
            country_lps[lp_country].append(lp['landing_point_id'])
        except Exception as exp:
            country_lps[lp_country] = list()
            country_lps[lp_country].append(lp['landing_point_id'])
    return country_lps 

def loadConnections(analyzer):
    connections_file = os.path.join('Data','connections.csv')
    input_file = pd.read_csv(connections_file)
    _,minC_cables = model.addConnections(analyzer, input_file)
    return minC_cables

def loadCountries(analyzer, country_lps, minC_cables):
    countries_file = os.path.join('Data','countries.csv')
    input_file = csv.DictReader(open(countries_file, encoding="utf-8"),
                                delimiter=",")
    for country in input_file:
        try:
            country_i_lps = country_lps[country['CountryName']]
            model.addCountries(analyzer, country, country_i_lps, minC_cables)
        except:
            print(country['CountryName'],'ot found in landing points...')
            continue

def plotGraph():
    connections_file = os.path.join('Data','connections.csv')
    input_file = pd.read_csv(connections_file)
    fig = go.Figure()
    fi
    pass

# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo


def VertexInComponents(analyzer, vertex1, vertex2):
    '''
    Calcula si dos vertices pertenecen al mismo cluster
    '''
    n_components, same_comp = model.VertexInComponents(analyzer, vertex1, vertex2)
    return n_components, same_comp


def mostConnectedLandingPoint(analyzer):
    '''
    Calcula los landing points mas conectados
    '''
    max_deg, max_lps, info_out = model.mostConnectedLandingPoint(analyzer)
    return max_deg, max_lps, info_out


def minDistanceBetweenCapitals(analyzer, countryA, countryB):
    '''
    Calcula la distancia minima entre las capitales de dos paises dados
    '''
    out = model.minDistanceBetweenCapitals(analyzer, countryA, countryB)
    return out

def minDistanceBetweenCities(analyzer, cityA, cityB):
    '''
    Calcula la distancia minima entre las capitales de dos paises dados
    '''
    min_path, total_dist, total_jumps, info_out = model.minDistanceBetweenCities(analyzer, cityA, cityB)
    return min_path, total_dist, total_jumps, info_out

def simulateFailure(analyzer, lp_name):
    '''
    Calcula la lista de paises afectados
    '''
    sort_vals,vert_dist_map,info_out_map, n_affected= model.simulateFailure(analyzer, lp_name)
    return sort_vals,vert_dist_map,info_out_map,n_affected

def LandingPointNN(analyzer, lp_name):
    '''
    Calcula los landing points vecinos
    '''
    adj_edges, sort_dist, info_out = model.LandingPointNN(analyzer, lp_name)
    return adj_edges, sort_dist, info_out

def infraRed(analyzer):
    prime=model.primSearch(analyzer)
    totalNodes=model.totalNodes(prime["marked"])
    minRoute=model.minRoute(prime)
    largeConnection=model.largeConnection(analyzer,prime)
    shortConnection=model.shortConnection(analyzer)
    return totalNodes,minRoute,largeConnection,shortConnection


def maxBandWidth(analyzer, country, cable):

    pass


def totalLPs(analyzer):
    """
    Total de landing points
    """
    return model.totalLPs(analyzer)


def totalConnections(analyzer):
    """
    Total de enlaces entre las paradas
    """
    return model.totalConnections(analyzer)

def totalCountries(analyzer):
    '''
    Retorna el total de países cargados
    '''
    return model.totalCountries(analyzer)

def getLastCountryInfo(analyzer):
    '''
    Retorna la informacion del ultimo pais cargado
    '''
    return model.getLastCountryInfo(analyzer)

def getFirstLandingPointInfo(analyzer):
    '''
    Retorna la informacion del primer landing point cargado
    '''
    return model.getFirstLandingPointInfo(analyzer)