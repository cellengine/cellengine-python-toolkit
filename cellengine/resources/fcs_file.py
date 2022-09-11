from __future__ import annotations
from cellengine.utils.helpers import is_valid_id
from cellengine.utils.parse_fcs_file import parse_fcs_file
from cellengine.utils.dataclass_mixin import DataClassMixin, ReadOnly
from dataclasses import dataclass, field
from dataclasses_json import config
from typing import Any, Dict, List, Optional, Union
from pandas.core.frame import DataFrame

import cellengine as ce
from cellengine.resources.plot import Plot
from cellengine.resources.compensation import Compensation


@dataclass
class FcsFile(DataClassMixin):
    filename: str
    gates_locked: str
    panel_name: str
    deleted: Optional[bool]
    panel: List[Dict[str, Any]]
    _id: str = field(
        metadata=config(field_name="_id"), default=ReadOnly()
    )  # type: ignore
    compensation: Optional[int] = None
    is_control: Optional[bool] = None
    _annotations: Optional[List[str]] = field(
        metadata=config(field_name="annotations"), default=None
    )
    crc32c: str = field(default=ReadOnly())  # type: ignore
    event_count: int = field(default=ReadOnly())  # type: ignore
    experiment_id: str = field(default=ReadOnly())  # type: ignore
    has_file_internal_comp: bool = field(default=ReadOnly())  # type: ignore
    header: Optional[str] = field(default=ReadOnly(optional=True))  # type: ignore
    md5: str = field(default=ReadOnly())  # type: ignore
    sample_name: Optional[str] = field(default=ReadOnly(optional=True))  # type: ignore
    size: int = field(default=ReadOnly())  # type: ignore
    _spill_string: Optional[str] = field(
        metadata=config(field_name="spillString"),
        default=None,
    )

    def __repr__(self):
        return f"FcsFile(_id='{self._id}', name='{self.name}')"

    def __post_init__(self):
        self._events_kwargs = {}

    @property
    def name(self):
        """Alias for `filename`."""
        return self.filename

    @name.setter
    def name(self, val):
        self.filename = val

    @property
    def annotations(self):
        """Return file annotations.
        New annotations may be added with file.annotations.append or
        redefined by setting file.annotations to a dict with a 'name'
        and 'value' key (i.e. {'name': 'plate row', 'value': 'A'}) or
        a list of such dicts.
        """
        return self._annotations

    @annotations.setter
    def annotations(self, val):
        """Set new annotations.
        Warning: This will overwrite current annotations!
        """
        if type(val) is not dict or "name" and "value" not in val:
            raise TypeError('Input must be a dict with a "name" and a "value" item.')
        else:
            self._annotations = val

    @property
    def channels(self) -> List:
        """Return all channels in the file"""
        return [f["channel"] for f in self.panel]  # type: ignore

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
        return ce.APIClient().upload_fcs_file(experiment_id, filepath)

    @classmethod
    def create(
        cls,
        experiment_id: str,
        fcs_files: Union[str, List[str], Dict[str, str]],
        filename: str = None,
        add_file_number: bool = False,
        add_event_number: bool = False,
        pre_subsample_n: int = None,
        pre_subsample_p: float = None,
        seed: int = None,
    ) -> FcsFile:
        """Creates an FCS file by copying, concatenating and/or
        subsampling existing file(s) from this or other experiments, or by
        importing from an S3-compatible service. This endpoint can be used to
        import files from other experiments.

        When concatenating and subsampling at the same time, subsampling is
        applied to each file before concatenating.

        If addFileNumber is true, a file number column (channel) will be added to the
        output file indicating which file each event (cell) came from. The values in
        this column have a uniform random spread (±0.25 of the integer value) to ease
        visualization. While this column can be useful for analysis, it will cause the
        experiment to have FCS files with different panels unless all FCS files that
        have not been concatenated are deleted.

        During concatenation, any FCS header parameters that do not match
        between files will be removed, with some exceptions:

            - $BTIM (clock time at beginning of acquisition) and $DATE will be
            set to the earliest value among the input files.
            - $ETIM (clock time at end of acquisition) will be set to the latest value
            among the input files.
            - $PnR (range for parameter n) will be set to
            the highest value among the input files.

        All channels present in the first FCS file in the fcsFiles parameter
        must also be present in the other FCS files.

        When importing from an S3-compatible service, be aware of the
        following:

            - Only a single file can be imported at a time.
            - The host property must include the bucket and region as
              applicable. For example, for AWS, this would look like
              mybucket.s3.us-east-2.amazonaws.com.
            - The path property must specify the full path to the object, e.g.
              /Study001/Specimen01.fcs.
            - Importing private S3 objects requires an accessKey and a
              secretKey for a user with appropriate permissions. For AWS,
              GetObject is required.
            - Importing objects may incur fees from the S3 service provider.

        Args:
            experiment_id: ID of the experiment to which the file belongs
            fcs_files: ID of file or list of IDs of files or objects to process.
                If more than one file is provided, they will be concatenated in
                order. To import files from other experiments, pass a list of dicts
                with _id and experimentId properties. To import a file from an
                S3-compatible service, provide a Dict with keys "host" and
                "path"; if the S3 object is private, additionally provide
                "access_key" and "secret_key".
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
            if type(args) is list and all(is_valid_id(arg) for arg in args):
                return args
            elif type(args) is dict:
                if {"host", "path"} <= args.keys():
                    return [args]
                if {"_id", "experiment_id"} <= args.keys():
                    return [args]
            elif type(args) is str and is_valid_id(args):
                return [args]
            else:
                raise ValueError("Invalid parameters for 'fcs_file'.")

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
            self.experiment_id, self._id, "fcsfiles", self.to_dict()
        )
        self.__dict__.update(FcsFile.from_dict(res).__dict__)

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
        """Build a plot for an FcsFile.

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
        if not self.has_file_internal_comp:
            raise ValueError(
                f"FCS File '{self._id}' does not have an internal compensation."
            )
        return Compensation.from_spill_string(self.spill_string)  # type: ignore

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
        if not self._spill_string and self.has_file_internal_comp:
            self._spill_string = ce.APIClient().get_fcs_file(
                self.experiment_id, self._id, as_dict=True
            )["spillString"]
        return self._spill_string

    def get_events(
        self, inplace: bool = False, destination=None, **kwargs: Any
    ) -> Union[DataFrame, None]:
        """
        Fetch a DataFrame containing this file's data.

        Args:
            inplace: bool
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

        if inplace is True:
            self._events_kwargs = kwargs

        fresp = parse_fcs_file(
            ce.APIClient().download_fcs_file(self.experiment_id, self._id, **kwargs),
            destination=destination,
        )
        if inplace:
            self.events = fresp
        return fresp
