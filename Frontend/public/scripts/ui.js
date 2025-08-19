// UI logic here

// Global variable to store client data
let clientData = [];

// Function to fetch client IDs from Firebase unified_data collection
async function fetchClientIDs() {
    try {
        console.log('Fetching client IDs from unified_data collection...');
        
        // For now, we'll use a direct HTTP request to a backend endpoint
        const response = await fetch('http://localhost:8001/api/equity-capture/client-ids');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Client IDs fetched:', data);
        
        // Store the client data globally
        clientData = data.client_ids || [];
        
        // Populate the dropdown
        const dropdown = document.getElementById('client-dropdown');
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Select a Client ID</option>';
            
            if (clientData.length > 0) {
                clientData.forEach(clientId => {
                    const option = document.createElement('option');
                    option.value = clientId;
                    option.textContent = clientId;
                    dropdown.appendChild(option);
                });
            } else {
                dropdown.innerHTML = '<option value="">No client IDs found</option>';
            }
        }
    } catch (error) {
        console.error('Error fetching client IDs:', error);
        const dropdown = document.getElementById('client-dropdown');
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Error loading client IDs</option>';
        }
    }
}

// Function to handle client selection
function handleClientSelection() {
    const dropdown = document.getElementById('client-dropdown');
    
    if (!dropdown) {
        console.error('Client dropdown not found');
        return;
    }
    
    const selectedClientId = dropdown.value;
    
    if (!selectedClientId) {
        // No client selected
        return;
    }
    
    // Since clientData now contains just the client ID strings, we can check if it exists
    if (clientData.includes(selectedClientId)) {
        console.log('Selected client ID:', selectedClientId);
        // Here you can add logic to fetch additional client details if needed
        // For example, fetch trades for this client, or other client-specific data
    } else {
        console.error('Client ID not found in available data:', selectedClientId);
    }
}

// Global function for parsing flexible date formats
function parseFlexibleDate(dateStr) {
    if (!dateStr) return null;
    // Try ISO first
    let d = new Date(dateStr);
    if (!isNaN(d.getTime())) return d;
    
    // Try YYYY-DD-MM format (as seen in the data: 2025-23-07)
    if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        let parts = dateStr.split('-');
        if (parts.length === 3) {
            let yyyy = parseInt(parts[0], 10);
            let dd = parseInt(parts[1], 10);
            let mm = parseInt(parts[2], 10);
            // Check if this is YYYY-DD-MM format (day > 12)
            if (dd > 12 && mm <= 12) {
                let d1 = new Date(yyyy, mm - 1, dd);
                if (!isNaN(d1.getTime())) return d1;
            }
        }
    }
    
    // Try DD/MM/YYYY format (common in UK/European format)
    let parts = dateStr.split('/');
    if (parts.length === 3) {
        let dd = parseInt(parts[0], 10), mm = parseInt(parts[1], 10), yyyy = parseInt(parts[2], 10);
        if (yyyy > 1000 && mm >= 1 && mm <= 12 && dd >= 1 && dd <= 31) {
            let d1 = new Date(yyyy, mm - 1, dd);
            if (!isNaN(d1.getTime())) return d1;
        }
    }
    
    // Try MM/DD/YYYY format (US format)
    if (parts.length === 3) {
        let mm = parseInt(parts[0], 10), dd = parseInt(parts[1], 10), yyyy = parseInt(parts[2], 10);
        if (yyyy > 1000 && mm >= 1 && mm <= 12 && dd >= 1 && dd <= 31) {
            let d2 = new Date(yyyy, mm - 1, dd);
            if (!isNaN(d2.getTime())) return d2;
        }
    }
    
    // Try YYYY-MM-DD (standard ISO format)
    if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
        let parts = dateStr.split('-');
        if (parts.length === 3) {
            let yyyy = parseInt(parts[0], 10);
            let mm = parseInt(parts[1], 10);
            let dd = parseInt(parts[2], 10);
            // Check if this is YYYY-MM-DD format (month <= 12)
            if (mm <= 12 && dd <= 31) {
                let d3 = new Date(yyyy, mm - 1, dd);
                if (!isNaN(d3.getTime())) return d3;
            }
        }
    }
    return null;
}

// Reverse mapping from API field names to display headers
const apiToDisplayFieldMap = {
    TradeID: "Trade ID",
    OrderID: "Order ID",
    ClientID: "Client ID",
    ISIN: "ISIN",
    Symbol: "Symbol",
    TradeType: "Trade Type",
    Quantity: "Quantity",
    Price: "Price",
    TradeValue: "Trade Val",
    Currency: "Currency",
    TradeDate: "Trade Date",
    SettlementDate: "Settlement",
    SettlementStatus: "Settlement Status",
    Counterparty: "Counterparty",
    TradingVenue: "Trading Venue",
    TraderName: "Trader Name",
    KYCStatus: "KYC Status",
    ReferenceDataValidated: "Reference",
    Commission: "Commission",
    Taxes: "Taxes",
    TotalCost: "Total Cost",
    ConfirmationStatus: "Confirmation Status",
    CountryOfTrade: "Country Of Trade",
    OpsTeamNotes: "Ops Team Notes",
    PricingSource: "Pricing Source",
    MarketImpactCost: "Market Impact Cost",
    FXRateApplied: "FX Rate Applied",
    NetAmount: "Net Amount",
    CollateralRequired: "Collateral",
    MarginType: "Margin Type",
    MarginStatus: "Margin Status",
    AssignedTo: "Assigned To",
    Actions: "Actions"
};

const forexApiToDisplayFieldMap = {
    TradeID: "Trade ID",
    TradeDate: "Trade Date",
    ValueDate: "Value Date",
    TradeTime: "Trade Time",
    TradeRefID: "Trade Ref ID",
    TraderID: "Trader ID",
    Counterparty: "Counterparty",
    CurrencyPair: "Currency",
    BuySell: "Buy/Sell",
    DealCurr: "Deal Curr",
    BaseCurr: "Base Curr",
    TermCurr: "Term Curr",
    Notional: "Notional",
    FXRate: "FX Rate",
    TradeStatus: "Trade Status",
    Settlement: "Settlement",
    SettlementStatus: "Settlement Status",
    Broker: "Broker",
    Execution: "Execution",
    ProductType: "Product Type",
    MaturityDt: "Maturity Dt",
    Contract: "Contract",
    SettlementBooking: "Settlement Booking",
    Portfolio: "Portfolio",
    TradeVersion: "Trade Version",
    Cancelled: "Cancelled",
    Amended: "Amended",
    RiskApproval: "Risk Approval",
    RiskType: "Risk Type",
    Regulation: "Regulation",
    TradeSource: "Trade Source",
    ConfirmMethod: "Confirm Method",
    ConfirmStatus: "Confirm Status",
    ConfirmSent: "Confirm Sent",
    Custodian: "Custodian",
    NettingFlag: "Netting Flag",
    TradeConf: "Trade Conf",
    KYCCheck: "KYC Status",
    Sanctions: "Sanctions",
    Exception: "Exception",
    ExceptionID: "Exception ID",
    AuditTrail: "Audit Trail",
    Commission: "Commission",
    Brokerage: "Brokerage",
    CustodyFee: "Custody Fee",
    CustodyCurr: "Custody Curr",
    SettlementFee: "Settlement Fee",
    SettlementCurr: "Settlement Curr",
    FXGainLoss: "FX Gain/Loss",
    PnL: "PnL",
    CostAlloc: "Cost Alloc",
    CostCentre: "Cost Centre",
    ExpenseAlloc: "Expense Alloc",
    CostBook: "Cost Book",
    AssignedTo: "Assigned To",
    Actions: "Actions"
};

// Add department assignment rules
const departmentAssignmentRules = {
    "TSA": ["TradeDate", "SettlementDate", "MaturityDate", "BuySell"],
    "LCM": ["FXRate", "NotionalAmount", "TradeValue", "KYCCheck"],
    "Front Office": ["Counterparty", "CurrencyPair", "ProductType", "BaseCurrency", "TermCurrency", "DealtCurrency"],
    "IBMO": ["TradeID"]
};

function extractFieldFromError(error) {
    // Handles errors like "TradeDate mismatch: trade='...' vs termsheet='...'"
    const match = error.match(/^([A-Za-z0-9_]+) mismatch:/);
    if (match) return match[1];
    // fallback: try to get the first word
    return error.split(' ')[0];
}

function getAssignedDepartment(trade) {
    if (trade.ValidationStatus === 'Passed') return 'NA';
    if (!trade.ValidationErrors || trade.ValidationErrors.length === 0) return 'NA';
    // Try to extract the field from each error and assign department
    for (const [dept, fields] of Object.entries(departmentAssignmentRules)) {
        for (const error of trade.ValidationErrors) {
            const field = extractFieldFromError(error);
            if (fields.includes(field)) {
                return dept;
            }
        }
    }
    return 'NA';
}

// Inline getTrades function (copied from src/scripts/api.js)
const API_BASE_URL = "http://localhost:8001"; // Default to equity capture service
async function getTrades() {
    const response = await fetch(`${API_BASE_URL}/trades`);
    if (!response.ok) throw new Error("Failed to fetch trades");
    return response.json();
}

let allTrades = [];
let currentSortField = null;
let currentSortAsc = true;
let currentSearch = '';
let currentInstrument = 'Equity'; // Track selected instrument

async function fetchForexTradesAndValidation() {
    // Fetch all captured forex trades
            const tradesRes = await fetch('http://localhost:8002/api/forex-capture/forexs');
    if (!tradesRes.ok) throw new Error('Failed to fetch forex trades');
    const trades = await tradesRes.json();
    // Fetch validation results (may be empty if no termsheets yet)
    let validationMap = {};
    try {
        const valRes = await fetch('http://localhost:8016/api/forex-validation/get-validation-status');
        if (valRes.ok) {
            const valData = await valRes.json();
            (valData.results || []).forEach(v => {
                validationMap[v.TradeID] = {
                    status: v.ValidationStatus,
                    assignedTo: v.AssignedTo
                };
            });
        }
    } catch (e) { /* ignore if validation not available yet */ }
    // Merge validation status and assignedTo into trades
    return trades.map(trade => ({
        TradeID: trade.TradeID,
        TraderID: trade.TraderID,
        Currency: trade.CurrencyPair,
        TradeDate: trade.TradeDate,
        KYCStatus: trade.KYCCheck,
        ValidationStatus: validationMap[trade.TradeID]?.status || 'Pending',
        AssignedTo: validationMap[trade.TradeID]?.assignedTo || getAssignedDepartment(trade),
        Actions: 'View Termsheet',
    }));
}

// Update fetchTradesByInstrument for Forex
async function fetchTradesByInstrument(instrument) {
    if (instrument === 'Equity') {
        // Fetch all equity trades from Firestore 'trades' collection
        const equitySnap = await db.collection('trades').get();
        const trades = [];
        equitySnap.forEach(doc => {
            const data = doc.data();
            // Add any normalization or mapping here if needed
            trades.push(data);
        });
        return trades;
    } else if (instrument === 'Forex') {
        return await fetchForexTradesAndValidation();
    } else {
        return [];
    }
}

// Fetch validation results and merge into allTrades
async function fetchAndMergeValidationResults() {
    try {
        let endpoint = '';
        if (currentInstrument === 'Equity') {
            endpoint = 'http://localhost:8011/api/equity-validation/validation-results?t=' + Date.now();
        } else if (currentInstrument === 'Forex') {
            // Run validation to check for new trades, then get results
            endpoint = 'http://localhost:8016/api/forex-validation/validate-forex-capture';
        } else {
            allTrades.forEach(trade => { trade.ValidationStatus = 'Pending'; });
            return;
        }
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Failed to fetch validation results');
        const validationResults = await response.json();
        
        // For forex, the validation endpoint returns results directly
        // For equity, we need to handle the different response structure
        let resultsToProcess = [];
        if (currentInstrument === 'Forex') {
            resultsToProcess = validationResults.results || [];
        } else {
            resultsToProcess = validationResults;
        }
        
        const validationMap = {};
        resultsToProcess.forEach(v => {
            // Handle both equity (status) and forex (ValidationStatus) data structures
            const status = v.ValidationStatus || v.status || 'Pending';
            validationMap[v["TradeID"]] = {
                status: status,
                assignedTo: v.AssignedTo || 'NA'
            };
        });

        allTrades.forEach(trade => {
            const validationData = validationMap[trade.TradeID] || { status: 'Pending', assignedTo: 'NA' };
            trade.ValidationStatus = validationData.status;
            trade.AssignedTo = validationData.assignedTo;
     
        });
    } catch (err) {
        allTrades.forEach(trade => {
            if (!trade.ValidationStatus) trade.ValidationStatus = 'Pending';
        });
    }
}

