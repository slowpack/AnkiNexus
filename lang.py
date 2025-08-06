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
        "link_text_placeholder": "Leave empty to use card title as default",
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
        "deck_switch_notice": "📋 Note: Due to Anki's review mechanism, linked cards not in the current review deck cannot be directly reviewed. They will open in preview mode instead.",
        
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
        "deck_label": "Deck",

        # Default note type
        "default_note_type_name": "AnkiNexus - Knowledge Linker",
        "front_field_name": "Front",
        "back_field_name": "Back",
        "card_template_name": "Card 1",
        "front_template": "{{Front}}",
        "back_template": "{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}",
        "create_note_type_failed": "Failed to create default note type: {}",

        # Template suggestions
        "switch_template_suggestion": "Found existing '{}' note type with '{}' field!\n\nWould you like to switch to this note type for creating linked cards?",
        "create_template_suggestion": "To use the Card Linker feature, you need a note type with '{}' field.\n\nWould you like me to create an 'AnkiNexus - Knowledge Linker' note type for you?\n\nThis will include:\n• Front and Back fields\n• LinkedCards field for storing links\n• Optimized templates for compound cards",
        "template_switched": "Successfully switched to AnkiNexus note type! You can now create linked cards.",
        "template_created_switched": "Successfully created and switched to AnkiNexus note type! You can now create linked cards.",
        "template_created_manual_switch": "Successfully created '{}' note type!\n\nPlease manually switch to this note type:\n\n1. Click the note type dropdown in the editor\n2. Select '{}'\n3. Then try creating links again",
        "switch_failed_error": "Failed to switch note type: {}",
        "manual_switch_instructions": "Please manually switch to '{}' note type:\n\n1. Click the note type dropdown in the editor\n2. Select '{}'\n3. Then try creating links again",

        # Suspended card handling
        "unsuspend_card_question": "The target card is suspended. Would you like to unsuspend it and continue?",
        "unbury_card_question": "The target card is buried. Would you like to unbury it and continue?",
        "restore_card_question": "The target card is not available for review. Would you like to restore it and continue?",
        "card_unsuspended": "Card has been unsuspended successfully!",
        "card_unburied": "Card has been unburied successfully!",
        "card_restored": "Card has been restored successfully!",
        "unsuspend_failed": "Failed to restore card: {}",

        # UI text
        "search_cards_group": "🔍 Search Cards",
        "selected_cards_group": "📋 Selected Cards",
        "create_new_card_group": "➕ Create New Card",
        "add_selected_card": "➕ Add Selected Card",
        "remove_selected": "🗑️ Remove Selected",
        "clear_all": "🧹 Clear All",
        "create_new_card_info": "Click button to quickly create new card, it will be automatically added as link after creation",
        "create_new_card_btn": "🆕 Create New Card",
        "close_dialog": "✅ Close",
        "status_select_cards": "Double-click or click add button to select cards, links will be created immediately after selection",
        "status_links_created": "{} links created",
        "status_link_added": "✅ Link added: {}...",
        "status_link_removed": "✅ Link removed: {}",
        "status_all_links_cleared": "✅ All links cleared",

        # Error messages
        "error_card_not_found": "Error: Card ID {} not found",
        "error_save_link_failed": "Failed to save link information",
        "error_card_already_linked": "This card is already linked",
        "error_card_already_added": "This card has already been added",
        "error_select_card_first": "Please select a card first",
        "error_link_creation_failed": "Link creation failed, please check if card exists",
        "error_select_card_to_remove": "Please select a card to remove first",
        "error_remove_link_failed": "Failed to remove link",
        "error_clear_links_failed": "Failed to clear links",
        "error_add_link_failed": "Failed to add link: {}",
        "error_create_card_failed": "Failed to create card: {}",
        "error_fill_front_back": "Please fill in front and back content",
        "error_card_creation_failed": "Card creation failed: No card generated",
        "error_new_card_link_failed": "New card created successfully, but link creation failed",

        # Confirmation messages
        "confirm_clear_all_links": "Are you sure you want to delete all created links?",

        # Success messages
        "success_card_created": "Card created successfully: {}...",
        "success_new_card_linked": "✅ New card created and linked: {}...",

        # Simple add card dialog
        "simple_add_card_title": "Create New Card",
        "simple_add_card_front": "Front Content:",
        "simple_add_card_back": "Back Content:",
        "simple_add_card_front_placeholder": "Enter front content...",
        "simple_add_card_back_placeholder": "Enter back content...",
        "simple_add_card_create": "Create Card",

        # Card status in review
        "card_status_deleted": "Deleted",
        "card_status_load_error": "Load Error",
        "card_status_unknown": "Unknown Card"
    },
    
    "zh": {
        # Editor button
        "link_button_tip": "创建知识点链接",
        "link_button_label": "🔗",
        
        # Dialog
        "dialog_title": "创建知识点链接",
        "link_text_label": "链接显示文本:",
        "link_text_placeholder": "留空将使用卡片标题作为默认名称",
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
        "deck_switch_notice": "📋 提示：由于Anki复习机制，链接卡片不属于当前复习牌组时无法直接跳转复习，已更换为预览模式。",
        
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
        "deck_label": "牌组",

        # Default note type
        "default_note_type_name": "AnkiNexus - 知识链接器",
        "front_field_name": "正面",
        "back_field_name": "背面",
        "card_template_name": "卡片 1",
        "front_template": "{{正面}}",
        "back_template": "{{FrontSide}}\n\n<hr id=answer>\n\n{{背面}}",
        "create_note_type_failed": "创建默认笔记类型失败: {}",

        # Template suggestions
        "switch_template_suggestion": "发现已存在的 '{}' 笔记类型，包含 '{}' 字段！\n\n是否切换到此笔记类型来创建链接卡片？",
        "create_template_suggestion": "要使用卡片链接功能，需要包含 '{}' 字段的笔记类型。\n\n是否让我为您创建一个 'AnkiNexus - 知识链接器' 笔记类型？\n\n它将包含：\n• 正面和背面字段\n• LinkedCards 字段用于存储链接\n• 为复合卡片优化的模板",
        "template_switched": "成功切换到 AnkiNexus 笔记类型！现在可以创建链接卡片了。",
        "template_created_switched": "成功创建并切换到 AnkiNexus 笔记类型！现在可以创建链接卡片了。",
        "template_created_manual_switch": "成功创建 '{}' 笔记类型！\n\n请手动切换到此笔记类型：\n\n1. 点击编辑器中的笔记类型下拉菜单\n2. 选择 '{}'\n3. 然后重新尝试创建链接",
        "switch_failed_error": "切换笔记类型失败: {}",
        "manual_switch_instructions": "请手动切换到 '{}' 笔记类型：\n\n1. 点击编辑器中的笔记类型下拉菜单\n2. 选择 '{}'\n3. 然后重新尝试创建链接",

        # Suspended card handling
        "unsuspend_card_question": "目标卡片已被暂停。是否要取消暂停并继续？",
        "unbury_card_question": "目标卡片已被搁置。是否要取消搁置并继续？",
        "restore_card_question": "目标卡片无法复习。是否要恢复该卡片并继续？",
        "card_unsuspended": "卡片已成功取消暂停！",
        "card_unburied": "卡片已成功取消搁置！",
        "card_restored": "卡片已成功恢复！",
        "unsuspend_failed": "恢复卡片失败: {}",

        # UI text
        "search_cards_group": "🔍 搜索卡片",
        "selected_cards_group": "📋 已选择的卡片",
        "create_new_card_group": "➕ 创建新卡片",
        "add_selected_card": "➕ 添加选中卡片",
        "remove_selected": "🗑️ 移除选中",
        "clear_all": "🧹 清空全部",
        "create_new_card_info": "点击按钮快速创建新卡片，创建成功后会自动添加为链接",
        "create_new_card_btn": "🆕 创建新卡片",
        "close_dialog": "✅ 关闭",
        "status_select_cards": "双击或点击添加按钮来选择卡片，选择后会立即创建链接",
        "status_links_created": "已创建 {} 个链接",
        "status_link_added": "✅ 已添加链接: {}...",
        "status_link_removed": "✅ 已移除链接: {}",
        "status_all_links_cleared": "✅ 已清空所有链接",

        # Error messages
        "error_card_not_found": "错误：找不到卡片 ID {}",
        "error_save_link_failed": "保存链接信息失败",
        "error_card_already_linked": "该卡片已经链接过了",
        "error_card_already_added": "该卡片已经添加过了",
        "error_select_card_first": "请先选择一张卡片",
        "error_link_creation_failed": "链接创建失败，请检查卡片是否存在",
        "error_select_card_to_remove": "请先选择要移除的卡片",
        "error_remove_link_failed": "移除链接失败",
        "error_clear_links_failed": "清空链接失败",
        "error_add_link_failed": "添加链接失败: {}",
        "error_create_card_failed": "创建卡片失败: {}",
        "error_fill_front_back": "请填写正面和背面内容",
        "error_card_creation_failed": "卡片创建失败：未生成卡片",
        "error_new_card_link_failed": "新卡片创建成功，但链接创建失败",

        # Confirmation messages
        "confirm_clear_all_links": "确定要删除所有已创建的链接吗？",

        # Success messages
        "success_card_created": "卡片创建成功: {}...",
        "success_new_card_linked": "✅ 新卡片已创建并添加链接: {}...",

        # Simple add card dialog
        "simple_add_card_title": "创建新卡片",
        "simple_add_card_front": "正面内容:",
        "simple_add_card_back": "背面内容:",
        "simple_add_card_front_placeholder": "输入卡片正面内容...",
        "simple_add_card_back_placeholder": "输入卡片背面内容...",
        "simple_add_card_create": "创建卡片",

        # Comments and debug messages
        "debug_save_link_data": "保存链接数据: {}",
        "debug_save_success": "成功保存到字段 {}",
        "debug_save_failed": "保存失败: {}",
        "comment_load_existing_links": "加载已有的链接到显示列表",
        "comment_card_not_exist": "卡片不存在，跳过",
        "comment_load_failed": "如果加载失败，继续正常流程",
        "comment_check_already_selected": "检查是否已经选择过这张卡片",
        "comment_set_selected_background": "如果已选择，设置不同的背景色",
        "comment_handle_double_click": "处理双击事件",
        "comment_check_already_linked": "检查是否已经链接过",
        "comment_refresh_editor": "刷新编辑器",
        "comment_update_status": "更新状态",
        "comment_refresh_search_results": "刷新搜索结果显示",
        "comment_set_deck": "设置牌组（使用当前卡片的牌组或默认牌组）",
        "comment_use_default_deck": "使用默认牌组",
        "comment_set_focus": "设置焦点",
        "comment_card_deleted": "卡片不存在，可能已被删除",
        "comment_card_load_error": "记录错误但继续处理其他链接",
        "comment_check_reviewed_today": "检查今日是否已复习",
        "comment_safe_handle_chars": "安全处理特殊字符",
        "comment_auto_browser_preview": "使用浏览器自动预览",
        "comment_check_card_found": "检查是否找到了卡片并自动触发预览",
        "comment_delay_execution": "延迟1秒执行，确保搜索完成",

        # Card status in review
        "card_status_deleted": "已删除",
        "card_status_load_error": "加载错误",
        "card_status_unknown": "未知卡片"
    }
}

def get_language():
    """Get current language setting"""
    try:
        from aqt import mw

        # Check user preference first
        try:
            config = mw.addonManager.getConfig(__name__)
            if config and config.get("language") and config.get("language") != "auto":
                return config["language"]
        except:
            pass

        # Fall back to Anki's language setting
        try:
            # Try multiple ways to get language setting
            lang = None

            # Method 1: Check profile meta
            if hasattr(mw, 'pm') and mw.pm and hasattr(mw.pm, 'meta'):
                lang = mw.pm.meta.get("defaultLang", None)

            # Method 2: Check collection language
            if not lang and hasattr(mw, 'col') and mw.col:
                try:
                    lang = mw.col.get_config("defaultLang", None)
                except:
                    pass

            # Method 3: Check system locale
            if not lang:
                import locale
                try:
                    lang = locale.getdefaultlocale()[0]
                except:
                    pass

            # Check if it's Chinese
            if lang:
                lang_lower = lang.lower()
                if any(x in lang_lower for x in ["zh", "chinese", "china", "taiwan", "hong"]):
                    return "zh"

            return "en"
        except:
            return "en"
    except:
        return "en"  # Default to English

def get_text(key):
    """Get localized text"""
    lang = get_language()
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
