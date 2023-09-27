import numpy as np
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
    help="Path to the image")
args = vars(ap.parse_args())

img = cv2.imread(args["image"])

cv2.imshow("original", img)

clahe = cv2.createCLAHE(clipLimit=30, tileGridSize=(8, 8))

# Convert the image to LAB color space
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

# Split the LAB image into L, A, and B channels
l, a, b = cv2.split(lab)

# Apply CLAHE to the L channel
l_equalized = clahe.apply(l)

# Merge the equalized L channel with the original A and B channels
lab_equalized = cv2.merge((l_equalized, a, b))

# Convert the LAB equalized image back to BGR color space
equalized_img = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)

cv2.imshow("black point", equalized_img)

# Increase or decrease the contrast of the equalized image
contrast_factor = 1.5  # Adjust this value to increase/decrease the contrast

# Compute the mean pixel intensity
mean_intensity = np.mean(equalized_img)

# Compute the adjusted image using contrast factor and mean intensity
adjusted_img = np.clip((equalized_img - mean_intensity) * contrast_factor + mean_intensity, 0, 255).astype(np.uint8)

cv2.imshow("Contrast Adjusted Image", adjusted_img)

gamma = 0.6  # Adjust this value to increase/decrease the exposure
adjusted_img = np.power(adjusted_img / 255.0, gamma) * 255.0
adjusted_img = adjusted_img.astype(np.uint8)

cv2.imshow("Exposure Adjusted Image", adjusted_img)

blurred_img = cv2.GaussianBlur(adjusted_img, (11, 11), 0)  # Adjust the kernel size as needed

cv2.imshow("Denoised Image", blurred_img)

cv2.waitKey(0)
cv2.destroyAllWindows()
