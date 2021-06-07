"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import ipapi
import controller
from DISClib.ADT import list as lt
from DISClib.ADT import stack
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

def printMenu():
    print("\nBienvenido")
    print("1- Cargar información en el catálogo")
    print("2- Encontrar componentes conectados y pertenencias")
    print("3- Encontrar landing points mas conectados")
    print("4- Encontrar ruta minima entre dos paises")
    print("5- Identificar red de expansion minima")
    print("6- Simular fallo de landing point")
    print("7- Calcular el ancho de banda maximo (bono)")
    print("8- Calcular la ruta minima para enviar informacion entre dos IPs (bono)")
    print("9- Salir")


def exMinima(analyzer):
    ans=controller.infraRed(cont["connections"])
    print("Numero de nodos conectados:"+str(ans[0]))
    print("Costo total de la red de expanción minima: "+str(ans[1]))
    print("La conexión más larga", str(ans[2]["key"]),"tiene una distancia en Km de ", str(ans[2]["value"]))
    print("La conexión más corta", str(ans[3]["key"]),"tiene una distancia en Km de ", str(ans[3]["value"]))


catalog = None

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    if int(inputs[0]) == 1:
        print("Cargando información de los archivos ....")
        cont = controller.init()
        controller.loadData(cont)
        numedges = controller.totalConnections(cont)
        numvertex = controller.totalLPs(cont)
        numcountries = controller.totalCountries(cont)
        firstlp = controller.getFirstLandingPointInfo(cont)
        lastcountry = controller.getLastCountryInfo(cont)
        print('Numero de landing points (vertices): ' + str(numvertex))
        print('Numero de conexiones (arcos): ' + str(numedges))
        print('Numero de paises : ' + str(numcountries))
        print('1st Landing point id: ', firstlp['id'],
              '| nombre :', firstlp['name'],
              '| cords :' , 'Lat. {} Long. {}'.format(firstlp['lat'],firstlp['long']))
        print('Last country Info: ', lastcountry['country'], ' -- ',
              'poblacion :', str(lastcountry['population']),
              '| usuarios :', str(lastcountry['internet_users']))

    elif int(inputs[0]) == 2:     # Req 1
        print('\nDefinir landings points a analizar...')
        lp1 = input('Landing point 1: ')
        lp2 = input('Landing point 2: ')
        n_comp, same = controller.VertexInComponents(cont, lp1, lp2)
        print('Numero total de clusters :', n_comp)
        if same is True:
            print(lp1,'y',lp2,'SI pertenecen al mismo cluster.')
        else:
            print(lp1,'y',lp2,'NO pertenecen al mismo cluster.')

    elif int(inputs[0]) == 3:     # Req 2
        maxdeg, mostconnected, info_out =  controller.mostConnectedLandingPoint(cont)
        print('\nLanding point(s) mas conectado(s)')
        for i, mostconn_ in enumerate(mostconnected):
            print(i+1,'--', 'landing point id :', mostconn_,
                  '| nombre :', info_out[mostconn_]['name'],
                  '| conexiones :', maxdeg)

    elif int(inputs[0]) == 4:     # Req 3
        print('\nDefinir paises para calcular la ruta minima...')
        countryA = input('Pais A: ')
        countryB = input('Pais B: ')
        out = controller.minDistanceBetweenCapitals(cont, countryA, countryB)
        if out[0] is not None:
            min_path = out[0]
            total_dist = out[1]
            info_out = out[0]
            print('\nRuta minima entre',countryA,'y',countryB)
            for path_ in lt.iterator(min_path):
                print(info_out[path_['vertexA']]['name'],'-->',info_out[path_['vertexB']]['name'],'dist [km]:', path_['weight'])
            print('Total distance [km] :', total_dist)
        else:
            print('\nNo existe una ruta de conexion entre', countryA, 'y', countryB)

    elif int(inputs[0]) == 5:
        print('\n Calculando red de expansión minima...')
        exMinima(cont)

    elif int(inputs[0]) == 6:     # Req 5
        print('\nDefinir landing point para simular fallo...')
        lp = input('Nombre del landing point (ciudad): ')
        sort_vals,vert_dist_map,info_out_map,n_affected= controller.simulateFailure(cont, lp)
        print('\nNumero de paises afectados :',n_affected)
        for i, country_ in enumerate(sort_vals):
            print(i+1,'--',info_out_map[country_[0]]['name'],
                '| dist [km]: ', country_[1])

    elif int(inputs[0]) == 8:     # Req 7
        print('\nEspecificar IPs')
        IPA = input('IP1: ')
        cityA = ipapi.location(ip=IPA)['city']
        print(cityA)
        IPB = input('IP2: ')
        cityB = ipapi.location(ip=IPB)['city']
        print(cityB)

    else:
        sys.exit(0)
