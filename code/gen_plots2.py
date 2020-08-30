# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 09:20:36 2019

@author: boa
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pylab
import os

def generate_plots2(input_path, results_path, param_file, result_file, experiment):
    
    print(" ")
    print("generating results plots")
    
    plot_path = results_path + experiment + '/'
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    
    results_data = 'results_data.xlsx'
    writer = pd.ExcelWriter(plot_path + results_data, engine='xlsxwriter')
    
    # READ LABELS FROM INPUT FILE
    energy_carriers = pd.read_excel(input_path,sheet_name='Energy Carriers', header=None, skiprows=3)
    conversion_techs = pd.read_excel(input_path,sheet_name='Energy Converters', header=None, skiprows=2,skipfooter=20)
    storage_techs = pd.read_excel(input_path,sheet_name='Storage', header=None, skiprows=2,skipfooter=15)
    
    energy_carriers2 = energy_carriers[0].tolist()
    conversion_techs2 = conversion_techs.drop([0],axis=1).transpose()
    conversion_techs2 = conversion_techs2[0].tolist()
    storage_techs2 = storage_techs.drop([0],axis=1).transpose()
    storage_techs2 = storage_techs2[0].tolist()
    
    # LOAD THE RESULTS DATA
    lines = []
    with open (result_file, 'rt') as in_file:
        for line in in_file:
            lines.append(line)
    
    cap = []
    capstor = []
    eout = []
    outstg = []
    instg = []
    socstg = []
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
            
        if(row.find("InvCost") >= 0):
            row2 = row.split(sep=" ")
            inv_cost = row2[2]
            
        if(row.find("FuelCost") >= 0):
            row2 = row.split(sep=" ")
            fuel_cost = row2[2]
            
        if(row.find("FOMCost") >= 0):
            row2 = row.split(sep=" ")
            fom_cost = row2[2]
            
        if(row.find("VOMCost") >= 0):
            row2 = row.split(sep=" ")
            vom_cost = row2[2]
    
        if(row.find("CapTech") >= 0):
            row2 = row.split(sep=" ")
            cap.append(row2[2:5])
    
        if(row.find("CapStg") >= 0):
            row2 = row.split(sep=" ")
            capstor.append(row2[2:5])
    
        if(row.find("Eout") >= 0):
            row2 = row.split(sep=" ")
            eout.append(row2[2:6])
    
        if(row.find("OutStg") >= 0):
            row2 = row.split(sep=" ")
            outstg.append(row2[2:6])
            
        if(row.find("InStg") >= 0):
            row2 = row.split(sep=" ")
            instg.append(row2[2:6])
            
        if(row.find("SoC") >= 0):
            row2 = row.split(sep=" ")
            socstg.append(row2[2:6])
    
        if(row.find("Eimp") >= 0):
            row2 = row.split(sep=" ")
            eimp.append(row2[2:5])
    
        if(row.find("Eexp") >= 0):
            row2 = row.split(sep=" ")
            eexp.append(row2[2:5])
            
            
    # ADD LABELS
    # conversion techs
    capacities = pd.DataFrame(cap, columns = ['tech', 'value'])
    capacities = capacities.apply(pd.to_numeric)
    i = 1
    for label in conversion_techs2:
        capacities['tech'] = capacities['tech'].replace(i,label)
        i = i+1
    
    # storage techs
    capacities_stor = pd.DataFrame(capstor, columns = ['tech','ec','value'])
    del capacities_stor['ec']
    capacities_stor = capacities_stor.apply(pd.to_numeric)
    i = 1
    for label in storage_techs2:
        capacities_stor['tech'] = capacities_stor['tech'].replace(i,label)
        i = i+1
    
    # conversion technology outputs
    eoutdf = pd.DataFrame(eout, columns = ['tm', 'tech', 'ec', 'value'])
    eoutdf = eoutdf.apply(pd.to_numeric)
    i = 1
    for label in conversion_techs2:
        eoutdf['tech'] = eoutdf['tech'].replace(i,label)
        i = i+1
    
    # storage technology outputs
    stgoutdf = pd.DataFrame(outstg, columns = ['tm', 'tech', 'ec', 'value'])
    stgoutdf = stgoutdf.apply(pd.to_numeric)
    i = 1
    for label in storage_techs2:
        stgoutdf['tech'] = stgoutdf['tech'].replace(i,label)
        i = i+1
    eoutdf = eoutdf.append(stgoutdf)
    
    # storage technology inputs
    stgindf = pd.DataFrame(instg, columns = ['tm', 'tech', 'ec', 'value'])
    stgindf = stgindf.apply(pd.to_numeric)
    i = 1
    for label in storage_techs2:
        stgindf['tech'] = stgindf['tech'].replace(i,label)
        i = i+1
        
    # storage soc
    stgsocdf = pd.DataFrame(socstg, columns = ['tm', 'tech', 'ec', 'value'])
    stgsocdf = stgsocdf.apply(pd.to_numeric)
    i = 1
    for label in storage_techs2:
        stgsocdf['tech'] = stgsocdf['tech'].replace(i,label)
        i = i+1
    
    # energy imports
    eimpdf = pd.DataFrame(eimp, columns = ['tm', 'ec', 'value'])
    eimpdf = eimpdf.apply(pd.to_numeric)
    i = 1
    for label in energy_carriers2:
        eimpdf['ec'] = eimpdf['ec'].replace(i,label)
        i = i+1
    
    # energy exports
    eexpdf = pd.DataFrame(eexp, columns = ['tm', 'ec', 'value'])
    eexpdf = eexpdf.apply(pd.to_numeric)
    i = 1
    for label in energy_carriers2:
        eexpdf['ec'] = eexpdf['ec'].replace(i,label)
        i = i+1
        
    # key results
    keyresults = [float(total_cost), float(total_income), float(total_carbon)]
    key_results = pd.DataFrame(keyresults)
    key_results = key_results.transpose()
    key_results.columns = ['cost','income','co2']
    
    
    # PRINT KEY RESULTS
    key_results.to_excel(writer, sheet_name='key_results')
    
    # PLOT CONVERSION TECHNOLOGY CAPACITIES
    cap = capacities.copy(deep=True)
    cap = cap[cap['value'] != 0]
    if cap.empty != True:
        cap2 = cap.groupby('tech').sum()
        cap2 = cap2.unstack()
        cap2.to_excel(writer, sheet_name='production_capacities')
        
    # PLOT STORAGE TECHNOLOGY CAPACITIES
    cap = capacities_stor.copy(deep=True)
    cap = cap[cap['value'] != 0]
    if cap.empty != True:
        cap2 = cap.groupby('tech').sum()
        cap2 = cap2.unstack()
        cap2.to_excel(writer, sheet_name='storage_capacities')
        
    # PLOT THE DAILY PRODUCTION
    ep = eoutdf.copy(deep=True)
    day = round(ep['tm'].astype(float)/(24))
    ep['day'] = day
    del ep['tm']
    del ep['ec']
    #ep = ep[ep['value'] != 0]
    if ep.empty != True:
        ep2 = ep.groupby(['day','tech']).sum()
        ep2 = ep2.unstack()
        ep2.columns = ep2.columns.droplevel()
        ep2.plot(kind='bar', stacked=True)
        plt.xticks([])
        plt.xlabel('Day')
        plt.ylabel('Energy generation (kWh)')
        plt.title('Energy generation per technology (aggregated by day)')
        plt.legend(loc=2, bbox_to_anchor=(0.0, 1.0))
        fig = plt.gcf()
        fig.savefig(plot_path + 'daily_output_conversion_technologies.png', format='png', dpi=300)
        plt.close('all')
        ep2.to_excel(writer, sheet_name='daily_production')
        
    # PLOT THE DAILY EXPORTS
    ep = eexpdf.copy(deep=True)
    day = round(ep['tm'].astype(float)/(24))
    ep['day'] = day
    del ep['tm']
    if ep.empty != True:
        ep2 = ep.groupby(['day','ec']).sum()
        ep2 = ep2.unstack()
        ep2.columns = ep2.columns.droplevel()
        ep2.plot(kind='bar', stacked=True)
        plt.xticks([])
        plt.xlabel('Day')
        plt.ylabel('Energy exports (kWh)')
        plt.title('Energy exports (aggregated by day)')
        plt.legend(loc=2, bbox_to_anchor=(0.0, 1.0))
        fig = plt.gcf()
        fig.savefig(plot_path + 'daily_exports.png', format='png', dpi=300)
        plt.close('all')
        ep2.to_excel(writer, sheet_name='daily_exports')
        
    # PLOT THE DAILY IMPORTS
    ep = eimpdf.copy(deep=True)
    day = round(ep['tm'].astype(float)/(24))
    ep['day'] = day
    del ep['tm']
    if ep.empty != True:
        ep2 = ep.groupby(['day','ec']).sum()
        ep2 = ep2.unstack()
        ep2.columns = ep2.columns.droplevel()
        ep2.plot(kind='bar', stacked=True)
        plt.xticks([])
        plt.xlabel('Day')
        plt.ylabel('Energy imports (kWh)')
        plt.title('Energy imports (aggregated by day)')
        plt.legend(loc=2, bbox_to_anchor=(0.0, 1.0))
        fig = plt.gcf()
        fig.savefig(plot_path + 'daily_imports.png', format='png', dpi=300)
        plt.close('all')
        ep2.to_excel(writer, sheet_name='daily_imports')
        
    #PLOT THE STORAGE SOC
    soc = stgsocdf.copy(deep=True)
    day = round(soc['tm'].astype(float)/(24))
    soc['day'] = day
    del soc['tm']
    del soc['ec']
    #soc = soc[soc['value'] != 0]
    if soc.empty != True:
        soc2 = soc.groupby(['day','tech']).sum()
        soc2 = soc2.unstack()
        soc2.columns = soc2.columns.droplevel()
        soc2.plot(kind='bar', stacked=True)
        plt.xticks([])
        plt.xlabel('Day')
        plt.ylabel('Storage SoC (kWh)')
        plt.title('Storage state of charge (aggregated by day)')
        plt.legend(loc=2, bbox_to_anchor=(0.0, 1.0))
        fig = plt.gcf()
        fig.savefig(plot_path + 'storage_soc.png', format='png', dpi=300)
        plt.close('all')
        soc.to_excel(writer, sheet_name='storage_soc')
        
    writer.save()
    
    print(" ")
    print("FINISHED!")