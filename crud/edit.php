<?php
// Подключаемся к базе данных
require_once 'includes/db_connect.php';
require_once 'includes/functions.php';

// Проверяем что передан ID услуги
if (!isset($_GET['id'])) {
    header('Location: index.php');
    exit();
}

$id = $_GET['id'];

// Получаем данные услуги
$service = getServiceById($pdo, $id);

// Если услуга не найдена
if (!$service) {
    header('Location: index.php');
    exit();
}

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

        // Подготавливаем SQL запрос для обновления
        $sql = "UPDATE services SET 
                name = ?, description = ?, price = ?, duration = ?, 
                is_special_offer = ?, discount_percent = ? 
                WHERE id = ?";
        
        $stmt = $pdo->prepare($sql);
        
        // Выполняем запрос
        $stmt->execute([$name, $description, $price, $duration, $is_special_offer, $discount_percent, $id]);
        
        // Перенаправляем на главную с сообщением об успехе
        header('Location: index.php?message=updated');
        exit();
        
    } catch (PDOException $e) {
        $error = "Ошибка при обновлении услуги: " . $e->getMessage();
    }
}
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Редактировать услугу - Разноцветный XM</title>
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
        .btn-danger { background: #dc3545; color: white; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; }
        .checkbox-group input { width: auto; }
        .actions { display: flex; gap: 10px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✏️ Редактировать услугу</h1>
        
        <a href="index.php" class="btn btn-secondary">← Назад к списку</a>
        
        <?php if (isset($error)): ?>
            <div class="error"><?= $error ?></div>
        <?php endif; ?>

        <form method="POST" action="edit.php?id=<?= $id ?>">
            <div class="form-group">
                <label for="name">Название услуги *</label>
                <input type="text" id="name" name="name" required 
                       value="<?= htmlspecialchars($service['name']) ?>"
                       placeholder="Например: Свадебная фотосессия">
            </div>

            <div class="form-group">
                <label for="description">Описание услуги</label>
                <textarea id="description" name="description" 
                          placeholder="Подробное описание услуги..."><?= htmlspecialchars($service['description']) ?></textarea>
            </div>

            <div class="form-group">
                <label for="price">Цена (руб) *</label>
                <input type="number" id="price" name="price" step="0.01" min="0" required 
                       value="<?= $service['price'] ?>"
                       placeholder="Например: 5000">
            </div>

            <div class="form-group">
                <label for="duration">Длительность (минут) *</label>
                <input type="number" id="duration" name="duration" min="1" required 
                       value="<?= $service['duration'] ?>"
                       placeholder="Например: 120">
            </div>

            <div class="form-group">
                <div class="checkbox-group">
                    <input type="checkbox" id="is_special_offer" name="is_special_offer" value="1" 
                           <?= $service['is_special_offer'] ? 'checked' : '' ?>>
                    <label for="is_special_offer">Акционное предложение</label>
                </div>
            </div>

            <div class="form-group">
                <label for="discount_percent">Скидка (%)</label>
                <input type="number" id="discount_percent" name="discount_percent" 
                       min="0" max="100" value="<?= $service['discount_percent'] ?>" 
                       placeholder="Размер скидки от 0 до 100">
            </div>

            <div class="actions">
                <button type="submit" class="btn btn-primary">💾 Сохранить изменения</button>
                <a href="index.php" class="btn btn-secondary">❌ Отмена</a>
                <a href="delete.php?id=<?= $id ?>" class="btn btn-danger" 
                   onclick="return confirm('Вы уверены что хотите удалить эту услугу?')">🗑️ Удалить услугу</a>
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