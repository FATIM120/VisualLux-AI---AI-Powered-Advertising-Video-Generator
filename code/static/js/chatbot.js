// Chatbot functionality

document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotInput = document.getElementById('chatbotInput');
    const chatbotSend = document.getElementById('chatbotSend');
    const chatbotMessages = document.getElementById('chatbotMessages');
    const chatbotAttachBtn = document.getElementById('chatbotAttachBtn');
    const chatbotImageUpload = document.getElementById('chatbotImageUpload');
    const chatbotPreview = document.getElementById('chatbotPreview');
    
    let currentChatImage = null;
    
    // Toggle chatbot window
    chatbotToggle.addEventListener('click', function() {
        chatbotWindow.classList.toggle('active');
        if (chatbotWindow.classList.contains('active')) {
            chatbotInput.focus();
        }
    });
    
    // Close chatbot window
    chatbotClose.addEventListener('click', function() {
        chatbotWindow.classList.remove('active');
    });
    
    // Send message on Enter key
    chatbotInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Send message on button click
    chatbotSend.addEventListener('click', sendMessage);
    
    // Trigger file upload when attach button is clicked
    chatbotAttachBtn.addEventListener('click', function() {
        chatbotImageUpload.click();
    });
    
    // Handle image upload
    chatbotImageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            
            // Check file type
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                addMessage('Only JPG and PNG images are supported.', 'bot');
                return;
            }
            
            // Check file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                addMessage('Image size should be less than 5MB.', 'bot');
                return;
            }
            
            // Upload the image
            const formData = new FormData();
            formData.append('image', file);
            
            fetch('/upload-chat-image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Save the image path
                    currentChatImage = data.image_path;
                    
                    // Display image preview
                    chatbotPreview.innerHTML = '';
                    const previewElement = document.createElement('div');
                    previewElement.className = 'chatbot-preview-image';
                    previewElement.style.backgroundImage = `url(${URL.createObjectURL(file)})`;
                    
                    const removeBtn = document.createElement('div');
                    removeBtn.className = 'chatbot-preview-remove';
                    removeBtn.innerHTML = '×';
                    removeBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        chatbotPreview.innerHTML = '';
                        currentChatImage = null;
                    });
                    
                    previewElement.appendChild(removeBtn);
                    chatbotPreview.appendChild(previewElement);
                } else {
                    addMessage(`Error: ${data.error}`, 'bot');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Failed to upload image. Please try again.', 'bot');
            });
        }
    });
    
    // Function to send message
    function sendMessage() {
        const message = chatbotInput.value.trim();
        
        if (message === '' && !currentChatImage) {
            return;
        }
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        chatbotInput.value = '';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message typing-indicator';
        typingIndicator.innerHTML = '<div class="message-content"><p>Typing...</p></div>';
        chatbotMessages.appendChild(typingIndicator);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        
        // Send to backend
        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: message,
                image_path: currentChatImage
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            chatbotMessages.removeChild(typingIndicator);
            
            // Add response
            if (data.answer) {
                addMessage(data.answer, 'bot');
            } else if (data.error) {
                addMessage(`Error: ${data.error}`, 'bot');
            }
            
            // Clear image after processing
            chatbotPreview.innerHTML = '';
            currentChatImage = null;
        })
        .catch(error => {
            // Remove typing indicator
            chatbotMessages.removeChild(typingIndicator);
            
            console.error('Error:', error);
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
        });
    }
    
    // Function to add message to chat
    function addMessage(message, sender) {
        if (!message) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        // Format links in the message
        message = formatLinks(message);
        
        // Format message with paragraphs
        const formattedMessage = message.split('\n')
            .filter(line => line.trim() !== '')
            .map(line => `<p>${line}</p>`)
            .join('');
        
        messageElement.innerHTML = `<div class="message-content">${formattedMessage}</div>`;
        
        chatbotMessages.appendChild(messageElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Function to format links in text
    function formatLinks(text) {
        // URL regex pattern
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, url => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`);
    }
});
