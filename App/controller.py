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
import model
import csv
import os

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
    loadConnections(analyzer)
    loadCountries(analyzer)
    loadLandingPoints(analyzer)

def loadConnections(analyzer):
    connections_file = os.path.join('Data','connections.csv')
    input_file = csv.DictReader(open(connections_file, encoding="utf-8"),
                                delimiter=",")
    for connection in input_file:
        model.addConnections(analyzer, connection)

def loadCountries(analyzer):
    countries_file = os.path.join('Data','countries.csv')
    input_file = csv.DictReader(open(countries_file, encoding="utf-8"),
                                delimiter=",")
    for country in input_file:
        model.addCountries(analyzer, country)

def loadLandingPoints(analyzer):
    landing_points_file = os.path.join('Data','landing_points.csv')
    input_file = csv.DictReader(open(landing_points_file, encoding="utf-8"),
                                delimiter=",")
    for lp in input_file:
        model.addLandingPoints(analyzer, lp)

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
    min_path, total_dist, info_out = model.minDistanceBetweenCapitals(analyzer, countryA, countryB)
    return min_path, total_dist, info_out


def LandingPointNN(analyzer, lp_name):
    '''
    Calcula los landing points vecinos
    '''
    adj_edges, sort_dist, info_out = model.LandingPointNN(analyzer, lp_name)
    return adj_edges, sort_dist, info_out

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