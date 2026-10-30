"""API router for quantitative strategy backtesting."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.backtesting import backtesting_service

router = APIRouter(prefix="/api/backtest", tags=["Backtesting"])


class BacktestRunRequest(BaseModel):
    strategy: str = Field(default="A", description="Strategy code (A, B, C, D, E)")
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    initial_investment: float = Field(default=100000.0, ge=1000.0)
    sip_amount: float = Field(default=10000.0, ge=500.0)
    rebalance_cost_pct: float = Field(default=0.10, ge=0.0, le=2.0)


@router.get("/strategies")
async def list_strategies():
    """List all available predefined investment strategies for backtesting."""
    return [
        {"code": code, "name": name}
        for code, name in backtesting_service.STRATEGIES.items()
    ]


@router.post("/run")
async def run_backtest(
    request: BacktestRunRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    """Run quantitative backtest across historical observations."""
    return await backtesting_service.run_backtest(
        db,
        strategy=request.strategy,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_investment=request.initial_investment,
        sip_amount=request.sip_amount,
        rebalance_cost_pct=request.rebalance_cost_pct,
    )

