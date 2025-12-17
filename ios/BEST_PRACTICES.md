# Liquid Glass Best Practices & Standards

## 📖 Quick Reference Guide

### Color Usage

```swift
// ✅ DO: Use theme colors
Text("Error occurred")
    .foregroundColor(LiquidGlassTheme.Colors.primary)

// ❌ DON'T: Hard-code colors
Text("Error occurred")
    .foregroundColor(Color(red: 0, green: 1, blue: 0.533))
```

### Typography

```swift
// ✅ DO: Use theme fonts
Text("Heading").font(LiquidGlassTheme.Typography.headline)

// ❌ DON'T: Mix font definitions
Text("Heading").font(.system(size: 17, weight: .semibold))
```

### Spacing

```swift
// ✅ DO: Use theme spacing
VStack(spacing: LiquidGlassTheme.Spacing.lg) {
    content
}
.padding(LiquidGlassTheme.Spacing.xl)

// ❌ DON'T: Hard-code numbers
VStack(spacing: 16) {
    content
}
.padding(24)
```

### Glass Effects

```swift
// ✅ DO: Use glass modifiers
VStack { content }
    .glassCard()

// ❌ DON'T: Replicate glass styling
VStack { content }
    .padding()
    .background(Color(red: 0.1, green: 0.1, blue: 0.15))
    .cornerRadius(8)
```

## 🎨 Color Palette Best Practices

### Primary Accent (#00FF88)
**Use for:**
- Active states
- Call-to-action buttons
- Important highlights
- Selected navigation items

**Example:**
```swift
Button("Download") {
    // Download action
}
.glassProminentButton()  // Uses primary color
```

### Background Colors
**Use for:**
- View backgrounds
- Safe area fills

**Example:**
```swift
ZStack {
    LiquidGlassTheme.Colors.background
        .ignoresSafeArea()
    
    // Content
}
```

### Card Backgrounds
**Use for:**
- Cards, containers
- Grouped content

**Example:**
```swift
VStack {
    // Card content
}
.glassCard()  // Uses cardBackground
```

## 📐 Spacing Guidelines

### Use Case Reference

| Situation | Spacing | Usage |
|-----------|---------|-------|
| Icon to text | `sm` (8) | Navigation, buttons |
| Element gap | `md` (12) | Within sections |
| Card padding | `lg` (16) | Card contents |
| Screen margins | `xl` (24) | Top-level padding |
| Large sections | `xxl` (32) | Page separation |

### Spacing in Views

```swift
struct MyView: View {
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.lg) {
            // Main sections
            Section1()
            Section2()
        }
        .padding(LiquidGlassTheme.Spacing.xl)  // Screen margin
    }
}
```

## 🧊 Glass Effects Guidelines

### When to Use Glass Cards

✅ **Perfect for:**
- Data containers
- Statistics cards
- List items
- Menu options

```swift
struct ReportRow: View {
    var body: some View {
        VStack {
            // Report content
        }
        .glassCard()  // Recommended
    }
}
```

❌ **Avoid for:**
- Text-only content
- Already-grouped sections

```swift
struct PlainText: View {
    var body: some View {
        Text("Plain text description")
            // Don't add glassCard - unnecessary
    }
}
```

### When to Use Custom Glass Effect

```swift
// ✅ Use custom glass for unique components
struct CustomComponent: View {
    var body: some View {
        VStack {
            // Unique content
        }
        .liquidGlass()  // Custom effect
    }
}

// ❌ Don't overuse - limit to special cases
struct EveryView: View {
    var body: some View {
        VStack {
            // Regular content
        }
        .liquidGlass()  // Too much glass!
    }
}
```

## 🔘 Button Styling Rules

### Primary Action Buttons

**Use `.glassProminentButton()` for:**
- Save, Submit, Download
- Confirmations
- Important actions

```swift
Button(action: saveData) {
    Label("Save", systemImage: "checkmark.circle.fill")
}
.glassProminentButton()
```

