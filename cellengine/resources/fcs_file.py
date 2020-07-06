from typing import List, Dict
from custom_inherit import doc_inherit

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

        The authenticated user must have write-access to the experiment.

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
        filename: str,
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

    def update(self, inplace=True):
        """Save changes to this FcsFile to CellEngine.

        Args:
            inplace (bool): Update this entity or return a new one.

        Returns:
            FcsFile or None: If inplace is True, returns a new FcsFile.
            Otherwise, updates the current entity.
            """
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "fcsfiles", self._properties
        )
        if inplace:
            self._properties.update(res)
        else:
            return self.__class__(res)

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
        """A DataFrame containing this file's data. This is fetched
        from the server on-demand the first time that this property is accessed.
        """
        if self._events is None:
            fresp = ce.APIClient().get_fcs_file_events(self.experiment_id, self._id)
            parser = fcsparser.api.FCSParser.from_data(fresp.content)
            self._events = pandas.DataFrame(parser.data, columns=parser.channel_names_n)
        return self._events

    @events.setter
    def events(self, val):
        self.__dict__["_events"] = val
