from fastapi import FastAPI

app = FastAPI()


@app.get("/about")
def get_about():
    return {}
