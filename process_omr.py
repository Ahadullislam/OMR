import cv2
import numpy as np

def process_omr(filepath, num_questions, num_choices):
    image = cv2.imread(filepath)
    if image is None:
        print(f"Error: Unable to load image at {filepath}")
        return []
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use Otsu's thresholding
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    # Morphological opening to remove noise and separate bubbles
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Find contours using RETR_LIST to capture all contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter bubbles with adjusted parameters
    bubble_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        area = cv2.contourArea(contour)
        # Wider aspect ratio and area range
        if 0.5 <= aspect_ratio <= 1.5 and 50 < area < 5000:
            bubble_contours.append(contour)
    
    # Sort contours
    bubble_contours = sorted(bubble_contours, 
                           key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    
    expected_count = num_questions * num_choices
    if len(bubble_contours) != expected_count:
        print(f"Bubble count mismatch: Detected {len(bubble_contours)}, Expected {expected_count}")
        return ['?'] * num_questions
    
    # Rest of the processing remains the same
    questions = [bubble_contours[i*num_choices : (i+1)*num_choices] for i in range(num_questions)]
    
    marked_answers = []
    for q_index, question in enumerate(questions):
        intensities = []
        for choice_index, contour in enumerate(question):
            mask = np.zeros(thresh.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            intensity = cv2.mean(thresh, mask=mask)[0]
            intensities.append((intensity, choice_index))
        
        intensities.sort(reverse=True)
        main_choice = intensities[0][1]
        
        if intensities[0][0] - intensities[1][0] > 10:
            marked_answers.append(chr(65 + main_choice))
        else:
            marked_answers.append('?')
    
    return marked_answers[:num_questions]

# Example usage remains the same