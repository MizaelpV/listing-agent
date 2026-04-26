from fastapi import FastAPI
from app.api import listings, auth, costs

app = FastAPI()

app.include_router(listings.router, prefix="/listings")
app.include_router(auth.router, prefix="/auth")
app.include_router(costs.router, prefix="/costs")

@app.get("/")
async def root():
    return {"message": "Hello World"}