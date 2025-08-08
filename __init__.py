"""
Card Linker Plugin for Anki
Allows linking related cards together to solve card fragmentation
"""
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo
from .components.CardLinker import CardLinker
from .lang import get_text

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

card_linker = CardLinker()

def setup_editor_buttons(buttons, editor):
    return card_linker.setup_editor_button(buttons, editor)
gui_hooks.editor_did_init_buttons.append(setup_editor_buttons)

def add_linked_cards_to_review(html, card, context):
    """Display linked cards during review - only on answer side, simplified interaction"""
    if context != 'reviewAnswer':
        return html
    try:
        note = card.note()
        linked_cards = card_linker.get_linked_cards(note)
        if linked_cards:
            css = '\n            <style>\n            .linked-cards-container {\n                border: 2px solid #2196f3;\n                border-radius: 8px;\n                padding: 10px;\n                margin: 10px 0;\n                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);\n            }\n            .linked-cards-wrapper {\n                margin-top: 8px;\n            }\n            .linked-card-item {\n                display: block;\n                padding: 6px 10px;\n                margin: 3px 0;\n                background-color: white;\n                border: 1px solid #e0e0e0;\n                border-radius: 6px;\n                color: #333;\n                cursor: pointer;\n                font-size: 12px;\n                transition: all 0.2s ease;\n                position: relative;\n                box-shadow: 0 1px 2px rgba(0,0,0,0.1);\n            }\n            .linked-card-item:hover {\n                background-color: #f5f5f5;\n                border-color: #2196f3;\n                transform: translateX(3px);\n                box-shadow: 0 2px 6px rgba(0,0,0,0.15);\n            }\n            .knowledge-point-status {\n                float: right;\n                font-size: 14px;\n                margin-left: 10px;\n            }\n            .status-reviewed { color: #4caf50; }\n            .status-pending { color: #ff9800; }\n            .linked-cards-title {\n                font-weight: bold;\n                text-align: center;\n                margin-bottom: 8px;\n                color: #1976d2;\n                font-size: 14px;\n            }\n            .linked-cards-tip {\n                font-size: 11px;\n                color: #666;\n                text-align: center;\n                margin-top: 6px;\n                font-style: italic;\n            }\n            </style>\n            '
            links_html = '<div class="linked-cards-container">'
            links_html += f"""<div class="linked-cards-title">{get_text('related_knowledge')}</div>"""
            links_html += '<div class="linked-cards-wrapper">'
            for link in linked_cards:
                try:
                    linked_card = mw.col.getCard(link['card_id'])
                    if linked_card:
                        is_reviewed = check_card_reviewed_today(linked_card)
                        status_icon = '✅' if is_reviewed else '⏳'
                        status_class = 'status-reviewed' if is_reviewed else 'status-pending'
                        click_action = f"pycmd('linked_card:{link['card_id']}:{str(is_reviewed).lower()}')"
                        safe_title = link['title'].replace('"', '&quot;').replace("'", '&#39;')
                        safe_deck = link['deck'].replace('"', '&quot;').replace("'", '&#39;')
                        tooltip = f"{safe_title} ({get_text('deck_label')}: {safe_deck})"
                        links_html += f'<div class="linked-card-item" onclick="{click_action}" title="{tooltip}">📚 {safe_title}<span class="knowledge-point-status {status_class}">{status_icon}</span></div>'
                    else:
                        safe_title = link['title'].replace('"', '&quot;').replace("'", '&#39;')
                        deleted_text = get_text('card_status_deleted')
                        links_html += f'<div class="linked-card-item" style="opacity: 0.5; cursor: not-allowed;" title="{safe_title} ({deleted_text})">📚 {safe_title} ❌</div>'
                except Exception as e:
                    safe_title = link.get('title', get_text('card_status_unknown')).replace('"', '&quot;').replace("'", '&#39;')
                    error_text = get_text('card_status_load_error')
                    links_html += f'<div class="linked-card-item" style="opacity: 0.5; cursor: not-allowed;" title="{safe_title} ({error_text})">📚 {safe_title} ⚠️</div>'
                    continue
            links_html += '</div>'
            links_html += f"""<div class="linked-cards-tip">{get_text('review_status_tip')}</div>"""
            links_html += f"""<div class="linked-cards-tip">{get_text('deck_switch_notice')}</div>"""
            links_html += '</div>'
            html = css + html + links_html
    except:
        pass
    return html

def check_card_reviewed_today(card):
    """Check if card has been reviewed today - compatible version"""
    try:
        try:
            import time
            today_start = int(time.time()) - int(time.time()) % 86400
        except:
            try:
                today_start = mw.col.sched.day_cutoff - 86400
            except:
                import time
                today_start = int(time.time()) - 86400
        reviews = mw.col.db.list('select id from revlog where cid = ? and id > ?', card.id, today_start * 1000)
        return len(reviews) > 0
    except Exception as e:
        return False

def is_card_in_current_deck(card):
    """Check if card is in the current review deck"""
    try:
        if not mw.reviewer or not mw.reviewer.card:
            return False
        current_deck_id = mw.reviewer.card.did
        target_deck_id = card.did
        if current_deck_id == target_deck_id:
            return True
        current_deck_name = mw.col.decks.name(current_deck_id)
        target_deck_name = mw.col.decks.name(target_deck_id)
        if target_deck_name.startswith(current_deck_name + '::'):
            return True
        return False
    except Exception as e:
        return False

