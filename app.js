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
    { title: 'Meta.com', description: 'Ultra premium short domain for tech giants.', link: '#' },
    { title: 'Crypto.net', description: 'Perfect for the next big cryptocurrency project.', link: '#' },
    { title: 'AI.org', description: 'Prime domain for open-source AI initiatives.', link: '#' }
];

const MOCK_ALL = [
    { title: 'TechStartup.com', description: 'Catchy and highly brandable startup name.', link: '#' },
    { title: 'FoodDelivery.app', description: 'Great for food delivery aggregators.', link: '#' },
    { title: 'CloudStorage.io', description: 'Ideal for modern cloud infrastructure.', link: '#' },
    { title: 'FinancePro.com', description: 'The absolute best name for financial services.', link: '#' },
    { title: 'SmartHome.net', description: 'Perfect for smart home automation.', link: '#' }
];

const MOCK_SOLD = [
    { title: 'GulfVentures.com', description: 'Acquired for an undisclosed amount.', link: '#' },
    { title: 'DubaiTech.net', description: 'Sold to a Dubai-based holding group.', link: '#' },
    { title: 'ArabShop.com', description: 'Bought by an e-commerce giant.', link: '#' }
];

/**
 * Parses simple CSV content. 
 */
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const result = [];
    
    // We expect columns: [Title, Description, Link]
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const currentLine = lines[i].split(',');
        result.push({
            title: currentLine[0] ? currentLine[0].trim() : '',
            description: currentLine[1] ? currentLine[1].trim() : 'A premium digital asset.',
            link: currentLine[2] ? currentLine[2].trim() : '#'
        });
    }
    return result;
}

/**
 * Creates the HTML for a single Domain Card
 */
function createDomainCard(domain, isPremium = false) {
    const card = document.createElement('article');
    card.className = 'domain-card glass-panel';
    
    // Support either traditional "domain" field or the new "title" field
    const domainTitle = domain.title || domain.domain || 'Unknown.com';
    const domainDescription = domain.description || domain.price || 'A premium digital asset.';
    
    card.innerHTML = `
        <div class="domain-header" style="flex-direction: column; align-items: flex-start; gap: 10px;">
            <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                <h3 class="domain-name" style="font-size: 1.6rem; word-break: break-all;">${domainTitle}</h3>
                ${isPremium ? '<span class="premium-badge">Premium</span>' : ''}
            </div>
        </div>
        <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 20px; font-weight: normal; line-height: 1.6; flex-grow: 1;">
            ${domainDescription}
        </p>
        <ul class="domain-features" style="margin-top: auto;">
            <li><span class="gradient-text">✓</span> Instant Secure Transfer</li>
            <li><span class="gradient-text">✓</span> 100% Buyer Protection</li>
        </ul>
        <a href="${domain.link || '#'}" target="_blank" class="btn-glow" style="width: 100%;">
            ${isPremium ? 'Buy Now' : 'Make an Offer'}
        </a>
    `;
    
    return card;
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
    
    grid.innerHTML = ''; // Clear existing content
    domains.forEach(d => grid.appendChild(createDomainCard(d, isPremium)));
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
        (d.title || d.domain || '').toLowerCase().includes(query) || 
        (d.description || d.price || '').toLowerCase().includes(query)
    );
    
    const filteredAll = allDomains.filter(d => 
        (d.title || d.domain || '').toLowerCase().includes(query) || 
        (d.description || d.price || '').toLowerCase().includes(query)
    );
    
    renderDomains(filteredPremium, 'premiumGrid', true);
    renderDomains(filteredAll, 'allGrid', false);
    
    // Render Recently Sold
    const filteredSold = MOCK_SOLD.filter(d => 
        (d.title || d.domain || '').toLowerCase().includes(query) || 
        (d.description || d.price || '').toLowerCase().includes(query)
    );
    renderDomains(filteredSold, 'soldGrid', false);
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
