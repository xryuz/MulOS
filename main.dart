import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:mulos/constants/app_colors.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import 'constants/app_prefs_keys.dart';
import 'constants/app_router.dart';
import 'service/preference_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AppPreferences().init();
  bool isLoginUser = AppPreferences().prefs?.getBool(AppPrefsKeys.isLoginUser) ?? false;

  runApp(MyApp(isLoginUser: isLoginUser));
}

class MyApp extends StatelessWidget {
  final bool isLoginUser;

  const MyApp({
    required this.isLoginUser,
    super.key
  });

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: isLoginUser ? AppRouter.home : AppRouter.sign_in,
      getPages: AppRouter.routes,
      theme: ThemeData(
        fontFamily: "NotoSans",
        scaffoldBackgroundColor: AppColors.background,
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.main,
              foregroundColor: Colors.white,
              overlayColor: Colors.grey,
              textStyle: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15)
          )
        ),
        scrollbarTheme: ScrollbarThemeData(
          thumbColor: WidgetStateProperty.all(const Color(0xFF4285F4)),
          trackColor: WidgetStateProperty.all(AppColors.grey200),
          thumbVisibility: WidgetStateProperty.all(true),
        ),
        appBarTheme: const AppBarTheme(
          color: AppColors.background,
          iconTheme: IconThemeData(
              color: AppColors.backgroundReverse
          ),
          surfaceTintColor: Colors.transparent,
          foregroundColor: Colors.transparent,
          titleTextStyle: TextStyle(fontFamily: "RubikMonoOne", fontSize: 25, color: Color(0xff00057E)),
        ),
        textButtonTheme: TextButtonThemeData(
          style: ElevatedButton.styleFrom(splashFactory: NoSplash.splashFactory,), // disable ripple
        ),
      ),
    );
  }
}

// 새로운 화면 또는 기능을 구현하는 StatefulWidget 추가
class QRScannerPage extends StatefulWidget {
  @override
  _QRScannerPageState createState() => _QRScannerPageState();
}

class _QRScannerPageState extends State<QRScannerPage> {
  final FlutterTts flutterTts = FlutterTts();

  Future<void> checkStudentId(String studentId) async {
    try {
      final response = await http.post(
        Uri.parse('http://your-server-url/scan_qr'), // 서버 URL
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'student_id': studentId}),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);
        if (responseData['status'] == 1) {
          await flutterTts.speak('인증되었습니다');
        } else {
          await flutterTts.speak('학생 정보가 없습니다');
        }
      } else {
        await flutterTts.speak('서버 요청에 실패했습니다');
      }
    } catch (e) {
      print('Error: $e');
      await flutterTts.speak('오류가 발생했습니다');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('QR Code Scanner')),
      body: Center(
        child: ElevatedButton(
          onPressed: () async {
            String mockStudentId = '12345678'; // 테스트용 student_id
            await checkStudentId(mockStudentId);
          },
          child: Text('QR 코드 스캔'),
        ),
      ),
    );
  }
}
