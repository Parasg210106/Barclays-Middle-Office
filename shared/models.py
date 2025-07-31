from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class TradeStatus(str, Enum):
    BOOKED = "BOOKED"
    VALIDATED = "VALIDATED"
    ENRICHED = "ENRICHED"
    ALLOCATED = "ALLOCATED"
    SETTLED = "SETTLED"
    EXCEPTION = "EXCEPTION"
    COMPLETED = "COMPLETED"

class RiskType(str, Enum):
    CREDIT = "CREDIT"
    MARKET = "MARKET"
    OPERATIONAL = "OPERATIONAL"

class ExceptionType(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RISK_VIOLATION = "RISK_VIOLATION"
    ENRICHMENT_ERROR = "ENRICHMENT_ERROR"
    ALLOCATION_ERROR = "ALLOCATION_ERROR"

class Trade(BaseModel):
    trade_id: str = Field(..., alias="TradeID")
    order_id: str = Field(..., alias="OrderID")
    client_id: str = Field(..., alias="ClientID")
    isin: str = Field(..., alias="ISIN")
    symbol: str = Field(..., alias="Symbol")
    trade_type: str = Field(..., alias="TradeType")
    quantity: int = Field(..., alias="Quantity")
    price: float = Field(..., alias="Price")
    trade_value: float = Field(..., alias="TradeValue")
    currency: str = Field(..., alias="Currency")
    trade_date: str = Field(..., alias="TradeDate")
    settlement_date: str = Field(..., alias="SettlementDate")
    settlement_status: str = Field(..., alias="SettlementStatus")
    counterparty: str = Field(..., alias="Counterparty")
    trading_venue: str = Field(..., alias="TradingVenue")
    trader_name: str = Field(..., alias="TraderName")
    kyc_status: str = Field(..., alias="KYCStatus")
    reference_data_validated: str = Field(..., alias="ReferenceDataValidated")
    commission: float = Field(..., alias="Commission")
    taxes: float = Field(..., alias="Taxes")
    total_cost: float = Field(..., alias="TotalCost")
    confirmation_status: str = Field(..., alias="ConfirmationStatus")
    country_of_trade: str = Field(..., alias="CountryOfTrade")
    ops_team_notes: str = Field(..., alias="OpsTeamNotes")
    pricing_source: str = Field(..., alias="PricingSource")
    market_impact_cost: float = Field(..., alias="MarketImpactCost")
    fx_rate_applied: float = Field(..., alias="FXRateApplied")
    net_amount: float = Field(..., alias="NetAmount")
    collateral_required: float = Field(..., alias="CollateralRequired")
    margin_type: str = Field(..., alias="MarginType")
    margin_status: str = Field(..., alias="MarginStatus")

    class Config:
        allow_population_by_field_name = True

class TradeEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    trade_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    source_service: str

class ValidationResult(BaseModel):
    trade_id: str
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

class RiskCheckResult(BaseModel):
    trade_id: str
    risk_type: RiskType
    passed: bool
    violations: List[str] = []
    details: Dict[str, Any] = {}

class ExceptionRecord(BaseModel):
    exception_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trade_id: str
    exception_type: ExceptionType
    description: str
    status: str = "OPEN"  # OPEN, RESOLVED, CLOSED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

class AllocationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    portfolio_id: str
    allocation_type: str  # PRO_RATA, FIXED_PERCENTAGE, CUSTOM
    percentage: float
    priority: int = 1

class TradeLifecycleEvent(BaseModel):
    trade_id: str
    from_status: TradeStatus
    to_status: TradeStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = {} 