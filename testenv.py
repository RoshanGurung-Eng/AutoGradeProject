# Test EasyOCR
try:
    import easyocr
    reader = easyocr.Reader(['en'])
    print(" EasyOCR loaded successfully")
except Exception as e:
    print(" EasyOCR error:", e)

# Test OpenCV + numpy
try:
    import cv2
    import numpy as np
    print(" OpenCV and NumPy loaded successfully, OpenCV version:", cv2.__version__)
except Exception as e:
    print(" OpenCV / NumPy error:", e)

# Test Pillow
try:
    from PIL import Image
    print(" Pillow loaded successfully")
except Exception as e:
    print(" Pillow error:", e)

# Test scikit-learn
try:
    import sklearn
    print(" Scikit-learn loaded successfully, version:", sklearn.__version__)
except Exception as e:
    print(" Scikit-learn error:", e)

# Test nltk
try:
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')
    print(" NLTK loaded successfully")
except Exception as e:
    print(" NLTK error:", e)


