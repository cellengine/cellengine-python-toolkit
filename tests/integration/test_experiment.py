import json
import uuid
import pytest
from typing import Iterator, Union, List, Dict
from datetime import datetime
from pandas import DataFrame

from cellengine import FILE_INTERNAL, PER_FILE, UNCOMPENSATED
from cellengine.resources.attachment import Attachment
from cellengine.resources.compensation import Compensation
from cellengine.resources.experiment import Experiment
from cellengine.resources.fcs_file import FcsFile
from cellengine.resources.gate import Gate
from cellengine.resources.population import Population


@pytest.fixture()
def full_experiment(
    blank_experiment: Experiment,
) -> Iterator[
    Dict[str, Union[Experiment, Compensation, List[FcsFile], Attachment, Gate]]
]:
    comp = blank_experiment.create_compensation(
        name="test_comp",
        channels=["Blue530-A", "Vio450-A"],
        spill_matrix=[1, 0.02, 0, 1],
    )

    file1 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )

    file2 = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A2_A02_MeOHperm(DL350neg).fcs"
    )

    att = blank_experiment.upload_attachment("tests/data/text.txt")

    gate = blank_experiment.create_rectangle_gate(
        name="test gate",
        x_channel="FSC-A",
        y_channel="SSC-A",
        x1=10,
        x2=100000,
        y1=10,
        y2=100000,
        create_population=False,
    )

    pop = blank_experiment.create_population(
        {
            "name": "Pop 1",
            "gates": json.dumps({"$and": [gate.gid]}),
            "parent_id": None,
            "terminal_gate_gid": gate.gid,
        }
    )

    yield {
        "experiment": blank_experiment,
        "compensation": comp,
        "fcs_files": [file1, file2],
        "attachment": att,
        "gate": gate,
        "population": pop,
    }


# Begin tests


def test_experiment_get(blank_experiment):
    expt_by_id = Experiment.get(blank_experiment._id)
    assert type(expt_by_id) is Experiment

    expt_by_name = Experiment.get(name=blank_experiment.name)
    assert type(expt_by_name) is Experiment


def test_experiment_create():
    experiment_name = uuid.uuid4().hex
    exp = Experiment.create(experiment_name)
    assert type(exp._id) is str
    assert exp.name == experiment_name
    assert type(exp.created) is datetime
    assert type(exp.deep_updated) is datetime
    assert exp.deleted is None
    assert type(exp.uploader.get("_id")) is str
    assert type(exp.primary_researcher.get("_id")) is str
    assert exp.path == []
    assert exp.data == {}
    assert exp.data_order == []
    assert exp.locked == False
    assert exp.retention_policy == {"history": []}
    assert exp.clone_source_experiment is None
    assert exp.revision_source_experiment is None
    assert exp.analysis_source_experiment is None
    assert exp.analysis_task is None
    assert exp.revisions == []
    assert exp.per_file_compensations_enabled == False
    assert exp.tags == []
    assert exp.sorting_spec == {}
    assert exp.color_spec == []
    assert exp.saved_statistics_exports == []
    assert exp.palettes == {}
    assert exp.permissions[0].get("grantee").get("_id") == exp.uploader.get("_id")  # type: ignore


def test_experiment_clone(blank_experiment: Experiment):
    exp = blank_experiment.clone()
    assert exp.name == blank_experiment.name + "-1"


def test_save_revision(blank_experiment):
    preDU = blank_experiment.deep_updated
    blank_experiment.save_revision("my description")
    assert len(blank_experiment.revisions) == 1
    assert blank_experiment.revisions[0].get("description") == "my description"
    assert blank_experiment.deep_updated > preDU


def test_experiment_upload_fcs_file(blank_experiment: Experiment):
    file = blank_experiment.upload_fcs_file(
        "tests/data/Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"
    )
    assert file.name == "Specimen_001_A1_A01_MeOHperm(DL350neg).fcs"


def test_experiment_delete(blank_experiment: Experiment):
    blank_experiment.delete()
    assert type(blank_experiment.deleted) is datetime


def test_experiment_undelete(blank_experiment: Experiment):
    blank_experiment.delete()
    assert type(blank_experiment.deleted) is datetime
    blank_experiment.undelete()
    assert blank_experiment.deleted is None


def test_experiment_get_set_active_compensation(blank_experiment: Experiment):
    pass


def test_experiment_get_set_comments(blank_experiment: Experiment):
    pass


# TODO download/upload/delete attachment
# TODO create/update/delete compensation
# TODO download/create/update/delete FCS file


@pytest.mark.parametrize(
    "entity,_type",
    [
        ("attachments", Attachment),
        ("compensations", Compensation),
        ("fcs_files", FcsFile),
        ("gates", Gate),
        ("populations", Population),
    ],
)
def test_get_list_of_entities(full_experiment, entity, _type):
    experiment = full_experiment["experiment"]
    all_entities = getattr(experiment, entity)
    assert type(all_entities) is list
    if entity == "gates":
        assert all(
            [str(ent.__module__) == "cellengine.resources.gate" for ent in all_entities]
        )
    else:
        assert all([type(ent) is _type for ent in all_entities])


@pytest.mark.parametrize(
    "entity,get_func,_type",
    [
        ("attachments", "get_attachment", Attachment),
        ("compensations", "get_compensation", Compensation),
        ("fcs_files", "get_fcs_file", FcsFile),
        ("gates", "get_gate", Gate),
        ("populations", "get_population", Population),
    ],
)
def test_get_one_entity(
    full_experiment,
    entity,
    get_func,
    _type,
):
    experiment = full_experiment["experiment"]
    all_entities = getattr(experiment, entity)
    _func = getattr(experiment, get_func)
    if len(all_entities) > 0:
        ent = _func(_id=all_entities[0]._id)
        if entity == "gates":
            assert str(ent.__module__) == "cellengine.resources.gate"
        else:
            assert type(ent) is _type
    else:
        raise Warning("No entities of type {} to test".format(entity))


def test_get_statistics(full_experiment):
    experiment = full_experiment["experiment"]
    # TODO more tests
    s = experiment.get_statistics(["mean"], ["FSC-A"])
    assert isinstance(s, DataFrame)


def test_sets_active_compensation_correctly(full_experiment):
    experiment = full_experiment["experiment"]
    compensation = full_experiment["compensation"]

    experiment.active_compensation = 0
    assert experiment.active_compensation == 0

    experiment.active_compensation = -1
    assert experiment.active_compensation == -1

    experiment.active_compensation = -2
    assert experiment.active_compensation == -2

    experiment.active_compensation = UNCOMPENSATED
    assert experiment.active_compensation == 0

    experiment.active_compensation = FILE_INTERNAL
    assert experiment.active_compensation == -1

    experiment.active_compensation = PER_FILE
    assert experiment.active_compensation == -2

    experiment.active_compensation = compensation._id
    assert experiment.active_compensation == compensation._id


def test_update_experiment(blank_experiment):
    assert blank_experiment.name != "new name"
    blank_experiment.name = "new name"
    blank_experiment.update()
    assert blank_experiment.name == "new name"
