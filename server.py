import http.server
import socketserver
import sqlite3
import os
import json
import urllib.parse
import time
from datetime import datetime

class GalleryHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path.startswith('/api/images'):
            self.send_images_list()
        elif self.path.startswith('/api/view'):
            self.increment_view_count()
        elif self.path.startswith('/api/reviews'):
            self.send_reviews_list()
        elif self.path.startswith('/api/stats'):
            self.send_stats()
        elif self.path.startswith('/api/like'):
            self.handle_like()  # Добавляем GET обработку для лайков
        elif self.path.startswith('/api/review-like'):
            self.handle_review_like()  # Добавляем GET обработку для лайков отзывов
        else:
            if self.path == '/':
                self.path = '/main.html'
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_upload_simple()
        elif self.path.startswith('/api/like'):
            self.handle_like()
        elif self.path == '/api/reviews':
            self.handle_review_submit()
        elif self.path.startswith('/api/review-like'):
            self.handle_review_like()
        else:
            self.send_json_error(404, "API endpoint not found")
    
    def send_json_error(self, code, message):
        """Отправляет ошибку в формате JSON"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_response = {
            'success': False,
            'error': message,
            'code': code
        }
        self.wfile.write(json.dumps(error_response).encode())
    
    def send_json_response(self, code, data):
        """Отправляет успешный JSON ответ"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_images_list(self):
        """Отправляет список изображений из БД"""
        try:
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, filepath, filesize, views, likes 
                FROM images ORDER BY id DESC
            ''')
            images = []
            for row in cursor.fetchall():
                if os.path.exists(row[2]):
                    images.append({
                        'id': row[0],
                        'filename': row[1],
                        'filepath': row[2],
                        'filesize': self.format_file_size(row[3]),
                        'views': row[4],
                        'likes': row[5]
                    })
            conn.close()
            
            self.send_json_response(200, images)
            
        except Exception as e:
            print(f"Database error: {e}")
            self.send_json_error(500, f"Database error: {str(e)}")
    
    def send_reviews_list(self):
        """Отправляет список отзывов"""
        try:
            query = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(query.query)
            limit = int(params.get('limit', [5])[0])
            sort = params.get('sort', ['recent'])[0]
            
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            
            if sort == 'popular':
                cursor.execute('''
                    SELECT id, author, text, rating, likes, created_at 
                    FROM reviews 
                    ORDER BY likes DESC, created_at DESC 
                    LIMIT ?
                ''', (limit,))
            else:  # recent
                cursor.execute('''
                    SELECT id, author, text, rating, likes, created_at 
                    FROM reviews 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            reviews = []
            for row in cursor.fetchall():
                reviews.append({
                    'id': row[0],
                    'author': row[1],
                    'text': row[2],
                    'rating': row[3],
                    'likes': row[4],
                    'created_at': row[5]
                })
            conn.close()
            
            self.send_json_response(200, reviews)
            
        except Exception as e:
            print(f"Reviews error: {e}")
            self.send_json_error(500, f"Reviews error: {str(e)}")
    
    def send_stats(self):
        """Отправляет статистику отзывов"""
        try:
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT AVG(rating), COUNT(*) FROM reviews')
            avg_rating, total_reviews = cursor.fetchone()
            
            cursor.execute('''
                SELECT rating, COUNT(*) 
                FROM reviews 
                GROUP BY rating 
                ORDER BY rating
            ''')
            rating_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            stats = {
                'average_rating': round(avg_rating, 2) if avg_rating else 0,
                'total_reviews': total_reviews or 0,
                'rating_distribution': rating_distribution
            }
            
            self.send_json_response(200, stats)
            
        except Exception as e:
            print(f"Stats error: {e}")
            self.send_json_error(500, f"Stats error: {str(e)}")
    
    def handle_review_submit(self):
        """Обрабатывает отправку отзыва"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            author = data.get('author', 'Аноним')
            text = data.get('text', '')
            rating = int(data.get('rating', 5))
            
            if not text.strip():
                self.send_json_error(400, 'Текст отзыва не может быть пустым')
                return
            
            if rating < 1 or rating > 5:
                self.send_json_error(400, 'Рейтинг должен быть от 1 до 5')
                return
            
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reviews (author, text, rating, likes, created_at)
                VALUES (?, ?, ?, 0, datetime('now'))
            ''', (author, text.strip(), rating))
            conn.commit()
            review_id = cursor.lastrowid
            conn.close()
            
            print(f"✅ Новый отзыв от {author}, рейтинг: {rating}")
            
            response = {
                'success': True,
                'message': 'Отзыв успешно добавлен',
                'review_id': review_id
            }
            self.send_json_response(200, response)
            
        except Exception as e:
            print(f"Review submit error: {e}")
            self.send_json_error(500, f"Review submit error: {str(e)}")
    
    def handle_review_like(self):
        """Обрабатывает лайки отзывов (GET и POST)"""
        try:
            # Извлекаем ID из query параметров
            query = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(query.query)
            review_id = int(params.get('id', [0])[0])
            
            if review_id == 0:
                self.send_json_error(400, 'ID отзыва не указан')
                return
            
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            
            # Проверяем существование отзыва
            cursor.execute('SELECT id, likes FROM reviews WHERE id = ?', (review_id,))
            result = cursor.fetchone()
            
            if not result:
                self.send_json_error(404, 'Отзыв не найден')
                return
            
            current_likes = result[1]
            
            # Увеличиваем счетчик лайков
            cursor.execute('UPDATE reviews SET likes = likes + 1 WHERE id = ?', (review_id,))
            conn.commit()
            
            # Получаем обновленное количество лайков
            cursor.execute('SELECT likes FROM reviews WHERE id = ?', (review_id,))
            new_likes = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Лайк для отзыва {review_id}: {current_likes} → {new_likes}")
            
            response = {
                'success': True, 
                'likes': new_likes,
                'message': f'Лайк добавлен! Теперь {new_likes} лайков'
            }
            self.send_json_response(200, response)
            
        except Exception as e:
            print(f"Review like error: {e}")
            self.send_json_error(500, f"Review like error: {str(e)}")
    
    def handle_like(self):
        """Обрабатывает лайки изображений (GET и POST)"""
        try:
            # Извлекаем ID из query параметров
            query = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(query.query)
            image_id = int(params.get('id', [0])[0])
            
            if image_id == 0:
                self.send_json_error(400, 'ID изображения не указан')
                return
            
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            
            # Проверяем существование изображения
            cursor.execute('SELECT id, filename, likes FROM images WHERE id = ?', (image_id,))
            result = cursor.fetchone()
            
            if not result:
                self.send_json_error(404, 'Изображение не найдено')
                return
            
            filename, current_likes = result[1], result[2]
            
            # Увеличиваем счетчик лайков
            cursor.execute('UPDATE images SET likes = likes + 1 WHERE id = ?', (image_id,))
            conn.commit()
            
            # Получаем обновленное количество лайков
            cursor.execute('SELECT likes FROM images WHERE id = ?', (image_id,))
            new_likes = cursor.fetchone()[0]
            conn.close()
            
            print(f"✅ Лайк для изображения {filename} (ID: {image_id}): {current_likes} → {new_likes}")
            
            response = {
                'success': True, 
                'likes': new_likes,
                'message': f'Лайк добавлен! Теперь {new_likes} лайков'
            }
            self.send_json_response(200, response)
            
        except Exception as e:
            print(f"Like error: {e}")
            self.send_json_error(500, f"Like error: {str(e)}")
    
    def format_file_size(self, size_bytes):
        """Форматирует размер файла в читаемый вид"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def handle_upload_simple(self):
        """Обрабатывает загрузку файлов"""
        try:
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']
            
            print(f"Upload request: {content_length} bytes, type: {content_type}")
            
            post_data = self.rfile.read(content_length)
            
            if 'multipart/form-data' in content_type:
                boundary = content_type.split('boundary=')[1].encode()
                parts = post_data.split(b'--' + boundary)
                
                for part in parts:
                    if b'name="image"' in part and b'filename="' in part:
                        header_end = part.find(b'\r\n\r\n')
                        if header_end == -1:
                            continue
                            
                        headers = part[:header_end]
                        file_data = part[header_end + 4:]
                        
                        if file_data.endswith(b'--\r\n'):
                            file_data = file_data[:-5]
                        
                        filename_start = headers.find(b'filename="') + 10
                        filename_end = headers.find(b'"', filename_start)
                        if filename_start != 9 and filename_end != -1:
                            filename = headers[filename_start:filename_end].decode('utf-8')
                            
                            if filename:
                                filepath = os.path.join(upload_dir, filename)
                                
                                counter = 1
                                name, ext = os.path.splitext(filename)
                                while os.path.exists(filepath):
                                    filename = f"{name}_{counter}{ext}"
                                    filepath = os.path.join(upload_dir, filename)
                                    counter += 1
                                
                                with open(filepath, 'wb') as f:
                                    f.write(file_data)
                                
                                filesize = os.path.getsize(filepath)
                                conn = sqlite3.connect('gallery.db')
                                cursor = conn.cursor()
                                cursor.execute('''
                                    INSERT INTO images (filename, filepath, filesize, views, likes)
                                    VALUES (?, ?, ?, 0, 0)
                                ''', (filename, filepath, filesize))
                                conn.commit()
                                image_id = cursor.lastrowid
                                conn.close()
                                
                                print(f"✅ Файл загружен: {filename} (ID: {image_id}, Size: {filesize} bytes)")
                                
                                response = {
                                    'success': True,
                                    'message': 'Файл успешно загружен',
                                    'image_id': image_id,
                                    'filename': filename
                                }
                                self.send_json_response(200, response)
                                return
            
            response = {
                'success': False,
                'message': 'Не удалось обработать файл'
            }
            self.send_json_response(400, response)
            
        except Exception as e:
            print(f"Upload error: {e}")
            response = {
                'success': False,
                'message': f'Ошибка загрузки: {str(e)}'
            }
            self.send_json_response(500, response)
    
    def increment_view_count(self):
        """Увеличивает счетчик просмотров"""
        try:
            query = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(query.query)
            image_id = int(params.get('id', [0])[0])
            
            if image_id == 0:
                self.send_json_error(400, 'ID изображения не указан')
                return
            
            conn = sqlite3.connect('gallery.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM images WHERE id = ?', (image_id,))
            if not cursor.fetchone():
                self.send_json_error(404, 'Изображение не найдено')
                return
            
            cursor.execute('UPDATE images SET views = views + 1 WHERE id = ?', (image_id,))
            conn.commit()
            conn.close()
            
            self.send_json_response(200, {'success': True})
            
        except Exception as e:
            print(f"View count error: {e}")
            self.send_json_error(500, f"Ошибка счетчика просмотров: {str(e)}")

