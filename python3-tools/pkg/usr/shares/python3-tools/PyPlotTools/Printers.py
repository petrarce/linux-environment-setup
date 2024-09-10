import matplotlib.pyplot as plt
import numpy as np


def plot_vectors(vectors, colors, xMin=-1, xMax=1, yMin=-1, yMax=1):
    """
    Plot one or more vectors in a 2D plane, specifying a color for each.

    Arguments
    ---------
    vectors: list of lists or of arrays
        Coordinates of the vectors to plot. For example, [[1, 3], [2, 2]]
        contains two vectors to plot, [1, 3] and [2, 2].
    colors: list
        Colors of the vectors. For instance: ['red', 'blue'] will display the
        first vector in red and the second in blue.

    Example
    -------
    plot_vectors([[1, 3], [2, 2]], ['red', 'blue'])
    plt.xlim(-1, 4)
    plt.ylim(-1, 4)
    """
    plt.figure()
    plt.axvline(x=0, color="lightgray")
    plt.axhline(y=0, color="lightgray")

    for i in range(len(vectors)):
        x = np.concatenate([[0, 0], vectors[i]])
        plt.quiver(
            [x[0]],
            [x[1]],
            [x[2]],
            [x[3]],
            angles="xy",
            scale_units="xy",
            scale=1,
            color=colors[i],
        )
    plt.xlim(xMin, xMax)
    plt.ylim(yMin, yMax)

    plt.show()
