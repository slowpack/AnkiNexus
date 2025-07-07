# AnkiNexus Configuration

## Configuration Options

### `language`
- **Type**: String
- **Default**: "auto"
- **Options**: "auto", "en", "zh"
- **Description**: Interface language setting. "auto" will detect from Anki's language setting.

### `linked_cards_field`
- **Type**: String
- **Default**: "LinkedCards"
- **Description**: Field name used to store link information. Change this if you want to use a different field name.

### `auto_create_template`
- **Type**: Boolean
- **Default**: true
- **Description**: Whether to automatically prompt for template creation when LinkedCards field is missing.

### `show_review_status`
- **Type**: Boolean
- **Default**: true
- **Description**: Whether to show review status indicators (✅/⏳) for linked cards during review.

### `enable_smart_switch`
- **Type**: Boolean
- **Default**: true
- **Description**: Whether to enable smart card switching functionality when clicking on linked cards.

### `max_search_results`
- **Type**: Integer
- **Default**: 30
- **Description**: Maximum number of search results to display when searching for cards to link.

## How to Configure

1. Open Anki
2. Go to Tools → Add-ons
3. Select "AnkiNexus - Knowledge Linker"
4. Click "Config"
5. Modify the settings as needed
6. Click "OK" and restart Anki

## Configuration Examples

### Chinese Interface Only
```json
{
    "language": "zh",
    "linked_cards_field": "LinkedCards",
    "auto_create_template": true,
    "show_review_status": true,
    "enable_smart_switch": true,
    "max_search_results": 30
}
```

### Custom Field Name
```json
{
    "language": "auto",
    "linked_cards_field": "RelatedCards",
    "auto_create_template": true,
    "show_review_status": true,
    "enable_smart_switch": true,
    "max_search_results": 30
}
```

### Minimal Configuration
```json
{
    "language": "auto",
    "linked_cards_field": "LinkedCards",
    "auto_create_template": false,
    "show_review_status": false,
    "enable_smart_switch": false,
    "max_search_results": 10
}
```
