import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/widgets/home/home_widgets.dart';
import 'package:ganithamithura/screens/units/units_list_screen.dart';
import 'package:ganithamithura/screens/learn/learn_units_screen.dart';

class UnitCardScreen extends StatefulWidget {
  const UnitCardScreen({super.key});

  @override
  State<UnitCardScreen> createState() => _UnitCardScreenState();
}

class _UnitCardScreenState extends State<UnitCardScreen> {
  int _selectedIndex = 1; // Learn tab selected

  void _onNavItemTapped(int index) {
    if (index == 0) {
      // Go back to home
      Get.back();
      return;
    }
    
    if (index == 1) {
      // Already on Learn/Units screen
      return;
    }
    
    // TODO: Navigate to other tabs when ready
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
      backgroundColor: const Color(AppColors.backgroundColor),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, size: 24),
                    onPressed: () => Get.back(),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'Measurement Units',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w600,
                      color: Color(AppColors.textBlack),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              
              // Learn Units Card - Special Featured Card
              _buildLearnUnitsCard(),
              
              const SizedBox(height: 20),
              
              const Text(
                'Practice by Topic',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: Color(AppColors.textBlack),
                ),
              ),
              const SizedBox(height: 12),
              
              // Content - Measurement Units Grid
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  childAspectRatio: 1.0,
                  children: [
                    _buildUnitCard(
                      title: 'Length',
                      subtitle: 'cm, m, km',
                      icon: Icons.straighten,
                      color: const Color(AppColors.measurementColor),
                      borderColor: const Color(AppColors.measurementBorder),
                      iconColor: const Color(AppColors.measurementIcon),
                      onTap: () {
                        Get.to(() => const UnitsListScreen(
                          grade: 3,
                          topic: 'Length',
                        ));
                      },
                    ),
                    _buildUnitCard(
                      title: 'Area',
                      subtitle: 'cm², m², km²',
                      icon: Icons.crop_square,
                      color: const Color(AppColors.measurementColor),
                      borderColor: const Color(AppColors.measurementBorder),
                      iconColor: const Color(AppColors.measurementIcon),
                      onTap: () {
                        Get.to(() => const UnitsListScreen(
                          grade: 3,
                          topic: 'Area',
                        ));
                      },
                    ),
                    _buildUnitCard(
                      title: 'Capacity',
                      subtitle: 'ml, l',
                      icon: Icons.local_drink,
                      color: const Color(AppColors.measurementColor),
                      borderColor: const Color(AppColors.measurementBorder),
                      iconColor: const Color(AppColors.measurementIcon),
                      onTap: () {
                        Get.to(() => const UnitsListScreen(
                          grade: 3,
                          topic: 'Capacity',
                        ));
                      },
                    ),
                    _buildUnitCard(
                      title: 'Weight',
                      subtitle: 'g, kg',
                      icon: Icons.fitness_center,
                      color: const Color(AppColors.measurementColor),
                      borderColor: const Color(AppColors.measurementBorder),
                      iconColor: const Color(AppColors.measurementIcon),
                      onTap: () {
                        Get.to(() => const UnitsListScreen(
                          grade: 3,
                          topic: 'Weight',
                        ));
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: _selectedIndex,
        onTap: _onNavItemTapped,
      ),
    );
  }

  Widget _buildLearnUnitsCard() {
    return GestureDetector(
      onTap: () {
        Get.to(() => const LearnUnitsScreen());
      },
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF667EEA).withOpacity(0.4),
              blurRadius: 16,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Icon(
                Icons.school,
                size: 40,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Learn Units',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Understand m, cm, L, mL, kg, g',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white70,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Start Learning',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF667EEA),
                          ),
                        ),
                        SizedBox(width: 4),
                        Icon(
                          Icons.arrow_forward,
                          size: 14,
                          color: Color(0xFF667EEA),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUnitCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required Color borderColor,
    required Color iconColor,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.24),
          border: Border.all(color: borderColor, width: 1.5),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: borderColor.withOpacity(0.3),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                size: 28,
                color: iconColor,
              ),
            ),
            const Spacer(),
            // Title
            Text(
              title,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Color(AppColors.textBlack),
                height: 1.2,
              ),
            ),
            const SizedBox(height: 4),
            // Subtitle
            Text(
              subtitle,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w400,
                color: Color(AppColors.subText1),
                height: 1.2,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
