/**
 * DomainID - Main Application Logic
 * Automatically fetches from Google Sheets CSVs and renders the domains dynamically.
 */

// --- CONFIGURATION ---
// USER: Replace these URLs with the "Published to Web (CSV)" links from your Google Sheets!
const PREMIUM_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTu-hMWPh-WbM--mMk7tZjJmgSlRDO6k8VFMk_lmoiNWP2-_267ev0rBwXC5jPvDPenXmRQNeLB-8-H/pub?output=csv";
const ALL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSqCdsEOjGGzEH5vKY7f_TMdobdDNYNcM24d9GDjGyrxZfHR4lomIuJUc6GzZLQ27OeQst-WYpIC0h1/pub?output=csv";

// Store data in memory for fast searching
let premiumDomains = [];
let allDomains = [];

// Fallback/Mock Data if user hasn't provided their CSV URL yet or if fetch fails
const MOCK_PREMIUM = [
    { domain: "cryptoarab.com", price: "$15,000", link: "#", features: ["كلمة قوية ومطلوبة", "امتداد .com المميز", "تاريخ نظيف"] },
    { domain: "aibusiness.ai", price: "$8,500", link: "#", features: ["امتداد الذكاء الاصطناعي", "سهل التذكر", "مستقبل تقني"] },
    { domain: "riyadh.store", price: "$5,000", link: "#", features: ["استهداف جغرافي", "مناسب للتجارة الإلكترونية", "قصير"] }
];

const MOCK_ALL = [
    { domain: "techsaudi.net", price: "$499", link: "#", features: ["تقنية"] },
    { domain: "smartgulf.io", price: "$850", link: "#", features: ["تطبيقات، أعمال"] },
    { domain: "halalfood.com", price: "$3,200", link: "#", features: ["أغذية، تجارة"] },
    { domain: "dubai-cars.online", price: "$299", link: "#", features: ["سيارات، دبي"] },
];

/**
 * Parses simple CSV content. 
 */
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const result = [];
    
    // We expect columns: [domain, price, link, features...]
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const currentLine = lines[i].split(',');
        result.push({
            domain: currentLine[0] ? currentLine[0].trim() : '',
            price: currentLine[1] ? currentLine[1].trim() : 'Available',
            link: currentLine[2] ? currentLine[2].trim() : '#',
            features: currentLine[3] ? currentLine.slice(3).map(f => f.replace(/[\r\n"']/g, '').trim()).filter(f=>f) : []
        });
    }
    return result;
}

/**
 * Creates the HTML for a single Domain Card
 */
function createDomainCard(domainObj, isPremium) {
    const featuresHtml = (domainObj.features && domainObj.features.length) 
        ? domainObj.features.map(feat => `<li>${feat}</li>`).join('') 
        : `<li>Instant Ownership Transfer</li><li>100% Secure Checkout</li>`;
        
    const badge = isPremium ? `<div class="premium-badge">SUPER PREMIUM</div>` : '';
        
    return `
        <div class="domain-card glass-panel ${isPremium ? 'premium-card' : ''}">
            ${badge}
            <div class="card-domain-name">${domainObj.domain}</div>
            <div class="card-price">${domainObj.price}</div>
            <ul class="card-features">
                ${featuresHtml}
            </ul>
            <a href="${domainObj.link}" target="_blank" rel="noopener noreferrer" class="btn-buy">
                ${isPremium ? 'Make an Offer' : 'Buy Now'}
            </a>
        </div>
    `;
}

/**
 * Renders an array of domains to a specific grid element
 */
function renderDomains(domains, gridElementId, isPremium) {
    const grid = document.getElementById(gridElementId);
    if (!grid) return;
    
    if (domains.length === 0) {
        grid.innerHTML = `<p style="text-align:center; grid-column: 1/-1; color: var(--text-muted);">No domains found matching criteria.</p>`;
        return;
    }
    
    grid.innerHTML = domains.map(d => createDomainCard(d, isPremium)).join('');
}

/**
 * Fetches and initializes the domains from CSV
 */
async function loadDomains() {
    const premiumLoader = document.getElementById('premiumLoader');
    const allLoader = document.getElementById('allLoader');
    
    if(premiumLoader) premiumLoader.style.display = 'block';
    if(allLoader) allLoader.style.display = 'block';

    try {
        if (PREMIUM_CSV_URL.includes("MOCK_URL")) {
            premiumDomains = MOCK_PREMIUM;
        } else {
            const premRes = await fetch(PREMIUM_CSV_URL);
            if(premRes.ok) {
                const csvData = await premRes.text();
                premiumDomains = parseCSV(csvData);
            } else {
                premiumDomains = MOCK_PREMIUM;
            }
        }
    } catch(err) {
        console.error("Failed to load Premium Domains:", err);
        premiumDomains = MOCK_PREMIUM;
    }

    try {
        if (ALL_CSV_URL.includes("MOCK_URL")) {
            allDomains = MOCK_ALL;
        } else {
            const allRes = await fetch(ALL_CSV_URL);
            if(allRes.ok) {
                const csvData = await allRes.text();
                allDomains = parseCSV(csvData);
            } else {
                allDomains = MOCK_ALL;
            }
        }
    } catch(err) {
        console.error("Failed to load All Domains:", err);
        allDomains = MOCK_ALL;
    }
    
    if(premiumLoader) premiumLoader.style.display = 'none';
    if(allLoader) allLoader.style.display = 'none';

    renderDomains(premiumDomains, 'premiumGrid', true);
    renderDomains(allDomains, 'allGrid', false);
}

/**
 * Search Functionality
 */
function handleSearch() {
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    
    if (!query) {
        renderDomains(premiumDomains, 'premiumGrid', true);
        renderDomains(allDomains, 'allGrid', false);
        return;
    }
    
    const filteredPremium = premiumDomains.filter(d => 
        d.domain.toLowerCase().includes(query) || 
        d.features.some(f => f.toLowerCase().includes(query))
    );
    
    const filteredAll = allDomains.filter(d => 
        d.domain.toLowerCase().includes(query) || 
        d.features.some(f => f.toLowerCase().includes(query))
    );
    
    renderDomains(filteredPremium, 'premiumGrid', true);
    renderDomains(filteredAll, 'allGrid', false);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadDomains();
    
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }
});
