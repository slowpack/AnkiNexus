# -*- coding: utf-8 -*-
"""
Card Linker Plugin for Anki
Allows linking related cards together to solve card fragmentation
"""

from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo, getText
from anki.notes import Note
import json
from .lang import get_text

# PyQt6 兼容性修复
try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QDialog
    USER_ROLE = Qt.ItemDataRole.UserRole
    DIALOG_ACCEPTED = QDialog.DialogCode.Accepted
except:
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QDialog
        USER_ROLE = Qt.UserRole
        DIALOG_ACCEPTED = QDialog.Accepted
    except:
        USER_ROLE = 256
        DIALOG_ACCEPTED = 1

class CardLinker:
    def __init__(self):
        self.linked_cards_field = "LinkedCards"
        
    def setup_editor_button(self, buttons, editor):
        """Add link button to editor"""
        def on_click(editor_instance):
            self.on_link_button_clicked(editor_instance)

        button = editor.addButton(
            icon=None,
            cmd="card_linker",
            func=on_click,
            tip=get_text("link_button_tip"),
            label=get_text("link_button_label")
        )
        buttons.append(button)
        return buttons
    
    def on_link_button_clicked(self, editor):
        """Handle link button click"""
        if not editor.note:
            showInfo(get_text("select_card_first"))
            return

        if not self.check_field_exists(editor.note):
            return

        self.show_link_dialog(editor)
    
    def check_field_exists(self, note):
        """Check if LinkedCards field exists"""
        try:
            _ = note[self.linked_cards_field]
            return True
        except KeyError:
            showInfo(get_text("field_missing").format(self.linked_cards_field, self.linked_cards_field))
            return False
    
    def show_link_dialog(self, editor):
        """显示链接对话框"""
        dialog = LinkDialog(editor, self)
        dialog.exec()
    
    def search_cards(self, query):
        """搜索卡片"""
        try:
            card_ids = mw.col.findCards(query)
            cards = []
            for card_id in card_ids[:30]:
                card = mw.col.getCard(card_id)
                note = card.note()
                cards.append({
                    'id': card_id,
                    'note_id': note.id,
                    'question': note.fields[0][:80],
                    'deck': mw.col.decks.name(card.did)
                })
            return cards
        except:
            return []
    
    def create_new_card(self, current_note, front, back):
        """Create new card"""
        try:
            model = current_note.model()
            new_note = Note(mw.col, model)
            new_note.fields[0] = front
            if len(new_note.fields) > 1:
                new_note.fields[1] = back

            current_card = mw.reviewer.card if mw.reviewer.card else None
            deck_id = current_card.did if current_card else mw.col.conf['curDeck']
            new_note.model()['did'] = deck_id

            mw.col.addNote(new_note)
            mw.col.save()

            new_cards = new_note.cards()
            return new_cards[0].id if new_cards else None
        except Exception as e:
            showInfo(get_text("create_failed").format(str(e)))
            return None
    
    def insert_link(self, editor, link_text, card_id):
        """在编辑器中插入链接"""
        escaped_text = link_text.replace("'", "\\'").replace('"', '\\"')
        link_html = f'<span style="background-color: #e3f2fd; border: 1px solid #2196f3; border-radius: 4px; padding: 3px 8px; margin: 0 3px; color: #1976d2; font-weight: 500;" data-card-id="{card_id}">🔗 {escaped_text}</span>'
        escaped_html = link_html.replace("'", "\\'")
        
        try:
            editor.web.eval(f"document.execCommand('insertHTML', false, '{escaped_html}');")
        except:
            link_mark = f" [🔗{link_text}] "
            editor.web.eval(f"document.execCommand('insertText', false, '{link_mark}');")
    
    def add_link_to_note(self, note, card_id, link_text):
        """Add link to note"""
        try:
            linked_cards = self.get_linked_cards(note)

            if not any(link['card_id'] == card_id for link in linked_cards):
                card = mw.col.getCard(card_id)
                linked_note = card.note()

                link_info = {
                    'card_id': card_id,
                    'note_id': linked_note.id,
                    'title': link_text,
                    'deck': mw.col.decks.name(card.did)
                }

                linked_cards.append(link_info)
                self.save_linked_cards(note, linked_cards)
        except Exception as e:
            showInfo(get_text("save_link_failed").format(str(e)))
    
    def get_linked_cards(self, note):
        """获取链接卡片"""
        try:
            field_content = note[self.linked_cards_field] or "[]"
            return json.loads(field_content)
        except:
            return []
    
    def save_linked_cards(self, note, linked_cards):
        """Save linked cards"""
        try:
            note[self.linked_cards_field] = json.dumps(linked_cards, ensure_ascii=False)
            if note.id != 0:
                mw.col.updateNote(note)
                mw.col.save()
                return True
            return False
        except Exception as e:
            showInfo(get_text("save_failed").format(str(e)))
            return False

