import numpy as np

type Position = tuple[int | float, int | float]


class MathHelper:
    @staticmethod
    def cross2d(x, y):
        """Return analog cross product of two 2D vectors."""
        return x[..., 0] * y[..., 1] - x[..., 1] * y[..., 0]

    @staticmethod
    def is_within_polygon(
            point: Position,
            edges: list[tuple[Position, Position]]
    ) -> bool:
        """Return whether a point is inside a polygon via raycasting.

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

        # Count number of intersections
        intersections: int = 0

        # Create ray in arbitrary nonzero direction
        p = np.array(point)
        ray_direction = np.array(
            [1 - np.random.random(), 1 - np.random.random()]
        )

        for i, edge in enumerate(edges):

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

    @staticmethod
    def check_edge_valence(edges):
        """Verify that all edges have two vertices."""
        counts = {}
        for edge in edges:
            for v in edge:
                counts[v] = counts.get(v, 0) + 1
        return all(n == 2 for n in counts.values())
