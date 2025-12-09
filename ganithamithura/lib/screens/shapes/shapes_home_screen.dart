import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/widgets/measurements/measurement_widgets.dart';
import 'package:ganithamithura/widgets/home/home_widgets.dart';

import '../../widgets/shapes/shape_widgets.dart';

/// ShapesHomeScreen - Main screen for Measurement module
class ShapesHomeScreen extends StatefulWidget {
  const ShapesHomeScreen({super.key});

  @override
  State<ShapesHomeScreen> createState() => _ShapesHomeScreenState();
}

class _ShapesHomeScreenState extends State<ShapesHomeScreen> {
  int _currentNavIndex = 0;

  void _onNavTap(int index) {
    if (index == 0) {
      // Navigate to home
      Get.back();
      return;
    }
    
    if (index == _currentNavIndex) {
      // Already on current tab
      return;
    }
    
    // TODO: Navigate to other screens when ready
    Get.snackbar(
      'Coming Soon',
      'This feature will be available soon',
      backgroundColor: const Color(AppColors.infoColor),
      colorText: Colors.white,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7FAFA),
      body: SafeArea(
        child: Stack(
          children: [
            // Main content
            Column(
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 24, 16, 0),
                  child: Row(
                    children: [
                      IconButton(
                        icon: const Icon(
                          Icons.arrow_back,
                          size: 24,
                          color: Color(AppColors.textBlack),
                        ),
                        onPressed: () => Get.back(),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Shapes',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.w600,
                                color: Color(AppColors.textBlack),
                                height: 1.2,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Let\'s learn about shapes!',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w400,
                                color: const Color(0xFF2D4059).withOpacity(0.64),
                                height: 1.2,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Scrollable content
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.only(
                      left: 15,
                      right: 15,
                      top: 24,
                      bottom: 90, // Space for bottom nav
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Learning Concepts Section
                        const SectionHeader(
                          title: 'Learning Concepts',
                          badgeText: 'Core Skills',
                        ),
                        const SizedBox(height: 16),
                        
                        // Concepts Grid
                        _buildConceptsGrid(),
                        const SizedBox(height: 24),
                        
                        // Learning Games Section
                        const SectionHeader(
                          title: 'Learning Games',
                          badgeText: 'Fun Practice',
                        ),
                        const SizedBox(height: 16),
                        
                        // Games Grid
                        _buildGamesGrid(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            
            // Bottom Navigation Bar
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: BottomNavBar(
                currentIndex: _currentNavIndex,
                onTap: _onNavTap,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConceptsGrid() {
    return Column(
      children: [
        // First row: Length and Capacity
        Row(
          children: [
            Expanded(
              child: ShapeConceptCard(
                title: '2D Shape',
                subtitle: 'Learn about 2D shapes',
                icon: Icons.straighten,
                backgroundColor: const Color(AppColors.numberColor).withOpacity(0.24),
                borderColor: const Color(AppColors.numberBorder),
                progress: 0.64,
                onTap: () {
                  Get.snackbar(
                    'Coming Soon',
                    'This section activities are under development',
                    backgroundColor: const Color(AppColors.infoColor),
                    colorText: Colors.white,
                  );
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: ShapeConceptCard(
                title: '3D Shapes',
                subtitle: 'Learn about 3D shapes',
                icon: Icons.local_drink,
                backgroundColor: const Color(AppColors.symbolColor).withOpacity(0.24),
                borderColor: const Color(AppColors.symbolBorder),
                progress: 0.64,
                onTap: () {
                  Get.snackbar(
                    'Coming Soon',
                    'Capacity activities are under development',
                    backgroundColor: const Color(AppColors.infoColor),
                    colorText: Colors.white,
                  );
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        // Second row: Area and Weight
        Row(
          children: [
            Expanded(
              child: ShapeConceptCard(
                title: 'Build & match',
                subtitle: 'Build & match',
                icon: Icons.grid_on,
                backgroundColor: const Color(AppColors.measurementColor).withOpacity(0.24),
                borderColor: const Color(AppColors.measurementBorder),
                progress: 0.64,
                onTap: () {
                  Get.snackbar(
                    'Coming Soon',
                    'Area activities are under development',
                    backgroundColor: const Color(AppColors.infoColor),
                    colorText: Colors.white,
                  );
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: ShapeConceptCard(
                title: 'Find real Shapes',
                subtitle: 'Learn about real shapes',
                icon: Icons.scale,
                backgroundColor: const Color(AppColors.shapeColor).withOpacity(0.24),
                borderColor: const Color(AppColors.shapeBorder),
                onTap: () {
                  Get.snackbar(
                    'Coming Soon',
                    'This section activities are under development',
                    backgroundColor: const Color(AppColors.infoColor),
                    colorText: Colors.white,
                  );
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildGamesGrid() {
    return Column(
      children: [
        // First row: Length and Capacity games
        Row(
          children: [
            Expanded(
              child: MeasurementGameCard(
                title: 'Match shapes',
                subtitle: 'Match shapes & Short questions',
                icon: Icons.straighten,
                backgroundColor: const Color(AppColors.numberColor).withOpacity(0.24),
                borderColor: const Color(AppColors.numberBorder),
                buttonColor: const Color(AppColors.numberBorder),
                onTap: () {
                  Get.snackbar(
                    'Coming Soon',
                    'Shapes game is under development',
                    backgroundColor: const Color(AppColors.infoColor),
                    colorText: Colors.white,
                  );
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: MeasurementGameCard(
                title: 'Create patterns',
                subtitle: 'Create patterns',
                icon: Icons.local_drink,
                backgroundColor: const Color(AppColors.symbolColor).withOpacity(0.24),
                borderColor: const Color(AppColors.symbolBorder),
                buttonColor: const Color(AppColors.symbolBorder),
                onTap: () {
                  Get.snackbar(
                    'Coming Soon',
                    'Patterns game is under development',
                    backgroundColor: const Color(AppColors.infoColor),
                    colorText: Colors.white,
                  );
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}
