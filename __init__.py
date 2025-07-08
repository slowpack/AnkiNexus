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

# PyQt6 compatibility fix
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
    


    def create_default_note_type(self):
        """Create default note type with LinkedCards field"""
        try:
            # Create new model
            model = mw.col.models.new(get_text("default_note_type_name"))

            # Add fields
            front_field = mw.col.models.newField(get_text("front_field_name"))
            mw.col.models.addField(model, front_field)

            back_field = mw.col.models.newField(get_text("back_field_name"))
            mw.col.models.addField(model, back_field)

            linked_cards_field = mw.col.models.newField(self.linked_cards_field)
            mw.col.models.addField(model, linked_cards_field)

            # Create card template
            template = mw.col.models.newTemplate(get_text("card_template_name"))
            template['qfmt'] = get_text("front_template")
            template['afmt'] = get_text("back_template")

            mw.col.models.addTemplate(model, template)

            # Save the model
            mw.col.models.add(model)
            mw.col.models.save(model)

            return model
        except Exception as e:
            showInfo(get_text("create_note_type_failed").format(str(e)))
            return None

    def add_linked_cards_field_to_model(self, model):
        """Add LinkedCards field to existing model"""
        try:
            linked_cards_field = mw.col.models.newField(self.linked_cards_field)
            mw.col.models.addField(model, linked_cards_field)
            mw.col.models.save(model)
        except Exception as e:
            # Silently fail to avoid disrupting user experience
            pass

    def check_field_exists(self, note):
        """Check if LinkedCards field exists and offer solutions"""
        try:
            _ = note[self.linked_cards_field]
            return True
        except KeyError:
            return self.handle_missing_field(note)

    def handle_missing_field(self, note):
        """Handle missing LinkedCards field with smart suggestions"""
        # Check if AnkiNexus note type exists
        note_type_name = get_text("default_note_type_name")
        existing_models = mw.col.models.all()
        ankiNexus_model = None

        for model in existing_models:
            if model['name'] == note_type_name:
                field_names = [field['name'] for field in model['flds']]
                if self.linked_cards_field in field_names:
                    ankiNexus_model = model
                    break

        if ankiNexus_model:
            # AnkiNexus template exists, suggest switching
            return self.suggest_switch_template(ankiNexus_model)
        else:
            # No AnkiNexus template, suggest creating one
            return self.suggest_create_template()

    def suggest_switch_template(self, ankiNexus_model):
        """Suggest switching to AnkiNexus template"""
        from aqt.utils import askUser

        message = get_text("switch_template_suggestion").format(
            ankiNexus_model['name'],
            self.linked_cards_field
        )

        if askUser(message):
            # Show manual switch instructions instead of automatic switching
            showInfo(get_text("manual_switch_instructions").format(ankiNexus_model['name'], ankiNexus_model['name']))
            return False
        return False

    def suggest_create_template(self):
        """Suggest creating AnkiNexus template"""
        from aqt.utils import askUser

        message = get_text("create_template_suggestion").format(self.linked_cards_field)

        if askUser(message):
            # Create AnkiNexus template
            model = self.create_default_note_type()
            if model:
                # Don't auto-switch, prompt user to manually switch
                showInfo(get_text("template_created_manual_switch").format(model['name'], model['name']))
                return False
            return False
        else:
            # User declined, show manual instructions
            showInfo(get_text("field_missing").format(self.linked_cards_field, self.linked_cards_field))
            return False
    
    def show_link_dialog(self, editor):
        """Show link dialog"""
        dialog = LinkDialog(editor, self)
        dialog.exec()
    
    def search_cards(self, query):
        """Search cards"""
        try:
            card_ids = mw.col.findCards(query)
            cards = []
            for card_id in card_ids[:30]:
                card = mw.col.getCard(card_id)
                note = card.note()

                # Clean title for display
                raw_question = note.fields[0] if note.fields else ""
                clean_question = self.clean_card_title_for_search(raw_question)

                cards.append({
                    'id': card_id,
                    'note_id': note.id,
                    'question': clean_question[:80],  # Limit length
                    'deck': mw.col.decks.name(card.did)
                })
            return cards
        except:
            return []

    def clean_card_title_for_search(self, title):
        """Clean card title for search results"""
        import re

        # Remove HTML tags
        clean_title = re.sub(r'<[^>]+>', '', title)

        # Remove extra whitespace and newlines
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        return clean_title
    
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
        """Insert link in editor - only store JSON data, no visual link display"""
        # No longer insert visual links in editor, only save JSON data
        # Link information is already saved to LinkedCards field via add_link_to_note method
        pass
    
    def add_link_to_note(self, note, card_id, link_text):
        """Add link to note"""
        try:
            linked_cards = self.get_linked_cards(note)

            if not any(link['card_id'] == card_id for link in linked_cards):
                card = mw.col.getCard(card_id)
                if not card:
                    showInfo(get_text("error_card_not_found").format(card_id))
                    return False

                linked_note = card.note()

                link_info = {
                    'card_id': card_id,
                    'note_id': linked_note.id,
                    'title': link_text,
                    'deck': mw.col.decks.name(card.did)
                }

                linked_cards.append(link_info)
                success = self.save_linked_cards(note, linked_cards)
                if not success:
                    showInfo(get_text("error_save_link_failed"))
                    return False
                return True
            else:
                showInfo(get_text("error_card_already_linked"))
                return True
        except Exception as e:
            showInfo(get_text("save_link_failed").format(str(e)))
            return False
    
    def get_linked_cards(self, note):
        """Get linked cards"""
        try:
            field_content = note[self.linked_cards_field] or "[]"
            return json.loads(field_content)
        except:
            return []
    
    def save_linked_cards(self, note, linked_cards):
        """Save linked cards"""
        try:
            json_data = json.dumps(linked_cards, ensure_ascii=False)
            print(get_text("debug_save_link_data").format(json_data))
            note[self.linked_cards_field] = json_data
            if note.id != 0:
                mw.col.updateNote(note)
                mw.col.save()
                print(get_text("debug_save_success").format(self.linked_cards_field))
            return True
        except Exception as e:
            error_msg = get_text("save_failed").format(str(e))
            print(get_text("debug_save_failed").format(error_msg))
            showInfo(error_msg)
            return False

