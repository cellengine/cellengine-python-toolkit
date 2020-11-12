from typing import List, Dict
from custom_inherit import doc_inherit
import fcsparser
import pandas

import cellengine as ce
from cellengine.payloads.fcs_file import _FcsFile
from cellengine.resources.plot import Plot


class FcsFile(_FcsFile):
    @classmethod
    def get(cls, experiment_id: str, _id: str = None, name: str = None):
        kwargs = {"name": name} if name else {"_id": _id}
        return ce.APIClient().get_fcs_file(experiment_id=experiment_id, **kwargs)

    @classmethod
    def upload(cls, experiment_id: str, filepath: str):
        """
        Uploads a file. The maximum file size is approximately 2.3 GB.
        Contact us if you need to work with larger files.

        Automatically parses panels and annotations and updates ScaleSets to
        include all channels in the file.

        Args:
            experiment_id: ID of the experiment to which the file belongs
            file: The file contents.
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
        pre_subsample_p: int = None,
        seed: int = None,
    ):
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
            add_event_number (optional): Add an event number column to the
                exported file. This number corresponds to the index of the event in
                the original file; when concatenating files, the same event number
                will appear more than once.
            pre_subsample_n (optional): Randomly subsample the file to contain
                this many events.
            pre_subsample_p (optional): Randomly subsample the file to contain
                this percent of events (0 to 1).
            seed (optional): Seed for random number generator used for subsampling.
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

    @doc_inherit(Plot.get)
    def plot(
        self, x_channel: str, y_channel: str, plot_type: str, properties: Dict = None
    ) -> Plot:
        plot = Plot.get(
            self.experiment_id, self._id, x_channel, y_channel, plot_type, properties
        )
        return plot

    @property
    def events(self):
        """A DataFrame containing this file's data.

        This is fetched from the server on-demand the first time that
        this property is accessed.

        To fetch a file with specific parameters (e.g. subsampling, or
        gated to a specific population) see FcsFile.get_events()
        """
        if self._events.empty:
            self.get_events()
            return self._events
        else:
            return self._events

    @events.setter
    def events(self, events):
        self._events = events

    def get_events(self, **params):
        """
        Fetch a DataFrame containing this file's data.

        Args:
            params (Dict): keyword arguments of form:
                compensatedQ (bool): If true, applies the compensation
                    specified in compensationId to the exported events. For TSV
                    format, the numerical values will be the compensated values.
                    For FCS format, the numerical values will be unchanged, but the
                    file header will contain the compensation as the spill string
                    (file-internal compensation).
                compensationId (str): Required if populationId is specified.
                    Compensation to use for gating.
                headers (bool): For TSV format only. If true, a header row
                    containing the channel names will be included.
                original (bool): If true, the returned file will be
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
                populationId (str): If provided, only events from this
                    population will be included in the output file.
                postSubsampleN (int): Randomly subsample the file to contain
                    this many events after gating.
                postSubsampleP (float): Randomly subsample the file to contain
                    this percent of events (0 to 1) after gating.
                preSubsampleN (int): Randomly subsample the file to contain
                    this many events before gating.
                preSubsampleP (float): Randomly subsample the file to contain
                    this percent of events (0 to 1) before gating.
                seed: (float): Seed for random number generator used for
                    subsampling. Use for deterministic (reproducible) subsampling.
                    If omitted, a pseudo-random value is used.
                addEventNumber (bool): Add an event number column to the
                    exported file. When a populationId is specified (when gating),
                    this number corresponds to the index of the event in the
                    original file.

        Returns: None; updates the self.events property.
        """
        fresp = ce.APIClient().download_fcs_file(
            self.experiment_id, self._id, params=params
        )
        parser = fcsparser.api.FCSParser.from_data(fresp)
        self._events = pandas.DataFrame(parser.data, columns=parser.channel_names_n)
