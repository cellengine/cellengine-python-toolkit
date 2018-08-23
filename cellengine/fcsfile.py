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
import fcsparser

class FcsFile(object):
    """A class representing a CellEngine FCS file.
    """

    def __init__(self, params):
        self._id = params["_id"]
        self.filename = params["filename"]
        self.experiment_id = params["experimentId"]
        self.annotations = params["annotations"]
        self.panel = params["panel"]
        self.panel_name = params["panelName"]
        self.event_count = params["eventCount"]
        self.is_control = params["isControl"]
        self.header = params["header"]
        self.sample_name = params["sampleName"]
        self.spill_string = params["spillString"]
        self.has_file_internal_comp = params["hasFileInternalComp"]
        self.md5 = params["md5"]
        self.crc32c = params["crc32c"]
        self.size = params["size"]
        if "compensation" in params:
            self.compensation = params["compensation"]
        else:
            self.compensation = None

        if "data" in params:
            self.data = params["data"]
        else:
            self.data = {}

        self._events = None

    @property
    def events(self):
        """A DataFrame containing this file's data. Note that this is fetched
        from the server on-demand the first time that this property is accessed.
        """
        if self._events is None:
            # TODO s
            fresp = s.get(f"https://cellengine.com/api/v1/experiments/{self.experiment_id}/fcsfiles/{self._id}.fcs")
            # We want the columns to be $PnN instead of fcsparser's default
            # $PnS. That's an option if reading from disk, but not from this
            # semi-internal from_data API.
            parser = fcsparser.api.FCSParser.from_data(fresp.content)
            columns = parser.channel_names_n
            self._events = pandas.DataFrame(parser.data, columns=columns)

        return self._events
