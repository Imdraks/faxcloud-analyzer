# Liquid Glass API Reference

## LiquidGlassTheme Colors

```swift
// Primary Colors
LiquidGlassTheme.Colors.primary                   // #00FF88 (RGB: 0, 255, 136)
LiquidGlassTheme.Colors.background                // #0A0A1E (RGB: 10, 10, 30)
LiquidGlassTheme.Colors.secondaryBackground       // #1A1A26 (RGB: 26, 26, 38)
LiquidGlassTheme.Colors.cardBackground            // #1A1A26 (RGB: 26, 26, 38)

// Glass Overlay Colors
LiquidGlassTheme.Colors.glassOverlay              // Black 20% opacity
LiquidGlassTheme.Colors.glassLight                // White 10% opacity
```

## LiquidGlassTheme Typography

```swift
LiquidGlassTheme.Typography.largeTitle            // 34pt Bold
LiquidGlassTheme.Typography.title2                // 22pt Bold
LiquidGlassTheme.Typography.headline              // 17pt Semibold
LiquidGlassTheme.Typography.body                  // 17pt Regular
LiquidGlassTheme.Typography.caption               // 12pt Regular
LiquidGlassTheme.Typography.caption2              // 11pt Regular
```

## LiquidGlassTheme Spacing

```swift
LiquidGlassTheme.Spacing.xs                       // 4pt
LiquidGlassTheme.Spacing.sm                       // 8pt
LiquidGlassTheme.Spacing.md                       // 12pt
LiquidGlassTheme.Spacing.lg                       // 16pt
LiquidGlassTheme.Spacing.xl                       // 24pt
LiquidGlassTheme.Spacing.xxl                      // 32pt
```

## LiquidGlassTheme Corner Radius

```swift
LiquidGlassTheme.CornerRadius.small               // 6pt
LiquidGlassTheme.CornerRadius.medium              // 12pt
LiquidGlassTheme.CornerRadius.large               // 16pt
LiquidGlassTheme.CornerRadius.xl                  // 20pt
```

## View Modifiers

### Glass Effects

#### .glassCard()
Applies glass material effect to container views.

**Usage:**
```swift
VStack {
    Text("Content")
}
.glassCard()
```

**Properties:**
- Applies theme background
- Adds glass effect (iOS 18) or fallback blur (iOS 16-17)
- Adds subtle border
- Includes appropriate padding

**Returns:** Modified view with glass card styling

---

#### .glassButton()
Applies secondary glass button styling.

**Usage:**
```swift
Button(action: { filterData() }) {
    Label("Filter", systemImage: "slider.horizontal.3")
}
.glassButton()
```

**When to use:**
- Filter, sort, options buttons
- Secondary actions
- Less critical operations

**iOS 18+:** Uses native `.buttonStyle(.glass)`  
**iOS 16-17:** Uses custom styling matching glass aesthetics

---

#### .glassProminentButton()
Applies primary glass button styling for important actions.

**Usage:**
```swift
Button(action: { saveData() }) {
    Label("Save", systemImage: "checkmark.circle.fill")
}
.glassProminentButton()
```

**When to use:**
- Save, submit, download buttons
- Confirmations
- Primary actions

**iOS 18+:** Uses native `.buttonStyle(.glassProminent)`  
**iOS 16-17:** Uses custom styling with primary color

---

#### .liquidGlass(intensity: Double)
Applies custom glass effect to any view.

**Usage:**
```swift
CustomView()
    .liquidGlass(intensity: 1.0)
```

**Parameters:**
- `intensity` (default: 1.0) - Glass effect strength (0.0 to 1.0)

**iOS 18+:** Uses `.glassEffect()`  
**iOS 16-17:** Uses blur + overlay simulation

---

### Common Modifiers

```swift
// Apply glass card styling
.glassCard()

// Apply secondary button style
.glassButton()

// Apply primary button style
.glassProminentButton()

// Apply custom glass effect
.liquidGlass()
.liquidGlass(intensity: 0.8)
```

## State View Components

### GlassLoadingView

Shows loading state with animated spinner.

**Parameters:**
- `message: String` - Loading message text

**Usage:**
```swift
if viewModel.isLoading {
    GlassLoadingView(message: "Loading reports...")
} else {
    ContentView()
}
```

**Features:**
- Animated circular spinner
- Message text
- Centered full-screen layout
- Dark background

---

### GlassErrorView

Shows error state with action button.

**Parameters:**
- `title: String` - Error title
- `message: String` - Detailed error message
- `action: () -> Void` - Retry action

**Usage:**
```swift
if let error = viewModel.errorMessage {
    GlassErrorView(
        title: "Connection Error",
        message: error,
        action: { viewModel.retry() }
    )
} else {
    ContentView()
}
```

**Features:**
- Error icon (orange)
- Title and message
- Retry button
- Full-screen layout

---

### GlassEmptyStateView

Shows empty state for no data scenarios.

**Parameters:**
- `icon: String` - SF Symbol name
- `title: String` - Empty state title
- `description: String` - Explanation text
- `actionTitle: String?` - Optional button text
- `action: (() -> Void)?` - Optional button action

**Usage:**
```swift
if viewModel.reports.isEmpty {
    GlassEmptyStateView(
        icon: "doc.text",
        title: "No Reports",
        description: "Create your first report",
        actionTitle: "Create",
        action: { showCreateForm() }
    )
} else {
    ReportList()
}
```

