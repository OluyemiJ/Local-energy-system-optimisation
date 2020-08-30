# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 16:56:29 2018

@author: boa
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
import os

def generate_plots(input_path, param_file, result_file, experiment, visualizations_directory):
    
    # LOAD RESULTS DATA

    lines = []
    with open (result_file, 'rt') as in_file:
        for line in in_file:
            lines.append(line) 
            
    capacities = {}
    capstor = []
    eout = []
    outstg = []
    eimp = []
    eexp = []
    for row in lines:
        if(row.find("TotalCost") >= 0):
            row2 = row.split(sep=" ")
            total_cost = row2[2]
            
        if(row.find("IncomeExp") >= 0):
            row2 = row.split(sep=" ")
            total_income = row2[2]
            
        if(row.find("TotalCarbon") >= 0):
            row2 = row.split(sep=" ")
            total_carbon = row2[2]
        
        if(row.find("CapTech") >= 0):
            row2 = row.split(sep=" ")
            capacities.update({row2[2]: float(row2[3])})
            
        if(row.find("CapStg") >= 0):
            row2 = row.split(sep=" ")
            capstor.append(row2[2:5])
            
        if(row.find("Eout") >= 0):
            row2 = row.split(sep=" ")
            eout.append(row2[2:6])
            
        if(row.find("OutStg") >= 0):
            row2 = row.split(sep=" ")
            outstg.append(row2[2:6])
            
        if(row.find("Eimp") >= 0):
            row2 = row.split(sep=" ")
            eimp.append(row2[2:5])
            
        if(row.find("Eexp") >= 0):
            row2 = row.split(sep=" ")
            eexp.append(row2[2:5])
    
    capacities['heat_pump'] = capacities['1']
    capacities['gas_boiler'] = capacities['2']
    capacities['solar_PV'] = capacities['3']
    if '4' in capacities:
        capacities['CHP_unit'] = capacities['4']
    del capacities['1']
    del capacities['2']
    del capacities['3']
    if '4' in capacities:
        del capacities['4']
    
    capacities_stor = pd.DataFrame(capstor, columns = ['tech','ec','value'])
    del capacities_stor['ec']
    capacities_stor = capacities_stor.apply(pd.to_numeric)
    capacities_stor['tech'] = capacities_stor['tech'].replace(1, 'hot_water_tank')
    capacities_stor['tech'] = capacities_stor['tech'].replace(2, 'battery')
    capacities_stor = capacities_stor.groupby(['tech']).sum()
    #capacities_stor['battery'] = capacities_stor['1']
    #capacities_stor['hot_water_tank'] = capacities_stor['2']
    #del capacities_stor['1']
    #del capacities_stor['2']
    
    eoutdf = pd.DataFrame(eout, columns = ['tm', 'tech', 'ec', 'value'])
    eoutdf = eoutdf.apply(pd.to_numeric)
    eoutdf['tech'] = eoutdf['tech'].replace(1, 'heat_pump')
    eoutdf['tech'] = eoutdf['tech'].replace(2, 'gas_boiler')
    eoutdf['tech'] = eoutdf['tech'].replace(3, 'solar_PV')
    eoutdf['tech'] = eoutdf['tech'].replace(4, 'CHP_unit')
    
    stgoutdf = pd.DataFrame(outstg, columns = ['tm', 'tech', 'ec', 'value'])
    stgoutdf = stgoutdf.apply(pd.to_numeric)
    stgoutdf['tech'] = stgoutdf['tech'].replace(1, 'hot_water_tank')
    stgoutdf['tech'] = stgoutdf['tech'].replace(2, 'battery')
    eoutdf = eoutdf.append(stgoutdf)
    
    eimpdf = pd.DataFrame(eimp, columns = ['tm', 'ec', 'value'])
    eimpdf = eimpdf.apply(pd.to_numeric)
    eimpdf['tech']='grid'
    eoutdf = eoutdf.append(eimpdf)
    
    eexpdf = pd.DataFrame(eexp, columns = ['tm', 'ec', 'value'])
    eexpdf = eexpdf.apply(pd.to_numeric)
    
    electricity_production = eoutdf.loc[eoutdf['ec'] == 1]
    heat_production = eoutdf.loc[eoutdf['ec'] == 2]
    electricity_exports = eexpdf.loc[eexpdf['ec'] == 1]
    
    directory = visualizations_directory + experiment
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    
    # TOTAL COSTS, INCOME & CARBON EMISSIONS
    print(" ")
    print("Key results:")
    print("Total cost (CHF) = " + str(round(float(total_cost))))
    print("Total income from exports (CHF) = " + str(round(float(total_income))))
    print("Total carbon emissions (kg CO2-eq) = " + str(round(float(total_carbon))))
    
    print(" ")
    print("Generating plots...")
    print("Saving plots to: " + directory)
    
    # CONVERSION TECHNOLOGY CAPACITIES
    plt.close('all')
    plt.bar(range(len(capacities)), list(capacities.values()), align='center')
    plt.xticks(range(len(capacities)), list(capacities.keys()))
    plt.xlabel('Technology')
    plt.ylabel('Capacity (kW)')
    plt.title('Generation technology capacities')
    fig = plt.gcf()
    fig.savefig(directory + '/capacities_conversion_technologies.pdf', format='pdf')


    # STORAGE TECHNOLOGY CAPACITIES
    plt.close()
    plt.close(fig)
    cs = capacities_stor.copy(deep=True)
    cs.plot(kind='bar')
    plt.xlabel('Technology')
    plt.ylabel('Capacity (kWh)')
    plt.title('Storage technology capacities')
    fig = plt.gcf()
    fig.savefig(directory + '/capacities_storage_technologies.pdf', format='pdf')
    
    
    # ELECTRICITY PRODUCTION - AGGREGATED WEEKLY RESULTS
    plt.close(fig)
    plt.close()
    ep = electricity_production.copy(deep=True)
    week = round(ep['tm']/(24))
    ep['week'] = week
    del ep['tm']
    del ep['ec']
    ep2 = ep.groupby(['week','tech']).sum()
    ep2 = ep2.unstack()
    ep2.columns = ep2.columns.droplevel()
    ep2.plot(kind='bar', stacked=True)
    plt.xticks([])
    plt.xlabel('Day')
    plt.ylabel('Electricity generation (kWh)')
    plt.title('Electricity generation per technology (aggregated by day)')
    fig = plt.gcf()
    fig.set_size_inches(12, 4, forward=True)
    plt.legend(loc=9, bbox_to_anchor=(1.0, 1.0))
    fig.savefig(directory + '/electricity_production_per_day.pdf', format='pdf')


    # HEAT PRODUCTION - AGGREGATED WEEKLY RESULTS
    plt.close(fig)
    plt.close()
    ep = heat_production.copy(deep=True)
    week = round(ep['tm']/(24))
    ep['week'] = week
    del ep['tm']
    del ep['ec']
    ep2 = ep.groupby(['week','tech']).sum()
    ep2 = ep2.unstack()
    ep2.columns = ep2.columns.droplevel()
    ep2.plot(kind='bar', stacked=True)
    plt.xticks([])
    plt.xlabel('Day')
    plt.ylabel('Heat generation (kWh)')
    plt.title('Heat generation per technology (aggregated by day)')
    fig = plt.gcf()
    fig.set_size_inches(12, 4, forward=True)
    plt.legend(loc=9, bbox_to_anchor=(1.0, 1.0))
    fig.savefig(directory + '/heat_production_per_day.pdf', format='pdf')
    
    # ELECTRICITY PRODUCTION - WINTER WEEK
