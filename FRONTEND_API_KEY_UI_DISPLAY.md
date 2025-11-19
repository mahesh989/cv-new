# Frontend API Key Configuration UI Display

This document describes how the frontend displays the API key configuration interface in two scenarios:
1. **First-time user** (no API keys configured)
2. **Already configured user** (has API keys)

---

## Scenario 1: First-Time User (No API Keys Configured)

### Location
**Home Tab** → AI Model Configuration Section

### Visual Display

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              [🎯 Large Rocket Icon]                    │
│          (Gradient purple/teal circle)                 │
│                                                         │
│         🚀 Welcome to CV Magic!                         │
│                                                         │
│  To get started, you need to configure your AI         │
│  provider API key. This will enable all AI-powered    │
│  features.                                              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 🔑 Select AI Provider                           │  │
│  │                                                  │  │
│  │  [Dropdown: Select AI Provider ▼]              │  │
│  │  [Configure Button]                             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ℹ️ Don't have an API key? Click "Configure" to        │
│     learn how to get one.                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features:
- **Gradient background** (purple/teal with opacity)
- **Large rocket icon** (48px) in gradient circle
- **Welcome message**: "🚀 Welcome to CV Magic!"
- **Clear instructions** about configuring API key
- **Bordered container** for provider selection (white background, teal border)
- **Help text** with info icon
- **Provider dropdown** with "Configure" button

### When User Clicks "Configure":
- Opens **API Key Input Dialog** (modal popup)
- Dialog shows:
  - Provider icon and name
  - "Configure API Key" title
  - Two input fields (API Key + Confirm API Key)
  - Show/Hide password toggles
  - Save button
  - Cancel button

---

## Scenario 2: Already Configured User (Has API Keys)

### Location
**Home Tab** → AI Model Configuration Section

### Visual Display (Collapsed State)

```
┌─────────────────────────────────────────────────────────┐
│  [🤖 Icon]  AI Model Configuration          [▼]         │
│             Currently using: GPT-4o                       │
└─────────────────────────────────────────────────────────┘
```

### Visual Display (Expanded State)

```
┌─────────────────────────────────────────────────────────┐
│  [🤖 Icon]  AI Model Configuration          [▲]         │
│             Currently using: GPT-4o                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  [✨]  GPT-4o RECOMMENDED              [✓]      │  │
│  │                                                  │  │
│  │  Most capable GPT model with vision.            │  │
│  │  Fast • High Cost                               │  │
│  │                                                  │  │
│  │  [Text] [Vision] [Code] [Analysis]             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Select AI Provider                                     │
│  ┌─────────────────────────────────────────────────┐  │
│  │  [☁️] OpenAI                    [Configure ▼]   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Select AI Model                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │  [⚙️] GPT-4o ⭐                          [▼]   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ★ Recommended Models                                  │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │GPT-4o│  │GPT-5 │  │GPT-5 │  │GPT-5 │              │
│  │      │  │Nano  │  │5.1   │  │Flex  │              │
│  └──────┘  └──────┘  └──────┘  └──────┘              │
│                                                         │
│  ℹ️ Model Information                                   │
│  [Model details and capabilities]                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Key Features:
- **Collapsible header** with current model name
- **Current model card** showing:
  - Model icon and name
  - "RECOMMENDED" badge (if applicable)
  - Description
  - Speed and cost info
  - Capability badges (Text, Vision, Code, Analysis)
  - Checkmark indicating it's selected
- **Provider dropdown** showing configured provider with "Configure" button
- **Model dropdown** showing current model
- **Recommended models grid** (4 models in a row)
- **Model information section** at bottom

### Differences from First-Time UI:
1. ✅ Shows **current model** prominently
2. ✅ Has **collapsible/expandable** functionality
3. ✅ Shows **model details** (speed, cost, capabilities)
4. ✅ Displays **recommended models** grid
5. ✅ Shows **configured provider** in dropdown
6. ✅ More **compact and information-dense** layout

---

## API Key Input Dialog (Both Scenarios)

When user clicks "Configure" button, this dialog appears:

```
┌─────────────────────────────────────────────────────────┐
│  [Provider Icon]  Configure API Key                     │
│              Add your [Provider] API key to use this     │
│              provider                                    │
│                                                         │
│  API Key                                                │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 🔑 Enter your [Provider] API key        [👁️]   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  Confirm API Key                                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 🔑 Re-enter your API key                   [👁️] │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Success/Error messages appear here]                   │
│                                                         │
│  [Cancel]                    [Save & Validate]          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Dialog Features:
- **Modal popup** (cannot be dismissed by tapping outside)
- **Provider-specific** icon and colors
- **Two input fields** (API key + confirmation)
- **Show/Hide toggle** for password visibility
- **Validation** on save
- **Success/Error messages**
- **Animated entrance** (scale + fade)

---

## User Flow Comparison

### First-Time User Flow:
1. User logs in → Home tab
2. Sees **Welcome screen** with rocket icon
3. Clicks provider dropdown → Selects provider
4. Clicks **"Configure"** button
5. **Dialog opens** → Enters API key
6. Saves → Dialog closes
7. UI **transitions** to configured state
8. Model automatically selected

### Already Configured User Flow:
1. User logs in → Home tab
2. Sees **collapsed model selector** showing current model
3. Can **expand** to see full configuration
4. Can **change provider** or **model** via dropdowns
5. Can click **"Configure"** to update API key
6. All features available immediately

---

## Visual Styling Details

### First-Time Setup UI:
- **Background**: Gradient (purple 10% opacity → teal 10% opacity)
- **Icon**: Large rocket (48px) in gradient circle
- **Text**: Bold heading, medium body text
- **Container**: White with teal border (2px)
- **Help box**: Teal background (10% opacity)

### Configured UI:
- **Background**: White card
- **Header**: Collapsible with gradient icon
- **Model card**: Gradient background matching model color
- **Badges**: Orange "RECOMMENDED", colored capability pills
- **Dropdowns**: Standard Material design
- **Grid**: 4-column model cards

---

## Key Differences Summary

| Feature | First-Time UI | Configured UI |
|---------|--------------|--------------|
| **Layout** | Centered welcome card | Collapsible section |
| **Icon** | Large rocket (48px) | Small robot (24px) |
| **Message** | "Welcome to CV Magic!" | "Currently using: [Model]" |
| **Model Display** | None | Prominent model card |
| **Provider** | Dropdown in bordered box | Standard dropdown |
| **Model Selection** | Not shown | Full dropdown + grid |
| **Information** | Basic instructions | Detailed model info |
| **State** | Always expanded | Collapsible |
| **Visual Style** | Gradient background | Clean white card |

---

## Code References

- **First-Time UI**: `_buildFirstTimeSetupUI()` in `ai_model_selector.dart`
- **Configured UI**: `_buildHeader()` + `_buildCurrentModelDisplay()` in `ai_model_selector.dart`
- **API Key Dialog**: `APIKeyInputDialog` widget
- **Status Check**: `_checkAPIKeyStatus()` method

