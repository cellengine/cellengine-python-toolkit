# Copyright 2018 Primity Bio
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pandas
import numpy

class Compensation(object):
    """A class representing a CellEngine compensation matrix. Can be applied to
    FCS files to compensate them.
    """

    def __init__(self, params):
        self._id = params["_id"]
        self.experiment_id = params["experimentId"]
        self.name = params["name"]
        self.channels = channels = params["channels"]
        N = len(self.channels)
        self.dataframe = pandas.DataFrame(
            data=numpy.array(params["spillMatrix"]).reshape((N, N)),
            columns=channels,
            index=channels
        )

    def apply(self, file, inplace=True):
        """Compensates the file's data.

        :type parser: :class:`cellengine.FcsFile`
        :param parser: The FCS file to compensate.

        :type inplace: bool
        :param inplace: Compensate the file's data in-place.

        :returns: If :attr:`inplace` is True, nothing, else a DataFrame.
        """
        data = file.events

        # spill -> comp by inverting
        inverted = numpy.linalg.inv(self.dataframe)

        # Calculate matrix product for channels matching between file and comp
        comped = data[self.channels].dot(inverted)
        comped.columns = self.channels

        data.update(comped)

        if inplace:
            file._events = data
        else:
            return data

    def _repr_html_(self):
        return self.dataframe._repr_html_()
