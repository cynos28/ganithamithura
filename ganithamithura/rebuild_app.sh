#!/bin/bash
# Rebuild Flutter app with new permissions and fixes

echo "🔨 Rebuilding Flutter App"
echo "========================="
echo ""

cd ganithamithura

echo "1️⃣  Cleaning build..."
flutter clean

echo ""
echo "2️⃣  Getting dependencies..."
flutter pub get

echo ""
echo "3️⃣  Building and installing to emulator..."
echo ""
echo "⚠️  Make sure your emulator is running!"
echo ""

flutter run

echo ""
echo "✅ Done! The app should now have:"
echo "   - INTERNET permission"
echo "   - Cleartext traffic support"
echo "   - Fixed snackbar code"
echo "   - 30s timeout configuration"
