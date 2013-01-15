from datetime import datetime
from unittest import TestCase
from opec import Processor
from opec.Output import Output
from opec.Configuration import Configuration
from opec.Matchup import Matchup
import os.path as path
import os as os

class OutputTest(TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        os.chdir('..')

    @classmethod
    def tearDownClass(self):
        os.chdir(self.cwd)

    def setUp(self):
        self.config = Configuration(1, 1, 0, 123, 12, 1234, 0.234)
        matchups = [
            Matchup('chl_ref', 'chl', 10, 11, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 9, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 11.2, 55, 20, 10000, 0, 0, 0, 0.1, 0),
            Matchup('chl_ref', 'chl', 10, 10.5, 55, 20, 10000, 0, 0, 0, 0.1, 0)
        ]
        self.stats = Processor.calculate_statistics(matchups, config=self.config)
        self.temp_filename = '../resources/test_output.csv'

    def tearDown(self):
        if path.exists(self.temp_filename):
            os.remove(self.temp_filename)
            if path.exists(self.temp_filename):
                self.fail('Failed to delete {}'.format(self.temp_filename))

    def test_output_statistics_from_dictionary(self):
        output = Output(
            source_file='somethingsomethingsomethingdarkside',
            config=self.config
        )

        expected_result = []
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results of file \'somethingsomethingsomethingdarkside\'")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Created on {}".format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        expected_result.append("#")
        expected_result.append("# Matchup criteria:")
        expected_result.append("#    Macro pixel size = 123")
        expected_result.append("#    Maximum geographic delta = 12.0 \"degrees\"")
        expected_result.append("#    Maximum time delta = 1234 seconds")
        expected_result.append("#    Maximum depth delta = 0.234 meters")
        expected_result.append("#")
        expected_result.append("# Algorithm parameters:")
        expected_result.append("#    ddof (delta degrees of freedom, used for computation of stddev) = 0")
        expected_result.append("#    alpha (used for percentile computation) = 1")
        expected_result.append("#    beta (used for percentile computation) = 1")
        expected_result.append("#")
        expected_result.append("variable_name\tref_variable_name\tmatchup_count\tmin\tmax\tmean\tstddev\tmedian\tp90\tp95\tref_min\tref_max\tref_mean\tref_stddev\tref_median\tref_p90\tref_p95\trmse\tunbiased_rmse\tbias\tpbias\tcorrcoeff\treliability_index\tmodel_efficiency")
        expected_result.append("chl\tchl_ref\t4\t9\t11.2\t10.425\t0.8613\t10.75\t11.14\t11.17\t10\t10\t10\t0\t10\t10\t10\t0.9605\t0.8613\t-0.425\t-4.25\tnan\t1.0417\tnan")

        csv = output.csv(self.stats, variable_name='chl', ref_variable_name='chl_ref', matchup_count=4)
        self.assertEqual("\n".join(expected_result), csv)

    def test_output_statistics_from_dictionary_minimum(self):

        output = Output(config=self.config)

        expected_result = []
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Benchmarking results")
        expected_result.append("#")
        expected_result.append("##############################################################")
        expected_result.append("#")
        expected_result.append("# Created on {}".format(datetime.now().strftime('%b %d, %Y at %H:%M:%S')))
        expected_result.append("#")
        expected_result.append("# Matchup criteria:")
        expected_result.append("#    Macro pixel size = 123")
        expected_result.append("#    Maximum geographic delta = 12.0 \"degrees\"")
        expected_result.append("#    Maximum time delta = 1234 seconds")
        expected_result.append("#    Maximum depth delta = 0.234 meters")
        expected_result.append("#")
        expected_result.append("# Algorithm parameters:")
        expected_result.append("#    ddof (delta degrees of freedom, used for computation of stddev) = 0")
        expected_result.append("#    alpha (used for percentile computation) = 1")
        expected_result.append("#    beta (used for percentile computation) = 1")
        expected_result.append("#")
        expected_result.append("variable_name\tref_variable_name\tmatchup_count\tmin\tmax\tmean\tstddev\tmedian\tp90\tp95\tref_min\tref_max\tref_mean\tref_stddev\tref_median\tref_p90\tref_p95\trmse\tunbiased_rmse\tbias\tpbias\tcorrcoeff\treliability_index\tmodel_efficiency")
        expected_result.append("Unknown\tUnknown\tUnknown\t9\t11.2\t10.425\t0.8613\t10.75\t11.14\t11.17\t10\t10\t10\t0\t10\t10\t10\t0.9605\t0.8613\t-0.425\t-4.25\tnan\t1.0417\tnan")

        self.assertEqual("\n".join(expected_result) , output.csv(self.stats))
        
    def test_output_statistics_from_dictionary_no_header(self):
        config = Configuration(1, 1, 0, 123, 12, 1234, 0.234, include_header=False, separator=';')
        output = Output(config=config)

        expected_result = []
        expected_result.append("variable_name;ref_variable_name;matchup_count;min;max;mean;stddev;median;p90;p95;ref_min;ref_max;ref_mean;ref_stddev;ref_median;ref_p90;ref_p95;rmse;unbiased_rmse;bias;pbias;corrcoeff;reliability_index;model_efficiency")
        expected_result.append("Unknown;Unknown;Unknown;9;11.2;10.425;0.8613;10.75;11.14;11.17;10;10;10;0;10;10;10;0.9605;0.8613;-0.425;-4.25;nan;1.0417;nan")

        self.assertEqual("\n".join(expected_result) , output.csv(self.stats))

    def test_write_csv_file(self):
        output = Output(statistics=self.stats)
        self.assertFalse(path.exists(self.temp_filename))
        output.csv(self.stats, target_file=self.temp_filename)
        self.assertTrue(path.exists(self.temp_filename))
        os.remove(self.temp_filename)
        self.assertFalse(path.exists(self.temp_filename))