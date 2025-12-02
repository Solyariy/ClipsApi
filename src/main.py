from fastapi import FastAPI, Response, status
from src.models import TaskPost

app = FastAPI()


@app.get("/")
def root():
    return Response(status_code=status.HTTP_200_OK)


# @app.post("/process_media")
# async def post_process_media():
#     return
