import socket
import threading
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = int(os.getenv("PORT", 8080))  # Получаем порт из окружения, по умолчанию 8080

server.bind(("0.0.0.0", PORT))  # Слушаем на всех интерфейсах
server.listen()
print(f"Сервер запущен на порту {PORT}")

players = {}  # ID игрока -> (x, y)
player_id = 0
lock = threading.Lock()  # Для потокобезопасного доступа к данным


def handle_client(client_socket, player_num):
    global players
    try:
        while True:
            data = client_socket.recv(4096).decode()
            if not data:
                break

            # Проверяем, не HTTP ли это
            if "HTTP" in data or "GET" in data or "Host:" in data:
                print(f"⚠️ Игрок {player_num} отправил HTTP-запрос, соединение закрыто.")
                client_socket.close()
                return

            try:
                x, y = map(int, data.split(","))  # Разбираем координаты

                with lock:
                    players[player_num] = (x, y)

                    # Отправляем всем игрокам обновленный список
                    client_socket.sendall(str(players).encode())

            except ValueError:
                print(f"⚠️ Некорректные данные от игрока {player_num}: {data}")

    except Exception as e:
        print(f"Игрок {player_num} отключился. Ошибка: {e}")

    finally:
        with lock:
            players.pop(player_num, None)  # Безопасное удаление
        client_socket.close()


while True:
    client_socket, addr = server.accept()

    with lock:
        player_id += 1
        players[player_id] = (250, 250)  # Начальная позиция игрока

    print(f"Игрок {player_id} подключился. {addr}")

    threading.Thread(target=handle_client, args=(client_socket, player_id)).start()
