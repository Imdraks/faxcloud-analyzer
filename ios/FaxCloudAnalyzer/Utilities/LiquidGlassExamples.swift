// MARK: - Advanced Liquid Glass Examples
// File: Utilities/LiquidGlassExamples.swift
// This file contains advanced usage examples of the Liquid Glass design system

import SwiftUI

// MARK: - Example 1: Custom Glass Card with Header

struct AdvancedGlassCard<Header: View, Content: View>: View {
    @ViewBuilder let header: Header
    @ViewBuilder let content: Content
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header Section
            header
                .padding(LiquidGlassTheme.Spacing.lg)
                .background(LiquidGlassTheme.Colors.primary.opacity(0.1))
                .frame(maxWidth: .infinity, alignment: .leading)
                .cornerRadius(
                    LiquidGlassTheme.CornerRadius.medium,
                    corners: [.topLeft, .topRight]
                )
            
            // Divider
            Divider()
                .background(LiquidGlassTheme.Colors.glassLight)
                .padding(.horizontal, LiquidGlassTheme.Spacing.lg)
            
            // Content Section
            content
                .padding(LiquidGlassTheme.Spacing.lg)
        }
        .glassCard()
    }
}

// MARK: - Example 2: Glass Grid Layout

struct GlassGridView<Content: View>: View {
    let columns: [GridItem] = [
        GridItem(.flexible(), spacing: LiquidGlassTheme.Spacing.lg),
        GridItem(.flexible(), spacing: LiquidGlassTheme.Spacing.lg)
    ]
    
    @ViewBuilder let content: Content
    
    var body: some View {
        LazyVGrid(columns: columns, spacing: LiquidGlassTheme.Spacing.lg) {
            content
        }
        .padding(LiquidGlassTheme.Spacing.lg)
    }
}

// MARK: - Example 3: Glass Segmented Picker

struct GlassSegmentedPicker: View {
    @State private var selection = 0
    let options: [String]
    let action: (Int) -> Void
    
    var body: some View {
        HStack(spacing: LiquidGlassTheme.Spacing.sm) {
            ForEach(Array(options.enumerated()), id: \.offset) { index, option in
                VStack {
                    Text(option)
                        .font(LiquidGlassTheme.Typography.caption)
                        .fontWeight(selection == index ? .semibold : .regular)
                        .foregroundColor(
                            selection == index ?
                            .black :
                            .white
                        )
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, LiquidGlassTheme.Spacing.md)
                .background(
                    selection == index ?
                    LiquidGlassTheme.Colors.primary :
                    LiquidGlassTheme.Colors.cardBackground.opacity(0.6)
                )
                .cornerRadius(LiquidGlassTheme.CornerRadius.small)
                .onTapGesture {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selection = index
                        action(index)
                    }
                }
            }
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .background(LiquidGlassTheme.Colors.cardBackground.opacity(0.6))
        .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
    }
}

// MARK: - Example 4: Glass Expandable Section

struct GlassExpandableSection: View {
    let title: String
    let icon: String
    @State private var isExpanded = false
    let content: String
    
    var body: some View {
        VStack(spacing: 0) {
            Button(action: {
                withAnimation(.easeInOut(duration: 0.3)) {
                    isExpanded.toggle()
                }
            }) {
                HStack {
                    Image(systemName: icon)
                        .foregroundColor(LiquidGlassTheme.Colors.primary)
                    Text(title)
                        .font(LiquidGlassTheme.Typography.headline)
                    Spacer()
                    Image(systemName: "chevron.right")
                        .foregroundColor(.gray)
                        .rotationEffect(.degrees(isExpanded ? 90 : 0))
                }
                .padding(LiquidGlassTheme.Spacing.lg)
            }
            
            if isExpanded {
                Divider()
                    .background(LiquidGlassTheme.Colors.glassLight)
                
                Text(content)
                    .font(LiquidGlassTheme.Typography.body)
                    .padding(LiquidGlassTheme.Spacing.lg)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .glassCard()
    }
}

// MARK: - Example 5: Glass Progress Indicator

struct GlassProgressView: View {
    let progress: Double // 0.0 to 1.0
    let label: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: LiquidGlassTheme.Spacing.md) {
            HStack {
                Text(label)
                    .font(LiquidGlassTheme.Typography.caption)
                Spacer()
                Text("\(Int(progress * 100))%")
                    .font(LiquidGlassTheme.Typography.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(LiquidGlassTheme.Colors.primary)
            }
            
            ZStack(alignment: .leading) {
                // Background track
                RoundedRectangle(cornerRadius: LiquidGlassTheme.CornerRadius.small)
                    .fill(LiquidGlassTheme.Colors.glassLight)
                
                // Progress fill
                RoundedRectangle(cornerRadius: LiquidGlassTheme.CornerRadius.small)
                    .fill(LiquidGlassTheme.Colors.primary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .scaleEffect(x: progress, anchor: .leading)
            }
            .frame(height: 6)
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .glassCard()
    }
}

// MARK: - Example 6: Glass Floating Action Button

struct GlassFloatingActionButton: View {
    let icon: String
    let label: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: LiquidGlassTheme.Spacing.sm) {
                Image(systemName: icon)
                    .font(.system(size: 24, weight: .semibold))
                Text(label)
                    .font(LiquidGlassTheme.Typography.caption2)
            }
            .frame(width: 64, height: 64)
            .foregroundColor(.black)
            .background(LiquidGlassTheme.Colors.primary)
            .cornerRadius(32)
            .shadow(color: LiquidGlassTheme.Colors.primary.opacity(0.4), radius: 8)
        }
    }
}

// MARK: - Example 7: Glass Menu/Dropdown

