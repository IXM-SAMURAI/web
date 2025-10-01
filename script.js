// script.js - используем GET запросы для лайков

// ========== ФУНКЦИИ ДЛЯ ГАЛЕРЕИ ==========
function loadImages() {
    console.log("Загрузка изображений...");
    
    fetch('/api/images')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(images => {
            const gallery = document.getElementById('gallery');
            
            if (!images || images.length === 0) {
                gallery.innerHTML = '<p>📷 Пока нет загруженных изображений</p>';
                return;
            }
            
            gallery.innerHTML = '';
            images.forEach(image => {
                const imageDiv = document.createElement('div');
                imageDiv.className = 'gallery-item';
                imageDiv.innerHTML = `
                    <a href="${image.filepath}" data-fancybox="gallery" data-caption="${image.filename}">
                        <img src="${image.filepath}" alt="${image.filename}">
                    </a>
                    <h4>${image.filename}</h4>
                    <div class="image-stats">
                        <div class="stat">👁️ ${image.views}</div>
                        <div class="stat">❤️ ${image.likes}</div>
                        <div class="stat">📊 ${image.filesize}</div>
                    </div>
                    <button class="like-btn" onclick="likeImage(${image.id})">Нравится</button>
                `;
                gallery.appendChild(imageDiv);
                
                // Увеличиваем счетчик просмотров
                fetch(`/api/view?id=${image.id}`).catch(() => {});
            });
        })
        .catch(error => {
            console.error('Error loading images:', error);
            document.getElementById('gallery').innerHTML = '<p>❌ Ошибка загрузки галереи</p>';
        });
}

function likeImage(imageId) {
    console.log('Liking image:', imageId);
    
    // Используем GET запрос для лайков
    fetch(`/api/like?id=${imageId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Like successful:', data.message);
                loadImages(); // Перезагружаем галерею
            } else {
                alert('Ошибка: ' + (data.error || data.message));
            }
        })
        .catch(error => {
            console.error('Error liking image:', error);
            alert('Ошибка сети при добавлении лайка');
        });
}

function uploadImage() {
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('uploadStatus');
    
    if (!fileInput.files[0]) {
        statusDiv.innerHTML = '<p style="color: #E4514A;">❌ Выберите файл</p>';
        return;
    }
    
    const file = fileInput.files[0];
    if (file.size > 10 * 1024 * 1024) {
        statusDiv.innerHTML = '<p style="color: #E4514A;">❌ Файл слишком большой</p>';
        return;
    }
    
    statusDiv.innerHTML = '<p>⏳ Загрузка...</p>';
    const formData = new FormData();
    formData.append('image', file);
    
    fetch('/api/upload', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                statusDiv.innerHTML = '<p style="color: green;">✅ Изображение загружено!</p>';
                fileInput.value = '';
                setTimeout(loadImages, 1000);
            } else {
                statusDiv.innerHTML = `<p style="color: #E4514A;">❌ ${data.message}</p>`;
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            statusDiv.innerHTML = '<p style="color: #E4514A;">❌ Ошибка загрузки</p>';
        });
}

// ========== ФУНКЦИИ ДЛЯ ОТЗЫВОВ ==========
function loadReviews(sort = 'recent') {
    fetch(`/api/reviews?limit=10&sort=${sort}`)
        .then(response => response.json())
        .then(reviews => {
            const reviewsContainer = document.getElementById('reviewsList');
            
            if (!reviews || reviews.length === 0) {
                reviewsContainer.innerHTML = '<p>Пока нет отзывов. Будьте первым!</p>';
                return;
            }
            
            reviewsContainer.innerHTML = '';
            reviews.forEach(review => {
                const reviewDiv = document.createElement('div');
                reviewDiv.className = 'review-item';
                reviewDiv.innerHTML = `
                    <div class="review-header">
                        <strong>${review.author}</strong>
                        <span class="review-date">${formatDate(review.created_at)}</span>
                    </div>
                    <div class="review-rating">${generateStars(review.rating)}</div>
                    <div class="review-text">${review.text}</div>
                    <div class="review-footer">
                        <button class="review-like-btn" onclick="likeReview(${review.id})">
                            👍 ${review.likes}
                        </button>
                    </div>
                `;
                reviewsContainer.appendChild(reviewDiv);
            });
        })
        .catch(error => {
            console.error('Error loading reviews:', error);
            document.getElementById('reviewsList').innerHTML = '<p>❌ Ошибка загрузки отзывов</p>';
        });
}

function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            const statsContainer = document.getElementById('reviewsStats');
            statsContainer.innerHTML = `
                <div class="stats-card">
                    <h3>📊 Статистика отзывов</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">${stats.average_rating}</div>
                            <div class="stat-label">Средний рейтинг</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${stats.total_reviews}</div>
                            <div class="stat-label">Всего отзывов</div>
                        </div>
                    </div>
                    <div class="rating-distribution">
                        ${generateRatingDistribution(stats.rating_distribution)}
                    </div>
                </div>
            `;
        })
        .catch(error => console.error('Error loading stats:', error));
}

function submitReview() {
    const author = document.getElementById('reviewAuthor').value || 'Аноним';
    const text = document.getElementById('reviewText').value;
    const rating = document.querySelector('input[name="rating"]:checked');
    
    if (!text.trim()) {
        alert('Пожалуйста, напишите текст отзыва');
        return;
    }
    
    if (!rating) {
        alert('Пожалуйста, выберите оценку');
        return;
    }
    
    const reviewData = {
        author: author,
        text: text,
        rating: parseInt(rating.value)
    };
    
    fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Отзыв успешно добавлен!');
            document.getElementById('reviewForm').reset();
            loadReviews();
            loadStats();
        } else {
            alert('❌ ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error submitting review:', error);
        alert('❌ Ошибка при отправке отзыва');
    });
}

function likeReview(reviewId) {
    console.log('Liking review:', reviewId);
    
    // Используем GET запрос для лайков отзывов
    fetch(`/api/review-like?id=${reviewId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Review like successful:', data.message);
                loadReviews();
            } else {
                alert('Ошибка: ' + (data.error || data.message));
            }
        })
        .catch(error => {
            console.error('Error liking review:', error);
            alert('Ошибка сети при добавлении лайка');
        });
}

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
function generateStars(rating) {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

function generateRatingDistribution(distribution) {
    let html = '<div class="distribution-title">Распределение оценок:</div>';
    const total = Object.values(distribution).reduce((a, b) => a + b, 0);
    
    for (let i = 5; i >= 1; i--) {
        const count = distribution[i] || 0;
        const percentage = total > 0 ? (count / total) * 100 : 0;
        html += `
            <div class="distribution-row">
                <span class="distribution-stars">${generateStars(i)}</span>
                <div class="distribution-bar">
                    <div class="distribution-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="distribution-count">${count}</span>
            </div>
        `;
    }
    return html;
}

// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('gallery')) loadImages();
    if (document.getElementById('reviewsList')) {
        loadReviews();
        loadStats();
    }
});

function initMainPage() {
    console.log("Главная страница загружена");
}

function initContactPage() {
    console.log("Страница контактов загружена");
}