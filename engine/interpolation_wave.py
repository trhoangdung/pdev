'''
This module implements interpolation class and its methods
Dung Tran: Nov/2017
Tianshu Bao: Jun/2018
'''
#add changes

import numpy as np
from engine.functions import Functions,lambdify
from scipy.optimize import minimize
from engine.set import RectangleSet2D, RectangleSet3D
from engine.set import DReachSet
from sympy import Function
from sympy.abc import alpha, beta

class InterpolSetInSpace(object):
    'represent the set after doing interpolation in space'

    ##########################################################################
    # U_n(x) = (a_n,i * alpha + b_n,i * beta) * x + c_n,i * alpha + d_n,i * beta
    # x[i] <= x < x[i + 1], timestep = n
    ##########################################################################

    def __init__(self):
        self.a_vec = None
        self.b_vec = None
        self.c_vec = None
        self.d_vec = None
        self.xlist = None

    def set_values(self, xlist, a_current_step_vec, b_current_step_vec,
                   c_current_step_vec, d_current_step_vec):
        'set values for parameter of interpolation set'

        assert isinstance(a_current_step_vec, np.ndarray)
        assert isinstance(b_current_step_vec, np.ndarray)
        assert isinstance(c_current_step_vec, np.ndarray)
        assert isinstance(d_current_step_vec, np.ndarray)

        assert a_current_step_vec.shape == b_current_step_vec.shape == \
            c_current_step_vec.shape == d_current_step_vec.shape, 'inconsistent data'

        assert isinstance(xlist, list)
        for i in xrange(0, len(xlist) - 1):
            assert xlist[i] < xlist[i + 1], 'invalid list'

        assert len(xlist) == a_current_step_vec.shape[0] + \
            1, 'inconsistency between xlist and vectors shapes'

        self.a_vec = a_current_step_vec
        self.b_vec = b_current_step_vec
        self.c_vec = c_current_step_vec
        self.d_vec = d_current_step_vec
        self.xlist = xlist

    def get_2D_boxes(self, alpha_range, beta_range):
        'get box contain all value of U_n(x) and min-max value of U_n(x)'

        assert self.a_vec is not None and self.b_vec is not None and self.c_vec is not None and self.d_vec is not None
        assert isinstance(alpha_range, tuple)
        assert isinstance(beta_range, tuple)
        assert len(alpha_range) == len(beta_range) == 2, 'invalid parameters'
        assert alpha_range[0] <= alpha_range[1]
        assert beta_range[0] <= beta_range[1]

        n = self.a_vec.shape[0]

        a_vec = self.a_vec
        b_vec = self.b_vec
        c_vec = self.c_vec
        d_vec = self.d_vec

        # minimum value of Un(x) at each segment
        min_vec = np.zeros((n,), dtype=float)
        # minimum points [x_min, alpha_min, beta_min]
        min_points = np.zeros((n, 3), dtype=float)
        # maximum value of Un(x) at each segment
        max_vec = np.zeros((n,), dtype=float)
        # maximum points [x_max, alpha_max, beta_max]
        max_points = np.zeros((n, 3), dtype=float)

        boxes_2D_list = []

        for i in xrange(0, n):
            min_func = Functions.intpl_inspace_func(
                a_vec[i], b_vec[i], c_vec[i], d_vec[i])
            max_func = Functions.intpl_inspace_func(
                -a_vec[i], -b_vec[i], -c_vec[i], -d_vec[i])
            xbounds = (self.xlist[i], self.xlist[i + 1])
            x0 = [self.xlist[i], alpha_range[0], beta_range[0]]
            bnds = (xbounds, alpha_range, beta_range)

            min_res = minimize(
                min_func,
                x0,
                method='L-BFGS-B',
                bounds=bnds,
                tol=1e-10, options={'disp': False})
            max_res = minimize(
                max_func,
                x0,
                method='L-BFGS-B',
                bounds=bnds,
                tol=1e-10, options={'disp': False})

            if min_res.status == 0:
                min_vec[i] = min_res.fun
                min_points[i, :] = min_res.x
            else:
                raise ValueError('min-optimization fail')

            if max_res.status == 0:
                max_vec[i] = -max_res.fun
                max_points[i, :] = max_res.x
            else:
                raise ValueError('max-optimization fail')

            box_2D = RectangleSet2D()
            box_2D.set_bounds(
                self.xlist[i], self.xlist[i + 1], min_vec[i], max_vec[i])
            boxes_2D_list.append(box_2D)

        return boxes_2D_list


