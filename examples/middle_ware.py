import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print(start_time)
    response = await call_next(request)
    process_time = time.time() - start_time
    print(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get('/')
def hello_world(request: Request):
    print(request)
    return 'Hola'


@app.get('/items')
def item():
    print('*****')
    return 'get all items'
