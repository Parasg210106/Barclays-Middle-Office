from pydantic import BaseModel, Field
from typing import Optional

class Forex(BaseModel):
    # Core required forex trade fields
    TradeID: str = Field(..., alias="TradeID")
    TradeDate: str = Field(..., alias="TradeDate")
    ValueDate: str = Field(..., alias="ValueDate")
    TradeTime: str = Field(..., alias="TradeTime")
    TraderID: str = Field(..., alias="TraderID")
    Counterparty: str = Field(..., alias="Counterparty")
    Counterparty_ID: str = Field("", alias="Counterparty ID")
    LEI: str = Field("", alias="LEI")
    CurrencyPair: str = Field(..., alias="CurrencyPair")
    BuySell: str = Field(..., alias="BuySell")
    DealtCurrency: str = Field(..., alias="DealtCurrency")
    BaseCurrency: str = Field(..., alias="BaseCurrency")
    TermCurrency: str = Field(..., alias="TermCurrency")
    NotionalAmount: float = Field(..., alias="NotionalAmount")
    FXRate: float = Field(..., alias="FXRate")
    TradeStatus: str = Field(..., alias="TradeStatus")
    SettlementStatus: str = Field(..., alias="SettlementStatus")
    SettlementMethod: str = Field(..., alias="SettlementMethod")
    Broker: str = Field(..., alias="Broker")
    ExecutionVenue: str = Field(..., alias="ExecutionVenue")
    ProductType: str = Field(..., alias="ProductType")
    MaturityDate: str = Field(..., alias="MaturityDate")
    ConfirmationTimestamp: str = Field(..., alias="ConfirmationTimestamp")
    SettlementDate: str = Field(..., alias="SettlementDate")
    BookingLocation: str = Field(..., alias="BookingLocation")
    Portfolio: str = Field(..., alias="Portfolio")
    TradeVersion: int = Field(1, alias="TradeVersion")
    CancellationFlag: str = Field(..., alias="CancellationFlag")
    AmendmentFlag: str = Field(..., alias="AmendmentFlag")
    RiskSystemID: str = Field(..., alias="RiskSystemID")
    RegulatoryReportingStatus: str = Field(..., alias="RegulatoryReportingStatus")
    TradeSourceSystem: str = Field(..., alias="TradeSourceSystem")
    ConfirmationMethod: str = Field(..., alias="ConfirmationMethod")
    ConfirmationStatus: str = Field(..., alias="ConfirmationStatus")
    SettlementInstructions: str = Field(..., alias="SettlementInstructions")
    Custodian_Name: str = Field("", alias="Custodian_Name")
    NettingEligibility: str = Field(..., alias="NettingEligibility")
    TradeComplianceStatus: str = Field(..., alias="TradeComplianceStatus")
    KYCCheck: str = Field(..., alias="KYCCheck")
    SanctionsScreening: str = Field(..., alias="SanctionsScreening")
    ExceptionFlag: str = Field(..., alias="ExceptionFlag")
    AuditTrailRef: str = Field(..., alias="AuditTrailRef")
    
    # Financial fields with default values
    CommissionAmount: float = Field(0.0, alias="CommissionAmount")
    CommissionCurrency: str = Field("", alias="CommissionCurrency")
    BrokerageFee: float = Field(0.0, alias="BrokerageFee")
    BrokerageCurrency: str = Field("", alias="BrokerageCurrency")
    CustodyFee: float = Field(0.0, alias="CustodyFee")
    CustodyCurrency: str = Field("", alias="CustodyCurrency")
    SettlementCost: float = Field(0.0, alias="SettlementCost")
    SettlementCurrency: str = Field("", alias="SettlementCurrency")
    FXGainLoss: float = Field(0.0, alias="FXGainLoss")
    PnlCalculated: float = Field(0.0, alias="PnlCalculated")
    
    # Cost and expense fields
    CostAllocationStatus: str = Field("", alias="CostAllocationStatus")
    CostCenter: str = Field("", alias="CostCenter")
    ExpenseApprovalStatus: str = Field("", alias="ExpenseApprovalStatus")
    CostBookedDate: str = Field("", alias="CostBookedDate")
    
    # Exception and reporting fields
    Exception_Type: str = Field("", alias="Exception Type")
    Exception_Description: str = Field("", alias="Exception Description")
    Exception_Resolution: str = Field("", alias="Exception Resolution")
    Reporting_Regulation: str = Field("", alias="Reporting Regulation")
    Exception_Reason: str = Field("", alias="Exception Reason")
    Reporting_Resolution: str = Field("", alias="Reporting Resolution")
    
    # Instrument and trading fields
    RID: str = Field("", alias="RID")
    ISIN: str = Field("", alias="ISIN")
    Symbol: str = Field("", alias="Symbol")
    Trading_Venue: str = Field("", alias="Trading Venue")
    Stock_Currency: str = Field("", alias="Stock_Currency")
    Country_of_Trade: str = Field("", alias="Country_of_Trade")
    Instrument_Status: str = Field("", alias="Instrument_Status")
    
    # Client and KYC fields
    ClientID_Equity: str = Field("", alias="ClientID_Equity")
    KYC_Status_Equity: str = Field("", alias="KYC_Status_Equity")
    Reference_Data_Validated: str = Field("", alias="Reference_Data_Validated")
    Margin_Type: str = Field("", alias="Margin_Type")
    Margin_Status: str = Field("", alias="Margin_Status")
    Client_Approval_Status_Equity: str = Field("", alias="Client_Approval_Status_Equity")
    ClientID_Forex: str = Field("", alias="ClientID_Forex")
    KYC_Status_Forex: str = Field("", alias="KYC_Status_Forex")
    Expense_Approval_Status: str = Field("", alias="Expense_Approval_Status")
    Client_Approval_Status_forex: str = Field("", alias="Client Approval Status(forex)")
    
    # Settlement and account fields
    Custodian_Ac_no: str = Field("", alias="Custodian_Ac_no")
    Beneficiary_Client_ID: str = Field("", alias="Beneficiary_Client_ID")
    Settlement_Cycle: str = Field("", alias="Settlement_Cycle")
    
    # Equity-specific fields
    EffectiveDate_Equity: str = Field("", alias="EffectiveDate_Equity")
    ConfirmationStatus_Equity: str = Field("", alias="ConfirmationStatus_Equity")
    SWIFT_Equity: str = Field("", alias="SWIFT_Equity")
    BeneficiaryName_Equity: str = Field("", alias="BeneficiaryName_Equity")
    Account_Number_Equity: str = Field("", alias="Account_Number_Equity")
    ABA_Equity: str = Field("", alias="ABA_Equity")
    BSB_Equity: str = Field("", alias="BSB_Equity")
    IBAN_Equity: str = Field("", alias="IBAN_Equity")
    SORT_Equity: str = Field("", alias="SORT_Equity")
    Zengin_Equity: str = Field("", alias="Zengin_Equity")
    Settlement_Method_Equity: str = Field("", alias="Settlement_Method_Equity")
    
    # Forex-specific fields
    EffectiveDate_Forex: str = Field("", alias="EffectiveDate_Forex")
    ConfirmationStatus_Forex: str = Field("", alias="ConfirmationStatus_Forex")
    Account_Number_Forex: str = Field("", alias="Account Number_Forex")
    SWIFT_Forex: str = Field("", alias="SWIFT_Forex")
    BeneficiaryName_Forex: str = Field("", alias="BeneficiaryName_Forex")
    ABA_Forex: str = Field("", alias="ABA_Forex")
    BSB_Forex: str = Field("", alias="BSB_Forex")
    IBAN_Forex: str = Field("", alias="IBAN_Forex")
    SORT_Forex: str = Field("", alias="SORT_Forex")
    Zengin_Forex: str = Field("", alias="Zengin_Forex")
    Settlement_Method_Forex: str = Field("", alias="Settlement_Method_Forex")
    
    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True