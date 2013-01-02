import numpy as np
import numpy.ma as ma

def extract_values(matchups):
    reference_values = np.empty(len(matchups))
    model_values = np.empty(len(matchups))
    index = 0
    for matchup in matchups:
        reference_values[index] = matchup.ref_value
        model_values[index] = matchup.model_value
        index += 1
    return reference_values, model_values

def compute_rmsd(reference_values, values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    if ma.count(values) != ma.count(reference_values):
        raise ValueError("len(values) != len(reference_values)")
    squareErrors = (values - reference_values) ** 2
    return np.sqrt(np.mean(squareErrors))

def compute_bias(reference_values, values):
    """
    according to http://en.wikipedia.org/wiki/Bias_of_an_estimator
    """
    return np.mean(reference_values) - np.mean(values)

def compute_unbiased_rmsd(reference_values, values):
    squared_differences = ((values - np.mean(values)) - (reference_values - np.mean(reference_values))) ** 2
    squared_differences /= ma.count(values)
    return np.sqrt(np.sum(squared_differences))

def compute_correlation(reference_values, values):
    return ma.corrcoef(values, reference_values)[0, 1]

def compute_percentage_model_bias(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return np.sum(reference_values - model_values) * 100 / np.sum(reference_values)


def compute_reliability_index(reference_values, model_values):
    """
    according to MEECE D2.7 User guide and report outlining validation methodology
    """
    n = 1 / ma.count(reference_values)
    return np.exp(np.sqrt(n * np.sum(np.power(np.log10(reference_values / model_values), 2))))

def compute_model_efficiency(reference_values, model_values):
    """
    Nash-Sutcliffe model efficiency according to MEECE D2.7 User guide and report outlining validation methodology
    """
    return 1 - np.sum(np.power(reference_values - model_values, 2)) / np.sum(np.power(reference_values - np.mean(reference_values), 2))

def create_masked_array(reference_values):
    false_mask = np.zeros(len(reference_values))
    if type(reference_values) is not ma.core.MaskedArray:
        reference_values = ma.array(reference_values, mask=false_mask)
    return reference_values

def cleanup(reference_values, model_values):
    reference_values = create_masked_array(reference_values)
    model_values = create_masked_array(model_values)
    reference_values.mask = reference_values.mask | model_values.mask
    model_values.mask = reference_values.mask | model_values.mask
    return reference_values, model_values

def compute_basic_statistics(matchups=None, reference_values=None, model_values=None):
    if reference_values is None or model_values is None:
        reference_values, model_values = extract_values(matchups)
    reference_values, model_values = cleanup(reference_values, model_values)
    basic_statistics = dict()
    basic_statistics['rmsd'] = compute_rmsd(reference_values, model_values)
    basic_statistics['unbiased_rmsd'] = compute_unbiased_rmsd(reference_values, model_values)
    basic_statistics['pbias'] = compute_percentage_model_bias(reference_values, model_values)
    basic_statistics['bias'] = compute_bias(reference_values, model_values)
    basic_statistics['corrcoeff'] = compute_correlation(reference_values, model_values)
    basic_statistics['reliability_index'] = compute_reliability_index(reference_values, model_values)
    basic_statistics['model_efficiency'] = compute_model_efficiency(reference_values, model_values)
    return basic_statistics
