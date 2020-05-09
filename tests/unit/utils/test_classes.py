from cellengine.utils.classes import ResourceFactory, FCSFILE
from cellengine.resources.fcsfile import FcsFile
from cellengine.resources.experiment import Experiment
from cellengine.resources.gate import Gate


def test_should_match_class_by_keys(fcsfiles):
    assert ResourceFactory()._keys_match(fcsfiles[0], FCSFILE)


def test_should_not_match_class_by_few_properties(fcsfiles):
    assert ResourceFactory()._keys_match({"_id": 1, "__v": 2}, FCSFILE) is False


def test_should_match_class_by_few_keys(fcsfiles):
    assert ResourceFactory()._keys_match(fcsfiles[0], {"_id", "md5"})


def test_should_not_match_class_with_wrong_keys(fcsfiles):
    assert ResourceFactory()._keys_match(fcsfiles[0], {"wrong", "keys"}) is False


def test_should_match_each_class(
    attachments, compensations, experiments, fcsfiles, gates, populations, scalesets
):
    assert ResourceFactory()._match_class(attachments[0]) == "Attachment"
    assert ResourceFactory()._match_class(compensations[0]) == "Compensation"
    assert ResourceFactory()._match_class(experiments[0]) == "Experiment"
    assert ResourceFactory()._match_class(fcsfiles[0]) == "FcsFile"
    assert ResourceFactory()._match_class(gates[0]) == "Gate"
    assert ResourceFactory()._match_class(populations[0]) == "Population"
    assert ResourceFactory()._match_class(scalesets) == "ScaleSet"


def test_should_load_correct_class():
    assert ResourceFactory()._load_class("FcsFile") is FcsFile


def test_should_instantiate_fcsfile(fcsfiles, experiments):
    file = ResourceFactory.load(fcsfiles[0])
    assert type(file) == FcsFile


def test_should_instantiate_experiment(fcsfiles, experiments):
    exp = ResourceFactory.load(experiments[0])
    assert type(exp) == Experiment


def test_should_instantiate_class(fcsfiles):
    file = ResourceFactory.load(fcsfiles[0])
    assert type(file) is FcsFile


def test_should_instantiate_list_of_classes(fcsfiles):
    files = ResourceFactory.load(fcsfiles)
    assert type(files) is list
    assert all([type(file) is FcsFile for file in files])


def test_should_instantiate_list_of_gates(gates):
    gate_instances = ResourceFactory.load(gates)
    assert type(gate_instances) is list
    assert all([gate.__class__ is Gate for gate in gate_instances])
