import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/services/local_storage/storage_service.dart';
import 'package:ganithamithura/screens/splash/splash_screen.dart';
import 'package:ganithamithura/screens/measurements/new_ar_measurement_screen.dart';
import 'package:ganithamithura/screens/measurements/ar_questions_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize storage service asynchronously
  // Don't block app launch - initialize in background
  StorageService.instance.init();
  
  runApp(const GanithamithuraApp());
}

class GanithamithuraApp extends StatelessWidget {
  const GanithamithuraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title: 'Ganitha Mithura',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: Color(AppColors.primaryColor),
        scaffoldBackgroundColor: Color(AppColors.backgroundColor),
        colorScheme: ColorScheme.fromSeed(
          seedColor: Color(AppColors.primaryColor),
        ),
        textTheme: GoogleFonts.poppinsTextTheme(),
        useMaterial3: true,
      ),
      home: const SplashScreen(),
      getPages: [
        GetPage(
          name: '/ar-measurement',
          page: () => const NewARMeasurementScreen(),
        ),
        GetPage(
          name: '/ar-questions',
          page: () => const ARQuestionsScreen(),
        ),
      ],
    );
  }
}

