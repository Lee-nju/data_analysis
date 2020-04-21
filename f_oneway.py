import scipy.stats as stats
import itertools as it

from bisect import bisect_left
from typing import List

import numpy as np
import pandas as pd

from pandas import Categorical

# example 1
# a = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
# b = [1000, 1000, 1000, 1000, 1000]
# c = [100, 100, 100, 100, 100, 100]
# print(stats.f_oneway(a, b, c))
# print(stats.f_oneway(a, c, b))
# print(stats.f_oneway(b, c, a))

# apache 2-way
# acts = [33, 33, 33, 33, 33, 33, 33, 33, 33, 33]
# casa = [30, 32, 38, 33, 33, 32, 35, 33, 34, 31]
# fastca = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30]
# pict = [39, 38, 38, 39, 39, 39, 40, 39, 37, 40]
#
# print(stats.f_oneway(acts, casa, fastca, pict))
# print(stats.f_oneway(acts, casa, pict, fastca))
# print(stats.f_oneway(acts, fastca, casa, pict))
# print(stats.f_oneway(pict, casa, fastca, acts))

# bugzilla 2-way
# acts = [19, 19, 19, 19, 19, 19, 19, 19, 19, 19]
# casa = [16, 16, 16, 16, 16, 16, 18, 16, 16, 16]
# pict = [20, 19, 18, 21, 20, 20, 18, 18, 20, 21]
#
# print(stats.f_oneway(acts, casa, pict))
# print(stats.f_oneway(acts, pict, casa))
# print(stats.f_oneway(pict, casa, acts))

def VD_A(treatment: List[float], control: List[float]):
    """
    Computes Vargha and Delaney A index
    A. Vargha and H. D. Delaney.
    A critique and improvement of the CL common language
    effect size statistics of McGraw and Wong.
    Journal of Educational and Behavioral Statistics, 25(2):101-132, 2000
    The formula to compute A has been transformed to minimize accuracy errors
    See: http://mtorchiano.wordpress.com/2014/05/19/effect-size-of-r-precision/
    :param treatment: a numeric list
    :param control: another numeric list
    :returns the value estimate and the magnitude
    """
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = stats.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m)  # equivalent formula to avoid accuracy errors

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude


def VD_A_DF(data, val_col: str = None, group_col: str = None, sort=True):
    """
    :param data: pandas DataFrame object
        An array, any object exposing the array interface or a pandas DataFrame.
        Array must be two-dimensional. Second dimension may vary,
        i.e. groups may have different lengths.
    :param val_col: str, optional
        Must be specified if `a` is a pandas DataFrame object.
        Name of the column that contains values.
    :param group_col: str, optional
        Must be specified if `a` is a pandas DataFrame object.
        Name of the column that contains group names.
    :param sort : bool, optional
        Specifies whether to sort DataFrame by group_col or not. Recommended
        unless you sort your data manually.
    :return: stats : pandas DataFrame of effect sizes
    Stats summary ::
    'A' : Name of first measurement
    'B' : Name of second measurement
    'estimate' : effect sizes
    'magnitude' : magnitude
    """

    x = data.copy()
    if sort:
        x[group_col] = Categorical(x[group_col], categories=x[group_col].unique(), ordered=True)
        x.sort_values(by=[group_col, val_col], ascending=True, inplace=True)

    groups = x[group_col].unique()

    # Pairwise combinations
    g1, g2 = np.array(list(it.combinations(np.arange(groups.size), 2))).T

    # Compute effect size for each combination
    ef = np.array([VD_A(list(x[val_col][x[group_col] == groups[i]].values),
                        list(x[val_col][x[group_col] == groups[j]].values)) for i, j in zip(g1, g2)])

    return pd.DataFrame({
        'A': np.unique(data[group_col])[g1],
        'B': np.unique(data[group_col])[g2],
        'estimate': ef[:, 0],
        'magnitude': ef[:, 1]
    })


a = [30.0 for i in range(20)]
b = [33.0 for i in range(20)]
pict = '30 32 38 33 33 32 35 33 34 31 34 35 31 35 36 34 35 37 36 36'
c = pict.split(' ')
c = [int(x) for x in b]

print(VD_A(a, b))
print(VD_A(b, a))
print(VD_A(a, c))