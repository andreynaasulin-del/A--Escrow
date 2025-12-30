"""Handlers package for Big Stepa Safe Escrow Bot."""

from aiogram import Router

from handlers.user_commands import router as user_router
from handlers.deal_flow import router as deal_router
from handlers.admin_panel import router as admin_router


def setup_routers() -> Router:
    """Create and configure the main router with all sub-routers."""
    main_router = Router()
    
    # Include all handlers
    main_router.include_router(user_router)
    main_router.include_router(deal_router)
    main_router.include_router(admin_router)
    
    return main_router
