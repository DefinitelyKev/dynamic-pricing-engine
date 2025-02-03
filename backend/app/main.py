from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import market_metrics

app = FastAPI(title="Dynamic Pricing Engine API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_metrics.router)


@app.get("/")
async def root():
    return {"message": "Dynamic Pricing Engine API"}