def init_database():
    """Инициализирует базу данных"""
    try:
        conn = sqlite3.connect('gallery.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                filesize INTEGER,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                text TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM images')
        count_images = cursor.fetchone()[0]
        
        if count_images == 0:
            photo_dir = 'фото'
            if os.path.exists(photo_dir):
                for filename in os.listdir(photo_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        filepath = os.path.join(photo_dir, filename)
                        if os.path.isfile(filepath):
                            filesize = os.path.getsize(filepath)
                            cursor.execute('''
                                INSERT INTO images (filename, filepath, filesize, views, likes)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (filename, filepath, filesize, 0, 0))
                            print(f"✅ Добавлено изображение: {filename}")
        
        cursor.execute('SELECT COUNT(*) FROM reviews')
        count_reviews = cursor.fetchone()[0]
        
        if count_reviews == 0:
            test_reviews = [
                ('Анна', 'Отличный фотограф! Очень профессионально подошел к съемке.', 5),
                ('Сергей', 'Качественные фото, быстрая обработка. Рекомендую!', 4),
                ('Мария', 'Прекрасные работы, видно что мастер своего дела!', 5),
                ('Дмитрий', 'Хорошие фото, но немного затянули с обработкой.', 3),
                ('Ольга', 'Супер! Лучший фотограф в городе!', 5)
            ]
            
            for author, text, rating in test_reviews:
                cursor.execute('''
                    INSERT INTO reviews (author, text, rating, likes, created_at)
                    VALUES (?, ?, ?, ?, datetime('now', '-' || abs(random() % 30) || ' days'))
                ''', (author, text, rating, abs(hash(text)) % 10))
                print(f"✅ Добавлен тестовый отзыв от {author}")
        
        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")
        print("✅ Таблицы: images, reviews")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")

def start_server():
    PORT = 8000
    
    init_database()
    
    with socketserver.TCPServer(("", PORT), GalleryHandler) as httpd:
        print("=" * 60)
        print("🖼️  Галерея фотографий с отзывами запущена!")
        print(f"🌐 Откройте: http://localhost:{PORT}")
        print("📁 Загрузка изображений доступна в галерее")
        print("💬 Система отзывов с рейтингом и лайками")
        print("👍 Лайки работают через GET и POST запросы")
        print("=" * 60)
        print("Для остановки: Ctrl+C")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")

if __name__ == "__main__":
    start_server()