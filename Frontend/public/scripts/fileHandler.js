// File upload and CSV parsing logic here

// Mapping from CSV headers to API field names
const csvToApiFieldMap = {
    "Trade ID": "TradeID",
    "Order ID": "OrderID",
    "Client ID": "ClientID",
    "ISIN": "ISIN",
    "Symbol": "Symbol",
    "Trade Type": "TradeType",
    "Quantity": "Quantity",
    "Price": "Price",
    "Trade Value": "TradeValue",
    "Currency": "Currency",
    "Trade Date": "TradeDate",
    "Settlement Date": "SettlementDate",
    "Settlement Status": "SettlementStatus",
    "Counterparty": "Counterparty",
    "Trading Venue": "TradingVenue",
    "Trader Name": "TraderName",
    "KYC Status": "KYCStatus",
    "Reference Data Validated": "ReferenceDataValidated",
    "Commission": "Commission",
    "Taxes": "Taxes",
    "Total Cost": "TotalCost",
    "Confirmation Status": "ConfirmationStatus",
    "Country Of Trade": "CountryOfTrade",
    "Ops Team Notes": "OpsTeamNotes",
    "Pricing Source": "PricingSource",
    "Market Impact Cost": "MarketImpactCost",
    "FX Rate Applied": "FXRateApplied",
    "Net Amount": "NetAmount",
    "Collateral Required": "CollateralRequired",
    "Margin Type": "MarginType",
    "Margin Status": "MarginStatus"
};

