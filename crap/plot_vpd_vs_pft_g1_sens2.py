#!/usr/bin/env python

"""
Compare transpiration sensitivity to PFT difference in g1 vs. inc. temp/VPD

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (23.07.2015)"
__email__ = "mdekauwe@gmail.com"

import sys
import numpy as np
import os
import math
import matplotlib.pyplot as plt

from farq import FarquharC3
from stomatal_conductance_models import StomtalConductance
from leaf_energy_balance import LeafEnergyBalance
from solve_coupled_An_gs_leaf_temp_transpiration import CoupledModel

def get_values(vpd, Ca, tair, par, pressure, C):
    store = []
    for ta in tair:
        (An, gs, et) = C.main(ta, par, vpd, wind, pressure, Ca)
        store.append(et*18*0.001*86400.)
    return store

if __name__ == '__main__':

    fig = plt.figure(figsize=(14,4))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.1)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color'] = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor'] = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    #colour_list = brewer2mpl.get_map('Accent', 'qualitative', 8).mpl_colors
    # CB palette  with grey:
    # from http://jfly.iam.u-tokyo.ac.jp/color/image/pallete.jpg
    colour_list = ["#CC79A7", "#E69F00", "#0072B2", "#009E73", "#F0E442",
                   "#56B4E9", "#D55E00", "#000000"]

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)



    # Parameters

    # gs stuff
    g0 = 0.01
    g1 = 9.0
    D0 = 1.5 # kpa

    # A stuff
    Vcmax25 = 30.0
    Jmax25 = Vcmax25 * 2.0
    Rd25 = 2.0
    Eaj = 30000.0
    Eav = 60000.0
    deltaSj = 650.0
    deltaSv = 650.0
    Hdv = 200000.0
    Hdj = 200000.0
    Q10 = 2.0

    # Misc stuff
    leaf_width = 0.02

    SW_abs = 0.5 # absorptance to short_wave rad [0,1], typically 0.4-0.6


    # variables though obviously fixed here.
    par = 1500.0

    wind = 2.5
    pressure = 101325.0

    tair = np.linspace(0, 50, 50)
    C = CoupledModel(g0, g1, D0, Vcmax25, Jmax25, Rd25, Eaj, Eav, deltaSj,
                     deltaSv, Hdv, Hdj, Q10, leaf_width, SW_abs,
                     gs_model="leuning")
    vpd = 1.0
    Ca = 400.0
    leu_amb = get_values(vpd, Ca, tair, par, pressure, C)

    Ca = 800.0
    leu_ele = get_values(vpd, Ca, tair, par, pressure, C)

    ax1.plot(tair, leu_amb, "r-", label="LEU: Amb=400ppm")
    ax1.plot(tair, leu_ele, "r--", label="LEU: Ele=800ppm")

    vpd = 3.0
    Ca = 400.0
    leu_amb = get_values(vpd, Ca, tair, par, pressure, C)

    Ca = 800.0
    leu_ele = get_values(vpd, Ca, tair, par, pressure, C)
    ax2.plot(tair, leu_amb, "r-", label="LEU: Amb=400ppm")
    ax2.plot(tair, leu_ele, "r--", label="LEU: Ele=800ppm")


    vpd = 5.0
    Ca = 400.0
    leu_amb = get_values(vpd, Ca, tair, par, pressure, C)

    Ca = 800.0
    leu_ele = get_values(vpd, Ca, tair, par, pressure, C)

    ax3.plot(tair, leu_amb, "r-", label="LEU: Amb=400ppm")
    ax3.plot(tair, leu_ele, "r--", label="LEU: Ele=800ppm")


    g0 = 0.01
    g1 = 2.35
    D0 = -999.9 # kpa
    C = CoupledModel(g0, g1, D0, Vcmax25, Jmax25, Rd25, Eaj, Eav, deltaSj,
                     deltaSv, Hdv, Hdj, Q10, leaf_width, SW_abs,
                     gs_model="medlyn")

    Ca = 400.0
    vpd = 1.0
    med_amb = get_values(vpd, Ca, tair, par, pressure, C)

    Ca = 800.0
    med_ele = get_values(vpd, Ca, tair, par, pressure, C)

    ax1.plot(tair, med_amb, "g-", label="MED: Amb=400ppm")
    ax1.plot(tair, med_ele, "g--", label="MED: Ele=800ppm")


    Ca = 400.0
    vpd = 3.0
    med_amb = get_values(vpd, Ca, tair, par, pressure, C)

    Ca = 800.0
    med_ele = get_values(vpd, Ca, tair, par, pressure, C)

    ax2.plot(tair, med_amb, "g-", label="MED: Amb=400ppm")
    ax2.plot(tair, med_ele, "g--", label="MED: Ele=800ppm")


    Ca = 400.0
    vpd = 5.0
    med_amb = get_values(vpd, Ca, tair, par, pressure, C)

    Ca = 800.0
    med_ele = get_values(vpd, Ca, tair, par, pressure, C)

    ax3.plot(tair, med_amb, "g-", label="MED: Amb=400ppm")
    ax3.plot(tair, med_ele, "g--", label="MED: Ele=800ppm")


    ax2.set_xlabel("Tair ($^{\circ}$C)")
    ax1.set_ylabel("Transpiration (mm d$^{-1}$)")
    ax1.legend(numpoints=1, loc="best", frameon=False)
    ax1.set_ylim(0,8)
    ax2.set_ylim(0,8)
    ax3.set_ylim(0,8)

    ax1.locator_params(nbins=6)
    ax2.locator_params(nbins=6)
    ax3.locator_params(nbins=6)

    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    ax1.set_title("VPD = 1.0 (kPa)")
    ax2.set_title("VPD = 3.0 (kPa)")
    ax3.set_title("VPD = 5.0 (kPa)")

    plt.show()