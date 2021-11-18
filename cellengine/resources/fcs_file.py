from __future__ import annotations
from cellengine.utils import readonly

from attr import define, field
from typing import Any, Dict, List, Optional, Union

from fcsparser.api import FCSParser
import pandas
from pandas.core.frame import DataFrame

import cellengine as ce
from cellengine.resources.plot import Plot
from cellengine.resources.compensation import Compensation


def check_annotation(_, annotation, values):
    try:
        assert type(values) is list
        assert all([type(val) is dict and "name" and "value" in val for val in values])
    except Exception:
        raise TypeError(
            'Annotations must be a List[Dict[str,str]] with a "name" and a "value" key.'
        )


@define
class FcsFile:
    _id: str = field(on_setattr=readonly)
    experiment_id: str = field(on_setattr=readonly)
    # TODO:
    annotations: Optional[List[Dict[str, str]]] = field(validator=check_annotation)
    crc32c: str = field(on_setattr=readonly)
    event_count: int = field(on_setattr=readonly)
    filename: str
    has_file_internal_comp: bool = field(on_setattr=readonly)
    is_control: bool
    md5: str = field(on_setattr=readonly)
    panel_name: str
    panel: List[Dict[str, Any]]
    size: int = field(on_setattr=readonly)
    compensation: Optional[int] = field(default=None)
    deleted: Optional[bool] = field(default=False)
    header: Optional[str] = field(on_setattr=readonly, default=None)
    sample_name: Optional[str] = field(on_setattr=readonly, default=None)
    _spill_string: Optional[str] = field(default=None)

    def __repr__(self):
        return f"FcsFile(_id='{self._id}', name='{self.name}')"

    @property
    def client(self):
        return ce.APIClient()

    @property
    def path(self):
        return f"experiments/{self.experiment_id}/fcsfiles/{self._id}".rstrip("/None")

    @property
    def name(self):
        """Alias for `filename`."""
        return self.filename

    @name.setter
    def name(self, val):
        self.filename = val

    # @property
    # def annotations(self):
    #     """Return file annotations.
    #     New annotations may be added with file.annotations.append or
    #     redefined by setting file.annotations to a dict with a 'name'
    #     and 'value' key (i.e. {'name': 'plate row', 'value': 'A'}) or
    #     a list of such dicts.
    #     """
    #     return self._annotations

    # @annotations.setter
    # def annotations(self, val):
    #     """Set new annotations.
    #     Warning: This will overwrite current annotations!
    #     """
    #     if type(val) is not dict or "name" and "value" not in val:
    #         raise TypeError('Input must be a dict with a "name" and a "value" item.')
    #     else:
    #         self._annotations = val

    @property
    def channels(self) -> List:
        """Return all channels in the file"""
        return [f["channel"] for f in self.panel]  # type: ignore

    @classmethod
    def upload(cls, experiment_id: str, filepath: str) -> FcsFile:
        """
        Uploads a file. The maximum file size is approximately 2.3 GB.
        Contact us if you need to work with larger files.

        Automatically parses panels and annotations and updates ScaleSets to
        include all channels in the file.

        Args:
            experiment_id: ID of the experiment to which the file belongs
            filepath: The file contents.
        """
        return ce.APIClient().upload_fcs_file(experiment_id, filepath)

    def update(self):
        """Save changes to CellEngine."""
        res = self.client.update(self)
        self.__setstate__(res.__getstate__())  # type: ignore

    def delete(self):
        return self.client.delete_entity(self.experiment_id, "fcsfiles", self._id)

    def plot(
        self,
        x_channel: str,
        y_channel: str,
        plot_type: str,
        z_channel: str = None,
        population_id: str = None,
        **kwargs,
    ) -> Plot:
        """Buid a plot for an FcsFile.

                See [`APIClient.get_plot()`][cellengine.APIClient.get_plot]
                for more information.
        """
        plot = Plot.get(
            experiment_id=self.experiment_id,
            fcs_file_id=self._id,
            plot_type=plot_type,
            x_channel=x_channel,
            y_channel=y_channel,
            z_channel=z_channel,
            population_id=population_id,
            **kwargs,
        )
        return plot

    def get_file_internal_compensation(self) -> Compensation:
        """Get the file-internal Compensation."""
        return Compensation.from_spill_string(self.spill_string)

    @property
    def events(self):
        """A DataFrame containing this file's data.

        This is fetched from the server on-demand the first time that
        this property is accessed.

        To fetch a file with specific parameters (e.g. subsampling, or
        gated to a specific population) see `FcsFile.get_events()`.
        """
        if not hasattr(self, "_events"):
            self._events = DataFrame()
        if self._events.empty:
            self.get_events(inplace=True)
            return self._events
        else:
            return self._events

    @events.setter
    def events(self, events):
        self._events = events

    @property
    def spill_string(self):
        if self._spill_string:
            return self._spill_string
        else:
            ss = self.client.get_spill_string(self.experiment_id, self._id)
            self._spill_string = ss
            return ss

    def get_events(
        self, inplace: bool = False, destination=None, **kwargs
    ) -> Union[DataFrame, None]:
        """
        Fetch a DataFrame containing this file's data.

        Args:
            **kwargs:
                - compensatedQ (bool): If true, applies the compensation
                    specified in compensationId to the exported events.
                    The numerical values will be unchanged, but the
                    file header will contain the compensation as the spill string.
                - compensationId ([int, str]): Required if populationId is
                    specified. Compensation to use for gating.
                - headers (bool): For TSV format only. If true, a header row
                    containing the channel names will be included.
                - original (bool): If true, the returned file will be
                    byte-for-byte identical to the originally uploaded file. If
                    false or unspecified (and compensatedQ is false, populationId
                    is unspecified and all subsampling parameters are unspecified),
                    the returned file will contain essentially the same data as the
                    originally uploaded file, but may not be byte-for-byte
                    identical. For example, the byte ordering of the DATA segment
                    will always be little-endian and any extraneous information
                    appended to the end of the original file will be stripped. This
                    parameter takes precedence over compensatedQ, populationId and
                    the subsampling parameters.
                - populationId (str): If provided, only events from this
                    population will be included in the output file.
                - postSubsampleN (int): Randomly subsample the file to contain
                    this many events after gating.
                - postSubsampleP (float): Randomly subsample the file to contain
                    this percent of events (0 to 1) after gating.
                - preSubsampleN (int): Randomly subsample the file to contain
                    this many events before gating.
                - preSubsampleP (float): Randomly subsample the file to contain
                    this percent of events (0 to 1) before gating.
                - seed: (int): Seed for random number generator used for
                    subsampling. Use for deterministic (reproducible) subsampling.
                    If omitted, a pseudo-random value is used.
                - addEventNumber (bool): Add an event number column to the
                    exported file. When a populationId is specified (when gating),
                    this number corresponds to the index of the event in the
                    original file.

        Returns:
            DataFrame: This file's data, with query parameters applied.
            If inplace=True, it updates the self.events property.
            If destination is a string, saves file to the destination and returns None.
        """

        fresp = self.client.download_fcs_file(self.experiment_id, self._id, **kwargs)
        if destination:
            with open(destination, "wb") as file:
                file.write(fresp)
            return
        parser = FCSParser.from_data(fresp)
        events = pandas.DataFrame(parser.data, columns=parser.channel_names_n)
        if inplace:
            self._events = events
        return events
