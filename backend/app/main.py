from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health", summary="Health Check", tags="System")
async def health_check():
    pass