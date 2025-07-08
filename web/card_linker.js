// Card Linker Plugin JavaScript

// Function to display linked cards
function showLinkedCards(linkedCards) {
    if (!linkedCards || linkedCards.length === 0) {
        return '';
    }

    let html = '<div class="linked-cards-container">';
    html += '<div class="linked-cards-title">Related Cards:</div>';

    for (let card of linkedCards) {
        html += `<a href="#" class="linked-card-item" onclick="openLinkedCard(${card.card_id})">`;
        html += `${card.title} (${card.deck})`;
        html += '</a>';
    }

    html += '</div>';
    return html;
}

// Open linked card
function openLinkedCard(cardId) {
    // Open card through Python backend
    pycmd(`card_linker:open_card:${cardId}`);
}

// Add link information when card is displayed
function addLinkedCardsToCard() {
    // This function will be called when card is displayed
    // Get link information from card's LinkedCards field and display
    const linkedCardsField = document.querySelector('[data-field-name="LinkedCards"]');
    if (linkedCardsField && linkedCardsField.textContent) {
        try {
            const linkedCards = JSON.parse(linkedCardsField.textContent);
            const cardContent = document.querySelector('.card');
            if (cardContent && linkedCards.length > 0) {
                const linkedCardsHtml = showLinkedCards(linkedCards);
                cardContent.innerHTML += linkedCardsHtml;
            }
        } catch (e) {
            console.log('Error parsing linked cards:', e);
        }
    }
}

// Execute after page loading is complete
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addLinkedCardsToCard);
} else {
    addLinkedCardsToCard();
}