**Features:**
- Large icon display
- Title and description
- Optional action button
- Centered layout

---

## Component Library (GlassCompatibility.swift)

### AdvancedGlassCard (from Examples)

Advanced card with header section.

**Usage:**
```swift
AdvancedGlassCard(
    header: { Text("Header") },
    content: { Text("Content") }
)
```

---

### GlassSegmentedPicker (from Examples)

Custom segmented picker with glass styling.

**Usage:**
```swift
GlassSegmentedPicker(
    options: ["All", "Sent", "Received"],
    action: { selectedIndex in
        filterData(by: selectedIndex)
    }
)
```

---

### GlassExpandableSection (from Examples)

Expandable section with glass card styling.

**Usage:**
```swift
GlassExpandableSection(
    title: "Details",
    icon: "info.circle",
    content: "Detailed information content..."
)
```

---

### GlassProgressView (from Examples)

Progress indicator with glass styling.

**Usage:**
```swift
GlassProgressView(
    progress: 0.75,
    label: "Download Progress"
)
```

---

### GlassFloatingActionButton (from Examples)

Floating action button with glass effect.

**Usage:**
```swift
GlassFloatingActionButton(
    icon: "plus",
    label: "Add",
    action: { showAddForm() }
)
```

---

### GlassNotificationBanner (from Examples)

Dismissible notification banner.

**Types:** `.info`, `.success`, `.warning`, `.error`

**Usage:**
```swift
GlassNotificationBanner(
    type: .success,
    title: "Saved",
    message: "Changes saved successfully",
    action: { dismiss() }
)
```

---

## Compatibility Helpers

### GlassEffectModifier

Automatically applies appropriate glass effect for iOS version.

```swift
@ViewBuilder
private func myContent() -> some View {
    VStack { Text("Content") }
        .modifier(GlassEffectModifier())
}
```

**Automatic handling:**
- iOS 18+: Uses native `.glassEffect()`
- iOS 16-17: Uses simulated effect with blur
- Respects Reduce Transparency setting

---

### SafeAreaAwareContainer

Container that properly handles safe areas.

```swift
SafeAreaAwareContainer {
    // Content automatically respects safe areas
}
```

---

## Example Usage Patterns

### Creating a Custom View

```swift
import SwiftUI

struct MyCustomView: View {
    var body: some View {
        ZStack {
            LiquidGlassTheme.Colors.background
                .ignoresSafeArea()
            
            VStack(spacing: LiquidGlassTheme.Spacing.lg) {
                Text("Title")
                    .font(LiquidGlassTheme.Typography.title2)
                
                MyContent()
                    .glassCard()
                
                Button(action: { /* action */ }) {
                    Text("Action")
                }
                .glassProminentButton()
            }
            .padding(LiquidGlassTheme.Spacing.xl)
        }
    }
    
    @ViewBuilder
    private func MyContent() -> some View {
        VStack {
            Text("Custom content")
                .font(LiquidGlassTheme.Typography.body)
        }
    }
}

#Preview {
    MyCustomView()
}
```

### Conditional State Views

```swift
struct DataView: View {
    @StateObject var viewModel = DataViewModel()
    
    var body: some View {
        ZStack {
            LiquidGlassTheme.Colors.background
                .ignoresSafeArea()
            
            Group {
                if viewModel.isLoading {
                    GlassLoadingView(message: "Loading data...")
                } else if let error = viewModel.errorMessage {
                    GlassErrorView(
                        title: "Error",
                        message: error,
                        action: { viewModel.retry() }
                    )
                } else if viewModel.data.isEmpty {
                    GlassEmptyStateView(
                        icon: "doc.text",
                        title: "No Data",
                        description: "No data available"
                    )
                } else {
                    DataListView(data: viewModel.data)
                }
            }
        }
        .onAppear { viewModel.loadData() }
    }
}
```

---

## Color Constants

### RGB Values

```swift
// Primary
#00FF88 = RGB(0, 255, 136)

// Dark Background
#0A0A1E = RGB(10, 10, 30)

// Card Background
#1A1A26 = RGB(26, 26, 38)
```

### Hex to SwiftUI

```swift
// Convert to SwiftUI Color
Color(red: 0, green: 1, blue: 0.533)         // Primary
Color(red: 0.04, green: 0.04, blue: 0.12)   // Background
Color(red: 0.1, green: 0.1, blue: 0.15)     // Card
```

---

## Font Metrics

| Level | Size | Weight | Use |
|-------|------|--------|-----|
| largeTitle | 34pt | Bold | Page titles |
| title2 | 22pt | Bold | View titles |
| headline | 17pt | Semibold | Section headers |
| body | 17pt | Regular | Main content |
| caption | 12pt | Regular | Secondary info |
| caption2 | 11pt | Regular | Metadata |

---

## Quick Reference

### When in Doubt

| Need | Use |
|------|-----|
| Main color | `LiquidGlassTheme.Colors.primary` |
| Background | `LiquidGlassTheme.Colors.background` |
| Card area | `.glassCard()` |
| Big button | `.glassProminentButton()` |
| Small button | `.glassButton()` |
| Text size | `LiquidGlassTheme.Typography.*` |
| Padding | `LiquidGlassTheme.Spacing.*` |
| Rounded corners | `LiquidGlassTheme.CornerRadius.*` |

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Compatibility:** iOS 16.0+