const forexCsvToApiFieldMap = {
    // Core forex fields - handle both with and without spaces
    "Trade ID": "TradeID",
    "TradeID": "TradeID",
    "Trade Date": "TradeDate",
    "TradeDate": "TradeDate",
    "Value Date": "ValueDate",
    "ValueDate": "ValueDate",
    "Trade Time": "TradeTime",
    "TradeTime": "TradeTime",
    "Trader ID": "TraderID",
    "TraderID": "TraderID",
    "Counterparty": "Counterparty",
    "Counterparty ID": "Counterparty ID",
    "CounterpartyID": "Counterparty ID",
    "LEI": "LEI",
    "Currency Pair": "CurrencyPair",
    "CurrencyPair": "CurrencyPair",
    "Buy/Sell": "BuySell",
    "BuySell": "BuySell",
    "Dealt Currency": "DealtCurrency",
    "DealtCurrency": "DealtCurrency",
    "Base Currency": "BaseCurrency",
    "BaseCurrency": "BaseCurrency",
    "Term Currency": "TermCurrency",
    "TermCurrency": "TermCurrency",
    "Notional Amount": "NotionalAmount",
    "NotionalAmount": "NotionalAmount",
    "FX Rate": "FXRate",
    "FXRate": "FXRate",
    "Trade Status": "TradeStatus",
    "TradeStatus": "TradeStatus",
    "Settlement Status": "SettlementStatus",
    "SettlementStatus": "SettlementStatus",
    "Settlement Method": "SettlementMethod",
    "SettlementMethod": "SettlementMethod",
    "Broker": "Broker",
    "Execution Venue": "ExecutionVenue",
    "ExecutionVenue": "ExecutionVenue",
    "Product Type": "ProductType",
    "ProductType": "ProductType",
    "Maturity Date": "MaturityDate",
    "MaturityDate": "MaturityDate",
    "Confirmation Timestamp": "ConfirmationTimestamp",
    "ConfirmationTimestamp": "ConfirmationTimestamp",
    "Settlement Date": "SettlementDate",
    "SettlementDate": "SettlementDate",
    "Booking Location": "BookingLocation",
    "BookingLocation": "BookingLocation",
    "Portfolio": "Portfolio",
    "Trade Version": "TradeVersion",
    "TradeVersion": "TradeVersion",
    "Cancellation Flag": "CancellationFlag",
    "CancellationFlag": "CancellationFlag",
    "Amendment Flag": "AmendmentFlag",
    "AmendmentFlag": "AmendmentFlag",
    "Risk System ID": "RiskSystemID",
    "RiskSystemID": "RiskSystemID",
    "Regulatory Reporting Status": "RegulatoryReportingStatus",
    "RegulatoryReportingStatus": "RegulatoryReportingStatus",
    "Trade Source System": "TradeSourceSystem",
    "TradeSourceSystem": "TradeSourceSystem",
    "Confirmation Method": "ConfirmationMethod",
    "ConfirmationMethod": "ConfirmationMethod",
    "Confirmation Status": "ConfirmationStatus",
    "ConfirmationStatus": "ConfirmationStatus",
    "Settlement Instructions": "SettlementInstructions",
    "SettlementInstructions": "SettlementInstructions",
    "Custodian": "Custodian_Name",
    "Custodian_Name": "Custodian_Name",
    "Netting Eligibility": "NettingEligibility",
    "NettingEligibility": "NettingEligibility",
    "Trade Compliance Status": "TradeComplianceStatus",
    "TradeComplianceStatus": "TradeComplianceStatus",
    "KYC Check": "KYCCheck",
    "KYCCheck": "KYCCheck",
    "Sanctions Screening": "SanctionsScreening",
    "SanctionsScreening": "SanctionsScreening",
    "Exception Flag": "ExceptionFlag",
    "ExceptionFlag": "ExceptionFlag",
    "Audit Trail Ref": "AuditTrailRef",
    "AuditTrailRef": "AuditTrailRef",
    "Commission Amount": "CommissionAmount",
    "CommissionAmount": "CommissionAmount",
    "Commission Currency": "CommissionCurrency",
    "CommissionCurrency": "CommissionCurrency",
    "Brokerage Fee": "BrokerageFee",
    "BrokerageFee": "BrokerageFee",
    "Brokerage Currency": "BrokerageCurrency",
    "BrokerageCurrency": "BrokerageCurrency",
    "Custody Fee": "CustodyFee",
    "CustodyFee": "CustodyFee",
    "Custody Currency": "CustodyCurrency",
    "CustodyCurrency": "CustodyCurrency",
    "Settlement Cost": "SettlementCost",
    "SettlementCost": "SettlementCost",
    "Settlement Currency": "SettlementCurrency",
    "SettlementCurrency": "SettlementCurrency",
    "FX Gain/Loss": "FXGainLoss",
    "FXGainLoss": "FXGainLoss",
    "P&L Calculated": "PnlCalculated",
    "PnlCalculated": "PnlCalculated",
    "Cost Allocation Status": "CostAllocationStatus",
    "CostAllocationStatus": "CostAllocationStatus",
    "Cost Center": "CostCenter",
    "CostCenter": "CostCenter",
    "Expense Approval Status": "ExpenseApprovalStatus",
    "ExpenseApprovalStatus": "ExpenseApprovalStatus",
    "Cost Booked Date": "CostBookedDate",
    "CostBookedDate": "CostBookedDate",
    
    // Exception and reporting fields
    "Exception Type": "Exception Type",
    "Exception Description": "Exception Description",
    "Exception Resolution": "Exception Resolution",
    "Reporting Regulation": "Reporting Regulation",
    "Exception Reason": "Exception Reason",
    "Reporting Resolution": "Reporting Resolution",
    
    // Instrument and trading fields
    "RID": "RID",
    "ISIN": "ISIN",
    "Symbol": "Symbol",
    "Trading Venue": "Trading Venue",
    "Stock_Currency": "Stock_Currency",
    "Country_of_Trade": "Country_of_Trade",
    "Instrument_Status": "Instrument_Status",
    
    // Client and KYC fields
    "ClientID_Equity": "ClientID_Equity",
    "KYC_Status_Equity": "KYC_Status_Equity",
    "Reference_Data_Validated": "Reference_Data_Validated",
    "Margin_Type": "Margin_Type",
    "Margin_Status": "Margin_Status",
    "Client_Approval_Status_Equity": "Client_Approval_Status_Equity",
    "ClientID_Forex": "ClientID_Forex",
    "KYC_Status_Forex": "KYC_Status_Forex",
    "Expense_Approval_Status": "Expense_Approval_Status",
    "Client Approval Status(forex)": "Client Approval Status(forex)",
    
    // Settlement and account fields
    "Custodian_Ac_no": "Custodian_Ac_no",
    "Beneficiary_Client_ID": "Beneficiary_Client_ID",
    "Settlement_Cycle": "Settlement_Cycle",
    
    // Equity-specific fields
    "EffectiveDate_Equity": "EffectiveDate_Equity",
    "ConfirmationStatus_Equity": "ConfirmationStatus_Equity",
    "SWIFT_Equity": "SWIFT_Equity",
    "BeneficiaryName_Equity": "BeneficiaryName_Equity",
    "Account_Number_Equity": "Account_Number_Equity",
    "ABA_Equity": "ABA_Equity",
    "BSB_Equity": "BSB_Equity",
    "IBAN_Equity": "IBAN_Equity",
    "SORT_Equity": "SORT_Equity",
    "Zengin_Equity": "Zengin_Equity",
    "Settlement_Method_Equity": "Settlement_Method_Equity",
    
    // Forex-specific fields
    "EffectiveDate_Forex": "EffectiveDate_Forex",
    "ConfirmationStatus_Forex": "ConfirmationStatus_Forex",
    "Account Number_Forex": "Account Number_Forex",
    "SWIFT_Forex": "SWIFT_Forex",
    "BeneficiaryName_Forex": "BeneficiaryName_Forex",
    "ABA_Forex": "ABA_Forex",
    "BSB_Forex": "BSB_Forex",
    "IBAN_Forex": "IBAN_Forex",
    "SORT_Forex": "SORT_Forex",
    "Zengin_Forex": "Zengin_Forex",
    "Settlement_Method_Forex": "Settlement_Method_Forex"
};