def handle_linked_card_click(cmd):
    """Handle linked card click"""
    try:
        if cmd.startswith('linked_card:'):
            parts = cmd.split(':')
            if len(parts) < 3:
                showInfo(f'Command format error: {cmd}')
                return
            card_id = int(parts[1])
            is_reviewed = parts[2] == 'true'
            target_card = mw.col.getCard(card_id)
            if not target_card:
                showInfo(get_text('card_not_found'))
                return
            in_current_deck = is_card_in_current_deck(target_card)
            if is_reviewed or not in_current_deck:
                show_card_preview(card_id)
            else:
                open_card_in_browser(card_id)
    except Exception as e:
        error_msg = f'Click handling failed: {str(e)}'
        showInfo(error_msg)

def show_card_preview(card_id):
    """Show card preview"""
    try:
        card = mw.col.getCard(card_id)
        if not card:
            showInfo(get_text('card_not_found'))
            return
        from aqt.browser import Browser
        from aqt.qt import QTimer
        browser = Browser(mw)
        browser.form.searchEdit.lineEdit().setText(f'cid:{card_id}')
        browser.onSearchActivated()
        browser.show()

        def auto_preview():
            try:
                if hasattr(browser, 'table') and browser.table.len_selection() > 0:
                    if hasattr(browser.form, 'actionPreview'):
                        browser.form.actionPreview.trigger()
                    elif hasattr(browser, 'onTogglePreview'):
                        browser.onTogglePreview()
                    elif hasattr(browser, '_on_preview_clicked'):
                        browser._on_preview_clicked()
                    else:
                        showInfo(get_text('manual_preview'))
                else:
                    showInfo(get_text('manual_preview'))
            except:
                showInfo(get_text('manual_preview'))
        QTimer.singleShot(1000, auto_preview)
    except Exception as e:
        showInfo(get_text('preview_failed'))

def open_card_in_browser(card_id):
    """Postpone current card and immediately review clicked card"""
    try:
        if not mw.reviewer:
            showInfo(get_text('switch_error'))
            return
        if not mw.reviewer.card:
            showInfo(get_text('no_current_card'))
            return
        current_card = mw.reviewer.card
        target_card = mw.col.getCard(card_id)
        if not target_card:
            showInfo(get_text('target_card_not_found'))
            return
        if target_card.queue < 0:
            if handle_suspended_card(target_card):
                target_card = mw.col.getCard(card_id)
            else:
                return
        success, error_msg = switch_to_target_card(current_card, target_card)
        if not success:
            showInfo(get_text('switch_failed'))
    except Exception as e:
        showInfo(get_text('switch_failed'))

def handle_suspended_card(card):
    """Handle suspended or buried card"""
    from aqt.utils import askUser
    try:
        if card.queue == -1:
            message = get_text('unsuspend_card_question')
            if askUser(message):
                mw.col.sched.unsuspendCards([card.id])
                mw.col.save()
                showInfo(get_text('card_unsuspended'))
                return True
            else:
                return False
        elif card.queue in (-2, -3):
            message = get_text('unbury_card_question')
            if askUser(message):
                mw.col.sched.unbury_cards([card.id])
                mw.col.save()
                showInfo(get_text('card_unburied'))
                return True
        else:
            message = get_text('restore_card_question')
            if askUser(message):
                card.queue = 0
                card.type = 0
                mw.col.updateCard(card)
                mw.col.save()
                showInfo(get_text('card_restored'))
                return True
            else:
                return False
        return False
    except Exception as e:
        showInfo(get_text('unsuspend_failed').format(str(e)))
        return False

def get_current_time():
    """Get current timestamp - compatible with different Anki versions"""
    try:
        import time
        return int(time.time())
    except:
        try:
            return mw.col.sched.intTime()
        except:
            import time
            return int(time.time())

def switch_to_target_card(current_card, target_card):
    """Execute card switching operation"""
    try:
        import time
        now = int(time.time())
        target_card.type = 1
        target_card.queue = 1
        target_card.due = now
        mw.col.db.execute('update cards set type=?, queue=?, due=? where id=?', target_card.type, target_card.queue, target_card.due, target_card.id)
        mw.col.save()
        target_card = mw.col.getCard(target_card.id)
        try:
            mw.col.sched.reset()
        except:
            pass
        mw.reviewer.nextCard()
        return (True, '')
    except Exception as e:
        return (False, str(e))

def setup_link_handler():
    """Setup link handler"""
    if hasattr(mw.reviewer, '_linkHandler'):
        original_handler = mw.reviewer._linkHandler

        def new_handler(url):
            if url.startswith('linked_card:'):
                handle_linked_card_click(url)
            elif original_handler:
                original_handler(url)
        mw.reviewer._linkHandler = new_handler

def on_reviewer_init():
    """Setup handler when reviewer initializes"""
    setup_link_handler()

gui_hooks.reviewer_did_init.append(lambda x: setup_link_handler())
gui_hooks.card_will_show.append(add_linked_cards_to_review)