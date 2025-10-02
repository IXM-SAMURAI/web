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

// Обрабатываем удаление
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // Вместо полного удаления делаем услугу неактивной (мягкое удаление)
        $sql = "UPDATE services SET is_active = FALSE WHERE id = ?";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$id]);
        
        // Перенаправляем на главную с сообщением об успехе
        header('Location: index.php?message=deleted');
        exit();
        
    } catch (PDOException $e) {
        $error = "Ошибка при удалении услуги: " . $e->getMessage();
    }
}
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Удалить услугу - Разноцветный XM</title>
    <style>
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .service-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .btn { 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 4px; 
            border: none;
            cursor: pointer;
            margin-right: 10px;
        }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; }
        .warning { color: #856404; background: #fff3cd; padding: 15px; border-radius: 4px; border: 1px solid #ffeaa7; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗑️ Удалить услугу</h1>
        
        <a href="index.php" class="btn btn-secondary">← Назад к списку</a>
        
        <?php if (isset($error)): ?>
            <div class="error"><?= $error ?></div>
        <?php endif; ?>

        <div class="warning">
            <h3>⚠️ Вы уверены что хотите удалить эту услугу?</h3>
            <p>Это действие нельзя будет отменить. Услуга будет скрыта из общего списка.</p>
        </div>

        <div class="service-info">
            <h3><?= htmlspecialchars($service['name']) ?></h3>
            <p><strong>Описание:</strong> <?= htmlspecialchars($service['description']) ?></p>
            <p><strong>Цена:</strong> <?= $service['price'] ?> руб.</p>
            <p><strong>Длительность:</strong> <?= $service['duration'] ?> мин.</p>
            <?php if ($service['is_special_offer']): ?>
                <p><strong>Акция:</strong> Да (скидка <?= $service['discount_percent'] ?>%)</p>
            <?php endif; ?>
        </div>

        <form method="POST" action="delete.php?id=<?= $id ?>">
            <button type="submit" class="btn btn-danger">🗑️ Да, удалить услугу</button>
            <a href="edit.php?id=<?= $id ?>" class="btn btn-secondary">✏️ Редактировать вместо удаления</a>
            <a href="index.php" class="btn btn-secondary">❌ Отмена</a>
        </form>
    </div>
</body>
</html>