sys.exit(0)

#------------- debbug --------------------------
# Input 1
print("Cargando información de los archivos ....")
cont = controller.init()
controller.loadData(cont)
numedges = controller.totalConnections(cont)
numvertex = controller.totalLPs(cont)
numcountries = controller.totalCountries(cont)
firstlp = controller.getFirstLandingPointInfo(cont)
lastcountry = controller.getLastCountryInfo(cont)
print('\nNumero de landing points (vertices): ' + str(numvertex))
print('Numero de conexiones (arcos): ' + str(numedges))
print('Numero de paises : ' + str(numcountries))
print('1st Landing point id: ', firstlp['id'],
        '| nombre :', firstlp['name'],
        '| cords :' , 'Lat. {} Long. {}'.format(firstlp['lat'],firstlp['long']))
print('n-Country Info: ', lastcountry['country'], ' -- ',
        'poblacion :', str(lastcountry['population']),
        '| usuarios :', str(lastcountry['internet_users']))

# Input 2 DONE
# print('Definir landings points a analizar...')
# lp1 = input('Landing point 1: ')
# lp2 = input('Landing point 2: ')
# out = controller.VertexInComponents(cont, lp1, lp2)

# Input 3 DONE
# maxdeg, mostconnected, info_out =  controller.mostConnectedLandingPoint(cont)
# print('\nLanding point(s) mas conectado(s)')
# for i, mostconn_ in enumerate(mostconnected):
#     print(i+1,'--', 'landing point id :', mostconn_,
#             '| nombre :', info_out[mostconn_]['name'],
#             '| conexiones :', maxdeg)
# Input 4
print('\nDefinir paises para calcular la ruta minima...')
countryA = 'Colombia'
countryB = 'Argentina'
out = controller.minDistanceBetweenCapitals(cont, countryA, countryB)
if out[0] is not None:
    min_path = out[0]
    total_dist = out[1]
    info_out = out[0]
    print('\nRuta minima entre',countryA,'y',countryB)
    for path_ in lt.iterator(min_path):
        print(info_out[path_['vertexA']]['name'],'-->',info_out[path_['vertexB']]['name'],'dist [km]:', path_['weight'])
    print('Total distance [km] :', total_dist)
else:
    print('\nNo existe una ruta de conexion entre', countryA, 'y', countryB)

# Input 5 DONE
# lp = 'Fortaleza'
# controller.simulateFailure(cont, lp)
# print('\nNumero de paises afectados :',len(sort_dist))
# for i, country_ in enumerate(sort_dist):
#     print(i+1,'--',info_out[country_[0]]['name'].split(','),
#           '| dist [km]: ', country_[1])

# Input 8
# print('\nEspecificar IPs')
# IPA = '165.132.67.89'
# cityA = ipapi.location(ip=IPA)['city']
# print(cityA)
# IPB = '8.8.8.8'
# cityB = ipapi.location(ip=IPB)['city']
# print(cityB)
# min_path, total_dist, total_jumps, info_out = controller.minDistanceBetweenCities(cont, cityA, cityB)
    

print('done')