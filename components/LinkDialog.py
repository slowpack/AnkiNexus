from ..lang import get_text
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.notes import Note

class LinkDialog(QDialog):

    def __init__(self, editor, card_linker):
        super().__init__()
        self.editor = editor
        self.card_linker = card_linker
        self.current_note = editor.note
        self.selected_cards = []
        self.setup_ui()

    def setup_ui(self):
        """Setup UI"""
        self.setWindowTitle(get_text('dialog_title'))
        self.setMinimumSize(800, 400)
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        search_group = QGroupBox(get_text('search_cards_group'))
        search_layout = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(get_text('search_placeholder'))
        self.search_input.textChanged.connect(self.search_cards)
        search_layout.addWidget(self.search_input)
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(200)
        self.search_results.itemDoubleClicked.connect(self.on_item_double_clicked)
        search_layout.addWidget(self.search_results)
        add_selected_btn = QPushButton(get_text('add_selected_card'))
        add_selected_btn.clicked.connect(self.on_add_button_clicked)
        add_selected_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 6px;')
        search_layout.addWidget(add_selected_btn)
        search_group.setLayout(search_layout)
        top_layout.addWidget(search_group)
        selected_group = QGroupBox(get_text('selected_cards_group'))
        selected_layout = QVBoxLayout()
        self.selected_cards_list = QListWidget()
        self.selected_cards_list.setMaximumHeight(200)
        selected_layout.addWidget(self.selected_cards_list)
        selected_buttons_layout = QHBoxLayout()
        remove_selected_btn = QPushButton(get_text('remove_selected'))
        remove_selected_btn.clicked.connect(self.remove_selected_card)
        remove_selected_btn.setStyleSheet('background-color: #f44336; color: white; padding: 4px;')
        clear_all_btn = QPushButton(get_text('clear_all'))
        clear_all_btn.clicked.connect(self.clear_all_selections)
        clear_all_btn.setStyleSheet('background-color: #ff9800; color: white; padding: 4px;')
        selected_buttons_layout.addWidget(remove_selected_btn)
        selected_buttons_layout.addWidget(clear_all_btn)
        selected_buttons_layout.addStretch()
        selected_layout.addLayout(selected_buttons_layout)
        selected_group.setLayout(selected_layout)
        top_layout.addWidget(selected_group)
        layout.addLayout(top_layout)
        create_group = QGroupBox(get_text('create_new_card_group'))
        create_layout = QHBoxLayout()
        create_info_label = QLabel(get_text('create_new_card_info'))
        create_info_label.setStyleSheet('color: #666; font-size: 12px;')
        create_layout.addWidget(create_info_label)
        create_layout.addStretch()
        create_btn = QPushButton(get_text('create_new_card_btn'))
        create_btn.clicked.connect(self.open_add_cards_dialog)
        create_btn.setStyleSheet('background-color: #2196F3; color: white; padding: 8px; font-weight: bold;')
        create_layout.addWidget(create_btn)
        create_group.setLayout(create_layout)
        layout.addWidget(create_group)
        self.status_label = QLabel(get_text('status_select_cards'))
        self.status_label.setStyleSheet('background-color: #e3f2fd; padding: 8px; border-radius: 4px; color: #1976d2;')
        layout.addWidget(self.status_label)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton(get_text('close_dialog'))
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet('background-color: #2196F3; color: white; font-weight: bold; padding: 8px;')
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.load_existing_links()

    def load_existing_links(self):
        """Load existing links to display list"""
        try:
            linked_cards = self.card_linker.get_linked_cards(self.current_note)
            for link in linked_cards:
                try:
                    card = mw.col.getCard(link['card_id'])
                    if card:
                        selected_card = {'id': link['card_id'], 'note_id': link['note_id'], 'title': link['title'], 'deck': link['deck'], 'display_text': link['title'][:40] + '...' if len(link['title']) > 40 else link['title']}
                        self.selected_cards.append(selected_card)
                except:
                    continue
            self.update_selected_cards_display()
            self.update_status()
        except:
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
            already_selected = any((selected['id'] == card_info['id'] for selected in self.selected_cards))
            item_text = f"{card_info['question']} ({get_text('deck_label')}: {card_info['deck']})"
            if already_selected:
                item_text = f'✅ {item_text}'
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, card_info)
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
            showInfo(get_text('error_select_card_first'))
            return
        self.add_card_to_selection(current_item)

    def add_card_to_selection(self, item):
        """添加卡片并立即创建链接"""
        if not item:
            return
        card_info = item.data(USER_ROLE)
        if not card_info:
            return
        if any((selected['id'] == card_info['id'] for selected in self.selected_cards)):
            showInfo(get_text('error_card_already_added'))
            return
        raw_title = card_info['question']
        clean_title = self.clean_card_title(raw_title)
        link_text = clean_title[:50]
        success = self.card_linker.add_link_to_note(self.current_note, card_info['id'], link_text)
        if success:
            selected_card = {'id': card_info['id'], 'note_id': card_info['note_id'], 'title': link_text, 'deck': card_info['deck'], 'display_text': clean_title[:40] + '...' if len(clean_title) > 40 else clean_title}
            self.selected_cards.append(selected_card)
            self.update_selected_cards_display()
            try:
                self.editor.loadNote()
            except:
                pass
            self.status_label.setText(get_text('status_link_added').format(clean_title[:30]))
            self.status_label.setStyleSheet('background-color: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;')
            self.search_cards()
        else:
            showInfo(get_text('error_link_creation_failed'))

    def update_selected_cards_display(self):
        """Update selected cards display"""
        self.selected_cards_list.clear()
        for i, card in enumerate(self.selected_cards):
            item_text = f"{i + 1}. {card['display_text']} ({card['deck']})"
            item = QListWidgetItem(item_text)
            item.setData(USER_ROLE, card)
            self.selected_cards_list.addItem(item)

    def update_status(self):
        """Update status display"""
        count = len(self.selected_cards)
        if count == 0:
            self.status_label.setText(get_text('status_select_cards'))
            self.status_label.setStyleSheet('background-color: #e3f2fd; padding: 8px; border-radius: 4px; color: #1976d2;')
        else:
            self.status_label.setText(get_text('status_links_created').format(count))
            self.status_label.setStyleSheet('background-color: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;')

    def remove_selected_card(self):
        """Remove selected card and delete link"""
        current_item = self.selected_cards_list.currentItem()
        if not current_item:
            showInfo(get_text('error_select_card_to_remove'))
            return
        card_info = current_item.data(USER_ROLE)
        if card_info:
            linked_cards = self.card_linker.get_linked_cards(self.current_note)
            linked_cards = [link for link in linked_cards if link['card_id'] != card_info['id']]
            success = self.card_linker.save_linked_cards(self.current_note, linked_cards)
            if success:
                self.selected_cards = [card for card in self.selected_cards if card['id'] != card_info['id']]
                self.update_selected_cards_display()
                self.update_status()
                try:
                    self.editor.loadNote()
                except:
                    pass
                self.search_cards()
                self.status_label.setText(get_text('status_link_removed').format(card_info['display_text']))
                self.status_label.setStyleSheet('background-color: #fff3cd; padding: 8px; border-radius: 4px; color: #856404;')
            else:
                showInfo(get_text('error_remove_link_failed'))

    def clear_all_selections(self):
        """Clear all links"""
        if not self.selected_cards:
            return
        from aqt.utils import askUser
        if askUser(get_text('confirm_clear_all_links')):
            success = self.card_linker.save_linked_cards(self.current_note, [])
            if success:
                self.selected_cards.clear()
                self.update_selected_cards_display()
                self.update_status()
                try:
                    self.editor.loadNote()
                except:
                    pass
                self.search_cards()
                self.status_label.setText(get_text('status_all_links_cleared'))
                self.status_label.setStyleSheet('background-color: #fff3cd; padding: 8px; border-radius: 4px; color: #856404;')
            else:
                showInfo(get_text('error_clear_links_failed'))

    def clean_card_title(self, title):
        """Clean card title, remove HTML tags and special characters"""
        import re
        clean_title = re.sub('<[^>]+>', '', title)
        clean_title = re.sub('\\s+', ' ', clean_title).strip()
        clean_title = re.sub('[^\\w\\s\\u4e00-\\u9fff.,!?;:()\\-\\[\\]{}"]', '', clean_title)
        return clean_title

    def open_add_cards_dialog(self):
        """Open simple add card dialog"""
        self.create_simple_add_card_dialog()

    def create_simple_add_card_dialog(self):
        """Create simple add card dialog (alternative solution)"""
        dialog = SimpleAddCardDialog(self)
        if dialog.exec() == DIALOG_ACCEPTED:
            if hasattr(dialog, 'created_card_id') and dialog.created_card_id:
                self.auto_add_created_card(dialog.created_card_id, dialog.created_card_title)

    def auto_add_created_card(self, card_id, card_title):
        """Automatically add newly created card as link"""
        try:
            clean_title = self.clean_card_title(card_title)
            link_text = clean_title[:50]
            success = self.card_linker.add_link_to_note(self.current_note, card_id, link_text)
            if success:
                card = mw.col.getCard(card_id)
                deck_name = mw.col.decks.name(card.did)
                selected_card = {'id': card_id, 'note_id': card.note().id, 'title': link_text, 'deck': deck_name, 'display_text': clean_title[:40] + '...' if len(clean_title) > 40 else clean_title}
                self.selected_cards.append(selected_card)
                self.update_selected_cards_display()
                try:
                    self.editor.loadNote()
                except:
                    pass
                self.status_label.setText(get_text('success_new_card_linked').format(clean_title[:30]))
                self.status_label.setStyleSheet('background-color: #e8f5e8; padding: 8px; border-radius: 4px; color: #2e7d32;')
            else:
                showInfo(get_text('error_new_card_link_failed'))
        except Exception as e:
            showInfo(get_text('error_add_link_failed').format(str(e)))

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
        self.setWindowTitle(get_text('simple_add_card_title'))
        self.setMinimumSize(400, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(get_text('simple_add_card_front')))
        self.front_input = QLineEdit()
        self.front_input.setPlaceholderText(get_text('simple_add_card_front_placeholder'))
        layout.addWidget(self.front_input)
        layout.addWidget(QLabel(get_text('simple_add_card_back')))
        self.back_input = QLineEdit()
        self.back_input.setPlaceholderText(get_text('simple_add_card_back_placeholder'))
        layout.addWidget(self.back_input)
        button_layout = QHBoxLayout()
        create_btn = QPushButton(get_text('simple_add_card_create'))
        create_btn.clicked.connect(self.create_card)
        create_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;')
        cancel_btn = QPushButton(get_text('cancel_button'))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.front_input.setFocus()

    def create_card(self):
        """Create card"""
        front = self.front_input.text().strip()
        back = self.back_input.text().strip()
        if not front or not back:
            showInfo(get_text('error_fill_front_back'))
            return
        try:
            current_note = self.parent_dialog.current_note
            model = current_note.model()
            new_note = Note(mw.col, model)
            if len(new_note.fields) > 0:
                new_note.fields[0] = front
            if len(new_note.fields) > 1:
                new_note.fields[1] = back
            try:
                if mw.reviewer and mw.reviewer.card:
                    deck_id = mw.reviewer.card.did
                else:
                    deck_id = mw.col.conf['curDeck']
                new_note.model()['did'] = deck_id
            except:
                pass
            mw.col.addNote(new_note)
            mw.col.save()
            new_cards = new_note.cards()
            if new_cards:
                self.created_card_id = new_cards[0].id
                self.created_card_title = front
                showInfo(get_text('success_card_created').format(front[:30]))
                self.accept()
            else:
                showInfo(get_text('error_card_creation_failed'))
        except Exception as e:
            showInfo(get_text('error_create_card_failed').format(str(e)))
            print(f'Create card error: {e}')
