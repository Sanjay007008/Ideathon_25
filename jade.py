import numpy as np
import cv2
from skimage import exposure, filters
import os

# Ensure output folder exists
OUTPUT_FOLDER = os.path.join(os.getcwd(), "static/uploads")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# JADE Parameters
ngen = 200  # Number of generations
npop = 20   # Population size

# Function to process image and localize optic disc
def process_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Error: Image file '{image_path}' not found.")

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Error: Unable to load image from '{image_path}'.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Preprocessing
    gray = cv2.medianBlur(gray, 31)
    gray = exposure.equalize_adapthist(gray)
    gray_filtered = cv2.medianBlur((gray * 255).astype(np.uint8), 109)
    gray = cv2.absdiff((gray * 255).astype(np.uint8), gray_filtered)
    gray = cv2.medianBlur(gray, 31)

    kernel = np.ones((40, 40), np.float32) / (40 * 40)
    gray = cv2.filter2D(gray, -1, kernel)

    height, width = gray.shape

    def initialize_population(npop, width, height):
        return np.column_stack([
            np.random.randint(150, width - 150, npop),
            np.random.randint(150, height - 150, npop),
            np.random.randint(-10, 10, npop),
            np.random.randint(-10, 10, npop)
        ])

    population = initialize_population(npop, width, height)

    def fitness_value(image, candidate):
        x, y, _, _ = candidate
        rmid, r1, r2 = 90, 5, 5

        x1, y1 = max(0, int(x - rmid - r2)), max(0, int(y - rmid - r1))
        x2, y2 = min(width, int(x + rmid + r2)), min(height, int(y + rmid + r1))

        roi = image[y1:y2, x1:x2]

        if roi.size == 0:
            return 0

        return filters.rank.entropy(roi.astype(np.uint8), np.ones((5, 5), np.uint8)).mean()

    fitness = np.array([fitness_value(gray, p) for p in population])

    mu_F, mu_CR = 0.5, 0.5
    archive = []

    for _ in range(ngen):
        F = np.clip(mu_F + 0.1 * np.random.randn(npop), 0, 1)
        CR = np.clip(mu_CR + 0.1 * np.random.randn(npop), 0, 1)

        new_population = []
        for i in range(npop):
            r1, r2, r3 = np.random.choice(npop, 3, replace=False)
            mutant = population[r1] + F[i] * (population[r2] - population[r3])

            mutant = np.clip(mutant, [150, 150, -10, -10], [width - 150, height - 150, 10, 10])
            trial = np.where(np.random.rand(4) < CR[i], mutant, population[i])

            new_fitness = fitness_value(gray, trial)

            if new_fitness >= fitness[i]:
                archive.append(population[i])
                new_population.append(trial)
                fitness[i] = new_fitness
            else:
                new_population.append(population[i])

        population = np.array(new_population)

    best_idx = np.argmax(fitness)
    x, y, _, _ = population[best_idx]

    final_image = image.copy()
    cv2.circle(final_image, (int(x), int(y)), 45, (0, 255, 0), 2)

    localized_image_path = os.path.join(OUTPUT_FOLDER, "localized_optic_disc.png")
    cv2.imwrite(localized_image_path, final_image)

    return localized_image_path




