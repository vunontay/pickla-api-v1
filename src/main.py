import logging

from fastapi import FastAPI
from src.api.v1 import router as api_router
from src.shared.errors.handlers import register_exception_handlers
from src.shared.middlewares.error_handling import ErrorHandlingMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Middlewares
app.add_middleware(ErrorHandlingMiddleware)

# Routers
app.include_router(api_router, prefix="/api/v1")

# Exception handlers
register_exception_handlers(app)
