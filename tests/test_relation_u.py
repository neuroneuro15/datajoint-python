from nose.tools import assert_equal, assert_true, raises, assert_list_equal
from . import schema, schema_simple
import datajoint as dj


class TestU:
    """
    Test base relations: insert, delete
    """

    def __init__(self):
        self.user = schema.User()
        self.language = schema.Language()
        self.subject = schema.Subject()
        self.experiment = schema.Experiment()
        self.trial = schema.Trial()
        self.ephys = schema.Ephys()
        self.channel = schema.Ephys.Channel()
        self.img = schema.Image()
        self.trash = schema.UberTrash()

    def test_restriction(self):
        language_set = {s[1] for s in self.language.contents}
        rel = dj.U('language') & self.language
        assert_list_equal(rel.heading.names, ['language'])
        assert_true(len(rel) == len(language_set))
        assert_true(set(rel.fetch['language']) == language_set)

    @staticmethod
    @raises(dj.DataJointError)
    def test_invalid_restriction():
        result = dj.U('color') & dict(color="red")

    def test_ineffective_restriction(self):
        rel = self.language & dj.U('language')
        assert_true(rel.make_sql() == self.language.make_sql())

    def test_join(self):
        rel = self.experiment*dj.U('experiment_date')
        assert_equal(self.experiment.primary_key, ['subject_id', 'experiment_id'])
        assert_equal(rel.primary_key, self.experiment.primary_key + ['experiment_date'])

        rel = dj.U('experiment_date')*self.experiment
        assert_equal(self.experiment.primary_key, ['subject_id', 'experiment_id'])
        assert_equal(rel.primary_key, self.experiment.primary_key + ['experiment_date'])

    @staticmethod
    @raises(dj.DataJointError)
    def test_invalid_join():
        rel = dj.U('language') * dict(language="English")

    def test_aggregations(self):
        rel = dj.U('language').aggr(schema.Language(), number_of_speakers='count(*)')
        assert_equal(len(rel), len(set(l[1] for l in schema.Language.contents)))
        assert_equal((rel & 'language="English"').fetch1['number_of_speakers'], 3)

    def test_argmax(self):
        rel = schema.Test()
        # get the tuples corresponding to maximum value
        mx = rel & dj.U().aggr(rel, value='max(value)')
        assert_equal(mx.fetch['value'][0], max(rel.fetch['value']))

    def test_aggr(self):
        rel = schema_simple.ArgmaxTest()
        amax1 = (dj.U('val') * rel) & dj.U('secondary_key').aggr(rel, val='min(val)')
        amax2 = (dj.U('val') * rel) * dj.U('secondary_key').aggr(rel, val='min(val)')
        assert_true(len(amax1) == len(amax2) == rel.n,
                    'Aggregated argmax with join and restriction does not yield same length.')
