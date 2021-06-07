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
from DISClib.ADT import map as m

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
    # Plot 
    plotConnectionsGraph()

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
            print(country['CountryName'],'not found in landing points...')
            continue

# Funciones de visualizacion

def prepareDataPlot():
    connections_file = os.path.join('Data','connections.csv')
    landing_points_file = os.path.join('Data','landing_points.csv')
    df_cons = pd.read_csv(connections_file)
    df_lps = pd.read_csv(landing_points_file)
    # Merge origin coords
    df_cons = df_cons.set_index('origin')
    df_lps  = df_lps.rename(columns={'landing_point_id':'origin'}).set_index('origin')
    df_orins = df_cons.merge(df_lps, how='left', on='origin')
    df_orins = df_orins.rename(columns={'latitude':'lat_origin', 'longitude':'lon_origin'})
    # Merge destination coords
    df_lps = df_lps.reset_index()
    df_lps = df_lps.rename(columns={'origin':'destination'}).set_index('destination')
    df_end = df_orins.reset_index()
    df_end = df_end.set_index('destination')
    df_end = df_end.merge(df_lps, how='left', on='destination')
    df_end = df_end.rename(columns={'latitude':'lat_destination', 'longitude':'lon_destination'})
    df_end = df_end.drop(columns=['id_x','name_x','id_y','name_y'])
    df_end = df_end.reset_index()
    return df_end

def plotConnectionsGraph():
    connections = prepareDataPlot()
    fig = go.Figure()
    for i in range(len(connections)):
        fig.add_trace(
            go.Scattergeo(
                lon = [connections['lon_origin'][i], connections['lon_destination'][i]],
                lat = [connections['lat_origin'][i], connections['lat_destination'][i]],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
                opacity = float(connections['capacityTBPS'][i]) / float(connections['capacityTBPS'].max()),
            ))
    fig.update_layout(
        title_text = 'Connections',
        showlegend = False,
        geo = dict(
            # projection_type = 'azimuthal equal area',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
            ),
        )
    fig.show()

def plotTwoLPs(analyzer,lp1, lp2):
    landing_points_file = os.path.join('Data','landing_points.csv')
    lps_info = pd.read_csv(landing_points_file)
    lpA = model.formatVertex(analyzer,lp1)
    lpB = model.formatVertex(analyzer,lp2)
    lpA_info = lps_info[lps_info['landing_point_id']==lpA]
    lpB_info = lps_info[lps_info['landing_point_id']==lpB]
    # Plot
    fig = go.Figure(data=go.Scattergeo(
        lat = [lpA_info['latitude'].iloc[0], lpB_info['latitude'].iloc[0]],
        lon = [lpA_info['longitude'].iloc[0], lpB_info['longitude'].iloc[0]],
        mode = 'lines',
        line = dict(width = 2, color = 'blue'),
        ))
    fig.update_layout(
        title_text = 'Landing points in same cluster',
        showlegend = False,
        geo = dict(
            # projection_type = 'azimuthal equal area',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
            ),
        )
    fig.show()

def plotMostConnected(analyzer, info_out, lp):
    neighbors_lps =  info_out['neighbors']
    df_l = []
    for nn_lp in neighbors_lps:
        lp_info = m.get(analyzer['landing_points'], nn_lp)['value']
        df_save = pd.DataFrame()
        df_save['origin'] = [lp]
        df_save['destination'] = [nn_lp]
        df_save['lat_origin'] = [info_out['lat']]
        df_save['lon_origin'] = [info_out['lon']]
        df_save['lat_destination'] = [lp_info['latitude']]
        df_save['lon_destination'] = [lp_info['longitude']]
        df_l.append(df_save)
    df_plot = pd.concat(df_l)
    df_plot = df_plot.reset_index()
    # Plot
    fig = go.Figure()
    for i in range(len(df_plot)):
        fig.add_trace(
            go.Scattergeo(
                lon = [df_plot['lon_origin'][i], df_plot['lon_destination'][i]],
                lat = [df_plot['lat_origin'][i], df_plot['lat_destination'][i]],
                mode = 'lines',
                line = dict(width = 2,color = 'green'),
            ))
    fig.update_layout(
        title_text = 'Most Connected - {}'.format(info_out['name']),
        showlegend = False,
        geo = dict(
            # projection_type = 'azimuthal equal area',
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
            ),
        )
    fig.show()

    pass

# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo


def VertexInComponents(analyzer, vertex1, vertex2):
    '''
    Calcula si dos vertices pertenecen al mismo cluster
    '''
    n_components, same_comp = model.VertexInComponents(analyzer, vertex1, vertex2)
    plotTwoLPs(analyzer,vertex1, vertex2)
    return n_components, same_comp


def mostConnectedLandingPoint(analyzer):
    '''
    Calcula los landing points mas conectados
    '''
    max_deg, max_lps, info_out = model.mostConnectedLandingPoint(analyzer)
    for i in range(len(max_lps)):
        plotMostConnected(analyzer, info_out[max_lps[i]], max_lps[i])
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