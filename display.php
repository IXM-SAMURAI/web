<?php
$pdo = new PDO('mysql:host=localhost;dbname=your_database', 'username', 'password');
$stmt = $pdo->query("SELECT id, filename, filedata FROM images");
while ($row = $stmt->fetch()) {
    echo '<img src="data:image/jpeg;base64,' . base64_encode($row['filedata']) . '" alt="' . htmlspecialchars($row['filename']) . '">';
}
?>
