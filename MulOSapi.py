from flask import Flask, jsonify, request, send_file, make_response
import pymysql
import qrcode
from PIL import Image
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

# MySQL 연결 설정
def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='qwer1234',
        db='MulOS',
        charset='utf8'
    )
    return conn

# 루트 경로 처리 (GET /)
@app.route('/')
def index():
    return "Welcome to the API! Use the appropriate endpoints for data."

# 사용자 조회 (GET /users)
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    users_list = []
    for user in users:
        users_list.append({
            'user_id': user[0],
            'student_id': user[1],
            'role': user[2],
            'email': user[3],
            'name': user[4],
            'photo_url': user[5],
            'professor': user[6]
        })

    return jsonify(users_list)

# 사용자 추가 (POST /users)
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    student_id = data.get('student_id')
    role = 0 if data.get('role') == 'manager' else 1  # role 값 변환
    email = data.get('email')
    name = data.get('name')
    photo_url = data.get('photo_url')
    professor = data.get('professor')

    # 이름 길이 확인
    if len(name) > 5:
        return jsonify({'error': 'Name must be 5 characters or less.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO user (student_id, role, email, name, photo_url, professor) VALUES (%s, %s, %s, %s, %s, %s)',
        (student_id, role, email, name, photo_url, professor)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '사용자가 추가되었습니다!'}), 201

# 기기 조회 (GET /devices)
@app.route('/devices', methods=['GET'])
def get_devices():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM device')
    devices = cursor.fetchall()
    cursor.close()
    conn.close()

    devices_list = []
    for device in devices:
        devices_list.append({
            'device_id': device[0],
            'type': device[1],
            'model': device[2],
            'availability': device[3],
            'created_at': device[4],
            'device_name': device[5],
            'memo': device[6]
        })

    return jsonify(devices_list)

# 기기 추가 (POST /devices)
@app.route('/devices', methods=['POST'])
def create_device():
    data = request.json
    device_type = data.get('type')
    
    # ENUM 타입 유효성 검사
    valid_types = ['window', 'mac', 'galaxy tab', 'ipad', 'accessary']
    if device_type not in valid_types:
        return jsonify({'error': 'Invalid device type'}), 400

    model = data.get('model')
    availability = data.get('availability')
    device_name = data.get('device_name')
    memo = data.get('memo')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO device (type, model, availability, device_name, memo) VALUES (%s, %s, %s, %s, %s)',
        (device_type, model, availability, device_name, memo)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '기기가 추가되었습니다!'}), 201

# 대여 기록 추가 (POST /rentals)
@app.route('/rentals', methods=['POST'])
def create_rental():
    data = request.json
    user_id = data.get('user_id')
    device_id = data.get('device_id')
    
    # 날짜 문자열을 datetime 형식으로 변환
    request_date = datetime.strptime(data.get('request_date'), '%Y-%m-%dT%H:%M:%S')
    status = data.get('status')
    approval_date = datetime.strptime(data.get('approval_date'), '%Y-%m-%dT%H:%M:%S') if data.get('approval_date') else None
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%dT%H:%M:%S') if data.get('end_date') else None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO rental (user_id, device_id, request_date, status, approval_date, end_date) VALUES (%s, %s, %s, %s, %s, %s)',
        (user_id, device_id, request_date, status, approval_date, end_date)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '대여 기록이 추가되었습니다!'}), 201

# 반납 기록 추가 (POST /returns)
@app.route('/returns', methods=['POST'])
def create_return():
    data = request.json
    rental_id = data.get('rental_id')
    return_date = datetime.strptime(data.get('return_date'), '%Y-%m-%dT%H:%M:%S')
    photo_url = data.get('photo_url')
    status = data.get('status')
    condition = data.get('condition')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO return (rental_id, return_date, photo_url, status, condition) VALUES (%s, %s, %s, %s, %s)',
        (rental_id, return_date, photo_url, status, condition)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': '반납 기록이 추가되었습니다!'}), 201

# 사람 수를 데이터베이스에 저장하는 엔드포인트 (POST /congestion)
@app.route('/congestion', methods=['POST'])
def add_congestion():
    data = request.json
    person_count = data.get('person_count', 0)  # 기본값을 0으로 설정

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO congestion (person_num) VALUES (%s)", (person_count,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': f'Saved person count {person_count} to congestion table.'}), 201

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    student_id = data.get('student_id')

    # student_id 유효성 검사
    if not student_id:
        return jsonify({'error': 'student_id is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT student_id FROM user WHERE student_id = %s', (student_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return jsonify({'error': 'User not found'}), 404

    # QR 코드 생성
    qr = qrcode.make(student_id)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    # QR 코드 이미지 반환
    response = make_response(buffer.getvalue())
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline; filename=qr_code.png')

    return response

@app.route('/scan_qr', methods=['POST'])
def check_student_id():
    data = request.json
    student_id = data.get('student_id')

    # student_id 유효성 검사
    if not student_id:
        return jsonify({'error': 'student_id is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT student_id FROM user WHERE student_id = %s', (student_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return jsonify({'status': 1})  # student_id가 데이터베이스에 존재함
    else:
        return jsonify({'status': 0})  # student_id가 데이터베이스에 존재하지 않음



# Flask 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
