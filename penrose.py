import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

ANGLE_OFFSET = np.pi/2.0
SYMMETRY = 5

def construction_line(x, j, k, sigma, symmetry=SYMMETRY, angle_offset=ANGLE_OFFSET):
    angle = (j * 2.0 * np.pi/symmetry) + angle_offset
    return (k - sigma - x * np.cos(angle)) / np.sin(angle)


def get_indices(r, sigmas, es, symmetry=SYMMETRY, angle_offset=ANGLE_OFFSET):
    """
    Returns the indices for any point on the plane.
    [a j0, b j1, c j2, d j3, e j4] where a,b,c,d,e are integers.
    `es` are the normal vectors for each line.
    """
    
    # Dot product with the unit vector will return the index without the original sigma shift, so then add the shift.
    # Note that since k is an integer, the distance between the lines is just 1 so it is already normalised.
    indices = np.zeros(5, dtype=int)
    i = 0
    for e in es:
        indices[i] = int(np.floor(np.dot(r, e) + sigmas[i]))
        i += 1

    return indices


class Intersection:
    """
    Takes r vector position, and the j and k values of the lines that intersect each other
    """
    def __init__(self, j1, k1, j2, k2, sigma1, sigma2, symmetry=SYMMETRY):  # Init calculates the intersection from given params
        self.r, self.rhomb_type = self.find_intersection(j1, k1, j2, k2, sigma1, sigma2, symmetry)
        self.j1 = j1
        self.j2 = j2
        self.k1 = k1
        self.k2 = k2
        self.sigma1 = sigma1
        self.sigma2 = sigma2

    def __repr__(self):
        return "%s" % self.r

    def find_intersection(self, j1, k1, j2, k2, sigma1, sigma2, symmetry=SYMMETRY, angle_offset=ANGLE_OFFSET):
        """
        Returns position vector of intersection between line j1,k1 and j2,k2, along with the rhombus type.
        rhomb_type is stored as "thin" or "thick", where the name corresponds to the thin/thick rhombus respectively.
        """
        a1 = (j1 * 2.0 * np.pi/symmetry) + angle_offset
        a2 = (j2 * 2.0 * np.pi/symmetry) + angle_offset
        angle_diff_index = ((a2 - a1) % np.pi)/np.pi
        rhomb_type = "thin"
        if angle_diff_index == 0.6 or angle_diff_index == 0.4:  # 0.6 and 0.4 are equivalent and both thick
            rhomb_type = "thick"

        x = ( (k1 - sigma1)/np.sin(a1) - (k2 - sigma2)/np.sin(a2) ) / ( (1.0/np.tan(a1)) - (1.0/np.tan(a2)) )

        return np.array([x, construction_line(x, j1, k1, sigma1, symmetry=SYMMETRY)]), rhomb_type

    def find_surrounding_indices(self, sigmas, symmetry=SYMMETRY, angle_offset=ANGLE_OFFSET):
        """
        Finds the indices for the spaces surrounding this intersection.
        Each intersection will be the corner between 4 spaces. Those 4 spaces will be either side
        of the two lines that intersected.
        """
        # Get indices that the point is located at
        point_indices = get_indices(self.r, sigmas, symmetry, angle_offset)
        point_indices[self.j1] = self.k1  # These are already known
        point_indices[self.j2] = self.k2
        # The indices of the spaces surrounding the points are then (for j1 = 0, j2 = 1):
        # [k1 + 1 or 0, k2 + 1 or 0, point_indices...]
        # There should be 4 total
        # had to copy each member of point_indices due to it just putting the array in by reference each time
        surrounding_indices = np.array([np.array([point_indices[j] for j in range(len(point_indices))]) for i in range(4)])
        # Do each permutation
        surrounding_indices[1][self.j1] += 1
        surrounding_indices[2][self.j2] += 1
        surrounding_indices[3][self.j1] += 1
        surrounding_indices[3][self.j2] += 1
        return surrounding_indices


def vertex_position_from_pentagrid(indices, es):
    """
    Calculates vertex positions in real space from pentagrid indices.
    """
    vertex = np.zeros(2)    # vector in 2D space
    for i in range(len(indices)):
        vertex += es[i] * indices[i]

    return vertex

"""
Plan:
1) Find intersections of line with another
2) Calculate what indices this line is by finding the neighbouring lines to that point.
3) Use those indices in de Bruijn's formula to find the vertices in 2D space.
"""

# Define normal unit vectors for each of the sets. Required for finding indices
es = [np.array([ np.cos( (j * 2 * np.pi/SYMMETRY) + ANGLE_OFFSET ), np.sin( (j * 2 * np.pi/SYMMETRY) + ANGLE_OFFSET ) ]) for j in range(SYMMETRY)]

rng = np.random.default_rng(32187)

K_RANGE = 1

sigmas = np.zeros(SYMMETRY)

for j in range(SYMMETRY):
    offset = 1 + rng.random() * 2
    sigmas[j] = offset
    # for k in range(K_RANGE):
    #     plt.plot(xspace, construction_line(xspace, j, k, offset), color=["r", "g", "b", "m", "y"][j])

plt.legend()

# Just find intersections along one line for now
# Let's choose j1 = 1, k1 = 1 and compare that with every other line
# Haven't drawn set 0 properly yet so set 1 is fine
x_intersections = []
y_intersections = []
intersections = []



for j1 in range(SYMMETRY):
    for j2 in range(j1 + 1, SYMMETRY):   # Compares 0 1, 0 2, 0 3, 0 4, 1 2, 1 3, ... 3 4
        for k1 in range(K_RANGE):
            for k2 in range(K_RANGE):   # Go through each line of the set j2
                intersection = Intersection(j1, k1, j2, k2, sigmas[j1], sigmas[j2])
                intersections.append(intersection)
                x_intersections.append(intersection.r[0])
                y_intersections.append(intersection.r[1])

# plt.plot(x_intersections, y_intersections, "xr")

indices = [i.find_surrounding_indices(sigmas, es) for i in intersections]

vertices = []
for indices_set in indices:
    for i in indices_set:
        vertices.append( vertex_position_from_pentagrid(i, es) )


x= []
y = []
for v in vertices:
    x.append(v[0])
    y.append(v[1])

plt.plot(x, y, ".")
plt.show()