// Helper to parse and clean numbers
function parseNumber(val) {
    if (typeof val !== "string") return typeof val === "number" ? val : 0.0;
    // Remove commas, currency, and non-numeric except dot and minus
    val = val.replace(/,/g, "").replace(/[^0-9.-]+/g, "");
    if (val === "") return 0.0;
    const num = parseFloat(val);
    return isNaN(num) ? 0.0 : num;
}

// Helper to parse and format dates as YYYY-MM-DD
function parseDate(val) {
    if (!val) return "";
    
    // Handle different date formats without timezone issues
    const dateStr = val.toString().trim();
    console.log(`🔍 parseDate input: "${val}" -> "${dateStr}"`);
    
    // Try DD/MM/YYYY format (European format like 24/1/2025)
    if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateStr)) {
        const parts = dateStr.split('/');
        // For European format, always assume DD/MM/YYYY
        const [day, month, year] = parts;
        const result = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        console.log(`🔍 parseDate DD/MM/YYYY: "${dateStr}" -> "${result}"`);
        return result;
    }
    
    // Try YYYY-MM-DD format
    if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(dateStr)) {
        const [year, month, day] = dateStr.split('-');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }
    
    // Try MM-DD-YYYY format
    if (/^\d{1,2}-\d{1,2}-\d{4}$/.test(dateStr)) {
        const [month, day, year] = dateStr.split('-');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }
    
    // Try DD-MM-YYYY format
    if (/^\d{1,2}-\d{1,2}-\d{4}$/.test(dateStr)) {
        const [day, month, year] = dateStr.split('-');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }
    
    // Fallback to original value if no format matches
    console.log(`🔍 parseDate output: "${val}" (no format matched)`);
    return val;
}

// Helper to parse booleans/yes/no
function parseBoolean(val) {
    if (typeof val === "boolean") return val ? "Yes" : "No";
    if (typeof val === "string") {
        const v = val.trim().toLowerCase();
        if (["yes", "y", "true", "1"].includes(v)) return "Yes";
        if (["no", "n", "false", "0"].includes(v)) return "No";
    }
    return val;
}

