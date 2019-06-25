from builtins import object
from collections import OrderedDict
from .downtimeModelConfig import DowntimeModelConfig
from lsst.sims.downtimeModel import version


__all__ = ["DowntimeModel"]


class DowntimeModel(object):
    """Downtime estimates, both scheduled and unscheduled.

    Parameters
    ----------
    config: DowntimeModelConfig, opt
        A configuration class for the downtime model.
        This can be None, in which case the default DowntimeModelConfig is used.
        The user should set any non-default values for DowntimeModelConfig before
        configuration of the actual DowntimeModel.

    self.efd_requirements and self.target_requirements are also set.
    efd_requirements is a tuple: (list of str, float).
    This corresponds to the data columns required from the EFD and the amount of time history required.
    target_requirements is a list of str.
    This corresponds to the data columns required in the target dictionary passed when calculating the
    processed telemetry values.
    """
    def __init__(self, config=None):
        self._configure(config=config)
        self.efd_requirements = (self._config.efd_columns, self._config.efd_delta_time)
        self.schedDown = self._config.efd_columns[0]
        self.unschedDown = self._config.efd_columns[1]
        self.target_requirements = self._config.target_columns

    def _configure(self, config=None):
        """Configure the model. After 'configure' the model config will be frozen.

        Parameters
        ----------
        config: DowntimeModelConfig, opt
            A configuration class for the downtime model.
            This can be None, in which case the default values are used.
        """
        if config is None:
            self._config = DowntimeModelConfig()
        else:
            if not isinstance(config, DowntimeModelConfig):
                raise ValueError('Must use a DowntimeModelConfig.')
            self._config = config
        self._config.validate()
        self._config.freeze()

    def config_info(self):
        """Report configuration parameters and version information.

        Returns
        -------
        OrderedDict
        """
        config_info = OrderedDict()
        config_info['DowntimeModel_version'] = '%s' % version.__version__
        config_info['DowntimeModel_sha'] = '%s' % version.__fingerprint__
        for k, v in self._config.iteritems():
            config_info[k] = v
        return config_info

    def __call__(self, efdData, targetDict):
        """Calculate the sky coverage due to clouds.

        Parameters
        ----------
        efdData: dict
            Dictionary of input telemetry, typically from the EFD.
            This must contain columns self.efd_requirements.
            (work in progress on handling time history).
        targetDict: dict
            Dictionary of target values over which to calculate the processed telemetry.
            (e.g. mapDict = {'ra': [], 'dec': [], 'altitude': [], 'azimuth': [], 'airmass': []})
            Here we use 'time', an astropy.time.Time, as we just need to know the time.

        Returns
        -------
        dict of bool, astropy.time.Time, astropy.time.Time
            Status of telescope (True = Down, False = Up) at time,
            time of expected end of downtime (~noon of the first available day),
            time of next scheduled downtime (~noon of the first available day).
        """
        # Check for downtime in scheduled downtimes.
        time = targetDict[self.target_requirements[0]]
        next_start = efdData[self.schedDown]['start'].searchsorted(time, side='right')
        next_end = efdData[self.schedDown]['end'].searchsorted(time, side='right')
        if next_start > next_end:
            # Currently in a scheduled downtime.
            current_sched = efdData[self.schedDown][next_end]
        else:
            # Not currently in a scheduled downtime.
            current_sched = None
        # This will be the next reported/expected downtime.
        next_sched = efdData[self.schedDown][next_start]
        # Check for downtime in unscheduled downtimes.
        next_start = efdData[self.unschedDown]['start'].searchsorted(time, side='right')
        next_end = efdData[self.unschedDown]['end'].searchsorted(time, side='right')
        if next_start > next_end:
            # Currently in an unscheduled downtime.
            current_unsched = efdData[self.unschedDown][next_end]
        else:
            current_unsched = None

        # Figure out what to report about current state.
        if current_sched is None and current_unsched is None:  # neither down
            status = False
            end_down = None
        else:   # we have a downtime from something ..
            if current_unsched is None:  # sched down only
                status = True
                end_down = current_sched['end']
            elif current_sched is None:  # unsched down only
                status = True
                # should decide what to report on end of downtime here ..
                end_down = current_unsched['end']
            else:  # both down ..
                status = True
                end_down = max(current_sched['end'], current_unsched['end'])
        return {'status': status, 'end': end_down, 'next': next_sched['start']}