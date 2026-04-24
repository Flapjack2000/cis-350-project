import unittest
import pygame

from checklist import Checklist
from scene import Scene, SceneManager, GameContext
from audio_player import AudioPlayer


class TestChecklist(unittest.TestCase):
    """Checklist tests."""

    # To allow Checklist's usage of pygame.mixer in complete_task
    pygame.init()

    # There are 28 possible tasks in the game
    tasks = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "10", "11", "12", "13", "14", "15", "16", "17",
        "18", "19", "20", "21", "22", "23", "24", "25",
        "26", "27"
    ]

    def test_task_completion(self):
        """Verify that the checklist updates when tasks are marked complete."""

        cl = Checklist(self.tasks)

        # All tasks start incomplete
        self.assertEqual(
            first=len(cl.get_phase_tasks()),
            second=len(cl.get_incomplete_tasks())
        )

        # Complete first task
        cl.complete_task(cl.get_phase_tasks()[0])

        # One task is complete
        self.assertEqual(
            first=1,
            second=len(cl.get_completed_tasks())
        )

        # One task is not incomplete
        self.assertEqual(
            first=len(cl.get_phase_tasks()) - 1,
            second=len(cl.get_incomplete_tasks())
        )

        # Complete second task
        cl.complete_task(cl.get_phase_tasks()[1])

        # Two tasks are complete
        self.assertEqual(
            first=2,
            second=len(cl.get_completed_tasks())
        )

        # Two tasks are not incomplete
        self.assertEqual(
            first=len(cl.get_phase_tasks()) - 2,
            second=len(cl.get_incomplete_tasks())
        )

        # Complete third task
        cl.complete_task(cl.get_phase_tasks()[3])

        # Three tasks are complete
        self.assertEqual(
            first=3,
            second=len(cl.get_completed_tasks())
        )

        # Three tasks are not incomplete
        self.assertEqual(
            first=len(cl.get_phase_tasks()) - 3,
            second=len(cl.get_incomplete_tasks())
        )

    def test_day_night_cycle(self):
        """Verify that the day/night cycle works automatically."""

        cl = Checklist(self.tasks)

        # Daytime phase of day 1
        self.assertTrue(cl.is_day)
        self.assertEqual(cl.day_count, 1)

        # Complete all tasks
        for task in cl.get_phase_tasks():
            cl.complete_task(task)

        # Nighttime phase of day 1
        self.assertFalse(cl.is_day)
        self.assertEqual(cl.day_count, 1)

        # Complete all tasks
        for task in cl.get_phase_tasks():
            cl.complete_task(task)

        # Daytime phase of day 2
        self.assertTrue(cl.is_day)
        self.assertEqual(cl.day_count, 2)

        # Complete all tasks
        for task in cl.get_phase_tasks():
            cl.complete_task(task)

        # Nighttime phase of day 2
        self.assertFalse(cl.is_day)
        self.assertEqual(cl.day_count, 2)

        # Complete all tasks
        for task in cl.get_phase_tasks():
            cl.complete_task(task)

        # Daytime phase of day 3
        self.assertTrue(cl.is_day)
        self.assertEqual(cl.day_count, 3)

        # Complete all tasks
        for task in cl.get_phase_tasks():
            cl.complete_task(task)

        # Nighttime phase of day 3
        self.assertFalse(cl.is_day)
        self.assertEqual(cl.day_count, 3)

    def test_load_tasks(self):
        """Verify that tasks are loaded correctly."""

        cl = Checklist(self.tasks)

        # Check tasks get saved to pool
        self.assertListEqual(
            cl.get_task_pool(),
            self.tasks
        )

        # Check that tasks get split between day and night
        self.assertEqual(
            Checklist.DAY_TASKS_REQUIRED,
            len(cl.get_phase_tasks())
        )

        for task in cl.get_phase_tasks():
            cl.complete_task(task)

        self.assertEqual(
            Checklist.NIGHT_TASKS_REQUIRED,
            len(cl.get_phase_tasks())
        )


