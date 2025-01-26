from fastapi import FastAPI, HTTPException
from fastapi import Request

app = FastAPI()

@app.get("/")
def index(request: Request):
	return {"hello": "world"}

@app.get("/demo_error")
def error():
	raise HTTPException(status_code=403, detail="Error demo")