class InterpolationSet(object):
    'represent the set after doing interpolation in both space and time'

    ###################################################################
    #    u(x,t) = (1 / k) *(delt_a_n,i * alpha + delt_bn,i * beta) * x * t +
    #             (delt_gamma_a_n,i * alpha + delt_gamma_b_n,i * beta) * x +
    #             (delta_gamma_c_n,i * alpha + delta_gamma_d_n,i * beta)
    #
    #    where x[i]< x <= x[i+1], t[n-1] < t <= t[n]
    ###################################################################

    def __init__(self):
        self.step = None
        self.cur_time_step = None
        self.xlist = None
        self.delta_a_vec = None
        self.delta_gamma_a_vec = None
        self.delta_b_vec = None
        self.delta_gamma_b_vec = None
        self.delta_c_vec = None
        self.delta_d_vec = None
        self.delta_gamma_c_vec = None
        self.delta_gamma_d_vec = None
	self.d_reach_prev = None 
	self.d_reach_curr = None

    def set_values(self, step, cur_time_step, xlist, delta_a_vec, delta_b_vec,
                   delta_gamma_a_vec, delta_gamma_b_vec,
                   delta_c_vec, delta_d_vec, delta_gamma_c_vec, delta_gamma_d_vec, d_reach_prev, d_reach_curr):
        'set values for the set'

        assert isinstance(step, float)
        assert isinstance(
            cur_time_step, int) and cur_time_step >= 1, 'invalid current_time_step'
        assert step > 0, 'invalid time step'
        assert isinstance(delta_a_vec, np.ndarray)
        assert isinstance(delta_b_vec, np.ndarray)
        assert isinstance(delta_c_vec, np.ndarray)
        assert isinstance(delta_c_vec, np.ndarray)
        assert isinstance(delta_gamma_a_vec, np.ndarray)
        assert isinstance(delta_gamma_b_vec, np.ndarray)
        assert isinstance(delta_gamma_c_vec, np.ndarray)
        assert isinstance(delta_gamma_d_vec, np.ndarray)
	assert isinstance(d_reach_prev, DReachSet)
        assert isinstance(d_reach_curr, DReachSet)


        assert delta_a_vec.shape == delta_b_vec.shape == \
            delta_gamma_a_vec.shape == delta_gamma_b_vec.shape == delta_gamma_c_vec.shape == \
            delta_gamma_d_vec.shape == delta_c_vec.shape == delta_d_vec.shape, 'invalid data set'

        assert isinstance(xlist, list)
        for i in xrange(0, len(xlist) - 1):
            assert xlist[i] < xlist[i + 1], 'invalid list'

        assert len(xlist) == delta_a_vec.shape[0] + \
            1, 'inconsistency between xlist and matrices shapes'

        self.step = step
        self.cur_time_step = cur_time_step
        self.xlist = xlist
        self.delta_a_vec = delta_a_vec
        self.delta_b_vec = delta_b_vec
        self.delta_gamma_a_vec = delta_gamma_a_vec
        self.delta_gamma_b_vec = delta_gamma_b_vec
        self.delta_c_vec = delta_c_vec
        self.delta_d_vec = delta_d_vec
        self.delta_gamma_c_vec = delta_gamma_c_vec
        self.delta_gamma_d_vec = delta_gamma_d_vec
	self.d_reach_prev = d_reach_prev
	self.d_reach_curr = d_reach_curr

    def get_3D_boxes(self, alpha_range, beta_range):
        'find minimum and maximum values of interpolation set U(x, t) and 3D boxes contain all U(x,t)'

        assert self.delta_a_vec is not None, 'empty interpolation set'
        assert isinstance(alpha_range, tuple) and len(
            alpha_range) == 2 and alpha_range[0] <= alpha_range[1], 'invalid alpha_range'
        assert isinstance(beta_range, tuple) and len(
            beta_range) == 2 and beta_range[0] <= beta_range[1], 'invalid beta_range'

        m = self.delta_a_vec.shape[0]		#number of mesh points

        min_vec = np.zeros((m,), dtype=float)
        max_vec = np.zeros((m,), dtype=float)
        min_points = []
        max_points = []
        boxes_3D_list = []

        for j in xrange(0, m):
            min_func = Functions.intpl_in_time_and_space_func(
                self.step,
                self.delta_a_vec[j],
                self.delta_b_vec[j],
                self.delta_gamma_a_vec[j],
                self.delta_gamma_b_vec[j],
                self.delta_c_vec[j],
                self.delta_d_vec[j], 
                self.delta_gamma_c_vec[j],
                self.delta_gamma_d_vec[j])
            max_func = Functions.intpl_in_time_and_space_func(self.step, -
                                                              self.delta_a_vec[j], -
                                                              self.delta_b_vec[j], -
                                                              self.delta_gamma_a_vec[j], -
                                                              self.delta_gamma_b_vec[j], -
                                                              self.delta_c_vec[j], -
                                                              self.delta_d_vec[j], -
                                                              self.delta_gamma_c_vec[j], -
                                                              self.delta_gamma_d_vec[j])

            x0 = [
                (self.cur_time_step - 1) * self.step,
                self.xlist[j],
                alpha_range[0],
                beta_range[0]]
            t_bnd = (
                (self.cur_time_step - 1) * self.step,
                self.cur_time_step * self.step)
            x_bnd = (self.xlist[j], self.xlist[j + 1])
            bnds = (t_bnd, x_bnd, alpha_range, beta_range)
            min_res = minimize(
                min_func,
                x0,
                method='L-BFGS-B',
                bounds=bnds,
                tol=1e-10, options={'disp': False})    # add options={'disp': True} to display optimization result
            max_res = minimize(
                max_func,
                x0,
                method='L-BFGS-B',
                bounds=bnds,
                tol=1e-10, options={'disp': False})    # add  options={'disp': True} to display optimization result

            if min_res.status == 0:
                min_vec[j] = min_res.fun
                min_points.append(min_res.x)
            else:
                print "\nmin_res.status = {}".format(min_res.status)
                print "\nminimization message: {}".format(min_res.message)
                raise ValueError(
                    'minimization for interpolation function fail!')

            if max_res.status == 0:
                max_vec[j] = -max_res.fun
                max_points.append(max_res.x)
            else:
                print "\nmax_res.status = {}".format(max_res.status)
                print "\nmaximization message: {}".format(max_res.message)
                raise ValueError(
                    'maximization for interpolation function fail!')

            ymin = (self.cur_time_step - 1) * self.step
            ymax = (self.cur_time_step) * self.step

	    if j == 0:	
		temp1, temp2 = 0, 0
		temp3, temp4 = self.get_min_max(alpha_range, beta_range, self.d_reach_prev.Vn[j].todense(), self.d_reach_prev.ln[j].todense())
		temp5, temp6 = 0, 0
		temp7, temp8 = self.get_min_max(alpha_range, beta_range, self.d_reach_curr.Vn[j].todense(), self.d_reach_curr.ln[j].todense())
	    elif 0 < j < m - 1:
		temp1, temp2 = self.get_min_max(alpha_range, beta_range, self.d_reach_prev.Vn[j - 1].todense(), self.d_reach_prev.ln[j - 1].todense())
		temp3, temp4 = self.get_min_max(alpha_range, beta_range, self.d_reach_prev.Vn[j].todense(), self.d_reach_prev.ln[j].todense())
		temp5, temp6 = self.get_min_max(alpha_range, beta_range, self.d_reach_curr.Vn[j - 1].todense(), self.d_reach_curr.ln[j - 1].todense())
		temp7, temp8 = self.get_min_max(alpha_range, beta_range, self.d_reach_curr.Vn[j].todense(), self.d_reach_curr.ln[j].todense())
	    elif j == m - 1:
		temp1, temp2 = self.get_min_max(alpha_range, beta_range, self.d_reach_prev.Vn[j - 1].todense(), self.d_reach_prev.ln[j - 1].todense())
		temp3, temp4 = 0, 0
		temp5, temp6 = self.get_min_max(alpha_range, beta_range, self.d_reach_curr.Vn[j - 1].todense(), self.d_reach_curr.ln[j - 1].todense())
		temp7, temp8 = 0, 0


	    temp = [temp1, temp2, temp3, temp4, temp5, temp6, temp7, temp8]
	    temp.sort()
	    min_vec[j] = temp[0]
	    print "\n min is {}".format(min_vec[j])
	    max_vec[j] = temp[7]
	    print "\n max is {}".format(max_vec[j])

            box_3D = RectangleSet3D()
            box_3D.set_bounds(self.xlist[j],
                              self.xlist[j + 1],
                              ymin,
                              ymax,
                              min_vec[j],
                              max_vec[j])
            boxes_3D_list.append(box_3D)

        return boxes_3D_list

    def get_min_max(self, alpha_range, beta_range, v, l):

	    x0 = [
                alpha_range[0],
                beta_range[0]]
            bnds = (alpha_range, beta_range)
	    fun_min = Function('fun_min')
            fun_min = alpha * v + beta * l
            fun_min_eval = lambdify((alpha, beta), fun_min)
	    fun_max = Function('fun_max')
            fun_max = - alpha * v - beta * l
            func_max_eval = lambdify((alpha, beta), fun_max)

            def my_func_1(y):
        	'convert to python numpy multivariable function'
        	return fun_min_eval(*tuple(y))
            def my_func_2(y):
        	'convert to python numpy multivariable function'
        	return func_max_eval(*tuple(y))
	    
            min_res = minimize(
                my_func_1,
                x0,
                method='L-BFGS-B',
                bounds=bnds,
                tol=1e-10, options={'disp': False})    # add options={'disp': True} to display optimization result	

            max_res = minimize(
                my_func_2,
                x0,
                method='L-BFGS-B',
                bounds=bnds,
                tol=1e-10, options={'disp': False})    # add  options={'disp': True} to display optimization result

            if min_res.status == 0:
                min_value = min_res.fun
            else:
                print "\nmin_res.status = {}".format(min_res.status)
                print "\nminimization message: {}".format(min_res.message)
                raise ValueError(
                    'minimization for interpolation function fail!')

            if max_res.status == 0:
                max_value = -max_res.fun
            else:
                print "\nmax_res.status = {}".format(max_res.status)
                print "\nmaximization message: {}".format(max_res.message)
                raise ValueError(
                    'maximization for interpolation function fail!')

	    return min_value, max_value



    def get_trace_func(self, alpha_value, beta_value, x_value):
        'return a trace function for specific values of alpha and beta'

        assert isinstance(alpha_value, float)
        assert isinstance(beta_value, float)
        m = len(self.xlist)
        assert isinstance(
            x_value, float) and self.xlist[0] <= x_value <= self.xlist[m - 1]

        for i in xrange(1, m):
            if self.xlist[i - 1] < x_value <= self.xlist[i]:
                delta_a = self.delta_a_vec[i]
                delta_b = self.delta_b_vec[i]
                delta_c = self.delta_c_vec[i]
                delta_d = self.delta_d_vec[i]
                delta_gamma_a = self.delta_gamma_a_vec[i]
                delta_gamma_b = self.delta_gamma_b_vec[i]
                delta_gamma_c = self.delta_gamma_c_vec[i]
                delta_gamma_d = self.delta_gamma_d_vec[i]

                break

        trace_func = Functions.trace_func(self.step, delta_a, delta_b, delta_gamma_a, delta_gamma_b,
                                          delta_c, delta_d, delta_gamma_c, delta_gamma_d, alpha_value, beta_value, x_value)

        return trace_func