class TestSceneManager(unittest.TestCase):
    """SceneManager tests."""

    tasks = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "10", "11", "12", "13", "14", "15", "16", "17",
        "18", "19", "20", "21", "22", "23", "24", "25",
        "26", "27"
    ]

    class BlankScene(Scene):
        """Dummy scene implementation for testing SceneManager."""

        def __init__(self, manager: SceneManager):
            super().__init__(manager)

        def handle_events(self, events: list[pygame.event.Event]) -> None:
            pass

        def update(self, dt: float) -> None:
            pass

        def draw(self, screen: pygame.Surface) -> None:
            pass

    def test_push(self):
        """Verify that pushing scenes works correctly."""

        # Example context for SceneManager initialization
        context = GameContext(
            checklist=Checklist(self.tasks),
            cursor=pygame.Surface((1, 1)),
            music_player=AudioPlayer()
        )

        # Create manager
        manager = SceneManager(context)

        # Scene stack is empty
        self.assertTrue(manager.is_empty)
        self.assertEqual(0, len(manager))
        self.assertIsNone(manager.current)

        # Push first scene
        manager.push(self.BlankScene(manager))

        # Scene stack has one scene
        self.assertFalse(manager.is_empty)
        self.assertEqual(1, len(manager))

        # Push second scene
        manager.push(self.BlankScene(manager))

        # Scene stack has two scenes
        self.assertFalse(manager.is_empty)
        self.assertEqual(2, len(manager))

        # Push third scene
        manager.push(self.BlankScene(manager))

        # Scene stack has three scenes
        self.assertFalse(manager.is_empty)
        self.assertEqual(3, len(manager))

    def test_pop(self):
        """Verify that popping scenes works correctly."""

        # Example context for SceneManager initialization
        context = GameContext(
            checklist=Checklist(self.tasks),
            cursor=pygame.Surface((1, 1)),
            music_player=AudioPlayer()
        )

        # Create empty manager
        manager = SceneManager(context)
        self.assertTrue(manager.is_empty)
        self.assertEqual(len(manager), 0)
        self.assertIsNone(manager.current)

        # Push five scenes
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))

        # Check stack length
        self.assertFalse(manager.is_empty)
        self.assertEqual(len(manager), 5)
        self.assertIsNotNone(manager.current)

        # Pop scene 5
        manager.pop()
        self.assertFalse(manager.is_empty)
        self.assertEqual(len(manager), 4)
        self.assertIsNotNone(manager.current)

        # Pop scene 4
        manager.pop()
        self.assertFalse(manager.is_empty)
        self.assertEqual(len(manager), 3)
        self.assertIsNotNone(manager.current)

        # Pop scene 3
        manager.pop()
        self.assertFalse(manager.is_empty)
        self.assertEqual(len(manager), 2)
        self.assertIsNotNone(manager.current)

        # Pop scene 2
        manager.pop()
        self.assertFalse(manager.is_empty)
        self.assertEqual(len(manager), 1)
        self.assertIsNotNone(manager.current)

        # Pop scene 1
        manager.pop()
        self.assertTrue(manager.is_empty)
        self.assertEqual(len(manager), 0)
        self.assertIsNone(manager.current)

    def test_exit_all(self):
        """Verify that exiting all scenes works correctly."""

        # Example context for SceneManager initialization
        context = GameContext(
            checklist=Checklist(self.tasks),
            cursor=pygame.Surface((1, 1)),
            music_player=AudioPlayer()
        )

        # Create empty manager
        manager = SceneManager(context)
        self.assertTrue(manager.is_empty)
        self.assertEqual(len(manager), 0)
        self.assertIsNone(manager.current)

        # Push five scenes
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))
        manager.push(self.BlankScene(manager))

        # Check stack length
        self.assertFalse(manager.is_empty)
        self.assertEqual(len(manager), 5)
        self.assertIsNotNone(manager.current)

        # Empty manager
        manager.exit_all()
        self.assertTrue(manager.is_empty)
        self.assertEqual(len(manager), 0)
        self.assertIsNone(manager.current)


import unittest
import numpy as np
import pygame

from math_helper import MathHelper


