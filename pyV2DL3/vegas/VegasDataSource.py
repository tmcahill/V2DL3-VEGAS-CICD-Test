import ROOT

from pyV2DL3.vegas.fillEVENTS_not_safe import __fillEVENTS_not_safe__
from pyV2DL3.vegas.fillRESPONSE_not_safe import __fillRESPONSE_not_safe__
from pyV2DL3.vegas.load_vegas import VEGASStatus
from pyV2DL3.VtsDataSource import VtsDataSource
from pyV2DL3.vegas.util import loadUserCuts


class VegasDataSource(VtsDataSource):
    def __init__(self, evt_file,
                 event_classes,
                 bypass_fov_cut=False,
                 event_class_mode=False,
                 reco_type=1,
                 save_msw_msl=False,
                 user_cut_file=None,
                 ):
        super(VegasDataSource, self).__init__("VEGAS", evt_file, None)

        # Developer exceptions to ensure this was constructed with EventClass(es)
        if event_classes is None:
            raise Exception("VegasDataSource uses EventClasses for effective areas")

        # Loading VEGAS if not already done so
        self.vegas_status = VEGASStatus()
        self.vegas_status.loadVEGAS()
        self.__evt_file__ = ROOT.VARootIO(evt_file, True)
        self.__event_classes__ = event_classes
        self.__event_class_mode__ = event_class_mode
        self.__fov_cut__ = not bypass_fov_cut
        self.__reco_type__ = reco_type
        self.__save_msw_msl__ = save_msw_msl
        if user_cut_file is not None:
            # Load user defined cuts. See loadUserCuts() in util.py for possible keys.
            self.__user_cuts__ = loadUserCuts(user_cut_file)
        else:
            self.__user_cuts__ = None

        # Auxiliary storage
        self.__azimuth__ = 0
        self.__zenith__ = 0
        self.__noise__ = 0

    def __del__(self):
        """Close the root files

        These typechecks will prevent the user from having their true exception
        buried by a CPyCppyy exception on program exit.
        """
        cpy_nonestring = "<class 'CPyCppyy_NoneType'>"

        if str(type(self.__evt_file__)) != cpy_nonestring and not isinstance(self.__evt_file__, str):
            self.__evt_file__.closeTheRootFile()


    def __fill_evt__(self):
        gti, ea_config, evt_dicts = __fillEVENTS_not_safe__(self.__evt_file__, self.__event_classes__,
                                                            event_class_mode=self.__event_class_mode__,
                                                            fov_cut=self.__fov_cut__,
                                                            reco_type=self.__reco_type__,
                                                            save_msw_msl=self.__save_msw_msl__,
                                                            user_cuts_dict=self.__user_cuts__,
                                                            )
        self.__gti__ = gti
        # This is an array of dicts for each event class (array of one when not using event class mode)
        self.__evt__ = evt_dicts
        self.__azimuth__ = ea_config["azimuth"]
        self.__zenith__ = ea_config["zenith"]
        self.__noise__ = ea_config["noise"]

    def __fill_gti__(self):
        pass

    def __fill_response__(self):
        az = self.__azimuth__
        ze = self.__zenith__
        nn = self.__noise__
        response_dicts = []
        # Fill response for each event class
        for ec in self.__event_classes__:
            response_dicts.append(
                __fillRESPONSE_not_safe__(ec, az, ze, nn, self.__irf_to_store__)
            )

        self.__response__ = response_dicts
