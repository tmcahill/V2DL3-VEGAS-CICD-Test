import logging

import numpy as np

from pyV2DL3.vegas.irfloader import getIRF

logger = logging.getLogger(__name__)


def __fillRESPONSE_not_safe__(
    event_class, azimuth, zenith, noise, irf_to_store=None
):

    if irf_to_store is None:
        irf_to_store = {}

    response_dict = {}
    ea_final_data, ebias_final_data, abias_final_data = getIRF(
        azimuth, zenith, noise, event_class, irf_to_store["point-like"]
    )
    minEnergy, maxEnergy = event_class.get_safe_energy(azimuth, zenith, noise)
    response_dict["LO_THRES"] = minEnergy
    response_dict["HI_THRES"] = maxEnergy

    # Point-like
    if irf_to_store["point-like"]:
        response_dict["EA"] = ea_final_data
        response_dict["MIGRATION"] = ebias_final_data
        response_dict["RAD_MAX"] = np.sqrt(event_class.theta_square_upper)

    # Full-enclosure
    elif irf_to_store["full-enclosure"]:
        response_dict["FULL_EA"] = ea_final_data
        response_dict["FULL_MIGRATION"] = ebias_final_data
        response_dict["PSF"] = abias_final_data
    else:
        raise ValueError("IRF requested should be point-like or full-enclosure")

    return response_dict
