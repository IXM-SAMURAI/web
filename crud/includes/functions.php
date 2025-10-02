<?php
// crud/includes/functions.php
function getServiceById($pdo, $id) {
    $stmt = $pdo->prepare("SELECT * FROM services WHERE id = ?");
    $stmt->execute([$id]);
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

function getAllServices($pdo) {
    $stmt = $pdo->query("SELECT * FROM services WHERE is_active = TRUE ORDER BY created_at DESC");
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function calculateDiscountedPrice($price, $discount) {
    return $price - ($price * $discount / 100);
}
?>