import string
import re
import math

DICT_TYPE = type({})

class LatencyDict(dict):
    """Latency dictionary"""

    def __init__(self, d):
        self.d = d

    def __str__(self):
        """String represenation aka ascii histogram"""

        return ''.join(self.dict_to_string(self.d))

    def dict_to_string(self, d, level="", res=None, suffix=", ", ljust=None):
        """Weird routine from couchbase testrunner"""

        res = res or []
        scalars = []
        complex = []

        for key in d.keys():
            if type(d[key]) == DICT_TYPE:
                complex.append(key)
            else:
                scalars.append(key)
        scalars.sort()
        complex.sort()

        # Special case for histogram output.
        histo_max = 0
        histo_sum = 0
        if scalars and not complex:
            for key in scalars:
                d[key] = float(d[key])
                v = d[key]
                histo_max = max(v, histo_max)
                histo_sum = histo_sum + v

        histo_cur = 0 # Running total for histogram output.
        for key in scalars:
            try:
                k = re.sub("0*$", "", "%.7f" % (float(key)))
            except:
                k = str(key)
            if ljust:
                k = string.ljust(k, ljust)
            x = d[key]
            if histo_max:
                histo_cur = histo_cur + x
            v = str(x)
            if histo_max:
                v = string.rjust(v, 8)
                v += " "
                v += string.rjust("{0:.1%}".format(histo_cur / float(histo_sum)), 8)
                v += " "
                v += ("*" * int(math.ceil(50.0 * d[key] / histo_max)))

            res.append(level + k + ": " + v + suffix)

        # Recurse for nested, dictionary values.
        if complex:
            res.append("\n")
        for key in complex:
            res.append(level + str(key) + ":\n")
            self.dict_to_string(d[key], level + "  ", res, "\n", 9)

        return res
