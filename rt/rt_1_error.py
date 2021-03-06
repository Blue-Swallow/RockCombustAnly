# -*- coding: utf-8 -*-
"""
Error Analysis for RT-1

@author: T.J.
"""

import copy
import pandas as pd
import numpy as np
from . import rt_1

def main(anl_df, ex_df, input_param):
    """Functioni of error analisys for RT1
    
    Parameters
    ----------
    anl_df : pandas.DataFrame
        Containing Rt-1 calculation result
    
    ex_df: pandas.DataFrame
        Containing experimental data
    
    input_param: dict
        Containing experimental condition and error of conditioni
    
    Returns
    -------
    anl_df : pandas.DataFrame
        Containg error analisys result as well as Rt-1 result
    """
    print("\nNow analyzing chamber pressure error...")
    delta_Pc = ex_df.Pc*1.1
    ex_df_Pc = ex_df.copy()
    ex_df_Pc.Pc = delta_Pc
    anl_df_dPc = rt_1.Main(ex_df_Pc, input_param)
    dof_dPc = (anl_df_dPc.of - anl_df.of)/(delta_Pc-ex_df.Pc)
    print("\nNow analyzing oxidizer mass flow rate error...")
    delta_mox = ex_df.mox*1.1
    ex_df_mox = ex_df.copy()
    ex_df_mox.mox = delta_mox
    anl_df_dmox = rt_1.Main(ex_df_mox, input_param)
    dof_dmox = (anl_df_dmox.of - anl_df.of)/(delta_mox - ex_df.mox)
    print("\nNow analyzing fuel mass consumption error...")
    delta_Mf = input_param["Mf"]*1.1
    input_param_Mf = copy.deepcopy(input_param)
    input_param_Mf["Mf"] = delta_Mf
    anl_df_Mf = rt_1.Main(ex_df, input_param_Mf)
    dof_dMf = (anl_df_Mf.of - anl_df.of)/(delta_Mf - input_param["Mf"])
    print("\nNow analyzing nozzle throat diameter error...")
    delta_Dt = input_param["Dt"]*1.1
    input_param_Dt = copy.deepcopy(input_param)
    input_param_Dt["Dt"] = delta_Dt
    anl_df_Dt = rt_1.Main(ex_df, input_param_Dt)
    dof_dDt = np.pi*(anl_df_Dt.of - anl_df.of)/(delta_Dt - input_param["Dt"])

    dPc = input_param["dPc"]
    dmox = input_param["dmox"]
    dMf = input_param["dMf"]
    dDt = input_param["dDt"]
    dof = np.sqrt(np.power(dof_dPc,2)*np.power(dPc,2) + np.power(dof_dMf,2)*np.power(dMf,2) + np.power(dof_dmox,2)*np.power(dmox,2) + np.power(dof_dDt,2)*np.power(dDt,2))
    anl_df["dof"] = dof
    anl_df["dmf"] = np.sqrt(np.power(1/anl_df.of*dmox, 2) + np.power(-anl_df.mox/np.power(anl_df.of,2)*dof, 2))
    return anl_df