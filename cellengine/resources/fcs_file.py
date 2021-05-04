from __future__ import annotations
from typing import List
import fcsparser
import pandas

import cellengine as ce
from cellengine.payloads.fcs_file import _FcsFile
from cellengine.resources.plot import Plot
from cellengine.resources.compensation import Compensation


class FcsFile(_FcsFile):
    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None) -> FcsFile:
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_fcs_file(experiment_id=experiment_id, **kwargs)

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
        file = {"upload_file": open(filepath, "rb")}
        return ce.APIClient().upload_fcs_file(experiment_id, file)

    @classmethod
    def create(
        cls,
        experiment_id: str,
        fcs_files: List[str],
        filename: str = None,
        add_file_number: bool = False,
        add_event_number: bool = False,
        pre_subsample_n: int = None,
        pre_subsample_p: float = None,
        seed: int = None,
    ) -> FcsFile:
        """Creates an FCS file by copying, concatenating and/or subsampling
        existing file(s) from this or other experiments.

        This endpoint can be used to import files from other experiments.

        Args:
            experiment_id: ID of the experiment to which the file belongs
            fcs_files: ID of file or list of IDs of files or objects to process.
                If more than one file is provided, they will be concatenated in
                order. To import files from other experiments, pass a list of dicts
                with _id and experimentId properties.
            filename (optional): Rename the uploaded file.
            add_file_number (optional): If
                concatenating files, adds a file number channel to the
                resulting file.
            add_event_number (bool): Add an event number column to the
                exported file. This number corresponds to the index of the event in
                the original file; when concatenating files, the same event number
                will appear more than once.
            pre_subsample_n (int): Randomly subsample the file to contain
                this many events.
            pre_subsample_p (float): Randomly subsample the file to contain
                this percent of events (0 to 1).
            seed (int): Seed for random number generator used for subsampling.
                Use for deterministic (reproducible) subsampling. If omitted, a
                pseudo-random value is used.

        Returns:
            FcsFile
        """

        def _parse_fcs_file_args(args):
            if type(args) is list:
                return args
            else:
                return [args]

        body = {"fcsFiles": _parse_fcs_file_args(fcs_files), "filename": filename}
        optional_params = {
            "addFileNumber": add_file_number,
            "addEventNumber": add_event_number,
            "preSubsampleN": pre_subsample_n,
            "preSubsampleP": pre_subsample_p,
            "seed": seed,
        }
        body.update(
            {key: val for key, val in optional_params.items() if optional_params[key]}
        )
        return ce.APIClient().create_fcs_file(experiment_id, body)

    def update(self):
        """Save changes to this FcsFile to CellEngine."""
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "fcsfiles", self._properties
        )
        self._properties.update(res)

    def delete(self):
        return ce.APIClient().delete_entity(self.experiment_id, "fcsfiles", self._id)

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

        See [`Plot.get`][cellengine.resources.plot.Plot.get] for more information.
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
        """Get the file-internal Compensation.
        """
        file = ce.APIClient().get_fcs_file(self.experiment_id, self._id)
        return Compensation.from_spill_string(file.spill_string)

    @property
    def events(self):
        """A DataFrame containing this file's data.

        This is fetched from the server on-demand the first time that
        this property is accessed.

        To fetch a file with specific parameters (e.g. subsampling, or
        gated to a specific population) see `FcsFile.get_events()`.
        """
        if self._events.empty:
            self.get_events(inplace=True)
            return self._events
        else:
            return self._events

    @events.setter
    def events(self, events):
        self._events = events

    def get_events(self, inplace: bool = False, **kwargs):
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
        """

        fresp = ce.APIClient().download_fcs_file(self.experiment_id, self._id, **kwargs)
        parser = fcsparser.api.FCSParser.from_data(fresp)
        events = pandas.DataFrame(parser.data, columns=parser.channel_names_n)
        if inplace:
            self._events = events
        return events
