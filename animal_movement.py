import pygame


class AnimalMovement:
    def __init__(self):
        pass

    @staticmethod
    def rotate_image(image, angle, pivot):
        """
        Rotate an image around a pivot point.

        :param image: Pygame surface
        :param angle: degrees to rotate
        :param pivot: (x, y) tuple to rotate around
        :return: rotated image, new rect
        """
        rect = image.get_rect(topleft=(0, 0))

        offset_center_to_pivot = pygame.math.Vector2(rect.center) - pivot

        rotated_offset = offset_center_to_pivot.rotate(-angle)

        rotated_center = (pivot[0] + rotated_offset.x, pivot[1] + rotated_offset.y)

        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=rotated_center)

        return rotated_image, rotated_rect