class LinkDialog(QDialog):
    def __init__(self, editor, card_linker):
        super().__init__()
        self.editor = editor
        self.card_linker = card_linker
        self.current_note = editor.note
        self.selected_card_id = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.setWindowTitle(get_text("dialog_title"))
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Link text
        layout.addWidget(QLabel(get_text("link_text_label")))
        self.link_text_input = QLineEdit()
        self.link_text_input.setPlaceholderText(get_text("link_text_placeholder"))
        layout.addWidget(self.link_text_input)

        # Search existing cards
        layout.addWidget(QLabel(get_text("search_existing_label")))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(get_text("search_placeholder"))
        self.search_input.textChanged.connect(self.search_cards)
        layout.addWidget(self.search_input)

        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(120)
        self.search_results.itemClicked.connect(self.select_existing_card)
        layout.addWidget(self.search_results)

        # Or create new card
        layout.addWidget(QLabel(get_text("create_new_label")))
        self.front_input = QLineEdit()
        self.front_input.setPlaceholderText(get_text("front_placeholder"))
        layout.addWidget(self.front_input)

        self.back_input = QLineEdit()
        self.back_input.setPlaceholderText(get_text("back_placeholder"))
        layout.addWidget(self.back_input)

        create_btn = QPushButton(get_text("create_new_button"))
        create_btn.clicked.connect(self.create_new_card)
        layout.addWidget(create_btn)

        # Status display
        self.status_label = QLabel(get_text("status_default"))
        self.status_label.setStyleSheet("background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton(get_text("create_link_button"))
        ok_btn.clicked.connect(self.create_link)
        cancel_btn = QPushButton(get_text("cancel_button"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
    
    def search_cards(self):
        """搜索卡片"""
        query = self.search_input.text().strip()
        if not query:
            self.search_results.clear()
            return
        
        self.search_results.clear()
        cards = self.card_linker.search_cards(query)
        
        for card_info in cards:
            if card_info['note_id'] == self.current_note.id:
                continue

            item_text = f"{card_info['question']} ({get_text('deck_label')}: {card_info['deck']})"
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, card_info)
            self.search_results.addItem(item)
    
    def select_existing_card(self, item):
        """选择现有卡片"""
        card_info = item.data(USER_ROLE)
        self.selected_card_id = card_info['id']
        self.status_label.setText(f"已选择: {card_info['question'][:40]}...")
        self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 4px;")
    
    def create_new_card(self):
        """Create new card"""
        front = self.front_input.text().strip()
        back = self.back_input.text().strip()

        if not front or not back:
            showInfo(get_text("enter_front_back"))
            return

        card_id = self.card_linker.create_new_card(self.current_note, front, back)
        if card_id:
            self.selected_card_id = card_id
            self.status_label.setText(f"Created: {front[:40]}...")
            self.status_label.setStyleSheet("background-color: #e3f2fd; padding: 8px; border-radius: 4px;")
            self.front_input.clear()
            self.back_input.clear()
    
    def create_link(self):
        """Create link"""
        link_text = self.link_text_input.text().strip()
        if not link_text:
            showInfo(get_text("enter_link_text"))
            return

        if not self.selected_card_id:
            showInfo(get_text("select_or_create"))
            return

        # Insert link to editor
        self.card_linker.insert_link(self.editor, link_text, self.selected_card_id)
        # Save link information
        self.card_linker.add_link_to_note(self.current_note, self.selected_card_id, link_text)

        showInfo(get_text("link_created"))
        self.accept()

# 创建插件实例
card_linker = CardLinker()

# 注册编辑器按钮
def setup_editor_buttons(buttons, editor):
    return card_linker.setup_editor_button(buttons, editor)

gui_hooks.editor_did_init_buttons.append(setup_editor_buttons)

# 复习时显示关联卡片 - 简化版本
def add_linked_cards_to_review(html, card, context):
    """Display linked cards during review - only on answer side, simplified interaction"""
    # Only show related knowledge points when displaying answer
    if context != "reviewAnswer":
        return html

    try:
        note = card.note()
        linked_cards = card_linker.get_linked_cards(note)

        if linked_cards:
            css = """
            <style>
            .linked-cards-container {
                border: 2px solid #2196f3;
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            }
            .linked-card-item {
                display: block;
                padding: 8px 12px;
                margin: 6px 0;
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                color: #333;
                cursor: pointer;
            }
            .linked-card-item:hover {
                background-color: #f5f5f5;
                border-color: #2196f3;
            }
            .knowledge-point-status {
                float: right;
                font-size: 16px;
                margin-left: 10px;
            }
            .status-reviewed { color: #4caf50; }
            .status-pending { color: #ff9800; }
            </style>
            """

            links_html = '<div class="linked-cards-container">'
            links_html += f'<div style="font-weight: bold; text-align: center; margin-bottom: 10px; color: #1976d2;">{get_text("related_knowledge")}</div>'
            
            for link in linked_cards:
                try:
                    linked_card = mw.col.getCard(link['card_id'])
                    if linked_card:
                        # 检查今日是否已复习
                        is_reviewed = check_card_reviewed_today(linked_card)
                        status_icon = "✅" if is_reviewed else "⏳"
                        status_class = "status-reviewed" if is_reviewed else "status-pending"

                        # Add click functionality
                        click_action = f"pycmd('linked_card:{link['card_id']}:{str(is_reviewed).lower()}')"

                        links_html += f'''
                        <div class="linked-card-item" onclick="{click_action}">
                            📚 {link['title']} ({get_text("deck_label")}: {link['deck']})
                            <span class="knowledge-point-status {status_class}">{status_icon}</span>
                        </div>
                        '''
                except:
                    continue
            
            links_html += f'<div style="font-size: 12px; color: #666; text-align: center; margin-top: 8px; font-style: italic;">{get_text("review_status_tip")}</div>'
            links_html += '</div>'
            html = css + html + links_html
    
    except:
        pass
    
    return html

def check_card_reviewed_today(card):
    """Check if card has been reviewed today - compatible version"""
    try:
        # Get today's start timestamp - compatible with different versions
        try:
            # Try new version method
            import time
            # Get timestamp for today at 00:00
            today_start = int(time.time()) - (int(time.time()) % 86400)
        except:
            try:
                # Try old version method
                today_start = mw.col.sched.day_cutoff - 86400
            except:
                # Last fallback method
                import time
                today_start = int(time.time()) - 86400

        # Check card's review records
        reviews = mw.col.db.list(
            "select id from revlog where cid = ? and id > ?",
            card.id, today_start * 1000
        )

        return len(reviews) > 0
    except Exception as e:
        return False

# Handle click commands
def handle_linked_card_click(cmd):
    """Handle linked card click"""
    try:
        if cmd.startswith("linked_card:"):
            parts = cmd.split(":")
            if len(parts) < 3:
                showInfo(f"Command format error: {cmd}")
                return

            card_id = int(parts[1])
            is_reviewed = parts[2] == "true"

            if is_reviewed:
                # Reviewed card: show preview
                show_card_preview(card_id)
            else:
                # Unreviewed card: execute smart switch
                open_card_in_browser(card_id)

    except Exception as e:
        error_msg = f"Click handling failed: {str(e)}"
        showInfo(error_msg)



def show_card_preview(card_id):
    """显示卡片预览"""
    try:
        card = mw.col.getCard(card_id)
        if not card:
            showInfo(get_text("card_not_found"))
            return

        # 使用浏览器自动预览
        from aqt.browser import Browser
        from aqt.qt import QTimer

        # 创建浏览器并搜索目标卡片
        browser = Browser(mw)
        browser.form.searchEdit.lineEdit().setText(f"cid:{card_id}")
        browser.onSearchActivated()
        browser.show()

        def auto_preview():
            try:
                # 检查是否找到了卡片并自动触发预览
                if hasattr(browser, 'table') and browser.table.len_selection() > 0:
                    if hasattr(browser.form, 'actionPreview'):
                        browser.form.actionPreview.trigger()
                    elif hasattr(browser, 'onTogglePreview'):
                        browser.onTogglePreview()
                    elif hasattr(browser, '_on_preview_clicked'):
                        browser._on_preview_clicked()
                    else:
                        showInfo(get_text("manual_preview"))
                else:
                    showInfo(get_text("manual_preview"))
            except:
                showInfo(get_text("manual_preview"))

        # 延迟1秒执行，确保搜索完成
        QTimer.singleShot(1000, auto_preview)

    except Exception as e:
        showInfo(get_text("preview_failed"))

# Preview functionality simplified, using Anki's built-in preview

def open_card_in_browser(card_id):
    """Postpone current card and immediately review clicked card"""
    try:
        # Check if in review mode
        if not mw.reviewer:
            showInfo(get_text("switch_error"))
            return

        if not mw.reviewer.card:
            showInfo(get_text("no_current_card"))
            return

        current_card = mw.reviewer.card
        target_card = mw.col.getCard(card_id)
        if not target_card:
            showInfo(get_text("target_card_not_found"))
            return

        # Check if target card can be reviewed
        if target_card.queue < 0:  # Suspended or buried cards
            showInfo(get_text("card_suspended"))
            return

        # Execute card switch
        success, error_msg = switch_to_target_card(current_card, target_card)

        if not success:
            showInfo(get_text("switch_failed"))

    except Exception as e:
        showInfo(get_text("switch_failed"))

def get_current_time():
    """Get current timestamp - compatible with different Anki versions"""
    try:
        # Try new version method
        import time
        return int(time.time())
    except:
        try:
            # Try old version method
            return mw.col.sched.intTime()
        except:
            # Last fallback method
            import time
            return int(time.time())

def switch_to_target_card(current_card, target_card):
    """Execute card switching operation"""
    try:
        # Use simple timestamp
        import time
        now = int(time.time())

        # Set target card to learning state, immediately reviewable
        target_card.type = 1    # Learning card
        target_card.queue = 1   # Learning queue
        target_card.due = now   # Immediately reviewable

        # Update database directly
        mw.col.db.execute(
            "update cards set type=?, queue=?, due=? where id=?",
            target_card.type, target_card.queue, target_card.due, target_card.id
        )

        # Save changes
        mw.col.save()

        # Reload target card to ensure state synchronization
        target_card = mw.col.getCard(target_card.id)

        # Reset scheduler
        try:
            mw.col.sched.reset()
        except:
            pass

        # Jump to next card
        mw.reviewer.nextCard()

        return True, ""

    except Exception as e:
        return False, str(e)



# Register command handlers
def setup_link_handler():
    """Setup link handler"""
    if hasattr(mw.reviewer, '_linkHandler'):
        original_handler = mw.reviewer._linkHandler

        def new_handler(url):
            if url.startswith("linked_card:"):
                handle_linked_card_click(url)
            elif original_handler:
                original_handler(url)

        mw.reviewer._linkHandler = new_handler

def on_reviewer_init():
    """Setup handler when reviewer initializes"""
    setup_link_handler()

# Register hooks
gui_hooks.reviewer_did_init.append(lambda x: setup_link_handler())
gui_hooks.card_will_show.append(add_linked_cards_to_review)