### Secondary Action Buttons

**Use `.glassButton()` for:**
- Filter, Sort, Options
- Cancel, Reset
- Less critical actions

```swift
Button(action: filterData) {
    Label("Filter", systemImage: "slider.horizontal.3")
}
.glassButton()
```

### Navigation Buttons

**Don't need button styling:**
- NavigationLink destinations
- Toolbar navigation items

```swift
// ✅ Correct
NavigationLink(destination: DetailView()) {
    Text("View Details")
}

// ❌ Avoid
NavigationLink(destination: DetailView()) {
    Text("View Details")
        .glassButton()
}
```

## 🏗️ Component Architecture

### Creating New Views

**Template:**
```swift
import SwiftUI

struct MyNewView: View {
    // MARK: - Properties
    @State private var myState = false
    
    // MARK: - Body
    var body: some View {
        ZStack {
            LiquidGlassTheme.Colors.background
                .ignoresSafeArea()
            
            VStack(spacing: LiquidGlassTheme.Spacing.lg) {
                HeaderSection()
                ContentSection()
            }
            .padding(LiquidGlassTheme.Spacing.xl)
        }
    }
    
    // MARK: - Sections
    
    @ViewBuilder
    private func HeaderSection() -> some View {
        Text("Header")
            .font(LiquidGlassTheme.Typography.title2)
    }
    
    @ViewBuilder
    private func ContentSection() -> some View {
        VStack {
            // Content
        }
        .glassCard()
    }
}

#Preview {
    MyNewView()
}
```

## 📱 iOS Version Compatibility

### Checking iOS Version

```swift
// ✅ Correct way
if #available(iOS 18.0, *) {
    // Use iOS 18 features
} else {
    // Use fallback for iOS 16-17
}
```

### Automatic Handling

Most views automatically handle iOS versions:

```swift
// This works on all iOS versions automatically
VStack { content }
    .glassCard()  // Adapts to iOS version
```

## ♿ Accessibility Checklist

### For Every View

- [ ] All colors have sufficient contrast (4.5:1)
- [ ] All interactive elements have labels
- [ ] Text scales with Dynamic Type
- [ ] No color-only information (also use icons/text)
- [ ] Reduce Transparency doesn't break UI

### Color Contrast

```swift
// ✅ Good contrast
Text("Label").foregroundColor(LiquidGlassTheme.Colors.primary)

// ❌ Poor contrast (don't use)
Text("Label").foregroundColor(Color.gray.opacity(0.3))
```

### Dynamic Type Support

```swift
// ✅ Scales with system
Text("Title").font(LiquidGlassTheme.Typography.headline)

// ❌ Fixed size
Text("Title").font(.system(size: 17))
```

### Testing Accessibility

```
1. Go to Settings > Accessibility > Display & Text Size
2. Toggle "Reduce Transparency"
   → Verify glass effects remain visible
   → Text should still be readable
   
3. Toggle "Larger Accessibility Sizes"
   → Verify layout doesn't break
   → All content remains accessible
```

## 🔄 State Management Best Practices

### Using @State

```swift
// ✅ Correct
@State private var isLoading = false

// ❌ Avoid multiple states
@State private var data1 = false
@State private var data2 = false
@State private var data3 = false  // Use ViewModel instead
```

### Using @StateObject for ViewModels

```swift
// ✅ Recommended for data logic
@StateObject private var viewModel = ReportViewModel()

// Use in body
.onAppear { viewModel.fetchData() }
```

## 🎭 Animation Best Practices

### Use withAnimation

```swift
// ✅ Correct
Button(action: {
    withAnimation(.easeInOut(duration: 0.3)) {
        isExpanded.toggle()
    }
}) {
    // Button content
}

// ❌ Avoid no animation
Button(action: {
    isExpanded.toggle()
}) {
    // Button content
}
```

### Transition Animations

