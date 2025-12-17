#!/usr/bin/env pwsh
<#
.SYNOPSIS
Script pour automatiser le build iOS avec GitHub Actions
.DESCRIPTION
Pousse votre code et déclenche un build iOS automatique sur le cloud
.EXAMPLE
.\build-ios.ps1 -Message "feat: Add new feature"
.PARAMETER Message
Message de commit (optionnel)
#>

param(
    [string]$Message = "chore: Build iOS app"
)

$ErrorActionPreference = "Stop"

# Couleurs (si supporté)
$hasColors = $PSVersionTable.Platform -ne "Unix"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# Navigation
Push-Location (Split-Path $PSCommandPath -Parent)

Write-Status "🚀 FaxCloud iOS Build Script" -Color Cyan
Write-Status "================================`n" -Color Cyan

# Vérifier Git
try {
    $null = git --version
}
catch {
    Write-Status "❌ Git n'est pas installé" -Color Red
    exit 1
}

Write-Status "📝 Préparation du build...`n" -Color Yellow

# Afficher le status
Write-Status "📊 Status Git:" -Color White
git status --short

# Ajouter les changements
Write-Status "`n📦 Ajout des changements..." -Color Yellow
git add .

# Commit
Write-Status "`n💾 Commit: $Message" -Color Yellow
try {
    git commit -m $Message
}
catch {
    Write-Status "ℹ️  Aucun changement à committer" -Color Gray
}

# Push
Write-Status "`n⬆️  Push vers GitHub..." -Color Yellow
try {
    git push origin main
}
catch {
    Write-Status "Tentative: push -u origin main..." -Color Gray
    git push -u origin main
}

# Extraire info du repo
$repoUrl = git config --get remote.origin.url
$repoName = [System.IO.Path]::GetFileNameWithoutExtension($repoUrl.Split('/')[-1])
$repoOwner = $repoUrl -match "github.com/([^/]+)/" ? $matches[1] : "unknown"

Write-Status "`n✅ Code poussé avec succès!`n" -Color Green

Write-Status "🔍 Voir le build:" -Color Cyan
Write-Status "   https://github.com/$repoOwner/$repoName/actions" -Color Blue

Write-Status "`n🟡 Le build démarre automatiquement..." -Color Green
Write-Status "⏳ Attendez 5-10 minutes pour la compilation`n" -Color Yellow

Write-Status "📥 Pour télécharger l'app:" -Color Cyan
Write-Status "   1. Allez sur le lien ci-dessus" -Color White
Write-Status "   2. Cliquez sur 'Build iOS App'" -Color White
Write-Status "   3. Cliquez sur votre build (en vert si succès)" -Color White
Write-Status "   4. Scroll down pour 'Artifacts'" -Color White
Write-Status "   5. Téléchargez 'FaxCloudAnalyzer.ipa'" -Color White
Write-Status "`n" -Color White

Write-Status "🎉 C'est tout! Votre app iOS est en cours de build!`n" -Color Green

# Ouvrir le lien (Windows)
if ($PSVersionTable.Platform -eq "Win32NT") {
    Write-Status "💻 Ouverture du navigateur..." -Color Yellow
    Start-Process "https://github.com/$repoOwner/$repoName/actions"
}

Pop-Location
