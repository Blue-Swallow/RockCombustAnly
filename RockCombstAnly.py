# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 13:40:16 2018

@author: T.J.-LAB-PC
"""

import os, sys
import numpy as np
import pandas as pd
from execute import Read_datset


class Cui_input():
    """
    Class to attract information through CUI to generate .inp file
    
    Class variable
    ----------
    self._langlist_: list ["jp","en",...]
        Contain initial two characters of language name.
    
    self._sntns_df_ : dict {outer_key: innerdict, ...}
        outer_key: string\n
            it is representative of the questionaire type. \n
        innerdict: string\n
            it is a questionaier sentense.

    self._lang_: string
        Selected language from the "_langlist_"
        
    self.ex_path: string
        Path containing experiment data
    
    self.ex_file: string
        The name of experimant data file (.csv)
        
    self.ex_param: dict {param_name: symbol}
        Parameter dictionary
        param_name: string; e.g., time [s], Oxidizer mass flow rate [kg/s], ...
        symbol: string; e.g., t, mox, ... 
        
    self.ex_df: DataFrame
        Data frame of measured parameter in an experiment
    
    self.input_param: dict{key, value}
        key: str, "mode"
        value: int, 1, 2, 3, 4, 5
        the value is reperesentative number,
        1: RT-1, Re-construction technique 1 
        2: RT-2, Re-construction technique 2
        3: RT-3, Re-construction technique 3 
        4: RT-4, Re-construction technique 4
        5: RT-5, Re-construction technique 5
        
        key: str, "Dt"
        value: float, nozzle throat diameter [m]
        
        key: str, "eps"
        value: float, nozzle expansion ratio [-]
        
        key: str, "Mf"
        value: float, fuel consumption [kg]
    
    self.cea_path: string
        Path containing the results of cea calculation
   
        
    """
    _langlist_ = ["jp","en"]
    _tmp_ = dict()
    _tmp_["oxid"] = {"jp": "\n\n計算オプション(0~2)を選択してください．\n例: 0: 全域平衡計算\n    1: 燃焼器内のみ平衡計算\n    2: スロートまで平衡計算",
                     "en": "\n\nPlease select option (0-2) of calculation.\ne.g.: 0: equilibrium during expansion\n      1: frozen after the end of chamber\n      2: frozen after nozzle throat"}

    def __init__(self):
        self._sntns_df_ = pd.DataFrame([], columns=self._langlist_)
        for i in self._tmp_:
            self._sntns_df_ = self._sntns_df_.append(pd.DataFrame(self._tmp_[i], index=[i]))
#        self._inp_lang_()
        self._get_expath_()
        self._get_ceapath_()
        self.cea_db = Read_datset(self.cea_path)
        self.input_param = dict()
        self._select_mode_()
        self._input_nozzle_()
        self._input_eps_()
        self._input_consump_()
        

    def _inp_lang_(self):
        """
        Select user language
        """
        print("Please select language.\n{}".format(self._langlist_))
        lang = input()
        if lang in self._langlist_:
            self._lang_ = lang
        else:
            print("There is no such language set!")

    def _get_expath_(self):
        """
        Get the experiment folder path, file name and data and, create template file to contain an experimental data
            ex_path: string, folder path 
            ex_file: string, file name
            ex_df: data frame of experintal data
            ex_param: dictionary of experimental data
        """
        cadir = os.path.dirname(os.path.abspath(__file__))
        while(True):
            print("\nInput a Experiment Name (The Name of Folder Containing Experiment Data) >>")
            foldername = input()
            self.ex_path = os.path.join(cadir, foldername)
            if os.path.exists(self.ex_path):
                self.ex_file = "ex_dat.csv"
                file_path = os.path.join(self.ex_path, self.ex_file)
                p_name = ("time [s]", "Oxidizer mass flow rate [g/s]", "Chamber pressure [MPaG]", "Thrust [N]", "Nozzle exit pressure [MPaG]")
                symbol = ("t", "mox", "Pc", "F", "Pe")
                self.ex_param = dict(zip(p_name, symbol))
                if os.path.exists(file_path):
                    self.ex_df = pd.read_csv(file_path,header=1, index_col=0)
                    self.ex_df.mox = self.ex_df.mox * 1.0e-3 #convert [g/s] to [kg/s]
                    self.ex_df.Pc = self.ex_df.Pc * 1.0e+6 + 0.1013 #convert [MPaG] to [Pa]
                    self.ex_df.Pe = self.ex_df.Pe * 1.0e+6 + 0.1013 #convert [MPaG] to [Pa]
                    break
                else: # create template file
                    print("\nThere is no such a experiment data/n{}".format(file_path))
                    print("\nDo you want to make a template file ?\ny/n ?")
                    flag = input()
                    if flag == "y":
                        df = pd.DataFrame(self.ex_param, index=[0], columns=p_name)
                        df.to_csv(file_path, index= False)
                    elif flag == "n":
                        sys.exit()
            else:
                print("\nThere is no such a Folder\n{}".format(self.ex_path))           


    def _get_ceapath_(self):
        """
        Return the folder path cantaining the results of cea calculation.
            cea.path: string, folder path containing "out" folder
        """
        cadir = os.path.dirname(os.path.abspath(__file__))
        while(True):
            print("\nInput the Folder Name Containing Results of CEA >>")
            foldername = input()
            self.cea_path = os.path.join(cadir, foldername)
            self.cea_path = os.path.join(self.cea_path, "out")
            if os.path.exists(self.cea_path):
                break
            else:
                print("There is no such a dataset folder/n{}".format(self.cea_path))
                
    def _select_mode_(self):
        """
        Select a calculation mode; RT-1,2,3,4,5,...
        """
        while(True):
            print("Please select calculation mode.\n")
            print("1: RT-1\n2: RT-2\n3: RT-3\n4: RT-4\n5: RT-5\n")
            mode = {1: "RT-1",
                    2: "RT-2",
                    3: "RT-3",
                    4: "RT-4",
                    5: "RT-5"}
            inp = int(input())
            if inp in mode.keys():
                self.input_param["mode"] = inp
                break
            else:
                print("There is no such a mode \"{}\"".format(inp))
                
    def _input_nozzle_(self):
        """
        Input the nozzle diameter [mm]
        """
        print("Please input nozzle throat diameter [mm]")
        self.input_param["Dt"] = float(input())*1.0e-3

    def _input_eps_(self):
        """
        Input the nozzle expansion ratio [-]
        """
        print("Please input nozzle expansion ratio")
        self.input_param["eps"] = float(input())
        
    def _input_consump_(self):
        """
        Input the fuel consumption [g]
        """
        print("Please input fuel consumption [g]")
        self.input_param["Mf"] = float(input())*1.0e-3

class RT():
    """
    Class executing re-construction technique and acquiering calculated results.
    
    Parameters
    ---------
    inst: class
        instance generated by "Cui_input()" class
        
    Class variable
    --------------
    self.of: 1-d ndarray
        list of oxidizer to fuel ratio calculated by CEA
    
    self.Pc: 1-d ndarray
        list of chamber pressure by CEA
        
    self.ex_df: pandas.DataFrame
        data frame of experimet data

    self.cstr: function
        function of characteristic exhaust velocity: self.cstr(of, Pc)
        
    self.gamma: function
        function of specific heat ratio at the end of chamber: self.gamma(of, Pc)
    """
    def __init__(self, inst):
        self.inst = inst
        self.of = inst.cea_db.of #range of O/F in the database calculated by CEA
        self.Pc = inst.cea_db.Pc #range of Chamber Pressure in the database calculated by CEA
        self.ex_df = inst.ex_df #Data Frame of experiment data
        self.input_param = inst.input_param
        self.cstr = inst.cea_db.gen_func("CSTAR") #data-base of characteristics exhaust velocity
        self.gamma = inst.cea_db.gen_func("GAMMAs_c") #data-base of specific heat ratio at chamber
        
    def _call_rt_(self):
        if self.input_param["mode"] == 1:
            anl_df = rt_1.main(self.ex_df, self.of, self.Pc, self.cstr, self.gamma, self.input_param)
        if self.input_param["mode"] == 2:
            anl_df = rt_2.main(self.ex_df, self.of, self.Pc, self.cstr, self.gamma, self.input_param)
        if self.input_param["mode"] == 3:
            anl_df = rt_3.main(self.ex_df, self.of, self.Pc, self.cstr, self.gamma, self.input_param)
        if self.input_param["mode"] == 4:
            anl_df = rt_4.main(self.ex_df, self.of, self.Pc, self.cstr, self.gamma, self.input_param)
        if self.input_param["mode"] == 5:
            anl_df = rt_5.main(self.ex_df, self.of, self.Pc, self.cstr, self.gamma, self.input_param)


    
if __name__ == "__main__":
    inst = Cui_input()
#    RT(inst)
    

    