#!/usr/bin/env python

"""
Isothermal Penman-Monteith

Reference:
==========
* Leuning et al. (1995) Leaf nitrogen, photosynthesis, conductance and
  transpiration: scaling from leaves to canopies

"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (23.07.2015)"
__email__ = "mdekauwe@gmail.com"


import math
import sys


class PenmanMonteith(object):

    def __init__(self, leaf_width, SW_abs, angle=35.0):

        self.kpa_2_pa = 1000.
        self.sigma = 5.6704E-08        # Stefan-Boltzmann constant, (w m-2 k-4)
        self.emissivity_leaf = 0.99    # emissivity of leaf (-)
        self.cp = 1010.0               # specific heat of dry air (j kg-1 k-1)
        self.h2olv0 = 2.501e6          # latent heat H2O (J kg-1)
        self.h2omw = 18E-3             # mol mass H20 (kg mol-1)
        self.air_mass = 29.0E-3        # mol mass air (kg mol-1)
        self.umol_to_j = 4.57          # conversion from J to umol quanta
        self.dheat = 21.5E-6           # molecular diffusivity for heat (m2 s-1)
        self.DEG_TO_KELVIN = 273.15
        self.RGAS = 8.314               # universal gas constant (mol-1 K-1)
        self.SW_abs = SW_abs            # absorptance to short-wave radiation
        self.leaf_width = leaf_width    # (m)
        self.Rspecifc_dry_air = 287.058 # Jkg-1 K-1

        self.GSC_2_GSW = 1.57
        self.GSW_2_GSC = 1.0 / self.GSC_2_GSW

        self.angle = angle              # angle from horizontal (deg) 0-90
        self.PAR_2_SW = 2.0 / self.umol_to_j

    def calc_et(self, tleaf, tair, vpd, pressure, wind, par, gh, gw,
                rnet):
        """
        Calculate transpiration following Penman-Monteith at the leaf level
        accounting for effects of leaf temperature and feedback on evaporation.
        For example, if leaf temperature is above the leaf temp, it can increase
        vpd, but it also reduves the lw and thus the net rad availble for
        evaporaiton.

        Parameters:
        ----------
        tair : float
            air temperature (deg C)
        tleaf : float
            leaf temperature (deg C)
        vpd : float
            Vapour pressure deficit (kPa, needs to be in Pa, see conversion
            below)
        pressure : float
            air pressure (using constant) (Pa)
        wind : float
            wind speed (m s-1)
        par : float
            Photosynthetically active radiation (umol m-2 s-1)
        gh : float
            boundary layer conductance to heat (mol m-2 s-1)
        gw :float
            conductance to water vapour (mol m-2 s-1)
        rnet : float
            Net radiation (J m-2 s-1 = W m-2)

        Returns:
        --------
        et : float
            transpiration (mol H2O m-2 s-1)
        lambda_et : float
            latent heat flux (W m-2)
        """
        # latent heat of water vapour at air temperature (j mol-1)
        lambda_et = (self.h2olv0 - 2.365E3 * tair) * self.h2omw

        # slope of sat. water vapour pressure (e_sat) to temperature curve
        # (pa K-1), note kelvin conversion in func
        slope = ((self.calc_esat(tair + 0.1, pressure) -
                  self.calc_esat(tair, pressure)) / 0.1)
        #slope = self.calc_slope_of_saturation_vapour_pressure_curve(tair)

        # psychrometric constant
        gamma = self.cp * self.air_mass * pressure / lambda_et

        if gw <= 0.0:
            # gs = 0, transpiration = 0
            return (0.0, 0.0)
        else:
            # Y cancels in eqn 10
            arg1 = (slope * rnet + (vpd * self.kpa_2_pa) * gh * self.cp *
                    self.air_mass)
            arg2 = slope + gamma * gh / gw
            et = arg1 / arg2

            # latent heat loss
            LE_et = et

            # et units = mol H20 m-2 s-1,
            # multiply by 18 (grams)* 0.001 (grams to kg) * 86400.
            # to get to kg m2 d-1 or mm d-1

            return (et / lambda_et, LE_et)

    def calc_conductances(self, tair_k, tleaf, tair, wind, gsc, cmolar):
        """
        Both forced and free convection contribute to exchange of heat and mass
        through leaf boundary layers at the wind speeds typically encountered
        within plant canopies (<0-5ms~'). It is particularly imponant to
        includethe contribution of buoyancy forces to the boundary
        conductance for sunlit leaves deep within the canopy where wind speeds
        are low, for without this mechanism computed leaf temperatures become
        excessively high.

        Parameters:
        ----------
        tair_k : float
            air temperature (K)
        tleaf : float
            leaf temperature (deg C)
        wind : float
            wind speed (m s-1)
        gsc : float
            stomatal conductance to CO2 (mol m-2 s-1)
        cmolar : float
            Conversion from m s-1 to mol m-2 s-1

        Returns:
        --------
        grn : float
            radiation conductance (mol m-2 s-1)
        gh : float
            total leaf conductance to heat (mol m-2 s-1), *note* two sided.
        gbH : float
            total boundary layer conductance to heat for one side of the leaf
        gw : float
            total leaf conductance to water vapour (mol m-2 s-1)

        References
        ----------
        * Leuning 1995, appendix E
        * Medlyn et al. 2007 appendix, for need for cmolar
        """

        # radiation conductance (mol m-2 s-1)
        grn = ((4.0 * self.sigma * tair_k**3 * self.emissivity_leaf) /
               (self.cp * self.air_mass))

        # boundary layer conductance for 1 side of leaf from forced convection
        # (mol m-2 s-1)
        gbHw = 0.003 * math.sqrt(wind / self.leaf_width) * cmolar

        # grashof number
        grashof_num = 1.6E8 * math.fabs(tleaf - tair) * self.leaf_width**3

        # boundary layer conductance for free convection
        # (mol m-2 s-1)
        gbHf = 0.5 * self.dheat * grashof_num**0.25 / self.leaf_width * cmolar

        # total boundary layer conductance to heat for one side of the leaf
        gbH = gbHw + gbHf

        # ... for hypostomatous leaves only gbH should be doubled and the
        # single-sided value used for gbv
        # total leaf conductance to heat (mol m-2 s-1), two sided see above.
        gh = 2.0 * (gbH + grn)
        gbw = gbH * self.GSC_2_GSW
        gsw = gsc * self.GSC_2_GSW

        # total leaf conductance to water vapour (mol m-2 s-1)
        gw = (gbw * gsw) / (gbw + gsw)

        return (grn, gh, gbH, gw)

    def calc_rnet(self, par, tair, tair_k, tleaf_k, vpd, pressure):
        """
        Net isothermal radaiation (Rnet, W m-2), i.e. the net radiation that
        would be recieved if leaf and air temperature were the same.

        References:
        ----------
        Jarvis and McNaughton (1986)

        Parameters:
        ----------
        par : float
            Photosynthetically active radiation (umol m-2 s-1)
        tair : float
            air temperature (deg C)
        tair_k : float
            air temperature (K)
        tleaf_k : float
            leaf temperature (K)
        vpd : float
            Vapour pressure deficit (kPa, needs to be in Pa, see conversion
            below)
        pressure : float
            air pressure (using constant) (Pa)

        Returns:
        --------
        rnet : float
            Net radiation (J m-2 s-1 = W m-2)

        """

        # Short wave radiation (W m-2)
        SW_rad = par * self.PAR_2_SW

        # absorbed short-wave radiation
        SW_abs = self.SW_abs * math.cos(math.radians(self.angle)) * SW_rad

        # atmospheric water vapour pressure (Pa)
        ea = max(0.0, self.calc_esat(tair, pressure) - (vpd * self.kpa_2_pa))

        # eqn D4
        emissivity_atm = 0.642 * (ea / tair_k)**(1.0 / 7.0)

        # incoming long-wave radiation (W m-2)
        lw_in = emissivity_atm * self.sigma * tair_k**4

        # outgoing long-wave radiation (W m-2)
        lw_out = self.emissivity_leaf * self.sigma * tleaf_k**4

        # isothermal net radiation (W m-2), note W m-2 = J m-2 s-1
        
        # Rnet < 0.0 causes discontinuity in plot, which I guess isn't there
        # if summing over day/not calculating instantaneous values...
        # set to zero to stop this for instantaneous calculations
        #rnet = SW_abs + lw_in - lw_out
        rnet = max(0.0, SW_abs + lw_in - lw_out)

        return rnet

    def calc_slope_of_saturation_vapour_pressure_curve(self, tair):
        """ Eqn 13 from FAO paper, Allen et al. 1998.

        Parameters:
        ----------
        tair : float
            air temperature (deg C)

        Returns:
        --------
        slope : float
            slope of saturation vapour pressure curve [Pa degC-1]

        """
        t = tair + 237.3
        arg1 = 4098.0 * (0.6108 * math.exp((17.27 * tair) / t))
        arg2 = t**2
        return (arg1 / arg2) * self.kpa_2_pa

    def calc_esat(self, tair, pressure):
        """
        Saturation vapor pressure

        Values of saturation vapour pressure from the Tetens formula are
        within 1 Pa of the exact values.

        Taken from

        Parameters:
        ----------
        tair : float
            air temperature (deg C)
        pressure : float
            air pressure (using constant) (Pa)

        Returns:
        --------
        esat : float
            Saturation vapor pressure (Pa K-1)

        References:
        * Buck, A. (1981) New equations for computing vapor pressure and
          enhancement factor. Journal of Applied Meteorology, 20, 1527-1532

        but also see...
        * Stull 2000 Meteorology for Scientist and Engineers
        * Jones 1992 p 110 (note error in a - wrong units)
        """
        #Tk = tair + self.DEG_TO_KELVIN
        #e0 = 0.611 * self.kpa_2_pa
        #b = 17.2694
        #T1 = 273.16 # kelvin
        #T2 = 35.86  # kelvin

        #return e0 * math.exp(b * (Tk - T1) / (Tk - T2))

        a = 611.21
        b = 17.502
        c = 240.97
        f = 1.0007 + 3.46 * 10E-8 * pressure
        esat = f * a * (math.exp(b * tair / (c + tair)))

        return esat



    def main(self, tleaf, tair, gs, vpd, pressure, wind, par):

        tleaf_k = tleaf + DEG_TO_KELVIN
        tair_k = tair + DEG_TO_KELVIN

        air_density = pressure  / (self.Rspecifc_dry_air * tair_k)
        cmolar = pressure  / (RGAS * tair_k)
        rnet = P.calc_rnet(par, tair, tair_k, tleaf_k, vpd, pressure)

        (grn, gh, gbH, gw) = P.calc_conductances(tair_k, tleaf, tair,
                                                 wind, gsc, cmolar)
        (et, lambda_et) = P.calc_et(tleaf, tair, vpd, pressure, wind, par,
                                    gh, gw, rnet)
        return (et, lambda_et)

if __name__ == '__main__':

    par = 1000.0
    tleaf = 21.5
    tair = 20.0
    gs = 0.15
    vpd = 2.0
    pressure = 101325.0 # Pa
    wind = 2.0
    leaf_width = 0.02
    SW_abs = 0.5 # absorptance to short_wave rad [0,1], typically 0.4-0.6
    DEG_TO_KELVIN = 273.15
    RGAS = 8.314
    angle = 35.0 # angle from horizontal

    P = PenmanMonteith(leaf_width, SW_abs, angle)
    (et, lambda_et) = P.main(tleaf, tair, gs, vpd, pressure, wind, par)

    print et, lambda_et