class TestMathHelper(unittest.TestCase):
    """MathHelper tests."""

    pygame.init()

    # Triangle edges used across several tests
    TRIANGLE = [
        ((0, 0), (4, 0)),
        ((4, 0), (2, 4)),
        ((2, 4), (0, 0)),
    ]

    # Simple convex quadrilateral
    QUAD = [
        ((0, 0), (6, 0)),
        ((6, 0), (6, 6)),
        ((6, 6), (0, 6)),
        ((0, 6), (0, 0)),
    ]

    def test_cross2d_orthogonal(self):
        """Orthogonal unit vectors should have cross product of 1."""
        x = np.array([1.0, 0.0])
        y = np.array([0.0, 1.0])
        result = MathHelper.cross2d(x, y)
        self.assertAlmostEqual(float(result), 1.0)

    def test_cross2d_parallel(self):
        """Parallel vectors should have a cross product of 0."""
        x = np.array([3.0, 0.0])
        y = np.array([6.0, 0.0])
        result = MathHelper.cross2d(x, y)
        self.assertAlmostEqual(float(result), 0.0)

    def test_cross2d_anticommutative(self):
        """Swapping operands should negate the result."""
        x = np.array([2.0, 3.0])
        y = np.array([4.0, 1.0])
        self.assertAlmostEqual(
            float(MathHelper.cross2d(x, y)),
            -float(MathHelper.cross2d(y, x))
        )

    def test_cross2d_invalid_dimension(self):
        """Non-2D inputs should raise ValueError."""
        with self.assertRaises(ValueError):
            MathHelper.cross2d(np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0]))

    def test_cross2d_invalid_2d_array(self):
        """2D matrix inputs should raise ValueError."""
        with self.assertRaises(ValueError):
            MathHelper.cross2d(np.array([[1.0, 0.0]]), np.array([[0.0, 1.0]]))

    def test_check_edge_valence_valid_triangle(self):
        """A properly connected triangle should pass valence check."""
        edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
        self.assertTrue(MathHelper.check_edge_valence(edges))

    def test_check_edge_valence_valid_square(self):
        """A properly connected square should pass valence check."""
        edges = [
            ((0, 0), (1, 0)),
            ((1, 0), (1, 1)),
            ((1, 1), (0, 1)),
            ((0, 1), (0, 0)),
        ]
        self.assertTrue(MathHelper.check_edge_valence(edges))

    def test_check_edge_valence_dangling_vertex(self):
        """A polygon with a vertex appearing only once should fail."""

        # (2, 2) only appears once
        edges = [((0, 0), (1, 0)), ((1, 0), (2, 2)), ((0, 0), (0, 1))]
        self.assertFalse(MathHelper.check_edge_valence(edges))

    def test_is_within_polygon_inside_triangle(self):
        """Verify point inside a triangle."""
        self.assertTrue(MathHelper.is_within_polygon((2, 1), self.TRIANGLE))

    def test_is_within_polygon_outside_triangle(self):
        """Verify point outside a triangle."""
        self.assertFalse(MathHelper.is_within_polygon((10, 10), self.TRIANGLE))

    def test_is_within_polygon_inside_quad(self):
        """Verify point inside a square."""
        self.assertTrue(MathHelper.is_within_polygon((3, 3), self.QUAD))

    def test_is_within_polygon_outside_quad(self):
        """Verify point outside a square."""
        self.assertFalse(MathHelper.is_within_polygon((-1, -1), self.QUAD))

    def test_is_within_polygon_too_few_edges(self):
        """Fewer than 3 edges should raise ValueError."""
        with self.assertRaises(ValueError):
            MathHelper.is_within_polygon(
                (0, 0),
                [((0, 0), (1, 0)), ((1, 0), (2, 0))]
            )

    def test_is_within_polygon_invalid_valence(self):
        """A non-closed polygon should raise ValueError."""

        # Missing closing edge back to (0,0)
        open_shape = [
            ((0, 0), (4, 0)),
            ((4, 0), (4, 4)),
            ((4, 4), (0, 4)),
            ((0, 4), (0, 2)),
        ]
        with self.assertRaises(ValueError):
            MathHelper.is_within_polygon((2, 2), open_shape)

    def test_rotate_image_zero_degrees(self):
        """Rotating 0 degrees should return an image of the same size."""
        surface = pygame.Surface((100, 60))
        pivot = pygame.Vector2(50, 30)
        rotated, rect = MathHelper.rotate_image(surface, 0, pivot)
        self.assertEqual(rotated.get_size(), surface.get_size())
        self.assertIsInstance(rect, pygame.Rect)

    def test_rotate_image_360_degrees(self):
        """A full rotation should produce
        the same dimensions as the original."""
        surface = pygame.Surface((100, 60))
        pivot = pygame.Vector2(50, 30)
        rotated, _ = MathHelper.rotate_image(surface, 360, pivot)
        self.assertEqual(rotated.get_size(), surface.get_size())

    def test_rotate_image_90_degrees(self):
        """A non-square surface rotated 90 degrees
        should swap its width and height."""
        surface = pygame.Surface((100, 40))
        pivot = pygame.Vector2(50, 20)
        rotated, _ = MathHelper.rotate_image(surface, 90, pivot)
        orig_w, orig_h = surface.get_size()
        rot_w, rot_h = rotated.get_size()
        self.assertEqual(rot_w, orig_h)
        self.assertEqual(rot_h, orig_w)


if __name__ == '__main__':
    unittest.main()