class LinkDialog(QDialog):
    def __init__(self, editor, card_linker):
        super().__init__()
        self.editor = editor
        self.card_linker = card_linker
        self.current_note = editor.note
        self.selected_cards = []  # Changed to list to store multiple selected cards
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.setWindowTitle(get_text("dialog_title"))
        self.setMinimumSize(800, 400)

        layout = QVBoxLayout()

        # Top section: search and selected cards side by side
        top_layout = QHBoxLayout()

        # Left side: search area
        search_group = QGroupBox(get_text("search_cards_group"))
        search_layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(get_text("search_placeholder"))
        self.search_input.textChanged.connect(self.search_cards)
        search_layout.addWidget(self.search_input)

        # Search results list
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(200)
        self.search_results.itemDoubleClicked.connect(self.on_item_double_clicked)
        search_layout.addWidget(self.search_results)

        # Add selected card button
        add_selected_btn = QPushButton(get_text("add_selected_card"))
        add_selected_btn.clicked.connect(self.on_add_button_clicked)
        add_selected_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px;")
        search_layout.addWidget(add_selected_btn)

        search_group.setLayout(search_layout)
        top_layout.addWidget(search_group)

        # Right side: selected cards area
        selected_group = QGroupBox(get_text("selected_cards_group"))
        selected_layout = QVBoxLayout()

        # Selected cards list
        self.selected_cards_list = QListWidget()
        self.selected_cards_list.setMaximumHeight(200)
        selected_layout.addWidget(self.selected_cards_list)

        # Operation buttons row
        selected_buttons_layout = QHBoxLayout()

        remove_selected_btn = QPushButton(get_text("remove_selected"))
        remove_selected_btn.clicked.connect(self.remove_selected_card)
        remove_selected_btn.setStyleSheet("background-color: #f44336; color: white; padding: 4px;")

        clear_all_btn = QPushButton(get_text("clear_all"))
        clear_all_btn.clicked.connect(self.clear_all_selections)
        clear_all_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 4px;")

        selected_buttons_layout.addWidget(remove_selected_btn)
        selected_buttons_layout.addWidget(clear_all_btn)
        selected_buttons_layout.addStretch()

        selected_layout.addLayout(selected_buttons_layout)
        selected_group.setLayout(selected_layout)
        top_layout.addWidget(selected_group)

        layout.addLayout(top_layout)

        # Create new card area
        create_group = QGroupBox(get_text("create_new_card_group"))
        create_layout = QHBoxLayout()

        create_info_label = QLabel(get_text("create_new_card_info"))
        create_info_label.setStyleSheet("color: #666; font-size: 12px;")
        create_layout.addWidget(create_info_label)

        create_layout.addStretch()

        create_btn = QPushButton(get_text("create_new_card_btn"))
        create_btn.clicked.connect(self.open_add_cards_dialog)
        create_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; font-weight: bold;")
        create_layout.addWidget(create_btn)

        create_group.setLayout(create_layout)
        layout.addWidget(create_group)

        # Status display
        self.status_label = QLabel(get_text("status_select_cards"))
        self.status_label.setStyleSheet("background-color: #e3f2fd; padding: 8px; border-radius: 4px; color: #1976d2;")
        layout.addWidget(self.status_label)

        # Only keep close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton(get_text("close_dialog"))
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Load existing links
        self.load_existing_links()

    def load_existing_links(self):
        """Load existing links to display list"""
        try:
            linked_cards = self.card_linker.get_linked_cards(self.current_note)

            for link in linked_cards:
                try:
                    # Verify if card still exists
                    card = mw.col.getCard(link['card_id'])
                    if card:
                        selected_card = {
                            'id': link['card_id'],
                            'note_id': link['note_id'],
                            'title': link['title'],
                            'deck': link['deck'],
                            'display_text': link['title'][:40] + "..." if len(link['title']) > 40 else link['title']
                        }
                        self.selected_cards.append(selected_card)
                except:
                    # Card does not exist, skip
                    continue

            self.update_selected_cards_display()
            self.update_status()
        except:
            # If loading fails, continue normal flow
            pass

    def search_cards(self):
        """Search cards"""
        query = self.search_input.text().strip()
        if not query:
            self.search_results.clear()
            return

        self.search_results.clear()
        cards = self.card_linker.search_cards(query)

        for card_info in cards:
            if card_info['note_id'] == self.current_note.id:
                continue

            # Check if this card has already been selected
            already_selected = any(selected['id'] == card_info['id'] for selected in self.selected_cards)

            item_text = f"{card_info['question']} ({get_text('deck_label')}: {card_info['deck']})"
            if already_selected:
                item_text = f"✅ {item_text}"

            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, card_info)

            # If already selected, set different background color
            if already_selected:
                item.setBackground(QColor(200, 255, 200))

            self.search_results.addItem(item)

    def on_item_double_clicked(self, item):
        """Handle double-click event"""
        self.add_card_to_selection(item)

    def on_add_button_clicked(self):
        """Handle add button click event"""
        current_item = self.search_results.currentItem()
        if not current_item:
            showInfo(get_text("error_select_card_first"))
            return
        self.add_card_to_selection(current_item)

    def add_card_to_selection(self, item):
        """添加卡片并立即创建链接"""
        if not item:
            return

        card_info = item.data(USER_ROLE)
        if not card_info:
            return

        # Check if already linked
        if any(selected['id'] == card_info['id'] for selected in self.selected_cards):
            showInfo(get_text("error_card_already_added"))
            return

        # 处理HTML格式和特殊字符，清理标题
        raw_title = card_info['question']
        clean_title = self.clean_card_title(raw_title)
        link_text = clean_title[:50]

        # 立即创建链接
        success = self.card_linker.add_link_to_note(self.current_note, card_info['id'], link_text)

        if success:
            # 添加到已选择列表用于显示
            selected_card = {
                'id': card_info['id'],
                'note_id': card_info['note_id'],
                'title': link_text,
                'deck': card_info['deck'],
                'display_text': clean_title[:40] + "..." if len(clean_title) > 40 else clean_title
            }

            self.selected_cards.append(selected_card)
            self.update_selected_cards_display()

            # Refresh editor
            try:
                self.editor.loadNote()
            except:
                pass

            # Update status
            self.status_label.setText(get_text("status_link_added").format(clean_title[:30]))
            self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;")

            # Refresh search results display
            self.search_cards()
        else:
            showInfo(get_text("error_link_creation_failed"))

    def update_selected_cards_display(self):
        """Update selected cards display"""
        self.selected_cards_list.clear()

        for i, card in enumerate(self.selected_cards):
            item_text = f"{i+1}. {card['display_text']} ({card['deck']})"
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, card)
            self.selected_cards_list.addItem(item)

    def update_status(self):
        """Update status display"""
        count = len(self.selected_cards)
        if count == 0:
            self.status_label.setText(get_text("status_select_cards"))
            self.status_label.setStyleSheet("background-color: #e3f2fd; padding: 8px; border-radius: 4px; color: #1976d2;")
        else:
            self.status_label.setText(get_text("status_links_created").format(count))
            self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;")

    def remove_selected_card(self):
        """Remove selected card and delete link"""
        current_item = self.selected_cards_list.currentItem()
        if not current_item:
            showInfo(get_text("error_select_card_to_remove"))
            return

        card_info = current_item.data(USER_ROLE)
        if card_info:
            # 从LinkedCards字段中移除链接
            linked_cards = self.card_linker.get_linked_cards(self.current_note)
            linked_cards = [link for link in linked_cards if link['card_id'] != card_info['id']]

            # 保存更新后的链接数据
            success = self.card_linker.save_linked_cards(self.current_note, linked_cards)

            if success:
                # 从显示列表中移除
                self.selected_cards = [card for card in self.selected_cards if card['id'] != card_info['id']]
                self.update_selected_cards_display()
                self.update_status()

                # 刷新编辑器
                try:
                    self.editor.loadNote()
                except:
                    pass

                # Refresh search results display
                self.search_cards()

                self.status_label.setText(get_text("status_link_removed").format(card_info['display_text']))
                self.status_label.setStyleSheet("background-color: #fff3cd; padding: 8px; border-radius: 4px; color: #856404;")
            else:
                showInfo(get_text("error_remove_link_failed"))

    def clear_all_selections(self):
        """Clear all links"""
        if not self.selected_cards:
            return

        from aqt.utils import askUser
        if askUser(get_text("confirm_clear_all_links")):
            # 清空LinkedCards字段
            success = self.card_linker.save_linked_cards(self.current_note, [])

            if success:
                self.selected_cards.clear()
                self.update_selected_cards_display()
                self.update_status()

                # Refresh editor
                try:
                    self.editor.loadNote()
                except:
                    pass

                # Refresh search results display
                self.search_cards()

                self.status_label.setText(get_text("status_all_links_cleared"))
                self.status_label.setStyleSheet("background-color: #fff3cd; padding: 8px; border-radius: 4px; color: #856404;")
            else:
                showInfo(get_text("error_clear_links_failed"))

    def clean_card_title(self, title):
        """Clean card title, remove HTML tags and special characters"""
        import re

        # Remove HTML tags
        clean_title = re.sub(r'<[^>]+>', '', title)

        # Remove extra whitespace and newlines
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        # Remove special characters, keep basic text, numbers, punctuation
        clean_title = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\-\[\]{}"]', '', clean_title)

        return clean_title
    
    def open_add_cards_dialog(self):
        """Open simple add card dialog"""
        self.create_simple_add_card_dialog()

    def create_simple_add_card_dialog(self):
        """Create simple add card dialog (alternative solution)"""
        dialog = SimpleAddCardDialog(self)
        if dialog.exec() == DIALOG_ACCEPTED:
            # 获取创建的卡片信息
            if hasattr(dialog, 'created_card_id') and dialog.created_card_id:
                self.auto_add_created_card(dialog.created_card_id, dialog.created_card_title)

    def auto_add_created_card(self, card_id, card_title):
        """Automatically add newly created card as link"""
        try:
            # 清理标题
            clean_title = self.clean_card_title(card_title)
            link_text = clean_title[:50]

            # 立即创建链接
            success = self.card_linker.add_link_to_note(self.current_note, card_id, link_text)

            if success:
                # 获取卡片信息
                card = mw.col.getCard(card_id)
                deck_name = mw.col.decks.name(card.did)

                # 添加到已选择列表用于显示
                selected_card = {
                    'id': card_id,
                    'note_id': card.note().id,
                    'title': link_text,
                    'deck': deck_name,
                    'display_text': clean_title[:40] + "..." if len(clean_title) > 40 else clean_title
                }

                self.selected_cards.append(selected_card)
                self.update_selected_cards_display()

                # Refresh editor
                try:
                    self.editor.loadNote()
                except:
                    pass

                # Update status
                self.status_label.setText(get_text("success_new_card_linked").format(clean_title[:30]))
                self.status_label.setStyleSheet("background-color: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;")
            else:
                showInfo(get_text("error_new_card_link_failed"))
        except Exception as e:
            showInfo(get_text("error_add_link_failed").format(str(e)))


