import SwiftUI

// MARK: - Liquid Glass Design System
// Based on Apple's Adopting Liquid Glass guidelines
// https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass

struct LiquidGlassTheme {
    // MARK: - Colors
    struct Colors {
        // Primary accent color (green)
        static let primary = Color(red: 0, green: 1, blue: 0.533)
        
        // Backgrounds
        static let background = Color(red: 0.04, green: 0.04, blue: 0.12)
        static let secondaryBackground = Color(red: 0.08, green: 0.08, blue: 0.16)
        static let cardBackground = Color(red: 0.1, green: 0.1, blue: 0.15)
        
        // Glass effect layers
        static let glassOverlay = Color.black.opacity(0.2)
        static let glassLight = Color.white.opacity(0.1)
    }
    
    // MARK: - Typography
    struct Typography {
        static let largeTitle = Font.system(size: 34, weight: .bold, design: .default)
        static let title2 = Font.system(size: 22, weight: .bold, design: .default)
        static let headline = Font.system(size: 17, weight: .semibold, design: .default)
        static let body = Font.system(size: 17, weight: .regular, design: .default)
        static let caption = Font.system(size: 12, weight: .regular, design: .default)
        static let caption2 = Font.system(size: 11, weight: .regular, design: .default)
    }
    
    // MARK: - Spacing
    struct Spacing {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 12
        static let lg: CGFloat = 16
        static let xl: CGFloat = 24
        static let xxl: CGFloat = 32
    }
    
    // MARK: - Corner Radius
    struct CornerRadius {
        static let small: CGFloat = 6
        static let medium: CGFloat = 12
        static let large: CGFloat = 16
        static let xl: CGFloat = 20
    }
}

// MARK: - Liquid Glass Effect Modifier
struct LiquidGlassEffect: ViewModifier {
    var intensity: Double = 1.0
    
    func body(content: Content) -> some View {
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

// MARK: - Glass Card Modifier
struct GlassCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(LiquidGlassTheme.Spacing.lg)
            .background(LiquidGlassTheme.Colors.cardBackground.opacity(0.6))
            .modifier(LiquidGlassEffect())
    }
}

// MARK: - View Extensions
extension View {
    func liquidGlass(intensity: Double = 1.0) -> some View {
        modifier(LiquidGlassEffect(intensity: intensity))
    }
    
    func glassCard() -> some View {
        modifier(GlassCardModifier())
    }
    
    func glassButton() -> some View {
        if #available(iOS 18.0, *) {
            return AnyView(
                self
                    .buttonStyle(.glass)
            )
        } else {
            return AnyView(
                self
                    .padding(.vertical, 10)
                    .padding(.horizontal, 16)
                    .background(LiquidGlassTheme.Colors.primary.opacity(0.2))
                    .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
            )
        }
    }
    
    func glassProminentButton() -> some View {
        if #available(iOS 18.0, *) {
            return AnyView(
                self
                    .buttonStyle(.glassProminent)
            )
        } else {
            return AnyView(
                self
                    .padding(.vertical, 12)
                    .padding(.horizontal, 16)
                    .background(LiquidGlassTheme.Colors.primary)
                    .foregroundColor(.black)
                    .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
            )
        }
    }
}

#Preview {
    VStack(spacing: 20) {
        Text("Liquid Glass Design")
            .font(LiquidGlassTheme.Typography.title2)
        
        VStack(spacing: 12) {
            Text("Glass Effect Card")
                .font(LiquidGlassTheme.Typography.headline)
        }
        .glassCard()
        
        Button(action: {}) {
            Label("Glass Button", systemImage: "star.fill")
        }
        .glassButton()
    }
    .padding()
    .background(LiquidGlassTheme.Colors.background)
}
