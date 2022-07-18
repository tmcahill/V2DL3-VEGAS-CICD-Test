import ROOT
import logging
import numpy as np
from ctypes import c_float

from pyV2DL3.vegas.util import getCuts
from pyV2DL3.vegas.load_vegas import VEGASStatus
logger = logging.getLogger(__name__)

"""
Construct an event class from an effective area cuts info

Event Classes are wrappers for VEGAS effective area files to efficiently
read, store, and validate parameters for event cutting or sorting

To extend event classes to include more parameters, add them
here in order to access them when filling events and IRFs.

https://veritas.sao.arizona.edu/wiki/V2dl3_dev_notes#Event_Classes
"""


class EventClass(object):
    def __init__(self, effective_area):
        self.__vegas__ = VEGASStatus()
        self.__vegas__.loadVEGAS()
        self.effective_area_IO = ROOT.VARootIO(effective_area, True)
        self.effective_area_IO.loadTheRootFile()
        self.manager = ROOT.VAEffectiveAreaManager()
        self.manager.setUseReconstructedEnergy(False)
        self.manager.loadEffectiveAreas(self.effective_area_IO)

        # Initialize the cuts parameter names to search for
        cut_searches = [
                        "ThetaSquareUpper",
                        "MeanScaledWidthLower", "MeanScaledWidthUpper",  # MSW
                        "MaxHeightLower",       "MaxHeightUpper",        # Max height
                        "FoVCutUpper",          "FoVCutLower",           # Field of view
                        ]

        # Initialize corresponding class variables
        self.theta_square_upper = None
        self.msw_lower = None
        self.msw_upper = None
        self.max_height_lower = None
        self.max_height_upper = None
        self.fov_cut_lower = None
        self.fov_cut_upper = None

        # Now load the cuts params
        self.__load_cuts_info__(cut_searches)

        # Build indexes for IRFs
        self.axis_dict, self.index_dict = self.__build_index__()


    """
    Build az, zen, noise, and offset indexes for this EA.
    """
    def __build_index__(self):
        manager = self.manager
        axis = ["Azimuth", "Zenith", "Noise"]
        if len(manager.fEffectiveAreas) <= 0:
            raise Exception("No effective areas! ")
        index_check = manager.fEffectiveAreas.at(0).fDimensionNames
        for k in axis:
            if k not in index_check:
                raise Exception("IRF missing axis: {}".format(k))
        index_dict = {"Index": []}

        for i, ea in enumerate(manager.fEffectiveAreas):
            index_dict["Index"].append(i)
            for name, val in zip(ea.fDimensionNames, ea.fDimensionValues):
                if name not in index_dict:
                    index_dict[name] = []
                else:
                    index_dict[name].append(val)

        # Deal with AbsoluteOffset
        if "AbsoluteOffset" not in index_check:
            logger.info("No offset axis available from file. Use 0.5 deg as default.")
            index_dict["AbsoluteOffset"] = []
            for _ in range(len(index_dict["Index"])):
                index_dict["AbsoluteOffset"].append(0.5)

        # Validate Completeness
        axis_dict = {}
        check_num = 1

        for k in axis + ["AbsoluteOffset"]:
            check_num *= len(np.unique(index_dict[k]))
            axis_dict[k] = np.sort(np.unique(index_dict[k]))
            if len(axis_dict[k]) < 2 and k != "AbsoluteOffset":
                raise Exception("{} Axis need to have more than two values".format(k))
        return axis_dict, index_dict


    def get_safe_energy(self, az, ze, noise):
        manager = self.manager
        effectiveAreaParameters = ROOT.VAEASimpleParameterData()
        effectiveAreaParameters.fAzimuth = az
        effectiveAreaParameters.fZenith = ze
        effectiveAreaParameters.fNoise = noise

        effectiveAreaParameters.fOffset = 0.5
        effectiveAreaParameters = manager.getVectorParamsFromSimpleParameterData(
            effectiveAreaParameters
        )
        minEnergy, maxEnergy = c_float(), c_float()
        # Is it the right way ? what does the offset here provide ?
        manager.getSafeEnergyRange(effectiveAreaParameters, 0.5, minEnergy, maxEnergy)
        return minEnergy.value / 1000.0, maxEnergy.value / 1000.0


    """
    Loads and stores the effective area's cuts parameters values
    """
    def __load_cuts_info__(self, cut_searches):
        # This dict will only contain keys from the found cuts.
        for cuts in self.effective_area_IO.loadTheCutsInfo():
            ea_cut_dict = getCuts(cuts.fCutsFileText, cut_searches)

        # MSW cuts are optional
        if "MeanScaledWidthLower" in ea_cut_dict:
            self.msw_lower = float(ea_cut_dict["MeanScaledWidthLower"])
        else:
            # Assign +/- inf so that comparisons will still work when filling events
            self.msw_lower = float('-inf')
        if "MeanScaledWidthUpper" in ea_cut_dict:
            self.msw_upper = float(ea_cut_dict["MeanScaledWidthUpper"])
        else:
            self.msw_upper = float('inf')
        if (self.msw_lower >= self.msw_upper):
            raise Exception("MeanScaledWidthLower: " + str(
                self.msw_lower) + " must be < MeanScaledWidthUpper: " + str(self.msw_upper))

        # Theta^2 cut is required
        if "ThetaSquareUpper" in ea_cut_dict:
            self.theta_square_upper = float(ea_cut_dict["ThetaSquareUpper"])
        else:
            raise Exception("ThetaSquareUpper not found in EA cuts parameters")