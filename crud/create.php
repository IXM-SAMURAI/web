<?php
// Подключаемся к базе данных
require_once 'includes/db_connect.php';

// Обрабатываем отправку формы
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // Получаем данные из формы
        $name = $_POST['name'];
        $description = $_POST['description'];
        $price = $_POST['price'];
        $duration = $_POST['duration'];
        $is_special_offer = isset($_POST['is_special_offer']) ? 1 : 0;
        $discount_percent = $_POST['discount_percent'] ?? 0;

        // Подготавливаем SQL запрос
        $sql = "INSERT INTO services (name, description, price, duration, is_special_offer, discount_percent) 
                VALUES (?, ?, ?, ?, ?, ?)";
        
        $stmt = $pdo->prepare($sql);
        
        // Выполняем запрос
        $stmt->execute([$name, $description, $price, $duration, $is_special_offer, $discount_percent]);
        
        // Перенаправляем на главную с сообщением об успехе
        header('Location: index.php?message=created');
        exit();
        
    } catch (PDOException $e) {
        $error = "Ошибка при создании услуги: " . $e->getMessage();
    }
}
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Добавить услугу - Разноцветный XM</title>
    <style>
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, select { 
            width: 100%; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            box-sizing: border-box;
        }
        textarea { height: 100px; }
        .btn { 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 4px; 
            border: none;
            cursor: pointer;
            margin-right: 10px;
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; }
        .checkbox-group input { width: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>➕ Добавить новую услугу</h1>
        
        <a href="index.php" class="btn btn-secondary">← Назад к списку</a>
        
        <?php if (isset($error)): ?>
            <div class="error"><?= $error ?></div>
        <?php endif; ?>

        <form method="POST" action="create.php">
            <div class="form-group">
                <label for="name">Название услуги *</label>
                <input type="text" id="name" name="name" required 
                       placeholder="Например: Свадебная фотосессия">
            </div>

            <div class="form-group">
                <label for="description">Описание услуги</label>
                <textarea id="description" name="description" 
                          placeholder="Подробное описание услуги..."></textarea>
            </div>

            <div class="form-group">
                <label for="price">Цена (руб) *</label>
                <input type="number" id="price" name="price" step="0.01" min="0" required 
                       placeholder="Например: 5000">
            </div>

            <div class="form-group">
                <label for="duration">Длительность (минут) *</label>
                <input type="number" id="duration" name="duration" min="1" required 
                       placeholder="Например: 120">
            </div>

            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" id="is_special_offer" name="is_special_offer" value="1">
                    <label for="is_special_offer">Акционное предложение</label>
                </div>
            </div>

            <div class="form-group">
                <label for="discount_percent">Скидка (%)</label>
                <input type="number" id="discount_percent" name="discount_percent" 
                       min="0" max="100" value="0" 
                       placeholder="Размер скидки от 0 до 100">
            </div>

            <div class="form-group">
                <button type="submit" class="btn btn-primary">💾 Сохранить услугу</button>
                <a href="index.php" class="btn btn-secondary">❌ Отмена</a>
            </div>
        </form>
    </div>

    <script>
        // Показываем/скрываем поле скидки в зависимости от чекбокса
        const specialOfferCheckbox = document.getElementById('is_special_offer');
        const discountField = document.getElementById('discount_percent');
        
        specialOfferCheckbox.addEventListener('change', function() {
            discountField.disabled = !this.checked;
            if (!this.checked) {
                discountField.value = '0';
            }
        });

        // При загрузке страницы устанавливаем начальное состояние
        discountField.disabled = !specialOfferCheckbox.checked;
    </script>
</body>
</html>