function mapCsvRowToApi(row) {
    const mapped = {};
    for (const [csvKey, apiKey] of Object.entries(csvToApiFieldMap)) {
        let value = row[csvKey] || "";
        // Numeric fields
        if (["TradeValue", "CollateralRequired", "Quantity", "Price", "Commission", "Taxes", "TotalCost", "MarketImpactCost", "FXRateApplied", "NetAmount"].includes(apiKey)) {
            value = parseNumber(value);
        }
        // Date fields
        else if (["TradeDate", "SettlementDate"].includes(apiKey)) {
            value = parseDate(value);
        }
        // Boolean/text fields
        else if (["ReferenceDataValidated"].includes(apiKey)) {
            value = parseBoolean(value);
        }
        // TradeType: map 'Buy'/'Sell' (case-insensitive) to 'BUY'/'SELL'
        else if (apiKey === "TradeType") {
            if (typeof value === "string") {
                const v = value.trim().toUpperCase();
                if (v === "BUY" || v === "SELL") {
                    value = v;
                } else if (v === "BUY".substring(0,3)) {
                    value = "BUY";
                } else if (v === "SELL".substring(0,4)) {
                    value = "SELL";
                } else if (v === "B") {
                    value = "BUY";
                } else if (v === "S") {
                    value = "SELL";
                } else {
                    value = value; // leave as is for backend to catch
                }
            }
        }
        // Everything else: trim whitespace
        else if (typeof value === "string") {
            value = value.trim();
        }
        mapped[apiKey] = value;
    }
    return mapped;
}

function mapForexCsvRowToApi(row) {
    // List of numeric (float) fields in the Forex model
    const floatFields = [
        "NotionalAmount", "FXRate", "CommissionAmount", "BrokerageFee", "CustodyFee", "SettlementCost", "FXGainLoss", "PnlCalculated"
    ];
    // List of integer fields in the Forex model
    const intFields = [
        "TradeVersion"
    ];
    
    const mapped = {};
    
    // Use the mapping instead of hardcoded fields
    for (const [csvKey, apiKey] of Object.entries(forexCsvToApiFieldMap)) {
        let value = row[csvKey] !== undefined ? row[csvKey] : "";
        
        if (floatFields.includes(apiKey)) {
            value = (value === "" || value === undefined) ? 0.0 : parseFloat(value.toString().replace(/,/g, "").replace(/[^0-9.-]+/g, ""));
            if (isNaN(value)) value = 0.0;
        } else if (intFields.includes(apiKey)) {
            value = (value === "" || value === undefined) ? 0 : parseInt(value, 10);
            if (isNaN(value)) value = 0;
        } else if (typeof value === "string") {
            value = value.trim();
        }
        mapped[apiKey] = value;
    }
    
    return mapped;
}

window.handleFileUpload = function(event) {
    const files = event.target.files;
    if (!files.length) return;
    Array.from(files).forEach(file => {
        // Determine endpoint and parser based on file name
        let endpoint = "";
        let parser = null;
        const lowerName = file.name.toLowerCase();
        if (lowerName.startsWith("equity")) {
            endpoint = "http://localhost:8001/trades/bulk"; // should be 8001, not 8000
            parser = mapCsvRowToApi;
        } else if (lowerName.startsWith("fx")) {
            endpoint = "http://localhost:8002/forexs/bulk";
            parser = mapForexCsvRowToApi;
        } else {
            alert("Unknown file type. File name must start with 'equity' or 'fx'.");
            return;
        }

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                // Map each row to API format
                const trades = results.data.map(parser);
                console.log("Mapped trades to send:", trades);
                sendBulkTrades(trades, endpoint);
            },
            error: function(err) {
                alert("CSV parsing error: " + err.message);
            }
        });
    });
};

function sendBulkTrades(trades, endpoint) {
    console.log(`[DEBUG] Sending ${trades.length} trades to ${endpoint}`);
    console.log(`[DEBUG] First trade data:`, trades[0]);
    console.log(`[DEBUG] All trade keys:`, Object.keys(trades[0]));
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(trades)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                console.error(`[DEBUG] Server error:`, errorData);
                throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log(`[DEBUG] Success response:`, data);
        alert(`Successfully uploaded ${trades.length} trades!`);
    })
    .catch(error => {
        console.error(`[DEBUG] Upload error:`, error);
        alert(`Upload failed: ${error.message}`);
    });
}
