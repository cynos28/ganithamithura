import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/widgets/common/buttons_and_cards.dart';
import 'package:ganithamithura/screens/number/number_home_screen.dart';

/// HomeScreen - Main entry point with 4 module buttons
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(AppColors.backgroundColor),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppConstants.standardPadding),
          child: Column(
            children: [
              // App Title
              _buildHeader(),
              const SizedBox(height: 32),
              
              // Module Grid
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: [
                    // Measurement Module
                    ModuleButton(
                      title: 'Measurement',
                      icon: Icons.straighten,
                      color: Color(AppColors.measurementColor),
                      isEnabled: false, // TODO: Phase 2
                      onTap: () {
                        // TODO: Phase 2 - Navigate to Measurement
                        Get.snackbar(
                          'Coming Soon',
                          'Measurement module will be available in Phase 2',
                          backgroundColor: Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                    
                    // Number Module (Enabled - Phase 1)
                    ModuleButton(
                      title: 'Numbers',
                      icon: Icons.pin,
                      color: Color(AppColors.numberColor),
                      isEnabled: true,
                      onTap: () {
                        Get.to(() => const NumberHomeScreen());
                      },
                    ),
                    
                    // Shape Module
                    ModuleButton(
                      title: 'Shapes',
                      icon: Icons.category,
                      color: Color(AppColors.shapeColor),
                      isEnabled: false, // TODO: Phase 2
                      onTap: () {
                        // TODO: Phase 2 - Navigate to Shapes
                        Get.snackbar(
                          'Coming Soon',
                          'Shapes module will be available in Phase 2',
                          backgroundColor: Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                    
                    // Symbol Module
                    ModuleButton(
                      title: 'Symbols',
                      icon: Icons.abc,
                      color: Color(AppColors.symbolColor),
                      isEnabled: false, // TODO: Phase 2
                      onTap: () {
                        // TODO: Phase 2 - Navigate to Symbols
                        Get.snackbar(
                          'Coming Soon',
                          'Symbols module will be available in Phase 2',
                          backgroundColor: Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Footer
              _buildFooter(),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildHeader() {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.school,
              size: 40,
              color: Color(AppColors.primaryColor),
            ),
            const SizedBox(width: 12),
            const Text(
              'Ganitha Mithura',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Choose a learning module',
          style: TextStyle(
            fontSize: 16,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
  
  Widget _buildFooter() {
    return Text(
      'Phase 1: Numbers Module (50% MVP)',
      style: TextStyle(
        fontSize: 12,
        color: Colors.grey[500],
      ),
    );
  }
}
