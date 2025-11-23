import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:ganithamithura/utils/constants.dart';

/// MeasurementHomeScreen - Main screen for Measurement module
class MeasurementHomeScreen extends StatelessWidget {
  const MeasurementHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(AppColors.backgroundColor),
      appBar: AppBar(
        backgroundColor: const Color(AppColors.measurementBorder),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(AppColors.textBlack)),
          onPressed: () => Get.back(),
        ),
        title: const Text(
          'Measurements',
          style: TextStyle(
            color: Color(AppColors.textBlack),
            fontSize: 20,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppConstants.standardPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Choose a measurement type',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(AppColors.textBlack),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Learn about different types of measurements',
                style: TextStyle(
                  fontSize: 16,
                  color: Color(AppColors.subText2),
                ),
              ),
              const SizedBox(height: 32),
              Expanded(
                child: GridView.count(
                  crossAxisCount: 2,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  children: [
                    _buildMeasurementCard(
                      context,
                      'Length',
                      Icons.straighten,
                      'Measure distances',
                      () {
                        // TODO: Navigate to Length activities
                        Get.snackbar(
                          'Coming Soon',
                          'Length measurement activities are under development',
                          backgroundColor: const Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                    _buildMeasurementCard(
                      context,
                      'Area',
                      Icons.grid_on,
                      'Measure spaces',
                      () {
                        // TODO: Navigate to Area activities
                        Get.snackbar(
                          'Coming Soon',
                          'Area measurement activities are under development',
                          backgroundColor: const Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                    _buildMeasurementCard(
                      context,
                      'Capacity',
                      Icons.local_drink,
                      'Measure volume',
                      () {
                        // TODO: Navigate to Capacity activities
                        Get.snackbar(
                          'Coming Soon',
                          'Capacity measurement activities are under development',
                          backgroundColor: const Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                    _buildMeasurementCard(
                      context,
                      'Weight',
                      Icons.scale,
                      'Measure mass',
                      () {
                        // TODO: Navigate to Weight activities
                        Get.snackbar(
                          'Coming Soon',
                          'Weight measurement activities are under development',
                          backgroundColor: const Color(AppColors.infoColor),
                          colorText: Colors.white,
                        );
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMeasurementCard(
    BuildContext context,
    String title,
    IconData icon,
    String description,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: const Color(AppColors.measurementColor),
          border: Border.all(
            color: const Color(AppColors.measurementBorder),
            width: 1.5,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.3),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                size: 32,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Color(AppColors.textBlack),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              description,
              style: const TextStyle(
                fontSize: 12,
                color: Color(AppColors.subText1),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
