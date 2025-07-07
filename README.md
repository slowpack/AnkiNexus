# AnkiNexus - Knowledge Linker

A powerful Anki plugin that solves card fragmentation by creating compound cards and linking related knowledge points.

## 🌟 Key Features

### 📚 Knowledge Point Linking
- **Smart Linking**: Easily create links between knowledge points while editing cards
- **Bidirectional Association**: Establish logical relationships between cards to build knowledge networks
- **Visual Display**: Show related knowledge points during review to help understand context

### 🔄 Intelligent Review
- **Associated Review**: Automatically display related knowledge points when reviewing main cards
- **Status Indicators**: Clearly show review status of linked cards (Reviewed ✅ / Pending ⏳)
- **One-Click Navigation**: Click linked cards to immediately jump to review or preview

### 🎯 Compound Card Creation
- **Unified Management**: Organize related knowledge points into compound cards
- **Flexible Creation**: Support linking existing cards or creating new cards
- **Smart Templates**: Intelligently detect and prompt to create AnkiNexus templates on first use
- **Seamless Switching**: Automatically switch to appropriate note types without manual configuration

## 🚀 Installation Guide

### Method 1: Install via Anki Add-on Store (Recommended)
1. Open Anki
2. Click `Tools` → `Add-ons`
3. Click `Get Add-ons...`
4. Enter add-on code: `[Add-on code to be published]`
5. Click `OK` and restart Anki

### Method 2: Manual Installation
1. Download the plugin files
2. Open Anki
3. Click `Tools` → `Add-ons`
4. Click `Install from file...`
5. Select the downloaded plugin file
6. Restart Anki

## 📖 User Guide

### Step 1: First-Time Setup (Automatic)

1. **After Installing the Plugin**
   - The plugin automatically detects your note types in the background
   - No manual configuration needed to start using

2. **First Click on Link Button**
   - The plugin intelligently detects the current note type
   - If LinkedCards field is missing, it automatically suggests solutions:
     - **AnkiNexus template found**: Ask if you want to switch to that template
     - **No suitable template**: Ask if you want to create AnkiNexus default template

### Step 2: Creating Knowledge Links

1. **Open Card Editor**
   - Create or edit a card in Anki
   - The plugin automatically ensures you're using a suitable note type

2. **Click Link Button**
   - Find the 🔗 button in the editor toolbar
   - Click to open the knowledge link dialog

3. **Set Link Information**
   - **Link Display Text**: Enter the name to display for the link in the card
   - **Search Existing Cards**: Enter keywords to search for cards to link
   - **Create New Card**: Or directly create a new related card

4. **Complete Link Creation**
   - Select target card or create new card
   - Click "Create Link" button
   - The link will be automatically inserted into the current card being edited

### Step 3: Review Linked Cards

1. **Start Review**
   - Begin normal Anki review
   - Related knowledge points will automatically display when showing answers

2. **View Association Status**
   - ✅ Green icon: Linked cards reviewed today
   - ⏳ Orange icon: Linked cards pending review

3. **Smart Navigation**
   - **Reviewed cards**: Click to preview card content
   - **Pending cards**: Click to immediately jump to review that card

### Step 4: Build Knowledge Networks

1. **Plan Knowledge Structure**
   - Identify main knowledge points and sub-knowledge points
   - Establish clear hierarchical relationships

2. **Create Compound Cards**
   - Create main cards for major concepts
   - Create sub-cards for related details
   - Use linking feature to establish associations

3. **Optimize Review Process**
   - Regularly check link effectiveness
   - Adjust link relationships based on learning progress

## ⚙️ Configuration Options

### Language Settings
The plugin supports Chinese and English interfaces, automatically adapting based on Anki's language settings.

### Custom Field Names
By default, uses "LinkedCards" field to store link information. Can be modified in the code if needed.

## 🔧 Troubleshooting

### Common Issues

**Q: No response when clicking the link button?**
A: Please ensure:
- Currently editing a card
- Plugin is correctly installed and enabled
- Template setup completed as prompted

**Q: Selected "No" when prompted to create template, how to reset?**
A: Click the link button again, the plugin will re-detect and prompt. Or manually add LinkedCards field to current note type.

**Q: Linked cards not displaying?**
A: Check that JSON data format in LinkedCards field is correct and card IDs are valid.

**Q: Navigation function not working?**
A: Ensure target cards are not suspended or buried and are in reviewable state.

**Q: How to switch back to original note type?**
A: In Anki, click "Tools" > "Manage Note Types", select your desired note type and set as default.

### Compatibility
- Supports Anki 2.1.50+
- Compatible with PyQt5 and PyQt6
- Supports Windows, macOS, Linux

## 🎯 Use Cases

### 1. Academic Knowledge System Building
```
Main concept cards → Link to sub-concepts
Theorem cards → Link to proof steps
Formula cards → Link to application examples
```

### 2. Language Learning
```
Vocabulary cards → Link to example sentences
Grammar cards → Link to practice exercises
Dialogue cards → Link to related expressions
```

### 3. Skill Learning
```
Theory cards → Link to practical steps
Concept cards → Link to specific cases
Problem cards → Link to solutions
```

## 🤝 Contributing

Welcome to submit issue reports and feature suggestions!

1. Fork this project
2. Create feature branch
3. Submit changes
4. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Thanks to the Anki community for their support and feedback, making this plugin continuously improve.

---

**Make learning more systematic, make knowledge more coherent!** 🚀
