// Card Linker Plugin JavaScript

// 显示链接卡片的函数
function showLinkedCards(linkedCards) {
    if (!linkedCards || linkedCards.length === 0) {
        return '';
    }
    
    let html = '<div class="linked-cards-container">';
    html += '<div class="linked-cards-title">相关卡片:</div>';
    
    for (let card of linkedCards) {
        html += `<a href="#" class="linked-card-item" onclick="openLinkedCard(${card.card_id})">`;
        html += `${card.title} (${card.deck})`;
        html += '</a>';
    }
    
    html += '</div>';
    return html;
}

// 打开链接的卡片
function openLinkedCard(cardId) {
    // 通过 Python 后端打开卡片
    pycmd(`card_linker:open_card:${cardId}`);
}

// 在卡片显示时添加链接信息
function addLinkedCardsToCard() {
    // 这个函数会在卡片显示时被调用
    // 从卡片的 LinkedCards 字段获取链接信息并显示
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

// 页面加载完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addLinkedCardsToCard);
} else {
    addLinkedCardsToCard();
}
