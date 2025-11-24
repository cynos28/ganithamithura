import 'package:flutter/material.dart';
import 'package:ganithamithura/utils/constants.dart';
import 'package:ganithamithura/services/daily_tip_service.dart';

/// ResourceCard - Card for each learning module (Numbers, Symbols, Measurements, Shapes)
class ResourceCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color backgroundColor;
  final Color borderColor;
  final Color iconColor;
  final VoidCallback onTap;
  final bool isEnabled;

  const ResourceCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.backgroundColor,
    required this.borderColor,
    required this.iconColor,
    required this.onTap,
    this.isEnabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: isEnabled ? onTap : null,
      child: Container(
        height: 148,
        decoration: BoxDecoration(
          color: backgroundColor,
          border: Border.all(color: borderColor, width: 1.5),
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Icon
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: borderColor.withOpacity(0.3),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                size: 26,
                color: iconColor,
              ),
            ),
            const SizedBox(height: 8),
            // Title
            Text(
              title,
              style: const TextStyle(
                fontSize: 19,
                fontWeight: FontWeight.w600,
                color: Color(AppColors.textBlack),
                height: 1.1,
              ),
            ),
            const SizedBox(height: 2),
            // Subtitle
            Flexible(
              child: Text(
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
            ),
          ],
        ),
      ),
    );
  }
}

/// TodayActivityCard - Shows today's activity summary
class TodayActivityCard extends StatelessWidget {
  final String activityTitle;
  final String activitySubtitle;
  final String timeToday;
  final String completedTasks;
  final String progressBadge;

  const TodayActivityCard({
    super.key,
    required this.activityTitle,
    required this.activitySubtitle,
    required this.timeToday,
    required this.completedTasks,
    this.progressBadge = 'Great progress!',
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 156,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment(0.50, 0.00),
          end: Alignment(0.64, 1.00),
          colors: [Color(0xFF2EB872), Color(0xFFA3DE83)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          width: 0.60,
          color: const Color(0x3D49596D),
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0C000000),
            blurRadius: 54,
            offset: Offset(24, 26),
            spreadRadius: 0,
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with title and badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title section
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      activityTitle,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      activitySubtitle,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w400,
                        color: Color(0xFFD9FFC5),
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              // Progress badge
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEFFE4),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  progressBadge,
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFFF08787),
                    height: 1.2,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Stats row
          Expanded(
            child: Row(
              children: [
                // Time today card
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.access_time,
                              size: 12,
                              color: Color(0xFF334156),
                            ),
                            const SizedBox(width: 4),
                            const Flexible(
                              child: Text(
                                'Time today',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w400,
                                  color: Color(0xFF334156),
                                  height: 1.2,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          timeToday,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF334156),
                            height: 1.2,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                // Completed tasks card
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.check_circle_outline,
                              size: 12,
                              color: Color(0xFF334156),
                            ),
                            const SizedBox(width: 4),
                            const Flexible(
                              child: Text(
                                'Completed',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w400,
                                  color: Color(0xFF334156),
                                  height: 1.2,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          completedTasks,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF334156),
                            height: 1.2,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// LearningTipCard - Daily tip card
class LearningTipCard extends StatefulWidget {
  const LearningTipCard({super.key});

  @override
  State<LearningTipCard> createState() => _LearningTipCardState();
}

class _LearningTipCardState extends State<LearningTipCard> with WidgetsBindingObserver {
  String _tipText = '';
  String _topicIcon = '💡';
  Color _backgroundColor = const Color(0xFFFF8C52);
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _loadTip();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Reload tip when app comes back to foreground
    if (state == AppLifecycleState.resumed) {
      _loadTip();
    }
  }

  Future<void> _loadTip() async {
    // Get random cached tip for immediate display
    final cachedData = DailyTipService.getRandomCachedTip();
    
    if (mounted) {
      setState(() {
        _backgroundColor = Color(cachedData['colorScheme']['background'] as int);
        _topicIcon = cachedData['colorScheme']['icon'] as String;
        _tipText = cachedData['tip'] as String;
        _isLoading = false;
      });
    }

    // Fetch from API in background
    try {
      final apiData = await DailyTipService.fetchRandomTip();
      if (mounted) {
        setState(() {
          _backgroundColor = Color(apiData['colorScheme']['background'] as int);
          _topicIcon = apiData['colorScheme']['icon'] as String;
          _tipText = apiData['tip'] as String;
        });
      }
    } catch (e) {
      // Keep cached tip if API fails
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Container(
        width: double.infinity,
        decoration: BoxDecoration(
          color: _backgroundColor,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 54,
              offset: const Offset(24, 26),
            ),
          ],
        ),
        padding: const EdgeInsets.all(16),
        child: const Center(
          child: CircularProgressIndicator(color: Colors.white),
        ),
      );
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [_backgroundColor, _backgroundColor.withOpacity(0.85)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: _backgroundColor.withOpacity(0.15),
            blurRadius: 54,
            offset: const Offset(24, 26),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                _topicIcon,
                style: const TextStyle(fontSize: 24),
              ),
              const SizedBox(width: 8),
              const Text(
                'Daily Tip',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                  height: 1.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 9),
          Text(
            _tipText,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w400,
              fontStyle: FontStyle.italic,
              color: Colors.white,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}

/// BottomNavBar - Custom bottom navigation bar
class BottomNavBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const BottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(16),
          topRight: Radius.circular(16),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.16),
            blurRadius: 54,
            offset: const Offset(6, 6),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _NavItem(
            icon: Icons.home,
            label: 'Home',
            isActive: currentIndex == 0,
            onTap: () => onTap(0),
          ),
          _NavItem(
            icon: Icons.school,
            label: 'Learn',
            isActive: currentIndex == 1,
            onTap: () => onTap(1),
          ),
          _NavItem(
            icon: Icons.bar_chart,
            label: 'Progress',
            isActive: currentIndex == 2,
            onTap: () => onTap(2),
          ),
          _NavItem(
            icon: Icons.person,
            label: 'Profile',
            isActive: currentIndex == 3,
            onTap: () => onTap(3),
          ),
        ],
      ),
    );
  }
}

/// Internal navigation item widget
class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 83.5,
        color: Colors.transparent,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 24,
              color: isActive
                  ? const Color(AppColors.navActiveColor)
                  : const Color(AppColors.navInactiveColor),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: isActive
                    ? const Color(AppColors.navActiveColor)
                    : const Color(AppColors.navInactiveColor),
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
