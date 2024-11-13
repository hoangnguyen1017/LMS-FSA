from contextlib import asynccontextmanager
from fastapi import FastAPI
from packages.face_detection import Face_Detection
from pydantic import BaseModel
from packages import ultis
import logging
import torch

@asynccontextmanager
async def lifespan(app: FastAPI):
    global face_detect_model 
    global potato_disease_model

    logging.basicConfig(level=logging.INFO, format='%(levelname)-9s "%(name)s": %(message)s')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    logger = logging.getLogger(__name__)
    logger.info(f'Using: {device}!')

    face_detect_model = Face_Detection(device, logging)

    yield
    pass

app = FastAPI(lifespan= lifespan)


@app.get("/")
async def root():
    return {"Hello!": "This is Truong's API Server!!!!!"}


class Face_Detection_Val(BaseModel):
    image : str

@app.post("/face_detector")
async def face_detector(item: Face_Detection_Val):
    decoded_img = ultis.base64_2_img(base64_img=item.image)
    img, data = face_detect_model.detect(img=decoded_img)
    encoded_img = ultis.img_2_base64(img)
   
    # return {"image": encoded_img}
    response = {'message': 'success!', 'data' : data}
    return response