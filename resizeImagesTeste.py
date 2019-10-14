import cv2
import numpy as np


#read = 'teste.jpg'
#read = 'teste-resize-jczhxeqkjpg.png'
read =  'teste-qtogeyx1jpg.png'

img = cv2.imread(read)

image2 = img.shape[0]
image3 =  img.shape[1]

dim =  (int(image3/2), int(image2/2))
#print(dim)

resize_image =  cv2.resize(img, (dim), interpolation = cv2.INTER_LANCZOS4)

teste  = np.ones((int(image2/2),int(image3/2),3))  
#print(teste)
#resize_image =  teste * resize_image


cv2.imshow('oi', resize_image)
cv2.imwrite('teste_resize.jpg', resize_image, [cv2.IMWRITE_JPEG_QUALITY,90])

cv2.waitKey()
cv2.destroyAllWindows()
exit()