# -----------------------------------------------------------------------------#
# Process Input Data
# ---------------------------------------------------------------------------

# from https://github.com/hues-platform/python-ehub/blob/NextGen/code/v2.0/input_data.py

from pyomo.core import *
from pyomo.opt import SolverFactory, SolverManagerFactory
import pyomo.environ
import pandas as pd
import numpy as np

from IPython.core.display import HTML


class prepate_data:

    # class initialization
    def __init__(self, ExcelPath, demands='Demand', solar='Solar Profile', tech='Energy Converters', stg='Storage',
                 gen='General', ec='Energy Carriers', net='Network', imp='Imports', exp='Exports', impHr='Imp Hr',
                 expHr='Exp Hr', cfHr="CF Hr"):  # if no values are passed, use defaults
        self.path = ExcelPath
        self.DemandSheet = demands
        self.SolarSheet = solar
        self.TechSheet = tech
        self.GeneralSheet = gen
        self.ECSheet = ec
        self.NetSheet = net
        self.ImpSheet = imp
        self.ExpSheet = exp
        self.StgSheet = stg
        self.ImpHrSheet = impHr
        self.ExpHrSheet = expHr
        self.CFHrSheet = cfHr

        self.Initialize()  # call variable intialization function

    # =============================================================================
    #      Functions to read and store input data
    # =============================================================================

    def Initialize(self):
        """
        Read-in and process Excel input data
        """
        self.Rd_EnergyCarriers()  # list first (builds EC_dict which used in other functions)
        self.Rd_General()
        self.Rd_Imports()
        self.Rd_Exports()
        self.Rd_Demand()
        self.Rd_Technologies()
        self.Rd_Storage()
        self.Rd_Network()
        self.Rd_Solar()
        self.Rd_EimpHr()
        self.Rd_EexpHr()
        self.Rd_CFHr()

    def LookupEC(self, ec, errmsg):
        """
        Looks up and returns energy carrier IDs for list 'ec'. Generates error message 'errmsg' if lookup fails
        """
        lu = []
        for i, EC_name in enumerate(ec):
            try:
                lu += [self.EC_dict[EC_name]]
            except KeyError:  # if a lookup error occurs
                print(errmsg)
                raise  # reraise last exception

        return lu

    def LookupTech(self, tech, errmsg):
        """
        Looks up and returns energy carrier IDs for list 'tech'. Generates error message 'errmsg' if lookup fails
        """
        lu = []
        for i, tech_name in enumerate(tech):
            try:
                lu += [self.tech_dict[tech_name]]
            except KeyError:  # if a lookup error occurs
                print(errmsg)
                raise  # reraise last exception

        return lu

    def ParseEC(self, ec):
        """
        Parses string of energy carriers in list 'ec'. Looks up and returns dictionary of corresponding energy carrier IDs
        """
        # lookup input energy carriers
        ecID = {}  # dictionary to store input EC IDs for each technology
        for i in range(0, len(ec)):
            eci = [x.strip() for x in str(ec[i]).split(',')]  # parse comma-delimited string and save as list
            lu = self.LookupEC(eci,
                               "Technology input/output energy carrier lookup failed; check Technology spreadsheet")  # lookup EC IDs
            ecID[i + 1] = lu  # store input ID for technology

        return ecID

    def ParseShare(self, shr):
        """
        Parses string of fixed input shares in list 'shr'. Returns a dictionary of checked and float-formatted values
        """
        parseShr = {}

        for i in range(0, len(shr)):
            shrS = [x.strip() for x in str(shr[i]).split(',')]  # parse comma-delimited string and save as list
            shrF = [float(j) for j in shrS]  # convert list of strings to float
            if sum(shrF) != 1 and np.isnan(sum(shrF)) == 0:  # generate error if user input shares that do not sum to 1
                raise ValueError("Fixed input or output share does not sum to 1")
            parseShr[i + 1] = shrF  # store share for technology

        return parseShr

    def Rd_EnergyCarriers(self):
        """
        Retrieve the list of energy carriers used in the model, assign the energy carriers values from 1 to N in a dictionary, and save the energy carrier values in a list
        """
        # Read data
        ECs = pd.read_excel(self.path, sheet_name=self.ECSheet, header=None, skiprows=3)
        ECs = ECs.dropna(axis=1, how='all')

        self.nEC = ECs.shape[0]

        # Create dictionary
        dic = {}
        for i in range(self.nEC):
            dic[ECs.loc[i][0]] = i + 1
        self.EC_dict = dic

    def Rd_General(self):
        """
        Retrieve number of hubs, interest rate, objective minimization target, and max CO2 emissions from input spreadsheet
        """
        gendata = pd.read_excel(self.path, sheet_name=self.GeneralSheet, skiprows=1, index_col=0)
        gendata = gendata.dropna(axis=1, how='all')
        self.nHub = int(gendata.loc["Number of hubs"][0])
        self.interest = gendata.loc["Interest rate (%)"][0] / 100
        self.minobj = gendata.loc["Minimization objective"][0]
        self.maxcarbon = gendata.loc["Maximum CO2 emissions (kg-CO2)"][0]
        self.bigm = gendata.loc["Big M"][0]

    def Rd_Imports(self):
        """
        Retrieve import EC data from Excel spreadsheet
        """
        Imp = pd.read_excel(self.path, sheet_name=self.ImpSheet, skiprows=2, index_col=0)

        Imp.loc[:, "Maximum supply (kWh)"] = Imp.loc[:, "Maximum supply (kWh)"].fillna(
            float('inf'))  # replace nan values for max cap with infinity
        Imp = Imp.fillna(0)  # fill the remaining blanks (nan) with zero values

        # lookup EC IDs
        ecID = self.LookupEC(Imp.index.tolist(),
                             "Import energy carrier lookup error")  # energy carriers which can be imported by model
        Imp.index = ecID
        self.ImportData = Imp

        # store other parameters
        self.impEC = ecID
        self.impCostFx = Imp["Price (CHF/kWh)"]
        self.impCO2 = Imp["CO2 (kg-CO2/kWh)"]
        self.impCO2Tax = Imp["CO2 tax (CHF/kg-CO2)"]
        self.impMax = Imp["Maximum supply (kWh)"]

    def Rd_Exports(self):
        """
        Retrieve export EC data from Excel spreadsheet
        """
        Exp = pd.read_excel(self.path, sheet_name=self.ExpSheet, skiprows=2, index_col=0)
        Exp = Exp.fillna(0)  # fill the remaining blanks (nan) with zero values

        # lookup EC IDs
        ecID = self.LookupEC(Exp.index.tolist(),
                             "Export energy carrier lookup error")  # energy carriers which can be exported by model
        Exp.index = ecID
        self.ExportData = Exp

        # store other parameters
        self.expEC = ecID
        self.expPriceFx = Exp["Export Price (CHF/kWh)"]

    #    def Rd_Demand(self):
    #        """
    #        Retrieve demand data from Excel spreadsheet
    #        """
    #        DemandDatas=pd.read_excel(self.path,sheet_name=self.DemandSheet, header=None, skiprows=1)
    #        self.DemandData = DemandDatas.loc[4:DemandDatas.shape[0],1:DemandDatas.shape[1]] # demand data; extract data from index row label 3:last row, and column label 1:last column
    #        self.DemandData = self.DemandData.fillna(0) # fill blanks (nan) with zero values
    #        self.DemandHub = DemandDatas.loc[2,1:DemandDatas.shape[1]].values.tolist() # hub data; convert to list to be consistent with DemEC formatting
    #        self.nTime= self.DemandData.shape[0] # number of time periods
    #        dec = DemandDatas.loc[1,1:DemandDatas.shape[1]] # row of demand energy carriers
    #
    #        # lookup energy carrier names
    #        DemEC = self.LookupEC(dec,"Energy carrier lookup failed in Demand Data input spreadsheet")
    #        self.DemandEC = DemEC # demand EC data

    # retrieve demand data from the XLSX
    def Rd_Demand(self):

        """
        Retrieve demand data from Excel spreadsheet
        """
        DemandDatas = pd.read_excel(self.path, sheet_name=self.DemandSheet, header=None, skiprows=1)
        self.DemandData = DemandDatas.loc[4:DemandDatas.shape[0], 1:DemandDatas.shape[
            1]]  # demand data; extract data from index row label 3:last row, and column label 1:last column
        self.DemandData = self.DemandData.fillna(0)  # fill blanks (nan) with zero values
        self.DemandHub = DemandDatas.loc[2, 1:DemandDatas.shape[
            1]].values.tolist()  # hub data; convert to list to be consistent with DemEC formatting
        self.nTime = self.DemandData.shape[0]  # number of time periods
        dec = DemandDatas.loc[1, 1:DemandDatas.shape[1]]  # row of demand energy carriers

        # lookup energy carrier names
        DemEC = self.LookupEC(dec, "Energy carrier lookup failed in Demand Data input spreadsheet")
        self.DemandEC = DemEC  # demand EC data

        DemandData2 = pd.read_excel(self.path, sheet_name=self.DemandSheet, header=[0, 1], skiprows=2, index_col=0)
        DemandData2 = DemandData2.rename(self.EC_dict, axis='columns')
        DemandData2 = DemandData2.stack().stack()
        DemandData2 = DemandData2.swaplevel(i=-2, j=-3)
        self.loads = DemandData2.to_dict()

    def TechInOut(self):
        """
        Identify/check technology input/output energy carriers and shares
        """
        # lookup and store input/output energy carriers
        self.inEC = self.ParseEC(self.TechData.loc["Input energy carrier"])
        self.outEC = self.ParseEC(self.TechData.loc["Output energy carrier"])

        # check and store given fixed input/output shares
        self.inShr = self.ParseShare(self.TechData.loc["Fixed input share"])
        self.outShr = self.ParseShare(self.TechData.loc["Fixed output share"])

        # check to ensure number of input/output share values matches the number of input/output energy carriers
        for i, vali in enumerate(self.inShr):  # for each technology
            if len(self.inShr[
                       vali]) > 1:  # if fixed input shares are given (i.e., multiple input shares values are given for a technology)
                if len(self.inEC[vali]) != len(self.inShr[
                                                   vali]):  # check to ensure number of input ECs matches number of fixed input shares provided
                    raise ValueError(
                        "Mismatch between number of input energy carriers and fixed input shares; check input spreadsheet")  # if not, raise error
            if len(self.outShr[
                       vali]) > 1:  # if fixed output shares are given (i.e., multiple output shares values are given for a technology)
                if len(self.outEC[vali]) != len(self.outShr[
                                                    vali]):  # check to ensure number of output ECs matches number of fixed output shares provided
                    raise ValueError(
                        "Mismatch between number of output energy carriers and fixed output shares; check input spreadsheet")  # if not, raise error

    def TechFixFree(self):
        """
        Identify technology IDs with fixed/free input/output shares
        """
        # store list of technology IDs with a fixed output share
        techfixout = []
        techfreeout = []
        for i, techi in enumerate(self.outEC):  # for each technology
            if len(self.outShr[techi]) > 1:  # if there is more than one output share specified
                techfixout.append(techi)
            else:  # the output share is only one (i.e., either = 1 or is nan (i.e., field left blank))
                techfreeout.append(techi)
        self.techFixOut = techfixout
        self.techFreeOut = techfreeout

        # store list of technology IDs with a fixed input share
        techfixin = []
        for i, techi in enumerate(self.inEC):  # for each technology
            if len(self.inShr[techi]) > 1:  # if there is more than one input share specified
                techfixin.append(techi)
        self.techFixIn = techfixin

    def Rd_Technologies(self):
        """
        Retrieve energy converter data from Excel spreadsheet
        """
        Technologies = pd.read_excel(self.path, sheet_name=self.TechSheet, skiprows=2,
                                     index_col=0)  # technology characteristics
        Technologies = Technologies.dropna(axis=1, how='all')  # technology characteristics
        self.TechData = Technologies

        # store parameters
        self.nTech = self.TechData.shape[1]
        self.instCapTech = self.TechData.loc[
            "Capacity (kW)"]  # pre-installed capcities; data is the same for all hubs; keep NaN flag
        self.invTech = self.TechData.loc["Investment cost (CHF/kW)"]
        self.invTech = self.invTech.fillna(0)
        self.omfTech = self.TechData.loc["Fixed O&M cost (CHF/kW)"]
        self.omfTech = self.omfTech.fillna(0)
        self.omvTech = self.TechData.loc["Variable O&M cost (CHF/kWh)"]
        self.omvTech = self.omvTech.fillna(0)
        self.effTech = self.TechData.loc["Efficiency (%)"] / 100
        self.effTech = self.effTech.fillna(0)
        self.TechInOut()  # process input/output energy carriers and fixed shares
        self.TechFixFree()  # define fixed and free output tech sets
        self.lifeTech = self.TechData.loc["Lifetime (years)"]  # keep NaN
        self.solkWm2 = self.TechData.loc["Solar specific power (kW/m2)"]  # keep NaN
        self.maxCapTech = self.TechData.loc["Maximum capacity (kW)"]
        self.maxCapTech = self.maxCapTech.fillna(float('inf'))  # replace nan values with infinity
        self.minCapTech = self.TechData.loc["Minimum capacity (kW)"]
        self.minCapTech = self.minCapTech.fillna(0)
        self.maxOutTech = self.TechData.loc["Maximum output (kWh)"]
        self.maxOutTech = self.maxOutTech.fillna(float('inf'))  # replace nan values with infinity
        self.minOutTech = self.TechData.loc["Minimum output (kWh)"]
        self.minOutTech = self.minOutTech.fillna(0)
        self.co2Tech = self.TechData.loc["CO2 investment (kg-CO2/kW)"]
        self.co2Tech = self.co2Tech.fillna(0)
        self.maxCFA = self.TechData.loc["Maximum capacity factor (%)"] / 100
        self.maxCFA = self.maxCFA.fillna(1)
        self.minCFA = self.TechData.loc["Minimum capacity factor (%)"] / 100
        self.minCFA = self.minCFA.fillna(0)
        self.hubTech = self.TechData.loc["Hubs"]  # keep NaN

        # store part load efficiencies and identify technologies
        self.pldict = dict(zip(range(1, self.nTech + 1), np.array(
            self.TechData.loc["Minimum load (%)"]) / 100))  # create dictionary with 1:N and part load efficiency values
        self.techPL = [k for (k, v) in self.pldict.items() if
                       v > 0]  # select partload tech IDs where partload efficiency is greater than 0

        # Create tech lookup dictionary
        d = {}
        for i in range(self.nTech):
            d[Technologies.columns[i]] = i + 1
        self.tech_dict = d

    def Rd_Storage(self):
        """
        Retrieve storage data from Excel spreadsheet
        """
        Storage = pd.read_excel(self.path, sheet_name=self.StgSheet, skiprows=2, index_col=0)
        Storage = Storage.dropna(axis=1, how='all')
        self.StorageData = Storage

        # convert stored energy carrier input data to assigned energy carrier ID in dictionary, save in list
        StgE = self.LookupEC(self.StorageData.loc["Stored energy carrier"],
                             "Energy carrier lookup failed for storage data")
        self.stgE = StgE

        # store other parameters
        self.nStg = self.StorageData.shape[1]  # number of storage devices
        self.instCapStg = self.StorageData.loc[
            "Capacity (kWh)"]  # pre-installed capcities; data is the same for all hubs; need to keep NaN flag
        self.invCostStg = self.StorageData.loc["Investment cost (CHF/kWh)"]
        self.invCostStg = self.invCostStg.fillna(0)
        self.omfCostStg = self.StorageData.loc["Fixed O&M cost (CHF/kWh)"]
        self.omfCostStg = self.omfCostStg.fillna(0)
        self.lifeStg = self.StorageData.loc["Lifetime (years)"]  # leave nan (generates error)
        self.chEff = self.StorageData.loc["Charging efficiency (%)"] / 100
        self.chEff = self.chEff.fillna(0)
        self.dchEff = self.StorageData.loc["Discharging efficiency (%)"] / 100
        self.dchEff = self.dchEff.fillna(0)
        self.chMax = self.StorageData.loc["Maximum charging rate (%)"] / 100
        self.chMax = self.chMax.fillna(0)
        self.dchMax = self.StorageData.loc["Maximum discharging rate (%)"] / 100
        self.dchMax = self.dchMax.fillna(0)
        self.stndby = self.StorageData.loc["Standby loss (%/hour)"] / 100
        self.stndby = self.stndby.fillna(0)
        self.minSoC = self.StorageData.loc["Minimum SoC (%)"] / 100
        self.minSoC = self.minSoC.fillna(0)
        #        self.maxCapStg = self.StorageData.loc["Maximum capacity (kWh)"]
        #        self.maxCapStg = self.maxCapStg.fillna(float('inf')) # replace nan values for max cap with infinity
        #        self.minCapStg = self.StorageData.loc["Minimum capacity (kWh)"]
        #        self.minCapStg = self.minCapStg.fillna(0)
        maxCapStg = self.StorageData.loc["Maximum capacity (kWh)"]
        maxCapStg = maxCapStg.fillna(float('inf'))  # replace nan values for max cap with infinity
        self.maxCapStg = self.GenDict(self.nStg, maxCapStg)
        minCapStg = self.StorageData.loc["Minimum capacity (kWh)"]
        minCapStg = minCapStg.fillna(0)
        self.minCapStg = self.GenDict(self.nStg, minCapStg)
        self.co2Stg = self.StorageData.loc["CO2 investment (kg-CO2/kWh)"]
        self.co2Stg = self.co2Stg.fillna(0)
        self.hubStg = self.StorageData.loc["Hubs"]  # leave nan

    def Rd_Network(self):
        """
        Retrieve network data from Excel spreadsheet
        """
        net = pd.read_excel(self.path, sheet_name=self.NetSheet, header=None, skiprows=2, index_col=0)
        net = net.dropna(axis=1, how='all')
        self.NetworkData = net

        # convert stored energy carrier input data to assigned energy carrier ID in dictionary, save in list
        NetE = self.LookupEC(self.NetworkData.loc["Energy carrier"],
                             "Energy carrier lookup failed for network link under Network input spreadsheet")
        self.netE = NetE

        # store other parameters
        self.node1 = self.NetworkData.loc["Node 1"]
        self.node2 = self.NetworkData.loc["Node 2"]
        self.netLength = self.NetworkData.loc["Length (m)"]
        self.netLength = self.netLength.fillna(0)
        self.netLoss = self.NetworkData.loc["Network loss (%/m)"] / 100
        self.netLoss = self.netLoss.fillna(0)
        self.instCapNet = self.NetworkData.loc["Installed capacity (kW)"]  # leave nan values
        self.maxCapNet = self.NetworkData.loc["Maximum capacity (kW)"]
        self.maxCapNet = self.maxCapNet.fillna(float('inf'))  # if maximum is not given, assign it to infinity
        self.minCapNet = self.NetworkData.loc["Minimum capacity (kW)"]
        self.minCapNet = self.minCapNet.fillna(0)
        self.invCostNet = self.NetworkData.loc["Investment cost (CHF/kW/m)"]
        self.invCostNet = self.invCostNet.fillna(0)
        self.omvCostNet = self.NetworkData.loc["Variable O&M cost (CHF/kWh)"]
        self.omvCostNet = self.omvCostNet.fillna(0)
        self.omfCostNet = self.NetworkData.loc["Fixed O&M cost (CHF/kW)"]
        self.omfCostNet = self.omfCostNet.fillna(0)
        self.co2Net = self.NetworkData.loc["CO2 investment (kg-CO2/kW/m)"]
        self.co2Net = self.co2Net.fillna(0)
        self.lifeNet = self.NetworkData.loc["Lifetime (years)"]
        self.uniFlow = self.NetworkData.loc["Uni-directional flow? (Y)"]
        if self.uniFlow.empty is False:
            self.uniFlow = self.uniFlow.str.lower()  # convert to lower

    def Rd_Solar(self):
        """
        Retrieve solar data from Excel spreadsheet
        """
        # solar irradiance
        SolarData = pd.read_excel(self.path, sheet_name=self.SolarSheet, skiprows=4)
        SolarData = SolarData.loc[0:SolarData.shape[0], 'Irradiation (kW/m2)']
        SolarData = SolarData.dropna(axis=0, how='all')
        self.solIrr = SolarData

        # lookup and store solar EC
        solEC = pd.read_excel(self.path, sheet_name=self.SolarSheet, skiprows=1, index_col=0)
        solEC = solEC.iloc[0][0]
        self.solECID = []
        self.techSol = []
        if type(solEC) is not float:  # if solEC is given (i.e., is a string and is not NaN (i.e., float))
            self.solECID = self.LookupEC([solEC],
                                         "Solar energy carrier label not recognized. Check solar input spreadsheet.")
            # identify solar technologies
            techsol = []
            for (k, v) in self.inEC.items():
                if self.solECID[0] in v:
                    techsol.append(k)
            self.techSol = techsol

    def Rd_EimpHr(self):
        impHrData = pd.read_excel(self.path, sheet_name=self.ImpHrSheet, header=None, skiprows=3)
        impHrData = impHrData.dropna(axis=1, how='all')
        self.impHr = impHrData.loc[1:impHrData.shape[0], 1:impHrData.shape[
            1]]  # extract data from index row label 0:last row, and column label 1:last column
        self.impHr = self.impHr.fillna(0)  # fill blanks (nan) with zero values

        impHrECid = []
        if self.impHr.empty is False:  # if data is given
            impHrEC = impHrData.loc[0, 1:impHrData.shape[1]].values.tolist()  # extract ec data, save as list
            impHrECid = self.LookupEC(impHrEC,
                                      "Hourly priced import energy carrier label not recognized. Check hourly import price input spreadsheet.")
            self.impHr.columns = impHrECid  # column labels
            self.impHr.index = list(range(1, self.nTime + 1))

        # store parameters
        self.impHrEC = impHrECid

    def Rd_EexpHr(self):
        expHrData = pd.read_excel(self.path, sheet_name=self.ExpHrSheet, header=None, skiprows=3)
        expHrData = expHrData.dropna(axis=1, how='all')
        self.expHr = expHrData.loc[1:expHrData.shape[0], 1:expHrData.shape[
            1]]  # extract data from index row label 0:last row, and column label 1:last column
        self.expHr = self.expHr.fillna(0)  # fill blanks (nan) with zero values

        expHrECid = []
        if self.expHr.empty is False:  # if data is given
            expHrEC = expHrData.loc[0, 1:expHrData.shape[1]].values.tolist()  # extract ec data, save as list
            expHrECid = self.LookupEC(expHrEC,
                                      "Hourly priced import energy carrier label not recognized. Check hourly import price input spreadsheet.")
            self.expHr.columns = expHrECid  # column labels
            self.expHr.index = list(range(1, self.nTime + 1))

        # store parameters
        self.expHrEC = expHrECid

    def Rd_CFHr(self):
        cfHrData = pd.read_excel(self.path, sheet_name=self.CFHrSheet, header=None, skiprows=2)
        cfHrTech = cfHrData.iloc[0, 1:cfHrData.shape[1]]
        cfHrTechId = self.LookupTech(cfHrTech,
                                     "Hourly capacity factor technology label not recognized. Check hourly capacity factor input spreadsheet.")
        self.cfHrEq = cfHrData.iloc[1, 1:cfHrData.shape[1]]
        cfHrVal = cfHrData.iloc[3:cfHrData.shape[0], 1:cfHrData.shape[1]] / 100
        cfHrVal.index = cfHrData.iloc[3:cfHrData.shape[0], 0]
        cfHrVal.columns = cfHrTechId
        self.cfHr = cfHrVal

    # =============================================================================
    #     Functions used to generate dictionary formats required by Pyomo
    # =============================================================================

    def GenDict(self, N, value):
        """
        Return dictionary with keys (labels) from 1:N and corresponding values
        """
        d = {}
        if value.empty is False:
            label = range(1, N + 1)  # labels from 1 to N
            d = dict(zip(label, value))
        return (d)  # create dictionary with labels and values

    def GenDict2D(self, mat):

        d = {}
        ncol = mat.shape[1]
        nrow = mat.shape[0]
        if mat.empty is False:  # if data exists
            for i in range(0, ncol):
                colID = mat.columns[i]
                for j in range(0, nrow):
                    rowID = mat.index[j]
                    d[colID, rowID] = mat.loc[rowID, colID]
        return (d)

    def GenDict3D(self, dictVar, panel):
        """
        Return dictionary for 3 dimensional panel
        """
        for x, valx in enumerate(panel.items):
            for i, vali in enumerate(panel[valx].dropna(axis=0, how='all').index):
                for j, valj in enumerate(panel[valx].dropna(axis=1, how='all').columns):
                    dictVar[x + 1, j + 1, i + 1] = panel[valx].loc[vali][valj]  # Pyomo starts from 1 and Python from 0
        return dictVar

    # ----------------------------------------------------------------------
    # Load profiles
    # ----------------------------------------------------------------------

    def DemandInit(self):
        """
        Return Pyomo-formatted dictionary of demand data
        """
        # create a dictionary of zeros which will be updated with demand values
        dummy = {}
        for i in range(self.nHub):
            dummy[i] = np.zeros((self.nEC, self.nTime))

        # update demand data dictionary one column at a time
        for i in range(0, self.DemandData.shape[1]):
            hub = self.DemandHub[i]
            ec = self.DemandEC[i]
            dummy[hub - 1][ec - 1, :] = self.DemandData.iloc[:, i]

        Demand = pd.Panel(dummy)
        loads_init = {}
        loads_init = self.GenDict3D(loads_init, Demand)
        return loads_init

    # ----------------------------------------------------------------------
    # Technologies
    # ----------------------------------------------------------------------

    def EffInit(self):
        """
        Return Pyomo-formatted dictionary of efficiencies for technologies without a fixed output share
        """
        d = {}
        d_eff = self.GenDict(self.nTech, self.effTech)  # lookup dictionary for efficiencies
        for i in self.techFreeOut:
            d[i] = d_eff[i]
        return d

    def EffFixOutInit(self):
        """
        Return Pyomo-formatted dictionary of efficiencies for technologies with a fixed output share
        """
        d = {}
        d_eff = self.GenDict(self.nTech, self.effTech)  # lookup dictionary for efficiencies
        for i in self.techFixOut:  # for each technology
            for j in range(1, self.nEC + 1):  # for each energy carrier
                if j in self.outEC[i]:
                    d[i, j] = d_eff[i] * self.outShr[i][self.outEC[i].index(j)] / self.outShr[i][0]
                else:
                    d[i, j] = 0
        return d

    def InFixInit(self):
        """
        Return Pyomo-formatted dictionary of values for technologies with fixed input shares
        """
        d = {}
        for i in self.techFixIn:  # for each technology
            for j in range(1, self.nEC + 1):  # for each energy carrier
                if j in self.inEC[i]:
                    d[i, j] = self.inShr[i][self.inEC[i].index(j)]
                else:
                    d[i, j] = 0

        return d

    def TechLimitInit(self, limit):
        """
        Return Pyomo-formatted dictionary of limit (e.g., max/min) per tech and hub
        """
        d = {}
        for i in range(self.nTech):
            techID = i + 1
            hublist = self.hubTech[i]
            if isinstance(hublist, float):  # if only a single hub was given and it is read as float, convert to int
                hublist = int(hublist)
            hublist = str(hublist).split(
                ',')  # convert to string (int case); if more thane one hub is given, splits hubs into a list using ',' as a delimiter

            for j in range(self.nHub):
                # check if technology is present in each hub
                hubID = j + 1
                if str(hubID) in hublist:  # if capacity is given and technology is present in hub
                    d[hubID, techID] = limit.iloc[i]
                else:
                    d[hubID, techID] = 0
        return d

    def TechCapInit(self, model):
        """
        Initialize existing technology capacities; return Pyomo-formatted dictionary for binary cost indicator
        """
        YN_techcost_dict = {}  # indicator to apply costs based on capacity (investment); model does not apply these costs to a pre-installed capacity
        #        setvals = [] # for tracking purposes only

        for i in range(len(self.instCapTech)):  # for each tech
            techID = i + 1
            if (np.isnan(self.instCapTech[i])):  # if capacity is not given
                YN_techcost_dict[techID] = 1  # investment costs apply
            else:
                YN_techcost_dict[techID] = 0  # capacity is pre-defined; investment costs do not apply
                hublist = self.hubTech[i]
                if isinstance(hublist, float):  # if only a single hub was given and it is read as float, convert to int
                    hublist = int(hublist)
                hublist = str(hublist).split(
                    ',')  # convert to string (int case); if more thane one hub is given, splits hubs into a list using ',' as a delimiter

                for j in range(self.nHub):  # for each hub
                    hubID = j + 1
                    if str(hubID) in hublist:  # if capacity is given and technology is present in hub
                        capVal = self.instCapTech[i]
                        model.CapTech[hubID, techID].fix(capVal)
        #                        setvals.append([hubID, techID, capVal])

        return (YN_techcost_dict)

    # ----------------------------------------------------------------------
    # Storage
    # ---------------------------------------------------------------------

    def StgMaxMinCapInit(self):
        """
        Return Pyomo-formatted dictionary of max and min cap per storage tech, hub and EC
        """
        dmax = {}
        dmin = {}

        if self.maxCapStg.empty is False:  # or self.minCapStg

            dmax = np.zeros((self.nHub, self.nEC, self.nStg))  # this format is used by GenDict3D
            dmin = np.zeros((self.nHub, self.nEC, self.nStg))

            for i in range(self.nStg):
                for k in range(self.nEC):
                    for j in range(self.nHub):
                        # check if technology is present in each hub
                        if isinstance(self.hubStg[i], float) or isinstance(self.hubStg[i],
                                                                           int):  # present in only one hub
                            if j + 1 == self.hubStg[i] and k + 1 == self.stgE[
                                i]:  # if hub j exists for tech i, AND the storage energy == energy carrier for tech i, then max cap is assigned; python starts with 0, Pyomo with 1
                                dmax[j, k, i] = self.maxCapStg.iloc[i]
                                dmin[j, k, i] = self.minCapStg.iloc[i]

                        elif str(j + 1) in list(self.hubStg[i]) and k + 1 == self.stgE[
                            i]:  # python starts with 0, Pyomo with 1; if hub j exists for tech i (in a list of multiple hubs), AND the storage energy == energy carrier for tech i, then max cap is assigned;
                            dmax[j, k, i] = self.maxCapStg.iloc[i]
                            dmin[j, k, i] = self.minCapStg.iloc[i]

        maxc = pd.Panel(dmax)
        maxc.major_axis = [int(x) + 1 for x in maxc.major_axis]
        maxc.minor_axis = [int(x) + 1 for x in maxc.minor_axis]
        maxcap_dict = {}
        maxcap_dict = self.GenDict3D(maxcap_dict, maxc)

        minc = pd.Panel(dmin)
        minc.major_axis = [int(x) + 1 for x in minc.major_axis]
        minc.minor_axis = [int(x) + 1 for x in minc.minor_axis]
        mincap_dict = {}
        mincap_dict = self.GenDict3D(mincap_dict, minc)

        return (maxcap_dict, mincap_dict)

    def StgCapInit(self, model):
        """
        Initialize existing storage capacities; return Pyomo-formatted dictionary for binary cost indicator
        """
        YN_stgcost_dict = {}  # indicator to apply costs based on capacity (investment); model does not apply these costs to a pre-installed capacity
        #        setvals = [] # for tracking purposes only

        if self.instCapStg.empty is False:
            for i in range(len(self.instCapStg)):  # for each tech
                stgID = i + 1
                ecID = self.stgE[i]
                if (np.isnan(self.instCapStg[i])):  # if capacity is not given
                    YN_stgcost_dict[stgID] = 1  # investment costs apply
                else:
                    YN_stgcost_dict[stgID] = 0  # capacity is pre-defined; investment costs do not apply

                    for j in range(self.nHub):  # for each hub
                        hubID = j + 1
                        hublist = self.StorageData.loc["Hubs"][i]
                        if isinstance(hublist,
                                      float):  # if only a single hub was given and it is read as float, convert to int
                            hublist = int(hublist)
                        hublist = str(hublist).split(
                            ',')  # convert to string (int case); if more thane one hub is given, split hubs into a list using ',' as a delimiter

                        if str(hubID) in hublist:  # if capacity is given and technology is present in hub
                            capVal = self.instCapStg[i]
                            model.CapStg[hubID, stgID, ecID].fix(capVal)
        #                            setvals.append([hubID, stgID, ecID, capVal])

        return (YN_stgcost_dict)

    # ----------------------------------------------------------------------
    # Network
    # ----------------------------------------------------------------------

    def NetworkInit(self, model):
        """
        Assign network connection data per link, connection hubs, and energy carrier; return pyomo-formatted dictionaries
        """
        YNx_dict = {}  # network link between hubs (indicator for allowable flow from hub i to j)
        len_dict = {}  # network length
        loss_dict = {}  # network loss
        invcost_dict = {}  # investment cost
        OMFcost_dict = {}  # fixed O&M cost
        OMVcost_dict = {}  # variable O&M cost
        maxcap_dict = {}  # maximum capacity
        mincap_dict = {}  # minimum capacity
        CO2_dict = {}  # CO2 factor
        life_dict = {}  # lifetime
        YN_netcost_dict = {}  # indicator to apply costs based on capacity (investment, fixed); model does not apply these costs to a pre-installed capacity, or from hub j to i where costs from hub i to j are already accounted for

        for i in range(self.NetworkData.shape[1]):
            linkID = i + 1
            len_dict[linkID] = self.netLength.iloc[i]
            loss_dict[linkID] = self.netLoss.iloc[i]
            invcost_dict[linkID] = self.invCostNet.iloc[i]
            OMFcost_dict[linkID] = self.omfCostNet.iloc[i]
            OMVcost_dict[linkID] = self.omvCostNet.iloc[i]
            CO2_dict[linkID] = self.co2Net.iloc[i]
            life_dict[linkID] = self.lifeNet.iloc[i]
            for j in range(self.nHub):
                hub_i = j + 1
                for k in range(self.nHub):
                    hub_j = k + 1
                    for l in range(self.nEC):
                        EC = l + 1
                        if self.node1.iloc[i] == hub_i and self.node2.iloc[i] == hub_j and self.netE[
                            i] == EC and hub_i != hub_j:
                            YNx_dict[linkID, hub_i, hub_j, EC] = 1

                            if self.uniFlow.iloc[i] == 'y':
                                YNx_dict[linkID, hub_j, hub_i, EC] = 0
                            else:
                                YNx_dict[linkID, hub_j, hub_i, EC] = 1

                            maxcap_dict[linkID, hub_i, hub_j, EC] = self.maxCapNet.iloc[i]
                            maxcap_dict[linkID, hub_j, hub_i, EC] = self.maxCapNet.iloc[i]
                            mincap_dict[linkID, hub_i, hub_j, EC] = self.minCapNet.iloc[i]
                            mincap_dict[linkID, hub_j, hub_i, EC] = self.minCapNet.iloc[i]

                            if np.isnan(self.instCapNet.iloc[i]) == False:  # if installed capacity exists
                                model.CapNet[linkID, hub_i, hub_j, EC].fix(
                                    self.instCapNet.iloc[i])  # set capacity to self.instCapNet.iloc[i]
                                YN_netcost_dict[
                                    linkID, hub_i, hub_j, EC] = 0  # do not apply cost based on capacity (investment, fixed)
                                YN_netcost_dict[linkID, hub_j, hub_i, EC] = 0
                            else:
                                YN_netcost_dict[
                                    linkID, hub_i, hub_j, EC] = 1  # only acccount for investment and fixed cost from i to j
                                YN_netcost_dict[
                                    linkID, hub_j, hub_i, EC] = 0  # ignore investment and fixed cost from j to i

                        elif self.node1.iloc[i] == hub_j and self.node2.iloc[i] == hub_i and self.netE[
                            i] == EC and hub_i != hub_j:
                            linkID  # do nothing (parameters have been set in previous block; this segment is to avoid overwriting values with 0)

                        else:
                            YNx_dict[linkID, hub_i, hub_j, EC] = 0
                            maxcap_dict[linkID, hub_i, hub_j, EC] = 0
                            mincap_dict[linkID, hub_i, hub_j, EC] = 0
                            YN_netcost_dict[linkID, hub_i, hub_j, EC] = 0
                            # set capacity to 0

        return (YNx_dict, YN_netcost_dict, len_dict, loss_dict, invcost_dict, OMFcost_dict, OMVcost_dict, maxcap_dict,
                mincap_dict, CO2_dict, life_dict)

    # ----------------------------------------------------------------------
    # Captial recovery factor
    # ----------------------------------------------------------------------

    def CRF(self, life):
        """
        Return Pyomo-formatted dictionary of capital recovery factor
        """
        CRFd = {}

        if life.empty is False:
            CRF = 1 / (((1 + self.interest) ** life - 1) / (self.interest * ((1 + self.interest) ** life)))
            CRFd = self.GenDict(life.shape[0], CRF)
        return CRFd