// Update loadAndShowTradeValidation to fetch validation results before rendering
let tradeValidationLoaded = false;
window.loadAndShowTradeValidationReal = async function() {
    console.log('🚀 Loading Trade Validation...');
    // Prevent repeated API calls if already loaded
    if (tradeValidationLoaded) {
        console.log('   Already loaded, just showing view');
        // Just show the view without loading data again
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById('trade-validation').classList.add('active');
        return;
    }
    
    try {
        currentInstrument = 'Equity'; // Set Equity as default
        allTrades = await fetchTradesByInstrument(currentInstrument);
        await fetchAndMergeValidationResults();
        console.log('Fetched trades from backend:', allTrades);
        renderTradeValidationSearchBox();
        // Set instrument dropdown to Equity after rendering
        const instrumentSelect = document.getElementById('tv-instrument-filter');
        if (instrumentSelect) {
            instrumentSelect.value = 'Equity';
        }
        renderTradeValidationTable();
        tradeValidationLoaded = true;
    } catch (err) {
        alert('Failed to load trades: ' + err.message);
        console.error('Error fetching trades:', err);
    }
}

function renderTradeValidationSearchBox() {
    let container = document.getElementById('tv-filters');
    if (!container) return;
    container.innerHTML = '';

    // Search input
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Search Trade ID, Client ID, Symbol...';
    input.className = 'border rounded px-2 py-1 text-sm';
    input.value = currentSearch;
    input.oninput = function(e) {
        currentSearch = e.target.value;
        renderTradeValidationTable();
    };
    container.appendChild(input);

    // Instrument dropdown
    const instrumentSelect = document.createElement('select');
    instrumentSelect.id = 'tv-instrument-filter';
    instrumentSelect.className = 'border rounded px-2 py-1 text-sm ml-2';
    instrumentSelect.innerHTML = `
        <option value="Equity">Equity</option>
        <option value="Forex">Forex</option>
    `;
    instrumentSelect.value = currentInstrument;
    instrumentSelect.onchange = async function() {
        console.log('🔄 Switching instrument to:', instrumentSelect.value);
        currentInstrument = instrumentSelect.value;
        // Reset the loaded flag when changing instruments to allow fresh data fetch
        tradeValidationLoaded = false;
        try {
            allTrades = await fetchTradesByInstrument(currentInstrument);
            await fetchAndMergeValidationResults();
            renderTradeValidationTable();
        } catch (err) {
            alert('Failed to load trades: ' + err.message);
            allTrades = [];
            renderTradeValidationTable();
        }
    };
    container.appendChild(instrumentSelect);

    // Validation status dropdown
    const validationSelect = document.createElement('select');
    validationSelect.id = 'tv-validation-filter';
    validationSelect.className = 'border rounded px-2 py-1 text-sm ml-2';
    validationSelect.innerHTML = `
        <option value="">All Statuses</option>
        <option value="Failed">Failed</option>
        <option value="Settled">Settled</option>
    `;
    validationSelect.onchange = function() {
        renderTradeValidationTable();
    };
    container.appendChild(validationSelect);
}

