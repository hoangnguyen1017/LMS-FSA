from facenet_pytorch import MTCNN, InceptionResnetV1, extract_face
import cv2
import torch

class Face_Detection():
    def __init__(self, device, logging) -> None:
        self.device = device
        self.mtcnn = MTCNN(device=self.device)
        self.logger = logging.getLogger(__name__)
        # self.resnet = InceptionResnetV1(pretrained='vggface2').eval()

    def detect(self, img):
        if self.device == 'cpu': self.logger.warning(f'"Cuda" is not detected. Using "Cpu"!')
        
        boxes, probs, points = self.mtcnn.detect(img, landmarks=True)
        data = {}
        if boxes is not None:
            for i, (box, prob, point) in enumerate(zip(boxes, probs, points)):
                if True:
                    bbox = list(map(int,box.tolist()))
                    # cv2.putText(img=img,
                    #             text= f"{prob}",
                    #             org=(bbox[0] - 10,bbox[1] - 10),
                    #             fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    #             fontScale=0.7,
                    #             color=(0,0,255),
                    #             thickness=3)
                    
                    left_eye = point[0]
                    right_eye = point[1]
                    nose = point[2]

                    margin_eye_x = (bbox[2] - bbox[0])* 0.17
                    margin_y = (bbox[3] - bbox[1])* 0.2

                    margin_nose_x = (bbox[2] - bbox[0])* 0.35

                    if (
                            (left_eye[0] < bbox[0] + margin_eye_x) or (right_eye[0] > bbox[2] - margin_eye_x) or
                            (nose[0] < bbox[0] + margin_nose_x) or (nose[0] > bbox[2] - margin_nose_x)
                        ):
                        color = (0,0,255)
                        data[f'face_{i}'] = 'unfocus'
                    else:
                        color = (0,255,0)
                        data[f'face_{i}'] = 'focus'

                    img = cv2.rectangle(img,(bbox[0],bbox[1]),(bbox[2],bbox[3]),color, 1)

                    for p in point:
                        p = list(map(int,p.tolist()))
                        cv2.circle(img, p, 1, [0, 0, 255], -1)

        return img, data