# Khi tướng địch sử dụng flash thì thời gian sẽ bắt đầu tính thêm 5 phút

import keyboard
import pyautogui as pag
import time
import threading
import winsound  # Thư viện để phát âm thanh bíp

# Khởi tạo thời gian game
current_time = 60  # Thời gian hiện tại được khởi tạo
timer_started = False  # Biến cờ để kiểm tra thời gian đã bắt đầu hay chưa

def start_timer():
    global current_time, timer_started
    if not timer_started:  # Kiểm tra nếu chưa bắt đầu
        # In ra thời gian bắt đầu
        print(f"Bắt đầu thời gian game: {current_time // 60}:{current_time % 60:02d}")
        timer_started = True  # Đánh dấu thời gian đã bắt đầu
        
        # Bắt đầu tăng thời gian mỗi giây
        threading.Thread(target=update_timer).start()
    else:
        print("Thời gian đã bắt đầu, không thể thiết lập lại.")

def update_timer():
    global current_time
    while True:
        time.sleep(1)  # Chờ 1 giây
        current_time += 1  # Tăng thời gian hiện tại lên 1 giây
        minutes = current_time // 60
        seconds = current_time % 60
        print(f"Thời gian hiện tại: {minutes}:{seconds:02d}")

def track_flash_cooldown():
    global current_time, timer_started

    if timer_started:  # Đảm bảo rằng chúng ta chỉ theo dõi khi thời gian đã bắt đầu
        cooldown_time = current_time + 300  # Thêm thời gian tùy chỉnh cho thử nghiệm
        cooldown_minutes = cooldown_time // 60
        cooldown_seconds = cooldown_time % 60
        formatted_time = f"{cooldown_minutes}:{cooldown_seconds:02d}"

        # Gửi tin nhắn vào game
        pag.typewrite(f"[Time Flash: {formatted_time}]")
        pag.press('enter')
        
        # Kiểm tra thời điểm khớp và phát âm thanh bíp
        threading.Thread(target=alarm_check, args=(cooldown_time,)).start()

def alarm_check(alarm_time):
    global current_time
    while True:
        time.sleep(1)  # Kiểm tra mỗi giây
        if current_time == alarm_time:  # Kiểm tra nếu thời gian hiện tại khớp với thời gian báo
            winsound.Beep(1000, 1000)  # Phát âm thanh bíp (tần số 1000Hz, âm thanh 1 giây)
            # Sau khi phát âm thanh bíp, có thể cần chờ một lúc rồi kiểm tra tiếp
            time.sleep(1)  # Đợi một giây trước khi tiếp tục kiểm tra
            # Cho phép phát lại âm thanh nếu vẫn khớp với thời gian
            while current_time == alarm_time:
                winsound.Beep(1000, 1000)
                time.sleep(1)  # Đợi 1 giây trước khi kiểm tra lại

def ask_for_time_setup():
    global current_time
    change_time = input("Bạn có muốn thay đổi thời gian mặc định 1:00 không? (yes/no): ").strip().lower()
    
    if change_time == 'yes':
        time_input = input("Nhập thời gian theo định dạng phút:giây (ví dụ: 2:00): ")
        try:
            minutes, seconds = map(int, time_input.split(':'))
            total_seconds = minutes * 60 + seconds
            if total_seconds > 0:
                current_time = total_seconds  # Cập nhật thời gian được nhập vào
                print(f"Thời gian đã được thiết lập là: {minutes}:{seconds:02d}")
            else:
                print("Thời gian phải lớn hơn 0. Sử dụng thời gian mặc định 1:00.")
                current_time = 60  # Quay lại thời gian mặc định
        except ValueError:
            print("Định dạng không hợp lệ. Sử dụng thời gian mặc định 1:00.")
            current_time = 60  # Quay lại thời gian mặc định
    else:
        print("Sử dụng thời gian mặc định 1:00.")

def main():
    print("Chương trình sẽ hỏi bạn có muốn thay đổi thời gian mặc định 1:00 hay không.")
    ask_for_time_setup()  # Hỏi người dùng trước khi bắt đầu

    print("Nhấn phím - để bắt đầu thời gian game và F5 để theo dõi thời gian hồi chiêu.")

    # Đặt phím tắt
    keyboard.add_hotkey('-', start_timer)
    keyboard.add_hotkey('F5', track_flash_cooldown)

    # Giữ chương trình chạy liên tục
    keyboard.wait('=')  # Bấm '=' để thoát

if __name__ == "__main__":
    main()