function renderTradeValidationTable() {
    const tbody = document.getElementById('trade-validation-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    // Always render the header dynamically
    const thead = tbody.parentElement.querySelector('thead');
    if (thead) thead.innerHTML = '';
    const headerRow = document.createElement('tr');
    if (currentInstrument === 'Equity') {
        const equityFields = [
            'TradeID', 'ClientID', 'Symbol', 'TradeDate', 'ValidationStatus', 'AssignedTo', 'Actions'
        ];
        headerRow.innerHTML = equityFields.map(f => `<th class="px-4 py-2" style="background: rgba(61, 202, 253, 0.25) !important;">${apiToDisplayFieldMap[f] || f.replace(/([A-Z])/g, ' $1').trim()}</th>`).join('');
    } else if (currentInstrument === 'Forex') {
        const forexFields = [
            'TradeID', 'TraderID', 'Currency', 'TradeDate', 'ValidationStatus', 'AssignedTo', 'Actions'
        ];
        headerRow.innerHTML = forexFields.map(f => `<th class="px-4 py-2" style="background: rgba(61, 202, 253, 0.25) !important;">${forexApiToDisplayFieldMap[f] || f.replace(/([A-Z])/g, ' $1').trim()}</th>`).join('');
    }
    if (thead) thead.appendChild(headerRow);

    // Filter and sort trades (reuse your existing logic)
    let filtered = allTrades;

    // Filter out empty objects (no TradeID for equity)
    filtered = filtered.filter(trade => trade && trade.TradeID && trade.TradeID.toString().trim() !== "");

    if (currentSearch) {
        const s = currentSearch.toLowerCase();
        filtered = filtered.filter(trade =>
            (trade.TradeID && trade.TradeID.toString().toLowerCase().includes(s)) ||
            (trade.TraderID && trade.TraderID.toString().toLowerCase().includes(s)) ||
            (trade.Currency && trade.Currency.toString().toLowerCase().includes(s))
        );
    }
    if (currentSortField) {
        filtered = filtered.slice().sort((a, b) => {
            let va = a[currentSortField] || '';
            let vb = b[currentSortField] || '';
            if (!isNaN(va) && !isNaN(vb)) {
                va = parseFloat(va); vb = parseFloat(vb);
            }
            if (va < vb) return currentSortAsc ? -1 : 1;
            if (va > vb) return currentSortAsc ? 1 : -1;
            return 0;
        });
    }

    // Render data rows
    filtered.forEach(trade => {
        const row = document.createElement('tr');
        if (currentInstrument === 'Equity') {
            let status = trade.ValidationStatus || 'Pending';
            let statusClass = 'text-gray-600 bg-gray-100';
            if (status === 'Validated') statusClass = 'text-green-600 bg-green-100';
            else if (status === 'Failed') statusClass = 'text-red-600 bg-red-100';
            else if (status === 'Pending') statusClass = 'text-yellow-600 bg-yellow-100';
            row.innerHTML = `
                <td class="px-4 py-2">${trade.TradeID !== undefined ? trade.TradeID : '-'}</td>
                <td class="px-4 py-2">${trade.ClientID !== undefined ? trade.ClientID : '-'}</td>
                <td class="px-4 py-2">${trade.Symbol !== undefined ? trade.Symbol : (trade.symbol !== undefined ? trade.symbol : (trade.Currency !== undefined ? trade.Currency : (trade.currency !== undefined ? trade.currency : '-')))}</td>
                <td class="px-4 py-2">${trade.TradeDate !== undefined ? trade.TradeDate : '-'}</td>
                <td class="px-4 py-2">${
                    status === 'Failed'
                        ? `<button class='rounded px-2 py-1 font-semibold ${statusClass}' onclick='showValidationFailureReason("${trade.TradeID}")'>Failed</button>`
                        : `<span class='rounded px-2 py-1 font-semibold ${statusClass}'>${status}</span>`
                }</td>
                <td class="px-4 py-2">${trade.AssignedTo || 'NA'}</td>
                <td class="px-4 py-2"><button class="text-xs font-bold py-1 px-2 rounded" style="background-color: #00AEEF; color: white; border: none;" onclick="showTermsheet('${trade.TradeID}')">View Termsheet</button></td>
            `;
        } else if (currentInstrument === 'Forex') {
            let status = trade.ValidationStatus || 'Pending';
            let statusClass = 'text-gray-600 bg-gray-100';
            if (status === 'Passed') statusClass = 'text-green-600 bg-green-100';
            else if (status === 'Failed') statusClass = 'text-red-600 bg-red-100';
            else if (status === 'Pending') statusClass = 'text-yellow-600 bg-yellow-100';
            row.innerHTML = `
                <td class="px-4 py-2">${trade.TradeID !== undefined ? trade.TradeID : '-'}</td>
                <td class="px-4 py-2">${trade.TraderID !== undefined ? trade.TraderID : '-'}</td>
                <td class="px-4 py-2">${trade.Currency !== undefined ? trade.Currency : '-'}</td>
                <td class="px-4 py-2">${trade.TradeDate !== undefined ? trade.TradeDate : '-'}</td>
                <td class="px-4 py-2">${
                    status === 'Failed'
                        ? `<button class='rounded px-2 py-1 font-semibold ${statusClass}' onclick='showValidationFailureReason("${trade.TradeID}")'>Failed</button>`
                        : `<span class='rounded px-2 py-1 font-semibold ${statusClass}'>${status}</span>`
                }</td>
                <td class="px-4 py-2">${trade.AssignedTo || 'NA'}</td>
                <td class="px-4 py-2"><button class="text-xs font-bold py-1 px-2 rounded" style="background-color: #00AEEF; color: white; border: none;" onclick="showTermsheet('${trade.TradeID}')">View Termsheet</button></td>
            `;
        }
        tbody.appendChild(row);
    });

    // Add sorting to headers
    if (thead) {
        const headerCells = thead.querySelectorAll('th');
        const sortFields = currentInstrument === 'Equity'
            ? ['TradeID', 'ClientID', 'Symbol', 'TradeDate', 'ValidationStatus']
            : ['TradeID', 'TraderID', 'Currency', 'TradeDate', 'ValidationStatus'];
        headerCells.forEach((th, idx) => {
            th.style.cursor = 'pointer';
            th.onclick = function() {
                const field = sortFields[idx];
                if (!field) return;
                if (currentSortField === field) {
                    currentSortAsc = !currentSortAsc;
                } else {
                    currentSortField = field;
                    currentSortAsc = true;
                }
                renderTradeValidationTable();
            };
        });
    }
}

window.sortTradeValidationTable = function(field) {
    if (currentSortField === field) {
        currentSortAsc = !currentSortAsc;
    } else {
        currentSortField = field;
        currentSortAsc = true;
    }
    renderTradeValidationTable();
}

// Update dashboard trade count from backend
window.updateTradeCountFromBackend = async function() {
    try {
        // Fetch both equity and forex trades
        const [equityRes, forexRes] = await Promise.all([
            fetch('http://localhost:8001/api/equity-capture/trades'),
            fetch('http://localhost:8002/api/forex-capture/forexs')
        ]);
        const equityTrades = equityRes.ok ? await equityRes.json() : [];
        const forexTrades = forexRes.ok ? await forexRes.json() : [];
        // Remove all forex trades from allTrades if forexTrades is empty
        if (forexTrades.length === 0) {
            allTrades = allTrades.filter(t => t.TradeType !== 'Forex');
        }
        const total = equityTrades.length + forexTrades.length;
        const countElem = document.getElementById('total-trades');
        if (countElem) countElem.textContent = total;
    } catch (err) {
        // Optionally show error or set to 0
        const countElem = document.getElementById('total-trades');
        if (countElem) countElem.textContent = '0';
    }
  }
  
  // Fetch and update overview statistics
  window.updateOverviewStats = async function() {
      console.log('Debug: updateOverviewStats function called!');
      try {
          console.log('Debug: Calling overview stats API...');
          const response = await fetch('http://localhost:8002/api/forex-capture/overview-stats');
          console.log('Debug: API response status:', response.status);
          if (response.ok) {
              const stats = await response.json();
              console.log('Debug: Received stats:', stats);
              
              // Update the card values
              const totalTradesElem = document.getElementById('total-trades');
              const lifecyclePendingElem = document.getElementById('lifecycle-pending');
              const breaksElem = document.getElementById('breaks');
              
              console.log('Debug: Found elements:', {
                  totalTrades: !!totalTradesElem,
                  lifecyclePending: !!lifecyclePendingElem,
                  breaks: !!breaksElem
              });
              
              if (totalTradesElem) {
                  totalTradesElem.textContent = stats.total_trades || 0;
                  console.log('Debug: Set total-trades to:', stats.total_trades || 0);
              }
              if (lifecyclePendingElem) {
                  lifecyclePendingElem.textContent = stats.lifecycle_events_pending || 0;
                  console.log('Debug: Set lifecycle-pending to:', stats.lifecycle_events_pending || 0);
              }
              if (breaksElem) {
                  breaksElem.textContent = stats.reconciliation_breaks || 0;
                  console.log('Debug: Set breaks to:', stats.reconciliation_breaks || 0);
              }
              
              console.log('Debug: Overview stats update completed');
          } else {
              console.error('Debug: API response not ok:', response.status, response.statusText);
          }
      } catch (error) {
          console.error('Error fetching overview stats:', error);
          // Set default values on error
          const totalTradesElem = document.getElementById('total-trades');
          const lifecyclePendingElem = document.getElementById('lifecycle-pending');
          const breaksElem = document.getElementById('breaks');
          
          if (totalTradesElem) totalTradesElem.textContent = '0';
          if (lifecyclePendingElem) lifecyclePendingElem.textContent = '0';
          if (breaksElem) breaksElem.textContent = '0';
      }
  }
  
  // Load overview stats when page loads
  window.loadOverviewStatsOnPageLoad = function() {
      console.log('Debug: Loading overview stats on page load');
      if (typeof window.updateOverviewStats === 'function') {
          window.updateOverviewStats();
      }
  }
  

  
  
  // Show Termsheet modal with trade details
window.showTermsheet = async function(tradeId) {
    try {
        let allowedFields = [];
        if (currentInstrument === 'Equity') {
            let url = `http://localhost:8013/api/equity-termsheet-capture/equity-termsheets/${tradeId}`;
            allowedFields = [
                "Trade ID", "Order ID", "Client ID", "ISIN", "Symbol", "Trade Type",
                "Quantity", "Price", "Trade Value", "Currency", "Trade Date", "Settlement Date",
                "Settlement Status", "Counterparty", "Trading Venue", "Trader Name", "KYC Status",
                "Reference Data Validated", "Commission", "Taxes", "Total Cost"
            ];
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch trade details');
            var trade = await response.json();
            var termsheetData = trade.termsheet || trade;
        } else if (currentInstrument === 'Forex') {
            allowedFields = [
                "TradeID", "TradeDate", "Counterparty", "CurrencyPair", "BuySell", "DealtCurrency", "BaseCurrency", "TermCurrency", "NotionalAmount", "FXRate", "ProductType", "MaturityDate", "SettlementDate", "KYCCheck"
            ];
            // Fetch from Firestore fx_termsheet (not fx_termsheets)
            const doc = await db.collection('fx_termsheet').doc(tradeId).get();
            if (!doc.exists) throw new Error('No termsheet found for this TradeID');
            var termsheetData = doc.data();
        } else {
            throw new Error('Unknown instrument type');
        }
        // Create modal or section
        let modal = document.getElementById('termsheet-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'termsheet-modal';
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100vw';
            modal.style.height = '100vh';
            modal.style.background = 'rgba(0,0,0,0.5)';
            modal.style.display = 'flex';
            modal.style.alignItems = 'center';
            modal.style.justifyContent = 'center';
            modal.style.zIndex = '1000';
            modal.onclick = function(e) { if (e.target === modal) modal.remove(); };
            document.body.appendChild(modal);
        } else {
            modal.innerHTML = '';
        }
        // Create document header
        const header = document.createElement('div');
        header.style.textAlign = 'center';
        header.style.marginBottom = '2rem';
        header.style.borderBottom = '2px solid #333';
        header.style.paddingBottom = '1rem';
        
        const mainHeading = document.createElement('h1');
        mainHeading.textContent = 'Barclays PLC';
        mainHeading.style.fontSize = '2rem';
        mainHeading.style.fontWeight = 'bold';
        mainHeading.style.margin = '0';
        mainHeading.style.color = '#333';
        
        const subHeading = document.createElement('h2');
        subHeading.textContent = 'Trade Termsheet';
        subHeading.style.fontSize = '1.5rem';
        subHeading.style.fontWeight = 'normal';
        subHeading.style.margin = '0.5rem 0 0 0';
        subHeading.style.color = '#666';
        
        header.appendChild(mainHeading);
        header.appendChild(subHeading);
        
        // Create table with proper styling
        const table = document.createElement('table');
        table.className = 'w-full border-collapse';
        table.style.border = '1px solid #ddd';
        table.style.borderRadius = '8px';
        table.style.overflow = 'hidden';
        table.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        
        // Create table header
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `
            <th style="background: rgba(61, 202, 253, 0.25); padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: bold;">Field</th>
            <th style="background: rgba(61, 202, 253, 0.25); padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: bold;">Value</th>
        `;
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        for (const key of allowedFields) {
            if (termsheetData[key] !== undefined) {
                const row = document.createElement('tr');
                row.style.borderBottom = '1px solid #eee';
                row.innerHTML = `
                    <td style="padding: 12px; font-weight: bold; background: #f9f9f9; border-right: 1px solid #ddd;">${key}</td>
                    <td style="padding: 12px; background: white;">${termsheetData[key]}</td>
                `;
                tbody.appendChild(row);
            }
        }
        table.appendChild(tbody);
        
        // Modal content
        const content = document.createElement('div');
        content.className = 'bg-white p-8 rounded shadow';
        content.style.maxHeight = '85vh';
        content.style.overflowY = 'auto';
        content.style.minWidth = '600px';
        content.style.maxWidth = '800px';
        content.style.position = 'relative';
        content.style.borderRadius = '12px';
        content.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
        
        // Close button (sticky at the top right)
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.setAttribute('aria-label', 'Close');
        closeBtn.style.position = 'absolute';
        closeBtn.style.top = '12px';
        closeBtn.style.right = '16px';
        closeBtn.style.fontSize = '1.8rem';
        closeBtn.style.background = 'none';
        closeBtn.style.border = 'none';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.color = '#666';
        closeBtn.style.width = '32px';
        closeBtn.style.height = '32px';
        closeBtn.style.borderRadius = '50%';
        closeBtn.style.display = 'flex';
        closeBtn.style.alignItems = 'center';
        closeBtn.style.justifyContent = 'center';
        closeBtn.onmouseover = function() { this.style.background = '#f0f0f0'; };
        closeBtn.onmouseout = function() { this.style.background = 'none'; };
        closeBtn.onclick = function() { modal.remove(); };
        
        content.appendChild(closeBtn);
        content.appendChild(header);
        content.appendChild(table);
        modal.appendChild(content);
        modal.style.display = 'flex';
    } catch (err) {
        alert('Failed to load termsheet: ' + err.message);
    }
}

    const TERMSHEET_SERVICE_URL = "http://localhost:8013/api/equity-termsheet-capture";

async function fetchTermsheets() {
    const response = await fetch(`${TERMSHEET_SERVICE_URL}/equity-termsheets`);
    if (!response.ok) throw new Error("Failed to fetch termsheets");
    const data = await response.json();
    // The termsheets object is a list of trade data
    return data;
}

// Example usage: fetch and display all termsheet trades in a table
window.loadAndShowTermsheets = async function() {
    try {
        const termsheetTrades = await fetchTermsheets();
        // Only call renderTermsheetsTable if container exists and termsheetTrades is not null
        if (typeof renderTermsheetsTable === 'function') {
            renderTermsheetsTable(termsheetTrades || []);
        }
    } catch (err) {
        alert('Failed to load termsheets: ' + err.message);
        console.error('Error fetching termsheets:', err);
    }
}

function renderTermsheetsTable(trades) {
    let container = document.getElementById('termsheet-trades-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'termsheet-trades-container';
        document.body.appendChild(container);
    }
    container.innerHTML = '';
    const table = document.createElement('table');
    table.className = 'w-full text-sm text-left text-gray-500 bg-white rounded shadow';
    const thead = document.createElement('thead');
    thead.innerHTML = `<tr>
        <th class="px-4 py-2">Trade ID</th>
        <th class="px-4 py-2">ISIN</th>
        <th class="px-4 py-2">Symbol</th>
        <th class="px-4 py-2">Quantity</th>
        <th class="px-4 py-2">Price</th>
        <th class="px-4 py-2">Trade Date</th>
        <th class="px-4 py-2">Counterparty</th>
        <th class="px-4 py-2">Actions</th>
    </tr>`;
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    (trades || []).forEach(trade => {
        // Skip null/blank entries
        if (!trade || (typeof trade === 'object' && Object.keys(trade).length === 0)) return;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-4 py-2">${trade["Trade ID"] || trade["trade_id"] || ''}</td>
            <td class="px-4 py-2">${trade["ISIN"] || ''}</td>
            <td class="px-4 py-2">${trade["Symbol"] || ''}</td>
            <td class="px-4 py-2">${trade["Quantity"] || ''}</td>
            <td class="px-4 py-2">${trade["Price"] || ''}</td>
            <td class="px-4 py-2">${trade["Trade Date"] || ''}</td>
            <td class="px-4 py-2">${trade["Counterparty"] || ''}</td>
            <td class="px-4 py-2"><a href="#" onclick="showTermsheet('${trade["Trade ID"] || trade["trade_id"]}');return false;">View Termsheet</a></td>
        `;
        tbody.appendChild(row);
    });
    table.appendChild(tbody);
    container.appendChild(table);
}

// Real-time Firestore listener for termsheets
function listenToTermsheetsRealtime() {
  db.collection("termsheets").onSnapshot((snapshot) => {
    const termsheets = [];
    snapshot.forEach(doc => termsheets.push({ id: doc.id, ...doc.data() }));
    renderTermsheetsTable(termsheets);
  });
}

// Call this function to start listening (e.g., on page load or when showing the termsheet view)
// listenToTermsheetsRealtime();

// Firebase config for barclays-network-management
const firebaseConfig = {
  apiKey: "AIzaSyCgK8fg7tXgaU-0oWcCGO9bdHWnwImLBmQ",
  authDomain: "barclays-network-management.firebaseapp.com",
  projectId: "barclays-network-management",
  storageBucket: "barclays-network-management.firebasestorage.app",
  messagingSenderId: "308811523712",
  appId: "1:308811523712:web:69e0bc7919d1057cbc2865",
  measurementId: "G-X0HKTS2D3E"
};
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();
window.db = db;

// Fallback function in case the main one fails to load
if (typeof window.handleTermsheetFileUpload === 'undefined') {
    window.handleTermsheetFileUpload = function(event) {
        console.log('Fallback handleTermsheetFileUpload called');
        alert('File upload function is loading. Please try again in a moment.');
    };
}

// Check if the equity termsheet service is running
window.checkEquityTermsheetService = async function() {
    try {
        const response = await fetch('http://localhost:8013/api/equity-termsheet-capture/equity-termsheets', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        return response.ok;
    } catch (error) {
        console.error('Equity termsheet service check failed:', error);
        return false;
    }
};

// Ensure the function is properly defined
window.handleTermsheetFileUpload = function(event) {
    const files = event.target.files;
    if (!files.length) return;
    
    const file = files[0];
        const lowerName = file.name.toLowerCase();
    
    let endpoint = "";
        if (lowerName.startsWith("equity")) {
            endpoint = "http://localhost:8013/api/equity-termsheet-capture/equity-termsheets";
        } else if (lowerName.startsWith("fx") || lowerName.startsWith("forex")) {
            endpoint = "http://localhost:8014/api/forex-termsheet-capture/forex-termsheets";
        } else {
            alert("Unknown file type. File name must start with 'equity' or 'fx'.");
            return;
        }
    
        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
            const termsheets = results.data;
            const idKeys = ['Trade ID', 'TradeID', 'Trade_Id', 'Trade Id', 'tradeid', 'trade_id', 'trade id', 'id', 'ID'];
                const valid = [];
                const skipped = [];
            
                for (const ts of termsheets) {
                    let found = false;
                    for (const key of idKeys) {
                        if (ts[key] && String(ts[key]).trim() !== "") {
                            found = true;
                            break;
                        }
                    }
                if (found) {
                    valid.push(ts);
                } else {
                    skipped.push(ts);
                }
            }
            
                if (skipped.length > 0) {
                alert(`Skipped ${skipped.length} row(s) missing a unique identifier. Only valid rows will be uploaded.`);
                }
            
                if (valid.length > 0) {
                    fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(valid)
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert(`Successfully uploaded ${data.length} termsheets. Skipped ${skipped.length} rows.`);
                    })
                    .catch(error => {
                        console.error('Error uploading termsheets:', error);
                    alert('Failed to upload termsheets: ' + error.message);
                    });
                }
            }
    });
}

// Fetch and render forex reconciliation table from Firebase
async function fetchForexReconciliationResultsFromFirebase() {
    // Determine which collection to fetch from based on current reconciliation type
    const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
    let collectionName = 'fx_reconciliation_FOBO'; // default
    
    if (reconTypeSelect && reconTypeSelect.value === 'fofo') {
        collectionName = 'fx_reconciliation_FOFO';
    } else {
        collectionName = 'fx_reconciliation_FOBO';
    }
    
    console.log(`Fetching forex reconciliation from collection: ${collectionName}`);
    const snapshot = await db.collection(collectionName).get();
    const results = [];
    snapshot.forEach(doc => results.push({ id: doc.id, ...doc.data() }));
    console.log(`Found ${results.length} forex reconciliation results`);
    return results;
}

// Fetch and render equity reconciliation table from Firebase
async function fetchEquityReconciliationResultsFromFirebase() {
    // Determine which collection to fetch from based on current reconciliation type
    const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
    let collectionName = 'eq_reconciliation_FOBO'; // default
    
    if (reconTypeSelect && reconTypeSelect.value === 'fofo') {
        collectionName = 'eq_reconciliation_FOFO';
    } else {
        collectionName = 'eq_reconciliation_FOBO';
    }
    
    console.log(`Fetching equity reconciliation from collection: ${collectionName}`);
    const snapshot = await db.collection(collectionName).get();
    const results = [];
    snapshot.forEach(doc => results.push({ id: doc.id, ...doc.data() }));
    console.log(`Found ${results.length} equity reconciliation results`);
    return results;
}

async function triggerBackendReconciliation(systemType) {
    // Adjust the backend URL and port as needed
            const url = `http://localhost:8025/api/forex-reconciliation/reconcile/${systemType}?save_to_firebase=true`;
    try {
        await fetch(url, { method: 'GET' });
    } catch (err) {
        // Optionally handle error
        console.error('Failed to trigger backend reconciliation:', err);
    }
}

async function triggerEquityBackendReconciliation(systemType) {
    // Equity reconciliation backend URL and port
            const url = `http://localhost:8026/api/equity-reconciliation/reconcile/${systemType}?save_to_firebase=true`;
    try {
        await fetch(url, { method: 'GET' });
    } catch (err) {
        // Optionally handle error
        console.error('Failed to trigger equity backend reconciliation:', err);
    }
}

window.loadAndShowForexReconciliation = async function() {
    console.log('Loading forex reconciliation...');
    // Determine system type from UI selection (default to FO-BO if not found)
    let systemType = 'FO-BO';
    const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
    if (reconTypeSelect && reconTypeSelect.value === 'fofo') {
        systemType = 'FO-FO';
    } else {
        systemType = 'FO-BO';
    }
    console.log('Forex system type:', systemType);
    
    try {
    await triggerBackendReconciliation(systemType);
        // Wait a moment for backend to write to Firestore
    await new Promise(res => setTimeout(res, 1000));
        const results = await fetchForexReconciliationResultsFromFirebase();
        console.log('Forex results:', results);
        renderReconciliationTable(results, 'Forex');
    } catch (err) {
        console.error('Forex reconciliation error:', err);
        alert('Failed to load reconciliation results: ' + err.message);
    }
}

window.loadAndShowEquityReconciliation = async function() {
    console.log('Loading equity reconciliation...');
    // Determine system type from UI selection (default to FO-BO if not found)
    let systemType = 'FO-BO';
    const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
    if (reconTypeSelect && reconTypeSelect.value === 'fofo') {
        systemType = 'FO-FO';
    } else {
        systemType = 'FO-BO';
    }
    console.log('Equity system type:', systemType);
    
    try {
        await triggerEquityBackendReconciliation(systemType);
        // Wait a moment for backend to write to Firestore
        await new Promise(res => setTimeout(res, 1000));
        const results = await fetchEquityReconciliationResultsFromFirebase();
        console.log('Equity results:', results);
        renderReconciliationTable(results, 'Equity');
    } catch (err) {
        console.error('Equity reconciliation error:', err);
        alert('Failed to load equity reconciliation results: ' + err.message);
    }
}

// Missing functions that are referenced in HTML
window.toggleInstrumentType = function() {
    const instrumentToggle = document.getElementById('instrument-toggle');
    if (instrumentToggle) {
        if (instrumentToggle.value === 'equity') {
            window.loadAndShowEquityReconciliation();
        } else if (instrumentToggle.value === 'forex') {
            window.loadAndShowForexReconciliation();
        }
    }
};

window.toggleReconciliationSection = function() {
    const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
    const fofoSection = document.getElementById('fofo-section');
    const foboSection = document.getElementById('fobo-section');
    
    if (reconTypeSelect && fofoSection && foboSection) {
        if (reconTypeSelect.value === 'fofo') {
            fofoSection.style.display = 'block';
            foboSection.style.display = 'none';
        } else if (reconTypeSelect.value === 'fobo') {
            fofoSection.style.display = 'none';
            foboSection.style.display = 'block';
        }
        
        // Clear both table bodies to prevent data mixing
        const fofoTableBody = document.getElementById('fofo-table-body');
        const foboTableBody = document.getElementById('fobo-table-body');
        if (fofoTableBody) fofoTableBody.innerHTML = '';
        if (foboTableBody) foboTableBody.innerHTML = '';
        
        // Trigger the appropriate reconciliation based on current instrument selection
        const instrumentToggle = document.getElementById('instrument-toggle');
        if (instrumentToggle) {
            if (instrumentToggle.value === 'equity') {
                window.loadAndShowEquityReconciliation();
            } else if (instrumentToggle.value === 'forex') {
            window.loadAndShowForexReconciliation();
            } else {
                // Default to forex if no selection
                window.loadAndShowForexReconciliation();
            }
        }
    }
};

function renderReconciliationTable(rows, instrument = 'Forex', showPlaceholder = false) {
    console.log('Rendering reconciliation table:', { rows, instrument, showPlaceholder });
    
    // Use the existing table structure from the HTML
    const fofoTableBody = document.getElementById('fofo-table-body');
    const foboTableBody = document.getElementById('fobo-table-body');
    
    console.log('Table bodies found:', { fofoTableBody: !!fofoTableBody, foboTableBody: !!foboTableBody });
    
    if (!fofoTableBody || !foboTableBody) {
        console.error('Reconciliation table bodies not found');
        console.log('Available elements:', {
            fofoTableBody: !!fofoTableBody,
            foboTableBody: !!foboTableBody
        });
        return;
    }
    
    // Clear existing content from both tables to prevent data mixing
    fofoTableBody.innerHTML = '';
    foboTableBody.innerHTML = '';
    
    console.log('Cleared both table bodies');
    
    // Determine which table to use based on the current selection
    const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
    const isFOFO = reconTypeSelect && reconTypeSelect.value === 'fofo';
    const isFOBO = reconTypeSelect && reconTypeSelect.value === 'fobo';
    
    // Default to FOBO if no selection
    const targetTableBody = (isFOFO) ? fofoTableBody : foboTableBody;
    
    console.log('Table selection:', { 
        reconTypeSelect: reconTypeSelect?.value, 
        isFOFO, 
        isFOBO, 
        targetTableBody: targetTableBody?.id 
    });
    
    // Show placeholder if no data
    if (showPlaceholder || rows.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="5" class="px-4 py-2 text-center">No reconciliation data available</td>';
        targetTableBody.appendChild(tr);
        return;
    }
    
    // Check if we have equity data to determine table structure
    const hasEquityData = rows.some(row => 
        (row.SystemA && typeof row.SystemA === 'string') || 
        (row.FrontOffice && typeof row.FrontOffice === 'string')
    );
    
    // Render rows
    rows.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = 'border-b hover:bg-gray-50';
        
        if (hasEquityData) {
            // Handle equity data format
            let discrepanciesHtml = '';
            if (Array.isArray(row.Discrepancy) && row.Discrepancy.length > 0) {
                discrepanciesHtml = row.Discrepancy.map(d => `<div>${d}</div>`).join('');
            } else {
                discrepanciesHtml = '<span>No discrepancies</span>';
            }
            
            // Format action - remove discrepancy names, keep only the action part
            let actionHtml = '';
            if (Array.isArray(row.Action)) {
                actionHtml = row.Action.map(a => {
                    // Remove the discrepancy name (e.g., "Symbol mismatch: " part)
                    const actionText = a.includes(': ') ? a.split(': ')[1] : a;
                    return `<div>${actionText}</div>`;
                }).join('');
            } else {
                actionHtml = '<span>No action required</span>';
            }
            
            tr.innerHTML = `
                <td class="px-4 py-2 align-top">${row.TradeID || ''}</td>
                <td class="px-4 py-2">${row.SystemA || row.FrontOffice || ''}</td>
                <td class="px-4 py-2">${row.SystemB || row.BackOffice || ''}</td>
                <td class="px-4 py-2">${discrepanciesHtml}</td>
                <td class="px-4 py-2">${actionHtml}</td>
            `;
        } else {
            // Handle forex data format - display in sentence format like equity
            let discrepanciesHtml = '';
            let actionsHtml = '';
            if (Array.isArray(row.discrepancies) && row.discrepancies.length > 0) {
                discrepanciesHtml = row.discrepancies.map(d => {
                    // Format discrepancy to show field name and values like "Settlement date: 5/16/2025 vs 5/26/2025"
                    if (d.systemA !== undefined && d.systemB !== undefined) {
                        return `<div>${d.reason}: ${d.systemA} vs ${d.systemB}</div>`;
                    } else if (d.frontOffice !== undefined && d.backOffice !== undefined) {
                        return `<div>${d.reason}: ${d.frontOffice} vs ${d.backOffice}</div>`;
                    } else {
                        return `<div>${d.reason}</div>`;
                    }
                }).join('');
                
                actionsHtml = row.discrepancies.map(d => {
                    return `<div>${d.action || 'No action required'}</div>`;
                }).join('');
            } else {
                discrepanciesHtml = '<span>No discrepancies</span>';
                actionsHtml = '<span>No action required</span>';
            }
            
            // Format forex data into sentence format
            let systemAHtml = '';
            let systemBHtml = '';
            
            if (row.SystemA && row.SystemB) {
                // FO-FO format
                const a = row.SystemA;
                const b = row.SystemB;
                systemAHtml = `${a['buy/sell'] || ''} Spot contract of ${a.instrument || ''} worth ${a.notionalamount || ''} at the rate of ${a.fxrate || ''}, to be settled on ${a.settlementdate || ''}. Counterparty: ${a.counterparty || ''}`;
                systemBHtml = `${b['buy/sell'] || ''} Spot contract of ${b.instrument || ''} worth ${b.notionalamount || ''} at the rate of ${b.fxrate || ''}, to be settled on ${b.settlementdate || ''}. Counterparty: ${b.counterparty || ''}`;
            } else if (row.FrontOffice && row.BackOffice) {
                // FO-BO format
                const f = row.FrontOffice;
                const b = row.BackOffice;
                systemAHtml = `${f['buy/sell'] || ''} Spot contract of ${f.instrument || ''} worth ${f.notionalamount || ''} at the rate of ${f.fxrate || ''}, to be settled on ${f.settlementdate || ''}. Counterparty: ${f.counterparty || ''}`;
                systemBHtml = `${b['buy/sell'] || ''} Spot contract of ${b.instrument || ''} worth ${b.notionalamount || ''} at the rate of ${b.fxrate || ''}, to be settled on ${b.settlementdate || ''}. Counterparty: ${b.counterparty || ''}`;
            }
            
            tr.innerHTML = `
                <td class="px-4 py-2 align-top">${row.TradeID || ''}</td>
                <td class="px-4 py-2">${systemAHtml}</td>
                <td class="px-4 py-2">${systemBHtml}</td>
                <td class="px-4 py-2">${discrepanciesHtml}</td>
                <td class="px-4 py-2">${actionsHtml}</td>
            `;
        }
        targetTableBody.appendChild(tr);
    });
}

// --- Reconciliation Toggle Logic ---
window.setReconInstrument = function(type) {
    var equityElem = document.getElementById('recon-instrument-equity');
    var forexElem = document.getElementById('recon-instrument-forex');
    if (equityElem) equityElem.className = 'px-3 py-1 rounded border mr-2 text-gray-800 font-normal';
    if (forexElem) forexElem.className = 'px-3 py-1 rounded border mr-8 text-gray-800 font-normal';
    if (type === 'Equity') {
        if (equityElem) equityElem.className += ' bg-blue-200 border-blue-600 font-bold';
        if (forexElem) forexElem.className += ' bg-gray-200';
    } else {
        if (forexElem) forexElem.className += ' bg-blue-200 border-blue-600 font-bold';
        if (equityElem) equityElem.className += ' bg-gray-200';
    }
    // Optionally, filter table data here
};
window.setReconSystemEntry = function(type) {
    var fofoSection = document.getElementById('fofo-table-section');
    var foboSection = document.getElementById('fobo-table-section');
    if (type === 'FO-FO') {
        if (fofoSection) fofoSection.style.display = '';
        if (foboSection) foboSection.style.display = 'none';
    } else {
        if (fofoSection) fofoSection.style.display = 'none';
        if (foboSection) foboSection.style.display = '';
    }
};
window.addEventListener('DOMContentLoaded', function() {
    var instrumentSelect = document.getElementById('recon-instrument-select');
    var systemEntrySelect = document.getElementById('recon-system-entry-select');
    var fofoSection = document.getElementById('fofo-table-section');
    var foboSection = document.getElementById('fobo-table-section');
    if (instrumentSelect && systemEntrySelect) {
        setReconInstrument(instrumentSelect.value);
        setReconSystemEntry(systemEntrySelect.value);
    } else {
        setReconInstrument('Equity');
        setReconSystemEntry('FO-FO');
    }
    // Always show the default table section (with headers) on load
    if (fofoSection && foboSection) {
        fofoSection.style.display = '';
        foboSection.style.display = 'none';
    }
    

});

// Only declare this ONCE at the top before any overrides
if (typeof originalShowView === 'undefined') {
    var originalShowView = window.showView;
}
// Add to showView logic
(function() {
    const originalShowView = window.showView || function(viewId) {
    document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        const viewElement = document.getElementById(viewId);
        if (viewElement) {
            viewElement.classList.add('active');
        } else {
            console.warn(`No element found with id="${viewId}"`);
        }
    // Page-level title functionality removed - all views now use their internal headings
        if (typeof renderAllTables === 'function') renderAllTables();
    };
    window.showView = function(viewId) {
        originalShowView(viewId);
        const viewElem = document.getElementById(viewId);
        if (viewElem) {
            viewElem.classList.add('active');
        } else {
            console.warn(`No element found with id="${viewId}"`);
        }
        if (viewId === 'consolidated-data' && typeof window.loadAndShowConsolidatedData === 'function') {
            window.loadAndShowConsolidatedData();
        }
        if (viewId === 'lifecycle-events' && typeof window.loadAndShowLifecycleEvents === 'function') {
        window.loadAndShowLifecycleEvents();
    }
    if (viewId === 'reconciliation') {
        console.log('Reconciliation view activated');
        // Automatically trigger reconciliation based on current instrument selection
        const instrumentToggle = document.getElementById('instrument-toggle');
        const reconTypeSelect = document.getElementById('fofo-fobo-toggle');
        
        console.log('Current selections:', {
            instrument: instrumentToggle?.value,
            reconType: reconTypeSelect?.value
        });
        
        if (instrumentToggle && instrumentToggle.value === 'equity') {
            window.loadAndShowEquityReconciliation();
        } else {
            // Default to forex if no selection or if forex is selected
            window.loadAndShowForexReconciliation();
        }
    }
    if (viewId === 'trade-validation') {
        window.loadAndShowTradeValidation();
    }
    if (viewId === 'overview') {
        console.log('Debug: Overview view shown, calling updateOverviewStats');
        if (typeof window.updateOverviewStats === 'function') {
            window.updateOverviewStats();
        } else {
            console.log('Debug: updateOverviewStats function not available in showView');
        }
    }
    };
})();

// Persistent controls for lifecycle events
let lifecycleControls = null;
let lifecycleSearchBox = null;
let lifecycleInstrumentSelect = null;
let lifecycleEventTypeSelect = null;
let lifecycleSearchBtn = null;

window.loadAndShowLifecycleEvents = async function() {
    try {
        // Determine selected instrument and event type
        let instrument = 'Forex';
        let eventType = 'Maturity';
        // If controls exist, get current selection
        if (lifecycleInstrumentSelect) instrument = lifecycleInstrumentSelect.value;
        if (lifecycleEventTypeSelect) eventType = lifecycleEventTypeSelect.value;
        let trades = [];
        if (instrument === 'Forex') {
            // Map event type to backend endpoint
            let eventEndpoint = 'maturity-forex';
            if (eventType === 'Maturity') eventEndpoint = 'maturity-forex';
            else if (eventType === 'Coupon Rate') eventEndpoint = 'coupon rate';
            else if (eventType === 'Early Redemption') eventEndpoint = 'early-redemption';
            else if (eventType === 'Barrier Monitoring') eventEndpoint = 'barrier-monitoring';
            // Fetch from backend - use the correct endpoint for Forex
            const res = await fetch(`http://localhost:8024/api/trade-lifecycle/api/event/${eventEndpoint}`);
            if (res.ok) trades = await res.json();
        } else if (instrument === 'Equity') {
            // Existing logic for equity
            const equitySnap = await db.collection('trades').get();
            trades = [];
            equitySnap.forEach(doc => {
                const data = doc.data();
                data.Instrument = 'Equity';
                data.EventType = data.EventType || data.event_type || 'Maturity';
                trades.push(data);
            });
        }
        console.log('Debug: Trades received:', trades);
        console.log('Debug: Number of trades:', trades.length);
        renderLifecycleEventsControlsAndTable(trades);
    } catch (err) {
        alert('Failed to load lifecycle events: ' + err.message);
        console.error('Error fetching lifecycle events:', err);
    }
}

function renderLifecycleEventsControlsAndTable(trades) {
    let container = document.getElementById('lifecycle-events-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'lifecycle-events-container';
        var el = document.getElementById('lifecycle-events');
        if (el) el.textContent = title;
    }
    // --- Controls Row (create only once) ---
    if (!lifecycleControls) {
        lifecycleControls = document.createElement('div');
        lifecycleControls.style.display = 'flex';
        lifecycleControls.style.justifyContent = 'flex-start';
        lifecycleControls.style.alignItems = 'center';
        lifecycleControls.className = 'mb-4';

        // Search box and button
        lifecycleSearchBox = document.createElement('input');
        lifecycleSearchBox.type = 'text';
        lifecycleSearchBox.placeholder = 'Search Trade ID or Symbol...';
        lifecycleSearchBox.className = 'border rounded px-2 py-1 text-sm mr-2';
        lifecycleSearchBtn = document.createElement('button');
        lifecycleSearchBtn.textContent = 'Search';
        lifecycleSearchBtn.className = 'border rounded px-2 py-1 text-sm bg-gray-200 hover:bg-gray-300 mr-2';
        const searchBoxDiv = document.createElement('div');
        searchBoxDiv.appendChild(lifecycleSearchBox);
        searchBoxDiv.appendChild(lifecycleSearchBtn);
        lifecycleControls.appendChild(searchBoxDiv);

        // Instrument toggle (Equity/Forex)
        lifecycleInstrumentSelect = document.createElement('select');
        lifecycleInstrumentSelect.className = 'border rounded px-2 py-1 text-sm mr-2';
        ['Forex', 'Equity'].forEach(inst => {
            const opt = document.createElement('option');
            opt.value = inst;
            opt.textContent = inst;
            lifecycleInstrumentSelect.appendChild(opt);
        });
        lifecycleControls.appendChild(lifecycleInstrumentSelect);

        // Event type toggle
        const eventTypes = ['Maturity', 'Coupon Rate', 'Early Redemption', 'Barrier Monitoring'];
        lifecycleEventTypeSelect = document.createElement('select');
        lifecycleEventTypeSelect.className = 'border rounded px-2 py-1 text-sm';
        eventTypes.forEach(type => {
            const opt = document.createElement('option');
            opt.value = type;
            opt.textContent = type;
            lifecycleEventTypeSelect.appendChild(opt);
        });
        lifecycleControls.appendChild(lifecycleEventTypeSelect);

        container.appendChild(lifecycleControls);

        // Attach event handlers ONCE
        lifecycleSearchBtn.onclick = function() {
            renderLifecycleEventsTableOnly(trades);
        };
        lifecycleSearchBox.onkeypress = function(e) {
            if (e.key === 'Enter') lifecycleSearchBtn.onclick();
        };
        lifecycleInstrumentSelect.onchange = function() {
            // Reload data when instrument changes
            loadAndShowLifecycleEvents();
        };
        lifecycleEventTypeSelect.onchange = function() {
            renderLifecycleEventsTableOnly(trades);
        };
    }
    renderLifecycleEventsTableOnly(trades);
}

function renderLifecycleEventsTableOnly(trades) {
    console.log('Debug: renderLifecycleEventsTableOnly called with trades:', trades);
    console.log('Debug: Number of trades in render:', trades.length);
    console.log('Debug: First trade object:', trades[0]);
    let container = document.getElementById('lifecycle-events-container');
    let table = container.querySelector('table');
    if (table) table.remove();
    table = document.createElement('table');
    table.className = 'lifecycle-table w-full text-sm text-center';
    // Determine the correct column header based on selected instrument
    let instrumentHeader = lifecycleInstrumentSelect.value;
    let columnHeader = instrumentHeader === 'Equity' ? 'Symbol' : 'Currency Pair';

    const thead = document.createElement('thead');
    thead.innerHTML = `<tr>
        <th class="px-4 py-2 text-center" style="background: rgba(61, 202, 253, 0.25) !important;">Trade ID</th>
        <th class="px-4 py-2 text-center" style="background: rgba(61, 202, 253, 0.25) !important;">${columnHeader}</th>
        <th class="px-4 py-2 text-center" style="background: rgba(61, 202, 253, 0.25) !important;">Event Type</th>
        <th class="px-4 py-2 text-center" style="background: rgba(61, 202, 253, 0.25) !important;">Event Date</th>
        <th class="px-4 py-2 text-center" style="background: rgba(61, 202, 253, 0.25) !important;">Event Status</th>
        <th class="px-4 py-2 text-center" style="background: rgba(61, 202, 253, 0.25) !important;">Actions</th>
    </tr>`;
    table.appendChild(thead);
    const tbody = document.createElement('tbody');

    // --- Filtering logic ---
    let filtered = trades;
    console.log('Debug: Initial filtered trades:', filtered.length);
    
    const search = lifecycleSearchBox.value.trim().toLowerCase();
    if (search) {
        filtered = filtered.filter(r => {
            const tradeId = (r.TradeID || '').toLowerCase();
            const isForex = (r.TradeID || '').toUpperCase().startsWith('FX');
            const symbolOrCurrency = isForex ? (r.CurrencyPair || '').toLowerCase() : (r.Symbol || '').toLowerCase();
            return tradeId.includes(search) || symbolOrCurrency.includes(search);
        });
        console.log('Debug: After search filter:', filtered.length);
    }
    
    const instrument = lifecycleInstrumentSelect.value;
    console.log('Debug: Selected instrument:', instrument);
    if (instrument) {
        if (instrument === 'Forex') {
            // Filter for FX trades (TradeID starting with 'FX')
            filtered = filtered.filter(r => (r.TradeID || '').toUpperCase().startsWith('FX'));
        } else if (instrument === 'Equity') {
            // Filter for non-FX trades (TradeID not starting with 'FX')
            filtered = filtered.filter(r => !(r.TradeID || '').toUpperCase().startsWith('FX'));
        }
        console.log('Debug: After instrument filter:', filtered.length);
    }
    
    const eventType = lifecycleEventTypeSelect.value;
    console.log('Debug: Selected event type:', eventType);
    if (eventType) {
        filtered = filtered.filter(r => (r.EventType || r.event_type || 'Maturity') === eventType);
        console.log('Debug: After event type filter:', filtered.length);
    }

    // --- Render rows ---
    if (filtered.length > 0) {
        filtered.forEach(trade => {
            // Check if trade should be auto-approved based on settlement date
            let eventStatus = trade.EventStatus || 'Pending';
            let settlementDate = trade.SettlementDate || trade.settlementDate;
            
            if (settlementDate && eventStatus === 'Pending') {
                let today = new Date();
                let parsedSettle = parseFlexibleDate(settlementDate);
                
                if (parsedSettle) {
                    let settleDateOnly = new Date(parsedSettle.getFullYear(), parsedSettle.getMonth(), parsedSettle.getDate());
                    let todayDateOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                    
                    // Auto-approve past dates
                    if (settleDateOnly < todayDateOnly) {
                        eventStatus = 'Approved';
                        // Auto-upload to fx_lifecycle
                        if (typeof firebase !== 'undefined' && typeof db !== 'undefined') {
                            const docId = trade.TradeID + '_' + (trade.EventType || (trade.event_type || 'Lifecycle'));
                            db.collection('fx_lifecycle').doc(docId).set({ ...trade, EventStatus: 'Approved' }, { merge: true });
                        }
                    }
                }
            }
            
            // Determine status styling
            let statusClass = 'text-gray-600 bg-gray-100';
            if (eventStatus === 'Approved') {
                statusClass = 'text-green-600 bg-green-100';
            } else if (eventStatus === 'Pending') {
                statusClass = 'text-yellow-600 bg-yellow-100';
            }
            
            // Determine if this is a forex or equity trade
            const isForex = (trade.TradeID || '').toUpperCase().startsWith('FX');
            const symbolOrCurrency = isForex ? (trade.CurrencyPair || '') : (trade.Symbol || '');
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="px-4 py-2 text-center">${trade.TradeID || ''}</td>
                <td class="px-4 py-2 text-center">${symbolOrCurrency}</td>
                <td class="px-4 py-2 text-center">${trade.EventType || trade.event_type || 'Maturity'}</td>
                <td class="px-4 py-2 text-center">${trade.EventDate || trade.TradeDate || ''}</td>
                <td class="px-4 py-2 text-center"><span class="rounded px-2 py-1 font-semibold ${statusClass}">${eventStatus}</span></td>
                <td class="px-4 py-2 text-center"><button class="px-2 py-1 rounded font-semibold" style="background-color: #00AEEF; color: white; border: none;" onclick="showLifecycleDetailsModal('${trade.TradeID}', '${isForex ? 'Forex' : 'Equity'}')">Check</button></td>
            `;
            tbody.appendChild(tr);
        });
    }
    table.appendChild(tbody);
    container.appendChild(table);
    if (filtered.length === 0) {
        tbody.innerHTML = '';
    }
}

window.showLifecycleDetailsModal = async function(tradeId, instrument) {
    let trade = null;
    if (instrument === 'Forex') {
        const doc = await db.collection('fx_capture').doc(tradeId).get();
        if (doc.exists) trade = doc.data();
    } else if (instrument === 'Equity') {
        const doc = await db.collection('trades').doc(tradeId).get();
        if (doc.exists) trade = doc.data();
    }
    if (!trade) {
        alert('Trade not found');
        return;
    }
    // Create modal
    let modal = document.getElementById('lifecycle-details-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'lifecycle-details-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(0,0,0,0.5)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '1000';
        modal.onclick = function(e) { if (e.target === modal) modal.remove(); };
        document.body.appendChild(modal);
    } else {
        modal.innerHTML = '';
    }
    // Create details table (show different fields for Equity and Forex)
    const table = document.createElement('table');
    table.className = 'bg-white p-4 rounded shadow';
    table.style.minWidth = '400px';
    let fields = [];
    if (instrument === 'Forex') {
        fields = [
            { label: 'Trade ID', key: 'TradeID' },
            { label: 'Currency Pair', key: 'CurrencyPair' },
            { label: 'FX Rate', key: 'FXRate' },
            { label: 'Notional Amount', key: 'NotionalAmount' },
            { label: 'Settlement Date', key: 'SettlementDate' }
        ];
    } else if (instrument === 'Equity') {
        fields = [
            { label: 'Trade ID', key: 'TradeID' },
            { label: 'Symbol', key: 'Symbol' },
            { label: 'Quantity', key: 'Quantity' },
            { label: 'Trade Value', key: 'TradeValue' },
            { label: 'Settlement Date', key: 'SettlementDate' }
        ];
    }
    fields.forEach(f => {
        const row = document.createElement('tr');
        row.innerHTML = `<td class="font-bold px-2 py-1">${f.label}</td><td class="px-2 py-1">${trade[f.key] || ''}</td>`;
        table.appendChild(row);
    });
    // Modal content
    const content = document.createElement('div');
    content.className = 'bg-white p-6 rounded shadow';
    content.style.maxHeight = '80vh';
    content.style.overflowY = 'auto';
    content.style.position = 'relative';
    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.textContent = '×';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.style.position = 'absolute';
    closeBtn.style.top = '8px';
    closeBtn.style.right = '12px';
    closeBtn.style.fontSize = '1.5rem';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.cursor = 'pointer';
    closeBtn.onclick = function() { modal.remove(); };
    content.appendChild(closeBtn);
    content.appendChild(table);

    // --- Approve Button Logic ---
    let isApproved = trade.EventStatus === 'Approved';
    if (!trade.EventStatus) trade.EventStatus = 'Pending';
    let canApprove = false;
    let today = new Date();
    let settlementDate = trade.SettlementDate || trade.settlementDate;
    

    
    if (settlementDate) {
        let parsedSettle = parseFlexibleDate(settlementDate);
        console.log('Settlement:', settlementDate, 'Parsed:', parsedSettle, 'Today:', today);
        
        if (parsedSettle) {
            // Compare dates by setting time to midnight for accurate comparison
            let settleDateOnly = new Date(parsedSettle.getFullYear(), parsedSettle.getMonth(), parsedSettle.getDate());
            let todayDateOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
            
            console.log('SettleDateOnly:', settleDateOnly, 'TodayDateOnly:', todayDateOnly);
            
            // Auto-approve past dates
            if (settleDateOnly < todayDateOnly) {
                if (!isApproved) {
                    console.log('Auto-approving past date trade:', trade.TradeID);
                    trade.EventStatus = 'Approved';
                    isApproved = true;
                    
                    // Auto-upload to fx_lifecycle
                    if (typeof firebase !== 'undefined' && typeof db !== 'undefined') {
                        const docId = trade.TradeID + '_' + (trade.EventType || (trade.event_type || 'Lifecycle'));
                        db.collection('fx_lifecycle').doc(docId).set({ ...trade, EventStatus: 'Approved' }, { merge: true });
                    }
                }
            }
            // Allow manual approval for current date
            else if (settleDateOnly.getTime() === todayDateOnly.getTime()) {
                canApprove = !isApproved;
                console.log('Current date trade - can approve:', canApprove);
            }
            // Future dates - cannot approve (will show gray button)
            else {
                canApprove = false;
                console.log('Future date trade - cannot approve');
            }
        }
    }
    
    if (!isApproved) {
        const approveBtn = document.createElement('button');
        approveBtn.textContent = 'Approve';
        approveBtn.className = 'inline-block mt-4 px-4 py-2 rounded';
        if (canApprove) {
            approveBtn.style.background = '#16a34a'; // green-600
            approveBtn.style.color = '#fff';
        } else {
            approveBtn.style.background = '#9ca3af'; // gray-400
            approveBtn.style.color = '#fff';
            approveBtn.style.cursor = 'not-allowed';
        }
        approveBtn.style.display = 'inline-block';
        approveBtn.style.opacity = '1';
        approveBtn.style.visibility = 'visible';
        approveBtn.style.position = 'relative';
        approveBtn.style.zIndex = '1000';
        approveBtn.onclick = function() {
            if (!canApprove) return;
            showApproveConfirmation(trade, instrument, modal);
            // Firebase upload is now handled automatically in showApproveConfirmation
        };
        content.appendChild(approveBtn);
    } else {
        const approvedMsg = document.createElement('div');
        approvedMsg.textContent = 'Approved!';
        approvedMsg.className = 'mt-4 text-green-600 font-bold';
        content.appendChild(approvedMsg);
    }
    modal.appendChild(content);
    modal.style.display = 'flex';
}

function showApproveConfirmation(trade, instrument, parentModal) {
    // Create confirmation modal
    let confirmModal = document.createElement('div');
    confirmModal.style.position = 'fixed';
    confirmModal.style.top = '0';
    confirmModal.style.left = '0';
    confirmModal.style.width = '100vw';
    confirmModal.style.height = '100vh';
    confirmModal.style.background = 'rgba(0,0,0,0.5)';
    confirmModal.style.display = 'flex';
    confirmModal.style.alignItems = 'center';
    confirmModal.style.justifyContent = 'center';
    confirmModal.style.zIndex = '1100';
    confirmModal.onclick = function(e) { if (e.target === confirmModal) confirmModal.remove(); };
    // Content
    const content = document.createElement('div');
    content.className = 'bg-white p-6 rounded shadow';
    content.style.position = 'relative';
    content.innerHTML = `<div class="mb-4 font-bold">Approve Trade?</div>
        <div class="mb-2">Trade ID: <span class="font-mono">${trade.TradeID}</span></div>
        <div class="mb-4">Settlement Date: <span class="font-mono">${trade.SettlementDate || ''}</span></div>`;
    // Yes/No buttons
    const yesBtn = document.createElement('button');
    yesBtn.textContent = 'Yes';
    yesBtn.className = '';
    yesBtn.style.background = '#16a34a'; // green-600
    yesBtn.style.color = '#fff';
    yesBtn.style.display = 'inline-block';
    yesBtn.style.opacity = '1';
    yesBtn.style.visibility = 'visible';
    yesBtn.style.position = 'relative';
    yesBtn.style.zIndex = '1000';
    const noBtn = document.createElement('button');
    noBtn.textContent = 'No';
    noBtn.className = 'px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500';
    yesBtn.onclick = async function() {
        // Mark as approved in source collection only
        try {
            const update = { EventStatus: 'Approved' };
            if (instrument === 'Forex') {
                await db.collection('fx_capture').doc(trade.TradeID).update(update);
            } else if (instrument === 'Equity') {
                await db.collection('trades').doc(trade.TradeID).update(update);
            }
            
            // Auto-upload to fx_lifecycle when status changes to Approved
            if (typeof firebase !== 'undefined' && typeof db !== 'undefined') {
                const docId = trade.TradeID + '_' + (trade.EventType || (trade.event_type || 'Lifecycle'));
                db.collection('fx_lifecycle').doc(docId).set({ ...trade, EventStatus: 'Approved' }, { merge: true });
            }
            
            confirmModal.remove();
            parentModal.remove();
            // Refresh lifecycle events table
            window.loadAndShowLifecycleEvents();
        } catch (e) {
            alert('Failed to approve trade: ' + e.message);
        }
    };
    noBtn.onclick = function() {
        confirmModal.remove();
    };
    content.appendChild(yesBtn);
    content.appendChild(noBtn);
    confirmModal.appendChild(content);
    document.body.appendChild(confirmModal);
}

// Add this function to fetch and render consolidated data from the backend
window.loadAndShowConsolidatedData = async function() {
    // Define the required columns, with TradeID first
    const columns = [
        'TradeID', 'TradeDate', 'ValueDate', 'TradeTime', 'TraderID', 'Counterparty', 'Counterparty ID', 'LEI', 'CurrencyPair', 'BuySell', 'DealtCurrency', 'BaseCurrency', 'TermCurrency', 'NotionalAmount', 'FXRate', 'TradeStatus', 'SettlementStatus', 'SettlementMethod', 'Broker', 'ExecutionVenue', 'ProductType', 'MaturityDate', 'ConfirmationTimestamp', 'SettlementDate', 'BookingLocation', 'Portfolio', 'TradeVersion', 'CancellationFlag', 'AmendmentFlag', 'RiskSystemID', 'RegulatoryReportingStatus', 'TradeSourceSystem', 'ConfirmationMethod', 'ConfirmationStatus', 'SettlementInstructions', 'Custodian_Name', 'NettingEligibility', 'TradeComplianceStatus', 'KYCCheck', 'SanctionsScreening', 'ExceptionFlag', 'AuditTrailRef', 'CommissionAmount', 'CommissionCurrency', 'BrokerageFee', 'BrokerageCurrency', 'CustodyFee', 'CustodyCurrency', 'SettlementCost', 'SettlementCurrency', 'FXGainLoss', 'PnlCalculated', 'CostAllocationStatus', 'CostCenter', 'ExpenseApprovalStatus', 'CostBookedDate', 'Exception Type', 'Exception Description', 'Exception Resolution', 'Reporting Regulation', 'Exception Reason', 'Reporting Resolution', 'RID', 'ISIN', 'Symbol', 'Trading Venue', 'Stock_Currency', 'Country_of_Trade', 'Instrument_Status', 'ClientID_Equity', 'KYC_Status_Equity', 'Reference_Data_Validated', 'Margin_Type', 'Margin_Status', 'Client_Approval_Status_Equity', 'ClientID_Forex', 'KYC_Status_Forex', 'Expense_Approval_Status', 'Client Approval Status(forex)', 'Custodian_Ac_no', 'Beneficiary_Client_ID', 'Settlement_Cycle', 'EffectiveDate_Equity', 'ConfirmationStatus_Equity', 'SWIFT_Equity', 'BeneficiaryName_Equity', 'Account_Number_Equity', 'ABA_Equity', 'BSB_Equity', 'IBAN_Equity', 'SORT_Equity', 'Zengin_Equity', 'Settlement_Method_Equity', 'EffectiveDate_Forex', 'ConfirmationStatus_Forex', 'Account Number_Forex', 'SWIFT_Forex', 'BeneficiaryName_Forex', 'ABA_Forex', 'BSB_Forex', 'IBAN_Forex', 'SORT_Forex', 'Zengin_Forex', 'Settlement_Method_Forex', 'Document ID'
    ];
    
    // Field name mappings for common variations
    const fieldMappings = {
        'Counterparty ID': ['assignedAccountId', 'CounterpartyID', 'CounterpartyId', 'counterparty_id', 'counterpartyId', 'Counterparty_ID', 'Counterparty ID', 'COUNTERPARTY ID', 'COUNTERPARTYID', 'counterparty id', 'counterpartyid', 'Counterparty ID '],
        'LEI': ['assignedAccountLei', 'lei', 'Lei', 'LegalEntityIdentifier', 'legal_entity_identifier'],
        'ExecutionVenue': ['ExecutionVenue', 'execution_venue', 'TradingVenue', 'trading_venue'],
        'Custodian_Name': ['CustodianName', 'custodian_name', 'Custodian', 'custodian'],
        'Exception Type': ['ExceptionType', 'exception_type', 'ExceptionType'],
        'Exception Description': ['ExceptionDescription', 'exception_description', 'ExceptionDesc'],
        'Exception Resolution': ['ExceptionResolution', 'exception_resolution'],
        'Reporting Regulation': ['ReportingRegulation', 'reporting_regulation'],
        'Exception Reason': ['ExceptionReason', 'exception_reason'],
        'Reporting Resolution': ['ReportingResolution', 'reporting_resolution'],
        'Trading Venue': ['TradingVenue', 'trading_venue', 'Venue', 'venue'],
        'Stock_Currency': ['StockCurrency', 'stock_currency', 'Currency', 'currency'],
        'Country_of_Trade': ['CountryOfTrade', 'country_of_trade', 'Country', 'country'],
        'Instrument_Status': ['InstrumentStatus', 'instrument_status', 'Status', 'status'],
        'Client_Approval_Status_Equity': ['ClientApprovalStatusEquity', 'client_approval_status_equity'],
        'Client Approval Status(forex)': ['ClientApprovalStatusForex', 'client_approval_status_forex', 'ClientApprovalStatus(forex)'],
        'Account Number_Forex': ['AccountNumberForex', 'account_number_forex', 'AccountNumber_Forex']
    };
    
    // Fetch all trades from unified_data collection
    const snapshot = await db.collection('unified_data').get();
    const trades = snapshot.docs.map(doc => ({ ...doc.data(), 'Document ID': doc.id }));
    
    // Debug: Log the first trade to see available fields
    if (trades.length > 0) {
        console.log('Sample trade fields:', Object.keys(trades[0]));
        console.log('Sample trade data:', trades[0]);
        
        // Specifically debug Counterparty ID field
        const sampleTrade = trades[0];
        console.log('=== COUNTERPARTY ID DEBUG ===');
        console.log('Looking for Counterparty ID in sample trade...');
        
        // Check all possible field name variations
        const counterpartyIdVariations = [
            'Counterparty ID', 'CounterpartyID', 'CounterpartyId', 'counterparty_id', 
            'counterpartyId', 'Counterparty_ID', 'CounterpartyId', 'counterpartyID',
            'COUNTERPARTY ID', 'COUNTERPARTYID', 'counterparty id', 'counterpartyid',
            'Counterparty ID '  // Add the exact field name with trailing space
        ];
        
        counterpartyIdVariations.forEach(fieldName => {
            if (sampleTrade[fieldName] !== undefined) {
                console.log(`✓ Found Counterparty ID with field name: "${fieldName}" = "${sampleTrade[fieldName]}"`);
            } else {
                console.log(`✗ Field name "${fieldName}" not found`);
            }
        });
        
        // Also check if there are any fields containing "counterparty" or "id"
        const allFields = Object.keys(sampleTrade);
        const relatedFields = allFields.filter(field => 
            field.toLowerCase().includes('counterparty') || 
            field.toLowerCase().includes('id')
        );
        console.log('Fields containing "counterparty" or "id":', relatedFields);
        
        // Show the exact field names that contain "counterparty"
        const counterpartyFields = allFields.filter(field => 
            field.toLowerCase().includes('counterparty')
        );
        console.log('Exact field names containing "counterparty":', counterpartyFields);
        
        // Show the exact field names that contain "id"
        const idFields = allFields.filter(field => 
            field.toLowerCase().includes('id')
        );
        console.log('Exact field names containing "id":', idFields);
        
        console.log('=== END COUNTERPARTY ID DEBUG ===');
    }
    
    // Store trades globally for sorting
    window.consolidatedTrades = trades;
    window.currentSortOrder = 'asc';
    
    // Render the table
    renderConsolidatedTable(trades, columns, fieldMappings);
    
    // Sync middle_office collection: remove any trades not in uploadDocs
    const middleOfficeSnapshot = await db.collection('middle_office').get();
    const currentMiddleOfficeIds = new Set(middleOfficeSnapshot.docs.map(doc => doc.id));
    const newIds = new Set(trades.map(trade => trade.TradeID));
    // Remove trades not present in uploadDocs
    const batch = db.batch();
    middleOfficeSnapshot.docs.forEach(doc => {
        if (!newIds.has(doc.id)) {
            batch.delete(doc.ref);
        }
    });
    // Add/update trades present in uploadDocs
    const collectionRef = db.collection('middle_office');
    trades.forEach(trade => {
        const docRef = collectionRef.doc(trade.TradeID);
        batch.set(docRef, trade);
    });
    await batch.commit();
    
    // Also load the multi-source data table
    await window.loadAndShowMultiSourceData();
};

// Function to render the consolidated table
function renderConsolidatedTable(trades, columns, fieldMappings) {
    const tbody = document.getElementById('consolidated-data-body');
    tbody.innerHTML = '';
    
    // Prepare data for upload
    const uploadDocs = [];
    
    trades.forEach(trade => {
        const tr = document.createElement('tr');
        const rowData = {};
        columns.forEach(col => {
            const td = document.createElement('td');
            
            // Try to get the value with field name mapping
            let value = '';
            if (trade[col] !== undefined) {
                value = trade[col];
                if (col === 'Counterparty ID') {
                    console.log(`Found Counterparty ID with exact match: "${value}"`);
                }
            } else if (fieldMappings[col]) {
                // Try alternative field names
                for (const altField of fieldMappings[col]) {
                    if (trade[altField] !== undefined) {
                        value = trade[altField];
                        if (col === 'Counterparty ID') {
                            console.log(`Found Counterparty ID using alternative field name: ${altField} = "${value}"`);
                        }
                        break;
                    }
                }
                if (col === 'Counterparty ID' && !value) {
                    console.log(`No Counterparty ID found for trade ${trade.TradeID}. Tried field names:`, fieldMappings[col]);
                }
            }
            
            td.textContent = value;
            rowData[col] = value;
            td.className = 'px-4 py-2';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
        if (trade.TradeID) {
            uploadDocs.push({ TradeID: trade.TradeID, ...rowData });
        }
    });
}

// Function to sort by Trade ID
window.sortByTradeId = function() {
    if (!window.consolidatedTrades) return;
    
    // Toggle sort order
    window.currentSortOrder = window.currentSortOrder === 'asc' ? 'desc' : 'asc';
    
    // Sort the trades
    const sortedTrades = [...window.consolidatedTrades].sort((a, b) => {
        const tradeIdA = (a.TradeID || '').toString();
        const tradeIdB = (b.TradeID || '').toString();
        
        if (window.currentSortOrder === 'asc') {
            return tradeIdA.localeCompare(tradeIdB);
        } else {
            return tradeIdB.localeCompare(tradeIdA);
        }
    });
    
    // Update the sort indicator in the header
    const tradeIdHeader = document.querySelector('#consolidated-data-table th:first-child');
    if (tradeIdHeader) {
        tradeIdHeader.innerHTML = `TradeID ${window.currentSortOrder === 'asc' ? '↑' : '↓'}`;
    }
    
    // Re-render the table with stored parameters
    const columns = [
        'TradeID', 'TradeDate', 'ValueDate', 'TradeTime', 'TraderID', 'Counterparty', 'Counterparty ID', 'LEI', 'CurrencyPair', 'BuySell', 'DealtCurrency', 'BaseCurrency', 'TermCurrency', 'NotionalAmount', 'FXRate', 'TradeStatus', 'SettlementStatus', 'SettlementMethod', 'Broker', 'ExecutionVenue', 'ProductType', 'MaturityDate', 'ConfirmationTimestamp', 'SettlementDate', 'BookingLocation', 'Portfolio', 'TradeVersion', 'CancellationFlag', 'AmendmentFlag', 'RiskSystemID', 'RegulatoryReportingStatus', 'TradeSourceSystem', 'ConfirmationMethod', 'ConfirmationStatus', 'SettlementInstructions', 'Custodian_Name', 'NettingEligibility', 'TradeComplianceStatus', 'KYCCheck', 'SanctionsScreening', 'ExceptionFlag', 'AuditTrailRef', 'CommissionAmount', 'CommissionCurrency', 'BrokerageFee', 'BrokerageCurrency', 'CustodyFee', 'CustodyCurrency', 'SettlementCost', 'SettlementCurrency', 'FXGainLoss', 'PnlCalculated', 'CostAllocationStatus', 'CostCenter', 'ExpenseApprovalStatus', 'CostBookedDate', 'Exception Type', 'Exception Description', 'Exception Resolution', 'Reporting Regulation', 'Exception Reason', 'Reporting Resolution', 'RID', 'ISIN', 'Symbol', 'Trading Venue', 'Stock_Currency', 'Country_of_Trade', 'Instrument_Status', 'ClientID_Equity', 'KYC_Status_Equity', 'Reference_Data_Validated', 'Margin_Type', 'Margin_Status', 'Client_Approval_Status_Equity', 'ClientID_Forex', 'KYC_Status_Forex', 'Expense_Approval_Status', 'Client Approval Status(forex)', 'Custodian_Ac_no', 'Beneficiary_Client_ID', 'Settlement_Cycle', 'EffectiveDate_Equity', 'ConfirmationStatus_Equity', 'SWIFT_Equity', 'BeneficiaryName_Equity', 'Account_Number_Equity', 'ABA_Equity', 'BSB_Equity', 'IBAN_Equity', 'SORT_Equity', 'Zengin_Equity', 'Settlement_Method_Equity', 'EffectiveDate_Forex', 'ConfirmationStatus_Forex', 'Account Number_Forex', 'SWIFT_Forex', 'BeneficiaryName_Forex', 'ABA_Forex', 'BSB_Forex', 'IBAN_Forex', 'SORT_Forex', 'Zengin_Forex', 'Settlement_Method_Forex', 'Document ID'
    ];
    
    const fieldMappings = {
        'Counterparty ID': ['assignedAccountId', 'CounterpartyID', 'CounterpartyId', 'counterparty_id', 'counterpartyId', 'Counterparty_ID', 'Counterparty ID', 'COUNTERPARTY ID', 'COUNTERPARTYID', 'counterparty id', 'counterpartyid', 'Counterparty ID '],
        'LEI': ['assignedAccountLei', 'lei', 'Lei', 'LegalEntityIdentifier', 'legal_entity_identifier'],
        'ExecutionVenue': ['ExecutionVenue', 'execution_venue', 'TradingVenue', 'trading_venue'],
        'Custodian_Name': ['CustodianName', 'custodian_name', 'Custodian', 'custodian'],
        'Exception Type': ['ExceptionType', 'exception_type', 'ExceptionType'],
        'Exception Description': ['ExceptionDescription', 'exception_description', 'ExceptionDesc'],
        'Exception Resolution': ['ExceptionResolution', 'exception_resolution'],
        'Reporting Regulation': ['ReportingRegulation', 'reporting_regulation'],
        'Exception Reason': ['ExceptionReason', 'exception_reason'],
        'Reporting Resolution': ['ReportingResolution', 'reporting_resolution'],
        'Trading Venue': ['TradingVenue', 'trading_venue', 'Venue', 'venue'],
        'Stock_Currency': ['StockCurrency', 'stock_currency', 'Currency', 'currency'],
        'Country_of_Trade': ['CountryOfTrade', 'country_of_trade', 'Country', 'country'],
        'Instrument_Status': ['InstrumentStatus', 'instrument_status', 'Status', 'status'],
        'Client_Approval_Status_Equity': ['ClientApprovalStatusEquity', 'client_approval_status_equity'],
        'Client Approval Status(forex)': ['ClientApprovalStatusForex', 'client_approval_status_forex', 'ClientApprovalStatus(forex)'],
        'Account Number_Forex': ['AccountNumberForex', 'account_number_forex', 'AccountNumber_Forex']
    };
    
    renderConsolidatedTable(sortedTrades, columns, fieldMappings);
};

// Add this function to fetch and show validation failure reason from Firestore
window.showValidationFailureReason = function(tradeId) {
    if (!tradeId) return;
    
    // Try to get validation data from both fx_validation and eq_validation collections
    Promise.all([
        db.collection('fx_validation').doc(tradeId).get(),
        db.collection('eq_validation').doc(tradeId).get()
    ]).then(([fxDoc, eqDoc]) => {
        let reason = 'No failure reason found.';
        let data = null;
        
        // Check forex validation first
        if (fxDoc.exists) {
            data = fxDoc.data();
        }
        // If no forex data, check equity validation
        else if (eqDoc.exists) {
            data = eqDoc.data();
        }
        
        if (data) {
            // Only show validation errors
            let errors = [];
            if (data.ValidationErrors) {
                errors = Array.isArray(data.ValidationErrors) ? data.ValidationErrors : [data.ValidationErrors];
            } else if (data.validation_errors) {
                errors = Array.isArray(data.validation_errors) ? data.validation_errors : [data.validation_errors];
            } else if (data.errors) {
                errors = Array.isArray(data.errors) ? data.errors : [data.errors];
            } else if (data.reason || data.Reason) {
                errors = [data.reason || data.Reason];
            }
            
            if (errors.length > 0) {
                // Format errors for equity validation popup
                const formattedErrors = errors.map(error => {
                    // Check if it's a mismatch error with the format we want
                    if (error.includes('mismatch:') && error.includes('trade=') && error.includes('termsheet=')) {
                        return `<li>${error}</li>`;
                    }
                    // For other types of errors, format them as-is
                    return `<li>${error}</li>`;
                });
                reason = `<ul>${formattedErrors.join('')}</ul>`;
            }
        }
        
        // Show popup/modal
        const modal = document.createElement('div');
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(0,0,0,0.5)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '2000';
        modal.onclick = function(e) { if (e.target === modal) modal.remove(); };
        const content = document.createElement('div');
        content.className = 'bg-white p-6 rounded shadow';
        content.style.position = 'relative';
        content.innerHTML = `<div class='mb-4 font-bold'>Validation Failure Reason</div><div class='mb-4'>${reason}</div>`;
        const closeBtn = document.createElement('button');
        closeBtn.textContent = 'Close';
        closeBtn.className = 'px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500';
        closeBtn.onclick = function() { modal.remove(); };
        content.appendChild(closeBtn);
        modal.appendChild(content);
        document.body.appendChild(modal);
    });
}

// --- Reconciliation CSV Upload Logic ---
const RECON_UPLOAD_ENDPOINTS = {
            SystemA: { url: 'http://localhost:8017/api/forex-systemA-capture/upload_systemA_csv' },
        SystemB: { url: 'http://localhost:8018/api/forex-systemB-capture/upload_systemB_csv' },
        FrontOffice: { url: 'http://localhost:8019/api/forex-FOentry-capture/upload_FOentry_csv' },
        BackOffice: { url: 'http://localhost:8020/api/forex-BOentry-capture/upload_BOentry_csv' },
};
window.openReconciliationUpload = function(type) {
    // Create a hidden file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,text/csv';
    input.style.display = 'none';
    document.body.appendChild(input);
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        const endpoint = RECON_UPLOAD_ENDPOINTS[type];
        if (!endpoint) {
            alert('Unknown upload type: ' + type);
            return;
        }
        const formData = new FormData();
        formData.append('file', file);
        fetch(endpoint.url, {
            method: 'POST',
            body: formData,
        })
        .then(async res => {
            if (!res.ok) {
                const err = await res.text();
                throw new Error(err);
            }
            return res.json();
        })
        .then(data => {
            alert('Upload successful! Rows stored: ' + (data.count || 0));
        })
        .catch(err => {
            alert('Upload failed: ' + err.message);
        })
        .finally(() => {
            document.body.removeChild(input);
        });
    };
    input.click();
};

function renderReconciliationTriggerButton() {
    // This function is now empty since we don't want buttons
    // Reconciliation happens automatically when page loads or instrument changes
}

window.loadAndShowNWMManagementData = async function() {
    const columns = [
        'Account_ID', 'Account_No', 'Account_Status', 'Approval_Status', 'Base_Currency', 'Booking_Location', 'Client_ID', 'Confirmation_Status', 'Counterparty', 'Currency_Pair', 'Custodian', 'Effective_Date', 'Execution_Venue', 'Expense_Approval_Status', 'IBAN', 'KYC_Status', 'LEI', 'Method', 'Netting_Eligibility', 'Portfolio', 'Product_Type', 'SWIFT', 'Sanctions_Screening', 'Settlement_Currency', 'source', 'uploadedAt', 'uploadedBy'
    ];
    const snapshot = await db.collection('NWM_Management').get();
    const records = snapshot.docs.map(doc => doc.data());
    const tbody = document.getElementById('nwm-management-body');
    tbody.innerHTML = '';
    records.forEach(record => {
        const tr = document.createElement('tr');
        columns.forEach(col => {
            const td = document.createElement('td');
            td.textContent = record[col] !== undefined ? record[col] : '';
            td.className = 'px-4 py-2';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
};

document.addEventListener('DOMContentLoaded', function() {
    const moBtn = document.getElementById('toggle-middle-office');
    const nwmBtn = document.getElementById('toggle-nwm');
    const moSection = document.getElementById('middle-office-section');
    const nwmSection = document.getElementById('nwm-section');
    if (moBtn && nwmBtn && moSection && nwmSection) {
        moBtn.onclick = function() {
            moSection.style.display = '';
            nwmSection.style.display = 'none';
            moBtn.className = 'px-4 py-2 bg-blue-600 text-black rounded hover:bg-blue-700 mr-2';
            nwmBtn.className = 'px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400';
        };
        nwmBtn.onclick = function() {
            moSection.style.display = 'none';
            nwmSection.style.display = '';
            nwmBtn.className = 'px-4 py-2 bg-blue-600 text-black rounded hover:bg-blue-700';
            moBtn.className = 'px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400 mr-2';
            window.loadAndShowNWMManagementData();
        };
    }
    var infoBtn = document.getElementById('toggle-consolidated-info');
    var consolidatedNav = document.getElementById('consolidated-data-nav');
    if (infoBtn && consolidatedNav) {
        infoBtn.onclick = function() {
            if (consolidatedNav.style.display === 'none') {
                consolidatedNav.style.display = '';
            } else {
                consolidatedNav.style.display = 'none';
            }
        };
    }
});

window.lifecycle = function() {
    window.showView('lifecycle-events');
};

// Function to load and display multi-source data
window.loadAndShowMultiSourceData = async function() {
    // Define the columns for the multi-source table
    const columns = [
        'TradeID', 'TradeDate', 'ValueDate', 'TradeTime', 'TraderID', 'Counterparty ID', 'BuySell', 'DealtCurrency', 'NotionalAmount', 'FXRate', 'TradeStatus', 'SettlementStatus', 'Broker', 'MaturityDate', 'ConfirmationTimestamp', 'SettlementDate', 'TradeVersion', 'CancellationFlag', 'AmendmentFlag', 'RiskSystemID', 'RegulatoryReportingStatus', 'TradeSourceSystem', 'ConfirmationMethod', 'TradeComplianceStatus', 'KYCCheck', 'ExceptionFlag', 'AuditTrailRef', 'CommissionAmount', 'CommissionCurrency', 'BrokerageFee', 'BrokerageCurrency', 'CustodyFee', 'CustodyCurrency', 'SettlementCost', 'FXGainLoss', 'PnlCalculated', 'CostAllocationStatus', 'CostCenter', 'CostBookedDate', 'Exception Type', 'Exception Description', 'Exception Resolution', 'Reporting Regulation', 'Exception Reason', 'Reporting Resolution', 'RID', 'ISIN', 'Symbol', 'Trading Venue', 'Stock_Currency', 'Country_of_Trade', 'Instrument_Status', 'ClientID_Equity', 'KYC_Status_Equity', 'Reference_Data_Validated', 'Margin_Type', 'Margin_Status', 'Client_Approval_Status_Equity', 'Client Approval Status(forex)', 'Custodian_Ac_no', 'Settlement_Cycle', 'EffectiveDate_Equity', 'ConfirmationStatus_Equity', 'SWIFT_Equity', 'BeneficiaryName_Equity', 'Account_Number_Equity', 'ABA_Equity', 'BSB_Equity', 'IBAN_Equity', 'SORT_Equity', 'Zengin_Equity', 'Settlement_Method_Equity', 'ConfirmationStatus_Forex', 'account', 'BeneficiaryName_Forex', 'ABA_Forex', 'Zengin_Forex', 'Settlement_Method_Forex', 'uniqueid', 'callAmount', 'exposure', 'bookingStatus', 'disputeAmount', 'priceMovement', 'bookingType', 'disputeReason', 'marginCallId', 'comments', 'reason', 'agreedAmount', 'client', 'notes', 'date', 'marginRequirement', 'accountName', 'domicile', 'mta.amount', 'mta.currency', 'currencies', 'assets', 'holidays', 'threshold', 'reportingCurrency', 'contact.phone', 'contact.email', 'notificationTime', 'principalEntity', 'direction', 'clientId', 'Validation status', 'Event Status'
    ];
    
    try {
        // Fetch data from all three collections
        const [fxCaptureSnapshot, fxValidationSnapshot, fxLifecycleSnapshot] = await Promise.all([
            db.collection('fx_capture').get(),
            db.collection('fx_validation').get(),
            db.collection('fx_lifecycle').get()
        ]);
        
        // Process fx_capture data (columns 1-109)
        const fxCaptureData = {};
        fxCaptureSnapshot.docs.forEach(doc => {
            const data = doc.data();
            if (data.TradeID) {
                fxCaptureData[data.TradeID] = data;
            }
        });
        
        // Process fx_validation data (column 110)
        const fxValidationData = {};
        fxValidationSnapshot.docs.forEach(doc => {
            const data = doc.data();
            if (data.TradeID) {
                fxValidationData[data.TradeID] = data;
            }
        });
        
        // Process fx_lifecycle data (column 111)
        const fxLifecycleData = {};
        fxLifecycleSnapshot.docs.forEach(doc => {
            const data = doc.data();
            if (data.TradeID) {
                fxLifecycleData[data.TradeID] = data;
            }
        });
        
        // Merge all data by TradeID
        const allTradeIds = new Set([
            ...Object.keys(fxCaptureData),
            ...Object.keys(fxValidationData),
            ...Object.keys(fxLifecycleData)
        ]);
        
        const mergedData = [];
        allTradeIds.forEach(tradeId => {
            // Only include rows that have data in fx_capture (primary source)
            if (fxCaptureData[tradeId]) {
                const mergedRow = {};
                
                // Add fx_capture data (columns 1-109)
                Object.assign(mergedRow, fxCaptureData[tradeId]);
                
                // Add fx_validation data (column 110)
                if (fxValidationData[tradeId]) {
                    mergedRow['Validation status'] = fxValidationData[tradeId].ValidationStatus || 
                                                    fxValidationData[tradeId]['Validation Status'] || 
                                                    fxValidationData[tradeId].status || '';
                }
                
                // Add fx_lifecycle data (column 111)
                if (fxLifecycleData[tradeId]) {
                    mergedRow['Event Status'] = fxLifecycleData[tradeId].EventStatus || 
                                               fxLifecycleData[tradeId]['Event Status'] || 
                                               fxLifecycleData[tradeId].status || '';
                }
                
                mergedData.push(mergedRow);
            }
        });
        
        // Get document IDs from consolidated data table for dropdown options
        const documentIds = [];
        if (window.consolidatedTrades) {
            window.consolidatedTrades.forEach(trade => {
                if (trade['Document ID']) {
                    documentIds.push(trade['Document ID']);
                }
            });
        }
        
        // Render the table
        renderMultiSourceTable(mergedData, columns, documentIds);
        
        console.log(`Loaded ${mergedData.length} records from multi-source collections`);
        
    } catch (error) {
        console.error('Error loading multi-source data:', error);
        // Show error in table
        const tbody = document.getElementById('multi-source-data-body');
        tbody.innerHTML = `<tr><td colspan="112" class="px-4 py-2 text-center text-red-500">Error loading data: ${error.message}</td></tr>`;
    }
};

// Function to render the multi-source table
function renderMultiSourceTable(data, columns, documentIds) {
    const tbody = document.getElementById('multi-source-data-body');
    tbody.innerHTML = '';
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="112" class="px-4 py-2 text-center text-gray-500">No data available</td></tr>';
        return;
    }
    
    data.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        tr.className = 'border-b hover:bg-gray-50';
        
        // Add dropdown cell as first column
        const dropdownTd = document.createElement('td');
        dropdownTd.className = 'px-4 py-2';
        dropdownTd.style.border = '1px solid #333';
        
        const dropdown = document.createElement('select');
        dropdown.className = 'w-full px-2 py-1 border border-gray-300 rounded text-sm';
        dropdown.setAttribute('data-row-index', rowIndex);
        
        // Add placeholder option
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = 'Select Document ID...';
        placeholderOption.selected = true;
        dropdown.appendChild(placeholderOption);
        
        // Add document ID options
        documentIds.forEach(docId => {
            const option = document.createElement('option');
            option.value = docId;
            option.textContent = docId;
            dropdown.appendChild(option);
        });
        
        dropdownTd.appendChild(dropdown);
        tr.appendChild(dropdownTd);
        
        // Add data columns
        columns.forEach(col => {
            const td = document.createElement('td');
            td.className = 'px-4 py-2';
            td.style.border = '1px solid #333';
            
            // Handle special field mappings for Counterparty ID
            let value = '';
            if (col === 'Counterparty ID') {
                // Try different field name variations
                const counterpartyIdVariations = [
                    'Counterparty ID', 'CounterpartyID', 'CounterpartyId', 'counterparty_id', 
                    'counterpartyId', 'Counterparty_ID', 'CounterpartyId', 'counterpartyID',
                    'COUNTERPARTY ID', 'COUNTERPARTYID', 'counterparty id', 'counterpartyid',
                    'Counterparty ID '
                ];
                
                for (const fieldName of counterpartyIdVariations) {
                    if (row[fieldName] !== undefined) {
                        value = row[fieldName];
                        break;
                    }
                }
            } else {
                value = row[col] !== undefined ? row[col] : '';
            }
            
            td.textContent = value;
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
}

// Function to save multi-source data to unified_data collection
window.saveMultiSourceData = async function() {
    const saveButton = document.getElementById('save-multi-source-btn');
    const originalText = saveButton.textContent;
    
    try {
        // Disable save button and show loading state
        saveButton.disabled = true;
        saveButton.textContent = 'Saving...';
        
        // Get all dropdowns
        const dropdowns = document.querySelectorAll('#multi-source-data-table select');
        const rowsToSave = [];
        
        // Collect rows with selected document IDs
        dropdowns.forEach((dropdown, index) => {
            const selectedDocId = dropdown.value;
            if (selectedDocId && selectedDocId.trim() !== '') {
                // Get the row data
                const row = dropdown.closest('tr');
                const cells = row.querySelectorAll('td');
                
                const rowData = {};
                // Skip the first cell (dropdown) and start from TradeID
                for (let i = 1; i < cells.length; i++) {
                    const cell = cells[i];
                    const columnIndex = i - 1; // Adjust for dropdown column
                    
                    // Get column name from header
                    const headerRow = document.querySelector('#multi-source-data-table thead tr');
                    const headers = headerRow.querySelectorAll('th');
                    const columnName = headers[i].textContent;
                    
                    const cellValue = cell.textContent.trim();
                    // Only add non-empty values
                    if (cellValue !== '') {
                        rowData[columnName] = cellValue;
                    }
                }
                
                rowsToSave.push({
                    documentId: selectedDocId,
                    data: rowData
                });
            }
        });
        
        if (rowsToSave.length === 0) {
            alert('No rows selected for saving. Please select document IDs for the rows you want to save.');
            return;
        }
        
        // Save data to Firebase
        let successCount = 0;
        let errorCount = 0;
        
        for (const row of rowsToSave) {
            try {
                // Get existing document
                const docRef = db.collection('unified_data').doc(row.documentId);
                const doc = await docRef.get();
                
                if (doc.exists) {
                    // Document exists, merge data without overwriting existing fields
                    const existingData = doc.data();
                    const mergedData = { ...existingData };
                    
                    // Add new fields only if they don't already exist
                    Object.keys(row.data).forEach(key => {
                        if (existingData[key] === undefined || existingData[key] === null || existingData[key] === '') {
                            mergedData[key] = row.data[key];
                        }
                    });
                    
                    await docRef.set(mergedData);
                    successCount++;
                } else {
                    // Document doesn't exist, skip it
                    console.log(`Document ${row.documentId} doesn't exist, skipping...`);
                    errorCount++;
                }
            } catch (error) {
                console.error(`Error saving row with document ID ${row.documentId}:`, error);
                errorCount++;
            }
        }
        
        // Show results
        let message = `Successfully saved ${successCount} rows to unified_data collection.`;
        if (errorCount > 0) {
            message += ` ${errorCount} rows were skipped (document not found or error occurred).`;
        }
        
        alert(message);
        
    } catch (error) {
        console.error('Error in saveMultiSourceData:', error);
        alert(`Error saving data: ${error.message}`);
    } finally {
        // Re-enable save button
        saveButton.disabled = false;
        saveButton.textContent = originalText;
    }
};