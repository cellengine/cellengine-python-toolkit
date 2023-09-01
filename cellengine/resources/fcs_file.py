from __future__ import annotations
import io
import json

from cellengine.utils.parse_fcs_file import parse_fcs_file
from cellengine.utils.helpers import (
    is_valid_id,
    timestamp_to_datetime,
    datetime_to_timestamp,
)
from typing import Any, Dict, List, Optional, Union, overload, cast

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from pandas.core.frame import DataFrame
from io import BytesIO
import flowio
from datetime import datetime

import cellengine as ce
from cellengine.resources.plot import Plot
from cellengine.resources.compensation import Compensation, FileCompensations


Annotations = TypedDict("Annotations", {"name": str, "value": str})
Channel = TypedDict(
    "Channel", {"channel": str, "reagent": Union[str, None], "index": int}
)


class FcsFile:
    """A class representing a CellEngine FCS file."""

    def __init__(self, properties: Dict[str, Any]):
        self._properties = properties
        self._changes = set()
        # Used for caching events
        self._events_kwargs = {}
        self._events = DataFrame()

    @property
    def _id(self) -> str:
        return self._properties["_id"]

    @property
    def id(self) -> str:
        """Alias for ``_id``."""
        return self._properties["_id"]

    @property
    def experiment_id(self) -> str:
        return self._properties["experimentId"]

    @property
    def filename(self) -> str:
        return self._properties["filename"]

    @filename.setter
    def filename(self, filename):
        self._properties["filename"] = filename
        self._changes.add("filename")

    @property
    def name(self) -> str:
        """Alias for `filename`."""
        return self.filename

    @name.setter
    def name(self, val: str):
        self.filename = val

    @property
    def md5(self) -> str:
        return self._properties["md5"]

    @property
    def crc32c(self) -> str:
        return self._properties["crc32c"]

    @property
    def size(self) -> int:
        return self._properties["size"]

    @property
    def gates_locked(self) -> bool:
        return self._properties["gatesLocked"]

    @gates_locked.setter
    def gates_locked(self, val: bool):
        self._properties["gatesLocked"] = val
        self._changes.add("gatesLocked")

    @property
    def deleted(self) -> Union[datetime, None]:
        deleted = self._properties["deleted"]
        return timestamp_to_datetime(deleted) if deleted else None

    @deleted.setter
    def deleted(self, deleted: Union[datetime, None]):
        self._properties["deleted"] = (
            datetime_to_timestamp(deleted) if deleted else None
        )
        self._changes.add("deleted")

    @property
    def is_control(self) -> bool:
        return self._properties["isControl"]

    @property
    def panel_name(self) -> str:
        return self._properties["panelName"]

    @property
    def panel(self) -> List[Channel]:
        return self._properties["panel"]

    @property
    def compensation(self) -> Union[FileCompensations, None]:
        return self._properties["compensation"]

    @property
    def annotations(self) -> List[Annotations]:
        return self._properties["annotations"]

    @property
    def event_count(self) -> int:
        return self._properties["eventCount"]

    @property
    def has_file_internal_comp(self) -> bool:
        return self._properties["hasFileInternalComp"]

    @property
    def spill_string(self) -> str:
        """Note: this property may be fetched lazily."""
        if "spillString" not in self._properties and self.has_file_internal_comp:
            base_url = ce.APIClient().base_url
            self._properties["spillString"] = ce.APIClient()._get(
                f"{base_url}/api/v1/experiments/{self.experiment_id}/fcsfiles/{self._id}"  # noqa: E501
            )["spillString"]
        return self._properties["spillString"]

    @property
    def header(self) -> Dict[str, str]:
        """Note: this property may be fetched lazily."""
        if "header" not in self._properties:
            base_url = ce.APIClient().base_url
            self._properties["header"] = ce.APIClient()._get(
                f"{base_url}/api/v1/experiments/{self.experiment_id}/fcsfiles/{self._id}"  # noqa: E501
            )["header"]
        return json.loads(self._properties["header"])

    @property
    def data(self) -> Dict[str, Any]:
        return self._properties["data"]

    @property
    def sample_name(self) -> Optional[str]:
        return self._properties["sampleName"]

    def __repr__(self):
        return f"FcsFile(_id='{self._id}', name='{self.filename}')"

    @property
    def channels(self) -> List[str]:
        """Return all channels in the file"""
        return [f["channel"] for f in self.panel]

    def channel_for_reagent(self, reagent: str) -> Union[str, None]:
        """
        Returns the channel name (`$PnN`) for the given reagent (`$PnS). Returns
        `None` if the channel isn't found.
        """
        c = [x for x in self.panel if x["reagent"] == reagent]
        # TODO reagents are not necessarily unique. This needs to throw if so
        return c[0]["channel"] if c else None

    @classmethod
    def get(
        cls, experiment_id: str, _id: Optional[str] = None, name: Optional[str] = None
    ) -> FcsFile:
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
    def create_from_dataframe(
        cls,
        experiment_id: str,
        filename: str,
        df: DataFrame,
        reagents: Optional[List[str]] = None,
        headers: Dict[str, str] = {},
    ) -> FcsFile:
        """Creates an FCS file from a DataFrame and uploads it CellEngine.

        Channel names (`$PnN` values such as "FITC-A" or "530/30-A") are read
        from the DataFrame column names.

        Reagent names (`$PnS` values such as "CD3") are optional and are read
        from the 2nd-level index of the DataFrame if present, or can be provided
        in a list in the same order as the channels via the `reagents` argument.

        Additional header keys can be provided via `headers`. In particular, it
        can be useful to set `$PnD` values, which CellEngine uses to set the
        initial display scaling:

        * For linear scales, set `"$PnD": "Linear,<min>,<max>"` (e.g.
          `"Linear,-200,50000"` for a linear scale ranging from -200 to 50,000).
        * For logarithmic scales, set `"$PnD": "Logarithmic,<decades>,<min>"`
          (e.g. `"Logarithmic,4,0.1"` for a logarithmic scale ranging from 0.1
          to 1000).
        * For arcsinh scales, leave `"$PnD"` unset. Aside from several
          heuristics, CellEngine will usually default to arcsinh with a max
          equal to the `"$PnR"` value.

        FCS files created with this method always use float32 encoding. For
        efficiency, consider using float32 arrays upstream when generating the
        FCS file values.

        Examples:
            With reagents specified in a multi-level index:
            ```py
            df = pandas.DataFrame(
                np.random.randn(6,3),
                columns=[["Ax488-A", "PE-A", "Cluster ID"],
                         ["CD3", "CD4", None]],
                dtype="float32"
            )
            FcsFile.create_from_dataframe(
                experiment_id,
                "myfile.fcs",
                df,
                headers={
                    "P3D": "Linear,0,20"
                }
            )
            ```

            With reagents specified in the `reagents` argument:
            ```py
            df = pandas.DataFrame(
                np.random.randn(6,3),
                columns=["Ax488-A", "PE-A", "Cluster ID"],
                dtype="float32"
            )
            FcsFile.create_from_dataframe(
                experiment_id,
                "myfile.fcs",
                df,
                reagents=["CD3", "CD4", None],
                headers={
                    "P3D": "Linear,0,20"
                }
            )
            ```

            Factorize categorical data into numbers for encoding as FCS:
            ```py
            df = pandas.DataFrame(
                [[1.0, "T cell", 1],
                 [2.0, "T cell", 2],
                 [3.0, "B cell", 3],
                 [4.0, "T cell", 4]],
                columns=["Ax488-A", "Cell Type", "Cluster ID"]
            )
            df["Cell Type"], cell_type_index = pandas.factorize(df["Cell Type"])
            created = FcsFile.create_from_dataframe(
                blank_experiment._id,
                "myfile.fcs",
                df,
                headers={
                    "$P2D": "Linear,0,10",
                    "$P3D": "Linear,0,10"
                }
            )
            ```
        Returns:
            The created FCS file.
        """

        if "$COM" not in headers:
            headers[
                "$COM"
            ] = f"Created by the CellEngine Python Toolkit v{ce.__version__}"

        if df.columns.nlevels > 1:
            channels = df.columns.get_level_values(0).tolist()
            if reagents is None:
                reagents = df.columns.get_level_values(1).tolist()
        else:
            channels = df.columns

        bytes = io.BytesIO()
        writer = io.BufferedRandom(
            cast(io.RawIOBase, bytes),
            buffer_size=df.memory_usage(index=False).sum() + 16536,
        )
        flowio.create_fcs(
            file_handle=writer,
            event_data=df.to_numpy().flatten(),
            channel_names=channels,
            opt_channel_names=reagents,
            metadata_dict=headers,
        )

        writer.flush()  # not sure if this is necessary

        return ce.APIClient().upload_fcs_file(experiment_id, bytes, filename)

    @classmethod
    def create(
        cls,
        experiment_id: str,
        fcs_files: Optional[Union[str, List[str], Dict[str, str]]] = None,
        filename: Optional[str] = None,
        add_file_number: Optional[bool] = False,
        add_event_number: Optional[bool] = False,
        pre_subsample_n: Optional[int] = None,
        pre_subsample_p: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> FcsFile:
        """Creates an FCS file by copying, concatenating and/or subsampling
        existing file(s) from this or other experiments, or by importing from an
        S3-compatible service.

        When concatenating and subsampling at the same time, subsampling is
        applied to each file before concatenating.

        If `addFileNumber` is true, a file number column (channel) will be added
        to the output file indicating which file each event (cell) came from.
        The values in this column have a uniform random spread (±0.25 of the
        integer value) to aid visualization. While this column can be useful for
        analysis, it will cause the experiment to have FCS files with different
        panels unless all FCS files that have not been concatenated are deleted.

        During concatenation, any FCS header parameters that do not match
        between files will be removed, with some exceptions:

        - `$BTIM` (clock time at beginning of acquisition) and `$DATE` will be
          set to the earliest value among the input files.
        - `$ETIM` (clock time at end of acquisition) will be set to the latest
          value among the input files.
        - `$PnR` (range for parameter n) will be set to the highest value among
          the input files.

        All channels present in the first FCS file in the fcsFiles parameter
        must also be present in the other FCS files.

        When importing from an S3-compatible service, be aware of the following:

        - Only a single file can be imported at a time.
        - The host property must include the bucket and region as applicable.
          For example, for AWS, this would look like
          "mybucket.s3.us-east-2.amazonaws.com".
        - The path property must specify the full path to the object, e.g.
          "/Study001/Specimen01.fcs".
        - Importing private S3 objects requires an accessKey and a secretKey for
          a user with appropriate permissions. For AWS, GetObject is required.
        - Importing objects may incur fees from the S3 service provider.

        Args:
            experiment_id: ID of the experiment to which the file belongs
            fcs_files: ID of file or list of IDs of files or objects to process.
                If more than one file is provided, they will be concatenated in
                order. To import files from other experiments, pass a list of
                dicts with `_id` and `experimentId` properties. To import a file
                from an S3-compatible service, provide a Dict with keys `"host"`
                and `"path"`; if the S3 object is private, additionally provide
                `"access_key"` and `"secret_key"`.
            filename: Rename the uploaded file.
            add_file_number: If concatenating files, adds a file number channel
                to the resulting file.
            add_event_number: Add an event number column to the exported file.
                This number corresponds to the index of the event in the
                original file; when concatenating files, the same event number
                will appear more than once.
            pre_subsample_n: Randomly subsample the file to contain this many
                events.
            pre_subsample_p: Randomly subsample the file to contain this percent
                of events (0 to 1).
            seed: Seed for random number generator used for subsampling. Use for
                deterministic (reproducible) subsampling. If omitted, a
                pseudo-random value is used.

        Returns:
            FcsFile
        """

        def _parse_fcs_file_args(args):
            if type(args) is list and all(is_valid_id(arg) for arg in args):
                return args
            elif type(args) is dict:
                if {"host", "path"} <= args.keys():
                    return [
                        {
                            "host": args["host"],
                            "path": args["path"],
                            "accessKey": args.get("access_key"),
                            "secretKey": args.get("secret_key"),
                        }
                    ]
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

    def update(self) -> None:
        """Save changes to this FcsFile to CellEngine."""
        update_properties = {key: self._properties[key] for key in self._changes}
        res = ce.APIClient().update_entity(
            self.experiment_id, self._id, "fcsfiles", update_properties
        )
        self._properties = res
        self._changes = set()

    def delete(self) -> None:
        return ce.APIClient().delete_entity(self.experiment_id, "fcsfiles", self._id)

    def plot(
        self,
        plot_type: str,
        x_channel: str,
        y_channel: str,
        z_channel: Optional[str] = None,
        population_id: Optional[str] = None,
        compensation: Union[str, Literal[-1], Literal[0]] = 0,
        **kwargs,
    ) -> Plot:
        """Build a plot for an FcsFile.

        See [`Plot.get()`][cellengine.Plot.get] for more information.
        """
        plot = Plot.get(
            experiment_id=self.experiment_id,
            fcs_file_id=self._id,
            plot_type=plot_type,
            x_channel=x_channel,
            y_channel=y_channel,
            z_channel=z_channel,
            population_id=population_id,
            compensation=compensation,
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
        """A DataFrame containing this file's events (typically cells).

        This is the last result from `FcsFile.get_events(inplace=True)`. If that
        method has not been called, a DataFrame will be fetched with all events
        (ungated, no compensation, no subsampling). To fetch events with
        subsampling, compensation and/or gating to a specific population, use
        `FcsFile.get_events()`.
        """
        if self._events.empty:
            self.get_events(inplace=True)
        return self._events

    @overload
    def get_events(
        self,
        inplace: Optional[bool] = ...,
        destination: None = ...,
        **kwargs: Any,
    ) -> DataFrame:
        ...

    @overload
    def get_events(
        self,
        inplace: Optional[bool] = ...,
        destination: str = ...,
        **kwargs: Any,
    ) -> None:
        ...

    def get_events(
        self,
        inplace: Optional[bool] = False,
        destination: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[DataFrame, None]:
        """
        Fetch a DataFrame containing this file's data.

        The returned DataFrame uses the channel names (`$PnN` values) for column
        names because, unlike reagent names (`$PnS`), they are required and must
        be unique. To find the `$PnN` value for a given reagent name (`$PnS`),
        use [`fcs_file.channel_for_reagent(reagent)`][cellengine.resources.fcs_file.FcsFile.channel_for_reagent].

        Args:
            inplace: bool
            **kwargs:
                - compensatedQ (bool): If `True`, applies the compensation
                    specified in compensationId to the exported events.
                    The numerical values will be unchanged, but the
                    file header will contain the compensation as the spill string.
                - compensationId ([int, str]): Required if populationId is
                    specified. Compensation to use for gating.
                - headers (bool): For TSV format only. If `True`, a header row
                    containing the channel names will be included.
                - original (bool): If `True`, the returned file will be
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

                    The Python toolkit uses the FlowIO library, which cannot
                    parse as many FCS files as CellEngine can. Setting this
                    parameter to `True` can cause parsing errors.

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
        """  # noqa

        if inplace is True:
            self._events_kwargs = kwargs

        file = ce.APIClient().download_fcs_file(self.experiment_id, self._id, **kwargs)

        if destination:
            with open(destination, "wb") as loc:
                loc.write(file)
        else:
            df = parse_fcs_file(BytesIO(file))
            if inplace:
                self._events = df
            return df
