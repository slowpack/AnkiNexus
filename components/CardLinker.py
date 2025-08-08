from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.notes import Note
import json
from ..lang import get_text
from .LinkDialog import LinkDialog

class CardLinker:

    def __init__(self):
        self.linked_cards_field = 'LinkedCards'

    def setup_editor_button(self, buttons, editor):
        """Add link button to editor"""

        def on_click(editor_instance):
            self.on_link_button_clicked(editor_instance)
        button = editor.addButton(icon=None, cmd='card_linker', func=on_click, tip=get_text('link_button_tip'), label=get_text('link_button_label'))
        buttons.append(button)
        return buttons

    def on_link_button_clicked(self, editor):
        """Handle link button click"""
        if not editor.note:
            showInfo(get_text('select_card_first'))
            return
        if not self.check_field_exists(editor.note):
            return
        self.show_link_dialog(editor)

    def create_default_note_type(self):
        """Create default note type with LinkedCards field"""
        try:
            model = mw.col.models.new(get_text('default_note_type_name'))
            front_field = mw.col.models.newField(get_text('front_field_name'))
            mw.col.models.addField(model, front_field)
            back_field = mw.col.models.newField(get_text('back_field_name'))
            mw.col.models.addField(model, back_field)
            linked_cards_field = mw.col.models.newField(self.linked_cards_field)
            mw.col.models.addField(model, linked_cards_field)
            template = mw.col.models.newTemplate(get_text('card_template_name'))
            template['qfmt'] = get_text('front_template')
            template['afmt'] = get_text('back_template')
            mw.col.models.addTemplate(model, template)
            mw.col.models.add(model)
            mw.col.models.save(model)
            return model
        except Exception as e:
            showInfo(get_text('create_note_type_failed').format(str(e)))
            return None

    def add_linked_cards_field_to_model(self, model):
        """Add LinkedCards field to existing model"""
        try:
            linked_cards_field = mw.col.models.newField(self.linked_cards_field)
            mw.col.models.addField(model, linked_cards_field)
            mw.col.models.save(model)
        except Exception as e:
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
        note_type_name = get_text('default_note_type_name')
        existing_models = mw.col.models.all()
        ankiNexus_model = None
        for model in existing_models:
            if model['name'] == note_type_name:
                field_names = [field['name'] for field in model['flds']]
                if self.linked_cards_field in field_names:
                    ankiNexus_model = model
                    break
        if ankiNexus_model:
            return self.suggest_switch_template(ankiNexus_model)
        else:
            return self.suggest_create_template()

    def suggest_switch_template(self, ankiNexus_model):
        """Suggest switching to AnkiNexus template"""
        from aqt.utils import askUser
        message = get_text('switch_template_suggestion').format(ankiNexus_model['name'], self.linked_cards_field)
        if askUser(message):
            showInfo(get_text('manual_switch_instructions').format(ankiNexus_model['name'], ankiNexus_model['name']))
            return False
        return False

    def suggest_create_template(self):
        """Suggest creating AnkiNexus template"""
        from aqt.utils import askUser
        message = get_text('create_template_suggestion').format(self.linked_cards_field)
        if askUser(message):
            model = self.create_default_note_type()
            if model:
                showInfo(get_text('template_created_manual_switch').format(model['name'], model['name']))
                return False
            return False
        else:
            showInfo(get_text('field_missing').format(self.linked_cards_field, self.linked_cards_field))
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
                raw_question = note.fields[0] if note.fields else ''
                clean_question = self.clean_card_title_for_search(raw_question)
                cards.append({'id': card_id, 'note_id': note.id, 'question': clean_question[:80], 'deck': mw.col.decks.name(card.did)})
            return cards
        except:
            return []

    def clean_card_title_for_search(self, title):
        """Clean card title for search results"""
        import re
        clean_title = re.sub('<[^>]+>', '', title)
        clean_title = re.sub('\\s+', ' ', clean_title).strip()
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
            showInfo(get_text('create_failed').format(str(e)))
            return None

    def insert_link(self, editor, link_text, card_id):
        """Insert link in editor - only store JSON data, no visual link display"""
        pass

    def add_link_to_note(self, note, card_id, link_text):
        """Add link to note"""
        try:
            linked_cards = self.get_linked_cards(note)
            if not any((link['card_id'] == card_id for link in linked_cards)):
                card = mw.col.getCard(card_id)
                if not card:
                    showInfo(get_text('error_card_not_found').format(card_id))
                    return False
                linked_note = card.note()
                link_info = {'card_id': card_id, 'note_id': linked_note.id, 'title': link_text, 'deck': mw.col.decks.name(card.did)}
                linked_cards.append(link_info)
                success = self.save_linked_cards(note, linked_cards)
                if not success:
                    showInfo(get_text('error_save_link_failed'))
                    return False
                return True
            else:
                showInfo(get_text('error_card_already_linked'))
                return True
        except Exception as e:
            showInfo(get_text('save_link_failed').format(str(e)))
            return False

    def get_linked_cards(self, note):
        """Get linked cards"""
        try:
            field_content = note[self.linked_cards_field] or '[]'
            return json.loads(field_content)
        except:
            return []

    def save_linked_cards(self, note, linked_cards):
        """Save linked cards"""
        try:
            json_data = json.dumps(linked_cards, ensure_ascii=False)
            print(get_text('debug_save_link_data').format(json_data))
            note[self.linked_cards_field] = json_data
            if note.id != 0:
                mw.col.updateNote(note)
                mw.col.save()
                print(get_text('debug_save_success').format(self.linked_cards_field))
            return True
        except Exception as e:
            error_msg = get_text('save_failed').format(str(e))
            print(get_text('debug_save_failed').format(error_msg))
            showInfo(error_msg)
            return False