struct GlassMenuButton<Label: View, Content: View>: View {
    @State private var isPresented = false
    @ViewBuilder let label: Label
    @ViewBuilder let content: Content
    
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.md) {
            Button(action: { isPresented.toggle() }) {
                HStack {
                    label
                    Spacer()
                    Image(systemName: "chevron.down")
                        .foregroundColor(LiquidGlassTheme.Colors.primary)
                        .rotationEffect(.degrees(isPresented ? 180 : 0))
                }
                .padding(LiquidGlassTheme.Spacing.lg)
                .glassCard()
            }
            
            if isPresented {
                content
                    .padding(LiquidGlassTheme.Spacing.lg)
                    .glassCard()
            }
        }
    }
}

// MARK: - Example 8: Glass Notification Banner

struct GlassNotificationBanner: View {
    let type: NotificationType
    let title: String
    let message: String
    let action: (() -> Void)?
    
    enum NotificationType {
        case info, success, warning, error
        
        var icon: String {
            switch self {
            case .info: return "info.circle.fill"
            case .success: return "checkmark.circle.fill"
            case .warning: return "exclamationmark.triangle.fill"
            case .error: return "xmark.circle.fill"
            }
        }
        
        var color: Color {
            switch self {
            case .info: return .blue
            case .success: return LiquidGlassTheme.Colors.primary
            case .warning: return .orange
            case .error: return .red
            }
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: LiquidGlassTheme.Spacing.sm) {
            HStack(spacing: LiquidGlassTheme.Spacing.md) {
                Image(systemName: type.icon)
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundColor(type.color)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(LiquidGlassTheme.Typography.headline)
                    Text(message)
                        .font(LiquidGlassTheme.Typography.caption)
                        .foregroundColor(.gray)
                }
                
                Spacer()
            }
            
            if let action = action {
                Button(action: action) {
                    Text("Action")
                        .font(LiquidGlassTheme.Typography.caption)
                        .foregroundColor(type.color)
                }
            }
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .glassCard()
    }
}

// MARK: - Example 9: Glass Tab Bar Alternative

struct GlassTabBarView<Content: View>: View {
    @State private var selectedTab = 0
    let tabs: [String]
    @ViewBuilder let content: Content
    
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.md) {
            // Custom tab bar
            HStack(spacing: LiquidGlassTheme.Spacing.sm) {
                ForEach(Array(tabs.enumerated()), id: \.offset) { index, tab in
                    VStack(spacing: 4) {
                        Text(tab)
                            .font(LiquidGlassTheme.Typography.caption)
                            .fontWeight(selectedTab == index ? .semibold : .regular)
                            .foregroundColor(
                                selectedTab == index ?
                                .black :
                                .white
                            )
                        
                        if selectedTab == index {
                            RoundedRectangle(cornerRadius: 2)
                                .fill(LiquidGlassTheme.Colors.primary)
                                .frame(height: 2)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, LiquidGlassTheme.Spacing.md)
                    .background(
                        selectedTab == index ?
                        LiquidGlassTheme.Colors.primary.opacity(0.1) :
                        Color.clear
                    )
                    .cornerRadius(LiquidGlassTheme.CornerRadius.small)
                    .onTapGesture {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            selectedTab = index
                        }
                    }
                }
            }
            .padding(LiquidGlassTheme.Spacing.md)
            .glassCard()
            
            // Tab content
            content
        }
    }
}

// MARK: - Example 10: Glass Stat Card with Animation

struct GlassAnimatedStatCard: View {
    let icon: String
    let title: String
    @State private var animatedValue: Double = 0
    let finalValue: Double
    let suffix: String = ""
    
    var body: some View {
        VStack(alignment: .leading, spacing: LiquidGlassTheme.Spacing.md) {
            HStack {
                Text(icon)
                    .font(.title2)
                Text(title)
                    .font(LiquidGlassTheme.Typography.caption)
                    .foregroundColor(.gray)
                Spacer()
            }
            
            HStack(baseline: .firstTextBaseline, spacing: 4) {
                Text(String(format: "%.0f", animatedValue))
                    .font(LiquidGlassTheme.Typography.title2)
                    .fontWeight(.semibold)
                    .foregroundColor(LiquidGlassTheme.Colors.primary)
                Text(suffix)
                    .font(LiquidGlassTheme.Typography.body)
                    .foregroundColor(.gray)
            }
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .glassCard()
        .onAppear {
            withAnimation(.easeInOut(duration: 2.0)) {
                animatedValue = finalValue
            }
        }
    }
}

// MARK: - Helper Extension for Corner Radius

extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}

// MARK: - Preview Examples

#Preview("Advanced Card") {
    AdvancedGlassCard(
        header: {
            Text("Card Header")
                .font(LiquidGlassTheme.Typography.headline)
        },
        content: {
            Text("Card content goes here")
                .font(LiquidGlassTheme.Typography.body)
        }
    )
    .padding()
    .background(LiquidGlassTheme.Colors.background)
}

#Preview("Progress View") {
    GlassProgressView(progress: 0.7, label: "Download Progress")
        .padding()
        .background(LiquidGlassTheme.Colors.background)
}

#Preview("Notification") {
    GlassNotificationBanner(
        type: .success,
        title: "Success",
        message: "Operation completed successfully",
        action: {}
    )
    .padding()
    .background(LiquidGlassTheme.Colors.background)
}

#Preview("FAB") {
    VStack {
        Spacer()
        HStack {
            Spacer()
            GlassFloatingActionButton(
                icon: "plus",
                label: "Add",
                action: {}
            )
            .padding()
        }
    }
    .background(LiquidGlassTheme.Colors.background)
}
