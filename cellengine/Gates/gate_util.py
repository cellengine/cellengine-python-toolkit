import re

from ..fcsfile import FcsFile
from .. import gate  # circular import here
from .. import _helpers


def common_gate_create(
    experiment_id, body, tailored_per_file, fcs_file_id, fcs_file, create_population
):
    """
    <Description>

        Args:
            experiment_id: The ID of the experiment to which to add the gate.
                Use when calling this as a static method; not needed when calling
                from an Experiment object
            name: The name of the gate
            x_channel: The name of the x channel to which the gate applies.
            <Gate Args>
            gid: Group ID of the gate, used for tailoring. If this is not
                specified, then a new Group ID will be created. If you wish you
                create a tailored gate, you must specify the gid of the global
                tailored gate.
            parent_population_id: ID of the parent population. Use ``None`` for
                the "ungated" population. If specified, do not specify
                ``parent_population``.
            parent_population: Name of the parent population. An attempt will
                be made to find the population by name.  If zero or more than
                one population exists with the name, an error will be thrown.
                If specified, do not specify ``parent_population_id``.
            tailored_per_file: Whether or not this gate is tailored per FCS file.
            fcs_file_id: ID of FCS file, if tailored per file. Use ``None`` for
                the global gate in a tailored gate group. If specified, do not
                specify ``fcs_file``.
            fcs_file: Name of FCS file, if tailored per file. An attempt will be made
                to find the file by name. If zero or more than one file exists with
                the name, an error will be thrown. Looking up files by name is
                slower than using the ID, as this requires additional requests
                to the server. If specified, do not specify ``fcs_file_id``.
            locked: Prevents modification of the gate via the web interface.
            create_population: Automatically create corresponding population.

        Returns:
            <Returns>

        Example:
            <Example>
    """
    body = parse_fcs_file_args(
        experiment_id, body, tailored_per_file, fcs_file_id, fcs_file
    )

    body = _helpers.convert_dict(body, "snake_to_camel")
    res = _helpers.base_create(
        gate.Gate,
        url="experiments/{0}/gates".format(experiment_id),
        expected_status=201,
        json=body,
        params={"createPopulation": create_population},
    )
    return res


def parse_fcs_file_args(experiment_id, body, tailored_per_file, fcs_file_id, fcs_file):
    """Find the fcs file ID if 'tailored_per_file' and either 'fcs_file' or
    'fcs_file_id' are specified."""
    if fcs_file is not None and fcs_file_id is not None:
        raise ValueError("Please specify only 'fcs_file' or 'fcs_file_id'.")
    if fcs_file is not None and tailored_per_file is True:  # lookup by name
        _file = get_fcsfile(experiment_id, name=fcs_file)
        fcs_file_id = _file._id
    body["tailoredPerFile"] = tailored_per_file
    body["fcsFileId"] = fcs_file_id
    return body


def get_fcsfile(experiment_id, _id=None, name=None):
    if _id:
        content = _helpers.base_get(
            "experiments/{0}/fcsfiles/{1}".format(experiment_id, _id)
        )
        content = FcsFile(properties=content)
    else:
        content = _helpers.load_fcsfile_by_name(experiment_id, name)
    return content


def create_gates(experiment_id=None, gates=None, create_all_populations=True):
    """Create multiple gates.

    Args:
        experiment_id (optional): The experiment to which all gates will be added.
            If ``experiment_id`` is specified, all gates will be created on that
            experiment. If not specified, each gate object must have the
            ``experiment_id`` key specifed. This allows for creation of multiple
            gates on different experiments.
        gates (list of dicts): A list of dicts with the keys:
            experiment_id (optional): ``str``: The experiment to which each gate
                will be added.  name: ``str``: Name of the gate.
            type: ``str``: Gate type, with casing like  "RectangleGate".
            gid (optional): ``str``: Group ID of the gate.
            x_channel: ``str``: X channel to which the gate applies.
            y_channel: ``str``: Y channel to which gate applies (for 3D gates).
            parent_population_id (optional): ``str``: ID of the parent population.
            model: ``dict``: The geometric description of the gate, with keys:
                locked: ``bool``: If true, the gate cannot be moved in the Web UI.
                label: ``str``: X, Y coordinate of the gate label. (Not
                    used for compound gates.
                <gate geometry>: ``dict``: Dict of keys and values
                    corresponding to gate geometries. Try
                    ``help(cellengine.Gate.<Gate Type>)``.
            fcs_file_id (optional): ``str``: ID of FCS file, if tailored per file. Use
                ``None`` for the global gate in the tailored gate group.
            tailored_per_file (optional): ``bool``: Whether this gate is tailored per FCS file.
            names (optional): ``list(str)``: For compound gates, a list of gate names.
            create_population (optional): Whether to create populations for each gate.
        create_populations: Whether to create populations for all gates. If set
        to False, ``create_population`` may be specified for each gate.

    Returns:
        A list of created Gate objects.
    """
    prepared_gates = []
    for g in gates:
        g.update({"_id": _helpers.generate_id()})
        if "gid" not in g.keys():
            g.update({"gid": _helpers.generate_id()})
        prepared_gates.append(g)

    new_gates = []
    for each_gate in prepared_gates:
        if create_all_populations is False:
            create_populations = each_gate.get("create_population", False)
        else:
            create_populations = create_all_populations
        new_gate = common_gate_create(
            experiment_id=each_gate.get("experiment_id", experiment_id),
            body=each_gate,
            tailored_per_file=each_gate.get("tailored_per_file", False),
            fcs_file_id=each_gate.get("fcs_file_id", None),
            fcs_file=each_gate.get("fcs_file", None),
            create_population=create_populations,
        )
        new_gates.append(new_gate)

    return new_gates


def delete_gates(experiment_id, _id=None, gid=None, exclude=None):
    """
    Deletes a gate or a tailored gate family.

    Works for compound gates if you specify the top-level gid. Specifying
    the gid of a sector (i.e. one listed in model.gids) will result in no
    gates being deleted.  If gateId is specified, only that gate will be
    deleted, regardless of the other parameters specified. May be called as
    a static method from cellengine.Gate or from an Experiment instance.

    Args:
        experimentId: ID of experiment.
        _id: ID of gate family.
        gateId: ID of gate.
        exclude: Gate ID to exclude from deletion.

    Examples:
        cellengine.Gate.delete_gate(experiment_id, gid = [gate family ID])
        experiment.delete_gate(_id = [gate ID])

    """
    if (_id and gid) or (not _id and not gid):
        raise ValueError("Either the gid or the gateId must be specified")
    if _id:
        url = "experiments/{0}/gates/{1}".format(experiment_id, _id)
    elif gid:
        url = "experiments/{0}/gates?gid={1}".format(experiment_id, gid)
        if exclude:
            url = "{0}%exclude={1}".format(url, exclude)

    _helpers.base_delete(url)


def gate_style(prnt_doc, child_doc):
    desc = child_doc[: child_doc.index("Args")].strip()
    args = child_doc[child_doc.index("Args") + 5 : child_doc.index("Returns")].strip()
    args = re.sub("\n", "\n    ", args)
    returns = child_doc[
        child_doc.index("Returns") + 10 : child_doc.index("Example")
    ].strip()
    example = child_doc[child_doc.index("Example") + 10 :].strip()
    keys = ["<Description>", "<Gate Args>", "<Returns>", "<Example>"]
    sections = [desc, args, returns, example]
    docs = prnt_doc
    for key, section in zip(keys, sections):
        docs = docs.replace(key, section)
    return docs
