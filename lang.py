# -*- coding: utf-8 -*-
"""
Multi-language support for Card Linker Plugin
"""

# Language definitions
LANGUAGES = {
    "en": {
        # Editor button
        "link_button_tip": "Create Knowledge Link",
        "link_button_label": "🔗",
        
        # Dialog
        "dialog_title": "Create Knowledge Link",
        "link_text_label": "Link Display Text:",
        "link_text_placeholder": "e.g., Step 1 - Material Preparation",
        "search_existing_label": "Search Existing Cards:",
        "search_placeholder": "Enter keywords to search...",
        "create_new_label": "Or Create New Card:",
        "front_placeholder": "Front content...",
        "back_placeholder": "Back content...",
        "create_new_button": "Create New Card",
        "status_default": "Please select an existing card or create a new one",
        "create_link_button": "Create Link",
        "cancel_button": "Cancel",
        
        # Messages
        "select_card_first": "Please select a card first",
        "field_missing": "Please add the '{}' field to the current note type:\n\n1. Click 'Tools' > 'Manage Note Types'\n2. Select current note type, click 'Fields...'\n3. Click 'Add' button\n4. Enter field name: {}\n5. Click 'OK' to save",
        "enter_front_back": "Please enter front and back content",
        "enter_link_text": "Please enter link display text",
        "select_or_create": "Please select an existing card or create a new one",
        "link_created": "Link created successfully!",
        "create_failed": "Failed to create card: {}",
        "save_failed": "Failed to save: {}",
        "save_link_failed": "Failed to save link: {}",
        
        # Review interface
        "related_knowledge": "🧠 Related Knowledge Points",
        "review_status_tip": "💡 Green ✅ means reviewed today, Orange ⏳ means pending review",
        
        # Card status
        "card_not_found": "Card not found",
        "manual_preview": "Card opened in browser, please click preview button manually",
        "preview_failed": "Failed to open preview",
        "preview_error": "Preview display failed",
        "switch_error": "Error: Reviewer not initialized",
        "no_current_card": "Error: No card currently being reviewed",
        "target_card_not_found": "Error: Target card not found",
        "card_suspended": "Target card is suspended or buried, cannot review immediately",
        "switch_failed": "Card switch failed",
        
        # Deck info
        "deck_label": "Deck"
    },
    
    "zh": {
        # Editor button
        "link_button_tip": "创建知识点链接",
        "link_button_label": "🔗",
        
        # Dialog
        "dialog_title": "创建知识点链接",
        "link_text_label": "链接显示文本:",
        "link_text_placeholder": "如: 步骤1-材料准备",
        "search_existing_label": "搜索现有卡片:",
        "search_placeholder": "输入关键词搜索...",
        "create_new_label": "或创建新卡片:",
        "front_placeholder": "正面内容...",
        "back_placeholder": "背面内容...",
        "create_new_button": "创建新卡片",
        "status_default": "请选择现有卡片或创建新卡片",
        "create_link_button": "创建链接",
        "cancel_button": "取消",
        
        # Messages
        "select_card_first": "请先选择一张卡片",
        "field_missing": "请先为当前笔记类型添加 '{}' 字段：\n\n1. 点击 '工具' > '管理笔记类型'\n2. 选择当前笔记类型，点击 '字段...'\n3. 点击 '添加' 按钮\n4. 输入字段名: {}\n5. 点击 '确定' 保存",
        "enter_front_back": "请输入正面和背面内容",
        "enter_link_text": "请输入链接显示文本",
        "select_or_create": "请选择现有卡片或创建新卡片",
        "link_created": "链接创建成功！",
        "create_failed": "创建卡片失败: {}",
        "save_failed": "保存失败: {}",
        "save_link_failed": "保存链接失败: {}",
        
        # Review interface
        "related_knowledge": "🧠 相关知识点",
        "review_status_tip": "💡 绿色✅表示今日已复习，橙色⏳表示待复习",
        
        # Card status
        "card_not_found": "找不到指定的卡片",
        "manual_preview": "已在浏览器中打开卡片，请手动点击预览按钮",
        "preview_failed": "无法打开预览",
        "preview_error": "显示预览失败",
        "switch_error": "错误：复习器未初始化",
        "no_current_card": "错误：当前没有正在复习的卡片",
        "target_card_not_found": "错误：找不到目标卡片",
        "card_suspended": "目标卡片已暂停或埋藏，无法立即复习",
        "switch_failed": "卡片切换失败",
        
        # Deck info
        "deck_label": "牌组"
    }
}

def get_language():
    """Get current language setting"""
    try:
        from aqt import mw
        # Check user preference first
        config = mw.addonManager.getConfig(__name__)
        if config and config.get("language"):
            return config["language"]
        
        # Fall back to Anki's language setting
        lang = mw.pm.meta.get("defaultLang", "en")
        if lang.startswith("zh") or lang in ["zh-CN", "zh-TW"]:
            return "zh"
        else:
            return "en"
    except:
        return "en"  # Default to English

def get_text(key):
    """Get localized text"""
    lang = get_language()
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