class Interpolation(object):
    'implements linear interpolation method'

    @staticmethod
    def interpolate_in_space(xlist, vector_Vn, vector_ln):
        'interpolation of u(x) in space at time t = tn, 0 boundary condition for both sides'

        # at t = n*time_step, using FEM, we have U_n,i = alpha * vector_Vn,i + beta * vector_ln,i
        # i = 1, 2, ... m is discreted meshpoints

        #######################################################################
        # we want to find U_n(x) between two meshpoints i and i+1 at time t = (n*time_step)
        # using the linear interpolation in space, we have:
        # U_n(x) = (1/h[i+1]) * [(U_n,i+1 - Un,i) * x + (U_n,i * x[i + 1] - U_n,i+1 * x[i])]
        # where: x[i] <= x < x[i+1] and h[i + 1] = x[i + 1] - x[i]
        # using above U_n,i we obtain the interpolation set:
        #######################################################################
        # U_n(x) = (a_n,i * alpha + b_n,i * beta) * x + c_n,i * alpha + d_n,i * beta
        #######################################################################

        assert isinstance(xlist, list)
        for i in xrange(0, len(xlist) - 1):
            assert xlist[i] < xlist[i + 1], 'invalid list'

        assert isinstance(vector_Vn, np.ndarray)
        assert isinstance(vector_ln, np.ndarray)
        assert len(
            xlist) - 2 == vector_Vn.shape[0]/2 == vector_ln.shape[0]/2, 'inconsistent data'
        assert vector_Vn.shape[1] == vector_ln.shape[1] == 1, 'invalid vectors'

        n = len(xlist) - 1	#n is half size of vector_Vn
        Vn = vector_Vn
        ln = vector_ln
        a_n_vector = np.zeros((n,), dtype=float)
        b_n_vector = np.zeros((n,), dtype=float)
        c_n_vector = np.zeros((n,), dtype=float)
        d_n_vector = np.zeros((n,), dtype=float)

        for i in xrange(0, n):
            hi = xlist[i + 1] - xlist[i]
            if i == 0:
                a_n_vector[i] = Vn[i, 0] / hi
                b_n_vector[i] = ln[i, 0] / hi
                c_n_vector[i] = 0.0
                d_n_vector[i] = 0.0
            elif 0 < i < n - 1:
                a_n_vector[i] = (Vn[i, 0] - Vn[i - 1, 0]) / hi
                b_n_vector[i] = (ln[i, 0] - ln[i - 1, 0]) / hi
                c_n_vector[i] = (Vn[i - 1, 0] * xlist[i + 1] -
                                 Vn[i, 0] * xlist[i]) / hi
                d_n_vector[i] = (ln[i - 1, 0] * xlist[i + 1] -
                                 ln[i, 0] * xlist[i]) / hi

            elif i == n - 1:
                a_n_vector[i] = - Vn[i - 1, 0] / hi
                b_n_vector[i] = - ln[i - 1, 0] / hi
                c_n_vector[i] = (i + 1) * Vn[i - 1, 0]
                d_n_vector[i] = (i + 1) * ln[i - 1, 0]

        interpol_inspace_set = InterpolSetInSpace()
        interpol_inspace_set.set_values(
            xlist,
            a_n_vector,
            b_n_vector,
            c_n_vector,
            d_n_vector)

        return interpol_inspace_set

    @staticmethod
    def increm_interpolation(
            step, cur_time_step, prev_intpl_inspace_set, cur_intpl_inspace_set, d_reach_prev, d_reach_curr):
        'incrementally doing interpolation'

        assert isinstance(prev_intpl_inspace_set, InterpolSetInSpace)
        assert isinstance(cur_intpl_inspace_set, InterpolSetInSpace)
	assert isinstance(d_reach_prev, DReachSet)
        assert isinstance(d_reach_curr, DReachSet)
        assert cur_intpl_inspace_set.xlist == prev_intpl_inspace_set.xlist, 'inconsistent data'

        assert isinstance(
            cur_time_step, int) and cur_time_step >= 1, 'invalid current_time_step'
        assert isinstance(step, float) and step > 0, 'invalid time step'
        xlist = cur_intpl_inspace_set.xlist
        delta_a_vec = prev_intpl_inspace_set.a_vec - cur_intpl_inspace_set.a_vec
        delta_b_vec = prev_intpl_inspace_set.b_vec - cur_intpl_inspace_set.b_vec
        delta_gamma_a_vec = np.multiply(cur_intpl_inspace_set.a_vec, cur_time_step) - np.multiply(
            prev_intpl_inspace_set.a_vec, cur_time_step - 1)
        delta_gamma_b_vec = np.multiply(
            cur_intpl_inspace_set.b_vec, cur_time_step) - np.multiply(
            prev_intpl_inspace_set.b_vec, cur_time_step - 1)
        delta_c_vec = prev_intpl_inspace_set.c_vec - cur_intpl_inspace_set.c_vec
        delta_d_vec = prev_intpl_inspace_set.d_vec - cur_intpl_inspace_set.d_vec
        delta_gamma_c_vec = np.multiply(
            cur_intpl_inspace_set.c_vec, cur_time_step) - np.multiply(
            prev_intpl_inspace_set.c_vec, cur_time_step - 1)
        delta_gamma_d_vec = np.multiply(
            cur_intpl_inspace_set.d_vec, cur_time_step) - np.multiply(
            prev_intpl_inspace_set.d_vec, cur_time_step - 1)

        intpl_set = InterpolationSet()
        intpl_set.set_values(
            step,
            cur_time_step,
            xlist,
            delta_a_vec,
            delta_b_vec,
            delta_gamma_a_vec,
            delta_gamma_b_vec,
            delta_c_vec,
            delta_d_vec,
            delta_gamma_c_vec,
            delta_gamma_d_vec,
	    d_reach_prev, 
	    d_reach_curr)

        return intpl_set
