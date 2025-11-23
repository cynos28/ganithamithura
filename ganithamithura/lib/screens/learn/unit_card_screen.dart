import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/widgets/home/home_widgets.dart';
import 'package:ganithamithura/screens/units/units_list_screen.dart';

class UnitCardScreen extends StatefulWidget {
  const UnitCardScreen({super.key});

  @override
  State<UnitCardScreen> createState() => _UnitCardScreenState();
}

class _UnitCardScreenState extends State<UnitCardScreen> {
  int _selectedIndex = 1; // Learn tab selected

  void _onNavItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
    // Handle navigation based on index
    if (index == 0) {
      Get.back(); // Go back to home
    }
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
