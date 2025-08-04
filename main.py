from fastapi import FastAPI

app = FastAPI(title="TovarTaxi by NESAKO")

@app.get("/")
def welcome():
    return {"msg": "Dobrodošli u TovarTaxi by NESAKO"}