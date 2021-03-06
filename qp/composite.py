import numpy as np
import scipy as sp
from scipy import stats as sps
import scipy.optimize as op

import qp

class composite(object):

    def __init__(self, components, vb=True):
        """
        A probability distribution that is a linear combination of scipy.stats.rv_continuous objects

        Parameters
        ----------
        components: list or tuple, dicts
            aggregation of dicts defining component functions and their coefficients
        vb: boolean
            report on progress to stdout?
        """
        self.components = components
        self.n_components = len(self.components)
        self.component_range = range(self.n_components)

        coefficients = np.array([component['coefficient'] for component in self.components])
        self.coefficients = coefficients / np.sum(coefficients)
        self.functions = np.array([component['function'] for component in self.components])

    def pdf(self, xs):
        """
        Evaluates the composite PDF at locations

        Parameters
        ----------
        xs: float or numpy.ndarray, float
            value(s) at which to evaluate the PDF

        Returns
        -------
        ps: float or numpy.ndarray, float
            value(s) of the PDF at xs
        """
        p = np.zeros(np.shape(xs))
        for c in self.component_range:
            p += self.coefficients[c] * self.functions[c].pdf(xs)
        return p

    def cdf(self, xs):
        """
        Evaluates the composite CDF at locations

        Parameters
        ----------
        xs: float or numpy.ndarray, float
            value(s) at which to evaluate the CDF

        Returns
        -------
        ps: float or numpy.ndarray, float
            value(s) of the CDF at xs
        """
        ps = np.zeros(np.shape(xs))
        for c in self.component_range:
            ps += self.coefficients[c] * self.functions[c].cdf(xs)
        return ps

    def rvs(self, size):
        """
        Samples the composite probability distribution

        Parameters
        ----------
        size: int
            number of samples to take

        Returns
        -------
        xs: numpy.ndarray, float
            samples from the PDF
        """
        groups = [0]*self.n_components
        for item in range(size):
            groups[qp.utils.choice(self.component_range, self.coefficients)] += 1
        samples = [] * size
        for c in self.component_range:
            for n in range(groups[c]):
                samples.append(self.functions[c].rvs())
        return np.array(samples)

    def ppf(self, cdfs, vb=True):
        """
        Evaluates the composite PPF at locations

        Parameters
        ----------
        cdfs: float or numpy.ndarray, float
            value(s) at which to find quantiles

        Returns
        -------
        xs: float or numpy.ndarray, float
            quantiles
        """
        N = np.shape(cdfs)
        xs = np.zeros(N)

        all_cdfs = np.zeros(N)
        for c in self.component_range:
            all_cdfs += self.functions[c].ppf(cdfs)
        xs0 = all_cdfs / self.n_components

        for n in range(N[0]):
            def ppf_helper(x):
                return np.absolute(cdfs[n] - self.cdf(x))
            res = op.minimize(ppf_helper, xs0[n], method="Nelder-Mead", options={"maxfev": 1e5, "maxiter":1e5})
            # res = op.basinhopping(ppf_helper, xs0[n])#, method="Nelder-Mead", options={"maxfev": 1e5, "maxiter":1e5})
            xs[n] += res.x
            # if vb:
            #     print(res.message, res.success)
        return xs
