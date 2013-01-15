import numpy as np
import numpy.ma as ma
import scipy.stats.mstats as mstats
from opec.Configuration import get_default_config

def extract_values(matchups):
    reference_values = np.empty(len(matchups))
    model_values = np.empty(len(matchups))
    index = 0
    for matchup in matchups:
        reference_values[index] = matchup.ref_value
        model_values[index] = matchup.model_value
        index += 1
    return reference_values, model_values

def mean(values):
    return np.mean(values)

def stddev(values, ddof):
    return np.std(values, ddof=ddof)

def percentiles(values, alphap, betap):
    return mstats.mquantiles(values, [0.5, 0.9, 0.95], alphap, betap)

def minmax(values):
    return [np.min(values), np.max(values)]

def rmse(reference_values, values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    squared_errors = (values - reference_values) ** 2
    return np.sqrt(np.mean(squared_errors))

def bias(reference_values, values):
    """
    according to http://en.wikipedia.org/wiki/Bias_of_an_estimator
    """
    return np.mean(reference_values) - np.mean(values)

def unbiased_rmse(reference_values, values):
    squared_differences = ((values - np.mean(values)) - (reference_values - np.mean(reference_values))) ** 2
    squared_differences /= ma.count(values)
    return np.sqrt(np.sum(squared_differences))

def correlation(reference_values, values):
    if len(np.unique(reference_values)) == 1 or len(np.unique(values)) == 1:
        return np.nan # if all reference or model values are equal, no sensible correlation coefficient can be computed.
    return ma.corrcoef(values, reference_values)[0, 1]

def percentage_model_bias(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return np.sum(reference_values - model_values) * 100 / np.sum(reference_values)


def reliability_index(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    n = 1 / ma.count(reference_values)
    return np.exp(np.sqrt(n * np.sum(np.power(np.log10(reference_values / model_values), 2))))

def model_efficiency(reference_values, model_values):
    """
    Nash-Sutcliffe model efficiency according to MEECE D2.7 User guide and report outlining validation methodology
    """
    if len(np.unique(reference_values)) == 1:
        return np.nan # if all reference values are equal, no sensible model efficiency can be computed.
    return 1 - np.sum(np.power(reference_values - model_values, 2)) / np.sum(np.power(reference_values - np.mean(reference_values), 2))

def create_masked_array(reference_values):
    false_mask = np.zeros(len(reference_values))
    if type(reference_values) is not ma.core.MaskedArray:
        reference_values = ma.array(reference_values, mask=false_mask)
    return reference_values

def harmonise(reference_values, model_values):
    reference_values = create_masked_array(reference_values)
    model_values = create_masked_array(model_values)
    reference_values.mask = reference_values.mask | model_values.mask
    model_values.mask = reference_values.mask | model_values.mask
    return reference_values, model_values

def calculate_statistics(matchups=None, reference_values=None, model_values=None, config=None, model_name=None, ref_name=None):
    if reference_values is None or model_values is None:
        reference_values, model_values = extract_values(matchups)
        if model_name is None:
            model_name = matchups[0].model_variable_name
        if ref_name is None:
            ref_name = matchups[0].ref_variable_name
    reference_values, model_values = harmonise(reference_values, model_values)
    if ma.count(model_values) != ma.count(reference_values):
        raise ValueError("len(values) != len(reference_values)")

    if config is None:
        config = get_default_config()

    model_percentiles = percentiles(model_values, config.alpha, config.beta)
    ref_percentiles = percentiles(reference_values, config.alpha, config.beta)
    model_minmax = minmax(model_values)
    ref_minmax = minmax(reference_values)
    stats = dict()
    stats['model_name'] = model_name
    stats['ref_name'] = ref_name
    stats['rmse'] = rmse(reference_values, model_values)
    stats['unbiased_rmse'] = unbiased_rmse(reference_values, model_values)
    stats['pbias'] = percentage_model_bias(reference_values, model_values)
    stats['bias'] = bias(reference_values, model_values)
    stats['corrcoeff'] = correlation(reference_values, model_values)
    stats['reliability_index'] = reliability_index(reference_values, model_values)
    stats['model_efficiency'] = model_efficiency(reference_values, model_values)
    stats['mean'] = mean(model_values)
    stats['ref_mean'] = mean(reference_values)
    stats['stddev'] = stddev(model_values, config.ddof)
    stats['ref_stddev'] = stddev(reference_values, config.ddof)
    stats['median'] = model_percentiles[0]
    stats['ref_median'] = ref_percentiles[0]
    stats['p90'] = model_percentiles[1]
    stats['ref_p90'] = ref_percentiles[1]
    stats['p95'] = model_percentiles[2]
    stats['ref_p95'] = ref_percentiles[2]
    stats['min'] = model_minmax[0]
    stats['ref_min'] = ref_minmax[0]
    stats['max'] = model_minmax[1]
    stats['ref_max'] = ref_minmax[1]
    return stats