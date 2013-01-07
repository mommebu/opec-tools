from unittest import TestCase
import numpy as np
import numpy.ma as ma
from numpy.testing import assert_array_equal
from src.main.python.Configuration import Configuration
from src.main.python.Data import Data
from src.main.python.MatchupEngine import MatchupEngine
from src.main.python.Processor import calculate_statistics, harmonise

class ProcessorTest(TestCase):

    def setUp(self):
        self.data = Data('../resources/test.nc')
        self.config = Configuration(macro_pixel_size=3, geo_delta=10, time_delta=86400, depth_delta=12, ddof=0, alpha=1, beta=1)
        self.me = MatchupEngine(self.data, self.config)

    def tearDown(self):
        self.data.close()

    def test_compute_statistics_for_matchups(self):
        matchups = self.me.find_all_matchups('chl_ref', 'chl')
        stats = calculate_statistics(matchups, config=self.config)
        self.assertAlmostEqual(0.0960456, stats['rmsd'], 5)
        self.assertAlmostEqual(0.0868041, stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(20.553573, stats['pbias'], 5)
        self.assertAlmostEqual(0.0411071, stats['bias'], 5)
        self.assertAlmostEqual(0.077279, stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.2662666, stats['reliability_index'], 5)
        self.assertAlmostEqual(-0.6143319, stats['model_efficiency'], 5)
        self.assertAlmostEqual(0.158892, stats['mean'], 5)
        self.assertAlmostEqual(0.2, stats['ref_mean'], 5)
        self.assertAlmostEqual(0.048909, stats['stddev'], 5)
        self.assertAlmostEqual(0.075593, stats['ref_stddev'], 5)
        self.assertAlmostEqual(0.12225, stats['median'], 5)
        self.assertAlmostEqual(0.2, stats['ref_median'], 5)
        self.assertAlmostEqual(0.22125, stats['p90'], 5)
        self.assertAlmostEqual(0.3, stats['ref_p90'], 5)
        self.assertAlmostEqual(0.222125, stats['p95'], 5)
        self.assertAlmostEqual(0.3, stats['ref_p95'], 5)
        self.assertAlmostEqual(0.1111, stats['min'], 5)
        self.assertAlmostEqual(0.1, stats['ref_min'], 5)
        self.assertAlmostEqual(0.2224, stats['max'], 5)
        self.assertAlmostEqual(0.3, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmsd'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_statistics(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertAlmostEqual(0.192028, stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(0.193649, stats['rmsd'], 5)
        self.assertAlmostEqual(-1.0101, stats['pbias'], 5)
        self.assertAlmostEqual(-0.025, stats['bias'], 5)
        self.assertAlmostEqual(0.99519, stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.03521, stats['reliability_index'], 5)
        self.assertAlmostEqual(0.9588759, stats['model_efficiency'], 5)
        self.assertAlmostEqual(2.5, stats['mean'], 5)
        self.assertAlmostEqual(2.475, stats['ref_mean'], 5)
        self.assertAlmostEqual(1.11803, stats['stddev'], 5)
        self.assertAlmostEqual(0.954921, stats['ref_stddev'], 5)
        self.assertAlmostEqual(2.5, stats['median'], 5)
        self.assertAlmostEqual(2.55, stats['ref_median'], 5)
        self.assertAlmostEqual(3.7, stats['p90'], 5)
        self.assertAlmostEqual(3.46, stats['ref_p90'], 5)
        self.assertAlmostEqual(3.85, stats['p95'], 5)
        self.assertAlmostEqual(3.58, stats['ref_p95'], 5)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1.1, stats['ref_min'], 5)
        self.assertAlmostEqual(4, stats['max'], 5)
        self.assertAlmostEqual(3.7, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmsd'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_statistics_with_masked_values(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertAlmostEqual(0.216024, stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(0.216024, stats['rmsd'], 5)
        self.assertAlmostEqual(6.344131e-15, stats['pbias'], 5)
        self.assertAlmostEqual(0.0, stats['bias'], 5)
        self.assertAlmostEqual(0.99484975, stats['corrcoeff'], 5)
        self.assertAlmostEqual(1.039815, stats['reliability_index'], 5)
        self.assertAlmostEqual(0.9589041, stats['model_efficiency'], 5)
        self.assertAlmostEqual(2.3333333, stats['mean'], 5)
        self.assertAlmostEqual(2.3333333, stats['ref_mean'], 5)
        self.assertAlmostEqual(1.24722, stats['stddev'], 5)
        self.assertAlmostEqual(1.06562, stats['ref_stddev'], 5)
        self.assertAlmostEqual(2, stats['median'], 5)
        self.assertAlmostEqual(2.2, stats['ref_median'], 5)
        self.assertAlmostEqual(3.6, stats['p90'], 5)
        self.assertAlmostEqual(3.4, stats['ref_p90'], 5)
        self.assertAlmostEqual(3.8, stats['p95'], 5)
        self.assertAlmostEqual(3.55, stats['ref_p95'], 5)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1.1, stats['ref_min'], 5)
        self.assertAlmostEqual(4, stats['max'], 5)
        self.assertAlmostEqual(3.7, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmsd'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_statistics_with_extreme_model_values(self):
        model_values = np.array(range(1, 5, 1)) # [1, 2, 3, 4]
        ref_values = np.array([1, 1, 1, 1])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertAlmostEqual(1.118034, stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(1.870829, stats['rmsd'], 5)
        self.assertAlmostEqual(-150, stats['pbias'], 5)
        self.assertAlmostEqual(-1.5, stats['bias'], 5)
        self.assertTrue(np.isnan(stats['corrcoeff']))
        self.assertAlmostEqual(1.5106421, stats['reliability_index'], 5)
        self.assertTrue(np.isnan(stats['model_efficiency']))
        self.assertAlmostEqual(2.5, stats['mean'], 5)
        self.assertAlmostEqual(1, stats['ref_mean'], 5)
        self.assertAlmostEqual(1.11803, stats['stddev'], 5)
        self.assertAlmostEqual(0.0, stats['ref_stddev'], 5)
        self.assertAlmostEqual(2.5, stats['median'], 5)
        self.assertAlmostEqual(1, stats['ref_median'], 5)
        self.assertAlmostEqual(3.7, stats['p90'], 5)
        self.assertAlmostEqual(1, stats['ref_p90'], 5)
        self.assertAlmostEqual(3.85, stats['p95'], 5)
        self.assertAlmostEqual(1, stats['ref_p95'], 5)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1, stats['ref_min'], 5)
        self.assertAlmostEqual(4, stats['max'], 5)
        self.assertAlmostEqual(1, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmsd'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmsd'] ** 2, 5)

    def test_compute_statistics_with_extreme_reference_values(self):
        model_values = np.array([1, 1, 1, 1])
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        stats = calculate_statistics(reference_values=ref_values, model_values=model_values, config=self.config)
        self.assertAlmostEqual(0.954921, stats['unbiased_rmsd'], 5)
        self.assertAlmostEqual(1.757128, stats['rmsd'], 5)
        self.assertAlmostEqual(59.595959, stats['pbias'], 5)
        self.assertAlmostEqual(1.475, stats['bias'], 5)
        self.assertTrue(np.isnan(stats['corrcoeff']))
        self.assertAlmostEqual(1.49908579, stats['reliability_index'], 5)
        self.assertAlmostEqual(-2.38588, stats['model_efficiency'], 5)
        self.assertAlmostEqual(1.0, stats['mean'], 5)
        self.assertAlmostEqual(2.475, stats['ref_mean'], 5)
        self.assertAlmostEqual(0, stats['stddev'], 5)
        self.assertAlmostEqual(0.954921, stats['ref_stddev'], 5)
        self.assertAlmostEqual(1, stats['median'], 5)
        self.assertAlmostEqual(2.545, stats['ref_median'], 2)
        self.assertAlmostEqual(1, stats['p90'], 5)
        self.assertAlmostEqual(3.46, stats['ref_p90'], 5)
        self.assertAlmostEqual(1, stats['p95'], 5)
        self.assertAlmostEqual(3.58, stats['ref_p95'], 2)
        self.assertAlmostEqual(1, stats['min'], 5)
        self.assertAlmostEqual(1.1, stats['ref_min'], 5)
        self.assertAlmostEqual(1, stats['max'], 5)
        self.assertAlmostEqual(3.7, stats['ref_max'], 5)

        self.assertAlmostEqual(stats['rmsd'] ** 2, stats['bias'] ** 2 + stats['unbiased_rmsd'] ** 2, 5)

    def test_cleanup_1(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, --, 3, 4]
        ref_values = np.array([1.1, 2.2, 2.9, 3.7])
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        assert_array_equal(np.array([False, False, True, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([False, False, True, False]), ref_values.mask)

    def test_cleanup_2(self):
        model_values = np.array(np.arange(1.0, 5.0, 1)) # [1, 2, 3, 4]
        ref_values = ma.array(np.array([1.1, 2.2, 2.9, 3.7]), mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1, 2, 3, 4]), model_values)
        assert_array_equal(np.array([True, False, False, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([True, False, False, False]), ref_values.mask)

    def test_cleanup_3(self):
        model_values = ma.array(np.arange(1.0, 5.0, 1), mask=np.array([False, False, True, False])) # [1, 2, --, 4]
        ref_values = ma.array([1.1, 2.2, 2.9, 3.7], mask=np.array([True, False, False, False]))
        ref_values, model_values = harmonise(ref_values, model_values)

        # Note: assert_array_equals does not tests if masks are equal
        # and there is no dedicated method for this
        # so masks need to be tested separately

        assert_array_equal(np.array([1.0, 2.0, 3.0, 4.0]), model_values)
        assert_array_equal(np.array([True, False, True, False]), model_values.mask)

        assert_array_equal(np.array([1.1, 2.2, 2.9, 3.7]), ref_values)
        assert_array_equal(np.array([True, False, True, False]), ref_values.mask)
