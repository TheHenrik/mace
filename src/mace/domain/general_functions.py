import numpy as np

def rotate_vector(vector: np.ndarray, alpha: float, beta: float, gamma: float) -> np.ndarray:
    """
    Rotates a vector around the x-, y- and z-axis.
    First: Rotation around the x-axis, then around the y-axis and finally around the z-axis.
    :param vector: Vector to be rotated
    :param alpha: Rotation around the x-axis in degrees
    :param beta: Rotation around the y-axis in degrees
    :param gamma: Rotation around the z-axis in degrees
    """
    
    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)
    gamma_rad = np.radians(gamma)

    # Drehmatrizen um die x-, y- und z-Achsen
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(alpha_rad), -np.sin(alpha_rad)],
                   [0, np.sin(alpha_rad), np.cos(alpha_rad)]])

    Ry = np.array([[np.cos(beta_rad), 0, np.sin(beta_rad)],
                   [0, 1, 0],
                   [-np.sin(beta_rad), 0, np.cos(beta_rad)]])

    Rz = np.array([[np.cos(gamma_rad), -np.sin(gamma_rad), 0],
                   [np.sin(gamma_rad), np.cos(gamma_rad), 0],
                   [0, 0, 1]])

    # Vektor drehen
    rotated_vector = np.dot(Rz, np.dot(Ry, np.dot(Rx, vector)))

    return rotated_vector