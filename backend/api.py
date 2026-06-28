from fastapi import FastAPI
from backend.incident_queue import (
    initialize_queue,
    add_incident
)

app = FastAPI()

initialize_queue()


@app.get("/")
def health():
    return {
        "status": "Running"
    }


@app.post("/new_incident")
def new_incident(payload: dict):

    add_incident(payload)

    return {
        "status": "success",
        "incident": payload["number"]
    }