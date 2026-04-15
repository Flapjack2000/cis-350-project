import numpy as np
import numpy.typing as npt

type Position = tuple[int | float, int | float]


class MathHelper:
    """
    Math helper functions
    """
    @staticmethod
    def cross2d(
            x: npt.NDArray[np.floating],
            y: npt.NDArray[np.floating],
    ) -> npt.NDArray[np.floating]:
        """Return analog cross product (determinant) of two 2D vectors.

        Args:
            x (npt.NDArray[np.floating]): first 2D vector
            y (npt.NDArray[np.floating]): second 2D vector

        Returns:
            npt.NDArray[np.floating]: scalar cross product
        """

        # Verify vector dimension
        if x.ndim != 1 or y.ndim != 1 or x.shape[0] != 2 or y.shape[0] != 2:
            raise ValueError(
                "Inputs must be 1D arrays of length 2 (2D vectors)."
            )

        # Calculate and return 2D cross product
        return x[..., 0] * y[..., 1] - x[..., 1] * y[..., 0]

    @staticmethod
    def check_edge_valence(edges: list[tuple[Position, Position]]):
        """Verify polygon connection.

        Args:
            edges (list[tuple[Position, Position]]): a list of polygon edges

        Returns:
            bool: whether the polygon is properly connected
        """

        # Count vertices
        counts = {}
        for edge in edges:
            for v in edge:
                counts[v] = counts.get(v, 0) + 1

        # Make sure every vertex shows up exactly twice
        return all(n == 2 for n in counts.values())

    @staticmethod
    def is_within_polygon(
            point: Position,
            edges: list[tuple[Position, Position]]
    ) -> bool:
        """Return whether a point is inside a polygon via raycasting.
        Works for convex polygons, concave polygons, and polygons with holes.

        Args:
            point (Position): the point to check, e.g. a mouse click position
            edges (list[tuple[Position, Position]]): the polygon's edges

        Returns:
            bool: whether the point is inside the polygon

        Solution derived from:
            https://math.stackexchange.com/q/4003918
            https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        """

        # Check that it's truly a polygon
        if len(edges) < 3:
            raise ValueError(
                "A polygon requires at least 3 edges."
            )
        if not MathHelper.check_edge_valence(edges):
            raise ValueError(
                "A vertex cannot be incident to more than 2 edges."
            )

        # Create point vector
        p = np.array(point)

        # Use faster method for triangles
        if len(edges) == 3:
            # Extract vertices from edges
            vertices = list({v for edge in edges for v in edge})
            a, b, c = [np.array(v) for v in vertices]

            # Compute cross products
            pa = p - a
            pb = p - b
            o1 = float(MathHelper.cross2d(b - a, pa))
            o3 = float(MathHelper.cross2d(a - c, pa))
            o2 = float(MathHelper.cross2d(c - b, pb))

            # Check that point is on same side of all three edges
            min_o = min(o1, o2, o3)
            max_o = max(o1, o2, o3)
            return min_o >= 0 or max_o <= 0

        # Count number of intersections
        intersections: int = 0

        # Create ray in arbitrary nonzero direction
        ray_direction = np.array(
            [1 - np.random.random(), 1 - np.random.random()]
        )

        # Check every edge for an intersection
        for edge in edges:

            # Edge point vectors
            v1 = np.array(edge[0])
            v2 = np.array(edge[1])
            edge_direction = v2 - v1

            # Check whether line extensions along the ray and edge intersect
            denom = MathHelper.cross2d(edge_direction, ray_direction)

            # Skip edge if ray and edge are parallel
            if denom == 0:
                continue

            # Compute intersection between ray and edge line extensions
            t = MathHelper.cross2d((p - v1), ray_direction) / denom
            u = MathHelper.cross2d((p - v1), edge_direction) / denom

            # Check that intersection is between edge's vertices
            if 0 <= t <= 1:
                # Check that intersection is in the ray's direction
                if u >= 0:
                    intersections += 1

        # Point is inside if ray intersects an odd number of edges
        return intersections % 2 == 1
