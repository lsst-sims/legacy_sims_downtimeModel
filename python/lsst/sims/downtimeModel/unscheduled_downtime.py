from builtins import object
import logging
import numpy as np
import time

__all__ = ['UnscheduledDowntime']


class UnscheduledDowntime(object):
    """Handle creating the unscheduled downtime information.

    This class handles the unscheduled downtime information.
    """
    MINOR_EVENT = {'probability': 0.0137,
                   'length': 1,
                   'comment': 'minor event'}
    INTERMEDIATE_EVENT = {'probability': 0.00548,
                          'length': 3,
                          'comment': 'intermediate event'}
    MAJOR_EVENT = {'probability': 0.00137,
                   'length': 7,
                   'comment': 'major event'}
    CATASTROPHIC_EVENT = {'probability': 0.000274,
                          'length': 14,
                          'comment': 'catastrophic event'}

    def __init__(self):
        """Initialize the class.
        """
        # Choose random, repeatable, seed for random number generation.
        # This can be overriden in the 'initialize' step.
        self.seed = 1516231121
        self.downtimes = []
        self.log = logging.getLogger("downtime.UnscheduledDowntime")

    def __call__(self):
        """Return the top downtime.
        """
        try:
            return self.downtimes.pop(0)
        except IndexError:
            return None

    def __len__(self):
        """Return number of scheduled downtimes.

        Returns
        -------
        int
        """
        return len(self.downtimes)

    @property
    def total_downtime(self):
        """Get the total downtime (units=days).

        Returns
        -------
        int
        """
        return sum([x[1] for x in self.downtimes])

    def initialize(self, use_random_seed=False, random_seed=-1, survey_length=7300):
        """Configure the set of unscheduled downtimes.

        This function creates the unscheduled downtimes based on a set of probabilities
        of the downtime type occurance. A default seed is used to produce the same set of
        downtimes, but a randomized seed can be requested.

        The random downtime is calculated using the following probabilities:

        minor event
            remainder of night and next day = 5/365 days e.g. power supply failure
        intermediate
            3 nights = 2/365 days e.g. repair filter mechanism, rotator, hexapod, or shutter
        major event
            7 nights = 1/2*365 days
        catastrophic event
            14 nights = 1/3650 days e.g. replace a raft

        Parameters
        ----------
        use_random_seed : bool, optional
            Flag to set the seed based on the current time. Default is to used fixed seed.
        random_seed : int, optional
            Provide an alternate random seed. Only works when use_random_seed is True.
        survey_length : int, optional
            The length of the survey in days. Default is the length of a 20 year survey.
        """
        if use_random_seed:
            if random_seed == -1:
                self.seed = int(time.time())
            else:
                self.seed = random_seed

        rng = np.random.RandomState(self.seed)

        night = 0
        while night < survey_length:
            prob = rng.random_sample()
            if prob < self.CATASTROPHIC_EVENT['probability']:
                self.downtimes.append((night, self.CATASTROPHIC_EVENT['length'],
                                       self.CATASTROPHIC_EVENT['comment']))
                night += self.CATASTROPHIC_EVENT['length'] + 1
            else:
                # Pick a new random number, and check again.
                prob = rng.random_sample()
                if prob < self.MAJOR_EVENT['probability']:
                    self.downtimes.append((night, self.MAJOR_EVENT['length'],
                                       self.MAJOR_EVENT['comment']))
                    night += self.MAJOR_EVENT['length'] + 1
                else:
                    prob = rng.random_sample()
                    if prob < self.INTERMEDIATE_EVENT['probability']:
                        self.downtimes.append((night, self.INTERMEDIATE_EVENT['length'],
                                       self.INTERMEDIATE_EVENT['comment']))
                        night += self.INTERMEDIATE_EVENT['length'] + 1
                    else:
                        prob = rng.random_sample()
                        if prob < self.MINOR_EVENT['probability']:
                            self.downtimes.append((night, self.MINOR_EVENT['length'],
                                       self.MINOR_EVENT['comment']))
                            night += self.MINOR_EVENT['length'] + 1
                        else:
                            night += 1

        # 15 = WORDY logging level
        self.log.log(15, "Total unscheduled downtime: {} days in {} days.".format(self.total_downtime,
                                                                                  survey_length))