```swift
// ✅ Smooth transitions
if isExpanded {
    DetailView()
        .transition(.move(edge: .top))
}

// ❌ Sudden appearance
if isExpanded {
    DetailView()
}
```

## 📊 Performance Tips

### List Performance

```swift
// ✅ Good for long lists
LazyVStack(spacing: LiquidGlassTheme.Spacing.lg) {
    ForEach(items) { item in
        ItemView(item: item)
            .glassCard()
    }
}

// ❌ Can be slow for many items
VStack(spacing: LiquidGlassTheme.Spacing.lg) {
    ForEach(items) { item in
        ItemView(item: item)
            .glassCard()
    }
}
```

### Image Loading

```swift
// ✅ Efficient
AsyncImage(url: imageURL) { image in
    image.resizable()
} placeholder: {
    Color.gray
}

// ❌ Can block UI
Image(uiImage: UIImage(data: imageData))
```

### Glass Effects

```swift
// ✅ Efficient
ForEach(items) { item in
    ItemView(item: item)
        .glassCard()
}

// ❌ Can impact performance
VStack {
    ForEach(items) { item in
        ItemView(item: item)
            .glassCard()
            .glassCard()  // Double effect!
            .liquidGlass()  // Triple effect!
    }
}
```

## 🧪 Testing Tips

### Unit Tests

```swift
// Test theme values
func testThemeColors() {
    XCTAssertEqual(
        LiquidGlassTheme.Colors.primary,
        Color(red: 0, green: 1, blue: 0.533)
    )
}
```

### UI Tests

```swift
// Test glass effect exists
let glassCard = app.otherElements["glassCard"]
XCTAssertTrue(glassCard.exists)

// Test button interaction
let saveButton = app.buttons["saveButton"]
saveButton.tap()
```

### Preview Testing

```swift
// Always include previews
#Preview("Light Content") {
    MyView()
}

#Preview("Dark Content") {
    MyView()
        .preferredColorScheme(.dark)
}
```

## 🚀 Code Review Checklist

Before submitting a PR:

- [ ] All colors use `LiquidGlassTheme.Colors`
- [ ] All fonts use `LiquidGlassTheme.Typography`
- [ ] All spacing uses `LiquidGlassTheme.Spacing`
- [ ] Glass effects use proper modifiers
- [ ] Views have #Preview
- [ ] No hard-coded colors/sizes
- [ ] Accessibility verified
- [ ] Performance profiled
- [ ] Documentation updated

## 📚 Common Patterns

### Card List

```swift
struct CardList<T: Identifiable>: View {
    let items: [T]
    
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.lg) {
            ForEach(items) { item in
                CardRow(item: item)
            }
        }
        .padding(LiquidGlassTheme.Spacing.xl)
    }
}
```

### Form Section

```swift
struct FormSection<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content
    
    var body: some View {
        VStack(alignment: .leading, spacing: LiquidGlassTheme.Spacing.md) {
            Text(title)
                .font(LiquidGlassTheme.Typography.headline)
            content
        }
        .glassCard()
    }
}
```

### Modal with Glass

```swift
@State private var showModal = false

var body: some View {
    Button("Open") { showModal = true }
        .sheet(isPresented: $showModal) {
            ModalContent()
                .background(LiquidGlassTheme.Colors.background)
        }
}
```

---

## Summary

**Follow these rules for consistent, maintainable, accessible Liquid Glass implementations:**

1. **Always use theme values** - Never hard-code colors or sizes
2. **Choose appropriate modifiers** - `.glassCard()` vs `.glassButton()` vs `.liquidGlass()`
3. **Test accessibility** - Reduce Transparency, High Contrast, Dynamic Type
4. **Profile performance** - Especially with multiple glass effects
5. **Document code** - Use sections and #Preview
6. **Code review carefully** - Check adherence to standards

**Questions?** See [LIQUID_GLASS_GUIDE.md](./LIQUID_GLASS_GUIDE.md) for detailed documentation.
