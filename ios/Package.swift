// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FaxCloudAnalyzer",
    platforms: [
        .iOS(.v16),
    ],
    products: [
        .library(
            name: "FaxCloudAnalyzer",
            targets: ["FaxCloudAnalyzer"]
        ),
    ],
    dependencies: [
        // Ajouter des dépendances externes ici si nécessaire
        // .package(url: "https://github.com/...", from: "1.0.0"),
    ],
    targets: [
        .target(
            name: "FaxCloudAnalyzer",
            dependencies: []
        ),
        .testTarget(
            name: "FaxCloudAnalyzerTests",
            dependencies: ["FaxCloudAnalyzer"]
        ),
    ]
)