class SimpleAddCardDialog(QDialog):
    """Simple add card dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_dialog = parent
        self.created_card_id = None
        self.created_card_title = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        self.setWindowTitle(get_text("simple_add_card_title"))
        self.setMinimumSize(400, 200)

        layout = QVBoxLayout()

        # Front content
        layout.addWidget(QLabel(get_text("simple_add_card_front")))
        self.front_input = QLineEdit()
        self.front_input.setPlaceholderText(get_text("simple_add_card_front_placeholder"))
        layout.addWidget(self.front_input)

        # Back content
        layout.addWidget(QLabel(get_text("simple_add_card_back")))
        self.back_input = QLineEdit()
        self.back_input.setPlaceholderText(get_text("simple_add_card_back_placeholder"))
        layout.addWidget(self.back_input)

        # Buttons
        button_layout = QHBoxLayout()

        create_btn = QPushButton(get_text("simple_add_card_create"))
        create_btn.clicked.connect(self.create_card)
        create_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")

        cancel_btn = QPushButton(get_text("cancel_button"))
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Set focus
        self.front_input.setFocus()

    def create_card(self):
        """Create card"""
        front = self.front_input.text().strip()
        back = self.back_input.text().strip()

        if not front or not back:
            showInfo(get_text("error_fill_front_back"))
            return

        try:
            # 使用当前笔记的模板创建新卡片
            current_note = self.parent_dialog.current_note
            model = current_note.model()

            # 创建新笔记
            new_note = Note(mw.col, model)

            # 设置字段内容
            if len(new_note.fields) > 0:
                new_note.fields[0] = front
            if len(new_note.fields) > 1:
                new_note.fields[1] = back

            # Set deck (use current card's deck or default deck)
            try:
                if mw.reviewer and mw.reviewer.card:
                    deck_id = mw.reviewer.card.did
                else:
                    deck_id = mw.col.conf['curDeck']
                new_note.model()['did'] = deck_id
            except:
                # Use default deck
                pass

            # 添加笔记到集合
            mw.col.addNote(new_note)
            mw.col.save()

            # 获取创建的卡片
            new_cards = new_note.cards()
            if new_cards:
                self.created_card_id = new_cards[0].id
                self.created_card_title = front

                showInfo(get_text("success_card_created").format(front[:30]))
                self.accept()
            else:
                showInfo(get_text("error_card_creation_failed"))

        except Exception as e:
            showInfo(get_text("error_create_card_failed").format(str(e)))
            print(f"Create card error: {e}")


# 创建插件实例
card_linker = CardLinker()

# 注册编辑器按钮
def setup_editor_buttons(buttons, editor):
    return card_linker.setup_editor_button(buttons, editor)

gui_hooks.editor_did_init_buttons.append(setup_editor_buttons)

# Display related cards during review - simplified version
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
                padding: 10px;
                margin: 10px 0;
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            }
            .linked-cards-wrapper {
                margin-top: 8px;
            }
            .linked-card-item {
                display: block;
                padding: 6px 10px;
                margin: 3px 0;
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                color: #333;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s ease;
                position: relative;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .linked-card-item:hover {
                background-color: #f5f5f5;
                border-color: #2196f3;
                transform: translateX(3px);
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            }
            .knowledge-point-status {
                float: right;
                font-size: 14px;
                margin-left: 10px;
            }
            .status-reviewed { color: #4caf50; }
            .status-pending { color: #ff9800; }
            .linked-cards-title {
                font-weight: bold;
                text-align: center;
                margin-bottom: 8px;
                color: #1976d2;
                font-size: 14px;
            }
            .linked-cards-tip {
                font-size: 11px;
                color: #666;
                text-align: center;
                margin-top: 6px;
                font-style: italic;
            }
            </style>
            """

            links_html = '<div class="linked-cards-container">'
            links_html += f'<div class="linked-cards-title">{get_text("related_knowledge")}</div>'
            links_html += '<div class="linked-cards-wrapper">'
            
            for link in linked_cards:
                try:
                    linked_card = mw.col.getCard(link['card_id'])
                    if linked_card:
                        # Check if reviewed today
                        is_reviewed = check_card_reviewed_today(linked_card)
                        status_icon = "✅" if is_reviewed else "⏳"
                        status_class = "status-reviewed" if is_reviewed else "status-pending"

                        # Add click functionality
                        click_action = f"pycmd('linked_card:{link['card_id']}:{str(is_reviewed).lower()}')"

                        # Safely handle special characters
                        safe_title = link["title"].replace('"', '&quot;').replace("'", '&#39;')
                        safe_deck = link["deck"].replace('"', '&quot;').replace("'", '&#39;')
                        tooltip = f"{safe_title} ({get_text('deck_label')}: {safe_deck})"

                        links_html += f'<div class="linked-card-item" onclick="{click_action}" title="{tooltip}">📚 {safe_title}<span class="knowledge-point-status {status_class}">{status_icon}</span></div>'
                    else:
                        # Card does not exist, may have been deleted
                        safe_title = link["title"].replace('"', '&quot;').replace("'", '&#39;')
                        deleted_text = get_text('card_status_deleted')
                        links_html += f'<div class="linked-card-item" style="opacity: 0.5; cursor: not-allowed;" title="{safe_title} ({deleted_text})">📚 {safe_title} ❌</div>'
                except Exception as e:
                    # Log error but continue processing other links
                    safe_title = link.get("title", get_text("card_status_unknown")).replace('"', '&quot;').replace("'", '&#39;')
                    error_text = get_text('card_status_load_error')
                    links_html += f'<div class="linked-card-item" style="opacity: 0.5; cursor: not-allowed;" title="{safe_title} ({error_text})">📚 {safe_title} ⚠️</div>'
                    continue
            
            links_html += '</div>'  # 关闭 linked-cards-wrapper
            links_html += f'<div class="linked-cards-tip">{get_text("review_status_tip")}</div>'
            links_html += '</div>'  # 关闭 linked-cards-container
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
    """Show card preview"""
    try:
        card = mw.col.getCard(card_id)
        if not card:
            showInfo(get_text("card_not_found"))
            return

        # Use browser auto preview
        from aqt.browser import Browser
        from aqt.qt import QTimer

        # Create browser and search target card
        browser = Browser(mw)
        browser.form.searchEdit.lineEdit().setText(f"cid:{card_id}")
        browser.onSearchActivated()
        browser.show()

        def auto_preview():
            try:
                # Check if card is found and auto trigger preview
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

        # Delay 1 second execution to ensure search completion
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
            if handle_suspended_card(target_card):
                # Card was unsuspended, reload it
                target_card = mw.col.getCard(card_id)
            else:
                return

        # Execute card switch
        success, error_msg = switch_to_target_card(current_card, target_card)

        if not success:
            showInfo(get_text("switch_failed"))

    except Exception as e:
        showInfo(get_text("switch_failed"))

