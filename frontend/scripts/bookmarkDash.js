
function toggleLinks(sectionId) {
    const sections = document.querySelectorAll('.links-container');
    sections.forEach(section => section.style.display = 'none');
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = section.style.display === 'block' ? 'none' : 'block';
    }
}

function toggleBookmark(button, resourceId) {
    // Toggle the visual appearance of the bookmark button
    if (button.textContent === '⭐') {
        button.textContent = '★';
        button.style.color = 'gold';
    } else {
        button.textContent = '⭐';
        button.style.color = '';
    }

    // Assuming the current user's ID is available on the frontend (from a global variable or session)
    const userId = getCurrentUserId(); // Implement this function to get the current user's ID

    // Send an AJAX request to save the bookmark
    fetch('/save_bookmark', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            resource_id: resourceId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Bookmark saved successfully!');
            } else {
                console.error('Error saving bookmark');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
