import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.0.122", 5555))  # Сервер слушает на этом порту
server.listen()

players = {}  # ID игрока -> (x, y)
player_id = 0
lock = threading.Lock()  # Чтобы избежать одновременной записи


def handle_client(client_socket, player_num):
    global players
    try:
        while True:
            data = client_socket.recv(4096).decode()
            if not data:
                break

            try:
                parts = data.split(",")
                if len(parts) != 2:  # Проверяем, что получили ровно две координаты
                    print(f"⚠️ Некорректные данные от клиента: {data}")
                    continue  # Пропускаем этот цикл

                x, y = map(int, parts)  # Конвертируем в числа

                with lock:
                    players[player_num] = (x, y)

                # Отправляем данные всех игроков
                with lock:
                    client_socket.sendall(str(players).encode())

            except Exception as e:
                print(f"Ошибка при обработке данных: {e}")
                break
            with lock:
                players[player_num] = (x, y)

            # Отправляем данные всех игроков
            with lock:
                client_socket.sendall(str(players).encode())

    except Exception as e:
        print(f"Игрок {player_num} отключился.")
        print(f"Ошибка при получении данных: {e}")
    finally:
        with lock:
            del players[player_num]
        client_socket.close()


while True:
    client_socket, addr = server.accept()

    with lock:
        player_id += 1
        players[player_id] = (250, 250)  # Начальная позиция игрока

    print(f"Игрок {player_id} подключился.")

    threading.Thread(target=handle_client, args=(client_socket, player_id)).start()
