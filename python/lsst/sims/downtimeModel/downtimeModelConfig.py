import lsst.pex.config as pexConfig


__all__ = ['DowntimeModelConfig']


class DowntimeModelConfig(pexConfig.Config):
    """A pex_config configuration class for default seeing model parameters.
    """
    efd_columns = pexConfig.ListField(doc="List of data required from EFD",
                                      dtype=str,
                                      default=['scheduled_downtimes', 'unscheduled_downtimes'])
    efd_delta_time = pexConfig.Field(doc="Length (delta time) of history to request from the EFD (seconds)",
                                     dtype=float,
                                     default=0)
    target_columns = pexConfig.ListField(doc="Names of the keys required in the "
                                             "scheduler target maps (time)",
                                         dtype=str,
                                         default=['time'])
