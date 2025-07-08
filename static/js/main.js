// Global variables
let allBills = [];
let filteredBills = [];
let selectedTags = new Set();
let sortField = 'state';
let sortDirection = 'asc';

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadStates();
    loadBills();
    populateDefinitions();
    
    // Add event listeners
    document.getElementById('searchInput').addEventListener('input', debounce(loadBills, 300));
    document.getElementById('stateFilter').addEventListener('change', loadBills);
    document.getElementById('taxonomyFilter').addEventListener('change', loadBills);
    document.getElementById('hideNR').addEventListener('change', loadBills);
});

// Initialize tag filters
function initializeFilters() {
    const tagFiltersDiv = document.getElementById('tagFilters');
    
    Object.entries(tagDefinitions).forEach(([key, info]) => {
        const button = document.createElement('button');
        button.className = 'tag-button px-3 py-1 rounded-full text-xs font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300';
        button.textContent = info.name;
        button.dataset.tag = key;
        button.onclick = () => toggleTag(key, button);
        tagFiltersDiv.appendChild(button);
    });
}

// Toggle tag selection
function toggleTag(tag, button) {
    if (selectedTags.has(tag)) {
        selectedTags.delete(tag);
        button.className = 'tag-button px-3 py-1 rounded-full text-xs font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300';
    } else {
        selectedTags.add(tag);
        button.className = 'tag-button px-3 py-1 rounded-full text-xs font-medium transition-colors bg-blue-600 text-white';
    }
    loadBills();
}

// Load states for dropdown
async function loadStates() {
    try {
        const response = await fetch('/api/states');
        if (!response.ok) throw new Error('Failed to load states');
        
        const states = await response.json();
        
        const stateFilter = document.getElementById('stateFilter');
        states.forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading states:', error);
        showError('Failed to load states');
    }
}

// Load bills from API
async function loadBills() {
    showLoading(true);
    
    const params = new URLSearchParams();
    
    // Add filters
    const search = document.getElementById('searchInput').value;
    const state = document.getElementById('stateFilter').value;
    const taxonomyCode = document.getElementById('taxonomyFilter').value;
    const hideNR = document.getElementById('hideNR').checked;
    
    if (search) params.append('search', search);
    if (state !== 'all') params.append('state', state);
    if (taxonomyCode !== 'all') params.append('taxonomy_code', taxonomyCode);
    params.append('hide_nr', hideNR);
    
    // Add selected tags
    selectedTags.forEach(tag => params.append('tags[]', tag));
    
    try {
        const response = await fetch(`/api/bills?${params}`);
        if (!response.ok) throw new Error('Failed to load bills');
        
        allBills = await response.json();
        displayBills();
        updateSummary();
    } catch (error) {
        console.error('Error loading bills:', error);
        showError('Failed to load bills. Please check your connection.');
    } finally {
        showLoading(false);
    }
}

// Display bills in table
function displayBills() {
    const tbody = document.getElementById('billsTableBody');
    tbody.innerHTML = '';
    
    // Sort bills
    const sortedBills = [...allBills].sort((a, b) => {
        let aVal = a[sortField];
        let bVal = b[sortField];
        
        // Handle numeric sorting for tag_count
        if (sortField === 'tag_count') {
            aVal = parseInt(aVal) || 0;
            bVal = parseInt(bVal) || 0;
        }
        
        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });
    
    if (sortedBills.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                    No bills found matching your criteria
                </td>
            </tr>
        `;
        return;
    }
    
    sortedBills.forEach(bill => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        
        // Get taxonomy color
        const taxonomyColor = getTaxonomyColor(bill.taxonomy_code);
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${escapeHtml(bill.state)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${escapeHtml(bill.bill)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${escapeHtml(bill.status || 'N/A')}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 rounded-full text-xs font-medium ${taxonomyColor}">
                    ${escapeHtml(bill.taxonomy_code)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                <div class="flex flex-wrap gap-1 max-w-xs">
                    ${bill.active_tags.map(tag => 
                        `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">${escapeHtml(tag)}</span>`
                    ).join('')}
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm no-print">
                <a href="${escapeHtml(bill.link)}" target="_blank" rel="noopener noreferrer" 
                   class="text-blue-600 hover:text-blue-800">
                    <i class="fas fa-external-link-alt"></i>
                </a>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Get taxonomy color class
function getTaxonomyColor(code) {
    switch(code) {
        case 'E': return 'bg-red-100 text-red-800';
        case 'SR': return 'bg-orange-100 text-orange-800';
        case 'II': return 'bg-yellow-100 text-yellow-800';
        case 'CB': return 'bg-purple-100 text-purple-800';
        case 'NR': return 'bg-gray-100 text-gray-800';
        default: return 'bg-gray-100 text-gray-800';
    }
}

// Update results summary
function updateSummary() {
    const summary = document.getElementById('resultsSummary');
    const tagText = selectedTags.size > 0 
        ? ` with tags: ${Array.from(selectedTags).map(t => tagDefinitions[t].name).join(', ')}`
        : '';
    summary.innerHTML = `Showing <span class="font-semibold">${allBills.length}</span> bills${tagText}`;
}

// Sort table
function sortTable(field) {
    if (sortField === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortField = field;
        sortDirection = 'asc';
    }
    displayBills();
}

// Show/hide loading indicator
function showLoading(show) {
    document.getElementById('loadingIndicator').classList.toggle('hidden', !show);
}

// Show error toast
function showError(message) {
    const toast = document.getElementById('errorToast');
    const messageEl = document.getElementById('errorMessage');
    
    messageEl.textContent = message;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 5000);
}

// Show modals
function showTagInfo() {
    document.getElementById('tagModal').classList.remove('hidden');
}

function showTaxonomyInfo() {
    document.getElementById('taxonomyModal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Close modals on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal('tagModal');
        closeModal('taxonomyModal');
    }
});

// Close modals on backdrop click
document.getElementById('tagModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal('tagModal');
    }
});

document.getElementById('taxonomyModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal('taxonomyModal');
    }
});

// Populate definitions in modals
function populateDefinitions() {
    // Tag definitions
    const tagList = document.getElementById('tagDefinitionsList');
    Object.entries(tagDefinitions).forEach(([key, info]) => {
        const div = document.createElement('div');
        div.className = 'border-b pb-4 last:border-b-0';
        div.innerHTML = `
            <h4 class="font-semibold text-gray-900 mb-2">${escapeHtml(info.name)}</h4>
            <p class="text-gray-600 text-sm">${escapeHtml(info.definition)}</p>
        `;
        tagList.appendChild(div);
    });
    
    // Taxonomy definitions
    const taxonomyList = document.getElementById('taxonomyDefinitionsList');
    Object.entries(taxonomyDefinitions).forEach(([code, info]) => {
        const div = document.createElement('div');
        div.className = 'border-b pb-6 last:border-b-0';
        const color = getTaxonomyColor(code);
        div.innerHTML = `
            <h4 class="font-semibold text-gray-900 text-lg mb-2">
                <span class="inline-block px-3 py-1 rounded-full text-sm mr-2 ${color}">
                    ${escapeHtml(code)}
                </span>
                ${escapeHtml(info.name)}
            </h4>
            <p class="text-gray-600 mb-2">${escapeHtml(info.definition)}</p>
            <p class="text-sm text-gray-500">
                <strong>Inclusion Criteria:</strong> ${escapeHtml(info.inclusion)}
            </p>
        `;
        taxonomyList.appendChild(div);
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Cmd/Ctrl + K for search focus
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
});