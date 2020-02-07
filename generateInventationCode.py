import cv2
import time
def generateInventationCode(mentionID, code, templatePath="inventation_code_template.jpg"):
    image = cv2.imread(templatePath)
    output = image.copy()
    cv2.putText(output, str(code), (60, 340), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 5, (255, 255, 255), 15) 
    cv2.imwrite(f"{mentionID}.jpg", output)
    return f"{mentionID}.jpg"

print(time.time())