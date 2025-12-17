import SwiftUI

// MARK: - iOS Version Compatibility Helper

@available(iOS 16.0, *)
struct GlassEffectModifier: ViewModifier {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    
    func body(content: Content) -> some View {
        if reduceTransparency {
            // Fallback for accessibility
            content
                .background(LiquidGlassTheme.Colors.cardBackground)
                .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
        } else {
            if #available(iOS 18.0, *) {
                content
                    .glassEffect(
                        .regular,
                        in: RoundedRectangle(cornerRadius: LiquidGlassTheme.CornerRadius.medium)
                    )
            } else {
                content
                    .background(
                        RoundedRectangle(cornerRadius: LiquidGlassTheme.CornerRadius.medium)
                            .fill(LiquidGlassTheme.Colors.cardBackground)
                            .blur(radius: 10)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: LiquidGlassTheme.CornerRadius.medium)
                            .stroke(LiquidGlassTheme.Colors.glassLight, lineWidth: 0.5)
                    )
            }
        }
    }
}

// MARK: - Safe Area Aware Layout

struct SafeAreaAwareContainer<Content: View>: View {
    @ViewBuilder let content: Content
    
    var body: some View {
        ZStack {
            LiquidGlassTheme.Colors.background
                .ignoresSafeArea()
            
            content
        }
    }
}

// MARK: - Glass Navigation Style (iOS 16+)

@available(iOS 16.0, *)
struct GlassNavigationStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(
                LiquidGlassTheme.Colors.cardBackground.opacity(0.6),
                for: .navigationBar
            )
            .toolbarBackground(.visible, for: .navigationBar)
    }
}

// MARK: - Form Styling Helper

struct GlassFormSection<Content: View>: View {
    let header: String
    @ViewBuilder let content: Content
    
    var body: some View {
        VStack(alignment: .leading, spacing: LiquidGlassTheme.Spacing.md) {
            Text(header)
                .font(LiquidGlassTheme.Typography.headline)
                .foregroundColor(.gray)
            
            content
                .padding(LiquidGlassTheme.Spacing.lg)
                .background(LiquidGlassTheme.Colors.cardBackground.opacity(0.6))
                .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
        }
    }
}

// MARK: - Liquid Glass List Row

struct GlassListRow<Label: View, Content: View>: View {
    @ViewBuilder let label: Label
    @ViewBuilder let content: Content
    
    var body: some View {
        HStack {
            label
            Spacer()
            content
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .background(LiquidGlassTheme.Colors.cardBackground.opacity(0.6))
        .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
    }
}

// MARK: - Loading State View

struct GlassLoadingView: View {
    @State private var isAnimating = false
    let message: String
    
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.xl) {
            ZStack {
                Circle()
                    .stroke(
                        LiquidGlassTheme.Colors.primary.opacity(0.2),
                        lineWidth: 4
                    )
                
                Circle()
                    .trim(from: 0, to: 0.7)
                    .stroke(
                        LiquidGlassTheme.Colors.primary,
                        lineWidth: 4
                    )
                    .rotationEffect(.degrees(isAnimating ? 360 : 0))
                    .animation(
                        .linear(duration: 1.0).repeatForever(autoreverses: false),
                        value: isAnimating
                    )
            }
            .frame(width: 60, height: 60)
            
            Text(message)
                .font(LiquidGlassTheme.Typography.body)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(LiquidGlassTheme.Colors.background)
        .onAppear { isAnimating = true }
    }
}

// MARK: - Error State View

struct GlassErrorView: View {
    let title: String
    let message: String
    let action: () -> Void
    
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.lg) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 40))
                .foregroundColor(.orange)
            
            VStack(spacing: LiquidGlassTheme.Spacing.sm) {
                Text(title)
                    .font(LiquidGlassTheme.Typography.headline)
                
                Text(message)
                    .font(LiquidGlassTheme.Typography.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            Button(action: action) {
                Label("Réessayer", systemImage: "arrow.clockwise")
                    .frame(maxWidth: .infinity)
                    .padding(LiquidGlassTheme.Spacing.lg)
                    .background(LiquidGlassTheme.Colors.primary)
                    .foregroundColor(.black)
                    .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
            }
        }
        .padding(LiquidGlassTheme.Spacing.xl)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(LiquidGlassTheme.Colors.background)
    }
}

// MARK: - Empty State View

struct GlassEmptyStateView: View {
    let icon: String
    let title: String
    let description: String
    var actionTitle: String? = nil
    var action: (() -> Void)? = nil
    
    var body: some View {
        VStack(spacing: LiquidGlassTheme.Spacing.lg) {
            Image(systemName: icon)
                .font(.system(size: 50))
                .foregroundColor(.gray)
                .opacity(0.5)
            
            VStack(spacing: LiquidGlassTheme.Spacing.sm) {
                Text(title)
                    .font(LiquidGlassTheme.Typography.headline)
                
                Text(description)
                    .font(LiquidGlassTheme.Typography.body)
                    .foregroundColor(.gray)
                    .multilineTextAlignment(.center)
            }
            
            if let actionTitle = actionTitle, let action = action {
                Button(action: action) {
                    Text(actionTitle)
                        .frame(maxWidth: .infinity)
                        .padding(LiquidGlassTheme.Spacing.lg)
                        .background(LiquidGlassTheme.Colors.primary.opacity(0.2))
                        .foregroundColor(LiquidGlassTheme.Colors.primary)
                        .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
                }
            }
        }
        .padding(LiquidGlassTheme.Spacing.xl)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(LiquidGlassTheme.Colors.background)
    }
}

// MARK: - Preview Helper

#Preview("Loading State") {
    GlassLoadingView(message: "Loading reports...")
}

#Preview("Error State") {
    GlassErrorView(
        title: "Connection Error",
        message: "Unable to connect to the server",
        action: {}
    )
}

#Preview("Empty State") {
    GlassEmptyStateView(
        icon: "doc.text",
        title: "No Reports",
        description: "Reports will appear here",
        actionTitle: "Refresh",
        action: {}
    )
}