def handle_suspended_card(card):
    """Handle suspended or buried card"""
    from aqt.utils import askUser

    try:
        if card.queue == -1:  # Suspended card
            message = get_text("unsuspend_card_question")
            if askUser(message):
                # Unsuspend the card
                mw.col.sched.unsuspendCards([card.id])
                mw.col.save()
                showInfo(get_text("card_unsuspended"))
                return True
            else:
                return False
        elif card.queue == -2:  # Buried card
            message = get_text("unbury_card_question")
            if askUser(message):
                # Unbury the card
                mw.col.sched.unburyCards()
                mw.col.save()
                showInfo(get_text("card_unburied"))
                return True
            else:
                return False
        elif card.queue == -3:  # Buried (sibling)
            message = get_text("unbury_card_question")
            if askUser(message):
                # Unbury the card
                mw.col.sched.unburyCards()
                mw.col.save()
                showInfo(get_text("card_unburied"))
                return True
            else:
                return False
        else:
            # Other negative queue values - ask generically
            message = get_text("restore_card_question")
            if askUser(message):
                # Try to restore the card by setting it to new state
                card.queue = 0  # New card
                card.type = 0   # New card type
                mw.col.updateCard(card)
                mw.col.save()
                showInfo(get_text("card_restored"))
                return True
            else:
                return False

        return False
    except Exception as e:
        showInfo(get_text("unsuspend_failed").format(str(e)))
        return False

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
