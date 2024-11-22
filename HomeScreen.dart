import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import 'dart:typed_data';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(HomeController());
    final shortestSide = MediaQuery.of(context).size.shortestSide;

    return Scaffold(
      body: Column(
        children: [
          Image.asset("assets/image/app_icon.png", width: shortestSide * 0.8, height: shortestSide * 0.8),
          Obx(() {
            return ElevatedButton(
              onPressed: () {
                if (controller.qrData.value.isEmpty) {
                  controller.fetchQrFromServer();
                }
              },
              child: Text(controller.qrData.value.isEmpty ? "QR 생성" : "QR 생성됨"),
            );
          }),
          const SizedBox(height: 20),
          Expanded(
            child: Obx(() {
              if (controller.qrData.value.isNotEmpty) {
                return Image.memory(
                  base64Decode(controller.qrData.value),
                  width: 200,
                  height: 200,
                );
              } else {
                return const Text("QR을 생성하세요.");
              }
            }),
          ),
        ],
      ),
    );
  }
}

class HomeController extends GetxController {
  var qrData = ''.obs; // Base64로 받은 QR 이미지 데이터를 저장
  RxString studentId = ''.obs; // 사용자 ID

  @override
  void onInit() {
    super.onInit();
    loadUserInfo();
  }

  // 사용자 정보 로드
  void loadUserInfo() {
    // 로컬 저장소나 초기 설정 값에서 studentId 로드 (샘플 데이터로 설정)
    studentId.value = "12345"; // 여기에 실제 studentId를 설정하세요.
    print("[DEBUG] Loaded user ID: ${studentId.value}");
  }

  // 서버에서 QR 요청
  void fetchQrFromServer() async {
    try {
      final url = 'http://3.39.184.195:5000/generate_qr'; // Flask 서버의 QR 생성 엔드포인트
      final headers = {'Content-Type': 'application/json'};
      final body = json.encode({'student_id': studentId.value});

      final response = await http.post(
        Uri.parse(url),
        headers: headers,
        body: body,
      );

      if (response.statusCode == 200) {
        qrData.value = base64Encode(response.bodyBytes); // QR 데이터를 Base64로 인코딩
      } else {
        print('Failed to fetch QR: ${response.body}');
      }
    } catch (e) {
      print('Error fetching QR from server: $e');
    }
  }
}
