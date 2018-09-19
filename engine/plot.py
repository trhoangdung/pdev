'''
This module implements Plot class and its methods
Dung Tran: Nov/2017
'''

from matplotlib.patches import Rectangle
from matplotlib.axes import Axes
from engine.set import RectangleSet2D, RectangleSet3D, LineSet
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d.axes3d import Axes3D
from engine.verifier import VerificationResult
from engine.specification import SafetySpecification
import numpy as np


class Plot(object):
    'implements methods for ploting different kind of set'

    @staticmethod
    def plot_boxes(ax, rectangle_set_list, facecolor, edgecolor):
        'plot reachable set using rectangle boxes'

        # return axes object to plot a figure
        n = len(rectangle_set_list)
        assert n > 0, 'empty set'
        assert isinstance(ax, Axes)

        for i in xrange(0, n):
            assert isinstance(rectangle_set_list[i], RectangleSet2D)

        xmin = []
        xmax = []
        ymin = []
        ymax = []

        for i in xrange(0, n):
            xmin.append(rectangle_set_list[i].xmin)
            xmax.append(rectangle_set_list[i].xmax)
            ymin.append(rectangle_set_list[i].ymin)
            ymax.append(rectangle_set_list[i].ymax)

            patch = Rectangle(
                (xmin[i],
                 ymin[i]),
                xmax[i] - xmin[i],
                ymax[i] - ymin[i],
                facecolor=facecolor,
                edgecolor=edgecolor,
                fill=True)
            ax.add_patch(patch)

        xmin.sort()
        xmax.sort()
        ymin.sort()
        ymax.sort()
        min_x = xmin[0]
        max_x = xmax[len(xmax) - 1]
        min_y = ymin[0]
        max_y = ymax[len(ymax) - 1]

        ax.set_xlim(min_x - 0.1 * abs(min_x), max_x + 0.1 * abs(max_x))
        ax.set_ylim(min_y - 0.1 * abs(min_y), max_y + 0.1 * abs(max_y))

        return ax

    @staticmethod
    def plot_vlines(ax, x_pos_list, lines_list, colors, linestyles):
        'plot vline at x'

        assert isinstance(ax, Axes)
        assert isinstance(x_pos_list, list)
        assert isinstance(lines_list, list)
        assert len(x_pos_list) == len(lines_list), 'inconsistent data, len_x = {} != len(line) = {}'.format(len(x_pos_list), len(lines_list))
        n = len(x_pos_list)
        ymin_list = []
        ymax_list = []
        for i in xrange(0, n):
            assert isinstance(lines_list[i], LineSet)
            ymin_list.append(lines_list[i].xmin)
            ymax_list.append(lines_list[i].xmax)

        ax.vlines(
            x_pos_list,
            ymin_list,
            ymax_list,
            colors=colors,
            linestyles=linestyles,
            linewidth=2)

        x_pos_list.sort()
        ymin_list.sort()
        ymax_list.sort()
        xmin = x_pos_list[0]
        xmax = x_pos_list[n - 1]
        ymin = ymin_list[0]
        ymax = ymax_list[n - 1]

        ax.set_xlim(xmin - 0.1 * abs(xmin), xmax + 0.1 * abs(xmax))
        ax.set_ylim(ymin - 0.1 * abs(ymin), ymax + 0.1 * abs(ymax))

        return ax

    @staticmethod
    def plot_3d_boxes(ax, boxes_list, facecolor, linewidth, edgecolor):	
        'plot 3d boxes contain reachable set'

        assert isinstance(boxes_list, list)
        assert isinstance(ax, Axes3D)
        for box in boxes_list:
            assert isinstance(box, RectangleSet3D)
            xmin = box.xmin
            xmax = box.xmax
            ymin = box.ymin
            ymax = box.ymax
            zmin = box.zmin
            zmax = box.zmax
            p1 = [xmin, ymin, zmin]
            p2 = [xmin, ymin, zmax]
            p3 = [xmin, ymax, zmin]
            p4 = [xmin, ymax, zmax]
            p5 = [xmax, ymin, zmin]
            p6 = [xmax, ymin, zmax]
            p7 = [xmax, ymax, zmin]
            p8 = [xmax, ymax, zmax]
            V = np.array([p1, p2, p3, p4, p5, p6, p7, p8])
            #ax.scatter3D(V[:, 0], V[:, 1], V[:, 2])
            verts = [
                [
                    V[0], V[1], V[6], V[4]], [
                    V[0], V[2], V[6], V[4]], [
                    V[0], V[1], V[3], V[2]], [
                    V[4], V[5], V[7], V[6]], [
                        V[2], V[3], V[7], V[6]], [
                            V[1], V[3], V[7], V[5]]]

            ax.add_collection3d(
                Poly3DCollection(
                    verts,
                    facecolors=facecolor,
                    linewidths=linewidth,
                    edgecolors=edgecolor))

        x_min_list = []
        x_max_list = []
        y_min_list = []
        y_max_list = []
        z_min_list = []
        z_max_list = []

        for box in boxes_list:
            x_min_list.append(box.xmin)
            x_max_list.append(box.xmax)
            y_min_list.append(box.ymin)
            y_max_list.append(box.ymax)
            z_min_list.append(box.zmin)
            z_max_list.append(box.zmax)

        x_min_list.sort()
        x_max_list.sort()
        y_min_list.sort()
        y_max_list.sort()
        z_min_list.sort()
        z_max_list.sort()

        min_x = x_min_list[0]
        max_x = x_max_list[len(x_max_list) - 1]
        min_y = y_min_list[0]
        max_y = y_max_list[len(y_max_list) - 1]
        min_z = z_min_list[0]
        max_z = z_max_list[len(z_max_list) - 1]

        ax.set_xlim(min_x - 0.1 * abs(min_x), max_x + 0.1 * abs(max_x))
        ax.set_ylim(min_y - 0.1 * abs(min_y), max_y + 0.1 * abs(max_y))
        ax.set_ylim(min_z - 0.1 * abs(min_z), max_z + 0.1 * abs(max_z))

        return ax

    @staticmethod
    def plot_interpolationset(ax, interpolationset_list, facecolor, linewidth, edgecolor):
        'plot interpolation set'

        assert isinstance(interpolationset_list, list)
        assert isinstance(ax, Axes3D)

        for boxes_list in interpolationset_list:	
            ax = Plot.plot_3d_boxes(ax, boxes_list, facecolor, linewidth, edgecolor)

        return ax

    @staticmethod
    def plot_unsafe_region(ax, safety_sp):
        'plot unsafe region'

        # todo: automatic adjust filled region
        assert isinstance(ax, Axes)
        assert isinstance(safety_sp, SafetySpecification)
        u1 = safety_sp.u1
        u2 = safety_sp.u2

        if u1 is not None and u2 is not None:
            y = [u1 - 1, u1, u2, u2 + 1]
            ax.fill_between(safety_sp.t_range, y[0], y[1], facecolor='r', edgecolor='r')
            ax.fill_between(safety_sp.t_range, y[2], y[3], facecolor='r', edgecolor='r')

        return ax

    @staticmethod
    def plot_unsafe_trace(ax, verification_result):
        'plot the unsafe trace and the safety specification and an unsafe point'

        assert isinstance(verification_result, VerificationResult)
        assert isinstance(ax, Axes)
        res = verification_result
        assert res.unsafe_trace_funcs != [], 'verification result is empty'

        unsafe_trace = res.generate_numerical_trace()
        unsafe_point = res.get_unsafe_point()
        safety_sp = res.get_specification()
        assert safety_sp is not None, 'safety region is empty'

        ax = Plot.plot_unsafe_region(ax, safety_sp)
        ax.plot(unsafe_trace[0], unsafe_trace[1], linestyle='solid', lw=2, marker='*')
        ax.set_ylabel('$u(x={},t)$'.format(unsafe_point[1]))
        ax.set_xlabel('$t$')

        return ax
