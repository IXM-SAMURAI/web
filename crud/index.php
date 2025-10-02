<?php
// crud/index.php
require_once 'includes/db_connect.php';
require_once 'includes/functions.php';

$services = getAllServices($pdo);

// Обработка сообщений об успехе/ошибках
$message = '';
if (isset($_GET['message'])) {
    $messages = [
        'created' => 'Услуга успешно создана!',
        'updated' => 'Услуга успешно обновлена!',
        'deleted' => 'Услуга успешно удалена!'
    ];
    $message = $messages[$_GET['message']] ?? '';
}
?>

<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Управление услугами - Разноцветный XM</title>
    <style>
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .alert.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .service-card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .special-offer { border-left: 4px solid #ff6b6b; background: #fff9f9; }
        .btn { padding: 8px 15px; text-decoration: none; border-radius: 4px; margin: 2px; display: inline-block; }
        .btn-primary { background: #007bff; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-success { background: #28a745; color: white; }
        .price { font-weight: bold; font-size: 1.2em; }
        .discount { color: #dc