#    plt.close(fig)
#    plt.close()
#    ep = electricity_production.copy(deep=True)
#    week = round(ep['tm']/(7*24))
#    ep['week'] = week
#    ep = ep.loc[ep['week'] == 1]
#    del ep['week']
#    del ep['ec']
#    ep2 = ep.groupby(['tech']).sum()
#    #ep2 = ep2.unstack()
#    print(ep2)
#    #ep2.columns = ep2.columns.droplevel()
#    ep2.plot(kind='bar', stacked=True)
#    plt.xlabel('Hour')
#    plt.ylabel('Electricity generation (kWh)')
#    plt.title('Electricity generation per technology for a week in winter')
#    fig = plt.gcf()
#    fig.set_size_inches(12, 4, forward=True)
#    plt.legend(loc=9, bbox_to_anchor=(1.0, 1.0))
#    fig.savefig(directory + '/electricity_production_winter_week.pdf', format='pdf')

    # ELECTRICITY EXPORTS - AGGREGATED DAILY RESULTS
    plt.close(fig)
    plt.close()
    exp = electricity_exports.copy(deep=True)
    day = round(exp['tm']/(24))
    exp['day'] = day
    del exp['tm']
    del exp['ec']
    exp2 = exp.groupby(['day']).sum()
    exp2.plot(kind='bar', stacked=True)
    plt.xlabel('Day')
    plt.ylabel('Electricity exports (kWh)')
    plt.title('Electricity exports to grid (aggregated daily)')
    plt.xticks([])
    fig = plt.gcf()
    fig.set_size_inches(12, 4, forward=True)
    plt.legend(loc=9, bbox_to_anchor=(1.0, 1.0))
    fig.savefig(directory + '/electricity_exports_per_day.pdf', format='pdf')
    plt.clf()
    plt.close('all')
    
    print("FINISHED!")
